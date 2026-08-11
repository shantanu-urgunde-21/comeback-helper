import json
import shutil
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from src.config import get_settings
from src.vault.manager import ObsidianVaultManager
from src.ingestion.handwriting.health import OllamaHealthCheck
from src.chunker import chunk_math_markdown
from src.logger import log

# ---------------------------------------------------------------------------
# App lifespan: initialize expensive objects once at startup, not per-request
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create heavy singletons once at startup, sharing dependencies."""
    from src.retrieval.engine import MathQueryEngine
    from src.atlas.store import AtlasStore
    from src.vector.store import LocalVectorStore

    log.info("Initializing app-scoped singletons...")

    # Create in dependency order: vector store -> atlas -> query engine
    vector_store = LocalVectorStore()
    atlas = AtlasStore()
    query_engine = MathQueryEngine(atlas=atlas, vector_store=vector_store)

    app.state.vector_store = vector_store
    app.state.atlas = atlas
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


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class QueryRequest(BaseModel):
    prompt: str
    top_k: int = Field(default=5, ge=1, le=20)
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    course: Optional[str] = None
    use_graph: bool = True


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse(
            "<h1>Comeback Helper Server Running</h1>"
            "<p>Static index.html building...</p>"
        )
    return HTMLResponse(index_file.read_text(encoding="utf-8"))


@app.get("/api/health/ollama")
async def check_ollama_health():
    """Returns live health telemetry for local Ollama service."""
    checker = OllamaHealthCheck()
    status = checker.check_health()
    return JSONResponse(status)


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------


@app.post("/api/ingest")
async def ingest_pdf(
    file: UploadFile = File(...),
    course: str = Form(...),
    ocr_mode: Optional[str] = Form("local_handwriting"),
    dpi: int = Form(200),
    auto_index: bool = Form(True),
):
    """
    Uploads a PDF file, runs OCR, saves a Markdown note to the vault,
    and optionally updates the knowledge graph + vector index.
    """
    log.info(
        f"Received API ingestion request for file '{file.filename}' "
        f"in course '{course}' (Mode: {ocr_mode}, DPI: {dpi}, AutoIndex: {auto_index})"
    )
    if not file.filename.endswith(".pdf"):
        log.warning(f"Rejected non-PDF upload attempt: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    settings = get_settings()
    temp_dir = settings.storage_path / "temp_uploads"
    temp_dir.mkdir(exist_ok=True)
    temp_pdf_path = temp_dir / file.filename

    try:
        with open(temp_pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Configure OCR Provider based on user selection
        if ocr_mode == "local_handwriting":
            from src.ingestion.handwriting_provider import HandwritingOCRProvider
            ocr_provider = HandwritingOCRProvider(
                vault_attachments_dir=Path(f"./.storage/vault/{course}/attachments")
            )
        else:  # gemini_vision
            from src.ingestion.gemini_ocr import GeminiOCRProvider
            ocr_provider = GeminiOCRProvider()

        from src.ingestion.pipeline import IngestionPipeline
        pipeline = IngestionPipeline(ocr_provider=ocr_provider)
        target_note_path = pipeline.process_pdf(
            pdf_path=temp_pdf_path,
            course_name=course,
        )

        # --- Optionally update graph index and vector store ---
        index_results = {"graph_indexed": False, "vector_chunks": 0}

        if auto_index:
            atlas = app.state.atlas
            vector_store = app.state.vector_store

            try:
                from src.atlas.extract import extract_note
                stmts, terms, _ = extract_note(target_note_path, atlas)
                atlas.add_terms(terms)
                atlas.add_statements(stmts)
                atlas.save()
                index_results["graph_indexed"] = True
                index_results["statements"] = len(stmts)
                log.info(f"Atlas updated with {len(stmts)} statements from {target_note_path.name}")
                app.state.query_engine.refresh_node_embeddings()
            except Exception as e:
                log.warning(f"Atlas indexing skipped for {target_note_path.name}: {e}")

            try:
                note_content = target_note_path.read_text(encoding="utf-8")
                chunks = chunk_math_markdown(
                    content=note_content,
                    course=course,
                    source_name=target_note_path.name,
                )
                if chunks:
                    vector_store.add_chunks(chunks)
                    index_results["vector_chunks"] = len(chunks)
                    log.info(f"Vector store updated with {len(chunks)} chunks from: {target_note_path.name}")
            except Exception as e:
                log.warning(f"Vector indexing skipped for {target_note_path.name}: {e}")

        # Read generated markdown content for instant UI preview
        note_text = ""
        if target_note_path.exists():
            note_text = target_note_path.read_text(encoding="utf-8")

        return JSONResponse({
            "status": "success",
            "filename": file.filename,
            "course": course,
            "ocr_mode": ocr_mode,
            "note_path": str(target_note_path),
            "content": note_text,
            **index_results,
        })

    except Exception as e:
        log.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_pdf_path.exists():
            temp_pdf_path.unlink()


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------


@app.post("/api/query")
async def query_knowledge_base(request: QueryRequest):
    """
    Asks mathematical questions to the hybrid RAG engine with
    configurable retrieval parameters.
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Query prompt cannot be empty.")

    try:
        engine = app.state.query_engine
        answer = engine.query(
            prompt=request.prompt,
            top_k=request.top_k,
            temperature=request.temperature,
            course=request.course,
            use_graph=request.use_graph,
        )
        return JSONResponse({"status": "success", "answer": answer})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Vault & Graph
# ---------------------------------------------------------------------------


@app.get("/api/vault")
async def get_vault_notes():
    """Returns list of course folders and notes in the Obsidian Vault."""
    settings = get_settings()
    vault_path = settings.vault_path

    if not vault_path.exists():
        return JSONResponse({"vault": {}})

    manager = ObsidianVaultManager(vault_path)
    notes = manager.get_all_notes()

    vault_data: dict = {}
    for note in notes:
        try:
            rel = note.relative_to(vault_path)
            parts = rel.parts
            course = parts[0] if len(parts) > 1 else "General"
        except Exception:
            course = "General"

        if course not in vault_data:
            vault_data[course] = []
        vault_data[course].append({
            "title": note.stem,
            "path": str(note),
            "size": note.stat().st_size,
        })

    return JSONResponse({"vault": vault_data})


@app.get("/api/graph")
async def get_graph_data():
    """
    Returns the atlas as nodes and edges: the context lattice plus every
    statement indexed against it.

    `extends` is the order relation and drives vertical position; `over` is
    parameterisation and is deliberately excluded from depth.
    """
    atlas = app.state.atlas

    nodes = [
        {
            "id": cid,
            "label": c.get("name", cid),
            "group": c.get("course", "context"),
            "type": "Context",
            "extends": c.get("extends", []),
            "over": c.get("over", []),
        }
        for cid, c in atlas.contexts.items()
    ]
    edges = [
        {"from": cid, "to": p, "relation": "EXTENDS", "label": "extends"}
        for cid, ps in atlas.extends.items() for p in ps if p in atlas.contexts
    ] + [
        {"from": cid, "to": p, "relation": "OVER", "label": "over"}
        for cid, ps in atlas.over.items() for p in ps if p in atlas.contexts
    ]

    for st in atlas.statements.values():
        nodes.append({
            "id": st.id,
            "label": st.slogan[:70],
            "group": atlas.contexts.get(st.context, {}).get("course", "statement"),
            "type": st.role.value if st.role else "Statement",
            "status": st.status.value,
            "context": st.context,
        })
        if st.context in atlas.contexts:
            edges.append({"from": st.id, "to": st.context,
                          "relation": "STATED_IN", "label": "stated in"})

    return JSONResponse({"nodes": nodes, "edges": edges})


@app.get("/api/atlas/ladder")
async def get_ladder(slogan: str):
    """A generalisation ladder: one result across the lattice, ordered by depth."""
    atlas = app.state.atlas
    return JSONResponse({
        "slogan": slogan,
        "rungs": [
            {
                "context": s.context,
                "depth": atlas.depth(s.context),
                "status": s.status.value,
                "slogan": s.slogan,
                "hypotheses": s.hypotheses,
                "witness": s.witness,
            }
            for s in atlas.ladder(slogan)
        ],
    })


@app.get("/api/atlas/context/{context_id}")
async def get_context(context_id: str):
    """Everything the atlas knows about one context."""
    atlas = app.state.atlas
    if context_id not in atlas.contexts:
        raise HTTPException(status_code=404, detail=f"Unknown context '{context_id}'")
    c = atlas.contexts[context_id]
    return JSONResponse({
        "context": c,
        "depth": atlas.depth(context_id),
        "assumes": sorted(atlas.ancestors(context_id)),
        "statements": [s.model_dump(mode="json")
                       for s in atlas.statements_in(context_id)],
        "terms": [t.model_dump(mode="json")
                  for t in atlas.terms.values() if t.context == context_id],
    })


@app.get("/api/atlas/check")
async def atlas_check():
    """Validation gate findings."""
    from src.atlas import validate
    findings = validate.check(app.state.atlas)
    return JSONResponse({"summary": validate.summarise(findings), "findings": findings})


# ---------------------------------------------------------------------------
# Settings & Stats
# ---------------------------------------------------------------------------


@app.get("/api/settings")
async def get_system_settings():
    """Returns current system configuration and index statistics."""
    settings = get_settings()
    vector_stats = app.state.vector_store.get_stats()
    atlas_stats = app.state.atlas.stats()

    return JSONResponse({
        "gemini_model": settings.gemini_model,
        "embed_model": settings.embed_model,
        "ocr_provider": settings.ocr_provider,
        "vault_path": str(settings.vault_path),
        "storage_path": str(settings.storage_path),
        "vector_store": vector_stats,
        "atlas": atlas_stats,
    })


@app.get("/api/courses")
async def get_courses():
    """Returns list of available course names from the vault."""
    settings = get_settings()
    vault_path = settings.vault_path
    courses = []
    if vault_path.exists():
        for child in vault_path.iterdir():
            if child.is_dir() and not child.name.startswith("."):
                courses.append(child.name)
    return JSONResponse({"courses": sorted(courses)})


@app.post("/api/rebuild/graph")
async def rebuild_graph_index():
    """Re-indexes all vault notes into the graph using LLM schema extraction."""
    try:
        from src.atlas.index import index_vault
        result = index_vault(store=app.state.atlas, rebuild=True)
        app.state.query_engine.refresh_node_embeddings()
        return JSONResponse({"status": "success", **result["stats"],
                             "validation": result["validation"]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rebuild/vectors")
async def rebuild_vector_index():
    """Re-embeds all vault notes into the vector store."""
    try:
        settings = get_settings()
        vault_path = settings.vault_path
        if not vault_path.exists():
            return JSONResponse({"status": "success", "chunks": 0})

        manager = ObsidianVaultManager(vault_path)
        notes = manager.get_all_notes()
        vector_store = app.state.vector_store
        total_chunks = 0

        for note in notes:
            content = note.read_text(encoding="utf-8")
            rel = note.relative_to(vault_path)
            course = rel.parts[0] if len(rel.parts) > 1 else "General"

            chunks = chunk_math_markdown(
                content=content,
                course=course,
                source_name=note.name,
            )
            if chunks:
                vector_store.add_chunks(chunks)
                total_chunks += len(chunks)

        return JSONResponse({"status": "success", "chunks": total_chunks})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear")
async def clear_all_databases():
    """Wipes all knowledge graph, KùzuDB, LanceDB vector store, and state tracker databases."""
    try:
        # Clear Graph Indexer & KuzuDB
        app.state.atlas.clear()

        # Wipe LanceDB Vector Store
        try:
            import shutil
            settings = get_settings()
            lancedb_dir = settings.storage_path / "lancedb"
            if lancedb_dir.exists():
                shutil.rmtree(lancedb_dir, ignore_errors=True)
                log.info("LanceDB vector store directory wiped.")
        except Exception as e:
            log.warning(f"Failed to wipe LanceDB directory: {e}")

        return JSONResponse({
            "status": "success",
            "message": "All Knowledge Graph, KùzuDB, LanceDB vector store, and state tracking databases have been completely cleared."
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host="127.0.0.1", port=8000, reload=True)
