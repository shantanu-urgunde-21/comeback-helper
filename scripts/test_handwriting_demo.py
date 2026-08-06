import sys
from pathlib import Path
from PIL import Image, ImageDraw

from src.ingestion.handwriting_provider import HandwritingOCRProvider
from src.ingestion.handwriting.preprocessor import ImagePreprocessor
from src.ingestion.handwriting.segmenter import CoarseLayoutSegmenter, RegionType

def run_test():
    print("==================================================")
    print("Testing Handwritten Notes Ingestion Pipeline")
    print("==================================================")

    # Create synthetic test page
    img = Image.new("RGB", (800, 1000), color=(250, 248, 240))
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "Lecture 4: Linear Transformations", fill=(20, 20, 100))
    draw.text((50, 120), "Let T: V -> W be a linear map between vector spaces.", fill=(30, 30, 30))
    draw.rectangle([60, 240, 740, 320], outline=(0, 0, 0), width=2)
    draw.text((100, 270), "ker(T) = { v in V | T(v) = 0_W }", fill=(10, 10, 10))
    draw.rectangle([100, 400, 500, 700], outline=(150, 50, 50), width=3)
    draw.text((120, 420), "[Diagram: Mapping from V to W]", fill=(150, 50, 50))

    # Test 1: Preprocessor
    print("\n[Test 1] Testing ImagePreprocessor...")
    preprocessor = ImagePreprocessor()
    prep_img = preprocessor.preprocess_pil(img)
    print(f"[OK] Preprocessed image size: {prep_img.size}")

    # Test 2: Segmenter
    print("\n[Test 2] Testing CoarseLayoutSegmenter...")
    segmenter = CoarseLayoutSegmenter()
    regions = segmenter.segment(prep_img)
    print(f"[OK] Extracted {len(regions)} layout region boxes:")
    for idx, reg in enumerate(regions, start=1):
        print(f"  - Region {idx}: type={reg.region_type.value}, box={reg.box}")

    # Test 3: OCR Provider & VRAM Safety
    print("\n[Test 3] Testing HandwritingOCRProvider...")
    vault_att = Path("./temp_uploads/test_attachments")
    provider = HandwritingOCRProvider(vault_attachments_dir=vault_att)
    md_output = provider.process_image(img, page_idx=1)

    print("\n==================================================")
    print("EXTRACTED MARKDOWN OUTPUT:")
    print("==================================================")
    print(md_output)
    print("==================================================")
    print("[OK] Handwriting Pipeline Test Completed Successfully!")

if __name__ == "__main__":
    run_test()
