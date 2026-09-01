"""DAG enforcement and cycle resolution algorithms for the concept knowledge graph.

A prerequisite/dependency graph must be a Directed Acyclic Graph (DAG) for
hierarchical layout, topological sorting, and learning path traversal.

Cycles arise from two main sources:
1. 2-cycles from mutual concepts or asymmetric relation extraction (e.g. A USES_DEFINITION B,
   while B was given a generic DEPENDS_ON A in another note).
2. Multi-hop cycles from narrative flow inversions in lecture notes (e.g. Concept -> Method -> Concept).
"""

from typing import Any, Dict, List, Set, Tuple
import networkx as nx

from shared.logger import log
from .schema import SYMMETRIC_RELATIONS, MathRelationType

# Specificity ranking: higher priority relations are preserved over lower priority generic relations
RELATION_PRIORITY: Dict[str, int] = {
    "PROVES": 90,
    "COROLLARY_OF": 85,
    "USES_IN_PROOF": 80,
    "HAS_HYPOTHESIS": 75,
    "CHARACTERIZES": 70,
    "USES_DEFINITION": 65,
    "SPECIAL_CASE_OF": 60,
    "GENERALIZES": 55,
    "INSTANCE_OF": 50,
    "DEPENDS_ON": 10,
    "EQUIVALENT_TO": 0,
}


def get_edge_priority(relation: str) -> int:
    return RELATION_PRIORITY.get(relation, 10)


def resolve_2cycle(rel_forward: str, rel_reverse: str) -> str:
    """Decides the outcome for one A->B / B->A conflict, by relation specificity.

    Returns "keep_forward", "keep_reverse", or "equivalent" (equal priority —
    treated as a mutual fact and canonicalized to one EQUIVALENT_TO edge).
    Shared by the batch repair pass (`break_2cycles`) and the write-time
    check in `MathGraphIndexer.index_note`, so both apply the same rule.
    """
    p_fwd = get_edge_priority(rel_forward)
    p_rev = get_edge_priority(rel_reverse)
    if p_fwd > p_rev:
        return "keep_forward"
    if p_rev > p_fwd:
        return "keep_reverse"
    return "equivalent"


def break_2cycles(G: nx.DiGraph) -> List[Tuple[str, str, str]]:
    """Resolves all 2-node cycles in-place.

    Returns a list of removed edges: [(source, target, relation), ...].
    """
    removed: List[Tuple[str, str, str]] = []
    pairs_checked: Set[Tuple[str, str]] = set()

    edges_to_check = list(G.edges(data=True))
    for u, v, d_uv in edges_to_check:
        if not G.has_edge(u, v) or not G.has_edge(v, u):
            continue

        pair_key = tuple(sorted([u, v]))
        if pair_key in pairs_checked:
            continue
        pairs_checked.add(pair_key)

        d_vu = G.get_edge_data(v, u)
        rel_uv = d_uv.get("relation", "DEPENDS_ON")
        rel_vu = d_vu.get("relation", "DEPENDS_ON")

        outcome = resolve_2cycle(rel_uv, rel_vu)

        if outcome == "keep_forward":
            # Drop the weaker edge (v -> u)
            G.remove_edge(v, u)
            removed.append((v, u, rel_vu))
            log.info(f"DAG break_2cycles: Removed weaker edge {v} -[{rel_vu}]-> {u} in favor of {u} -[{rel_uv}]-> {v}")
        elif outcome == "keep_reverse":
            # Drop the weaker edge (u -> v)
            G.remove_edge(u, v)
            removed.append((u, v, rel_uv))
            log.info(f"DAG break_2cycles: Removed weaker edge {u} -[{rel_uv}]-> {v} in favor of {v} -[{rel_vu}]-> {u}")
        else:
            # Both have equal priority (e.g. both DEPENDS_ON).
            # If symmetric (e.g. Linear Dependence <-> Linear Independence), convert to single EQUIVALENT_TO edge.
            G.remove_edge(u, v)
            G.remove_edge(v, u)
            canon_src, canon_tgt = sorted([u, v])
            G.add_edge(canon_src, canon_tgt, relation="EQUIVALENT_TO", label="EQUIVALENT_TO")
            removed.append((u, v, rel_uv))
            removed.append((v, u, rel_vu))
            log.info(f"DAG break_2cycles: Converted mutual {u} <-> {v} into single canonical EQUIVALENT_TO edge")

    return removed


def prune_feedback_edges(G: nx.DiGraph) -> List[Tuple[str, str, str]]:
    """Breaks remaining multi-hop cycles in-place by iteratively removing the lowest-priority feedback edge.

    Returns a list of removed edges: [(source, target, relation), ...].
    """
    removed: List[Tuple[str, str, str]] = []

    while not nx.is_directed_acyclic_graph(G):
        try:
            cycle = nx.find_cycle(G, orientation="original")
        except nx.NetworkXNoCycle:
            break

        # cycle is a list of (u, v, direction)
        cycle_edges = [(u, v) for u, v, _ in cycle]

        # Find the edge with lowest priority in the cycle
        min_edge = None
        min_priority = float("inf")
        min_rel = "DEPENDS_ON"

        for u, v in cycle_edges:
            data = G.get_edge_data(u, v, default={})
            rel = data.get("relation", "DEPENDS_ON")
            priority = get_edge_priority(rel)

            # Ties keep whichever edge was found first in the cycle walk.
            if priority < min_priority:
                min_priority = priority
                min_edge = (u, v)
                min_rel = rel

        if min_edge and G.has_edge(min_edge[0], min_edge[1]):
            u, v = min_edge
            G.remove_edge(u, v)
            removed.append((u, v, min_rel))
            log.info(f"DAG prune_feedback_edges: Removed feedback edge {u} -[{min_rel}]-> {v} to break cycle")
        else:
            # Fallback if no edge found
            break

    return removed


def repair_graph_dag(G: nx.DiGraph, prune_multihop: bool = False) -> Dict[str, Any]:
    """Applies graph repair in-place:
    1. Breaks 2-node cycles (prioritizes specific relations, converts mutuals to canonical EQUIVALENT_TO).
    2. Optionally prunes multi-hop feedback edges if prune_multihop=True (defaults to False).
    """
    initial_cycles = len(list(nx.simple_cycles(G))) if G.number_of_nodes() < 500 else -1
    removed_2cycles = break_2cycles(G)
    removed_multihop = prune_feedback_edges(G) if prune_multihop else []
    is_dag = nx.is_directed_acyclic_graph(G)

    return {
        "initial_cycles": initial_cycles,
        "removed_2cycles": removed_2cycles,
        "removed_multihop": removed_multihop,
        "total_removed": len(removed_2cycles) + len(removed_multihop),
        "is_dag": is_dag,
    }


def will_create_cycle(G: nx.DiGraph, source: str, target: str) -> bool:
    """Returns True if adding directed edge source -> target would create a cycle in G.

    An edge source -> target creates a cycle iff there is already a path from target to source.
    """
    if source == target:
        return True
    if not G.has_node(source) or not G.has_node(target):
        return False
    return nx.has_path(G, target, source)
