import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from utils.translation import TRANSLATIONS


class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = DatabaseManager()

        self.grid_columnconfigure(0, weight=1)

        # --- HEADER ---
        self.title_label = ctk.CTkLabel(
            self,
            text="",
            font=("Impact", 35, "bold"),
            fg_color=("#3B8ED0", "#1F6AA5"),
            text_color="white",
            corner_radius=10,
        )
        self.title_label.pack(pady=(40, 30), padx=20, fill="x")

        # --- INPUTS ---
        self.username_label = ctk.CTkLabel(self, text="", font=("Impact", 18))
        self.username_label.pack(pady=(10, 0))
        self.username_entry = ctk.CTkEntry(
            self,
            width=300,
            height=40,
            corner_radius=10,
            border_color=("#3B8ED0", "#1F6AA5"),
        )
        self.username_entry.pack(pady=5)

        self.email_label = ctk.CTkLabel(self, text="", font=("Impact", 18))
        self.email_label.pack(pady=(10, 0))
        self.email_entry = ctk.CTkEntry(
            self,
            width=300,
            height=40,
            corner_radius=10,
            border_color=("#3B8ED0", "#1F6AA5"),
        )
        self.email_entry.pack(pady=5)

        self.password_label = ctk.CTkLabel(self, text="", font=("Impact", 18))
        self.password_label.pack(pady=(10, 0))
        self.password_entry = ctk.CTkEntry(
            self,
            width=300,
            height=40,
            corner_radius=10,
            show="*",
            border_color=("#3B8ED0", "#1F6AA5"),
        )
        self.password_entry.pack(pady=5)

        # --- ACTION BUTTONS ---
        self.register_button = ctk.CTkButton(
            self,
            text="",
            command=self.handle_register,
            font=("Impact", 18),
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#1F6AA5", "#144870"),
            corner_radius=15,
            height=45,
            width=220,
        )
        self.register_button.pack(pady=(30, 10))

        self.back_button = ctk.CTkButton(
            self,
            text="",
            command=lambda: controller.show_frame("LoginPage"),
            font=("Impact", 16),
            fg_color="transparent",
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            text_color=("#3B8ED0", "white"),
            hover_color=("#EBF4FC", "#2E2E2E"),
            corner_radius=15,
            height=40,
            width=200,
        )
        self.back_button.pack(pady=10)

        # Load localized labels
        self.update_texts()

    def handle_register(self) -> None:
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        lang = self.controller.current_language
        common_txt = TRANSLATIONS[lang]["common"]

        if not username or not email or not password:
            messagebox.showerror(common_txt["error"], "Please fill in all fields.")
            return

        if self.db.add_user(username, password, email):
            messagebox.showinfo(common_txt["success"], "Registration successful! You can now log in.")
            self.controller.show_frame("LoginPage")
        else:
            messagebox.showerror(common_txt["error"], "Username or email already exists.")

    def update_texts(self) -> None:
        lang = self.controller.current_language
        t = TRANSLATIONS[lang]["register"]

        self.title_label.configure(text=t["title"])
        self.username_label.configure(text=t["username"])
        self.email_label.configure(text=t["email"])
        self.password_label.configure(text=t["password"])
        self.register_button.configure(text=t["register_btn"])
        self.back_button.configure(text=t["has_account"])
