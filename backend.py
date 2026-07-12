import os.path
import socket
import json
import time
import threading

broad_port=50000
tcp_port=50001
peers={}
peer_lock=threading.Lock()
socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

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
print(my_name)
print(my_ip)
def broadcast():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    while True:

        msg={
            "type":"hello",
            "name": my_name,
            "ip address": my_ip,
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

def extract_test(filepath):
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





