import os
import sqlite3
import hashlib
from dataclasses import dataclass
from typing import Optional, Dict, Any


def _hash_password(password: str) -> str:
    # Simple SHA-256 hashing (ok for a small demo app). For production use a slow KDF (bcrypt/argon2).
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@dataclass
class User:
    id: int
    username: str
    email: str


class DatabaseManager:
    """
    Minimal SQLite user store:
      - Creates database/users.db automatically
      - users table: username UNIQUE, email UNIQUE, password_hash
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
            conn.commit()

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
            # username/email already used by another user
            return False
