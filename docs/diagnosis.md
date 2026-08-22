# Graph Quality: Diagnosis and Recommendations

What is wrong with the knowledge graph, why it happens, and what to do about it.

Measurements below come from `.storage/graph.json` on **2026-08-15** (123 nodes, 164 edges,
13 notes), taken *after* commits `c382750` (snake_case self-heal) and `7726289` (graph-wide
dedup) had landed. Reproduce them at any time with:

```bash
python scripts/graph_health.py
```

See also [flow.md](flow.md) for how data moves and [structure.md](structure.md) for the
call graph.

---

## Summary

Six measured defects. They are not six bugs — they are one missing concept showing up in
six places.

| | Defect | Measured |
|---|---|---|
| **D1** | Duplicate nodes survive deduplication | 14 groups; merging → 108 nodes |
| **D2** | The alias table is never read | 93 of 123 nodes carry aliases |
| **D3** | One similarity threshold can't separate the populations | 0.93, still misses exact duplicates |
| **D4** | Isolated nodes are debris, not sparse maths | 32 isolated (26%), 17 provably junk |
| **D5** | Typed vocabularies have collapsed | 77% of edges `DEPENDS_ON`, 74% of nodes `Concept` |
| **D6** | Taxonomy tier 2 fragments on synonymy | 24 subdomains for 123 nodes |

**Root cause:** the graph has no identity function. `GraphNode.id` defaults to `name`
([schema.py:70](../src/graph/schema.py#L70)), and `name` is free text generated fresh by an
LLM on every call, with no view of what it generated last time.

**Primary recommendation:** [A — canonical key + read the aliases](#a-canonical-key--read-the-aliases),
then [D — lookup-first extraction](#d-lookup-first-extraction).

> **Status (2026-08-22): Recommendations A and B are implemented**, as
> [plan.md](../plan.md) Phases 0-2. `normalize()` now lives in
> `services/graph/app/schema.py`; `_resolve_entity` in
> `services/graph/app/indexer.py` is a deterministic lookup
> (`services/graph/app/authority.py`: document → course → global-authority → mint), not
> embedding similarity — `ENTITY_MERGE_THRESHOLD` and `dedupe_graph()` below are now
> dead code on the write path (still present, still callable, deletion is plan.md Phase 6).
> **The live graph itself was migrated onto this scheme** (`graph-migrate-identity`,
> plan.md Phase 2): the specific numbers below (123 nodes, 14 duplicate groups, 32 isolated,
> the `Lipschitz Condition` example) are now a **dated snapshot of the pre-fix state**, not
> the graph's current shape — `scripts/graph_health.py` now reports 0 duplicate groups
> against the live file (75 nodes, down from 119 after junk removal and merging). D1, D2, D4
> are fixed both for the historical data and for new extractions; D3 (the threshold) is moot
> since nothing on the write path consults it anymore; D5/D6 (vocabulary and taxonomy
> collapse) are **not** addressed by this — those still need Recommendation D or an MSC2020
> taxonomy swap. Note paths below (`src/graph/...`) predate the `services/` extraction and
> are now `services/graph/app/...`; left as originally written since this document is itself
> a dated measurement, not living reference.

---

## The defects

### D1 — Duplicate nodes survive deduplication

Fourteen groups of node ids normalize to the same key. These are not subtle semantic
near-misses; they are the same string with a different separator, each holding its own
half of the edge set.

```
'Lipschitz Condition' deg=5, 'lipschitz-condition' deg=5, 'lipschitz_condition' deg=0
'picards_theorem' deg=5, 'picards-theorem' deg=6
'Bessel Equation' deg=4, 'bessel-equation' deg=4
```

Three id conventions are in simultaneous use — 49 Title Case, 43 snake_case, 29 kebab-case.
All three come from the *same* LLM extraction pass; the vault contains no wikilinks, so the
block extractor is not the source. The model simply does not spell a concept the same way
twice.

Merging the exact-normalizing groups takes the graph from **123 to 108 nodes** and reunites
the split edge sets.

### D2 — The alias table is never read

Every reference to `aliases` in the codebase is an append or a serialization
([indexer.py:213, 271, 617, 720, 781](../src/graph/indexer.py#L617)). `_resolve_entity`
compares an incoming name against node **ids** and **descriptions** — never against the
alias lists it has been building.

The cost is visible in the data:

```
'Lipschitz Condition'.aliases = ['Lipschitz continuity', 'Lipschitz Condition',
                                 'lipschitz_condition',  <- still a separate node
                                 'lipshitz_condition', 'Lipschitz Continuity']
```

The answer was computed, stored, and then never consulted. A dictionary lookup against
existing aliases would resolve this case at zero cost.

### D3 — One threshold cannot separate the two populations

`ENTITY_MERGE_THRESHOLD` was raised to `0.93`
([indexer.py:563](../src/graph/indexer.py#L563)) to stop false merges like *normal subgroup*
/ *normal operator*. But true duplicates get their descriptions written by independent LLM
calls, in unrelated words:

```
'Lipschitz Condition'  "A function satisfies the Lipschitz condition on an interval
                        if the absolute difference between its values..."
'lipschitz_condition'  "A strengthening of uniform continuity where a function is
                        limited by a linear scaling of the distance..."
```

Same concept, near-orthogonal phrasing. No threshold separates that pair from a genuine
near-miss, because **the two populations overlap**. This is not a tuning problem; embedding
similarity is the wrong instrument for a job that string normalization does exactly.

Note the counter-example the fix must respect: `y-lipschitz-condition` is genuinely
*different* from `lipschitz-condition` (Lipschitz in *y* for `f(x,y)`). It normalizes
differently, so a key-based rule handles it correctly.

### D4 — Isolated nodes are debris

Of 32 zero-degree nodes:

- **13 are dead note containers** (`MA301 Lecture 1–7`, `Lecture notes 4-6`, …). The
  `CONTAINS` edge type was retired in `402a40e`; the edges were dropped on load
  ([indexer.py:225](../src/graph/indexer.py#L225)) but the nodes they connected were never
  removed.
- **5 are duplicate-group losers** whose twin holds the edges.
- **1 relation type leaked in as a node**: `DEPENDS_ON`, degree 1.
- **2 placeholder labels**: `Theorem T1`, `Theorem T2`.
- **1 raw sentence fragment**: `If $\frac{N_x - M_y}{M}$ is continuous and depends only on $y$, then`.

`_is_valid_entity` ([indexer.py:88](../src/graph/indexer.py#L88)) rejects `if the …` but not
`If $…`, and has no rule against relation names or single-letter-plus-digit placeholders.

The graph is not displaying sparsely-connected mathematics. It is displaying wreckage.

### D5 — Typed vocabularies have collapsed

Nine entity types and seven relation types are defined. In practice:

| Relation | Share | | Entity type | Share |
|---|---|---|---|---|
| `DEPENDS_ON` | 77.4% | | `Concept` | 74.0% |
| `USES_DEFINITION` | 14.6% | | `Theorem` | 13.8% |
| `USES_LEMMA` | 4.3% | | `Definition` | 10.6% |
| `COROLLARY_OF` | 2.4% | | `Formula` | 1.6% |
| `PROVES` | 1.2% | | `Proof` / `Lemma` / `Axiom` / `Corollary` / `Example` | **0** |
| `USES_AXIOM` | **0** | | | |

A vault full of proofs produced **two** `PROVES` edges and **zero** `Proof` nodes. The
atlas exists to make small distinctions visible; they are being flattened at extraction.

Note also that the same concept gets different types across duplicates — `picards_theorem`
is a `Concept` while `picards-theorem` is a `Theorem`. Typing is as unstable as naming.

### D6 — Taxonomy tier 2 fragments on synonymy

Commit `1cf4a0a` normalized `domain` **casing**. Tier 2 fragments on **synonymy**, which
casing normalization cannot touch — 24 subdomains for 123 nodes:

```
Ordinary Differential Equations               30
First-Order ODEs                              13
Systems of Ordinary Differential Equations     7   ┐ one subdomain
Systems of ODEs                                6   ┘
First-Order Ordinary Differential Equations    4   ← same as "First-Order ODEs"
Second-Order Ordinary Differential Equations   4   ┐
Second-Order Linear ODEs                       4   │ one subdomain
Second-Order ODEs                              1   ┘
```

Tier 1 has the same disease in miniature: `Physics And Differential Equations` is a
compound domain that a free-text field has no way to reject.

### Also worth fixing

**Provenance appends without dedup.** 60 nodes carry repeated records; `wronskian` has 10
extras, `Lipschitz Condition` 8. `index_note` appends a record on every index
([indexer.py:785-788](../src/graph/indexer.py#L785)) without checking whether that document
is already listed.

**Dedup is a manual chore, not a pipeline stage.** `dedupe_graph()` is reachable only from
`cli graph-dedupe` ([cli.py:142](../src/cli.py#L142)). Nothing in the ingest path calls it,
so duplicates accumulate freely between hand-run passes.

**The load-time self-heal never persists.** `_load_graph` applies its repairs in memory on
every startup but only reaches disk if something later calls `save_graph()`. The same
repair is recomputed forever and `graph.json` stays dirty.

**The same document can be ingested twice.** `vault_state.json` keys on absolute path, so
`Lecture notes 7 to 9.md` and `Lecture notes 7 to 9 (1).md` are two documents. They share
only 6 of their concepts and generate parallel duplicates.

---

## Root cause

All six defects are the same absence.

A node's id **is** its display name. `GraphNode.populate_id_from_name` sets `id = name`
when no id is supplied, and `name` is free text produced by a language model, fresh, on
every call. Nothing binds the string the model writes today to the string it wrote
yesterday for the same concept.

Read the defects through that lens and they stop being separate:

- **D1 and D3** are *repairs* for identity that was never assigned.
- **D2** is the identity index we accidentally built and then forgot to query.
- **D4** persists because no authority says which strings are allowed to be nodes.
- **D5 and D6** are the same free-text problem in the type and taxonomy fields — the model
  picks a value per call and nothing constrains the picking.

The pattern in one line: **the values that must stay stable across notes are owned by the
least stable actor.** Deterministic code owns formatting and plumbing; the LLM owns
identity, type and taxonomy; the embedding model is then paid, repeatedly and expensively,
to guess which of the LLM's decisions were meant to be the same decision.

### What Graphify does differently

[Graphify](https://github.com/Graphify-Labs/graphify) is a code-understanding skill that
builds the same kind of graph from source code. Its deduplication stage is a footnote while
ours is the main event, and the reason is instructive: **tree-sitter assigns identity by
construction.** A symbol resolves to `auth.User.login` every time, because the language
grammar defines what "same" means.

Their advantage is not the parser. It is that *something outside the model decides what an
entity is*. There is no grammar for a handwritten proof, so the parser does not transfer —
but that property does, and the recommendations below are three ways to get it.

What is worth borrowing from them directly: **confidence-tagging edges**
(`EXTRACTED` vs `INFERRED`) and **community detection** as a check on the taxonomy. What is
not worth borrowing: the skill/plugin distribution model. A codebase is self-contained and
cheap to re-derive; our vault accumulates from expensive, irreversible OCR, and the atlas is
a single centralized artifact rather than per-run output.

---

## Recommendations

In dependency order. A is a prerequisite for D.

### A. Canonical key + read the aliases

**Do this first.**

Give every node a deterministic key derived from its name — lowercase, strip possessives
and punctuation, collapse `_`/`-`/space — and keep the display name as a separate field.
Then make resolution a dictionary lookup against keys **and** the alias table, with
embeddings demoted to a fallback for genuine rephrasings.

`scripts/graph_health.py::normalize` already implements exactly this key; the same function
can move into `graph/schema.py` and become the id rule.

- **Fixes:** D1 and D2 outright.
- **Effect:** 123 → 108 nodes, edge sets reunited, resolution stops re-deriving stored answers.
- **Cost:** small, self-contained, no new dependencies, no threshold to tune.
- **Touch:** [schema.py:70](../src/graph/schema.py#L70), [indexer.py:565](../src/graph/indexer.py#L565).

### B. Reject junk at extraction

Extend `_is_valid_entity` to reject relation names, `Theorem T\d+`-style placeholders, ids
containing `$`, and anything over ~70 characters. Separately, delete the 13 orphaned note
containers — retiring `CONTAINS` should have removed its endpoints too.

- **Fixes:** D4.
- **Cost:** an afternoon.
- **Touch:** [indexer.py:88](../src/graph/indexer.py#L88), plus a one-time cleanup pass.

### C. Make the repairs part of the pipeline

Call `dedupe_graph()` from `build_or_update_index`, and `save_graph()` after `_load_graph`
when redirects actually fired. Deduplicate provenance records on append. Key
`vault_state.json` on content hash rather than path so a `(1)` suffix is recognised as the
same document.

- **Fixes:** the four "also worth fixing" items.
- **Cost:** small, but do it after A, or you will be automating a pass that still misses
  the duplicates it was written to catch.

### D. Lookup-first extraction

**The structural fix.** Move extraction from a one-shot structured-output call into a
tool-calling loop. Give the extractor:

| Tool | Purpose |
|---|---|
| `search_concepts(query)` | semantic + lexical search over existing nodes, returning id, description and aliases |
| `get_concept(id)` | full node detail |
| `propose_concept(...)` | create — only after a lookup miss |
| `link(source, target, relation, quote)` | edge, with the evidence quote required |
| `list_taxonomy()` | existing domain/subdomain values |

Identity stops being repaired afterwards and becomes a constraint at generation time: look
up before emitting, link if it exists, propose only on a miss. **The graph becomes its own
authority file**, which is the property tree-sitter gives Graphify — without needing a
pre-built concept lexicon.

The same mechanism fixes the other free-text fields. `list_taxonomy()` stops
`Systems of ODEs` from being coined next to `Systems of Ordinary Differential Equations`
(D6). Requiring `quote` on `link()` yields the `EXTRACTED`/`INFERRED` distinction for free,
which matters when 77% of edges currently read `DEPENDS_ON` (D5).

It is also the answer to **continuous addition**. A batch extractor processes each note in
isolation and needs dedup bolted on afterwards. An extractor whose first move is always
"what do we already have?" is incremental by construction — continuous addition stops being
the hard case and becomes the only case.

- **Fixes:** D1, D3, D5, D6 as *classes* rather than instances.
- **Cost:** real. 10–30 LLM calls per note instead of 2, and a new extraction contract.
- **Prerequisite:** A. An agent with `search_concepts` pointed at a graph that still holds
  three Lipschitz nodes will confidently link to whichever it finds first, cementing the
  duplicates instead of ending them.
- **Fix first regardless:** `_get_candidate_context`
  ([indexer.py:503](../src/graph/indexer.py#L503)) fills the prompt slot labelled
  "EXISTING KNOWLEDGE BASE CONCEPTS" from `r.get("source")` on vector hits — but that field
  is the **note filename** ([store.py:75](../src/vector/store.py#L75)). Up to 20 of 25
  candidates are strings like `MA301 Lecture 2`, padded with `list(graph.nodes)[:30]` —
  the first thirty by insertion order, not by relevance. Whatever shape extraction takes,
  the lookup it depends on has to actually return concepts.

### E. Community detection as a standing check

Run Leiden (via `igraph`/`leidenalg`) over the finished graph and diff the communities
against the assigned taxonomy. If `Systems of ODEs` and `Systems of Ordinary Differential
Equations` nodes land in one community, the graph has told you they are one subdomain.

- **Turns:** taxonomy drift from a thing noticed by eye into a thing detected automatically.
- **Do after A**, since community structure computed over duplicate nodes measures the
  wrong graph.

### Deliberately not recommended

- **Tuning the 0.93 threshold.** The populations overlap; see D3.
- **A full LLM rebuild as a fix.** `/api/rebuild/graph` re-rolls every naming decision. It
  changes which duplicates you have, not whether you have them.
- **Packaging as a distributable skill.** See *What Graphify does differently*.
- **Pre-building an MSC2020 or Wikidata concept lexicon before D.** Recommendation D makes
  the existing graph serve that role, which avoids the cold-start problem. A closed
  vocabulary is still the right long-term answer for `taxonomy.domain` — the stopgap note
  at [schema.py:44](../src/graph/schema.py#L44) says so — but it is not a prerequisite.

---

## Why identity, not resolution

Every commit in the recent run — `1cf4a0a` casing normalization, `5cae91e` threshold
raising, `c382750` snake_case self-heal, `7726289` graph-wide dedup — is a well-built repair
downstream of the same absence. Each one holds. The duplicates keep coming back in a new
spelling, because nothing upstream decides what a concept is called.

We have been fixing entity **resolution**. The missing piece is entity **identity**.
