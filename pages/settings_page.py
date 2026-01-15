import customtkinter as ctk
from utils.translation import TRANSLATIONS


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)

        # HEADER
        self.title_label = ctk.CTkLabel(
            self,
            text="",
            font=("Impact", 40, "bold"),
            fg_color=("#3B8ED0", "#1F6AA5"),
            text_color="white",
            corner_radius=12,
        )
        self.title_label.pack(pady=(40, 20), padx=20, fill="x")

        # SETTINGS FORM
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.pack(pady=10, padx=50, fill="x")

        # 1) Language selection (segmented control)
        self.lang_label = ctk.CTkLabel(self.form_frame, text="", font=("Impact", 20))
        self.lang_label.pack(pady=(10, 5))

        self.lang_var = ctk.StringVar(value=self.controller.current_language)
        self.lang_switch = ctk.CTkSegmentedButton(
            self.form_frame,
            values=["English", "Turkish"],
            command=self.change_language,
            variable=self.lang_var,
            font=("Impact", 16),
            selected_color=("#3B8ED0", "#1F6AA5"),
            corner_radius=10,
            width=300,
            height=40,
        )
        self.lang_switch.pack(pady=5)

        # 2) Dark mode
        self.dark_label = ctk.CTkLabel(self.form_frame, text="", font=("Impact", 20))
        self.dark_label.pack(pady=(20, 5))

        self.dark_switch = ctk.CTkSwitch(
            self.form_frame,
            text="",
            command=self.toggle_dark_mode,
            font=("Impact", 16),
            progress_color=("#3B8ED0", "#1F6AA5"),
        )
        # Sync switch state with the current appearance mode
        if ctk.get_appearance_mode() == "Dark":
            self.dark_switch.select()
        self.dark_switch.pack(pady=5)

        # 3) Music on/off
        self.music_label = ctk.CTkLabel(self.form_frame, text="", font=("Impact", 20))
        self.music_label.pack(pady=(20, 5))

        self.music_switch = ctk.CTkSwitch(
            self.form_frame,
            text="",
            command=self.toggle_music,
            font=("Impact", 16),
            progress_color=("#3B8ED0", "#1F6AA5"),
        )
        if self.controller.sound_manager.music_enabled:
            self.music_switch.select()
        self.music_switch.pack(pady=5)

        # 4) Sound effects on/off
        self.sfx_label = ctk.CTkLabel(self.form_frame, text="", font=("Impact", 20))
        self.sfx_label.pack(pady=(20, 5))

        self.sfx_switch = ctk.CTkSwitch(
            self.form_frame,
            text="",
            command=self.toggle_sfx,
            font=("Impact", 16),
            progress_color=("#3B8ED0", "#1F6AA5"),
        )
        if self.controller.sound_manager.sfx_enabled:
            self.sfx_switch.select()
        self.sfx_switch.pack(pady=5)

        # --- BACK BUTTON ---
        self.back_btn = ctk.CTkButton(
            self,
            text="",
            command=lambda: controller.show_frame("HomePage"),
            font=("Impact", 18),
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#1F6AA5", "#144870"),
            corner_radius=15,
            height=45,
            width=200,
        )
        self.back_btn.pack(pady=(40, 20))

        self.update_texts()

    def toggle_dark_mode(self) -> None:
        if self.dark_switch.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

        # Refresh labels so the on/off text stays in sync
        self.update_texts()

    def toggle_music(self) -> None:
        is_on = bool(self.music_switch.get())
        self.controller.sound_manager.toggle_music(is_on)
        self.update_texts()

    def toggle_sfx(self) -> None:
        is_on = bool(self.sfx_switch.get())
        self.controller.sound_manager.toggle_sfx(is_on)
        self.update_texts()

    def change_language(self, choice: str) -> None:
        self.controller.current_language = choice
        self.controller.update_all_languages()

    def update_texts(self) -> None:
        lang = self.controller.current_language
        t = TRANSLATIONS[lang]["settings"]
        common = TRANSLATIONS[lang]["common"]

        self.title_label.configure(text=t["title"])
        self.lang_label.configure(text=t["language"])
        self.dark_label.configure(text=t["dark_mode"])
        self.music_label.configure(text=t["music"])
        self.sfx_label.configure(text=t["sfx"])

        # Switch state labels (ON/OFF)
        on_txt = t.get("on", "ON")
        off_txt = t.get("off", "OFF")

        self.dark_switch.configure(text=on_txt if self.dark_switch.get() else off_txt)
        self.music_switch.configure(text=on_txt if self.music_switch.get() else off_txt)
        self.sfx_switch.configure(text=on_txt if self.sfx_switch.get() else off_txt)

        self.back_btn.configure(text=common["back"])
