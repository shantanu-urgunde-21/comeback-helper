from abc import ABC, abstractmethod
from pathlib import Path
from PIL import Image

class BaseOCRProvider(ABC):
    """
    Abstract Base Class for OCR Providers (Gemini Vision, Baidu Unlimited-OCR, etc.).
    """
    
    @abstractmethod
    def process_image(self, image: Image.Image) -> str:
        """
        Converts a single PIL Image into clean Markdown/LaTeX.
        """
        pass

    @abstractmethod
    def process_images_batch(self, images: list[Image.Image]) -> str:
        """
        Converts a batch of PIL Images into clean Markdown/LaTeX.
        """
        pass
