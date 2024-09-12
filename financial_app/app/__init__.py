# app/__init__.py

import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy (no app binding yet)
db = SQLAlchemy()

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Set the database URI with an absolute path to ensure it points to the database/ directory outside app/
project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db_path = os.path.join(project_dir, 'database', 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Print the database URI to verify it's correct
print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])

# Ensure the 'database' directory exists outside the app directory
db_folder = os.path.join(project_dir, 'database')
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# Initialize SQLAlchemy with the app (this ensures the app is registered with SQLAlchemy)
db.init_app(app)

# Check if the database file exists; otherwise, create one using db.create_all()
with app.app_context():
    if not os.path.exists(db_path):
        print("Database file not found, creating the database...")
        db.create_all()
        print("Database created!")

# Ensure the upload folder exists inside the 'app' directory
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"Created uploads folder at: {UPLOAD_FOLDER}")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_user_route'

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.find_by_id(user_id)

# Define routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout_route():
    logout_user()  
    flash('Logged out', 'info')
    return redirect(url_for('login_user_route'))

# Import routes from controllers
from app.auth_controller import register_user, login_user_view, request_password_reset, reset_password, logout
from app.api_controller import protected_resource
from app.file_controller import upload_file, list_files, download_selected_file

@app.route('/register', methods=['GET', 'POST'])
def register_user_route():
    return register_user()

@app.route('/login', methods=['GET', 'POST'])
def login_user_route():
    return login_user_view()

@app.route('/request-reset', methods=['GET', 'POST'])
def request_password_reset_route():
    return request_password_reset()

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_route(token):
    return reset_password(token)

@app.route('/api/protected', methods=['GET'])
def protected_resource_route():
    return protected_resource()

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file_route():
    return upload_file()

@app.route('/download', methods=['GET'])  
@login_required
def list_files_route():
    return list_files()

@app.route('/download/<filename>', methods=['GET'])
@login_required
def download_selected_file_route(filename):
    return download_selected_file(filename)

# Create all database tables if they don't exist
with app.app_context():
    db.create_all()