# 🌐 LANShare

**Offline AI-powered LAN file sharing — devices on the same network discover each other, share files with no internet required, and search across everyone's files by meaning, not just filename.**

[![Repo](https://img.shields.io/badge/GitHub-LANShare-181717?logo=github)](https://github.com/shauryasri14/LANShare)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/shauryasri14/LANShare/blob/main/LICENSE)

> Built for OSDHack 2026 · On-Device AI track

---

## 📖 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [On-Device AI Explanation](#-on-device-ai-explanation)
- [Tech Stack](#️-tech-stack)
- [Setup Instructions](#-setup-instructions)
- [Usage Instructions](#-usage-instructions)
- [Demo Video](#-demo-video)
- [Screenshots](#-screenshots)
- [Known Limitations & Future Scope](#-known-limitations--future-scope)
- [License](#-license)

---

## 🧩 Problem Statement

Campus and hostel networks are often slow or unreliable, but everyone on the same Wi-Fi can already talk to each other directly. Finding a specific file someone else has shared today usually means asking around in a group chat and hoping someone remembers what they have — there's no way to search across everyone's files by what they actually contain.

## 💡 Solution Overview

**LANShare** turns every device on a LAN into a node in a lightweight peer-to-peer network:

- Each node **broadcasts its presence** over UDP and **discovers peers** automatically — no manual IP entry, no central server.
- Each node exposes its shared folder over a simple **TCP protocol**, so any peer can request a file manifest or download a file directly, node-to-node.
- A **browser-based semantic search bar** lets anyone type what they're looking for in plain language (e.g. *"diagrams about database relationships"*) and instantly surface the most relevant files from **every connected peer** — ranked by meaning, not just filename matching.
- Everything runs **entirely on-device**: peer discovery, file transfer, and the AI search model all execute locally, with zero data leaving the LAN.

## 🧠 On-Device AI Explanation

LANShare's search is powered by a **local embedding model running entirely in the browser** — no API calls, no server-side inference, no internet dependency once the model is cached.

- **Model:** [`Xenova/all-MiniLM-L6-v2`](https://huggingface.co/Xenova/all-MiniLM-L6-v2), a compact sentence-embedding transformer converted to ONNX for in-browser use.
- **Runtime:** [`transformers.js`](https://github.com/xenova/transformers.js) loads and runs the model client-side via WebAssembly/WebGL, directly in the user's browser tab.
- **How it works:**
  1. When a peer's file manifest is fetched, each file's extracted text (or filename, as a fallback) is passed through the model to generate a 384-dimensional embedding vector.
  2. When the user types a search query, the query is embedded using the same model.
  3. **Cosine similarity** is computed between the query embedding and every indexed file's embedding, entirely in JavaScript.
  4. Results are ranked by similarity score and rendered instantly — all inference happens on the user's own machine.
- **Why this matters:** the model downloads once (cached by the browser afterward), and from then on search works even if the LAN has no path to the wider internet — the AI never needs to "phone home."

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Peer discovery | Python `socket` (UDP broadcast) |
| File transfer | Python `socket` (TCP) |
| Backend / API server | Python `http.server` (`ThreadingHTTPServer`) |
| Frontend | HTML, CSS, vanilla JavaScript (ES modules) |
| On-device AI | [`transformers.js`](https://github.com/xenova/transformers.js) + `Xenova/all-MiniLM-L6-v2` |
| Data format | JSON over TCP/HTTP |

**Project structure:**
```
LANShare/
├── backend.py         # UDP peer discovery, TCP file server, HTTP API + static file server
├── static/
│   ├── index.html      # UI shell
│   ├── style.css        # Styling
│   └── ai.js              # Model loading, embedding, search, rendering
├── shared files/       # Folder whose contents are shared with peers
├── LICENSE
└── README.md
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.8+
- A modern browser (Chrome, Edge, or Firefox) with WebAssembly support
- All devices connected to the **same LAN / Wi-Fi network**
- Internet access on first run only (to download the AI model from the CDN — it is cached afterward)

### Steps

1. **Clone the repository** on every machine that wants to share files:
   ```bash
   git clone https://github.com/shauryasri14/LANShare.git
   cd LANShare
   ```

2. **Create the shared folder** (if not already present) and add the files you want to share:
   ```bash
   mkdir "shared files"
   cp /path/to/your/files "shared files/"
   ```

3. **Run the backend:**
   ```bash
   python backend.py
   ```
   You should see console output confirming your hostname, LAN IP, and shared folder path.

4. **Open the app** in your browser:
   ```
   http://localhost:8000
   ```

5. **Allow the app through your firewall** if prompted — peer discovery uses UDP broadcast (port `50000`) and file transfer uses TCP (port `50001`).

Repeat steps 1–4 on every peer's machine. Peers discover each other automatically within a few seconds.

---

## 🚀 Usage Instructions

1. Launch LANShare on each device (see Setup above).
2. Open `http://localhost:8000` — the **peer status** bar at the top will update once other nodes are discovered on the LAN.
3. Wait for **"Local AI model ready"** to appear — this means the on-device model has loaded and search is ready.
4. Type a natural-language query into the search bar (e.g. *"budget spreadsheet for Q3"*) and press **Enter** or click **Search**.
5. Browse results ranked by semantic match score, showing which peer each file came from.
6. Click **Download** on any result to pull that file directly from its owning peer.

The peer list and search index refresh automatically every 10 seconds, so newly joined peers and newly shared files appear without a manual reload.

---

## 🎥 Demo Video

📺 *[https://youtu.be/Sz7Kio3CUm0?si=jTXUkJrP8EcEhhvS]*

---

## 🖼️ Screenshots


<img width="1600" height="1000" alt="WhatsApp Image 2026-07-15 at 17 41 40" src="https://github.com/user-attachments/assets/05d550ef-c90c-44d4-85e0-3ca12b4d105d" />
<img width="1600" height="899" alt="WhatsApp Image 2026-07-15 at 17 41 45" src="https://github.com/user-attachments/assets/3611fa7d-7eb0-44f7-88cf-ac4c15721f21" />


---

## 🔭 Known Limitations & Future Scope

**Current limitations:**
- Text extraction currently supports `.txt` and `.md` files natively; `.pdf` support depends on `PyPDF2` being installed and is best-effort.
- Peer discovery relies on UDP broadcast, which does not cross subnets or routers that block broadcast traffic.
- No authentication or access control — any device on the LAN that can reach the broadcast/TCP ports can see and download shared files.
- The AI model is downloaded from a public CDN on first launch, so a brief internet connection is required once per machine.

**Future scope:**
- Support richer file previews (images, code syntax highlighting, more document formats).
- Add optional access control / shared-secret pairing for private LAN sessions.
- Persist the search index to disk so re-indexing isn't needed on every restart.
- Explore mDNS/Bonjour-style discovery as a fallback for networks that block UDP broadcast.
- Add transfer resumption for large files and progress indicators in the UI.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](https://github.com/shauryasri14/LANShare/blob/main/LICENSE) file for details. You're free to use, modify, and distribute this project, including commercially, as long as the original copyright notice is retained.

---

<p align="center">Built for OSDHack 2026 — On-Device AI track</p>
<p align="center"><a href="https://github.com/shauryasri14/LANShare">github.com/shauryasri14/LANShare</a></p>
