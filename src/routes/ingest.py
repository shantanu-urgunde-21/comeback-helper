"""POST /api/ingest — PDF upload, OCR, vault write, and optional graph/vector indexing."""

import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from shared.config import get_settings
from shared.logger import log
from vector.app.chunker import chunk_math_markdown

router = APIRouter()


@router.post("/api/ingest")
async def ingest_pdf(
    request: Request,
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
            from ingestion.app.handwriting_provider import HandwritingOCRProvider
            ocr_provider = HandwritingOCRProvider(
                vault_attachments_dir=Path(f"./.storage/vault/{course}/attachments")
            )
        else:  # gemini_vision
            from ingestion.app.gemini_ocr import GeminiOCRProvider
            ocr_provider = GeminiOCRProvider()

        from ingestion.app.pipeline import IngestionPipeline
        pipeline = IngestionPipeline(ocr_provider=ocr_provider)
        target_note_path = pipeline.process_pdf(
            pdf_path=temp_pdf_path,
            course_name=course,
        )

        # --- Optionally update graph index and vector store ---
        index_results = {"graph_indexed": False, "vector_chunks": 0}

        if auto_index:
            graph_indexer = request.app.state.graph_indexer
            vector_store = request.app.state.vector_store

            try:
                graph_indexer.index_note(target_note_path, use_llm=True)
                graph_indexer.save_graph()
                index_results["graph_indexed"] = True
                log.info(f"Graph index updated with note: {target_note_path.name}")
                # Refresh semantic node embeddings in the query engine
                request.app.state.query_engine.refresh_node_embeddings()
            except Exception as e:
                log.warning(f"Graph indexing skipped for {target_note_path.name}: {e}")

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
