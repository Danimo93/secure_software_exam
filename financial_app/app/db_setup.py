# app/db_setup.py

import sqlite3

DATABASE = 'users.db'

def connect_db():
    return sqlite3.connect(DATABASE)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Create users table with password reset token and expiry
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            api_token TEXT,
            reset_token TEXT,
            token_expiry TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
