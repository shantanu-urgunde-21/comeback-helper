"""
Centralized Google Gemini client singleton.

All Gemini API consumers (graph indexer, retrieval engine, OCR provider)
import from here instead of creating their own client instances.
"""

from typing import List
from google import genai
from shared.config import get_settings
from shared.logger import log

_client: genai.Client | None = None


def get_gemini_client() -> genai.Client | None:
    """
    Returns a lazy-initialized Gemini client singleton.
    Returns None if no valid API key is configured.
    """
    global _client
    if _client is not None:
        return _client

    settings = get_settings()
    api_key = settings.gemini_api_key

    if not api_key or api_key.startswith("your_"):
        log.info("No valid Gemini API key configured. Gemini client unavailable.")
        return None

    try:
        _client = genai.Client(api_key=api_key)
        log.info("Gemini GenAI client singleton initialized.")
        return _client
    except Exception as e:
        log.warning(f"Failed to initialize Gemini client: {e}")
        return None


def get_gemini_model_name() -> str:
    """Returns the configured Gemini model name, stripped of 'models/' prefix."""
    return get_settings().gemini_model.replace("models/", "")


def get_gemini_candidate_models() -> List[str]:
    """Returns a prioritized list of Gemini model candidates for automatic rate-limit fallbacks."""
    primary = get_gemini_model_name()
    candidates = [primary, "gemini-flash-latest", "gemini-flash-lite-latest"]
    # Preserve order while stripping duplicates
    seen = set()
    res = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            res.append(c)
    return res
