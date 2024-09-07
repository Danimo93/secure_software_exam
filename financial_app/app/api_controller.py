# app/api_controller.py

from flask import request, jsonify
from app.models import User

def protected_resource():
    token = request.headers.get('Authorization')

    # Validate the API token
    user = User.find_by_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized access'}), 403

    return jsonify({'message': 'You have accessed a protected resource'})
