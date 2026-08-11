"""
Render the built lattice as layered text.

    python -m src.atlas.lattice.show                 # whole lattice
    python -m src.atlas.lattice.show --course ode    # one course's slice
    python -m src.atlas.lattice.show --above LinearODEConstCoeff

Depth is longest-path-to-a-root, which is the layout axis Model B uses in place
of a guessed `abstraction_level`: it is read off the lattice, not estimated.
"""

import argparse
import json
from pathlib import Path

import networkx as nx

DATA = Path(__file__).parent / "data" / "contexts.json"


def load() -> tuple[nx.DiGraph, dict]:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    G = nx.DiGraph()
    for c in d["contexts"]:
        G.add_node(c["id"], **c)
    for c in d["contexts"]:
        for p in c["extends"]:
            G.add_edge(c["id"], p)  # child -> parent
    return G, d


def depths(G: nx.DiGraph) -> dict[str, int]:
    """Longest path from each node up to a root. Roots are depth 0."""
    order = list(nx.topological_sort(G.reverse()))
    depth = {n: 0 for n in G}
    for n in order:
        for child in G.reverse().successors(n):
            depth[child] = max(depth[child], depth[n] + 1)
    return depth


def render(G: nx.DiGraph, data: dict, nodes: set[str] | None = None) -> str:
    nodes = nodes or set(G.nodes)
    sub = G.subgraph(nodes)
    d = depths(G)
    src = data.get("edge_sources", {})

    layers: dict[int, list[str]] = {}
    for n in sub.nodes:
        layers.setdefault(d[n], []).append(n)

    out = []
    for lvl in sorted(layers, reverse=True):
        out.append(f"\n  depth {lvl}   {'(most general)' if lvl == 0 else ''}")
        for n in sorted(layers[lvl]):
            name = G.nodes[n].get("name", n)
            parents = sorted(p for p in sub.successors(n))
            marks = []
            for p in parents:
                s = src.get(f"{n}->{p}", [])
                tag = "*" if len(s) >= 2 else "?"
                marks.append(f"{p}{tag}")
            arrow = ("  extends  " + ", ".join(marks)) if marks else ""
            out.append(f"    {name:<38}{arrow}")
    out.append("\n  * corroborated by 2+ sources    ? single source (review)")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", help="filter to one course slice")
    ap.add_argument("--above", help="show only the ancestors of this context")
    args = ap.parse_args()

    G, data = load()
    nodes = None
    if args.course:
        nodes = {n for n, a in G.nodes(data=True) if a.get("course") == args.course}
    if args.above:
        nodes = nx.descendants(G, args.above) | {args.above}

    print(render(G, data, nodes))


if __name__ == "__main__":
    main()
