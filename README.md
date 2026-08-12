# Comeback Helper

> **A visual atlas of mathematics.** Turns handwritten STEM lecture notes into
> structured Markdown, then indexes what they assert against a curated lattice of
> mathematical *contexts* — so you can see how results generalise, what each
> hypothesis is doing, and where one field connects to another.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![LanceDB](https://img.shields.io/badge/LanceDB-Vector--Store-orange.svg)](https://lancedb.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-lightgrey.svg)](LICENSE)

---

## The idea

Mathematics is dense with dependency, and the same word means different things in
different fields — *normal* subgroup, *normal* operator, *normal* space. A knowledge
graph of loose "concepts" linked by loose "relations" collapses exactly those
distinctions, which is what the first version of this project did.

So the atom here is not a concept. It is a **statement in a context**.

- A **context** is an ambient theory defined by the axioms it assumes. Contexts form
  a partial order by axiom inclusion — `MetricSpace` sits below `TopologicalSpace`
  because it assumes strictly more.
- A **term** is a defined name scoped to its context. Identity is the pair, so
  `normal@Group` and `normal@HilbertOperator` can never merge.
- A **statement** lives in exactly one context and carries a status: `THEOREM`,
  `DEFINITION`, or `FALSE` — and a `FALSE` requires a counterexample.

Everything structural is then **derived rather than extracted**:

| | comes from |
|---|---|
| abstraction level | position in the lattice, not an estimate |
| generalisation ladder | same slogan, contexts ordered by the lattice |
| disambiguation | terms sharing a name across contexts, by construction |

Full design, prior-art survey and the competing model that was rejected:
[`docs/ATLAS_DESIGN.md`](docs/ATLAS_DESIGN.md).

---

## Architecture

```
 ┌──────────────────┐     ┌──────────────────────────┐     ┌──────────────────────────┐
 │  Coursework PDF  │ ──► │ Ingestion                │ ──► │ Markdown Vault Note      │
 │  (handwritten)   │     │ Gemini Vision / Qwen2.5-VL│     │ (LaTeX preserved)        │
 └──────────────────┘     └──────────────────────────┘     └────────────┬─────────────┘
                                                                        │
        ┌───────────────────────────────────────────────────────────────┤
        ▼                                                               ▼
 ┌──────────────────────────┐                            ┌──────────────────────────┐
 │ Context Lattice          │                            │ LanceDB Vector Store     │
 │ transcribed from 3       │◄── statements indexed ─────│ (FastEmbed, for RAG)     │
 │ independent sources      │      against it            └──────────────────────────┘
 └────────────┬─────────────┘
              ▼
 ┌──────────────────────────┐     ┌──────────────────────────┐
 │ Atlas store              │ ──► │ FastAPI (:8000)          │
 │ terms · statements ·     │     │ + Hasse diagram renderer │
 │ witnesses                │     └──────────────────────────┘
 └──────────────────────────┘
```

---

## Features

| Feature | Details |
|---|---|
| **Context lattice** | ~54 contexts for ODE / Calculus / Linear Algebra, transcribed from Wikipedia ledes, Wikidata `P279` and an LLM, merged by vote. Graded against 42 hand-written anchors: **40/42 recovered, zero direction inversions** |
| **Two relations, not one** | `extends` (axiom strengthening) is the order and drives layout; `over` (parameterisation — a vector space *over* a field) is held out of it. Conflating them routed 39 of 54 contexts through `Field` and added six spurious levels |
| **Trust tiers** | Every relation is `SEED`, `USER`, `EXTRACTED` or `INFERRED`. Corroborated edges are solid, single-source dashed, and one toggle collapses the diagram to the verified spine |
| **Classification, not generation** | Statement extraction asks "which of these ~54 contexts?" rather than "find all relations", trading open-ended generation for a closed-set choice |
| **Self-checking** | Validation gates catch misclassification with no human labelling: a statement using a term not visible from its context is almost certainly misfiled; a `THEOREM` above a `FALSE` is a contradiction |
| **Hasse diagram renderer** | Deterministic layered layout — height *is* the order relation, so there are no physics controls to tune. Statements plot beneath the context that holds them |
| **Handwriting OCR** | Google Gemini Vision with 3-page batching, or 100% local Qwen2.5-VL via Ollama (~2 GB VRAM) with OpenCV ruling-line removal |
| **Crash-safe ingestion** | Notes build into a sidecar and are moved into place only on success, so a failed run cannot truncate an existing note |
| **Obsidian compatible** | Standard Markdown, YAML frontmatter, SHA-256 change tracking |

---

## Quick start

```bash
git clone https://github.com/your-username/comeback-helper.git
cd comeback-helper
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env            # add GEMINI_API_KEY
python -m src.server            # http://127.0.0.1:8000
```

---

## Working with the atlas

```bash
# Build the context lattice from independent sources (cached; re-runs are cheap)
python -m src.atlas.lattice.build
python -m src.atlas.lattice.build --no-llm     # Wikipedia + Wikidata only

# Inspect it as text
python -m src.atlas.lattice.show --course ode
python -m src.atlas.lattice.show --above HilbertSpace

# Render the Hasse diagram
python -m src.atlas.lattice.render                # static/lattice.html
python -m src.atlas.lattice.render --statements   # static/atlas.html

# Index vault notes into the atlas
python -m src.cli atlas-index
python -m src.cli atlas-index --note "path/to/note.md"
python -m src.cli atlas-index --rebuild

# Telemetry, gates, and a generalisation ladder
python -m src.cli atlas-stats
python -m src.cli atlas-check
python -m src.cli ladder "wronskian"

# Ask the vault a question (hybrid vector + atlas retrieval)
python -m src.cli query --prompt "What is an integrating factor?" -c "differential equations"
```

---

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/ingest` | `POST` | Upload a PDF, OCR it, save to the vault, index into the atlas |
| `/api/query` | `POST` | Hybrid RAG query with top-K, temperature and course filter |
| `/api/graph` | `GET` | The atlas: contexts, `extends`/`over` relations, statements |
| `/api/atlas/ladder?slogan=` | `GET` | One result across the lattice, ordered by depth |
| `/api/atlas/context/{id}` | `GET` | Everything known about one context |
| `/api/atlas/check` | `GET` | Validation gate findings |
| `/api/vault` | `GET` | Courses and notes in the vault |
| `/api/rebuild/graph` | `POST` | Re-extract every note into the atlas |
| `/api/rebuild/vectors` | `POST` | Re-embed every note |
| `/api/health/ollama` | `GET` | Local Ollama service and model health |

Swagger UI at **http://127.0.0.1:8000/docs**.

---

## Project structure

```
comeback_helper/
├── src/
│   ├── server.py            # FastAPI app, lifespan singletons
│   ├── cli.py               # atlas-index / atlas-stats / atlas-check / ladder / query
│   ├── config.py            # Pydantic settings (.env driven)
│   ├── chunker.py           # math-aware Markdown chunking
│   ├── atlas/
│   │   ├── schema.py        # Context · Term · Statement · Witness, trust tiers
│   │   ├── store.py         # persistence + derived ladder / disambiguation views
│   │   ├── extract.py       # note → statements, by classification
│   │   ├── validate.py      # gates
│   │   ├── index.py         # vault indexing orchestrator
│   │   └── lattice/         # lattice build · merge · show · render
│   ├── ingestion/           # OCR providers and the PDF pipeline
│   ├── llm/                 # Gemini and Ollama clients
│   ├── vector/              # LanceDB + FastEmbed
│   ├── retrieval/           # hybrid vector + atlas RAG
│   └── vault/               # Obsidian vault manager
├── static/                  # dashboard, lattice.html, atlas.html
├── docs/ATLAS_DESIGN.md     # design, prior art, the rejected alternative
└── tests/
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *required* | Google AI Studio API key |
| `GEMINI_MODEL` | `gemini-flash-latest` | Model for OCR, extraction and synthesis |
| `OCR_PROVIDER` | `gemini` | `gemini` or `handwriting` (local Qwen2.5-VL) |
| `OBSIDIAN_VAULT_LOCATION` | `./.storage/vault` | Obsidian vault directory |
| `STORAGE_DIR` | `./.storage` | Atlas, vector DB, logs |
| `EMBED_MODEL` | `BAAI/bge-small-en-v1.5` | FastEmbed embedding model |

---

## Status

Early. The lattice is solid; the material indexed against it is not yet.
Measured over 9 ODE lecture notes: **32 statements, 18 terms, 11 of 54 contexts
populated, 0 statements dropped for unknown context, 0 validation errors.**

Known gaps, in the order they matter:

1. Terms are extracted but not yet drawn — the concept layer is invisible.
2. Coverage is one course; four-fifths of the lattice is empty.
3. Extraction recall is unstable run-to-run (same note gave 7 statements, then 4).
4. Provenance lands on 2 of 32 statements.
5. No counterexamples yet, so the boundary lens has no data.

---

## License

[Apache License 2.0](LICENSE)
