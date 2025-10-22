import socket
import threading
import json
from client.utils.constants import SERVER_IP, SERVER_PORT

class ClientSocket:
    def __init__(self, server_ip=SERVER_IP, server_port=SERVER_PORT):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = None
        self.callbacks = {}   # action -> function
        self.running = False
        self.lock = threading.Lock()  # send thread-safe

    def connect(self, on_error=None):
        """Sunucuya bağlan, GUI'i engellemeden thread içinde çağrılmalı"""
        def _connect():
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.server_ip, self.server_port))
                self.running = True
                listener = threading.Thread(target=self.listen, daemon=True)
                listener.start()
            except Exception as e:
                if on_error:
                    on_error(e)
                else:
                    print("Connection error:", e)

        threading.Thread(target=_connect, daemon=True).start()

    def listen(self):
        while self.running:
            try:
                data = self.sock.recv(65536)
                if not data:
                    break
                try:
                    msg = json.loads(data.decode('utf-8'))
                except Exception:
                    continue
                action = msg.get("action")
                payload = msg.get("payload")
                if action and action in self.callbacks:
                    # callback'i GUI thread'de çağırmak için
                    try:
                        self.callbacks[action](payload)
                    except Exception as e:
                        print("Callback error:", e)
            except Exception:
                break
        self.running = False

    def on(self, action, func):
        """Server'dan gelen mesaj için callback kaydet"""
        self.callbacks[action] = func

    def send(self, action, payload):
        """Server'a JSON mesaj gönder (thread-safe)"""
        msg = json.dumps({"action": action, "payload": payload})
        try:
            with self.lock:
                if self.sock:
                    self.sock.send(msg.encode("utf-8"))
        except Exception as e:
            print("Send error:", e)

    def close(self):
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
