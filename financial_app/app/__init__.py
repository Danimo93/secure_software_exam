# app/__init__.py

from flask import Flask, jsonify, request, redirect, url_for, render_template
from app.auth_controller import register, login

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Define home route
@app.route('/')
def home():
    # You can render a home page or redirect to login or register page
    return render_template('home.html')  # Make sure home.html exists in the templates folder

# Define routes for registration and login
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    return register()

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    return login()

@app.route('/dashboard')
def dashboard():
    return "<h1>Welcome to the dashboard!</h1>"
