"""
Atlas schema — Model B.

The atom is a *statement in a context*, not a concept. Concepts are the
vocabulary statements are written in, and every structural relation the old
concept graph asserted (GENERALIZES, DEPENDS_ON, the abstraction level, the
disambiguation group) is derived here rather than extracted:

    abstraction level      position in the context lattice
    generalises            same slogan, contexts ordered by the lattice
    definitional depends   terms occurring in a definition
    disambiguation         terms sharing a name across different contexts

See docs/ATLAS_DESIGN.md Part III.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class Status(str, Enum):
    THEOREM = "THEOREM"
    FALSE = "FALSE"          # requires a witness
    DEFINITION = "DEFINITION"
    OPEN = "OPEN"


class TermKind(str, Enum):
    OBJECT = "OBJECT"                # Hilbert space, matrix
    PROPERTY = "PROPERTY"            # normal, compact, exact
    CONSTRUCTION = "CONSTRUCTION"    # quotient, integrating factor
    OPERATOR = "OPERATOR"            # derivative, Wronskian


class Role(str, Enum):
    THEOREM = "Theorem"
    LEMMA = "Lemma"
    COROLLARY = "Corollary"
    PROPOSITION = "Proposition"
    DEFINITION = "Definition"
    AXIOM = "Axiom"
    METHOD = "Method"                # solution procedures, which ODE notes are full of


class ProvenanceKind(str, Enum):
    SEED = "SEED"            # curated backbone
    USER = "USER"            # confirmed by the student; never overwritten
    EXTRACTED = "EXTRACTED"  # stated in the student's own notes
    INFERRED = "INFERRED"    # model background knowledge, not in any note


class Provenance(BaseModel):
    doc_title: str = ""
    doc_path: str = ""
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    exact_quote: str = ""


class Term(BaseModel):
    """A defined name, scoped to the context that defines it."""

    name: str
    context: str
    kind: TermKind = TermKind.PROPERTY
    definition_latex: str = ""
    uses_terms: List[str] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)
    provenance_kind: ProvenanceKind = ProvenanceKind.EXTRACTED
    provenance: List[Provenance] = Field(default_factory=list)

    @property
    def key(self) -> str:
        """Identity is the pair — `normal@Group` never merges with `normal@Hilbert`."""
        return f"{self.name}@{self.context}"


class Statement(BaseModel):
    """The atom: an assertion that lives in exactly one context."""

    id: str = ""
    context: str
    slogan: str                       # join key for the generalisation ladder
    hypotheses: List[str] = Field(default_factory=list)
    conclusion: str = ""
    statement_latex: str = ""
    status: Status = Status.THEOREM
    witness: Optional[str] = None     # required when status is FALSE
    role: Optional[Role] = None
    provenance_kind: ProvenanceKind = ProvenanceKind.EXTRACTED
    provenance: List[Provenance] = Field(default_factory=list)
    uses_terms: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _default_id(self):
        if not self.id:
            slug = "".join(
                ch if ch.isalnum() else "_" for ch in self.slogan.lower()
            ).strip("_")[:60]
            self.id = f"{self.context}:{slug}"
        return self


class Witness(BaseModel):
    """An object that inhabits or fails a context — what makes a FALSE useful."""

    id: str
    name: str
    description: str = ""
    inhabits: List[str] = Field(default_factory=list)
    satisfies: List[str] = Field(default_factory=list)
    fails: List[str] = Field(default_factory=list)
    provenance_kind: ProvenanceKind = ProvenanceKind.EXTRACTED


class NoteExtraction(BaseModel):
    """LLM response shape for one note."""

    statements: List[Statement] = Field(default_factory=list)
    terms: List[Term] = Field(default_factory=list)
