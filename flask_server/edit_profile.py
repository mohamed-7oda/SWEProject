from flask import Blueprint, request, jsonify, session
import pyodbc
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
import random
import string
import pyodbc
from flask import Flask, render_template, request, redirect, url_for
import pyodbc


editprofile_bp = Blueprint('edit_profile', __name__)

# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn

@editprofile_bp.route('/profile', methods=['GET'])
def get_profile():
    # Assuming the user's email is sent via a query parameter or retrieved from session
    email = request.args.get('email')  # Replace with session handling if needed

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Updated query to include UserName, UserAddress, UserPhone, and Email
        query = "SELECT UserName, UserAddress, UserPhone, Email FROM Users WHERE Email = ?"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        conn.close()

        if user:
            # Return the user's details as JSON
            return jsonify({
                "name": user.UserName,
                "address": user.UserAddress,
                "phone": user.UserPhone,
                "email": user.Email
            }), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    

@editprofile_bp.route('/edit-profile', methods=['POST'])
def edit_profile():
    data = request.get_json()
    email = data.get('email')  # Get user email
    name = data.get('name')
    address = data.get('address')
    phone = data.get('phone')

    if not all([name, address, phone]):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update query
    query = """
    UPDATE Users
    SET UserName = ?, UserAddress = ?, UserPhone = ?
    WHERE Email = ?
    """
    
    cursor.execute(query, (name, address, phone, email))
    conn.commit()

    return jsonify({"message": "Profile updated successfully!"})
