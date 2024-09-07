# app/api_controller.py

from flask import request, jsonify
from app.models import User
from datetime import datetime

# Secure API route that requires a valid token and checks for token expiry
def protected_resource():
    # Extract the Authorization token from the request headers
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'error': 'Token is missing'}), 400  # Bad Request if token is missing

    # Validate the API token
    user = User.find_by_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized access: invalid token'}), 403  # Forbidden if token is invalid

    # Check if the token has expired
    if user.api_token_expiry < datetime.utcnow():
        return jsonify({'error': 'Token has expired'}), 403  # Forbidden if token has expired

    # If everything is valid, allow access to the protected resource
    return jsonify({'message': 'You have accessed a protected resource'})


# Example of a secure API route with parameters
def get_user_info():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'error': 'Token is missing'}), 400

    # Validate the API token
    user = User.find_by_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized access: invalid token'}), 403

    # Check if the token has expired
    if user.api_token_expiry < datetime.utcnow():
        return jsonify({'error': 'Token has expired'}), 403

    # Return the user info (for demonstration purposes)
    return jsonify({
        'username': user.username,
        'email': user.email,
        'message': 'User information retrieved successfully'
    })
