import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Optional

from shared.logger import log


class ObsidianVaultManager:
    """
    Reads, parses, and lists Markdown notes in the Obsidian Vault.
    Extracts [[wikilinks]], frontmatter tags, and tracks SHA-256 state hashes
    to enable incremental graph indexing.
    """

    WIKILINK_REGEX = re.compile(r"\[\[(.*?)\]\]")
    FRONTMATTER_REGEX = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    def __init__(self, vault_path: Path, state_file_path: Optional[Path] = None):
        self.vault_path = vault_path.resolve()
        self.state_file_path = state_file_path or (self.vault_path.parent / "vault_state.json")
        self.state: dict[str, str] = self._load_state()

    def get_all_notes(self) -> List[Path]:
        """Returns all .md files in the vault."""
        if not self.vault_path.exists():
            return []
        return list(self.vault_path.rglob("*.md"))

    def extract_wikilinks(self, content: str) -> List[str]:
        """Extracts all [[wikilink]] target names from markdown text."""
        matches = self.WIKILINK_REGEX.findall(content)
        links = []
        for m in matches:
            clean_link = m.split("|")[0].strip()
            links.append(clean_link)
        return links

    # ------------------------------------------------------------------
    # Incremental SHA-256 State Tracking
    # ------------------------------------------------------------------

    def _load_state(self) -> dict[str, str]:
        if self.state_file_path.exists():
            try:
                return json.loads(self.state_file_path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def save_state(self):
        self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_file_path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    @staticmethod
    def compute_file_hash(file_path: Path) -> str:
        hasher = hashlib.sha256()
        hasher.update(file_path.read_bytes())
        return hasher.hexdigest()

    def is_file_modified(self, file_path: Path) -> bool:
        rel_key = str(file_path.resolve())
        current_hash = self.compute_file_hash(file_path)
        return self.state.get(rel_key) != current_hash

    def update_file_hash(self, file_path: Path):
        rel_key = str(file_path.resolve())
        self.state[rel_key] = self.compute_file_hash(file_path)

    def remove_file_hash(self, file_path: Path):
        rel_key = str(file_path.resolve())
        self.state.pop(rel_key, None)

    def clear_state(self):
        self.state.clear()
        self.save_state()
