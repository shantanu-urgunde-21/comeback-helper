import json
import re
import time
from pathlib import Path
from typing import Optional, List

import networkx as nx
from google.genai import types

from shared.config import get_settings
from .schema import (
    MathNodeExtraction,
    MathEdgeExtraction,
    MathEntityExtraction,
    GraphNode,
    GraphEdge,
    ConceptTaxonomy,
    Provenance,
    normalize,
)
from shared.llm.gemini import get_gemini_client, get_gemini_model_name, get_gemini_candidate_models
from shared.llm.ollama import get_ollama_client
from shared.logger import log


# ---------------------------------------------------------------------------
# Noise filter — rejects structural headings and sentence fragments
# ---------------------------------------------------------------------------

NOISE_PATTERN = re.compile(
    r"(?i)^("
    r"exercise|solution|hint|problem|conclusion|example|"
    r"page\s*\d*|lecture\s*notes?|note\s*\d*|figure\s*\d*|"
    r"table\s*\d*|section\s*\d*|chapter\s*\d*|"
    r"from\s|if\s+the\s|the\s+differential|"
    r"lec\s*\d*|q\.?\s*\d+|ans(wer)?|"
    r"assignment|homework|quiz|test|exam"
    r").*"
)

# Minimum meaningful words after stripping articles/prepositions
_STRIP_WORDS = {"a", "an", "the", "of", "in", "on", "for", "to", "and", "or", "is", "are", "was", "were"}


def _normalize_relation(source: str, target: str, relation: str) -> tuple[str, str, str]:
    """Canonicalizes inverse relation types onto one direction.

    PREREQUISITE_FOR(A, B) and DEPENDS_ON(B, A) assert the same fact, but
    the extractor could emit either one depending on the note's phrasing.
    Left unnormalized, a note asserting both forms for the same pair (or
    two notes each picking one) produces two directed edges pointing
    opposite ways between the same nodes — an artificial cycle that breaks
    any hierarchical/topological layout. DEPENDS_ON is the only form stored;
    PREREQUISITE_FOR(A, B) is flipped to DEPENDS_ON(B, A).
    """
    if relation == "PREREQUISITE_FOR":
        return target, source, "DEPENDS_ON"
    return source, target, relation


def _is_valid_entity(name: str) -> bool:
    """Returns True if the name looks like a real math concept, not noise."""
    clean = name.strip()
    if not clean or len(clean) < 3 or clean.startswith("<!--"):
        return False
    if NOISE_PATTERN.match(clean):
        return False
    words = [w for w in clean.split() if w.lower() not in _STRIP_WORDS]
    if len(words) < 1:
        return False
    return True


# ---------------------------------------------------------------------------
# 2-Pass Extraction Prompts
# ---------------------------------------------------------------------------

PASS1_NODE_PROMPT = """\
You are an expert mathematical entity and taxonomy extractor.
TASK: Extract formal mathematical entities (Theorems, Definitions, Concepts, Formulas, Proofs, Lemmas) and their 3-tier SKOS taxonomy from the text.

STRICT RULES:
1. DO NOT extract structural terms (e.g. 'Exercise 1', 'Problem', 'Solution', 'Hint', 'Example', 'Conclusion', 'Page 1', 'Lecture notes').
2. EXTRACT ONLY formal mathematical concept names (e.g. 'Exact Differential Equation', 'Total Differential', 'Mixed Partials Theorem', 'Integrating Factor', 'Separable ODE').
3. Capitalize formal math concept names properly.
4. Each node MUST have a formal 1-2 sentence definition description.
5. Assign domain taxonomy (domain, subdomain, topic).

TEXT:
{text}
"""

PASS2_EDGE_PROMPT = """\
You are an expert mathematical relationship and prerequisite linker.
TASK: Establish directional relationships between mathematical concepts using ONLY the concept IDs in the dictionary below.

CONCEPT DICTIONARY (concept_id → display name):
{concept_id_map}

NEW CONCEPT IDS FROM THIS NOTE (focus edges on these):
{new_concept_ids}

EXISTING KNOWLEDGE BASE CONCEPT IDS (available link targets):
{existing_concept_ids}

STRICT RULES:
1. Use ONLY concept IDs from the CONCEPT DICTIONARY as edge source and target values. Never invent a new name or ID.
2. Valid relation types: DEPENDS_ON, USES_DEFINITION, PROVES, COROLLARY_OF, USES_AXIOM, USES_LEMMA.
3. DEPENDS_ON(A, B) means A requires B — B is the more foundational concept. Never emit an inverse "is a prerequisite for" edge.
4. Include an evidence quote (the sentence from the text that supports the relationship) in the description field where possible.

TEXT:
{text}
"""


class MathGraphIndexer:
    """
    Indexes mathematical Markdown notes into a NetworkX Property Graph.

    Uses a decoupled 2-Pass extraction architecture:
      Pass 1: Concept & SKOS Taxonomy Extractor (LLM Call #1)
      Pass 2: Relationship & Prerequisite Linker (LLM Call #2)

    Fallback hierarchy: Gemini API → Local Ollama LLM → Deterministic Block Parser.
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        vault_path: Optional[Path] = None,
        vector_store=None,
        vault_manager=None,
    ):
        """
        `vault_manager` and `vector_store` are injected rather than imported.

        In a container the caller passes the HTTP clients from .clients; run
        in-process (the monolith) it passes the real objects. Importing either
        one at module scope would hard-wire this module to a deployment shape
        and make the graph package unimportable outside its own container.

        Falling back to the HTTP client when nothing is passed keeps the
        containerised default working with no wiring.
        """
        self.settings = get_settings()
        self.storage_path = storage_path or self.settings.storage_path
        self.vault_path = vault_path or self.settings.vault_path

        self.graph_file = self.storage_path / "graph.json"
        self.graph = self._load_graph()

        if vault_manager is None:
            from .clients import ObsidianVaultManager
            vault_manager = ObsidianVaultManager(
                vault_path=self.vault_path,
                state_file_path=self.storage_path / "vault_state.json",
            )
        self.vault_manager = vault_manager

        self._vector_store = vector_store
        log.info("MathGraphIndexer initialized (2-Pass Architecture).")

    # ------------------------------------------------------------------
    # Graph I/O
    # ------------------------------------------------------------------

    def _load_graph(self) -> nx.DiGraph:
        """Builds the in-memory graph from SQLite (.storage/concepts.db) —
        the store of record as of plan.md Phase 3. graph.json is now only a
        cache/export written by save_graph(); this no longer reads it.
        """
        from . import graph_store
        return graph_store.load_graph()

    def clear_graph(self):
        """Clears in-memory graph, the SQLite store of record, graph.json,
        and state tracker.

        As of plan.md Phase 3, graph.json alone is not enough to clear —
        _load_graph now rebuilds from SQLite, so a restart after this would
        otherwise resurrect everything. concepts/aliases (identity) are
        deliberately left intact by graph_store.clear_all — see its
        docstring.
        """
        from . import graph_store
        self.graph.clear()
        graph_store.clear_all()
        if self.graph_file.exists():
            try:
                self.graph_file.write_text(
                    '{"nodes":[],"edges":[]}', encoding="utf-8"
                )
            except Exception as e:
                log.warning(f"Failed to clear graph.json: {e}")

        self.vault_manager.clear_state()
        log.info("Knowledge graph and vault state cleared.")

    def save_graph(self):
        """Exports the in-memory graph to graph.json.

        As of plan.md Phase 3, SQLite (.storage/concepts.db) is the store of
        record — this is now a cache/export step, not the persistence
        mechanism. Kept as its own call (same call sites as before) because
        two consumers read graph.json directly off disk, never through this
        class: src/server.py's `/api/graph` and the stdlib-only
        scripts/graph_health.py. Both depend on this running at the same
        points it always has and producing the same file shape.
        """
        from . import graph_store
        graph_store.export_graph_json(self.graph, self.graph_file)

    # ------------------------------------------------------------------
    # Pass 1: Node & Taxonomy Extraction
    # ------------------------------------------------------------------

    def _extract_nodes_pass(
        self, text: str, course_domain: str
    ) -> List[GraphNode]:
        """Executes Pass 1 (Node & Taxonomy Extraction) via Gemini or Ollama."""
        client = get_gemini_client()
        if client:
            prompt = PASS1_NODE_PROMPT.format(text=text)
            for model_name in get_gemini_candidate_models():
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=MathNodeExtraction,
                            temperature=0.1,
                        ),
                    )
                    data = json.loads(response.text)
                    nodes = MathNodeExtraction(**data).nodes
                    log.info(f"Pass 1 (Gemini {model_name}): Extracted {len(nodes)} concept nodes.")
                    return nodes
                except Exception as e:
                    log.warning(f"Pass 1 Gemini ({model_name}) node extraction failed ({e}), trying candidate...")

        # Ollama Fallback
        ollama = get_ollama_client()
        if ollama.is_available():
            for model in ["llama3.2", "qwen2.5:3b", "phi3:mini"]:
                if not ollama.has_model(model):
                    continue
                prompt = PASS1_NODE_PROMPT.format(text=text[:3000])
                prompt += (
                    "\n\nRespond ONLY with valid JSON matching:\n"
                    '{"nodes": [{"name": "...", "entity_type": "Theorem|Definition|Concept|Formula|Proof|Lemma", '
                    '"description": "...", "taxonomy": {"domain": "...", "subdomain": "...", "topic": "..."}}]}'
                )
                resp = ollama.chat(prompt=prompt, model=model, response_format="json", timeout=60)
                if resp:
                    try:
                        data = json.loads(resp)
                        nodes = MathNodeExtraction(**data).nodes
                        log.info(f"Pass 1 (Ollama {model}): Extracted {len(nodes)} concept nodes.")
                        return nodes
                    except Exception:
                        pass

        return []

    # ------------------------------------------------------------------
    # Pass 2: Edge & Relationship Extraction
    # ------------------------------------------------------------------

    def _extract_edges_pass(
        self,
        text: str,
        doc_concept_map: dict[str, str],      # name → canonical_id (this document)
        existing_concept_map: dict[str, str],  # canonical_id → label (existing graph)
    ) -> list[GraphEdge]:
        """Executes Pass 2 (Relationship & Edge Linker) via Gemini or Ollama.

        Receives pre-resolved concept maps so the LLM works with canonical IDs
        rather than display names. The concept_id_map in the prompt is the
        merged id→name view; new_concept_ids and existing_concept_ids separate
        the two populations so the LLM knows which are new vs. already known.
        """
        if not doc_concept_map:
            return []

        # Build the id→name view the prompt exposes to the LLM
        id_to_name: dict[str, str] = {v: k for k, v in doc_concept_map.items()}
        id_to_name.update(existing_concept_map)

        concept_id_map_json = json.dumps(id_to_name, ensure_ascii=False)
        new_concept_ids_json = json.dumps(list(doc_concept_map.values()))
        existing_concept_ids_json = json.dumps(list(existing_concept_map.keys()))

        client = get_gemini_client()
        if client:
            prompt = PASS2_EDGE_PROMPT.format(
                concept_id_map=concept_id_map_json,
                new_concept_ids=new_concept_ids_json,
                existing_concept_ids=existing_concept_ids_json,
                text=text,
            )
            for model_name in get_gemini_candidate_models():
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=MathEdgeExtraction,
                            temperature=0.1,
                        ),
                    )
                    data = json.loads(response.text)
                    edges = MathEdgeExtraction(**data).edges
                    log.info(f"Pass 2 (Gemini {model_name}): Linked {len(edges)} relationship edges.")
                    return edges
                except Exception as e:
                    log.warning(f"Pass 2 Gemini ({model_name}) edge extraction failed ({e}), trying candidate...")

        # Ollama Fallback
        ollama = get_ollama_client()
        if ollama.is_available():
            for model in ["llama3.2", "qwen2.5:3b", "phi3:mini"]:
                if not ollama.has_model(model):
                    continue
                prompt = PASS2_EDGE_PROMPT.format(
                    concept_id_map=concept_id_map_json,
                    new_concept_ids=new_concept_ids_json,
                    existing_concept_ids=existing_concept_ids_json,
                    text=text[:3000],
                )
                prompt += (
                    "\n\nRespond ONLY with valid JSON matching:\n"
                    '{"edges": [{"source": "concept_id", "target": "concept_id", "relation": "DEPENDS_ON|USES_DEFINITION|PROVES|COROLLARY_OF|USES_AXIOM|USES_LEMMA", "description": "evidence quote"}]}'
                )
                resp = ollama.chat(prompt=prompt, model=model, response_format="json", timeout=60)
                if resp:
                    try:
                        data = json.loads(resp)
                        edges = MathEdgeExtraction(**data).edges
                        log.info(f"Pass 2 (Ollama {model}): Linked {len(edges)} relationship edges.")
                        return edges
                    except Exception:
                        pass

        return []

    # ------------------------------------------------------------------
    # Tier 3: Deterministic LaTeX block + heading parser (NO prose regex)
    # ------------------------------------------------------------------

    def _block_extraction(
        self, text: str, course_domain: str
    ) -> MathEntityExtraction:
        """
        100% offline, deterministic fallback parsing LaTeX environments,
        Markdown headings with typed prefixes, and wikilinks.
        """
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        node_names: set[str] = set()

        def _add_node(name: str, etype: str, desc: str = ""):
            clean = name.strip().rstrip(":")
            if clean in node_names or not _is_valid_entity(clean):
                return
            node_names.add(clean)
            nodes.append(
                GraphNode(
                    id=clean,
                    name=clean,
                    entity_type=etype,
                    taxonomy=ConceptTaxonomy(
                        domain=course_domain,
                        subdomain="Course Notes",
                        topic=clean,
                    ),
                    description=desc or f"{etype}: {clean}",
                )
            )

        # 1. LaTeX environments: \begin{theorem}[Name]...\end{theorem}
        env_pattern = re.compile(
            r"\\begin\{(theorem|definition|lemma|corollary|proof|proposition|axiom)\}"
            r"(?:\[([^\]]+)\])?"
            r"(.*?)"
            r"\\end\{\1\}",
            re.DOTALL | re.IGNORECASE,
        )
        for match in env_pattern.finditer(text):
            env_type = match.group(1).title()
            env_name = match.group(2)
            env_body = match.group(3).strip()[:200]
            if env_name and _is_valid_entity(env_name):
                _add_node(env_name.strip(), env_type, env_body)

        # 2. Typed Markdown headings: ## Theorem: Cauchy-Schwarz Inequality
        heading_pattern = re.compile(
            r"^#{1,3}\s+"
            r"(?:(Theorem|Definition|Concept|Lemma|Proof|Formula|Proposition|Corollary|Axiom)"
            r"\s*:\s*)"
            r"(.+)$",
            re.MULTILINE | re.IGNORECASE,
        )
        for match in heading_pattern.finditer(text):
            etype = match.group(1).title()
            name = match.group(2).strip().rstrip(":")
            if etype == "Proposition":
                etype = "Theorem"
            if etype not in ["Theorem", "Definition", "Concept", "Proof", "Formula", "Lemma", "Corollary", "Axiom"]:
                etype = "Concept"
            _add_node(name, etype)

        # 3. Obsidian wikilinks [[Target Concept]]
        wikilinks = re.findall(r"\[\[(.*?)\]\]", text)
        for link in wikilinks:
            link_clean = link.split("|")[0].strip()
            if (
                _is_valid_entity(link_clean)
                and not link_clean.endswith((".png", ".jpg", ".pdf"))
            ):
                _add_node(link_clean, "Concept", "Wikilink reference from vault note")
                if nodes and nodes[0].name != link_clean:
                    edges.append(
                        GraphEdge(
                            source=nodes[0].name,
                            target=link_clean,
                            relation="DEPENDS_ON",
                        )
                    )

        log.info(f"Block extractor found {len(nodes)} nodes and {len(edges)} edges.")
        return MathEntityExtraction(nodes=nodes, edges=edges)

    # ------------------------------------------------------------------
    # Helper & Decoupled Extraction Pipeline
    # ------------------------------------------------------------------

    def _get_candidate_context(self, text: str) -> dict[str, str]:
        """Returns {concept_id: display_label} for existing graph concepts, used
        as Pass 2 context. Capped at 25 entries.

        TODO (Phase 5): source relevance ranking via the vector store. The
        vector store's chunk `source` field holds note filenames, not graph
        node keys (QIDs/CUST_), so the query result cannot be joined back to
        graph nodes without a round-trip through the `mentions` table. Until
        that join is implemented, all graph nodes contribute equally.
        """
        candidates: dict[str, str] = {}
        for n in list(self.graph.nodes)[:25]:
            candidates[n] = self.graph.nodes[n].get("label", n)
        return candidates

    def _split_chunks(self, text: str, document_id: str) -> list[tuple[str, str]]:
        """Split markdown text into (chunk_id, chunk_text) by heading (H1–H3).

        Each section heading starts a new chunk. Sections that contain only a
        heading line (no content beyond the heading itself) are treated as empty
        and dropped — a heading with no body has nothing for Pass 1 to extract.
        chunk_id format: '{document_id}#s{n:04d}', zero-indexed over non-empty
        sections only.
        Falls back to the whole document as one chunk when no headings exist.
        """
        sections = re.split(r'\n(?=#{1,3} )', text)
        chunks = []
        for s in sections:
            stripped = s.strip()
            if not stripped:
                continue
            # Check if this section has content beyond just headings
            lines = stripped.split('\n')
            has_content = False
            for line in lines:
                # If a line doesn't start with # and has text, it's content
                if line.strip() and not re.match(r'^#+\s', line):
                    has_content = True
                    break
            # Keep the chunk if it has non-heading content, or if it's a plain line (no heading)
            if has_content or (len(lines) == 1 and not re.match(r'^#+\s', lines[0].strip())):
                chunks.append((f"{document_id}#s{len(chunks):04d}", stripped))

        return chunks if chunks else [(f"{document_id}#s0000", text)]

    def _normalize_edge_endpoint(
        self,
        raw: str,
        id_to_name: dict[str, str],
        name_to_id: dict[str, str],
    ) -> str | None:
        """Map a Pass 2 edge endpoint to a canonical concept id.

        The LLM should emit canonical IDs (the keys of id_to_name), but may
        emit display names instead. This method handles both cases and falls
        back to normalize()-based matching for minor casing differences.
        Returns None if the endpoint cannot be resolved — the caller must
        skip that edge rather than storing a garbage id.
        """
        if raw in id_to_name:
            return raw
        if raw in name_to_id:
            return name_to_id[raw]
        norm_raw = normalize(raw)
        for name, cid in name_to_id.items():
            if normalize(name) == norm_raw:
                return cid
        log.warning(f"Pass 2 edge endpoint '{raw}' not in concept map — skipping edge")
        return None

    def extract_from_text(
        self,
        text: str,
        use_llm: bool = False,
        course_domain: str = "Differential Equations",
    ) -> MathEntityExtraction:
        """
        Executes decoupled 2-pass graph extraction:
          Pass 1: Node & SKOS Taxonomy Extraction
          Pass 2: Relationship & Edge Linking
        """
        if not use_llm:
            return self._block_extraction(text, course_domain)

        # Pass 1: Extract concept nodes
        extracted_nodes = self._extract_nodes_pass(text, course_domain)

        # Fallback to block extractor if LLM node extraction returned nothing
        if not extracted_nodes:
            return self._block_extraction(text, course_domain)

        # Filter extracted nodes through noise validator
        valid_nodes = [n for n in extracted_nodes if _is_valid_entity(n.name)]

        # Pass 2: Link relationships & edges between nodes
        doc_concept_map = {n.name: (n.id if n.id else n.name) for n in valid_nodes}
        existing_concept_map = self._get_candidate_context(text)
        extracted_edges = self._extract_edges_pass(text, doc_concept_map, existing_concept_map)

        return MathEntityExtraction(nodes=valid_nodes, edges=extracted_edges)

    # ------------------------------------------------------------------
    # Entity Resolution (deduplication)
    # ------------------------------------------------------------------

    def _resolve_entity(
        self, name: str, document_id: Optional[str] = None, course: Optional[str] = None
    ) -> str:
        """Resolves a surface form to a canonical concept id via the
        deterministic identity ladder (document -> course -> global
        authority -> mint), instead of embedding similarity.

        Replaces the old ENTITY_MERGE_THRESHOLD cosine-similarity comparison
        (see docs/diagnosis.md and plan.md Phase 1): that approach paid an
        embedding call per candidate on every extraction and still missed
        exact duplicates worded differently, because no similarity threshold
        separates "same concept, different words" from "different concept,
        shared word". This does not need `self._vector_store` at all —
        resolution no longer depends on the graph service having a vector
        service dependency (plan.md's "dependency graph gets sparser").
        """
        from .authority import resolve_concept
        return resolve_concept(name, document_id=document_id, course=course)

    # Debris identified in docs/diagnosis.md D4, dropped by migrate_to_identity_layer.
    _RELATION_NAMES = {
        "DEPENDS_ON", "USES_DEFINITION", "PROVES", "COROLLARY_OF",
        "USES_AXIOM", "USES_LEMMA", "PREREQUISITE_FOR",
    }
    _PLACEHOLDER_LABEL = re.compile(r"(?i)^(theorem|lemma)\s*[tl]?\d+$")

    def migrate_to_identity_layer(self) -> dict:
        """Plan.md Phase 2: retrofits the deterministic identity layer (Phase
        1, `_resolve_entity`/`authority.resolve_concept`) onto nodes already
        sitting in the graph from before it existed.

        Every surviving node's id (and every alias already recorded on it —
        docs/diagnosis.md D2: previously write-only) is resolved through the
        same global-scope ladder new extractions use, so nodes that only
        differ by spelling convention collapse onto one canonical id. Junk
        identified in D4 is dropped outright first: retired note-container
        nodes (`CONTAINS` was removed but its endpoints weren't), relation
        names that leaked in as nodes, `Theorem T1`-style placeholders, and
        raw LaTeX/sentence fragments extracted as if they were concept names.

        Deterministic and idempotent — resolving an already-canonical id
        (a QID or CUST_<hash>) just returns it unchanged via its own global
        alias, so re-running this after Phase 1 is fully adopted is a no-op,
        not a hazard.
        """
        from .authority import resolve_concept, register_alias

        def is_note_container(nid: str) -> bool:
            return str(self.graph.nodes[nid].get("description", "")).startswith("Course Note")

        def is_junk(nid: str) -> bool:
            if is_note_container(nid):
                return True
            if nid in self._RELATION_NAMES:
                return True
            if self._PLACEHOLDER_LABEL.match(nid):
                return True
            if "$" in nid or len(nid) > 70:
                return True
            return False

        dropped = [n for n in list(self.graph.nodes) if is_junk(n)]
        for n in dropped:
            self.graph.remove_node(n)

        # Resolve every surviving node, and every alias already recorded on
        # it, to a canonical id. A small pause per node keeps this polite to
        # Wikidata on a graph with many not-yet-cached concepts; most of a
        # previously-touched graph will be alias-table hits (no network).
        canonical_for: dict[str, str] = {}
        for nid in list(self.graph.nodes):
            canon_id = resolve_concept(nid)
            canonical_for[nid] = canon_id
            for alias in self.graph.nodes[nid].get("aliases", []) or []:
                register_alias(alias, canon_id)
            time.sleep(0.2)

        def sort_key(nid: str):
            data = self.graph.nodes[nid]
            has_desc = bool(data.get("description"))
            return (0 if has_desc else 1, -self.graph.degree(nid), nid)

        groups: dict[str, list[str]] = {}
        for nid in sorted(self.graph.nodes, key=sort_key):
            groups.setdefault(canonical_for[nid], []).append(nid)

        def best_display_label(candidates: list[str]) -> str:
            # Richest-node-wins (sort_key above) picks the best description
            # and degree, but that node's own id/label is often the ugliest
            # spelling (e.g. lowercase "wronskian", created because it
            # happened to carry the description) or literal math notation
            # recorded as an alias ("W(y1, y2)", "F = ma", "dF", "y_p"). The
            # atlas is meant to be read, so the display label is chosen
            # separately from every id/label/alias in the merged group:
            # prefer a proper name (starts uppercase, no formula syntax or
            # digits) over one with digits (still readable: "Theorem 1.6")
            # over anything else (snake_case, lowercase, notation
            # fragments); shortest within a tier.
            def score(s: str) -> tuple:
                if not s:
                    return (9, 0)
                has_formula_syntax = bool(re.search(r"[=(){}\\_]", s))
                starts_upper = s[:1].isupper()
                has_digit = any(ch.isdigit() for ch in s)
                if starts_upper and not has_formula_syntax and not has_digit:
                    tier = 0
                elif starts_upper and not has_formula_syntax:
                    tier = 1
                else:
                    tier = 2
                return (tier, len(s))
            return min(candidates, key=score)

        merged_count = 0
        for canon_id, members in groups.items():
            base_nid = members[0]
            base_data = dict(self.graph.nodes[base_nid])
            merged_provenance = list(base_data.get("provenance") or [])
            merged_aliases = list(base_data.get("aliases") or [])
            label_candidates = [base_nid, base_data.get("label", base_nid)]

            for dup_nid in members[1:]:
                dup_data = self.graph.nodes[dup_nid]
                if not base_data.get("description") and dup_data.get("description"):
                    base_data["description"] = dup_data["description"]
                for p in dup_data.get("provenance") or []:
                    if p not in merged_provenance:
                        merged_provenance.append(p)
                for a in [dup_nid, *(dup_data.get("aliases") or [])]:
                    if a not in merged_aliases:
                        merged_aliases.append(a)
                label_candidates.append(dup_nid)
                label_candidates.append(dup_data.get("label", dup_nid))
                merged_count += 1

            label = best_display_label(label_candidates + merged_aliases)

            # Rewire every member's edges onto the canonical id before any
            # member node is removed (includes base_nid itself, whose own id
            # may differ from canon_id).
            for member_nid in members:
                for _, tgt, edata in list(self.graph.out_edges(member_nid, data=True)):
                    tgt_canon = canonical_for.get(tgt, tgt)
                    if tgt_canon != canon_id:
                        self.graph.add_edge(canon_id, tgt_canon, **edata)
                for src, _, edata in list(self.graph.in_edges(member_nid, data=True)):
                    src_canon = canonical_for.get(src, src)
                    if src_canon != canon_id:
                        self.graph.add_edge(src_canon, canon_id, **edata)

            for nid in members:
                self.graph.remove_node(nid)

            self.graph.add_node(
                canon_id,
                id=canon_id,
                label=label,
                entity_type=base_data.get("entity_type", "Concept"),
                taxonomy=base_data.get("taxonomy", {}),
                description=base_data.get("description", ""),
                provenance=merged_provenance,
                aliases=merged_aliases,
            )

        return {
            "dropped_junk_nodes": len(dropped),
            "nodes_merged_away": merged_count,
            "final_node_count": self.graph.number_of_nodes(),
            "final_edge_count": self.graph.number_of_edges(),
        }

    def backfill_sql_store(self) -> dict:
        """Plan.md Phase 3: one-time backfill of `mentions`/`edges` (and the
        `concepts.node_attrs_json` bridge column) from the graph already
        sitting in memory (loaded from graph.json at construction time).

        Must run before `_load_graph` is switched over to read from SQLite —
        it is what populates the store `_load_graph` will then read from.
        Every node id here is already a `concepts` row (Phases 1-2's
        `resolve_concept` guarantees that), so `upsert_node_attrs` — UPDATE-
        only by design — is safe to call unconditionally.

        Two known, deliberate approximations, not silently treated as
        equivalent to what `index_note` writes going forward:
          - Backfilled `mentions.surface_text` uses each node's current
            display label, not the literal surface string a given document
            used — today's `Provenance` records never captured that
            separately.
          - Backfilled `edges` carry no `quote` and share the chunk_id
            sentinel `"__backfill__"` (not NULL, so the composite PK's
            dedup — NULL != NULL in SQLite — still works on a re-run):
            nothing wrote per-edge evidence before this phase existed, so
            there is nothing genuine to backfill.
        """
        from . import graph_store

        concepts_touched = 0
        mentions_inserted = 0
        edges_inserted = 0

        with graph_store.connect() as conn:
            for n_id, data in self.graph.nodes(data=True):
                graph_store.upsert_node_attrs(
                    conn, n_id,
                    label=data.get("label", n_id),
                    entity_type=data.get("entity_type", "Concept"),
                    taxonomy=data.get("taxonomy", {}),
                    description=data.get("description", ""),
                    provenance=data.get("provenance", []),
                    aliases=data.get("aliases", []),
                )
                concepts_touched += 1

                seen_docs = set()
                for prov in data.get("provenance", []) or []:
                    doc_id = prov.get("doc_id") if isinstance(prov, dict) else None
                    if doc_id and doc_id not in seen_docs:
                        seen_docs.add(doc_id)
                        graph_store.insert_mention(
                            conn, chunk_id=doc_id,
                            surface_text=data.get("label", n_id),
                            concept_id=n_id,
                        )
                        mentions_inserted += 1

            for u, v, edata in self.graph.edges(data=True):
                graph_store.insert_edge(
                    conn, source_id=u, target_id=v,
                    relation=edata.get("relation", "DEPENDS_ON"),
                    chunk_id="__backfill__", quote=None, origin="extracted",
                )
                edges_inserted += 1

        return {
            "concepts_touched": concepts_touched,
            "mentions_inserted": mentions_inserted,
            "edges_inserted": edges_inserted,
        }

    # ------------------------------------------------------------------
    # Note indexing
    # ------------------------------------------------------------------

    def index_note(self, note_path: Path, use_llm: bool = False):
        """Indexes a single Markdown file into the NetworkX graph.

        Phase 4 flow (use_llm=True):
          - Split note into chunks by heading.
          - Pass 1 runs per chunk: extract nodes, resolve names → canonical IDs,
            write mentions with chunk-level chunk_id, accumulate doc_concept_map.
          - Pass 2 runs once on the full text: receives the accumulated id map,
            emits edges already keyed by canonical ID.

        Phase 4 flow (use_llm=False):
          - Block extraction on full text (unchanged from Phase 3).
          - Chunks are still used for mentions so provenance is chunk-level.
        """
        content = note_path.read_text(encoding="utf-8")
        course = note_path.parent.name if note_path.parent != self.vault_path else "General"
        main_node = note_path.stem
        document_id = str(note_path)

        prov_record = Provenance(
            doc_id=main_node,
            doc_title=f"{main_node}.md",
            doc_path=str(note_path),
            exact_quote=content[:200].replace("\n", " "),
        ).model_dump()

        chunks = self._split_chunks(content, document_id)

        # ------------------------------------------------------------------
        # Pass 1: per chunk — extract nodes, resolve, accumulate concept map.
        # _resolve_entity opens its own DB connection (authority._connect),
        # so we run all resolutions here, BEFORE opening graph_store.connect(),
        # to avoid two concurrent writers on the same SQLite file.
        # ------------------------------------------------------------------
        doc_concept_map: dict[str, str] = {}  # surface_name → canonical_id
        chunk_node_lists: list[tuple[str, list]] = []  # (chunk_id, [resolved node dicts])

        for chunk_id, chunk_text in chunks:
            if use_llm:
                raw_nodes = self._extract_nodes_pass(chunk_text, course)
                chunk_nodes = [n for n in raw_nodes if _is_valid_entity(n.name)]
                if not chunk_nodes:
                    block = self._block_extraction(chunk_text, course)
                    chunk_nodes = [n for n in block.nodes if _is_valid_entity(n.name)]
            else:
                block = self._block_extraction(chunk_text, course)
                chunk_nodes = [n for n in block.nodes if _is_valid_entity(n.name)]

            resolved_nodes = []
            for node in chunk_nodes:
                n_id = self._resolve_entity(
                    node.id or node.name, document_id=document_id, course=course
                )
                doc_concept_map[node.name] = n_id
                resolved_nodes.append((node, n_id))

            chunk_node_lists.append((chunk_id, resolved_nodes))

        # ------------------------------------------------------------------
        # Pass 2: once on full document — edges with canonical IDs.
        # Also resolved before opening graph_store connection.
        # ------------------------------------------------------------------
        existing_concept_map = self._get_candidate_context(content)

        if use_llm:
            raw_edges = self._extract_edges_pass(content, doc_concept_map, existing_concept_map)
        else:
            block = self._block_extraction(content, course)
            raw_edges = block.edges

        # Build lookup maps for endpoint normalization
        id_to_name: dict[str, str] = {v: k for k, v in doc_concept_map.items()}
        # lossy when two names share one id — acceptable, upstream dedup owns this
        id_to_name.update(existing_concept_map)
        name_to_id: dict[str, str] = dict(doc_concept_map)
        for cid, label in existing_concept_map.items():
            name_to_id.setdefault(label, cid)

        from . import graph_store

        with graph_store.connect() as conn:
            # Write nodes and chunk-level mentions
            for chunk_id, resolved_nodes in chunk_node_lists:
                for node, n_id in resolved_nodes:
                    etype = (
                        node.entity_type.value
                        if hasattr(node.entity_type, "value")
                        else str(node.entity_type)
                    )
                    tax_dict = (
                        node.taxonomy.model_dump()
                        if hasattr(node.taxonomy, "model_dump")
                        else {"domain": course, "subdomain": "Course Notes", "topic": n_id}
                    )

                    if n_id not in self.graph:
                        self.graph.add_node(
                            n_id,
                            id=n_id,
                            label=node.name,
                            entity_type=etype,
                            taxonomy=tax_dict,
                            description=node.description,
                            provenance=[prov_record],
                            aliases=node.aliases if hasattr(node, "aliases") else [],
                        )
                    else:
                        self.graph.nodes[n_id]["taxonomy"] = tax_dict
                        prov_list = self.graph.nodes[n_id].get("provenance", [])
                        if isinstance(prov_list, list):
                            prov_list.append(prov_record)
                            self.graph.nodes[n_id]["provenance"] = prov_list

                    node_data = self.graph.nodes[n_id]
                    graph_store.upsert_node_attrs(
                        conn, n_id,
                        label=node_data.get("label", n_id),
                        entity_type=node_data.get("entity_type", "Concept"),
                        taxonomy=node_data.get("taxonomy", {}),
                        description=node_data.get("description", ""),
                        provenance=node_data.get("provenance", []),
                        aliases=node_data.get("aliases", []),
                    )
                    # Chunk-level chunk_id (Phase 4: was document_id in Phase 3)
                    graph_store.insert_mention(
                        conn,
                        chunk_id=chunk_id,
                        surface_text=node.name,
                        concept_id=n_id,
                    )

            # Write edges (document-level chunk_id for Phase 4)
            for edge in raw_edges:
                src = self._normalize_edge_endpoint(edge.source, id_to_name, name_to_id)
                tgt = self._normalize_edge_endpoint(edge.target, id_to_name, name_to_id)
                if not src or not tgt:
                    continue

                if src not in self.graph:
                    self.graph.add_node(src, id=src, label=edge.source)
                    graph_store.upsert_node_attrs(conn, src, label=edge.source)
                if tgt not in self.graph:
                    self.graph.add_node(tgt, id=tgt, label=edge.target)
                    graph_store.upsert_node_attrs(conn, tgt, label=edge.target)

                rel = edge.relation.value if hasattr(edge.relation, "value") else str(edge.relation)
                src, tgt, rel = _normalize_relation(src, tgt, rel)
                self.graph.add_edge(src, tgt, relation=rel, label=rel)
                graph_store.insert_edge(
                    conn,
                    source_id=src,
                    target_id=tgt,
                    relation=rel,
                    chunk_id=document_id,
                    quote=edge.description,
                    origin="extracted",
                )

    # ------------------------------------------------------------------
    # Full index build
    # ------------------------------------------------------------------

    def build_or_update_index(self, use_llm: bool = False, force: bool = False) -> nx.DiGraph:
        """Processes new or modified Markdown files in the vault and updates graph."""
        notes = self.vault_manager.get_all_notes()
        modified = notes if force else [n for n in notes if self.vault_manager.is_file_modified(n)]

        if not modified:
            log.info("Vault graph is up-to-date.")
            return self.graph

        log.info(f"Indexing {len(modified)} notes (2-Pass, use_llm={use_llm}, force={force})...")
        for note in modified:
            log.info(f"Extracting from: {note.name}")
            self.index_note(note, use_llm=use_llm)
            self.vault_manager.update_file_hash(note)

        self.vault_manager.save_state()
        self.save_graph()
        return self.graph
