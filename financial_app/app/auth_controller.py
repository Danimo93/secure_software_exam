# app/auth_controller.py

from flask import request, render_template, redirect, flash, url_for
from app.user_model import User
import logging

# Setup logging to display in the terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return redirect(url_for('register'))

        success = User.create_user(username, password)
        if success:
            logging.info(f"User {username} registered successfully")
            flash('User registered successfully', 'success')
            return redirect(url_for('login'))
        else:
            logging.warning(f"Registration failed for {username}, username already exists")
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('login'))

        if User.verify_user(username, password):
            logging.info(f"User {username} logged in successfully")
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            logging.warning(f"Failed login attempt for {username}")
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')
