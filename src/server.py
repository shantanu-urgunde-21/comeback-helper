import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from src.config import get_settings
from src.vault.manager import ObsidianVaultManager
from src.ingestion.handwriting.health import OllamaHealthCheck
from src.logger import log

app = FastAPI(title="Comeback Helper - Math Knowledge Base & Ingestion API")

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

@app.get("/api/health/ollama")
async def check_ollama_health():
    """
    Returns live health telemetry for local Ollama service and qwen2.5vl:3b VLM model.
    """
    checker = OllamaHealthCheck()
    status = checker.check_health()
    return JSONResponse(status)

@app.post("/api/ingest")
async def ingest_pdf(
    file: UploadFile = File(...),
    course: str = Form(...),
    ocr_mode: Optional[str] = Form("local_handwriting")
):
    """
    Endpoint to upload a PDF file, run selected OCR provider (local Ollama Qwen2.5-VL or Gemini Vision),
    and save structured Markdown note to Obsidian Vault.
    """
    log.info(f"Received API ingestion request for file '{file.filename}' in course '{course}' (Mode: {ocr_mode})")
    if not file.filename.endswith(".pdf"):
        log.warning(f"Rejected non-PDF upload attempt: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_dir = Path("./temp_uploads")
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
        else: # gemini_vision
            from src.ingestion.gemini_ocr import GeminiOCRProvider
            ocr_provider = GeminiOCRProvider()

        from src.ingestion.pipeline import IngestionPipeline
        pipeline = IngestionPipeline(ocr_provider=ocr_provider)
        target_note_path = pipeline.process_pdf(
            pdf_path=temp_pdf_path,
            course_name=course
        )

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
            "content": note_text
        })

    except Exception as e:
        log.error(f"Ingestion error: {e}")
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

    if graph_file.exists():
        try:
            import json
            data = json.loads(graph_file.read_text(encoding="utf-8"))
            if data.get("nodes"):
                return JSONResponse(data)
        except Exception:
            pass

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
