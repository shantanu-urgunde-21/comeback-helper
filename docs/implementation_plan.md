# Comeback Helper: Modular Implementation Plan

This plan details the step-by-step refactoring and modularization of **Comeback Helper**. Each step is isolated, easy to test independently, and driven by centralized configuration files to prevent hardcoded parameters.

---

## 🏗️ Audit of Existing Code vs. Refactored Services

| Existing Component | Status | Required Modification / Refactoring |
| :--- | :--- | :--- |
| `src/config.py` | 🔄 Refactor | Expand into modular Pydantic settings (`Ingestion`, `Vector`, `Graph`, `Server`). Externalize all paths & parameters. |
| `src/ingestion/` | ➕ Extend | Add `MarkerOCRProvider` for fast local PDF extraction. Maintain Gemini & LightOnOCR as fallbacks. |
| `src/graph/indexer.py` | 🔄 Rewrite | Replace raw string prompt parsing with **Instructor** for 100% type-safe Pydantic graph extraction. |
| `src/vector/` | ✨ New Module | Implement `LanceDB` vector store + `FastEmbed` local CPU embedding generator. |
| `src/retrieval/engine.py` | 🔄 Refactor | Upgrade to Hybrid Search combining LanceDB vector similarity with Math PropertyGraph traversal. |
| `src/server.py` | 🔄 Refactor | Inject modularized service singletons into FastAPI endpoints. |

---

## 🎯 Step-by-Step Implementation Roadmap

```
Phase 1: Config System ──► Phase 2: Marker Ingestion ──► Phase 3: Instructor Graph
                                                                 │
Phase 5: Server Integration ◄── Phase 4: LanceDB Vector Store ◄──┘
```

---

### Phase 1: Centralized Configuration System
> **Goal:** Eliminate hardcoded parameters across all files. Drive system behavior through `.env` and `src/config.py`.

* **Step 1.1: Expand Pydantic Settings Schema**
  * Update [`src/config.py`](file:///d:/programming/comeback_helper/src/config.py) to define isolated config sections:
    * `IngestionConfig`: Default provider (`marker`, `gemini`, `local_ocr`), Marker CLI flags, output paths.
    * `VectorConfig`: LanceDB storage directory (`.storage/lancedb`), embedding model name (`BAAI/bge-small-en-v1.5`), chunk size, overlap.
    * `GraphConfig`: LLM provider (`gemini`, `ollama`), model name, temperature, Instructor retry count.
    * `ServerConfig`: Host, port, debug mode.
* **Step 1.2: Update Environment Example (`.env.example`)**
  * Populate `.env.example` with clear comments for all configurable knobs.

---

### Phase 2: Ingestion Modularization & Marker Provider
> **Goal:** Add fast, local PDF-to-Markdown processing using Marker while maintaining clean OCR fallback interfaces.

* **Step 2.1: Implement `MarkerOCRProvider`**
  * Create `src/ingestion/marker_provider.py` implementing `BaseOCRProvider`.
  * Calls `marker` CLI / Python API to extract PDF pages to Markdown + LaTeX.
* **Step 2.2: Refactor Ingestion Pipeline**
  * Update [`src/ingestion/pipeline.py`](file:///d:/programming/comeback_helper/src/ingestion/pipeline.py) to dynamically instantiate the provider specified in `config.ingestion.ocr_provider`.
  * Ensure real-time page-by-page streaming to the Obsidian vault is preserved.

---

### Phase 3: Instructor-Powered Graph Extraction
> **Goal:** Guarantee 100% type-safe math entity and relationship extraction without JSON parsing errors.

* **Step 3.1: Define Extraction Pydantic Schemas**
  * Refactor [`src/graph/schema.py`](file:///d:/programming/comeback_helper/src/graph/schema.py) to include `MathEntityExtraction` models optimized for `instructor`.
* **Step 3.2: Rebuild Graph Indexer with Instructor**
  * Rewrite [`src/graph/indexer.py`](file:///d:/programming/comeback_helper/src/graph/indexer.py) using `instructor.from_gemini()` or `instructor.from_provider()`.
  * Indexer processes vault Markdown files in isolated chunks and updates the NetworkX graph in `.storage/graph.json`.

---

### Phase 4: Local Vector Store & Hybrid Retrieval Engine
> **Goal:** Add local vector search (LanceDB + FastEmbed) and combine it with Graph traversal.

* **Step 4.1: Create Vector Store Service (`src/vector/store.py`)**
  * Create new module `src/vector/store.py` initializing `lancedb` table and `fastembed` TextEmbedding generator.
  * Implement `add_documents(chunks)` and `search_similar(query, top_k)`.
* **Step 4.2: Build Hybrid Retrieval Engine**
  * Refactor [`src/retrieval/engine.py`](file:///d:/programming/comeback_helper/src/retrieval/engine.py):
    1. Query LanceDB for top semantic text chunks.
    2. Query NetworkX Math PropertyGraph for related concepts/prerequisites.
    3. Merge context into unified prompt for LLM answer synthesis.

---

### Phase 5: FastAPI Server Integration & End-to-End Testing
> **Goal:** Connect all modular services cleanly in `src/server.py` and verify performance.

* **Step 5.1: Clean Service Injection in `src/server.py`**
  * Instantiate `IngestionPipeline`, `GraphIndexer`, `VectorStore`, and `RetrievalEngine` cleanly at app startup.
  * Connect `/api/ingest`, `/api/graph`, `/api/query`, and `/api/stats` to their respective isolated service calls.
* **Step 5.2: End-to-End Verification**
  * Test ingesting a sample math PDF.
  * Verify Markdown output in Obsidian Vault.
  * Verify visual graph rendering in Vis.js frontend and math equation formatting in KaTeX.

---

## 🎯 Verification Criteria & Isolation Strategy

Each phase can be tested independently:
- **Phase 1 Test:** Run `python -c "from src.config import get_settings; print(get_settings())"`.
- **Phase 2 Test:** Run `python -m tests.test_marker_ingestion` on a sample 2-page PDF.
- **Phase 3 Test:** Run `python -m tests.test_instructor_indexer` on a sample Markdown note.
- **Phase 4 Test:** Run `python -m tests.test_vector_store` to insert and query chunks in LanceDB.
- **Phase 5 Test:** Start `python -m src.server` and test the Web Dashboard UI.
