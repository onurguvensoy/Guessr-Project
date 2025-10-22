# client/ui/lobby_screen.py

import tkinter as tk
from tkinter import messagebox, simpledialog

class LobbyScreen:
    def __init__(self, root, username, client_socket, navigate):
        self.root = root
        self.username = username
        self.client = client_socket
        self.navigate = navigate
        self.frame = tk.Frame(self.root)
        self.build_ui()

    def build_ui(self):
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text=f"Welcome, {self.username}", font=("Arial", 20)).pack(pady=10)
        tk.Button(self.frame, text="Create Room", command=self.create_room).pack(pady=5)
        tk.Button(self.frame, text="Join Room", command=self.join_room).pack(pady=5)
        tk.Button(self.frame, text="Logout", command=lambda: self.navigate("login")).pack(pady=10)

    def create_room(self):
        self.client.send("create_room", {"username": self.username})
        self.navigate("waiting", username=self.username)

    def join_room(self):
        room_id = simpledialog.askstring("Join Room", "Enter Room ID:")
        if room_id:
            self.client.send("join_room", {"username": self.username, "room_id": room_id})
            self.navigate("waiting", username=self.username)
