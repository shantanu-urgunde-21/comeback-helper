# Comeback Helper - Changelog

All notable changes, refactorings, and architectural improvements to **Comeback Helper** are documented in this file.

## [2.3.0] - 2026-08-08 (Decoupled 2-Pass Graph Extraction & Architecture Consolidation)

### 🚀 Highlights
- **Decoupled 2-Pass Graph Extraction Pipeline**: Refactored graph extraction in `src/graph/indexer.py` into a 2-pass LLM pipeline:
  - **Pass 1 (`MathNodeExtraction`)**: Concept & SKOS Taxonomy Extractor — identifies formal entities, roles (`Theorem`, `Definition`), descriptions, and 3-tier SKOS taxonomy.
  - **Pass 2 (`MathEdgeExtraction`)**: Relationship & Prerequisite Linker — inputs Pass 1 nodes + Top-20 vector candidates to wire directional edges (`DEPENDS_ON`, `PROVES`, `PREREQUISITE_FOR`).
- **Automatic Model Candidate Fallbacks**: Added fallback candidate loop (`gemini-3.6-flash` $\rightarrow$ `gemini-flash-latest` $\rightarrow$ `gemini-flash-lite-latest` $\rightarrow$ `Ollama`) in `src/llm/gemini.py` and `src/graph/indexer.py` to seamlessly handle API rate limits (429).
- **Single-Process FastAPI Server**: Consolidated the server architecture into a single, high-speed Python FastAPI server running on port `:8000`. Retired `go_backend`.
- **Consolidated Vault State Management**: Merged `VaultStateTracker` (SHA-256 state tracking) directly into `ObsidianVaultManager` (`src/vault/manager.py`). Purged standalone `src/vault/state.py`.
- **LanceDB Native BM25 Hybrid Search**: Enabled native FTS BM25 full-text indexing (`create_index("text", config=FTS())`) and hybrid query mode (`query_type="hybrid"`) in `src/vector/store.py`.

### 🔨 Detailed Changes

#### 1. Ingestion & Vault (`src/vault/`, `src/ingestion/`)
- **`src/vault/manager.py`**: Integrated SHA-256 file hashing, modification detection, and state JSON persistence directly into `ObsidianVaultManager`.
- **`src/vault/state.py`**: Retired standalone module.
- **`src/ingestion/handwriting/health.py`**: Consolidated health telemetry to wrap `src/llm/ollama.py`.

#### 2. Network & Storage
- **`src/graph/indexer.py`**: Purged KùzuDB C++ sync dead code (`_sync_to_kuzu()`). NetworkX `graph.json` is the sole source of truth.
- **`requirements.txt`**: Dropped `kuzu` dependency.

---

## [2.2.0] - 2026-08-08 (3-Tier Extraction Cascade, LLM Consolidation & Singleton Lifecycle)

### 🚀 Highlights
- **3-Tier Extraction Cascade**: Replaced single-pass regex fallback with a robust 3-tier fallback hierarchy (`Gemini API` $\rightarrow$ `Local Ollama LLM JSON` $\rightarrow$ `Deterministic LaTeX Block Parser`). Eliminates garbage string slicing fragments like `"From Calculus"` and `"If The Equation"`.
- **Centralized LLM Module (`src/llm/`)**: Created unified client singletons for Gemini (`src/llm/gemini.py`) and Ollama (`src/llm/ollama.py`), eliminating 6+ redundant initialization and HTTP call sites across OCR, Graph, and RAG modules.
- **Shared Singleton Lifecycle**: Refactored FastAPI `lifespan` in `src/server.py` to instantiate `LocalVectorStore` $\rightarrow$ `MathGraphIndexer` $\rightarrow$ `MathQueryEngine` in strict dependency order, removing double memory overhead and out-of-sync store states.
- **Vector Candidate Context Injection**: Injected Top-25 semantically nearest existing graph concepts into LLM extraction prompts, establishing cross-note prerequisite edges across isolated lecture note files.
- **Post-Extraction Entity Resolution**: Added FastEmbed cosine-similarity deduplication ($>0.88$ threshold) to automatically merge entity synonyms and maintain alias lists.

### 🔨 Detailed Changes

#### 1. Knowledge Graph Engine (`src/graph/`)
- **`src/graph/indexer.py`**: Fully rewritten to implement the 3-tier cascade, noise filtering regex, vector candidate context injection, and cosine entity resolution.
- **`src/graph/schema.py`**: Purged unused `SCHEMA_SYSTEM_PROMPT`, `ALLOWED_ENTITIES`, and `ALLOWED_RELATIONS` dead code constants.

#### 2. LLM Client Architecture (`src/llm/`)
- **`src/llm/gemini.py`**: Lazy-initialized singleton wrapper for `google.genai.Client`.
- **`src/llm/ollama.py`**: Unified client supporting text chat, vision chat (Qwen2.5-VL), and health telemetry.
- Refactored `GeminiOCRProvider`, `OllamaVisionOCR`, `ContextualReassembler`, and `MathQueryEngine` to consume `src/llm/`.

#### 3. Core Engine & Server (`src/server.py`, `src/retrieval/engine.py`, `src/__init__.py`)
- **`src/retrieval/engine.py`**: Accepts shared `MathGraphIndexer` and `LocalVectorStore` instances via constructor dependency injection. Removed dead `_keyword_match_nodes()` stub.
- **`src/__init__.py`**: Bumped package `__version__` to `"2.1.0"` $\rightarrow$ `"2.2.0"`.

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
