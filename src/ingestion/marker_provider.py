import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

from src.ingestion.base import BaseOCRProvider
from src.ingestion.sanitizer import LaTeXSanitizer
from src.logger import log

class MarkerOCRProvider(BaseOCRProvider):
    """
    Local PDF-to-Markdown OCR provider using Marker (marker-pdf).
    Optimized for high-speed GPU/CPU extraction of academic PDFs and LaTeX math formatting.
    """

    def __init__(self):
        self.sanitizer = LaTeXSanitizer
        self._check_availability()

    def _check_availability(self):
        self.marker_cmd = shutil.which("marker_single") or shutil.which("marker")
        if not self.marker_cmd:
            log.warning("'marker_single' CLI tool not found in PATH. Install via: pip install marker-pdf")

    def process_pdf_direct(self, pdf_path: Path) -> str:
        """
        Processes a full PDF document directly using Marker CLI for maximum speed and layout accuracy.
        Returns clean Markdown string.
        """
        if not self.marker_cmd:
            raise RuntimeError(
                "Marker CLI ('marker_single') is not installed or not in PATH. "
                "Please run 'pip install marker-pdf' or set OCR_PROVIDER=gemini in .env."
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_out = Path(temp_dir)
            cmd = [
                self.marker_cmd,
                str(pdf_path.resolve()),
                str(temp_out),
                "--output_format", "markdown"
            ]

            log.info(f"Running Marker CLI on: {pdf_path.name}...")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"Marker execution failed: {result.stderr}")

            # Find generated markdown file in temp_out
            md_files = list(temp_out.glob("**/*.md"))
            if not md_files:
                raise FileNotFoundError(f"Marker completed but no Markdown file was generated in {temp_out}")

            raw_md = md_files[0].read_text(encoding="utf-8")
            return self.sanitizer.sanitize(raw_md)

    def process_image(self, image: Image.Image) -> str:
        """
        Fallback implementation for single image processing by saving image to temporary PDF.
        """
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
            image.save(tmp_img.name)
            tmp_path = Path(tmp_img.name)

        try:
            # Convert single image to temp PDF for marker
            pdf_tmp = tmp_path.with_suffix(".pdf")
            image.convert("RGB").save(pdf_tmp, "PDF")
            
            raw_md = self.process_pdf_direct(pdf_tmp)
            if pdf_tmp.exists():
                pdf_tmp.unlink()
            return raw_md
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def process_images_batch(self, images: list[Image.Image]) -> str:
        """
        Processes a batch of PIL Images by rendering them into Markdown.
        """
        results = [self.process_image(img) for img in images]
        return "\n\n".join(results)
