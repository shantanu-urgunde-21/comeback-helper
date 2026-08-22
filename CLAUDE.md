# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
python -m src.cli graph-migrate-identity           # one-time: migrate existing nodes onto authority.py ids (writes .bak first)
python -m src.cli query --prompt "..." --course "Differential Equations"

# Identity authority (plan.md Phase 0/1) — .storage/concepts.db, independent of graph.json
python -m src.cli authority-seed-msc               # bulk-load MSC2020 taxonomy (idempotent)
python -m src.cli authority-resolve --label "..."  # resolve one surface form: alias -> Wikidata -> mint CUST_
python -m src.cli authority-stats                  # concept/alias/cache/review-queue counts

# Graph health report (read-only, stdlib only, no .env needed)
python scripts/graph_health.py
```

Every CLI verb accepts `--json`, which prints exactly one JSON object on stdout and routes
logs to stderr. That is the contract the `/comeback-helper` skill
([.claude/skills/comeback-helper/SKILL.md](.claude/skills/comeback-helper/SKILL.md)) is
built on: the skill talks to the engine **only** through these verbs, never by importing
`src/` or reading `graph.json`. Keep the verb surface stable when refactoring internals —
if a verb's output shape changes, update the skill in the same commit.

`.env` is **required for any import of `src`** — `Settings.gemini_api_key` and
`obsidian_vault_location` have no defaults ([services/shared/config.py](services/shared/config.py)),
so a missing `.env` fails at import time, including in tests. Copy `.env.example`.

## Architecture

**The implementation lives in `services/`, not `src/`.** `src/` holds only the two entry
points (`server.py`, `cli.py`) plus `wiring.py`, the composition root. There is one copy of
every module, and it runs in two deployments: in-process (the monolith, dependencies
injected by `wiring.py`) and containerised (`services/*/main.py`, dependencies defaulting to
the HTTP clients in `app/clients.py`). See [services/README.md](services/README.md) for the
two rules that keep both working, and [plan.md](plan.md) for where this is going.

Modules are imported under their container names — `shared.config`, `graph.app.indexer` —
never `services.shared.config`. `src/__init__.py` puts the services root on `sys.path` to
make that spelling resolve. This is load-bearing: a module reached under two names becomes
two module objects with separate state, which silently breaks the CLI's `--json` contract.

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
([services/graph/app/indexer.py](services/graph/app/indexer.py)): pass 1 emits concept
nodes + taxonomy, pass 2 links edges. Both fall back Gemini → Ollama → a deterministic
block parser.

For the full picture see [docs/flow.md](docs/flow.md) (data shapes, stage-by-stage I/O) and
[docs/structure.md](docs/structure.md) (call chains, module reference, dead code).

## Invariants — breaking these causes silent, hard-to-trace bugs

- **`_resolve_entity` is a deterministic lookup, not embedding similarity, as of plan.md
  Phase 1.** It delegates to `authority.resolve_concept()` (`services/graph/app/authority.py`):
  document → course → global-authority (Wikidata, on-demand + cached in
  `.storage/concepts.db`) → mint a `CUST_<hash>` id. It no longer needs `vector_store` at
  all — a node's graph key is now an opaque id (a QID or `CUST_` hash), with the human-
  readable name stored separately in that node's `label` attribute. `vector_store` is still
  used for Pass-2 LLM candidate context (`_get_candidate_context`) — nothing else. The old
  `dedupe_graph()`/`ENTITY_MERGE_THRESHOLD` cosine-merge path was deleted in plan.md Phase 6;
  there is no dead code left on this path.
- **`save_graph()` writes `entity_type` as `type`**, and `_load_graph` renames it back.
  Anything reading `graph.json` directly must expect `type`.
- **`PREREQUISITE_FOR(A,B)` is canonicalized to `DEPENDS_ON(B,A)`** on both write and load.
  Never emit or store the inverse form — two directions between the same pair create fake
  cycles that break hierarchical layout.
- **Notes are not graph nodes.** The `CONTAINS` note→concept edge was retired; which note a
  concept came from lives in that concept's `provenance` list. Do not reintroduce it.
- **`_load_graph` still normalizes in memory only.** It renames `type` back to `entity_type`,
  normalizes taxonomy domain casing, and drops legacy `CONTAINS` edges on every startup, but
  only reaches disk if something later calls `save_graph()`. The snake_case/Title-Case
  duplicate-folding self-heal that used to live here was deleted in plan.md Phase 6 — node
  identity is now canonical at write time (Phase 1/2), so there is nothing left to fold on
  load.
- **Tests are not isolated.** They read and write the real `.storage/` — the live
  `graph.json` and the production LanceDB table. `tests/test_vector_and_retrieval.py`
  inserts chunks into it. There is no fixture directory or teardown.
- **`scripts/` is gitignored** ([.gitignore:37](.gitignore#L37)). Anything placed there
  won't be committed.

## Known defects — read before "fixing" the graph

[docs/diagnosis.md](docs/diagnosis.md) documents six measured defects, their root cause, and
recommendations in dependency order. The short version, **as it stood before plan.md Phases
0-1 landed**: node identity was the LLM-generated display name (`GraphNode.id` defaulted to
`name`), so the same concept got re-coined as `Lipschitz Condition` / `lipschitz-condition` /
`lipschitz_condition` and embedding similarity was used to repair it after the fact.

**That root cause is fixed, both for new extractions and for the live graph.** See the
`_resolve_entity` invariant above for new extractions; `.storage/graph.json` itself was
migrated onto the new scheme via `graph-migrate-identity` (plan.md Phase 2) — 119 nodes
(the 123 on-disk minus 4 folded by `_load_graph`'s self-heal) became 75: 17 junk nodes
dropped (retired note-containers, a relation name that leaked in as a node, placeholder
labels, a LaTeX fragment) and 27 duplicate spellings merged onto canonical ids.
`graph_health.py` now reports 0 duplicate groups against the live file. A `.bak` of the
pre-migration file was written to `.storage/graph.json.bak`.

One trap remains:

- **A full `rebuild-graph` is not a repair.** It re-rolls every naming decision, changing
  which duplicates exist rather than whether they exist.

(`ENTITY_MERGE_THRESHOLD`, `dedupe_graph()`, and the `_snake_case_redirects` self-heal — the
other traps this section used to warn about — no longer exist; plan.md Phase 6 deleted them
now that identity is canonical before edges are drawn.)

## Conventions

- Logging is Loguru via `from shared.logger import log` — not `print`, not `logging`.
- Config is read only through `get_settings()`, which is `lru_cache`d.
- CLI imports are function-local so `--help` doesn't load FastEmbed or NetworkX.
- New OCR providers subclass `BaseOCRProvider` and register in
  `IngestionPipeline.__init__`'s provider switch.
- `docs/` is public documentation; `private_docs/` holds deeper design notes.
