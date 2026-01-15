import customtkinter as ctk
import multiprocessing
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.settings_page import SettingsPage
from pages.lobby_screen import LobbyScreen
from pages.profile_page import ProfilePage
from pages.game_screen import GameScreen
from utils.sound_manager import SoundManager
from pages.leaderboard_page import LeaderboardPage
from pages.create_playlist_page import CreatePlaylistPage

# Global theme settings
ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")

class GeoGuessrApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Guess the Location")
        self.geometry("900x700")

        
        self.current_user = None
        self.current_language = "English"  # Default language
        
        # Initialize audio system
        self.sound_manager = SoundManager()
        self.sound_manager.play_bg_music()

        # MAIN CONTAINER
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Page registry
        self.frames = {}
        for F in (HomePage, LoginPage, RegisterPage, SettingsPage, LobbyScreen, ProfilePage, GameScreen, LeaderboardPage, CreatePlaylistPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name: str):
        # Click sound effect
        self.sound_manager.play_click_sfx()
        
        frame = self.frames[page_name]
        
        # Refresh page data before showing it (if `on_show` exists)
        if hasattr(frame, "on_show") and callable(frame.on_show):
            frame.on_show()
            
        frame.tkraise()

    def update_all_languages(self):
        for frame in self.frames.values():
            if hasattr(frame, "update_texts"):
                frame.update_texts()

    def on_closing(self):
        self.sound_manager.stop_music()
        self.destroy()

if __name__ == "__main__":
    multiprocessing.freeze_support()

    app = GeoGuessrApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
