# Handwritten STEM Document Ingestion & VLM Pipeline

## Why this exists

A photo of handwritten lecture notes is a much harder OCR target than a typeset PDF: faint
pencil strokes, blue/grey notebook ruling lines that a vision model's tokenizer can confuse
with characters (`+` misread as `†`), and — if you're running the vision model locally rather
than paying per page for a cloud API — real GPU memory limits on consumer hardware (a GTX
1650 or a laptop 3050 has ~4 GB VRAM, and a naive full-resolution image blows past that fast).
This pipeline (`HandwritingOCRProvider`, `services/ingestion/app/handwriting_provider.py`) is
the 100%-local answer to that: OpenCV preprocessing to strip the ruling lines before the
model ever sees them, an aggressive resize to keep VRAM bounded, and a lightweight local LLM
pass afterward to clean up the raw transcription. `gemini_ocr.py` is the cloud alternative —
same output contract, no local GPU needed, paced to survive the free-tier rate limit.

## The four stations, as the code actually runs them

`HandwritingOCRProvider.process_image` runs every page through exactly these four steps —
this is corrected against the code, not the pipeline an earlier draft of this doc described
(which invented a separate "resize" station; resizing is not a station of its own):

```
[ Input page image ]
        │
        ▼
 Station 1 — Preprocessing            ImagePreprocessor.preprocess_pil
   (red-channel extraction + CLAHE, one function, not two stations)
        │
        ▼
 Station 2 — Local Vision OCR         OllamaVisionOCR.process_image
   (resize to ≤1024px happens here, inside OllamaClient.vision_chat)
        │
        ▼
 Station 3 — Contextual Repair        ContextualReassembler.refine_markdown
   (a second, smaller local LLM call — falls back to the raw transcript if unavailable)
        │
        ▼
 Station 4 — Export
   (no further processing — returns the refined Markdown for this page)
```

Debug artifacts from every station are written under `.storage/debug_handwriting/page_N/` —
useful for actually seeing where a bad transcription went wrong, since each station's output
is a plain file you can open.

### Station 1 — `ImagePreprocessor.preprocess_pil` (`handwriting/preprocessor.py`)

One function does two things, not two separate stations: **channel extraction**, then
**contrast enhancement**, on the same image.

Blue/cyan notebook ruling lines are high in the Blue and Green channels and low in Red;
pencil and black ink are low across all three. Splitting the image into channels and keeping
only Red (`cv2.split(cv_img)` → `r`) makes the ruling lines vanish while the ink stays. CLAHE
(Contrast Limited Adaptive Histogram Equalization, `cv2.createCLAHE`) is then applied to that
red-channel image to sharpen faint pencil strokes without blowing out the paper texture —
tuned gently (`clipLimit=1.5`) because a stronger setting introduces dot noise that the vision
model then tries to transcribe as content.

### Station 2 — `OllamaVisionOCR.process_image` (`handwriting/ollama_vlm.py`)

Sends the preprocessed image to local Ollama's `qwen2.5vl:3b` via `OllamaClient.vision_chat`
(`shared/llm/ollama.py`), with a prompt asking for clean Markdown with `$...$`/`$$...$$` math
delimiters. **The VRAM bound is enforced here, not as a separate station**:
`OllamaClient._pil_to_base64` thumbnails the image to a max 1024px long edge before encoding
it — this is what actually keeps the request under the ~2 GB VRAM a 3B vision model needs on
a consumer GPU, not a preprocessing step.

### Station 3 — `ContextualReassembler.refine_markdown` (`handwriting/reassembler.py`)

A vision model transcribing a full page in one pass tends to produce broken sentence
boundaries and inconsistent LaTeX delimiters. This station is a second, separate local LLM
call (`qwen2.5-coder:3b` — a smaller *text* model, not a vision model, since the input here is
already the draft Markdown) whose only job is repairing those two things without touching
mathematical meaning. It's explicitly optional: `refine_markdown` returns the raw
transcription unchanged if Ollama isn't reachable, rather than failing the page.

### Station 4 — Export

Not a processing step. `process_image` returns the refined Markdown for the page;
`process_images_batch` concatenates every page's output with an HTML `<!-- Page N -->`
comment marker, which is what lets `chunk_math_markdown` later split back on page boundaries.

## The cloud alternative — `gemini_ocr.py`

`GeminiOCRProvider` solves a different problem: no local GPU needed, at the cost of API
calls. Its two load-bearing details:

- **3-page multi-image batching** (`process_images_batch`, `batch_size=3`): one Gemini call
  carries three page images instead of one, cutting a 30-page PDF from 30 calls to 10.
- **4-second pacing delay** between batch calls: 10 calls at 4s apart take ~40s total, which
  stays under Gemini's free-tier 15 requests/minute ceiling — the alternative (no pacing) hits
  `429 RESOURCE_EXHAUSTED` around page 12–15 on a naive one-call-per-page loop.

Both providers implement the same `BaseOCRProvider` interface and produce the same Markdown
contract, so `IngestionPipeline` (`services/ingestion/app/pipeline.py`) doesn't need to know
or care which one ran.
