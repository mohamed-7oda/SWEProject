import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app

class TestCartAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test client for the Flask app
        self.client = app.test_client()
        self.base_url_add = '/api/add_to_cart'
        self.base_url_get = '/api/cart'
        self.base_url_remove = '/api/remove_from_cart'

    @patch('pyodbc.connect')  # Mock the database connection
    def test_add_to_cart_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate the user and product
        mock_cursor.fetchone.return_value = [1]  # User ID = 1
        mock_cursor.fetchall.return_value = []  # No existing items in the cart

        # Define the payload
        payload = {
            "email": "johndoe@example.com",
            "productId": 123,
            "quantity": 2
        }

        # Mock the cart item insertion
        mock_cursor.execute.return_value = None

        response = self.client.post(self.base_url_add, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Product added to cart", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_add_to_cart_update_quantity(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate the user and existing cart item
        mock_cursor.fetchone.return_value = [1]  # User ID = 1
        mock_cursor.fetchall.return_value = [(1, 2, 5, 3, "http://example.com/image.jpg")]  # Existing cart item

        # Define the payload
        payload = {
            "email": "johndoe@example.com",
            "productId": 2,
            "quantity": 3
        }

        # Mock the cart item update
        mock_cursor.execute.return_value = None

        response = self.client.post(self.base_url_add, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Product added to cart", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_cart_items_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate the user
        mock_cursor.fetchone.return_value = [1]  # User ID = 1

        # Mock the cart items retrieval
        mock_cursor.fetchall.return_value = [
            (1, "Product A", 50.0, 2, "http://example.com/imageA.jpg"),
            (2, "Product B", 30.0, 1, "http://example.com/imageB.jpg")
        ]

        response = self.client.get(f"{self.base_url_get}?email=johndoe@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['cartItems']), 2)
        self.assertEqual(response.json['cartItems'][0]['name'], "Product A")
        self.assertEqual(response.json['cartItems'][1]['name'], "Product B")

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_cart_items_no_items(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate the user
        mock_cursor.fetchone.return_value = [1]  # User ID = 1

        # Simulate no items in the cart
        mock_cursor.fetchall.return_value = []

        response = self.client.get(f"{self.base_url_get}?email=johndoe@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['cartItems'], [])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_remove_from_cart_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate the user
        mock_cursor.fetchone.return_value = [1]  # User ID = 1

        # Mock the item removal
        mock_cursor.execute.return_value = None

        payload = {
            "email": "johndoe@example.com",
            "productId": 123
        }

        response = self.client.post(self.base_url_remove, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Item removed from cart", response.json['message'])

if __name__ == "__main__":
    unittest.main()
