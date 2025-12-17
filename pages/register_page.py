import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from utils.translation import TRANSLATIONS

class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        # Frame otomatik tema takibi yapar
        super().__init__(parent)
        self.controller = controller
        self.db = DatabaseManager()

        # Grid yapılandırması (Merkezleme)
        self.grid_columnconfigure(0, weight=1)

        # --- BAŞLIK ---
        self.title_label = ctk.CTkLabel(
            self, text="", 
            font=("Impact", 35, "bold"),
            fg_color=("#3B8ED0", "#1F6AA5"),
            text_color="white",
            corner_radius=10
        )
        self.title_label.pack(pady=(40, 30), padx=20, fill="x")

        # --- GİRİŞ ALANLARI FORMU ---
        # Kullanıcı Adı
        self.username_label = ctk.CTkLabel(self, text="", font=("Impact", 18))
        self.username_label.pack(pady=(10, 0))
        self.username_entry = ctk.CTkEntry(
            self, width=300, height=40, corner_radius=10,
            border_color=("#3B8ED0", "#1F6AA5")
        )
        self.username_entry.pack(pady=5)

        # Email
        self.email_label = ctk.CTkLabel(self, text="", font=("Impact", 18))
        self.email_label.pack(pady=(10, 0))
        self.email_entry = ctk.CTkEntry(
            self, width=300, height=40, corner_radius=10,
            border_color=("#3B8ED0", "#1F6AA5")
        )
        self.email_entry.pack(pady=5)

        # Şifre
        self.password_label = ctk.CTkLabel(self, text="", font=("Impact", 18))
        self.password_label.pack(pady=(10, 0))
        self.password_entry = ctk.CTkEntry(
            self, width=300, height=40, corner_radius=10,
            show="*", border_color=("#3B8ED0", "#1F6AA5")
        )
        self.password_entry.pack(pady=5)

        # --- BUTONLAR ---
        # Kayıt Ol Butonu
        self.register_button = ctk.CTkButton(
            self, text="", 
            command=self.handle_register,
            font=("Impact", 18),
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#1F6AA5", "#144870"),
            corner_radius=15, height=45, width=220
        )
        self.register_button.pack(pady=(30, 10))

        # Giriş Sayfasına Dön Butonu
        self.back_button = ctk.CTkButton(
            self, text="", 
            command=lambda: controller.show_frame("LoginPage"),
            font=("Impact", 16),
            fg_color="transparent", # Daha az vurgulu, modern görünüm
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            text_color=("#3B8ED0", "white"),
            hover_color=("#EBF4FC", "#2E2E2E"),
            corner_radius=15, height=40, width=200
        )
        self.back_button.pack(pady=10)

        # Metinleri yükle
        self.update_texts()

    def handle_register(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        lang = self.controller.current_language
        common_txt = TRANSLATIONS[lang]["common"]

        if not username or not email or not password:
            messagebox.showerror(common_txt["error"], "Lütfen tüm alanları doldurun." if lang == "Turkish" else "Please fill in all fields.")
            return

        if self.db.add_user(username, password, email):
            messagebox.showinfo(common_txt["success"], "Kayıt başarılı! Giriş yapabilirsiniz." if lang == "Turkish" else "Registration Successful! You can now log in.")
            self.controller.show_frame("LoginPage")
        else:
            messagebox.showerror(common_txt["error"], "Kullanıcı adı veya email zaten mevcut." if lang == "Turkish" else "Username or email already exists.")

    def update_texts(self):
        lang = self.controller.current_language
        t = TRANSLATIONS[lang]["register"]
        common = TRANSLATIONS[lang]["common"]

        self.title_label.configure(text=t["title"])
        self.username_label.configure(text=t["username"])
        self.email_label.configure(text=t["email"])
        self.password_label.configure(text=t["password"])
        self.register_button.configure(text=t["register_btn"])
        self.back_button.configure(text=t["has_account"])