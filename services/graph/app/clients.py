"""HTTP clients standing in for what used to be in-process imports.

`indexer.py` was written against local objects (`ObsidianVaultManager`, an
injected vector store). Isolating it into its own service turns those into
network calls. These clients keep the original method surfaces so the
extracted code did not have to be rewritten — only its imports changed.

Each client is deliberately thin and synchronous. The point of this phase is
to make the service boundaries explicit and runnable, not fast.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from shared.logger import log

VAULT_URL = "http://vault:8001"
VECTOR_URL = "http://vector:8003"
TIMEOUT = 60


class ObsidianVaultManager:
    """Client for the vault service.

    Mirrors the in-process class the indexer used to construct directly.
    Note the shape mismatch this exposes: the original returned `Path`
    objects the indexer then opened itself. Across a network it cannot, so
    `read_note()` is added and `get_all_notes()` returns paths that are only
    meaningful to the vault service. Call sites that do `note_path.read_text()`
    must move to `read_note()` when the indexer is rewritten.
    """

    def __init__(self, vault_path: Optional[Path] = None, state_file_path: Optional[Path] = None,
                 base_url: str = VAULT_URL):
        self.base_url = base_url.rstrip("/")
        self.vault_path = vault_path
        self.state_file_path = state_file_path

    def _get(self, path: str, **params) -> Any:
        r = requests.get(f"{self.base_url}{path}", params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, payload: dict) -> Any:
        r = requests.post(f"{self.base_url}{path}", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()

    def get_all_notes(self) -> List[Path]:
        return [Path(p) for p in self._get("/notes")["notes"]]

    def read_note(self, note_path: Path) -> str:
        return self._get("/note", path=str(note_path))["content"]

    def is_file_modified(self, file_path: Path) -> bool:
        return self._get("/state/modified", path=str(file_path))["modified"]

    def update_file_hash(self, file_path: Path) -> None:
        self._post("/state/update", {"path": str(file_path)})

    def save_state(self) -> None:
        self._post("/state/save", {})

    def clear_state(self) -> None:
        self._post("/state/clear", {})


class VectorStoreClient:
    """Client for the vector service.

    Only `search_similar` is used, for Pass 2 candidate context (existing
    concept names fed into the edge-linking prompt). Entity resolution no
    longer needs embeddings at all (see `_resolve_entity` in indexer.py), and
    candidate context is expected to move to the concept table rather than
    chunk search in a later phase — at that point this client goes away
    entirely. See plan.md.
    """

    def __init__(self, base_url: str = VECTOR_URL):
        self.base_url = base_url.rstrip("/")

    def search_similar(self, query: str, top_k: int = 5, course: Optional[str] = None,
                       query_type: str = "hybrid") -> List[Dict[str, Any]]:
        try:
            r = requests.post(
                f"{self.base_url}/search",
                json={"query": query, "top_k": top_k, "course": course, "query_type": query_type},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            return r.json()["results"]
        except Exception as e:
            log.warning(f"Vector search failed ({e}). Returning empty result list.")
            return []
