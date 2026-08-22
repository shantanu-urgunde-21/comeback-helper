# Puts the services root on sys.path under the module names the containers
# use. Must precede the service imports below. See src/__init__.py.
import src  # noqa: F401
import unittest
from pathlib import Path
from graph.app.schema import MathEntityExtraction, GraphNode, GraphEdge, MathEntityType, MathRelationType
from graph.app.indexer import MathGraphIndexer

class TestGraphIndexer(unittest.TestCase):
    def test_schema_models(self):
        node1 = GraphNode(name="Eigenvalue", entity_type=MathEntityType.CONCEPT, description="Scalar lambda")
        node2 = GraphNode(name="Spectral Theorem", entity_type=MathEntityType.THEOREM, description="Symmetric matrix breakdown")
        edge = GraphEdge(source="Spectral Theorem", target="Eigenvalue", relation=MathRelationType.DEPENDS_ON)

        extraction = MathEntityExtraction(nodes=[node1, node2], edges=[edge])
        
        self.assertEqual(len(extraction.nodes), 2)
        self.assertEqual(len(extraction.edges), 1)
        self.assertEqual(extraction.nodes[0].name, "Eigenvalue")
        self.assertEqual(extraction.edges[0].relation, MathRelationType.DEPENDS_ON)

    def test_indexer_graph_structure(self):
        indexer = MathGraphIndexer()
        node1 = GraphNode(name="Vector Space", entity_type=MathEntityType.DEFINITION, description="Set with vector addition")
        node2 = GraphNode(name="Linear Independence", entity_type=MathEntityType.CONCEPT, description="Vectors without linear combination")
        edge = GraphEdge(source="Linear Independence", target="Vector Space", relation=MathRelationType.DEPENDS_ON)

        extraction = MathEntityExtraction(nodes=[node1, node2], edges=[edge])
        
        for n in extraction.nodes:
            indexer.graph.add_node(n.name, entity_type=n.entity_type.value, description=n.description)
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

if __name__ == "__main__":
    unittest.main()
