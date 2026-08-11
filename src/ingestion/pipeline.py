from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF

from src.config import get_settings
from src.ingestion.base import BaseOCRProvider
from src.ingestion.gemini_ocr import GeminiOCRProvider
from src.logger import log

class IngestionPipeline:
    """
    Handles PDF loading, page rendering, OCR parsing, and real-time vault output generation.
    Supports real-time incremental file writing page-by-page.
    """

    def __init__(self, ocr_provider: BaseOCRProvider | None = None):
        self.settings = get_settings()
        
        if ocr_provider is not None:
            self.ocr_provider = ocr_provider
        else:
            provider_type = self.settings.ocr_provider.lower()
            if provider_type == "handwriting":
                from src.ingestion.handwriting_provider import HandwritingOCRProvider
                self.ocr_provider = HandwritingOCRProvider()
            else:
                self.ocr_provider = GeminiOCRProvider()
        
        log.info(f"Initialized IngestionPipeline with OCR provider: {self.ocr_provider.__class__.__name__}")

    def pdf_to_images(self, pdf_path: Path, dpi: int = 200) -> list[Image.Image]:
        """
        Renders a PDF file into a list of PIL Images.
        """
        log.debug(f"Rendering PDF to images (dpi={dpi}): {pdf_path.name}")
        doc = fitz.open(pdf_path)
        images = []
        zoom = dpi / 72  # Standard 72 dpi baseline
        mat = fitz.Matrix(zoom, zoom)

        for page in doc:
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)

        doc.close()
        log.info(f"Rendered {len(images)} pages from PDF: {pdf_path.name}")
        return images

    def process_pdf(
        self,
        pdf_path: str | Path,
        course_name: str,
        output_filename: str | None = None
    ) -> Path:
        """
        Processes a PDF document page-by-page, appending results incrementally to Obsidian Vault in real-time.
        """
        pdf_path = Path(pdf_path).resolve()
        if not pdf_path.exists():
            log.error(f"PDF file not found at: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        log.info(f"Starting PDF ingestion for: {pdf_path.name} (Course: {course_name})")

        # Prepare Obsidian target file path
        vault_path = self.settings.vault_path
        course_dir = vault_path / course_name
        course_dir.mkdir(parents=True, exist_ok=True)

        filename = output_filename or f"{pdf_path.stem}.md"
        if not filename.endswith(".md"):
            filename += ".md"

        target_path = course_dir / filename
        
        # Write initial metadata header
        header = f"---\ncourse: \"{course_name}\"\nsource_file: \"{pdf_path.name}\"\ntags: [\"math\", \"coursework\", \"{course_name.lower().replace(' ', '-')}\"]\n---\n\n# {pdf_path.stem}\n\n"
        
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(header)
            f.flush()

        log.info(f"Initialized output vault file: {target_path}")

        # Check for fast direct PDF processing (e.g. Marker)
        if hasattr(self.ocr_provider, "process_pdf_direct"):
            try:
                log.info(f"Executing direct PDF parsing via {self.ocr_provider.__class__.__name__}...")
                parsed_md = self.ocr_provider.process_pdf_direct(pdf_path)
                with open(target_path, "a", encoding="utf-8") as f:
                    f.write(parsed_md)
                    f.flush()
                log.info(f"Direct PDF processing completed: {target_path}")
                return target_path
            except Exception as e:
                log.warning(f"Direct PDF processing failed ({e}). Falling back to page-by-page image rendering...")

        images = self.pdf_to_images(pdf_path)
        total_pages = len(images)
        log.info(f"Processing {total_pages} pages via {self.ocr_provider.__class__.__name__}...")

        with open(target_path, "a", encoding="utf-8") as f:
            if hasattr(self.ocr_provider, "process_images_batch"):
                try:
                    batched_chunks = self.ocr_provider.process_images_batch(images, batch_size=3, delay_sec=4.0)
                    for chunk_md in batched_chunks:
                        f.write(f"{chunk_md}\n\n")
                        f.flush()
                except Exception as e:
                    log.warning(f"Batch processing failed ({e}). Falling back to single-page iteration...")
                    for idx, img in enumerate(images, start=1):
                        page_md = self.ocr_provider.process_image(img)
                        f.write(f"<!-- Page {idx} -->\n{page_md}\n\n")
                        f.flush()
            else:
                for idx, img in enumerate(images, start=1):
                    log.info(f"Processing page {idx}/{total_pages}...")
                    page_md = self.ocr_provider.process_image(img)
                    f.write(f"<!-- Page {idx} -->\n{page_md}\n\n")
                    f.flush()
                    log.info(f"Page {idx}/{total_pages} saved to vault note.")

        if hasattr(self.ocr_provider, "unload_model"):
            self.ocr_provider.unload_model()

        log.info(f"PDF Ingestion complete! Vault note ready at: {target_path}")
        return target_path
