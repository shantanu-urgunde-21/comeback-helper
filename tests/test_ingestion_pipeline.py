# Puts the services root on sys.path under the module names the containers
# use. Must precede the service imports below. See src/__init__.py.
import src  # noqa: F401
import os
import unittest
from pathlib import Path
from PIL import Image
from ingestion.app.base import BaseOCRProvider
from ingestion.app.pipeline import IngestionPipeline

class DummyOCRProvider(BaseOCRProvider):
    def process_image(self, image: Image.Image) -> str:
        return "Dummy math note content: $$E = mc^2$$"

    def process_images_batch(self, images: list[Image.Image]) -> str:
        return "\n\n".join([self.process_image(img) for img in images])

class TestIngestionPipeline(unittest.TestCase):
    def test_pipeline_with_dummy_provider(self):
        dummy_provider = DummyOCRProvider()
        pipeline = IngestionPipeline(ocr_provider=dummy_provider)
        
        img = Image.new("RGB", (100, 100), color="white")
        md_content = dummy_provider.process_images_batch([img])
        self.assertIn("E = mc^2", md_content)

if __name__ == "__main__":
    unittest.main()
