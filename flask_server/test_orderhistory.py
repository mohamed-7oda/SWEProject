import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app

class TestOrderHistoryAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test client for the Flask app
        self.client = app.test_client()
        self.base_url = '/api/order-history'

    @patch('pyodbc.connect')  # Mock the database connection
    def test_order_history_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock the database response for the user
        mock_cursor.fetchone.return_value = (1,)  # Simulate user found with UserID = 1

        # Mock the database response for orders
        mock_cursor.fetchall.return_value = [
            (101, 200.0, '2024-12-20', 1, 'Product A', 50.0, 2, 'path/to/image1.jpg'),
            (102, 150.0, '2024-12-19', 2, 'Product B', 75.0, 1, 'path/to/image2.jpg')
        ]

        response = self.client.get(self.base_url, query_string={'email': 'johndoe@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['orders']), 2)
        self.assertEqual(response.json['orders'][0]['orderId'], 101)
        self.assertEqual(response.json['orders'][1]['products'][0]['productName'], 'Product B')

    @patch('pyodbc.connect')  # Mock the database connection
    def test_order_history_no_orders(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock the database response for the user
        mock_cursor.fetchone.return_value = (1,)  # Simulate user found with UserID = 1

        # Mock no orders for the user
        mock_cursor.fetchall.return_value = []

        response = self.client.get(self.base_url, query_string={'email': 'johndoe@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['orders'], [])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_order_history_user_not_found(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Simulate no user found with the provided email
        mock_cursor.fetchone.return_value = None

        response = self.client.get(self.base_url, query_string={'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('User not found', response.json['message'])

    @patch('pyodbc.connect')  # Mock the database connection
    def test_order_history_database_error(self, mock_connect):
        # Mock the database connection to simulate an error
        mock_connect.side_effect = Exception("Database error")

        response = self.client.get(self.base_url, query_string={'email': 'johndoe@example.com'})
        self.assertEqual(response.status_code, 500)
        self.assertIn('Database error', response.json['message'])

if __name__ == "__main__":
    unittest.main()
