from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
import pyodbc
from flask import Flask, jsonify, send_from_directory
import os

# Create a Blueprint for the products functionality
categories_bp = Blueprint('categories', __name__)


# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn

# Fetch categories
@categories_bp.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CategoryID, CategoryName FROM Categories")
    categories = cursor.fetchall()

    category_list = [{'CategoryID': cat[0], 'CategoryName': cat[1]} for cat in categories]
    conn.close()
    return jsonify(category_list)