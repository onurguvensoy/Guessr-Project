import os
import random
import math
import multiprocessing
import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from utils.translation import TRANSLATIONS

try:
    import webview  # pywebview
except ImportError:
    webview = None


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute great-circle distance between two points on Earth (in kilometers)
    using the Haversine formula.

    Args:
        lat1, lon1: First point in degrees.
        lat2, lon2: Second point in degrees.

    Returns:
        Distance in kilometers as a float.
    """
    R = 6371.0  # Earth's average radius in kilometers
    p = math.pi / 180.0
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = (
        (math.sin(dlat / 2) ** 2)
        + math.cos(lat1 * p) * math.cos(lat2 * p) * (math.sin(dlon / 2) ** 2)
    )
    return 2 * R * math.asin(math.sqrt(a))


class GameApi:
    """
    Bridge object exposed to JavaScript via pywebview.
    This class also persists session/round data through DatabaseManager.
    """
    def __init__(self, db: DatabaseManager, user_id: int, config: dict):
        self.db = db
        self.user_id = user_id
        self.config = config

        self.playlist_name = config.get("playlist", "World Spotlight")
        self.session_id = self.db.start_session(user_id, self.playlist_name)

        # Pull the coordinate pool based on the chosen playlist/map
        self.coords_pool = self.db.get_locations_for_playlist(self.playlist_name)

        self.rounds_total = int(config.get("rounds", 3))
        self.round_index = 1
        self.total_score = 0

        # Choose a random target for the first round
        self.target = random.choice(self.coords_pool)
        self.window = None

    def set_window(self, window) -> None:
        """Store a reference to the webview window so we can close it from Python."""
        self.window = window

    def close_window(self) -> None:
        """Close the webview window (called from JS at the end of the game, if needed)."""
        if self.window:
            self.window.destroy()

    def get_state(self) -> dict:
        """
        Return the full game state to the JS layer.
        """
        return {
            "round": self.round_index,
            "rounds_total": self.rounds_total,
            "total_score": self.total_score,
            "target": {"lat": self.target[0], "lng": self.target[1]},
            "no_move": self.config.get("no_move", False),
            "timer": self.config.get("timer", "No Limit"),
        }

    def submit_guess(self, lat, lng) -> dict:
        """
        Score a user's guess and advance the game.

        Scoring model (simple and presentation-friendly):
        - Start from 5000 points.
        - Subtract 2 points per kilometer.
        - Clamp to 0 (no negative scores).

        Returns a payload for JS:
        - distance_km, score, total_score
        - finished flag
        - next_target (if another round exists)
        """
        try:
            # Ensure numeric input (pywebview can deliver strings from JS)
            guess_lat = float(lat)
            guess_lng = float(lng)
            target_lat = float(self.target[0])
            target_lng = float(self.target[1])

            # Compute distance between target and guess
            dist_km = haversine_km(target_lat, target_lng, guess_lat, guess_lng)

            # Score from 5000 (distance penalty is linear here)
            score = max(0, int(5000 - (dist_km * 2)))
            self.total_score += score

            # Persist this round
            self.db.add_round(
                self.session_id,
                target_lat,
                target_lng,
                guess_lat,
                guess_lng,
                dist_km,
                score,
            )

            finished = self.round_index >= self.rounds_total

            result = {
                "finished": finished,
                "round": int(self.round_index),
                "rounds_total": int(self.rounds_total),
                "distance_km": float(dist_km),
                "score": int(score),
                "total_score": int(self.total_score),
            }

            if not finished:
                self.round_index += 1
                self.target = random.choice(self.coords_pool)
                result["next_target"] = {
                    "lat": float(self.target[0]),
                    "lng": float(self.target[1]),
                }
            else:
                self.db.end_session(self.session_id)

            return result

        except Exception as e:
            # Keep errors visible in terminal logs for debugging
            print(f"Scoring error: {e}")
            return {"error": str(e), "score": 0, "total_score": int(self.total_score)}


def launch_game_process(user_id: int, config: dict) -> None:
    if webview is None:
        raise RuntimeError(
            "pywebview is not installed. Install it with: pip install pywebview"
        )

    db = DatabaseManager()
    api = GameApi(db, user_id, config)

    # Resolve path: /project_root/web/game.html
    current_dir = os.path.dirname(os.path.abspath(__file__))  # pages folder
    project_root = os.path.dirname(current_dir)  # project root folder
    html_path = os.path.join(project_root, "web", "game.html")

    print(f"Loading HTML from: {html_path}")

    if not os.path.exists(html_path):
        print("ERROR: game.html not found. Please check your /web folder.")

    window = webview.create_window(
        title=f"Guessr - {config.get('playlist')}",
        url=html_path,
        js_api=api,
        width=1200,
        height=850,
    )
    api.set_window(window)

    # With http_server=True, pywebview serves local files through a small internal server.
    webview.start(http_server=True)


class GameScreen(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = DatabaseManager()

        self.grid_columnconfigure(0, weight=1)

        # --- UI HEADER ---
        self.title_label = ctk.CTkLabel(
            self,
            text="PREPARE FOR ADVENTURE",
            font=("Impact", 40, "bold"),
            fg_color=("#3B8ED0", "#1F6AA5"),
            text_color="white",
            corner_radius=12,
        )
        self.title_label.pack(pady=(40, 20), padx=20, fill="x")

        # --- SUMMARY CARD ---
        self.summary_card = ctk.CTkFrame(
            self,
            fg_color=("#EBF4FC", "#1A1A1A"),
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            corner_radius=15,
        )
        self.summary_card.pack(pady=20, padx=50, fill="x")

        self.info_label = ctk.CTkLabel(
            self.summary_card,
            text="Select a playlist in the lobby...",
            font=("Impact", 18),
            text_color=("#1F6AA5", "#3B8ED0"),
            wraplength=600,
        )
        self.info_label.pack(pady=30, padx=20)

        # --- ACTIONS ---
        self.start_btn = ctk.CTkButton(
            self,
            text="LAUNCH GAME",
            command=self.start_game_process,
            font=("Impact", 24),
            height=60,
            width=320,
            fg_color=("#3B8ED0", "#1F6AA5"),
        )
        self.start_btn.pack(pady=20)

        self.back_btn = ctk.CTkButton(
            self,
            text="BACK TO LOBBY",
            command=lambda: controller.show_frame("LobbyScreen"),
            font=("Impact", 16),
            fg_color="transparent",
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
        )
        self.back_btn.pack(pady=10)

    def on_show(self) -> None:

        config = getattr(
            self.controller,
            "game_config",
            {"playlist": "World Spotlight", "rounds": 3, "timer": "No Limit", "no_move": False},
        )

        mode_str = "No Move" if config.get("no_move") else "Classic (Movement On)"
        msg = (
            f"Playlist: {config['playlist']}\n"
            f"Mode: {mode_str}\n"
            f"Rounds: {config['rounds']}\n"
            f"Timer: {config['timer']}"
        )
        self.info_label.configure(text=msg)

    def start_game_process(self) -> None:

        user = getattr(self.controller, "current_user", None)
        config = getattr(self.controller, "game_config", {"playlist": "World Spotlight", "rounds": 3})

        if not user:
            messagebox.showerror("Error", "Please log in first!")
            return

        self.controller.sound_manager.play_click_sfx()

        # Start the pywebview game in a separate process
        p = multiprocessing.Process(target=launch_game_process, args=(user["id"], config))
        p.start()
