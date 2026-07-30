import io
from PIL import Image
from google import genai
from google.genai import types

from src.config import get_settings
from src.ingestion.base import BaseOCRProvider
from src.ingestion.sanitizer import LaTeXSanitizer

MATH_OCR_SYSTEM_PROMPT = """
You are an expert mathematical OCR and document parsing engine.
Your task is to convert the provided document image into accurate, clean Markdown containing precise LaTeX math notation.

Rules:
1. Preserve all mathematical notation. Use $...$ for inline math and $$...$$ for display math blocks.
2. Maintain headings (#, ##, ###), lists, tables, theorems, definitions, and proofs structure.
3. Do NOT omit any equations, matrices, or derivations.
4. Output ONLY the raw parsed Markdown/LaTeX content. Do NOT include meta-commentary like "Here is the parsed markdown".
"""

class GeminiOCRProvider(BaseOCRProvider):
    """
    OCR provider using Google Gemini Vision API.
    """
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = model_name

    def process_image(self, image: Image.Image) -> str:
        """
        Parses a single page image into Markdown + LaTeX.
        """
        # Convert PIL Image to PNG bytes
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/png"
                ),
                MATH_OCR_SYSTEM_PROMPT
            ]
        )
        raw_md = response.text or ""
        return LaTeXSanitizer.sanitize(raw_md)

    def process_images_batch(self, images: list[Image.Image]) -> str:
        """
        Processes a list of page images sequentially or in multi-part prompt.
        """
        results = []
        for idx, img in enumerate(images, start=1):
            parsed_page = self.process_image(img)
            results.append(f"<!-- Page {idx} -->\n{parsed_page}")
        return "\n\n".join(results)
