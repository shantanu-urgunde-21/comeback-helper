# Comeback Helper Architecture & Handwritten STEM Notes Pipeline

## Executive Overview
**Comeback Helper** is an offline-first, local-first STEM Knowledge Base & RAG Assistant designed for university mathematics coursework, lecture notes, and textbook derivations. It combines **LanceDB** vector search, **NetworkX** conceptual MathPropertyGraph indexing, and a **100% Local Vision-Language (VLM)** handwritten notes ingestion engine powered by **Ollama (`qwen2.5vl:3b`)**.

---

## 🏗️ High-Level System Architecture

```
+-----------------------------------------------------------------------------------+
|                                  USER INTERFACE                                   |
|                      Web GUI (FastAPI + HTML5 + KaTeX + Vis.js)                  |
+------------------------------------------+----------------------------------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
     +------------------------------+             +------------------------------+
     |   Query & Retrieval Engine   |             |  Handwritten Ingestion Engine |
     | (Vector + Graph Hybrid RAG)  |             | (100% Local Ollama Vision)   |
     +--------------+---------------+             +--------------+---------------+
                    |                                             |
    +---------------+---------------+             +---------------+---------------+
    |                               |             |                               |
    v                               v             v                               v
+-------+                       +-------+     +-------+                       +-------+
|LanceDB|                       |NetworkX|    |Preproc|                       |Qwen2.5|
|Vectors|                       | Graph |     | (Red  |                       |  VL   |
| Store |                       | Index |     |Channel|                       | (3B)  |
+-------+                       +-------+     +-------+                       +-------+
```

---

## 🎨 Multi-Stage Handwritten Notes Pipeline (100% Local VLM)

Handwritten STEM lecture notes present unique challenges: blue notebook ruling lines, inline math symbols ($F(x) := \int_a^x f(t) dt$), and multi-line equations ($\frac{dy}{dx}$).

To run blazingly fast and 100% offline within a **4GB VRAM limit (NVIDIA GTX 1650)** without CUDA memory paging freezes, Comeback Helper uses a 4-station local VLM pipeline:

### 1. Station 1: Preprocessing & Ruling Line Erasure ([`preprocessor.py`](file:///d:/programming/comeback_helper/src/ingestion/handwriting/preprocessor.py))
* **Channel Analysis:** Extracts the Red color channel from RGB page renders. Because blue ruling lines are bright in the Red spectrum, notebook ruling lines evaporate completely, leaving sharp black ink handwriting.
* **Contrast Enhancement:** Applies adaptive CLAHE contrast sharpening.

### 2. Station 2: Native Local VLM Extraction ([`ollama_vlm.py`](file:///d:/programming/comeback_helper/src/ingestion/handwriting/ollama_vlm.py))
* **Engine:** GGUF 4-bit Quantized **`qwen2.5vl:3b`** running locally via Ollama.
* **Resolution Scaling:** Automatically resizes page renders to a maximum $1024\text{px}$ dimension before visual patch encoding, accelerating per-page inference to **~15–20 seconds**.
* **VRAM Footprint:** Consumes **~2.1 GB VRAM**, eliminating CUDA memory spillover on 4GB GPUs.

### 3. Station 3: Contextual LLM Repair Pass ([`reassembler.py`](file:///d:/programming/comeback_helper/src/ingestion/handwriting/reassembler.py))
* Normalizes LaTeX notation, repairs sentence boundaries, and verifies inline ($...$) vs block ($$...$$$) math environments.

### 4. Station 4: Vault & RAG Indexing ([`handwriting_provider.py`](file:///d:/programming/comeback_helper/src/ingestion/handwriting_provider.py))
* Saves structured Markdown notes directly to `D:\obsidian\comeback-helper\<Course>\Note.md` and updates LanceDB vector embeddings.

---

## 🏥 Health Check & Monitoring API ([`health.py`](file:///d:/programming/comeback_helper/src/ingestion/handwriting/health.py))

The system includes automated telemetry checks exposed via `/api/health/ollama`:
* **Service Status:** Verifies `http://localhost:11434` availability.
* **Model Check:** Confirms `qwen2.5vl:3b` model presence.
* **VRAM Utilization:** Real-time monitoring of CUDA allocated/reserved VRAM.
