# 🔒 Private Documentation Index

This directory contains internal technical documentation, deep-dive architectural specifications, computer vision pipeline details, and system integration test reports.

---

## 📑 Core Deep-Dive Documents

1. [**`ARCHITECTURE_DEEP_DIVE.md`**](./ARCHITECTURE_DEEP_DIVE.md)
   - End-to-end system architecture, data flow diagrams, module responsibilities, Pydantic schemas, and FastAPI singletons context lifecycle.

2. [**`HANDWRITING_VLM_PIPELINE.md`**](./HANDWRITING_VLM_PIPELINE.md)
   - Detailed breakdown of the 4-Station Local VLM Pipeline for handwritten STEM notes.
   - Red channel color space extraction for ruling line erasure.
   - Resolution downscaling and memory footprint tuning for consumer 4GB VRAM GPUs (NVIDIA GTX 1650).

3. [**`HYBRID_RAG_AND_GRAPH.md`**](./HYBRID_RAG_AND_GRAPH.md)
   - Math-aware Markdown chunking algorithm protecting `$$...$$` blocks.
   - Serverless LanceDB vector database integration and GPU FastEmbed model configuration.
   - Instructor + Pydantic PropertyGraph extraction and embedding-based semantic node matching.

---

## 🧪 Subsystem Test Reports

The [`test_reports/`](./test_reports/) directory contains diagnostic metrics and verification logs for system integration:
- [`overall_system_integration_report.md`](./test_reports/overall_system_integration_report.md)
- [`process_1_ingestion_report.md`](./test_reports/process_1_ingestion_report.md)
- [`process_2_graph_report.md`](./test_reports/process_2_graph_report.md)
- [`process_3_vector_store_report.md`](./test_reports/process_3_vector_store_report.md)
- [`process_4_hybrid_retrieval_report.md`](./test_reports/process_4_hybrid_retrieval_report.md)
