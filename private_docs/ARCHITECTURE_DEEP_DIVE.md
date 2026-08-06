# 🔬 System Architecture & Design Deep Dive

## Executive Overview

**Comeback Helper** is an offline-first, local-first technical study assistant and knowledge management system. It solves the fundamental limitation of standard vector-only RAG pipelines when dealing with STEM coursework: loss of explicit prerequisite/logical structure and math formula corruption.

It combines:
1. **Multi-Engine Document Ingestion:** Cloud Gemini Vision API or 100% Local Vision-Language Models (Qwen2.5-VL via Ollama) with custom CV pre-processing.
2. **Obsidian Vault Serialization:** Markdown persistence preserving `$inline$` and `$$block$$` LaTeX with standard YAML frontmatter and `[[wikilinks]]`.
3. **Structured Math PropertyGraph:** Instructor + Pydantic schema extraction backed by NetworkX disk serialization (`.storage/graph.json`).
4. **Local Vector Search:** LanceDB serverless vector database paired with FastEmbed embedding models (`BAAI/bge-small-en-v1.5`).
5. **Math-Aware Chunking & Hybrid Retrieval Engine:** Custom chunking algorithm respecting LaTeX display math blocks, combined with semantic graph node matching and Gemini synthesis.

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
                      |  - Vision LLM (Gemini / Qwen)   |
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
|       Math Graph Indexer           |  |       LanceDB Vector Store         |
| - Math-aware entity extraction     |  | - Math-aware chunking (chunker.py) |
| - Typed nodes: Theorem, Def, etc.  |  | - BAAI/bge-m3 embeddings           |
| - Edges: DEPENDS_ON, PROVES        |  | - Course-scoped LanceDB storage    |
| - Serialized to graph.json         |  | - CUDA / CPU ONNX Execution        |
+------------------+-----------------+  +------------------+-----------------+
                   |                                       |
                   +-------------------+-------------------+
                                       |
                                       v
                      +----------------------------------+
                      |     Hybrid Retrieval Engine      |
                      | - Top-K vector similarity search |
                      | - Semantic graph node matching   |
                      | - Predecessor & Successor traversal|
                      +----------------+-----------------+
                                       |
                                       v
                      +----------------------------------+
                      |       Gemini 2.0 Flash Synthesis |
                      | - Strictly scoped math tutor     |
                      | - KaTeX math rendering output    |
                      +----------------------------------+
```

---

## Subsystem Breakdown

### 1. Ingestion Subsystem (`src/ingestion/`)

* **`pipeline.py` (`IngestionPipeline`):** Orchestrates PDF page extraction via PyMuPDF (`fitz`), image preprocessing, OCR execution, and real-time page-by-page streaming to the Obsidian vault.
* **`gemini_ocr.py` (`GeminiOCRProvider`):** Direct API integration with `google-genai` SDK using `gemini-2.0-flash`. Features automatic backoff retries on rate limits (HTTP 429).
* **`handwriting_provider.py` (`HandwritingOCRProvider`):** Integrates the 4-station local VLM pipeline for handwritten STEM notes.
* **`handwriting/preprocessor.py` (`ImagePreprocessor`):** CV pipeline using OpenCV. Splits RGB channels and extracts the Red channel to erase blue notebook ruling lines while keeping pencil/black ink handwriting sharp. Applies adaptive CLAHE contrast adjustment.
* **`handwriting/ollama_vlm.py` (`OllamaVisionOCR`):** Interacts with Ollama HTTP REST API (`http://localhost:11434/api/generate`) targeting `qwen2.5vl:3b`. Downscales images to max 1024px to enforce ~2.1 GB VRAM limit on consumer GPUs.

---

### 2. Knowledge Graph Subsystem (`src/graph/`)

* **`schema.py`:** Defines strict Pydantic models for zero-error LLM structured extraction:
  * `MathEntityType`: `Theorem`, `Definition`, `Concept`, `Proof`, `Formula`, `Lemma`, `Example`, `Course`.
  * `MathRelationType`: `DEPENDS_ON`, `PROVES`, `USES_DEFINITION`, `DERIVED_FROM`, `APPLIES_TO`, `SPECIAL_CASE_OF`.
  * `GraphNode`: `id`, `label`, `entity_type`, `description`, `course`.
  * `GraphEdge`: `source_id`, `target_id`, `relation`, `weight`.
* **`indexer.py` (`MathGraphIndexer`):** Reads vault Markdown notes, sends them to Gemini with structured system prompts, parses responses into `MathEntityExtraction`, and updates an in-memory NetworkX `DiGraph`. Persists to disk at `.storage/graph.json`.

---

### 3. Vector Subsystem (`src/vector/`) & Math Chunker (`src/chunker.py`)

* **`chunker.py` (`chunk_math_markdown`):** Standard character-length chunkers destroy mathematical derivations by breaking equations mid-line. Our chunker:
  1. Splits on page markers (`<!-- Page N -->`).
  2. Splits on Markdown headers (`#`, `##`, `###`).
  3. Protects display math blocks (`$$...$$`) from being split.
  4. Merges tiny fragments under `min_chunk_size` (100 chars).
  5. Appends `overlap_chars` (150 chars) of context to preserve theorem → proof logical continuity.
* **`store.py` (`LocalVectorStore`):** Connects to serverless LanceDB table at `.storage/lancedb/`. Uses `fastembed.TextEmbedding` (`BAAI/bge-m3` by default) with CUDA GPU execution fallback to CPU. Provides `search_similar()` with course filtering and score thresholding.

---

### 4. Hybrid Retrieval Engine (`src/retrieval/engine.py`)

* **`MathQueryEngine`:**
  1. **Vector Retrieval:** Queries LanceDB for top-$K$ semantic chunks matching prompt and course filter.
  2. **Semantic Graph Traversal:** Instead of naive string matching, pre-embeds graph node labels/descriptions using `embed_texts()`. Computes cosine similarity between query embedding and all graph nodes. Traverses both outgoing (successors) and incoming (predecessors) edges for matched nodes.
  3. **Context Assembly & Prompt Synthesis:** Formats retrieved vector chunks and graph triplets into `MATH_QUERY_PROMPT_TEMPLATE` and calls Gemini API.

---

### 5. Application Server (`src/server.py`)

* **Lifespan Manager:** Instantiates `MathQueryEngine`, `MathGraphIndexer`, and `LocalVectorStore` singletons once at FastAPI application startup, preventing heavy model re-allocation on every HTTP request.
* **REST Endpoints:**
  * `POST /api/ingest`: PDF upload, OCR execution, auto-indexing.
  * `POST /api/query`: Tunable hybrid query execution.
  * `GET /api/vault`, `/api/graph`, `/api/courses`, `/api/settings`.
  * `POST /api/rebuild/graph`, `/api/rebuild/vectors`.
