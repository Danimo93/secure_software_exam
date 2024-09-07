# app/__init__.py

from flask import Flask, render_template
from app.auth_controller import register_user, login_user, request_password_reset, reset_password
from app.api_controller import protected_resource

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Define routes

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register_user_route():
    return register_user()

@app.route('/login', methods=['GET', 'POST'])
def login_user_route():
    return login_user()

@app.route('/request-reset', methods=['GET', 'POST'])
def request_password_reset_route():
    return request_password_reset()

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_route(token):
    return reset_password(token)

# Move the API route definition here to avoid circular imports
@app.route('/api/protected', methods=['GET'])
def protected_resource_route():
    return protected_resource()
