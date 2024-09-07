from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Initialize the database object
db = SQLAlchemy()

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_user_route'  # Specify the default login route

# User loader for Flask-Login (loads user by their ID for session management)
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.find_by_id(user_id)

# Define routes
@app.route('/')
def home():
    return render_template('home.html')

# Now import your controllers after app is initialized
from app.auth_controller import register_user, login_user_view, request_password_reset, reset_password, logout
from app.api_controller import protected_resource
from app.file_controller import upload_file  # Import the upload route

# Define routes for authentication
@app.route('/register', methods=['GET', 'POST'])
def register_user_route():
    return register_user()

@app.route('/login', methods=['GET', 'POST'])
def login_user_route():
    return login_user_view()

@app.route('/logout', methods=['GET'])
def logout_route():
    return logout()

@app.route('/request-reset', methods=['GET', 'POST'])
def request_password_reset_route():
    return request_password_reset()

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_route(token):
    return reset_password(token)

# Secure API route that requires token authentication
@app.route('/api/protected', methods=['GET'])
def protected_resource_route():
    return protected_resource()

# File upload route
@app.route('/upload', methods=['GET', 'POST'])  # Define the upload file route
def upload_file_route():
    return upload_file()

# Initialize the app and database context
with app.app_context():
    db.create_all()  # Create database tables if they don't exist
