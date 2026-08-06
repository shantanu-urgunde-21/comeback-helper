import json
from pathlib import Path
from PIL import Image

from src.ingestion.base import BaseOCRProvider
from src.ingestion.handwriting.preprocessor import ImagePreprocessor
from src.ingestion.handwriting.segmenter import CoarseLayoutSegmenter
from src.ingestion.handwriting.ocr_engine import SpecializedOCREngine
from src.ingestion.handwriting.reassembler import ContextualReassembler
from src.ingestion.handwriting.progress import GranularProgressLogger
from src.logger import log

class HandwritingOCRProvider(BaseOCRProvider):
    """
    Multi-stage, VRAM-optimized OCR Provider specifically designed for handwritten STEM notes.
    Provides real-time granular terminal logging and saves intermediate artifacts at every station
    for full end-to-end user observability.
    """

    def __init__(self, vault_attachments_dir: Path | None = None, debug_dir: Path | None = None):
        self.preprocessor = ImagePreprocessor()
        self.segmenter = CoarseLayoutSegmenter()
        self.ocr_engine = SpecializedOCREngine(vault_attachments_dir=vault_attachments_dir)
        self.reassembler = ContextualReassembler()
        self.logger = GranularProgressLogger()
        
        self.debug_dir = debug_dir or Path("./.storage/debug_handwriting")
        self.debug_dir.mkdir(parents=True, exist_ok=True)

    def process_image(self, image: Image.Image, page_idx: int = 1) -> str:
        """
        Processes a single handwritten note page image through 5 stations,
        saving debug image artifacts and JSON layout metadata at each step.
        """
        total_stations = 5
        page_debug_dir = self.debug_dir / f"page_{page_idx}"
        page_debug_dir.mkdir(parents=True, exist_ok=True)

        # Station 1: Preprocessing
        self.logger.log_station(1, total_stations, f"Page {page_idx} Preprocessing", f"Input dimensions: {image.size}")
        self.logger.log_step("Executing contrast enhancement and shadow reduction...")
        prep_img = self.preprocessor.preprocess_pil(image)
        step1_path = page_debug_dir / "step1_preprocessed.png"
        prep_img.save(step1_path)
        self.logger.log_step(f"Saved preprocessed image artifact: {step1_path}", status="SUCCESS")

        # Station 2: Layout Segmentation
        self.logger.log_station(2, total_stations, f"Page {page_idx} Layout Analysis", "Analyzing spatial contours...")
        regions = self.segmenter.segment(prep_img)
        
        # Save visual bounding box annotations
        annotated_img = CoarseLayoutSegmenter.draw_annotated_boxes(prep_img, regions)
        step2_img_path = page_debug_dir / "step2_annotated_layout.png"
        annotated_img.save(step2_img_path)

        # Save JSON metadata of regions
        region_meta = [
            {"index": idx, "type": r.region_type.value, "box": r.box, "size": r.cropped_image.size}
            for idx, r in enumerate(regions, start=1)
        ]
        step2_json_path = page_debug_dir / "step2_layout_regions.json"
        step2_json_path.write_text(json.dumps(region_meta, indent=2), encoding="utf-8")
        
        self.logger.log_step(f"Extracted {len(regions)} layout region blocks.", status="SUCCESS")
        self.logger.log_step(f"Saved annotated layout artifact: {step2_img_path}", status="SUCCESS")

        # Station 3: Task-Specific OCR Execution
        self.logger.log_station(3, total_stations, f"Page {page_idx} Task-Specific OCR Execution", f"Routing {len(regions)} regions on CUDA GPU...")
        
        # Save individual region crops for step 3 inspection
        crops_dir = page_debug_dir / "step3_region_crops"
        crops_dir.mkdir(exist_ok=True)
        for idx, r in enumerate(regions, start=1):
            r.cropped_image.save(crops_dir / f"region_{idx}_{r.region_type.value}.png")

        draft_md = self.ocr_engine.process_regions(regions, page_idx=page_idx, logger=self.logger)
        step3_md_path = page_debug_dir / "step3_raw_ocr.md"
        step3_md_path.write_text(draft_md, encoding="utf-8")
        self.logger.log_step(f"Saved raw OCR draft artifact: {step3_md_path}", status="SUCCESS")

        # Station 4: Contextual LLM Repair Pass
        self.logger.log_station(4, total_stations, f"Page {page_idx} Contextual Repair", "Restoring sentence boundaries and LaTeX syntax...")
        refined_md = self.reassembler.refine_markdown(draft_md)
        step4_md_path = page_debug_dir / "step4_refined_note.md"
        step4_md_path.write_text(refined_md, encoding="utf-8")
        self.logger.log_step(f"Saved refined note artifact: {step4_md_path}", status="SUCCESS")

        # Station 5: Obsidian Vault Ready
        self.logger.log_station(5, total_stations, f"Page {page_idx} Completed", f"Generated final Markdown output ({len(refined_md)} chars)")

        return refined_md

    def process_images_batch(self, images: list[Image.Image]) -> str:
        results = []
        for idx, img in enumerate(images, start=1):
            parsed = self.process_image(img, page_idx=idx)
            results.append(f"<!-- Page {idx} -->\n{parsed}")

        self.ocr_engine.clear_vram()
        return "\n\n".join(results)
