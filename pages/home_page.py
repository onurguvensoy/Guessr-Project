import customtkinter as ctk
from utils.translation import TRANSLATIONS


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Grid configuration (helps keep content centered)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        # MAIN
        self.title_label = ctk.CTkLabel(
            self,
            text="HalonGuessr",
            font=("Impact", 50, "bold"),
            fg_color=("#3B8ED0", "#1F6AA5"),
            text_color="white",
            corner_radius=15,
            height=100,
        )
        self.title_label.grid(row=1, column=0, pady=(0, 50), padx=40, sticky="ew")

        # BUTTONS
        self.menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_frame.grid(row=2, column=0)

        # Standard button sizing
        btn_width = 250
        btn_height = 50
        btn_font = ("Impact", 20)

        # Login
        self.login_btn = ctk.CTkButton(
            self.menu_frame,
            text="",
            command=lambda: controller.show_frame("LoginPage"),
            font=btn_font,
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#1F6AA5", "#144870"),
            corner_radius=15,
            width=btn_width,
            height=btn_height,
        )
        self.login_btn.pack(pady=10)

        # Register
        self.register_btn = ctk.CTkButton(
            self.menu_frame,
            text="",
            command=lambda: controller.show_frame("RegisterPage"),
            font=btn_font,
            fg_color="transparent",
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            text_color=("#3B8ED0", "white"),
            hover_color=("#EBF4FC", "#2E2E2E"),
            corner_radius=15,
            width=btn_width,
            height=btn_height,
        )
        self.register_btn.pack(pady=10)

        # Leaderboard
        self.leaderboard_btn = ctk.CTkButton(
            self.menu_frame,
            text="LEADERBOARD",
            command=lambda: controller.show_frame("LeaderboardPage"),
            font=btn_font,
            fg_color="transparent",
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            text_color=("#3B8ED0", "white"),
            hover_color=("#EBF4FC", "#2E2E2E"),
            corner_radius=15,
            width=btn_width,
            height=btn_height,
        )
        self.leaderboard_btn.pack(pady=10)

        # Settings
        self.settings_btn = ctk.CTkButton(
            self.menu_frame,
            text="",
            command=lambda: controller.show_frame("SettingsPage"),
            font=btn_font,
            fg_color="transparent",
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            text_color=("#3B8ED0", "white"),
            hover_color=("#EBF4FC", "#2E2E2E"),
            corner_radius=15,
            width=btn_width,
            height=btn_height,
        )
        self.settings_btn.pack(pady=10)

        # Exit (red accent)
        self.exit_btn = ctk.CTkButton(
            self,
            text="",
            command=controller.quit,
            font=("Impact", 16),
            fg_color="#CC3333",
            hover_color="#992626",
            corner_radius=15,
            width=180,
            height=40,
        )
        self.exit_btn.grid(row=5, column=0, pady=(60, 0))

        # Load localized text labels
        self.update_texts()

    def update_texts(self) -> None:
        lang = self.controller.current_language
        t = TRANSLATIONS[lang]["home"]
        common = TRANSLATIONS[lang]["common"]

        self.title_label.configure(text=t["title"])
        self.login_btn.configure(text=t["login"])
        self.register_btn.configure(text=t["register"])
        self.settings_btn.configure(text=t["settings"])
        self.exit_btn.configure(text=common["exit"])
