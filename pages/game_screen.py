import os
import random
import math
import tkinter as tk
from tkinter import messagebox

from database.db_manager import DatabaseManager

try:
    import webview
except ImportError:
    webview = None


COORDS = [
    (41.0082, 28.9784),   # Istanbul
    (48.8584, 2.2945),    # Eiffel Tower
    (40.6892, -74.0445),  # Statue of Liberty
    (51.5007, -0.1246),   # London
    (35.6586, 139.7454),  # Tokyo Tower
]


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p = math.pi / 180.0
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


class GameApi:
    """
    3 rounds:
      - game_sessions: 1 session
      - game_rounds: 3 rows
    """
    def __init__(self, db: DatabaseManager, user_id: int):
        self.db = db
        self.user_id = user_id

        self.session_id = self.db.start_session(user_id)

        self.rounds_total = 3
        self.round_index = 1
        self.total_score = 0

        self.target = random.choice(COORDS)
        self.window = None

    def set_window(self, window):
        self.window = window

    def close_window(self):
        if self.window is not None:
            self.window.destroy()

    def get_state(self):
        return {
            "round": self.round_index,
            "rounds_total": self.rounds_total,
            "total_score": self.total_score,
            "target": {"lat": self.target[0], "lng": self.target[1]},
        }

    def submit_guess(self, lat, lng):
        lat = float(lat)
        lng = float(lng)

        dist_km = haversine_km(self.target[0], self.target[1], lat, lng)
        score = max(0, int(5000 - dist_km * 50))
        self.total_score += score

        # Save the round
        self.db.add_round(
            session_id=self.session_id,
            target_lat=float(self.target[0]),
            target_lng=float(self.target[1]),
            guess_lat=lat,
            guess_lng=lng,
            distance_km=float(dist_km),
            score=int(score),
        )

        finished = (self.round_index >= self.rounds_total)

        if finished:
            self.db.end_session(self.session_id)
            return {
                "finished": True,
                "round": self.round_index,
                "rounds_total": self.rounds_total,
                "distance_km": float(dist_km),
                "score": int(score),
                "total_score": int(self.total_score),
            }

        # Next round
        self.round_index += 1
        self.target = random.choice(COORDS)

        return {
            "finished": False,
            "round": self.round_index,
            "rounds_total": self.rounds_total,
            "distance_km": float(dist_km),
            "score": int(score),
            "total_score": int(self.total_score),
            "next_target": {"lat": self.target[0], "lng": self.target[1]},
        }


def open_game_window(user_id: int):
    if webview is None:
        messagebox.showerror(
            "Missing package",
            "pywebview is not installed.\n\nRun:\n\npip install pywebview"
        )
        return

    db = DatabaseManager()
    api = GameApi(db, user_id)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    html_path = os.path.join(base_dir, "web", "game.html")

    if not os.path.exists(html_path):
        messagebox.showerror("File not found", f"Not found:\n{html_path}")
        return

    window = webview.create_window(
        "Guessr Game",
        html_path,
        js_api=api,
        width=1200,
        height=800
    )
    api.set_window(window)

    # More stable than file:// for Google Maps
    webview.start(debug=False, http_server=True)


class GameScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#4B0082")
        self.controller = controller

        title = tk.Label(
            self,
            text="Game Screen",
            font=("Impact", 36, "bold"),
            bg="#9370DB",
            fg="white",
            bd=0,
            relief=tk.FLAT,
            padx=20,
            pady=10,
        )
        title.pack(pady=30)

        info = tk.Label(
            self,
            text="Play 3 rounds: after each guess a new location loads.\nAfter round 3, your total score is shown.",
            font=("Impact", 14),
            bg="#4B0082",
            fg="white",
        )
        info.pack(pady=10)

        btn_style = {
            "font": ("Impact", 18),
            "bg": "#9370DB",
            "fg": "white",
            "activebackground": "#B57EDC",
            "activeforeground": "white",
            "padx": 20,
            "pady": 10,
            "bd": 0,
            "width": 18,
        }

        tk.Button(self, text="Start Game (3 Rounds)", command=self.start_game, **btn_style).pack(pady=10)
        tk.Button(self, text="Back to Lobby", command=lambda: controller.show_frame("LobbyScreen"), **btn_style).pack(pady=10)

    def start_game(self):
        user = getattr(self.controller, "current_user", None)
        if not user:
            messagebox.showerror("Not logged in", "Please log in first.")
            self.controller.show_frame("LoginPage")
            return
        open_game_window(user["id"])

    def on_show(self):
        pass
