"""SQLite-backed graph structure: `mentions` and `edges` (plan.md's Target
data model), plus the `concepts.node_attrs_json` bridge column that carries
everything the live graph needs (description, taxonomy, provenance, display
aliases) that plan.md's `concepts` table doesn't have a column for.

Deliberately separate from `authority.py`, which is scoped to identity
resolution (`concepts`/`aliases`) — this module owns graph *structure* and
will keep changing independently as Phase 4/5 land, without touching
resolution. Shares `.storage/concepts.db` with `authority.py` (both use
`CREATE TABLE IF NOT EXISTS`, so either module can be imported first).

`MathGraphIndexer._load_graph`/`save_graph` (indexer.py) are this module's
only caller: `load_graph` is now the store of record read path (graph.json
is a cache/export only), and `index_note`/`backfill_sql_store` are the
write path.
"""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import networkx as nx

from shared.logger import log
from .schema import normalize_domain_casing

_SCHEMA = """
CREATE TABLE IF NOT EXISTS mentions (
    chunk_id        TEXT NOT NULL,
    surface_text    TEXT NOT NULL,
    concept_id      TEXT NOT NULL REFERENCES concepts(id),
    char_span       TEXT,
    PRIMARY KEY (chunk_id, concept_id, surface_text)
);

CREATE TABLE IF NOT EXISTS edges (
    source_id       TEXT NOT NULL REFERENCES concepts(id),
    target_id       TEXT NOT NULL REFERENCES concepts(id),
    relation        TEXT NOT NULL,
    chunk_id        TEXT,
    quote           TEXT,
    origin          TEXT NOT NULL,
    PRIMARY KEY (source_id, target_id, relation, chunk_id)
);
"""

# Tiers `_extract_nodes_pass`/`_extract_edges_pass` can resolve to, in the
# order index_note tries them. "block_parser" means both LLM tiers were
# unavailable or returned nothing usable for that chunk/document, so a note
# indexed on that tier got the regex/heading extractor, not an LLM.
EXTRACTION_METHODS = ("gemini", "ollama", "block_parser")


def _db_path() -> Path:
    from shared.config import get_settings
    return get_settings().storage_path / "concepts.db"


def _ensure_node_attrs_column(conn: sqlite3.Connection) -> None:
    """Additive, idempotent ALTER TABLE — guarded rather than relying on a
    SQLite-version-specific `ADD COLUMN IF NOT EXISTS`, matching this
    codebase's "idempotent, re-runnable" convention elsewhere (authority.py's
    seed functions, migrate_to_identity_layer).
    """
    cols = {row[1] for row in conn.execute("PRAGMA table_info(concepts)")}
    if "node_attrs_json" not in cols:
        conn.execute("ALTER TABLE concepts ADD COLUMN node_attrs_json TEXT")


def _ensure_edges_extraction_method_column(conn: sqlite3.Connection) -> None:
    """Additive, idempotent ALTER TABLE for `edges.extraction_method` — which
    LLM tier (or the block-parser fallback) produced this edge. NULL for rows
    written before this column existed. Same guarded pattern as
    `_ensure_node_attrs_column`.
    """
    cols = {row[1] for row in conn.execute("PRAGMA table_info(edges)")}
    if "extraction_method" not in cols:
        conn.execute("ALTER TABLE edges ADD COLUMN extraction_method TEXT")


@contextmanager
def connect(db_path: Optional[Path] = None):
    path = db_path or _db_path()
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        conn.executescript(_SCHEMA)
        _ensure_node_attrs_column(conn)
        _ensure_edges_extraction_method_column(conn)
        yield conn
        conn.commit()
    finally:
        conn.close()


def insert_mention(
    conn: sqlite3.Connection,
    chunk_id: str,
    surface_text: str,
    concept_id: str,
    char_span: Optional[str] = None,
) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO mentions (chunk_id, surface_text, concept_id, char_span) "
        "VALUES (?, ?, ?, ?)",
        (chunk_id, surface_text, concept_id, char_span),
    )


def insert_edge(
    conn: sqlite3.Connection,
    source_id: str,
    target_id: str,
    relation: str,
    *,
    chunk_id: str,
    quote: Optional[str],
    origin: str = "extracted",
    extraction_method: Optional[str] = None,
) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO edges (source_id, target_id, relation, chunk_id, quote, origin, extraction_method) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (source_id, target_id, relation, chunk_id, quote, origin, extraction_method),
    )


def delete_edge(conn: sqlite3.Connection, source_id: str, target_id: str) -> None:
    """Removes any directed edge between source_id and target_id."""
    conn.execute(
        "DELETE FROM edges WHERE source_id = ? AND target_id = ?",
        (source_id, target_id),
    )


def sync_edges_from_graph(conn: sqlite3.Connection, G: nx.DiGraph) -> None:
    """Syncs SQLite edges table to match the in-memory graph G after DAG pruning."""
    existing_edges = set(conn.execute("SELECT DISTINCT source_id, target_id FROM edges").fetchall())
    graph_edges = set(G.edges())

    # Edges in SQLite that were pruned from G
    stale_edges = existing_edges - graph_edges
    for src, tgt in stale_edges:
        delete_edge(conn, src, tgt)


def upsert_node_attrs(
    conn: sqlite3.Connection,
    concept_id: str,
    *,
    label: str,
    kind: str = "Object",
    role: "str | None" = None,
    taxonomy: "dict | None" = None,
    description: str = "",
    provenance: "list | None" = None,
    aliases: "list | None" = None,
    extraction_method: "str | None" = None,
) -> None:
    """UPDATE-only: the `concepts` row must already exist — every node id
    this is called with has already gone through `authority.resolve_concept`,
    which always inserts the row first.

    `kind` carries the intrinsic MathEntityKind value; `role` carries the
    optional StatementRole (None for most nodes). See docs/vocabulary-diagnosis.md V2.
    `extraction_method` (gemini | ollama | block_parser | None) records which
    tier's output this node's attrs came from — see EXTRACTION_METHODS.
    """
    attrs = {
        "label": label,
        "kind": kind,
        "role": role,
        "taxonomy": taxonomy or {},
        "description": description,
        "provenance": provenance or [],
        "aliases": aliases or [],
        "extraction_method": extraction_method,
    }
    conn.execute(
        "UPDATE concepts SET node_attrs_json = ? WHERE id = ?",
        (json.dumps(attrs, ensure_ascii=False), concept_id),
    )


def clear_all(db_path: Optional[Path] = None) -> None:
    """Clears graph *structure* (mentions, edges, and every concept's
    node_attrs_json — which is what makes a concepts row a graph node, see
    `load_graph`) while deliberately leaving `concepts`/`aliases` identity
    intact. A rebuild after this re-mints the same canonical ids for the
    same surface forms via the existing alias table, rather than starting
    identity resolution over from nothing.
    """
    with connect(db_path) as conn:
        conn.execute("DELETE FROM mentions")
        conn.execute("DELETE FROM edges")
        conn.execute("UPDATE concepts SET node_attrs_json = NULL")


def load_graph(db_path: Optional[Path] = None) -> nx.DiGraph:
    """Rebuilds the in-memory nx.DiGraph from SQLite — the read-path
    counterpart to `export_graph_json`. Nodes come only from `concepts` rows
    that have been given attrs by `index_note`/backfill (`node_attrs_json IS
    NOT NULL`); a `concepts` row created by e.g. a standalone
    `authority-resolve` CLI call, never touched by the graph, correctly does
    not become a graph node.

    Falls back to an empty graph on any read failure, matching the old
    `_load_graph`'s behavior for a missing/corrupt graph.json — this runs at
    graph-service import time (`services/graph/main.py`), so a missing or
    fresh `.storage/concepts.db` must not crash startup.
    """
    G = nx.DiGraph()
    try:
        with connect(db_path) as conn:
            for cid, concepts_label, node_attrs_json in conn.execute(
                "SELECT id, label, node_attrs_json FROM concepts WHERE node_attrs_json IS NOT NULL"
            ):
                attrs = json.loads(node_attrs_json)
                taxonomy = attrs.get("taxonomy")
                if isinstance(taxonomy, dict) and "domain" in taxonomy:
                    taxonomy["domain"] = normalize_domain_casing(taxonomy["domain"])
                # `attrs["label"]` (the graph's own curated display label —
                # e.g. Phase 2's migrate_to_identity_layer picked a
                # best-of-group spelling) always wins over `concepts.label`
                # (authority.py's identity-resolution label, e.g. whichever
                # surface form happened to resolve the concept first — a
                # different, unrelated value). Falls back to the concepts
                # column only for a node whose attrs never recorded a label.
                label = attrs.pop("label", concepts_label)
                # Nodes written before the kind/role split carry entity_type.
                # Map them onto both axes so an un-re-extracted graph loads.
                if "entity_type" in attrs:
                    if "kind" not in attrs:
                        from .schema import LEGACY_TYPE_MAP, MathEntityKind
                        kind, role = LEGACY_TYPE_MAP.get(
                            str(attrs.get("entity_type")), (MathEntityKind.OBJECT, None)
                        )
                        attrs["kind"] = kind.value
                        attrs["role"] = role.value if role else None
                    # Always remove the retired key so it never appears on graph node attrs.
                    attrs.pop("entity_type")
                attrs.setdefault("kind", "Object")
                attrs.setdefault("role", None)
                G.add_node(cid, id=cid, label=label, **attrs)
            for src, tgt, relation, extraction_method in conn.execute(
                "SELECT source_id, target_id, relation, extraction_method FROM edges "
                "GROUP BY source_id, target_id, relation"
            ):
                G.add_edge(src, tgt, relation=relation, label=relation, extraction_method=extraction_method)
        log.info(
            f"Loaded graph from SQLite ({G.number_of_nodes()} nodes, "
            f"{G.number_of_edges()} edges)"
        )
    except Exception as e:
        log.warning(f"Failed to load graph from SQLite ({e}), starting empty.")
    return G


def export_graph_json(graph: nx.DiGraph, path: Path) -> None:
    """Writes `graph.json` as an export/cache format — moved verbatim from
    the old `MathGraphIndexer.save_graph()` body, same field mapping (`type`
    not `entity_type`), so consumers that read graph.json directly off disk
    (`src/server.py`'s `/api/graph`, `scripts/graph_health.py`) see no shape
    change.
    """
    data = {
        "nodes": [
            {
                "id": n,
                "label": graph.nodes[n].get("label", n),
                # `type` carries the KIND, not the retired entity_type. The key
                # name is kept because scripts/graph_health.py and
                # src/server.py's /api/graph parse graph.json directly and
                # expect that key. See CLAUDE.md invariant.
                "type": graph.nodes[n].get("kind", "Object"),
                "role": graph.nodes[n].get("role"),
                "description": graph.nodes[n].get("description", ""),
                "taxonomy": graph.nodes[n].get(
                    "taxonomy",
                    {"domain": "General Math", "subdomain": "General", "topic": n},
                ),
                "provenance": graph.nodes[n].get("provenance", []),
                "aliases": graph.nodes[n].get("aliases", []),
                "extraction_method": graph.nodes[n].get("extraction_method"),
            }
            for n in graph.nodes
        ],
        "edges": [
            {
                "from": u,
                "to": v,
                "source": u,
                "target": v,
                "relation": d.get("relation", "DEPENDS_ON"),
                "label": d.get("relation", "DEPENDS_ON"),
                "extraction_method": d.get("extraction_method"),
            }
            for u, v, d in graph.edges(data=True)
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    log.info(f"Saved graph ({len(data['nodes'])} nodes, {len(data['edges'])} edges)")
