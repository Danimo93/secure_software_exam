# test.py

import unittest
import io
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_status_code(self):
        """Test that the home page returns a status code 200."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        """Test the login functionality with valid and invalid credentials."""
        # Invalid login attempt (check for redirect)
        response = self.app.post('/login', data=dict(username="invalid", password="invalid"))
        self.assertEqual(response.status_code, 302)  # Check for redirect on invalid login
        self.assertIn('/login', response.headers['Location'])  # Ensure it's redirecting to login

        # Valid login attempt
        response = self.app.post('/login', data=dict(username="testuser", password="password"))
        self.assertEqual(response.status_code, 302)  # Redirect after valid login
        self.assertIn('/dashboard', response.headers['Location'])  # Ensure it's redirecting to the dashboard

    def test_reset_password(self):
        """Test the password reset process."""
        response = self.app.post('/request_password_reset', data=dict(username="testuser"))
        self.assertEqual(response.status_code, 302)  # Ensure the route exists and returns a redirect
        self.assertIn('/reset_password', response.headers['Location'])  # Check redirect to reset page

    def test_upload_file(self):
        """Test file upload functionality."""
        # Log in first to authenticate the request
        response = self.app.post('/login', data=dict(username="testuser", password="password"))
        self.assertEqual(response.status_code, 302)  # Ensure login was successful
        self.assertIn('/dashboard', response.headers['Location'])  # Ensure redirect to dashboard

        # Then upload the file
        data = {
            'file': (io.BytesIO(b"test file content"), 'test.txt')
        }
        response = self.app.post('/upload', content_type='multipart/form-data', data=data, follow_redirects=True)

        # Check for the correct status code after upload and check for success message
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'File uploaded successfully', response.data)

if __name__ == '__main__':
    unittest.main()
