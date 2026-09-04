"""GET /api/vault, /api/vault/note, /api/graph — vault browsing and the
graph.json-with-wikilink-fallback the frontend graph view reads."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from shared.config import get_settings

router = APIRouter()


@router.get("/api/vault")
async def get_vault_notes(request: Request):
    """Returns list of course folders and notes in the Obsidian Vault."""
    settings = get_settings()
    vault_path = settings.vault_path

    if not vault_path.exists():
        return JSONResponse({"vault": {}})

    manager = request.app.state.graph_indexer.vault_manager
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


@router.get("/api/vault/note")
async def get_vault_note_content(path: str):
    """Returns one vault note's raw markdown content.

    `path` is a full path as returned by /api/vault — round-tripped through
    the client rather than trusted, so it's resolved and checked against
    the configured vault directory before reading (path-traversal guard;
    without it a crafted `path` could read any file the server process can).
    """
    settings = get_settings()
    vault_path = settings.vault_path

    try:
        note_path = Path(path).resolve()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

    if note_path.suffix.lower() != ".md" or not note_path.is_relative_to(vault_path):
        raise HTTPException(status_code=403, detail="Path is outside the configured vault")
    if not note_path.exists():
        raise HTTPException(status_code=404, detail="Note not found")

    try:
        content = note_path.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read note: {e}")

    return JSONResponse({"title": note_path.stem, "path": str(note_path), "content": content})


@router.get("/api/graph")
async def get_graph_data(request: Request):
    """
    Returns nodes and edges from the MathGraphIndexer or Obsidian
    Vault wikilinks as a fallback.
    """
    settings = get_settings()
    graph_file = settings.storage_path / "graph.json"

    if graph_file.exists():
        try:
            data = json.loads(graph_file.read_text(encoding="utf-8"))
            if data.get("nodes"):
                return JSONResponse(data)
        except Exception:
            pass

    manager = request.app.state.graph_indexer.vault_manager
    notes = manager.get_all_notes()

    nodes: list[dict] = []
    edges: list[dict] = []
    node_set: set[str] = set()

    for note in notes:
        node_id = note.stem
        if node_id not in node_set:
            node_set.add(node_id)
            course_group = (
                note.parent.name
                if note.parent != settings.vault_path
                else "General"
            )
            nodes.append({
                "id": node_id,
                "label": node_id,
                "group": course_group,
                "type": "Note",
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
                    "type": "Concept",
                })
            edges.append({
                "from": node_id,
                "to": link_target,
                "label": "links_to",
            })

    return JSONResponse({"nodes": nodes, "edges": edges})
