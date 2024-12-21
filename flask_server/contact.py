from flask import Flask, request, jsonify
import pyodbc
from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime
from flask import Flask, request, jsonify
from flask import Blueprint, request, jsonify, session
import pyodbc
import os

contact_bp = Blueprint('contact', __name__)

# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn



@contact_bp.route('/api/contact', methods=['POST'])
def handle_contact():
    data = request.get_json()
    
    # Get the contact form data
    name = data.get('name')
    email = data.get('email')
    number = data.get('number')
    message = data.get('message')

    if not name or not email or not number or not message:
        return jsonify({"error": "All fields are required."}), 400

    # Insert the contact data into the database

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert query
    cursor.execute("""
        INSERT INTO Contacts (UserName, Email, Number, Message)
        VALUES (?, ?, ?, ?)
    """, (name, email, number, message))
    
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Message sent successfully!"}), 200
