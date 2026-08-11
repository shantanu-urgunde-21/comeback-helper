# The Atlas Design

> Design specification for turning Comeback Helper's knowledge graph from a
> note-link visualiser into a **navigable atlas of mathematics**.
>
> Status: proposal · Written: 2026-08-12 · Supersedes the graph portions of
> [`knowledge_graph_redesign.md`](./knowledge_graph_redesign.md)
>
> Contains **two competing models** (Parts II and III) over one shared analysis
> (Part I), with a comparison and a decision procedure in Part IV. Nothing here
> is implemented yet.

---

## 0. Contents

**Part I — Shared analysis** (applies to either model)

1. [Intent](#1-intent)
2. [Diagnosis: why the current graph fails](#2-diagnosis-why-the-current-graph-fails)
3. [Prior art — and whether it worked](#3-prior-art--and-whether-it-worked)
4. [Design lessons extracted](#4-design-lessons-extracted)
5. [Worked example: the Spectral Theorem](#5-worked-example-the-spectral-theorem)
6. [Worked example: compactness (conditional edges)](#6-worked-example-compactness-conditional-edges)

**Part II — Model A: concept-primary** (evolution of the current code)

7. [Model A: the model](#7-model-a-the-model)
8. [Model A: the representation](#8-model-a-the-representation)
9. [Model A: construction pipeline](#9-model-a-construction-pipeline)

**Part III — Model B: the context lattice** (a different shape)

10. [Model B: statements indexed by a context lattice](#10-model-b-statements-indexed-by-a-context-lattice)
11. [Model B: the representation — lenses](#11-model-b-the-representation--lenses)
12. [Model B: construction](#12-model-b-construction)

**Part IV — Decision**

13. [Choosing between the models](#13-choosing-between-the-models)
14. [Roadmap](#14-roadmap)
15. [Risks and open questions](#15-risks-and-open-questions)
16. [References](#16-references)

> **How to read this.** Part I is settled: the diagnosis and the prior-art
> evidence hold whichever way you go. Parts II and III are **two different
> answers** to the same problem, not two phases of one plan. Model A evolves the
> existing schema; Model B changes what the atoms are. §13 compares them
> honestly and proposes a cheap experiment to decide.

---

# Part I — Shared analysis

> *The diagnosis and the evidence below hold whichever model you choose.*

## 1. Intent

Mathematics is unusually well-suited to graph representation and unusually
badly served by it in practice. Concepts are dense with dependency; a single
term (*normal*, *compact*, *regular*, *simple*) names several inequivalent
things depending on the field; and the same theorem exists at four or five
levels of abstraction simultaneously, each level gated by different hypotheses.

The goal is a **centralised, visual, navigable structure** in which:

- a concept can be seen at abstract and concrete levels *at the same time*;
- an implication carries the conditions under which it actually holds;
- name collisions across fields are rendered as distinctions, not merged away;
- the whole thing is built from the student's own coursework and stays theirs.

The graph is not a feature of the product. **The graph is the product.**
Ingestion, the vault, and RAG are the supply chain that feeds it.

A secondary, later goal: the vocabulary should generalise beyond mathematics to
any field with formal structure. Section 7 keeps this in view.

---

## 2. Diagnosis: why the current graph fails

Assessed against the current rendering (~30 nodes, `graph.json` v2.4.0) and
[`src/graph/indexer.py`](../src/graph/indexer.py).

| # | Failure | Location | Effect |
|---|---------|----------|--------|
| 1 | **Note nodes dominate the picture.** A `CONTAINS` edge is added from the note to every concept it mentions. | [`indexer.py:551`](../src/graph/indexer.py#L551) | The largest hubs and the majority of edges encode "appeared on the same page" — provenance, not mathematics. Estimated 60–70% of visible edges. |
| 2 | **No semantic axis.** Node position is pure force-simulation output. | [`static/app.js`](../static/app.js) | Nothing about *where* a node sits means anything. This is why five layout sliders were needed: no arrangement is right because none encodes anything. |
| 3 | **`DEPENDS_ON` and `PREREQUISITE_FOR` are inverses**, both emitted. | [`schema.py:18-27`](../src/graph/schema.py#L18-L27) | Direction is inconsistent, cycles appear, hierarchical layout cannot produce a sensible order. |
| 4 | **Edges are unconditional.** No slot for a hypothesis. | [`schema.py:60-65`](../src/graph/schema.py#L60-L65) | In mathematics `A ⟹ B` is nearly always `A ⟹ B given C`. An edge without `C` is wrong roughly as often as it is right. |
| 5 | **Entity resolution destroys the exact distinction the project exists to show.** Merges any two nodes whose *names* embed within 0.88 cosine. | [`indexer.py:465-496`](../src/graph/indexer.py#L465-L496) | "Normal subgroup" and "normal operator" will merge. So will "compact (topology)" and "compact operator". |

Secondary: the LanceDB `init` placeholder leaks into the concept graph;
[`_get_candidate_context`](../src/graph/indexer.py#L413-L430) feeds note
*filenames* to the edge-linking prompt as though they were concepts.

---

## 3. Prior art — and whether it worked

Six independent lines of work bear on this. None of them is the same product,
but each has already answered a question we would otherwise pay to learn.

### 3.1 Prerequisite graphs as a learning interface

**Knowledge Space Theory → ALEKS.** Doignon & Falmagne (1985) formalised
knowledge as a combinatorial structure: a *surmise relation* over items where
mastering an item implies mastery of its prerequisites, and a *fringe* — the
set of items exactly one step beyond the learner's current state. ALEKS
("Assessment and LEarning in Knowledge Spaces") commercialised this for maths,
chemistry, statistics and accounting.

> **Verdict: worked, decisively — but not at our granularity.** Forty years,
> hundreds of peer-reviewed papers, millions of students, a meta-analysis of
> learning effects (Fang et al. 2019). *However:* ALEKS's items are fine-grained
> **problem types**, not abstract concepts, and its prerequisite structure is
> inferred from **student response data at scale**, not from text. The success
> is evidence for the interface idea, not for building the structure the way we
> intend to.

**Metacademy** (Roger Grosse & Colorado Reed). A hand-curated prerequisite graph
of ML/probabilistic-AI concepts, each node carrying a short description,
learning goals, a time estimate, and curated resources. Selecting a concept
generated an ordered **learning plan** — the transitive prerequisite closure,
topologically sorted. Widely admired; described at the time as "a package
manager for knowledge."

> **Verdict: the UX worked; the content model didn't scale.** The concept →
> closure → ordered plan interaction is the right one and we should copy it
> directly. But content stayed concentrated in ML because every node was
> hand-written, and the project appears long dormant (repositories show little
> recent activity; I could not reach the site during this research, so treat
> "dead" as unconfirmed). **The bottleneck was curation, not the graph engine.**

### 3.2 Does a concept graph actually help anyone learn?

Two meta-analyses, and the second contains the single most actionable finding
in this entire document.

- **Nesbit & Adesope (2006)**, *Review of Educational Research*: 67 effect sizes
  from 55 studies, 5,818 participants, Grade 4 → postsecondary. Concept and
  knowledge maps were associated with increased knowledge retention across
  instructional conditions and settings.
- **Schroeder, Nesbit, Anguiano & Adesope (2018)**, *Educational Psychology
  Review*: 142 independent effect sizes, n = 11,814. Overall **g = 0.58**
  (p < 0.001), effective in both STEM and non-STEM domains. Crucially:

  | Activity | Effect size |
  |---|---|
  | **Creating** a concept map | **g = 0.72** |
  | **Studying** a concept map | g = 0.43 |

> **Verdict: worked, with a caveat that should reshape the product.** Node-link
> knowledge representations demonstrably aid learning. But *making* the map is
> worth roughly 1.7× *reading* one. A graph the system generates and the student
> passively views is the weaker of the two interventions we could build.
> **The editing affordance is not a nice-to-have; it is where most of the
> measured benefit lives.** It also happens to be the fix for the trust problem
> in §3.5.

### 3.3 Dependency graphs over formal mathematics

- **Metamath** — every theorem drills down through its dependencies to the
  axioms of logic and set theory; the Proof Explorer makes this interactively
  navigable.
- **Lean / mathlib tooling** — `LeanBlueprint` uses dependency graphs to steer
  formalisation efforts; `LeanDepViz` deliberately produces graphs of *hundreds
  to thousands* of nodes rather than millions, on the explicit grounds that
  millions are not visualisable; `lean-graph` renders per-theorem dependency
  subgraphs; `LeanNets` adds semantic content to each edge, recording **how** a
  dependency is used rather than just that it is.
- **TheoremGraph** (arXiv 2606.25363, 2026) — statement-level dependency graph
  spanning informal and formal maths: 11.7M theorem-like environments parsed
  from arXiv yielding 18.3M candidate dependencies, plus a Lean 4
  elaborator-level extraction of 388,105 declaration nodes and 11.3M typed edges
  across 25 projects, bridged by embedding natural-language "slogans" into a
  shared semantic space.
- **KnowTeX** (arXiv 2601.15294, 2026) — extracts dependencies from LaTeX via a
  `\uses` annotation and emits DOT/TikZ graphs, arguing such graphs should become
  standard in mathematical writing.

> **Verdict: worked at scale, but answers a different question.** These are
> **proof-dependency** graphs: "the proof of X invokes lemma Y." That is not the
> same relation as "you should understand Y before X" — proofs routinely invoke
> machinery a learner meets much later, and conceptual prerequisites routinely
> appear in no proof at all. Do not conflate them. Three transferable specifics:
> **(a)** `LeanDepViz` treating "few thousand nodes" as the visualisable ceiling
> is a direct constraint on our default view; **(b)** `LeanNets` typing *how* an
> edge is used is the same instinct as our `context` field; **(c)** TheoremGraph
> **labels each extraction method so users can trade coverage for precision** —
> adopt this wholesale as our trust tiers (§7.4).

### 3.4 Ontologies that already model mathematics

- **OntoMathPRO 2.0** (arXiv 2303.13542) — the first Linked Open Data ontology of
  professional mathematical knowledge. Two parallel hierarchies: **mathematical
  objects** and **reified relationships**. Three layers: foundational ontology,
  domain ontology, linguistic. Concepts are annotated as **kinds and roles**
  (respecting meta-ontological distinctions from a foundational ontology), with
  multilingual lexicons for how each concept surfaces in natural-language text.
  Built to extract facts from LaTeX papers and publish them as Linked Data.
- **Wikidata qualifiers** — every statement is reified to a statement node
  carrying qualifiers that encode "the validity context of the statement, its
  causality, provenance." Four reification strategies are documented in the
  literature (standard reification, n-ary relations, singleton properties, named
  graphs).
- **Domain-Contextualized Concept Graphs** (arXiv 2510.16802) — argues directly
  that fixed ontologies fail because *domains are treated as implicit context
  rather than explicit reasoning-level components*, and proposes the triple
  `<Concept, Relation@Domain, Concept'>` with 20+ standardised predicates.

> **Verdict: worked, and it means we should not invent a vocabulary.**
> OntoMathPRO independently arrived at **exactly** the two structural moves this
> design needs — splitting *kind* from *role*, and reifying relationships as
> first-class objects. And `Relation@Domain` is, character for character, the
> `context`-on-edges proposal in §7.2. Attaching conditions to an assertion is
> not exotic; it is the mainstream solution, deployed at Wikidata scale.

### 3.5 How good is LLM-built knowledge-graph extraction?

- Entity extraction against expert-annotated datasets: precision 98.82%, recall
  93.18%, F1 95.92%.
- **Relation extraction precision "frequently exceeds 75%."**
- Ontology-constrained extraction shows *low relation hallucination*, and
  hallucinations are **easy to detect** when the relation must conform to a
  supplied ontology and both endpoints must occur in the source text.
- Education-specific: LLM prerequisite-relation extraction beat deep-learning
  baselines by +18.75% accuracy / +16.99% F1; a classifier over a GPT-4-extracted
  prerequisite graph reached 80.0% accuracy across 43 labels in a graduate AI
  course.
- TheoremGraph's LLM-judged cross-graph matching accepted 47,952 matches above
  0.8 cosine, with **acceptance rising to 87% only at the ≥0.9 tier**.

> **Verdict: works well enough to be useful, nowhere near well enough to be
> trusted silently.** ~75% relation precision means **roughly one edge in four
> is wrong.** On a screen of 200 edges that is 50 false claims about mathematics.
> Three direct consequences: constrain the relation vocabulary (proven to lower
> hallucination *and* make it detectable); mark every edge with its extraction
> method; make correction one click. The 0.9-cosine finding is also a direct
> indictment of `_resolve_entity`'s 0.88 threshold **on names alone** — that is
> below the tier where even *description-rich* matching becomes reliable.

### 3.6 Does the visualisation actually work?

- **Obsidian's graph view** is the cautionary tale directly adjacent to us:
  widely described as beautiful but impractical, with a real ceiling around a few
  hundred notes. The critique is precise — it visualises connections but exposes
  no structural insight (no centrality, no communities, no gaps), because it is a
  *note-link visualiser* rather than a typed-entity-and-relation graph.
- **Semantic zoom** — changing representation *type* with scale rather than just
  size — dates to Perlin & Fox's Pad and Pad++; hierarchical aggregation systems
  (Matrix Zoom, ZAME) merge nodes and edges by clustering.
- **But**: evaluation work reports that *most people cannot read* networks using
  hierarchical cluster representations such as super-noding and edge bundling,
  and that **map-like visualisations are superior in task performance,
  memorisation and engagement**. GMap (Gansner, Hu & Kobourov) combines layout
  with clustering, cluster colouring, and drawn *boundaries*, producing
  contiguous territories rather than clouds of dots.

> **Verdict: partly worked — and this corrects the obvious plan.** Semantic zoom
> by clustering, on its own, is *not* validated; super-noding is specifically
> reported as hard for people to read. The evidence favours **map-like rendering
> with drawn regions** plus **filtering to a focused subgraph**, over
> collapse/expand of abstract super-nodes. Obsidian's failure also isolates the
> variable: their graph is untyped, so no amount of layout work could have saved
> it. Typing the edges is the precondition for the picture being worth drawing.

### 3.7 The gap

| Project | Grounded in own notes | Conceptual (not proof) | Hypothesis-aware | Multi-scale visual | Personal / local |
|---|---|---|---|---|---|
| ALEKS | ✗ | ✗ (problem types) | ✗ | ✗ | ✗ |
| Metacademy | ✗ | ✓ | ✗ | partial | ✗ |
| Metamath / mathlib | ✗ | ✗ (proof deps) | implicit | ✗ | ✗ |
| TheoremGraph | ✗ | ✗ (statements) | ✗ | ✗ | ✗ |
| OntoMathPRO | ✗ | ✓ | partial | ✗ | ✗ |
| Obsidian graph | ✓ | ✗ (untyped) | ✗ | ✗ | ✓ |
| **This design** | ✓ | ✓ | ✓ | ✓ | ✓ |

The slot is genuinely unoccupied. Every column has been solved by someone; the
combination has not been assembled, and the pieces that would assemble it are
individually validated.

---

## 4. Design lessons extracted

1. **Make the graph editable.** g = 0.72 vs 0.43. Highest-confidence directive in
   this document, and it doubles as the fix for 25% relation error.
2. **Copy Metacademy's core interaction**: concept → transitive prerequisite
   closure → topologically ordered plan.
3. **Do not conflate proof dependency with conceptual prerequisite.**
4. **Do not invent a vocabulary** — align with OntoMathPRO's kind/role split and
   reified relationships.
5. **Put conditions on edges.** Wikidata qualifiers and `Relation@Domain` are the
   established pattern.
6. **Label extraction provenance and let the user trade coverage for precision**
   (TheoremGraph).
7. **Constrain the relation vocabulary** — proven to reduce and expose
   hallucination.
8. **Raise the merge threshold and gate it by domain**; 0.88 on names alone is
   below the reliability tier.
9. **Cap the default view in the low thousands of nodes** (LeanDepViz).
10. **Prefer map-like regions and focused subgraphs over super-node collapse.**
11. **Curation, not engineering, is the bottleneck** (Metacademy) — so seed the
    spine and automate curation.

---

## 5. Worked example: the Spectral Theorem

Chosen because it exhibits every pathology at once: one name, six inequivalent
statements, three fields, a generalisation ladder, each rung gated by a
hypothesis, and a counterexample that explains why a rung exists.

Vertical position **is** abstraction level. Horizontal is field. Nothing else
moves.

```
 abstract
    ▲
    │        ┌─────────────────────────────────┐
 L4 │        │ ◆ SPECTRAL THEOREM              │   T = ∫ λ dE(λ)
    │        │   (projection-valued measure)   │
    │        └───┬──────────┬─────────────┬────┘
    │            │          │             │        generalizes ▲
 L3 │      ┌─────┴────┐ ┌───┴──────┐ ┌────┴──────┐  specializes ▼
    │      │ unbounded│ │ bounded  │ │ compact   │
    │      │self-adj. │ │normal /H │ │self-adj.  │
    │      └──────────┘ └──────────┘ └────┬──────┘
    │                                     │
 L2 │                              ┌──────┴────────┐        ╭────────────────╮
    │                              │ normal matrix │╌╌╌╌╌╌╌▷│ ⊘ [0 −1; 1  0]  │
    │                              │  A = UΛU*     │ needs  │ normal, but no │
    │                              └──────┬────────┘   ℂ    │ REAL eigenbasis│
    │                                     │                 ╰────────────────╯
 L1 │                              ┌──────┴────────┐
    │                              │ real symmetric│  A = QΛQᵀ
    │                              └───────────────┘
    │
 L0 │   ● PCA          ● QM observables        ≈ Fourier transform
    │     instance-of     instance-of            analogous-to (diagonalising ∂ₓ)
 concrete
    └──────────────────────────────────────────────────────────────────────────▶
         Linear Algebra          Functional Analysis          Applications
```

What this achieves that a force layout structurally cannot:

- **The ladder reads as a ladder.** "Real symmetric is the baby case of normal is
  the baby case of the PVM version" is the most useful single fact about this
  cluster, and it is legible at a glance because *up = more general*.
- **Detailed and abstract coexist in one frame** — the stated goal — because
  abstraction is a *spatial dimension* rather than another edge in the tangle.
- **The counterexample is attached to the edge it blocks.** `[0 −1; 1 0]` is not
  trivia; it is *why* the real-symmetric case needs its own statement.

Under the current system this cluster renders as either one node (merged at 0.88
cosine) or six unrelated nodes. Both are wrong; the truth is one abstract node
and five specialisations joined by `GENERALIZES`.

---

## 6. Worked example: compactness (conditional edges)

```
   sequentially compact ──────── implies ────────▶ compact
                                    │
                                    ├─ holds when:  X is a metric space
                                    │
                                    └─ ⊘ fails for: [0, ω₁)  ordinal space
                                          (seq. compact, not compact)
```

One edge, three pieces of information. The current schema stores the arrow and a
prose blurb. The `holds when` clause **is** the mathematical content; the
counterexample is what makes it stick. Without both, an atlas of mathematics is
a pile of arrows the student has to distrust — which, at 75% precision, is the
correct response.

The compactness family (compact / sequentially compact / countably compact /
limit-point compact) is the ideal first test fixture: four concepts, pairwise
implications that hold *only* under stated hypotheses, and standard separating
counterexamples for each failure.

---

# Part II — Model A: concept-primary

> *Concepts are the atoms; typed relations are the glue. This is the current
> code's shape, corrected and extended. Lower risk, works with what exists,
> inherits the reliability ceiling of §3.5.*

## 7. Model A: the model

Changes to [`src/graph/schema.py`](../src/graph/schema.py).

### 7.1 Split `entity_type` into `kind` and `role`

The current field conflates ontological category with rhetorical function.
OntoMathPRO makes the same split (kinds vs roles); follow it.

| `kind` | Meaning | Examples |
|---|---|---|
| `OBJECT` | A mathematical thing | Hilbert space, matrix, group |
| `PROPERTY` | A predicate on objects | normal, compact, self-adjoint |
| `STATEMENT` | An assertion | Spectral Theorem, Heine–Borel |
| `CONSTRUCTION` | An operation producing objects | quotient, completion, tensor product |
| `EXAMPLE` / `COUNTEREXAMPLE` | A witness | ℝⁿ, the long line, Weierstrass function |

`role` retains the existing `Theorem / Lemma / Corollary / Definition / Axiom`
enum and applies only where `kind = STATEMENT`.

`kind` drives node shape and enables "show me only the objects," which yields a
clean skeleton of any field.

### 7.2 `context` on every edge — the highest-value single field

```python
class GraphEdge(BaseModel):
    source: str
    target: str
    relation: RelationType
    context: Optional[str] = None   # "X metric" · "dim V < ∞" · "char k ≠ 2"
    provenance_kind: ProvenanceKind = ProvenanceKind.EXTRACTED
    confidence: float = 0.0
    provenance: List[Provenance] = []
```

`context` is the ambient hypothesis as a short string. This is the Wikidata
qualifier pattern and the `Relation@Domain` pattern; both are validated at scale.
Pass-2 prompts should demand it and mark the edge low-confidence when the model
cannot supply one.

### 7.3 `abstraction_level: int` (0–5) on nodes

The layout axis. Estimated by Pass 1, then **reconciled against `GENERALIZES`
edges** — a generalisation must sit strictly above its specialisation. That
reconciliation is a free consistency check that catches bad extractions without
any human in the loop.

### 7.4 `provenance_kind` — trust tiers

Direct adoption of TheoremGraph's coverage/precision trade-off.

| Tier | Meaning | Default visibility |
|---|---|---|
| `SEED` | From the curated backbone ontology | always |
| `USER` | Created or confirmed by the student | always, never overwritten |
| `EXTRACTED` | Stated in the student's own notes, with provenance | on |
| `INFERRED` | LLM background knowledge, not in any note | toggleable, visually distinct |

At ~75% relation precision this separation is not optional. `INFERRED` edges are
the ones that make the atlas rich *and* the ones most likely to be wrong; the
student must be able to see which is which.

### 7.5 Relation vocabulary

Current relations are all "uses/depends" flavoured. Add the structural ones, and
**pick a single canonical direction** (drop `PREREQUISITE_FOR` as a stored
relation; it is `DEPENDS_ON` reversed and having both breaks acyclicity).

| Relation | Purpose |
|---|---|
| `GENERALIZES` / `SPECIALIZES_TO` | the vertical axis |
| `DEPENDS_ON` | conceptual prerequisite (single canonical direction) |
| `EQUIVALENT_UNDER` | with `context` carrying the condition — how the compactness family is actually wired |
| `SEPARATES` | counterexample → the pair of concepts it distinguishes |
| `INSTANCE_OF` | PCA → Spectral Theorem |
| `ANALOGOUS_TO` | cross-field structural echo (Galois correspondence ↔ covering spaces) — non-rigorous, often the most illuminating edge on screen, keep visually distinct |

Constraining the vocabulary is itself a quality measure: ontology-conformant
extraction demonstrably lowers hallucination and makes what remains detectable.

### 7.6 Identity and disambiguation

The change that most directly serves the stated intent.

- Node id becomes `name @ subdomain`, not `name`.
- Add `disambiguation_group` so `Normal (group theory)` / `Normal (operator
  theory)` / `Normal (topology)` render as visibly related siblings that can
  **never** merge.
- Rewrite `_resolve_entity`: compare **description** embeddings, not name
  embeddings; require same `domain`; raise the threshold to ≥ 0.92; refuse
  cross-domain merges outright — cross-field similarity is what `ANALOGOUS_TO`
  is for.

### 7.7 On generalising beyond mathematics

`OBJECT / PROPERTY / STATEMENT / CONSTRUCTION / EXAMPLE` and `GENERALIZES /
DEPENDS_ON / EQUIVALENT_UNDER / SEPARATES / INSTANCE_OF` are not mathematical
vocabulary — they are the vocabulary of any formalised field. Keep everything
field-specific confined to the SKOS taxonomy and the seed spine, and later
expansion is a data problem rather than a rewrite. OntoMathPRO's three-layer
split (foundational / domain / linguistic) is the precedent.

---

## 8. Model A: the representation

### 8.1 Immediate structural fixes

- **Remove `Note` nodes and `CONTAINS` edges from the default view.** Provenance
  moves to an inspector panel on node click. Expected to remove the majority of
  visible edges at zero cost to information.
- **Fix `y` from `abstraction_level`; run physics only on `x`.** In vis.js: set
  each node's `y` from its level with `fixed: {y: true}` and keep Barnes-Hut for
  horizontal spread. Semantically meaningful vertical order, organic horizontal
  layout, without hierarchical layout's rigid combing. ~20 lines in
  [`app.js`](../static/app.js), and it obsoletes most of the solver dropdown.

### 8.2 Visual channels

| Channel | Encodes |
|---|---|
| Vertical position | abstraction level |
| Horizontal region | domain (drawn as a **map-like territory**, GMap-style, not a dot cloud) |
| Shape | `kind` |
| Border | `role` |
| Edge style | `GENERALIZES` solid · `DEPENDS_ON` thin grey · `SEPARATES` red dashed · `ANALOGOUS_TO` dotted · `INFERRED` reduced opacity |

Edge labels on hover only, and only for non-`DEPENDS_ON` relations. The existing
decluttering sliders treat the symptom.

### 8.3 Multi-scale — with the evidence-based correction

The obvious plan is semantic zoom by clustering the SKOS taxonomy. The
literature only partly supports it: super-noding and edge bundling are
specifically reported as hard for people to read, while map-like renderings win
on task performance, memorisation and engagement.

So:

1. **Primary mechanism: focused subgraph.** Select a concept → render its
   dependency closure (and optionally its generalisation ladder), topologically
   layered. This is Metacademy's validated interaction and keeps node counts far
   inside LeanDepViz's few-thousand ceiling.
2. **Secondary: map-like domain regions.** Draw domains as coloured, bounded
   territories with concepts inside them, rather than collapsing them into
   super-nodes.
3. **Collapse/expand is available but not the default**, and only per-branch —
   so Functional Analysis can be open at full detail while Algebra stays a
   region.
4. **Hard cap the default view.** Above the cap, fall back to region-level.

### 8.4 The inspector

On node click: statement (LaTeX), hypotheses, `context` of each incident edge,
provenance (note, page, verbatim quote), counterexamples, aliases and
disambiguation siblings. This is where §2 provenance work finally pays off.

### 8.5 Editing — the highest-value feature in this document

Per §3.2 (g = 0.72 vs 0.43) and §3.5 (~75% precision), direct manipulation is
both the strongest learning intervention available and the only viable error
correction path:

- add / retype / redirect / delete an edge in the canvas;
- supply or correct an edge's `context`;
- split a wrongly merged node, or merge two siblings;
- promote an `INFERRED` edge to `USER` by confirming it.

Every such action writes `provenance_kind = USER`, which re-extraction must
never overwrite. Confirming an inferred edge is one click and is *itself* the
studying activity the meta-analysis measures.

---

## 9. Model A: construction pipeline

The current pipeline **cannot** produce §5, and no amount of prompt work will fix
that: almost none of those edges appear in any single lecture note. They are
background structure. Metacademy's experience says curation is the bottleneck;
the answer is to automate curation and seed the spine.

```
 ┌── A. GROUNDED PASS ──────────┐   per note, on ingest
 │  concepts actually stated    │   → provenance_kind = EXTRACTED
 │  + page / heading / verbatim │   → full provenance, high trust
 └──────────────┬───────────────┘
                │
 ┌── B. SEED SPINE ─────────────┐   shipped with the app
 │  ~200–300 backbone concepts  │   → provenance_kind = SEED
 │  levels + GENERALIZES edges  │   → hand-curated once
 └──────────────┬───────────────┘
                │  every ingested note attaches to an existing trunk
                ▼
 ┌── C. CURATION PASS ──────────┐   global, periodic, no note involved
 │  over the concept catalogue: │   → provenance_kind = INFERRED
 │  ladders, equivalences-under │   → toggleable, lower trust
 │  hypotheses, separating       │
 │  counterexamples, analogies  │
 └──────────────┬───────────────┘
                │
 ┌── D. CORRECTION LOOP ────────┐   student edits in the canvas
 │  confirm / fix / split /     │   → provenance_kind = USER
 │  delete                      │   → permanent, never overwritten
 └──────────────────────────────┘
```

**On the seed spine.** Without it, bottom-up extraction from one student's notes
yields an archipelago — which is exactly what the current rendering shows. A
curated trunk of undergraduate mathematics is what makes the atlas *centralised*
in the sense intended, and it is a one-time cost measured in days.

**On the curation pass.** This is where the atlas actually comes from, and it is
the step no existing project in §3 performs: TheoremGraph extracts from corpora,
OntoMathPRO is hand-built, Metacademy was hand-written. Running a background
knowledge model over an already-populated concept catalogue — asking only for
structural relations among concepts *already present* — is a materially easier
task than open-ended extraction, and both endpoints existing in the graph is one
of the conditions under which hallucination is reported to be easy to detect.

**Validation gates** (cheap, no human required):

- `GENERALIZES` must strictly decrease `abstraction_level`.
- No cycles in `DEPENDS_ON` after canonicalisation.
- Both endpoints of every edge must already exist as nodes.
- `EQUIVALENT_UNDER` without a `context` is rejected or demoted.
- Every relation must be in the enum.

---

# Part III — Model B: the context lattice

> *Statements are the atoms; concepts are the vocabulary statements are written
> in. Higher upfront cost, but most of what Model A extracts, Model B computes.*

## 10. Model B: statements indexed by a context lattice

### 10.1 The premise

Model A and the current code share an assumption so basic it never gets stated:
**concepts are the atoms and relations are the glue.** That is the default
knowledge-graph shape, and it is the wrong shape for mathematics.

"Integrating factor" is not a fact. *"For a first-order linear ODE, multiplying
by μ = e^∫p makes the left-hand side an exact derivative"* is a fact. Concepts
are the **vocabulary** that statements are written in. When concepts are made
primary, the actual mathematical content — quantifiers, hypotheses, ambient
structure — has to be smuggled back in as decoration on an arrow.

§7.2's `context: Optional[str]` field is precisely that smuggling: an admission
that the model cannot hold the real content, patched with free text.

Model B makes the statement primary and the ambient theory structural. The
consequence that matters: **most of what Model A asserts, Model B derives.**

### 10.2 Three primitives

#### Context — an ambient theory, defined by the axioms it assumes

Contexts form a **partial order by axiom inclusion**: down = more structure,
up = more general.

```
                    Set
                     │
        ┌────────────┼────────────┐
     TopSpace                   Group
      │    │                      │
Hausdorff  │                 AbelianGroup
      │  Metric                   │
      └────┤                     Ring
         Normed                   │
           │                    Field
     InnerProduct                 │
           │                 ┌────┴────┐
        Hilbert           char 0   char p
```

```python
class Context(BaseModel):
    id: str                  # "MetricSpace"
    name: str                # "Metric space"
    extends: List[str]       # ["TopSpace"] — immediate parents in the lattice
    signature: List[str]     # primitive symbols introduced: ["d"]
    axioms: List[str]        # informal statements of what this context adds
```

This is a **real mathematical object**, not an LLM's guess at an integer. It is
finite (~100 contexts covers undergraduate through early graduate mathematics),
stable, and identical for every user — so it is built once and shared.

#### Term — a defined name, scoped to its defining context

```python
class Term(BaseModel):
    name: str                # "compact"
    context: str             # "TopSpace"      →  identity is the PAIR
    kind: TermKind           # OBJECT | PROPERTY | CONSTRUCTION | OPERATOR
    definition_latex: str
    uses_terms: List[str]    # definitional dependency — computed, not extracted
    aliases: List[str]
    provenance: List[Provenance]
```

`normal @ Group`, `normal @ Hilbert.Operator` and `normal @ TopSpace` are three
distinct terms that **can never merge**, because identity is structural rather
than statistical.

#### Statement — the atom

```python
class Statement(BaseModel):
    id: str
    context: str                    # the ONE context this statement lives in
    slogan: str                     # "sequentially compact implies compact"
    hypotheses: List[str]           # term ids
    conclusion: str                 # term id, or a free assertion
    statement_latex: str
    status: Status                  # THEOREM | FALSE | DEFINITION | OPEN
    witness: Optional[str]          # REQUIRED when status = FALSE
    role: Optional[Role]            # Theorem | Lemma | Corollary (presentational)
    provenance_kind: ProvenanceKind # SEED | USER | EXTRACTED | INFERRED
    provenance: List[Provenance]
```

The `slogan` is the join key: the same slogan appearing at several lattice points
is what a "generalisation ladder" actually *is*.

#### Witness — objects that inhabit or fail contexts

```python
class Witness(BaseModel):
    id: str                  # "ordinal_space_omega_1"
    name: str                # "[0, ω₁) with the order topology"
    inhabits: List[str]      # contexts it is an object of
    satisfies: List[str]     # term ids it does satisfy
    fails: List[str]         # term ids it does not
```

Counterexamples finally have a home. This is the primitive that makes *"why is
Hausdorff in the hypothesis?"* an answerable query rather than a footnote.

### 10.3 What is derived rather than stored

| Model A stores… | Model B derives it from… |
|---|---|
| `abstraction_level: int` | position in the context lattice — a genuine partial order |
| `context: str` on edges | the statement's context — structural, not free text |
| `GENERALIZES` / `SPECIALIZES_TO` | same `slogan`, contexts ordered by the lattice |
| `DEPENDS_ON` (definitional) | terms occurring in a definition — string match against the term table |
| `EQUIVALENT_UNDER` | mutual implication between two statements in one context |
| `SEPARATES` | a `Witness` that satisfies one term and fails another |
| `disambiguation_group` | terms sharing a `name` across different contexts |
| `_resolve_entity` cosine merge | **deleted** — identity is `(name, context)` |
| `confidence` on structural edges | not needed; structural relations are computed, not guessed |

The last three rows carry the argument.

**The merge disappears rather than getting tuned.** §7.6 spends a paragraph
arguing 0.88 → 0.92 and domain gating. Model B deletes the most damaging line in
the codebase instead of calibrating it.

**The ladder stops inheriting the 75% precision ceiling.** In Model A the
Spectral Theorem picture in §5 is *extracted*, so per §3.5 roughly one edge in
four is wrong. In Model B it is *computed from the lattice*, so it is exactly as
reliable as the lattice — hand-curated once, shared by everyone, and verifiable
by inspection.

### 10.4 The three dependencies, separated

`DEPENDS_ON` currently conflates three unrelated relations, and that conflation
is most of why the rendering is mush. Model B keeps them apart by construction:

| Kind | Meaning | How you get it | Reliability |
|---|---|---|---|
| **Definitional** | you cannot *state* X without Y | which defined terms occur in X's statement | ~exact, **no LLM** |
| **Logical** | the proof of X invokes Y | from the proof text | good |
| **Pedagogical** | you should learn Y before X | human judgment, contested | subjective, user-owned |

Definitional dependency is the one nobody in §3 extracts, and it is nearly free:
match statement text against the term table. No judgment, no hallucination. It
yields a **reliable spine underneath everything uncertain** — which is exactly
what is missing today, where every edge is equally suspect.

Separating pedagogical order out as explicitly subjective is also the honest
move. There is no fact of the matter about whether determinants come before
eigenvalues; pretending the graph knows is how trust is lost.

### 10.5 Compactness in Model B

§6's conditional edge dissolves into two statements at different lattice points:

```
 context: TopSpace
   slogan:     "sequentially compact implies compact"
   status:     FALSE
   witness:    [0, ω₁) with the order topology
               (sequentially compact; not compact)

 context: TopSpace
   slogan:     "compact implies sequentially compact"
   status:     FALSE
   witness:    {0,1}^[0,1] with the product topology
               (compact by Tychonoff; not sequentially compact)

 context: MetricSpace           ← strictly below TopSpace in the lattice
   slogan:     "sequentially compact iff compact"
   status:     THEOREM
```

This is not a nicer encoding of the same information. It is **checkable**, it is
where a mathematician would file it, and the `context` string is gone — replaced
by a lattice position that the layout can read directly.

### 10.6 The Spectral Theorem in Model B

§5's ladder is not six extracted `GENERALIZES` edges. It is **one slogan
instantiated at six lattice points**, and the ladder is read off the lattice:

| Context | Hypothesis | Status | Witness |
|---|---|---|---|
| `Matrix(ℝ)` | symmetric | THEOREM | — (A = QΛQᵀ) |
| `Matrix(ℝ)` | normal | **FALSE** | `[0 −1; 1 0]` — normal, no real eigenbasis |
| `Matrix(ℂ)` | normal | THEOREM | — (A = UΛU*) |
| `CompactOperator(Hilbert)` | self-adjoint | THEOREM | — (discrete spectrum, eigenbasis) |
| `BoundedOperator(Hilbert)` | normal | THEOREM | — (T = ∫ λ dE) |
| `UnboundedOperator(Hilbert)` | self-adjoint, densely defined | THEOREM | — (domain conditions) |

The rotation-matrix counterexample is no longer a decoration hanging off an
edge — it is **row 2**, a first-class false statement at a specific lattice
point, which is precisely why row 1 needs its own hypothesis. The picture in §5
is a *rendering* of this table, and the vertical axis is the lattice.

---

## 11. Model B: the representation — lenses

If graphs are queries over the store, the interface is not "here is your graph,
please pan around." It is **pick a lens**. Each lens is a different projection of
the same three primitives, and each answers a question a student actually asks.

| Lens | Question | Computed from | Reliability |
|---|---|---|---|
| **Ladder** | "how does this generalise?" | one slogan across the lattice | exact |
| **Definition** | "what vocabulary do I need to even read this?" | `uses_terms` transitive closure | exact |
| **Boundary** | "why is *that* hypothesis there?" | statements with status FALSE at weaker contexts | exact |
| **Neighbourhood** | "what else lives here?" | statements sharing a context | exact |
| **Path** | "what order should I learn this in?" | pedagogical overlay | subjective, user-owned |

Note the reliability column. Four of the five lenses are exact because they read
structure rather than extracted assertions. Only the subjective one is soft, and
it is *labelled* subjective.

### 11.1 The boundary lens

The novel one, and the one I would build first — no tool in the §3 survey does
this:

```
  Statement:  "a continuous bijection is a homeomorphism"
  Context:    CompactHausdorff          hypotheses: compact (domain),
                                                    Hausdorff (codomain)

  ┌─ walk UP the lattice: which hypothesis is load-bearing? ─────────────┐
  │                                                                      │
  │   drop  compact   ─▶ context Hausdorff          status: FALSE        │
  │        witness:  id : (ℝ, discrete) → (ℝ, usual)                     │
  │                  continuous bijection; inverse not continuous        │
  │                                                                      │
  │   drop  Hausdorff ─▶ context CompactTop         status: FALSE        │
  │        witness:  id : ({a,b}, discrete) → ({a,b}, indiscrete)        │
  │                  domain compact; not a homeomorphism                 │
  │                                                                      │
  │   ⇒ both hypotheses are load-bearing.                                │
  └──────────────────────────────────────────────────────────────────────┘
```

This is how mathematicians actually understand a definition: not by reading it,
but by seeing what breaks without each clause. It falls straight out of the model
with no extra machinery, and it is the strongest argument for Model B.

### 11.2 What carries over from §8

Model B changes what is drawn, not how. These survive unchanged:

- note nodes and `CONTAINS` stay out of the default view (§8.1);
- vertical position encodes abstraction — now **lattice depth** rather than a
  guessed integer (§8.1);
- map-like domain regions over super-node collapse (§8.3);
- the inspector (§8.4);
- **edit affordances (§8.5) — still the highest-value feature**, and cheaper
  here: confirming a *classification* ("this statement lives in MetricSpace") is
  a lighter judgment than auditing a free-text hypothesis on an arrow.

---

## 12. Model B: construction

### 12.1 The extraction job gets easier, not harder

This is the practical payoff. Model A asks one open-ended question; Model B asks
two constrained ones:

| | Task | Shape | Verifiable? |
|---|---|---|---|
| **Model A** | "find all relations in this note" | open-ended generation | hard — §3.5 gives ~75% precision |
| **Model B** ① | "which context does this statement live in?" | classification over ~100 known options | yes — wrong answers are visible |
| **Model B** ② | "which known terms appear in it?" | string match against the term table | **not an LLM task at all** |

Trading an open-ended generation problem for a constrained classification plus a
lookup is the single largest reliability win available, and it comes from the
*shape of the model* rather than from better prompting. It also lands squarely
on §3.5's finding that ontology-constrained extraction both lowers hallucination
and makes what remains detectable.

### 12.2 Bootstrapping the lattice

The lattice is Model B's one hard prerequisite, and the reason it might be cheap:
**mathlib's typeclass hierarchy is already a machine-checked context lattice**
with hundreds of correctly ordered nodes, and §3.3's tooling shows the data is
extractable (`LeanDepViz` emits declaration names, module paths and kinds as
JSON).

> ⚠️ **Unverified.** I have not confirmed that the typeclass hierarchy can be
> extracted cleanly and mapped to informal context names. This is the first thing
> to check, because it converts Model B's largest upfront cost into an afternoon.
> If it fails, hand-building ~100 contexts is on the order of a few days.

### 12.3 Pipeline

```
 ┌── A. LATTICE ────────────────┐   built or imported once, shared
 │  ~100 contexts, ordered      │   → provenance_kind = SEED
 │  by axiom inclusion          │   → stable; the spine everything hangs on
 └──────────────┬───────────────┘
 ┌── B. TERM TABLE ─────────────┐   per context
 │  defined names + definitions │   → definitional deps computed by string match
 └──────────────┬───────────────┘
 ┌── C. GROUNDED PASS ──────────┐   per note, on ingest
 │  statements + context        │   → provenance_kind = EXTRACTED
 │  classification              │   → full provenance
 └──────────────┬───────────────┘
 ┌── D. WITNESS PASS ───────────┐   global, periodic
 │  counterexamples for FALSE   │   → provenance_kind = INFERRED
 │  statements at each point    │   → this is what powers the boundary lens
 └──────────────┬───────────────┘
 ┌── E. CORRECTION LOOP ────────┐   student edits
 │  reclassify / add witness /  │   → provenance_kind = USER, never overwritten
 │  mark status                 │   → the g = 0.72 activity from §3.2
 └──────────────────────────────┘
```

### 12.4 Validation gates

Stronger than §9's, because the structure supports real checks:

- a `Statement` must reference a context that exists in the lattice;
- `status = FALSE` **requires** a `witness`;
- a witness must `fail` at least one term named in the statement's hypotheses;
- a term used in a statement must be defined in that context **or an ancestor**
  (this catches misclassification automatically — a statement using `d` cannot
  live in `TopSpace`);
- if a slogan is a THEOREM at context C, it should not be FALSE at any context
  *below* C — a contradiction flags a bad extraction with no human involved.

The fourth and fifth gates have no analogue in Model A. They are the model
checking itself.

---

# Part IV — Decision

## 13. Choosing between the models

### 13.1 Honest comparison

| Dimension | Model A (concept-primary) | Model B (context lattice) |
|---|---|---|
| Upfront cost before anything works | low — evolves current schema | **high** — lattice must exist first |
| Reliability of the generalisation ladder | ~75% (extracted) | exact (computed) |
| Disambiguation of same-name concepts | special-cased via `disambiguation_group` | free — identity is `(name, context)` |
| Hypothesis handling | free-text `context` on edges | structural; the statement's context |
| Extraction difficulty | open-ended generation | classification + lookup |
| Self-validating | weakly (§9 gates) | strongly (§12.4 gates) |
| Fit to messy undergraduate notes | good — degrades gracefully | **poorer** — notes that drift between contexts resist classification |
| Fit to applied maths, intuitions, heuristics | good | **poor** — not everything is a statement |
| Answers "why is this hypothesis here?" | no | **yes** — the boundary lens |
| Generalises beyond mathematics | yes (§7.7) | yes — jurisdictions, physical regimes, machine models |
| Works with the existing pipeline | mostly | needs rework |

### 13.2 Where Model B is genuinely worse

Stated plainly, because the comparison is otherwise one-sided:

1. **The lattice must exist before anything works.** Model A's seed spine (§9) is
   optional and the system degrades gracefully without it. Model B's lattice is
   load-bearing.
2. **Undergraduate notes live in three to five contexts.** The lattice is small
   there — which means the vertical axis is nearly free, but also that the payoff
   is modest until you span several courses. The value appears exactly at the
   moment two courses use the same word differently, which may be a year away.
3. **Not everything is a statement.** "Eigenvalue" *as an idea*, intuitions,
   worked examples, heuristics and motivation fit awkwardly. Concepts return as
   second-class citizens, which reintroduces some of what §10.3 deleted.
4. **Applied mathematics fits poorly.** Numerical methods and modelling do not
   decompose into axiomatic contexts anything like as cleanly as algebra and
   topology do.
5. **It is further from the current code**, and the §3 survey contains no
   instance of anyone shipping this for personal study notes. The formal-methods
   precedent (§16, "little theories") is real but it is for proof assistants, not
   students.

### 13.3 The cheap experiment

Do not choose on argument. **Phase 1 of §14 is shared** — ship it first, then run
this before committing to either model:

> Touch no pipeline code. By hand, build a lattice of ~15 contexts for one course
> you are actually taking, enter ~40 statements, and render only the **ladder**
> and **boundary** lenses.
>
> If *"here is the theorem, here is the axiom you dropped, here is the
> counterexample that appears"* feels revelatory — build the extractor.
> If it feels like bookkeeping — Model A is sitting there, fully specified, and
> you have spent a weekend.

Two days of manual data entry is a very cheap price for deciding an architecture,
and the manual entry is itself the g = 0.72 activity from §3.2.

### 13.4 Recommendation

**Ship §14 phase 1 immediately** (model-independent). **Then run §13.3.** My
expectation is that Model B wins on the boundary lens alone, but that expectation
is exactly what the experiment is for — and Model A is not a wasted fallback,
because §7.1's kind/role split, §7.4's trust tiers and §8.5's edit affordances
are all needed either way.

A hybrid is also viable and probably the realistic end state: Model B's lattice
and statements for the rigorous core, Model A's looser concept nodes for
intuitions, applications and everything that resists axiomatisation.

---

## 14. Roadmap

### Phase 0 — shared, ship regardless of which model wins

| Phase | Work | Payoff |
|---|---|---|
| **1** | Hide `Note` nodes + `CONTAINS`; fix vertical position from an abstraction ordering; drop the redundant solver controls | The screenshot becomes legible. One afternoon. Independent of the model. |

Then run the §13.3 experiment before committing to a track.

### Track A — concept-primary

| Phase | Work | Payoff |
|---|---|---|
| **A2** | Add `context`, `provenance_kind`, `kind`/`role` split, `GENERALIZES`/`SEPARATES`; canonicalise `DEPENDS_ON`; fix `_resolve_entity` (descriptions, ≥0.92, domain-gated) | The model can express the Spectral Theorem picture. |
| **A3** | Node inspector: statement, hypotheses, provenance, counterexamples, disambiguation siblings | The graph becomes readable as mathematics. |
| **A4** | **Edit affordances** + `USER` tier persistence | The g = 0.72 intervention. Also the error-correction path. |
| **A5** | Focused-subgraph mode (Metacademy-style closure + topological order); map-like domain regions | Scales past a few hundred nodes. |
| **A6** | Seed spine + curation pass + validation gates | The atlas stops being an archipelago. |

### Track B — context lattice

| Phase | Work | Payoff |
|---|---|---|
| **B2** | Build or import the lattice (§12.2 — check the mathlib route first) | The spine. Everything else depends on it. |
| **B3** | `Context` / `Term` / `Statement` / `Witness` schemas; term table for 2–3 contexts | Identity becomes structural; `_resolve_entity` is deleted. |
| **B4** | **Ladder + boundary lenses** | The two views that justify the whole model. |
| **B5** | Context classification in the grounded pass + §12.4 validation gates | Ingestion feeds the lattice; the model checks itself. |
| **B6** | **Edit affordances** (reclassify, add witness, set status) | Same g = 0.72 payoff, lighter judgments than Track A. |
| **B7** | Witness pass; remaining lenses | The atlas fills in. |

Note that **edit affordances appear in both tracks** and are the highest-measured-
value item in each. If anything slips, do not let it be that.

**Test fixture (either track)**: build the compactness family (§6 / §10.5) by
hand first. Four concepts, implications that hold only under stated hypotheses,
standard separating counterexamples. If the model and the renderer can express
that cluster correctly, they can express most of undergraduate mathematics.

---

## 15. Risks and open questions

### Shared

1. **~25% of inferred relations will be wrong** (§3.5). Mitigated by trust tiers,
   validation gates and one-click correction — not eliminated. An atlas that is
   confidently wrong about a hypothesis is worse than one that is sparse; when in
   doubt, prefer omission and let the student add it.
2. **Editing UX is not free.** The highest-value phase in both tracks is the
   largest engineering item, and vis.js's manipulation API is limited. Worth
   evaluating Cytoscape.js before committing, since it is also a better fit for
   the map-like rendering in A5.
3. **Unverified**: Metacademy's current status. The search evidence suggests
   dormancy but I could not reach the site; if it is live, its content model is
   worth studying directly rather than reconstructing from descriptions.

### Model A specific

4. **`abstraction_level` may not be a total order.** Is "measure-theoretic
   spectral theorem" above or below "compact self-adjoint"? Generalisation is a
   partial order and the layout needs a total one. Proposed resolution: longest
   path in the `GENERALIZES` DAG, with the LLM estimate as a tiebreak for
   unconnected nodes. **Model B dissolves this** — the lattice is natively a
   partial order, so nothing needs flattening.
5. **`context` as free text is not machine-checkable.** The right *first* move
   (Wikidata's qualifiers are similarly loose in practice), but a controlled
   vocabulary of ambient hypotheses would be far more powerful. Note that a
   controlled vocabulary of ambient hypotheses **is** Model B's lattice — so
   tightening this field is the migration path from A to B.
6. **Seed spine scope.** 200–300 concepts is a guess. Too small and notes still
   form islands; too large and it drowns the student's own material. Start with
   one subject actually being taken and measure attachment rate.

### Model B specific

7. **Lattice extraction from mathlib is unverified** (§12.2) and is the single
   largest cost lever. Check it before anything else in Track B.
8. **Context classification accuracy is unmeasured.** The claim that "which of
   ~100 contexts?" is materially easier than open-ended relation extraction is
   well-motivated but untested on handwritten undergraduate notes. §12.4's gate
   — terms must be definable in the context or an ancestor — gives a way to
   measure it cheaply.
9. **Notes that drift between contexts without saying so.** A lecture that opens
   in ℝⁿ and silently generalises mid-page will misclassify. Possibly needs
   statement-level rather than note-level classification, which is more calls.
10. **Concepts that are not statements** (intuitions, motivation, worked
    examples) have no natural home. The hybrid in §13.4 is the likely answer, but
    it reintroduces some of the ambiguity §10.3 removed.
11. **`slogan` as the join key is fragile.** Two renderings of the same theorem
    must produce the same slogan for the ladder to assemble. Embedding similarity
    over slogans is the obvious fix — but that reintroduces a threshold, and
    §3.5's ≥0.9 finding applies again. Better: make the slogan a *user-editable*
    field surfaced in the ladder lens, so mis-joins are visible and one click to
    fix.

---

## 16. References

**Little theories / context-indexed formalisation** (Model B precedent)

- Farmer, Guttman & Thayer, *Little Theories* (CADE-11, 1992) — the IMPS approach:
  many small axiomatic theories linked by theory interpretations, rather than one
  monolithic foundation. Model B's context lattice is this idea applied to
  informal mathematics.
- Farmer, *An Infrastructure for Intertheory Reasoning* — theory morphisms as the
  mechanism for transporting results between contexts.
- Lean 4 / mathlib's algebraic and topological typeclass hierarchy — a working,
  machine-checked context lattice; the proposed bootstrap in §12.2.
- Mizar's structures — an earlier instance of the same pattern.

> These are cited from background knowledge rather than verified during this
> session's research, unlike everything below. Confirm before relying on
> specifics.

**Learning-side prior art**

- [Knowledge Space Theory — the research behind ALEKS](https://www.aleks.com/about_aleks/knowledge_space_theory)
- Falmagne, *The Assessment of Knowledge, in Theory and in Practice* ([PDF](https://www.aleks.com/about_aleks/Science_Behind_ALEKS.pdf))
- Matayoshi & Uzun, *A practical perspective on knowledge space theory: ALEKS and its data* ([preprint](https://jmatayoshi.github.io/publications/JMP2021_KST_ALEKS_preprint.pdf))
- Falmagne & Doignon, *Knowledge Spaces and Learning Spaces* ([arXiv:1511.06757](https://arxiv.org/abs/1511.06757))
- [Metacademy](https://metacademy.org/) · [content repo](https://github.com/metacademy/metacademy-content) · [Langford, *Metacademy: a package manager for knowledge*](https://hunch.net/?p=2714)

**Concept-map effectiveness**

- Nesbit & Adesope (2006), *Learning With Concept and Knowledge Maps: A Meta-Analysis*, Review of Educational Research 76(3) ([PDF](https://www.sfu.ca/~jcnesbit/research/NesbitAdesope2006.pdf))
- Schroeder, Nesbit, Anguiano & Adesope (2018), *Studying and Constructing Concept Maps: a Meta-Analysis*, Educational Psychology Review ([Springer](https://link.springer.com/article/10.1007/s10648-017-9403-9))

**Formal-mathematics dependency graphs**

- [Metamath](https://us.metamath.org/) · [Proof Explorer](https://us.metamath.org/mpeuni/mmset.html)
- [LeanDepViz](https://github.com/cameronfreer/LeanDepViz) · [lean-graph](https://github.com/patrik-cihal/lean-graph)
- *TheoremGraph: Bridging Formal and Informal Mathematics* ([arXiv:2606.25363](https://arxiv.org/abs/2606.25363))
- *KnowTeX: Visualizing Mathematical Dependencies* ([arXiv:2601.15294](https://arxiv.org/abs/2601.15294))

**Ontologies and contextual relations**

- *OntoMathPRO 2.0 Ontology: Updates of the Formal Model* ([arXiv:2303.13542](https://arxiv.org/pdf/2303.13542)) · [Doklady Mathematics](https://link.springer.com/article/10.1134/S1064562422700016)
- *Handling Wikidata Qualifiers in Reasoning* ([arXiv:2304.03375](https://arxiv.org/abs/2304.03375))
- *Domain-Contextualized Concept Graphs* ([arXiv:2510.16802](https://arxiv.org/pdf/2510.16802))

**LLM-based KG construction quality**

- *LLM-empowered knowledge graph construction: A survey* ([arXiv:2510.20345](https://arxiv.org/pdf/2510.20345))
- *Knowledge Graph Construction: Extraction, Learning, and Evaluation* ([Applied Sciences 15(7)](https://www.mdpi.com/2076-3417/15/7/3727))
- *Leveraging LLMs for Automated Extraction and Structuring of Educational Concepts and Relationships* ([MAKE 7(3)](https://doi.org/10.3390/make7030103))
- *Inferring Prerequisite Knowledge Concepts in Educational Knowledge Graphs* ([arXiv:2509.05393](https://arxiv.org/html/2509.05393))

**Visualisation**

- *GMap: Drawing Graphs as Maps*, Gansner, Hu & Kobourov ([arXiv:0907.2585](https://arxiv.org/abs/0907.2585))
- *Node, Node-Link, and Node-Link-Group Diagrams: An Evaluation* ([arXiv:1404.1911](https://arxiv.org/pdf/1404.1911))
- *A Hierarchical Aggregation Framework for Graph Visualization* ([arXiv:1511.04750](https://arxiv.org/pdf/1511.04750))
- Munzner, *Interactive Visualization of Large Graphs and Networks* ([Stanford thesis](https://graphics.stanford.edu/papers/munzner_thesis/allbw.pdf))
- [What's the point of the graph view? — Obsidian Forum](https://forum.obsidian.md/t/whats-the-point-of-the-graph-view-how-are-you-using-it/71316)
