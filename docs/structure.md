# Structure

Module reference and call chains. For data shapes see [flow.md](flow.md); for the roadmap
see [plan.md](../plan.md).

No line numbers here on purpose — they go stale faster than anything else in a doc.

## Layout

```
src/                    entry points only
  server.py             FastAPI app, 11 routes, lifespan builds the singletons
  cli.py                click group, 8 verbs, all --json
  wiring.py             composition root — builds the real classes, one process
  __init__.py           puts services/ on sys.path (load-bearing, see CLAUDE.md)

services/
  shared/               config, logger, LLM clients — used by every package
  vault/app/manager.py  reads notes, SHA-256 ingest state
  ingestion/app/        PDF → Markdown (OCR providers + LaTeX sanitizer)
  vector/app/           chunker (math-aware) + LanceDB store
  graph/app/            schema, authority (identity), graph_store (SQLite), indexer
  retrieval/app/engine  hybrid context + answer synthesis
```

Packages import each other under short names (`graph.app.indexer`), never
`services.graph.app.indexer`.

## The four largest modules

| Module | Lines | Owns |
|---|---:|---|
| `graph/app/indexer.py` | 762 | 2-pass extraction, `index_note`, `neighborhood`, block-parser fallback |
| `src/server.py` | 440 | HTTP surface + lifespan singletons |
| `graph/app/authority.py` | 438 | identity ladder, Wikidata cache, MSC2020 table |
| `src/cli.py` | 329 | the `--json` verb surface the skill consumes |

## Call chains

**Ingest a PDF**
```
POST /api/ingest ─ or ─ cli ingest
  → IngestionPipeline.process_pdf
      → <provider>.extract          gemini_ocr | handwriting | marker | local_ocr
      → sanitizer.normalize         LaTeX cleanup
      → writes vault/<course>/<note>.md
```
Writes the note only. The graph and vector index are not touched — run `rebuild-graph
--no-force` afterwards to index just the new note.

**Index a note into the graph**
```
cli rebuild-graph → build_or_update_index(force)
  → index_note(note)
      → _split_chunks                       H1–H3 sections, chunk_id "{doc}#s0000"
      → per chunk: _extract_nodes_pass      Pass 1, LLM
          → _resolve_entity → authority.resolve_concept()   canonical id
          → graph_store.upsert_node_attrs + insert_mention
      → _extract_edges_pass                 Pass 2, LLM, once on full text
          → _normalize_edge_endpoint        map LLM output back to canonical ids
          → _normalize_relation             PREREQUISITE_FOR → DEPENDS_ON
          → graph_store.insert_edge
  → save_graph()                            exports graph.json
```

**Answer a query**
```
POST /api/query ─ or ─ cli query
  → MathQueryEngine.query
      → retrieve_context
          → vector_store.search_similar          LanceDB hybrid
          → _find_similar_nodes                  embedding match → seed ids
          → indexer.neighborhood(seeds, hops=1)  bounded subgraph
      → Gemini (candidate fallback) → Ollama → raw context
```

**Read the graph on startup**
```
MathGraphIndexer.__init__ → graph_store.load_graph()
  → SELECT from concepts WHERE node_attrs_json IS NOT NULL
  → edges table → nx.DiGraph
```
SQLite is the store of record; `graph.json` is written *out* by `save_graph()` for
`/api/graph` and `graph_health.py`, and is never read back.

## Extraction fallbacks

Both passes degrade the same way, and every level is exercised in practice:

```
Gemini (candidate models, 429 → next)  →  Ollama (llama3.2, qwen2.5:3b, phi3:mini)  →  _block_extraction
```

`_block_extraction` is deterministic — wikilinks and headings, no LLM. It is also the
`use_llm=False` path used by tests.

## Dead code

- `ingestion/app/handwriting/segmenter.py` and `ocr_engine.py` (~276 lines) are referenced
  by nothing in the tracked tree. The only importer is a gitignored script that still uses
  the pre-`services/` import path, so it is already broken. Safe to delete.

Nothing else is unreferenced. `extract_from_text` looks orphaned but is what `graph-preview`
calls; it was also the container `/extract` handler before plan.md Phase 7 removed those.
