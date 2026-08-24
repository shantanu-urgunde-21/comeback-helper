# Diagnosis: Graph Identity (historical)

**This describes a fixed problem.** It is kept because the root-cause reasoning still governs
how extraction is designed, and because these numbers are the baseline a future regression
would be measured against.

For what is *currently* wrong, see [vocabulary-diagnosis.md](vocabulary-diagnosis.md).

## What was wrong

Measured 2026-08-15 against a 123-node graph: **the graph had no identity function.**
`GraphNode.id` defaulted to `name`, and `name` was free text an LLM generated fresh on every
call with no view of what it had produced before. One concept was re-coined under several
spellings, each holding a fraction of the edges:

```
'Lipschitz Condition' deg=5   'lipschitz-condition' deg=5   'lipschitz_condition' deg=0
'picards_theorem'     deg=5   'picards-theorem'     deg=6
```

Three id conventions were in simultaneous use — 49 Title Case, 43 snake_case, 29 kebab-case —
all from the *same* extraction pass.

Four defects followed from that one absence:

| | Defect | Measured |
|---|---|---|
| **D1** | Duplicate nodes survive deduplication | 14 groups |
| **D2** | The alias table is written but never read | 93 of 123 nodes carried aliases |
| **D3** | One similarity threshold can't separate the populations | 0.93, still missed exact duplicates |
| **D4** | Isolated nodes are debris, not sparse maths | 32 isolated (26%), 17 provably junk |

D3 is the load-bearing one. Embedding similarity was used to repair identity after the fact,
but true duplicates get their descriptions written by independent LLM calls in unrelated
words, so they score *lower* than genuine near-misses like *normal subgroup* / *normal
operator*. **The populations overlap; no threshold separates them.** Not a tuning problem —
the wrong instrument for a job string normalisation does exactly.

## Root cause, stated generally

> The values that had to stay stable across notes were owned by the least stable actor.

Deterministic code owned formatting and plumbing; the LLM owned identity, type, and taxonomy;
the embedding model was then paid, repeatedly, to guess which of the LLM's decisions were
meant to be the same decision.

The comparison that clarified it: tree-sitter–based code graphs barely need a dedup stage,
because the grammar decides what "same" means. The transferable property is not the parser —
it is that **something outside the model decides what an entity is.**

## How it was fixed

plan.md Phases 0–2:

- `normalize()` in `graph/app/schema.py` — one canonical comparison key.
- `_resolve_entity` became a deterministic ladder in `graph/app/authority.py`: document →
  course → Wikidata (cached) → mint `CUST_<hash>`. No embeddings on the write path.
- Node keys became opaque ids; display names moved to a separate `label` attribute.
- The live graph was migrated onto the scheme: **119 nodes → 75**, 17 junk dropped and 27
  duplicate spellings merged. (The one-shot `graph-migrate-identity` verb has since been
  removed — the migration is done.)

`graph_health.py` now reports **0 duplicate groups**. D1, D2, D4 fixed for both historical
data and new extractions; D3 moot, since nothing consults a threshold any more.
`ENTITY_MERGE_THRESHOLD`, `dedupe_graph()`, and the load-time self-heal were deleted in
Phase 6.

Note that embeddings were removed from the **write** path only. Retrieval still embeds node
labels to pick seed concepts for a query — that is a search problem, not an identity one, and
is a documented invariant in CLAUDE.md.

## What this did not fix

The defects this document originally listed as D5 and D6 — entity and relation vocabularies
collapsing (76% `Concept`, 78.5% `DEPENDS_ON`), and taxonomy tier 2 fragmenting on synonymy —
were untouched by the identity work. Re-measured and specified in
[vocabulary-diagnosis.md](vocabulary-diagnosis.md).

## The trap that remains

**A full `rebuild-graph` is not a repair.** It re-rolls every naming decision, changing which
duplicates exist rather than whether they exist. It is now safe — identity is canonical before
edges are drawn — but it fixes nothing on its own.
