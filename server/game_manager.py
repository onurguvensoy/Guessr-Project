# server/game_manager.py
import json
import random
import time
import threading
import math

# Basit koordinat listesi — gerektiğinde genişlet
SAMPLE_LOCATIONS = [
    {"name": "Eiffel Tower, Paris", "lat": 48.8584, "lon": 2.2945},
    {"name": "Times Square, New York", "lat": 40.7580, "lon": -73.9855},
    {"name": "Shibuya Crossing, Tokyo", "lat": 35.6595, "lon": 139.7005},
    {"name": "Colosseum, Rome", "lat": 41.8902, "lon": 12.4922},
    {"name": "Brandenburg Gate, Berlin", "lat": 52.5163, "lon": 13.3777},
]

def haversine(lat1, lon1, lat2, lon2):
    # km
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

class GameManager:
    def __init__(self):
        # rooms: room_id -> {
        #   "players": {conn: {"username": str, "score": int, "guessed": bool}},
        #   "state": "waiting"/"playing"/"finished",
        #   "current_round": int,
        #   "coords": {...},
        #   "guesses": {conn: {"lat":..., "lon":..., "time":...}}
        # }
        self.rooms = {}
        self.lock = threading.Lock()

    # Utility: safe send JSON
    def send(self, conn, obj):
        try:
            msg = json.dumps(obj).encode('utf-8')
            conn.send(msg)
        except Exception:
            # ignore send errors; higher layer handles disconnects
            pass

    def broadcast(self, room_id, obj):
        with self.lock:
            room = self.rooms.get(room_id)
            if not room: return
            for conn in list(room["players"].keys()):
                self.send(conn, obj)

    def create_room(self, room_id, username, conn):
        with self.lock:
            if room_id in self.rooms:
                self.send(conn, {"action": "create_room_failed", "payload": {"reason": "Room exists"}})
                return
            self.rooms[room_id] = {
                "players": {conn: {"username": username, "score": 5000, "guessed": False}},
                "state": "waiting",
                "current_round": 0,
                "coords": None,
                "guesses": {}
            }
            self.send(conn, {"action": "create_room_ok", "payload": {"room_id": room_id}})
            self.broadcast_room_update(room_id)

    def join_room(self, room_id, username, conn):
        with self.lock:
            room = self.rooms.get(room_id)
            if not room:
                self.send(conn, {"action": "join_room_failed", "payload": {"reason": "No such room"}})
                return
            room["players"][conn] = {"username": username, "score": 5000, "guessed": False}
            self.send(conn, {"action": "join_room_ok", "payload": {"room_id": room_id}})
            self.broadcast_room_update(room_id)

    def leave_room(self, room_id, conn):
        with self.lock:
            room = self.rooms.get(room_id)
            if not room: return
            if conn in room["players"]:
                del room["players"][conn]
            # if no players left, remove room
            if not room["players"]:
                del self.rooms[room_id]
                return
            self.broadcast_room_update(room_id)

    def broadcast_room_update(self, room_id):
        room = self.rooms.get(room_id)
        if not room: return
        players = [{"username": p["username"], "score": p["score"]} for p in room["players"].values()]
        self.broadcast(room_id, {"action": "room_update", "payload": {"players": players}})

    def start_game(self, room_id):
        with self.lock:
            room = self.rooms.get(room_id)
            if not room: return
            if len(room["players"]) < 2:
                self.broadcast(room_id, {"action": "start_failed", "payload": {"reason": "Need at least 2 players"}})
                return
            room["state"] = "playing"
            room["current_round"] = 0
            # reset scores
            for p in room["players"].values():
                p["score"] = 5000
            # start game loop in background
            t = threading.Thread(target=self.game_loop, args=(room_id,), daemon=True)
            t.start()

    def game_loop(self, room_id):
        # runs until winner found or room removed
        while True:
            with self.lock:
                room = self.rooms.get(room_id)
                if not room or room["state"] != "playing":
                    break
                room["current_round"] += 1
                multiplier = 1.0 + (room["current_round"] - 1) * 0.25
                coords = random.choice(SAMPLE_LOCATIONS)
                room["coords"] = coords
                room["guesses"] = {}
                # reset guessed flags
                for p in room["players"].values():
                    p["guessed"] = False

            # send round start with coords (clients will fetch Street View)
            self.broadcast(room_id, {"action": "new_round", "payload": {
                "round": room["current_round"],
                "multiplier": multiplier,
                "coords": coords
            }})

            # wait until all players guessed or timeout
            start = time.time()
            timeout = 60  # seconds per round
            while time.time() - start < timeout:
                with self.lock:
                    room = self.rooms.get(room_id)
                    if not room:
                        return
                    if len(room["guesses"]) >= len(room["players"]):
                        break
                time.sleep(0.5)

            # evaluate guesses
            with self.lock:
                room = self.rooms.get(room_id)
                if not room:
                    return
                self.evaluate_round(room_id)

                # check for end condition: if a player's score <= 0 -> other wins
                alive = [p for p in room["players"].values() if p["score"] > 0]
                if len(alive) < 2:
                    winner = None
                    if len(alive) == 1:
                        winner = alive[0]["username"]
                    self.broadcast(room_id, {"action": "game_over", "payload": {"winner": winner}})
                    room["state"] = "finished"
                    return

            # small pause before next round
            time.sleep(2)

    def submit_guess(self, room_id, conn, lat, lon):
        with self.lock:
            room = self.rooms.get(room_id)
            if not room: return
            # record guess
            room["guesses"][conn] = {"lat": lat, "lon": lon, "time": time.time()}
            # mark guessed
            if conn in room["players"]:
                room["players"][conn]["guessed"] = True
            # notify others someone guessed
            username = room["players"][conn]["username"] if conn in room["players"] else "Unknown"
            self.broadcast(room_id, {"action": "player_guessed", "payload": {"username": username}})

    def evaluate_round(self, room_id):
        room = self.rooms.get(room_id)
        if not room: return
        coords = room.get("coords")
        multiplier = 1.0 + (room["current_round"] - 1) * 0.25
        results = []
        for conn, p in list(room["players"].items()):
            guess = room["guesses"].get(conn)
            if not guess:
                # if no guess, treat as max distance penalty (e.g. 20000 km)
                dist = 20000.0
            else:
                dist = haversine(coords["lat"], coords["lon"], guess["lat"], guess["lon"])
            damage = int(dist * 10 * multiplier)
            p["score"] -= damage
            results.append({
                "username": p["username"],
                "dist_km": round(dist, 2),
                "damage": damage,
                "new_score": p["score"]
            })
        # broadcast round results
        self.broadcast(room_id, {"action": "round_result", "payload": {"results": results, "coords": coords}})
        # update room player list
        self.broadcast_room_update(room_id)
