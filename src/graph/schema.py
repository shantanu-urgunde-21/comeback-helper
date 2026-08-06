from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class MathEntityType(str, Enum):
    CONCEPT = "Concept"
    THEOREM = "Theorem"
    DEFINITION = "Definition"
    PROOF = "Proof"
    FORMULA = "Formula"
    COURSE = "Course"
    EXAMPLE = "Example"

class MathRelationType(str, Enum):
    DEPENDS_ON = "DEPENDS_ON"
    PROVES = "PROVES"
    USES_FORMULA = "USES_FORMULA"
    DERIVED_FROM = "DERIVED_FROM"
    APPLIES_TO = "APPLIES_TO"
    EQUIVALENT_TO = "EQUIVALENT_TO"
    PREREQUISITE_FOR = "PREREQUISITE_FOR"

class GraphNode(BaseModel):
    name: str = Field(..., description="Name of the mathematical concept, theorem, definition, formula, etc.")
    entity_type: MathEntityType = Field(..., description="The type of mathematical entity")
    description: str = Field("", description="Short summary or definition of the entity")

class GraphEdge(BaseModel):
    source: str = Field(..., description="Name of the source node entity")
    target: str = Field(..., description="Name of the target node entity")
    relation: MathRelationType = Field(..., description="Directional mathematical relationship between source and target")

class MathEntityExtraction(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list, description="List of mathematical entities extracted from text")
    edges: List[GraphEdge] = Field(default_factory=list, description="List of relationships between extracted entities")

ALLOWED_ENTITIES: List[str] = [e.value for e in MathEntityType]
ALLOWED_RELATIONS: List[str] = [r.value for r in MathRelationType]

SCHEMA_SYSTEM_PROMPT = """
You are a mathematical knowledge graph extraction engine.
Extract mathematical entities (Concepts, Theorems, Definitions, Proofs, Formulas, Examples) and their directional relationships from the text.
Only extract clear, relevant mathematical entities.
"""
