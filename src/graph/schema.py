from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

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
    CONTAINS = "CONTAINS"

class Provenance(BaseModel):
    doc_id: str = Field(..., description="Unique hash or ID of source vault note")
    doc_title: str = Field(..., description="Title of source document note")
    doc_path: str = Field("", description="Relative path in Obsidian vault")
    page_number: Optional[int] = Field(None, description="Page number in OCR PDF")
    section_heading: Optional[str] = Field(None, description="Surrounding heading section")
    exact_quote: str = Field("", description="Exact verbatim LaTeX sentence or snippet")

class ConceptTaxonomy(BaseModel):
    domain: str = Field("General Math", description="Tier 1 Discipline (e.g. Differential Equations, Calculus, Linear Algebra)")
    subdomain: str = Field("General", description="Tier 2 Area (e.g. First-Order ODEs, Multivariable Calculus)")
    topic: str = Field("General", description="Tier 3 Specific Topic (e.g. Integrating Factors, Spectral Theorem)")

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

class MathEntityExtraction(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list, description="List of mathematical entities extracted")
    edges: List[GraphEdge] = Field(default_factory=list, description="List of relationships extracted")


