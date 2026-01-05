import customtkinter as ctk
from database.db_manager import DatabaseManager


class LeaderboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = DatabaseManager()

        self.grid_columnconfigure(0, weight=1)

        # Header
        self.title_label = ctk.CTkLabel(
            self,
            text="🏆 TOP SCORES",
            font=("Impact", 40, "bold"),
            fg_color=("#3B8ED0", "#1F6AA5"),
            text_color="white",
            corner_radius=12,
        )
        self.title_label.pack(pady=(30, 20), padx=20, fill="x")

        # Table area
        self.table_frame = ctk.CTkScrollableFrame(
            self, fg_color=("#EBF4FC", "#1A1A1A"), corner_radius=15
        )
        self.table_frame.pack(pady=10, padx=40, fill="both", expand=True)

        # Navigation
        self.back_btn = ctk.CTkButton(
            self,
            text="BACK TO HOME",
            command=lambda: controller.show_frame("HomePage"),
            font=("Impact", 18),
            height=45,
            width=250,
        )
        self.back_btn.pack(pady=20)

    def on_show(self) -> None:
        # Clear old rows
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Fetch top scores from DB
        scores = self.db.get_leaderboard()

        # Header row
        headers = ["Rank", "Player", "Score", "Map"]
        for i, header in enumerate(headers):
            lbl = ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=("Impact", 18, "bold"),
                text_color="#3B8ED0",
            )
            lbl.grid(row=0, column=i, padx=20, pady=10, sticky="nsew")

        # Data rows
        for index, row in enumerate(scores):
            rank_color = (
                "#FFD700"
                if index == 0
                else "#C0C0C0"
                if index == 1
                else "#CD7F32"
                if index == 2
                else "white"
            )

            ctk.CTkLabel(self.table_frame, text=f"#{index + 1}", text_color=rank_color).grid(
                row=index + 1, column=0, pady=5
            )
            ctk.CTkLabel(self.table_frame, text=row["username"]).grid(
                row=index + 1, column=1, pady=5
            )
            ctk.CTkLabel(
                self.table_frame, text=str(row["total_score"]), font=("Helvetica", 14, "bold")
            ).grid(row=index + 1, column=2, pady=5)
            ctk.CTkLabel(
                self.table_frame, text=row["playlist_name"], font=("Helvetica", 12, "italic")
            ).grid(row=index + 1, column=3, pady=5)
