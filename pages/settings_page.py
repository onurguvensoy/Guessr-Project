import tkinter as tk
from tkinter import ttk


class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#4B0082')
        self.controller = controller

        style = ttk.Style()

        style.element_create("RoundedFrame", "from", "clam")
        style.layout("Rounded.TButton",
                     [('Button.focus',
                       {'children': [('Button.padding',
                                      {'children': [('Button.label', {'sticky': 'nswe'})],
                                       'sticky': 'nswe'})],
                        'sticky': 'nswe'})])

        style.configure('Rounded.TButton',
                        font=("Impact", 16),
                        background='#9370DB',
                        foreground='white',
                        padding=10,
                        borderwidth=0,
                        relief="flat",
                        focusthickness=0)

        style.map('Rounded.TButton',
                  foreground=[('disabled', '#AAAAAA'), ('active', 'white')],
                  background=[('disabled', '#6A0DAD'), ('active', '#B57EDC')],
                  relief=[('pressed', 'flat'), ('!pressed', 'flat')])

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(11, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        title_label = tk.Label(
            self,
            text="SETTINGS",
            font=("Impact", 28, "bold"),
            bg='#9370DB',
            fg='white',
            bd=0,
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        title_label.grid(row=1, column=1, pady=20, sticky="ew")

        section_font = ("Impact", 18)
        radio_font = ("Impact", 16)

        # LANGUAGE
        language_label = tk.Label(self, text="LANGUAGE", font=section_font, bg='#4B0082', fg='white')
        language_label.grid(row=2, column=1, pady=10)

        self.language_var = tk.StringVar(value="English")
        language_frame = tk.Frame(self, bg='#4B0082')
        language_frame.grid(row=3, column=1, pady=5)

        tk.Radiobutton(language_frame, text="ENGLISH 🇺🇸", variable=self.language_var, value="English",
                       font=radio_font, bg='#4B0082', fg='white', selectcolor='#9370DB',
                       activebackground='#4B0082', activeforeground='white').pack(side="left", padx=15)

        tk.Radiobutton(language_frame, text="TÜRKÇE 🇹🇷", variable=self.language_var, value="Turkish",
                       font=radio_font, bg='#4B0082', fg='white', selectcolor='#9370DB',
                       activebackground='#4B0082', activeforeground='white').pack(side="left", padx=15)

        # DARK MODE
        dark_label = tk.Label(self, text="DARK MODE", font=section_font, bg='#4B0082', fg='white')
        dark_label.grid(row=4, column=1, pady=10)

        self.darkmode_var = tk.StringVar(value="No")
        dark_frame = tk.Frame(self, bg='#4B0082')
        dark_frame.grid(row=5, column=1, pady=5)

        tk.Radiobutton(dark_frame, text="YES", variable=self.darkmode_var, value="Yes",
                       font=radio_font, bg='#4B0082', fg='white', selectcolor='#9370DB',
                       activebackground='#4B0082', activeforeground='white').pack(side="left", padx=15)

        tk.Radiobutton(dark_frame, text="NO", variable=self.darkmode_var, value="No",
                       font=radio_font, bg='#4B0082', fg='white', selectcolor='#9370DB',
                       activebackground='#4B0082', activeforeground='white').pack(side="left", padx=15)

        # MUSIC
        music_label = tk.Label(self, text="MUSIC", font=section_font, bg='#4B0082', fg='white')
        music_label.grid(row=6, column=1, pady=10)

        self.music_var = tk.StringVar(value="On")
        music_frame = tk.Frame(self, bg='#4B0082')
        music_frame.grid(row=7, column=1, pady=5)

        tk.Radiobutton(music_frame, text="ON", variable=self.music_var, value="On",
                       font=radio_font, bg='#4B0082', fg='white', selectcolor='#9370DB',
                       activebackground='#4B0082', activeforeground='white').pack(side="left", padx=15)

        tk.Radiobutton(music_frame, text="OFF", variable=self.music_var, value="Off",
                       font=radio_font, bg='#4B0082', fg='white', selectcolor='#9370DB',
                       activebackground='#4B0082', activeforeground='white').pack(side="left", padx=15)

        # SOUND EFFECTS
        sfx_label = tk.Label(self, text="SOUND EFFECTS", font=section_font, bg='#4B0082', fg='white')
        sfx_label.grid(row=8, column=1, pady=10)

        self.sfx_var = tk.StringVar(value="On")
        sfx_frame = tk.Frame(self, bg='#4B0082')
        sfx_frame.grid(row=9, column=1, pady=5)

        tk.Radiobutton(sfx_frame, text="ON", variable=self.sfx_var, value="On",
                       font=radio_font, bg='#4B0082', fg='white', selectcolor='#9370DB',
                       activebackground='#4B0082', activeforeground='white').pack(side="left", padx=15)

        tk.Radiobutton(sfx_frame, text="OFF", variable=self.sfx_var, value="Off",
                       font=radio_font, bg='#4B0082', fg='white', selectcolor='#9370DB',
                       activebackground='#4B0082', activeforeground='white').pack(side="left", padx=15)

        # BACK BUTTON
        back_button = ttk.Button(self, text="BACK",
                                 command=lambda: controller.show_frame("HomePage"),
                                 style='Rounded.TButton', width=18)
        back_button.grid(row=10, column=1, pady=25)
