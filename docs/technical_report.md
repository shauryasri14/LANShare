# Technical Report — LANShare

## Model and runtime used

- **Model:** `Xenova/all-MiniLM-L6-v2` (sentence embedding model)
- **Runtime:** Transformers.js, running in-browser via WebAssembly/WebGPU (whichever the browser selects automatically)
- **Backend runtime:** Python 3 standard library (no ML runtime on the backend — all inference happens client-side)

## Quantization or optimization techniques

> Fill in based on what you actually used. If you used the model as-is with no changes, say so plainly — that's a valid and honest answer.

- [ ] Using the default quantized ONNX version Transformers.js loads automatically (most likely — Xenova's hosted models are typically pre-quantized to `int8` by default)
- [ ] No additional quantization applied on top of the default
- [ ] Any caching/reuse-of-embeddings optimization: **yes** — LANShare avoids re-embedding files that haven't changed since the last index build (see `ai.js`)

## Model size

> Check the actual downloaded model size. Easiest way: open your browser's DevTools → Network tab, reload the page, filter by the model files, and sum the transferred sizes.

- Approximate size: **~25–30MB** (typical for `all-MiniLM-L6-v2` quantized) — replace with your measured value: `___ MB`

## Inference latency

> Measure this directly rather than estimating. Quick way to do it: wrap the embedding call in `ai.js` with timestamps.
>
> ```javascript
> const start = performance.now();
> const embedding = await embedText(text);
> const elapsed = performance.now() - start;
> console.log(`Embedding took ${elapsed.toFixed(1)} ms`);
> ```
> Run this a few times on a typical file and on a typical search query, then report the average.

- Time to embed one document (~500 words): `___ ms`
- Time to embed one search query: `___ ms`
- Time for a full search across N indexed files: `___ ms` (note: search itself, i.e. cosine similarity over cached embeddings, should be near-instant; the model-loading step is the only slow part, and only happens once per session)

## CPU / GPU / NPU usage

> Transformers.js in the browser typically runs on CPU via WebAssembly unless WebGPU is available and used. State plainly which one your setup actually used — check via `navigator.gpu` in the browser console, or just note that no GPU acceleration was configured.

- Execution path used: `___` (CPU via WASM / WebGPU, if enabled)
- No dedicated NPU usage (standard laptop/browser environment)

## Peak memory usage

> Quick way to measure: open Chrome DevTools → Performance/Memory tab, take a heap snapshot before and after loading the model + building the index, and report the difference. Alternatively, use your OS's task manager and watch the browser tab's memory while the app runs.

- Peak browser memory during model load + indexing: `___ MB`

## Tested device specifications

> List every device you actually tested on — this matters more than sounding impressive; two real laptops is genuinely fine.

| Device | OS | CPU | RAM | Browser |
|---|---|---|---|---|
| Device A | | | | |
| Device B | | | | |

## Additional relevant technical details

- Text extraction is capped at ~5000 characters per file to keep embedding time reasonable — this is a deliberate tradeoff, not a limitation you need to apologize for.
- The embedding model is loaded once per browser session and reused for both indexing and query embedding.
