from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

# User model using SQLAlchemy
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api_token = db.Column(db.String(200), nullable=True)
    api_token_expiry = db.Column(db.DateTime, nullable=True)
    reset_token = db.Column(db.String(200), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)

    # Flask-Login required properties
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)  # Flask-Login expects the ID to be a string

    # Create a new user in the database
    @staticmethod
    def create_user(username, email, password_hash):
        try:
            new_user = User(username=username, email=email, password_hash=password_hash)
            db.session.add(new_user)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    # Find a user by username
    @staticmethod
    def find_by_username(username):
        return User.query.filter_by(username=username).first()

    # Find a user by their ID (used by Flask-Login)
    @staticmethod
    def find_by_id(user_id):
        return User.query.get(user_id)

    # Update the user's API token and its expiry time
    def update_token(self, token, expiry_time):
        self.api_token = token
        self.api_token_expiry = expiry_time
        db.session.commit()

    # Clear the user's API token and its expiry time
    def clear_token(self):
        self.api_token = None
        self.api_token_expiry = None
        db.session.commit()

    # Update the user's password
    def update_password(self, new_password_hash):
        self.password_hash = new_password_hash
        db.session.commit()

    # Find a user by email or username for password reset
    @staticmethod
    def find_by_email_or_username(email_or_username):
        return User.query.filter((User.username == email_or_username) | (User.email == email_or_username)).first()

    # Update the user's password reset token and its expiry time
    def update_reset_token(self, reset_token, expiry_time):
        self.reset_token = reset_token
        self.token_expiry = expiry_time
        db.session.commit()

    # Clear the password reset token
    def clear_reset_token(self):
        self.reset_token = None
        self.token_expiry = None
        db.session.commit()


# File model using SQLAlchemy
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a new file record in the database
    @staticmethod
    def create_file(user_id, filename, filepath):
        try:
            new_file = File(user_id=user_id, filename=filename, filepath=filepath)
            db.session.add(new_file)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error creating file record: {e}")
            return False

    # Find a file by filename
    @staticmethod
    def find_by_filename(filename):
        return File.query.filter_by(filename=filename).first()

    # Delete a file record by its ID
    @staticmethod
    def delete_file(file_id):
        try:
            file = File.query.get(file_id)
            if file:
                db.session.delete(file)
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
