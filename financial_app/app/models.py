# app/models.py

import sqlite3
import bcrypt
import secrets
from app.db_setup import connect_db

class User:
    @staticmethod
    def create_user(username, password, role='user'):
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode()
        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                           (username, password_hash, role))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return False  # Username already exists
        conn.close()
        return True

    @staticmethod
    def verify_user(username, password):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result is None:
            return False

        stored_hash = result[0]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True
        return False

    @staticmethod
    def generate_token(username):
        token = secrets.token_hex(16)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET api_token=? WHERE username=?", (token, username))
        conn.commit()
        conn.close()
        return token

    @staticmethod
    def verify_token(token):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE api_token=?", (token,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    @staticmethod
    def get_user_role(token):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE api_token=?", (token,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return None
