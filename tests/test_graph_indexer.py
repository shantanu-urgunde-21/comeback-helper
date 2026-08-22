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

if __name__ == "__main__":
    unittest.main()
