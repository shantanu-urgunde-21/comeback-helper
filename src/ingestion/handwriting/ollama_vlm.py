import base64
import io
import requests
from PIL import Image
from src.logger import log

class OllamaVisionOCR:
    """
    100% Local Vision-Language OCR Provider using GGUF Quantized models via Ollama.
    Uses Ollama's per-request `num_gpu` and `main_gpu` options for GPU layer offloading.
    """

    def __init__(self, model_name: str = "qwen2.5vl:3b", host: str = "http://localhost:11434", max_dim: int = 1024):
        self.model_name = model_name
        self.host = host.rstrip("/")
        self.max_dim = max_dim

    def _pil_to_base64(self, image: Image.Image) -> str:
        img_copy = image.copy()
        img_copy.thumbnail((self.max_dim, self.max_dim), Image.Resampling.LANCZOS)
        
        buffered = io.BytesIO()
        img_copy.save(buffered, format="JPEG", quality=90)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def process_image(self, image: Image.Image) -> str:
        """
        Sends the full handwritten page image directly to local Ollama Vision model
        with explicit NVIDIA Discrete GPU layer offloading (num_gpu: 99, main_gpu: 0).
        """
        img_b64 = self._pil_to_base64(image)
        prompt = (
            "You are an expert handwritten STEM note OCR engine. "
            "Transcribe this handwritten note page into clean Markdown. "
            "Preserve all headings (#, ##), paragraphs, and lists. "
            "Format math expressions with precision: use $...$ for inline math and $$...$$ for block equations."
        )

        url = f"{self.host}/api/chat"
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [img_b64]
                }
            ],
            "options": {
                "num_gpu": 99,       # Offload ALL layers to NVIDIA Discrete GPU
                "main_gpu": 0,      # Select NVIDIA GTX 1650
                "temperature": 0.1,
                "num_predict": 1024
            },
            "stream": False
        }

        try:
            log.info(f"Sending page image to local Ollama Vision model ('{self.model_name}') [Forcing NVIDIA GPU 1 Offload]...")
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            extracted_text = data.get("message", {}).get("content", "")
            return extracted_text.strip()
        except Exception as e:
            log.error(f"Ollama Vision API call failed: {e}")
            raise RuntimeError(f"Local Ollama Vision processing error: {e}")
