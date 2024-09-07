# app/auth_controller.py

from flask import request, jsonify, g
from app.models import User

def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')  # Default to 'user' if no role is provided

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    success = User.create_user(username, password, role)
    if success:
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'error': 'Username already exists'}), 400

def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if User.verify_user(username, password):
        token = User.generate_token(username)
        return jsonify({'message': 'Login successful', 'api_token': token}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401
