"""Shared Gemini -> Ollama fallback ladder.

Every LLM call site in this codebase (graph extraction Pass 1, Pass 2, and
retrieval's answer synthesis) degrades the same way: try each Gemini
candidate model in order (a 429/quota error or any other failure moves on to
the next candidate), then try each local Ollama model in order, then give up.
This module is that ladder, written once.
"""

from typing import Callable, Optional, Sequence, TypeVar

from shared.llm.gemini import get_gemini_client, get_gemini_candidate_models
from shared.llm.ollama import get_ollama_client
from shared.logger import log

T = TypeVar("T")

# Same three local models every call site has tried, in the same order.
DEFAULT_OLLAMA_MODELS: tuple[str, ...] = ("llama3.2", "qwen2.5:3b", "phi3:mini")


def with_gemini_then_ollama(
    try_gemini: Callable[[object, str], T],
    try_ollama: Callable[[str], Optional[T]],
    ollama_models: Sequence[str] = DEFAULT_OLLAMA_MODELS,
) -> tuple[Optional[T], str]:
    """Runs `try_gemini` across candidate Gemini models, then `try_ollama`
    across `ollama_models`.

    `try_gemini(client, model_name)` must raise on failure — any exception
    (rate limit or otherwise) moves on to the next candidate model, matching
    every existing call site's behavior. `try_ollama(model_name)` returns its
    result, or None on failure/no output.

    Returns `(result, method)` where `method` is "gemini", "ollama", or
    "none" — the same three-value contract the extraction passes and the
    query engine already return.
    """
    client = get_gemini_client()
    if client:
        for model_name in get_gemini_candidate_models():
            try:
                return try_gemini(client, model_name), "gemini"
            except Exception as e:
                log.warning(f"Gemini ({model_name}) call failed ({e}), trying candidate...")

    ollama = get_ollama_client()
    if ollama.is_available():
        for model in ollama_models:
            if not ollama.has_model(model):
                continue
            result = try_ollama(model)
            if result is not None:
                return result, "ollama"

    return None, "none"
