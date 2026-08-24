# Private Documentation

Internal design notes. Public docs live in [`../docs/`](../docs/); the canonical guide is
[`../CLAUDE.md`](../CLAUDE.md).

| Document | Covers |
|---|---|
| [ARCHITECTURE_DEEP_DIVE.md](ARCHITECTURE_DEEP_DIVE.md) | End-to-end architecture, single-process data flow, module responsibilities, singleton lifecycle |
| [HANDWRITING_VLM_PIPELINE.md](HANDWRITING_VLM_PIPELINE.md) | Multi-image OCR batching and pacing; the local Qwen2.5-VL pipeline (OpenCV thresholding, Ollama tuning) |
| [HYBRID_RAG_AND_GRAPH.md](HYBRID_RAG_AND_GRAPH.md) | Math-aware chunking (`$$…$$` protection), LanceDB + BM25, 2-pass extraction and model fallback |

## Test reports

Point-in-time diagnostic runs in [`test_reports/`](./test_reports/) — ingestion, graph,
vector store, hybrid retrieval, and overall integration. These are **dated snapshots, not
living reference**; check `graph-stats` or `graph_health.py` for current numbers.
