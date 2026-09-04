"""Tier 3 fallback: deterministic LaTeX block + heading parser, no LLM.

Runs when both Gemini and Ollama are unavailable or return nothing usable,
and is also the `use_llm=False` path used by tests. Parses LaTeX theorem/
definition environments, typed Markdown headings, and Obsidian wikilinks.
"""

import re

from shared.logger import log
from .extraction_filters import is_valid_entity
from .schema import ConceptTaxonomy, GraphEdge, GraphNode, MathEntityExtraction, MathEntityKind


def block_extraction(text: str, course_domain: str) -> MathEntityExtraction:
    """
    100% offline, deterministic fallback parsing LaTeX environments,
    Markdown headings with typed prefixes, and wikilinks.
    """
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    node_names: set[str] = set()

    def _add_node(name: str, kind: str, desc: str = ""):
        clean = name.strip().rstrip(":")
        if clean in node_names or not is_valid_entity(clean):
            return
        node_names.add(clean)
        nodes.append(
            GraphNode(
                id=clean,
                name=clean,
                kind=kind,
                taxonomy=ConceptTaxonomy(
                    domain=course_domain,
                    subdomain="Course Notes",
                    topic=clean,
                ),
                description=desc or f"{kind}: {clean}",
            )
        )

    # 1. LaTeX environments: \begin{theorem}[Name]...\end{theorem}
    env_pattern = re.compile(
        r"\\begin\{(theorem|definition|lemma|corollary|proof|proposition|axiom)\}"
        r"(?:\[([^\]]+)\])?"
        r"(.*?)"
        r"\\end\{\1\}",
        re.DOTALL | re.IGNORECASE,
    )
    # Maps LaTeX env names to MathEntityKind values
    _ENV_KIND_MAP = {
        "theorem": MathEntityKind.STATEMENT.value,
        "lemma": MathEntityKind.STATEMENT.value,
        "corollary": MathEntityKind.STATEMENT.value,
        "proposition": MathEntityKind.STATEMENT.value,
        "axiom": MathEntityKind.STATEMENT.value,
        "definition": MathEntityKind.DEFINITION.value,
        "proof": MathEntityKind.PROOF.value,
    }
    for match in env_pattern.finditer(text):
        env_type_raw = match.group(1).lower()
        env_name = match.group(2)
        env_body = match.group(3).strip()[:200]
        env_kind = _ENV_KIND_MAP.get(env_type_raw, MathEntityKind.OBJECT.value)
        if env_name and is_valid_entity(env_name):
            _add_node(env_name.strip(), env_kind, env_body)

    # 2. Typed Markdown headings: ## Theorem: Cauchy-Schwarz Inequality
    heading_pattern = re.compile(
        r"^#{1,3}\s+"
        r"(?:(Theorem|Definition|Concept|Lemma|Proof|Formula|Proposition|Corollary|Axiom|Method|Example)"
        r"\s*:\s*)"
        r"(.+)$",
        re.MULTILINE | re.IGNORECASE,
    )
    _HEADING_KIND_MAP = {
        "theorem": MathEntityKind.STATEMENT.value,
        "lemma": MathEntityKind.STATEMENT.value,
        "corollary": MathEntityKind.STATEMENT.value,
        "proposition": MathEntityKind.STATEMENT.value,
        "axiom": MathEntityKind.STATEMENT.value,
        "definition": MathEntityKind.DEFINITION.value,
        "proof": MathEntityKind.PROOF.value,
        "formula": MathEntityKind.FORMULA.value,
        "method": MathEntityKind.METHOD.value,
        "example": MathEntityKind.EXAMPLE.value,
        "concept": MathEntityKind.OBJECT.value,
    }
    for match in heading_pattern.finditer(text):
        htype = match.group(1).lower()
        name = match.group(2).strip().rstrip(":")
        h_kind = _HEADING_KIND_MAP.get(htype, MathEntityKind.OBJECT.value)
        _add_node(name, h_kind)

    # 3. Obsidian wikilinks [[Target Concept]]
    wikilinks = re.findall(r"\[\[(.*?)\]\]", text)
    for link in wikilinks:
        link_clean = link.split("|")[0].strip()
        if (
            is_valid_entity(link_clean)
            and not link_clean.endswith((".png", ".jpg", ".pdf"))
        ):
            _add_node(link_clean, MathEntityKind.OBJECT.value, "Wikilink reference from vault note")
            if nodes and nodes[0].name != link_clean:
                edges.append(
                    GraphEdge(
                        source=nodes[0].name,
                        target=link_clean,
                        relation="DEPENDS_ON",
                    )
                )

    log.info(f"Block extractor found {len(nodes)} nodes and {len(edges)} edges.")
    return MathEntityExtraction(nodes=nodes, edges=edges)
