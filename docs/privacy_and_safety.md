# Privacy and Safety — LANShare

## Data handling

- Files are only shared from the specific folder the user places them in (`shared files/`) — nothing outside that folder is ever scanned, read, or exposed.
- File content and extracted text are transmitted only between devices on the same local network, directly peer-to-peer, never through any third-party server.
- Search queries are processed entirely in-browser and are never transmitted to any peer or external service.

## Permissions

- The application requires network access on the local machine (to open sockets for discovery and file transfer) — no elevated system permissions are required.
- No camera, microphone, location, or contacts access is requested or used.
- The browser may request permission to download the AI model from a CDN on first use, which is a standard resource fetch, not a data-collection permission.

## Storage

- Shared files remain on each user's own device in the `shared files/` folder; downloaded files from peers are saved locally by the user.
- No database, cloud storage, or persistent server-side storage is used — there is no central server at all.
- The AI model is cached by the browser after first download, using standard browser caching (no custom persistent storage of user data).

## Limitations

- There is currently no authentication — any device on the same local network can discover peers and request files. This is acceptable for a trusted hackathon/demo environment but would need access control before any real-world deployment.
- There is no encryption on the peer-to-peer file transfer — file contents are sent in plaintext over the local network.
- Text extraction only supports a limited set of file types (`.txt`, `.md`, `.pdf`); other file types can still be shared and downloaded but aren't searchable by content.

## Potential risks

- On an untrusted or shared network (e.g., public Wi-Fi without client isolation), other devices on that network could discover peers and request shared files, since there's no authentication layer yet.
- Users should only run LANShare on networks they trust (home, hostel, or a controlled hackathon/demo network), and should be mindful of what they place in the shared folder.
- These risks are explicitly scoped as "future work" beyond the current hackathon build, not oversights — the priority was demonstrating on-device AI search over a working LAN discovery/transfer layer.
