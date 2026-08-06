import json
from pathlib import Path
from PIL import Image

from src.ingestion.base import BaseOCRProvider
from src.ingestion.handwriting.preprocessor import ImagePreprocessor
from src.ingestion.handwriting.ollama_vlm import OllamaVisionOCR
from src.ingestion.handwriting.reassembler import ContextualReassembler
from src.ingestion.handwriting.progress import GranularProgressLogger
from src.logger import log

class HandwritingOCRProvider(BaseOCRProvider):
    """
    100% Local Vision-Language OCR Provider using GGUF Quantized Qwen2.5-VL (3B) via Ollama.
    Maintains ~2GB VRAM usage on GTX 1650, providing real-time granular terminal logging
    and saving intermediate artifacts at every station.
    """

    def __init__(self, vault_attachments_dir: Path | None = None, debug_dir: Path | None = None, model_name: str = "qwen2.5vl:3b"):
        self.preprocessor = ImagePreprocessor()
        self.vision_ocr = OllamaVisionOCR(model_name=model_name)
        self.reassembler = ContextualReassembler()
        self.logger = GranularProgressLogger()
        
        self.debug_dir = debug_dir or Path("./.storage/debug_handwriting")
        self.debug_dir.mkdir(parents=True, exist_ok=True)

    def process_image(self, image: Image.Image, page_idx: int = 1) -> str:
        """
        Processes a single handwritten note page image through 4 streamlined VLM stations,
        saving debug image artifacts and raw text at each step.
        """
        total_stations = 4
        page_debug_dir = self.debug_dir / f"page_{page_idx}"
        page_debug_dir.mkdir(parents=True, exist_ok=True)

        # Station 1: Preprocessing & Ruling Line Removal
        self.logger.log_station(1, total_stations, f"Page {page_idx} Preprocessing", f"Input dimensions: {image.size}")
        self.logger.log_step("Erasing blue notebook ruling lines & sharpening ink...")
        prep_img = self.preprocessor.preprocess_pil(image)
        step1_path = page_debug_dir / "step1_preprocessed.png"
        prep_img.save(step1_path)
        self.logger.log_step(f"Saved preprocessed image artifact: {step1_path}", status="SUCCESS")

        # Station 2: Native 100% Local VLM Extraction (qwen2.5vl:3b)
        self.logger.log_station(2, total_stations, f"Page {page_idx} Local Qwen2.5-VL (3B) Vision OCR", "Transcribing full page layout & math notation...")
        raw_vlm_text = self.vision_ocr.process_image(prep_img)
        step2_md_path = page_debug_dir / "step2_raw_vlm_transcript.md"
        step2_md_path.write_text(raw_vlm_text, encoding="utf-8")
        self.logger.log_step(f"Saved raw VLM transcript artifact: {step2_md_path}", status="SUCCESS")

        # Station 3: Contextual LLM Repair Pass
        self.logger.log_station(3, total_stations, f"Page {page_idx} Contextual Repair", "Restoring sentence boundaries and LaTeX syntax...")
        refined_md = self.reassembler.refine_markdown(raw_vlm_text)
        step3_md_path = page_debug_dir / "step3_refined_note.md"
        step3_md_path.write_text(refined_md, encoding="utf-8")
        self.logger.log_step(f"Saved refined note artifact: {step3_md_path}", status="SUCCESS")

        # Station 4: Vault Ready Export
        self.logger.log_station(4, total_stations, f"Page {page_idx} Completed", f"Generated Markdown output ({len(refined_md)} chars)")

        return refined_md

    def process_images_batch(self, images: list[Image.Image]) -> str:
        results = []
        for idx, img in enumerate(images, start=1):
            parsed = self.process_image(img, page_idx=idx)
            results.append(f"<!-- Page {idx} -->\n{parsed}")

        return "\n\n".join(results)
