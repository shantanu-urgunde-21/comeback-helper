import re
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

# Words dropped before comparing two names for equivalence.
_NORMALIZE_STOP = {"the", "a", "an", "of", "for", "in", "on", "and"}


def normalize(name: str) -> str:
    """Collapses a node id/surface form to a comparison key.

    Lowercases, folds `_`/`-` to spaces, drops punctuation and stopwords, then
    sorts the remaining words so word order can't hide a duplicate. Two
    strings with the same key are the same concept under any spelling
    convention. Lifted from scripts/graph_health.py so the identity layer
    (schema.py, authority.py) and the read-only health report use exactly the
    same fold.
    """
    s = name.lower().replace("_", " ").replace("-", " ").replace("'", "")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(sorted(w for w in s.split() if w not in _NORMALIZE_STOP))


class MathEntityType(str, Enum):
    AXIOM = "Axiom"
    DEFINITION = "Definition"
    LEMMA = "Lemma"
    THEOREM = "Theorem"
    COROLLARY = "Corollary"
    PROOF = "Proof"
    FORMULA = "Formula"
    EXAMPLE = "Example"
    CONCEPT = "Concept"


class MathRelationType(str, Enum):
    USES_AXIOM = "USES_AXIOM"
    USES_DEFINITION = "USES_DEFINITION"
    USES_LEMMA = "USES_LEMMA"
    PROVES = "PROVES"
    COROLLARY_OF = "COROLLARY_OF"
    PREREQUISITE_FOR = "PREREQUISITE_FOR"
    DEPENDS_ON = "DEPENDS_ON"


class Provenance(BaseModel):
    doc_id: str = Field(..., description="Unique hash or ID of source vault note")
    doc_title: str = Field(..., description="Title of source document note")
    doc_path: str = Field("", description="Relative path in Obsidian vault")
    page_number: Optional[int] = Field(None, description="Page number in OCR PDF")
    section_heading: Optional[str] = Field(None, description="Surrounding heading section")
    exact_quote: str = Field("", description="Exact verbatim LaTeX sentence or snippet")


def normalize_domain_casing(value: str) -> str:
    """Canonicalizes a domain string's whitespace/casing.

    "Differential Equations" and "differential equations" are the same
    domain, but as free text they compare unequal — which silently splits
    one subject into two buckets anywhere domain drives grouping or color
    (e.g. the graph's domain-colored rendering). This is a stopgap; the
    real fix is a closed domain vocabulary (e.g. MSC2020 codes) instead of
    free text, which removes the ambiguity instead of normalizing around it.
    """
    return value.strip().title() if value else value


class ConceptTaxonomy(BaseModel):
    domain: str = Field("General Math", description="Tier 1 Discipline (e.g. Differential Equations, Calculus, Linear Algebra)")
    subdomain: str = Field("General", description="Tier 2 Area (e.g. First-Order ODEs, Multivariable Calculus)")
    topic: str = Field("General", description="Tier 3 Specific Topic (e.g. Integrating Factors, Spectral Theorem)")

    @field_validator("domain", mode="before")
    @classmethod
    def _normalize_domain(cls, value):
        return normalize_domain_casing(value) if isinstance(value, str) else value


class GraphNode(BaseModel):
    id: str = Field("", description="Canonical ID of the entity")
    name: str = Field(..., description="Display name of mathematical entity")
    entity_type: MathEntityType = Field(MathEntityType.CONCEPT, description="Role type of mathematical entity")
    taxonomy: ConceptTaxonomy = Field(default_factory=ConceptTaxonomy, description="SKOS 3-tier domain taxonomy")
    aliases: List[str] = Field(default_factory=list, description="Alternative names or symbols for entity")
    description: str = Field("", description="Short formal definition or summary")
    provenance: List[Provenance] = Field(default_factory=list, description="Source provenance locations")

    @model_validator(mode="after")
    def populate_id_from_name(self):
        if not self.id and self.name:
            self.id = self.name
        return self


class GraphEdge(BaseModel):
    source: str = Field(..., description="ID of source entity node")
    target: str = Field(..., description="ID of target entity node")
    relation: MathRelationType = Field(..., description="Directional relationship")
    description: Optional[str] = Field(None, description="Short evidence explanation of relationship")
    provenance: List[Provenance] = Field(default_factory=list, description="Source provenance locations")


class MathNodeExtraction(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list, description="Pass 1: Extracted mathematical entity nodes")


class MathEdgeExtraction(BaseModel):
    edges: List[GraphEdge] = Field(default_factory=list, description="Pass 2: Extracted relationship edges")


class MathEntityExtraction(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list, description="List of mathematical entities extracted")
    edges: List[GraphEdge] = Field(default_factory=list, description="List of relationships extracted")
