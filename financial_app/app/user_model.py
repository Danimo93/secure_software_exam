# app/user_model.py

import sqlite3
import bcrypt
from app.db_setup import connect_db

class User:
    @staticmethod
    def create_user(username, password):
        salt = bcrypt.gensalt().decode()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode()
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                           (username, password_hash, salt))
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
        cursor.execute("SELECT password_hash, salt FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result is None:
            return False
        
        stored_hash, salt = result
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True
        return False
