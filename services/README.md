# services/ — the implementation, split into modules

Five packages, each owning one concern. **This is the running app** — `src/server.py` and
`src/cli.py` are thin entry points; everything they do lives here, imported and wired
together in one process by `src/wiring.py`.

**There is exactly one copy of every module.** `src/` holds only the two entry points plus
`wiring.py`, the composition root. Editing a service changes what the running app does
immediately — no porting step, no drift between "the code" and "what's deployed."

Plan.md Phase 7 decided this deliberately: an earlier version of this tree also carried a
parallel container-per-service deployment (`Dockerfile`, `main.py` FastAPI shim, HTTP
client stand-ins per package) staged for a microservice split that was never actually run.
For a single-user local app, the extra indirection bought nothing — it was deleted, and the
module boundaries below are kept because they are still worth having on their own.

---

## Layout

```
services/
├── shared/                config, logger, LLM clients
│   ├── config.py
│   ├── logger.py
│   └── llm/{gemini,ollama}.py
└── <service>/
    └── app/                the implementation
```

Modules are imported under their container-style names (`shared.config`, `graph.app.indexer`)
rather than `services.graph.app.indexer`. That's load-bearing, not cosmetic: a module reached
under two names becomes two module objects with separate state, and `logger.py` installs a
Loguru sink at import — a dual identity would quietly produce two stdout sinks and break the
CLI's `--json` contract. `src/__init__.py` puts `services/` on `sys.path` to keep one spelling.

---

## The packages

| Package | Owns | Depends on |
|---|---|---|
| **vault** | Obsidian notes, SHA-256 ingest state | — |
| **vector** | LanceDB, FastEmbed, chunking | — |
| **ingestion** | PDF → Markdown (OCR) | vault |
| **graph** | Concept extraction, the graph (SQLite-backed) | vault |
| **retrieval** | Hybrid context, answer synthesis | graph, vector |

`graph` no longer depends on `vector` — entity resolution is a deterministic SQLite lookup
(`graph/app/authority.py`, plan.md Phase 1), not embedding similarity. `retrieval` no longer
imports `networkx` — it calls `MathGraphIndexer.neighborhood()` for a bounded 1-hop subgraph
instead of walking the whole graph (plan.md Phase 5).

Each package still takes its collaborators as constructor arguments rather than importing
them at module scope, and each falls back to constructing the real class when nothing is
injected — that's what lets `wiring.py` build the shared singletons once and lets tests
construct a package in isolation with no args.
