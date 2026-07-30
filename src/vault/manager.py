import re
from pathlib import Path
from typing import List, Dict, Any

class ObsidianVaultManager:
    """
    Reads, parses, and lists Markdown notes in the Obsidian Vault.
    Extracts [[wikilinks]] and frontmatter tags/metadata.
    """

    WIKILINK_REGEX = re.compile(r"\[\[(.*?)\]\]")
    FRONTMATTER_REGEX = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path.resolve()

    def get_all_notes(self) -> List[Path]:
        """
        Returns all .md files in the vault.
        """
        if not self.vault_path.exists():
            return []
        return list(self.vault_path.rglob("*.md"))

    def extract_wikilinks(self, content: str) -> List[str]:
        """
        Extracts all [[wikilink]] target names from markdown text.
        """
        matches = self.WIKILINK_REGEX.findall(content)
        links = []
        for m in matches:
            # Handle [[link|display text]] -> extract target "link"
            clean_link = m.split("|")[0].strip()
            links.append(clean_link)
        return links
