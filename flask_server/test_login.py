import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app
from werkzeug.security import generate_password_hash

class TestLoginAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test client for the Flask app
        self.client = app.test_client()
        self.base_url = '/login'

    @patch('pyodbc.connect')  # Mock the database connection
    def test_login_success(self, mock_connect):
        # Mock the database cursor and connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock a hashed password in the database
        hashed_password = generate_password_hash('password123')

        # Simulate the query result where the email is found with the correct hashed password
        mock_cursor.fetchone.return_value = (hashed_password,)

        payload = {
            "email": "johndoe@example.com",
            "password": "password123"
        }

        response = self.client.post(self.base_url, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome", response.json['message'])
        self.assertIn("/profile", response.json['redirect'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_login_invalid_password(self, mock_connect):
        # Mock the database cursor and connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock a hashed password in the database
        hashed_password = generate_password_hash('password123')

        # Simulate the query result where the email is found but with an incorrect password
        mock_cursor.fetchone.return_value = (hashed_password,)

        payload = {
            "email": "johndoe@example.com",
            "password": "wrongpassword"
        }

        response = self.client.post(self.base_url, json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid password", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_login_user_not_found(self, mock_connect):
        # Mock the database cursor and connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate the query result where the user is not found (None)
        mock_cursor.fetchone.return_value = None

        payload = {
            "email": "nonexistentuser@example.com",
            "password": "password123"
        }

        response = self.client.post(self.base_url, json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.json['message'])

if __name__ == "__main__":
    unittest.main()
