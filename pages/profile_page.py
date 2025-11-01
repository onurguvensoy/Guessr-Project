import tkinter as tk
from tkinter import messagebox
from database.db_manager import DatabaseManager

class ProfilePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#4B0082')
        self.controller = controller
        self.db = DatabaseManager()

        # Title
        title_label = tk.Label(
            self,
        text="User Profile",
            font=('Impact', 36, 'bold'),
            bg='#9370DB',
            fg='white',
            bd=0,
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        title_label.pack(pady=30)

        # Profile info frame
        self.info_frame = tk.Frame(self, bg='#4B0082')
        self.info_frame.pack(pady=20)

        # Labels and entries with consistent style
        label_style = {
            'font': ('Impact', 14),
            'bg': '#4B0082',
            'fg': 'white'
        }

        entry_style = {
            'font': ('Helvetica', 12),
            'width': 30
        }

        # Username
        tk.Label(self.info_frame, text="Username:", **label_style).pack(pady=5)
        self.username_entry = tk.Entry(self.info_frame, **entry_style)
        self.username_entry.pack(pady=5)

        # Email
        tk.Label(self.info_frame, text="Email:", **label_style).pack(pady=5)
        self.email_entry = tk.Entry(self.info_frame, **entry_style)
        self.email_entry.pack(pady=5)

        # Buttons
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

        # Save button
        save_btn = tk.Button(
            self,
            text="Save Changes",
            command=self.save_changes,
            **button_style
        )
        save_btn.pack(pady=10)

        # Back button
        back_btn = tk.Button(
            self,
            text="Back to Lobby",
            command=lambda: controller.show_frame("LobbyScreen"),
            **button_style
        )
        back_btn.pack(pady=10)

    def save_changes(self):
        # Add implementation for saving profile changes
        messagebox.showinfo("Success", "Profile updated successfully!")

    def update_profile_info(self, username, email):
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, username)
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, email)
