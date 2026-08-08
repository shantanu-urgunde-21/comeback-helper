# Comeback Helper

> **Math Knowledge Graph & Study Assistant** — Local-first RAG pipeline that turns handwritten STEM lecture notes into structured LaTeX Markdown in Obsidian, indexes mathematical entities into a NetworkX PropertyGraph, and provides hybrid RAG synthesis.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![LanceDB](https://img.shields.io/badge/LanceDB-Vector--Store-orange.svg)](https://lancedb.com)
[![NetworkX](https://img.shields.io/badge/NetworkX-Property--Graph-green.svg)](https://networkx.org)
[![License](https://img.shields.io/badge/License-Apache_2.0-lightgrey.svg)](LICENSE)

---

## Architecture

```
 ┌──────────────────┐     ┌──────────────────────────┐     ┌──────────────────────────────┐
 │  Coursework PDF  │ ──► │ Ingestion Pipeline       │ ──► │ Markdown Vault Note          │
 │  (Handwritten)   │     │ (Gemini / Qwen2.5-VL)    │     │ (LaTeX Math Preservation)    │
 └──────────────────┘     └──────────────────────────┘     └──────────────────────────────┘
                                     │                                   │
                                     ▼                                   ▼
                          ┌──────────────────────────┐     ┌──────────────────────────────┐
                          │ Math PropertyGraph       │     │ LanceDB Vector Store         │
                          │ (NetworkX PropertyGraph) │     │ (FastEmbed + BM25 FTS)       │
                          └──────────────────────────┘     └──────────────────────────────┘
                                     │                                   │
                                     └───────────────┬──────────────────┘
                                                     ▼
                                         ┌───────────────────────────┐
                                         │ Unified FastAPI Server    │
                                         │ (:8000 Async Backend)     │
                                         └───────────────────────────┘
                                                     │
                                                     ▼
                                         ┌───────────────────────────┐
                                         │ Vis.js Dashboard & Web UI │
                                         │ (KaTeX + Layout Controls) │
                                         └───────────────────────────┘
```

---

## Features

| Feature | Details |
|---------|---------|
| **Unified FastAPI Server** | Single high-performance async process (`:8000`) serving UI dashboard, vault API, graph indexer, and RAG synthesis |
| **Multi-Page OCR & Pacing** | 3-page multi-image batching per Gemini call with automatic 4s rate-limit pacing delay (no more 12-page ceiling) |
| **Handwriting OCR** | Google Gemini Vision or 100% local Qwen2.5-VL (3B) via Ollama (~2 GB VRAM) |
| **2-Pass Math PropertyGraph** | Decoupled 2-pass LLM pipeline: Pass 1 extracts concept nodes & SKOS taxonomy; Pass 2 links relationship edges |
| **Local Vector & BM25 Search** | LanceDB + FastEmbed with native BM25 hybrid search, CUDA GPU acceleration, and course-scoped filtering |
| **Math-Aware Chunking** | Splits on page markers → headings → paragraphs while preserving `$$...$$` blocks intact with overlap for theorem→proof continuity |
| **Hybrid RAG Synthesis** | Combines vector similarity + semantic graph node matching + candidate model fallback loop (`gemini-3.6-flash` $\rightarrow$ `gemini-flash-latest` $\rightarrow$ `gemini-flash-lite-latest` $\rightarrow$ `Ollama`) |
| **Interactive Graph Controls** | Vis.js UI with real-time layout solvers (`Barnes-Hut`, `Force-Atlas 2`, `Hierarchical`), node distance sliders, physics toggle, and edge label decluttering |
| **Obsidian Compatible** | Notes saved as standard Markdown with YAML frontmatter, SHA-256 state tracking, and `[[wikilinks]]` |

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-username/comeback-helper.git
cd comeback-helper
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Configure

Copy `.env.example` to `.env` and add your Gemini API key:

```ini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-flash-latest
OCR_PROVIDER=gemini
OBSIDIAN_VAULT_LOCATION=./.storage/vault
STORAGE_DIR=./.storage
```

### 3. Run

```bash
python -m src.server
```

Open **http://127.0.0.1:8000** — you're ready to go.

---

## Developer CLI Diagnostics

Comeback Helper includes a terminal-native diagnostic suite:

```bash
# View Knowledge Graph statistics & connected component health
python -m src.cli graph-stats

# Dry-run 2-pass extraction on any note without saving
python -m src.cli graph-preview --note "D:\path\to\lecture_note.md"

# Rebuild Knowledge Graph for all vault notes
python -m src.cli rebuild-graph

# Query the Math Knowledge Base directly from terminal
python -m src.cli query --prompt "What is an integrating factor?" --course "Differential Equations"
```

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ingest` | `POST` | Upload PDF, run OCR, save to vault, index into graph & vectors |
| `/api/query` | `POST` | Hybrid RAG query with configurable top-K, temperature, course filter |
| `/api/vault` | `GET` | List all courses and notes in the vault |
| `/api/graph` | `GET` | Get knowledge graph nodes & edges as JSON |
| `/api/courses` | `GET` | List available course names |
| `/api/settings` | `GET` | System config, index stats |
| `/api/rebuild/graph` | `POST` | Re-index all vault notes into the knowledge graph |
| `/api/rebuild/vectors` | `POST` | Re-embed all vault notes into the vector store |
| `/api/health/ollama` | `GET` | Local Ollama service & model health check |

Full API docs available at **http://127.0.0.1:8000/docs** (auto-generated Swagger UI).

---

## Project Structure

```
comeback_helper/
├── src/
│   ├── server.py            # FastAPI app with lifespan singletons
│   ├── config.py            # Pydantic settings (.env driven)
│   ├── logger.py            # Loguru centralized logging
│   ├── cli.py               # Click CLI (ingest, query, graph-stats, graph-preview, rebuild)
│   ├── chunker.py           # Math-aware Markdown chunking
│   ├── llm/                 # Centralized LLM clients
│   │   ├── gemini.py        # Gemini client singleton & candidate model fallbacks
│   │   └── ollama.py        # Ollama client (text + vision + health)
│   ├── ingestion/           # OCR providers & pipeline
│   │   ├── pipeline.py      # PDF → page images → batched OCR → vault
│   │   ├── gemini_ocr.py    # Gemini Vision provider (3-page batching + 4s pacing)
│   │   ├── handwriting_provider.py
│   │   └── handwriting/     # Local Qwen VLM pipeline
│   ├── graph/               # Knowledge graph
│   │   ├── schema.py        # Pydantic entity/relation models & 2-pass schemas
│   │   └── indexer.py       # Decoupled 2-pass extraction → NetworkX
│   ├── vector/
│   │   └── store.py         # LanceDB + FastEmbed store (native BM25 FTS)
│   ├── retrieval/
│   │   └── engine.py        # Hybrid RAG engine with model candidate fallbacks
│   └── vault/
│       └── manager.py       # Vault file parsing & SHA-256 state tracker
├── static/                  # Web dashboard (HTML/JS/CSS with Vis.js Graph Controls)
├── tests/                   # Unit tests
├── docs/                    # Public documentation
└── requirements.txt
```

---

## Configuration Options

All settings are read from `.env` via Pydantic:

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | *required* | Google AI Studio API key |
| `GEMINI_MODEL` | `gemini-flash-latest` | Model for OCR and RAG synthesis |
| `OCR_PROVIDER` | `gemini` | `gemini` or `handwriting` |
| `OBSIDIAN_VAULT_LOCATION` | `./.storage/vault` | Path to Obsidian vault directory |
| `STORAGE_DIR` | `./.storage` | Path for graph, vector DB, logs |
| `EMBED_MODEL` | `BAAI/bge-small-en-v1.5` | FastEmbed model for vector embeddings |

---

## License

[Apache License 2.0](LICENSE)
