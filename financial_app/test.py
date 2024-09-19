import unittest
import io
from app import app
from app.models import User
from datetime import datetime, timedelta, timezone

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Ensure test user exists
        self.test_username = 'test'
        self.test_password = 'test'

        with app.app_context():
            user = User.find_by_username(self.test_username)
            if not user:
                User.create_user(self.test_username, self.test_password)
            else:
                # Update password in case it has changed
                user.update_password(self.test_password)

    def test_home_status_code(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        # Test invalid login (should redirect back to login)
        response = self.app.post('/login', data=dict(username="invalid", password="invalid"), follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

        # Test valid login (should render two-factor page)
        response = self.app.post('/login', data=dict(username=self.test_username, password=self.test_password))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Two-Factor Authentication', response.data)

        # Simulate two-factor authentication
        with app.app_context():
            user = User.find_by_username(self.test_username)
            two_factor_code = user.two_factor_code

        response = self.app.post('/verify_two_factor', data=dict(
            username=self.test_username,
            two_factor_code=two_factor_code,
            flow_type='login'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

    def test_reset_password(self):
        # Request password reset (renders two-factor page)
        response = self.app.post('/request_password_reset', data=dict(username=self.test_username))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Two-Factor Authentication', response.data)

        # Simulate two-factor authentication
        with app.app_context():
            user = User.find_by_username(self.test_username)
            two_factor_code = user.two_factor_code

        response = self.app.post('/verify_two_factor', data=dict(
            username=self.test_username,
            two_factor_code=two_factor_code,
            flow_type='reset_password'
        ), follow_redirects=True)

        # After verification, should redirect to reset_password page
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Reset Your Password', response.data)

        # Now reset the password
        new_password = 'newtestpassword'
        with app.app_context():
            user = User.find_by_username(self.test_username)
            reset_token = user.reset_token

        response = self.app.post(f'/reset_password/{reset_token}', data=dict(
            password=new_password,
            confirm_password=new_password
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password reset successful', response.data)

        # Verify that we can log in with the new password
        response = self.app.post('/login', data=dict(username=self.test_username, password=new_password))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Two-Factor Authentication', response.data)

    def test_upload_file(self):
        """Test file upload functionality."""
        # Log in first
        response = self.app.post('/login', data=dict(username=self.test_username, password=self.test_password))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Two-Factor Authentication', response.data)

        # Simulate two-factor authentication
        with app.app_context():
            user = User.find_by_username(self.test_username)
            two_factor_code = user.two_factor_code

        response = self.app.post('/verify_two_factor', data=dict(
            username=self.test_username,
            two_factor_code=two_factor_code,
            flow_type='login'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

        # Now test file upload
        data = {
            'file': (io.BytesIO(b"test file content"), 'test.txt')
        }
        response = self.app.post('/upload', content_type='multipart/form-data', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'File uploaded successfully', response.data)

if __name__ == '__main__':
    unittest.main()
