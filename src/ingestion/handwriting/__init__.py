"""
Handwritten Notes Ingestion Subpackage
Provides image preprocessing, coarse region segmentation, specialized OCR routing, and contextual assembly.
"""

from src.ingestion.handwriting.preprocessor import ImagePreprocessor
from src.ingestion.handwriting.segmenter import CoarseLayoutSegmenter, RegionBox, RegionType
from src.ingestion.handwriting.ocr_engine import SpecializedOCREngine

__all__ = [
    "ImagePreprocessor",
    "CoarseLayoutSegmenter",
    "RegionBox",
    "RegionType",
    "SpecializedOCREngine",
]
