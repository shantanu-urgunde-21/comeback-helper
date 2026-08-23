# Plan: the Base-Graph Atlas

The single idea, the target design, and the order to get there.

Companion docs: [docs/diagnosis.md](docs/diagnosis.md) (why the current graph fails),
[docs/flow.md](docs/flow.md) (how data moves today), [docs/structure.md](docs/structure.md)
(call chains), [services/README.md](services/README.md) (the decomposition).

---

## The idea, in one page

Every defect in the current graph traces to one absence: **nothing decides what a concept
is called before edges are drawn between concepts.** `GraphNode.id` defaults to the
LLM-generated display name, so the same idea gets re-coined as `Lipschitz Condition`,
`lipschitz-condition`, `lipschitz_condition` — and embedding similarity is then paid,
repeatedly, to guess which of those were meant to be the same thing.

The fix is to assign identity **before** extracting relationships, deterministically, from
an authority that lives outside the model. That is the Base-Graph proposal and it is right.

The one correction it needs: **a surface string and a concept are not the same object.**
`T` is a linear map in one lecture, a topology in another; `L` is a Lipschitz constant here
and a differential operator there. Overloading is the default in mathematics, not an edge
case. A global string→ID map would make the graph cleaner and less true — and the
distinctions it would flatten are precisely the ones this atlas exists to show.

So: **resolve identity deterministically, but resolve it in scope.**

```
mention  ──resolve(scope)──▶  concept  ──▶  edges drawn between concept ids
(surface form,               (canonical,
 at a location)               global)
```

---

## Target data model

Four tables. The one that carries the idea is `mentions`.

```sql
concepts (
  id              TEXT PRIMARY KEY,   -- Q1059, or CUST_<hash of normalized key>
  label           TEXT NOT NULL,      -- display name
  msc_code        TEXT,               -- MSC2020, closed vocabulary (replaces free-text taxonomy)
  authority       TEXT,               -- wikidata | msc | local
  authority_ver   TEXT,               -- so seeding is re-runnable, not once-only
  status          TEXT                -- confirmed | provisional
);

aliases (
  surface_norm    TEXT NOT NULL,      -- normalized key, NOT the raw string
  concept_id      TEXT NOT NULL REFERENCES concepts(id),
  scope           TEXT NOT NULL,      -- global | course | document
  scope_ref       TEXT,               -- course name or doc id when scoped
  PRIMARY KEY (surface_norm, scope, scope_ref)
);

mentions (
  chunk_id        TEXT NOT NULL,
  surface_text    TEXT NOT NULL,      -- exactly as written on the page
  concept_id      TEXT NOT NULL REFERENCES concepts(id),
  char_span       TEXT
);

edges (
  source_id       TEXT NOT NULL REFERENCES concepts(id),
  target_id       TEXT NOT NULL REFERENCES concepts(id),
  relation        TEXT NOT NULL,
  chunk_id        TEXT,               -- provenance: where this was claimed
  quote           TEXT,               -- the sentence that supports it
  origin          TEXT NOT NULL       -- extracted | inferred | authority
);
```

`mentions` gives provenance for free, lets the same string resolve differently in different
documents, and preserves *how a concept was written in each place* — which for a maths
atlas is content, not metadata.

`edges.origin` is the `EXTRACTED`/`INFERRED` split. The `atlas-model-b` branch already had
this as `sources: ["llm"] | ["wikipedia"]` in `review_queue.json`. Bring it forward rather
than reinventing it.

### The resolution ladder

Narrowest scope first. Never a similarity threshold.

| Rung | Rule |
|---|---|
| **document** | Surface form already bound in this document? Reuse that binding. |
| **course** | Bound elsewhere in this course? Reuse — notation is usually stable within a course. |
| **global** | Exact match on the normalized key against the authority. |
| **miss** | Mint `CUST_<hash(normalized key)>`, propose near-matches, **queue for review**. |

Two rules that make or break this:

1. **Hash the normalized key, never the raw surface.** `hash("ker(T)")` and
   `hash("kernel of T")` are different IDs for one concept — the current bug in hex. Use the
   same fold `scripts/graph_health.py::normalize` already implements.
2. **Fuzzy matching proposes, it never commits.** `LIKE '%ker(T)%'` over a namespace full of
   single letters will confidently unify `ker(T)` and `ker(S)`. Exact-on-normalized is the
   only path that writes without review.

---

## Target topology

Five services, already isolated in [`services/`](services/). Dependency edges:

```
ingestion ──▶ vault                    (vault is the only writer)
graph     ──▶ vault
retrieval ──▶ graph, vector
```

Two edges present today that the rewrite **removes**:

- `graph ──▶ vector` — exists only for embedding-based entity resolution. Deterministic
  lookup replaces it, and the graph service stops needing the vector service at all.
- `retrieval` rebuilding the whole graph locally — replaced by the graph service's
  `/neighborhood` endpoint, after which retrieval no longer needs `networkx`.

That is the test of whether this design is working: **the dependency graph gets sparser.**

---

## Order of work

Each phase is independently landable and leaves the system working. Phases 1–2 belong in the
monolith; only from phase 3 does the service split start to matter.

### Phase 0 — Seed the authority — **DONE** (revised scope, see below)
- Fetch MSC2020 (taxonomy tier) and a Wikidata mathematics subset (concept tier).
- Write `concepts` + `aliases` with `authority_ver` stamped.
- **Idempotent and re-runnable.** "Run once" is a trap: coverage you want later isn't in
  today's snapshot, and re-seeding must not orphan existing IDs.
- *Use them at different tiers.* MSC2020 is ~6k subject areas, not a concept list — it
  replaces the free-text `domain`/`subdomain` fields. Wikidata supplies concept identity.
  Import Wikidata *edges* selectively or not at all: they are ontological (`subclass of`),
  and this atlas needs pedagogical (`must understand first`).

**Exit:** `concepts` populated, `graph_health.py` unchanged, nothing else touched.

**Measured, then revised:** open question 1 (below) was answered before building this —
Wikidata exact-label coverage on 92 real concepts from the live graph is ~15-21%, not the
near-total coverage bulk-seeding would imply is worth curating for. So Phase 0 shipped as:
MSC2020 bulk-seeded in full (6,603 codes, real data from `msc2020.org/MSC_2020.csv`, cp1252
encoded — not UTF-8, causes a silent mis-decode of accented names like "Picard-Lindelöf" if
you assume otherwise), and Wikidata as an **on-demand, cached lookup** instead of a curated
subset — a normalized key crosses the network at most once, ever; the local corpus grows
from usage, not from a one-time import. Implementation: `services/graph/app/authority.py`
(`concepts`/`aliases`/`msc_taxonomy`/`wikidata_lookup_cache`/`review_queue` tables in
`.storage/concepts.db`). CLI: `authority-seed-msc`, `authority-resolve --label`,
`authority-stats`.

### Phase 1 — Identity layer in the monolith — **DONE**
- Add `normalize()` to `graph/schema.py` (lift from `scripts/graph_health.py`).
- Give `GraphNode` a canonical key separate from its display name.
- Make `_resolve_entity` a lookup: normalized key → alias table → scope ladder. Embeddings
  demoted to *proposing* review-queue candidates only.
- **This is the prerequisite for everything else.** An extractor that looks up concepts,
  pointed at a graph that still holds three Lipschitz nodes, will link to whichever it finds
  first and cement the duplicates.

**Exit:** `graph_health.py` reports 0 duplicate groups.

**Shipped:** `normalize()` lives in `services/graph/app/schema.py`. `_resolve_entity` in
`services/graph/app/indexer.py` now delegates to `authority.resolve_concept()` — the
document → course → global → mint ladder — and needs no `vector_store` at all (the plan's
"dependency graph gets sparser" test, one edge down). `GraphNode`'s id is now genuinely
opaque (a Wikidata QID or `CUST_<hash>`); nodes carry a separate `label` field for display,
threaded through `save_graph()` and the Pass-2 candidate-context prompt (both used to assume
node key == display name — that assumption is gone now, watch for it resurfacing anywhere
else that reads a node id and expects readable text).

Verified live against a real note (`MA301 Lecture 4.md`, isolated scratch storage, not the
production `graph.json`): `Wronskian` → `Q124743`, `Characteristic Equation` → `Q33104580`,
two concepts with no Wikidata match minted deterministic `CUST_` ids, all four edges
resolved consistently. Full test suite: 11/12 pass, the one failure is the pre-existing
corrupted-LanceDB issue this same document schedules a fix for in Phase 5, unrelated to this
work. **Gap:** no permanent unit test added yet for the new resolver path — tests still only
exercise `extraction`/schema objects directly, not `index_note`'s resolution. `dedupe_graph()`
and `ENTITY_MERGE_THRESHOLD` are untouched (still there, unused by the new path, deletion is
Phase 6) and the live 119-node `graph.json` is untouched (old string-keyed nodes) — that
migration is Phase 2.

### Phase 2 — Migrate the live graph — **DONE**
- Map each of the existing 123 nodes through its alias list to a canonical id. This is where
  the currently write-only `aliases` data finally earns its keep.
- The 14 duplicate groups collapse as a side effect (123 → ~108).
- Drop the 13 orphaned note-container nodes left behind when `CONTAINS` was retired, the
  relation-name node (`DEPENDS_ON`), the placeholder labels, and the LaTeX fragment.
- Deduplicate provenance records on write (60 nodes currently carry repeats).

**Exit:** node count reflects concepts, not spellings. Isolated nodes are real, not debris.

**Shipped:** `MathGraphIndexer.migrate_to_identity_layer()` in
`services/graph/app/indexer.py`, exposed as `python -m src.cli graph-migrate-identity`
(writes `graph.json.bak` first — this mutates the live graph, so it's not auto-run). Ran
against the actual 119-node live graph (the 123 on-disk nodes minus 4 already folded by
`_load_graph`'s in-memory self-heal): **17 junk nodes dropped, 27 duplicates merged, landing
at 75 nodes / 121 edges.** `scripts/graph_health.py` confirms **0 duplicate groups** (was 14)
against the migrated file. Node display labels are picked separately from the canonical id —
a small tiered heuristic (proper name > name-with-digits > everything else, shortest within
a tier) over every id/label/alias in a merged group, needed because the "richest" member by
description/degree is often *not* the best-looking spelling (e.g. lowercase `wronskian`, or
literal notation like `W(y1, y2)` recorded as an alias) and the graph is meant to be read.
Provenance dedup on write was already free from reusing `dedupe_graph()`'s merge shape.
9 isolated nodes remain — real standalone concepts now, not debris (verified via
`graph_health.py`, which also reports these separately from suspect/junk).

### Phase 3 — SQLite behind the graph service — **DONE**
- Implement the four tables. `graph.json` becomes an export format, not the store of record.
- Keep `nx.DiGraph` as a **derived, rebuildable projection** — do not delete it. Traversal,
  topological layering, cycle detection and community detection are one-liners in NetworkX
  and painful recursive CTEs in SQL. Demote it from truth to cache.

**Exit:** graph service's public endpoints unchanged; internals relational.

**Shipped:** new `mentions`/`edges` tables in `.storage/concepts.db`
(`services/graph/app/graph_store.py`), joining the `concepts`/`aliases` tables Phase 0/1
already populate. One deliberate deviation from the literal schema: `concepts` gained an
additive `node_attrs_json` column (entity_type/taxonomy/description/provenance/aliases/label
as one JSON blob) rather than typed columns for `description`/taxonomy — nothing queries
those fields via SQL yet, and typed columns would be schema investment in a shape this
document's own "What this deletes" table already marks for replacement by `msc_code`.
`msc_code`/`msc_taxonomy` bulk-seeding (`authority-seed-msc`) ran on 2026-08-24, well after
this section was written — 6,603 codes loaded (`msc_codes: 6603`). The `concepts`/`aliases`
tables it feeds still aren't consulted by anything on the extraction write path (that's the
"Free-text domain/subdomain" row in "What this deletes", still Not started); seeding populated
the table but did not wire it in. `index_note()` dual-writes: the existing in-memory
`self.graph.add_node`/`add_edge` calls are untouched, and SQLite writes happen alongside —
including finally reading `edge.description` (Pass-2 already asks the LLM for evidence
quotes; nothing persisted them before this). `_load_graph`/`save_graph` flipped to
`graph_store.load_graph`/`export_graph_json`; a one-time `graph-backfill-sql` CLI verb
populated the new tables from the live 75-node/121-edge graph before the flip.
`clear_graph()` now also clears SQLite structure (not just graph.json) — see its docstring
for why this was a real gap, not a hypothetical one, once SQLite became the store of record.

**Bug caught during this phase, not shipped broken:** the first backfill run used
`concepts.label` (authority.py's identity-resolution bookkeeping — whichever surface form
first resolved a concept) as the graph node's display label, instead of the graph's own
curated label (e.g. Phase 2's `migrate_to_identity_layer` best-of-group spelling) — a
byte-diff of the re-exported `graph.json` against a pre-flip backup caught all 62 nodes'
labels silently reverting. Fixed by storing `label` inside `node_attrs_json` itself and
preferring it on read; see the CLAUDE.md invariant on this. Verified after the fix: 0 diffs
node-for-node and edge-for-edge against the pre-Phase-3 graph.json, full test suite
unchanged (11/12, same pre-existing LanceDB failure), `graph_health.py` unchanged
(75/121/10 components/9 isolated/0 duplicate groups), and an end-to-end `query` smoke test
still finds node descriptions post-flip.

**Not shipped — deliberately out of scope, not forgotten:** `msc_code` assignment/MSC
bulk-seeding (no domain-string→MSC mapper exists); the `graph → vector` dependency Phase 6
left narrowed (Pass-2 candidate context still calls `vector_store.search_similar()` — see
Phase 6's note, unchanged by this phase); retrieval still reads `indexer.graph`/`/graph`
directly rather than `/neighborhood` (Phase 5's job).

### Phase 4 — Resolve-then-link extraction — **DONE**
- Pass 1 becomes: identify surface forms → `resolve_concept()` → return concept ids.
- Pass 2 receives **ids**, not names, and is told to use only those ids.
- **Accumulate resolved ids across the document, not per chunk.**
- Every edge carries `chunk_id`, `quote`, `origin`.

**Exit:** new ingests add no duplicate concepts; edges carry evidence.

**Shipped:** `index_note()` now splits the note into chunks (`_split_chunks()`, by H1–H3
heading, `chunk_id = "{doc_id}#s{n:04d}"`). Pass 1 runs per chunk: block or LLM extraction
→ `_resolve_entity()` per node → chunk-level `insert_mention()` → accumulate
`doc_concept_map: dict[name→id]`. All `_resolve_entity()` calls happen before
`graph_store.connect()` opens (avoids SQLite WAL lock contention between two write-capable
connections to `concepts.db`). Pass 2 runs once on full text: new `PASS2_EDGE_PROMPT`
passes `{concept_id → name}` dict so the LLM emits edges keyed by canonical ID; new
`_normalize_edge_endpoint()` resolves LLM output to canonical IDs (passthrough → name
lookup → `normalize()`-folded → warn+skip). No `_resolve_entity()` calls on edge endpoints
any more. `_get_candidate_context()` now returns `dict[str,str]` (id→label); the
vector-store branch was dead (chunk `source` = note filename, never matched a QID/CUST_
graph key) and has been removed with a Phase 5 TODO. Branch: `phase4-resolve-then-link`,
4 commits (`6bd2ec9`…`ff73c02`). Tests: 24/25 (1 pre-existing LanceDB failure, Phase 5).

### Phase 5 — Retrieval over the new shape — **DONE**
- ✓ Engine calls `/neighborhood` instead of reconstructing the graph (retrieval/app/engine.py).
- ✓ `add_chunks` delete-by-source before insert for idempotent re-indexing (vector/app/store.py).
- ⏳ Serialize that subgraph straight to the vis.js payload — bounded, so the frontend layout
  stops struggling (optimization, not blocking).

**Exit:** retrieval no longer imports `networkx`. To rebuild vector index from scratch:
`rm -rf .storage/lancedb && python -m src.cli rebuild-graph`

### Phase 6 — Delete what identity made unnecessary — **DONE**
- ✓ `dedupe_graph()` — nothing to repair when ids are canonical before edges exist.
- ✓ `ENTITY_MERGE_THRESHOLD` and the whole cosine-merge path.
- ✓ `_snake_case_redirects` and the load-time self-heal.
- ✓ Embedding-based node matching from retrieval (Phase 5).
- ✓ Updated diagnosis.md to describe historical issues, not current state.

**Exit:** the graph is healthy (75 nodes, 122 edges, 0 duplicate groups); diagnosis document
describes the pre-fix era only. `/comeback-helper` skill is the only client of the graph API.
`/dedupe` HTTP endpoint are deleted from `services/graph/app/indexer.py`,
`services/graph/main.py` and `src/cli.py`. `_snake_case_redirects()` and the id-folding
block it fed in `_load_graph()` are deleted too; `_load_graph()` now only does the
unrelated, still-needed normalization (rename `type`→`entity_type`, taxonomy domain
casing, drop legacy `CONTAINS` edges) — nothing left to self-heal since identity is
canonical at write time (Phases 1-2). `VectorStoreClient.embed_texts()` in
`services/graph/app/clients.py` is deleted (it existed only for `dedupe_graph()`'s cosine
comparison).

**Not shipped — the `graph ──▶ vector` dependency stays, narrowed but not removed.**
`_get_candidate_context()` still calls `self._vector_store.search_similar()` for Pass-2 LLM
candidate context (existing concept names fed into the edge-linking prompt), and
`services/graph/main.py` still constructs `MathGraphIndexer(vector_store=VectorStoreClient())`
to support it. Removing this dependency outright requires re-sourcing Pass-2 candidates from
the concept table instead of chunk search — deferred, since that's a design change (which
concepts to offer as candidates), not a deletion, and belongs with Phase 3/4 once the concept
table is the thing to source from.

### Phase 7 — Assemble — **DONE**
- ✓ Decided the real topology: single process. The container-per-service split
  (`docker-compose.yml`, 5 Dockerfiles, 5 `main.py` FastAPI shims, HTTP client stand-ins in
  `app/clients.py`) was staged for a deployment that was never actually run — deleted.
  `services/<name>/app/` module boundaries are kept; `src/wiring.py` remains the single
  composition root.
- ✓ `MathGraphIndexer.neighborhood()` added to the real class (was only on the now-deleted
  HTTP client stub) — fixes a bug where the Phase 5 retrieval change would have thrown
  `AttributeError` in the monolith the first time a query hit the graph-context branch.
- ✓ Dropped the dead `vector_store` param from `MathGraphIndexer.__init__` — threaded through
  `wiring.py` but never read.

**Exit:** the app runs as one process; `services/README.md` and `CLAUDE.md` describe that
topology, not a staged microservice split.

---

## What this deletes

| Goes away | Because | Status |
|---|---|---|
| Embedding-based entity resolution | Deterministic lookup replaces it | Done (Phase 1) |
| `ENTITY_MERGE_THRESHOLD` | No threshold exists that separates the two populations | Done (Phase 6) |
| `dedupe_graph()` | Nothing to deduplicate after the fact | Done (Phase 6) |
| Load-time self-heal | Nothing to heal | Done (Phase 6) |
| `graph.json` as source of truth | Becomes an export | Done (Phase 3) |
| Free-text `domain` / `subdomain` | MSC2020 codes | Not started |
| `graph → vector` dependency | Resolution no longer needs embeddings | Done (Phase 7) — dead `vector_store` param removed from `MathGraphIndexer` |
| Container-per-service deployment | Never actually run; single process is simpler for one user | Done (Phase 7) |

---

## Open questions

1. ~~**Wikidata coverage for undergraduate maths** is thinner than it looks.~~ **Measured.**
   92 canonical concepts (deduped via `normalize()`) across all 13 lecture notes in the live
   differential-equations course — a bigger sample than "one lecture." Raw stored spelling:
   14/92 (15%) exact label match. Humanized (kebab/snake → spaces) before querying: 19/92
   (21%) — the other 5 were reclassified from "fuzzy hit" to "exact," not rescued from
   "miss"; the miss count (62/92, 67%) is identical either way. The "close but not exact"
   bucket (11-16/92) is mostly noise — single-token-overlap academic paper titles (`Mixing
   Problem` → hepatic-artery-infusion papers), not real disambiguation candidates a review
   queue could act on. **Conclusion, acted on:** yes, most concepts fall through to `CUST_*`
   (~79%) — the review queue is the majority path, not an edge case, confirming the
   suspicion below. Decision: don't pre-curate a Wikidata subset (low payoff at ~20%); do
   on-demand exact lookup instead, cached so the network cost is paid once per normalized
   key ever. See Phase 0.
2. **Who curates the review queue?** It is the quality mechanism, so it needs an owner and a
   surface. An agent pre-triaging into obvious/uncertain would keep it tractable.
3. **Scope granularity.** Document-level may still be too coarse where notation is rebound
   mid-lecture. Section-level is more correct and more expensive; start with document and
   measure.
4. **Relation vocabulary.** 77% of current edges are `DEPENDS_ON` and 0 are `USES_AXIOM`.
   Before enriching the schema, find out whether the vocabulary is too fine for the model to
   use reliably — a smaller, well-used vocabulary beats a large, ignored one.
