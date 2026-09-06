# System Architecture & Design Deep Dive

This is the doc to read front-to-back to actually understand Comeback Helper — what it's
for, why it's shaped the way it is, and how the pieces connect. `docs/structure.md` and
`docs/flow.md` are the terse reference layer once you already have this picture; come back
to them when you need an exact call chain or data shape. `CLAUDE.md` is the canonical,
agent-facing guide — its Invariants section is the list of things that will bite you if you
change them without reading this doc first.

## What this is actually for

The name is a light joke, not a product thesis. What it builds is a **visual atlas of
mathematics**: one knowledge graph across every course a student has taken, typing the
*specific relationship* between concepts — not just within a course, but across them (a
theorem in Machine Learning might `GENERALIZES` a result from Linear Algebra, or merely
`USES_DEFINITION` one; the Cauchy-Schwarz inequality `CHARACTERIZES` a property that a dozen
unrelated-looking theorems each turn out to be an `INSTANCE_OF`).

**This is a project about finding relations, not dependencies.** That's a specific claim
about what Pass 2 is for, not a loose description — worth being precise about because
"knowledge graph" invites the wrong mental model (a prerequisite tree, easy to degrade into
if you're not careful). Read the Pass 2 prompt (`prompts.py`) and it says the opposite of
what you'd expect from a dependency finder: *"pick the most specific relation that applies. Do NOT fall back to
DEPENDS_ON."* `DEPENDS_ON` is the residual bucket for when nothing sharper fits, not the
target. And half the vocabulary isn't dependency-shaped at all — `EQUIVALENT_TO` is
symmetric (neither side is "more foundational"), `GENERALIZES`/`SPECIAL_CASE_OF`/
`INSTANCE_OF` are taxonomic, `CHARACTERIZES` is a definitional equivalence. None of those
answer "what must I learn first"; they answer "what *is* this thing, in relation to that
other thing." Phase 8 (`plan.md`, `docs/vocabulary-diagnosis.md`) exists specifically because
an earlier version of this graph *had* collapsed toward "almost everything is `DEPENDS_ON`"
— and that was diagnosed as a defect to fix, not the system working as intended. A
prerequisite ordering is a real, useful thing you can *derive* from this graph afterward
(filter to the dependency-flavored relations and topologically sort) — but it's a projection
of the relational structure, not what extraction is reaching for.

**Intent verified against the actual data, not just the prompt.** Reading `prompts.py` tells
you what the system is *trying* to do; it doesn't tell you whether it succeeds. Pulled
directly from `.storage/concepts.db` (`SELECT source_id, target_id, quote FROM edges WHERE
relation = ?`, one query per relation, sampled and read by hand):

- The specific relations are real and mostly well-reasoned, not noise. Sampled
  `SPECIAL_CASE_OF`, `CHARACTERIZES`, `INSTANCE_OF`, and `HAS_HYPOTHESIS` edges each carry an
  evidence quote that genuinely supports the typed relation — e.g. `"Picard's Uniqueness
  Theorem" -[SPECIAL_CASE_OF]-> "Picard's Theorem"`, evidence *"Picard's Uniqueness Theorem is
  the uniqueness component of Picard's theorem"*; `"Picard's Theorem" -[HAS_HYPOTHESIS]->
  "Lipschitz Condition"`, evidence *"Picard's theorem requires the function to satisfy the
  y-Lipschitz condition for uniqueness."* This isn't the LLM picking a relation at random and
  writing a plausible-sounding sentence after the fact.
- But the "most specific relation" instruction is followed **inconsistently**, not reliably.
  Every edge whose own evidence quote contains the word "characterizes"/"characterize" (7
  edges, a clean keyword to search for since it's specific to one relation): 3 were correctly
  typed `CHARACTERIZES`, but 4 were not — one stored as `EQUIVALENT_TO` (*"Criterion for
  Exactness characterizes exact ODEs"*), three as the generic `DEPENDS_ON` (*"Theorem (T1)
  characterizes linear independence using the Wronskian"*). The model's own extracted evidence
  names the sharper relation and it still defaulted to the residual bucket more than half the
  time on this sample.
- `GENERALIZES` — present in the schema, present in the Pass 2 prompt with a definition — has
  **zero edges** in the live graph. Not rare: unused. Whether that's because the extracted
  course material genuinely contains no generalization relationships worth surfacing, or
  because the model reliably reaches for `SPECIAL_CASE_OF` (its inverse) or `DEPENDS_ON`
  instead when one would apply, isn't something this doc can answer without a targeted
  extraction test — but it's a fact worth knowing, not glossing over.

So: the philosophy is real (present in the prompt design, present in the schema, present in a
meaningful share of the actual output, and the whole reason Phase 8 exists) — but it's
aspirational to a real, measurable degree, not fully realized. `DEPENDS_ON` at 61.1% of edges
(see "Known open issues" below) is that same gap expressed as one number.

The premise is that math concepts are hard to hold in your head not because any one of them
is hard, but because they differ by *small, easily-confused distinctions* — the same name
meaning something different in two fields, two results that look unrelated until you see one
is a special case of the other. A wall of vector-search text chunks doesn't surface that; a
typed relation does.

**The graph is the product.** OCR, the Obsidian vault, the vector store, and the RAG chat
engine all exist to feed and query that graph — they are supply chain, not the point. If a
proposed feature is a study planner, a quiz generator, or spaced repetition, it's off the
product's actual thesis; that direction was raised once during development and explicitly
turned down. The generalizing ambition (this isn't meant to stay math-specific forever) is
also why the relation vocabulary (`DEPENDS_ON`, `GENERALIZES`, `INSTANCE_OF`, ...) is written
to be field-agnostic rather than math-specific jargon.

## Why one process, five packages, not five services

An earlier version of this codebase had a real microservice split staged for it —
per-package `Dockerfile`s, HTTP client stand-ins, a container-per-service deployment plan.
It was deleted (`plan.md` Phase 7) because it was never actually run: this is a single-user
local app, and the extra network hop between "packages" bought nothing except latency and a
second thing to keep in sync. What's kept from that era is the *module boundary* — five
packages under `services/`, each owning one concern, each still taking its collaborators as
constructor arguments rather than importing them at module scope — because that discipline
is worth having even with everything living in one Python process. `src/wiring.py` is the
one place that actually constructs the real objects and wires them together; every package
can otherwise be instantiated and tested in isolation with no args.

```
services/
├── shared/     config, logger, Gemini/Ollama clients, the LLM fallback ladder — everyone depends on this
├── vault/      reads Obsidian notes, tracks SHA-256 ingest state — nothing depends on this being the vault specifically
├── ingestion/  PDF → Markdown (depends on vault)
├── vector/     chunking + LanceDB (standalone — no dependency on graph)
├── graph/      identity resolution + the concept graph itself (depends on vault; NOT on vector)
└── retrieval/  hybrid context assembly + answer synthesis (the only package that depends on both graph and vector)
```

`graph` not depending on `vector` is deliberate and was a real refactor (`plan.md` Phase 1),
not an accident of layering — see "Why identity resolution is a lookup, not a vector search"
below.

## Why these tools, specifically

Every dependency here (`requirements.txt`) is doing a specific job, not just "the popular
choice." Marked *(inferred)* where the reasoning is drawn from how the code actually uses the
tool rather than from an explicit comment saying so.

- **FastAPI + Uvicorn.** Async-native, gets a free interactive API explorer at `/docs` from
  the route type hints, and — the load-bearing reason, not a nice-to-have — its request/
  response models are the *same* Pydantic classes used everywhere else in this codebase
  (`QueryRequest` in `src/routes/query.py`), so validation is one system, not two. *(inferred)*
  Caveat: the async-ness isn't actually exploited for concurrency — see "Is this following
  good practices?" below.
- **Pydantic** does two unrelated-looking jobs with one library. The obvious one is FastAPI
  request/response validation. The load-bearing one: `services/graph/app/schema.py`'s models
  (`MathNodeExtraction`, `MathEdgeExtraction`) are passed straight to the Gemini SDK as
  `response_schema=` (`llm_extraction.py`), which makes Gemini itself constrain its JSON
  output to that shape *before* it ever reaches this codebase. Pass 1/2 then do
  `MathNodeExtraction(**data)` and trust it to mostly just work — and when a response doesn't
  validate, that `ValidationError` is exactly the exception `with_gemini_then_ollama` catches
  to move to the next fallback tier. The schema isn't just documentation of the shape; it's an
  active gate in the fallback ladder.
- **LanceDB.** Embedded and serverless — no database process to run, no Docker Compose, just a
  directory on disk (`.storage/lancedb/`) — for the same reason SQLite was chosen for the
  graph: this is meant to run entirely as one local process on one person's machine. Its
  native FTS (BM25) index is what makes `query_type="hybrid"` search possible without a second
  search engine alongside the vector index.
- **FastEmbed**, not `sentence-transformers` directly. It's an ONNX Runtime wrapper — no full
  PyTorch dependency needed just to embed text — with a CUDA execution provider tried first
  and a CPU fallback on failure (`vector/app/store.py`'s `try`/`except` around
  `TextEmbedding(...)`). *(inferred)* That fallback only makes sense as a deliberate choice if
  running on a GPU-less laptop is a real target environment, which matches "runs on a
  student's machine" as a design constraint throughout this codebase (see the handwriting VLM
  pipeline's aggressive VRAM budgeting for the same reason).
- **NetworkX**, not a graph database. Pure-Python, no server, and its algorithms
  (`nx.is_directed_acyclic_graph`, `nx.find_cycle`, `nx.simple_cycles`, `nx.has_path`) are
  exactly the primitives `dag.py` needs for cycle detection and repair — implementing those
  correctly over raw SQL joins would be real, unnecessary work. The tradeoff this makes
  explicit: the graph has to fit in memory, which is fine at hundreds of nodes and would need
  revisiting at a very different scale.
- **SQLite**, for the same "one local file, no server" reason as LanceDB — plus it gives the
  identity ladder (`authority.py`'s `resolve_concept`) real transactional atomicity for its
  check-then-insert resolution logic, which matters even in a single process because a crash
  mid-resolution shouldn't leave a concept row without its alias binding.
- **Click + Rich**, split by audience. Click owns the command/option surface; Rich renders
  human-readable colored tables and panels — but every command also accepts `--json`
  specifically to *bypass* Rich, emitting one bare JSON object on stdout instead
  (`src/cli.py`'s `_json_mode` callback, which reroutes Loguru's sink to stderr the instant
  `--json` is parsed, so log lines can never interleave with and corrupt the JSON output).
  That's not incidental politeness — it's the entire mechanism the `comeback-helper` skill
  relies on to talk to this codebase without importing it.
- **Loguru over stdlib `logging`.** One `log.info(...)` call, no handler/formatter
  boilerplate, colorized by default — chosen for less ceremony, at the cost of being a
  dependency stdlib logging isn't. *(inferred)*
- **PyMuPDF (`fitz`)** for PDF→image rendering, not a text-extraction library — because a
  scanned handwritten page has no text layer to extract; the only way to OCR it is to render
  it to a raster image first and hand that to a vision model.
- **OpenCV**, for the one preprocessing step (`ImagePreprocessor.preprocess_pil`) that's
  classic, cheap computer vision (channel splitting, CLAHE) rather than another model call —
  stripping notebook ruling lines with a matrix operation is orders of magnitude cheaper than
  asking a second VLM to do it.
- **Ollama** as the local inference runtime for both text and vision models
  (`llama3.2`, `qwen2.5:3b`, `phi3:mini`, `qwen2.5-coder:3b` for text; `qwen2.5vl:3b` for
  vision), all through one HTTP API (`shared/llm/ollama.py`'s `OllamaClient`). *(inferred)* It
  abstracts GGUF quantization and model management, so this codebase talks to one stable
  `/api/chat` contract instead of embedding `llama.cpp` bindings directly.

## The pipeline, stage by stage

```
Coursework PDF ──OCR──▶ vault/<course>/<note>.md ─┬──▶ 2-pass extraction ──▶ SQLite ──▶ graph.json
                                                   └──▶ chunking ──▶ FastEmbed ──▶ LanceDB
                                                                 │
                                        query ──────────────────▶ hybrid retrieval ──▶ answer
```

The vault is the fixed point everything else derives from and can be rebuilt from. The graph
(SQLite + the in-memory NetworkX view of it) and the vector index (LanceDB) are both
*derived, rebuildable caches* over the vault's Markdown — delete either one and
`rebuild-graph`/`rebuild-vectors` regenerate it. The vault notes themselves are not
rebuildable: re-running OCR costs money and re-rolls the transcription, possibly differently.
That asymmetry is why `ObsidianVaultManager` treats the vault as an external system this repo
reads through an adapter, not as a domain concept it owns (see `CONTEXT-MAP.md`).

### 1. Ingestion — turning a photo of handwriting into a graph-ready Markdown note

`IngestionPipeline.process_pdf` (`services/ingestion/app/pipeline.py`) renders each PDF page
to an image via PyMuPDF, hands each page to whichever `BaseOCRProvider` subclass was
configured, and streams the result into the vault incrementally — one page written at a
time, not buffered until the end, so a crash on page 40 of 60 doesn't lose pages 1–39. It
writes to a hidden `.{filename}.partial` sidecar and only `os.replace`s it over the real
target once OCR succeeds end to end; writing straight to the target file used to truncate
any *existing* note on a re-ingest before the new content was ready, destroying good content
on a mid-run failure.

Four OCR providers exist because "run a vision model over a photo of handwriting" has very
different cost/accuracy/privacy tradeoffs depending on what's available: `gemini_ocr.py`
(cloud, 3-page batching to stay under the 15 RPM free-tier ceiling, paced 4s between
batches), `handwriting_provider.py` (100% local, 4-station VLM pipeline — see
`HANDWRITING_VLM_PIPELINE.md` for the real per-station breakdown, since the stations aren't
what an older draft of this doc claimed), `marker_provider.py` (typeset PDFs, not
handwriting), `local_ocr.py` (pix2tex, optional). Output passes through
`ingestion/app/sanitizer.py` for LaTeX normalization before it's written.

**Ingestion writes the vault note only.** It does not touch the graph or the vector index —
that's `rebuild-graph --no-force` afterwards, indexing just the new note. Keeping these
separate means an ingest that fails halfway through OCR never leaves the graph half-updated.

### 2. Graph extraction — two LLM passes, then identity resolution, then storage

This is the part that actually builds the product. Given one vault note, the goal is: what
mathematical entities does this note introduce, and how do they relate to entities already in
the graph (possibly from a different course, possibly from a note ingested months ago)?

**Why two passes instead of one.** A single LLM call asked to extract entities *and* their
relationships from a long note runs into token truncation and hallucinated garbage nodes
(`"From Calculus"`, `"If The Equation"` — sentence fragments, not concepts) faster than the
same work split into two focused calls. So `MathGraphIndexer.index_note`
(`services/graph/app/indexer.py`) splits the note into H1–H3 sections
(`_split_chunks`) and runs:

- **Pass 1**, once per section — `llm_extraction.extract_nodes_pass`
  (`services/graph/app/llm_extraction.py`), using the prompt in `prompts.py`. Extracts
  entities and classifies each on two independent axes: `kind` (`Object`, `Statement`,
  `Definition`, `Method`, `Formula`, `Proof`, `Example` — what the thing *is*) and `role`
  (`Theorem`, `Lemma`, `Corollary`, ... — only set when the *source text itself* labels it
  that way; role is reported, never inferred). This two-axis split replaced a single
  `entity_type` enum that conflated the two (`docs/vocabulary-diagnosis.md` V2) — a named
  result that the text never calls a theorem shouldn't silently become one.
- **Pass 2**, once on the whole document — `llm_extraction.extract_edges_pass`. Takes the
  node ids Pass 1 resolved plus a sample of existing graph concepts, and links directional
  relationships (`DEPENDS_ON`, `PROVES`, `USES_DEFINITION`, `HAS_HYPOTHESIS`, `EQUIVALENT_TO`,
  ...) between them, picking the most specific relation that applies rather than defaulting
  everything to `DEPENDS_ON`.

Both passes degrade the same way: try each Gemini candidate model (any failure — quota,
timeout, malformed response — moves to the next candidate), then each local Ollama model,
then fall back to `block_extractor.block_extraction` — a 100% deterministic parser for LaTeX
theorem/definition environments, typed Markdown headings, and `[[wikilinks]]`. That ladder is
one shared function, `shared/llm/fallback.with_gemini_then_ollama`, used identically here and
by retrieval's answer synthesis — the point being that **nothing in this system hard-fails
because a cloud API is rate-limited or a local model isn't pulled yet**; it just degrades to
a less precise but still-usable tier. `graph_health.py`'s extraction-provenance report exists
specifically to surface how much of the graph is currently running on the degraded tier.

**Why identity resolution is a deterministic lookup, not a vector search.** Two notes both
mentioning "the Wronskian" need to resolve to the *same* graph node; two notes both
mentioning "T" (a linear map in one lecture, a topology in another) need to resolve to
*different* nodes. An embedding-similarity threshold can't reliably tell those apart — it
either merges the overloaded symbol into one node, or fails to merge the same concept
spelled differently, and there is no threshold that gets both right. `authority.py`'s
`resolve_concept` instead walks a fixed ladder: does this surface form already mean something
specific *in this document*? *In this course*? Globally (an existing alias, or a fresh exact
Wikidata lookup, cached forever after)? Only if all of that misses does it mint a new
`CUST_<hash>` id and queue the surface form for human review. This is why `graph/` has no
dependency on `vector/` at all — resolution needs no embedding model, and the id it produces
is opaque (a QID or a hash) on purpose, so the only thing that can carry meaning afterward is
the node's `label` attribute, never the id itself.

**Why SQLite, not the in-memory graph, is the source of truth.** `.storage/concepts.db`
(`graph_store.py`) holds `concepts`/`aliases` (identity, owned by `authority.py`) and
`mentions`/`edges` (structure). `MathGraphIndexer.graph` — the `nx.DiGraph` everything else
in this codebase touches — is rebuilt from that SQLite data on every startup
(`graph_store.load_graph`); it's a derived cache kept because traversal, layering, and cycle
detection are trivial in NetworkX and awkward in SQL, not because it's authoritative.
`graph.json` is one further export off *that*, written by `save_graph()` purely for the two
consumers that read a file directly instead of going through code — `/api/graph` and
`scripts/graph_health.py` — and is never read back in. Three representations of the same
graph, in strict one-directional derivation: **SQLite → NetworkX → graph.json**. Confusing
that order (e.g. writing to graph.json as if it were persistence) is the exact mistake
`CLAUDE.md`'s invariants section exists to prevent.

**Cycles are a real, structural risk, not a hypothetical.** Every one of these relations is
well-founded mathematically — nothing should legitimately generalize itself, or use itself in
its own proof — so a cycle is always evidence of a conflict, never a valid structure to
preserve. Two notes can each independently assert a relation between the same pair of
concepts in opposite directions (one says "A depends on B" via a generic relation, another
says "B uses A in its proof" via a specific one), and that breaks hierarchical layout and
topological traversal regardless of which relation is involved. `dag.py`'s `resolve_2cycle`
picks the more specific relation by a fixed priority
table when two edges conflict (used identically at write time in `index_note` and in the
batch `repair_graph_dag` pass), and converts genuinely mutual pairs into a single
`EQUIVALENT_TO` edge rather than leaving both directions stored. This is applied, not just
theoretical: the live graph currently has 0 cycles.

### 3. Vector indexing — chunking that doesn't destroy math

`chunk_math_markdown` (`services/vector/app/chunker.py`) exists because a standard
character-count chunker will split `$$ \int_0^1 f(x)\,dx $$` in half, or separate a theorem
statement from the proof that immediately follows it — both of which produce chunks that
embed to something meaningless. It splits on page markers, then headings, then enforces a
max size *without ever splitting inside a `$$...$$` block*, merges fragments that end up too
small to be useful on their own, and finally prepends a trailing overlap from the previous
chunk specifically so a proof chunk still carries the theorem statement it's proving.
`LocalVectorStore.add_chunks` (`services/vector/app/store.py`) embeds with FastEmbed
(CUDA if available, CPU fallback) and writes to LanceDB — **deleting existing rows for the
same `source` first**, so re-running ingestion on an updated note is idempotent instead of
accumulating stale duplicate chunks forever.

### 4. Retrieval — hybrid context, then synthesis with the same fallback ladder

`MathQueryEngine.retrieve_context` (`services/retrieval/app/engine.py`) does two independent
lookups and concatenates their output into one context string: LanceDB hybrid (vector +
native BM25) search over chunks, and a **bounded graph neighborhood** — embed the query,
find the graph nodes whose `label`+`description` embed closest to it (seeds are found by
*meaning*, since node ids are opaque), then call `MathGraphIndexer.neighborhood(seeds,
hops=1)` for a 1-hop expansion. That bound is deliberate: the alternative (walking the whole
graph, or unlimited hops) doesn't stay relevant to the query, it just gets noisy. Retrieval
never walks `.graph` directly for this reason — `neighborhood()` is the only sanctioned
entry point, and it's also why `retrieval/` doesn't import NetworkX at all.

The assembled context is handed to the same `with_gemini_then_ollama` ladder extraction uses.
If every tier is unavailable, the query still returns something: the raw retrieved context
with a note appended, rather than a 500 error — a deliberate "always produce something"
philosophy that shows up throughout this codebase, not just here.

### 5. Serving

`src/server.py` builds the FastAPI app, runs a `lifespan` that constructs the three shared
singletons in dependency order (`LocalVectorStore` → `MathGraphIndexer` → `MathQueryEngine`,
each expensive enough — loading an embedding model, loading the graph, embedding every graph
node — that they're built once per process and shared via `app.state`, never per request),
and mounts one `APIRouter` per concern from `src/routes/`: `ingest.py`, `query.py`,
`vault.py` (also serves `/api/graph`), `admin.py` (health, settings, rebuilds, clear). The
same singletons back `src/cli.py`'s `--json` verbs via `src/wiring.py` — the CLI and the HTTP
API are two entry points onto the identical in-process objects, not two implementations.

## End-to-end request lifecycle

The stage-by-stage walkthrough above explains each piece; this traces two full requests
through the actual call sequence, function by function, the way you'd step through it in a
debugger. Both start at `lifespan` in `src/server.py` having already built and attached
`app.state.vector_store` / `.graph_indexer` / `.query_engine` — neither trace constructs
anything expensive itself, only reaches into what's already there.

**`POST /api/query`** — "explain the Wronskian":

1. `src/routes/query.py::query_knowledge_base(payload, request)`. FastAPI has already
   validated `payload` against `QueryRequest` (Pydantic) before this function body runs — a
   non-empty `prompt`, `top_k` in `[1, 20]`, `temperature` in `[0.0, 1.0]` are enforced by the
   model's `Field(...)` constraints, not by hand-written `if` checks here.
2. `payload.prompt.strip()` is checked non-empty (the one validation Pydantic's `Field`
   couldn't express); empty raises `HTTPException(400)` immediately.
3. `request.app.state.query_engine.query(...)` — `MathQueryEngine.query`
   (`services/retrieval/app/engine.py`).
4. `self.retrieve_context(...)`, which does two independent lookups:
   - `self.vector_store.search_similar(prompt, top_k, course, query_type="hybrid")` →
     `LocalVectorStore.search_similar` (`vector/app/store.py`) embeds the prompt with
     FastEmbed, runs `self.table.search(query_vec).limit(top_k)` against LanceDB, optionally
     narrowed by `.where(f"course = '{course}'")` (see "Is this following good practices?"
     for why that specific line is worth a second look), returns a list of chunk dicts.
   - `self._find_similar_nodes(prompt, top_k=3)` embeds the prompt again, compares against
     `self._node_embeddings` (precomputed at engine construction / after each rebuild, keyed
     by node label+description, never by node id), keeps ids with cosine similarity > 0.3.
     Those seed ids go to `self.indexer.neighborhood(seed_ids, hops=1)`
     (`graph/app/indexer.py`) — a pure in-memory NetworkX BFS one hop out, no I/O.
   - Both results are formatted into one context string.
5. Back in `query()`: the context is dropped into `MATH_QUERY_PROMPT_TEMPLATE`, then handed to
   `with_gemini_then_ollama(try_gemini, try_ollama)` (`shared/llm/fallback.py`) — Gemini
   candidate models in order, then local Ollama models in order, closures defined inline in
   `query()`.
6. The synthesized answer (or, if every tier failed, the raw retrieved context with a note
   appended) is wrapped `{"status": "success", "answer": ...}` and returned; FastAPI
   serializes it via `JSONResponse`.

Nothing in this path writes anything — a query is pure read, which is why it's safe to retry
and cheap to run repeatedly while iterating on a prompt.

**`POST /api/ingest`** (`auto_index=true`) — a PDF lecture note becomes vault content, then
graph nodes, then vector chunks:

1. `src/routes/ingest.py::ingest_pdf(...)`. Validates the filename ends in `.pdf`, copies the
   uploaded file to `.storage/temp_uploads/` via `shutil.copyfileobj`.
2. Picks an OCR provider by `ocr_mode` (`HandwritingOCRProvider` or `GeminiOCRProvider`),
   constructs `IngestionPipeline(ocr_provider=...)`
   (`services/ingestion/app/pipeline.py`), calls `.process_pdf(pdf_path, course_name)`.
3. Inside `process_pdf`: `pdf_to_images` renders every page via PyMuPDF, then each page goes
   through the provider (batched if it supports `process_images_batch`, page-by-page
   otherwise), streamed into a `.{filename}.partial` sidecar file as it goes — see "Ingestion"
   above for why. On success, `os.replace`s the sidecar over the real vault path and returns
   it.
4. Back in the route, if `auto_index`:
   - `request.app.state.graph_indexer.index_note(target_note_path, use_llm=True)` — the full
     Pass 1 (per section) → Pass 2 (whole document) → identity resolution → SQLite write
     sequence described in "Graph extraction" above, followed by `.save_graph()` (exports
     `graph.json`) and `request.app.state.query_engine.refresh_node_embeddings()` (so the very
     next query can find the concepts this note just introduced).
   - Independently, `chunk_math_markdown(...)` (`vector/app/chunker.py`) then
     `vector_store.add_chunks(...)` — chunking and embedding the same note's text for hybrid
     retrieval. This is a **separate** pass over the note from graph extraction, not a
     byproduct of it; a chunk and a graph node are unrelated units derived independently from
     the same Markdown.
   - Each of those two blocks is wrapped in its own `try`/`except` that logs and continues —
     a graph-indexing failure doesn't prevent the vector index from updating, or vice versa,
     and either way the vault note (already written in step 3) is kept regardless.
5. Returns the note's content plus `graph_indexed`/`vector_chunks` counts so the UI can show
   what happened.
6. `finally:` deletes the temp upload — happens even if anything above raised.

This path is where the earlier claim about `async def` not buying real concurrency matters
most: steps 2–4 can legitimately take tens of seconds to minutes (OCR is the dominant cost),
and for that whole span, per "Is this following good practices?" below, this one request
blocks every other endpoint in the process — including a client polling `/api/settings` to
show ingest progress.

## Known open issues (so this doc doesn't oversell a finished system)

Graph identity is fixed and verified (0 duplicate groups on the live graph — 225 nodes as of
this writing). DAG-ness is also fixed: `dag.py`'s write-time and batch repair genuinely work
— the live graph currently has 0 cycles. `docs/diagnosis.md` and `plan.md` Phase 9 have the
history of how each got closed out; don't trust an older doc that says otherwise (one did,
inside this repo, until this pass corrected it — see `CLAUDE.md`'s "Known defects" for the
current numbers, since that's the section that stays current).

What's genuinely still open, per `plan.md` Phase 8's own stated exit bar (no relation over
~50%, no kind over ~55%): the two-axis `kind`/`role` split and 12-relation vocabulary are
shipped and running, and node `kind` has cleared its bar (`Object` 44%, spread across 10
kind/role combinations) — but relation hasn't quite cleared its bar yet. `DEPENDS_ON` sits at
61.1% of edges, sharply down from the 78.5% Phase-7 baseline but still above target. A
handful of edges (`USES_LEMMA`) also predate `_normalize_relation`'s retired-name rewrite and
haven't been migrated. Re-running `rebuild-graph` on the notes extracted before Phase 8
shipped is the most direct path to closing the gap, and hasn't been done project-wide yet.

A full `rebuild-graph` is **not** a repair by itself for either of the above — it re-runs
every naming and typing decision through the LLM again, which changes *which* relations or
cycles exist without guaranteeing fewer of them. It only helps here because the newer prompt
(Phase 8's relation definitions) is what's actually different, not because rebuilding is
inherently corrective.

## Is this following good practices?

An honest audit, not a sales pitch — each item below is something actually observed in the
code this session, not a general opinion about what "good" looks like.

**What's done well:**

- **Dependency injection with real defaults, not just for testability's sake.**
  `MathGraphIndexer`, `MathQueryEngine`, and `LocalVectorStore` all take their collaborators
  as constructor arguments defaulting to `None` and falling back to constructing the real
  class — `wiring.py` uses the injection side for the shared singletons, tests use it to
  construct one package in isolation, and nothing had to be built twice to support both.
- **Idempotent writes, checked in practice, not just claimed.** `add_chunks` deletes existing
  rows for a `source` before inserting; `graph_store`'s inserts use `INSERT OR IGNORE`/
  `INSERT OR REPLACE`; `authority.resolve_concept` re-derives the same `CUST_<hash>` from a
  normalized key every time, so re-running extraction on an unchanged note doesn't accumulate
  duplicates. Re-running the same ingest twice is safe by design, not by luck.
- **Parameterized SQL, consistently, in the SQLite layer.** Every query in `graph_store.py`
  and `authority.py` uses `?` placeholders, never string interpolation — the one place that
  pattern *isn't* followed is LanceDB (see below), which makes the inconsistency more visible,
  not less.
- **The LLM output contract is structural, not textual.** `response_schema=MathNodeExtraction`
  makes Gemini itself conform to the Pydantic shape; nothing here regexes a JSON blob out of
  free text. Combined with `with_gemini_then_ollama`, a malformed response is just another
  exception the fallback ladder already knows how to handle.
- **A path-traversal guard exists on the one route that needed it.**
  `GET /api/vault/note`'s `path` query param is `Path(path).resolve()`d and checked
  `.is_relative_to(vault_path)` before the file is read — the one endpoint that takes a
  filesystem path from the client doesn't trust it blindly.
- **`CLAUDE.md`'s Invariants section is a genuinely unusual practice worth naming as a
  strength.** Most repos don't maintain a living list of "this specific bug happened because
  of this specific assumption, here's the rule that prevents it happening again" — this one
  does, and it's precise enough to have caught real drift during this session (see the "Known
  defects" correction above).
- **The test suite is substantive, not decorative.** `tests/test_dag.py`,
  `test_graph_indexer.py`, and `test_graph_store.py` cover real edge cases — 2-cycle
  resolution by relation priority, symmetric-relation canonicalization, legacy
  `entity_type`-to-`kind`/`role` migration — not just "does it import."

**What's questionable — real gaps, verified this session, not guesses:**

- **LanceDB filter strings are built by raw f-string interpolation, not parameter binding** —
  the one inconsistency in an otherwise-careful codebase. `vector/app/store.py`:
  `self.table.delete(f"source = '{source}'")` and
  `search.where(f"course = '{course}'")`. `course` is client-supplied — a request body field
  on `/api/query`, a form field on `/api/ingest` — and neither is escaped. A `course` value
  containing a single quote breaks the query outright today (a self-inflicted correctness bug,
  demonstrable, not theoretical); a deliberately crafted value could manipulate the filter's
  boolean logic, since LanceDB's `.where()` accepts a SQL-like predicate. Low real-world
  severity right now — this only binds to `127.0.0.1` with no auth, so the "attacker" already
  has full filesystem access — but it's exactly the kind of pattern that becomes a real
  vulnerability the moment this is ever exposed past localhost, and every SQLite call
  elsewhere in this same codebase shows the fix is already the house style: bind the
  parameter, don't format the string.
- **The FastAPI app is async in name only — no route handler actually yields the event
  loop.** Every handler in `src/routes/` is declared `async def`, which means FastAPI does
  *not* automatically run it in a threadpool (that escape hatch only applies to plain `def`
  handlers) — it assumes the body is either fast or properly non-blocking. None of it is:
  `requests.post()` to Ollama (synchronous, up to a 300s timeout for vision calls), the Gemini
  SDK's `generate_content()` call, PyMuPDF page rendering, and every graph/vector write all
  run directly on the event loop with no `await`, `run_in_executor`, or `asyncio.to_thread`
  anywhere in the request path (checked directly — zero occurrences). The practical
  consequence: this process can genuinely serve exactly one in-flight request at a time. A
  multi-minute `/api/ingest` or `/api/rebuild/graph` call stalls every other endpoint,
  including a trivial `/api/settings` read, for its entire duration. For a single person using
  their own local instance this is mostly invisible — but it means the "async" framework isn't
  currently buying any concurrency, and that's worth knowing before assuming otherwise.
- **Tests are not isolated** (already an invariant in `CLAUDE.md`, restated here because it's
  a genuine practices gap, not just a fact to know): most tests read and write the real
  `.storage/` — including production LanceDB and SQLite — with no fixtures or teardown.
  `test_graph_store.py` is the one file that does this right, with an injectable `db_path`
  every SQLite-touching function already accepts. That pattern existing and not being used
  everywhere is the gap, not a missing capability.
- **No auth, no rate limiting, no upload size cap, no CORS policy — and this assumption is
  nowhere written down as a decision.** Consistent with a genuinely local, single-user tool,
  and not a defect in that context; `uvicorn.run(..., host="127.0.0.1", ...)` in
  `src/server.py` is the only thing currently enforcing that boundary. The gap is that this is
  an implicit assumption embedded in one line of one file, not a documented threat model — the
  moment someone changes that host to `0.0.0.0` to reach it from another device on their LAN,
  every item above becomes live and unauthenticated with no doc anywhere saying "don't do that
  without adding X."
- **47 bare `except Exception` blocks** across `services/`+`src/`. Mostly a deliberate,
  working instance of the "always degrade, never hard-fail" philosophy this whole codebase is
  built around — but broad enough that a genuine bug in, say, the node-writing loop inside
  `index_note` would currently look identical in the logs to "the LLM tier was unavailable."
  Worth an occasional pass asking, of each one, "is this catching a real fallback boundary, or
  hiding a bug as a degraded tier" — not a rewrite, just a habit this codebase's own density of
  the pattern makes easy to lose track of.
- **The "most specific relation" instruction is followed inconsistently in the actual
  output** — covered in detail above, restated here because it's as much a practices question
  (is the prompt's stated intent actually being enforced, or just hoped for) as a data-quality
  one: `DEPENDS_ON` is the fallback 61% of the time, and a same-session sample found the
  model's own evidence text naming a sharper relation in cases where a more generic one was
  still stored.

## Where to go from here

- **`HANDWRITING_VLM_PIPELINE.md`** — the local OCR pipeline's actual four stations.
- **`docs/structure.md`** — exact call chains, one line per function, no prose.
- **`docs/flow.md`** — the data shape at each stage (what a chunk dict looks like, what the
  SQLite tables hold).
- **`docs/API.md`** — the HTTP contract.
- **`plan.md`** — the full phase-by-phase history, including Phase 8's own exit-bar numbers
  in more detail than the summary above.
