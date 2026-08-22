"""Composition root for the in-process (monolith) deployment.

The packages under `services/` are deployment-agnostic: each takes its
dependencies by injection and, when given none, falls back to an HTTP client
addressing a docker-internal hostname. That default is correct inside a
container and useless in one process.

Running the whole stack in one process therefore means supplying the real
objects instead. That wiring lives here, in exactly one place, so `server.py`
and `cli.py` cannot drift apart on it — and so there is a single file to
delete when the services are genuinely split out.

There is now one copy of every module: these imports reach into `services/`,
and `src/` holds only the two entry points plus this wiring.
"""

from typing import Optional, Tuple

from graph.app.indexer import MathGraphIndexer
from retrieval.app.engine import MathQueryEngine
from shared.config import get_settings
from vault.app.manager import ObsidianVaultManager
from vector.app.store import LocalVectorStore


def build_vault_manager() -> ObsidianVaultManager:
    settings = get_settings()
    return ObsidianVaultManager(
        vault_path=settings.vault_path,
        state_file_path=settings.storage_path / "vault_state.json",
    )


def build_indexer(vector_store: Optional[LocalVectorStore] = None) -> MathGraphIndexer:
    """Builds an indexer wired to in-process collaborators.

    Passing `vector_store=None` is legitimate for read-only use (stats,
    dry-run extraction) but silently disables entity resolution, so any caller
    that will *write* to the graph must supply one.
    """
    return MathGraphIndexer(
        vector_store=vector_store,
        vault_manager=build_vault_manager(),
    )


def build_stack() -> Tuple[LocalVectorStore, MathGraphIndexer, MathQueryEngine]:
    """Constructs the three heavy singletons in dependency order.

    Each is expensive — the vector store loads an embedding model, the indexer
    loads the graph, the query engine embeds every node — so build this once
    per process and share it, never per request.
    """
    vector_store = LocalVectorStore()
    indexer = build_indexer(vector_store=vector_store)
    engine = MathQueryEngine(graph_indexer=indexer, vector_store=vector_store)
    return vector_store, indexer, engine
