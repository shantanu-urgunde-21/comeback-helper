import json
import hashlib
from pathlib import Path

class VaultStateTracker:
    """
    Tracks SHA-256 hashes of Markdown files in the Obsidian Vault to allow incremental graph indexing.
    """

    def __init__(self, state_file_path: Path):
        self.state_file_path = state_file_path
        self.state: dict[str, str] = self._load_state()

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
        if self.state.get(rel_key) != current_hash:
            return True
        return False

    def update_file_hash(self, file_path: Path):
        rel_key = str(file_path.resolve())
        self.state[rel_key] = self.compute_file_hash(file_path)

    def remove_file(self, file_path: Path):
        rel_key = str(file_path.resolve())
        self.state.pop(rel_key, None)
