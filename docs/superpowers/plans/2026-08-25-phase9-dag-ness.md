# Phase 9 Implementation Plan: DAG-ness and Cycle Resolution

## Objective
Convert the knowledge graph into a true Directed Acyclic Graph (DAG) for prerequisite and dependency relations by eliminating all 36 existing cycles and enforcing acyclicity at write time.

## Diagnosis of Current Cycles (Post-Phase 8 Rebuild)
- **Total Simple Cycles**: 36
  - **16 Two-node Cycles (2-cycles)**:
    - Mutual/dual concepts emitted as bidirectional `DEPENDS_ON` (e.g. `Linear Dependence` <-> `Linear Independence`, `Well-Posed Problem` <-> `Well-Posed IVP`).
    - Semantic asymmetry vs generic `DEPENDS_ON` (e.g. `Criterion for Exactness` `USES_DEFINITION` `Exact ODE`, but `Exact ODE` had generic `DEPENDS_ON` `Criterion for Exactness`).
    - Specific method pointing to concept and concept pointing to method (e.g. `Exact ODE` <-> `Integrating Factor`).
  - **20 Multi-node Cycles (>2-cycles)**:
    - Narrative lecture flow inversions (e.g. `LHODE` -> `Explicit Solution` -> `Undetermined Coefficients` -> `LHODE`). Foundational concept `LHODE` should be the target/sink, not a source to its solution methods.

## Implementation Tasks

### Task 1: Add Cycle Telemetry to `scripts/graph_health.py` and `src/cli.py`
- Report number of simple cycles, strongly connected components (SCCs) > 1, and sample cycles with offending edge relations in `scripts/graph_health.py`.
- Include `cycles: int` and `is_dag: bool` in `python -m src.cli graph-stats --json`.

### Task 2: Cycle Resolution & Pruning Engine in `graph/app/dag.py`
- Create `services/graph/app/dag.py` with:
  1. `break_2cycles(G)`: Resolves 2-cycles:
     - If one relation is specific (`USES_DEFINITION`, `USES_IN_PROOF`, `HAS_HYPOTHESIS`, `CHARACTERIZES`, `SPECIAL_CASE_OF`) and the other is generic `DEPENDS_ON`, drop the generic `DEPENDS_ON` edge.
     - If both are `DEPENDS_ON` between mutual/dual concepts, convert to `EQUIVALENT_TO` (stored canonically in one direction).
  2. `prune_feedback_edges(G)`: Minimum feedback arc set / topological ordering algorithm to break multi-hop cycles by removing or reversing backward edges that violate topological hierarchy.
  3. `repair_graph_dag(G)`: Full pipeline that turns any graph into a strict DAG for hierarchical relations.

### Task 3: Write-Time Cycle Prevention in `indexer.py` / `graph_store.py`
- In `MathGraphIndexer.index_note` / `_normalize_relation`:
  - When adding a hierarchical directed edge `source -> target` (`DEPENDS_ON`, `USES_DEFINITION`, `USES_IN_PROOF`, `HAS_HYPOTHESIS`, `SPECIAL_CASE_OF`, `COROLLARY_OF`, `INSTANCE_OF`):
  - Check if `nx.has_path(G, target, source)` (which would complete a cycle).
  - If a reverse path exists:
    - If `G.has_edge(target, source)` with a generic `DEPENDS_ON` and the new edge is more specific, replace the reverse edge.
    - Otherwise, log a warning and skip inserting the cycle-creating edge.

### Task 4: Clean Database & Apply DAG Repair
- Run cycle repair across SQLite `.storage/concepts.db` and export to `graph.json`.
- Verify with `scripts/graph_health.py` that total cycles = 0 and `is_dag` = True.

### Task 5: Unit Tests
- Add tests in `tests/test_dag.py` verifying 2-cycle breaking, feedback edge pruning, and write-time prevention.
