import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app

class TestPaymentAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test client for the Flask app
        self.client = app.test_client()
        self.checkout_url = '/api/checkout'

    @patch('pyodbc.connect')  # Mock the database connection
    def test_checkout_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock a user found in the database with UserID
        mock_cursor.fetchone.return_value = MagicMock(UserID=1)

        # Mock cart items for the user
        mock_cursor.fetchall.return_value = [
            MagicMock(ProductID=101, Quantity=2, ProdcutPrice=50.00),
            MagicMock(ProductID=102, Quantity=1, ProdcutPrice=100.00)
        ]

        payload = {
            "userEmail": "johndoe@example.com",
            "totalPrice": 200.00,
            "cardNumber": "1234567890123456",
            "billingAddress": "123 Test St, Test City"
        }

        response = self.client.post(self.checkout_url, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Payment successful", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_checkout_user_not_found(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate no user found in the database
        mock_cursor.fetchone.return_value = None

        payload = {
            "userEmail": "nonexistentuser@example.com",
            "totalPrice": 200.00,
            "cardNumber": "1234567890123456",
            "billingAddress": "123 Test St, Test City"
        }

        response = self.client.post(self.checkout_url, json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("User not found", response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_checkout_no_items_in_cart(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock user found in the database
        mock_cursor.fetchone.return_value = MagicMock(UserID=1)

        # Simulate no cart items for the user
        mock_cursor.fetchall.return_value = []

        payload = {
            "userEmail": "johndoe@example.com",
            "totalPrice": 200.00,
            "cardNumber": "1234567890123456",
            "billingAddress": "123 Test St, Test City"
        }

        response = self.client.post(self.checkout_url, json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("No items found in cart", response.json['message'])

if __name__ == "__main__":
    unittest.main()
