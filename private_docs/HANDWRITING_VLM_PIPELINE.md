# 🖊️ Handwritten STEM Document Ingestion & VLM Pipeline

## Overview

Handwritten mathematics lecture notes present unique challenges:
1. **Low Contrast & Blue Notebook Ruling Lines:** Notebook lines interfere with vision model OCR, causing misread symbols ($+ \rightarrow \dagger$).
2. **Heavy GPU Memory Constraints:** Local VLM models easily trigger Out-Of-Memory (OOM) crashes on 4 GB VRAM consumer GPUs (NVIDIA GTX 1650 / RTX 3050 mobile).
3. **Cloud API Rate Limits:** Multi-page PDF ingestion hitting 1-by-1 page loops can hit Gemini free-tier rate limits (15 RPM).

Comeback Helper addresses these challenges through custom OpenCV pre-processing, 100% offline Qwen2.5-VL via Ollama, and **3-Page Multi-Image Batching with 4s Pacing Delays** in `GeminiOCRProvider`.

---

## Ingestion Architecture

```
                                [ Input PDF ]
                                      │
                                      ▼
                        [ PyMuPDF Image Extraction ]
                        (Render pages at 200 DPI)
                                      │
              ┌───────────────────────┴───────────────────────┐
              │                                               │
              ▼                                               ▼
   [ Local Handwriting Mode ]                        [ Cloud Gemini Vision Mode ]
   (Station 1: OpenCV Red Channel)                   (Station 1: 3-Page Image Batching)
   (Station 2: CLAHE Contrast)                       (Station 2: 4s Rate-Limit Pacing)
   (Station 3: Max 1024px Resize)                     (Station 3: Candidate Model Retry)
   (Station 4: Ollama qwen2.5vl)                     (Station 4: Stream Markdown Note)
              │                                               │
              └───────────────────────┬───────────────────────┘
                                      │
                                      ▼
                        [ Obsidian Vault Note Output ]
```

---

## 1. Cloud Gemini Vision Subsystem (`services/ingestion/app/gemini_ocr.py`)

### 3-Page Multi-Image Batching (`process_images_batch`)
- Groups **3 consecutive page images per API call** (`batch_size = 3`).
- For a 30-page PDF, API calls are reduced from 30 down to 10 (66% reduction in API calls).

### Rate-Limit Pacing Delay (4s)
- Applies a **4-second pacing delay** between batch calls.
- 10 API calls with a 4s delay execute in ~40 seconds total, remaining safely under Gemini's **15 Requests Per Minute (RPM)** free-tier quota ceiling.

### Automatic 429 Retry Backoff & Candidate Loop
- Parses Gemini `Retry-After` delay headers on `429 RESOURCE_EXHAUSTED` responses and pauses execution cleanly before retrying.
- Loops over candidate models (`gemini-flash-latest` $\rightarrow$ `gemini-flash-lite-latest`) to guarantee ingestion completion.

---

## 2. Local 4-Station VLM Subsystem (`services/ingestion/app/handwriting/`)

### Station 1: Red Channel Thresholding (`preprocessor.py`)
Standard blue or gray notebook lines overlap handwritten ink. In RGB color space, blue lines have high values in the Blue and Green channels but low values in the Red channel. Pencil and black ink have low values across all three channels.

By extracting the **Red channel image**, notebook ruling lines vanish completely while black ink and pencil text remain crisp.

### Station 2: Adaptive CLAHE Contrast Enhancement
Contrast Limited Adaptive Histogram Equalization (CLAHE) is applied to sharpen faint pencil strokes without blowing out background paper texture.

### Station 3: Resolution & VRAM Tuning
Images are dynamically resized to max 1024px long edge, reducing image token counts and enforcing a strict **~2.1 GB VRAM limit** on Ollama.

### Station 4: Ollama Qwen2.5-VL (3B) Execution
Sends base64-encoded preprocessed images to local Ollama (`qwen2.5vl:3b`) with system prompts mandating standard LaTeX Markdown output (`$inline$` and `$$block$$`).
