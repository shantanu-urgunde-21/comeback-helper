# Flow

What each stage takes in and hands on. For call chains see [structure.md](structure.md).

The **vault is the source of truth**. Everything downstream — graph, vector index,
`graph.json` — is derived and rebuildable. The notes are not: re-OCR costs money and
re-rolls transcription.

```
PDF ──OCR──▶ vault/<course>/<note>.md ─┬──▶ 2-pass extraction ──▶ SQLite ──▶ graph.json
                                       └──▶ chunking ──▶ FastEmbed ──▶ LanceDB
                                                     │
                            query ──────────────────▶ hybrid retrieval ──▶ answer
```

## 1. Ingestion — PDF to Markdown

**In:** a PDF path + course name. **Out:** one `.md` file in the vault. Nothing else moves.

Provider is chosen in `IngestionPipeline.__init__`; all subclass `BaseOCRProvider`:

| Provider | Engine | Notes |
|---|---|---|
| `gemini_ocr` | Gemini Vision | batches 3 pages/request, paced |
| `handwriting_provider` | Ollama Qwen2.5-VL | fully local; OpenCV preprocessing |
| `marker_provider` | Marker | typeset PDFs |
| `local_ocr` | pix2tex | optional dependency |

Output passes through `sanitizer.py` (LaTeX normalisation) before being written.

## 2. Chunking and embedding

`chunk_math_markdown()` splits on headings while keeping `$$…$$` blocks intact — splitting
inside display math produces fragments that embed meaninglessly.

```python
{"id": "MA301 Lecture 4_7", "text": "...", "course": "differential equations",
 "source": "MA301 Lecture 4.md"}
```

`LocalVectorStore.add_chunks()` embeds with FastEmbed and writes to LanceDB, **deleting
existing rows for the same `source` first** so re-indexing is idempotent. A BM25 FTS index
is refreshed after each insert; search is hybrid (vector + BM25).

## 3. Extraction — two LLM passes

**Pass 1, per markdown section** (`chunk_id = "{doc_path}#s{n:04d}"`):

```python
GraphNode(id, name, entity_type, taxonomy{domain,subdomain,topic},
          aliases[], description, provenance[])
```

Each `name` is resolved to a canonical id before anything is stored — `_resolve_entity` →
`authority.resolve_concept()` walks document → course → Wikidata (cached) → mint
`CUST_<hash>`. The id is opaque; the readable name lives in `label`. Resolved ids accumulate
into `doc_concept_map` across the whole document.

**Pass 2, once on the full text**, receives that id-map and emits edges already keyed by
canonical id:

```python
GraphEdge(source, target, relation, description)   # description = evidence quote
```

`_normalize_relation` rewrites `PREREQUISITE_FOR(A,B)` to `DEPENDS_ON(B,A)` before storage.

Both passes degrade Gemini → Ollama → `_block_extraction` (deterministic, wikilinks and
headings only).

## 4. Persistence

`.storage/concepts.db` is the store of record:

| Table | Columns | Holds |
|---|---|---|
| `concepts` | `id, label, msc_code, authority, authority_ver, status, node_attrs_json` | identity + the node's graph attrs as JSON |
| `aliases` | `surface_norm, concept_id, scope, scope_ref` | every surface form seen, scoped |
| `mentions` | `chunk_id, surface_text, concept_id, char_span` | chunk-level provenance |
| `edges` | `source_id, target_id, relation, chunk_id, quote, origin` | graph structure + evidence |
| `msc_taxonomy` | `code, text, description` | MSC2020, 6,603 rows |
| `wikidata_lookup_cache` | `query_label, qid, label, description, …` | one network call per key, ever |
| `review_queue` | … | unresolved surface forms awaiting a human |

A concepts row becomes a **graph node** only once `node_attrs_json` is set — that column is
what separates "known identity" from "in the graph".

`graph.json` is an **export**, written by `save_graph()` for the two consumers that read the
file directly (`/api/graph`, `graph_health.py`). It is never read back in;
`graph_store.load_graph()` queries SQLite. Note the export renames `entity_type` to `type`.

## 5. Retrieval

```
query
 ├─ vector_store.search_similar(hybrid)      top-k chunks
 └─ _find_similar_nodes(query)               embedding match over label+description
      └─ indexer.neighborhood(seeds, hops=1) bounded subgraph, nodes + edges
                    ↓
   context string ──▶ Gemini (candidate fallback) ──▶ Ollama ──▶ raw context
```

Seeds come from embedding node labels, not from chunk metadata — a chunk's `source` is a
note filename and never matches an opaque node id.

If both LLMs are unavailable the retrieved context is returned verbatim with a note, rather
than failing.

## What writes what

| Action | Vault | SQLite | LanceDB | graph.json |
|---|:--:|:--:|:--:|:--:|
| `cli ingest` | ✅ | — | — | — |
| `cli rebuild-graph` | — | ✅ | — | ✅ |
| `POST /api/rebuild/vectors` | — | — | ✅ | — |
| `cli query` | — | — | — | — |
| `cli graph-preview` | — | — | — | — |
