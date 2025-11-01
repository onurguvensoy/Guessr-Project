import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager

db = DatabaseManager()

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#4B0082')
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
                         text="Register",
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

        tk.Label(self, text="Email:", bg='#4B0082', fg='white', font=('Impact', 14)).pack(pady=5)
        self.email_entry = tk.Entry(self)
        self.email_entry.pack(pady=5)

        tk.Label(self, text="Password:", bg='#4B0082', fg='white', font=('Impact', 14)).pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        register_button = ttk.Button(
            self,
            text="Register",
            style='Rounded.TButton',
            command=self.handle_register
        )
        register_button.pack(pady=10)

        back_button = ttk.Button(
            self,
            text="Back to Login",
            style='Rounded.TButton',
            command=lambda: controller.show_frame("LoginPage")
        )
        back_button.pack(pady=10)

    def handle_register(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not email or not password:
            messagebox.showerror("Registration Failed", "Please fill in all fields.")
            return

        if db.add_user(username, password, email):
            messagebox.showinfo("Registration Successful", "You can now log in.")
            self.controller.show_frame("LoginPage")
        else:
            messagebox.showerror("Registration Failed", "Username or email already exists.")
