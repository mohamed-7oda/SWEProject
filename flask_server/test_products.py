import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app

class TestProductsAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test client for the Flask app
        self.client = app.test_client()
        self.base_url = '/api/products'
        self.image_url = '/images/test_image.jpg'

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_products_success(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock the products fetched from the database
        mock_cursor.fetchall.return_value = [
            (1, 'Product A', 'Description of Product A', 100.0, 1, 'path/to/image1.jpg'),
            (2, 'Product B', 'Description of Product B', 150.0, 2, 'path/to/image2.jpg')
        ]

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['ProductName'], 'Product A')
        self.assertEqual(response.json[1]['ProductPrice'], 150.0)

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_products_with_category_filter(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock the products fetched from the database based on category filter
        mock_cursor.fetchall.return_value = [
            (1, 'Product A', 'Description of Product A', 100.0, 1, 'path/to/image1.jpg')
        ]

        response = self.client.get(self.base_url, query_string={'category_id': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['ProductName'], 'Product A')
        self.assertEqual(response.json[0]['CategoryID'], 1)

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_products_no_results(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock an empty list of products
        mock_cursor.fetchall.return_value = []

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

    @patch('pyodbc.connect')  # Mock the database connection
    def test_get_products_database_error(self, mock_connect):
        # Mock the database connection and simulate an error
        mock_connect.side_effect = Exception("Database error")

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Database error", response.json['message'])

    @patch('flask.send_from_directory')  # Mock the static image serving function
    def test_serve_image_success(self, mock_send_from_directory):
        # Simulate serving the image from the image folder
        mock_send_from_directory.return_value = "Image served successfully"
        
        response = self.client.get(self.image_url)
        self.assertEqual(response.status_code, 200)
        mock_send_from_directory.assert_called_with("C:/Users/mohamed mahmoud emam/Desktop/Seif/myapp/src/assets", 'test_image.jpg')

    def test_serve_image_not_found(self):
        # Test if image is not found (404)
        response = self.client.get(self.image_url)
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
