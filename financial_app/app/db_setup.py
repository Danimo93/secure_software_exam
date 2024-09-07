# app/db_setup.py

import sqlite3

DATABASE = 'secure_api.db'

def connect_db():
    return sqlite3.connect(DATABASE)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            api_token TEXT
        )
    ''')

    conn.commit()
    conn.close()