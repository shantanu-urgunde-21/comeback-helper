# CLAUDE.md

Guidance for Claude Code working in this repository.

## Commands

```bash
python -m src.server                               # dashboard + API on 127.0.0.1:8000

# Tests — unittest, not pytest (pytest is not a dependency)
python -m unittest discover -s tests -v
python -m unittest tests.test_graph_indexer -v     # one module

# CLI
python -m src.cli graph-stats                      # node/edge counts, components, isolates
python -m src.cli graph-preview --note "path.md"   # dry-run extraction, writes nothing
python -m src.cli rebuild-graph                    # re-extract every vault note (LLM cost)
python -m src.cli query --prompt "..." --course "Differential Equations"

# Identity authority — .storage/concepts.db
python -m src.cli authority-seed-msc               # bulk-load MSC2020 taxonomy (idempotent)
python -m src.cli authority-resolve --label "..."  # alias -> Wikidata -> mint CUST_
python -m src.cli authority-stats                  # concept/alias/cache/review-queue counts

python scripts/graph_health.py                     # read-only report, stdlib only, no .env
```

Every verb accepts `--json`: exactly one JSON object on stdout, logs to stderr. That is the
`/comeback-helper` skill's contract ([SKILL.md](.claude/skills/comeback-helper/SKILL.md)) —
the skill talks to the engine *only* through these verbs, never by importing `src/` or
reading `graph.json`. **If a verb's output shape changes, update the skill in the same commit.**

`.env` is **required for any `import src`** — `gemini_api_key` and `obsidian_vault_location`
have no defaults ([config.py](services/shared/config.py)), so it fails at import time,
including in tests. Copy `.env.example`.

## Architecture

**Implementation lives in `services/`, not `src/`.** `src/` holds two entry points
(`server.py`, `cli.py`) plus `wiring.py`, the composition root that builds every package's
real classes into one process. One copy of every module. See
[services/README.md](services/README.md).

Modules import under short names — `shared.config`, `graph.app.indexer` — never
`services.shared.config`. `src/__init__.py` puts the services root on `sys.path`.
Load-bearing: a module reached under two names becomes two module objects with separate
state, which silently breaks the `--json` contract.

The **Obsidian vault is the source of truth**. Graph and vector index derive from it and are
rebuildable; vault notes are not (re-OCR costs money and re-rolls transcription).

```
PDF → OCR → vault/<course>/<note>.md ─┬→ 2-pass LLM extraction → SQLite (+ graph.json export)
                                      └→ math-aware chunking → FastEmbed → LanceDB
                                                    ↓
                                    hybrid retrieval (chunks + 1-hop subgraph) → answer
```

Three heavy singletons are built once in the FastAPI lifespan ([server.py](src/server.py))
and shared via `app.state`: `LocalVectorStore` → `MathGraphIndexer` → `MathQueryEngine(both)`.

**The graph lives in RAM, backed by SQLite.** `indexer.graph` is a live `nx.DiGraph` but a
*derived cache*; `.storage/concepts.db` is the store of record (`concepts`/`aliases` +
`mentions`/`edges`). `index_note()` writes both in the same call. `graph.json` is only an
export, for the two consumers that read it directly: `/api/graph` and `graph_health.py`.

Extraction is two LLM calls ([indexer.py](services/graph/app/indexer.py)). **Pass 1** runs
per markdown section (`chunk_id="{doc_id}#s{n:04d}"`): extracts nodes, resolves each to a
canonical id, writes `mentions`, accumulates `doc_concept_map`. **Pass 2** runs once on the
full document with that id-map and emits edges keyed by canonical id. Both fall back
Gemini → Ollama → deterministic block parser.

Deeper: [docs/flow.md](docs/flow.md) (data shapes), [docs/structure.md](docs/structure.md)
(call chains), [plan.md](plan.md) (roadmap, Phases 0–7 done).

## Invariants — breaking these causes silent, hard-to-trace bugs

- **`_resolve_entity` is a deterministic lookup, not embedding similarity.** Delegates to
  `authority.resolve_concept()`: document → course → Wikidata (cached) → mint `CUST_<hash>`.
  The node key is an opaque id; the human label lives in the `label` attribute. The
  extraction pipeline has no vector-store dependency at all.
- **A node's display `label` lives in `node_attrs_json`, not `concepts.label`.**
  `concepts.label` is identity bookkeeping (whichever surface form resolved first);
  `node_attrs_json["label"]` is the curated display name. Any write path must put `label` in
  the attrs dict passed to `upsert_node_attrs` — omitting it silently reverts the display
  name to whatever authority.py happened to store.
- **`export_graph_json()` writes `entity_type` under the key `type`** in graph.json, because
  `graph_health.py` and `/api/graph` parse the file directly. `load_graph()` — the real read
  path — has no such mapping.
- **`PREREQUISITE_FOR(A,B)` is canonicalized to `DEPENDS_ON(B,A)`** on write and load. Two
  directions between one pair create fake cycles that break hierarchical layout.
- **Notes are not graph nodes.** Which note a concept came from lives in its `provenance`
  list. The `CONTAINS` edge was retired; don't reintroduce it.
- **Retrieval finds graph seeds by embedding, then expands bounded.**
  `_find_similar_nodes()` embeds each node's `label`+`description` and compares to the query
  — node *ids* are opaque, so only the label carries meaning. Expansion goes through
  `MathGraphIndexer.neighborhood(ids, hops)`, never live `.neighbors()` on `.graph`. Do not
  source seeds from a vector chunk's `source` field (a note filename); filenames never match
  node ids and the lookup silently returns nothing.
- **`add_chunks()` deletes-by-source before inserting**, so re-indexing is idempotent. To
  rebuild the vector index: delete `.storage/lancedb`, then `POST /api/rebuild/vectors`.
- **Tests are not isolated**, with one exception. Most read and write the real `.storage/`,
  including the production LanceDB table; there is no teardown. `tests/test_graph_store.py`
  is the exception — it uses a throwaway `db_path` (an override every `authority.py` /
  `graph_store.py` function accepts). Follow that pattern for new SQLite-touching tests.
- **`scripts/` is gitignored.** Anything placed there won't be committed.

## Known defects

Graph identity is fixed (75 nodes, 0 duplicate groups). [docs/diagnosis.md](docs/diagnosis.md)
records the history — node identity used to be the LLM's display name, so one concept got
re-coined under several spellings.

Still open, specified in [docs/vocabulary-diagnosis.md](docs/vocabulary-diagnosis.md):
**type and relation vocabulary have collapsed** (76% `Concept`, 78.5% `DEPENDS_ON`), and the
graph is **not a DAG** (29 cycles). Plan:
[vocabulary-redesign](docs/superpowers/plans/2026-08-24-vocabulary-redesign.md).

One trap: **a full `rebuild-graph` is not a repair.** It re-rolls every naming decision,
changing which duplicates exist rather than whether they exist.

## Conventions

- Logging is Loguru via `from shared.logger import log` — not `print`, not `logging`.
- Config is read only through `get_settings()`, which is `lru_cache`d.
- CLI imports are function-local so `--help` doesn't load FastEmbed or NetworkX.
  `retrieval/app/engine.py` does not import NetworkX.
- New OCR providers subclass `BaseOCRProvider` and register in `IngestionPipeline.__init__`.
- `docs/` is public; `private_docs/` holds deeper design notes.
