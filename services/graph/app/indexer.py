import re
from pathlib import Path
from typing import Optional

import networkx as nx

from shared.config import get_settings
from .schema import (
    MathEntityExtraction,
    Provenance,
    normalize,
    SYMMETRIC_RELATIONS,
)
from shared.logger import log
from .dag import repair_graph_dag, resolve_2cycle
from .extraction_filters import is_valid_entity
from .block_extractor import block_extraction
from .llm_extraction import extract_nodes_pass, extract_edges_pass


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


class MathGraphIndexer:
    """
    Indexes mathematical Markdown notes into a NetworkX Property Graph.

    Uses a decoupled 2-Pass extraction architecture (see `llm_extraction.py`):
      Pass 1: Concept & SKOS Taxonomy Extractor (LLM Call #1)
      Pass 2: Relationship & Prerequisite Linker (LLM Call #2)

    Fallback hierarchy: Gemini API → Local Ollama LLM → Deterministic Block
    Parser (`block_extractor.py`).
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
            return block_extraction(text, course_domain)

        # Pass 1: Extract concept nodes
        extracted_nodes, _ = extract_nodes_pass(text, course_domain)

        # Fallback to block extractor if LLM node extraction returned nothing
        if not extracted_nodes:
            return block_extraction(text, course_domain)

        # Filter extracted nodes through noise validator
        valid_nodes = [n for n in extracted_nodes if is_valid_entity(n.name)]

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
        extracted_edges, _ = extract_edges_pass(text, doc_concept_map, existing_concept_map, node_types)

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
                raw_nodes, method = extract_nodes_pass(chunk_text, course)
                chunk_nodes = [n for n in raw_nodes if is_valid_entity(n.name)]
                if not chunk_nodes:
                    block = block_extraction(chunk_text, course)
                    chunk_nodes = [n for n in block.nodes if is_valid_entity(n.name)]
                    method = "block_parser"
            else:
                block = block_extraction(chunk_text, course)
                chunk_nodes = [n for n in block.nodes if is_valid_entity(n.name)]
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
            raw_edges, edge_method = extract_edges_pass(content, doc_concept_map, existing_concept_map, node_types)
        else:
            block = block_extraction(content, course)
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
        from . import graph_store

        stats = repair_graph_dag(self.graph)
        with graph_store.connect() as conn:
            graph_store.sync_edges_from_graph(conn, self.graph)
        self.save_graph()
        log.info(f"DAG repair complete: {stats}")
        return stats
