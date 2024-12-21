import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app
import pyodbc

class TestSignupAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test client for the Flask app
        self.client = app.test_client()
        self.base_url = '/submit_form'

    @patch('pyodbc.connect')  # Mock the database connection
    def test_sign_up_success(self, mock_connect):
        # Mock the database cursor and connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        payload = {
            "name": "Jane Doe",
            "email": "janedoe@example.com",
            "password": "password123",
            "phone": "9876543210",
            "address": "123 Street Name"
        }

        # Mock the commit and close methods to avoid actual DB operations
        mock_cursor.execute.return_value = None
        mock_conn.commit.return_value = None
        mock_conn.close.return_value = None

        response = self.client.post(self.base_url, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Signed Up!", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_sign_up_missing_fields(self, mock_connect):
        # Test submission with missing fields
        payload = {
            "name": "Jane Doe",
            "email": "janedoe@example.com",
            "password": "password123",
        }

        response = self.client.post(self.base_url, json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("All fields are required", response.json['error'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_sign_up_email_exists(self, mock_connect):
        # Mock the database cursor and connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        payload = {
            "name": "John Doe",
            "email": "existinguser@example.com",
            "password": "password123",
            "phone": "1234567890",
            "address": "456 Avenue"
        }

        # Simulate a database integrity error (duplicate email)
        mock_cursor.execute.side_effect = pyodbc.IntegrityError('Duplicate email', '', '')

        response = self.client.post(self.base_url, json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email already exists", response.json['error'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_sign_up_database_error(self, mock_connect):
        # Mock the database cursor and connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        payload = {
            "name": "John Doe",
            "email": "janedoe@example.com",
            "password": "password123",
            "phone": "9876543210",
            "address": "123 Street Name"
        }

        # Simulate a general exception (non-integrity error)
        mock_cursor.execute.side_effect = Exception('Some database error')

        response = self.client.post(self.base_url, json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("An error occurred", response.json['error'])

if __name__ == "__main__":
    unittest.main()
