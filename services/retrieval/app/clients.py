"""HTTP clients standing in for what used to be in-process imports.

`engine.py` held a live `MathGraphIndexer` and a live `LocalVectorStore` and
reached into both. Across a service boundary those become network calls.

The awkward one is `indexer.graph`: the engine treats it as a real
`nx.DiGraph`, calling `.neighbors()`, `.predecessors()` and `.nodes[...]` on
it. A network cannot hand back a live object, so `GraphClient.graph` fetches
the whole graph once and rebuilds it locally.

That works, and it is honest about the cost: **this is the boundary that is
wrong as currently drawn.** The engine only ever needs the 1-hop neighbourhood
of three matched nodes, so the graph service should expose
`/neighborhood?ids=…&hops=1` and the engine should ask for that instead of
reconstructing the entire graph per process. That change belongs to the
rewrite phase, not the isolation phase — see plan.md.
"""

from typing import Any, Dict, List, Optional

import networkx as nx
import requests

from shared.logger import log

GRAPH_URL = "http://graph:8004"
VECTOR_URL = "http://vector:8003"
TIMEOUT = 60


class MathGraphIndexer:
    """Client for the graph service, exposing the `.graph` attribute the
    engine already reads."""

    def __init__(self, base_url: str = GRAPH_URL):
        self.base_url = base_url.rstrip("/")
        self._graph: Optional[nx.DiGraph] = None

    @property
    def graph(self) -> nx.DiGraph:
        if self._graph is None:
            self._graph = self._fetch_graph()
        return self._graph

    def refresh(self) -> None:
        """Drops the cached copy so the next access refetches."""
        self._graph = None

    def _fetch_graph(self) -> nx.DiGraph:
        G = nx.DiGraph()
        try:
            r = requests.get(f"{self.base_url}/graph", timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            log.warning(f"Could not fetch graph from {self.base_url} ({e}). Using empty graph.")
            return G

        for node in data.get("nodes", []):
            node = dict(node)
            # The service serialises entity_type as `type`; the engine reads
            # `entity_type`. Same rename the in-process loader performs.
            if "type" in node:
                node["entity_type"] = node.pop("type")
            G.add_node(node["id"], **node)
        for edge in data.get("edges", []):
            G.add_edge(edge["source"], edge["target"], relation=edge.get("relation", "DEPENDS_ON"))
        return G

    def neighborhood(self, node_ids: List[str], hops: int = 1) -> Dict[str, Any]:
        """What the engine *should* call instead of reading `.graph`.

        Not yet wired into engine.py — that is a rewrite-phase change.
        """
        r = requests.post(
            f"{self.base_url}/neighborhood",
            json={"ids": node_ids, "hops": hops},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()


class LocalVectorStore:
    """Client for the vector service."""

    def __init__(self, base_url: str = VECTOR_URL):
        self.base_url = base_url.rstrip("/")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        r = requests.post(f"{self.base_url}/embed", json={"texts": texts}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()["vectors"]

    def search_similar(self, query: str, top_k: int = 5, course: Optional[str] = None,
                       query_type: str = "hybrid") -> List[Dict[str, Any]]:
        try:
            r = requests.post(
                f"{self.base_url}/search",
                json={"query": query, "top_k": top_k, "course": course, "query_type": query_type},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            return r.json()["results"]
        except Exception as e:
            log.warning(f"Vector search failed ({e}). Returning empty result list.")
            return []

    def get_stats(self) -> Dict[str, Any]:
        r = requests.get(f"{self.base_url}/stats", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
