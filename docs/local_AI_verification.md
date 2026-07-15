# Local AI Verification — LANShare

## What runs fully on-device

- **Text extraction** from shared files (`.txt`, `.md`, `.pdf`) — runs in `backend.py`, entirely on the local device, no network call involved.
- **Embedding generation** — runs in the browser via Transformers.js, using the `Xenova/all-MiniLM-L6-v2` model. This is the "AI" step: turning file text and search queries into vectors that capture meaning.
- **Semantic search / ranking** — cosine similarity between embeddings is computed entirely client-side in JavaScript, in-memory.
- **Peer discovery and file transfer** — plain UDP/TCP sockets between devices on the same local network. No internet involved at any point.

## What requires internet access

- **One-time model download.** The first time the app runs in a given browser profile, Transformers.js downloads the `all-MiniLM-L6-v2` model weights from a CDN (jsDelivr, hosting Xenova's models). After this first download, the browser caches the model, and every subsequent run works fully offline.
- No other part of the application requires internet access.

## Whether any user data leaves the device

**No.** Specifically:
- File contents and extracted text are only ever sent between peers over the local network (never to an external server).
- Search queries are embedded locally and never transmitted anywhere, including to peers — only the resulting search *results* (which reference peer files) involve any network activity, and that's peer-to-peer over LAN, not to any third party.
- The only outbound internet traffic in the entire application is the one-time, anonymous model file download — no personal data, file content, or query text is part of that request.

## Summary

| Data type | Where it goes |
|---|---|
| File content / extracted text | Stays on LAN, exchanged only between peers directly |
| Search queries | Never leaves the device |
| Embeddings | Computed and stored locally in-browser only |
| Model weights | Downloaded once from a CDN (no user data included in this request) |
