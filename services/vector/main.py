"""Vector service — chunking, embeddings, and hybrid chunk search.

Owns LanceDB and the FastEmbed model. The embedding model is loaded once at
import; it is the expensive part of this service, so it must not be
constructed per request.

Two consumers today: retrieval (chunk search) and graph (entity resolution).
The second one goes away under the Base-Graph design — deterministic lookup
replaces embedding comparison — leaving this service with a single, clean
responsibility.
"""

from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from app.chunker import chunk_math_markdown
from app.store import LocalVectorStore
from shared.logger import log

app = FastAPI(title="Comeback Helper — Vector Service")

# Loaded once: constructing this per request would reload the embedding model.
store = LocalVectorStore()


class EmbedIn(BaseModel):
    texts: List[str]


class SearchIn(BaseModel):
    query: str
    top_k: int = 5
    course: Optional[str] = None
    query_type: str = "hybrid"


class ChunkIn(BaseModel):
    content: str
    course: str
    source_name: str


class IndexIn(ChunkIn):
    pass


@app.get("/health")
def health():
    return {"status": "ok", **store.get_stats()}


@app.get("/stats")
def stats():
    return store.get_stats()


@app.post("/embed")
def embed(body: EmbedIn):
    return {"vectors": store.embed_texts(body.texts)}


@app.post("/search")
def search(body: SearchIn):
    results = store.search_similar(
        body.query, top_k=body.top_k, course=body.course, query_type=body.query_type
    )
    return {"results": results, "count": len(results)}


@app.post("/chunk")
def chunk(body: ChunkIn):
    """Chunk without indexing — useful for inspecting boundaries."""
    chunks = chunk_math_markdown(body.content, body.course, body.source_name)
    return {"chunks": chunks, "count": len(chunks)}


@app.post("/index")
def index(body: IndexIn):
    """Chunk a note and write it into the vector store.

    Note: append-only. Re-indexing the same note duplicates its chunks rather
    than replacing them — a known defect carried over from the monolith, to be
    fixed with a delete-by-source before insert.
    """
    chunks = chunk_math_markdown(body.content, body.course, body.source_name)
    if chunks:
        store.add_chunks(chunks)
    log.info(f"Indexed {len(chunks)} chunks from {body.source_name}")
    return {"status": "success", "chunks": len(chunks)}
