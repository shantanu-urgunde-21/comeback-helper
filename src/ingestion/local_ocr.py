import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText, AutoModelForCausalLM, AutoModel

from src.ingestion.base import BaseOCRProvider
from src.ingestion.sanitizer import LaTeXSanitizer

class LightOnOCRProvider(BaseOCRProvider):
    """
    Offline local OCR provider using LightOnOCR-2-1B on local GPU/CPU.
    """
    def __init__(self, model_id: str = "lightonai/LightOnOCR-2-1B"):
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = None
        self.model = None

    def _load_model(self):
        if self.model is not None and self.processor is not None:
            return

        print(f"[LightOnOCR] Loading local model '{self.model_id}' on device: {self.device}...")
        self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
        
        try:
            self.model = AutoModelForImageTextToText.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                trust_remote_code=True
            ).to(self.device)
        except Exception:
            try:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    trust_remote_code=True
                ).to(self.device)
            except Exception:
                self.model = AutoModel.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    trust_remote_code=True
                ).to(self.device)

        print("[LightOnOCR] Model loaded successfully!")

    def process_image(self, image: Image.Image) -> str:
        """
        Processes a single page image locally using LightOnOCR-2-1B.
        """
        self._load_model()

        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            if hasattr(self.model, "generate"):
                generated_ids = self.model.generate(**inputs, max_new_tokens=1536)
                raw_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            else:
                outputs = self.model(**inputs)
                raw_text = str(outputs)

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
