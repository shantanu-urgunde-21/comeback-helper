import json
import re
from pathlib import Path
from typing import Optional, List

import networkx as nx
from google.genai import types

from src.config import get_settings
from src.graph.schema import (
    MathNodeExtraction,
    MathEdgeExtraction,
    MathEntityExtraction,
    GraphNode,
    GraphEdge,
    ConceptTaxonomy,
    Provenance,
)
from src.llm.gemini import get_gemini_client, get_gemini_model_name, get_gemini_candidate_models
from src.llm.ollama import get_ollama_client
from src.logger import log
from src.vault.manager import ObsidianVaultManager


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
TASK: Establish directional relationships between the newly extracted concepts from this note AND existing knowledge base concepts.

NEW CONCEPTS IN THIS NOTE:
{new_concepts}

EXISTING KNOWLEDGE BASE CONCEPTS:
{existing_concepts}

STRICT RULES:
1. Create directed edges connecting new concepts to existing concepts or among new concepts.
2. Valid relation types: DEPENDS_ON, USES_DEFINITION, PROVES, COROLLARY_OF, USES_AXIOM, USES_LEMMA.
3. DEPENDS_ON(A, B) means A requires B — B is the more foundational concept. Always phrase the dependency this way; do not emit an inverse "is a prerequisite for" edge.
4. Provide evidence quotes where applicable.

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
    ):
        self.settings = get_settings()
        self.storage_path = storage_path or self.settings.storage_path
        self.vault_path = vault_path or self.settings.vault_path

        self.graph_file = self.storage_path / "graph.json"
        self.graph = self._load_graph()
        self.vault_manager = ObsidianVaultManager(
            vault_path=self.vault_path,
            state_file_path=self.storage_path / "vault_state.json",
        )

        self._vector_store = vector_store
        log.info("MathGraphIndexer initialized (2-Pass Architecture).")

    # ------------------------------------------------------------------
    # Graph I/O
    # ------------------------------------------------------------------

    def _load_graph(self) -> nx.DiGraph:
        """Loads NetworkX graph from .storage/graph.json if it exists."""
        G = nx.DiGraph()
        if self.graph_file.exists():
            try:
                data = json.loads(self.graph_file.read_text(encoding="utf-8"))
                for node in data.get("nodes", []):
                    G.add_node(node["id"], **node)
                for edge in data.get("edges", []):
                    relation = edge.get("relation", "DEPENDS_ON")
                    if relation == "CONTAINS":
                        # Legacy note->concept membership edge. The same fact
                        # already lives in each concept node's `provenance`
                        # list, so this edge type is retired rather than kept
                        # in sync in two places.
                        continue
                    src, tgt, relation = _normalize_relation(
                        edge["source"], edge["target"], relation
                    )
                    G.add_edge(src, tgt, relation=relation)
                log.info(
                    f"Loaded existing graph ({G.number_of_nodes()} nodes, "
                    f"{G.number_of_edges()} edges)"
                )
            except Exception as e:
                log.warning(f"Failed to load graph.json ({e}), starting empty.")
        return G

    def clear_graph(self):
        """Clears in-memory graph, graph.json, and state tracker."""
        self.graph.clear()
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
        """Saves NetworkX graph to graph.json."""
        data = {
            "nodes": [
                {
                    "id": n,
                    "label": n,
                    "type": self.graph.nodes[n].get("entity_type", "Concept"),
                    "description": self.graph.nodes[n].get("description", ""),
                    "taxonomy": self.graph.nodes[n].get(
                        "taxonomy",
                        {"domain": "General Math", "subdomain": "General", "topic": n},
                    ),
                    "provenance": self.graph.nodes[n].get("provenance", []),
                    "aliases": self.graph.nodes[n].get("aliases", []),
                }
                for n in self.graph.nodes
            ],
            "edges": [
                {
                    "from": u,
                    "to": v,
                    "source": u,
                    "target": v,
                    "relation": d.get("relation", "DEPENDS_ON"),
                    "label": d.get("relation", "DEPENDS_ON"),
                }
                for u, v, d in self.graph.edges(data=True)
            ],
        }
        self.graph_file.parent.mkdir(parents=True, exist_ok=True)
        self.graph_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        log.info(
            f"Saved graph ({len(data['nodes'])} nodes, {len(data['edges'])} edges)"
        )

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
        self, text: str, new_nodes: List[GraphNode]
    ) -> List[GraphEdge]:
        """Executes Pass 2 (Relationship & Edge Linker) via Gemini or Ollama."""
        if not new_nodes:
            return []

        new_concept_names = [n.name for n in new_nodes]
        existing_candidates = self._get_candidate_context(text)

        client = get_gemini_client()
        if client:
            prompt = PASS2_EDGE_PROMPT.format(
                new_concepts=json.dumps(new_concept_names),
                existing_concepts=json.dumps(existing_candidates),
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
                    new_concepts=json.dumps(new_concept_names),
                    existing_concepts=json.dumps(existing_candidates),
                    text=text[:3000],
                )
                prompt += (
                    "\n\nRespond ONLY with valid JSON matching:\n"
                    '{"edges": [{"source": "...", "target": "...", "relation": "DEPENDS_ON|USES_DEFINITION|PROVES|COROLLARY_OF"}]}'
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

    def _get_candidate_context(self, text: str) -> List[str]:
        """Retrieves existing concept names for Pass 2 relationship linking."""
        candidates: set[str] = set()
        if self._vector_store is not None:
            try:
                summary = text[:500]
                results = self._vector_store.search_similar(summary, top_k=20)
                for r in results:
                    source = r.get("source", "")
                    if source and source != "init.md":
                        candidates.add(source)
            except Exception:
                pass

        for n in list(self.graph.nodes)[:30]:
            candidates.add(n)

        return list(candidates)[:25]

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
        extracted_edges = self._extract_edges_pass(text, valid_nodes)

        return MathEntityExtraction(nodes=valid_nodes, edges=extracted_edges)

    # ------------------------------------------------------------------
    # Entity Resolution (deduplication)
    # ------------------------------------------------------------------

    # Below this similarity, two names are not considered the same entity.
    # Raised from 0.88: at that threshold names embedded alone routinely
    # merged entities that share a word but not a meaning (e.g. "normal
    # subgroup" and "normal operator"). Literature on LLM-judged entity
    # matching puts the reliable tier at >=0.9 even for description-rich
    # comparisons; 0.93 leaves margin above that given this is name+
    # description similarity from a general-purpose embedding model, not a
    # matcher tuned for the task.
    ENTITY_MERGE_THRESHOLD = 0.93

    def _resolve_entity(self, name: str, description: str = "") -> str:
        """Merges entity synonyms above ENTITY_MERGE_THRESHOLD cosine similarity.

        Compares `name: description`, not the bare name, against each existing
        node's own stored `name: description` — two entities that share a name
        but mean different things (different descriptions) should not merge
        just because the name matches. When no description is available (e.g.
        resolving a bare edge endpoint), falls back to name-only comparison,
        which is a weaker signal and more conservative merging is expected.
        """
        if not self._vector_store or self.graph.number_of_nodes() == 0:
            return name

        try:
            query_text = f"{name}: {description}" if description else name
            new_emb = self._vector_store.embed_texts([query_text])[0]
            import numpy as np
            q = np.array(new_emb)

            best_match = None
            best_sim = 0.0

            for existing_node in self.graph.nodes:
                existing_desc = self.graph.nodes[existing_node].get("description", "")
                existing_text = f"{existing_node}: {existing_desc}" if existing_desc else existing_node
                existing_emb = self._vector_store.embed_texts([existing_text])[0]
                e = np.array(existing_emb)
                sim = float(np.dot(q, e) / (np.linalg.norm(q) * np.linalg.norm(e) + 1e-9))
                if sim > best_sim:
                    best_sim = sim
                    best_match = existing_node

            if best_match and best_sim > self.ENTITY_MERGE_THRESHOLD and best_match != name:
                log.info(f"Entity resolution: '{name}' → '{best_match}' (sim={best_sim:.3f})")
                aliases = self.graph.nodes[best_match].get("aliases", [])
                if name not in aliases:
                    aliases.append(name)
                    self.graph.nodes[best_match]["aliases"] = aliases
                return best_match
        except Exception:
            pass

        return name

    # ------------------------------------------------------------------
    # Note indexing
    # ------------------------------------------------------------------

    def index_note(self, note_path: Path, use_llm: bool = False):
        """Indexes a single Markdown file into the NetworkX graph.

        The note itself is not added as a graph node. Which note a concept
        came from is already captured by that concept's own `provenance`
        list; a separate Note node plus a CONTAINS edge to every concept it
        mentions was the same fact stored twice, and in practice it dominated
        the graph (note titles were consistently the highest-degree nodes,
        and CONTAINS was roughly half of all edges).
        """
        content = note_path.read_text(encoding="utf-8")
        course = note_path.parent.name if note_path.parent != self.vault_path else "General"
        main_node = note_path.stem

        prov_record = Provenance(
            doc_id=main_node,
            doc_title=f"{main_node}.md",
            doc_path=str(note_path),
            exact_quote=content[:200].replace("\n", " "),
        ).model_dump()

        extraction = self.extract_from_text(content, use_llm=use_llm, course_domain=course)

        for node in extraction.nodes:
            n_id = self._resolve_entity(node.id or node.name, description=node.description)
            etype = node.entity_type.value if hasattr(node.entity_type, "value") else str(node.entity_type)
            tax_dict = node.taxonomy.model_dump() if hasattr(node.taxonomy, "model_dump") else {"domain": course, "subdomain": "Course Notes", "topic": n_id}

            if n_id not in self.graph:
                self.graph.add_node(
                    n_id,
                    id=n_id,
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

        for edge in extraction.edges:
            src = self._resolve_entity(edge.source) if self._vector_store else edge.source
            tgt = self._resolve_entity(edge.target) if self._vector_store else edge.target
            rel = edge.relation.value if hasattr(edge.relation, "value") else str(edge.relation)
            src, tgt, rel = _normalize_relation(src, tgt, rel)
            self.graph.add_edge(src, tgt, relation=rel, label=rel)

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
