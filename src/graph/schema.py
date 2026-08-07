from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class MathEntityType(str, Enum):
    AXIOM = "Axiom"
    DEFINITION = "Definition"
    LEMMA = "Lemma"
    THEOREM = "Theorem"
    COROLLARY = "Corollary"
    PROOF = "Proof"
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
