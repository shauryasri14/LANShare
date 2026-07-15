# Technical Report — LANShare

## Model and runtime used

- **Model:** `Xenova/all-MiniLM-L6-v2` (sentence embedding model)
- **Runtime:** Transformers.js, running in-browser via WebAssembly/WebGPU (whichever the browser selects automatically)
- **Backend runtime:** Python 3 standard library (no ML runtime on the backend — all inference happens client-side)

## Quantization or optimization techniques

- **Quantization:** None applied manually. `pipeline()` is called with only the task ("feature-extraction") and model ID ("Xenova/all-MiniLM-L6-v2") — no options object, so Transformers.js's default behavior applies, which loads the pre-quantized `int8` ONNX version automatically.
- **Other runtime optimization:** None beyond the library defaults — no `device` option, so it uses the default execution provider (WASM/CPU) rather than explicitly requesting WebGPU.
- **Application-level optimization:** Embeddings are cached and reused across indexing cycles — `buildIndex()` checks for an existing entry (matched by filename + peer IP) before re-embedding a file, so unchanged files aren't reprocessed by the model on every 10-second refresh.

## Model size

- Actual measured size: **22.97 MB** (transferred, verified via DevTools Network tab, filtered on `onnx`, cold load with cache disabled — measured request from `cas-bridge.xethub.hf.co`, the actual weights-serving endpoint; the `huggingface.co` request preceding it is a redirect with no payload)



## CPU / GPU / NPU usage


- No dedicated NPU usage (standard laptop/browser environment)



## Tested device specifications



| Device | OS | CPU | RAM | Browser |
|---|---|---|---|---|
| Asus Vivobook |Windows 11 |AMD Ryzen 3 7320U |8.00 GB |Chrome |
| HP Pavillion |Windows 11 |Intel Core Ultra 5 125H |16.00 GB |Chrome |

## Additional relevant technical details

- Text extraction is capped at ~5000 characters per file to keep embedding time reasonable.
- The embedding model is loaded once per browser session and reused for both indexing and query embedding.
