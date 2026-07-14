import os.path
import socket
import json
import time
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
broad_port=50000
tcp_port=50001
HTTP_PORT = 8000
peers={}
peer_lock=threading.Lock()
socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
SHARED_DIR=os.path.join(os.path.dirname(__file__),"shared files")

my_name=socket.gethostname()

def getmyip():
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
      s.connect(("1.1.1.1",1))
      ip=s.getsockname()[0]
    except Exception as e:
        ip="127.0.0.1"
    finally:
        s.close()
    return ip

my_ip=getmyip()

def broadcast():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    while True:

        msg={
            "type":"hello",
            "name": my_name,
            "ip": my_ip,
            "tcp_port":tcp_port
        }
        try:
            sock.sendto(json.dumps(msg).encode(), ("<broadcast>",broad_port))
        except OSError as e:
            print(f"OS Error {e}")
        time.sleep(3)

def listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", broad_port))
    while True:
        data,addr=sock.recvfrom(2048)
        try:
            msg=json.loads(data.decode())
        except json.JSONDecodeError:
            continue

        if msg.get("type")!="hello":
            continue
        if msg.get("ip") == my_ip:
            continue
        with peer_lock:
            peers[msg["ip"]]={
                "name": msg.get("name", "Unknown"),
                "tcp_port": msg.get("tcp_port", tcp_port),
                "last_seen": time.time(),
            }

def cleanup():
    while True:
        time.sleep(5)
        cutoff=time.time()-15
        with peer_lock:
            stale = []
            for ip, info in peers.items():
                if info["last_seen"] < cutoff:
                    stale.append(ip)
            for ip in stale:
                del peers[ip]

def getpeersnapshot():
    with peer_lock:
        new_dictionary = {}
        for ip, info in peers.items():
            new_dictionary[ip] = dict(info)
    return new_dictionary

def extract_text(filepath):
    ext=os.path.splitext((filepath))[1].lower()
    try:
        if ext==".txt" or ext == ".md":
            with open(filepath,"r",errors= "ignore") as f:
                return f.read()[:5000]

        if ext==".pdf":
            try:
                import PyPDF2
                text=""
                with open(filepath,"rb") as f:
                    reader=PyPDF2.Pdfreader(f)
                    for page in reader.pages[:5]:
                        text+=page.extract_text() or ""
                    return text[:5000]
            except ImportError:
                return ""
    except Exception as e:
        print(f"extract text failed for {filepath}:{e}")
    return ""

def build_my_manifest():
    file_list = []
    for filename in os.listdir(SHARED_DIR):
        full_path = os.path.join(SHARED_DIR, filename)
        if not os.path.isfile(full_path):
            continue
        file_list.append({
            "filename": filename,
            "size": os.path.getsize(full_path),
            "text": extract_text(full_path),
        })
    return file_list

def handle_tcp_client(conn, addr):
    try:
        request = conn.recv(4096).decode(errors="ignore").strip()
        if request == "MANIFEST":
            manifest = build_my_manifest()
            payload = json.dumps(manifest).encode()
            conn.sendall(len(payload).to_bytes(8, "big"))
            conn.sendall(payload)
        elif request.startswith("GET "):
            filename = request[4:].strip()
            filepath = os.path.join(SHARED_DIR, filename)
            if not os.path.abspath(filepath).startswith(os.path.abspath(SHARED_DIR)):
                conn.sendall((0).to_bytes(8, "big"))
                return
            if not os.path.isfile(filepath):
                conn.sendall((0).to_bytes(8, "big"))
                return
            filesize = os.path.getsize(filepath)
            conn.sendall(filesize.to_bytes(8, "big"))
            with open(filepath, "rb") as f:
                conn.sendfile(f)
        else:
            conn.sendall((0).to_bytes(8, "big"))
    except Exception as e:
        print(f"[tcp] error handling {addr}: {e}")
    finally:
        conn.close()

def tcp_server_loop():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", tcp_port))
    server.listen(5)
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True).start()

def request_manifest_from_peer(ip, tcp_port1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((ip, tcp_port1))
        sock.sendall(b"MANIFEST")
        size_bytes = sock.recv(8)
        size = int.from_bytes(size_bytes, "big")
        data = b""
        while len(data) < size:
            chunk = sock.recv(min(4096, size - len(data)))
            if not chunk:
                break
            data += chunk
        return json.loads(data.decode())
    finally:
        sock.close()

def request_file_from_peer(ip, tcp_port2, filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    try:
        sock.connect((ip, tcp_port2))
        sock.sendall(f"GET {filename}".encode())
        size_bytes = sock.recv(8)
        size = int.from_bytes(size_bytes, "big")
        data = b""
        while len(data) < size:
            chunk = sock.recv(min(65536, size - len(data)))
            if not chunk:
                break
            data += chunk
        return data
    finally:
        sock.close()
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

class apihandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        if path == "/api/peers":
            snapshot = getpeersnapshot()
            snapshot["_self"] = {"name": my_name, "ip": my_ip}
            self._send_json(snapshot)
            return

        if path == "/api/manifest":
            peer = params.get("peer", ["local"])[0]
            if peer == "local":
                self._send_json(build_my_manifest())
                return
            snapshot = getpeersnapshot()
            info = snapshot.get(peer)
            if not info:
                self._send_json({"error": "unknown peer"}, status=404)
                return
            try:
                manifest = request_manifest_from_peer(peer, info["tcp_port"])
                self._send_json(manifest)
            except Exception as e:
                self._send_json({"error": str(e)}, status=502)
            return

        if path == "/api/download":
            peer = params.get("peer", ["local"])[0]
            filename = params.get("file", [""])[0]
            if not filename:
                self.send_response(400)
                self.end_headers()
                return

            if peer == "local":
                filepath = os.path.join(SHARED_DIR, filename)
                if not os.path.isfile(filepath):
                    self.send_response(404)
                    self.end_headers()
                    return
                with open(filepath, "rb") as f:
                    data = f.read()
            else:
                snapshot = getpeersnapshot()
                info = snapshot.get(peer)
                if not info:
                    self.send_response(404)
                    self.end_headers()
                    return
                data = request_file_from_peer(peer, info["tcp_port"], filename)

            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        self._serve_static(path)

    def _serve_static(self, path):
        if path == "/":
            path = "/index.html"
        filepath = os.path.join(STATIC_DIR, path.lstrip("/"))
        if not os.path.abspath(filepath).startswith(os.path.abspath(STATIC_DIR)):
            self.send_response(403)
            self.end_headers()
            return
        if not os.path.isfile(filepath):
            self.send_response(404)
            self.end_headers()
            return
        mime, _ = mimetypes.guess_type(filepath)
        with open(filepath, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    print(f"== LAN P2P Resource Sharing ==")
    print(f"My name: {my_name}")
    print(f"My IP:   {my_ip}")
    print(f"Sharing folder: {SHARED_DIR}")
    print(f"Open http://localhost:{HTTP_PORT} in your browser\n")

    threading.Thread(target=broadcast, daemon=True).start()
    threading.Thread(target=listener, daemon=True).start()
    threading.Thread(target=cleanup, daemon=True).start()
    threading.Thread(target=tcp_server_loop, daemon=True).start()

    httpd = ThreadingHTTPServer(("0.0.0.0", HTTP_PORT), apihandler)
    httpd.serve_forever()
if __name__=="__main__":
    main()
