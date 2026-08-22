"""Retrieval service — hybrid context assembly and answer synthesis.

Holds no state of its own. It reads from the graph and vector services and
calls an LLM to synthesise. That makes it the easiest service to redeploy and
the one whose contract is least likely to change under the Base-Graph rewrite.

What *will* change: the engine currently reconstructs the whole graph locally
to walk three nodes' neighbourhoods (see app/clients.py). Once it calls the
graph service's /neighborhood endpoint instead, this service stops needing
networkx at all.
"""

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.clients import MathGraphIndexer, LocalVectorStore
from app.engine import MathQueryEngine

app = FastAPI(title="Comeback Helper — Retrieval Service")

graph_client = MathGraphIndexer()
vector_client = LocalVectorStore()
engine = MathQueryEngine(graph_indexer=graph_client, vector_store=vector_client)


class QueryIn(BaseModel):
    prompt: str
    top_k: int = Field(default=5, ge=1, le=20)
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    course: Optional[str] = None
    use_graph: bool = True


class ContextIn(BaseModel):
    prompt: str
    top_k: int = 5
    course: Optional[str] = None
    use_graph: bool = True


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/refresh")
def refresh():
    """Drop cached graph state after an ingest.

    The monolith called `refresh_node_embeddings()` directly after every graph
    write. Across services that becomes an explicit call, which is a good
    thing: the coupling is now visible instead of implicit.
    """
    graph_client.refresh()
    engine.refresh_node_embeddings()
    return {"status": "success"}


@app.post("/context")
def context(body: ContextIn):
    """Assembled context without synthesis — useful for debugging retrieval
    quality separately from answer quality."""
    return {"context": engine.retrieve_context(
        body.prompt, top_k=body.top_k, course=body.course, use_graph=body.use_graph
    )}


@app.post("/query")
def query(body: QueryIn):
    answer = engine.query(
        prompt=body.prompt,
        top_k=body.top_k,
        temperature=body.temperature,
        course=body.course,
        use_graph=body.use_graph,
    )
    return {"status": "success", "answer": answer}
