# Comeback Helper: Architecture, Vision & Refined Roadmap

## 🎯 1. Project Vision & Core Purpose

**Comeback Helper** is an open-source, local-first study assistant and knowledge management system designed for students, researchers, and engineers taking complex, math-heavy, or technical coursework (e.g., Linear Algebra, Real Analysis, Quantum Computing, Machine Learning Theory).

When overwhelmed by hundreds of pages of PDF lecture slides, problem sets, and textbooks, Comeback Helper automatically ingests documents, parses LaTeX formulas cleanly, and constructs an **Obsidian Markdown Vault** alongside an **Interactive Math PropertyGraph**.

---

## 🔄 2. End-to-End User Experience

```
[ PDF Upload ] ──► [ Local Ingestion (Marker) ] ──► [ Obsidian Markdown Vault ]
                                                             │
                                   ┌─────────────────────────┴─────────────────────────┐
                                   ▼                                                   ▼
                     [ Math PropertyGraph Indexer ]                           [ LanceDB + FastEmbed ]
                     (Instructor + Pydantic Schema)                            (Local Vector Hybrid RAG)
                                   │                                                   │
                                   └─────────────────────────┬─────────────────────────┘
                                                             ▼
                                                [ Web Dashboard UI & Q&A ]
                                                 (Vis.js Graph + KaTeX Math)
```

1. **Ingest & Real-time Stream:** User drops PDFs into the Web Dashboard or CLI. Pages render live into structured Markdown notes with LaTeX equations directly saved to their Obsidian Vault (`/vault/Linear Algebra/Lecture 04.md`).
2. **Visual Graph Exploration:** The system extracts typed mathematical nodes (`Concept`, `Theorem`, `Definition`, `Proof`, `Lemma`) and visualizes dependencies in an interactive Vis.js graph UI.
3. **Contextual Study Q&A:** The student asks questions like *"I don't understand the proof of Theorem 3.2, what prerequisites am I missing?"* The assistant traverses the Math PropertyGraph and LanceDB vector index to return exact LaTeX explanations linked to their notes.

---

## 🛠️ 3. Critical Critique & Refined Toolstack

### Identified Architectural Flaws & Fixes

1. **Eliminated Tool Bloat (Marker vs MinerU):** Recommending multiple PDF parsers adds unnecessary complexity. **Marker** is selected as the primary local PDF engine—it is ~10x faster on GPU, uses ~3-4GB VRAM, and outputs clean Markdown + LaTeX. Cloud Gemini OCR / `LightOnOCR-2-1B` serve as fallbacks for scanned images.
2. **Dropped Generic LightRAG in favor of Custom Math Schema:** Generic GraphRAG tools extract arbitrary entity triples. `comeback_helper` requires a domain-specific **`MathPropertyGraph`** (`depends_on`, `proves`, `uses_definition`). We use **Instructor + Pydantic** to enforce exact schema extractions.
3. **VRAM Safety via Sequential Execution:** Running local OCR and local 7B LLMs simultaneously on consumer GPUs (8GB VRAM) causes CUDA OOM crashes. The pipeline executes in sequential stages with explicit model unloading.

---

## 📦 4. Selected Stack Component Breakdown

| Layer | Selected Tool | Role & Justification | Hardware Specs & Constraints |
| :--- | :--- | :--- | :--- |
| **PDF Ingestion** | **Marker** | Fast local PDF-to-Markdown parser preserving LaTeX formulas (`$$...$$`). | 3-4 GB VRAM (GPU) / 8-16 GB RAM. CPU supported (slower). |
| **Structured Graph Extraction** | **Instructor** | Wraps LLM calls with Pydantic for 100% type-safe JSON extraction of `GraphNode` and `GraphEdge`. | Minimal overhead (< 10MB RAM). Eliminates JSON syntax errors. |
| **Vector Storage** | **LanceDB** | Embedded, serverless Rust vector database running locally inside `.storage/lancedb/`. | Extremely lightweight (< 100MB RAM), fast disk-backed vector search. |
| **Local Embeddings** | **FastEmbed** | Runs local embedding models (e.g. `BAAI/bge-small-en-v1.5`) via ONNX Runtime without API calls. | ~300-500 MB RAM on CPU. Zero VRAM required. |
| **Graph Storage & UI** | **NetworkX + Vis.js** | In-memory graph structure persisted to `.storage/graph.json`, visualized via Vis.js and rendered with KaTeX. | Low RAM usage. Browser-native interactive math visualization. |
| **LLM Inference** | **Dual Engine** (Gemini API / Ollama DeepSeek-R1) | Cloud Gemini (Free Tier) for high speed, or Ollama locally for 100% offline private study. | Ollama 7B requires ~5.5-6 GB VRAM (`Q4_K_M`). |

---

## ⚡ 5. Sequential Execution Pipeline (VRAM Management)

To avoid CUDA Out-Of-Memory errors on 8GB VRAM consumer GPUs:

```
[Stage 1: PDF Parsing] ──► Loads Marker/VLM ──► Writes Markdown to Vault ──► Unloads OCR Weights
                                                                                   │
[Stage 2: Vector Index] ──► FastEmbed (CPU) ──► Writes Embeddings to LanceDB ─────┤
                                                                                   │
[Stage 3: Graph Extraction] ──► Instructor + LLM ──► Updates `.storage/graph.json` ─┘
```

---

## 📋 6. Key Functional Requirements

1. **LaTeX Integrity:** Zero corruption of block (`$$...$$`) and inline (`$...$`) math expressions.
2. **Incremental Vault Synchronization:** Real-time page writing so users never wait on black-box spinners.
3. **Obsidian Compatibility:** Markdown notes must use standard YAML frontmatter and `[[wikilinks]]`.
4. **Offline Resilience:** The entire system must be operable offline using local models (Marker + FastEmbed + Ollama).
