import io
import re
import time
from typing import List
from PIL import Image
from google.genai import types

from shared.config import get_settings
from .base import BaseOCRProvider
from .sanitizer import LaTeXSanitizer
from shared.llm.gemini import get_gemini_client, get_gemini_candidate_models
from shared.logger import log

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
    OCR provider using Google Gemini Vision API with automatic candidate fallback,
    multi-page batching (3 pages per call), and 4s pacing delay to prevent 429 quota exhaustion.
    """

    def __init__(self, model_name: str | None = None):
        settings = get_settings()
        self.client = get_gemini_client()
        if not self.client:
            raise RuntimeError("No valid Gemini API key configured for OCR.")
        self.candidate_models = get_gemini_candidate_models()
        log.info(f"Initialized GeminiOCRProvider with candidate models: {self.candidate_models}")

    def process_image(self, image: Image.Image) -> str:
        """
        Parses a single page image into Markdown + LaTeX with candidate model fallback and retry pacing.
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
                    time.sleep(2.0)  # Pacing delay
                    return LaTeXSanitizer.sanitize(raw_md)
                except Exception as e:
                    err_str = str(e)
                    log.warning(f"Gemini OCR model '{model}' attempt {retry+1} failed: {e}")
                    last_exception = e
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        wait_sec = 15
                        m = re.search(r"retry in (\d+\.?\d*)s", err_str)
                        if m:
                            wait_sec = int(float(m.group(1))) + 2
                        log.warning(f"Rate limit quota hit. Pausing for {wait_sec}s for API quota reset...")
                        time.sleep(wait_sec)
                    else:
                        break

        log.error(f"All Gemini OCR models failed. Last error: {last_exception}")
        raise RuntimeError(f"All Gemini OCR models failed. Last error: {last_exception}")

    def process_images_batch(
        self,
        images: List[Image.Image],
        batch_size: int = 3,
        delay_sec: float = 4.0
    ) -> List[str]:
        """
        Processes page images in batches of `batch_size` (default: 3 pages per Gemini call)
        with a `delay_sec` (default: 4s) pacing delay between calls. Returns list of page Markdown strings.
        """
        total_pages = len(images)
        log.info(
            f"Batched OCR processing: {total_pages} total pages in chunks of {batch_size} "
            f"with {delay_sec}s pacing delay..."
        )

        results: List[str] = []

        for i in range(0, total_pages, batch_size):
            batch_imgs = images[i : i + batch_size]
            batch_start = i + 1
            batch_end = min(i + batch_size, total_pages)
            log.info(f"Processing page batch [{batch_start}-{batch_end}/{total_pages}] via Gemini Vision...")

            # Prepare multi-image payload
            parts = []
            for page_num, img in zip(range(batch_start, batch_end + 1), batch_imgs):
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                parts.append(types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png"))

            batch_prompt = (
                f"You are an expert mathematical OCR engine. "
                f"Transcribe these {len(batch_imgs)} consecutive page images into clean Markdown with LaTeX math ($...$ and $$...$$). "
                f"Clearly separate each page with the comment: <!-- Page X --> (e.g. <!-- Page {batch_start} -->)."
            )
            parts.append(batch_prompt)

            batch_success = False
            last_exception = None

            for model in self.candidate_models:
                for retry in range(3):
                    try:
                        response = self.client.models.generate_content(
                            model=model,
                            contents=parts
                        )
                        raw_md = response.text or ""
                        sanitized = LaTeXSanitizer.sanitize(raw_md)
                        results.append(sanitized)
                        batch_success = True
                        log.info(
                            f"Batch [{batch_start}-{batch_end}] succeeded via '{model}' "
                            f"({len(sanitized)} chars)"
                        )
                        break
                    except Exception as e:
                        err_str = str(e)
                        last_exception = e
                        log.warning(f"Batch [{batch_start}-{batch_end}] attempt {retry+1} via '{model}' failed: {e}")
                        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                            wait_sec = 20
                            m = re.search(r"retry in (\d+\.?\d*)s", err_str)
                            if m:
                                wait_sec = int(float(m.group(1))) + 2
                            log.warning(f"Rate limit hit during batch. Pausing for {wait_sec}s...")
                            time.sleep(wait_sec)
                        else:
                            break

                if batch_success:
                    break

            if not batch_success:
                log.warning(f"Batched OCR failed for pages [{batch_start}-{batch_end}]. Falling back to single-page processing...")
                for page_num, img in zip(range(batch_start, batch_end + 1), batch_imgs):
                    single_md = self.process_image(img)
                    results.append(f"<!-- Page {page_num} -->\n{single_md}")

            # Pacing delay between batch calls
            if batch_end < total_pages:
                log.info(f"Pacing delay: sleeping {delay_sec}s before next batch...")
                time.sleep(delay_sec)

        return results
