# main.py

from app import app
from app.db_setup import create_tables

if __name__ == "__main__":
    create_tables()
    # Listen on all available network interfaces (0.0.0.0) and on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
