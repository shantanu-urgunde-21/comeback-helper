# Private Documentation

Internal design notes. Public docs live in [`../docs/`](../docs/); the canonical guide is
[`../CLAUDE.md`](../CLAUDE.md).

**Start with [ARCHITECTURE_DEEP_DIVE.md](ARCHITECTURE_DEEP_DIVE.md).** It's the front-to-back
narrative — what this system is for, why each subsystem is shaped the way it is, and where
the code lives for each piece. Read it once, whole, before touching anything. Everything else
here and in `../docs/` is reference material to come back to once you have that picture:

| Document | Covers |
|---|---|
| [ARCHITECTURE_DEEP_DIVE.md](ARCHITECTURE_DEEP_DIVE.md) | **Read first.** What this is for and why it's shaped this way (verified against real extracted data, not just the prompt's stated intent), why each major dependency was chosen, two full request-lifecycle traces (query, ingest), an honest code-practices audit, and "known open issues" |
| [HANDWRITING_VLM_PIPELINE.md](HANDWRITING_VLM_PIPELINE.md) | Deep dive on one subsystem: the local 4-station OCR pipeline (OpenCV preprocessing, Ollama vision, contextual repair), and the cloud Gemini alternative |
| [`../docs/structure.md`](../docs/structure.md) | Exact call chains, one line per function — no prose, no "why" |
| [`../docs/flow.md`](../docs/flow.md) | Exact data shapes at each pipeline stage (chunk dicts, SQLite table columns) |
| [`../docs/API.md`](../docs/API.md) | The HTTP contract |
| [`../plan.md`](../plan.md) | The roadmap and its current status, phase by phase |

## Test reports

Point-in-time diagnostic runs in [`test_reports/`](./test_reports/) — ingestion, graph,
vector store, hybrid retrieval, and overall integration. These are **dated snapshots, not
living reference**; check `graph-stats` or `graph_health.py` for current numbers.
