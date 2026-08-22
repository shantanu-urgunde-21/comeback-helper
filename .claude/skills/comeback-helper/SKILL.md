---
name: comeback-helper
description: "Use for anything involving this repository's mathematics knowledge graph or Obsidian vault — ingesting handwritten lecture notes from PDF, asking questions about the maths in them, inspecting or repairing the concept graph, and checking graph health. Wraps the local `src/` engine through its CLI; the graph is the product, so prefer graph-aware answers over plain file reading."
---

# /comeback-helper

Drive the Comeback Helper pipeline: handwritten PDF → OCR'd Obsidian note → concept graph →
answers grounded in that graph.

## Usage

```
/comeback-helper                                  # report vault + graph state, suggest next step
/comeback-helper ingest <pdf> --course "<name>"   # OCR a PDF into the vault, then index it
/comeback-helper query "<question>"               # ask the knowledge base
/comeback-helper query "<question>" --course "<name>"   # scope to one course
/comeback-helper preview <note.md>                # dry-run extraction, writes nothing
/comeback-helper health                           # full graph quality report
/comeback-helper stats                            # quick node/edge counts
/comeback-helper rebuild                          # re-extract every note (expensive)
```

## What this skill is for

The Obsidian vault is the source of truth. The graph and the vector index both derive from
it and are rebuildable; the vault notes are not, because re-OCR costs money and re-rolls
transcription. **Never delete or overwrite a vault note.**

The graph is the product — a visual atlas of how mathematical concepts build on each other.
When a question can be answered from the graph, answer from the graph rather than grepping
the vault.

## Contract

Talk to the engine **only through `python -m src.cli <verb> --json`**. Do not import from
`src/` directly, and do not read `.storage/graph.json` to answer questions when a CLI verb
would do it. The internals are actively being rewritten; the CLI verbs are the stable
surface. If a verb you need doesn't exist, say so rather than reaching around it.

Every verb accepts `--json` and then prints exactly one JSON object on stdout, with logs on
stderr. Failures come back as `{"status": "error", "command": ..., "error": ...}` and a
non-zero exit code — parse that rather than scraping text.

Run everything from the repository root. `.env` must exist (copy `.env.example`); without it
every `src` import fails at load time, including these commands.

## What You Must Do When Invoked

### Step 0 — Orient

Unless the user named a specific verb, start here:

```bash
python -m src.cli graph-stats --json
```

Report nodes, edges, isolated nodes and connected components. If `isolated_nodes` is more
than ~10% of `nodes`, or `connected_components` is large, mention that the graph has known
quality problems and point at `docs/diagnosis.md` — but do not start fixing them unless
asked.

### Step 1 — Ingest (only when given a PDF)

Ingestion is two steps, because `ingest` writes the vault note but does **not** index it.

```bash
python -m src.cli ingest --file "<pdf>" --course "<course>" --json
python -m src.cli rebuild-graph --no-force --json
```

`--no-force` indexes only notes whose SHA-256 changed, so this costs one note's worth of LLM
calls rather than re-extracting the whole vault. Use plain `rebuild-graph` (force) only when
the user explicitly asks for a full rebuild.

Report the note path and the resulting node/edge counts. If node count didn't move, say so —
it usually means extraction returned nothing, not that the note was empty.

The vector index is not updated by the CLI at all. If the user needs chunk retrieval, tell
them to run the server and POST `/api/rebuild/vectors`.

### Step 2 — Query

```bash
python -m src.cli query --prompt "<question>" --json
python -m src.cli query --prompt "<question>" --course "<course>" --json
```

Pass `--course` whenever the user names a subject; it scopes retrieval and cuts noise.

The `answer` field is already synthesised prose — relay it, don't re-summarise it into
something shorter. If it cites concepts, you may follow up with `graph-stats` or a look at
the concept's neighbours to add structure, but do not contradict it from your own knowledge
without saying you're doing so.

### Step 3 — Inspect before changing

To see what extraction *would* produce on a note without touching the graph:

```bash
python -m src.cli graph-preview --note "<path.md>" --json
```

This is the safe way to test a prompt or schema change. It writes nothing.

For a full quality report — duplicate groups, isolated nodes, vocabulary collapse, taxonomy
sprawl:

```bash
python scripts/graph_health.py
```

Read-only, stdlib only, no `.env` needed. Its output is human-formatted, not JSON.

### Step 4 — Repair, carefully

There is no `dedupe` verb anymore: node identity is resolved deterministically before edges
are drawn (see "Known state" below), so there is nothing left to merge after the fact. If
`graph_health.py` still reports duplicate groups, that is a new bug, not something a repair
command can paper over — investigate rather than reaching for a merge pass.

**Do not** attempt these without the user explicitly asking:

- A full `rebuild-graph` as a repair. It re-rolls every naming decision, changing *which*
  duplicates exist rather than whether they exist.
- Editing `graph.json` by hand.

## Invariants

These fail silently rather than loudly, so respect them even when a change looks safe:

- **`PREREQUISITE_FOR(A,B)` is stored as `DEPENDS_ON(B,A)`.** Never emit the inverse form —
  two directions between one pair create fake cycles that break hierarchical layout.
- **Notes are not graph nodes.** Which note a concept came from lives in that concept's
  `provenance` list. The `CONTAINS` note→concept edge was retired; don't reintroduce it.
- **`graph.json` writes `entity_type` as `type`.** Anything reading the file directly must
  expect `type`.
- **The graph lives in RAM in the running server.** If the server is up, CLI writes and
  server state can diverge until it restarts. Prefer one or the other in a single session.
- **`scripts/` is gitignored.** Anything written there won't be committed.

## Known state

As of `plan.md` Phases 0-2, node identity is resolved deterministically (a Wikidata QID or a
`CUST_<hash>` id) instead of an LLM-generated display name compared by embedding similarity
— both for newly indexed concepts and for the live graph, which was migrated onto this
scheme (`graph-migrate-identity`): 119 nodes → 75 (17 junk dropped, 27 duplicate spellings
merged). `graph_health.py` reports 0 duplicate groups against the current file. If you see
this reported as a duplicate-nodes problem in older context, it's stale — re-run
`graph-stats`/`graph_health.py` rather than trusting a prior summary.

Node ids are now opaque (a QID or `CUST_` hash); the human-readable name lives in each
node's separate `label` field. Three more CLI verbs exist for the identity layer,
independent of `graph.json`: `authority-seed-msc`, `authority-resolve --label "..."`,
`authority-stats`.

As of `plan.md` Phase 6, the embedding-similarity repair path (`dedupe_graph()`,
`ENTITY_MERGE_THRESHOLD`, the `graph-dedupe` verb) and the load-time snake_case/Title-Case
self-heal are deleted, not just unused — they're gone from the codebase entirely, so don't
suggest them even as a fallback.

The LanceDB vector table is currently empty and its data files are missing, so chunk
retrieval returns nothing and queries run graph-only. Recovery is to delete
`.storage/lancedb`, restart the server, then POST `/api/rebuild/vectors`.

## Reference

| Document | Contains |
|---|---|
| `CLAUDE.md` | Commands, architecture, invariants |
| `docs/flow.md` | Data flow, stage-by-stage inputs and outputs |
| `docs/structure.md` | Call chains, module reference, dead code |
| `docs/diagnosis.md` | Measured graph defects and the planned fixes |
