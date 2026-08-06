# 📊 Hybrid RAG & Knowledge Graph Engine

## Overview

Traditional vector-only RAG systems fail on university mathematics and STEM coursework for two main reasons:
1. **Loss of Relational Structure:** Vector search matches text chunks with high surface similarity. However, a theorem in a Machine Learning course may depend on a linear algebra concept (e.g., Eigenvalue Decomposition) taught in a different course. Vector search cannot navigate these explicit conceptual prerequisites unless the query matches identical phrasing.
2. **Naive Text Chunking:** Standard chunkers split text based on character counts or blank lines (`\n\n`). In math documents, splitting inside a multi-step proof or between a theorem statement and its display math block (`$$...$$`) creates orphaned, context-less fragments.

Comeback Helper solves this with **Math-Aware Chunking**, **LanceDB Vector Similarity**, and **NetworkX Math PropertyGraph Semantic Traversal**.

---

## 1. Math-Aware Chunking Algorithm (`src/chunker.py`)

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

## 2. Vector Subsystem (`src/vector/store.py`)

### LanceDB Integration
LanceDB is an embedded, serverless vector database stored at `.storage/lancedb/`.

```python
# Table schema
records.append({
    "id": "Lecture_04_0",
    "text": "Chunk text with LaTeX math...",
    "course": "Linear Algebra",
    "source": "Lecture 04.md",
    "vector": [0.012, -0.045, ...] # 1024-dim embedding
})
```

### FastEmbed & GPU Acceleration
- **Model:** Configured via `EMBED_MODEL` in `.env` (default: `BAAI/bge-small-en-v1.5`).
- **Providers:** Priority list `["CUDAExecutionProvider", "CPUExecutionProvider"]`.
- **Course Scoping:** `search_similar(query, course="Linear Algebra")` applies a native LanceDB SQL `where` clause (`course = 'Linear Algebra'`).

---

## 3. Math PropertyGraph Indexer (`src/graph/indexer.py`)

### Extraction Schema
The system uses Gemini with Pydantic structured output models (`Instructor` pattern):

#### Typed Nodes
- **`Theorem`**: Formal mathematical theorems (e.g., *Spectral Theorem*).
- **`Definition`**: Formal definitions (e.g., *Symmetric Matrix*).
- **`Concept`**: Mathematical concepts or terms.
- **`Proof`**: Mathematical proofs or derivations.
- **`Formula`**: Core equations or identities.
- **`Lemma` / `Example` / `Course`**

#### Directed Edges
- **`DEPENDS_ON`**: Prerequisite link ($A \rightarrow B$).
- **`PROVES`**: Proof to theorem relation.
- **`USES_DEFINITION`**: Concept using a definition.
- **`DERIVED_FROM`**: Formula derivation sequence.
- **`APPLIES_TO`**: Theoretical concept applied to practical domain.

---

## 4. Semantic Graph Node Matching & Traversal

Legacy GraphRAG systems use exact keyword substring matching to find entry points in the graph. This fails when:
- Query uses "matrix diagonalization" but graph node is titled "Spectral Theorem".

### Embedding-Based Node Matching (`src/retrieval/engine.py`)

```python
# Pre-compute graph node embeddings
node_text = f"{node_id}: {node_description}"
node_embedding = vector_store.embed_texts([node_text])

# At query time
query_embedding = vector_store.embed_texts([query])
similarity = cosine_similarity(query_embedding, node_embedding)
```

1. **Top Node Selection:** Selects top 3 graph nodes with similarity score $> 0.3$.
2. **Dual-Direction Traversal:** Collects outgoing edges (successors / dependencies) AND incoming edges (predecessors / applications).
3. **Context Fusion:** Formats graph connections as explicit bullet points injected alongside LanceDB vector chunks into the Gemini synthesis prompt.
