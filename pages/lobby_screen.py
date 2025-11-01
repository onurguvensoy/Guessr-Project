import tkinter as tk
from tkinter import messagebox

class LobbyScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#4B0082')
        self.controller = controller

        # Title
        title_label = tk.Label(
            self,
            text="Game Lobby",
            font=('Impact', 36, 'bold'),
            bg='#9370DB',
            fg='white',
            bd=0,
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        title_label.pack(pady=50)

        # Buttons with consistent style
        buttons_frame = tk.Frame(self, bg='#4B0082')
        buttons_frame.pack(pady=20)

        button_style = {
            'font': ("Impact", 18),
            'bg': '#9370DB',
            'fg': 'white',
            'activebackground': '#B57EDC',
            'activeforeground': 'white',
            'padx': 20,
            'pady': 10,
            'bd': 0,
            'width': 15
        }

        start_game_btn = tk.Button(
            buttons_frame,
            text="Start Game",
            command=self.start_game,
            **button_style
        )
        start_game_btn.pack(pady=10)

        profile_btn = tk.Button(
            buttons_frame,
            text="Profile",
            command=lambda: controller.show_frame("ProfilePage"),
            **button_style
        )
        profile_btn.pack(pady=10)

        back_button = tk.Button(
            buttons_frame,
            text="Back",
            command=lambda: controller.show_frame("HomePage"),
            **button_style
        )
        back_button.pack(pady=10)

    def start_game(self):
        self.controller.show_frame("GameScreen")
