import pytest
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from src.ingestion.handwriting_provider import HandwritingOCRProvider
from src.ingestion.handwriting.preprocessor import ImagePreprocessor
from src.ingestion.handwriting.segmenter import CoarseLayoutSegmenter, RegionType

def create_mock_handwritten_page() -> Image.Image:
    """
    Creates a synthetic handwritten note image with text lines, math equation, and a diagram box.
    """
    img = Image.new("RGB", (800, 1000), color=(250, 248, 240))
    draw = ImageDraw.Draw(img)
    
    # Header & Handwritten text lines
    draw.text((50, 50), "Lecture 4: Linear Transformations", fill=(20, 20, 100))
    draw.text((50, 120), "Let T: V -> W be a linear map between vector spaces.", fill=(30, 30, 30))
    draw.text((50, 160), "Definition 1.1 (Kernel and Image)", fill=(30, 30, 30))

    # Block Math equation box
    draw.rectangle([60, 240, 740, 320], outline=(0, 0, 0), width=2)
    draw.text((100, 270), "ker(T) = { v in V | T(v) = 0_W }", fill=(10, 10, 10))

    # Diagram box
    draw.rectangle([100, 400, 500, 700], outline=(150, 50, 50), width=3)
    draw.text((120, 420), "[Diagram: Mapping from V to W]", fill=(150, 50, 50))
    draw.ellipse([150, 480, 280, 650], outline=(50, 150, 50), width=2)
    draw.ellipse([320, 480, 450, 650], outline=(50, 50, 150), width=2)

    # Footer text
    draw.text((50, 800), "Theorem 1.2: dim(V) = dim(ker T) + dim(im T)", fill=(30, 30, 30))
    
    return img

def test_image_preprocessor():
    img = create_mock_handwritten_page()
    preprocessor = ImagePreprocessor()
    processed = preprocessor.preprocess_pil(img)
    assert isinstance(processed, Image.Image)
    assert processed.size == img.size

def test_coarse_layout_segmenter():
    img = create_mock_handwritten_page()
    segmenter = CoarseLayoutSegmenter()
    regions = segmenter.segment(img)
    assert len(regions) > 0
    # Verify regions contain valid RegionBox objects
    for reg in regions:
        assert reg.box is not None
        assert isinstance(reg.region_type, RegionType)
        assert isinstance(reg.cropped_image, Image.Image)

def test_handwriting_ocr_provider(tmp_path: Path):
    img = create_mock_handwritten_page()
    provider = HandwritingOCRProvider(vault_attachments_dir=tmp_path / "attachments")
    result_md = provider.process_image(img, page_idx=1)
    
    assert isinstance(result_md, str)
    assert len(result_md) > 0
    print("\n--- Extracted Markdown Output ---")
    print(result_md)
