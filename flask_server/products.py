from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
import pyodbc
from flask import Flask, jsonify, send_from_directory
import os

# Create a Blueprint for the products functionality
products_bp = Blueprint('products', __name__)

# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn

# Path to the folder containing your images
IMAGE_FOLDER = os.path.abspath("C:/Users/mohamed mahmoud emam/Desktop/Seif/myapp/src/assets")

# Fetch products
@products_bp.route('/api/products', methods=['GET'])
def get_products():
    category_id = request.args.get('category_id')  # Optional category filter
    conn = get_db_connection()
    cursor = conn.cursor()

    # Adjust the query based on category filter
    if category_id:
        query = "SELECT ProductID, ProductName, ProductDescription, ProdcutPrice, CategoryID, ImageURL FROM Products WHERE CategoryID = ?"
        cursor.execute(query, (category_id,))
    else:
        query = "SELECT ProductID, ProductName, ProductDescription, ProdcutPrice, CategoryID, ImageURL FROM Products"
        cursor.execute(query)

    products = cursor.fetchall()
    product_list = []
    for product in products:
        product_dict = {
            'ProductID': product[0],
            'ProductName': product[1],
            'ProductDescription': product[2],
            'ProductPrice': product[3],
            'CategoryID': product[4],
            'ImageURL': f"http://127.0.0.1:5000/images/{os.path.basename(product[5])}"
        }
        product_list.append(product_dict)
    
    conn.close()
    return jsonify(product_list)


# Serve static images
@products_bp.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)
