# Setup Guide

## Prerequisites

- **Python 3.11+**
- **NVIDIA GPU** (optional, recommended) — CUDA toolkit for GPU-accelerated embeddings and local OCR
- **Ollama** (optional) — Only needed for 100% local handwriting OCR via Qwen2.5-VL

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/comeback-helper.git
cd comeback-helper
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy the example environment file and fill in your API key:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash
OCR_PROVIDER=gemini
OBSIDIAN_VAULT_LOCATION=./.storage/vault
STORAGE_DIR=./.storage
EMBED_MODEL=BAAI/bge-m3
```

### 5. (Optional) Install Ollama for local handwriting OCR

If you want 100% offline handwriting recognition:

```bash
# Install Ollama from https://ollama.com
ollama pull qwen2.5vl:3b
```

This requires ~2 GB VRAM. The system will auto-detect Ollama availability.

---

## Running

### Development server

```bash
python -m src.server
```

The dashboard will be available at **http://127.0.0.1:8000**.

### CLI ingestion

```bash
python -m src.cli ingest --pdf ./path/to/notes.pdf --course "Linear Algebra"
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ | — | API key from [Google AI Studio](https://aistudio.google.com/) |
| `GEMINI_MODEL` | ❌ | `gemini-2.0-flash` | Gemini model for OCR and RAG synthesis |
| `OCR_PROVIDER` | ❌ | `gemini` | OCR engine: `gemini`, `marker`, `handwriting`, `local` |
| `OBSIDIAN_VAULT_LOCATION` | ✅ | `./.storage/vault` | Path to vault directory |
| `STORAGE_DIR` | ❌ | `./.storage` | Path for graph DB, vector DB, logs |
| `EMBED_MODEL` | ❌ | `BAAI/bge-small-en-v1.5` | FastEmbed model for vector embeddings |

---

## OCR Provider Options

| Provider | Mode | Requires | Notes |
|----------|------|----------|-------|
| `gemini` | Cloud | API key | Best quality, uses Gemini Vision API |
| `handwriting` | Local | Ollama + qwen2.5vl:3b | Offline, optimized for handwritten notes on ruled paper, ~2 GB VRAM |
| `marker` | Local | marker package | Fast typed document parsing, ~3-4 GB VRAM |
| `local` | Local | pix2tex | Lightweight local OCR, experimental |

---

## Storage Layout

After running, the `.storage/` directory will contain:

```
.storage/
├── vault/                # Obsidian Markdown vault (notes organized by course)
│   ├── Linear Algebra/
│   │   └── Lecture 04.md
│   └── Real Analysis/
│       └── Chapter 3.md
├── lancedb/              # LanceDB vector database files
├── graph.json            # NetworkX knowledge graph (JSON serialized)
├── logs/
│   └── app.log           # Rotating application logs
└── temp_uploads/         # Transient (auto-cleaned after ingestion)
```

---

## Troubleshooting

### `CUDA out of memory` during ingestion

The pipeline runs OCR and embedding sequentially to avoid VRAM conflicts. If you still hit OOM:
- Lower the DPI slider in the ingestion settings (150 instead of 200)
- Use the `gemini` provider (cloud, zero local VRAM)

### `Connection refused` on Ollama health check

Ollama must be running before using the `handwriting` OCR mode:

```bash
ollama serve
```

### Vector store returns no results

If you ingested notes before the vector store was set up, use the **Rebuild Vector Index** button in the Settings tab.
