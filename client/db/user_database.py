# client/db/user_database.py

import sqlite3
from pathlib import Path

class UserDatabase:
    def __init__(self, db_path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_user(self, username, password):
        try:
            self.conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def validate_user(self, username, password):
        cursor = self.conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone() is not None
