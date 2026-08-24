# Vocabulary Redesign: Two-Axis Node Typing and a Mathematical Relation Set

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single 9-valued `entity_type` enum with two orthogonal fields (`kind`, `role`) and extend the relation vocabulary from 7 to 12, so the graph stops collapsing to 76% `Concept` / 78.5% `DEPENDS_ON`.

**Architecture:** Node typing splits into `kind` (intrinsic — what sort of mathematical thing this is, required, no default) and `role` (the label the *document itself* applies to a statement — reported, never inferred, optional). Argument structure that used to be mis-encoded as node types stays where it already works: edges. Pass 2 additionally receives each concept's kind and role, so relation choice can be constrained by endpoint types, and every relation gets an explicit definition in the prompt rather than only `DEPENDS_ON`.

**Tech Stack:** Python 3.11, Pydantic v2, NetworkX, SQLite (`graph_store.py`), Gemini/Ollama via existing wrappers, vanilla JS + vis-network frontend, `unittest`.

**Spec:** [`docs/vocabulary-diagnosis.md`](../../vocabulary-diagnosis.md) — read it first; this plan argues from its V1–V5 findings.

## Global Constraints

- Test runner is **`python -m unittest`**, not pytest — pytest is not installed.
- Imports use container-style names: `graph.app.indexer`, `shared.config` — never `services.graph.app.indexer`. `import src` at the top of each test file puts `services/` on `sys.path`.
- **Baseline is branch `phase4-resolve-then-link`**, not `main`. Phase 7 deleted `services/*/main.py`, all `Dockerfile`s, and both `app/clients.py` files. Do not write code referencing them.
- `PREREQUISITE_FOR(A,B)` must stay canonicalized to `DEPENDS_ON(B,A)` via `_normalize_relation()`. Do not bypass it.
- `export_graph_json()` writes the node's kind under the JSON key **`type`** (not `kind`) for back-compat with `scripts/graph_health.py` and `src/server.py`'s `/api/graph`, which parse graph.json directly. See the CLAUDE.md invariant; Task 2 updates its wording.
- `.env` is required for any `import src`, including in tests.
- Most tests share real `.storage/`. **New SQLite-touching tests must follow `tests/test_graph_store.py`'s throwaway `db_path` pattern**, not the shared-state default.
- `scripts/` is gitignored. Two files there (`test_process2_graph.py`, `test_process4_hybrid_retrieval.py`) construct `GraphNode(entity_type=...)` and will break; they are local scratch, out of scope, and must not be committed.
- Re-extraction (Task 7) costs real LLM calls. Do not run it during Tasks 1–6.

---

## File Map

**Modified:**
- `services/graph/app/schema.py` — new `MathEntityKind` / `StatementRole` enums, extended `MathRelationType`, `GraphNode` fields + legacy coercion
- `services/graph/app/graph_store.py` — `upsert_node_attrs` signature, `load_graph` legacy mapping, `export_graph_json` output
- `services/graph/app/indexer.py` — both prompts, `_extract_edges_pass` signature, `_normalize_relation`, `index_note` node write, `_block_extraction`
- `services/retrieval/app/engine.py` — node-kind display in graph context
- `src/cli.py` — `graph-stats` counts, `graph-preview` output
- `static/app.js`, `static/index.html`, `static/style.css` — kind-based filters, detail panel, legend
- `tests/test_graph_indexer.py`, `tests/test_graph_store.py`
- `CLAUDE.md`, `plan.md`, `docs/vocabulary-diagnosis.md`

**Not modified:** `authority.py` (identity is orthogonal to typing), `vector/`, `ingestion/`, `vault/`.

---

### Task 1: Two-axis node typing in the schema

**Files:**
- Modify: `services/graph/app/schema.py`
- Test: `tests/test_graph_indexer.py`

**Interfaces:**
- Produces:
  - `MathEntityKind` — enum: `OBJECT`, `STATEMENT`, `DEFINITION`, `METHOD`, `FORMULA`, `PROOF`, `EXAMPLE`
  - `StatementRole` — enum: `AXIOM`, `THEOREM`, `LEMMA`, `COROLLARY`, `PROPOSITION`, `CONJECTURE`
  - `GraphNode.kind: MathEntityKind` (**required**, no default) and `GraphNode.role: Optional[StatementRole]` (default `None`)
  - `LEGACY_TYPE_MAP: dict[str, tuple[MathEntityKind, StatementRole | None]]`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_graph_indexer.py` (import `MathEntityKind`, `StatementRole` alongside the existing schema imports):

```python
class TestTwoAxisTyping(unittest.TestCase):
    def test_kind_is_required(self):
        """Omitting kind must raise, not silently default to a residual bucket."""
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            GraphNode(name="Wronskian")

    def test_role_defaults_to_none(self):
        n = GraphNode(name="Wronskian", kind=MathEntityKind.OBJECT)
        self.assertIsNone(n.role)

    def test_legacy_theorem_splits_into_kind_and_role(self):
        n = GraphNode(name="Schwarz's Theorem", entity_type="Theorem")
        self.assertEqual(n.kind, MathEntityKind.STATEMENT)
        self.assertEqual(n.role, StatementRole.THEOREM)

    def test_legacy_concept_becomes_object_with_no_role(self):
        n = GraphNode(name="Integrating Factor", entity_type="Concept")
        self.assertEqual(n.kind, MathEntityKind.OBJECT)
        self.assertIsNone(n.role)

    def test_legacy_lemma_splits_into_statement_and_lemma_role(self):
        n = GraphNode(name="Abel's Lemma", entity_type="Lemma")
        self.assertEqual(n.kind, MathEntityKind.STATEMENT)
        self.assertEqual(n.role, StatementRole.LEMMA)

    def test_explicit_kind_wins_over_legacy_entity_type(self):
        n = GraphNode(name="X", entity_type="Concept", kind=MathEntityKind.METHOD)
        self.assertEqual(n.kind, MathEntityKind.METHOD)
```

- [ ] **Step 2: Run tests to verify they fail**

```
python -m unittest tests.test_graph_indexer.TestTwoAxisTyping -v
```
Expected: FAIL — `MathEntityKind` cannot be imported.

- [ ] **Step 3: Add the enums**

In `services/graph/app/schema.py`, directly below the existing `MathEntityType` class (leave `MathEntityType` in place — Task 2 still needs it for legacy reads):

```python
class MathEntityKind(str, Enum):
    """What sort of mathematical thing a node is — intrinsic, always
    determinable from the text that introduces it. Axis 1 of 2; see
    docs/vocabulary-diagnosis.md V2 for why this is separate from role.
    """
    OBJECT = "Object"          # a construct or property: Wronskian, Linear Independence
    STATEMENT = "Statement"    # a proposition asserted to hold
    DEFINITION = "Definition"  # assigns meaning to a term
    METHOD = "Method"          # a procedure: Variation of Parameters
    FORMULA = "Formula"        # a specific equation: Abel's Identity
    PROOF = "Proof"            # an argument establishing a statement
    EXAMPLE = "Example"        # a concrete instance or model


class StatementRole(str, Enum):
    """The label the source document applies to a statement.

    REPORTED, NEVER INFERRED. Whether a result is a lemma or a theorem is a
    property of how an argument uses it, not of the statement — so this is
    only set when the text says so (a heading "Lemma 3.1", or a name like
    "Abel's Lemma"). Otherwise it stays None and the argument structure
    lives in edges (COROLLARY_OF, USES_IN_PROOF), which is where it already
    worked. Only meaningful when kind == STATEMENT.
    """
    AXIOM = "Axiom"
    THEOREM = "Theorem"
    LEMMA = "Lemma"
    COROLLARY = "Corollary"
    PROPOSITION = "Proposition"
    CONJECTURE = "Conjecture"


# Maps the retired single-axis MathEntityType onto (kind, role). Used by the
# GraphNode validator below and by graph_store.load_graph for nodes written
# before this split.
LEGACY_TYPE_MAP: dict[str, tuple[MathEntityKind, "StatementRole | None"]] = {
    "Concept":    (MathEntityKind.OBJECT, None),
    "Definition": (MathEntityKind.DEFINITION, None),
    "Formula":    (MathEntityKind.FORMULA, None),
    "Proof":      (MathEntityKind.PROOF, None),
    "Example":    (MathEntityKind.EXAMPLE, None),
    "Theorem":    (MathEntityKind.STATEMENT, StatementRole.THEOREM),
    "Lemma":      (MathEntityKind.STATEMENT, StatementRole.LEMMA),
    "Corollary":  (MathEntityKind.STATEMENT, StatementRole.COROLLARY),
    "Axiom":      (MathEntityKind.STATEMENT, StatementRole.AXIOM),
}
```

- [ ] **Step 4: Replace `GraphNode`'s type field**

In `GraphNode`, delete the `entity_type` field line and add `kind`/`role` plus a pre-validator:

```python
class GraphNode(BaseModel):
    id: str = Field("", description="Canonical ID of the entity")
    name: str = Field(..., description="Display name of mathematical entity")
    kind: MathEntityKind = Field(..., description="What sort of mathematical thing this is (required)")
    role: Optional[StatementRole] = Field(None, description="Label the document applies to a statement; None unless stated")
    taxonomy: ConceptTaxonomy = Field(default_factory=ConceptTaxonomy, description="SKOS 3-tier domain taxonomy")
    aliases: List[str] = Field(default_factory=list, description="Alternative names or symbols for entity")
    description: str = Field("", description="Short formal definition or summary")
    provenance: List[Provenance] = Field(default_factory=list, description="Source provenance locations")

    @model_validator(mode="before")
    @classmethod
    def _coerce_legacy_entity_type(cls, data):
        """Accepts pre-split `entity_type` input and splits it onto (kind, role).

        Keeps old graph.json rows, old fixtures, and any LLM output that
        still emits the retired field loadable. An explicit `kind` always
        wins over a legacy `entity_type`.
        """
        if not isinstance(data, dict):
            return data
        legacy = data.pop("entity_type", None)
        if legacy is not None and not data.get("kind"):
            key = getattr(legacy, "value", legacy)
            kind, role = LEGACY_TYPE_MAP.get(str(key), (MathEntityKind.OBJECT, None))
            data["kind"] = kind
            if role is not None and not data.get("role"):
                data["role"] = role
        return data
```

- [ ] **Step 5: Run the tests to verify they pass**

```
python -m unittest tests.test_graph_indexer.TestTwoAxisTyping -v
```
Expected: 6 PASS

- [ ] **Step 6: Fix the two existing schema tests that construct nodes the old way**

`tests/test_graph_indexer.py` lines 11–12 and 24–25 pass `entity_type=MathEntityType.*`. The validator keeps these working, but they should assert the new axes. Replace those four constructions:

```python
        node1 = GraphNode(name="Eigenvalue", kind=MathEntityKind.OBJECT, description="Scalar lambda")
        node2 = GraphNode(name="Spectral Theorem", kind=MathEntityKind.STATEMENT,
                          role=StatementRole.THEOREM, description="Symmetric matrix breakdown")
```

and

```python
        node1 = GraphNode(name="Vector Space", kind=MathEntityKind.DEFINITION, description="Set with vector addition")
        node2 = GraphNode(name="Linear Independence", kind=MathEntityKind.OBJECT, description="Vectors without linear combination")
```

Line 31 does `indexer.graph.add_node(n.name, entity_type=n.entity_type.value, ...)` — change to:

```python
            indexer.graph.add_node(n.name, kind=n.kind.value, role=(n.role.value if n.role else None),
                                   description=n.description)
```

- [ ] **Step 7: Run the full suite**

```
python -m unittest discover -s tests -v
```
Expected: `test_graph_indexer` fully passes. Failures in `test_graph_store` are expected here and fixed in Task 2 — note which, do not fix them yet.

- [ ] **Step 8: Commit**

```bash
git add services/graph/app/schema.py tests/test_graph_indexer.py
git commit -m "feat: split node typing into kind + role axes (vocabulary-diagnosis V2)"
```

---

### Task 2: Persist and load both axes

**Files:**
- Modify: `services/graph/app/graph_store.py`
- Test: `tests/test_graph_store.py`

**Interfaces:**
- Consumes (Task 1): `MathEntityKind`, `StatementRole`, `LEGACY_TYPE_MAP`
- Produces:
  - `upsert_node_attrs(conn, concept_id, *, label, kind, role=None, taxonomy, description, provenance, aliases)` — `entity_type=` parameter removed
  - `load_graph()` sets node attrs `kind` and `role`, mapping legacy `entity_type` rows through `LEGACY_TYPE_MAP`
  - `export_graph_json()` writes `"type"` (the kind) and `"role"`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_graph_store.py`, following its existing throwaway-`db_path` pattern:

```python
    def test_round_trip_preserves_kind_and_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "concepts.db"
            graph_store.init_db(db_path=db)
            with graph_store.connect(db_path=db) as conn:
                conn.execute("INSERT OR IGNORE INTO concepts (id, label) VALUES (?, ?)", ("CUST_t", "Schwarz"))
                graph_store.upsert_node_attrs(
                    conn, "CUST_t", label="Schwarz's Theorem",
                    kind="Statement", role="Theorem",
                    taxonomy={}, description="", provenance=[], aliases=[],
                )
            G = graph_store.load_graph(db_path=db)
            self.assertEqual(G.nodes["CUST_t"]["kind"], "Statement")
            self.assertEqual(G.nodes["CUST_t"]["role"], "Theorem")

    def test_legacy_entity_type_row_loads_as_kind_and_role(self):
        """A node written before the split must still load, mapped onto both axes."""
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "concepts.db"
            graph_store.init_db(db_path=db)
            with graph_store.connect(db_path=db) as conn:
                conn.execute("INSERT OR IGNORE INTO concepts (id, label) VALUES (?, ?)", ("CUST_o", "Old"))
                conn.execute(
                    "UPDATE concepts SET node_attrs_json = ? WHERE id = ?",
                    (json.dumps({"label": "Abel's Lemma", "entity_type": "Lemma"}), "CUST_o"),
                )
            G = graph_store.load_graph(db_path=db)
            self.assertEqual(G.nodes["CUST_o"]["kind"], "Statement")
            self.assertEqual(G.nodes["CUST_o"]["role"], "Lemma")

    def test_export_writes_kind_under_type_key_and_role_alongside(self):
        import networkx as nx
        with tempfile.TemporaryDirectory() as tmp:
            G = nx.DiGraph()
            G.add_node("CUST_t", label="Schwarz's Theorem", kind="Statement", role="Theorem")
            out = Path(tmp) / "graph.json"
            graph_store.export_graph_json(G, out)
            data = json.loads(out.read_text(encoding="utf-8"))
            node = data["nodes"][0]
            self.assertEqual(node["type"], "Statement")   # back-compat key
            self.assertEqual(node["role"], "Theorem")
```

Ensure `json`, `tempfile`, and `Path` are imported at the top of the test module.

- [ ] **Step 2: Run tests to verify they fail**

```
python -m unittest tests.test_graph_store -v
```
Expected: the three new tests FAIL (`upsert_node_attrs` rejects `kind=`), plus the pre-existing `entity_type` assertion at line 63.

- [ ] **Step 3: Change `upsert_node_attrs`**

Replace the `entity_type` parameter and its use in the attrs dict:

```python
def upsert_node_attrs(conn, concept_id: str, *, label: str,
                      kind: str = "Object", role: str | None = None,
                      taxonomy: dict | None = None, description: str = "",
                      provenance: list | None = None, aliases: list | None = None) -> None:
    attrs = {
        "label": label,
        "kind": kind,
        "role": role,
        "taxonomy": taxonomy or {},
        "description": description,
        "provenance": provenance or [],
        "aliases": aliases or [],
    }
    conn.execute(
        "UPDATE concepts SET node_attrs_json = ? WHERE id = ?",
        (json.dumps(attrs, ensure_ascii=False), concept_id),
    )
```

- [ ] **Step 4: Map legacy rows in `load_graph`**

Inside `load_graph`'s row loop, after `attrs = json.loads(node_attrs_json)`, before the node is added:

```python
                # Nodes written before the kind/role split carry entity_type.
                # Map them onto both axes so an un-re-extracted graph loads.
                if "kind" not in attrs and "entity_type" in attrs:
                    from .schema import LEGACY_TYPE_MAP, MathEntityKind
                    kind, role = LEGACY_TYPE_MAP.get(
                        str(attrs.get("entity_type")), (MathEntityKind.OBJECT, None)
                    )
                    attrs["kind"] = kind.value
                    attrs["role"] = role.value if role else None
                attrs.setdefault("kind", "Object")
                attrs.setdefault("role", None)
```

- [ ] **Step 5: Update `export_graph_json`**

In the node dict comprehension, replace the `"type"` line and add `"role"`:

```python
                # `type` carries the KIND, not the retired entity_type. The key
                # name is kept because scripts/graph_health.py and
                # src/server.py's /api/graph parse graph.json directly.
                "type": graph.nodes[n].get("kind", "Object"),
                "role": graph.nodes[n].get("role"),
```

- [ ] **Step 6: Fix the pre-existing assertion**

`tests/test_graph_store.py` line ~42-63 writes `entity_type="Concept"` / `"Theorem"` and asserts `entity_type` on load. Change the two writes to `kind="Object"` and `kind="Statement", role="Theorem"`, and the assertion to:

```python
        self.assertEqual(G.nodes["CUST_b"]["kind"], "Statement")
```

- [ ] **Step 7: Run the tests**

```
python -m unittest tests.test_graph_store -v
```
Expected: all PASS

- [ ] **Step 8: Update the CLAUDE.md invariant**

The invariant currently reads "**`export_graph_json()` (graph_store.py) writes `entity_type` as `type`**". Replace that bullet's first sentence with:

```markdown
- **`export_graph_json()` (graph_store.py) writes the node's `kind` under the JSON key
  `type`**, with `role` alongside it — a holdover name from when `entity_type` was one
  field, kept because `scripts/graph_health.py` and `src/server.py`'s `/api/graph` both
  parse graph.json directly and expect that key.
```

- [ ] **Step 9: Commit**

```bash
git add services/graph/app/graph_store.py tests/test_graph_store.py CLAUDE.md
git commit -m "feat: persist kind/role, map legacy entity_type rows on load"
```

---

### Task 3: Pass 1 — kind criteria and reported-role rule

**Files:**
- Modify: `services/graph/app/indexer.py` (`PASS1_NODE_PROMPT`, `_block_extraction`, `index_note`'s node write)
- Test: `tests/test_graph_indexer.py`

**Interfaces:**
- Consumes (Task 1): `MathEntityKind`, `StatementRole`
- Consumes (Task 2): `upsert_node_attrs(..., kind=, role=)`
- Produces: graph nodes carrying `kind` and `role` attributes instead of `entity_type`

- [ ] **Step 1: Write the failing test**

```python
    def test_index_note_writes_kind_attribute(self):
        """Block-extracted nodes carry kind, not entity_type."""
        import tempfile, os
        note = "## Wronskian\nThe Wronskian is a determinant used to test linear independence.\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", dir=self.indexer.vault_path,
                                         delete=False, encoding="utf-8") as f:
            f.write(note)
            tmp_path = f.name
        try:
            self.indexer.index_note(Path(tmp_path), use_llm=False)
            attrs = [d for _, d in self.indexer.graph.nodes(data=True)]
            self.assertTrue(any("kind" in a for a in attrs), "expected at least one node with a kind attr")
            self.assertFalse(any("entity_type" in a for a in attrs), "entity_type must be gone from the write path")
        finally:
            os.unlink(tmp_path)
```

Add it to the existing `TestPhase4` class (it already has `self.indexer` and vault-path setup).

- [ ] **Step 2: Run it to verify it fails**

```
python -m unittest tests.test_graph_indexer.TestPhase4.test_index_note_writes_kind_attribute -v
```
Expected: FAIL — nodes still carry `entity_type`.

- [ ] **Step 3: Rewrite `PASS1_NODE_PROMPT`**

Replace the whole constant:

```python
PASS1_NODE_PROMPT = """\
You are an expert mathematical entity extractor.
TASK: Extract formal mathematical entities from the text, classify each on TWO
independent axes, and assign a 3-tier SKOS taxonomy.

AXIS 1 — kind (REQUIRED, pick exactly one; this is what the thing IS):
  Object     — a mathematical object, construct, or property (e.g. Wronskian, Integrating Factor, Linear Independence)
  Statement  — a proposition asserted to hold (e.g. Schwarz's Theorem, Criterion for Exactness)
  Definition — text that assigns meaning to a term
  Method     — a procedure or solution technique (e.g. Variation of Parameters, Undetermined Coefficients)
  Formula    — a specific equation or expression (e.g. Abel's Identity)
  Proof      — an argument establishing a statement
  Example    — a concrete instance or model (e.g. a bungee-jumping model)

AXIS 2 — role (OPTIONAL, only when kind is Statement):
  Axiom | Theorem | Lemma | Corollary | Proposition | Conjecture

  CRITICAL: role is REPORTED, NOT INFERRED. Set it ONLY when the text itself
  applies that label — a heading such as "Lemma 3.1", or a name such as
  "Abel's Lemma" or "Picard's Theorem". If the text merely states a result
  without labelling it, OMIT role entirely. Do NOT reason about whether
  something "acts like" a lemma; relationships between results are captured
  as edges, not as this field.

STRICT RULES:
1. DO NOT extract structural terms (e.g. 'Exercise 1', 'Problem', 'Solution', 'Hint', 'Conclusion', 'Page 1', 'Lecture notes').
2. Extract the formal mathematical entity name, properly capitalised.
3. Every node MUST have a `kind`. Do not default to Object when another kind fits — a named result is a Statement, a solution technique is a Method.
4. Each node MUST have a formal 1-2 sentence description.
5. Assign domain taxonomy (domain, subdomain, topic).

TEXT:
{text}
"""
```

- [ ] **Step 4: Update the Ollama JSON hint**

`_extract_nodes_pass`'s Ollama fallback appends a literal JSON shape containing
`"entity_type": "Theorem|Definition|Concept|Formula|Proof|Lemma"`. Replace that fragment with:

```python
                '{"nodes": [{"name": "Concept Name", "kind": "Object|Statement|Definition|Method|Formula|Proof|Example", '
                '"role": "Theorem|Lemma|Corollary|Axiom|Proposition|Conjecture or omit", '
                '"description": "formal definition", "taxonomy": {"domain": "...", "subdomain": "...", "topic": "..."}}]}'
```

- [ ] **Step 5: Update `_block_extraction`**

Its inner `_add_node(name, etype, desc="")` builds `GraphNode(..., entity_type=etype)`. Change the signature and construction to carry a kind:

```python
        def _add_node(name: str, kind: str, desc: str = ""):
            nodes.append(GraphNode(
                name=name,
                kind=kind,
                description=desc,
                taxonomy=ConceptTaxonomy(domain=course_domain, subdomain="Course Notes", topic=name),
            ))
```

Update every `_add_node(...)` call site in that method to pass a `MathEntityKind` value
(`MathEntityKind.OBJECT.value` for the generic wikilink/heading case) instead of the old
`"Concept"`/`"Theorem"` strings.

- [ ] **Step 6: Update `index_note`'s node write**

Replace the `etype = ...` block and the two write sites:

```python
                kind = node.kind.value if hasattr(node.kind, "value") else str(node.kind)
                role = node.role.value if getattr(node, "role", None) is not None else None
```

then in `self.graph.add_node(...)` replace `entity_type=etype` with `kind=kind, role=role`,
in the update branch leave taxonomy/provenance handling as-is, and in the
`graph_store.upsert_node_attrs(...)` call replace
`entity_type=node_data.get("entity_type", "Concept")` with:

```python
                    kind=node_data.get("kind", "Object"),
                    role=node_data.get("role"),
```

- [ ] **Step 7: Run the test**

```
python -m unittest tests.test_graph_indexer.TestPhase4.test_index_note_writes_kind_attribute -v
```
Expected: PASS

- [ ] **Step 8: Run the full suite**

```
python -m unittest discover -s tests -v
```
Expected: all pass.

- [ ] **Step 9: Commit**

```bash
git add services/graph/app/indexer.py tests/test_graph_indexer.py
git commit -m "feat: Pass 1 classifies on kind/role axes with reported-role rule (V1, V2)"
```

---

### Task 4: Pass 2 — typed dictionary and a mathematical relation set

**Files:**
- Modify: `services/graph/app/schema.py` (`MathRelationType`), `services/graph/app/indexer.py` (`PASS2_EDGE_PROMPT`, `_extract_edges_pass`, `_normalize_relation`, `index_note`'s edge loop)
- Test: `tests/test_graph_indexer.py`

**Interfaces:**
- Consumes (Task 3): nodes carrying `kind`/`role`
- Produces:
  - `MathRelationType` extended with `HAS_HYPOTHESIS`, `USES_IN_PROOF`, `GENERALIZES`, `SPECIAL_CASE_OF`, `EQUIVALENT_TO`, `CHARACTERIZES`, `INSTANCE_OF`; `USES_AXIOM` removed
  - `SYMMETRIC_RELATIONS: frozenset[str]` — currently `{"EQUIVALENT_TO"}`
  - `_normalize_relation(source, target, relation) -> tuple[str, str, str]` — additionally maps legacy `USES_LEMMA` to `USES_IN_PROOF` and orders symmetric relations by id
  - `_extract_edges_pass(text, doc_concept_map, existing_concept_map, node_types)` — new fourth parameter `node_types: dict[str, dict]` mapping concept id to `{"kind": str, "role": str | None}`

- [ ] **Step 1: Write the failing tests**

```python
class TestRelationVocabulary(unittest.TestCase):
    def setUp(self):
        self.indexer = MathGraphIndexer()

    def test_legacy_uses_lemma_maps_to_uses_in_proof(self):
        s, t, r = _normalize_relation("A", "B", "USES_LEMMA")
        self.assertEqual((s, t, r), ("A", "B", "USES_IN_PROOF"))

    def test_prerequisite_for_still_flips_to_depends_on(self):
        s, t, r = _normalize_relation("A", "B", "PREREQUISITE_FOR")
        self.assertEqual((s, t, r), ("B", "A", "DEPENDS_ON"))

    def test_symmetric_relation_is_stored_in_one_direction(self):
        """EQUIVALENT_TO(B,A) and EQUIVALENT_TO(A,B) must normalize identically,
        otherwise the pair manufactures a 2-cycle (vocabulary-diagnosis V5)."""
        forward = _normalize_relation("A", "B", "EQUIVALENT_TO")
        reverse = _normalize_relation("B", "A", "EQUIVALENT_TO")
        self.assertEqual(forward, reverse)

    def test_new_relations_exist_and_uses_axiom_is_gone(self):
        names = {r.value for r in MathRelationType}
        for expected in ("HAS_HYPOTHESIS", "USES_IN_PROOF", "GENERALIZES",
                         "SPECIAL_CASE_OF", "EQUIVALENT_TO", "CHARACTERIZES", "INSTANCE_OF"):
            self.assertIn(expected, names)
        self.assertNotIn("USES_AXIOM", names)
```

Import `_normalize_relation` and `MathRelationType` in the test module.

- [ ] **Step 2: Run to verify failure**

```
python -m unittest tests.test_graph_indexer.TestRelationVocabulary -v
```
Expected: FAIL — new members missing, `USES_LEMMA` unmapped.

- [ ] **Step 3: Extend `MathRelationType`**

Replace the class in `services/graph/app/schema.py`:

```python
class MathRelationType(str, Enum):
    DEPENDS_ON = "DEPENDS_ON"            # A requires understanding B
    HAS_HYPOTHESIS = "HAS_HYPOTHESIS"    # statement A holds only under condition B
    USES_DEFINITION = "USES_DEFINITION"  # A invokes definition B
    USES_IN_PROOF = "USES_IN_PROOF"      # A's proof relies on result B
    PROVES = "PROVES"                    # A establishes B
    COROLLARY_OF = "COROLLARY_OF"        # A follows easily from B
    GENERALIZES = "GENERALIZES"          # A is a strictly more general form of B
    SPECIAL_CASE_OF = "SPECIAL_CASE_OF"  # A is B under added constraints
    EQUIVALENT_TO = "EQUIVALENT_TO"      # A iff B — symmetric, see SYMMETRIC_RELATIONS
    CHARACTERIZES = "CHARACTERIZES"      # A is an iff-criterion for property B
    INSTANCE_OF = "INSTANCE_OF"          # A is a concrete example or model of B
    PREREQUISITE_FOR = "PREREQUISITE_FOR"  # inverse of DEPENDS_ON; canonicalized away on write


# Relations asserting a mutual fact. Stored in exactly one direction (ordered
# by endpoint id) so that A~B and B~A cannot both persist and form a 2-cycle.
SYMMETRIC_RELATIONS = frozenset({"EQUIVALENT_TO"})
```

- [ ] **Step 4: Extend `_normalize_relation`**

In `services/graph/app/indexer.py`, replace the function body (keep the existing docstring's `PREREQUISITE_FOR` explanation and append to it):

```python
def _normalize_relation(source: str, target: str, relation: str) -> tuple[str, str, str]:
    """Canonicalizes relation direction and retired names.

    PREREQUISITE_FOR(A, B) and DEPENDS_ON(B, A) assert the same fact; storing
    both directions between one pair creates an artificial cycle that breaks
    hierarchical layout. DEPENDS_ON is the only stored form.

    USES_LEMMA is the retired name for USES_IN_PROOF — it was in practice
    used for any auxiliary result, not only lemmas (docs/vocabulary-diagnosis.md
    V3), so the rename is also a correction.

    Symmetric relations (SYMMETRIC_RELATIONS) are stored with endpoints
    ordered by id, so an LLM emitting both directions yields one edge, not a
    2-cycle.
    """
    if relation == "PREREQUISITE_FOR":
        return target, source, "DEPENDS_ON"
    if relation == "USES_LEMMA":
        relation = "USES_IN_PROOF"
    if relation in SYMMETRIC_RELATIONS and source > target:
        return target, source, relation
    return source, target, relation
```

Add `SYMMETRIC_RELATIONS` to the `from .schema import (...)` block at the top of the module.

- [ ] **Step 5: Run the relation tests**

```
python -m unittest tests.test_graph_indexer.TestRelationVocabulary -v
```
Expected: 4 PASS

- [ ] **Step 6: Rewrite `PASS2_EDGE_PROMPT` with per-relation definitions**

```python
PASS2_EDGE_PROMPT = """\
You are an expert mathematical relationship linker.
TASK: Establish directional relationships between the entities below, using ONLY their IDs.

ENTITY DICTIONARY (id -> name, kind, role):
{concept_id_map}

NEW ENTITY IDS FROM THIS NOTE (focus edges on these):
{new_concept_ids}

EXISTING KNOWLEDGE BASE IDS (available link targets):
{existing_concept_ids}

RELATION TYPES — pick the most specific one that applies. Do NOT fall back to
DEPENDS_ON when a precise relation fits:

  DEPENDS_ON(A, B)       A requires understanding B first. B is more foundational.
                         Use only when no more specific relation below applies.
  HAS_HYPOTHESIS(A, B)   Statement A holds only under condition B.
                         e.g. Picard's Theorem HAS_HYPOTHESIS Lipschitz Condition
  USES_DEFINITION(A, B)  A invokes definition B.
  USES_IN_PROOF(A, B)    A's proof relies on result B.
  PROVES(A, B)           A is an argument establishing statement B.
                         A should be a Proof and B a Statement.
  COROLLARY_OF(A, B)     A follows easily from B.
  GENERALIZES(A, B)      A is a strictly more general form of B.
  SPECIAL_CASE_OF(A, B)  A is B with additional constraints.
  EQUIVALENT_TO(A, B)    A and B are logically equivalent. Emit ONCE, in either order.
  CHARACTERIZES(A, B)    A is an if-and-only-if criterion for property B.
                         e.g. Wronskian Criterion CHARACTERIZES Linear Dependence
  INSTANCE_OF(A, B)      A is a concrete example or model of B.

STRICT RULES:
1. Use ONLY IDs from the ENTITY DICTIONARY as source and target. Never invent an ID.
2. Respect the kinds: do not emit PROVES targeting a Definition; do not emit
   USES_IN_PROOF targeting an Object that is not a result.
3. Never emit an inverse "is a prerequisite for" edge — express it as DEPENDS_ON.
4. Do NOT emit an edge in both directions between the same pair. If the
   relationship is mutual, use EQUIVALENT_TO once.
5. Include the supporting sentence from the text in the description field.

TEXT:
{text}
"""
```

- [ ] **Step 7: Pass node types into `_extract_edges_pass`**

Change the signature and the dictionary it serialises:

```python
    def _extract_edges_pass(
        self,
        text: str,
        doc_concept_map: dict[str, str],       # surface name -> canonical id
        existing_concept_map: dict[str, str],  # canonical id -> label
        node_types: dict[str, dict],           # canonical id -> {"kind":…, "role":…}
    ) -> list[GraphEdge]:
        """Executes Pass 2 via Gemini or Ollama.

        `node_types` is what lets the LLM pick type-appropriate relations —
        without it, Pass 2 was type-blind and emitted USES_LEMMA at theorems
        and PROVES at definitions (docs/vocabulary-diagnosis.md V3).
        """
        if not doc_concept_map:
            return []

        id_to_name: dict[str, str] = {v: k for k, v in doc_concept_map.items()}
        id_to_name.update(existing_concept_map)

        entity_dict = {
            cid: {
                "name": name,
                "kind": node_types.get(cid, {}).get("kind", "Object"),
                "role": node_types.get(cid, {}).get("role"),
            }
            for cid, name in id_to_name.items()
        }

        concept_id_map_json = json.dumps(entity_dict, ensure_ascii=False)
        new_concept_ids_json = json.dumps(list(doc_concept_map.values()))
        existing_concept_ids_json = json.dumps(list(existing_concept_map.keys()))
```

The rest of the method body (Gemini loop, Ollama fallback) is unchanged except that the
Ollama JSON hint's relation list must become:

```python
                '{"edges": [{"source": "id", "target": "id", "relation": "DEPENDS_ON|HAS_HYPOTHESIS|USES_DEFINITION|USES_IN_PROOF|PROVES|COROLLARY_OF|GENERALIZES|SPECIAL_CASE_OF|EQUIVALENT_TO|CHARACTERIZES|INSTANCE_OF", "description": "evidence quote"}]}'
```

- [ ] **Step 8: Update both call sites**

In `index_note`, build the type map from the graph and pass it:

```python
            node_types = {
                nid: {
                    "kind": self.graph.nodes[nid].get("kind", "Object"),
                    "role": self.graph.nodes[nid].get("role"),
                }
                for nid in set(doc_concept_map.values()) | set(existing_concept_map)
                if nid in self.graph
            }
            raw_edges = self._extract_edges_pass(content, doc_concept_map, existing_concept_map, node_types)
```

In `extract_from_text`, which has no graph-backed types yet, pass the kinds off the
extracted nodes:

```python
        doc_concept_map = {n.name: (n.id if n.id else n.name) for n in valid_nodes}
        existing_concept_map = self._get_candidate_context(text)
        node_types = {
            (n.id if n.id else n.name): {
                "kind": n.kind.value if hasattr(n.kind, "value") else str(n.kind),
                "role": n.role.value if getattr(n, "role", None) is not None else None,
            }
            for n in valid_nodes
        }
        extracted_edges = self._extract_edges_pass(text, doc_concept_map, existing_concept_map, node_types)
```

- [ ] **Step 9: Run the full suite**

```
python -m unittest discover -s tests -v
```
Expected: all pass.

- [ ] **Step 10: Commit**

```bash
git add services/graph/app/schema.py services/graph/app/indexer.py tests/test_graph_indexer.py
git commit -m "feat: typed Pass 2 dictionary + 11-relation math vocabulary (V3, V4, V5)"
```

---

### Task 5: Update CLI and retrieval consumers

**Files:**
- Modify: `src/cli.py` (`graph-stats`, `graph-preview`), `services/retrieval/app/engine.py`
- Test: manual CLI verification (these are display paths with no unit tests today)

**Interfaces:**
- Consumes (Tasks 1–4): node attrs `kind`/`role`

- [ ] **Step 1: Update `graph-stats`**

It counts `data.get("entity_type", "Concept")` into `types_count`. Replace with a kind count
plus a role count, and emit both under `--json`:

```python
            for _, data in G.nodes(data=True):
                k = data.get("kind", "Object")
                kinds_count[k] = kinds_count.get(k, 0) + 1
                r = data.get("role")
                if r:
                    roles_count[r] = roles_count.get(r, 0) + 1
```

Initialise `kinds_count: dict[str, int] = {}` and `roles_count: dict[str, int] = {}` where
`types_count` was declared. In the `--json` payload replace `"entity_types": types_count`
with `"kinds": kinds_count, "roles": roles_count`. In the Rich table replace the
`"Entity Types"` row with two rows, `"Kinds"` and `"Roles"`, formatted the same way.

**The `--json` shape is the `/comeback-helper` skill's contract** — CLAUDE.md requires that a
verb's output-shape change updates the skill in the same commit. `SKILL.md` does not name the
`entity_types` key, but line ~136 states an invariant that this work invalidates:

> **`graph.json` writes `entity_type` as `type`.** Anything reading the file directly must
> expect `type`.

Replace those two lines with:

```markdown
- **`graph.json` writes the node's `kind` under the key `type`,** with `role` alongside.
  Anything reading the file directly must expect `type` (kind) and `role`.
```

- [ ] **Step 2: Update `graph-preview`**

Its node dicts emit `"entity_type": str(getattr(n.entity_type, "value", n.entity_type))`.
Replace with:

```python
                        "kind": str(getattr(n.kind, "value", n.kind)),
                        "role": (str(getattr(n.role, "value", n.role)) if n.role else None),
```

- [ ] **Step 3: Update the retrieval context formatter**

`services/retrieval/app/engine.py`'s `retrieve_context` reads
`node.get("entity_type", "Concept")` when formatting the neighbourhood block. Replace with:

```python
                        node_kind = node.get("kind", "Object")
                        node_role = node.get("role")
                        type_label = f"{node_role or node_kind}"
```

and use `type_label` in the `f"• [{type_label}] {label}"` line, so a theorem reads
`[Theorem]` and a plain object reads `[Object]`.

- [ ] **Step 4: Verify the CLI runs**

```
python -m src.cli graph-stats --json
```
Expected: one JSON object containing `"kinds"` and `"roles"` keys, no `entity_types`.

```
python -m unittest discover -s tests
```
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add src/cli.py services/retrieval/app/engine.py .claude/skills/comeback-helper/SKILL.md
git commit -m "refactor: CLI and retrieval read kind/role instead of entity_type"
```

---

### Task 6: Frontend — kind filters, role display, legend

**Files:**
- Modify: `static/index.html`, `static/app.js`, `static/style.css`

**Interfaces:**
- Consumes (Task 2): graph.json nodes with `type` (= kind) and `role`

- [ ] **Step 1: Replace the type filter chips**

In `static/index.html`, the six `.graph-type-filter` checkboxes have values
`Note`/`Concept`/`Theorem`/`Definition`/`Formula`/`Proof`. Replace that whole
`.filter-group` block's checkboxes with the seven kinds:

```html
                        <label class="chip-check"><input type="checkbox" value="Object" checked class="graph-type-filter"><span class="chip">🔵 Objects</span></label>
                        <label class="chip-check"><input type="checkbox" value="Statement" checked class="graph-type-filter"><span class="chip">📐 Statements</span></label>
                        <label class="chip-check"><input type="checkbox" value="Definition" checked class="graph-type-filter"><span class="chip">📖 Definitions</span></label>
                        <label class="chip-check"><input type="checkbox" value="Method" checked class="graph-type-filter"><span class="chip">🛠️ Methods</span></label>
                        <label class="chip-check"><input type="checkbox" value="Formula" checked class="graph-type-filter"><span class="chip">🔣 Formulas</span></label>
                        <label class="chip-check"><input type="checkbox" value="Proof" checked class="graph-type-filter"><span class="chip">✏️ Proofs</span></label>
                        <label class="chip-check"><input type="checkbox" value="Example" checked class="graph-type-filter"><span class="chip">💡 Examples</span></label>
```

- [ ] **Step 2: Update the five `n.type` read sites in `static/app.js`**

Lines ~487, 552, 566, 848, 899, 917 all read `n.type || n.entity_type || 'Concept'`.
Replace each with `n.type || 'Object'`, and the filter predicate at ~552 with:

```javascript
            if (!activeTypes.has(n.type || 'Object')) return false;
```

- [ ] **Step 3: Show role in the node detail panel**

In `showNodeDetail`, replace the `role` derivation and the type chip with kind + role:

```javascript
        const kind = n.type || 'Object';
        const role = n.role || null;
        const kindColor = KIND_COLORS[kind] || '#94a3b8';
        ...
        html += `<span class="graph-detail-type" style="background:${kindColor}22; color:${kindColor};">${escapeHtml(kind)}</span>`;
        if (role) {
            html += `<span class="graph-detail-type" style="background:#f59e0b22; color:#f59e0b; margin-left:6px;">${escapeHtml(role)}</span>`;
        }
```

Replace the `ROLE_BORDER_COLORS` constant with a kind-keyed one:

```javascript
    const KIND_COLORS = {
        'Object':     '#94a3b8',
        'Statement':  '#f59e0b',
        'Definition': '#10b981',
        'Method':     '#8b5cf6',
        'Formula':    '#06b6d4',
        'Proof':      '#ec4899',
        'Example':    '#818cf8',
    };
```

- [ ] **Step 4: Update the legend text**

In `static/index.html`, the second `.legend-group` reads "Concept type — click any node to
see it". Change to "Kind & role — click any node to see them".

- [ ] **Step 5: Bump the cache-busting version**

`static/index.html` currently loads `style.css?v=3` and `app.js?v=3`. Bump both to `v=4`,
otherwise browsers keep the old bundle and the filters silently fail.

- [ ] **Step 6: Verify**

```
node --check static/app.js
```
Expected: no output (valid).

Start the server, hard-refresh the Knowledge Graph tab, and confirm: seven filter chips
present, toggling one hides those nodes, clicking a node shows a kind chip (and a role chip
where the document labelled one).

```
python -m src.server
```

- [ ] **Step 7: Commit**

```bash
git add static/index.html static/app.js static/style.css
git commit -m "feat: frontend filters and detail panel use kind/role"
```

---

### Task 7: Re-extract the vault and measure the result

**Files:**
- Modify: `docs/vocabulary-diagnosis.md` (results section), `plan.md`, `CLAUDE.md`

**Interfaces:**
- Consumes: everything from Tasks 1–6

**This task spends LLM budget** — two Gemini passes over 13 notes. Do not run it until
Tasks 1–6 are committed and the suite is green.

- [ ] **Step 1: Back up the current graph**

```bash
cp .storage/graph.json .storage/graph.json.pre-vocabulary.bak
cp .storage/concepts.db .storage/concepts.db.pre-vocabulary.bak
```

- [ ] **Step 2: Record the before-numbers**

```bash
python -m src.cli graph-stats --json > /tmp/before.json
cat /tmp/before.json
```
Expected: `kinds` dominated by `Object` (the legacy `Concept` mapping), no roles.

- [ ] **Step 3: Clear graph structure, keeping identity**

`clear_graph()` deliberately preserves the `concepts`/`aliases` identity tables and clears
only structure — so canonical ids survive and re-extraction will not re-coin duplicates.

```bash
python -c "import src; from src.wiring import build_indexer; build_indexer().clear_graph()"
```

- [ ] **Step 4: Re-extract every note with the LLM**

`build_or_update_index` does not clear first, which is why Step 3 exists; `force=True` makes
it re-index all notes rather than only modified ones.

```bash
python -m src.cli rebuild-graph --json
```
Expected: a success object with the new node/edge counts. This takes several minutes.

- [ ] **Step 5: Measure the after-numbers**

```bash
python -m src.cli graph-stats --json
python scripts/graph_health.py
```

Then the distribution the spec cares about:

```bash
python -c "
import src, json, collections
from shared.config import get_settings
d = json.loads((get_settings().storage_path/'graph.json').read_text(encoding='utf-8'))
rel = collections.Counter(e.get('relation') for e in d['edges'])
kind = collections.Counter(n.get('type') for n in d['nodes'])
role = collections.Counter(n.get('role') for n in d['nodes'] if n.get('role'))
for name, c, tot in (('RELATIONS', rel, len(d['edges'])), ('KINDS', kind, len(d['nodes'])), ('ROLES', role, len(d['nodes']))):
    print(name)
    for k, v in c.most_common(): print(f'  {k:20} {v:4}  {100*v/tot:5.1f}%')
"
```

**Success criteria** (record actual numbers whether or not they are met):
- No single relation exceeds ~50% (was 78.5% `DEPENDS_ON`)
- No single kind exceeds ~55% (was 76% `Concept`)
- At least one `Statement` node carries a `role`
- At least three relation types beyond `DEPENDS_ON` are in use

- [ ] **Step 6: Write the results into the spec**

Append a `## Results (re-extraction YYYY-MM-DD)` section to
`docs/vocabulary-diagnosis.md` with the before/after tables from Steps 2 and 5, and state
plainly which success criteria were and were not met. Do not overstate a partial result.

- [ ] **Step 7: Update plan.md and CLAUDE.md**

In `plan.md`'s "What this deletes" table, change the `Free-text domain / subdomain` row's
neighbours as appropriate and add a row:

```markdown
| Single-axis `entity_type` | Conflated three orthogonal questions | Done (vocabulary redesign) |
```

In `CLAUDE.md`, add an invariant:

```markdown
- **Node typing is two axes, not one (docs/vocabulary-diagnosis.md).** `kind` is intrinsic
  and required (`Object`/`Statement`/`Definition`/`Method`/`Formula`/`Proof`/`Example`);
  `role` (`Theorem`/`Lemma`/`Corollary`/…) is **reported, never inferred** — set only when
  the source text applies that label, `None` otherwise. Argument structure belongs in edges
  (`COROLLARY_OF`, `USES_IN_PROOF`), which is where it already worked. Do not reintroduce a
  single `entity_type` field, and do not give `kind` a default — a default is what made 76%
  of nodes `Concept`.
- **Symmetric relations are stored in one direction.** `EQUIVALENT_TO` is ordered by
  endpoint id in `_normalize_relation`; storing both directions manufactures a 2-cycle.
```

- [ ] **Step 8: Commit**

```bash
git add docs/vocabulary-diagnosis.md plan.md CLAUDE.md
git commit -m "docs: record vocabulary re-extraction results and new invariants"
```

---

## Self-Review

**Spec coverage:**

| Spec finding | Covered by |
|---|---|
| V1 — `Concept` is default + residual | Task 1 (`kind` required, no default), Task 3 (prompt gives explicit criteria, rule 3 forbids defaulting to Object) |
| V2 — Lemma/Corollary/Axiom are relational roles | Task 1 (`role` optional, separate axis), Task 3 (reported-never-inferred rule in prompt), Task 7 (CLAUDE.md invariant) |
| V3 — Pass 2 is type-blind | Task 4 (`node_types` 4th parameter; entity dictionary carries kind + role; prompt rule 2 constrains by kind) |
| V4 — only `DEPENDS_ON` defined | Task 4 (every relation defined in the prompt with an example for the two least obvious) |
| V5 — relation set too poor; 29 cycles | Task 4 (7 new relations, `USES_AXIOM` dropped, `USES_LEMMA` renamed, symmetric canonicalization prevents the 2-cycle class). Repairing the existing 29 cycles is explicitly out of scope per the spec. |
| Design: kind axis (7 values) | Task 1 Step 3 |
| Design: role axis (6 values, optional) | Task 1 Step 3 |
| Design: relation table (12 rows) | Task 4 Step 3 |
| Design: symmetric canonicalization | Task 4 Steps 3–4, test in Step 1 |
| Legacy data must still load | Task 1 Step 4 (validator), Task 2 Step 4 (`load_graph` mapping), both tested |

**Placeholder scan:** No TBDs, no "handle edge cases", no "similar to Task N". Every code
step carries the actual code; every test step carries the actual assertions.

**Type consistency:**
- `MathEntityKind` / `StatementRole` / `LEGACY_TYPE_MAP` defined Task 1, consumed Tasks 2, 3, 4.
- `upsert_node_attrs(..., kind=, role=)` defined Task 2 Step 3, called Task 3 Step 6 with exactly those keyword names.
- `_extract_edges_pass(text, doc_concept_map, existing_concept_map, node_types)` defined Task 4 Step 7, called at both sites in Step 8 with the same parameter order.
- `node_types` shape `{id: {"kind": str, "role": str | None}}` is identical in Task 4 Steps 7 and 8.
- `SYMMETRIC_RELATIONS` defined Task 4 Step 3 (schema.py), imported and used Task 4 Step 4 (indexer.py).
- graph.json key is `type` (carrying kind) in Task 2 Step 5 and read as `n.type` in Task 6 Step 2 — consistent.
- `KIND_COLORS` replaces `ROLE_BORDER_COLORS` in Task 6 Step 3; no reference to the old name survives that task.

**Known ordering constraint:** Task 1 Step 7 leaves `tests/test_graph_store.py` failing on
purpose; Task 2 Step 6 fixes it. A reviewer gating Task 1 must accept that one known failure
rather than treating it as a regression.
