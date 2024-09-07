# import sqlite3
# 
# # Function to connect to the database
# def connect_db():
#     return sqlite3.connect('users.db')
# 
# # Function to create the required tables
# def create_tables():
#     conn = connect_db()
#     cursor = conn.cursor()
# 
#     # Create users table if it does not exist
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             password_hash TEXT NOT NULL,
#             email TEXT UNIQUE NOT NULL,
#             api_token TEXT,                     -- Column for API token authentication
#             api_token_expiry TIMESTAMP,         -- Column for API token expiry
#             reset_token TEXT,                   -- Column for password reset tokens
#             token_expiry TIMESTAMP              -- Column for password reset token expiry
#         )
#     ''')
# 
#     # Create files table if it does not exist
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS files (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER NOT NULL,
#             filename TEXT NOT NULL,
#             filepath TEXT NOT NULL,
#             upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (user_id) REFERENCES users(id)
#         )
#     ''')
# 
#     conn.commit()
#     conn.close()
# 
# # Initialize the database by creating tables
# if __name__ == '__main__':
#     create_tables()
# 