# server/server.py
import socket
import threading
import json
from game_manager import GameManager

HOST = "0.0.0.0"
PORT = 5555
BUFFER = 65536  # bytes

class Server:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.game = GameManager()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(50)
        print(f"[SERVER] Listening on {self.host}:{self.port}")
        self.clients = {}  # conn -> (addr, username, current_room)

    def start(self):
        try:
            while True:
                conn, addr = self.server.accept()
                print(f"[CONNECT] {addr}")
                t = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                t.start()
        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            self.server.close()

    def send(self, conn, obj):
        try:
            conn.send(json.dumps(obj).encode('utf-8'))
        except Exception:
            pass

    def handle_client(self, conn, addr):
        # initial state
        self.clients[conn] = {"addr": addr, "username": None, "room": None}
        try:
            while True:
                data = conn.recv(BUFFER)
                if not data:
                    break
                try:
                    msg = json.loads(data.decode('utf-8'))
                except Exception:
                    # ignore bad messages
                    continue
                action = msg.get("action")
                payload = msg.get("payload", {})

                # handle actions
                if action == "create_room":
                    room_id = payload.get("room_id")
                    username = payload.get("username")
                    self.clients[conn]["username"] = username
                    self.clients[conn]["room"] = room_id
                    self.game.create_room(room_id, username, conn)

                elif action == "join_room":
                    room_id = payload.get("room_id")
                    username = payload.get("username")
                    self.clients[conn]["username"] = username
                    self.clients[conn]["room"] = room_id
                    self.game.join_room(room_id, username, conn)

                elif action == "leave_room":
                    room_id = payload.get("room_id")
                    self.game.leave_room(room_id, conn)
                    self.clients[conn]["room"] = None

                elif action == "start_game":
                    room_id = payload.get("room_id")
                    self.game.start_game(room_id)

                elif action == "submit_guess":
                    room_id = payload.get("room_id")
                    lat = payload.get("lat")
                    lon = payload.get("lon")
                    self.game.submit_guess(room_id, conn, lat, lon)

                else:
                    # unknown action, ignore
                    pass

        except ConnectionResetError:
            pass
        finally:
            # cleanup
            client = self.clients.get(conn)
            if client and client["room"]:
                try:
                    self.game.leave_room(client["room"], conn)
                except Exception:
                    pass
            if conn in self.clients:
                del self.clients[conn]
            try:
                conn.close()
            except:
                pass
            print(f"[DISCONNECT] {addr}")

if __name__ == "__main__":
    server = Server()
    server.start()
