"""Graph service — concept extraction and the concept graph itself.

This is the service the Base-Graph rewrite targets. Today it wraps the
extracted `indexer.py`: two LLM passes, deterministic entity resolution via
`authority.resolve_concept()`, an in-RAM `nx.DiGraph` persisted to graph.json.

The endpoints below are drawn to survive the rest of that rewrite (plan.md
Phase 3+). `/extract`, `/index`, `/graph` and `/neighborhood` describe *what
the service does*, not how it currently does it, so replacing the internals
with SQLite-backed canonical IDs should not change this surface.
"""

from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.clients import VectorStoreClient
from app.indexer import MathGraphIndexer

app = FastAPI(title="Comeback Helper — Graph Service")

# The indexer holds the graph in memory. Constructed once; a vector store
# client must be supplied or entity resolution silently no-ops.
indexer = MathGraphIndexer(vector_store=VectorStoreClient())


class ExtractIn(BaseModel):
    text: str
    course_domain: str = "General Math"
    use_llm: bool = True


class IndexIn(BaseModel):
    note_path: str
    use_llm: bool = True


class RebuildIn(BaseModel):
    use_llm: bool = True
    force: bool = False


class NeighborhoodIn(BaseModel):
    ids: List[str]
    hops: int = 1


@app.get("/health")
def health():
    return {"status": "ok",
            "nodes": indexer.graph.number_of_nodes(),
            "edges": indexer.graph.number_of_edges()}


@app.get("/stats")
def stats():
    import networkx as nx
    G = indexer.graph
    types: dict = {}
    for _, data in G.nodes(data=True):
        t = data.get("entity_type", "Concept")
        types[t] = types.get(t, 0) + 1
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "connected_components": nx.number_connected_components(G.to_undirected()) if G.number_of_nodes() else 0,
        "isolated_nodes": len(list(nx.isolates(G))) if G.number_of_nodes() else 0,
        "entity_types": types,
    }


@app.get("/graph")
def get_graph():
    """Full serialised graph. Fine at this size; the 1-hop endpoint below is
    what callers should prefer once they are rewritten to use it."""
    G = indexer.graph
    return {
        "nodes": [{"id": n, **{k: v for k, v in G.nodes[n].items() if k != "id"}} for n in G.nodes],
        "edges": [{"source": u, "target": v, "relation": d.get("relation", "DEPENDS_ON")}
                  for u, v, d in G.edges(data=True)],
    }


@app.post("/neighborhood")
def neighborhood(body: NeighborhoodIn):
    """N-hop subgraph around the given ids.

    This is the endpoint retrieval should call instead of pulling the whole
    graph — it bounds what crosses the wire and what the frontend has to lay
    out.
    """
    G = indexer.graph
    keep: set = set()
    frontier = {i for i in body.ids if i in G}
    keep |= frontier
    for _ in range(max(body.hops, 0)):
        nxt: set = set()
        for n in frontier:
            nxt |= set(G.successors(n)) | set(G.predecessors(n))
        nxt -= keep
        keep |= nxt
        frontier = nxt

    return {
        "nodes": [{"id": n, **{k: v for k, v in G.nodes[n].items() if k != "id"}} for n in keep],
        "edges": [{"source": u, "target": v, "relation": d.get("relation", "DEPENDS_ON")}
                  for u, v, d in G.edges(data=True) if u in keep and v in keep],
        "seeds": body.ids,
    }


@app.post("/extract")
def extract(body: ExtractIn):
    """Dry run — extract from text without touching the graph."""
    result = indexer.extract_from_text(
        body.text, use_llm=body.use_llm, course_domain=body.course_domain
    )
    return {
        "nodes": [n.model_dump() for n in result.nodes],
        "edges": [e.model_dump() for e in result.edges],
    }


@app.post("/index")
def index_note(body: IndexIn):
    p = Path(body.note_path)
    if not p.exists():
        raise HTTPException(404, f"No note at {body.note_path}")
    before = indexer.graph.number_of_nodes()
    indexer.index_note(p, use_llm=body.use_llm)
    indexer.save_graph()
    return {"status": "success", "nodes_added": indexer.graph.number_of_nodes() - before,
            "nodes": indexer.graph.number_of_nodes(),
            "edges": indexer.graph.number_of_edges()}


@app.post("/rebuild")
def rebuild(body: RebuildIn):
    G = indexer.build_or_update_index(use_llm=body.use_llm, force=body.force)
    return {"status": "success", "nodes": G.number_of_nodes(), "edges": G.number_of_edges()}
