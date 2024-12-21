import os
from flask import Blueprint, request, jsonify
import pyodbc
import uuid

admin_bp = Blueprint('admin', __name__)

server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;' 


def get_db_connection():
    return pyodbc.connect(conn_str)

@admin_bp.route('/api/admin/check', methods=['GET'])
def check_admin():
    user_email = request.args.get('email')  # Email sent from frontend
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT IsAdmin FROM Users WHERE Email = ?", (user_email,))
    result = cursor.fetchone()

    if result and result[0]:  # If IsAdmin == 1
        return jsonify({"isAdmin": True}), 200
    return jsonify({"isAdmin": False}), 403

# Delete a product (admin-only)
@admin_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Products WHERE ProductID = ?", (product_id,))
        conn.commit()
        return jsonify({"success": True, "message": "Product deleted successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

# Define the assets folder relative to the project structure
base_dir = os.path.dirname(__file__)  # This gets the directory where admin.py is located
assets_folder = os.path.join('c:\\','Users','mohamed mahmoud emam','Desktop','Seif','myapp', 'src', 'assets')  # Going up one directory from flask_server to Seif

@admin_bp.route('/api/products', methods=['POST'])
def add_product():
        conn = None  # Initialize conn to avoid reference errors in the finally block
        data = request.form  # Get form data (text fields)
        image_file = request.files.get('ImageFile')  # Get the uploaded image file
        
        product_name = data['ProductName']
        product_description = data['ProductDescription']
        product_price = data['ProductPrice']
        category_id = data['CategoryID']

        # Ensure the assets folder exists
        if not os.path.exists(assets_folder):
            os.makedirs(assets_folder)  # Create the directory if it doesn't exist
        
        # Create a unique name for the image file
        image_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
        image_file.save(os.path.join(assets_folder, image_filename))
        image_url = f'C:\\Users\\mohamed mahmoud emam\\Desktop\\Seif\\myapp\\src\\assets\\{image_filename}'  # The relative path for the image

        conn = get_db_connection()  # Create the connection here, before querying the database
        cursor = conn.cursor()

        # Insert new product into the database
        cursor.execute(""" 
            INSERT INTO Products (ProductName, ProductDescription, ProdcutPrice, CategoryID, ImageURL)
            VALUES (?, ?, ?, ?, ?)
        """, (product_name, product_description, product_price, category_id, image_url))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Product added successfully."}), 201


@admin_bp.route('/api/products/price', methods=['PUT'])
def update_product_price():
    try:
        data = request.get_json()

        product_name = data['ProductName']
        new_price = data['ProductPrice']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the product's price in the database
        cursor.execute("""
            UPDATE Products 
            SET ProdcutPrice = ? 
            WHERE ProductName = ?
        """, (new_price, product_name))

        conn.commit()

        return jsonify({"success": True, "message": "Product price updated successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@admin_bp.route('/api/categories', methods=['POST'])
def add_category():
    try:
        data = request.get_json()

        # Extract category name from the request
        category_name = data['CategoryName']
        category_id = data['CategoryID']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert new category into the database
        cursor.execute("""
            INSERT INTO Categories (CategoryID, CategoryName)
            VALUES (?, ?)
        """, (category_id, category_name))
        conn.commit()

        return jsonify({"success": True, "message": "Category added successfully."}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()
