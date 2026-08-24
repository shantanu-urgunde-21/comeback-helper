# 📊 Hybrid RAG & Knowledge Graph Engine

## Overview

Traditional vector-only RAG systems fail on university mathematics and STEM coursework for two main reasons:
1. **Loss of Relational Structure:** Vector search matches text chunks with high surface similarity. However, a theorem in a Machine Learning course may depend on a linear algebra concept (e.g., Eigenvalue Decomposition) taught in a different course. Vector search cannot navigate these explicit conceptual prerequisites unless the query matches identical phrasing.
2. **Naive Text Chunking:** Standard chunkers split text based on character counts or blank lines (`\n\n`). In math documents, splitting inside a multi-step proof or between a theorem statement and its display math block (`$$...$$`) creates orphaned, context-less fragments.

Comeback Helper solves this with **Math-Aware Chunking**, **LanceDB Vector Similarity + Native BM25 FTS**, and **Decoupled 2-Pass NetworkX Math PropertyGraph Semantic Traversal**.

---

## 1. Math-Aware Chunking Algorithm (`services/vector/app/chunker.py`)

The chunking algorithm follows a strict hierarchy designed to protect mathematical structures:

```
[ Full Markdown Document ]
            │
            ▼
 1. Split on Page Markers  ──► <!-- Page N -->
            │
            ▼
 2. Split on Headings      ──► # / ## / ###
            │
            ▼
 3. Enforce Max Chunk Size ──► Protect $$ ... $$ display math blocks
            │
            ▼
 4. Merge Tiny Fragments   ──► Minimum chunk size (100 chars)
            │
            ▼
 5. Add Trailing Overlap   ──► 150 chars overlap from preceding chunk
```

### Key Safety Rules
- **Never split display math:** Equations enclosed in `$$...$$` are treated as atomic tokens.
- **Theorem-Proof Continuity:** Trailing overlap (150 chars) ensures that if a proof begins immediately after a theorem header, the theorem statement context is prepended to the proof chunk.

---

## 2. Vector Subsystem (`services/vector/app/store.py`)

### LanceDB Integration
LanceDB is an embedded, serverless vector database stored at `.storage/lancedb/`.

```python
# Table record format
records.append({
    "id": "Lecture_04_0",
    "text": "Chunk text with LaTeX math...",
    "course": "Linear Algebra",
    "source": "Lecture 04.md",
    "vector": [0.012, -0.045, ...] # FastEmbed vector embedding
})
```

### FastEmbed & Native BM25 FTS Index
- **Model:** Configured via `EMBED_MODEL` in `.env` (default: `BAAI/bge-small-en-v1.5`).
- **Providers:** Priority list `["CUDAExecutionProvider", "CPUExecutionProvider"]`.
- **BM25 FTS:** LanceDB native full-text search index (`create_index("text", config=FTS())`).
- **Error Recovery:** Automated table integrity check and clean table creation if disk files are corrupted.

---

## 3. Decoupled 2-Pass Math PropertyGraph Indexer (`services/graph/app/indexer.py`)

### Decoupled 2-Pass Pipeline Architecture

Extraction is decoupled into two separate, focused passes to eliminate token truncation and halluncinated garbage nodes:

```
[ Vault Note Content ]
           │
           ▼
 ┌────────────────────────────────────────────────────────┐
 │ Pass 1: MathNodeExtraction                             │
 │ - Extracts formal concept entity names                 │
 │ - Assigns 1-2 sentence definitions & roles             │
 │ - Generates 3-tier SKOS taxonomy (domain/sub/topic)   │
 └─────────────────────────┬──────────────────────────────┘
                           │
                           ▼
 ┌────────────────────────────────────────────────────────┐
 │ Candidate Vector Context Matching                      │
 │ - Retrieves Top-20 vector chunks from LanceDB         │
 └─────────────────────────┬──────────────────────────────┘
                           │
                           ▼
 ┌────────────────────────────────────────────────────────┐
 │ Pass 2: MathEdgeExtraction                             │
 │ - Links Pass 1 concepts + candidate context chunks     │
 │ - Generates directional edges (DEPENDS_ON, PROVES,    │
 │   USES_DEFINITION, PREREQUISITE_FOR)                   │
 └────────────────────────────────────────────────────────┘
```

#### Pass 1 Typed Roles (`MathNodeExtraction`)
- **`Theorem`**: Formal mathematical theorems (e.g., *Mixed Partials Theorem*).
- **`Definition`**: Formal definitions (e.g., *Wronskian*).
- **`Concept`**: Mathematical concepts or terms.
- **`Proof`**: Mathematical proofs or derivations.
- **`Formula`**: Core equations or identities.
- **`Lemma` / `Example`**

#### Pass 2 Directed Edges (`MathEdgeExtraction`)
- **`DEPENDS_ON`**: Prerequisite link ($A \rightarrow B$).
- **`PROVES`**: Proof to theorem relation.
- **`USES_DEFINITION`**: Concept using a definition.
- **`DERIVED_FROM`**: Formula derivation sequence.
- **`PREREQUISITE_FOR`**: Structural prerequisite link.

---

## 4. Semantic Graph Node Matching & Candidate Fallbacks

### Embedding-Based Node Matching (`services/retrieval/app/engine.py`)

```python
# Pre-compute graph node embeddings
node_text = f"{node_id}: {node_description}"
node_embedding = vector_store.embed_texts([node_text])

# At query time
query_embedding = vector_store.embed_texts([query])
# Cosine similarity matching retrieves top-3 matching graph nodes
```

### Candidate Model Fallback Loop
Synthesis uses a multi-tiered fallback loop (`gemini-3.6-flash` $\rightarrow$ `gemini-flash-latest` $\rightarrow$ `gemini-flash-lite-latest` $\rightarrow$ `Ollama`). Rate limit (`429`) errors trigger instant failover to candidate models without server errors.
