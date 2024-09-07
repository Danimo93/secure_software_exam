# app/auth_controller.py

import secrets
import bcrypt
from flask import request, jsonify, redirect, flash, render_template, url_for
from datetime import datetime, timedelta
from app.models import User

# User Registration
def register_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Hash the password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode()

        # Store user in the database
        success = User.create_user(username, email, password_hash)
        if success:
            flash('User registered successfully', 'success')
            return redirect(url_for('login_user'))
        else:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('register_user'))

    return render_template('register.html')

# User Login
def login_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Find the user by username
        user = User.find_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # Generate API token
            token = secrets.token_urlsafe(32)
            user.update_token(token)
            flash('Login successful', 'success')
            return jsonify({'api_token': token})  # Return the token for API usage
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login_user'))

    return render_template('login.html')

# Request Password Reset
def request_password_reset():
    if request.method == 'POST':
        email_or_username = request.form.get('email')

        # Find user by email or username
        user = User.find_by_email_or_username(email_or_username)
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('request_password_reset_route'))

        # Generate secure reset token
        reset_token = secrets.token_urlsafe(32)
        token_expiry = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour

        # Store the token and expiry in the database
        user.update_reset_token(reset_token, token_expiry)

        # For simplicity, print token to console (normally, you'd email this)
        print(f"Password reset token for {user.username}: {reset_token}")

        flash('Password reset link has been sent to your email', 'info')
        return redirect(url_for('login_user'))

    return render_template('request_reset.html')

# Reset Password
def reset_password(token):
    user = User.find_by_reset_token(token)
    if not user or user.token_expiry < datetime.utcnow():
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('request_password_reset_route'))

    if request.method == 'POST':
        password = request.form.get('password')

        # Hash the new password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode()

        # Update user's password and clear the reset token
        user.update_password(password_hash)
        user.clear_reset_token()

        flash('Password reset successfully', 'success')
        return redirect(url_for('login_user'))

    return render_template('reset_password.html', token=token)
