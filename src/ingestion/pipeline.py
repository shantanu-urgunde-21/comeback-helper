from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF

from src.config import get_settings
from src.ingestion.base import BaseOCRProvider
from src.ingestion.gemini_ocr import GeminiOCRProvider

class IngestionPipeline:
    """
    Handles PDF loading, page rendering, OCR parsing, and vault output generation.
    """

    def __init__(self, ocr_provider: BaseOCRProvider | None = None):
        self.ocr_provider = ocr_provider or GeminiOCRProvider()
        self.settings = get_settings()

    def pdf_to_images(self, pdf_path: Path, dpi: int = 200) -> list[Image.Image]:
        """
        Renders a PDF file into a list of PIL Images.
        """
        doc = fitz.open(pdf_path)
        images = []
        zoom = dpi / 72  # Standard 72 dpi baseline
        mat = fitz.Matrix(zoom, zoom)

        for page in doc:
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)

        doc.close()
        return images

    def process_pdf(
        self,
        pdf_path: str | Path,
        course_name: str,
        output_filename: str | None = None
    ) -> Path:
        """
        Processes a PDF document, runs OCR, and saves the Markdown file to the Obsidian Vault.
        """
        pdf_path = Path(pdf_path).resolve()
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        print(f"[Ingestion] Extracting pages from: {pdf_path.name}...")
        images = self.pdf_to_images(pdf_path)
        print(f"[Ingestion] Rendered {len(images)} pages. Running OCR...")

        parsed_markdown = self.ocr_provider.process_images_batch(images)

        # Prepare Obsidian target directory
        vault_path = self.settings.vault_path
        course_dir = vault_path / course_name
        course_dir.mkdir(parents=True, exist_ok=True)

        filename = output_filename or f"{pdf_path.stem}.md"
        if not filename.endswith(".md"):
            filename += ".md"

        target_path = course_dir / filename
        
        # Add metadata header
        header = f"---\ncourse: \"{course_name}\"\nsource_file: \"{pdf_path.name}\"\ntags: [\"math\", \"coursework\", \"{course_name.lower().replace(' ', '-')}\"]\n---\n\n# {pdf_path.stem}\n\n"
        full_content = header + parsed_markdown

        target_path.write_text(full_content, encoding="utf-8")
        print(f"[Ingestion] Saved Markdown note to Obsidian Vault: {target_path}")

        return target_path
