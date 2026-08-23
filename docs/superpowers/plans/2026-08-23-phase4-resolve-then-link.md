# Phase 4: Resolve-then-link Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework the 2-pass LLM extraction pipeline so that Pass 1 resolves concept names to canonical IDs per-chunk (chunk-level mention provenance), and Pass 2 receives those IDs and emits edges already keyed by canonical ID, eliminating all post-hoc `_resolve_entity` calls on edge endpoints.

**Architecture:** Split the note into chunks by markdown heading; run Pass 1 per chunk, immediately resolving each extracted name to a canonical concept ID and writing a mention with the chunk-level `chunk_id`; accumulate a document-wide `{name → id}` map; run Pass 2 once on the full document text, providing the accumulated ID map so the LLM emits edges with canonical IDs directly; validate/fallback edge endpoints via the pre-built map rather than re-querying the authority.

**Tech Stack:** Python 3.11, NetworkX, SQLite (via `graph_store.py`), Gemini/Ollama via existing client wrappers

**Spec:** `plan.md` (Phase 4 section) + `CLAUDE.md` (invariants section)

## Global Constraints

- Test runner is **`python -m unittest`**, not pytest — no pytest installed.
- Tests read/write the real `.storage/` (not fixtures) — this is by design. Do not add teardown that deletes `.storage/graph.json` or the SQLite DB.
- Imports use container names: `graph.app.indexer`, `shared.config` — never `services.graph.app.indexer`. `import src` at the top of each test file puts `services/` on sys.path.
- `PREREQUISITE_FOR(A,B)` must be canonicalized to `DEPENDS_ON(B,A)` — the existing `_normalize_relation()` handles this; do not bypass it.
- `save_graph()` writes `entity_type` as `type` in graph.json — do not change this mapping.
- The block-extraction path (`use_llm=False`) must keep working unchanged — Phase 4 changes are scoped to the LLM path.
- `normalize()` is in `services/graph/app/schema.py` line 10 — import it via the existing `from .schema import (...)` block.

---

## File Map

**Modified:**
- `services/graph/app/indexer.py` — three new methods + prompt rewrite + `index_note()` refactor
- `tests/test_graph_indexer.py` — new test class `TestPhase4`

**Not modified:** `schema.py`, `graph_store.py`, `authority.py` — their interfaces are unchanged.

---

### Task 1: Add `_split_chunks()` and tests

**Files:**
- Modify: `services/graph/app/indexer.py` (add method inside `MathGraphIndexer`)
- Test: `tests/test_graph_indexer.py` (add `test_split_chunks_*` methods to new `TestPhase4` class)

**Interfaces:**
- Produces: `MathGraphIndexer._split_chunks(text: str, document_id: str) -> list[tuple[str, str]]` — each tuple is `(chunk_id, chunk_text)` where `chunk_id = f"{document_id}#s{n:04d}"` and `chunk_text` is the stripped section content.

- [ ] **Step 1: Write the failing tests**

Add a new test class at the bottom of `tests/test_graph_indexer.py`:

```python
class TestPhase4(unittest.TestCase):
    def setUp(self):
        self.indexer = MathGraphIndexer()
        self.doc_id = "/vault/course/note.md"

    def test_split_chunks_with_headings(self):
        text = "## Section 1\nContent A\n## Section 2\nContent B"
        chunks = self.indexer._split_chunks(text, self.doc_id)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0][0], f"{self.doc_id}#s0000")
        self.assertEqual(chunks[1][0], f"{self.doc_id}#s0001")
        self.assertIn("Content A", chunks[0][1])
        self.assertIn("Content B", chunks[1][1])

    def test_split_chunks_no_headings_returns_one_chunk(self):
        text = "No headings here, just plain content."
        chunks = self.indexer._split_chunks(text, self.doc_id)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0][0], f"{self.doc_id}#s0000")
        self.assertIn("plain content", chunks[0][1])

    def test_split_chunks_skips_empty_sections(self):
        # First section has no content after heading — should be skipped
        text = "## Empty Section\n\n## Real Section\nContent B"
        chunks = self.indexer._split_chunks(text, self.doc_id)
        # Only the non-empty section should appear
        self.assertEqual(len(chunks), 1)
        self.assertIn("Content B", chunks[0][1])

    def test_split_chunks_three_levels(self):
        text = "# H1\nContent A\n## H2\nContent B\n### H3\nContent C"
        chunks = self.indexer._split_chunks(text, self.doc_id)
        self.assertEqual(len(chunks), 3)
```

- [ ] **Step 2: Run tests to verify they fail**

```
python -m unittest tests.test_graph_indexer.TestPhase4 -v
```
Expected: `AttributeError: 'MathGraphIndexer' object has no attribute '_split_chunks'`

- [ ] **Step 3: Implement `_split_chunks()`**

Add after the `_get_candidate_context` method (around line 439 in `services/graph/app/indexer.py`), before `extract_from_text`:

```python
def _split_chunks(self, text: str, document_id: str) -> list[tuple[str, str]]:
    """Split markdown text into (chunk_id, chunk_text) by heading (H1–H3).

    Each section heading starts a new chunk. Empty sections are dropped.
    chunk_id format: '{document_id}#s{n:04d}', zero-indexed.
    Falls back to the whole document as one chunk when no headings exist.
    """
    sections = re.split(r'\n(?=#{1,3} )', text)
    chunks = [
        (f"{document_id}#s{i:04d}", s.strip())
        for i, s in enumerate(sections)
        if s.strip()
    ]
    return chunks if chunks else [(f"{document_id}#s0000", text)]
```

- [ ] **Step 4: Run tests to verify they pass**

```
python -m unittest tests.test_graph_indexer.TestPhase4.test_split_chunks_with_headings tests.test_graph_indexer.TestPhase4.test_split_chunks_no_headings_returns_one_chunk tests.test_graph_indexer.TestPhase4.test_split_chunks_skips_empty_sections tests.test_graph_indexer.TestPhase4.test_split_chunks_three_levels -v
```
Expected: 4 PASS

- [ ] **Step 5: Run full test suite to verify no regressions**

```
python -m unittest discover -s tests -v
```
Expected: 12/12 pass (or 11/12 with the pre-existing LanceDB failure — see plan.md Phase 5 note)

- [ ] **Step 6: Commit**

```bash
git add services/graph/app/indexer.py tests/test_graph_indexer.py
git commit -m "feat: add _split_chunks() for chunk-level mention provenance (plan.md Phase 4)"
```

---

### Task 2: Update Pass 2 — id-map prompt, new signature, edge-endpoint normalizer

**Files:**
- Modify: `services/graph/app/indexer.py`:
  - Replace `PASS2_EDGE_PROMPT` (module-level constant)
  - Add `_normalize_edge_endpoint()` method to `MathGraphIndexer`
  - Replace `_get_candidate_context()` return type `List[str]` → `dict[str, str]`
  - Replace `_extract_edges_pass()` signature and body
- Test: `tests/test_graph_indexer.py` — add methods to `TestPhase4`

**Interfaces:**
- Consumes (from Task 1): `MathGraphIndexer._split_chunks()`
- Produces:
  - `MathGraphIndexer._get_candidate_context(text: str) -> dict[str, str]` — `{concept_id: display_label}`
  - `MathGraphIndexer._normalize_edge_endpoint(raw: str, id_to_name: dict[str, str], name_to_id: dict[str, str]) -> str | None`
  - `MathGraphIndexer._extract_edges_pass(text: str, doc_concept_map: dict[str, str], existing_concept_map: dict[str, str]) -> list[GraphEdge]`
  - `PASS2_EDGE_PROMPT` — new string template with `{concept_id_map}`, `{new_concept_ids}`, `{existing_concept_ids}`, `{text}`

- [ ] **Step 1: Write the failing tests**

Add to `class TestPhase4` in `tests/test_graph_indexer.py`:

```python
    def test_normalize_edge_endpoint_canonical_id_passthrough(self):
        id_to_name = {"Q124743": "Wronskian", "CUST_abc123": "Integrating Factor"}
        name_to_id = {"Wronskian": "Q124743", "Integrating Factor": "CUST_abc123"}
        # A canonical ID should pass through unchanged
        result = self.indexer._normalize_edge_endpoint("Q124743", id_to_name, name_to_id)
        self.assertEqual(result, "Q124743")

    def test_normalize_edge_endpoint_display_name_fallback(self):
        id_to_name = {"Q124743": "Wronskian", "CUST_abc123": "Integrating Factor"}
        name_to_id = {"Wronskian": "Q124743", "Integrating Factor": "CUST_abc123"}
        # LLM emitted a display name instead of an ID — should resolve via name_to_id
        result = self.indexer._normalize_edge_endpoint("Wronskian", id_to_name, name_to_id)
        self.assertEqual(result, "Q124743")

    def test_normalize_edge_endpoint_normalized_fallback(self):
        id_to_name = {"CUST_abc123": "Integrating Factor"}
        name_to_id = {"Integrating Factor": "CUST_abc123"}
        # LLM emitted slightly different casing — normalize() should bridge the gap
        result = self.indexer._normalize_edge_endpoint("integrating factor", id_to_name, name_to_id)
        self.assertEqual(result, "CUST_abc123")

    def test_normalize_edge_endpoint_unknown_returns_none(self):
        id_to_name = {"Q124743": "Wronskian"}
        name_to_id = {"Wronskian": "Q124743"}
        # Completely unknown endpoint — should return None
        result = self.indexer._normalize_edge_endpoint("Frobenius Method", id_to_name, name_to_id)
        self.assertIsNone(result)
```

- [ ] **Step 2: Run tests to verify they fail**

```
python -m unittest tests.test_graph_indexer.TestPhase4.test_normalize_edge_endpoint_canonical_id_passthrough -v
```
Expected: `AttributeError: 'MathGraphIndexer' object has no attribute '_normalize_edge_endpoint'`

- [ ] **Step 3: Add `normalize` to the schema import in indexer.py**

The import block at the top of `services/graph/app/indexer.py` starts at line 11. Add `normalize` to it:

```python
from .schema import (
    MathNodeExtraction,
    MathEdgeExtraction,
    MathEntityExtraction,
    GraphNode,
    GraphEdge,
    ConceptTaxonomy,
    Provenance,
    normalize,
)
```

- [ ] **Step 4: Replace `PASS2_EDGE_PROMPT`**

The current `PASS2_EDGE_PROMPT` (lines 92–110 in indexer.py) uses `{new_concepts}`, `{existing_concepts}`, `{text}`. Replace the entire constant with:

```python
PASS2_EDGE_PROMPT = """\
You are an expert mathematical relationship and prerequisite linker.
TASK: Establish directional relationships between mathematical concepts using ONLY the concept IDs in the dictionary below.

CONCEPT DICTIONARY (concept_id → display name):
{concept_id_map}

NEW CONCEPT IDS FROM THIS NOTE (focus edges on these):
{new_concept_ids}

EXISTING KNOWLEDGE BASE CONCEPT IDS (available link targets):
{existing_concept_ids}

STRICT RULES:
1. Use ONLY concept IDs from the CONCEPT DICTIONARY as edge source and target values. Never invent a new name or ID.
2. Valid relation types: DEPENDS_ON, USES_DEFINITION, PROVES, COROLLARY_OF, USES_AXIOM, USES_LEMMA.
3. DEPENDS_ON(A, B) means A requires B — B is the more foundational concept. Never emit an inverse "is a prerequisite for" edge.
4. Include an evidence quote (the sentence from the text that supports the relationship) in the description field where possible.

TEXT:
{text}
"""
```

- [ ] **Step 5: Add `_normalize_edge_endpoint()` method**

Add this method inside `MathGraphIndexer`, after `_split_chunks()`:

```python
def _normalize_edge_endpoint(
    self,
    raw: str,
    id_to_name: dict[str, str],
    name_to_id: dict[str, str],
) -> str | None:
    """Map a Pass 2 edge endpoint to a canonical concept id.

    The LLM should emit canonical IDs (the keys of id_to_name), but may
    emit display names instead. This method handles both cases and falls
    back to normalize()-based matching for minor casing differences.
    Returns None if the endpoint cannot be resolved — the caller must
    skip that edge rather than storing a garbage id.
    """
    if raw in id_to_name:
        return raw
    if raw in name_to_id:
        return name_to_id[raw]
    norm_raw = normalize(raw)
    for name, cid in name_to_id.items():
        if normalize(name) == norm_raw:
            return cid
    log.warning(f"Pass 2 edge endpoint '{raw}' not in concept map — skipping edge")
    return None
```

- [ ] **Step 6: Replace `_get_candidate_context()` return type**

Find `_get_candidate_context` (around line 420) and replace the entire method:

```python
def _get_candidate_context(self, text: str) -> dict[str, str]:
    """Returns {concept_id: display_label} for the most relevant existing
    concepts, used as Pass 2 context. Capped at 25 entries to keep the
    prompt size bounded.
    """
    candidates: dict[str, str] = {}
    if self._vector_store is not None:
        try:
            summary = text[:500]
            results = self._vector_store.search_similar(summary, top_k=20)
            for r in results:
                source = r.get("source", "")
                if source and source != "init.md" and source in self.graph.nodes:
                    label = self.graph.nodes[source].get("label", source)
                    candidates[source] = label
        except Exception:
            pass

    for n in list(self.graph.nodes)[:30]:
        if n not in candidates:
            candidates[n] = self.graph.nodes[n].get("label", n)

    return dict(list(candidates.items())[:25])
```

- [ ] **Step 7: Replace `_extract_edges_pass()` signature and body**

Replace the existing `_extract_edges_pass` method (lines 267–327):

```python
def _extract_edges_pass(
    self,
    text: str,
    doc_concept_map: dict[str, str],      # name → canonical_id (this document)
    existing_concept_map: dict[str, str],  # canonical_id → label (existing graph)
) -> list[GraphEdge]:
    """Executes Pass 2 (Relationship & Edge Linker) via Gemini or Ollama.

    Receives pre-resolved concept maps so the LLM works with canonical IDs
    rather than display names. The concept_id_map in the prompt is the
    merged id→name view; new_concept_ids and existing_concept_ids separate
    the two populations so the LLM knows which are new vs. already known.
    """
    if not doc_concept_map:
        return []

    # Build the id→name view the prompt exposes to the LLM
    id_to_name: dict[str, str] = {v: k for k, v in doc_concept_map.items()}
    id_to_name.update(existing_concept_map)

    concept_id_map_json = json.dumps(id_to_name, ensure_ascii=False)
    new_concept_ids_json = json.dumps(list(doc_concept_map.values()))
    existing_concept_ids_json = json.dumps(list(existing_concept_map.keys()))

    client = get_gemini_client()
    if client:
        prompt = PASS2_EDGE_PROMPT.format(
            concept_id_map=concept_id_map_json,
            new_concept_ids=new_concept_ids_json,
            existing_concept_ids=existing_concept_ids_json,
            text=text,
        )
        for model_name in get_gemini_candidate_models():
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=MathEdgeExtraction,
                        temperature=0.1,
                    ),
                )
                data = json.loads(response.text)
                edges = MathEdgeExtraction(**data).edges
                log.info(f"Pass 2 (Gemini {model_name}): Linked {len(edges)} relationship edges.")
                return edges
            except Exception as e:
                log.warning(f"Pass 2 Gemini ({model_name}) edge extraction failed ({e}), trying candidate...")

    # Ollama Fallback
    ollama = get_ollama_client()
    if ollama.is_available():
        for model in ["llama3.2", "qwen2.5:3b", "phi3:mini"]:
            if not ollama.has_model(model):
                continue
            prompt = PASS2_EDGE_PROMPT.format(
                concept_id_map=concept_id_map_json,
                new_concept_ids=new_concept_ids_json,
                existing_concept_ids=existing_concept_ids_json,
                text=text[:3000],
            )
            prompt += (
                "\n\nRespond ONLY with valid JSON matching:\n"
                '{"edges": [{"source": "concept_id", "target": "concept_id", "relation": "DEPENDS_ON|USES_DEFINITION|PROVES|COROLLARY_OF|USES_AXIOM|USES_LEMMA", "description": "evidence quote"}]}'
            )
            resp = ollama.chat(prompt=prompt, model=model, response_format="json", timeout=60)
            if resp:
                try:
                    data = json.loads(resp)
                    edges = MathEdgeExtraction(**data).edges
                    log.info(f"Pass 2 (Ollama {model}): Linked {len(edges)} relationship edges.")
                    return edges
                except Exception:
                    pass

    return []
```

- [ ] **Step 8: Run the endpoint-normalizer tests to verify they pass**

```
python -m unittest tests.test_graph_indexer.TestPhase4.test_normalize_edge_endpoint_canonical_id_passthrough tests.test_graph_indexer.TestPhase4.test_normalize_edge_endpoint_display_name_fallback tests.test_graph_indexer.TestPhase4.test_normalize_edge_endpoint_normalized_fallback tests.test_graph_indexer.TestPhase4.test_normalize_edge_endpoint_unknown_returns_none -v
```
Expected: 4 PASS

- [ ] **Step 9: Run full test suite**

```
python -m unittest discover -s tests -v
```
Expected: no new failures (existing tests use `extract_from_text()` which still calls the old `_extract_edges_pass()` internally — we'll fix that wiring in Task 3).

- [ ] **Step 10: Commit**

```bash
git add services/graph/app/indexer.py tests/test_graph_indexer.py
git commit -m "feat: Pass 2 now receives id-map and emits canonical IDs (plan.md Phase 4)"
```

---

### Task 3: Refactor `index_note()` — chunk-level Pass 1, accumulated Pass 2

**Files:**
- Modify: `services/graph/app/indexer.py` — `index_note()` body only
- Test: `tests/test_graph_indexer.py` — add `test_index_note_mentions_chunk_ids` to `TestPhase4`

**Interfaces:**
- Consumes (from Task 1): `_split_chunks(text, document_id) -> list[tuple[str, str]]`
- Consumes (from Task 2): `_normalize_edge_endpoint(raw, id_to_name, name_to_id) -> str | None`, new `_extract_edges_pass(text, doc_concept_map, existing_concept_map)`, new `_get_candidate_context() -> dict[str, str]`

- [ ] **Step 1: Write the failing test**

The test verifies that after `index_note()` runs on a note with two sections, the `mentions` table contains rows with section-level chunk_ids (not just the document id).

Add to `class TestPhase4` in `tests/test_graph_indexer.py`:

```python
    def test_index_note_mentions_use_chunk_ids(self):
        """Mentions written during index_note() carry chunk-level chunk_ids."""
        import tempfile, os
        from graph.app import graph_store

        # Build a two-section note with a concept in each section
        note_content = (
            "## First Principles\n"
            "The Wronskian is a determinant used to check linear independence.\n\n"
            "## Applications\n"
            "Abel's Identity relates the Wronskian to the coefficient of y'.\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", dir=self.indexer.vault_path,
            delete=False, encoding="utf-8"
        ) as f:
            f.write(note_content)
            tmp_path = f.name

        try:
            self.indexer.index_note(Path(tmp_path), use_llm=False)
            document_id = tmp_path

            # At least one mention should have a chunk-level chunk_id (contains '#s')
            with graph_store.connect() as conn:
                rows = conn.execute(
                    "SELECT chunk_id FROM mentions WHERE chunk_id LIKE ?",
                    (f"{document_id}#s%",)
                ).fetchall()

            self.assertGreater(len(rows), 0, "Expected at least one chunk-level mention")
        finally:
            os.unlink(tmp_path)
```

- [ ] **Step 2: Run test to verify it fails**

```
python -m unittest tests.test_graph_indexer.TestPhase4.test_index_note_mentions_use_chunk_ids -v
```
Expected: FAIL — mentions currently store `chunk_id=document_id` (no `#s` suffix).

- [ ] **Step 3: Refactor `index_note()`**

Replace the `index_note` method body (lines 717–801 in `services/graph/app/indexer.py`) with:

```python
def index_note(self, note_path: Path, use_llm: bool = False):
    """Indexes a single Markdown file into the NetworkX graph.

    Phase 4 flow (use_llm=True):
      - Split note into chunks by heading.
      - Pass 1 runs per chunk: extract nodes, resolve names → canonical IDs,
        write mentions with chunk-level chunk_id, accumulate doc_concept_map.
      - Pass 2 runs once on the full text: receives the accumulated id map,
        emits edges already keyed by canonical ID.

    Phase 4 flow (use_llm=False):
      - Block extraction on full text (unchanged from Phase 3).
      - Chunks are still used for mentions so provenance is chunk-level.
    """
    content = note_path.read_text(encoding="utf-8")
    course = note_path.parent.name if note_path.parent != self.vault_path else "General"
    main_node = note_path.stem
    document_id = str(note_path)

    prov_record = Provenance(
        doc_id=main_node,
        doc_title=f"{main_node}.md",
        doc_path=str(note_path),
        exact_quote=content[:200].replace("\n", " "),
    ).model_dump()

    chunks = self._split_chunks(content, document_id)

    from . import graph_store

    with graph_store.connect() as conn:
        # ----------------------------------------------------------------
        # Pass 1: per chunk — extract nodes, resolve, accumulate concept map
        # ----------------------------------------------------------------
        doc_concept_map: dict[str, str] = {}  # surface_name → canonical_id

        for chunk_id, chunk_text in chunks:
            if use_llm:
                raw_nodes = self._extract_nodes_pass(chunk_text, course)
                chunk_nodes = [n for n in raw_nodes if _is_valid_entity(n.name)]
                if not chunk_nodes:
                    block = self._block_extraction(chunk_text, course)
                    chunk_nodes = [n for n in block.nodes if _is_valid_entity(n.name)]
            else:
                block = self._block_extraction(chunk_text, course)
                chunk_nodes = [n for n in block.nodes if _is_valid_entity(n.name)]

            for node in chunk_nodes:
                n_id = self._resolve_entity(
                    node.id or node.name, document_id=document_id, course=course
                )
                doc_concept_map[node.name] = n_id

                etype = (
                    node.entity_type.value
                    if hasattr(node.entity_type, "value")
                    else str(node.entity_type)
                )
                tax_dict = (
                    node.taxonomy.model_dump()
                    if hasattr(node.taxonomy, "model_dump")
                    else {"domain": course, "subdomain": "Course Notes", "topic": n_id}
                )

                if n_id not in self.graph:
                    self.graph.add_node(
                        n_id,
                        id=n_id,
                        label=node.name,
                        entity_type=etype,
                        taxonomy=tax_dict,
                        description=node.description,
                        provenance=[prov_record],
                        aliases=node.aliases if hasattr(node, "aliases") else [],
                    )
                else:
                    self.graph.nodes[n_id]["taxonomy"] = tax_dict
                    prov_list = self.graph.nodes[n_id].get("provenance", [])
                    if isinstance(prov_list, list):
                        prov_list.append(prov_record)
                        self.graph.nodes[n_id]["provenance"] = prov_list

                node_data = self.graph.nodes[n_id]
                graph_store.upsert_node_attrs(
                    conn, n_id,
                    label=node_data.get("label", n_id),
                    entity_type=node_data.get("entity_type", "Concept"),
                    taxonomy=node_data.get("taxonomy", {}),
                    description=node_data.get("description", ""),
                    provenance=node_data.get("provenance", []),
                    aliases=node_data.get("aliases", []),
                )
                # Chunk-level chunk_id (Phase 4: was document_id in Phase 3)
                graph_store.insert_mention(
                    conn,
                    chunk_id=chunk_id,
                    surface_text=node.name,
                    concept_id=n_id,
                )

        # ----------------------------------------------------------------
        # Pass 2: once on full document — edges with canonical IDs
        # ----------------------------------------------------------------
        existing_concept_map = self._get_candidate_context(content)

        if use_llm:
            raw_edges = self._extract_edges_pass(content, doc_concept_map, existing_concept_map)
        else:
            block = self._block_extraction(content, course)
            raw_edges = block.edges

        # Build lookup maps for endpoint normalization
        id_to_name: dict[str, str] = {v: k for k, v in doc_concept_map.items()}
        id_to_name.update(existing_concept_map)
        name_to_id: dict[str, str] = dict(doc_concept_map)
        for cid, label in existing_concept_map.items():
            name_to_id.setdefault(label, cid)

        for edge in raw_edges:
            src = self._normalize_edge_endpoint(edge.source, id_to_name, name_to_id)
            tgt = self._normalize_edge_endpoint(edge.target, id_to_name, name_to_id)
            if not src or not tgt:
                continue

            if src not in self.graph:
                self.graph.add_node(src, id=src, label=edge.source)
                graph_store.upsert_node_attrs(conn, src, label=edge.source)
            if tgt not in self.graph:
                self.graph.add_node(tgt, id=tgt, label=edge.target)
                graph_store.upsert_node_attrs(conn, tgt, label=edge.target)

            rel = edge.relation.value if hasattr(edge.relation, "value") else str(edge.relation)
            src, tgt, rel = _normalize_relation(src, tgt, rel)
            self.graph.add_edge(src, tgt, relation=rel, label=rel)
            graph_store.insert_edge(
                conn,
                source_id=src,
                target_id=tgt,
                relation=rel,
                chunk_id=document_id,
                quote=edge.description,
                origin="extracted",
            )
```

- [ ] **Step 4: Run the chunk-id test to verify it passes**

```
python -m unittest tests.test_graph_indexer.TestPhase4.test_index_note_mentions_use_chunk_ids -v
```
Expected: PASS

- [ ] **Step 5: Run full test suite**

```
python -m unittest discover -s tests -v
```
Expected: all previously passing tests still pass. The existing `test_schema_models` and `test_indexer_graph_structure` tests do not call `index_note()` so they are unaffected.

- [ ] **Step 6: Smoke-test the CLI (no LLM cost, block extraction)**

```
python -m src.cli graph-stats
```
Expected: server prints node/edge counts without error. Graph structure is unchanged (this is read-only).

- [ ] **Step 7: Verify graph health unchanged**

```
python scripts/graph_health.py
```
Expected: same output as before — 75 nodes, 121 edges, 0 duplicate groups. (The refactor does not re-index existing notes.)

- [ ] **Step 8: Commit**

```bash
git add services/graph/app/indexer.py tests/test_graph_indexer.py
git commit -m "refactor: index_note() uses chunks for Pass 1, id-map for Pass 2 (plan.md Phase 4)"
```

---

## Self-Review

**Spec coverage check:**

| Phase 4 requirement | Covered by |
|---|---|
| Pass 1 → identify surface forms → resolve_concept() → return concept ids | Task 3: per-chunk Pass 1 calls `_resolve_entity()` per node, builds `doc_concept_map` |
| Pass 2 receives ids, not names, uses only those ids | Task 2: new `PASS2_EDGE_PROMPT` + new `_extract_edges_pass` signature; id_to_name dict drives the prompt |
| Accumulate resolved ids across the document, not per chunk | Task 3: `doc_concept_map` accumulates across all chunks before Pass 2 runs |
| Every edge carries chunk_id, quote, origin | Task 3: `insert_edge()` still called with `chunk_id=document_id`, `quote=edge.description`, `origin="extracted"` — already satisfied from Phase 3; edge chunk_id is document-level (chunk-level edge provenance is a later refinement) |
| chunk-level (not document-level) granularity | Task 1 + Task 3: `insert_mention()` now called with `chunk_id=chunk_id` from `_split_chunks` |
| Exit: new ingests add no duplicate concepts | Ensured by `_resolve_entity()` deterministic ladder — unchanged from Phase 1/2; this refactor preserves it |

**Placeholder scan:** No TBDs, no "implement later", no "similar to Task N" patterns.

**Type consistency:**
- `_split_chunks` → `list[tuple[str, str]]` used consistently in Task 1 and Task 3.
- `_get_candidate_context` → `dict[str, str]` introduced in Task 2, consumed in Task 3 as `existing_concept_map`.
- `_extract_edges_pass(text, doc_concept_map, existing_concept_map)` — signature defined in Task 2, called in Task 3 with exact same parameter names.
- `_normalize_edge_endpoint(raw, id_to_name, name_to_id)` — defined in Task 2, called in Task 3.
- `id_to_name` and `name_to_id` built in Task 3's `index_note()` and passed to `_normalize_edge_endpoint` — consistent with Task 2's test which constructs them the same way.

**One known gap (intentional, not a bug):** `extract_from_text()` (the public method called by tests) still calls the old `_extract_edges_pass(text, new_nodes)` signature. After Task 2 replaces that method, `extract_from_text()` will break. **Fix:** also update `extract_from_text()` in Task 2 to use the new signature — or delete it since `index_note()` after Task 3 no longer calls it.

**Action:** Add a sub-step in Task 2 to update `extract_from_text()`:

> **Step 5b: Update `extract_from_text()` to use the new `_extract_edges_pass` signature**
>
> `extract_from_text()` (lines 441–468) calls `self._extract_edges_pass(text, valid_nodes)`. After Task 2 changes the signature, this breaks. Replace the call site:
>
> ```python
> # Pass 2: Link relationships & edges between nodes (Phase 4: receives id map)
> # Build a minimal doc_concept_map from the nodes extracted in this call.
> doc_concept_map = {n.name: (n.id if n.id else n.name) for n in valid_nodes}
> existing_concept_map = self._get_candidate_context(text)
> extracted_edges = self._extract_edges_pass(text, doc_concept_map, existing_concept_map)
> ```
>
> This keeps `extract_from_text()` functional for the two existing tests that use it directly.

---

**Plan complete and saved to `docs/superpowers/plans/2026-08-23-phase4-resolve-then-link.md`.**

Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints

Which approach?
