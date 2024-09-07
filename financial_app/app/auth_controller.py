# app/auth_controller.py

from flask import request, jsonify, redirect, url_for, flash, render_template

def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('register_user'))

        success = User.create_user(username, password)
        if success:
            flash('User registered successfully', 'success')
            return redirect(url_for('login_user'))
        else:
            flash('Username already exists', 'danger')
            return redirect(url_for('register_user'))

    return render_template('register.html')

def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('login_user'))

        if User.verify_user(username, password):
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login_user'))

    return render_template('login.html')
