# Graph

Resolves mathematical concepts to a stable identity and stores the structure (nodes and typed
relationships) between them. This context owns identity resolution and the concept graph itself
— it has no dependency on Vector or Retrieval.

## Language

**Concept**:
A mathematical idea that has been resolved to a stable, opaque id (a Wikidata QID or a minted
`CUST_<hash>`) — the unit of identity in this context. Matches the `concepts` table.
_Avoid_: Node (fine only when speaking graph-theoretically — edges, hops, neighborhoods),
Entity

**Graph store**:
The SQLite tables (`concepts`, `aliases`, `mentions`, `edges`, …) — the store of record for
this context.
_Avoid_: "the graph" (ambiguous — see Live graph, Graph export)

**Live graph**:
The in-memory `nx.DiGraph` built from the graph store. A derived cache kept because traversal,
layering, and cycle detection are easy in NetworkX and awkward in SQL.
_Avoid_: "the graph" (ambiguous — see Graph store, Graph export)

**Graph export**:
`graph.json` — a point-in-time export of the live graph, read directly by two consumers
(`/api/graph`, `scripts/graph_health.py`) that don't go through the graph store.
_Avoid_: "the graph" (ambiguous — see Graph store, Live graph)
