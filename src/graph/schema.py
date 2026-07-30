from enum import Enum
from typing import List

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

ALLOWED_ENTITIES: List[str] = [e.value for e in MathEntityType]
ALLOWED_RELATIONS: List[str] = [r.value for r in MathRelationType]

SCHEMA_SYSTEM_PROMPT = """
You are a mathematical knowledge graph extraction engine.
Extract entities and relationships from the provided mathematical text according to this exact schema:

Entity Types:
- Concept (e.g. Eigenvalue, Principal Component Analysis, Vector Space)
- Theorem (e.g. Spectral Theorem, Cauchy-Schwarz Inequality)
- Definition (e.g. Definition of Covariance Matrix)
- Formula (e.g. Characteristic Equation)
- Proof (e.g. Proof of Orthogonality)
- Course (e.g. Machine Learning, Linear Algebra)

Allowed Relationship Types:
- DEPENDS_ON
- PROVES
- USES_FORMULA
- DERIVED_FROM
- APPLIES_TO
- EQUIVALENT_TO
- PREREQUISITE_FOR

Do NOT create generic or arbitrary relationships. Only use the listed Relationship Types.
"""
