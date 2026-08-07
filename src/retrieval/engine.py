import numpy as np
from typing import Optional

from google import genai
from google.genai import types as genai_types

from src.config import get_settings
from src.graph.indexer import MathGraphIndexer
from src.vector.store import LocalVectorStore
from src.logger import log


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
    + Math PropertyGraph Traversal + Gemini Synthesis.
    """

    def __init__(self):
        self.settings = get_settings()
        self.indexer = MathGraphIndexer()
        self.vector_store = LocalVectorStore()

        # Initialize Gemini Client
        self.client = genai.Client(api_key=self.settings.gemini_api_key)

        # Pre-compute graph node embeddings for semantic matching
        self._node_embeddings: dict[str, list[float]] = {}
        self._build_node_embeddings()

        log.info("Initialized MathQueryEngine with hybrid vector + graph retrieval engine.")

    # ------------------------------------------------------------------
    # Graph node embedding index
    # ------------------------------------------------------------------

    def _build_node_embeddings(self):
        """Embed all graph node labels+descriptions for semantic matching."""
        graph = self.indexer.graph
        if graph.number_of_nodes() == 0:
            return

        node_ids = list(graph.nodes)
        texts = []
        for nid in node_ids:
            desc = graph.nodes[nid].get("description", "")
            texts.append(f"{nid}: {desc}" if desc else nid)

        try:
            embeddings = self.vector_store.embed_texts(texts)
            for nid, emb in zip(node_ids, embeddings):
                self._node_embeddings[nid] = emb
            log.info(f"Pre-computed embeddings for {len(node_ids)} graph nodes.")
        except Exception as e:
            log.warning(f"Could not embed graph nodes ({e}). Falling back to keyword matching.")

    def refresh_node_embeddings(self):
        """Re-build node embeddings (called after graph updates)."""
        self._node_embeddings.clear()
        self._build_node_embeddings()

    def _find_similar_nodes(self, query: str, top_k: int = 3) -> list[str]:
        """Find graph nodes semantically closest to the query."""
        if not self._node_embeddings:
            # Fallback: keyword matching
            return self._keyword_match_nodes(query, top_k)

        try:
            query_emb = self.vector_store.embed_texts([query])[0]
            q = np.array(query_emb)

            scored: list[tuple[str, float]] = []
            for nid, emb in self._node_embeddings.items():
                e = np.array(emb)
                # Cosine similarity
                sim = float(np.dot(q, e) / (np.linalg.norm(q) * np.linalg.norm(e) + 1e-9))
                scored.append((nid, sim))

            scored.sort(key=lambda x: x[1], reverse=True)
            # Only return nodes with meaningful similarity
            return [nid for nid, sim in scored[:top_k] if sim > 0.3]
        except Exception as e:
            log.warning(f"Semantic node matching failed ({e}). Using keyword fallback.")
            return self._keyword_match_nodes(query, top_k)

    @staticmethod
    def _keyword_match_nodes(query: str, top_k: int = 3) -> list[str]:
        """Legacy keyword substring matching as fallback."""
        # This won't be used normally, but keeps things working if embeddings fail
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
        Retrieves top semantic text chunks from LanceDB and matching
        graph nodes/edges from the NetworkX PropertyGraph.
        """
        # 1. Semantic Vector Search via LanceDB
        vector_results = self.vector_store.search_similar(
            prompt, top_k=top_k, course=course
        )
        vector_context = []
        for idx, res in enumerate(vector_results, start=1):
            source = res.get("source", "Note")
            text = res.get("text", "")
            course_tag = res.get("course", "")
            vector_context.append(
                f"[Chunk {idx} — {source} ({course_tag})]\n{text}"
            )

        # 2. Graph Traversal via NetworkX & KùzuDB PropertyGraph
        graph_context = []
        if use_graph:
            graph = self.indexer.graph
            matched_nodes = self._find_similar_nodes(prompt, top_k=3)

            for n in matched_nodes:
                if n not in graph.nodes:
                    continue
                node_data = graph.nodes[n]
                node_type = node_data.get("entity_type", "Concept")
                desc = node_data.get("description", "")

                rel_info = []
                for nbr in list(graph.neighbors(n))[:4]:
                    rel = graph.edges[n, nbr].get("relation", "DEPENDS_ON")
                    rel_info.append(f"{n} --[{rel}]--> {nbr}")

                for pred in list(graph.predecessors(n))[:4]:
                    rel = graph.edges[pred, n].get("relation", "DEPENDS_ON")
                    rel_info.append(f"{pred} --[{rel}]--> {n}")

                node_str = f"• [{node_type}] {n}" + (f" — {desc}" if desc else "")
                if rel_info:
                    node_str += "\n  Relations: " + " | ".join(rel_info)
                graph_context.append(node_str)

        # Assemble unified context string
        context_parts = []
        if vector_context:
            context_parts.append(
                "### Semantic Vector Chunks:\n" + "\n\n".join(vector_context)
            )
        if graph_context:
            context_parts.append(
                "### Math PropertyGraph Nodes & Relations:\n" + "\n".join(graph_context)
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
        using Gemini with configurable parameters.
        """
        log.info(
            f"Processing hybrid RAG query: '{prompt}' "
            f"(top_k={top_k}, temp={temperature}, course={course or 'all'}, graph={use_graph})"
        )
        context_str = self.retrieve_context(
            prompt, top_k=top_k, course=course, use_graph=use_graph
        )
        log.debug(f"Retrieved hybrid context ({len(context_str)} chars)")

        full_prompt = MATH_QUERY_PROMPT_TEMPLATE.format(
            context_str=context_str,
            query_str=prompt,
        )

        model_name = self.settings.gemini_model.replace("models/", "")
        log.info(f"Synthesizing RAG response via Gemini model '{model_name}'...")
        response = self.client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=genai_types.GenerateContentConfig(
                temperature=temperature,
            ),
        )
        log.info("RAG response synthesis complete.")

        return response.text
