import customtkinter as ctk
from database.db_manager import DatabaseManager

class LobbyScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = DatabaseManager()
        self.selected_playlist = "World Spotlight"

        self.grid_columnconfigure(0, weight=1)

        # --- BAŞLIK ---
        self.title_label = ctk.CTkLabel(self, text="LOBBY", font=("Impact", 35), fg_color=("#3B8ED0", "#1F6AA5"), text_color="white", corner_radius=10)
        self.title_label.pack(pady=(20, 5), padx=20, fill="x")

        # --- PLAYLIST LİSTESİ ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=250, label_text="Select Playlist", fg_color="transparent")
        self.scroll_frame.pack(pady=5, padx=40, fill="both", expand=True)

        # --- AYARLAR PANELİ ---
        self.settings_card = ctk.CTkFrame(self, fg_color=("#EBF4FC", "#1A1A1A"), corner_radius=15)
        self.settings_card.pack(pady=10, padx=40, fill="x")

        # Round & Timer
        self.opt_frame = ctk.CTkFrame(self.settings_card, fg_color="transparent")
        self.opt_frame.pack(pady=10)
        
        ctk.CTkLabel(self.opt_frame, text="Rounds:").grid(row=0, column=0, padx=5)
        self.round_combo = ctk.CTkComboBox(self.opt_frame, values=["3", "5", "10"], width=90)
        self.round_combo.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(self.opt_frame, text="Timer:").grid(row=0, column=2, padx=5)
        self.timer_combo = ctk.CTkComboBox(self.opt_frame, values=["30", "60", "No Limit"], width=100)
        self.timer_combo.grid(row=0, column=3, padx=5)

        # NO PAN / NO MOVE SWITCH (Yeni Özellik)
        self.no_move_var = ctk.BooleanVar(value=False)
        self.no_move_switch = ctk.CTkSwitch(
            self.settings_card, text="Disable Navigation (No Move)", 
            variable=self.no_move_var, font=("Impact", 14),
            progress_color=("#3B8ED0", "#1F6AA5")
        )
        self.no_move_switch.pack(pady=(0, 15))

        # --- BUTONLAR ---
        self.start_btn = ctk.CTkButton(self, text="START GAME", command=self.start_game, font=("Impact", 20), fg_color="#1F6AA5", height=45)
        self.start_btn.pack(pady=5, padx=40, fill="x")

        self.create_btn = ctk.CTkButton(self, text="CREATE PLAYLIST / MAP", command=lambda: controller.show_frame("CreatePlaylistPage"), fg_color="#1F6AA5")
        self.create_btn.pack(pady=5, padx=40, fill="x")

        self.back_btn = ctk.CTkButton(self, text="BACK", command=lambda: controller.show_frame("HomePage"), fg_color="gray")
        self.back_btn.pack(pady=5)

    def on_show(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        playlists = self.db.get_all_playlists()
        for p in playlists:
            btn = ctk.CTkButton(self.scroll_frame, text=p, fg_color=("#D1E8FF", "#2B2B2B"), text_color=("#1F6AA5", "white"),
                                 command=lambda n=p: self.select_p(n))
            btn.pack(pady=2, fill="x", padx=10)

    def select_p(self, name):
        self.selected_playlist = name
        self.title_label.configure(text=f"MAP: {name.upper()}")

    def start_game(self):
        self.controller.game_config = {
            "playlist": self.selected_playlist,
            "rounds": int(self.round_combo.get()),
            "timer": self.timer_combo.get(),
            "no_move": self.no_move_var.get() # JS'e gönderilecek veri
        }
        self.controller.show_frame("GameScreen")