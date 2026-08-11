# Knowledge Graph Architecture Redesign & Implementation Specification

> [!NOTE]
> **Partially superseded by [`ATLAS_DESIGN.md`](./ATLAS_DESIGN.md) (2026-08-12).**
> Tasks 1, 2 and 4 below are implemented; Task 3 (provenance inspector) is not.
> `ATLAS_DESIGN.md` revisits the schema and visual model with prior-art research,
> and replaces the node/edge specifications given here.

## Executive Overview

This document specifies the technical design, ontologies, schemas, algorithms, and task roadmap to upgrade the **Comeback Helper Knowledge Graph System**. 

The design incorporates established semantic web and graph RAG standards:
- **SKOS (Simple Knowledge Organization System)**: 3-tier hierarchical taxonomy (`domain` $\rightarrow$ `subdomain` $\rightarrow$ `topic`).
- **W3C PROV-O Provenance Ontology**: Full material traceability (`doc_id`, `doc_title`, `page_number`, `section_heading`, `exact_quote`).
- **Microsoft GraphRAG Vector Sub-Catalog Linker**: Top-K nearest neighbor concept candidate retrieval to eliminate LLM token bloat while guaranteeing cross-document link discovery.

---

## 1. Data Schemas & Ontologies

### A. Provenance Schema (W3C PROV-O Model)

Every extracted node and edge contains a structured list of `provenance` records tracking exact material origin:

```python
class Provenance(BaseModel):
    doc_id: str                      # Hash of vault note
    doc_title: str                   # e.g. "Lecture notes 7 to 9.md"
    doc_path: str                    # File path in Obsidian vault
    page_number: Optional[int] = None # OCR PDF page number
    section_heading: Optional[str] = None # Surrounding section heading
    exact_quote: str                 # Exact LaTeX sentence snippet (max 250 chars)
```

### B. Concept Taxonomy Schema (SKOS Standard)

```python
class ConceptTaxonomy(BaseModel):
    domain: str                      # Tier 1: Discipline (e.g. "Differential Equations")
    subdomain: str                   # Tier 2: Area (e.g. "First-Order ODEs")
    topic: str                       # Tier 3: Specific Topic (e.g. "Integrating Factors")
```

### C. Refined Node & Edge Schemas

```python
class MathEntityRole(str, Enum):
    THEOREM = "Theorem"
    DEFINITION = "Definition"
    LEMMA = "Lemma"
    AXIOM = "Axiom"
    COROLLARY = "Corollary"
    PROVES = "Proof"
    FORMULA = "Formula"
    CONCEPT = "Concept"

class GraphNode(BaseModel):
    id: str                          # Canonical entity ID (e.g. "Integrating Factor")
    name: str                        # Display label
    role: MathEntityRole             # Entity role (Theorem, Definition, Formula, etc.)
    taxonomy: ConceptTaxonomy        # SKOS 3-level domain hierarchy
    aliases: List[str] = []          # ["u(x) factor", "Integrating Multiplier"]
    description: str                 # Formal mathematical summary definition
    provenance: List[Provenance] = [] # Exact material source locations

class GraphEdge(BaseModel):
    source: str                      # Source node ID
    target: str                      # Target node ID
    relation: str                    # e.g. "DEPENDS_ON", "USES_DEFINITION", "PROVES", "PREREQUISITE_FOR"
    description: Optional[str] = None
    provenance: List[Provenance] = [] # Evidence for relationship
```

---

## 2. Implementation Roadmap & Task Breakdown

### Task 1: Multi-Tag SKOS Taxonomy & Visual Rendering Engine

#### Objective
Refactor node schemas to include 3-tier SKOS taxonomy and implement a tag-aware dual-color scheme in the Vis.js frontend dashboard.

#### Implementation Details
1. **Schema Refactoring (`src/graph/schema.py`)**:
   - Implement `ConceptTaxonomy`, `Provenance`, and updated `GraphNode`.
2. **Vis.js Dual-Color Renderer (`static/app.js`)**:
   - **Node Fill Color (Primary Domain)**:
     - `Differential Equations` $\rightarrow$ `#8b5cf6` (Purple)
     - `Calculus` $\rightarrow$ `#10b981` (Emerald)
     - `Linear Algebra` $\rightarrow$ `#3b82f6` (Blue)
     - `General Math` $\rightarrow$ `#6366f1` (Indigo)
   - **Node Border Ring (Entity Role)**:
     - `Theorem` $\rightarrow$ `#f59e0b` (Gold Border, width: 4px)
     - `Definition` $\rightarrow` `#10b981` (Green Border, width: 3px)
     - `Formula` $\rightarrow$ `#06b6d4` (Cyan Border, width: 3px)

---

### Task 2: Vector Sub-Catalog Nearest-Neighbor LLM Linking

#### Objective
Connect concepts across separate lecture notes (*e.g., Notes 4–6 and Notes 7–9*) without passing entire database catalog into LLM context.

#### Implementation Details
1. **Candidate Retrieval**:
   - Perform FastEmbed vector search against LanceDB `concept_catalog` table to retrieve **Top-20 nearest existing concepts**.
2. **LLM Prompt Context**:
   - Pass Top-20 candidates into extraction prompt (<180 tokens), instructing Gemini to form directed edges to existing concepts when dependencies exist.

---

### Task 3: Provenance Tracking & UI Slideout Inspector

#### Objective
Clicking any node or edge in the Vis.js canvas opens a right slideout drawer displaying exact source references (Note name, PDF Page #, LaTeX quote).

#### Implementation Details
1. **Pipeline Ingestion (`src/ingestion/pipeline.py`)**:
   - Retain OCR page numbers (`<!-- Page 3 -->`) and section headings.
2. **UI Slideout Inspector (`static/app.js` & `static/index.html`)**:
   - Render provenance list with clickable note links and verbatim LaTeX quote accordions.

---

### Task 4: Noise Filtering & Heading Normalization

#### Objective
Eliminate structural headings (*e.g., "Exercise 1", "Hint", "Solution"*) from cluttering the graph as standalone concept nodes.

#### Implementation Details
1. **Regex Noise Filter**:
   - Filter structural headings matching `(?i)^(Exercise|Solution|Hint|Problem|Conclusion|Page \d+|Lecture notes).*`.
2. **Snippet Attachment**:
   - Attach exercise text as `Provenance` quotes to underlying math theorems.

---

### Task 5: NetworkX Single Source of Truth & FastAPI Sync

#### Objective
Ensure NetworkX graph store and FastAPI server mirror the new taxonomy and provenance schemas.

---

## Task Summary Table

| Task ID | Component | Summary | Output Files |
|---|---|---|---|
| **TASK-1** | Taxonomy & UI | Implement `ConceptTaxonomy` and Vis.js dual-color renderer | `src/graph/schema.py`, `static/app.js` |
| **TASK-2** | Sub-Catalog Linker | Vector candidate retrieval for cross-note linking | `src/graph/indexer.py`, `src/vector/store.py` |
| **TASK-3** | Provenance Inspector | W3C PROV-O provenance tracking & UI slideout drawer | `src/graph/schema.py`, `static/index.html`, `static/app.js` |
| **TASK-4** | Noise Filter | Blacklist structural headings and attach as provenance quotes | `src/graph/indexer.py` |
| **TASK-5** | Storage & API Sync | PropertyGraph schema migration and FastAPI router synchronization | `src/graph/indexer.py`, `src/server.py` |
