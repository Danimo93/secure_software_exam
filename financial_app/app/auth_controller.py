# app/auth_controller.py

import secrets
import bcrypt
from flask import request, flash, render_template, redirect, url_for
from datetime import datetime, timedelta, timezone
from app.models import User
from flask_login import login_user, logout_user, login_required, current_user
from app import app

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Register attempt username: {username}")
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode()
        success = User.create_user(username, password_hash)
        if success:
            flash('User registered', 'success')
            return redirect(url_for('login_user_view'))
        else:
            flash('Username already exists', 'danger')
            return redirect(url_for('register_user'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_user_view():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Login attempt username: {username}")
        user = User.find_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            login_user(user)
            flash('Login success', 'success')
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

        # Generate two-factor authentication code
        two_factor_code = secrets.token_hex(4)  # Generates 8-character code
        print(f"Two-factor code for {username}: {two_factor_code}")

        code_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        user.set_two_factor_code(two_factor_code, code_expiry)

        return render_template('two_factor.html', username=username)
    return render_template('request_reset.html')

@app.route('/verify_two_factor', methods=['POST'])
def verify_two_factor():
    username = request.form.get('username')
    code_entered = request.form.get('two_factor_code')

    user = User.find_by_username_for_reset(username)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('request_password_reset'))

    # Ensure user.two_factor_expiry is offset-aware (i.e., includes timezone info)
    if user.two_factor_expiry.tzinfo is None:
        # Convert to UTC if it's naive
        user.two_factor_expiry = user.two_factor_expiry.replace(tzinfo=timezone.utc)

    # Check if the two-factor code is valid
    if not user.two_factor_code or not user.two_factor_expiry or user.two_factor_expiry < datetime.now(timezone.utc):
        flash('Two-factor code expired. Please request a new password reset.', 'danger')
        return redirect(url_for('request_password_reset'))

    if code_entered != user.two_factor_code:
        flash('Invalid authentication code.', 'danger')
        return render_template('two_factor.html', username=username)

    # Code is valid; generate reset token
    reset_token = secrets.token_urlsafe(32)
    print(f"Reset token generated for {username}: {reset_token}")

    token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    user.update_reset_token(reset_token, token_expiry)
    user.clear_two_factor_code()

    return redirect(url_for('reset_password_route', token=reset_token))

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.find_by_reset_token(token)
    if not user or (user.token_expiry.replace(tzinfo=timezone.utc) if user.token_expiry.tzinfo is None else user.token_expiry) < datetime.now(timezone.utc):
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('request_password_reset'))

    if request.method == 'POST':
        password = request.form.get('password')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode()
        user.update_password(password_hash)
        user.clear_reset_token()
        flash('Password reset success', 'success')
        return redirect(url_for('login_user_view'))
    return render_template('reset_password.html', token=token)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('login_user_view'))