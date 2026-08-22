from PIL import Image

from shared.llm.ollama import get_ollama_client
from shared.logger import log


class OllamaVisionOCR:
    """
    100% Local Vision-Language OCR Provider using GGUF Quantized models via Ollama.
    Delegates to the centralized OllamaClient from src/llm/ollama.py.
    """

    def __init__(self, model_name: str = "qwen2.5vl:3b"):
        self.model_name = model_name
        self.client = get_ollama_client()

    def process_image(self, image: Image.Image) -> str:
        """
        Sends the full handwritten page image to local Ollama Vision model.
        """
        prompt = (
            "You are an expert handwritten STEM note OCR engine. "
            "Transcribe this handwritten note page into clean Markdown. "
            "Preserve all headings (#, ##), paragraphs, and lists. "
            "Format math expressions with precision: use $...$ for inline math "
            "and $$...$$ for block equations."
        )

        log.info(f"Sending page image to local Ollama Vision model ('{self.model_name}')...")
        result = self.client.vision_chat(
            prompt=prompt,
            image=image,
            model=self.model_name,
            temperature=0.1,
            max_tokens=1024,
        )

        if result is None:
            raise RuntimeError(f"Local Ollama Vision processing failed for model '{self.model_name}'")

        return result
