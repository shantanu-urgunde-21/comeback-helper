# 🔬 System Architecture & Design Deep Dive

## Executive Overview

**Comeback Helper** is an offline-first, local-first technical study assistant and knowledge management system. It solves the fundamental limitation of standard vector-only RAG pipelines when dealing with STEM coursework: loss of explicit prerequisite/logical structure and math formula corruption.

It combines:
1. **Multi-Engine Document Ingestion:** Cloud Gemini Vision API (with 3-page multi-image batching + 4s pacing delay) or 100% Local Vision-Language Models (Qwen2.5-VL via Ollama) with custom CV pre-processing.
2. **Obsidian Vault Serialization:** Markdown persistence preserving `$inline$` and `$$block$$` LaTeX with standard YAML frontmatter and `[[wikilinks]]`.
3. **Decoupled 2-Pass Math PropertyGraph:** 2-Pass LLM extraction (`MathNodeExtraction` $\rightarrow$ `MathEdgeExtraction`) backed by NetworkX disk serialization (`.storage/graph.json`).
4. **Local Hybrid Vector & BM25 Search:** LanceDB serverless vector database paired with FastEmbed embedding models (`BAAI/bge-small-en-v1.5`) and native BM25 full-text search.
5. **Single-Process FastAPI Server (`:8000`):** Unified async server hosting REST endpoints, lifespan singletons, Vis.js graph UI, and RAG synthesis engine.
6. **Vis.js Real-Time Layout & Decluttering Suite:** Interactive runtime visual controls (Barnes-Hut, Force-Atlas 2, Hierarchical tree layout, spring length separation slider, edge label toggle, physics freeze).

---

## High-Level System Data Flow

```
                      +----------------------------------+
                      |       Coursework PDF Upload      |
                      +----------------+-----------------+
                                       |
                                       v
                      +----------------------------------+
                      |   Ingestion & OCR Subsystem      |
                      |  - Channel Thresholding (OpenCV) |
                      |  - Gemini 3-Page Batching (4s)   |
                      |  - Local Qwen2.5-VL via Ollama   |
                      +----------------+-----------------+
                                       |
                                       v
                      +----------------------------------+
                      |      Obsidian Vault Note         |
                      |   (.storage/vault/<Course>/*.md) |
                      +----------------+-----------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
+------------------------------------+  +------------------------------------+
|     2-Pass Math Graph Indexer      |  |       LanceDB Hybrid Store         |
| - Pass 1: Concept & SKOS Taxonomy  |  | - Math-aware chunking (chunker.py) |
| - Pass 2: Prerequisite & Edge Link |  | - FastEmbed embeddings + BM25 FTS  |
| - Candidate model retry fallback   |  | - Course-scoped LanceDB storage    |
| - Serialized to graph.json         |  | - Error-recovery table init        |
+------------------+-----------------+  +------------------+-----------------+
                   |                                       |
                   +-------------------+-------------------+
                                       |
                                       v
                      +----------------------------------+
                      |     Hybrid Retrieval Engine      |
                      | - Vector search + LanceDB BM25   |
                      | - Semantic graph node matching   |
                      | - Candidate LLM model loop       |
                      +----------------+-----------------+
                                       |
                                       v
                      +----------------------------------+
                      |   Unified FastAPI Server (:8000) |
                      | - Interactive Vis.js Graph UI    |
                      | - KaTeX math rendering output    |
                      +----------------------------------+
```

---

## Subsystem Breakdown

### 1. Ingestion Subsystem (`src/ingestion/`)

* **`pipeline.py` (`IngestionPipeline`):** Orchestrates PDF page rendering via PyMuPDF (`fitz`), image preprocessing, OCR execution, and real-time page-by-page streaming to the Obsidian vault. Utilizes `process_images_batch` when supported by the OCR provider.
* **`gemini_ocr.py` (`GeminiOCRProvider`):** Gemini Vision provider featuring **3-page multi-image batching** (`process_images_batch`), automatic **4-second pacing delay** between API calls to prevent 429 quota exhaustion, and candidate model fallback loops (`gemini-flash-latest` $\rightarrow$ `gemini-flash-lite-latest`).
* **`handwriting_provider.py` (`HandwritingOCRProvider`):** Integrates the 4-station local VLM pipeline for handwritten STEM notes.
* **`handwriting/preprocessor.py` (`ImagePreprocessor`):** CV pipeline using OpenCV. Splits RGB channels and extracts the Red channel to erase blue notebook ruling lines while keeping pencil/black ink handwriting sharp. Applies adaptive CLAHE contrast adjustment.
* **`handwriting/ollama_vlm.py` (`OllamaVisionOCR`):** Interacts with Ollama HTTP REST API (`http://localhost:11434/api/generate`) targeting `qwen2.5vl:3b`. Downscales images to max 1024px to enforce ~2.1 GB VRAM limit on consumer GPUs.

---

### 2. Knowledge Graph Subsystem (`src/graph/`)

* **`schema.py`:** Defines strict Pydantic models for 2-pass extraction:
  * `MathNodeExtraction` (Pass 1): Extracts formal concept entities, 1-2 sentence definitions, roles (`Theorem`, `Definition`, `Formula`, `Proof`, `Lemma`), and 3-tier SKOS taxonomy (`domain`, `subdomain`, `topic`).
  * `MathEdgeExtraction` (Pass 2): Takes Pass 1 concepts + Top-20 vector candidates and links directional relationship edges (`DEPENDS_ON`, `PROVES`, `USES_DEFINITION`, `PREREQUISITE_FOR`).
* **`indexer.py` (`MathGraphIndexer`):** Executes the 2-pass extraction pipeline. Applies strict candidate model fallback loops and noise filters (rejecting garbage sentence fragment nodes). Persists graph to `.storage/graph.json`.

---

### 3. Vector Subsystem (`src/vector/`) & Math Chunker (`src/chunker.py`)

* **`chunker.py` (`chunk_math_markdown`):** Standard character-length chunkers destroy mathematical derivations by breaking equations mid-line. Our chunker:
  1. Splits on page markers (`<!-- Page N -->`).
  2. Splits on Markdown headers (`#`, `##`, `###`).
  3. Protects display math blocks (`$$...$$`) from being split.
  4. Merges tiny fragments under `min_chunk_size` (100 chars).
  5. Appends `overlap_chars` (150 chars) of context to preserve theorem → proof logical continuity.
* **`store.py` (`LocalVectorStore`):** Connects to serverless LanceDB table at `.storage/lancedb/`. Uses `fastembed.TextEmbedding` (`BAAI/bge-small-en-v1.5`) with native BM25 full-text search (`create_index("text", config=FTS())`) and automated corruption recovery during initialization.

---

### 4. Hybrid RAG Engine (`src/retrieval/engine.py`)

* Combines vector similarity results with NetworkX semantic node matching.
* Prompts Gemini / Ollama with retrieved vault context and question templates.
* Applies candidate model loop (`gemini-3.6-flash` $\rightarrow$ `gemini-flash-latest` $\rightarrow$ `gemini-flash-lite-latest` $\rightarrow$ `Ollama`) to ensure 100% synthesis uptime without 500 errors.

---

### 5. Unified FastAPI Server & Vis.js Controls (`src/server.py`, `static/`)

* Serves UI static assets (`/static`), vault browsing (`/api/vault`), graph API (`/api/graph`), settings, and RAG synthesis (`/api/query`).
* **Vis.js Graph Customization Toolbar:** Provides runtime controls for solver algorithms (`Barnes-Hut`, `Force-Atlas 2`, `Hierarchical`), node distance sliders, edge label visibility, and physics simulation freezing.
