# main.py

from app import app
from app.db_setup import create_tables

if __name__ == "__main__":
    # Call create_tables() before running the app to ensure the database is initialized
    create_tables()
    app.run(debug=True)
