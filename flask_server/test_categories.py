import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app

class TestCategoriesAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test client for the Flask app
        self.client = app.test_client()
        self.base_url = '/api/categories'

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_categories_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock the database response for categories
        mock_cursor.fetchall.return_value = [
            (1, "Electronics"),
            (2, "Clothing"),
            (3, "Home & Kitchen")
        ]

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)
        self.assertIn("CategoryID", response.json[0])
        self.assertEqual(response.json[0]['CategoryName'], "Electronics")
        self.assertEqual(response.json[1]['CategoryName'], "Clothing")
        self.assertEqual(response.json[2]['CategoryName'], "Home & Kitchen")

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_categories_empty(self, mock_connect):
        # Simulate an empty categories table (no categories)
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        mock_cursor.fetchall.return_value = []

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)  # Expect an empty list since no categories exist

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_categories_database_error(self, mock_connect):
        # Simulate a database connection error
        mock_connect.side_effect = Exception("Database error")

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertIn("Database error", response.json['error'])

if __name__ == "__main__":
    unittest.main()
