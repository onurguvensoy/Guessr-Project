import os
import random
import math
import multiprocessing
import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from utils.translation import TRANSLATIONS

try:
    import webview
except ImportError:
    webview = None

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p = math.pi / 180.0
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = (math.sin(dlat / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))

class GameApi:
    """JavaScript ile Python arasındaki köprü."""
    def __init__(self, db, user_id, config):
        self.db = db
        self.user_id = user_id
        self.config = config 
        
        self.playlist_name = config.get("playlist", "World Spotlight")
        self.session_id = self.db.start_session(user_id, self.playlist_name)
        
        # Seçilen playlist'e göre koordinat havuzunu çek
        self.coords_pool = self.db.get_locations_for_playlist(self.playlist_name)
        
        self.rounds_total = int(config.get("rounds", 3))
        self.round_index = 1
        self.total_score = 0
        self.target = random.choice(self.coords_pool)
        self.window = None

    def set_window(self, window):
        self.window = window

    def close_window(self):
        if self.window:
            self.window.destroy()

    def get_state(self):
        """JS tarafına tüm ayarları gönderir."""
        return {
            "round": self.round_index,
            "rounds_total": self.rounds_total,
            "total_score": self.total_score,
            "target": {"lat": self.target[0], "lng": self.target[1]},
            "no_move": self.config.get("no_move", False),
            "timer": self.config.get("timer", "No Limit")
        }

    def submit_guess(self, lat, lng):
        try:
            # Gelen verilerin float olduğundan emin olalım
            guess_lat = float(lat)
            guess_lng = float(lng)
            target_lat = float(self.target[0])
            target_lng = float(self.target[1])

            # Mesafe hesapla
            dist_km = haversine_km(target_lat, target_lng, guess_lat, guess_lng)
            
            # Puanlama Mantığı: 5000 üzerinden (1000km üstü puan hızla düşer)
            # max(0, ...) ile eksi puan almayı engelliyoruz
            score = max(0, int(5000 - (dist_km * 2))) 
            
            # Eğer mesafe çok uzaksa (örn 2500km+) skorun 0 olmamasını istiyorsan 
            # minimum bir puan verebilirsin: score = max(10, score)

            self.total_score += score
            
            # Veritabanına Kaydet
            self.db.add_round(self.session_id, target_lat, target_lng, guess_lat, guess_lng, dist_km, score)
            
            finished = (self.round_index >= self.rounds_total)
            
            res = {
                "finished": finished, 
                "round": int(self.round_index), 
                "rounds_total": int(self.rounds_total), 
                "distance_km": float(dist_km), 
                "score": int(score), 
                "total_score": int(self.total_score)
            }
            
            if not finished:
                self.round_index += 1
                self.target = random.choice(self.coords_pool)
                res["next_target"] = {"lat": float(self.target[0]), "lng": float(self.target[1])}
            else:
                self.db.end_session(self.session_id)
            
            return res
        except Exception as e:
            print(f"Scoring Error: {e}")
            return {"error": str(e), "score": 0, "total_score": self.total_score}

def launch_game_process(user_id, config):
    """Oyunu ayrı bir sistem prosesi olarak başlatır."""
    db = DatabaseManager()
    api = GameApi(db, user_id, config)
    
    # DOSYA YOLU DÜZELTMESİ:
    # Bu yöntem, script nerede çalışırsa çalışsın 'web/game.html'i doğru bulur.
    current_dir = os.path.dirname(os.path.abspath(__file__)) # pages klasörü
    project_root = os.path.dirname(current_dir) # Ana proje klasörü
    html_path = os.path.join(project_root, "web", "game.html")
    
    # Terminale yazdırarak kontrol edelim (Sorun olursa buradaki yolu kontrol et)
    print(f"Loading HTML from: {html_path}")
    
    if not os.path.exists(html_path):
        print("HATA: game.html dosyası bulunamadı! Lütfen web klasörünü kontrol edin.")

    window = webview.create_window(
        title=f"Guessr - {config.get('playlist')}", 
        url=html_path, 
        js_api=api, 
        width=1200, 
        height=850
    )
    api.set_window(window)
    
    # http_server=True kullanıldığında webview dosyayı sunucu üzerinden servis eder
    webview.start(http_server=True)

class GameScreen(ctk.CTkFrame):
    """Tkinter tarafındaki oyun başlatma ekranı."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = DatabaseManager()

        self.grid_columnconfigure(0, weight=1)

        # --- UI ELEMANLARI ---
        self.title_label = ctk.CTkLabel(
            self, text="PREPARE FOR ADVENTURE", 
            font=("Impact", 40, "bold"), 
            fg_color=("#3B8ED0", "#1F6AA5"), 
            text_color="white", 
            corner_radius=12
        )
        self.title_label.pack(pady=(40, 20), padx=20, fill="x")

        self.summary_card = ctk.CTkFrame(self, fg_color=("#EBF4FC", "#1A1A1A"), border_width=2, border_color=("#3B8ED0", "#1F6AA5"), corner_radius=15)
        self.summary_card.pack(pady=20, padx=50, fill="x")

        self.info_label = ctk.CTkLabel(
            self.summary_card, text="Select a playlist in the lobby...", 
            font=("Impact", 18), text_color=("#1F6AA5", "#3B8ED0"), wraplength=600
        )
        self.info_label.pack(pady=30, padx=20)

        self.start_btn = ctk.CTkButton(
            self, text="LAUNCH GAME", 
            command=self.start_game_process, 
            font=("Impact", 24), 
            height=60, 
            width=320,
            fg_color=("#3B8ED0", "#1F6AA5")
        )
        self.start_btn.pack(pady=20)

        self.back_btn = ctk.CTkButton(
            self, text="BACK TO LOBBY", 
            command=lambda: controller.show_frame("LobbyScreen"),
            font=("Impact", 16), 
            fg_color="transparent", 
            border_width=2, 
            border_color=("#3B8ED0", "#1F6AA5")
        )
        self.back_btn.pack(pady=10)

    def on_show(self):
        """Lobi seçimlerini özete yansıtır."""
        config = getattr(self.controller, "game_config", {"playlist": "World Spotlight", "rounds": 3, "timer": "No Limit", "no_move": False})
        
        mode_str = "No Move" if config.get("no_move") else "Classic (Movement On)"
        msg = f"Playlist: {config['playlist']}\nMode: {mode_str}\nRounds: {config['rounds']}\nTimer: {config['timer']}"
        self.info_label.configure(text=msg)

    def start_game_process(self):
        user = getattr(self.controller, "current_user", None)
        config = getattr(self.controller, "game_config", {"playlist": "World Spotlight", "rounds": 3})
        
        if not user:
            messagebox.showerror("Error", "Please login first!")
            return

        self.controller.sound_manager.play_click_sfx()
        
        # MULTIPROCESSING BAŞLATMA
        p = multiprocessing.Process(target=launch_game_process, args=(user["id"], config))
        p.start()