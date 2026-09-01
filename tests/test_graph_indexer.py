# Puts the services root on sys.path under the module names the containers
# use. Must precede the service imports below. See src/__init__.py.
import src  # noqa: F401
import unittest
from pathlib import Path
from graph.app.schema import (
    MathEntityExtraction, GraphNode, GraphEdge,
    MathEntityType, MathEntityKind, StatementRole, MathRelationType,
)
from graph.app.indexer import MathGraphIndexer, _normalize_relation


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


class TestGraphIndexer(unittest.TestCase):
    def test_schema_models(self):
        node1 = GraphNode(name="Eigenvalue", kind=MathEntityKind.OBJECT, description="Scalar lambda")
        node2 = GraphNode(name="Spectral Theorem", kind=MathEntityKind.STATEMENT,
                          role=StatementRole.THEOREM, description="Symmetric matrix breakdown")
        edge = GraphEdge(source="Spectral Theorem", target="Eigenvalue", relation=MathRelationType.DEPENDS_ON)

        extraction = MathEntityExtraction(nodes=[node1, node2], edges=[edge])

        self.assertEqual(len(extraction.nodes), 2)
        self.assertEqual(len(extraction.edges), 1)
        self.assertEqual(extraction.nodes[0].name, "Eigenvalue")
        self.assertEqual(extraction.edges[0].relation, MathRelationType.DEPENDS_ON)

    def test_indexer_graph_structure(self):
        indexer = MathGraphIndexer()
        node1 = GraphNode(name="Vector Space", kind=MathEntityKind.DEFINITION, description="Set with vector addition")
        node2 = GraphNode(name="Linear Independence", kind=MathEntityKind.OBJECT, description="Vectors without linear combination")
        edge = GraphEdge(source="Linear Independence", target="Vector Space", relation=MathRelationType.DEPENDS_ON)

        extraction = MathEntityExtraction(nodes=[node1, node2], edges=[edge])

        for n in extraction.nodes:
            indexer.graph.add_node(n.name, kind=n.kind.value, role=(n.role.value if n.role else None),
                                   description=n.description)
        for e in extraction.edges:
            indexer.graph.add_edge(e.source, e.target, relation=e.relation.value)

        self.assertIn("Vector Space", indexer.graph.nodes)
        self.assertIn("Linear Independence", indexer.graph.nodes)
        self.assertTrue(indexer.graph.has_edge("Linear Independence", "Vector Space"))


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

    def test_index_note_mentions_use_chunk_ids(self):
        """Mentions written during index_note() carry chunk-level chunk_ids."""
        import tempfile, os
        from graph.app import graph_store

        # Build a two-section note with a concept in each section.
        # Use wikilinks so the block extractor (use_llm=False) picks up nodes.
        note_content = (
            "## First Principles\n"
            "The [[Wronskian]] is a determinant used to check linear independence.\n\n"
            "## Applications\n"
            "[[Abel's Identity]] relates the Wronskian to the coefficient of y'.\n"
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

    def test_index_note_tags_extraction_method_block_parser(self):
        """use_llm=False must tag new nodes/edges block_parser, so graph_health.py
        can tell degraded (non-LLM) content apart from Gemini/Ollama output."""
        import tempfile, os
        # Synthetic, unlikely-to-collide names — a name already present in the
        # (unisolated, real) graph would hit the node-update branch instead of
        # node-creation, which deliberately leaves extraction_method untouched.
        note = (
            "## Zzq Synthetic Extraction Probe\nA synthetic test concept.\n"
            "## Zzq Synthetic Extraction Probe Two\nDepends on the probe above.\n"
            "[[Zzq Synthetic Extraction Probe]]\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", dir=self.indexer.vault_path,
                                         delete=False, encoding="utf-8") as f:
            f.write(note)
            tmp_path = f.name
        nodes_before = set(self.indexer.graph.nodes)
        new_nodes: set = set()
        try:
            self.indexer.index_note(Path(tmp_path), use_llm=False)
            new_nodes = set(self.indexer.graph.nodes) - nodes_before
            self.assertTrue(new_nodes, "expected at least one newly created node")
            node_methods = [self.indexer.graph.nodes[n].get("extraction_method") for n in new_nodes]
            self.assertTrue(all(m == "block_parser" for m in node_methods),
                            f"every newly created node from a use_llm=False index should be tagged block_parser, got {node_methods}")
        finally:
            os.unlink(tmp_path)
            # This test writes real .storage/concepts.db (CLAUDE.md: tests
            # aren't isolated) — unlike other tests here, the concept it
            # creates is synthetic junk, not a real course concept worth
            # keeping around, so scrub it rather than leaving it for
            # graph_health.py to report as a suspect node forever.
            for n in new_nodes:
                self.indexer.graph.remove_node(n)
            if new_nodes:
                import sqlite3
                from shared.config import get_settings
                conn = sqlite3.connect(get_settings().storage_path / "concepts.db")
                placeholders = ",".join("?" for _ in new_nodes)
                ids = tuple(new_nodes)
                conn.execute(f"DELETE FROM mentions WHERE concept_id IN ({placeholders})", ids)
                conn.execute(f"DELETE FROM aliases WHERE concept_id IN ({placeholders})", ids)
                conn.execute(f"DELETE FROM edges WHERE source_id IN ({placeholders}) OR target_id IN ({placeholders})", ids + ids)
                conn.execute(f"DELETE FROM concepts WHERE id IN ({placeholders})", ids)
                conn.commit()
                conn.close()


if __name__ == "__main__":
    unittest.main()
