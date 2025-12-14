import tkinter as tk

from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.settings_page import SettingsPage
from pages.lobby_screen import LobbyScreen
from pages.profile_page import ProfilePage
from pages.game_screen import GameScreen


class GeoGuessrApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GeoGuessr Clone")
        self.geometry("800x600")
        self.minsize(800, 600)

        # Logged-in user state (dict: id/username/email) or None
        self.current_user = None

        self.container = tk.Frame(self, bg="#1E90FF")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.configure(bg="#1E90FF")

        self.frames = {}
        for F in (HomePage, LoginPage, RegisterPage, SettingsPage, LobbyScreen, ProfilePage, GameScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name: str):
        frame = self.frames[page_name]
        frame.tkraise()

        # Optional lifecycle hook for pages that need refresh when shown
        on_show = getattr(frame, "on_show", None)
        if callable(on_show):
            on_show()


if __name__ == "__main__":
    app = GeoGuessrApp()
    app.mainloop()
