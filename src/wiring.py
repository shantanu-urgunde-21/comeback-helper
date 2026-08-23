"""Composition root for the app.

Every package under `services/` takes its dependencies by constructor
injection rather than importing them. This module is the one place that
constructs the real objects and wires them together, so `server.py` and
`cli.py` cannot drift apart on it.

There is one copy of every module: these imports reach into `services/`,
and `src/` holds only the two entry points plus this wiring.
"""

from typing import Tuple

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


def build_indexer() -> MathGraphIndexer:
    """Builds an indexer wired to in-process collaborators."""
    return MathGraphIndexer(vault_manager=build_vault_manager())


def build_stack() -> Tuple[LocalVectorStore, MathGraphIndexer, MathQueryEngine]:
    """Constructs the three heavy singletons in dependency order.

    Each is expensive — the vector store loads an embedding model, the indexer
    loads the graph, the query engine embeds every node — so build this once
    per process and share it, never per request.
    """
    vector_store = LocalVectorStore()
    indexer = build_indexer()
    engine = MathQueryEngine(graph_indexer=indexer, vector_store=vector_store)
    return vector_store, indexer, engine
