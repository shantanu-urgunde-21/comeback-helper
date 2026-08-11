"""
Atlas store — the context lattice plus everything indexed against it.

Persists to `.storage/atlas.json`. The lattice itself is *not* stored here: it
ships as curated data in `src/atlas/lattice/data/contexts.json` and is shared by
every user, which is the point of a spine.
"""

import json
from pathlib import Path
from typing import Iterable, Optional

import networkx as nx

from src.config import get_settings
from src.logger import log
from src.atlas.schema import (
    ProvenanceKind, Statement, Status, Term, Witness,
)

LATTICE_FILE = Path(__file__).parent / "lattice" / "data" / "contexts.json"


class AtlasStore:
    """
    Holds contexts (read-only spine), terms, statements and witnesses.

    Exposes `.graph` as a NetworkX view so retrieval can traverse the atlas the
    way it used to traverse the old concept graph.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.settings = get_settings()
        self.storage_path = storage_path or self.settings.storage_path
        self.file = self.storage_path / "atlas.json"

        self.contexts: dict[str, dict] = {}
        self.extends: dict[str, list[str]] = {}
        self.over: dict[str, list[str]] = {}
        self.terms: dict[str, Term] = {}
        self.statements: dict[str, Statement] = {}
        self.witnesses: dict[str, Witness] = {}

        self._load_lattice()
        self._load()
        log.info(
            f"AtlasStore ready: {len(self.contexts)} contexts, "
            f"{len(self.statements)} statements, {len(self.terms)} terms."
        )

    # ------------------------------------------------------------------
    # Lattice (read-only spine)
    # ------------------------------------------------------------------

    def _load_lattice(self):
        if not LATTICE_FILE.exists():
            log.warning(f"No context lattice at {LATTICE_FILE}; run src.atlas.lattice.build")
            return
        data = json.loads(LATTICE_FILE.read_text(encoding="utf-8"))
        for c in data["contexts"]:
            self.contexts[c["id"]] = c
            self.extends[c["id"]] = c.get("extends", [])
            self.over[c["id"]] = c.get("over", [])

    def ancestors(self, context_id: str) -> set[str]:
        """Every context this one assumes, transitively (upward in the lattice)."""
        seen, stack = set(), [context_id]
        while stack:
            cur = stack.pop()
            for p in self.extends.get(cur, []):
                if p not in seen:
                    seen.add(p)
                    stack.append(p)
        return seen

    def descendants(self, context_id: str) -> set[str]:
        seen = set()
        for cid in self.contexts:
            if context_id in self.ancestors(cid):
                seen.add(cid)
        return seen

    def depth(self, context_id: str) -> int:
        G = nx.DiGraph()
        for c, ps in self.extends.items():
            G.add_node(c)
            for p in ps:
                G.add_edge(c, p)
        if context_id not in G:
            return 0
        d = 0
        for root in [n for n in G if G.out_degree(n) == 0]:
            for path in nx.all_simple_paths(G, context_id, root):
                d = max(d, len(path) - 1)
        return d

    def visible_terms(self, context_id: str) -> set[str]:
        """Terms usable in a context: defined there or in any ancestor."""
        allowed = {context_id} | self.ancestors(context_id)
        return {t.name.lower() for t in self.terms.values() if t.context in allowed}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_terms(self, terms: Iterable[Term]):
        for t in terms:
            existing = self.terms.get(t.key)
            if existing and existing.provenance_kind == ProvenanceKind.USER:
                continue  # never overwrite a user correction
            if existing:
                existing.provenance.extend(t.provenance)
                for a in t.aliases:
                    if a not in existing.aliases:
                        existing.aliases.append(a)
            else:
                self.terms[t.key] = t

    def add_statements(self, statements: Iterable[Statement]):
        for s in statements:
            existing = self.statements.get(s.id)
            if existing and existing.provenance_kind == ProvenanceKind.USER:
                continue
            if existing:
                existing.provenance.extend(s.provenance)
            else:
                self.statements[s.id] = s

    def add_witnesses(self, witnesses: Iterable[Witness]):
        for w in witnesses:
            self.witnesses.setdefault(w.id, w)

    # ------------------------------------------------------------------
    # Derived views — the relations Model A had to extract
    # ------------------------------------------------------------------

    def ladder(self, slogan_key: str) -> list[Statement]:
        """
        A generalisation ladder: the same slogan across the lattice, ordered by
        depth. Derived, not extracted — so it does not inherit the ~75%
        relation-extraction error rate.
        """
        key = slogan_key.strip().lower()
        hits = [s for s in self.statements.values() if key in s.slogan.lower()]
        return sorted(hits, key=lambda s: self.depth(s.context))

    def disambiguations(self) -> dict[str, list[Term]]:
        """Terms sharing a name across different contexts — free, by construction."""
        by_name: dict[str, list[Term]] = {}
        for t in self.terms.values():
            by_name.setdefault(t.name.lower(), []).append(t)
        return {n: ts for n, ts in by_name.items() if len(ts) > 1}

    def statements_in(self, context_id: str, include_ancestors: bool = False) -> list[Statement]:
        allowed = {context_id} | (self.ancestors(context_id) if include_ancestors else set())
        return [s for s in self.statements.values() if s.context in allowed]

    @property
    def graph(self) -> nx.DiGraph:
        """
        NetworkX view over contexts and statements, so the retrieval engine can
        traverse the atlas the way it traversed the old concept graph.
        """
        G = nx.DiGraph()
        for cid, c in self.contexts.items():
            G.add_node(cid, entity_type="Context", description=c.get("name", cid),
                       course=c.get("course", ""))
        for cid, ps in self.extends.items():
            for p in ps:
                if p in G:
                    G.add_edge(cid, p, relation="EXTENDS")
        for cid, ps in self.over.items():
            for p in ps:
                if p in G:
                    G.add_edge(cid, p, relation="OVER")
        for s in self.statements.values():
            G.add_node(s.id, entity_type=(s.role.value if s.role else "Statement"),
                       description=s.slogan, status=s.status.value)
            if s.context in G:
                G.add_edge(s.id, s.context, relation="STATED_IN")
        for t in self.terms.values():
            G.add_node(t.key, entity_type="Term", description=t.definition_latex[:160])
            if t.context in G:
                G.add_edge(t.key, t.context, relation="DEFINED_IN")
        return G

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self):
        if not self.file.exists():
            return
        try:
            d = json.loads(self.file.read_text(encoding="utf-8"))
            self.terms = {t["name"] + "@" + t["context"]: Term(**t) for t in d.get("terms", [])}
            self.statements = {s["id"]: Statement(**s) for s in d.get("statements", [])}
            self.witnesses = {w["id"]: Witness(**w) for w in d.get("witnesses", [])}
        except Exception as e:
            log.warning(f"Could not load atlas.json ({e}); starting empty.")

    def save(self):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "terms": [t.model_dump(mode="json") for t in self.terms.values()],
            "statements": [s.model_dump(mode="json") for s in self.statements.values()],
            "witnesses": [w.model_dump(mode="json") for w in self.witnesses.values()],
        }
        self.file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        log.info(
            f"Saved atlas: {len(self.statements)} statements, "
            f"{len(self.terms)} terms, {len(self.witnesses)} witnesses."
        )

    def clear(self):
        self.terms.clear()
        self.statements.clear()
        self.witnesses.clear()
        if self.file.exists():
            self.file.unlink()
        log.info("Atlas cleared (lattice spine untouched).")

    def stats(self) -> dict:
        by_status: dict[str, int] = {}
        for s in self.statements.values():
            by_status[s.status.value] = by_status.get(s.status.value, 0) + 1
        by_ctx: dict[str, int] = {}
        for s in self.statements.values():
            by_ctx[s.context] = by_ctx.get(s.context, 0) + 1
        return {
            "contexts": len(self.contexts),
            "statements": len(self.statements),
            "terms": len(self.terms),
            "witnesses": len(self.witnesses),
            "by_status": by_status,
            "contexts_used": len(by_ctx),
            "top_contexts": sorted(by_ctx.items(), key=lambda kv: -kv[1])[:8],
        }
