# Puts the services root on sys.path under the module names the containers
# use. Must precede the service imports below. See src/__init__.py.
import src  # noqa: F401
import unittest
from pathlib import Path
from vector.app.store import LocalVectorStore
from retrieval.app.engine import MathQueryEngine

class TestVectorAndRetrieval(unittest.TestCase):
    def test_vector_store_indexing_and_search(self):
        store = LocalVectorStore()
        
        test_chunks = [
            {
                "id": "chunk_1",
                "text": "The Spectral Theorem states that any real symmetric matrix can be diagonalized by an orthogonal matrix.",
                "course": "Linear Algebra",
                "source": "lecture1.md"
            },
            {
                "id": "chunk_2",
                "text": "Principal Component Analysis uses eigenvalues of the covariance matrix to perform dimensionality reduction.",
                "course": "Machine Learning",
                "source": "lecture5.md"
            }
        ]
        
        store.add_chunks(test_chunks)
        
        results = store.search_similar("symmetric matrix diagonalized", top_k=2)
        self.assertTrue(len(results) > 0)
        self.assertIn("Spectral Theorem", results[0]["text"])

    def test_hybrid_retrieval_context_assembly(self):
        engine = MathQueryEngine()
        context = engine.retrieve_context("Spectral Theorem")
        self.assertIsInstance(context, str)

if __name__ == "__main__":
    unittest.main()
