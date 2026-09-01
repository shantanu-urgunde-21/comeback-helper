# Puts the services root on sys.path under the module names the containers
# use. Must precede the service imports below. See src/__init__.py.
import src  # noqa: F401
import unittest
import networkx as nx
from graph.app.dag import break_2cycles, prune_feedback_edges, repair_graph_dag, will_create_cycle


class TestDAGEnforcement(unittest.TestCase):
    def test_will_create_cycle(self):
        G = nx.DiGraph()
        G.add_edge("A", "B")
        G.add_edge("B", "C")

        # Adding C -> A would create a cycle A -> B -> C -> A
        self.assertTrue(will_create_cycle(G, "C", "A"))
        # Adding A -> C does not create a cycle
        self.assertFalse(will_create_cycle(G, "A", "C"))
        # Adding self-loop creates a cycle
        self.assertTrue(will_create_cycle(G, "A", "A"))

    def test_break_2cycles_specific_overrides_generic(self):
        G = nx.DiGraph()
        # Picard's Theorem HAS_HYPOTHESIS Lipschitz Condition
        G.add_edge("Picard", "Lipschitz", relation="HAS_HYPOTHESIS")
        # Lipschitz Condition DEPENDS_ON Picard's Theorem (generic reverse edge)
        G.add_edge("Lipschitz", "Picard", relation="DEPENDS_ON")

        removed = break_2cycles(G)
        self.assertEqual(len(removed), 1)
        self.assertEqual(removed[0], ("Lipschitz", "Picard", "DEPENDS_ON"))
        self.assertTrue(G.has_edge("Picard", "Lipschitz"))
        self.assertFalse(G.has_edge("Lipschitz", "Picard"))
        self.assertEqual(G.edges["Picard", "Lipschitz"]["relation"], "HAS_HYPOTHESIS")

    def test_break_2cycles_mutual_becomes_canonical_equivalent(self):
        G = nx.DiGraph()
        G.add_edge("Linear_Dep", "Linear_Indep", relation="DEPENDS_ON")
        G.add_edge("Linear_Indep", "Linear_Dep", relation="DEPENDS_ON")

        removed = break_2cycles(G)
        self.assertEqual(len(removed), 2)
        # Should have 1 canonical EQUIVALENT_TO edge
        self.assertEqual(G.number_of_edges(), 1)
        src, tgt = sorted(["Linear_Dep", "Linear_Indep"])
        self.assertTrue(G.has_edge(src, tgt))
        self.assertEqual(G.edges[src, tgt]["relation"], "EQUIVALENT_TO")

    def test_prune_feedback_edges_multihop_cycle(self):
        G = nx.DiGraph()
        # A -> B -> C -> A
        G.add_edge("A", "B", relation="USES_IN_PROOF")
        G.add_edge("B", "C", relation="USES_DEFINITION")
        G.add_edge("C", "A", relation="DEPENDS_ON")

        self.assertFalse(nx.is_directed_acyclic_graph(G))
        removed = prune_feedback_edges(G)
        self.assertTrue(nx.is_directed_acyclic_graph(G))
        self.assertEqual(len(removed), 1)
        # The lowest priority edge (DEPENDS_ON) should be dropped
        self.assertEqual(removed[0], ("C", "A", "DEPENDS_ON"))

    def test_repair_graph_dag_end_to_end(self):
        G = nx.DiGraph()
        # 2-cycle
        G.add_edge("X", "Y", relation="USES_IN_PROOF")
        G.add_edge("Y", "X", relation="DEPENDS_ON")
        # 3-cycle
        G.add_edge("1", "2", relation="USES_DEFINITION")
        G.add_edge("2", "3", relation="USES_DEFINITION")
        G.add_edge("3", "1", relation="DEPENDS_ON")

        # Default mode: resolves 2-cycles, preserves multi-hop connections
        stats = repair_graph_dag(G, prune_multihop=False)
        self.assertEqual(len(stats["removed_2cycles"]), 1)
        self.assertTrue(G.has_edge("X", "Y"))
        self.assertFalse(G.has_edge("Y", "X"))
        self.assertTrue(G.has_edge("3", "1"))

        # prune_multihop=True mode: breaks multi-hop cycles as well
        stats_full = repair_graph_dag(G, prune_multihop=True)
        self.assertTrue(stats_full["is_dag"])
        self.assertTrue(nx.is_directed_acyclic_graph(G))


if __name__ == "__main__":
    unittest.main()
