import os
import shutil
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from src.config import get_settings
from src.vault.manager import ObsidianVaultManager
from src.logger import log

app = FastAPI(title="Comeback Helper - Math Knowledge Base API")

# Setup static files directory
STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class QueryRequest(BaseModel):
    prompt: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>Comeback Helper Server Running</h1><p>Static index.html building...</p>")
    return HTMLResponse(index_file.read_text(encoding="utf-8"))

@app.post("/api/ingest")
async def ingest_pdf(file: UploadFile = File(...), course: str = Form(...)):
    """
    Endpoint to upload a PDF file, run Gemini Vision OCR, and save Markdown to Obsidian Vault.
    """
    log.info(f"Received API ingestion request for file '{file.filename}' in course '{course}'")
    if not file.filename.endswith(".pdf"):
        log.warning(f"Rejected non-PDF upload attempt: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_dir = Path("./temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_pdf_path = temp_dir / file.filename

    try:
        with open(temp_pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Lazy load pipeline
        from src.ingestion.pipeline import IngestionPipeline
        pipeline = IngestionPipeline()
        target_note_path = pipeline.process_pdf(
            pdf_path=temp_pdf_path,
            course_name=course
        )

        return JSONResponse({
            "status": "success",
            "filename": file.filename,
            "course": course,
            "note_path": str(target_note_path)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_pdf_path.exists():
            temp_pdf_path.unlink()

@app.post("/api/query")
async def query_knowledge_base(request: QueryRequest):
    """
    Endpoint to ask mathematical questions to the Knowledge Graph RAG engine.
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Query prompt cannot be empty.")

    try:
        # Lazy load query engine
        from src.retrieval.engine import MathQueryEngine
        engine = MathQueryEngine()
        answer = engine.query(request.prompt)
        return JSONResponse({"status": "success", "answer": answer})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vault")
async def get_vault_notes():
    """
    Returns list of course folders and notes in the Obsidian Vault.
    """
    settings = get_settings()
    manager = ObsidianVaultManager(settings.vault_path)
    notes = manager.get_all_notes()

    vault_data = {}
    for note in notes:
        try:
            rel = note.relative_to(settings.vault_path)
            parts = rel.parts
            course = parts[0] if len(parts) > 1 else "General"
        except Exception:
            course = "General"

        if course not in vault_data:
            vault_data[course] = []
        vault_data[course].append({
            "title": note.stem,
            "path": str(note),
            "size": note.stat().st_size
        })

    return JSONResponse({"vault": vault_data})

@app.get("/api/graph")
async def get_graph_data():
    """
    Extracts nodes and edges from MathGraphIndexer (.storage/graph.json) or Obsidian Vault wikilinks.
    """
    settings = get_settings()
    graph_file = settings.storage_path / "graph.json"

    # 1. Check for persisted MathPropertyGraph JSON from MathGraphIndexer
    if graph_file.exists():
        try:
            import json
            data = json.loads(graph_file.read_text(encoding="utf-8"))
            if data.get("nodes"):
                return JSONResponse(data)
        except Exception:
            pass

    # 2. Fallback to Obsidian Vault Wikilink Graph
    manager = ObsidianVaultManager(settings.vault_path)
    notes = manager.get_all_notes()

    nodes = []
    edges = []
    node_set = set()

    for note in notes:
        node_id = note.stem
        if node_id not in node_set:
            node_set.add(node_id)
            course_group = note.parent.name if note.parent != settings.vault_path else "General"
            nodes.append({
                "id": node_id,
                "label": node_id,
                "group": course_group,
                "type": "Note"
            })

        content = note.read_text(encoding="utf-8", errors="ignore")
        wikilinks = manager.extract_wikilinks(content)
        for link in wikilinks:
            link_target = Path(link).stem
            if link_target not in node_set:
                node_set.add(link_target)
                nodes.append({
                    "id": link_target,
                    "label": link_target,
                    "group": "Concept",
                    "type": "Concept"
                })
            edges.append({
                "from": node_id,
                "to": link_target,
                "label": "links_to"
            })

    return JSONResponse({"nodes": nodes, "edges": edges})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host="127.0.0.1", port=8000, reload=True)
