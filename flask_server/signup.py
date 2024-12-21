from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash
import pyodbc

# Create a Blueprint for the signup functionality
signup_bp = Blueprint('signup', __name__)

# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn

@signup_bp.route('/submit_form', methods=['POST'])
def sign_up():
    # Get JSON data from the request body
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    address = data.get('address')

    # Validate input
    if not all([name, email, password, phone, address]):
        return jsonify({'error': 'All fields are required'}), 400

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query to insert data into Users table
        query = """
        INSERT INTO Users (UserName, Email, HashedPassword, UserPhone, UserAddress)
        VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (name, email, hashed_password, phone, address))

        # Commit changes and close connection
        conn.commit()
        conn.close()

        # Store email in session for tracking (optional)
        session['user'] = {'email': email}

        # Return email to frontend for localStorage
        return jsonify({'email': email, 'message': f'Welcome, {email} Signed Up!'}), 200
    except pyodbc.IntegrityError:
        # Handle duplicate email insertion
        conn.rollback()
        conn.close()
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        # Handle other potential errors
        conn.rollback()
        conn.close()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
