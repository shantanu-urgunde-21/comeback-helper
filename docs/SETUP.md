# Setup Guide & Developer Operations

## Prerequisites

- **Python 3.10+** (Python 3.11/3.12 supported)
- **NVIDIA GPU** (Optional, recommended) — CUDA toolkit for GPU-accelerated FastEmbed embeddings
- **Ollama** (Optional) — Needed for 100% local offline handwriting OCR via Qwen2.5-VL (`qwen2.5vl:3b`)

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
GEMINI_MODEL=gemini-flash-latest
OCR_PROVIDER=gemini
OBSIDIAN_VAULT_LOCATION=./.storage/vault
STORAGE_DIR=./.storage
EMBED_MODEL=BAAI/bge-small-en-v1.5
```

### 5. (Optional) Install Ollama for 100% local handwriting OCR

If you want 100% offline handwriting recognition:

```bash
# Install Ollama from https://ollama.com
ollama pull qwen2.5vl:3b
```

This requires ~2 GB VRAM. The system automatically detects Ollama availability.

---

## Running the Application

### 1. Unified Web Server

Launch the single-process FastAPI server:

```bash
python -m src.server
```

Open **http://127.0.0.1:8000** in your browser to access the dashboard, Vis.js graph controls, and math query assistant.

### 2. Developer Terminal Diagnostic Suite

Comeback Helper includes a terminal-native CLI diagnostic suite:

```bash
# View Knowledge Graph statistics & connected component health
python -m src.cli graph-stats

# Dry-run 2-pass extraction on any note without saving
python -m src.cli graph-preview --note "D:\path\to\lecture_note.md"

# Rebuild Knowledge Graph for all vault notes
python -m src.cli rebuild-graph

# Run CLI query
python -m src.cli query --prompt "What is an integrating factor?" --course "Differential Equations"
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ | — | API key from [Google AI Studio](https://aistudio.google.com/) |
| `GEMINI_MODEL` | ❌ | `gemini-flash-latest` | Gemini model for OCR, graph extraction, and RAG synthesis |
| `OCR_PROVIDER` | ❌ | `gemini` | Ingestion engine: `gemini` (cloud API) or `handwriting` (local Qwen2.5-VL) |
| `OBSIDIAN_VAULT_LOCATION` | ✅ | `./.storage/vault` | Path to Obsidian vault directory |
| `STORAGE_DIR` | ❌ | `./.storage` | Path for NetworkX graph, LanceDB vector store, app logs |
| `EMBED_MODEL` | ❌ | `BAAI/bge-small-en-v1.5` | FastEmbed model for vector embeddings |

---

## Testing & Verification

Run tests (`unittest`, not pytest — pytest is not a dependency of this project):

```bash
python -m unittest discover -s tests -v

# One module
python -m unittest tests.test_graph_indexer -v
```
