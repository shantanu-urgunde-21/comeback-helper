import requests
from src.config import get_settings
from src.logger import log

class ContextualReassembler:
    """
    Optional Contextual Repair Pass. Passes draft Markdown extracted from coarse blocks through a lightweight
    local LLM (e.g. Ollama running qwen2.5:3b or phi3:mini) to repair broken sentence boundaries and normalize LaTeX syntax.
    """

    def __init__(self, ollama_url: str = "http://localhost:11434/api/generate", model_name: str = "qwen2.5-coder:3b"):
        self.ollama_url = ollama_url
        self.model_name = model_name

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

        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                refined = data.get("response", "").strip()
                if refined:
                    log.info(f"Successfully refined handwritten Markdown via local Ollama model '{self.model_name}'")
                    return refined
        except Exception as e:
            log.debug(f"Local Ollama refinement unavailable ({e}). Retaining structured draft Markdown.")

        return raw_md
