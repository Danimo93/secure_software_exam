# app/__init__.py

import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
app = Flask(__name__)
app.secret_key = 'secretkey'

project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db_path = os.path.join(project_dir, 'database', 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])

db_folder = os.path.join(project_dir, 'database')
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

db.init_app(app)

with app.app_context():
    if not os.path.exists(db_path):
        print("Database file not found, creating the database...")
        db.create_all()
        print("Database created!")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"Created uploads folder at: {UPLOAD_FOLDER}")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_user_route'

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.find_by_id(user_id)

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
    
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_route(token):
    return reset_password(token)

@app.route('/download/<filename>', methods=['GET'])
@login_required
def download_selected_file_route(filename):
    return download_selected_file(filename)

with app.app_context():
    db.create_all()