import re
import json
from typing import Optional

from google.genai import types as genai_types

from shared.config import get_settings
from shared.llm.gemini import get_gemini_client, get_gemini_candidate_models
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

        log.info("Initialized MathQueryEngine with hybrid vector + graph retrieval (bounded neighborhood).")

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
        Retrieves top semantic text chunks from LanceDB and a bounded
        neighborhood subgraph from the graph service's /neighborhood endpoint.
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

        # 2. Bounded Graph Neighborhood via /neighborhood endpoint
        graph_context = []
        if use_graph:
            try:
                # Try to extract seed concept IDs from vector results.
                # Vector chunks may carry concept_id in metadata (future);
                # for now, use note source as a heuristic starting point.
                seed_ids = []
                for res in vector_results[:3]:
                    source = res.get("source", "").replace(".md", "").strip()
                    if source and source not in ["", "init"]:
                        seed_ids.append(source)

                if seed_ids:
                    neighborhood = self.indexer.neighborhood(seed_ids, hops=1)
                    nodes = neighborhood.get("nodes", [])
                    edges = neighborhood.get("edges", [])

                    # Format nodes with their descriptions and immediate relations
                    for node in nodes:
                        node_id = node.get("id", "")
                        node_type = node.get("entity_type", "Concept")
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

        # Try Gemini API with candidate model fallback
        client = get_gemini_client()
        if client:
            candidates = get_gemini_candidate_models()
            for model_name in candidates:
                try:
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
                except Exception as e:
                    err_str = str(e)
                    log.warning(f"Gemini RAG synthesis via '{model_name}' failed: {e}")
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        log.info(f"Candidate '{model_name}' rate-limited. Trying next candidate...")
                        continue

        # Ollama Fallback
        ollama = get_ollama_client()
        if ollama.is_available():
            for model in ["llama3.2", "qwen2.5:3b", "phi3:mini"]:
                if ollama.has_model(model):
                    log.info(f"Synthesizing RAG response via local Ollama '{model}'...")
                    ans = ollama.chat(prompt=full_prompt, model=model, temperature=temperature)
                    if ans:
                        return ans

        return (
            "### Retrieved Vault Context & Graph Connections:\n\n"
            + context_str
            + "\n\n*(Note: Gemini API and local Ollama are currently offline or rate-limited. Answer synthesized from raw vault context above.)*"
        )
