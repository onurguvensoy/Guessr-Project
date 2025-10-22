# client/ui/login_screen.py

import tkinter as tk
from tkinter import messagebox
from client.db.user_database import UserDatabase
from client.utils.constants import DB_PATH

class LoginScreen:
    def __init__(self, root, navigate):
        self.root = root
        self.navigate = navigate
        self.db = UserDatabase(DB_PATH)
        self.frame = tk.Frame(self.root)
        self.build_ui()

    def build_ui(self):
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="GeoGuessr Login", font=("Arial", 24)).pack(pady=20)

        tk.Label(self.frame, text="Username:").pack()
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.pack()

        tk.Label(self.frame, text="Password:").pack()
        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.pack()

        tk.Button(self.frame, text="Sign In", command=self.sign_in).pack(pady=10)
        tk.Button(self.frame, text="Sign Up", command=self.sign_up).pack(pady=10)

    def sign_in(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()
        if not u or not p:
            messagebox.showerror("Error", "All fields required!")
            return
        if self.db.validate_user(u, p):
            self.navigate("lobby", username=u)
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    def sign_up(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()
        if not u or not p:
            messagebox.showerror("Error", "All fields required!")
            return
        if self.db.add_user(u, p):
            messagebox.showinfo("Success", "Account created! You can now log in.")
        else:
            messagebox.showerror("Error", "Username already exists.")
