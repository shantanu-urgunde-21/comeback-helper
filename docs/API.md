# API Reference

Base URL: `http://127.0.0.1:8000`. Interactive Swagger at **`/docs`**.

| | Route | Purpose |
|---|---|---|
| GET | `/` | Dashboard (HTML) |
| POST | `/api/ingest` | PDF → OCR → vault note |
| POST | `/api/query` | Hybrid RAG answer |
| GET | `/api/vault` | List courses and notes |
| GET | `/api/graph` | Full graph as JSON |
| GET | `/api/courses` | Course names present in the vault |
| GET | `/api/settings` | Effective configuration (read-only) |
| GET | `/api/health/ollama` | Local Ollama telemetry |
| POST | `/api/rebuild/graph` | Re-extract every note (LLM cost) |
| POST | `/api/rebuild/vectors` | Re-chunk and re-embed every note |
| POST | `/api/clear` | Clear graph, vectors, and ingest state |

---

## `POST /api/ingest`

Runs OCR on a PDF and writes one Markdown note into the vault.

**Request** (`multipart/form-data`):

| Field | Type | Default | Description |
|---|---|---|---|
| `file` | File | *required* | PDF to ingest |
| `course` | string | *required* | Target course folder |
| `ocr_mode` | string | `local_handwriting` | `local_handwriting` (Qwen2.5-VL) or `gemini_vision` |
| `dpi` | int | `200` | Render resolution, 100–400 |
| `auto_index` | bool | `true` | Also index into graph + vector store |

```json
{
  "status": "success",
  "note_path": ".storage/vault/Differential Equations/lecture_04.md",
  "graph_indexed": true,
  "vector_chunks": 12
}
```

## `POST /api/query`

Hybrid retrieval (vector chunks + 1-hop graph neighbourhood) followed by LLM synthesis, with
Gemini → Ollama fallback.

| Field | Type | Default | Description |
|---|---|---|---|
| `prompt` | string | *required* | The question |
| `top_k` | int | `5` | Vector chunks to retrieve, 1–20 |
| `temperature` | float | `0.3` | Synthesis temperature |
| `course` | string \| null | `null` | Restrict to one course |
| `use_graph` | bool | `true` | Include graph context |

```json
{ "status": "success", "answer": "The Mixed Partials Theorem states that..." }
```

If both Gemini and Ollama are unavailable, the retrieved context is returned verbatim with a
note appended, rather than erroring.

## `GET /api/graph`

The whole graph, shaped for vis-network. Read directly from `graph.json`, so it reflects the
last `save_graph()` rather than live in-memory state.

```json
{
  "nodes": [
    {
      "id": "Q124743",
      "label": "Wronskian",
      "type": "Concept",
      "taxonomy": {"domain": "Differential Equations", "subdomain": "Second-Order ODEs", "topic": "Wronskian"},
      "description": "A determinant used to test linear independence of solutions."
    }
  ],
  "edges": [
    {"from": "Q124743", "to": "CUST_a1b2c3d4e5f6", "relation": "DEPENDS_ON", "label": "DEPENDS_ON"}
  ]
}
```

**`id` is opaque** — a Wikidata QID or a minted `CUST_<hash>`, never readable text. Render
`label`. This changed in plan.md Phase 1; anything keying off a human-readable id is broken.

`type` carries the node's entity type (the export renames `entity_type` → `type`).

## `GET /api/vault`

```json
{"vault": {"Differential Equations": [{"title": "Lecture 7.md", "path": "...", "size": 12345}]}}
```

## Maintenance

`POST /api/rebuild/graph` re-extracts every note through the 2-pass pipeline — this spends
LLM budget. `POST /api/rebuild/vectors` re-chunks and re-embeds; it is local-only and free.
`POST /api/clear` drops graph structure, vectors, and ingest-state hashes, but **preserves
the identity tables** (`concepts`/`aliases`), so canonical ids survive a rebuild.
