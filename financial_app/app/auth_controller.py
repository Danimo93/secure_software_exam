import secrets
import bcrypt
from flask import request, jsonify, redirect, flash, render_template, url_for
from datetime import datetime, timedelta, timezone
from app.models import User
from flask_login import login_user, login_required, logout_user, current_user
from app import app

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Register attempt with username: {username}")
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode()
        success = User.create_user(username, password_hash)

        if success:
            # flash('User registered successfully', 'success')  # Uncomment after testing
            print("Registration successful!")
            return jsonify({'message': 'User registered successfully', 'status': 'success'}), 200
        else:
            # flash('Username already exists', 'danger')  # Uncomment after testing
            print("Registration failed: Username already exists")
            return jsonify({'message': 'Username already exists', 'status': 'error'}), 400
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_user_view():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Login attempt with username: {username}")

        user = User.find_by_username(username)
        print(f"User found: {user}")  # Debugging

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            login_user(user)
            # flash('Login successful', 'success')  # Uncomment after testing
            return jsonify({'message': 'Login successful', 'status': 'success'}), 200
        else:
            # flash('Invalid username or password', 'danger')  # Uncomment after testing
            return jsonify({'message': 'Invalid username or password', 'status': 'error'}), 400
    return render_template('login.html')


@app.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    if request.method == 'POST':
        username = request.form.get('username')
        print(f"Username from form: {username}")  # Debugging output
        user = User.find_by_username_for_reset(username)
        if not user:
            # flash('User not found', 'danger')  # Uncomment after testing
            return jsonify({'message': 'User not found', 'status': 'error'}), 404

        reset_token = secrets.token_urlsafe(32)
        print(f"Reset token generated: {reset_token}")  # Debugging

        token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        user.update_reset_token(reset_token, token_expiry)

        # flash('Password reset link generated. Redirecting...', 'info')  # Uncomment after testing
        return jsonify({
            'message': 'Password reset token generated successfully',
            'reset_token': reset_token,
            'expiry_time': token_expiry.isoformat(),
            'status': 'success'
        }), 200

    return render_template('request_reset.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.find_by_reset_token(token)
    print(f"Reset token checked for validity: {token}")  # Debugging

    # Ensure user.token_expiry is timezone-aware before comparison
    if not user or (user.token_expiry.replace(tzinfo=timezone.utc) if user.token_expiry.tzinfo is None else user.token_expiry) < datetime.now(timezone.utc):
        # flash('Invalid or expired token', 'danger')  # Uncomment after testing
        return jsonify({'message': 'Invalid or expired token', 'status': 'error'}), 400

    if request.method == 'POST':
        password = request.form.get('password')

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode()

        user.update_password(password_hash)
        user.clear_reset_token()

        # flash('Password reset successfully', 'success')  # Uncomment after testing
        return jsonify({'message': 'Password reset successfully', 'status': 'success'}), 200

    return render_template('reset_password.html', token=token)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    # flash('You have been logged out', 'info')  # Uncomment after testing
    return jsonify({'message': 'Logged out successfully', 'status': 'success'}), 200
