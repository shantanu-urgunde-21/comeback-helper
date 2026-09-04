from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from shared.logger import log
from src.routes import admin, ingest, query, vault

# ---------------------------------------------------------------------------
# App lifespan: initialize expensive objects once at startup, not per-request
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create heavy singletons once at startup, sharing dependencies."""
    from src.wiring import build_stack

    log.info("Initializing app-scoped singletons...")

    # Built in dependency order by the composition root, which supplies the
    # in-process collaborators the service packages would otherwise default
    # to HTTP clients for.
    vector_store, graph_indexer, query_engine = build_stack()

    app.state.vector_store = vector_store
    app.state.graph_indexer = graph_indexer
    app.state.query_engine = query_engine

    log.info("Singletons ready.")
    yield
    log.info("Shutting down Comeback Helper server.")


app = FastAPI(
    title="Comeback Helper - Math Knowledge Base & Ingestion API",
    lifespan=lifespan,
)

# Setup static files directory
STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Route modules under src/routes/ — one router per concern (ingest, query,
# vault/graph, admin). Handlers read shared singletons off `request.app.state`,
# set once in `lifespan` above.
app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(vault.router)
app.include_router(admin.router)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse(
            "<h1>Comeback Helper Server Running</h1>"
            "<p>Static index.html building...</p>"
        )
    return HTMLResponse(index_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host="127.0.0.1", port=8000, reload=True)
