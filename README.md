# 🧠 Comeback Helper

> **Local RAG & Knowledge Graph Engine for Mathematics & Technical Coursework**

**Comeback Helper** is an advanced learning assistant designed for math and technical subjects. It ingests lecture notes and PDFs (including handwritten notes), parses mathematical LaTeX formulas, constructs a structured **Math PropertyGraph**, indices vector embeddings locally, and provides **Hybrid RAG Retrieval** paired with an interactive **Vis.js Knowledge Graph Dashboard**.

---

## 🏗️ Architecture Overview

```
 ┌─────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────────┐
 │  Coursework PDF │ ───► │ Ingestion Pipeline      │ ───► │ Markdown Vault Note         │
 │  (Handwritten)  │      │ (Gemini / Marker / VLM) │      │ (LaTeX Math Preservation)   │
 └─────────────────┘      └─────────────────────────┘      └─────────────────────────────┘
                                       │                                  │
                                       ▼                                  ▼
                          ┌─────────────────────────┐      ┌─────────────────────────────┐
                          │ Math PropertyGraph      │      │ LanceDB Vector Store        │
                          │ (Instructor + NetworkX) │      │ (FastEmbed BAAI/bge-small)  │
                          └─────────────────────────┘      └─────────────────────────────┘
                                       │                                  │
                                       └────────────────┬─────────────────┘
                                                        ▼
                                           ┌───────────────────────────┐
                                           │ Hybrid Retrieval Engine   │
                                           │ (Vector + Graph Context)  │
                                           └───────────────────────────┘
                                                        │
                                                        ▼
                                           ┌───────────────────────────┐
                                           │ FastAPI Dashboard & Web UI│
                                           │ (Vis.js Graph + KaTeX)    │
                                           └───────────────────────────┘
```

---

## 🌟 Key Features

* **✍️ Handwritten & Vision OCR Ingestion:** Uses **Google Gemini 2.0/2.5 Flash VLM** or local **LightOnOCR-2-1B** to translate handwritten equations, matrices, and diagrams into clean LaTeX Markdown.
* **🕸️ Math PropertyGraph Indexer:** Uses **Instructor** and **Pydantic** schemas (`MathEntityExtraction`, `GraphNode`, `GraphEdge`) to extract concept prerequisites (`Spectral Theorem --[DEPENDS_ON]--> Symmetric Matrix`) persisted to NetworkX JSON (`.storage/graph.json`).
* **⚡ High-Speed Local Vector Search:** Uses embedded **LanceDB** and **FastEmbed** (`BAAI/bge-small-en-v1.5`) for local, zero-API vector retrieval.
* **🎮 CUDA GPU Acceleration & RAM Management:** Runs ONNX embeddings on NVIDIA GPUs (`CUDAExecutionProvider`). Includes `unload_model()` and `torch.cuda.empty_cache()` memory release hooks to prevent RAM spikes (< 4 GB RAM footprint).
* **🪵 Centralized Loguru Logging:** Formatted, colorized terminal logs and rotating file logs stored at `.storage/logs/app.log`.
* **🌐 Web Dashboard & Vis.js Visualizer:** Embedded FastAPI web server serving an interactive node graph visualizer and KaTeX math viewer.

---

## 🚀 Quick Start Guide

### 1. Environment Setup

Clone the repository and install dependencies:

```bash
# Install Python dependencies
pip install -r requirements.txt
```

Create a `.env` file from `.env.example`:

```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
OCR_PROVIDER=gemini  # Options: gemini, marker, local
STORAGE_PATH=./.storage
OBSIDIAN_VAULT_LOCATION=./.storage/vault
```

### 2. Start the FastAPI Web Dashboard

Run the server:

```bash
python -m src.server
```

Open your browser and navigate to:
* **Web Dashboard:** `http://127.0.0.1:8000`
* **API Documentation:** `http://127.0.0.1:8000/docs`

---

## 🔌 API Endpoints Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/ingest` | `POST` | Uploads a PDF file, parses OCR, generates Vault note, updates Math Graph & Vector index. |
| `/api/vault` | `GET` | Returns list of ingested courses and notes. |
| `/api/graph` | `GET` | Serves `.storage/graph.json` node & edge data for the Vis.js interactive graph UI. |
| `/api/query` | `POST` | Executes Hybrid RAG search (Vector similarity + Graph context assembly). |
| `/health` | `GET` | Returns system health and OCR provider status. |

---

## 🧪 Diagnostic Test Suite

Run unit tests and component diagnostic suites:

```bash
# Run all unit tests
python -m unittest discover -s tests

# Run Master Integration Check
python scripts/test_full_system_integration.py
```

Process reports are generated in `docs/test_reports/`:
* [`docs/test_reports/overall_system_integration_report.md`](file:///d:/programming/comeback_helper/docs/test_reports/overall_system_integration_report.md)
* [`docs/test_reports/process_1_ingestion_report.md`](file:///d:/programming/comeback_helper/docs/test_reports/process_1_ingestion_report.md)
* [`docs/test_reports/process_2_graph_report.md`](file:///d:/programming/comeback_helper/docs/test_reports/process_2_graph_report.md)
* [`docs/test_reports/process_3_vector_store_report.md`](file:///d:/programming/comeback_helper/docs/test_reports/process_3_vector_store_report.md)
* [`docs/test_reports/process_4_hybrid_retrieval_report.md`](file:///d:/programming/comeback_helper/docs/test_reports/process_4_hybrid_retrieval_report.md)

---

## 📜 License
MIT License - see [`LICENSE`](file:///d:/programming/comeback_helper/LICENSE) for details.
