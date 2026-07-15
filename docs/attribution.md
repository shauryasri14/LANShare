# Attribution — LANShare

## Pretrained models

- **all-MiniLM-L6-v2** — sentence embedding model, used via the `Xenova/all-MiniLM-L6-v2` ONNX conversion for browser compatibility.
  Original model by the Sentence-Transformers team; ONNX/browser-compatible conversion hosted by Xenova.

## Libraries and frameworks

- **Transformers.js** (`@xenova/transformers`) — used to load and run the embedding model directly in the browser.
- **PyPDF2** — used for text extraction from PDF files in `backend.py`.
- **Python standard library** — `socket`, `threading`, `json`, `http.server` used for peer discovery, TCP file transfer, and the local HTTP API. No third-party backend frameworks were used.

## Datasets

- No custom dataset was used or created; the embedding model is a general-purpose pretrained sentence encoder, not fine-tuned for this project.

## APIs

- No external/cloud AI APIs are used anywhere in the application. The only external network call in the entire app is the one-time model file download from a CDN (jsDelivr), which serves static model files, not an API in the traditional sense.


## AI assistance disclosure

> 

Portions of the initial code scaffold (peer discovery structure, HTTP API layout, and frontend embedding pipeline) were drafted with AI assistance (Claude) as a starting point, then debugged, tested, and extended by the team across the hackathon period — including diagnosing and fixing real networking issues (VM bridged-networking configuration, broadcast address handling) encountered during development.
