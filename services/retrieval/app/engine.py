from typing import Optional

import numpy as np
from google.genai import types as genai_types

from shared.config import get_settings
from shared.llm.fallback import with_gemini_then_ollama
from shared.llm.ollama import get_ollama_client
from shared.logger import log


MATH_QUERY_PROMPT_TEMPLATE = """\
You are a brilliant university mathematics and computer science tutor assisting a student.
Use the provided retrieved context from the student's Obsidian coursework vault (including mathematical theorems, definitions, proofs, formulas, and concept graph connections) to answer their question.

Retrieved Vault Context & Knowledge Graph Connections:
------------------------
{context_str}
------------------------

Question: {query_str}

Instructions:
1. Provide a rigorous, step-by-step explanation with clean LaTeX formulas ($...$ for inline, $$...$$ for block).
2. Explicitly highlight prerequisite concepts or cross-course connections found in the context (e.g. how a Linear Algebra theorem applies to Machine Learning).
3. Be clear, precise, and encouraging. If any proof steps are involved, lay them out logically.
4. If the retrieved context doesn't contain enough information, state that clearly rather than hallucinating.
"""


class MathQueryEngine:
    """
    Hybrid RAG query engine combining LanceDB Vector Similarity
    + Math PropertyGraph Traversal + Gemini / Ollama Synthesis.

    Accepts shared singletons via constructor to avoid creating
    duplicate instances of expensive objects.
    """

    def __init__(
        self,
        graph_indexer=None,
        vector_store=None,
    ):
        """
        Both dependencies are optional — default to the real classes so
        callers that only need one (e.g. tests) don't have to wire up both
        by hand.
        """
        self.settings = get_settings()
        if graph_indexer is None:
            from graph.app.indexer import MathGraphIndexer
            graph_indexer = MathGraphIndexer()
        if vector_store is None:
            from vector.app.store import LocalVectorStore
            vector_store = LocalVectorStore()
        self.indexer = graph_indexer
        self.vector_store = vector_store

        # Pre-compute graph node embeddings, used to find seed concepts for
        # the bounded neighborhood lookup below.
        self._node_embeddings: dict[str, list[float]] = {}
        self._build_node_embeddings()

        log.info("Initialized MathQueryEngine with hybrid vector + graph retrieval (bounded neighborhood).")

    # ------------------------------------------------------------------
    # Graph node embedding index
    # ------------------------------------------------------------------

    def _build_node_embeddings(self):
        """Embed every graph node's label+description for semantic seed matching.

        Node ids are opaque (a Wikidata QID or CUST_<hash> — plan.md Phase 1),
        so the embedded text uses each node's display `label`, not its id.
        """
        graph = self.indexer.graph
        if graph.number_of_nodes() == 0:
            return

        node_ids = list(graph.nodes)
        texts = []
        for nid in node_ids:
            label = graph.nodes[nid].get("label", nid)
            desc = graph.nodes[nid].get("description", "")
            texts.append(f"{label}: {desc}" if desc else label)

        try:
            embeddings = self.vector_store.embed_texts(texts)
            for nid, emb in zip(node_ids, embeddings):
                self._node_embeddings[nid] = emb
            log.info(f"Pre-computed embeddings for {len(node_ids)} graph nodes.")
        except Exception as e:
            log.warning(f"Could not embed graph nodes ({e}).")

    def refresh_node_embeddings(self):
        """Re-build node embeddings (called after graph updates)."""
        self._node_embeddings.clear()
        self._build_node_embeddings()

    def _find_similar_nodes(self, query: str, top_k: int = 3) -> list[str]:
        """Find graph node ids semantically closest to the query."""
        if not self._node_embeddings:
            return []

        try:
            query_emb = self.vector_store.embed_texts([query])[0]
            q = np.array(query_emb)

            scored: list[tuple[str, float]] = []
            for nid, emb in self._node_embeddings.items():
                e = np.array(emb)
                sim = float(
                    np.dot(q, e) / (np.linalg.norm(q) * np.linalg.norm(e) + 1e-9)
                )
                scored.append((nid, sim))

            scored.sort(key=lambda x: x[1], reverse=True)
            return [nid for nid, sim in scored[:top_k] if sim > 0.3]
        except Exception as e:
            log.warning(f"Semantic node matching failed ({e}).")
            return []

    # ------------------------------------------------------------------
    # Context retrieval
    # ------------------------------------------------------------------

    def retrieve_context(
        self,
        prompt: str,
        top_k: int = 5,
        course: Optional[str] = None,
        use_graph: bool = True,
    ) -> str:
        """
        Retrieves top semantic text chunks from LanceDB, plus a bounded
        1-hop neighborhood (via `MathGraphIndexer.neighborhood()`) around the
        graph nodes semantically closest to the prompt.
        """
        # 1. Semantic Vector Search via LanceDB (Hybrid BM25 + Vector)
        vector_results = self.vector_store.search_similar(
            prompt, top_k=top_k, course=course, query_type="hybrid"
        )
        vector_context = []
        for idx, res in enumerate(vector_results, start=1):
            source = res.get("source", "Note")
            text = res.get("text", "")
            course_tag = res.get("course", "")
            vector_context.append(
                f"[Chunk {idx} — {source} ({course_tag})]\n{text}"
            )

        # 2. Bounded Graph Neighborhood: semantic node match, then 1-hop expand
        graph_context = []
        if use_graph:
            try:
                seed_ids = self._find_similar_nodes(prompt, top_k=3)

                if seed_ids:
                    neighborhood = self.indexer.neighborhood(seed_ids, hops=1)
                    nodes = neighborhood.get("nodes", [])
                    edges = neighborhood.get("edges", [])

                    # Format nodes with their descriptions and immediate relations
                    for node in nodes:
                        node_id = node.get("id", "")
                        node_type = node.get("kind", "Concept")
                        label = node.get("label", node_id)
                        desc = node.get("description", "")

                        # Find edges connected to this node
                        rel_info = []
                        for edge in edges:
                            if edge["source"] == node_id:
                                rel = edge.get("relation", "DEPENDS_ON")
                                rel_info.append(f"{label} --[{rel}]--> {edge['target']}")
                            elif edge["target"] == node_id:
                                rel = edge.get("relation", "DEPENDS_ON")
                                rel_info.append(f"{edge['source']} --[{rel}]--> {label}")

                        node_str = f"• [{node_type}] {label}" + (f" — {desc}" if desc else "")
                        if rel_info:
                            node_str += "\n  " + " | ".join(rel_info[:2])
                        graph_context.append(node_str)
            except Exception as e:
                log.warning(f"Graph neighborhood retrieval failed ({e}).")

        # Assemble unified context string
        context_parts = []
        if vector_context:
            context_parts.append(
                "### Semantic Vector Chunks:\n" + "\n\n".join(vector_context)
            )
        if graph_context:
            context_parts.append(
                "### Math PropertyGraph (1-hop neighborhood):\n"
                + "\n".join(graph_context)
            )

        if not context_parts:
            return "No prior context found in vault notes yet."

        return "\n\n".join(context_parts)

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(
        self,
        prompt: str,
        top_k: int = 5,
        temperature: float = 0.3,
        course: Optional[str] = None,
        use_graph: bool = True,
    ) -> str:
        """
        Retrieves hybrid context and synthesizes a math explanation
        using Gemini / Ollama with automatic candidate fallback.
        """
        log.info(
            f"Processing hybrid RAG query: '{prompt}' "
            f"(top_k={top_k}, temp={temperature}, course={course or 'all'}, "
            f"graph={use_graph})"
        )
        context_str = self.retrieve_context(
            prompt, top_k=top_k, course=course, use_graph=use_graph
        )
        log.debug(f"Retrieved hybrid context ({len(context_str)} chars)")

        full_prompt = MATH_QUERY_PROMPT_TEMPLATE.format(
            context_str=context_str,
            query_str=prompt,
        )

        def try_gemini(client, model_name: str) -> str:
            log.info(f"Synthesizing RAG response via Gemini '{model_name}'...")
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=temperature,
                ),
            )
            log.info("RAG response synthesis complete.")
            return response.text

        def try_ollama(model: str) -> "str | None":
            log.info(f"Synthesizing RAG response via local Ollama '{model}'...")
            return get_ollama_client().chat(prompt=full_prompt, model=model, temperature=temperature)

        answer, _ = with_gemini_then_ollama(try_gemini, try_ollama)
        if answer is not None:
            return answer

        return (
            "### Retrieved Vault Context & Graph Connections:\n\n"
            + context_str
            + "\n\n*(Note: Gemini API and local Ollama are currently offline or rate-limited. Answer synthesized from raw vault context above.)*"
        )
