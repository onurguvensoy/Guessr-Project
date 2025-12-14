import tkinter as tk
from tkinter import messagebox


class LobbyScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#4B0082')
        self.controller = controller

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
        title_label.pack(pady=30)

        self.welcome_label = tk.Label(
            self,
            text="Welcome!",
            font=('Impact', 18, 'bold'),
            bg='#4B0082',
            fg='white'
        )
        self.welcome_label.pack(pady=10)

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

        logout_btn = tk.Button(
            buttons_frame,
            text="Logout",
            command=self.logout,
            **button_style
        )
        logout_btn.pack(pady=10)

    def on_show(self):
        user = getattr(self.controller, "current_user", None)
        if user:
            self.welcome_label.config(text=f"Welcome, {user['username']}!")
        else:
            self.welcome_label.config(text="Welcome!")

    def start_game(self):
        user = getattr(self.controller, "current_user", None)
        if not user:
            messagebox.showerror("Not Logged In", "Please log in first.")
            self.controller.show_frame("LoginPage")
            return
        self.controller.show_frame("GameScreen")

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame("HomePage")
