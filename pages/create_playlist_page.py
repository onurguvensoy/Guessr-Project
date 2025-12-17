import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager

class CreatePlaylistPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = DatabaseManager()

        self.grid_columnconfigure(0, weight=1)

        # --- BAŞLIK ---
        self.title_label = ctk.CTkLabel(
            self, text="CONTRIBUTE TO GLOBAL MAP", 
            font=("Impact", 35, "bold"), 
            fg_color=("#3B8ED0", "#1F6AA5"), 
            text_color="white", 
            corner_radius=12
        )
        self.title_label.pack(pady=(30, 20), padx=20, fill="x")

        # --- FORM ALANI ---
        self.form_frame = ctk.CTkFrame(self, fg_color=("#EBF4FC", "#1A1A1A"), corner_radius=15)
        self.form_frame.pack(pady=10, padx=60, fill="both", expand=True)

        # Giriş Alanları
        self.lat_entry = self.create_input("Latitude (ex: 41.0082)")
        self.lng_entry = self.create_input("Longitude (ex: 28.9784)")
        self.cont_entry = self.create_input("Continent (ex: Europe)")
        self.country_entry = self.create_input("Country (ex: Turkey)")

        # Başkent mi? (Switch)
        self.cap_var = ctk.BooleanVar(value=False)
        self.cap_switch = ctk.CTkSwitch(
            self.form_frame, 
            text="Is this a Capital City?", 
            variable=self.cap_var, 
            font=("Impact", 16),
            progress_color=("#3B8ED0", "#1F6AA5")
        )
        self.cap_switch.pack(pady=15)

        # --- AKSİYON BUTONLARI (Mavi Tema) ---
        self.save_btn = ctk.CTkButton(
            self, text="SAVE TO DATABASE", 
            command=self.save_location,
            font=("Impact", 22), 
            fg_color=("#3B8ED0", "#1F6AA5"), 
            hover_color=("#1F6AA5", "#144870"), 
            height=55, 
            width=300
        )
        self.save_btn.pack(pady=15)

        self.back_btn = ctk.CTkButton(
            self, text="BACK TO LOBBY", 
            command=lambda: controller.show_frame("LobbyScreen"),
            fg_color="gray", 
            height=40, 
            width=200
        )
        self.back_btn.pack(pady=5)

    def create_input(self, placeholder):
        entry = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text=placeholder, 
            width=350, 
            height=40,
            border_color=("#3B8ED0", "#1F6AA5")
        )
        entry.pack(pady=10)
        return entry

    def save_location(self):
        """Kullanıcı verilerini DB'ye kaydeder."""
        user = getattr(self.controller, "current_user", None)
        if not user:
            messagebox.showerror("Error", "You must be logged in to contribute.")
            return

        try:
            # Verileri topla
            lat = float(self.lat_entry.get())
            lng = float(self.lng_entry.get())
            continent = self.cont_entry.get().strip()
            country = self.country_entry.get().strip()
            is_capital = self.cap_var.get()

            if not continent or not country:
                raise ValueError("Continent and Country cannot be empty.")

            success = self.db.add_location(lat, lng, continent, country, is_capital, user["id"])
            
            if success:
                self.controller.sound_manager.play_click_sfx()
                messagebox.showinfo("Success", "Location added to the Global Map Tree!")
                # Alanları temizle
                for entry in [self.lat_entry, self.lng_entry, self.cont_entry, self.country_entry]:
                    entry.delete(0, 'end')
                self.controller.show_frame("LobbyScreen")
            else:
                messagebox.showerror("Error", "Database error occurred.")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid Input: {e}")