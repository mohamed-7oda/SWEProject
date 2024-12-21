import unittest
from app import app  # Import your Flask app

class TestContactAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test client for the Flask app
        self.client = app.test_client()
        self.base_url = '/api/contact'

    def test_handle_contact_success(self):
        # Test successful contact form submission
        payload = {
            "name": "John Doe",
            "email": "johndoe@example.com",
            "number": "1234567890",
            "message": "Hello, this is a test message."
        }

        response = self.client.post(self.base_url, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Message sent successfully!", response.json['message'])

    def test_handle_contact_missing_fields(self):
        # Test submission with missing fields
        payload = {
            "name": "John Doe",
            "email": "johndoe@example.com",
        }

        response = self.client.post(self.base_url, json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("All fields are required.", response.json['error'])

if __name__ == "__main__":
    unittest.main()
