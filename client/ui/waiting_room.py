# client/ui/waiting_room.py

import tkinter as tk

class WaitingRoom:
    def __init__(self, root, username, client_socket, navigate):
        self.root = root
        self.username = username
        self.client = client_socket
        self.navigate = navigate
        self.frame = tk.Frame(self.root)
        self.players = []
        self.build_ui()

    def build_ui(self):
        self.frame.pack(fill="both", expand=True)
        tk.Label(self.frame, text="Waiting Room", font=("Arial", 22)).pack(pady=10)
        self.player_list = tk.Listbox(self.frame)
        self.player_list.pack(pady=10)

        tk.Button(self.frame, text="Start Game", command=self.start_game).pack(pady=10)
        tk.Button(self.frame, text="Back to Lobby", command=lambda: self.navigate("lobby", username=self.username)).pack(pady=5)

    def update_players(self, players):
        self.player_list.delete(0, tk.END)
        for p in players:
            self.player_list.insert(tk.END, p)

    def start_game(self):
        self.client.send("start_game", {"username": self.username})
