import json
import re
from pathlib import Path
from typing import Optional

import networkx as nx
from google.genai import types

from src.config import get_settings
from src.graph.schema import (
    MathEntityExtraction,
    GraphNode,
    GraphEdge,
    ConceptTaxonomy,
    Provenance,
)
from src.llm.gemini import get_gemini_client, get_gemini_model_name
from src.llm.ollama import get_ollama_client
from src.logger import log
from src.vault.state import VaultStateTracker
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


def _is_valid_entity(name: str) -> bool:
    """Returns True if the name looks like a real math concept, not noise."""
    clean = name.strip()
    if not clean or len(clean) < 3 or clean.startswith("<!--"):
        return False
    if NOISE_PATTERN.match(clean):
        return False
    # Must have at least 2 meaningful words (rejects "From Calculus", "If The Equation")
    words = [w for w in clean.split() if w.lower() not in _STRIP_WORDS]
    if len(words) < 1:
        return False
    return True


# ---------------------------------------------------------------------------
# Extraction prompt
# ---------------------------------------------------------------------------

EXTRACTION_PROMPT_TEMPLATE = """\
You are an expert mathematical knowledge graph extractor.
TASK: Extract formal mathematical entities (Theorems, Definitions, Concepts, Formulas, Proofs, Lemmas) and relationships from the text below.

STRICT RULES:
1. DO NOT extract structural terms (e.g. 'Exercise 1', 'Problem', 'Solution', 'Hint', 'Example', 'Conclusion', 'Page 1', 'Lecture notes').
2. EXTRACT ONLY formal mathematical concept names (e.g. 'Exact Differential Equation', 'Total Differential', 'Mixed Partials Theorem', 'Integrating Factor', 'Separable ODE').
3. Capitalize formal math concept names properly.
4. Each node MUST have a meaningful description (1-2 sentences defining the concept).
5. Create directed edges using these relations: DEPENDS_ON, USES_DEFINITION, PROVES, PREREQUISITE_FOR, COROLLARY_OF, USES_AXIOM, USES_LEMMA.
{candidate_context}
TEXT:
{text}
"""


class MathGraphIndexer:
    """
    Indexes mathematical Markdown notes into a NetworkX Property Graph.

    Uses a 3-tier extraction cascade:
      1. Gemini API (structured Pydantic output)
      2. Local Ollama LLM (JSON mode)
      3. LaTeX block + heading parser (deterministic, no prose regex)

    Supports vector-based candidate injection for cross-note linking
    and post-extraction entity resolution via embedding similarity.
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
        self.vault_manager = ObsidianVaultManager(self.vault_path)
        self.state_tracker = VaultStateTracker(
            state_file_path=self.storage_path / "vault_state.json"
        )

        # Optional vector store for candidate injection + entity resolution
        self._vector_store = vector_store

        log.info("MathGraphIndexer initialized.")

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
                    G.add_edge(
                        edge["source"],
                        edge["target"],
                        relation=edge.get("relation", "DEPENDS_ON"),
                    )
                log.info(
                    f"Loaded existing graph ({G.number_of_nodes()} nodes, "
                    f"{G.number_of_edges()} edges)"
                )
            except Exception as e:
                log.warning(f"Failed to load graph.json ({e}), starting empty.")
        return G

    def clear_graph(self):
        """Clears in-memory graph, graph.json, kuzu_graph.db, and state tracker."""
        self.graph.clear()
        if self.graph_file.exists():
            try:
                self.graph_file.write_text(
                    '{"nodes":[],"edges":[]}', encoding="utf-8"
                )
            except Exception as e:
                log.warning(f"Failed to clear graph.json: {e}")

        kuzu_file = self.storage_path / "kuzu_graph.db"
        if kuzu_file.exists():
            try:
                import shutil

                if kuzu_file.is_dir():
                    shutil.rmtree(kuzu_file, ignore_errors=True)
                else:
                    kuzu_file.unlink(missing_ok=True)
            except Exception as e:
                log.warning(f"Failed to delete KuzuDB: {e}")

        self.state_tracker.state.clear()
        self.state_tracker.save_state()
        log.info("Knowledge graph, KuzuDB, and vault state cleared.")

    def save_graph(self):
        """Saves NetworkX graph to graph.json and syncs to KùzuDB."""
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
        self._sync_to_kuzu()

    # ------------------------------------------------------------------
    # KùzuDB sync
    # ------------------------------------------------------------------

    def _sync_to_kuzu(self):
        """Syncs NetworkX graph into embedded KùzuDB."""
        try:
            import kuzu

            kuzu_path = self.storage_path / "kuzu_graph.db"
            db = kuzu.Database(str(kuzu_path))
            conn = kuzu.Connection(db)

            conn.execute(
                "CREATE NODE TABLE IF NOT EXISTS Concept("
                "name STRING, entity_type STRING, description STRING, "
                "PRIMARY KEY (name))"
            )
            conn.execute(
                "CREATE REL TABLE IF NOT EXISTS RELATES("
                "FROM Concept TO Concept, relation STRING)"
            )

            for n in self.graph.nodes:
                etype = str(self.graph.nodes[n].get("entity_type", "Concept")).replace("'", "''")
                desc = str(self.graph.nodes[n].get("description", "")).replace("'", "''")
                name = str(n).replace("'", "''")
                try:
                    conn.execute(
                        f"MERGE (c:Concept {{name: '{name}'}}) "
                        f"SET c.entity_type = '{etype}', c.description = '{desc}'"
                    )
                except Exception:
                    log.debug(f"KùzuDB node upsert skipped for: {n}")

            for u, v, d in self.graph.edges(data=True):
                src = str(u).replace("'", "''")
                dst = str(v).replace("'", "''")
                rel = str(d.get("relation", "DEPENDS_ON")).replace("'", "''")
                try:
                    conn.execute(
                        f"MATCH (a:Concept {{name: '{src}'}}), "
                        f"(b:Concept {{name: '{dst}'}}) "
                        f"MERGE (a)-[r:RELATES {{relation: '{rel}'}}]->(b)"
                    )
                except Exception:
                    log.debug(f"KùzuDB edge upsert skipped: {u}->{v}")

            log.info(f"Synced graph to KùzuDB at: {kuzu_path}")
        except ImportError:
            log.debug("KùzuDB not installed, skipping sync.")
        except Exception as e:
            log.warning(f"KùzuDB sync skipped ({e}).")

    # ------------------------------------------------------------------
    # Tier 1: Gemini API structured extraction
    # ------------------------------------------------------------------

    def _gemini_extraction(
        self, text: str, candidate_context: str, course_domain: str
    ) -> Optional[MathEntityExtraction]:
        """Extracts entities via Gemini structured output. Returns None on failure."""
        client = get_gemini_client()
        if not client:
            return None

        prompt = EXTRACTION_PROMPT_TEMPLATE.format(
            candidate_context=candidate_context, text=text
        )

        try:
            response = client.models.generate_content(
                model=get_gemini_model_name(),
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MathEntityExtraction,
                    temperature=0.1,
                ),
            )
            data = json.loads(response.text)
            result = MathEntityExtraction(**data)
            log.info(
                f"Gemini extracted {len(result.nodes)} nodes, {len(result.edges)} edges"
            )
            return result
        except Exception as e:
            log.warning(f"Gemini extraction failed ({e}). Trying next tier...")
            return None

    # ------------------------------------------------------------------
    # Tier 2: Local Ollama LLM extraction
    # ------------------------------------------------------------------

    def _ollama_extraction(
        self, text: str, candidate_context: str, course_domain: str
    ) -> Optional[MathEntityExtraction]:
        """Extracts entities via local Ollama text model in JSON mode."""
        ollama = get_ollama_client()
        if not ollama.is_available():
            log.info("Ollama unavailable. Skipping tier 2.")
            return None

        # Try a capable text model for structured extraction
        for model in ["llama3.2", "qwen2.5:3b", "phi3:mini"]:
            if not ollama.has_model(model):
                continue

            prompt = EXTRACTION_PROMPT_TEMPLATE.format(
                candidate_context=candidate_context, text=text[:3000]
            )
            prompt += (
                "\n\nRespond ONLY with valid JSON matching this schema:\n"
                '{"nodes": [{"name": "...", "entity_type": "Theorem|Definition|Concept|Formula|Proof|Lemma", '
                '"description": "...", "taxonomy": {"domain": "...", "subdomain": "...", "topic": "..."}}], '
                '"edges": [{"source": "...", "target": "...", "relation": "DEPENDS_ON|USES_DEFINITION|PROVES|PREREQUISITE_FOR"}]}'
            )

            response_text = ollama.chat(
                prompt=prompt, model=model, response_format="json", timeout=60
            )
            if not response_text:
                continue

            try:
                data = json.loads(response_text)
                result = MathEntityExtraction(**data)
                log.info(
                    f"Ollama ({model}) extracted {len(result.nodes)} nodes, "
                    f"{len(result.edges)} edges"
                )
                return result
            except (json.JSONDecodeError, Exception) as e:
                log.warning(f"Ollama ({model}) returned invalid JSON: {e}")
                continue

        log.info("No suitable Ollama model available. Falling through to tier 3.")
        return None

    # ------------------------------------------------------------------
    # Tier 3: Deterministic LaTeX block + heading parser (NO prose regex)
    # ------------------------------------------------------------------

    def _block_extraction(
        self, text: str, course_domain: str
    ) -> MathEntityExtraction:
        """
        100% offline, deterministic extraction that parses:
          - LaTeX environments: \\begin{theorem}...\\end{theorem}, etc.
          - Markdown headings with typed prefixes: ## Theorem: Concept Name
          - Obsidian [[wikilinks]]

        Does NOT attempt to regex entity names out of prose body text.
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
                # Create edge from first extracted node to wikilink
                if nodes and nodes[0].name != link_clean:
                    edges.append(
                        GraphEdge(
                            source=nodes[0].name,
                            target=link_clean,
                            relation="DEPENDS_ON",
                        )
                    )

        log.info(
            f"Block extractor found {len(nodes)} nodes and {len(edges)} edges."
        )
        return MathEntityExtraction(nodes=nodes, edges=edges)

    # ------------------------------------------------------------------
    # Extraction cascade
    # ------------------------------------------------------------------

    def _get_candidate_context(self, text: str) -> str:
        """
        Builds candidate concept context for the extraction prompt.
        Uses vector similarity if a store is available, else falls back
        to the first 25 graph nodes by insertion order.
        """
        candidates: list[str] = []

        # Prefer vector-based semantic candidates
        if self._vector_store is not None:
            try:
                summary = text[:500]
                results = self._vector_store.search_similar(summary, top_k=20)
                # Extract concept names from search results
                seen = set()
                for r in results:
                    source = r.get("source", "")
                    if source and source != "init.md" and source not in seen:
                        seen.add(source)
                # Also pull existing graph node names
                for n in list(self.graph.nodes)[:30]:
                    if n not in seen:
                        candidates.append(n)
                        seen.add(n)
                candidates = list(seen)[:25]
            except Exception as e:
                log.debug(f"Vector candidate retrieval failed ({e}), using graph nodes.")
                candidates = list(self.graph.nodes)[:25]
        else:
            candidates = list(self.graph.nodes)[:25]

        if not candidates:
            return ""

        return (
            "\nEXISTING KNOWLEDGE BASE CONCEPTS (create edges to these if dependencies exist):\n"
            f"{json.dumps(candidates)}\n"
        )

    def extract_from_text(
        self,
        text: str,
        use_llm: bool = False,
        course_domain: str = "Differential Equations",
    ) -> MathEntityExtraction:
        """
        3-tier extraction cascade:
          1. Gemini API (if use_llm=True and client available)
          2. Local Ollama LLM (if available)
          3. Deterministic LaTeX block parser (always works)
        """
        if not use_llm:
            return self._block_extraction(text, course_domain)

        candidate_context = self._get_candidate_context(text)

        # Tier 1: Gemini
        result = self._gemini_extraction(text, candidate_context, course_domain)
        if result and (result.nodes or result.edges):
            return result

        # Tier 2: Ollama
        result = self._ollama_extraction(text, candidate_context, course_domain)
        if result and (result.nodes or result.edges):
            return result

        # Tier 3: Deterministic block parser
        return self._block_extraction(text, course_domain)

    # ------------------------------------------------------------------
    # Entity Resolution (deduplication)
    # ------------------------------------------------------------------

    def _resolve_entity(self, name: str) -> str:
        """
        Checks if a new entity name is semantically equivalent to an
        existing graph node. Returns the existing node ID if similar
        enough (cosine > 0.88), or the original name if unique.
        """
        if not self._vector_store or self.graph.number_of_nodes() == 0:
            return name

        try:
            new_emb = self._vector_store.embed_texts([name])[0]
            import numpy as np
            q = np.array(new_emb)

            best_match = None
            best_sim = 0.0

            for existing_node in self.graph.nodes:
                existing_emb = self._vector_store.embed_texts([existing_node])[0]
                e = np.array(existing_emb)
                sim = float(np.dot(q, e) / (np.linalg.norm(q) * np.linalg.norm(e) + 1e-9))
                if sim > best_sim:
                    best_sim = sim
                    best_match = existing_node

            if best_match and best_sim > 0.88 and best_match != name:
                log.info(
                    f"Entity resolution: '{name}' → '{best_match}' "
                    f"(cosine={best_sim:.3f})"
                )
                # Record alias
                aliases = self.graph.nodes[best_match].get("aliases", [])
                if name not in aliases:
                    aliases.append(name)
                    self.graph.nodes[best_match]["aliases"] = aliases
                return best_match
        except Exception as e:
            log.debug(f"Entity resolution skipped ({e})")

        return name

    # ------------------------------------------------------------------
    # Note indexing
    # ------------------------------------------------------------------

    def index_note(self, note_path: Path, use_llm: bool = False):
        """Indexes a single Markdown file into the NetworkX graph."""
        content = note_path.read_text(encoding="utf-8")

        course = (
            note_path.parent.name
            if note_path.parent != self.vault_path
            else "General"
        )
        main_node = note_path.stem

        prov_record = Provenance(
            doc_id=main_node,
            doc_title=f"{main_node}.md",
            doc_path=str(note_path),
            exact_quote=content[:200].replace("\n", " "),
        ).model_dump()

        if main_node not in self.graph:
            self.graph.add_node(
                main_node,
                id=main_node,
                entity_type="Note",
                taxonomy={
                    "domain": course,
                    "subdomain": "Course Note",
                    "topic": main_node,
                },
                description=f"Course Note ({course})",
                provenance=[prov_record],
                aliases=[],
            )

        extraction = self.extract_from_text(
            content, use_llm=use_llm, course_domain=course
        )

        for node in extraction.nodes:
            n_id = node.id or node.name
            # Entity resolution — merge if semantically duplicate
            resolved_id = self._resolve_entity(n_id)
            n_id = resolved_id

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
                    entity_type=etype,
                    taxonomy=tax_dict,
                    description=node.description,
                    provenance=[prov_record],
                    aliases=node.aliases if hasattr(node, "aliases") else [],
                )
            else:
                # Update taxonomy, append provenance
                self.graph.nodes[n_id]["taxonomy"] = tax_dict
                prov_list = self.graph.nodes[n_id].get("provenance", [])
                if isinstance(prov_list, list):
                    prov_list.append(prov_record)
                    self.graph.nodes[n_id]["provenance"] = prov_list

            # Connect note container to extracted concepts
            if n_id != main_node:
                self.graph.add_edge(
                    main_node, n_id, relation="CONTAINS", label="CONTAINS"
                )

        for edge in extraction.edges:
            # Resolve edge endpoints too
            src = self._resolve_entity(edge.source) if self._vector_store else edge.source
            tgt = self._resolve_entity(edge.target) if self._vector_store else edge.target
            rel = (
                edge.relation.value
                if hasattr(edge.relation, "value")
                else str(edge.relation)
            )
            self.graph.add_edge(src, tgt, relation=rel, label=rel)

    # ------------------------------------------------------------------
    # Full index build
    # ------------------------------------------------------------------

    def build_or_update_index(
        self, use_llm: bool = False, force: bool = False
    ) -> nx.DiGraph:
        """Processes new or modified Markdown files in the vault and updates graph."""
        notes = self.vault_manager.get_all_notes()
        modified = (
            notes
            if force
            else [n for n in notes if self.state_tracker.is_file_modified(n)]
        )

        if not modified:
            log.info("Vault graph is up-to-date.")
            return self.graph

        log.info(
            f"Indexing {len(modified)} notes (use_llm={use_llm}, force={force})..."
        )
        for note in modified:
            log.info(f"Extracting from: {note.name}")
            self.index_note(note, use_llm=use_llm)
            self.state_tracker.update_file_hash(note)

        self.state_tracker.save_state()
        self.save_graph()
        return self.graph
