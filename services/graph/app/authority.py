"""The identity authority: MSC2020 taxonomy codes + on-demand Wikidata concept
lookup, backed by a local SQLite corpus that grows as concepts are resolved.

This is Phase 0 of plan.md, revised per the coverage spike (see
docs/diagnosis.md and the session that measured it): exact-label Wikidata
coverage on real course concepts is ~15-21%, so bulk-seeding a "Wikidata
mathematics subset" is low value. Instead this module queries Wikidata live,
exactly once per normalized surface form, and caches the result (hit or miss)
locally — the corpus is what accumulates from usage, not from a one-time
import.

Nothing here is wired into MathGraphIndexer yet. That is Phase 1: making
`_resolve_entity` a lookup against this module instead of an embedding
similarity check. This module is deliberately usable and testable standalone
first.
"""

import csv
import hashlib
import json
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .schema import normalize

_SCHEMA = """
CREATE TABLE IF NOT EXISTS concepts (
    id            TEXT PRIMARY KEY,
    label         TEXT NOT NULL,
    msc_code      TEXT,
    authority     TEXT NOT NULL,
    authority_ver TEXT,
    status        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS aliases (
    surface_norm  TEXT NOT NULL,
    concept_id    TEXT NOT NULL REFERENCES concepts(id),
    scope         TEXT NOT NULL,
    scope_ref     TEXT,
    PRIMARY KEY (surface_norm, scope, scope_ref)
);

CREATE TABLE IF NOT EXISTS msc_taxonomy (
    code          TEXT PRIMARY KEY,
    text          TEXT NOT NULL,
    description   TEXT
);

CREATE TABLE IF NOT EXISTS msc_meta (
    id            INTEGER PRIMARY KEY CHECK (id = 1),
    source        TEXT,
    row_count     INTEGER,
    loaded_at     TEXT
);

-- Every Wikidata query result, hit or miss, keyed by the humanized label we
-- actually sent. This is the on-demand cache: a normalized key only ever
-- crosses the network once. candidates_json holds the raw top-N hits
-- (exact or not) so a miss can populate the review queue without a second
-- round trip.
CREATE TABLE IF NOT EXISTS wikidata_lookup_cache (
    query_label     TEXT PRIMARY KEY,
    qid             TEXT,
    label           TEXT,
    description     TEXT,
    candidates_json TEXT,
    checked_at      TEXT NOT NULL
);

-- Every CUST_ mint, for a human (or a pre-triage agent) to later confirm,
-- merge into an existing concept, or promote to a real authority entry.
-- Fuzzy Wikidata candidates are proposed here, never auto-committed.
CREATE TABLE IF NOT EXISTS review_queue (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    concept_id      TEXT NOT NULL,
    surface_text    TEXT NOT NULL,
    normalized_key  TEXT NOT NULL,
    scope           TEXT,
    scope_ref       TEXT,
    candidates_json TEXT,
    status          TEXT NOT NULL DEFAULT 'open',
    created_at      TEXT NOT NULL
);
"""


def _db_path() -> Path:
    from shared.config import get_settings
    return get_settings().storage_path / "concepts.db"


@contextmanager
def _connect(db_path: Optional[Path] = None):
    path = db_path or _db_path()
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = OFF")  # sqlite FKs aren't enforced across INSERTs we batch
    try:
        conn.executescript(_SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# MSC2020 — bulk-seeded once, re-runnable, ~6.6k rows
# ---------------------------------------------------------------------------

MSC2020_URL = "https://msc2020.org/MSC_2020.csv"


def fetch_msc2020_csv(dest: Path) -> Path:
    """Downloads the canonical MSC2020 CSV (tab-delimited) to `dest`."""
    req = urllib.request.Request(
        MSC2020_URL, headers={"User-Agent": "comeback-helper/0.1 (local research tool)"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        dest.write_bytes(r.read())
    return dest


def seed_msc2020(csv_path: Optional[Path] = None, db_path: Optional[Path] = None) -> dict:
    """Loads MSC2020 codes into `msc_taxonomy`. Idempotent — safe to re-run;
    re-running re-imports every row (INSERT OR REPLACE) rather than skipping,
    so a newer CSV drop updates descriptions without orphaning codes already
    referenced by concepts.msc_code.
    """
    fetched = False
    if csv_path is None:
        csv_path = _db_path().parent / "MSC_2020.csv"
        if not csv_path.exists():
            fetch_msc2020_csv(csv_path)
            fetched = True

    rows = []
    # msc2020.org serves this file as cp1252, not utf-8 (accented author/place
    # names like "Picard-Lindelof" decode wrong otherwise).
    with open(csv_path, encoding="cp1252", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)
        for row in reader:
            if len(row) < 2:
                continue
            code, text = row[0], row[1]
            description = row[2] if len(row) > 2 else text
            rows.append((code, text, description))

    with _connect(db_path) as conn:
        conn.executemany(
            "INSERT OR REPLACE INTO msc_taxonomy (code, text, description) VALUES (?, ?, ?)",
            rows,
        )
        conn.execute(
            "INSERT OR REPLACE INTO msc_meta (id, source, row_count, loaded_at) VALUES (1, ?, ?, ?)",
            (str(csv_path), len(rows), datetime.now(timezone.utc).isoformat()),
        )

    return {"rows_loaded": len(rows), "fetched": fetched, "csv_path": str(csv_path)}


# ---------------------------------------------------------------------------
# Wikidata — on-demand exact lookup, cached
# ---------------------------------------------------------------------------

WIKIDATA_API = "https://www.wikidata.org/w/api.php"


def humanize(surface: str) -> str:
    """Turns a stored kebab/snake surface form into a queryable label.

    Wikidata labels never contain '_' or '-' as word separators, so a raw
    stored id (e.g. "picard-lindelof-theorem") will never exact-match — it
    has to be turned into words first. Measured on the live graph: this
    alone moved 5/92 concepts from "no match" into "exact match" in the
    coverage spike.
    """
    return re.sub(r"[-_]", " ", surface).strip()


@dataclass
class WikidataMatch:
    qid: str
    label: str
    description: str


def _wikidata_search(label: str, limit: int = 5, retries: int = 5) -> dict:
    url = WIKIDATA_API + "?" + urllib.parse.urlencode({
        "action": "wbsearchentities",
        "search": label,
        "language": "en",
        "format": "json",
        "limit": limit,
    })
    req = urllib.request.Request(url, headers={"User-Agent": "comeback-helper/0.1 (local research tool)"})
    backoff = 2.0
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise


def _cached_lookup(conn, query_label: str) -> Optional[tuple]:
    return conn.execute(
        "SELECT qid, label, description, candidates_json FROM wikidata_lookup_cache WHERE query_label = ?",
        (query_label,),
    ).fetchone()


def resolve_wikidata_exact(surface_text: str, db_path: Optional[Path] = None) -> Optional[WikidataMatch]:
    """Exact-label Wikidata lookup, cached by the humanized query string.

    Never returns a fuzzy/close match — the plan is explicit that fuzzy
    matching proposes, it never commits. A cached miss (qid IS NULL) short-
    circuits future lookups of the same string without a network call.
    """
    query_label = humanize(surface_text)

    with _connect(db_path) as conn:
        cached = _cached_lookup(conn, query_label)
        if cached is not None:
            qid, label, description, _ = cached
            return WikidataMatch(qid, label, description) if qid else None

        result = _wikidata_search(query_label)
        hits = result.get("search", [])
        exact = next(
            (h for h in hits if h.get("label", "").strip().lower() == query_label.strip().lower()),
            None,
        )
        candidates = [
            {"qid": h["id"], "label": h.get("label", ""), "description": h.get("description", "")}
            for h in hits[:5]
        ]

        conn.execute(
            "INSERT OR REPLACE INTO wikidata_lookup_cache "
            "(query_label, qid, label, description, candidates_json, checked_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                query_label,
                exact["id"] if exact else None,
                exact.get("label") if exact else None,
                exact.get("description", "") if exact else None,
                json.dumps(candidates),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    return WikidataMatch(exact["id"], exact.get("label", query_label), exact.get("description", "")) if exact else None


# ---------------------------------------------------------------------------
# The resolution ladder: document -> course -> global -> mint.
#
# Narrowest scope first, never a similarity threshold. A hit at document or
# course scope means "this surface form already means something specific
# here" and short-circuits before ever asking Wikidata — which is what keeps
# an overloaded symbol ('T' as a linear map in one lecture, a topology in
# another) from being flattened into one global identity. Only a genuine
# authority match (Wikidata) is written back at global scope; a CUST_ mint
# is only ever bound at the scope it was minted in; a *later* mint of the
# exact same normalized spelling in an unrelated scope will still collide on
# the same CUST_<hash> id (the hash is a pure function of the normalized
# key), which is an accepted, explicitly out-of-scope-for-automation case —
# that class of collision is what the review queue is for.
# ---------------------------------------------------------------------------


def _cust_id(normalized_key: str) -> str:
    digest = hashlib.sha256(normalized_key.encode("utf-8")).hexdigest()[:12]
    return f"CUST_{digest}"


def _alias_lookup(conn, key: str, scope: str, scope_ref: Optional[str]) -> Optional[str]:
    if scope != "global" and scope_ref is None:
        return None
    row = conn.execute(
        "SELECT concept_id FROM aliases WHERE surface_norm = ? AND scope = ? AND scope_ref IS ?",
        (key, scope, scope_ref),
    ).fetchone()
    return row[0] if row else None


def _bind_alias(conn, key: str, concept_id: str, scope: str, scope_ref: Optional[str]) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO aliases (surface_norm, concept_id, scope, scope_ref) VALUES (?, ?, ?, ?)",
        (key, concept_id, scope, scope_ref),
    )


def _queue_for_review(conn, concept_id: str, surface_text: str, key: str,
                       scope: Optional[str], scope_ref: Optional[str]) -> None:
    cached = _cached_lookup(conn, humanize(surface_text))
    candidates_json = cached[3] if cached else "[]"
    conn.execute(
        "INSERT INTO review_queue "
        "(concept_id, surface_text, normalized_key, scope, scope_ref, candidates_json, status, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, 'open', ?)",
        (concept_id, surface_text, key, scope, scope_ref, candidates_json,
         datetime.now(timezone.utc).isoformat()),
    )


def resolve_concept(
    surface_text: str,
    *,
    document_id: Optional[str] = None,
    course: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> str:
    """Resolves a surface form to a concept id via the full scope ladder.

    `document_id` and `course` are the caller's own identifiers (e.g. a note
    path and a course folder name) — this function does not interpret them
    beyond using them as scope_ref keys, so callers must pass the same value
    consistently for the same document/course across calls.
    """
    key = normalize(surface_text)
    if not key:
        key = surface_text.strip().lower() or "unknown"

    with _connect(db_path) as conn:
        for scope, scope_ref in (("document", document_id), ("course", course)):
            hit = _alias_lookup(conn, key, scope, scope_ref)
            if hit:
                return hit

        global_hit = _alias_lookup(conn, key, "global", None)
        if global_hit:
            concept_id = global_hit
        else:
            match = resolve_wikidata_exact(surface_text, db_path=db_path)
            if match:
                conn.execute(
                    "INSERT OR REPLACE INTO concepts (id, label, authority, authority_ver, status) "
                    "VALUES (?, ?, 'wikidata', ?, 'confirmed')",
                    (match.qid, match.label, datetime.now(timezone.utc).date().isoformat()),
                )
                _bind_alias(conn, key, match.qid, "global", None)
                concept_id = match.qid
            else:
                concept_id = _cust_id(key)
                is_new = conn.execute(
                    "SELECT 1 FROM concepts WHERE id = ?", (concept_id,)
                ).fetchone() is None
                conn.execute(
                    "INSERT OR IGNORE INTO concepts (id, label, authority, authority_ver, status) "
                    "VALUES (?, ?, 'local', NULL, 'provisional')",
                    (concept_id, surface_text),
                )
                if is_new:
                    if document_id is not None:
                        review_scope, review_ref = "document", document_id
                    elif course is not None:
                        review_scope, review_ref = "course", course
                    else:
                        review_scope, review_ref = None, None
                    _queue_for_review(conn, concept_id, surface_text, key, review_scope, review_ref)

        for scope, scope_ref in (("document", document_id), ("course", course)):
            if scope_ref is not None:
                _bind_alias(conn, key, concept_id, scope, scope_ref)

    return concept_id


def get_or_create_concept(surface_text: str, db_path: Optional[Path] = None) -> str:
    """Global-scope-only convenience wrapper over `resolve_concept`, for
    callers with no document/course context (e.g. manual CLI testing)."""
    return resolve_concept(surface_text, db_path=db_path)


def register_alias(surface_text: str, concept_id: str, db_path: Optional[Path] = None) -> None:
    """Binds a surface form to an *already-resolved* concept id at global
    scope, without going through the ladder or touching Wikidata.

    For a caller that already knows two spellings are the same concept —
    e.g. a graph migration folding an existing node's own `aliases` list
    (previously write-only, see docs/diagnosis.md D2) onto the node's newly
    resolved canonical id.
    """
    key = normalize(surface_text)
    if not key:
        return
    with _connect(db_path) as conn:
        _bind_alias(conn, key, concept_id, "global", None)


def stats(db_path: Optional[Path] = None) -> dict:
    with _connect(db_path) as conn:
        msc_count = conn.execute("SELECT COUNT(*) FROM msc_taxonomy").fetchone()[0]
        concept_count = conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
        wikidata_concepts = conn.execute(
            "SELECT COUNT(*) FROM concepts WHERE authority = 'wikidata'"
        ).fetchone()[0]
        local_concepts = conn.execute(
            "SELECT COUNT(*) FROM concepts WHERE authority = 'local'"
        ).fetchone()[0]
        alias_count = conn.execute("SELECT COUNT(*) FROM aliases").fetchone()[0]
        cache_hits = conn.execute(
            "SELECT COUNT(*) FROM wikidata_lookup_cache WHERE qid IS NOT NULL"
        ).fetchone()[0]
        cache_misses = conn.execute(
            "SELECT COUNT(*) FROM wikidata_lookup_cache WHERE qid IS NULL"
        ).fetchone()[0]
        review_open = conn.execute(
            "SELECT COUNT(*) FROM review_queue WHERE status = 'open'"
        ).fetchone()[0]
    return {
        "msc_codes": msc_count,
        "concepts": concept_count,
        "concepts_wikidata": wikidata_concepts,
        "concepts_local": local_concepts,
        "aliases": alias_count,
        "wikidata_cache_hits": cache_hits,
        "wikidata_cache_misses": cache_misses,
        "review_queue_open": review_open,
    }
