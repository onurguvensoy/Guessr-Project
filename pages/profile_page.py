import tkinter as tk
from tkinter import messagebox
from database.db_manager import DatabaseManager


class ProfilePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#4B0082')
        self.controller = controller
        self.db = DatabaseManager()

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
        title_label.pack(pady=20)

        self.info_frame = tk.Frame(self, bg='#4B0082')
        self.info_frame.pack(pady=10)

        label_style = {'font': ('Impact', 14), 'bg': '#4B0082', 'fg': 'white'}
        entry_style = {'font': ('Helvetica', 12), 'width': 30}

        tk.Label(self.info_frame, text="Username:", **label_style).pack(pady=5)
        self.username_entry = tk.Entry(self.info_frame, **entry_style)
        self.username_entry.pack(pady=5)

        tk.Label(self.info_frame, text="Email:", **label_style).pack(pady=5)
        self.email_entry = tk.Entry(self.info_frame, **entry_style)
        self.email_entry.pack(pady=5)

        self.stats_label = tk.Label(
            self,
            text="Games: 0 | Total: 0 | Best: 0",
            font=('Impact', 16),
            bg='#4B0082',
            fg='white'
        )
        self.stats_label.pack(pady=10)

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

        save_btn = tk.Button(self, text="Save Changes", command=self.save_changes, **button_style)
        save_btn.pack(pady=10)

        back_btn = tk.Button(self, text="Back to Lobby", command=lambda: controller.show_frame("LobbyScreen"), **button_style)
        back_btn.pack(pady=10)

    def on_show(self):
        user = getattr(self.controller, "current_user", None)
        if not user:
            messagebox.showerror("Not Logged In", "Please log in first.")
            self.controller.show_frame("LoginPage")
            return

        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, user["username"])
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, user["email"])

        stats = self.db.get_user_stats(user["id"])
        self.stats_label.config(
            text=f"Games: {stats['games_played']} | Total: {stats['total_score']} | Best: {stats['best_score']}"
        )

    def save_changes(self):
        user = getattr(self.controller, "current_user", None)
        if not user:
            messagebox.showerror("Not Logged In", "Please log in first.")
            self.controller.show_frame("LoginPage")
            return

        new_username = self.username_entry.get().strip()
        new_email = self.email_entry.get().strip()

        if not new_username or not new_email:
            messagebox.showerror("Error", "Username and Email cannot be empty.")
            return

        ok = self.db.update_user(user["id"], new_username, new_email)
        if not ok:
            messagebox.showerror("Error", "Username/email already used by another user.")
            return

        self.controller.current_user = {"id": user["id"], "username": new_username, "email": new_email}
        messagebox.showinfo("Success", "Profile updated successfully!")
        self.on_show()
