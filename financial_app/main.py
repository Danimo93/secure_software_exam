# main.py

from app import app
from app.db_setup import create_tables

if __name__ == "__main__":
    # Create the database tables if they don't exist
    create_tables()
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0')
