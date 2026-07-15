# Architecture — LANShare

Repo: https://github.com/shauryasri14/LANShare

This document describes how LANShare is built: the system diagram, the on-device AI pipeline, data flow, local vs. cloud components, and the reasoning behind key design decisions.

---

## 1. System diagram

```
┌─────────────────────────────┐          ┌─────────────────────────────┐
│           Device A           │          │           Device B           │
│                               │          │                               │
│  ┌─────────────────────────┐  │          │  ┌─────────────────────────┐  │
│  │      backend.py           │  │  UDP     │  │      backend.py           │  │
│  │  (Python)                 │◄─┼──────────┼─►│  (Python)                 │  │
│  │                           │  │broadcast │  │                           │  │
│  │  • peer discovery        │  │          │  │  • peer discovery        │  │
│  │  • peer list + timeout   │  │          │  │  • peer list + timeout   │  │
│  │                           │  │  TCP     │  │                           │  │
│  │  • manifest server       │◄─┼──────────┼─►│  • manifest server       │  │
│  │  • file transfer server  │  │          │  │  • file transfer server  │  │
│  └───────────┬───────────────┘  │          │  └───────────┬───────────────┘  │
│              │ serves            │          │              │ serves            │
│              ▼                   │          │              ▼                   │
│  ┌─────────────────────────┐  │          │  ┌─────────────────────────┐  │
│  │ index.html + style.css   │  │          │  │ index.html + style.css   │  │
│  │ ai.js                     │  │          │  │ ai.js                     │  │
│  │                           │  │          │  │                           │  │
│  │ • loads Transformers.js  │  │          │  │ • loads Transformers.js  │  │
│  │ • generates embeddings   │  │          │  │ • generates embeddings   │  │
│  │ • cosine similarity      │  │          │  │ • cosine similarity      │  │
│  │ • search UI               │  │          │  │ • search UI               │  │
│  └─────────────────────────┘  │          │  └─────────────────────────┘  │
└─────────────────────────────┘          └─────────────────────────────┘
```

The browser never talks to another device directly — it only calls its own `backend.py`, which does the actual LAN networking (discovery, manifests, file transfer) on its behalf.

---

## 2. On-device AI model pipeline

```
File in "shared files/"
        │
        ▼
 ┌───────────────────────────┐
 │  Text extraction (backend.py)│   .txt / .md read directly,
 │                             │   .pdf via PyPDF2
 └─────────────┬───────────────┘
               │ extracted text
               ▼
 ┌───────────────────────────────┐
 │  Manifest                       │   {filename, size, text}
 │  {filename, size, text}         │   exchanged over TCP (LAN only)
 └─────────────┬─────────────────┘
               ▼
 ┌───────────────────────────────┐
 │  ai.js (browser)                 │
 │  Transformers.js                 │
 │  model: Xenova/all-MiniLM-L6-v2   │   Runs fully client-side
 │  → generate embedding             │
 └─────────────┬─────────────────┘
               ▼
 ┌───────────────────────────────┐
 │  Query embedding + cosine         │
 │  similarity against known          │
 │  document embeddings               │
 └───────────────────────────────┘
```

**Model choice:** `Xenova/all-MiniLM-L6-v2` is a small sentence-embedding model that runs well in-browser via Transformers.js, giving a reasonable balance of semantic search quality against size/speed for a laptop-class on-device model. No external AI API is called at any point.

**Current status:** manifest retrieval and embedding generation are implemented; full cross-peer semantic indexing (searching ranked results across all discovered peers at once) is still in progress.

---

## 3. Data flow (end-to-end)

1. **Startup:** `backend.py` starts on each device, begins broadcasting its presence over UDP and listening for others.
2. **Discovery:** Devices on the same LAN populate each other's peer lists automatically; peers that go quiet are removed after a timeout.
3. **Manifest generation:** Each device scans its `shared files/` folder, extracts text from supported formats, and builds a manifest of `{filename, size, text}`.
4. **Manifest exchange:** Peers request each other's manifests over TCP, without needing to download the actual files first.
5. **Embedding:** The frontend (`ai.js`) loads the embedding model and generates vector embeddings for document text, entirely in-browser.
6. **Search:** A typed query is embedded the same way and compared to known document embeddings using cosine similarity to produce ranked results.
7. **File transfer:** Requesting a specific file opens a direct TCP connection to the owning peer, which streams the file back.

---

## 4. Local vs. cloud components

| Component | Where it runs |
|---|---|
| Peer discovery (UDP) | Local — LAN only |
| Manifest exchange & file transfer (TCP) | Local — LAN only |
| Text extraction (`.txt`, `.md`, `.pdf`) | Local — `backend.py` |
| Embedding generation | Local — in-browser via Transformers.js |
| Similarity search / ranking | Local — in-browser |
| AI model weights | Cached locally after first load; one-time download from a CDN |
| Hosting the UI | Local — served by each device's own `backend.py` |

The only point of contact with the internet is the one-time model download on first use of a given browser profile. No file content or search query is ever sent to an external server — this is what satisfies the hackathon's on-device AI requirement.

---

## 5. Key design decisions

**UDP for discovery, TCP for transfer.**
Discovery has to reach devices whose existence isn't known yet, and only UDP broadcast can do that; occasional lost broadcasts don't matter since presence is re-announced continuously. Manifest and file transfer need guaranteed, ordered delivery, so TCP is used once two peers already know about each other.

**A local backend as a bridge, rather than the browser handling networking itself.**
Browsers can't open raw sockets. `backend.py` exposes what the frontend needs and handles all LAN communication itself, keeping socket logic in one place and the frontend free to focus purely on UI and on-device inference.

**Embeddings are generated in the browser, not in `backend.py`.**
This keeps the AI genuinely on-device and keeps the Python backend dependency-light. Peers exchange raw extracted text rather than embeddings, so each device computes its own vectors locally and isn't dependent on another device's model version.

**Manifests carry text, not files, on first exchange.**
Peers can see what's available and search it by content before committing to a full file download — useful on constrained networks and avoids unnecessary transfers.

---

## 6. Known constraints

- Works only within a single broadcast domain; networks with client isolation (some public/guest Wi-Fi) will block peer discovery.
- Supported text-extractable formats are currently `.txt`, `.md`, and `.pdf` (PyPDF2 required for PDFs).
- The AI model requires internet access once, to download from a CDN; all inference afterward is fully offline.
- No authentication or encryption yet — any device on the same LAN can see and request shared files.
- Cross-peer semantic search ranking is still being finalized (see Features → AI-Powered Semantic Search in the README).
