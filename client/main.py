# client/main.py
import tkinter as tk
from client.ui.login_screen import LoginScreen
from client.ui.lobby_screen import LobbyScreen
from client.ui.waiting_room import WaitingRoom
from client.ui.game_screen import GameScreen
from client.network.client_socket import ClientSocket
from client.db.user_database import UserDatabase
from client.utils.constants import WINDOW_SIZE, DB_PATH, SERVER_IP, SERVER_PORT

class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry(WINDOW_SIZE)
        self.root.title("GeoExplorer - Multiplayer GeoGuessr")
        self.client = ClientSocket(SERVER_IP, SERVER_PORT)
        self.client.connect()
        # register generic callbacks for UI to update
        self.client.on("room_update", self._on_room_update)
        self.client.on("create_room_ok", lambda p: None)
        self.client.on("join_room_ok", lambda p: None)
        # hold references
        self.frames = {}
        self.username = None
        self.current_room = None

        # start with login
        self.show_login()

    def clear_frame(self):
        for child in self.root.winfo_children():
            child.destroy()

    def show_login(self):
        self.clear_frame()
        login = LoginScreen(self.root, navigate=self._navigate)
        self.frames["login"] = login

    def show_lobby(self, username):
        self.clear_frame()
        self.username = username
        lobby = LobbyScreen(self.root, username, self.client, navigate=self._navigate)
        self.frames["lobby"] = lobby

    def show_waiting(self, username, room_id=None):
        self.clear_frame()
        self.username = username
        self.current_room = room_id
        waiting = WaitingRoom(self.root, username, self.client, navigate=self._navigate)
        self.frames["waiting"] = waiting

    def show_game(self, username, room_id):
        self.clear_frame()
        self.username = username
        self.current_room = room_id
        game = GameScreen(self.root, username, self.client, room_id, navigate=self._navigate)
        self.frames["game"] = game

    def _navigate(self, where, **kwargs):
        # central navigation method used by screens
        if where == "login":
            self.show_login()
        elif where == "lobby":
            username = kwargs.get("username", self.username)
            self.show_lobby(username)
        elif where == "waiting":
            username = kwargs.get("username", self.username)
            room_id = kwargs.get("room_id", None)
            self.show_waiting(username, room_id)
        elif where == "game":
            username = kwargs.get("username", self.username)
            room_id = kwargs.get("room_id", self.current_room)
            self.show_game(username, room_id)
        else:
            pass

    # server -> update room players
    def _on_room_update(self, payload):
        players = payload.get("players", [])
        # if waiting frame active, update its list
        frame = self.frames.get("waiting")
        if frame:
            frame.update_players([p["username"] for p in players])
        # if enough players and in waiting frame, enable start (handled in UI via Start Game button)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
