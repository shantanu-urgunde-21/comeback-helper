from llama_index.core import PropertyGraphIndex
from llama_index.llms.gemini import Gemini

from src.config import get_settings
from src.graph.indexer import MathGraphIndexer

MATH_QUERY_PROMPT_TEMPLATE = """
You are a brilliant university mathematics and computer science tutor assisting a student.
Use the provided retrieved context from the student's Obsidian coursework vault (including mathematical theorems, definitions, proofs, formulas, and concept graph connections) to answer their question.

Retrieved Vault Context:
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
    RAG query engine combining PropertyGraph + Dense Vector Retrieval + Gemini Synthesis.
    """

    def __init__(self):
        self.settings = get_settings()
        self.indexer = MathGraphIndexer()
        self.index: PropertyGraphIndex = self.indexer.build_or_update_index()
        self.llm = Gemini(
            model="models/gemini-2.5-flash",
            api_key=self.settings.gemini_api_key
        )

    def query(self, prompt: str) -> str:
        """
        Retrieves graph & vector context and generates a math explanation using Gemini.
        """
        retriever = self.index.as_retriever(
            sub_retrievers=["vector", "property_graph"],
            similarity_top_k=5
        )
        nodes = retriever.retrieve(prompt)

        context_str = "\n\n".join([f"--- Context Chunk {i+1} ---\n{n.node.get_content()}" for i, n in enumerate(nodes)])

        full_prompt = MATH_QUERY_PROMPT_TEMPLATE.format(
            context_str=context_str,
            query_str=prompt
        )

        response = self.llm.complete(full_prompt)
        return str(response.text)
