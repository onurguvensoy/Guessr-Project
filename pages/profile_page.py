import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from utils.translation import TRANSLATIONS

class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = DatabaseManager()

        self.grid_columnconfigure(0, weight=1)

        # --- BAŞLIK ---
        self.title_label = ctk.CTkLabel(
            self, text="", 
            font=("Impact", 35, "bold"),
            fg_color=("#3B8ED0", "#1F6AA5"),
            text_color="white",
            corner_radius=10
        )
        self.title_label.pack(pady=(30, 20), padx=20, fill="x")

        # --- GİRİŞ ALANLARI ---
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.pack(pady=10)

        self.username_label = ctk.CTkLabel(self.form_frame, text="", font=("Impact", 18))
        self.username_label.pack(pady=(10, 0))
        self.username_entry = ctk.CTkEntry(
            self.form_frame, width=300, height=40, corner_radius=10,
            border_color=("#3B8ED0", "#1F6AA5")
        )
        self.username_entry.pack(pady=5)

        self.email_label = ctk.CTkLabel(self.form_frame, text="", font=("Impact", 18))
        self.email_label.pack(pady=(10, 0))
        self.email_entry = ctk.CTkEntry(
            self.form_frame, width=300, height=40, corner_radius=10,
            border_color=("#3B8ED0", "#1F6AA5")
        )
        self.email_entry.pack(pady=5)

        # --- İSTATİSTİK KARTI ---
        self.stats_frame = ctk.CTkFrame(
            self, 
            fg_color=("#EBF4FC", "#1A1A1A"), # Light'ta çok açık mavi, Dark'ta çok koyu gri/siyah
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            corner_radius=15
        )
        self.stats_frame.pack(pady=20, padx=50, fill="x")
        
        self.stats_label = ctk.CTkLabel(
            self.stats_frame,
            text="",
            font=("Impact", 18),
            text_color=("#1F6AA5", "#3B8ED0")
        )
        self.stats_label.pack(pady=15)

        # --- BUTONLAR ---
        self.save_btn = ctk.CTkButton(
            self, text="", 
            command=self.save_changes,
            font=("Impact", 18),
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#1F6AA5", "#144870"),
            corner_radius=15, height=45, width=220
        )
        self.save_btn.pack(pady=10)

        self.back_btn = ctk.CTkButton(
            self, text="", 
            command=lambda: controller.show_frame("LobbyScreen"),
            font=("Impact", 16),
            fg_color="transparent",
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            text_color=("#3B8ED0", "white"),
            hover_color=("#EBF4FC", "#2E2E2E"),
            corner_radius=15, height=40, width=200
        )
        self.back_btn.pack(pady=10)

        self.update_texts()

    def on_show(self):
        """Sayfa her gösterildiğinde verileri yeniler."""
        user = getattr(self.controller, "current_user", None)
        lang = self.controller.current_language
        common_txt = TRANSLATIONS[lang]["common"]

        if not user:
            messagebox.showerror(common_txt["error"], "Lütfen önce giriş yapın." if lang == "Turkish" else "Please log in first.")
            self.controller.show_frame("LoginPage")
            return

        self.username_entry.delete(0, 'end')
        self.username_entry.insert(0, user["username"])
        self.email_entry.delete(0, 'end')
        self.email_entry.insert(0, user["email"])

        stats = self.db.get_user_stats(user["id"])
        t = TRANSLATIONS[lang]["profile"]
        
        # İstatistik metnini dinamik olarak birleştir
        stats_text = (f"{t['games_played']}: {stats['games_played']}  |  "
                      f"{t['total_score']}: {stats['total_score']}  |  "
                      f"{t['best_score']}: {stats['best_score']}")
        self.stats_label.configure(text=stats_text)

    def save_changes(self):
        user = getattr(self.controller, "current_user", None)
        lang = self.controller.current_language
        common_txt = TRANSLATIONS[lang]["common"]

        if not user: return

        new_username = self.username_entry.get().strip()
        new_email = self.email_entry.get().strip()

        if not new_username or not new_email:
            messagebox.showerror(common_txt["error"], "Alanlar boş bırakılamaz." if lang == "Turkish" else "Fields cannot be empty.")
            return

        if self.db.update_user(user["id"], new_username, new_email):
            self.controller.current_user = {"id": user["id"], "username": new_username, "email": new_email}
            messagebox.showinfo(common_txt["success"], "Profil güncellendi!" if lang == "Turkish" else "Profile updated!")
            self.on_show()
        else:
            messagebox.showerror(common_txt["error"], "Kullanıcı adı veya email kullanımda." if lang == "Turkish" else "Username/email already in use.")

    def update_texts(self):
        lang = self.controller.current_language
        t = TRANSLATIONS[lang]["profile"]
        common = TRANSLATIONS[lang]["common"]

        self.title_label.configure(text=t["title"])
        self.username_label.configure(text=t["username"])
        self.email_label.configure(text=t["email"])
        self.save_btn.configure(text=common["save"])
        self.back_btn.configure(text=common["back"])
        # İstatistik metnini de mevcut verilerle güncellemek için on_show'u tetikleyebiliriz
        if getattr(self.controller, "current_user", None):
            self.on_show()