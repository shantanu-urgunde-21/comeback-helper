# 🔒 Private Documentation Index

This directory contains internal technical documentation, deep-dive architectural specifications, computer vision pipeline details, and system integration test reports for **Comeback Helper v2.4.0**.

---

## 📑 Core Deep-Dive Documents

1. [**`ARCHITECTURE_DEEP_DIVE.md`**](./ARCHITECTURE_DEEP_DIVE.md)
   - End-to-end system architecture, single-process FastAPI data flow, module responsibilities, 2-Pass Pydantic graph schemas, singletons context lifecycle, and Vis.js real-time graph layout controls.

2. [**`HANDWRITING_VLM_PIPELINE.md`**](./HANDWRITING_VLM_PIPELINE.md)
   - Detailed breakdown of 3-page multi-image OCR batching + 4s pacing delay in Gemini Vision.
   - Breakdown of the 4-Station Local VLM Pipeline for handwritten STEM notes (OpenCV Red Channel thresholding & Ollama Qwen2.5-VL tuning).

3. [**`HYBRID_RAG_AND_GRAPH.md`**](./HYBRID_RAG_AND_GRAPH.md)
   - Math-aware Markdown chunking algorithm protecting `$$...$$` blocks.
   - LanceDB serverless vector database with native BM25 full-text search (FTS) and table corruption auto-recovery.
   - Decoupled 2-Pass PropertyGraph extraction (`MathNodeExtraction` $\rightarrow$ `MathEdgeExtraction`) and candidate model synthesis fallback loop.

---

## 🧪 Subsystem Test Reports

The [`test_reports/`](./test_reports/) directory contains diagnostic metrics and verification logs for system integration:
- [`overall_system_integration_report.md`](./test_reports/overall_system_integration_report.md)
- [`process_1_ingestion_report.md`](./test_reports/process_1_ingestion_report.md)
- [`process_2_graph_report.md`](./test_reports/process_2_graph_report.md)
- [`process_3_vector_store_report.md`](./test_reports/process_3_vector_store_report.md)
- [`process_4_hybrid_retrieval_report.md`](./test_reports/process_4_hybrid_retrieval_report.md)
