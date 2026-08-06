"""
Handwritten Notes Ingestion Subpackage
Provides image preprocessing, ruling line removal, local Qwen2.5-VL VLM OCR, health check telemetry, and contextual assembly.
"""

from src.ingestion.handwriting.preprocessor import ImagePreprocessor
from src.ingestion.handwriting.ollama_vlm import OllamaVisionOCR
from src.ingestion.handwriting.reassembler import ContextualReassembler
from src.ingestion.handwriting.progress import GranularProgressLogger
from src.ingestion.handwriting.health import OllamaHealthCheck

__all__ = [
    "ImagePreprocessor",
    "OllamaVisionOCR",
    "ContextualReassembler",
    "GranularProgressLogger",
    "OllamaHealthCheck",
]
