# Comeback Helper - Changelog

All notable changes, refactorings, and architectural improvements to **Comeback Helper** are documented in this file.

---

## [2.1.0] - 2026-08-08 (Go Microservice & KùzuDB Graph Engine)

### 🚀 Highlights
- **Go Microservice Backend (`go_backend/`)**: Built a zero-latency, concurrent vault scanning service in Go using goroutines and standard library `filepath.WalkDir`. Serves `/api/vault`, `/api/graph`, `/api/settings`, and static assets on port `8080`.
- **API Reverse Proxy**: Go server acts as high-speed static asset and vault scanner server on port `8080`, transparently reverse-proxying heavy AI endpoints (`POST /api/ingest`, `POST /api/query`, `POST /api/rebuild/`) to Python FastAPI worker on port `8000`.
- **KùzuDB Embedded Graph Store**: Integrated embedded C++ Cypher graph database (`kuzu`) dual-persisting NetworkX property graph nodes and edges into `.storage/kuzu_graph.db`.
- **Gemini Rate Limit & Quota Fix**: Updated model defaults to `gemini-flash-latest` and set `use_llm=False` for startup vault indexing, making vault startup 100% offline with 0 API calls burnt.

### 🔨 Detailed Changes

#### 1. Go Backend Microservice (`go_backend/`)
- **`vault/scanner.go`**: Concurrent SHA-256 vault file scanner utilizing goroutines for multi-core directory traversal.
- **`vault/chunker.go`**: Native math-aware Markdown section chunker preserving `$$...$$` blocks.
- **`graph/indexer.go`**: Fast local regex entity and wikilink relation extractor.
- **`server/router.go`**: `net/http` router with `httputil.SingleHostReverseProxy` forwarding heavy AI POST calls to Python.

#### 2. Graph & Vault API Schema Formatting
- **`/api/graph`**: Formatted `nodes` as a JSON array (`[ {id, label, type, description}, ... ]`) for Vis.js UI rendering.
- **`/api/vault`**: Formatted `vault` as a course-grouped JSON dictionary (`{"course_name": [...]}`).
- **`/api/health/ollama`**: Added strict `Cache-Control: no-store` headers to prevent stale browser disk caching.

---

## [2.0.0] - 2026-08-05 (Architectural Refactoring & High-Performance Optimization)

### 🚀 Highlights
* **Modular Pipeline Architecture:** Fully refactored monolithic scripts into decoupled, production-grade packages under `src/` (`config`, `ingestion`, `graph`, `vector`, `retrieval`, `vault`, `logger`).
* **Instructor Schema Indexing:** Rebuilt property graph generation with Pydantic schemas (`MathEntityExtraction`, `GraphNode`, `GraphEdge`) and NetworkX disk persistence (`.storage/graph.json`).
* **LanceDB + FastEmbed Hybrid RAG:** Built local vector search engine paired with graph prerequisite traversal.
* **RAM & GPU Optimization:** Fixed 14.6 GB RAM memory spikes by enabling CUDA ONNX GPU execution and implementing explicit model unloading (`unload_model()`, `torch.cuda.empty_cache()`, `gc.collect()`).
* **Loguru Framework:** Integrated centralized, timestamped console & rotating file logging (`.storage/logs/app.log`).

---

### 🔨 Detailed Component Changes

#### 1. Ingestion Subsystem (`src/ingestion/`)
* **Added `MarkerOCRProvider` ([`src/ingestion/marker_provider.py`](file:///d:/programming/comeback_helper/src/ingestion/marker_provider.py)):** Supports fast local PDF-to-Markdown processing with LaTeX math block preservation (`$$...$$`).
* **Upgraded `GeminiOCRProvider` ([`src/ingestion/gemini_ocr.py`](file:///d:/programming/comeback_helper/src/ingestion/gemini_ocr.py)):** Added automatic rate-limit backoff, multi-model fallbacks (`gemini-2.0-flash`, `gemini-2.5-pro`), and retry delay parsing.
* **Upgraded `LightOnOCRProvider` ([`src/ingestion/local_ocr.py`](file:///d:/programming/comeback_helper/src/ingestion/local_ocr.py)):** Added `unload_model()` hook with `torch.cuda.empty_cache()` and `gc.collect()` to purge VLM weights from VRAM/RAM after processing.
* **Modularized `IngestionPipeline` ([`src/ingestion/pipeline.py`](file:///d:/programming/comeback_helper/src/ingestion/pipeline.py)):** Implemented real-time page rendering and incremental Vault note writes.

#### 2. Math PropertyGraph Engine (`src/graph/`)
* **Pydantic Schemas ([`src/graph/schema.py`](file:///d:/programming/comeback_helper/src/graph/schema.py)):** Defined strict enums (`MathEntityType`, `MathRelationType`) and schema models for zero-error LLM output validation.
* **Instructor Indexer ([`src/graph/indexer.py`](file:///d:/programming/comeback_helper/src/graph/indexer.py)):** Extracted structured graph nodes (`Theorem`, `Definition`, `Concept`) and directed edges (`DEPENDS_ON`, `PROVES`), persisting graphs to NetworkX JSON (`.storage/graph.json`).

#### 3. Local Vector Store & Hybrid Retrieval (`src/vector/` & `src/retrieval/`)
* **LanceDB + FastEmbed Store ([`src/vector/store.py`](file:///d:/programming/comeback_helper/src/vector/store.py)):** Configured embedded LanceDB with FastEmbed (`BAAI/bge-small-en-v1.5`) embeddings and CUDA GPU execution provider (`CUDAExecutionProvider`).
* **Hybrid Retrieval Engine ([`src/retrieval/engine.py`](file:///d:/programming/comeback_helper/src/retrieval/engine.py)):** Merged top-k vector similarity chunks with 1-hop prerequisite graph context for student Q&A.

#### 4. Web Application Server & Logging (`src/server.py` & `src/logger.py`)
* **FastAPI Endpoints ([`src/server.py`](file:///d:/programming/comeback_helper/src/server.py)):** Exposed REST endpoints (`/api/ingest`, `/api/vault`, `/api/graph`, `/api/query`) serving Vis.js interactive knowledge graph JSON.
* **Central Loguru Logger ([`src/logger.py`](file:///d:/programming/comeback_helper/src/logger.py)):** Added colorized console logging and rotating file logs at `.storage/logs/app.log`.

#### 5. Testing & Diagnostics (`scripts/` & `docs/test_reports/`)
* **Modular Test Scripts:** Created `test_process1_ingestion.py`, `test_process2_graph.py`, `test_process3_vector_store.py`, `test_process4_hybrid_retrieval.py`, and `test_full_system_integration.py`.
* **Diagnostic Reports:** Generated Markdown test reports in `docs/test_reports/` detailing subsystem metrics and integration verification.

---

## [1.0.0] - Initial Prototype
* Initial single-file script implementation for PDF parsing and vector generation.
