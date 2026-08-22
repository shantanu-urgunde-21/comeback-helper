import gc
from pathlib import Path
from typing import List, Optional, Any
from PIL import Image
import torch

from .segmenter import RegionBox, RegionType
from ..sanitizer import LaTeXSanitizer
from shared.logger import log

class SpecializedOCREngine:
    """
    Executes specialized OCR routing per region type with VRAM memory safety for 4GB GPUs.
    Routes BLOCK_MATH -> pix2tex (LaTeX-OCR).
    Routes DIAGRAM -> Image export to attachments.
    Routes TEXT_BLOCK -> TrOCR / VLM text provider.
    """

    def __init__(self, vault_attachments_dir: Path | None = None):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.vault_attachments_dir = vault_attachments_dir
        if self.vault_attachments_dir:
            self.vault_attachments_dir.mkdir(parents=True, exist_ok=True)
            
        self.pix2tex_model = None
        self.trocr_processor = None
        self.trocr_model = None

    def clear_vram(self):
        """
        Clears PyTorch CUDA memory cache and triggers garbage collection to prevent 4GB GPU OOM.
        """
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

    def process_block_math(self, image: Image.Image) -> str:
        """
        Processes standalone block math equation crop using pix2tex (LaTeX-OCR).
        """
        try:
            from pix2tex.cli import LatexOCR
            if self.pix2tex_model is None:
                log.info("Loading pix2tex (LaTeX-OCR) model onto GPU...")
                self.pix2tex_model = LatexOCR()

            latex_str = self.pix2tex_model(image)
            return f"\n$$\n{latex_str}\n$$\n"
        except Exception as e:
            log.warning(f"pix2tex unavailable or failed ({e}). Using fallback.")
            return "\n$$\n% [Math Block Equation]\n$$\n"

    def process_text_block(self, image: Image.Image) -> str:
        """
        Processes handwritten text paragraph block using TrOCR.
        """
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel, RobertaTokenizer, ViTImageProcessor
            if self.trocr_model is None or self.trocr_processor is None:
                log.info(f"Loading TrOCR model ('microsoft/trocr-base-handwritten') on device: {self.device}...")
                tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
                img_proc = ViTImageProcessor.from_pretrained("microsoft/trocr-base-handwritten")
                self.trocr_processor = TrOCRProcessor(image_processor=img_proc, tokenizer=tokenizer)
                self.trocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten").to(self.device)

            pixel_values = self.trocr_processor(image.convert("RGB"), return_tensors="pt").pixel_values.to(self.device)
            with torch.no_grad():
                generated_ids = self.trocr_model.generate(pixel_values, max_new_tokens=512)
                generated_text = self.trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

            return generated_text
        except Exception as e:
            log.warning(f"TrOCR execution warning ({e}). Falling back to placeholder.")
            return "[Handwritten text block]"

    def process_diagram(self, image: Image.Image, page_idx: int, region_idx: int) -> str:
        """
        Exports hand-drawn figure/diagram crop to Obsidian vault attachments and returns markdown link.
        """
        if self.vault_attachments_dir:
            file_name = f"handwriting_p{page_idx}_fig{region_idx}.png"
            out_path = self.vault_attachments_dir / file_name
            image.save(out_path)
            log.info(f"Saved diagram crop to: {out_path}")
            return f"\n![Diagram Page {page_idx} Figure {region_idx}](attachments/{file_name})\n"
        return "\n![Handwritten Diagram](attachments/diagram.png)\n"

    def process_regions(self, regions: List[RegionBox], page_idx: int = 1, logger: Optional[Any] = None) -> str:
        """
        Sequentially routes regions, logs real-time granular progress, accumulates Markdown output, and recycles VRAM.
        """
        output_chunks = []
        total_regs = len(regions)

        for idx, reg in enumerate(regions, start=1):
            reg_info = f"Region [{idx}/{total_regs}] | Type: {reg.region_type.value} | Crop size: {reg.cropped_image.size}"
            
            if logger:
                logger.log_step(reg_info)

            if reg.region_type == RegionType.BLOCK_MATH:
                chunk = self.process_block_math(reg.cropped_image)
            elif reg.region_type == RegionType.DIAGRAM:
                chunk = self.process_diagram(reg.cropped_image, page_idx, idx)
            else: # TEXT_BLOCK
                chunk = self.process_text_block(reg.cropped_image)

            output_chunks.append(chunk)
            
            # Reclaim GPU memory between region crops to keep VRAM usage under 2.5 GB
            self.clear_vram()

        full_md = "\n\n".join(output_chunks)
        return LaTeXSanitizer.sanitize(full_md)
