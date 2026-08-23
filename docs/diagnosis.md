# Graph Quality: Diagnosis and Recommendations

History of graph issues and how they were fixed. Current state: **healthy**. See [flow.md](flow.md)
and [structure.md](structure.md) for how data moves and the call graph.

## Current State (as of plan.md Phase 5)

**Graph health:** 75 nodes, 122 edges, 0 duplicate groups.

Reproduce any time with:
```bash
python scripts/graph_health.py
```

The major issues documented below (D1–D6) have been fixed or addressed:

| Issue | Status | Fixed by |
|---|---|---|
| **D1** — Duplicate nodes | ✓ Fixed | plan.md Phase 1–2: canonical identity + authority resolve |
| **D2** — Alias table ignored | ✓ Fixed | Phase 1: alias lookups integrated into `_resolve_entity` |
| **D3** — Threshold tuning | ✓ Moot | Phase 1: embedding similarity removed from write path |
| **D4** — Isolated junk nodes | ✓ Fixed | Phase 2: graph migration cleaned 17 junk nodes |
| **D5** — Vocabulary collapse | ⏳ Partial | Phase 4: 2-pass extraction (awaiting richer type taxonomy) |
| **D6** — Taxonomy fragmentation | ⏳ Partial | Phase 0: MSC2020 seeding (awaiting structured domain/subdomain) |

**Dead code removal (Phase 6):**
- ✓ Removed: `ENTITY_MERGE_THRESHOLD`, `dedupe_graph()`, `graph-dedupe` CLI verb
- ✓ Removed: `_snake_case_redirects` load-time self-heal
- ✓ Removed: embedding-based node matching from retrieval

---

## Historical Issues (Pre-Phase 0, preserved for reference)

### D1 — Duplicate nodes survive deduplication (Fixed)

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

### D2 — The alias table is never read (Fixed)

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

### D3 — One threshold cannot separate the two populations (Moot)

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

### D4 — Isolated nodes are debris (Fixed)

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

### D5 — Typed vocabularies have collapsed (Partial)

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

### D6 — Taxonomy tier 2 fragments on synonymy (Partial)

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

## Root Cause (Pre-Phase 0)

All six defects were the same absence:

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

### A. Canonical key + read the aliases — ✓ **IMPLEMENTED** (Phase 1)

**Status: DONE**

Implemented as `normalize()` in `services/graph/app/schema.py` and integrated into
`_resolve_entity()` in `services/graph/app/indexer.py`. Resolution is now a deterministic
dictionary lookup (document → course → global-authority → mint CUST_) instead of embedding
similarity. `services/graph/app/authority.py` maintains the identity authority in SQLite.

- **Fixes:** D1 and D2 completely.
- **Effect:** Pre-Phase-0 graph: 123 → 108 nodes, edge sets reunited. Live graph: 75 nodes, 0 duplicates.
- **Status:** Shipping with all graph containers.

### B. Reject junk at extraction — ✓ **IMPLEMENTED** (Phase 2 migration)

Integrated into `_is_valid_entity()` (services/graph/app/indexer.py). Junk node cleanup
and orphaned note-container removal happened during `graph-migrate-identity` (Phase 2).

- **Fixes:** D4 completely (17 junk nodes removed, 32 → 0 isolated nodes).
- **Status:** Live graph clean; new extractions follow the validation rules.

### C. Make the repairs part of the pipeline — ⏳ **PARTIAL** (Phase 3+)

Dedup-on-repair was superseded by Phase 1's deterministic identity: with canonical IDs,
duplicates stop occurring at extraction (Phase 4: 2-pass LLM with resolve-then-link).

Automated provenance dedup and content-hash-based vault state tracking remain as future
refinements (low priority — current graph health supports incremental indexing).

- **Status:** Partially addressed by identity layer; full pipeline automation deferred.

### D. Lookup-first extraction — ⏳ **PARTIAL** (Phase 4, future expansion)

**Structural answer to D5/D6.** Phase 4 implemented the first step: Pass 1 resolves concept
names to canonical IDs (lookup), Pass 2 emits edges using those IDs (eliminates floating names).

Full tool-loop extraction (with `search_concepts`, `propose_concept`, `link` as LLM tools)
remains as a future enhancement for richer taxonomy support. Current 2-pass approach is
sufficient for Phase 5–7.

- **Partially fixes:** D1, D3 (identity), D5/D6 (as classes rather than per-instance).
- **Status:** Core mechanism in place (Phase 4); full agent loop deferred.
- **Remaining:** structured domain/subdomain vocabulary (Phase 7+).

### E. Community detection as a standing check — ⏳ **FUTURE** (Phase 7+)

Run Leiden (via `igraph`/`leidenalg`) over the finished graph and diff communities
against assigned taxonomy. Turns taxonomy drift from manual inspection into automated checks.

- **Do after:** A (done), D (partial).
- **Status:** Deferred until taxonomy stabilizes.

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
