"""Filters extracted entity names down to plausible math concepts, rejecting
structural noise (headings, exercise/page labels, sentence fragments) that
would otherwise become spurious graph nodes. Shared by all three extraction
tiers (`llm_extraction.py`, `block_extractor.py`, and `indexer.py`'s
post-LLM validation pass).
"""

import re

NOISE_PATTERN = re.compile(
    r"(?i)^("
    r"exercise|solution|hint|problem|conclusion|example|"
    r"page\s*\d*|lecture\s*notes?|note\s*\d*|figure\s*\d*|"
    r"table\s*\d*|section\s*\d*|chapter\s*\d*|"
    r"from\s|if\s+the\s|the\s+differential|"
    r"lec\s*\d*|q\.?\s*\d+|ans(wer)?|"
    r"assignment|homework|quiz|test|exam"
    r").*"
)

# Minimum meaningful words after stripping articles/prepositions
_STRIP_WORDS = {"a", "an", "the", "of", "in", "on", "for", "to", "and", "or", "is", "are", "was", "were"}


def is_valid_entity(name: str) -> bool:
    """Returns True if the name looks like a real math concept, not noise."""
    clean = name.strip()
    if not clean or len(clean) < 3 or clean.startswith("<!--"):
        return False
    if NOISE_PATTERN.match(clean):
        return False
    words = [w for w in clean.split() if w.lower() not in _STRIP_WORDS]
    if len(words) < 1:
        return False
    return True
