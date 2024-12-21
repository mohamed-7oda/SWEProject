from flask import Flask, request, jsonify
from flask import Blueprint, request, jsonify, session
import pyodbc
import os

cart_bp = Blueprint('cart', __name__)


# Path to the folder containing your images
IMAGE_FOLDER = os.path.abspath("C:/Users/mohamed mahmoud emam/Desktop/Seif/myapp/src/assets")

# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn


@cart_bp.route('/api/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        email = data.get('email')
        product_id = data.get('productId')
        quantity = data.get('quantity', 1)

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the user ID from the Users table using the email
        cursor.execute("SELECT UserID FROM Users WHERE Email = ?", email)
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        user_id = user[0]

        # Check if the product is already in the cart
        cursor.execute("""
            SELECT * FROM ShoppingCarts
            WHERE UserID = ? AND ProductID = ?
        """, (user_id, product_id))

        cart_item = cursor.fetchone()

        if cart_item:
            # If the item already exists in the cart, update the quantity
            cursor.execute("""
                UPDATE ShoppingCarts
                SET Quantity = Quantity + ?
                WHERE UserID = ? AND ProductID = ?
            """, (quantity, user_id, product_id))
        else:
            # If the item does not exist in the cart, insert it
            cursor.execute("""
                INSERT INTO ShoppingCarts (UserID, ProductID, Quantity)
                VALUES (?, ?, ?)
            """, (user_id, product_id, quantity))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Product added to cart"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@cart_bp.route('/api/cart', methods=['GET'])
def get_cart_items():
    try:
        email = request.args.get('email')  # Get email from query parameter

        if not email:
            return jsonify({"message": "Email is required"}), 400
        
        # Get the user ID from the Users table
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID FROM Users WHERE Email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "User not found"}), 404
        
        user_id = user[0]

        # Fetch cart items for the user
        cursor.execute("""
            SELECT p.ProductID, p.ProductName, p.ProdcutPrice, sc.Quantity, p.ImageURL
            FROM ShoppingCarts sc
            JOIN Products p ON sc.ProductID = p.ProductID
            WHERE sc.UserID = ?
        """, (user_id,))

        cart_items = cursor.fetchall()

        if cart_items:
            cart_items_list = [
                {
                    "id": item[0],
                    "name": item[1],
                    "price": item[2],
                    "quantity": item[3],
                    "image": f"http://127.0.0.1:5000/images/{os.path.basename(item[4])}",
                }
                for item in cart_items
            ]
            return jsonify({"cartItems": cart_items_list}), 200
        else:
            return jsonify({"cartItems": []}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500



@cart_bp.route('/api/remove_from_cart', methods=['POST'])
def remove_from_cart():
    try:
        data = request.get_json()
        email = data.get('email')
        product_id = data.get('productId')

        # Get the user ID from the Users table
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID FROM Users WHERE Email = ?", email)
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "User not found"}), 404

        user_id = user[0]

        # Remove the item from the cart
        cursor.execute("""
            DELETE FROM ShoppingCarts
            WHERE UserID = ? AND ProductID = ?
        """, (user_id, product_id))

        conn.commit()
        conn.close()

        return jsonify({"message": "Item removed from cart"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500
