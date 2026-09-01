# Puts the services root on sys.path under the module names the containers
# use. Must precede the service imports below. See src/__init__.py.
import src  # noqa: F401
import json
import tempfile
import unittest
from pathlib import Path

from graph.app import authority, graph_store


class TestGraphStore(unittest.TestCase):
    """Isolated round-trip test for the SQLite-backed graph structure
    (plan.md Phase 3) — uses a throwaway concepts.db via the same `db_path=`
    override pattern authority.py's own functions already support, unlike
    most tests in this suite (see CLAUDE.md: "Tests are not isolated").
    """

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "concepts.db"

    def tearDown(self):
        self._tmpdir.cleanup()

    def _make_concept(self, concept_id: str, label: str) -> None:
        # Mirrors reality: every concept id graph_store is asked to attach
        # attrs/mentions/edges to has already gone through
        # authority.resolve_concept, which creates the concepts row first.
        with authority._connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO concepts (id, label, authority, status) VALUES (?, ?, 'local', 'provisional')",
                (concept_id, label),
            )

    def test_round_trip(self):
        self._make_concept("CUST_a", "Alpha Concept")
        self._make_concept("CUST_b", "Beta Concept")

        with graph_store.connect(self.db_path) as conn:
            graph_store.upsert_node_attrs(
                conn, "CUST_a",
                label="Alpha Concept", kind="Object",
                taxonomy={"domain": "Test", "subdomain": "Sub", "topic": "CUST_a"},
                description="An alpha thing.", provenance=[], aliases=[],
            )
            graph_store.upsert_node_attrs(
                conn, "CUST_b",
                label="Beta Concept", kind="Statement", role="Theorem",
                taxonomy={"domain": "Test", "subdomain": "Sub", "topic": "CUST_b"},
                description="A beta thing.", provenance=[], aliases=[],
            )
            graph_store.insert_mention(conn, chunk_id="doc1", surface_text="Alpha Concept", concept_id="CUST_a")
            graph_store.insert_edge(
                conn, source_id="CUST_b", target_id="CUST_a", relation="DEPENDS_ON",
                chunk_id="doc1", quote="beta depends on alpha", origin="extracted",
            )

        G = graph_store.load_graph(self.db_path)

        self.assertEqual(G.number_of_nodes(), 2)
        self.assertEqual(G.number_of_edges(), 1)
        self.assertEqual(G.nodes["CUST_a"]["label"], "Alpha Concept")
        self.assertEqual(G.nodes["CUST_b"]["kind"], "Statement")
        self.assertTrue(G.has_edge("CUST_b", "CUST_a"))
        self.assertEqual(G.edges["CUST_b", "CUST_a"]["relation"], "DEPENDS_ON")

        with graph_store.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT quote, chunk_id, origin FROM edges WHERE source_id = ? AND target_id = ?",
                ("CUST_b", "CUST_a"),
            ).fetchone()
        self.assertEqual(row, ("beta depends on alpha", "doc1", "extracted"))

    def test_concept_without_attrs_is_not_a_graph_node(self):
        # A concepts row that authority.resolve_concept created (e.g. a
        # standalone authority-resolve CLI call) but that index_note never
        # touched must not become a graph node.
        self._make_concept("CUST_c", "Untouched Concept")
        G = graph_store.load_graph(self.db_path)
        self.assertEqual(G.number_of_nodes(), 0)

    def test_inserts_are_idempotent(self):
        self._make_concept("CUST_a", "Alpha Concept")
        self._make_concept("CUST_b", "Beta Concept")
        for _ in range(2):
            with graph_store.connect(self.db_path) as conn:
                graph_store.insert_mention(conn, chunk_id="doc1", surface_text="Alpha Concept", concept_id="CUST_a")
                graph_store.insert_edge(
                    conn, source_id="CUST_a", target_id="CUST_b", relation="DEPENDS_ON",
                    chunk_id="doc1", quote=None, origin="extracted",
                )

        with graph_store.connect(self.db_path) as conn:
            mention_count = conn.execute("SELECT COUNT(*) FROM mentions").fetchone()[0]
            edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        self.assertEqual(mention_count, 1)
        self.assertEqual(edge_count, 1)

    def test_clear_all_removes_structure_but_keeps_identity(self):
        self._make_concept("CUST_a", "Alpha Concept")
        with graph_store.connect(self.db_path) as conn:
            graph_store.upsert_node_attrs(conn, "CUST_a", label="Alpha Concept")
            graph_store.insert_mention(conn, chunk_id="doc1", surface_text="Alpha Concept", concept_id="CUST_a")

        self.assertEqual(graph_store.load_graph(self.db_path).number_of_nodes(), 1)

        graph_store.clear_all(self.db_path)

        self.assertEqual(graph_store.load_graph(self.db_path).number_of_nodes(), 0)
        with authority._connect(self.db_path) as conn:
            still_there = conn.execute("SELECT COUNT(*) FROM concepts WHERE id = 'CUST_a'").fetchone()[0]
        self.assertEqual(still_there, 1)

    def test_round_trip_preserves_kind_and_role(self):
        self._make_concept("CUST_t", "Schwarz")
        with graph_store.connect(self.db_path) as conn:
            graph_store.upsert_node_attrs(
                conn, "CUST_t", label="Schwarz's Theorem",
                kind="Statement", role="Theorem",
                taxonomy={}, description="", provenance=[], aliases=[],
            )
        G = graph_store.load_graph(db_path=self.db_path)
        self.assertEqual(G.nodes["CUST_t"]["kind"], "Statement")
        self.assertEqual(G.nodes["CUST_t"]["role"], "Theorem")

    def test_legacy_entity_type_row_loads_as_kind_and_role(self):
        """A node written before the split must still load, mapped onto both axes."""
        self._make_concept("CUST_o", "Old")
        with graph_store.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE concepts SET node_attrs_json = ? WHERE id = ?",
                (json.dumps({"label": "Abel's Lemma", "entity_type": "Lemma"}), "CUST_o"),
            )
        G = graph_store.load_graph(db_path=self.db_path)
        self.assertEqual(G.nodes["CUST_o"]["kind"], "Statement")
        self.assertEqual(G.nodes["CUST_o"]["role"], "Lemma")

    def test_export_writes_kind_under_type_key_and_role_alongside(self):
        import networkx as nx
        G = nx.DiGraph()
        G.add_node("CUST_t", label="Schwarz's Theorem", kind="Statement", role="Theorem")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "graph.json"
            graph_store.export_graph_json(G, out)
            data = json.loads(out.read_text(encoding="utf-8"))
        node = data["nodes"][0]
        self.assertEqual(node["type"], "Statement")   # back-compat key carries kind
        self.assertEqual(node["role"], "Theorem")

    def test_round_trip_preserves_extraction_method(self):
        """Node and edge extraction_method survive a SQLite write/read cycle,
        so degraded (block_parser) content stays distinguishable from LLM output."""
        self._make_concept("CUST_g", "Gemini Node")
        self._make_concept("CUST_b", "Block Node")
        with graph_store.connect(self.db_path) as conn:
            graph_store.upsert_node_attrs(
                conn, "CUST_g", label="Gemini Node", kind="Object",
                taxonomy={}, description="", provenance=[], aliases=[],
                extraction_method="gemini",
            )
            graph_store.upsert_node_attrs(
                conn, "CUST_b", label="Block Node", kind="Object",
                taxonomy={}, description="", provenance=[], aliases=[],
                extraction_method="block_parser",
            )
            graph_store.insert_edge(
                conn, source_id="CUST_g", target_id="CUST_b", relation="DEPENDS_ON",
                chunk_id="doc1", quote="", origin="extracted",
                extraction_method="ollama",
            )
        G = graph_store.load_graph(db_path=self.db_path)
        self.assertEqual(G.nodes["CUST_g"]["extraction_method"], "gemini")
        self.assertEqual(G.nodes["CUST_b"]["extraction_method"], "block_parser")
        self.assertEqual(G.edges["CUST_g", "CUST_b"]["extraction_method"], "ollama")

    def test_legacy_node_without_extraction_method_loads_as_none(self):
        """A node written before this column existed must still load (as None),
        not crash graph_health.py's extraction-provenance report."""
        self._make_concept("CUST_l", "Legacy")
        with graph_store.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE concepts SET node_attrs_json = ? WHERE id = ?",
                (json.dumps({"label": "Legacy", "kind": "Object"}), "CUST_l"),
            )
        G = graph_store.load_graph(db_path=self.db_path)
        self.assertIsNone(G.nodes["CUST_l"].get("extraction_method"))


if __name__ == "__main__":
    unittest.main()
