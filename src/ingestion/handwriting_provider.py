from pathlib import Path
from PIL import Image

from src.ingestion.base import BaseOCRProvider
from src.ingestion.handwriting.preprocessor import ImagePreprocessor
from src.ingestion.handwriting.segmenter import CoarseLayoutSegmenter
from src.ingestion.handwriting.ocr_engine import SpecializedOCREngine
from src.ingestion.handwriting.reassembler import ContextualReassembler
from src.logger import log

class HandwritingOCRProvider(BaseOCRProvider):
    """
    Multi-stage, VRAM-optimized OCR Provider specifically designed for handwritten STEM notes.
    Flow: Preprocessing -> Coarse Block DLA -> Task-Specific OCR Routing -> Contextual LLM Repair.
    Optimized for consumer GPUs with 4GB VRAM.
    """

    def __init__(self, vault_attachments_dir: Path | None = None):
        self.preprocessor = ImagePreprocessor()
        self.segmenter = CoarseLayoutSegmenter()
        self.ocr_engine = SpecializedOCREngine(vault_attachments_dir=vault_attachments_dir)
        self.reassembler = ContextualReassembler()
        log.info("Initialized HandwritingOCRProvider (Multi-stage 4GB VRAM Pipeline)")

    def process_image(self, image: Image.Image, page_idx: int = 1) -> str:
        """
        Processes a single handwritten note page image through the multi-stage pipeline.
        """
        log.info(f"[HandwritingOCRProvider] Step 1: Preprocessing page {page_idx}...")
        prep_img = self.preprocessor.preprocess_pil(image)

        log.info(f"[HandwritingOCRProvider] Step 2: Coarse Layout Analysis page {page_idx}...")
        regions = self.segmenter.segment(prep_img)
        log.info(f"[HandwritingOCRProvider] Extracted {len(regions)} coarse layout blocks.")

        log.info(f"[HandwritingOCRProvider] Step 3: Routing specialized OCR engines page {page_idx}...")
        draft_md = self.ocr_engine.process_regions(regions, page_idx=page_idx)

        log.info(f"[HandwritingOCRProvider] Step 4: Contextual LLM Repair page {page_idx}...")
        refined_md = self.reassembler.refine_markdown(draft_md)

        return refined_md

    def process_images_batch(self, images: list[Image.Image]) -> str:
        """
        Processes a batch of handwritten page images sequentially.
        """
        results = []
        for idx, img in enumerate(images, start=1):
            log.info(f"[HandwritingOCRProvider] Processing page {idx}/{len(images)}...")
            parsed = self.process_image(img, page_idx=idx)
            results.append(f"<!-- Page {idx} -->\n{parsed}")

        self.ocr_engine.clear_vram()
        return "\n\n".join(results)
