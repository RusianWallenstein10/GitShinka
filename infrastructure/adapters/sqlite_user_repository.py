import sqlite3
from typing import Optional
from core.ports.user_repository import UserRepository

class SqliteUserRepository(UserRepository):
    def __init__(self, db_path: str = "gitshinka.db"):
        self.db_path = db_path

    def authenticate_user(self, username: str, password: str) -> Optional[int]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        return user[0] if user else None

    def create_user(self, username: str, password: str) -> Optional[int]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            return None

    def save_github_token(self, user_id: int, token: Optional[str]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET github_token = ? WHERE id = ?", (token, user_id))
        conn.commit()
        conn.close()

    def get_github_token(self, user_id: int) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT github_token FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] else None
