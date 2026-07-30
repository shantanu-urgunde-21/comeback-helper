import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq

from src.ingestion.base import BaseOCRProvider
from src.ingestion.sanitizer import LaTeXSanitizer

class LightOnOCRProvider(BaseOCRProvider):
    """
    Offline local OCR provider using LightOnOCR-2-1B on local GPU/CPU.
    """
    def __init__(self, model_id: str = "lightonai/LightOnOCR-2-1B"):
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[LightOnOCR] Loading local model '{model_id}' on device: {self.device}...")
        
        try:
            self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
            self.model = AutoModelForVision2Seq.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                trust_remote_code=True
            ).to(self.device)
            print("[LightOnOCR] Model loaded successfully!")
        except Exception as e:
            print(f"[LightOnOCR] Could not load '{model_id}' directly ({e}). Ready for Hugging Face download.")
            self.processor = None
            self.model = None

    def process_image(self, image: Image.Image) -> str:
        """
        Processes a single page image locally using LightOnOCR-2-1B.
        """
        if self.model is None or self.processor is None:
            # Fallback loader
            self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
            self.model = AutoModelForVision2Seq.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                trust_remote_code=True
            ).to(self.device)

        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            generated_ids = self.model.generate(**inputs, max_new_tokens=1536)

        raw_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return LaTeXSanitizer.sanitize(raw_text)

    def process_images_batch(self, images: list[Image.Image]) -> str:
        """
        Processes a batch of page images sequentially.
        """
        results = []
        for idx, img in enumerate(images, start=1):
            parsed_page = self.process_image(img)
            results.append(f"<!-- Page {idx} -->\n{parsed_page}")
        return "\n\n".join(results)
