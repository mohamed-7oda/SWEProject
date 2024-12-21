import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app

class TestEditProfileAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test client for the Flask app
        self.client = app.test_client()
        self.base_url_profile = '/profile'
        self.base_url_edit_profile = '/edit-profile'

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_profile_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock the database response for the user
        mock_cursor.fetchone.return_value = MagicMock(
            UserName="John Doe",
            UserAddress="123 Main St",
            UserPhone="1234567890",
            Email="johndoe@example.com"
        )

        response = self.client.get(self.base_url_profile, query_string={'email': 'johndoe@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.json)
        self.assertEqual(response.json['name'], "John Doe")
        self.assertEqual(response.json['address'], "123 Main St")
        self.assertEqual(response.json['phone'], "1234567890")
        self.assertEqual(response.json['email'], "johndoe@example.com")

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_profile_missing_email(self, mock_connect):
        # Test the case where email is missing
        response = self.client.get(self.base_url_profile)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email is required", response.json['error'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_profile_user_not_found(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate no user found with the provided email
        mock_cursor.fetchone.return_value = None

        response = self.client.get(self.base_url_profile, query_string={'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.json['error'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_edit_profile_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock the POST request payload
        payload = {
            "email": "johndoe@example.com",
            "name": "John Doe",
            "address": "123 New Address",
            "phone": "9876543210"
        }

        # Mock the database update execution
        mock_cursor.execute.return_value = None
        mock_conn.commit.return_value = None

        response = self.client.post(self.base_url_edit_profile, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Profile updated successfully!", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_edit_profile_missing_fields(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Test submission with missing fields
        payload = {
            "email": "johndoe@example.com",
            "name": "John Doe",
            "address": "123 New Address"
            # Missing phone number
        }

        response = self.client.post(self.base_url_edit_profile, json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("All fields are required", response.json['error'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_edit_profile_database_error(self, mock_connect):
        # Simulate a database connection error
        mock_connect.side_effect = Exception("Database error")

        payload = {
            "email": "johndoe@example.com",
            "name": "John Doe",
            "address": "123 New Address",
            "phone": "9876543210"
        }

        response = self.client.post(self.base_url_edit_profile, json=payload)
        self.assertEqual(response.status_code, 500)
        self.assertIn("An error occurred", response.json['error'])

if __name__ == "__main__":
    unittest.main()
