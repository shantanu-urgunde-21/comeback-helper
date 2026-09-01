import json
import re
from pathlib import Path
from typing import Optional, List

import networkx as nx
from google.genai import types

from shared.config import get_settings
from .schema import (
    MathNodeExtraction,
    MathEdgeExtraction,
    MathEntityExtraction,
    MathEntityKind,
    GraphNode,
    GraphEdge,
    ConceptTaxonomy,
    Provenance,
    normalize,
    SYMMETRIC_RELATIONS,
)
from shared.llm.gemini import get_gemini_client, get_gemini_model_name, get_gemini_candidate_models
from shared.llm.ollama import get_ollama_client
from shared.logger import log
from .dag import will_create_cycle, repair_graph_dag, resolve_2cycle


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
    """Canonicalizes relation direction and retired names.

    PREREQUISITE_FOR(A, B) and DEPENDS_ON(B, A) assert the same fact; storing
    both directions between one pair creates an artificial cycle that breaks
    hierarchical layout. DEPENDS_ON is the only stored form.

    USES_LEMMA is the retired name for USES_IN_PROOF — it was in practice
    used for any auxiliary result, not only lemmas (docs/vocabulary-diagnosis.md
    V3), so the rename is also a correction.

    Symmetric relations (SYMMETRIC_RELATIONS) are stored with endpoints
    ordered by id, so an LLM emitting both directions yields one edge, not a
    2-cycle.
    """
    if relation == "PREREQUISITE_FOR":
        return target, source, "DEPENDS_ON"
    if relation == "USES_LEMMA":
        relation = "USES_IN_PROOF"
    if relation in SYMMETRIC_RELATIONS and source > target:
        return target, source, relation
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
You are an expert mathematical entity extractor.
TASK: Extract formal mathematical entities from the text, classify each on TWO
independent axes, and assign a 3-tier SKOS taxonomy.

AXIS 1 — kind (REQUIRED, pick exactly one; this is what the thing IS):
  Object     — a mathematical object, construct, or property (e.g. Wronskian, Integrating Factor, Linear Independence)
  Statement  — a proposition asserted to hold (e.g. Schwarz's Theorem, Criterion for Exactness)
  Definition — text that assigns meaning to a term
  Method     — a procedure or solution technique (e.g. Variation of Parameters, Undetermined Coefficients)
  Formula    — a specific equation or expression (e.g. Abel's Identity)
  Proof      — an argument establishing a statement
  Example    — a concrete instance or model (e.g. a bungee-jumping model)

AXIS 2 — role (OPTIONAL, only when kind is Statement):
  Axiom | Theorem | Lemma | Corollary | Proposition | Conjecture

  CRITICAL: role is REPORTED, NOT INFERRED. Set it ONLY when the text itself
  applies that label — a heading such as "Lemma 3.1", or a name such as
  "Abel's Lemma" or "Picard's Theorem". If the text merely states a result
  without labelling it, OMIT role entirely. Do NOT reason about whether
  something "acts like" a lemma; relationships between results are captured
  as edges, not as this field.

STRICT RULES:
1. DO NOT extract structural terms (e.g. 'Exercise 1', 'Problem', 'Solution', 'Hint', 'Conclusion', 'Page 1', 'Lecture notes').
2. Extract the formal mathematical entity name, properly capitalised.
3. Every node MUST have a `kind`. Do not default to Object when another kind fits — a named result is a Statement, a solution technique is a Method.
4. Each node MUST have a formal 1-2 sentence description.
5. Assign domain taxonomy (domain, subdomain, topic).

TEXT:
{text}
"""

PASS2_EDGE_PROMPT = """\
You are an expert mathematical relationship linker.
TASK: Establish directional relationships between the entities below, using ONLY their IDs.

ENTITY DICTIONARY (id -> name, kind, role):
{concept_id_map}

NEW ENTITY IDS FROM THIS NOTE (focus edges on these):
{new_concept_ids}

EXISTING KNOWLEDGE BASE IDS (available link targets):
{existing_concept_ids}

RELATION TYPES — pick the most specific one that applies. Do NOT fall back to
DEPENDS_ON when a precise relation fits:

  DEPENDS_ON(A, B)       A requires understanding B first. B is more foundational.
                         Use only when no more specific relation below applies.
  HAS_HYPOTHESIS(A, B)   Statement A holds only under condition B.
                         e.g. Picard's Theorem HAS_HYPOTHESIS Lipschitz Condition
  USES_DEFINITION(A, B)  A invokes definition B.
  USES_IN_PROOF(A, B)    A's proof relies on result B.
  PROVES(A, B)           A is an argument establishing statement B.
                         A should be a Proof and B a Statement.
  COROLLARY_OF(A, B)     A follows easily from B.
  GENERALIZES(A, B)      A is a strictly more general form of B.
  SPECIAL_CASE_OF(A, B)  A is B with additional constraints.
  EQUIVALENT_TO(A, B)    A and B are logically equivalent. Emit ONCE, in either order.
  CHARACTERIZES(A, B)    A is an if-and-only-if criterion for property B.
                         e.g. Wronskian Criterion CHARACTERIZES Linear Dependence
  INSTANCE_OF(A, B)      A is a concrete example or model of B.

STRICT RULES:
1. Use ONLY IDs from the ENTITY DICTIONARY as source and target. Never invent an ID.
2. Respect the kinds: do not emit PROVES targeting a Definition; do not emit
   USES_IN_PROOF targeting an Object that is not a result.
3. Never emit an inverse "is a prerequisite for" edge — express it as DEPENDS_ON.
4. Do NOT emit an edge in both directions between the same pair. If the
   relationship is mutual, use EQUIVALENT_TO once.
5. Include the supporting sentence from the text in the description field.

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
        vault_manager=None,
    ):
        """
        `vault_manager` is optional — defaults to a real `ObsidianVaultManager`
        over `vault_path`/`storage_path` so callers that only need read access
        (tests, dry-run extraction) don't have to construct one by hand.
        """
        self.settings = get_settings()
        self.storage_path = storage_path or self.settings.storage_path
        self.vault_path = vault_path or self.settings.vault_path

        self.graph_file = self.storage_path / "graph.json"
        self.graph = self._load_graph()

        if vault_manager is None:
            from vault.app.manager import ObsidianVaultManager
            vault_manager = ObsidianVaultManager(
                vault_path=self.vault_path,
                state_file_path=self.storage_path / "vault_state.json",
            )
        self.vault_manager = vault_manager

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
    ) -> tuple[List[GraphNode], str]:
        """Executes Pass 1 (Node & Taxonomy Extraction) via Gemini or Ollama.

        Returns (nodes, method) — method is "gemini" or "ollama" on success,
        "none" if every tier failed or was unavailable (index_note's caller
        then falls back to the block parser and re-tags the chunk
        "block_parser"). See graph_store.EXTRACTION_METHODS.
        """
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
                    return nodes, "gemini"
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
                    '{"nodes": [{"name": "Concept Name", "kind": "Object|Statement|Definition|Method|Formula|Proof|Example", '
                    '"role": "Theorem|Lemma|Corollary|Axiom|Proposition|Conjecture or omit", '
                    '"description": "formal definition", "taxonomy": {"domain": "...", "subdomain": "...", "topic": "..."}}]}'
                )
                resp = ollama.chat(prompt=prompt, model=model, response_format="json", timeout=60)
                if resp:
                    try:
                        data = json.loads(resp)
                        nodes = MathNodeExtraction(**data).nodes
                        log.info(f"Pass 1 (Ollama {model}): Extracted {len(nodes)} concept nodes.")
                        return nodes, "ollama"
                    except Exception:
                        pass

        return [], "none"

    # ------------------------------------------------------------------
    # Pass 2: Edge & Relationship Extraction
    # ------------------------------------------------------------------

    def _extract_edges_pass(
        self,
        text: str,
        doc_concept_map: dict[str, str],       # surface name -> canonical_id (this document)
        existing_concept_map: dict[str, str],   # canonical_id -> label (existing graph)
        node_types: "dict[str, dict]",          # canonical_id -> {"kind":..., "role":...}
    ) -> "tuple[list[GraphEdge], str]":
        """Executes Pass 2 (Relationship & Edge Linker) via Gemini or Ollama.

        `node_types` is what lets the LLM pick type-appropriate relations —
        without it, Pass 2 was type-blind and emitted USES_LEMMA at theorems
        and PROVES at definitions (docs/vocabulary-diagnosis.md V3).

        Returns (edges, method) — see `_extract_nodes_pass` for the method tag.
        """
        if not doc_concept_map:
            return [], "none"

        # Build the id->name view the prompt exposes to the LLM
        id_to_name: dict[str, str] = {v: k for k, v in doc_concept_map.items()}
        id_to_name.update(existing_concept_map)

        entity_dict = {
            cid: {
                "name": name,
                "kind": node_types.get(cid, {}).get("kind", "Object"),
                "role": node_types.get(cid, {}).get("role"),
            }
            for cid, name in id_to_name.items()
        }

        concept_id_map_json = json.dumps(entity_dict, ensure_ascii=False)
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
                    return edges, "gemini"
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
                    '{"edges": [{"source": "id", "target": "id", "relation": "DEPENDS_ON|HAS_HYPOTHESIS|USES_DEFINITION|USES_IN_PROOF|PROVES|COROLLARY_OF|GENERALIZES|SPECIAL_CASE_OF|EQUIVALENT_TO|CHARACTERIZES|INSTANCE_OF", "description": "evidence quote"}]}'
                )
                resp = ollama.chat(prompt=prompt, model=model, response_format="json", timeout=60)
                if resp:
                    try:
                        data = json.loads(resp)
                        edges = MathEdgeExtraction(**data).edges
                        log.info(f"Pass 2 (Ollama {model}): Linked {len(edges)} relationship edges.")
                        return edges, "ollama"
                    except Exception:
                        pass

        return [], "none"

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

        def _add_node(name: str, kind: str, desc: str = ""):
            clean = name.strip().rstrip(":")
            if clean in node_names or not _is_valid_entity(clean):
                return
            node_names.add(clean)
            nodes.append(
                GraphNode(
                    id=clean,
                    name=clean,
                    kind=kind,
                    taxonomy=ConceptTaxonomy(
                        domain=course_domain,
                        subdomain="Course Notes",
                        topic=clean,
                    ),
                    description=desc or f"{kind}: {clean}",
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
        # Maps LaTeX env names to MathEntityKind values
        _ENV_KIND_MAP = {
            "theorem": MathEntityKind.STATEMENT.value,
            "lemma": MathEntityKind.STATEMENT.value,
            "corollary": MathEntityKind.STATEMENT.value,
            "proposition": MathEntityKind.STATEMENT.value,
            "axiom": MathEntityKind.STATEMENT.value,
            "definition": MathEntityKind.DEFINITION.value,
            "proof": MathEntityKind.PROOF.value,
        }
        for match in env_pattern.finditer(text):
            env_type_raw = match.group(1).lower()
            env_name = match.group(2)
            env_body = match.group(3).strip()[:200]
            env_kind = _ENV_KIND_MAP.get(env_type_raw, MathEntityKind.OBJECT.value)
            if env_name and _is_valid_entity(env_name):
                _add_node(env_name.strip(), env_kind, env_body)

        # 2. Typed Markdown headings: ## Theorem: Cauchy-Schwarz Inequality
        heading_pattern = re.compile(
            r"^#{1,3}\s+"
            r"(?:(Theorem|Definition|Concept|Lemma|Proof|Formula|Proposition|Corollary|Axiom|Method|Example)"
            r"\s*:\s*)"
            r"(.+)$",
            re.MULTILINE | re.IGNORECASE,
        )
        _HEADING_KIND_MAP = {
            "theorem": MathEntityKind.STATEMENT.value,
            "lemma": MathEntityKind.STATEMENT.value,
            "corollary": MathEntityKind.STATEMENT.value,
            "proposition": MathEntityKind.STATEMENT.value,
            "axiom": MathEntityKind.STATEMENT.value,
            "definition": MathEntityKind.DEFINITION.value,
            "proof": MathEntityKind.PROOF.value,
            "formula": MathEntityKind.FORMULA.value,
            "method": MathEntityKind.METHOD.value,
            "example": MathEntityKind.EXAMPLE.value,
            "concept": MathEntityKind.OBJECT.value,
        }
        for match in heading_pattern.finditer(text):
            htype = match.group(1).lower()
            name = match.group(2).strip().rstrip(":")
            h_kind = _HEADING_KIND_MAP.get(htype, MathEntityKind.OBJECT.value)
            _add_node(name, h_kind)

        # 3. Obsidian wikilinks [[Target Concept]]
        wikilinks = re.findall(r"\[\[(.*?)\]\]", text)
        for link in wikilinks:
            link_clean = link.split("|")[0].strip()
            if (
                _is_valid_entity(link_clean)
                and not link_clean.endswith((".png", ".jpg", ".pdf"))
            ):
                _add_node(link_clean, MathEntityKind.OBJECT.value, "Wikilink reference from vault note")
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

    def neighborhood(self, ids: list[str], hops: int = 1) -> dict:
        """N-hop bounded subgraph around the given node ids.

        What retrieval calls instead of walking `.graph` directly, so a
        query only pulls in what it needs rather than the whole graph.
        """
        G = self.graph
        keep: set = set()
        frontier = {i for i in ids if i in G}
        keep |= frontier
        for _ in range(max(hops, 0)):
            nxt: set = set()
            for n in frontier:
                nxt |= set(G.successors(n)) | set(G.predecessors(n))
            nxt -= keep
            keep |= nxt
            frontier = nxt

        return {
            "nodes": [{"id": n, **{k: v for k, v in G.nodes[n].items() if k != "id"}} for n in keep],
            "edges": [{"source": u, "target": v, "relation": d.get("relation", "DEPENDS_ON")}
                      for u, v, d in G.edges(data=True) if u in keep and v in keep],
            "seeds": ids,
        }

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
        extracted_nodes, _ = self._extract_nodes_pass(text, course_domain)

        # Fallback to block extractor if LLM node extraction returned nothing
        if not extracted_nodes:
            return self._block_extraction(text, course_domain)

        # Filter extracted nodes through noise validator
        valid_nodes = [n for n in extracted_nodes if _is_valid_entity(n.name)]

        # Pass 2: Link relationships & edges between nodes
        doc_concept_map = {n.name: (n.id if n.id else n.name) for n in valid_nodes}
        existing_concept_map = self._get_candidate_context(text)
        node_types = {
            (n.id if n.id else n.name): {
                "kind": n.kind.value if hasattr(n.kind, "value") else str(n.kind),
                "role": n.role.value if getattr(n, "role", None) is not None else None,
            }
            for n in valid_nodes
        }
        extracted_edges, _ = self._extract_edges_pass(text, doc_concept_map, existing_concept_map, node_types)

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
        shared word". This needs no vector store at all — the graph package
        has no dependency on the vector package.
        """
        from .authority import resolve_concept
        return resolve_concept(name, document_id=document_id, course=course)

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
        chunk_methods: dict[str, str] = {}  # chunk_id → extraction tier actually used

        for chunk_id, chunk_text in chunks:
            if use_llm:
                raw_nodes, method = self._extract_nodes_pass(chunk_text, course)
                chunk_nodes = [n for n in raw_nodes if _is_valid_entity(n.name)]
                if not chunk_nodes:
                    block = self._block_extraction(chunk_text, course)
                    chunk_nodes = [n for n in block.nodes if _is_valid_entity(n.name)]
                    method = "block_parser"
            else:
                block = self._block_extraction(chunk_text, course)
                chunk_nodes = [n for n in block.nodes if _is_valid_entity(n.name)]
                method = "block_parser"

            chunk_methods[chunk_id] = method
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
            # Build node_types from the resolved node attributes for type-aware relation selection
            node_types: dict[str, dict] = {}
            for _, resolved in chunk_node_lists:
                for node, n_id in resolved:
                    if n_id in self.graph:
                        node_types[n_id] = {
                            "kind": self.graph.nodes[n_id].get("kind", "Object"),
                            "role": self.graph.nodes[n_id].get("role"),
                        }
            # Also include existing concepts' types
            for cid in existing_concept_map:
                if cid in self.graph and cid not in node_types:
                    node_types[cid] = {
                        "kind": self.graph.nodes[cid].get("kind", "Object"),
                        "role": self.graph.nodes[cid].get("role"),
                    }
            raw_edges, edge_method = self._extract_edges_pass(content, doc_concept_map, existing_concept_map, node_types)
        else:
            block = self._block_extraction(content, course)
            raw_edges = block.edges
            edge_method = "block_parser"

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
                chunk_method = chunk_methods.get(chunk_id)
                for node, n_id in resolved_nodes:
                    kind = node.kind.value if hasattr(node.kind, "value") else str(node.kind)
                    role = node.role.value if getattr(node, "role", None) is not None else None
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
                            kind=kind,
                            role=role,
                            taxonomy=tax_dict,
                            description=node.description,
                            provenance=[prov_record],
                            aliases=node.aliases if hasattr(node, "aliases") else [],
                            extraction_method=chunk_method,
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
                        kind=node_data.get("kind", "Object"),
                        role=node_data.get("role"),
                        taxonomy=node_data.get("taxonomy", {}),
                        description=node_data.get("description", ""),
                        provenance=node_data.get("provenance", []),
                        aliases=node_data.get("aliases", []),
                        extraction_method=node_data.get("extraction_method"),
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
                if src == tgt:
                    continue

                if rel != "EQUIVALENT_TO" and self.graph.has_edge(tgt, src):
                    # 2-cycle conflict: same rule the batch repair pass uses (dag.break_2cycles).
                    existing_rel = self.graph.get_edge_data(tgt, src, {}).get("relation", "DEPENDS_ON")
                    outcome = resolve_2cycle(rel, existing_rel)
                    if outcome == "keep_forward":
                        self.graph.remove_edge(tgt, src)
                        graph_store.delete_edge(conn, tgt, src)
                        self.graph.add_edge(src, tgt, relation=rel, label=rel, extraction_method=edge_method)
                        graph_store.insert_edge(
                            conn,
                            source_id=src,
                            target_id=tgt,
                            relation=rel,
                            chunk_id=document_id,
                            quote=edge.description,
                            origin="extracted",
                            extraction_method=edge_method,
                        )
                        log.info(f"DAG: Replaced weaker reverse edge {tgt} -> {src} with {src} -[{rel}]-> {tgt}")
                    elif outcome == "equivalent":
                        # Mutual / equivalent concepts: convert to EQUIVALENT_TO
                        self.graph.remove_edge(tgt, src)
                        graph_store.delete_edge(conn, tgt, src)
                        canon_u, canon_v = sorted([src, tgt])
                        self.graph.add_edge(canon_u, canon_v, relation="EQUIVALENT_TO", label="EQUIVALENT_TO", extraction_method=edge_method)
                        graph_store.insert_edge(
                            conn,
                            source_id=canon_u,
                            target_id=canon_v,
                            relation="EQUIVALENT_TO",
                            chunk_id=document_id,
                            quote=edge.description,
                            origin="extracted",
                            extraction_method=edge_method,
                        )
                        log.info(f"DAG: Converted mutual 2-cycle between {src} and {tgt} into EQUIVALENT_TO")
                    else:
                        log.info(f"DAG: Kept stronger existing edge {tgt} -[{existing_rel}]-> {src} over {src} -[{rel}]-> {tgt}")
                else:
                    self.graph.add_edge(src, tgt, relation=rel, label=rel, extraction_method=edge_method)
                    graph_store.insert_edge(
                        conn,
                        source_id=src,
                        target_id=tgt,
                        relation=rel,
                        chunk_id=document_id,
                        quote=edge.description,
                        origin="extracted",
                        extraction_method=edge_method,
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

        repair_stats = repair_graph_dag(self.graph)
        log.info(f"Post-index DAG repair complete: {repair_stats}")
        from . import graph_store
        with graph_store.connect() as conn:
            graph_store.sync_edges_from_graph(conn, self.graph)

        self.vault_manager.save_state()
        self.save_graph()
        return self.graph

    def repair_dag(self) -> dict:
        """Enforces DAG property on the in-memory graph and syncs SQLite store."""
        from .dag import repair_graph_dag
        from . import graph_store

        stats = repair_graph_dag(self.graph)
        with graph_store.connect() as conn:
            graph_store.sync_edges_from_graph(conn, self.graph)
        self.save_graph()
        log.info(f"DAG repair complete: {stats}")
        return stats
