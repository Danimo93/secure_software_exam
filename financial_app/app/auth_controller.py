import secrets
import bcrypt
from flask import request, redirect, flash, render_template, url_for
from datetime import datetime, timedelta, timezone
from app.models import User
from flask_login import login_user, login_required, logout_user, current_user
from app import app

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Register attempt username: {username}")

        success = User.create_user(username, password)
        if success:
            flash('User registered', 'success')
            print("Registration success!")
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

        print(f"Login attempt username: {username}")
        user = User.find_by_username(username)

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            two_factor_code = secrets.token_hex(4)
            print(f"\n---- Two-Factor Authentication ----\nKey For {username}: {two_factor_code}\n------------")

            code_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
            user.set_two_factor_code(two_factor_code, code_expiry)
            return render_template('two_factor.html', username=username, flow_type='login')
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login_user_view'))
    return render_template('login.html')

@app.route('/verify_two_factor', methods=['POST'])
def verify_two_factor():
    username = request.form.get('username')
    code_entered = request.form.get('two_factor_code')
    flow_type = request.form.get('flow_type')
    user = User.find_by_username(username)

    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('login_user_view'))

    if user.two_factor_expiry.tzinfo is None:
        user.two_factor_expiry = user.two_factor_expiry.replace(tzinfo=timezone.utc)

    if not user.two_factor_code or user.two_factor_expiry < datetime.now(timezone.utc):
        flash('Two-factor code expired. Please try again.', 'danger')
        return redirect(url_for('login_user_view'))

    if code_entered != user.two_factor_code:
        flash('Invalid authentication code.', 'danger')
        return render_template('two_factor.html', username=username, flow_type=flow_type)

    user.clear_two_factor_code()

    if flow_type == 'login':
        login_user(user)
        flash('Login success', 'success')
        return redirect(url_for('dashboard'))
        
    elif flow_type == 'reset_password':
        reset_token = secrets.token_urlsafe(32)
        token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        user.update_reset_token(reset_token, token_expiry)
        return redirect(url_for('reset_password_route', token=reset_token))

@app.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.find_by_username_for_reset(username)
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('request_password_reset'))

        two_factor_code = secrets.token_hex(4)
        print(f"\n---- Two-Factor Authentication ----\nKey For {username}: {two_factor_code}\n------------")
        code_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        user.set_two_factor_code(two_factor_code, code_expiry)

        return render_template('two_factor.html', username=username, flow_type='reset_password')
    return render_template('request_reset.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.find_by_reset_token(token)
    
    if not user:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('request_password_reset'))

    if user.token_expiry.tzinfo is None:
        user.token_expiry = user.token_expiry.replace(tzinfo=timezone.utc)

    if user.token_expiry < datetime.now(timezone.utc):
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('request_password_reset'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('reset_password.html', token=token)

        user.update_password(password)  
        user.clear_reset_token()
        flash('Password reset successful', 'success')
        return redirect(url_for('login_user_view'))

    return render_template('reset_password.html', token=token)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('login_user_view'))
