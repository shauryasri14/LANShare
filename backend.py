import socket
import json
import time

broad_port=50000
tcp_port=50001
socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
# print(socket.gethostbyname(socket.gethostname()))
my_name=socket.gethostname()
# my_ip=socket.gethostbyname(socket.gethostname())
# print(my_name)
# print(my_ip)
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

