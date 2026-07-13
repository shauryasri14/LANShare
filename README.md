# LANShare – Offline AI-Powered LAN File Sharing

LANShare is a local network file-sharing application that allows devices on the same LAN to automatically discover one another, exchange file metadata, and perform AI-powered semantic search without relying on the internet or cloud services.

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
├── script.js               # AI semantic search logic
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
