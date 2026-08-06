import torch
from PIL import Image
from transformers import LightOnOcrForConditionalGeneration, LightOnOcrProcessor

from src.ingestion.base import BaseOCRProvider
from src.ingestion.sanitizer import LaTeXSanitizer
from src.logger import log

class LightOnOCRProvider(BaseOCRProvider):
    """
    Offline local OCR provider using LightOnOCR-2-1B on local GPU/CPU.
    Uses official LightOnOcrForConditionalGeneration & LightOnOcrProcessor.
    """
    def __init__(self, model_id: str = "lightonai/LightOnOCR-2-1B"):
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.processor = None
        self.model = None

    def _load_model(self):
        if self.model is not None and self.processor is not None:
            return

        log.info(f"Loading local model '{self.model_id}' on device: {self.device} ({self.dtype})...")
        self.processor = LightOnOcrProcessor.from_pretrained(self.model_id)
        self.model = LightOnOcrForConditionalGeneration.from_pretrained(
            self.model_id,
            torch_dtype=self.dtype
        ).to(self.device)
    def unload_model(self):
        """
        Unloads model from RAM/VRAM and clears PyTorch CUDA memory cache.
        """
        import gc
        self.model = None
        self.processor = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        log.info("Unloaded model and cleared PyTorch memory cache.")

    def process_image(self, image: Image.Image) -> str:
        """
        Processes a single page image locally using LightOnOCR-2-1B.
        """
        self._load_model()

        conversation = [{"role": "user", "content": [{"type": "image", "image": image}]}]
        
        inputs = self.processor.apply_chat_template(
            conversation,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        )

        # Move floating point inputs to target dtype (float16/float32) and device
        inputs = {
            k: v.to(device=self.device, dtype=self.dtype) if v.is_floating_point() else v.to(self.device)
            for k, v in inputs.items()
        }

        with torch.no_grad():
            output_ids = self.model.generate(**inputs, max_new_tokens=1536, do_sample=False)
            # Slice newly generated tokens starting after prompt length
            generated_ids = output_ids[0, inputs["input_ids"].shape[1]:]
            raw_text = self.processor.decode(generated_ids, skip_special_tokens=True)

        return LaTeXSanitizer.sanitize(raw_text)

    def process_images_batch(self, images: list[Image.Image]) -> str:
        """
        Processes a batch of page images sequentially.
        """
        results = []
        for idx, img in enumerate(images, start=1):
            log.info(f"Processing page {idx}/{len(images)}...")
            parsed_page = self.process_image(img)
            results.append(f"<!-- Page {idx} -->\n{parsed_page}")
        return "\n\n".join(results)
