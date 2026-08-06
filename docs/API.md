# API Reference

Base URL: `http://127.0.0.1:8000`

Full interactive Swagger docs available at `/docs`.

---

## Ingestion

### `POST /api/ingest`

Upload a PDF, run OCR, save a Markdown note to the vault, and optionally update the knowledge graph and vector index.

**Request** (multipart form):

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `file` | File | *required* | PDF file |
| `course` | string | *required* | Course folder name (e.g. `"Linear Algebra"`) |
| `ocr_mode` | string | `local_handwriting` | `local_handwriting` or `gemini_vision` |
| `dpi` | int | `200` | PDF render resolution (100–400) |
| `auto_index` | bool | `true` | Whether to update graph & vector index |

**Response:**

```json
{
    "status": "success",
    "filename": "lecture_04.pdf",
    "course": "Linear Algebra",
    "ocr_mode": "local_handwriting",
    "note_path": ".storage/vault/Linear Algebra/lecture_04.md",
    "content": "# Lecture 04\n...",
    "graph_indexed": true,
    "vector_chunks": 12
}
```

---

## Query

### `POST /api/query`

Ask a question using the hybrid RAG engine (vector search + graph traversal + Gemini synthesis).

**Request** (JSON):

```json
{
    "prompt": "Explain the Spectral Theorem and its prerequisites",
    "top_k": 5,
    "temperature": 0.3,
    "course": "Linear Algebra",
    "use_graph": true
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `prompt` | string | *required* | The question to ask |
| `top_k` | int | `5` | Number of vector chunks to retrieve (1–20) |
| `temperature` | float | `0.3` | Gemini generation temperature (0.0–1.0) |
| `course` | string | `null` | Scope to a specific course, or `null` for all |
| `use_graph` | bool | `true` | Include knowledge graph context |

**Response:**

```json
{
    "status": "success",
    "answer": "The Spectral Theorem states that..."
}
```

---

## Vault & Graph

### `GET /api/vault`

List all course folders and notes in the Obsidian vault.

```json
{
    "vault": {
        "Linear Algebra": [
            {"title": "Lecture 04", "path": "...", "size": 12345}
        ]
    }
}
```

### `GET /api/graph`

Get the knowledge graph as nodes and edges JSON (for Vis.js rendering).

```json
{
    "nodes": [
        {"id": "Spectral Theorem", "label": "Spectral Theorem", "type": "Theorem", "group": "Linear Algebra"}
    ],
    "edges": [
        {"from": "Spectral Theorem", "to": "Symmetric Matrix", "label": "DEPENDS_ON"}
    ]
}
```

### `GET /api/courses`

List available course names.

```json
{"courses": ["Linear Algebra", "Real Analysis"]}
```

---

## System Management

### `GET /api/settings`

Returns current configuration and index statistics.

```json
{
    "gemini_model": "gemini-2.0-flash",
    "embed_model": "BAAI/bge-m3",
    "vector_store": {"total_chunks": 156, "courses": ["Linear Algebra"]},
    "graph": {"total_nodes": 23, "total_edges": 31}
}
```

### `POST /api/rebuild/graph`

Re-indexes all vault notes into the knowledge graph. Returns node/edge counts.

### `POST /api/rebuild/vectors`

Re-embeds all vault notes into the vector store. Returns total chunk count.

### `GET /api/health/ollama`

Health check for local Ollama service and Qwen2.5-VL model availability.

```json
{
    "service_online": true,
    "model_available": true,
    "target_model": "qwen2.5vl:3b"
}
```
