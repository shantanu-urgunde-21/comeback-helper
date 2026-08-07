import io
import time
from PIL import Image
from google import genai
from google.genai import types

from src.config import get_settings
from src.ingestion.base import BaseOCRProvider
from src.ingestion.sanitizer import LaTeXSanitizer
from src.logger import log

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
    OCR provider using Google Gemini Vision API with automatic model fallback.
    """
    def __init__(self, model_name: str | None = None):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.gemini_api_key)
        primary_model = model_name or settings.gemini_model.replace("models/", "")
        self.candidate_models = [primary_model, "gemini-flash-latest", "gemini-flash-lite-latest"]
        log.info(f"Initialized GeminiOCRProvider with candidate models: {self.candidate_models}")

    def process_image(self, image: Image.Image) -> str:
        """
        Parses a single page image into Markdown + LaTeX with model fallback and rate limit retries.
        """
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        last_exception = None
        for model in self.candidate_models:
            for retry in range(4):
                try:
                    log.debug(f"Sending OCR image to Gemini model '{model}' (attempt {retry+1})...")
                    response = self.client.models.generate_content(
                        model=model,
                        contents=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type="image/png"
                            ),
                            MATH_OCR_SYSTEM_PROMPT
                        ]
                    )
                    raw_md = response.text or ""
                    log.info(f"Successfully processed image via '{model}' ({len(raw_md)} chars)")
                    time.sleep(1.5)
                    return LaTeXSanitizer.sanitize(raw_md)
                except Exception as e:
                    err_str = str(e)
                    log.warning(f"Gemini OCR model '{model}' attempt {retry+1} failed: {e}")
                    last_exception = e
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        wait_sec = 30
                        import re
                        m = re.search(r"retry in (\d+\.?\d*)s", err_str)
                        if m:
                            wait_sec = int(float(m.group(1))) + 2
                        log.warning(f"Rate limit quota hit. Pausing for {wait_sec}s for API quota reset...")
                        time.sleep(wait_sec)
                    else:
                        break  # If non-rate error, try next candidate model

        log.error(f"All Gemini OCR models failed. Last error: {last_exception}")
        raise RuntimeError(f"All Gemini OCR models failed. Last error: {last_exception}")

    def process_images_batch(self, images: list[Image.Image]) -> str:
        """
        Processes a list of page images sequentially.
        """
        results = []
        for idx, img in enumerate(images, start=1):
            parsed_page = self.process_image(img)
            results.append(f"<!-- Page {idx} -->\n{parsed_page}")
        return "\n\n".join(results)
