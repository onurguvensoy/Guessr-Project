# client/ui/game_screen.py
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
from client.utils.constants import API_KEY

class GameScreen:
    def __init__(self, root, username, client_socket, room_id, navigate):
        self.root = root
        self.username = username
        self.client = client_socket
        self.room_id = room_id
        self.navigate = navigate

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        # UI
        self.header = tk.Label(self.frame, text=f"Room: {room_id} | Player: {username}", font=("Arial", 14))
        self.header.pack(pady=6)

        self.canvas = tk.Canvas(self.frame, width=800, height=450, bg="black")
        self.canvas.pack(padx=10, pady=10)

        # map thumbnail bottom-right
        self.map_thumb_label = tk.Label(self.frame)
        self.map_thumb_label.place(relx=0.75, rely=0.65)

        # guess controls
        controls = tk.Frame(self.frame)
        controls.pack(pady=8)
        tk.Label(controls, text="Guess Lat:").grid(row=0, column=0)
        self.lat_ent = tk.Entry(controls, width=12)
        self.lat_ent.grid(row=0, column=1, padx=4)
        tk.Label(controls, text="Lon:").grid(row=0, column=2)
        self.lon_ent = tk.Entry(controls, width=12)
        self.lon_ent.grid(row=0, column=3, padx=4)
        tk.Button(controls, text="Submit Guess", command=self.submit_guess).grid(row=0, column=4, padx=8)

        self.info_label = tk.Label(self.frame, text="Waiting for round...", font=("Arial", 12))
        self.info_label.pack(pady=6)

        # bind socket callbacks
        self.client.on("new_round", self.on_new_round)
        self.client.on("player_guessed", self.on_player_guessed)
        self.client.on("round_result", self.on_round_result)
        self.client.on("game_over", self.on_game_over)

        self.current_coords = None
        self.photo = None
        self.map_photo = None

    # ----------------- Socket event handlers -----------------
    def on_new_round(self, payload):
        # payload: {'round':.., 'multiplier':.., 'coords':{name,lat,lon}}
        coords = payload.get("coords")
        rnd = payload.get("round")
        mult = payload.get("multiplier")
        self.current_coords = coords
        self.info_label.config(text=f"Round {rnd} — multiplier {mult}")
        lat = coords.get("lat")
        lon = coords.get("lon")
        # fetch street view image in background
        threading.Thread(target=self.load_street_view, args=(lat, lon), daemon=True).start()
        threading.Thread(target=self.load_map_thumb, args=(lat, lon), daemon=True).start()

    def on_player_guessed(self, payload):
        username = payload.get("username")
        self.info_label.config(text=f"{username} has submitted a guess...")

    def on_round_result(self, payload):
        results = payload.get("results", [])
        coords = payload.get("coords", {})
        # show results in popup
        txt = f"Correct location: {coords.get('name')} ({coords.get('lat')}, {coords.get('lon')})\n\n"
        for r in results:
            txt += f"{r['username']}: dist {r['dist_km']} km, damage {r['damage']}, new score {r['new_score']}\n"
        messagebox.showinfo("Round Results", txt)
        self.info_label.config(text="Round finished. Waiting for next round...")

    def on_game_over(self, payload):
        winner = payload.get("winner")
        if winner:
            messagebox.showinfo("Game Over", f"Winner: {winner}")
        else:
            messagebox.showinfo("Game Over", "No winner.")
        # return to lobby
        self.navigate("lobby", username=self.username)

    # ----------------- Image loaders -----------------
    def load_street_view(self, lat, lon):
        try:
            url = f"https://maps.googleapis.com/maps/api/streetview?size=800x450&location={lat},{lon}&fov=90&heading=0&pitch=0&key={API_KEY}"
            resp = requests.get(url, timeout=15)
            img = Image.open(BytesIO(resp.content))
            self.photo = ImageTk.PhotoImage(img)
            # draw on canvas in main thread
            self.canvas.after(0, lambda: self.canvas.create_image(0,0, anchor='nw', image=self.photo))
        except Exception as e:
            print("StreetView load error:", e)

    def load_map_thumb(self, lat, lon):
        try:
            url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=14&size=200x120&key={API_KEY}"
            resp = requests.get(url, timeout=10)
            img = Image.open(BytesIO(resp.content))
            self.map_photo = ImageTk.PhotoImage(img)
            self.map_thumb_label.after(0, lambda: self.map_thumb_label.configure(image=self.map_photo))
            # bind hover to enlarge
            def on_enter(e):
                top = tk.Toplevel(self.root)
                top.title("Map")
                top.geometry("600x360")
                try:
                    url_big = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=14&size=600x360&key={API_KEY}"
                    resp2 = requests.get(url_big, timeout=10)
                    img2 = Image.open(BytesIO(resp2.content))
                    img2 = ImageTk.PhotoImage(img2)
                    lbl = tk.Label(top, image=img2)
                    lbl.image = img2
                    lbl.pack()
                except Exception as ex:
                    tk.Label(top, text="Map load error").pack()
            self.map_thumb_label.bind("<Enter>", on_enter)
        except Exception as e:
            print("Map thumb load error:", e)

    # ----------------- Guessing -----------------
    def submit_guess(self):
        try:
            lat = float(self.lat_ent.get().strip())
            lon = float(self.lon_ent.get().strip())
        except Exception:
            messagebox.showerror("Error", "Invalid lat/lon format.")
            return
        # validate ranges
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            messagebox.showerror("Error", "Latitude must be -90..90 and longitude -180..180.")
            return
        # send to server
        self.client.send("submit_guess", {"room_id": self.room_id, "lat": lat, "lon": lon, "username": self.username})
        self.info_label.config(text="You submitted a guess. Waiting for results...")
