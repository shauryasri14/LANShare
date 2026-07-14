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
        " Local AI model ready — search runs fully on this device.";
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

async function buildIndex() {
    const peers = await fetchPeers();

    const selfInfo = peers._self;
    delete peers._self;

    const peerIds = ["local", ...Object.keys(peers)];

    const peerNames = {
        local: `${selfInfo.name} (this laptop)`
    };

    for (const [ip, info] of Object.entries(peers)) {
        peerNames[ip] = info.name;
    }
    peerStatusEl.textContent =
    Object.keys(peers).length === 0
        ? "No other peers found yet on the LAN — still listening..."
        : `Connected peers: ${Object.values(peers)
              .map((p) => p.name)
              .join(", ")}`;

const newIndex = [];

for (const peerId of peerIds) {
    const manifest = await fetchManifest(peerId);

    for (const file of manifest) {
        const existing = searchIndex.find(
            (item) =>
                item.filename === file.filename &&
                item.peerIp === peerId
        );

        if (existing) {
            newIndex.push(existing);
            continue;
        }
        const embedding = await embedText(file.text || file.filename);

    newIndex.push({
    filename: file.filename,
    size: file.size,
    peerIp: peerId,
    peerName: peerNames[peerId] || peerId,
    text: file.text || "",
    embedding,
});
    }
}
searchIndex = newIndex;
}
async function runSearch(query) {
    if (!query.trim()) {
        resultsEl.innerHTML = "";
        return;
    }

    const queryEmbedding = await embedText(query);

    if (!queryEmbedding) return;

    const scored = searchIndex
        .filter((item) => item.embedding)
        .map((item) => ({
            ...item,
            score: cosineSimilarity(queryEmbedding, item.embedding),
        }))
        .sort((a, b) => b.score - a.score)
        .slice(0, 15);

    renderResults(scored);
}

async function init() {
    await loadModel();
}

init();