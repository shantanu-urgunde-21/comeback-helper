"""
Centralized Ollama client for text and vision LLM interactions.

Replaces scattered Ollama HTTP calls in:
  - handwriting/ollama_vlm.py (vision OCR)
  - handwriting/reassembler.py (text refinement)
  - handwriting/health.py (health check)
  - graph/indexer.py (graph extraction fallback — NEW)
"""

import base64
import io
import json
from typing import Optional

import requests
from PIL import Image

from src.logger import log


class OllamaClient:
    """
    Unified Ollama HTTP client supporting text chat, vision chat, and health checks.
    """

    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host.rstrip("/")

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def is_available(self, timeout: float = 2.0) -> bool:
        """Returns True if the Ollama service is reachable."""
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=timeout)
            return resp.status_code == 200
        except Exception:
            return False

    def has_model(self, model_name: str, timeout: float = 2.0) -> bool:
        """Returns True if a specific model is pulled and available."""
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=timeout)
            if resp.status_code != 200:
                return False
            models = [m.get("name", "") for m in resp.json().get("models", [])]
            return any(model_name in m for m in models)
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Text Chat (for graph extraction fallback)
    # ------------------------------------------------------------------

    def chat(
        self,
        prompt: str,
        model: str = "llama3.2",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        timeout: int = 120,
        response_format: Optional[str] = None,
    ) -> Optional[str]:
        """
        Sends a text-only chat request to Ollama.
        Returns the response text, or None on failure.

        If response_format is "json", instructs the model to return JSON.
        """
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": False,
        }
        if response_format == "json":
            payload["format"] = "json"

        try:
            resp = requests.post(
                f"{self.host}/api/chat", json=payload, timeout=timeout
            )
            resp.raise_for_status()
            return resp.json().get("message", {}).get("content", "").strip()
        except Exception as e:
            log.warning(f"Ollama text chat failed (model={model}): {e}")
            return None

    # ------------------------------------------------------------------
    # Vision Chat (for handwriting OCR)
    # ------------------------------------------------------------------

    def vision_chat(
        self,
        prompt: str,
        image: Image.Image,
        model: str = "qwen2.5vl:3b",
        temperature: float = 0.1,
        max_tokens: int = 1024,
        max_dim: int = 1024,
        timeout: int = 300,
    ) -> Optional[str]:
        """
        Sends an image + text prompt to an Ollama vision model.
        Returns the response text, or None on failure.
        """
        img_b64 = self._pil_to_base64(image, max_dim)

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [img_b64],
                }
            ],
            "options": {
                "num_gpu": 99,
                "main_gpu": 0,
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": False,
        }

        try:
            log.info(f"Sending image to Ollama vision model '{model}'...")
            resp = requests.post(
                f"{self.host}/api/chat", json=payload, timeout=timeout
            )
            resp.raise_for_status()
            return resp.json().get("message", {}).get("content", "").strip()
        except Exception as e:
            log.error(f"Ollama vision chat failed (model={model}): {e}")
            return None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _pil_to_base64(image: Image.Image, max_dim: int = 1024) -> str:
        img_copy = image.copy()
        img_copy.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img_copy.save(buf, format="JPEG", quality=90)
        return base64.b64encode(buf.getvalue()).decode("utf-8")


# Module-level default instance
_default_client: OllamaClient | None = None


def get_ollama_client() -> OllamaClient:
    """Returns the module-level OllamaClient singleton."""
    global _default_client
    if _default_client is None:
        _default_client = OllamaClient()
    return _default_client
