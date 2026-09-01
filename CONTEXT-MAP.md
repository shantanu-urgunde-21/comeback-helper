# Context Map

## Contexts

- [Graph](./services/graph/CONTEXT.md): resolves concept identity and stores the concept graph
- Vector: chunks notes and indexes them for semantic search (context confirmed, no terms resolved yet — no CONTEXT.md until one is)
- Retrieval: combines graph and vector results into an answer at query time (context confirmed, no terms resolved yet — no CONTEXT.md until one is)

## External systems (not part of this repo's domain)

- **Obsidian vault** — a folder the user's own Obsidian workflow owns. This repo treats it as an external source, read through an adapter (`vault/app/`), not as a domain concept it models. "Source of truth" describes a data-provenance fact (not re-derivable, don't lose it) — not a claim that the vault belongs to this domain.

## Relationships

- **Graph → Vault (external)**: reads notes through the vault adapter; writes nothing back except via ingestion (OCR output).
- **Vector → Vault (external)**: reads notes independently of Graph — no shared model between the two.
- **Graph ↔ Vector**: deliberately no dependency between these two contexts. They don't share ubiquitous language (a *chunk* in Vector isn't a *Concept* in Graph).
- **Retrieval → Graph, Retrieval → Vector**: the only context that depends on both; it coordinates rather than belongs to either side.

## Open

- Whether **Ingestion** (PDF → OCR → vault note) is its own context or folded into the Vault boundary — not yet settled.
