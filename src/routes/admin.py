"""System routes: Ollama health, settings/stats, course listing, index
rebuilds, and clear-all."""

import shutil

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from ingestion.app.handwriting.health import OllamaHealthCheck
from shared.config import get_settings
from shared.logger import log
from vector.app.chunker import chunk_math_markdown

router = APIRouter()


@router.get("/api/health/ollama")
async def check_ollama_health():
    """Returns live health telemetry for local Ollama service."""
    checker = OllamaHealthCheck()
    status = checker.check_health()
    return JSONResponse(status)


@router.get("/api/settings")
async def get_system_settings(request: Request):
    """Returns current system configuration and index statistics."""
    settings = get_settings()
    vector_stats = request.app.state.vector_store.get_stats()
    graph = request.app.state.graph_indexer.graph

    return JSONResponse({
        "gemini_model": settings.gemini_model,
        "embed_model": settings.embed_model,
        "ocr_provider": settings.ocr_provider,
        "vault_path": str(settings.vault_path),
        "storage_path": str(settings.storage_path),
        "vector_store": vector_stats,
        "graph": {
            "total_nodes": graph.number_of_nodes(),
            "total_edges": graph.number_of_edges(),
        },
    })


@router.get("/api/courses")
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


@router.post("/api/rebuild/graph")
async def rebuild_graph_index(request: Request):
    """Re-indexes all vault notes into the graph using LLM schema extraction."""
    try:
        indexer = request.app.state.graph_indexer
        result = indexer.build_or_update_index(use_llm=True, force=True)
        request.app.state.query_engine.refresh_node_embeddings()
        return JSONResponse({
            "status": "success",
            "nodes": result.number_of_nodes(),
            "edges": result.number_of_edges(),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/rebuild/vectors")
async def rebuild_vector_index(request: Request):
    """Re-embeds all vault notes into the vector store."""
    try:
        settings = get_settings()
        vault_path = settings.vault_path
        if not vault_path.exists():
            return JSONResponse({"status": "success", "chunks": 0})

        manager = request.app.state.graph_indexer.vault_manager
        notes = manager.get_all_notes()
        vector_store = request.app.state.vector_store
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


@router.post("/api/clear")
async def clear_all_databases(request: Request):
    """Wipes all knowledge graph, KùzuDB, LanceDB vector store, and state tracker databases."""
    try:
        # Clear Graph Indexer & KuzuDB
        request.app.state.graph_indexer.clear_graph()

        # Wipe LanceDB Vector Store
        try:
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
