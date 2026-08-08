# API Reference

Base URL: `http://127.0.0.1:8000`

Full interactive Swagger documentation available at **`/docs`**.

---

## Ingestion API

### `POST /api/ingest`

Upload a PDF, run OCR (batched in 3-page chunks with 4s pacing delay), save a Markdown note to the vault, and optionally update the knowledge graph and vector index.

**Request** (multipart/form-data):

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `file` | File | *required* | PDF file to ingest |
| `course` | string | *required* | Target course folder name (e.g. `"Differential Equations"`) |
| `ocr_mode` | string | `local_handwriting` | `local_handwriting` (Qwen2.5-VL 3B) or `gemini_vision` |
| `dpi` | int | `200` | PDF render resolution (100–400 DPI) |
| `auto_index` | bool | `true` | Whether to trigger graph indexing & vector embedding |

**Response:**

```json
{
    "status": "success",
    "filename": "lecture_04.pdf",
    "course": "Differential Equations",
    "ocr_mode": "local_handwriting",
    "note_path": ".storage/vault/Differential Equations/lecture_04.md",
    "content": "# Lecture 04\n...",
    "graph_indexed": true,
    "vector_chunks": 12
}
```

---

## RAG Query API

### `POST /api/query`

Ask a mathematical question using the hybrid RAG engine (vector similarity + graph node matching + candidate model fallback synthesis).

**Request** (application/json):

```json
{
    "prompt": "Explain the Mixed Partials Theorem and its prerequisites",
    "top_k": 5,
    "temperature": 0.3,
    "course": "Differential Equations",
    "use_graph": true
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `prompt` | string | *required* | The mathematical query |
| `top_k` | int | `5` | Number of vector chunks to retrieve (1–20) |
| `temperature` | float | `0.3` | Synthesis temperature (0.0–1.0) |
| `course` | string | `null` | Filter search to specific course, or `null` for all courses |
| `use_graph` | bool | `true` | Include Knowledge Graph context and relationships |

**Response:**

```json
{
    "status": "success",
    "answer": "The Mixed Partials Theorem states that..."
}
```

---

## Vault & Knowledge Graph API

### `GET /api/vault`

List all course folders and notes in the Obsidian Vault.

```json
{
    "vault": {
        "Differential Equations": [
            {"title": "Lecture notes 7 to 9.md", "path": "...", "size": 12345}
        ]
    }
}
```

### `GET /api/graph`

Get the property graph nodes and edges as JSON (for Vis.js network visualization).

```json
{
    "nodes": [
        {
            "id": "Exact Differential Equation",
            "label": "Exact Differential Equation",
            "type": "Definition",
            "taxonomy": {
                "domain": "Differential Equations",
                "subdomain": "Course Notes",
                "topic": "Exact Differential Equation"
            },
            "description": "A first-order ODE of the form M(x,y)dx + N(x,y)dy = 0..."
        }
    ],
    "edges": [
        {
            "from": "Exact Differential Equation",
            "to": "Total Differential",
            "relation": "DEPENDS_ON",
            "label": "DEPENDS_ON"
        }
    ]
}
```

### `GET /api/courses`

Returns a list of available course names present in the vault.

---

## Index Maintenance & Health

### `POST /api/rebuild/graph`

Re-indexes all vault notes into the Knowledge Graph using the decoupled 2-pass extraction pipeline.

### `POST /api/rebuild/vectors`

Re-chunks and re-embeds all vault notes into the LanceDB vector store.

### `POST /api/clear`

Clears the Knowledge Graph index, LanceDB vector store, and vault state hashes.

### `GET /api/health/ollama`

Returns live telemetry for local Ollama service and available models.
