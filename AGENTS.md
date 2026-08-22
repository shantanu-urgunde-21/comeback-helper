# AGENTS.md

Orientation for coding agents working in this repository.

**[CLAUDE.md](CLAUDE.md) is the canonical, detailed guide.** It is kept current; this file
is a short vendor-neutral entry point that defers to it rather than restating it, so the two
cannot drift apart.

## Commands

```bash
# Run the server (dashboard + API on http://127.0.0.1:8000, --reload enabled)
python -m src.server

# Tests — unittest, not pytest (pytest is not a dependency)
python -m unittest discover -s tests -v
python -m unittest tests.test_graph_indexer -v                    # one module
python -m unittest tests.test_graph_indexer.TestGraphIndexer.test_schema_models   # one test

# CLI
python -m src.cli graph-stats                      # node/edge counts, components, isolates
python -m src.cli graph-preview --note "path.md"   # dry-run extraction, writes nothing
python -m src.cli rebuild-graph                    # re-extract every vault note (LLM cost)
python -m src.cli graph-dedupe                     # merge duplicate nodes, then save
python -m src.cli query --prompt "..." --course "Differential Equations"

# Graph health report (read-only, stdlib only, no .env needed)
python scripts/graph_health.py
```

`.env` is **required for any import of `src`** — `Settings.gemini_api_key` and
`obsidian_vault_location` have no defaults ([src/config.py](src/config.py)), so a missing
`.env` fails at import time, including in tests. Copy `.env.example`.

## Architecture

Four subsystems behind one FastAPI process. The **Obsidian vault is the source of truth**;
the graph and the vector index both derive from it and are rebuildable, while the vault
notes are not (re-OCR costs money and re-rolls transcription).

```
PDF → OCR → vault/<course>/<note>.md ─┬→ 2-pass LLM extraction → NetworkX graph → graph.json
                                      └→ math-aware chunking → FastEmbed → LanceDB
                                                    ↓
                                    hybrid retrieval (chunks + graph traversal) → answer
```

Three heavy objects are constructed once in the FastAPI lifespan
([src/server.py](src/server.py)) and shared via `app.state`, in dependency order:
`LocalVectorStore` → `MathGraphIndexer(vector_store=…)` → `MathQueryEngine(both)`.

**The graph lives in RAM.** `app.state.graph_indexer.graph` is the live `nx.DiGraph`;
`graph.json` is only a snapshot written by `save_graph()`. In-memory mutations that aren't
followed by a save are lost on restart.

Graph extraction is deliberately two decoupled LLM calls
([src/graph/indexer.py](src/graph/indexer.py)): pass 1 emits concept nodes + taxonomy,
pass 2 links edges. Both fall back Gemini → Ollama → a deterministic block parser.

For the full picture see [docs/flow.md](docs/flow.md) (data shapes, stage-by-stage I/O) and
[docs/structure.md](docs/structure.md) (call chains, module reference, dead code).

## Invariants — breaking these causes silent, hard-to-trace bugs

- **`MathGraphIndexer` without a `vector_store` silently disables entity resolution.**
  `_resolve_entity` short-circuits and returns the name unchanged. Always pass one when
  the indexer will write. The server does; only two of the six CLI commands do.
- **`save_graph()` writes `entity_type` as `type`**, and `_load_graph` renames it back.
  Anything reading `graph.json` directly must expect `type`.
- **`PREREQUISITE_FOR(A,B)` is canonicalized to `DEPENDS_ON(B,A)`** on both write and load.
  Never emit or store the inverse form — two directions between the same pair create fake
  cycles that break hierarchical layout.
- **Notes are not graph nodes.** The `CONTAINS` note→concept edge was retired; which note a
  concept came from lives in that concept's `provenance` list. Do not reintroduce it.
- **`_load_graph` self-heals in memory only.** It folds snake_case duplicates, normalizes
  domain casing and drops legacy edges on every startup, but only reaches disk if something
  later calls `save_graph()`. The live file currently holds 123 nodes while the loaded graph
  is 119 — that gap is this, not a bug in either number.
- **Tests are not isolated.** They read and write the real `.storage/` — the live
  `graph.json` and the production LanceDB table. `tests/test_vector_and_retrieval.py`
  inserts chunks into it. There is no fixture directory or teardown.
- **`scripts/` is gitignored** ([.gitignore:37](.gitignore#L37)). Anything placed there
  won't be committed.

## Known defects — read before "fixing" the graph

[docs/diagnosis.md](docs/diagnosis.md) documents six measured defects, their root cause, and
recommendations in dependency order. The short version: node identity is the LLM-generated
display name (`GraphNode.id` defaults to `name`), so the same concept gets re-coined as
`Lipschitz Condition` / `lipschitz-condition` / `lipschitz_condition` and embedding
similarity is then used to repair it after the fact.

Two traps in particular:

- **Do not tune `ENTITY_MERGE_THRESHOLD`.** It was raised to 0.93 to stop false merges, and
  it still misses exact duplicates whose descriptions were worded differently. The two
  populations overlap; no threshold separates them. The fix is a deterministic key plus
  reading the (currently write-only) `aliases` list, not a better number.
- **A full `rebuild-graph` is not a repair.** It re-rolls every naming decision, changing
  which duplicates exist rather than whether they exist.

## Conventions

- Logging is Loguru via `from src.logger import log` — not `print`, not `logging`.
- Config is read only through `get_settings()`, which is `lru_cache`d.
- CLI imports are function-local so `--help` doesn't load FastEmbed or NetworkX.
- New OCR providers subclass `BaseOCRProvider` and register in
  `IngestionPipeline.__init__`'s provider switch.
- `docs/` is public documentation; `private_docs/` holds deeper design notes.
