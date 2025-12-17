import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from utils.translation import TRANSLATIONS

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = DatabaseManager()

        self.grid_columnconfigure(0, weight=1)

        # --- BAŞLIK ---
        self.title_label = ctk.CTkLabel(
            self, text="", 
            font=("Impact", 40, "bold"),
            fg_color=("#3B8ED0", "#1F6AA5"),
            text_color="white",
            corner_radius=12
        )
        self.title_label.pack(pady=(50, 40), padx=20, fill="x")

        # --- GİRİŞ FORMU ---
        self.username_label = ctk.CTkLabel(self, text="", font=("Impact", 18))
        self.username_label.pack(pady=(10, 0))
        self.username_entry = ctk.CTkEntry(
            self, width=320, height=45, corner_radius=10,
            border_color=("#3B8ED0", "#1F6AA5"),
            placeholder_text="Username..."
        )
        self.username_entry.pack(pady=5)

        self.password_label = ctk.CTkLabel(self, text="", font=("Impact", 18))
        self.password_label.pack(pady=(15, 0))
        self.password_entry = ctk.CTkEntry(
            self, width=320, height=45, corner_radius=10,
            show="*", border_color=("#3B8ED0", "#1F6AA5"),
            placeholder_text="Password..."
        )
        self.password_entry.pack(pady=5)

        # --- BUTONLAR ---
        self.login_button = ctk.CTkButton(
            self, text="", 
            command=self.handle_login,
            font=("Impact", 20),
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#1F6AA5", "#144870"),
            corner_radius=15, height=50, width=250
        )
        self.login_button.pack(pady=(35, 10))

        # Kayıt Ol ve Geri Butonları (Yan yana veya alt alta ikincil stil)
        self.register_button = ctk.CTkButton(
            self, text="", 
            command=lambda: controller.show_frame("RegisterPage"),
            font=("Impact", 16),
            fg_color="transparent",
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            text_color=("#3B8ED0", "white"),
            hover_color=("#EBF4FC", "#2E2E2E"),
            corner_radius=15, height=40, width=220
        )
        self.register_button.pack(pady=5)

        self.back_button = ctk.CTkButton(
            self, text="", 
            command=lambda: controller.show_frame("HomePage"),
            font=("Impact", 14),
            fg_color="transparent",
            text_color="gray", # Geri butonu en az dikkat çeken olmalı
            hover_color=("#EBF4FC", "#2E2E2E"),
            width=100
        )
        self.back_button.pack(pady=(10, 20))

        self.update_texts()

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        lang = self.controller.current_language
        t = TRANSLATIONS[lang]["login"]
        common = TRANSLATIONS[lang]["common"]

        if not username or not password:
            messagebox.showerror(common["error"], t.get("fields_empty", "Lütfen tüm alanları doldurun."))
            return

        user = self.db.verify_user(username, password)
        if user:
            self.controller.current_user = user
            welcome_msg = t.get("welcome_msg", "Hoş geldin")
            messagebox.showinfo(common["success"], f"{welcome_msg}, {user['username']}!")
            self.controller.show_frame("LobbyScreen")
        else:
            messagebox.showerror(common["error"], t.get("invalid_creds", "Geçersiz kullanıcı adı veya şifre."))

    def update_texts(self):
        lang = self.controller.current_language
        t = TRANSLATIONS[lang]["login"]
        common = TRANSLATIONS[lang]["common"]

        self.title_label.configure(text=t["title"])
        self.username_label.configure(text=t["username"])
        self.password_label.configure(text=t["password"])
        self.login_button.configure(text=t["login_btn"])
        self.register_button.configure(text=t["no_account"])
        self.back_button.configure(text=common["back"])
        
        # Placeholder metinlerini de güncelleyelim
        self.username_entry.configure(placeholder_text=f"{t['username']}...")
        self.password_entry.configure(placeholder_text=f"{t['password']}...")