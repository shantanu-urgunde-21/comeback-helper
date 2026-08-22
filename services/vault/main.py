"""Vault service — owns the Obsidian notes and the SHA-256 ingest state.

The vault is the source of truth for the whole system: every other store is
derived from it and rebuildable, while these notes are not (re-OCR costs money
and re-rolls transcription). This service is therefore the only one permitted
to write into the vault directory, and it exposes no delete endpoint.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.manager import ObsidianVaultManager
from shared.config import get_settings
from shared.logger import log

app = FastAPI(title="Comeback Helper — Vault Service")


def manager() -> ObsidianVaultManager:
    settings = get_settings()
    return ObsidianVaultManager(
        vault_path=settings.vault_path,
        state_file_path=settings.storage_path / "vault_state.json",
    )


class PathIn(BaseModel):
    path: str


class WriteIn(BaseModel):
    course: str
    filename: str
    content: str


@app.get("/health")
def health():
    settings = get_settings()
    return {"status": "ok", "vault": str(settings.vault_path),
            "exists": settings.vault_path.exists()}


@app.get("/notes")
def list_notes():
    return {"notes": [str(p) for p in manager().get_all_notes()]}


@app.get("/note")
def read_note(path: str):
    p = Path(path)
    if not p.exists():
        raise HTTPException(404, f"No note at {path}")
    return {"path": path, "content": p.read_text(encoding="utf-8")}


@app.get("/courses")
def list_courses():
    vault = get_settings().vault_path
    if not vault.exists():
        return {"courses": []}
    return {"courses": sorted(c.name for c in vault.iterdir()
                              if c.is_dir() and not c.name.startswith("."))}


@app.post("/note")
def write_note(body: WriteIn):
    """Writes a note via a sidecar, then atomically replaces.

    Same discipline as the original pipeline: a partial write must never
    truncate a good note.
    """
    import os
    vault = get_settings().vault_path
    course_dir = vault / body.course
    course_dir.mkdir(parents=True, exist_ok=True)

    name = body.filename if body.filename.endswith(".md") else f"{body.filename}.md"
    target = course_dir / name
    work = course_dir / f".{name}.partial"

    work.write_text(body.content, encoding="utf-8")
    os.replace(work, target)
    log.info(f"Wrote vault note: {target}")
    return {"status": "success", "path": str(target)}


@app.get("/state/modified")
def is_modified(path: str):
    p = Path(path)
    if not p.exists():
        raise HTTPException(404, f"No note at {path}")
    return {"path": path, "modified": manager().is_file_modified(p)}


@app.post("/state/update")
def update_state(body: PathIn):
    m = manager()
    m.update_file_hash(Path(body.path))
    m.save_state()
    return {"status": "success"}


@app.post("/state/save")
def save_state(body: dict | None = None):
    manager().save_state()
    return {"status": "success"}


@app.post("/state/clear")
def clear_state(body: dict | None = None):
    manager().clear_state()
    return {"status": "success"}
