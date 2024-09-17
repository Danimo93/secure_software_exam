# app/api_controller.py

from flask import request, jsonify
from datetime import datetime, timedelta
from app.models import User
from app import db, app
import secrets
from flask_login import login_required ## Commented out If you're gonna use Postman

def protected_resource():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token is missing'}), 400
    user = User.query.filter_by(api_token=token).first()
    if not user:
        return jsonify({'error': 'Unauthorized access: invalid token'}), 403
    if user.api_token_expiry < datetime.utcnow():
        return jsonify({'error': 'Token has expired'}), 403
    return jsonify({'message': 'You have accessed a protected resource'}), 200

def get_user_info():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token is missing'}), 400
    user = User.query.filter_by(api_token=token).first()
    if not user:
        return jsonify({'error': 'Unauthorized access: invalid token'}), 403
    if user.api_token_expiry < datetime.utcnow():
        return jsonify({'error': 'Token has expired'}), 403
    return jsonify({
        'username': user.username,
        'message': 'User information retrieved successfully'
    }), 200

def update_token(user_id):
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    token = secrets.token_hex(16)
    expiry_time = datetime.utcnow() + timedelta(hours=1)
    user.update_token(token, expiry_time)
    return jsonify({
        'message': 'Token updated successfully',
        'api_token': token,
        'expiry_time': expiry_time.isoformat()
    }), 200

def clear_token(user_id):
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user.clear_token()
    return jsonify({'message': 'Token cleared successfully'}), 200

@app.route('/update-token/<int:user_id>', methods=['POST'])
@login_required  # Commented out If you're gonna use Postman
def update_token_route(user_id):
    return update_token(user_id)

