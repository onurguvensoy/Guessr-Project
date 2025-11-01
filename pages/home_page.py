import tkinter as tk
from tkinter import ttk


class HomePage(tk.Frame):
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

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        title_label = tk.Label(
            self,
            text="GEOGUESSER!",
            font=("Impact", 36, "bold"),
            bg='#9370DB',
            fg='white',
            bd=0,
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        title_label.grid(row=1, column=1, pady=30, sticky="ew")

        button_width = 20

        style.configure('Soft.TButton', font=("Impact", 18), background='white', foreground='black',
                        padding=15, borderwidth=0, relief="flat", focusthickness=0)
        style.map('Soft.TButton', foreground=[('disabled', 'gray'), ('active', 'black')],
                  background=[('disabled', '#E0E0E0'), ('active', '#CCCCCC')],
                  relief=[('pressed', 'groove'), ('!pressed', 'flat')])

        login_button = ttk.Button(self, text="LOGIN",
                                  command=lambda: controller.show_frame("LoginPage"),
                                  style='Rounded.TButton', width=button_width)
        login_button.grid(row=2, column=1, pady=15)

        register_button = ttk.Button(self, text="REGISTER",
                                     command=lambda: controller.show_frame("RegisterPage"),
                                     style='Rounded.TButton', width=button_width)
        register_button.grid(row=3, column=1, pady=15)

        settings_button = ttk.Button(self, text="SETTINGS",
                                     command=lambda: controller.show_frame("SettingsPage"),
                                     style='Rounded.TButton', width=button_width)
        settings_button.grid(row=4, column=1, pady=15)

        exit_button = ttk.Button(self, text="PULL THE PLUG (EXIT)",
                                 command=controller.quit,
                                 style='Rounded.TButton', width=button_width + 5)
        exit_button.grid(row=5, column=1, pady=40)
