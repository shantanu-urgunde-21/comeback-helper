from shared.llm.ollama import get_ollama_client
from shared.logger import log


class ContextualReassembler:
    """
    Optional Contextual Repair Pass. Passes draft Markdown through a lightweight
    local LLM to repair broken sentence boundaries and normalize LaTeX syntax.
    """

    def __init__(self, model_name: str = "qwen2.5-coder:3b"):
        self.model_name = model_name
        self.client = get_ollama_client()

    def refine_markdown(self, raw_md: str) -> str:
        """
        Attempts to refine draft Markdown using local Ollama endpoint if available.
        Falls back cleanly to raw_md if Ollama service is not running locally.
        """
        if not raw_md.strip():
            return raw_md

        prompt = f"""You are an expert handwritten note OCR post-processor.
Your job is to repair broken sentence boundaries and normalize LaTeX formatting ($...$ for inline math, $$...$$ for block math) without altering any mathematical meaning or deleting equations.

Draft Handwritten OCR Markdown:
-------------------
{raw_md}
-------------------

Output ONLY the corrected Markdown:"""

        result = self.client.chat(
            prompt=prompt,
            model=self.model_name,
            timeout=10,
        )

        if result:
            log.info(f"Refined handwritten Markdown via Ollama '{self.model_name}'")
            return result

        return raw_md
