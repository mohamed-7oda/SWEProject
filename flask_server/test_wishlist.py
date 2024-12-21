import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app

class TestWishlistAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test client for the Flask app
        self.client = app.test_client()
        self.base_add_url = '/api/add_to_wishlist'
        self.base_get_url = '/api/wishlist'
        self.base_remove_url = '/api/remove_from_wishlist'

    @patch('pyodbc.connect')  # Mock the database connection
    def test_add_to_wishlist_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock a user found in the database
        mock_cursor.fetchone.return_value = MagicMock(UserID=1)

        # Mock no item found in wishlist
        mock_cursor.fetchone.return_value = None

        payload = {
            "email": "johndoe@example.com",
            "productId": 101
        }

        response = self.client.post(self.base_add_url, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Product added to wishlist", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_add_to_wishlist_user_not_found(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate no user found in the database
        mock_cursor.fetchone.return_value = None

        payload = {
            "email": "nonexistentuser@example.com",
            "productId": 101
        }

        response = self.client.post(self.base_add_url, json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_add_to_wishlist_product_already_in_wishlist(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock a user found in the database
        mock_cursor.fetchone.return_value = MagicMock(UserID=1)

        # Mock the product already in the wishlist
        mock_cursor.fetchone.return_value = MagicMock(ProductID=101)

        payload = {
            "email": "johndoe@example.com",
            "productId": 101
        }

        response = self.client.post(self.base_add_url, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Product is already in the wishlist", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_wishlist_items_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock a user found in the database
        mock_cursor.fetchone.return_value = MagicMock(UserID=1)

        # Mock wishlist items returned from the database
        mock_cursor.fetchall.return_value = [
            (101, 'Product A', 50.00, 'path/to/image1.jpg'),
            (102, 'Product B', 100.00, 'path/to/image2.jpg')
        ]

        response = self.client.get(self.base_get_url, query_string={"email": "johndoe@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("wishlistItems", response.json)
        self.assertEqual(len(response.json["wishlistItems"]), 2)

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_wishlist_items_user_not_found(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate no user found in the database
        mock_cursor.fetchone.return_value = None

        response = self.client.get(self.base_get_url, query_string={"email": "nonexistentuser@example.com"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_remove_from_wishlist_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock a user found in the database
        mock_cursor.fetchone.return_value = MagicMock(UserID=1)

        # Mock the item removed successfully
        mock_cursor.rowcount = 1

        payload = {
            "email": "johndoe@example.com",
            "productId": 101
        }

        response = self.client.post(self.base_remove_url, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Item removed from wishlist", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_remove_from_wishlist_user_not_found(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate no user found in the database
        mock_cursor.fetchone.return_value = None

        payload = {
            "email": "nonexistentuser@example.com",
            "productId": 101
        }

        response = self.client.post(self.base_remove_url, json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.json['message'])

if __name__ == "__main__":
    unittest.main()
