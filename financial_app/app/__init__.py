# app/__init__.py

from flask import Flask, render_template, flash, redirect, url_for
from app.auth_controller import register, login

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Define home route to render the updated home page
@app.route('/')
def home():
    return render_template('home.html')

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
