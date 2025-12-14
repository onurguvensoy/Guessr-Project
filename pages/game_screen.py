import os
import random
import math
import tkinter as tk
from tkinter import messagebox

try:
    import webview
except ImportError:
    webview = None


COORDS = [
    (41.0082, 28.9784),   # İstanbul
    (48.8584, 2.2945),    # Eiffel
    (40.6892, -74.0445),  # Statue of Liberty
]

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p = math.pi / 180.0
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = (math.sin(dlat/2)**2 +
         math.cos(lat1*p)*math.cos(lat2*p)*math.sin(dlon/2)**2)
    return 2 * R * math.asin(math.sqrt(a))


class GameApi:
    def __init__(self):
        self.target = random.choice(COORDS)

    def get_target(self):
        return {"lat": self.target[0], "lng": self.target[1]}

    def submit_guess(self, lat, lng):
        dist_km = haversine_km(self.target[0], self.target[1], lat, lng)
        score = max(0, int(5000 - dist_km * 50))
        return {"distance_km": dist_km, "score": score, "target": self.get_target()}


def open_game_window():
    if webview is None:
        messagebox.showerror(
            "Eksik Paket",
            "pywebview kurulu değil.\n\nTerminalde şunu çalıştır:\n\npip install pywebview"
        )
        return

    api = GameApi()

    # pages/ içinden proje köküne çıkıp web/game.html buluyoruz
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    html_path = os.path.join(base_dir, "web", "game.html")

    if not os.path.exists(html_path):
        messagebox.showerror(
            "Dosya bulunamadı",
            f"Bulunamadı:\n{html_path}\n\nweb/game.html oluşturduğundan emin ol."
        )
        return

    webview.create_window(
        "Guessr Game",
        html_path,
        js_api=api,
        width=1200,
        height=800
    )
    webview.start()


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
            text="GeoGuessr modu: Street View + haritadan tahmin",
            font=("Impact", 16),
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

        tk.Button(self, text="Start Round", command=open_game_window, **btn_style).pack(pady=10)
        tk.Button(self, text="Back to Lobby", command=lambda: controller.show_frame("LobbyScreen"), **btn_style).pack(pady=10)
        tk.Button(self, text="Quit", command=controller.quit, **btn_style).pack(pady=10)

    def on_show(self):
        pass
