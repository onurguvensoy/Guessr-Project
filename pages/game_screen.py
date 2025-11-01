import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
import io
import math
from database.db_manager import DatabaseManager

class GameScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#4B0082')
        self.controller = controller
        self.db = DatabaseManager()
        self.current_round = 1
        self.total_score = 0
        self.TOTAL_ROUNDS = 5
        
        # API Keys (replace with your actual keys)
        self.STREET_VIEW_KEY = "AIzaSyCdSDsJTF4IeUKY8QKgoKrVqSRol0HJg1w"
        self.MAPS_KEY = "AIzaSyCdSDsJTF4IeUKY8QKgoKrVqSRol0HJg1w"

        # Game layout
        self.setup_layout()
        self.setup_street_view()
        self.setup_map()
        self.setup_game_info()

    def setup_layout(self):
        # Main frame for street view
        self.street_view_frame = tk.Frame(self, bg='black', width=600, height=400)
        self.street_view_frame.pack(pady=20)
        self.street_view_frame.pack_propagate(False)

        # Mini-map frame (starts small, expands on hover)
        self.map_frame = tk.Frame(self, bg='white', width=200, height=200)
        self.map_frame.pack(side='right', padx=20, pady=20)
        self.map_frame.pack_propagate(False)

        # Game info frame
        self.info_frame = tk.Frame(self, bg='#4B0082')
        self.info_frame.pack(side='left', padx=20)

    def setup_street_view(self):
        # Example location (will be random in actual game)
        location = self.get_random_location()
        
        # Get Street View image
        url = f"https://maps.googleapis.com/maps/api/streetview?size=600x400&location={location['lat']},{location['lng']}&key={self.STREET_VIEW_KEY}"
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content))
        photo = ImageTk.PhotoImage(img)
        
        self.street_view_label = tk.Label(self.street_view_frame, image=photo)
        self.street_view_label.image = photo
        self.street_view_label.pack()

    def setup_map(self):
        # Initialize map with click handler
        self.map_canvas = tk.Canvas(self.map_frame, width=200, height=200)
        self.map_canvas.pack()

        # Load and display world map image
        # You'll need to implement actual Google Maps integration here
        
        # Bind hover events for map expansion
        self.map_frame.bind('<Enter>', self.expand_map)
        self.map_frame.bind('<Leave>', self.shrink_map)
        self.map_canvas.bind('<Button-1>', self.handle_guess)

    def setup_game_info(self):
        self.round_label = tk.Label(
            self.info_frame,
            text=f"Round: {self.current_round}/{self.TOTAL_ROUNDS}",
            font=('Impact', 16),
            bg='#4B0082',
            fg='white'
        )
        self.round_label.pack(pady=5)

        self.score_label = tk.Label(
            self.info_frame,
            text=f"Score: {self.total_score}",
            font=('Impact', 16),
            bg='#4B0082',
            fg='white'
        )
        self.score_label.pack(pady=5)

    def expand_map(self, event):
        self.map_frame.configure(width=400, height=400)
        # Update map display

    def shrink_map(self, event):
        self.map_frame.configure(width=200, height=200)
        # Update map display

    def handle_guess(self, event):
        # Convert click coordinates to lat/lng
        guessed_lat, guessed_lng = self.convert_click_to_coordinates(event.x, event.y)
        
        # Calculate distance and score
        distance = self.calculate_distance(
            guessed_lat, guessed_lng,
            self.current_location['lat'],
            self.current_location['lng']
        )
        
        round_score = self.calculate_score(distance)
        self.total_score += round_score

        # Show result dialog
        self.show_round_result(distance, round_score)

        # Move to next round or end game
        if self.current_round < self.TOTAL_ROUNDS:
            self.current_round += 1
            self.start_new_round()
        else:
            self.end_game()

    def get_random_location(self):
        # Get random location from database
        return {'lat': 0, 'lng': 0}  # Placeholder

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        # Haversine formula for distance calculation
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def calculate_score(self, distance):
        # Score calculation based on distance
        max_score = 5000
        if distance < 1:
            return max_score
        return int(max_score * math.exp(-distance/2000))

    def show_round_result(self, distance, score):
        # Show dialog with round results
        pass

    def start_new_round(self):
        # Update UI for new round
        self.current_location = self.get_random_location()
        self.setup_street_view()
        self.round_label.config(text=f"Round: {self.current_round}/{self.TOTAL_ROUNDS}")
        self.score_label.config(text=f"Score: {self.total_score}")

    def end_game(self):
        # Save score and show final results
        self.db.save_score(self.controller.current_user, self.total_score)
        # Show final score dialog
        self.controller.show_frame("LobbyScreen")
