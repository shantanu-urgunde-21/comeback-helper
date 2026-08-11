"""
Merge independently transcribed edge sets by vote, then validate.

Agreement between independent sources is evidence; disagreement is a targeted
review queue. For a lattice this size the queue is small enough to clear by
hand, which is what makes the lattice trustworthy enough to be a spine.
"""

from collections import defaultdict
from typing import Iterable

import networkx as nx

from src.logger import log
from src.atlas.lattice.seed import ANCHORS, ALL_CONTEXTS, OVER_SEED, is_over

Edge = tuple[str, str]  # (child, parent) — child extends parent


def tally(sources: dict[str, Iterable[Edge]]) -> dict[Edge, list[str]]:
    votes: dict[Edge, list[str]] = defaultdict(list)
    for name, edges in sources.items():
        for e in edges:
            votes[e].append(name)
    return dict(votes)


def anchor_report(edges: set[Edge]) -> dict:
    """
    Checks the hand-written certainties. Direction inversion is the dominant
    failure mode, so an inverted anchor is reported separately from a missing
    one — a miss is a coverage problem, an inversion is a correctness problem.
    """
    found, missing, inverted = [], [], []
    for child, parent in ANCHORS:
        if (child, parent) in edges:
            found.append(f"{child} -> {parent}")
        elif (parent, child) in edges:
            inverted.append(f"{parent} -> {child}  (should be {child} -> {parent})")
        else:
            missing.append(f"{child} -> {parent}")
    return {
        "total": len(ANCHORS),
        "found": len(found),
        "missing": missing,
        "inverted": inverted,
        "pass": not inverted,
    }


def break_cycles(
    edges: set[Edge], votes: dict[Edge, list[str]]
) -> tuple[set[Edge], list[dict]]:
    """
    A lattice must be acyclic. Drops the *weakest* edge in each cycle — fewest
    supporting sources, never an anchor — and reports both the cycle and what
    was dropped. Dropping the last edge found (the naive approach) removes
    correct edges as often as wrong ones.
    """
    anchors = set(ANCHORS)
    G = nx.DiGraph()
    G.add_edges_from(edges)
    removed: list[dict] = []

    while True:
        try:
            cycle = nx.find_cycle(G, orientation="original")
        except nx.NetworkXNoCycle:
            break
        pairs = [(u, v) for u, v, *_ in cycle]
        droppable = [p for p in pairs if p not in anchors] or pairs
        drop = min(droppable, key=lambda p: (len(votes.get(p, [])), p))
        G.remove_edge(*drop)
        removed.append({
            "cycle": [f"{u}->{v}" for u, v in pairs],
            "dropped": f"{drop[0]}->{drop[1]}",
            "reason": f"weakest link ({len(votes.get(drop, []))} source(s))",
        })
    return set(G.edges()), removed


def transitive_reduction(edges: set[Edge]) -> set[Edge]:
    """
    Keep only immediate parents.

    Anchors are re-added afterwards: a single wrong low-support edge can create
    a spurious path that makes a *correct* anchored edge look redundant, which
    silently deletes known-good structure (e.g. a bogus
    `CompactSpace -> EuclideanSpace` hid the anchored
    `CompactSpace -> TopologicalSpace`). Certainties survive reduction.
    """
    G = nx.DiGraph()
    G.add_nodes_from(c.id for c in ALL_CONTEXTS)
    G.add_edges_from(edges)
    reduced = set(nx.transitive_reduction(G).edges())
    return reduced | (set(ANCHORS) & edges)


def resolve_mutual(
    edges: set[Edge], votes: dict[Edge, list[str]]
) -> tuple[set[Edge], list[dict]]:
    """
    Pairs asserted in both directions. Impossible in a lattice, so it signals
    either a *sibling* relation misread as a parent (Wikipedia's ODE lede links
    to PDE, a peer) or a genuine edge plus a spurious reverse.

    Resolution order: an anchored direction always wins; otherwise the direction
    with more supporting sources wins; only a genuine tie drops both.
    """
    anchors = set(ANCHORS)
    resolved, notes = set(edges), []
    seen: set[frozenset] = set()

    for a, b in list(edges):
        if (b, a) not in edges:
            continue
        key = frozenset((a, b))
        if key in seen:
            continue
        seen.add(key)

        fwd, rev = (a, b), (b, a)
        if fwd in anchors or rev in anchors:
            keep = fwd if fwd in anchors else rev
            drop = rev if keep == fwd else fwd
            reason = "anchored direction wins"
        elif len(votes.get(fwd, [])) != len(votes.get(rev, [])):
            keep = max((fwd, rev), key=lambda e: len(votes.get(e, [])))
            drop = rev if keep == fwd else fwd
            reason = f"more sources ({len(votes.get(keep, []))} vs {len(votes.get(drop, []))})"
        else:
            resolved.discard(fwd)
            resolved.discard(rev)
            notes.append({"pair": f"{a}<->{b}", "action": "dropped both",
                          "reason": "tied support — likely siblings, not parent/child"})
            continue

        resolved.discard(drop)
        notes.append({"pair": f"{a}<->{b}", "action": f"kept {keep[0]}->{keep[1]}",
                      "reason": reason})

    return resolved, notes


def merge(sources: dict[str, list[Edge]], corroboration_votes: int = 2) -> dict:
    """
    Union-with-tiers, not vote-gating.

    Measured source profile: the LLM is high-recall, while the Wikipedia lede
    rule and Wikidata P279 are high-precision but *low-recall* corroborators.
    Requiring two votes therefore discards most true edges (it yielded 8 of an
    expected ~60). So the union is the working lattice, corroboration sets a
    confidence tier, and structural validation is the real gate.
    """
    # Grade the automated sources against the anchors BEFORE injecting them,
    # otherwise the test measures nothing.
    automated = tally(sources)
    source_grade = anchor_report({e for e in automated if not is_over(*e)})

    # Anchors are hand-verified certainties, so they belong in the lattice as
    # an authoritative source — not merely as a scoring rubric.
    votes = tally({**sources, "anchor": list(ANCHORS), "over-seed": list(OVER_SEED)})

    # Split parameterisation out before any order-theoretic work. `over` edges
    # are not order relations, so they must not contribute to depth, cycles, or
    # transitive reduction — including them is what created the Field chokepoint.
    over = {e for e in votes if is_over(*e)}
    union = set(votes) - over

    union, mutual_notes = resolve_mutual(union, votes)
    acyclic, cycles = break_cycles(union, votes)
    reduced = transitive_reduction(acyclic)
    implied = acyclic - reduced  # true, but not an immediate parent

    corroborated = {e for e in reduced if len(votes[e]) >= corroboration_votes}
    single = reduced - corroborated

    anchors = anchor_report(acyclic)
    anchors["source_grade"] = source_grade

    all_ids = {c.id for c in ALL_CONTEXTS}
    orphans = sorted(all_ids - {c for c, _ in reduced} - {"Set"})

    log.info(
        f"Merge: union {len(votes)} -> {len(reduced)} extends after reduction "
        f"({len(corroborated)} corroborated, {len(single)} single-source) "
        f"+ {len(over)} 'over' parameterisations held out of the order."
    )

    def _rows(es):
        return sorted(
            ({"child": c, "parent": p, "sources": votes[(c, p)]} for c, p in es),
            key=lambda d: (d["child"], d["parent"]),
        )

    return {
        "edges": sorted(reduced),
        "over_edges": sorted(over),
        "edge_sources": {f"{c}->{p}": votes[(c, p)] for c, p in reduced | over},
        "corroborated": sorted(corroborated),
        "single_source": sorted(single),
        "implied_edges": sorted(implied),
        "review_queue": _rows(single),
        "mutual_resolved": mutual_notes,
        "anchors": anchors,
        "cycles_broken": cycles,
        "orphans": orphans,
        "vote_histogram": {
            str(n): sum(1 for v in votes.values() if len(v) == n)
            for n in sorted({len(v) for v in votes.values()})
        },
    }
