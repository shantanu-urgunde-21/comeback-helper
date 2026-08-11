"""
Build the context lattice from independent sources.

    python -m src.atlas.lattice.build              # all sources
    python -m src.atlas.lattice.build --no-llm     # Wikipedia + Wikidata only
    python -m src.atlas.lattice.build --min-votes 1

Writes `src/lattice/data/contexts.json` (the lattice) and
`src/lattice/data/review_queue.json` (edges only one source claimed).
"""

import argparse
import json
from pathlib import Path

from src.logger import log
from src.atlas.lattice import sources
from src.atlas.lattice.merge import merge
from src.atlas.lattice.seed import ALL_CONTEXTS, context_by_id

DATA_DIR = Path(__file__).parent / "data"


def build(use_llm: bool = True, min_votes: int = 2) -> dict:
    log.info(f"Building context lattice over {len(ALL_CONTEXTS)} scoped contexts.")

    edge_sets: dict[str, list] = {}
    reports: dict[str, dict] = {}

    wiki_edges, wiki_report = sources.wikipedia_edges()
    edge_sets["wikipedia"] = wiki_edges
    reports["wikipedia"] = wiki_report

    wd_edges, wd_report = sources.wikidata_edges()
    edge_sets["wikidata"] = wd_edges
    reports["wikidata"] = wd_report

    if use_llm:
        llm_e, llm_report = sources.llm_edges()
        edge_sets["llm"] = llm_e
        reports["llm"] = llm_report

    result = merge(edge_sets, corroboration_votes=min_votes)

    by_id = context_by_id()
    parents: dict[str, list[str]] = {c.id: [] for c in ALL_CONTEXTS}
    for child, parent in result["edges"]:
        parents[child].append(parent)

    over: dict[str, list[str]] = {c.id: [] for c in ALL_CONTEXTS}
    for child, parent in result["over_edges"]:
        over[child].append(parent)

    lattice = {
        "scope": "ODE, Calculus, Linear Algebra (+ analysis/algebra spine)",
        "edge_semantics": {
            "extends": "assumes everything the parent assumes, and more (an order relation)",
            "over": "is parameterised by this structure (scalars / base ring) - NOT an order relation",
        },
        "contexts": [
            {
                "id": c.id,
                "name": c.name,
                "course": c.course,
                "wikipedia": c.wikipedia,
                "extends": sorted(parents[c.id]),
                "over": sorted(over[c.id]),
            }
            for c in ALL_CONTEXTS
        ],
        "edge_sources": result["edge_sources"],
        "provenance": {
            "source_edge_counts": {k: len(v) for k, v in edge_sets.items()},
            "source_reports": reports,
            "corroboration_votes": min_votes,
            "corroborated": len(result["corroborated"]),
            "single_source": len(result["single_source"]),
            "anchors": result["anchors"],
            "cycles_broken": result["cycles_broken"],
            "mutual_resolved": result["mutual_resolved"],
            "orphans": result["orphans"],
            "vote_histogram": result["vote_histogram"],
            "implied_edges": result["implied_edges"],
        },
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "contexts.json").write_text(
        json.dumps(lattice, indent=2), encoding="utf-8"
    )
    (DATA_DIR / "review_queue.json").write_text(
        json.dumps(result["review_queue"], indent=2), encoding="utf-8"
    )

    _print_summary(lattice, result, edge_sets)
    return lattice


def _print_summary(lattice, result, edge_sets):
    a = result["anchors"]
    print("\n" + "=" * 68)
    print("  CONTEXT LATTICE BUILD")
    print("=" * 68)
    print(f"  contexts in scope     {len(lattice['contexts'])}")
    for name, edges in edge_sets.items():
        print(f"  {name:<20}  {len(edges):>4} candidate edges")
    print("-" * 68)
    print(f"  {'LATTICE (extends)':<20}  {len(result['edges']):>4} edges after reduction")
    print(f"  {'OVER (parameters)':<20}  {len(result['over_edges']):>4} held out of the order")
    print(f"  {'  corroborated':<20}  {len(result['corroborated']):>4} (>=2 sources)")
    print(f"  {'  single-source':<20}  {len(result['single_source']):>4} (review queue)")
    print("-" * 68)
    g = a["source_grade"]
    status = "PASS" if g["pass"] else "FAIL (direction inversions)"
    print("  SOURCE QUALITY  (automated sources graded against anchors)")
    print(f"    anchors recovered   {g['found']}/{g['total']}   [{status}]")
    if g["inverted"]:
        print("    !! DIRECTION INVERSIONS:")
        for x in g["inverted"]:
            print(f"         {x}")
    if g["missing"]:
        print(f"    missed by sources ({len(g['missing'])}) - supplied by anchor set:")
        for x in g["missing"]:
            print(f"         {x}")
    if result["mutual_resolved"]:
        print(f"  mutual pairs resolved: {len(result['mutual_resolved'])}")
        for m in result["mutual_resolved"]:
            print(f"       {m['pair']:<32} {m['action']:<26} ({m['reason']})")
    if result["cycles_broken"]:
        print(f"  cycles broken: {len(result['cycles_broken'])}")
        for c in result["cycles_broken"]:
            print(f"       dropped {c['dropped']}  ({c['reason']})")
    if result["orphans"]:
        print(f"  orphans (no parent): {', '.join(result['orphans'])}")
    print("=" * 68)
    print(f"  wrote {DATA_DIR / 'contexts.json'}")
    print(f"  wrote {DATA_DIR / 'review_queue.json'}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--min-votes", type=int, default=2)
    args = ap.parse_args()
    build(use_llm=not args.no_llm, min_votes=args.min_votes)


if __name__ == "__main__":
    main()
