"""
Handwritten Notes Ingestion Subpackage
Provides image preprocessing, ruling line removal, local Qwen2.5-VL VLM OCR, health check telemetry, and contextual assembly.
"""

from .preprocessor import ImagePreprocessor
from .ollama_vlm import OllamaVisionOCR
from .reassembler import ContextualReassembler
from .progress import GranularProgressLogger
from .health import OllamaHealthCheck

__all__ = [
    "ImagePreprocessor",
    "OllamaVisionOCR",
    "ContextualReassembler",
    "GranularProgressLogger",
    "OllamaHealthCheck",
]
