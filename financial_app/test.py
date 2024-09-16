# test.py

import unittest
import io
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_status_code(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.app.post('/login', data=dict(username="invalid", password="invalid"))
        self.assertEqual(response.status_code, 302)  
        self.assertIn('/login', response.headers['Location'])  

        response = self.app.post('/login', data=dict(username="asdasd", password="asdasd"))
        self.assertEqual(response.status_code, 302) 
        self.assertIn('/dashboard', response.headers['Location']) 

    def test_reset_password(self):
        response = self.app.post('/request_password_reset', data=dict(username="asdasd"))
        self.assertEqual(response.status_code, 302)  
        self.assertIn('/reset_password', response.headers['Location'])  

    def test_upload_file(self):
        """Test file upload functionality."""
        response = self.app.post('/login', data=dict(username="asdasd", password="asdasd"))
        self.assertEqual(response.status_code, 302)  
        self.assertIn('/dashboard', response.headers['Location']) 

        data = {
            'file': (io.BytesIO(b"test file content"), 'test.txt')
        }
        response = self.app.post('/upload', content_type='multipart/form-data', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'File uploaded successfully', response.data)

if __name__ == '__main__':
    unittest.main()


