import { pipeline } from "https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.1";

let embedder = null;
let searchIndex = [];

const modelStatusEl = document.getElementById("model-status");
const peerStatusEl = document.getElementById("peer-status");
const resultsEl = document.getElementById("results");
const searchInput = document.getElementById("search-input");
const searchButton = document.getElementById("search-button");

async function loadModel() {
    modelStatusEl.textContent = "Loading local AI model...";

    embedder = await pipeline(
        "feature-extraction",
        "Xenova/all-MiniLM-L6-v2"
    );

    modelStatusEl.textContent =
        "✅ Local AI model ready — search runs fully on this device.";
}
async function embedText(text) {
    if (!text || !text.trim()) {
        return null;
    }

    const output = await embedder(text, {
        pooling: "mean",
        normalize: true,
    });

    return Array.from(output.data);
}
function cosineSimilarity(a, b) {
    let dot = 0;

    for (let i = 0; i < a.length; i++) {
        dot += a[i] * b[i];
    }

    return dot;
}
async function fetchPeers() {
    const res = await fetch("/api/peers");
    return res.json();
}

async function fetchManifest(peerIp) {
    const res = await fetch(`/api/manifest?peer=${encodeURIComponent(peerIp)}`);

    if (!res.ok) {
        return [];
    }

    return res.json();
}
async function init() {
    await loadModel();
}

init();