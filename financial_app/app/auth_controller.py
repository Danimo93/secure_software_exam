# app/auth_controller.py

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
            flash('User registered successfully', 'success')
            print("Registration successful!")
            return redirect(url_for('login_user_view'))
        else:
            flash('Username already exists', 'danger')
            print("Registration failed: Username already exists")
            return redirect(url_for('register_user'))
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
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login_user_view'))
    return render_template('login.html')


@app.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    if request.method == 'POST':
        username = request.form.get('username')

        user = User.find_by_username_for_reset(username)
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('request_password_reset'))

        reset_token = secrets.token_urlsafe(32)
        print(f"Reset token generated: {reset_token}")  # Debugging

        token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)  # Updated to use timezone-aware datetime
        user.update_reset_token(reset_token, token_expiry)

        flash('Password reset link generated. Redirecting...', 'info')

        return redirect(url_for('reset_password', token=reset_token))

    return render_template('request_reset.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.find_by_reset_token(token)
    print(f"Reset token checked for validity: {token}")  # Debugging

    if not user or user.token_expiry < datetime.now(timezone.utc):  # Updated to use timezone-aware datetime
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('request_password_reset'))

    if request.method == 'POST':
        password = request.form.get('password')

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode()

        user.update_password(password_hash)
        user.clear_reset_token()

        flash('Password reset successfully', 'success')
        return redirect(url_for('login_user_view'))

    return render_template('reset_password.html', token=token)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login_user_view'))
