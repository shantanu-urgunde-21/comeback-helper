# services/ — isolated, containerised, stashed

Five services carved out of `src/`, each independently buildable and runnable. **Nothing
here is wired into the running app.** The monolith still serves everything on `:8000` from
`src/`; this directory is a staging area for the rewrite described in [../plan.md](../plan.md).

**There is exactly one copy of every module, and it lives here.** `src/` was reduced to the
two entry points (`server.py`, `cli.py`) plus `wiring.py`; everything they need is imported
from these packages. Editing a service therefore changes what the running app does
immediately — no porting step, and no way for the two to drift.

Each package runs in **two deployments**, and both are verified working:

| | How it is reached | Dependencies come from |
|---|---|---|
| **Container** | `main.py`, PYTHONPATH `/srv` | HTTP clients in `app/clients.py` (default) |
| **In-process** | `src/wiring.py` | Real objects, injected |

Two rules keep that dual life working — break either and one deployment fails silently:

1. **Intra-package imports are relative** (`from .clients import`). An absolute `app.x`
   only resolves when that service's directory is on `sys.path`, which is true in its own
   container and false when several services share one process — they would all claim the
   name `app`.
2. **Nothing imports a client at module scope.** `indexer.py` and `engine.py` take their
   collaborators as constructor arguments and import the HTTP fallback lazily. A module-level
   client import would hard-wire the package to one deployment shape.

Module names are identical in both deployments (`shared.config`, not
`services.shared.config`). That is load-bearing, not cosmetic: a module reached under two
names becomes two module objects with separate state, and `logger.py` installs a Loguru sink
at import — so a dual identity quietly produces two stdout sinks and breaks the CLI's
`--json` contract. `src/__init__.py` puts the services root on `sys.path` to keep one
spelling.

---

## Layout

```
services/
├── docker-compose.yml     assembly definition (not run against live data)
├── shared/                config, logger, LLM clients — copied into every image
│   ├── config.py
│   ├── logger.py
│   └── llm/{gemini,ollama}.py
└── <service>/
    ├── Dockerfile
    ├── requirements.txt   only what this service actually needs
    ├── main.py            FastAPI shim — the service's contract
    └── app/               the extracted implementation
        └── clients.py     HTTP stand-ins for what used to be imports
```

Imports were rewritten during extraction: `src.config` → `shared.config`,
`src.llm.*` → `shared.llm.*`, and intra-service modules → `app.*`. No `src.` imports remain.

---

## The services

| Service | Port | Owns | Depends on |
|---|---|---|---|
| **vault** | 8001 | Obsidian notes, SHA-256 ingest state | — |
| **vector** | 8003 | LanceDB, FastEmbed, chunking | — |
| **ingestion** | 8002 | PDF → Markdown (OCR) | vault |
| **graph** | 8004 | Concept extraction, the graph | vault, vector\* |
| **retrieval** | 8005 | Hybrid context, answer synthesis | graph, vector |

\* `graph → vector` exists **only** for embedding-based entity resolution. It disappears
under the Base-Graph design. Watch this table get sparser as the rewrite lands — that is the
signal the design is working.

### Contracts

```
vault      GET  /notes /note /courses /health
           POST /note /state/{update,save,clear}
vector     POST /embed /search /chunk /index      GET /stats /health
ingestion  POST /ingest                           GET /health /health/ollama
graph      POST /extract /index /rebuild /neighborhood /dedupe
           GET  /graph /stats /health
retrieval  POST /query /context /refresh          GET /health
```

---

## Running

```bash
cd services
docker compose build
docker compose up vault vector       # leaves only
docker compose up                    # full assembly
```

Reads `../.env`. Storage and vault are shared named volumes — the vault is one source of
truth, and everything else is derived from it.

Import-check without Docker, from the repo root:

```bash
python -c "import sys,os; sys.path[:0]=[os.path.abspath('services'),os.path.abspath('services/graph')]; import main; print(len(main.app.routes),'routes')"
```

All five currently import clean.

---

## What the extraction exposed

Isolation is a good way to find out where the boundaries were wrong. Three findings:

**1. Retrieval reaches into the graph as a live object.** `engine.py` calls `.neighbors()`,
`.predecessors()` and `.nodes[...]` on a real `nx.DiGraph`. That cannot cross a network, so
`retrieval/app/clients.py` fetches the entire graph and rebuilds it locally per process.
It works and it is honest about the cost — but the engine only ever needs the 1-hop
neighbourhood of three matched nodes. The graph service already exposes `/neighborhood`;
switching the engine to it is a Phase 5 task, after which retrieval drops `networkx`
entirely.

**2. The vault hands out `Path` objects it expects the caller to open.** Fine in-process,
meaningless across a service boundary. `read_note()` was added to the vault client; call
sites doing `note_path.read_text()` must move to it during the rewrite.

**3. The graph service needs the vector service for one reason only.** Entity resolution.
That single edge is what forces the two heaviest services to be co-deployed, and it is
exactly what Phase 1 of the plan removes. **Update:** the resolution *logic* no longer uses
it — `MathGraphIndexer._resolve_entity` is now a deterministic lookup
(`graph/app/authority.py`) that needs no vector store. `services/graph/main.py` still wires
a `VectorStoreClient()` into the indexer by default, though, because `_get_candidate_context`
(Pass-2 LLM prompt context) and the old `dedupe_graph()` still read it — actually dropping
that wiring, and the container-level dependency it implies, is Phase 6, not done yet.

---

## Known carry-overs

These defects came across with the code and are deliberately **not** fixed here — they are
scheduled in [../plan.md](../plan.md):

- Duplicate concept nodes under different spellings (14 groups) — **fixed**, both for new
  writes (`graph/app/authority.py`'s deterministic resolver, Phase 1) and for the existing
  graph (`graph-migrate-identity`, Phase 2: 119 → 75 nodes, 0 duplicate groups now).
- `vector /index` is append-only: re-indexing a note duplicates its chunks.
- `graph /dedupe` exists only to repair identity that was never assigned; scheduled for
  deletion, not reimplementation.
- `ingestion/app/handwriting/{segmenter,ocr_engine}.py` are unreferenced by the live path
  (~276 lines) — carried over rather than dropped, so nothing is lost by accident. Safe to
  delete once confirmed.
