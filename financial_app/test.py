# test.py

import unittest
import io
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_status_code(self):
        #Test Home page returns status 200 OK.
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        #Test the login valid and invalid credentials.
        response = self.app.post('/login', data=dict(username="invalid", password="invalid"))
        self.assertEqual(response.status_code, 302)  
        self.assertIn('/login', response.headers['Location'])  

        # Valid login attempt
        response = self.app.post('/login', data=dict(username="testuser", password="password"))
        self.assertEqual(response.status_code, 302) 
        self.assertIn('/dashboard', response.headers['Location']) 
    def test_reset_password(self):
        # Test the password reset.
        response = self.app.post('/request_password_reset', data=dict(username="testuser"))
        self.assertEqual(response.status_code, 302)  
        self.assertIn('/reset_password', response.headers['Location'])  

    def test_upload_file(self):
        """Test file upload functionality."""
        # Log in authenticate the request
        response = self.app.post('/login', data=dict(username="testuser", password="password"))
        self.assertEqual(response.status_code, 302)  
        self.assertIn('/dashboard', response.headers['Location']) 

        # Then upload the file
        data = {
            'file': (io.BytesIO(b"test file content"), 'test.txt')
        }
        response = self.app.post('/upload', content_type='multipart/form-data', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'File uploaded successfully', response.data)

if __name__ == '__main__':
    unittest.main()
