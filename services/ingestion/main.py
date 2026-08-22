"""Ingestion service — PDF to Markdown.

The only service that touches OCR models, and the only one whose output is
irreplaceable: a vault note cannot be regenerated for free, because re-OCR
costs money and re-rolls the transcription. Everything downstream is
rebuildable from what this service produces.

It writes the note through the vault service rather than to disk directly, so
that "who is allowed to write to the vault" has exactly one answer.
"""

import shutil
import tempfile
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from shared.logger import log

app = FastAPI(title="Comeback Helper — Ingestion Service")

VAULT_URL = "http://vault:8001"


def build_pipeline(ocr_mode: str):
    """Provider switch. New OCR providers subclass BaseOCRProvider and are
    registered here."""
    from app.pipeline import IngestionPipeline

    if ocr_mode == "local_handwriting":
        from app.handwriting_provider import HandwritingOCRProvider
        return IngestionPipeline(ocr_provider=HandwritingOCRProvider())
    if ocr_mode == "marker":
        from app.marker_provider import MarkerOCRProvider
        return IngestionPipeline(ocr_provider=MarkerOCRProvider())
    if ocr_mode == "local":
        from app.local_ocr import LightOnOCRProvider
        return IngestionPipeline(ocr_provider=LightOnOCRProvider())
    from app.gemini_ocr import GeminiOCRProvider
    return IngestionPipeline(ocr_provider=GeminiOCRProvider())


class HealthOut(BaseModel):
    status: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/ollama")
def ollama_health():
    from app.handwriting.health import OllamaHealthCheck
    return OllamaHealthCheck().check_health()


@app.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
    course: str = Form(...),
    ocr_mode: str = Form("gemini_vision"),
    dpi: int = Form(200),
):
    """OCR a PDF and hand the Markdown to the vault service.

    Does not index. Indexing is the graph and vector services' job, triggered
    by whoever orchestrates the pipeline — keeping this service responsible
    for exactly one transformation.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")

    tmp_dir = Path(tempfile.mkdtemp())
    tmp_pdf = tmp_dir / file.filename
    try:
        with open(tmp_pdf, "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        pipeline = build_pipeline(ocr_mode)
        note_path = pipeline.process_pdf(pdf_path=tmp_pdf, course_name=course)
        content = Path(note_path).read_text(encoding="utf-8")

        # Hand off to the vault service — the single writer.
        r = requests.post(
            f"{VAULT_URL}/note",
            json={"course": course, "filename": Path(note_path).name, "content": content},
            timeout=120,
        )
        r.raise_for_status()
        stored = r.json()

        log.info(f"Ingested {file.filename} -> {stored['path']}")
        return {"status": "success", "filename": file.filename, "course": course,
                "note_path": stored["path"], "indexed": False}
    except Exception as e:
        log.error(f"Ingestion failed: {e}")
        raise HTTPException(500, str(e))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
