# Puts the services root on sys.path under the module names the containers
# use. Must precede the service imports below. See src/__init__.py.
import src  # noqa: F401
import unittest
from PIL import Image, ImageDraw
from pathlib import Path
from ingestion.app.handwriting_provider import HandwritingOCRProvider
from ingestion.app.handwriting.preprocessor import ImagePreprocessor
from ingestion.app.handwriting.health import OllamaHealthCheck

def create_mock_handwritten_page() -> Image.Image:
    """
    Creates a synthetic handwritten note image with text lines and math equations.
    """
    img = Image.new("RGB", (800, 1000), color=(250, 248, 240))
    draw = ImageDraw.Draw(img)
    
    # Blue notebook ruling lines
    for y in range(80, 950, 30):
        draw.line([(0, y), (800, y)], fill=(180, 210, 240), width=1)

    # Handwritten text lines & equations
    draw.text((50, 50), "Lecture 4: Fundamental Theorem of Calculus", fill=(20, 20, 100))
    draw.text((50, 120), "Let f be a continuous function on [a, b].", fill=(30, 30, 30))
    draw.text((50, 160), "F(x) = int_a^x f(t) dt", fill=(10, 10, 10))
    draw.text((50, 220), "F'(x) = f(x) for all x in [a, b]", fill=(30, 30, 30))

    return img

class TestHandwritingPipeline(unittest.TestCase):

    def test_image_preprocessor(self):
        img = create_mock_handwritten_page()
        preprocessor = ImagePreprocessor()
        processed = preprocessor.preprocess_pil(img)
        self.assertIsInstance(processed, Image.Image)
        self.assertEqual(processed.size, img.size)

    def test_ollama_health_check(self):
        checker = OllamaHealthCheck()
        health_info = checker.check_health()
        self.assertIn("service_online", health_info)
        self.assertIn("vram", health_info)

    def test_handwriting_ocr_provider(self):
        img = create_mock_handwritten_page()
        tmp_dir = Path("./.storage/test_tmp")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        
        provider = HandwritingOCRProvider(vault_attachments_dir=tmp_dir)
        # Verify provider object initialization and properties
        self.assertIsNotNone(provider.preprocessor)
        self.assertIsNotNone(provider.vision_ocr)

if __name__ == "__main__":
    unittest.main()
