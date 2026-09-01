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
    """Retired single-axis enum — kept only for legacy read compatibility.
    New code must use MathEntityKind and StatementRole instead.
    See docs/vocabulary-diagnosis.md V2 and LEGACY_TYPE_MAP below.
    """
    AXIOM = "Axiom"
    DEFINITION = "Definition"
    LEMMA = "Lemma"
    THEOREM = "Theorem"
    COROLLARY = "Corollary"
    PROOF = "Proof"
    FORMULA = "Formula"
    EXAMPLE = "Example"
    CONCEPT = "Concept"


class MathEntityKind(str, Enum):
    """What sort of mathematical thing a node is — intrinsic, always
    determinable from the text that introduces it. Axis 1 of 2; see
    docs/vocabulary-diagnosis.md V2 for why this is separate from role.
    """
    OBJECT = "Object"          # a construct or property: Wronskian, Linear Independence
    STATEMENT = "Statement"    # a proposition asserted to hold
    DEFINITION = "Definition"  # assigns meaning to a term
    METHOD = "Method"          # a procedure: Variation of Parameters
    FORMULA = "Formula"        # a specific equation: Abel's Identity
    PROOF = "Proof"            # an argument establishing a statement
    EXAMPLE = "Example"        # a concrete instance or model


class StatementRole(str, Enum):
    """The label the source document applies to a statement.

    REPORTED, NEVER INFERRED. Whether a result is a lemma or a theorem is a
    property of how an argument uses it, not of the statement — so this is
    only set when the text says so (a heading "Lemma 3.1", or a name like
    "Abel's Lemma"). Otherwise it stays None and the argument structure
    lives in edges (COROLLARY_OF, USES_IN_PROOF), which is where it already
    worked. Only meaningful when kind == STATEMENT.
    """
    AXIOM = "Axiom"
    THEOREM = "Theorem"
    LEMMA = "Lemma"
    COROLLARY = "Corollary"
    PROPOSITION = "Proposition"
    CONJECTURE = "Conjecture"


# Maps the retired single-axis MathEntityType onto (kind, role). Used by the
# GraphNode validator below and by graph_store.load_graph for nodes written
# before this split.
LEGACY_TYPE_MAP: dict[str, tuple[MathEntityKind, "StatementRole | None"]] = {
    "Concept":    (MathEntityKind.OBJECT, None),
    "Definition": (MathEntityKind.DEFINITION, None),
    "Formula":    (MathEntityKind.FORMULA, None),
    "Proof":      (MathEntityKind.PROOF, None),
    "Example":    (MathEntityKind.EXAMPLE, None),
    "Theorem":    (MathEntityKind.STATEMENT, StatementRole.THEOREM),
    "Lemma":      (MathEntityKind.STATEMENT, StatementRole.LEMMA),
    "Corollary":  (MathEntityKind.STATEMENT, StatementRole.COROLLARY),
    "Axiom":      (MathEntityKind.STATEMENT, StatementRole.AXIOM),
}


class MathRelationType(str, Enum):
    DEPENDS_ON = "DEPENDS_ON"            # A requires understanding B
    HAS_HYPOTHESIS = "HAS_HYPOTHESIS"    # statement A holds only under condition B
    USES_DEFINITION = "USES_DEFINITION"  # A invokes definition B
    USES_IN_PROOF = "USES_IN_PROOF"      # A's proof relies on result B
    PROVES = "PROVES"                    # A establishes B
    COROLLARY_OF = "COROLLARY_OF"        # A follows easily from B
    GENERALIZES = "GENERALIZES"          # A is a strictly more general form of B
    SPECIAL_CASE_OF = "SPECIAL_CASE_OF"  # A is B under added constraints
    EQUIVALENT_TO = "EQUIVALENT_TO"      # A iff B — symmetric, see SYMMETRIC_RELATIONS
    CHARACTERIZES = "CHARACTERIZES"      # A is an iff-criterion for property B
    INSTANCE_OF = "INSTANCE_OF"          # A is a concrete example or model of B
    PREREQUISITE_FOR = "PREREQUISITE_FOR"  # inverse of DEPENDS_ON; canonicalized away on write


# Relations asserting a mutual fact. Stored in exactly one direction (ordered
# by endpoint id) so that A~B and B~A cannot both persist and form a 2-cycle.
SYMMETRIC_RELATIONS = frozenset({"EQUIVALENT_TO"})


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
    kind: MathEntityKind = Field(..., description="What sort of mathematical thing this is (required, no default)")
    role: Optional[StatementRole] = Field(None, description="Label the document applies to a statement; None unless stated")
    taxonomy: ConceptTaxonomy = Field(default_factory=ConceptTaxonomy, description="SKOS 3-tier domain taxonomy")
    aliases: List[str] = Field(default_factory=list, description="Alternative names or symbols for entity")
    description: str = Field("", description="Short formal definition or summary")
    provenance: List[Provenance] = Field(default_factory=list, description="Source provenance locations")

    @model_validator(mode="before")
    @classmethod
    def _coerce_legacy_entity_type(cls, data):
        """Accepts pre-split `entity_type` input and splits it onto (kind, role).

        Keeps old graph.json rows, old fixtures, and any LLM output that
        still emits the retired field loadable. An explicit `kind` always
        wins over a legacy `entity_type`.
        """
        if not isinstance(data, dict):
            return data
        legacy = data.pop("entity_type", None)
        if legacy is not None and not data.get("kind"):
            key = getattr(legacy, "value", legacy)
            kind, role = LEGACY_TYPE_MAP.get(str(key), (MathEntityKind.OBJECT, None))
            data["kind"] = kind
            if role is not None and not data.get("role"):
                data["role"] = role
        return data

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
