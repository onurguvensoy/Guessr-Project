import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager

db = DatabaseManager()


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#4B0082')
        self.controller = controller

        style = ttk.Style()
        style.layout("Rounded.TButton",
                     [('Button.focus',
                       {'children': [('Button.padding',
                                      {'children': [('Button.label', {'sticky': 'nswe'})],
                                       'sticky': 'nswe'})],
                        'sticky': 'nswe'})])
        style.configure('Rounded.TButton',
                        font=("Impact", 18),
                        background='white',
                        foreground='black',
                        padding=15,
                        borderwidth=0,
                        relief="flat",
                        focusthickness=0,
                        anchor="center",
                        bordercolor='white')
        style.map('Rounded.TButton',
                  foreground=[('disabled', 'gray'), ('active', 'black')],
                  background=[('disabled', '#E0E0E0'), ('active', '#CCCCCC')],
                  relief=[('pressed', 'flat'), ('!pressed', 'flat')])

        title = tk.Label(self,
                         text="Login",
                         font=('Impact', 36, 'bold'),
                         bg='#9370DB',
                         fg='white',
                         bd=0,
                         relief=tk.FLAT,
                         padx=20,
                         pady=10)
        title.pack(pady=50)

        tk.Label(self, text="Username:", bg='#4B0082', fg='white', font=('Impact', 14)).pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password:", bg='#4B0082', fg='white', font=('Impact', 14)).pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        login_button = ttk.Button(
            self,
            text="Login",
            style='Rounded.TButton',
            command=self.handle_login
        )
        login_button.pack(pady=10)

        register_button = ttk.Button(
            self,
            text="Register",
            style='Rounded.TButton',
            command=lambda: controller.show_frame("RegisterPage")
        )
        register_button.pack(pady=10)

        back_button = ttk.Button(
            self,
            text="Back",
            style='Rounded.TButton',
            command=lambda: controller.show_frame("HomePage")
        )
        back_button.pack(pady=10)

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Login Failed", "Please fill in all fields.")
            return

        user = db.verify_user(username, password)
        if user:
            messagebox.showinfo("Login Successful", f"Welcome, {user['username']}!")
            self.controller.show_frame("LobbyScreen")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
