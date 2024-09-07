import secrets
import bcrypt
from flask import request, jsonify, redirect, flash, render_template, url_for
from datetime import datetime, timedelta
from app.models import User
from flask_login import login_user, login_required, logout_user, current_user
from app import app  # Assuming app is initialized in app/__init__.py
# Optional: Flask-Mail integration
from flask_mail import Message  # If using Flask-Mail (optional)

# User Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Debugging: Log received form data
        print(f"Register attempt with username: {username}, email: {email}")

        # Hash the password using bcrypt
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode()

        # Create a new user in the database
        success = User.create_user(username, email, password_hash)
        
        if success:
            flash('User registered successfully', 'success')
            print("Registration successful!")
            return redirect(url_for('login_user_view'))  # Redirect to login page
        else:
            flash('Username or email already exists', 'danger')
            print("Registration failed: Username or email already exists")
            return redirect(url_for('register_user'))  # Stay on the registration page

    return render_template('register.html')


# User Login Route
@app.route('/login', methods=['GET', 'POST'])
def login_user_view():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Debugging: Log received form data
        print(f"Login attempt with username: {username}")

        # Retrieve user by username
        user = User.find_by_username(username)
        if user:
            print(f"User found: {user.username}")
        else:
            print(f"User not found: {username}")

        # Check if the password is correct
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # Generate API token (if needed)
            token = secrets.token_urlsafe(32)
            token_expiry = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
            user.update_token(token, token_expiry)

            # Log the user in using Flask-Login
            login_user(user)
            flash('Login successful', 'success')
            print("Login successful")
            return redirect(url_for('upload_file'))  # Redirect to upload page after login
        else:
            flash('Invalid username or password', 'danger')
            print("Login failed: Invalid username or password")
            return redirect(url_for('login_user_view'))  # Redirect back to login page

    return render_template('login.html')


# Request Password Reset Route
@app.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    if request.method == 'POST':
        email_or_username = request.form.get('email')

        # Find user by email or username
        user = User.find_by_email_or_username(email_or_username)
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('request_password_reset'))

        # Generate a secure reset token
        reset_token = secrets.token_urlsafe(32)
        token_expiry = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
        user.update_reset_token(reset_token, token_expiry)

        # Optionally send the reset link via email (Flask-Mail)
        # msg = Message("Password Reset Request", sender="your_email@example.com", recipients=[user.email])
        # msg.body = f"Hi {user.username}, use the following link to reset your password: {url_for('reset_password', token=reset_token, _external=True)}"
        # mail.send(msg)

        # Debugging: Print the token to the console (replace this with email functionality in production)
        print(f"Password reset token for {user.username}: {reset_token}")

        flash('Password reset link has been sent to your email', 'info')
        return redirect(url_for('login_user_view'))  # Redirect to login after request

    return render_template('request_reset.html')


# Password Reset Route
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.find_by_reset_token(token)
    if not user or user.token_expiry < datetime.utcnow():
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('request_password_reset'))

    if request.method == 'POST':
        password = request.form.get('password')

        # Hash the new password using bcrypt
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode()

        # Update user's password and clear the reset token
        user.update_password(password_hash)
        user.clear_reset_token()

        flash('Password reset successfully', 'success')
        return redirect(url_for('login_user_view'))  # Redirect to login page after reset

    return render_template('reset_password.html', token=token)


# User Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login_user_view'))  # Redirect to login page after logout
