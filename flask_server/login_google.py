from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import random
import string
import pyodbc

# Create a Blueprint for the login functionality
logingoogle_bp = Blueprint('login_google', __name__)

# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn


@logingoogle_bp.route('/login/google')
def login_with_google():
    # Generate a nonce (a random string)
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    # Store the nonce in the session
    session['nonce'] = nonce

    # Google OAuth redirect URI
    redirect_uri = url_for('login_google.google_callback', _external=True)

    # Get the OAuth client from the app (the one initialized in app.py)
    from app import google  # Import it from app.py where it's initialized
    return google.authorize_redirect(redirect_uri, nonce=nonce)

@logingoogle_bp.route('/login/google/callback')
def google_callback():
    try:
        # Retrieve the nonce from the session
        nonce = session.get('nonce')

        from app import google  # Import it from app.py where it's initialized

        # Get the token and user info
        token = google.authorize_access_token()
        user_info = google.parse_id_token(token, nonce=nonce)

        # Extract user details
        email = user_info['email']
        name = user_info.get('name', email.split('@')[0])
        google_id = user_info['sub']

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user exists in the database
        query = "SELECT * FROM Users WHERE Email = ?"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if not user:
            # First-time login: insert user into the database
            query = "INSERT INTO Users (UserName, Email, goog_id, UserPhone, UserAddress) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (name, email, google_id, 'N/A', 'N/A'))  # Default values for phone/address
            conn.commit()

        # Close the connection
        conn.close()
        
        # Redirect to the React frontend with the email
        react_url = f"http://localhost:3000?email={email}"
        return redirect(react_url, code=302)

    except Exception as e:
        return jsonify({'message': 'User not found. Please check your email.'}), 404