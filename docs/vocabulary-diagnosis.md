# Vocabulary Diagnosis: Type and Relation Collapse

Why the graph is 76% `Concept` and 78.5% `DEPENDS_ON`, what is a category error versus an
implementation bug, and what the redesign has to change.

Measurements taken **2026-08-24** against `.storage/graph.json` (75 nodes, 121 edges, 13
notes), after plan.md Phases 0–7. Reproduce with `python scripts/graph_health.py` and the
snippets inline below.

Companion to [diagnosis.md](diagnosis.md), which covers the *identity* defects (D1–D4, fixed).
This document covers D5/D6, which it recorded but did not fix.

---

## Summary

| | Declared | Ever used | Dominant value |
|---|---|---|---|
| `MathEntityType` | 9 | 4 | `Concept` — 76.0% |
| `MathRelationType` | 7 | 5 | `DEPENDS_ON` — 78.5% |

```
EDGES (121)                      NODES (75)
  DEPENDS_ON       95  78.5%       Concept      57  76.0%
  USES_DEFINITION  15  12.4%       Theorem      10  13.3%
  USES_LEMMA        5   4.1%       Definition    6   8.0%
  COROLLARY_OF      4   3.3%       Formula       2   2.7%
  PROVES            2   1.7%
```

Zero `Axiom`, `Lemma`, `Corollary`, `Proof`, `Example` nodes. Zero `USES_AXIOM` edges.

**These numbers have not moved.** diagnosis.md measured 77.4% `DEPENDS_ON` / 74% `Concept`
before Phases 0–2. Identity was fixed; vocabulary was not touched.

---

## The five problems

### V1 — `Concept` is simultaneously the default and the residual category

Three reinforcing causes:

1. **Schema default.** `GraphNode.entity_type` defaults to `MathEntityType.CONCEPT`
   ([schema.py](../services/graph/app/schema.py)). Under structured output, any omission
   silently becomes `Concept`.
2. **Prompt priming.** `PASS1_NODE_PROMPT` rule 2 reads *"EXTRACT ONLY formal mathematical
   concept names"*, and all five worked examples are object-like (`Integrating Factor`,
   `Separable ODE`, …).
3. **No selection criteria.** The prompt lists six of the nine types in its preamble and
   then never says how to choose among them. Rule 4 asks for "a formal 1-2 sentence
   definition description" for *every* node — framing everything as definable, i.e.
   concept-shaped.

Consequence: nodes whose names literally contain their own type are typed `Concept`.

```
Schwarz's Theorem                      [Concept]
First Fundamental Theorem of Calculus  [Concept]
Abel's Lemma                           [Concept]
```

**Implementation bug.** Fixable by prompt and default changes.

### V2 — `Lemma` / `Corollary` / `Axiom` are relational roles, not intrinsic types

Whether a statement is a lemma is not a property *of the statement*. `Abel's Lemma` is a
lemma because `Abel's Identity` is proved from it; the identical statement in another text
is a theorem. "Axiom" means *assumed rather than proved in this development*. "Corollary"
means *follows easily from X* — a relation to X.

Pass 1 sees one chunk. Argument role is a whole-document property. Asking a per-chunk
extractor for it is a category error, and the graph already demonstrates the correct
alternative:

> **4 `COROLLARY_OF` edges. 0 `Corollary` nodes.**
>
> The relation captured the fact. The node type structurally could not.

`Concept` vs `Theorem` is fuzzy for a *different* reason: they are not on one axis at all.
`Concept` names a mathematical object or idea; `Theorem` names a proven statement. A named
theorem is both a statement *and* a referenceable entity, so it satisfies either label.

The enum flattens **three orthogonal questions** into one 9-valued field:

| Question | Values it produced |
|---|---|
| What kind of thing is it? | Concept, Definition, Formula, Example, Proof |
| What is its epistemic status? | Axiom (assumed) vs the rest (proven) |
| What is its role in an argument? | Lemma, Theorem, Corollary |

**Genuine category error.** Not fixable by prompting.

### V3 — Pass 2 is type-blind

`_extract_edges_pass` builds the prompt's dictionary as `{concept_id: display_name}`. Node
kinds and roles are never passed. Relation choice is therefore unconstrained by what the
endpoints actually are:

```
USES_LEMMA  →  First Fundamental Theorem of Calculus   (a theorem, not a lemma)
PROVES      →  Uniform Lipschitz Continuity [Definition] (definitions are not proved)
```

The prompt also calls the map a "CONCEPT DICTIONARY" and every entry a "concept",
reinforcing the flattening.

**Implementation bug — and the cheapest high-leverage fix.**

### V4 — Only `DEPENDS_ON` has stated semantics

`PASS2_EDGE_PROMPT` rule 2 lists six relations by name. Rule 3 defines exactly one:

> `DEPENDS_ON(A, B)` means A requires B — B is the more foundational concept.

The defined relation takes 78.5%; the five undefined ones split the remaining 21.5%.
`USES_AXIOM` sits at 0 because it presupposes `Axiom` nodes, of which there are none —
an empty category chaining into an empty relation.

**Implementation bug.**

### V5 — The relation set is too poor for mathematics, and it is measurably breaking the graph

Sampling `DEPENDS_ON` edges, at least six distinct mathematical relations are being
flattened into it (labels below are a reading of the pairs, not ground truth):

```
Picard's Theorem       → Lipschitz Condition      has-hypothesis
Picard's Uniqueness    → Peano's Theorem          strengthens / refines
Wronskian Criterion    → Linear Dependence        characterizes (iff)
Peano's Theorem        → Extreme Value Theorem    uses-in-proof
Bungee-Jumping Model   → First Order DE           is-modeled-by / instance-of
Characteristic Equation→ LHODE                    associated construction
Linear Dependence      ↔ Linear Independence      complement — emitted BOTH ways
```

Absent from the vocabulary entirely: generalizes / special-case-of, equivalent-to,
counterexample-to, instance-of, motivates, dual-to.

**The measurable consequence: the graph is not a DAG — 29 cycles.**

```
Well-Posed Problem      → Well-posed IVP        → Well-Posed Problem
Linear Dependence       → Linear Independence   → Linear Dependence
Criterion for Exactness → Exact ODE             → Criterion for Exactness
Exact ODE               → Integrating Factor    → Exact ODE
```

Symmetric or mutual relations (complement, equivalence, mutual characterization) have no
representation, so the extractor emits directional `DEPENDS_ON` in both directions. This
breaks hierarchical layout (level assignment requires a DAG) and corrupts any depth metric
computed over the graph.

Note `Well-Posed Problem ↔ Well-posed IVP` is additionally a residual *identity* near-duplicate,
not purely a relation defect.

**Both.** The missing vocabulary is a design gap; the resulting cycles are a data defect.

---

## Design: split the axes

Replace the single 9-valued `entity_type` with two fields.

### Axis 1 — `kind` (required, intrinsic, always determinable from the text)

| Kind | Means | Example from this vault |
|---|---|---|
| `OBJECT` | A mathematical object, construct, or property | Wronskian, Integrating Factor, Linear Independence |
| `STATEMENT` | A proposition asserted to hold | Schwarz's Theorem, Criterion for Exactness |
| `DEFINITION` | Assigns meaning to a term | Uniform Lipschitz Continuity |
| `METHOD` | A procedure or solution technique | Variation of Parameters, Undetermined Coefficients |
| `FORMULA` | A specific equation or expression | Abel's Identity |
| `PROOF` | An argument establishing a statement | — |
| `EXAMPLE` | A concrete instance or model | Bungee-Jumping Model |

### Axis 2 — `role` (optional; **reported, never inferred**)

`AXIOM`, `THEOREM`, `LEMMA`, `COROLLARY`, `PROPOSITION`, `CONJECTURE`, or absent.

**The rule that resolves V2:** the extractor *transcribes the label the document uses* and
does not judge argument structure. If the text says "Lemma 3.1" or the name is
`Abel's Lemma`, record `LEMMA`. If the text simply states a result, leave `role` absent —
and let edges carry the argument structure, which is where it already works.

Only meaningful when `kind == STATEMENT`.

### Relation vocabulary

| Relation | Meaning | Status |
|---|---|---|
| `DEPENDS_ON` | A requires understanding B | kept (now with competition) |
| `HAS_HYPOTHESIS` | Statement A holds only under condition B | **new** |
| `USES_DEFINITION` | A invokes definition B | kept |
| `USES_IN_PROOF` | A's proof relies on result B | **renamed** from `USES_LEMMA` |
| `PROVES` | A establishes B | kept |
| `COROLLARY_OF` | A follows easily from B | kept |
| `GENERALIZES` | A is a strictly more general form of B | **new** |
| `SPECIAL_CASE_OF` | A is B under added constraints | **new** |
| `EQUIVALENT_TO` | A and B are logically equivalent (**symmetric**) | **new** |
| `CHARACTERIZES` | A is an iff-criterion for property B | **new** |
| `INSTANCE_OF` | A is a concrete example or model of B | **new** |
| `PREREQUISITE_FOR` | inverse of `DEPENDS_ON` | kept, canonicalized away on write |

Dropped: `USES_AXIOM` — 0 uses, and now redundant (`USES_IN_PROOF` to a node with
`role=AXIOM`).

**Symmetric relations must be canonicalized.** `EQUIVALENT_TO(A,B)` and `EQUIVALENT_TO(B,A)`
are the same fact; stored both ways they manufacture a 2-cycle — precisely the V5 failure.
Store symmetric relations in one direction only, ordered by concept id. This is preventive;
repairing the existing 29 cycles is deliberately **out of scope** (separate plan).

---

## What this does not address

- **The 29 existing cycles.** Better vocabulary should reduce *new* ones; repairing current
  data and enforcing DAG-ness is a separate piece of work.
- **D6, taxonomy fragmentation.** `domain`/`subdomain` remain free text. MSC2020 is seeded
  (6,603 codes as of 2026-08-24) but nothing on the write path consults it.
- **Near-duplicate identity residue** such as `Well-Posed Problem` / `Well-posed IVP`.
