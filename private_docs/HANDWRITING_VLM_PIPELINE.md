# ✍️ Handwritten STEM Notes VLM Pipeline

## Overview

Handwritten mathematics notes written on blue/cyan ruled notebook paper present severe OCR challenges:
- Notebook ruling lines intersect mathematical symbols (frac bars, integral signs, exponent dots).
- Low contrast between dark blue ink and light blue paper lines.
- Hardware constraints: Running local Vision-Language Models alongside vector search on consumer GPUs (e.g., 4GB VRAM NVIDIA GTX 1650) typically causes CUDA Out-Of-Memory (OOM) crashes or system RAM paging freezes.

Comeback Helper addresses this with a specialized **4-Station Sequential Local VLM Pipeline**.

---

## The 4 Processing Stations

```
[ Page Image ]
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ Station 1: OpenCV Red-Channel Line Erasure & CLAHE     │
│ (src/ingestion/handwriting/preprocessor.py)            │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ Station 2: Native Local VLM via Ollama (qwen2.5vl:3b)  │
│ (src/ingestion/handwriting/ollama_vlm.py)              │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ Station 3: Contextual LLM Repair Pass                  │
│ (src/ingestion/handwriting/reassembler.py)             │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ Station 4: Incremental Vault Persistence & Indexing    │
│ (src/ingestion/handwriting_provider.py)                │
└─────────────────────────┴──────────────────────────────┘
```

---

## Station 1: Red Channel Extraction & Line Erasure

### Computer Vision Rationale
Notebook paper ruling lines are printed with blue/cyan ink. In RGB color space:
- Blue ruling lines have **high values in the Blue channel** and **low values in the Red channel**.
- Black pencil or ink handwriting has **low values across all channels (Red, Green, Blue)**.

By extracting only the **Red channel** from the page render:
1. The blue ruling lines become nearly white/invisible ($R \approx 255$).
2. The handwritten ink remains dark ($R \approx 0$).

```python
# src/ingestion/handwriting/preprocessor.py
cv_img = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
b, g, r = cv2.split(cv_img)  # Extract Red channel

# Contrast adjustment on Red channel using CLAHE
clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
enhanced = clahe.apply(r)
```

This optical pre-processing completely erases notebook paper gridlines without heavy deep-learning segmentation models.

---

## Station 2: Local VLM Execution (Ollama `qwen2.5vl:3b`)

### Resolution Downscaling & Base64 Encoding
Vision Transformers process images by splitting them into visual patches. High-resolution renders (e.g., $3000 \times 4000\text{px}$) create thousands of patches, leading to quadratic memory expansion ($O(N^2)$) in self-attention layers.

`ollama_vlm.py` uses PIL `.thumbnail()` inside `_pil_to_base64` to enforce a max dimension bound (`max_dim = 1024`):

```python
# src/ingestion/handwriting/ollama_vlm.py
def _pil_to_base64(self, image: Image.Image) -> str:
    img_copy = image.copy()
    img_copy.thumbnail((self.max_dim, self.max_dim), Image.Resampling.LANCZOS)
    
    buffered = io.BytesIO()
    img_copy.save(buffered, format="JPEG", quality=90)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
```

### Options & Per-Request GPU Offloading
In `process_image()`, Ollama API options explicitly mandate GPU offloading:

```python
payload = {
    "model": self.model_name,
    "messages": [{"role": "user", "content": prompt, "images": [img_b64]}],
    "options": {
        "num_gpu": 99,       # Offload ALL layers to NVIDIA Discrete GPU
        "main_gpu": 0,       # Select NVIDIA GTX 1650
        "temperature": 0.1,
        "num_predict": 1024
    },
    "stream": False
}
```

### Telemetry & Memory Footprint
- **Model:** `qwen2.5vl:3b` (GGUF 4-bit Quantized)
- **VRAM Allocation:** ~2.1 GB
- **Inference Speed:** ~15–20 seconds per page (NVIDIA GTX 1650)
- **Zero VRAM Spillover:** Safe execution on 4GB consumer GPUs.

---

## Station 3: Contextual LLM Repair Pass

Raw VLM output occasionally misinterprets inline versus block math environments or produces unclosed LaTeX delimiters (e.g., `$\int f(x) dx`).

`reassembler.py` executes a fast repair pass via local Ollama (`qwen2.5-coder:3b`):
1. Verifies inline math delimiters (`$...$`).
2. Normalizes multi-line aligned equations to standard `$$\begin{aligned} ... \end{aligned}$$` blocks.
3. Fixes common LaTeX OCR syntax mistakes.
4. **Graceful Fallback:** If Ollama is unavailable or times out, it retains the raw VLM transcript cleanly without failing.

---

## Station 4: Incremental Vault Persistence & Debug Artifacts

`handwriting_provider.py` orchestrates execution across all stations while saving debugging artifacts:
1. `step1_preprocessed.png` (Ruling lines removed)
2. `step2_raw_vlm_transcript.md` (Raw VLM transcription)
3. `step3_refined_note.md` (Contextually repaired note)
4. Saves the finished note to the vault and returns the markdown text for auto-indexing.
