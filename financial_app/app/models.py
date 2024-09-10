from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    api_token = db.Column(db.String(200), nullable=True)
    api_token_expiry = db.Column(db.DateTime, nullable=True)
    reset_token = db.Column(db.String(200), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)

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
        return str(self.id)

    @staticmethod
    def create_user(username, password_hash):
        try:
            new_user = User(username=username, password_hash=password_hash)
            db.session.add(new_user)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    @staticmethod
    def find_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def find_by_id(user_id):
        # Updated to use Session.get() as per SQLAlchemy 2.0 standards
        return db.session.get(User, user_id)

    def update_token(self, token, expiry_time):
        self.api_token = token
        self.api_token_expiry = expiry_time
        db.session.commit()

    def clear_token(self):
        self.api_token = None
        self.api_token_expiry = None
        db.session.commit()

    def update_password(self, new_password_hash):
        self.password_hash = new_password_hash
        db.session.commit()

    @staticmethod
    def find_by_username_for_reset(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def find_by_reset_token(token):
        return User.query.filter_by(reset_token=token).first()

    def update_reset_token(self, reset_token, expiry_time):
        self.reset_token = reset_token
        self.token_expiry = expiry_time
        db.session.commit()

    def clear_reset_token(self):
        self.reset_token = None
        self.token_expiry = None
        db.session.commit()


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    # Updated to use timezone-aware datetime
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

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

    @staticmethod
    def find_by_filename(filename):
        return File.query.filter_by(filename=filename).first()

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
