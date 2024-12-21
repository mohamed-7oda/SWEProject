import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app

class TestCommentAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test client for the Flask app
        self.client = app.test_client()
        self.add_comment_url = '/api/add_comment'
        self.get_comments_url = '/api/get_comments'

    @patch('pyodbc.connect')  # Mock the database connection
    def test_add_comment_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock a user found in the database with UserID
        mock_cursor.fetchone.return_value = MagicMock(UserID=1)

        payload = {
            "productId": 101,
            "userEmail": "johndoe@example.com",
            "comment": "This is a test comment",
            "rating": 5
        }

        response = self.client.post(self.add_comment_url, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json)
        self.assertTrue(response.json['success'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_add_comment_user_not_found(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate no user found by returning None
        mock_cursor.fetchone.return_value = None

        payload = {
            "productId": 101,
            "userEmail": "nonexistentuser@example.com",
            "comment": "This is a test comment",
            "rating": 5
        }

        response = self.client.post(self.add_comment_url, json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("success", response.json)
        self.assertFalse(response.json['success'])
        self.assertIn("User not found", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_comments_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate multiple comments for the product
        mock_cursor.fetchall.return_value = [
            MagicMock(UserName="John Doe", Comment="Great product!", Rating=5, DatePosted="2024-12-20 12:00:00"),
            MagicMock(UserName="Jane Doe", Comment="Not bad", Rating=4, DatePosted="2024-12-19 11:00:00")
        ]

        # Query parameter for productId
        response = self.client.get(self.get_comments_url, query_string={"productId": 101})
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json)
        self.assertTrue(response.json['success'])
        self.assertEqual(len(response.json['comments']), 2)

    def test_get_comments_missing_product_id(self):
        # Test for missing productId in the query string
        response = self.client.get(self.get_comments_url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Product ID is required", response.json['message'])

if __name__ == "__main__":
    unittest.main()
