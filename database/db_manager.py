import os
import sqlite3
import hashlib
from dataclasses import dataclass
from typing import Optional, Dict, Any


def _hash_password(password: str) -> str:
    # Demo için basit SHA-256. Prod için bcrypt/argon2 kullan.
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@dataclass
class User:
    id: int
    username: str
    email: str


class DatabaseManager:
    """
    SQLite user store + game stats
      - database/users.db otomatik oluşur
      - users table: username UNIQUE, email UNIQUE, password_hash
      - game_sessions: user'a bağlı oyun oturumu (toplam skor)
      - game_rounds: her tahmin (round) kaydı
    """

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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    ended_at TEXT,
                    total_score INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )

            conn.execute(
                """
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
                """
            )

            conn.commit()

    # -------------------- USERS --------------------

    def add_user(self, username: str, password: str, email: str) -> bool:
        username = username.strip()
        email = email.strip()
        if not username or not password or not email:
            return False

        pw_hash = _hash_password(password)
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, pw_hash),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        username = username.strip()
        if not username or not password:
            return None

        pw_hash = _hash_password(password)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?",
                (username, pw_hash),
            ).fetchone()
        if not row:
            return None
        return {"id": row["id"], "username": row["username"], "email": row["email"]}

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, email FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if not row:
            return None
        return {"id": row["id"], "username": row["username"], "email": row["email"]}

    def update_user(self, user_id: int, username: str, email: str) -> bool:
        username = username.strip()
        email = email.strip()
        if not username or not email:
            return False
        try:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE users SET username = ?, email = ? WHERE id = ?",
                    (username, email, user_id),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    # -------------------- GAME STATS --------------------

    def start_session(self, user_id: int) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO game_sessions (user_id) VALUES (?)",
                (user_id,),
            )
            conn.commit()
            return int(cur.lastrowid)

    def add_round(
        self,
        session_id: int,
        target_lat: float,
        target_lng: float,
        guess_lat: float,
        guess_lng: float,
        distance_km: float,
        score: int,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO game_rounds
                (session_id, target_lat, target_lng, guess_lat, guess_lng, distance_km, score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, target_lat, target_lng, guess_lat, guess_lng, distance_km, score),
            )
            conn.execute(
                "UPDATE game_sessions SET total_score = total_score + ? WHERE id = ?",
                (score, session_id),
            )
            conn.commit()

    def end_session(self, session_id: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE game_sessions SET ended_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,),
            )
            conn.commit()

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                  COUNT(*) AS games_played,
                  COALESCE(SUM(total_score), 0) AS total_score,
                  COALESCE(MAX(total_score), 0) AS best_score
                FROM game_sessions
                WHERE user_id = ? AND ended_at IS NOT NULL
                """,
                (user_id,),
            ).fetchone()
        return {
            "games_played": int(row["games_played"]),
            "total_score": int(row["total_score"]),
            "best_score": int(row["best_score"]),
        }
