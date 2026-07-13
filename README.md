# LANShare – Offline AI-Powered LAN File Sharing

Campus and hostel networks are often slow or unreliable, but everyone on the same Wi-Fi can already talk to each other directly. Finding a specific file someone else has shared today usually means asking around in a group chat and hoping someone remembers what they have.
LANShare lets every device on the same local network automatically discover each other, share files with no internet required, and search across everyone's files by meaning, not just filename - e.g. searching "diagrams about database relationships" instead of guessing an exact filename

---

# Features

## Peer Discovery
- Automatic peer discovery using UDP broadcasts.
- Maintains a live list of available devices on the local network.
- Automatically removes inactive peers after a timeout.

## TCP File Sharing
- TCP server for peer-to-peer communication.
- Supports:
  - Manifest requests
  - File download requests
- Securely serves files from the shared directory.

## File Manifest
Each peer generates a manifest containing:
- Filename
- File size
- Extracted text content

This allows other peers to search available files without downloading them first.

## Text Extraction
Currently supported file formats:
- `.txt`
- `.md`
- `.pdf`

Extracted text is included in the manifest for semantic search.

## AI-Powered Semantic Search *(Work in Progress)*
The frontend uses **Transformers.js** with the **Xenova/all-MiniLM-L6-v2** embedding model.

Current implementation:
- Loads the embedding model locally.
- Generates embeddings for text.
- Uses cosine similarity to compare search queries with document embeddings.
- Retrieves manifests from peers for future semantic indexing.

No external AI APIs are used.

---

# Project Structure

```text
.
├── backend.py              # UDP discovery, TCP server, manifest and file transfer
├── shared files/           # Files shared over the LAN
├── index.html              # Frontend interface
├── style.css               # Frontend styling
├── ai.js               # AI semantic search logic
└── README.md
```

---

# Technologies Used

## Backend
- Python
- Socket Programming
- Threading
- JSON
- PyPDF2

## Frontend
- HTML
- CSS
- JavaScript (ES Modules)

## AI
- Transformers.js
- Xenova/all-MiniLM-L6-v2
- Cosine Similarity

---

# How It Works

1. Every peer broadcasts its presence using UDP.
2. Other peers discover the device and maintain an active peer list.
3. Each peer generates a manifest of its shared files.
4. Peers request manifests over TCP.
5. Files are transferred directly using TCP.
6. The frontend loads a local embedding model.
7. Semantic embeddings are generated locally for AI-powered search.

---



---

# Team

Developed as part of a hackathon project.
