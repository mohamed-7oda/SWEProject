from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from signup import signup_bp  # Import the Blueprint
from login import login_bp  # Import the Blueprint
from login_google import logingoogle_bp  # Import the Blueprint

from flask import Flask, render_template, request, redirect, url_for, flash, session
from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template, request, redirect, url_for, flash, session
from authlib.integrations.flask_client import OAuth
from signup import signup_bp  # Import the Blueprint
from login import login_bp  # Import the Blueprint
from login_google import logingoogle_bp  # Import the Blueprint
from edit_profile import editprofile_bp
from wishlist import wishlist_bp
from categories import categories_bp
from comment import comment_bp
from admin import admin_bp
from payment import payment_bp
from contact import contact_bp
from order_history import orderhistory_bp
from flask_mail import Mail
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
from flask import Flask
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import bcrypt
import sqlite3
from products import products_bp
from cart import cart_bp
from werkzeug.security import generate_password_hash



# Create the Flask app
app = Flask(__name__, static_folder='../flask-server/build/static', template_folder='../flask-server/build')

# Apply CORS to the entire app
CORS(app)

app.secret_key = os.urandom(24)  

app.config['SESSION_COOKIE_SECURE'] = True  # Make sure to use HTTPS in production

# Initialize OAuths
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='52282127191-qli867g0kpl2co7ajjjtafq37hdf1qkt.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid profile email'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'
)

# Register Blueprints
app.register_blueprint(signup_bp)
app.register_blueprint(login_bp)
app.register_blueprint(logingoogle_bp)
app.register_blueprint(editprofile_bp)
app.register_blueprint(products_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(wishlist_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(orderhistory_bp)
app.register_blueprint(contact_bp)




# Serve the React app's index.html as the homepage
@app.route('/')
def home():
    return send_from_directory(app.template_folder, 'index.html')

# Serve static files from the React build (CSS, JS, images, etc.)
@app.route('/<path:path>')
def serve_static(path):
    if path == 'manifest.json':
        return send_from_directory('../flask-server/build', 'manifest.json')
    return send_from_directory(app.static_folder, path)


# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn



# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Or another SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'mohamedmahmoudemam23@gmail.com'  # Use your email
app.config['MAIL_PASSWORD'] = 'kglp prrh qobo upaw'  # Use your email password or app password
app.config['MAIL_DEFAULT_SENDER'] = 'mohamedmahmoudemam23@gmail.com'

mail = Mail(app)

# Serializer for generating and verifying tokens
serializer = URLSafeTimedSerializer('your_secret_key')  # Replace with your secret key


# Endpoint to request a password reset
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"message": "Email is required."}), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Users WHERE Email = ?', (email,)).fetchone()

    if user is None:
        return jsonify({"message": "Email not found."}), 404

    # Generate reset token
    reset_token = serializer.dumps(email, salt='password-reset-salt')
    conn.execute('UPDATE Users SET reset_token = ? WHERE Email = ?', (reset_token, email))
    conn.commit()
    conn.close()

    # Send reset email
    reset_link = f"http://localhost:3000/reset-password/{reset_token}"
    try:
        msg = Message(
            "Password Reset Request",
            sender="mohamedmahmoudemam23@gmail.co",
            recipients=[email],
        )
        msg.body = f"Click the link to reset your password: {reset_link}"
        mail.send(msg)
        return jsonify({"message": "Reset link sent to your email."}), 200
    except Exception as e:
        print("Error sending email:", e)
        return jsonify({"message": "Failed to send reset email."}), 500


# Endpoint to reset the password
@app.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hour validity
    except Exception:
        return jsonify({"message": "Invalid or expired token."}), 400

    data = request.get_json()
    new_password = data.get('password')

    if not new_password:
        return jsonify({"message": "Password is required."}), 400

    # Hash the new password
    hashed_password =  generate_password_hash(new_password)

    conn = get_db_connection()
    conn.execute('UPDATE Users SET HashedPassword = ?, reset_token = NULL WHERE Email = ?', 
                 (hashed_password, email))
    conn.commit()
    conn.close()

    return jsonify({"message": "Password reset successfully."}), 200

if __name__ == '__main__':
    app.run(debug=True)