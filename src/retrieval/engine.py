from google import genai
from src.config import get_settings
from src.graph.indexer import MathGraphIndexer
from src.vector.store import LocalVectorStore
from src.logger import log

MATH_QUERY_PROMPT_TEMPLATE = """
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
"""

class MathQueryEngine:
    """
    Hybrid RAG query engine combining LanceDB Vector Similarity + Math PropertyGraph Traversal + Gemini Synthesis.
    """

    def __init__(self):
        self.settings = get_settings()
        self.indexer = MathGraphIndexer()
        self.vector_store = LocalVectorStore()
        
        # Initialize Gemini Client
        self.client = genai.Client(api_key=self.settings.gemini_api_key)
        log.info("Initialized MathQueryEngine with hybrid vector + graph retrieval engine.")

    def retrieve_context(self, prompt: str, top_k: int = 5) -> str:
        """
        Retrieves top semantic text chunks from LanceDB and matching graph nodes/edges from NetworkX graph.
        """
        # 1. Semantic Vector Search via LanceDB
        vector_results = self.vector_store.search_similar(prompt, top_k=top_k)
        vector_context = []
        for idx, res in enumerate(vector_results, start=1):
            source = res.get('source', 'Note')
            text = res.get('text', '')
            vector_context.append(f"[Chunk {idx} - Source: {source}]\n{text}")

        # 2. Graph Traversal via NetworkX Math PropertyGraph
        graph = self.indexer.graph
        graph_context = []
        
        # Search for node labels mentioned in query or matching prompt terms
        query_words = prompt.lower().split()
        matched_nodes = []
        for node in graph.nodes:
            if any(w in node.lower() for w in query_words if len(w) > 3):
                matched_nodes.append(node)

        for n in matched_nodes[:3]: # Limit to top 3 matching graph nodes
            node_data = graph.nodes[n]
            node_type = node_data.get("entity_type", "Concept")
            desc = node_data.get("description", "")
            
            # Get prerequisites / outgoing relations
            neighbors = list(graph.neighbors(n))
            rel_info = []
            for nbr in neighbors:
                rel = graph.edges[n, nbr].get("relation", "DEPENDS_ON")
                rel_info.append(f"{n} --[{rel}]--> {nbr}")

            node_str = f"• Graph Node [{node_type}]: {n} - {desc}"
            if rel_info:
                node_str += "\n  Relations: " + ", ".join(rel_info)
            graph_context.append(node_str)

        # Assemble unified context string
        context_parts = []
        if vector_context:
            context_parts.append("### Semantic Vector Chunks:\n" + "\n\n".join(vector_context))
        if graph_context:
            context_parts.append("### Math PropertyGraph Nodes & Relations:\n" + "\n".join(graph_context))

        if not context_parts:
            return "No prior context found in vault notes yet."

        return "\n\n".join(context_parts)

    def query(self, prompt: str) -> str:
        """
        Retrieves hybrid context and synthesizes math explanation using Gemini.
        """
        log.info(f"Processing hybrid RAG query: '{prompt}'")
        context_str = self.retrieve_context(prompt)
        log.debug(f"Retrieved hybrid context ({len(context_str)} chars)")

        full_prompt = MATH_QUERY_PROMPT_TEMPLATE.format(
            context_str=context_str,
            query_str=prompt
        )

        model_name = self.settings.gemini_model.replace("models/", "")
        log.info(f"Synthesizing RAG response via Gemini model '{model_name}'...")
        response = self.client.models.generate_content(
            model=model_name,
            contents=full_prompt
        )
        log.info("RAG response synthesis complete.")

        return response.text
