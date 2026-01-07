import os
import sqlite3
import hashlib
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class DatabaseManager:

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            here = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(here, "users.db")
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            # 1) USERS TABLE
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL
                )
            """)

            # 2) LOCATIONS TABLE (global pool / "map tree")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lat REAL NOT NULL,
                    lng REAL NOT NULL,
                    continent TEXT NOT NULL,
                    country TEXT NOT NULL,
                    is_capital INTEGER DEFAULT 0,
                    added_by_user_id INTEGER,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(added_by_user_id) REFERENCES users(id)
                )
            """)

            # 3) PLAYLISTS TABLE
            conn.execute("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT
                )
            """)

            # 4) GAME SESSIONS
            conn.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    playlist_name TEXT,
                    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    ended_at TEXT,
                    total_score INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)

            # 5) GAME ROUNDS
            conn.execute("""
                CREATE TABLE IF NOT EXISTS game_rounds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    target_lat REAL NOT NULL,
                    target_lng REAL NOT NULL,
                    guess_lat REAL NOT NULL,
                    guess_lng REAL NOT NULL,
                    distance_km REAL NOT NULL,
                    score INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES game_sessions(id)
                )
            """)

            # Seed default data (idempotent)
            self._seed_initial_data(conn)
            conn.commit()

    def _seed_initial_data(self, conn):
        playlists = [
            ("The Grand Tour", "A random selection from every corner of the world."),
            ("Capital Cities", "Only capital cities from the map tree."),
            ("Turkey: All Cities", "Explore the diverse geography of Turkey."),
            ("Continent: Europe", "Focus on the European continent."),
            ("Continent: Asia", "Giant cities of the Asian continent."),
            ("Metropolises", "Huge cities that are not necessarily capitals.")
        ]
        conn.executemany("INSERT OR IGNORE INTO playlists (name, description) VALUES (?, ?)", playlists)

    # -------------------- USER OPERATIONS --------------------

    def add_user(self, username, password, email) -> bool:
        try:
            with self._connect() as conn:
                conn.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                             (username.strip(), email.strip(), _hash_password(password)))
                conn.commit()
            return True
        except sqlite3.IntegrityError: return False

    def verify_user(self, username, password) -> Optional[Dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?",
                               (username.strip(), _hash_password(password))).fetchone()
        return dict(row) if row else None

    def update_user(self, user_id, username, email) -> bool:
        try:
            with self._connect() as conn:
                conn.execute("UPDATE users SET username = ?, email = ? WHERE id = ?", (username, email, user_id))
                conn.commit()
            return True
        except sqlite3.IntegrityError: return False

    # -------------------- LOCATION POOL & PLAYLIST OPERATIONS --------------------

    def add_location(self, lat, lng, continent, country, is_capital, user_id) -> bool:
        try:
            with self._connect() as conn:
                conn.execute("""
                    INSERT INTO locations (lat, lng, continent, country, is_capital, added_by_user_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (lat, lng, continent, country, 1 if is_capital else 0, user_id))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error adding location: {e}")
            return False

    def get_all_playlists(self) -> List[str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT name FROM playlists").fetchall()
            return [row["name"] for row in rows]

    def get_locations_for_playlist(self, playlist_name: str) -> list:
        query = "SELECT lat, lng FROM locations"
        params = []

        if playlist_name == "The Grand Tour":
            pass 
        elif playlist_name == "Capital Cities":
            query += " WHERE is_capital = 1"
        elif playlist_name == "Turkey: All Cities":
            query += " WHERE country = ?"
            params.append("Turkey")
        elif "Continent:" in playlist_name:
            cont = playlist_name.split(": ")[1]
            query += " WHERE continent = ?"
            params.append(cont)
        elif playlist_name == "Metropolises":
            query += " WHERE is_capital = 0"
        
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            # If the selected filter returns no rows, fall back to the full pool to keep the game runnable
            if not rows:
                rows = conn.execute("SELECT lat, lng FROM locations").fetchall()
            return [(row["lat"], row["lng"]) for row in rows]

    # -------------------- GAME STATISTICS --------------------

    def get_leaderboard(self, limit=10) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT u.username, s.total_score, s.playlist_name, s.ended_at
                FROM game_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.ended_at IS NOT NULL
                ORDER BY s.total_score DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]

    def start_session(self, user_id, playlist_name="World Spotlight") -> int:
        with self._connect() as conn:
            cur = conn.execute("INSERT INTO game_sessions (user_id, playlist_name) VALUES (?, ?)", (user_id, playlist_name))
            conn.commit()
            return cur.lastrowid

    def add_round(self, session_id, t_lat, t_lng, g_lat, g_lng, dist, score):
        with self._connect() as conn:
            conn.execute("INSERT INTO game_rounds (session_id, target_lat, target_lng, guess_lat, guess_lng, distance_km, score) VALUES (?,?,?,?,?,?,?)",
                         (session_id, t_lat, t_lng, g_lat, g_lng, dist, score))
            conn.execute("UPDATE game_sessions SET total_score = total_score + ? WHERE id = ?", (score, session_id))
            conn.commit()

    def end_session(self, session_id):
        with self._connect() as conn:
            conn.execute("UPDATE game_sessions SET ended_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
            conn.commit()

    def get_user_stats(self, user_id) -> Dict:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT COUNT(*) as games_played, COALESCE(SUM(total_score), 0) as total_score, COALESCE(MAX(total_score), 0) as best_score
                FROM game_sessions WHERE user_id = ? AND ended_at IS NOT NULL
            """, (user_id,)).fetchone()
        return dict(row)