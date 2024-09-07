# app/models.py

import sqlite3
from datetime import datetime
from app.db_setup import connect_db

class User:
    @staticmethod
    def create_user(username, email, password_hash):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", 
                           (username, email, password_hash))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def find_by_username(username):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return User(*result)
        return None

    @staticmethod
    def find_by_email_or_username(email_or_username):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? OR email=?", (email_or_username, email_or_username))
        result = cursor.fetchone()
        conn.close()
        if result:
            return User(*result)
        return None

    @staticmethod
    def find_by_token(token):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE api_token=?", (token,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return User(*result)
        return None

    def update_token(self, token):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET api_token=? WHERE id=?", (token, self.id))
        conn.commit()
        conn.close()

    def update_reset_token(self, reset_token, expiry_time):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET reset_token=?, token_expiry=? WHERE id=?", (reset_token, expiry_time, self.id))
        conn.commit()
        conn.close()

    def update_password(self, new_password_hash):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash=? WHERE id=?", (new_password_hash, self.id))
        conn.commit()
        conn.close()

    def clear_reset_token(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET reset_token=NULL, token_expiry=NULL WHERE id=?", (self.id,))
        conn.commit()
        conn.close()
