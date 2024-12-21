from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
import pyodbc

# Create a Blueprint for the login functionality
login_bp = Blueprint('login', __name__)

# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn

@login_bp.route('/login', methods=['POST'])
def login():
    # Get the JSON data from the request
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to get the user's hashed password
    query = "SELECT HashedPassword FROM Users WHERE Email = ?"
    cursor.execute(query, (email,))
    user = cursor.fetchone()

    # Check if user exists and if the password matches
    if user:
        if check_password_hash(user[0], password):

            return jsonify({'message': f'Welcome, {email}!', 'redirect': '/profile', 'email': email}), 200
        else:
            return jsonify({'message': 'Invalid password. Please try again.'}), 400
    else:
        return jsonify({'message': 'User not found or invalid Password.'}), 404


