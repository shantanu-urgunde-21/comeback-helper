# Structure

Module reference and call chains. For data shapes see [flow.md](flow.md); for the roadmap
see [plan.md](../plan.md).

No line numbers here on purpose — they go stale faster than anything else in a doc.

## Layout

```
src/                    entry points only
  server.py             FastAPI app factory, lifespan builds the singletons, mounts routers
  routes/                one APIRouter per HTTP concern — ingest, query, vault, admin
  cli.py                click group, 8 verbs, all --json
  wiring.py             composition root — builds the real classes, one process
  __init__.py           puts services/ on sys.path (load-bearing, see CLAUDE.md)

services/
  shared/               config, logger, LLM clients (incl. shared/llm/fallback.py)
  vault/app/manager.py  reads notes, SHA-256 ingest state
  ingestion/app/        PDF → Markdown (OCR providers + LaTeX sanitizer)
  vector/app/           chunker (math-aware) + LanceDB store
  graph/app/            schema, authority (identity), graph_store (SQLite), indexer + its
                         extraction helpers (prompts, extraction_filters, block_extractor,
                         llm_extraction)
  retrieval/app/engine  hybrid context + answer synthesis
```

Packages import each other under short names (`graph.app.indexer`), never
`services.graph.app.indexer`.

## The `graph/app/` extraction split

`indexer.py` used to hold prompts, entity-name filtering, the deterministic block parser,
and both LLM passes inline (945 lines). Those are now separate modules it calls into, so
`MathGraphIndexer` itself is just orchestration (graph I/O, `index_note`,
`build_or_update_index`, `repair_dag`, `neighborhood`):

| Module | Lines | Owns |
|---|---:|---|
| `graph/app/indexer.py` | ~560 | `MathGraphIndexer`: graph I/O, `index_note`, `build_or_update_index`, `neighborhood`, `_normalize_relation` |
| `graph/app/llm_extraction.py` | ~150 | Pass 1/2 LLM calls (`extract_nodes_pass`, `extract_edges_pass`), built on `shared/llm/fallback.py` |
| `graph/app/block_extractor.py` | ~115 | Tier-3 deterministic parser (`block_extraction`) — LaTeX envs, typed headings, wikilinks |
| `graph/app/prompts.py` | ~85 | `PASS1_NODE_PROMPT`, `PASS2_EDGE_PROMPT` |
| `graph/app/authority.py` | 438 | identity ladder, Wikidata cache, MSC2020 table |
| `graph/app/extraction_filters.py` | ~35 | `is_valid_entity` — rejects structural noise as a node name |

`_split_chunks`, `_normalize_edge_endpoint`, and `_get_candidate_context` stayed on
`MathGraphIndexer` (not extracted) because `tests/test_graph_indexer.py` calls them
directly as instance methods.

`src/server.py` (69 lines) and `src/routes/{ingest,query,vault,admin}.py` (~100–135 lines
each) split the same way: one file per HTTP concern instead of 11 routes in one module.

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
      → _split_chunks                          H1–H3 sections, chunk_id "{doc}#s0000"
      → per chunk: llm_extraction.extract_nodes_pass   Pass 1, LLM
          → _resolve_entity → authority.resolve_concept()   canonical id
          → graph_store.upsert_node_attrs + insert_mention
      → llm_extraction.extract_edges_pass       Pass 2, LLM, once on full text
          → _normalize_edge_endpoint            map LLM output back to canonical ids
          → _normalize_relation                 PREREQUISITE_FOR → DEPENDS_ON
          → graph_store.insert_edge
  → save_graph()                                exports graph.json
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

Both passes degrade the same way, and every level is exercised in practice. The Gemini →
Ollama half of the ladder is one shared function, `shared/llm/fallback.with_gemini_then_ollama`
— also used by `retrieval/app/engine.py`'s answer synthesis, not just graph extraction:

```
Gemini (candidate models, any failure → next)  →  Ollama (llama3.2, qwen2.5:3b, phi3:mini)  →  block_extraction
```

`block_extractor.block_extraction` is deterministic — wikilinks and headings, no LLM. It is
also the `use_llm=False` path used by tests.

## Dead code

Nothing currently unreferenced. `extract_from_text` looks orphaned but is what `graph-preview`
calls; it was also the container `/extract` handler before plan.md Phase 7 removed those.
