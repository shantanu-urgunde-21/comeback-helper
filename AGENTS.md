# AGENTS.md

Orientation for coding agents working in this repository.

**[CLAUDE.md](CLAUDE.md) is the canonical guide — read it.** This file is a short
vendor-neutral entry point. It deliberately does *not* restate CLAUDE.md's commands,
architecture, or invariants: an earlier version did, drifted out of date, and had to be
corrected. Anything specific belongs there, once.

## The five-minute version

- **Implementation is in `services/`, not `src/`.** `src/` holds `server.py`, `cli.py`, and
  `wiring.py` (the composition root). One process, one copy of every module.
- **Imports use short package names** — `shared.config`, `graph.app.indexer`. Never
  `services.shared.config`; the double identity breaks module state.
- **`.env` is required for any `import src`**, including in tests. Copy `.env.example`.
- **Tests are `unittest`, not pytest**: `python -m unittest discover -s tests -v`.
- **The Obsidian vault is the source of truth.** The graph and vector index derive from it
  and are rebuildable; the notes are not.
- **`.storage/concepts.db` (SQLite) is the graph's store of record.** `graph.json` is an
  export. The in-memory `nx.DiGraph` is a derived cache.

## Before you change anything

1. Read **CLAUDE.md's Invariants section**. Each entry exists because breaking it caused a
   bug that was hard to trace.
2. Check **[plan.md](plan.md)** for where the architecture is headed (Phases 0–7 complete).
3. If you touch a CLI verb's `--json` output, update
   [the skill](.claude/skills/comeback-helper/SKILL.md) in the same commit — it is a
   consumer contract.
