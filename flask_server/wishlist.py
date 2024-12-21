from flask import Flask, request, jsonify
from flask import Blueprint, request, jsonify, session
import pyodbc
import os

wishlist_bp = Blueprint('wishlist', __name__)


# Path to the folder containing your images
IMAGE_FOLDER = os.path.abspath("C:/Users/mohamed mahmoud emam/Desktop/Seif/myapp/src/assets")

# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn


@wishlist_bp.route('/api/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    try:
        data = request.get_json()
        email = data.get('email')
        product_id = data.get('productId')

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the user ID from the Users table using the email
        cursor.execute("SELECT UserID FROM Users WHERE Email = ?", email)
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        user_id = user[0]

        # Check if the product is already in the wishlist
        cursor.execute("""
            SELECT * FROM WishList
            WHERE UserID = ? AND ProductID = ?
        """, (user_id, product_id))

        wishlist_item = cursor.fetchone()

        if wishlist_item:
            # If the item already exists in the wishlist, return a message
            return jsonify({"success": False, "message": "Product is already in the wishlist"}), 200

        # If the item does not exist in the wishlist, insert it
        cursor.execute("""
            INSERT INTO WishList (UserID, ProductID)
            VALUES (?, ?)
        """, (user_id, product_id))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Product added to wishlist"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@wishlist_bp.route('/api/wishlist', methods=['GET'])
def get_wishlist_items():
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
        # Fetch wishlist items
        cursor.execute("""
            SELECT p.ProductID, p.ProductName, p.ProdcutPrice, p.ImageURL
            FROM Wishlist w
            JOIN Products p ON w.ProductID = p.ProductID
            WHERE w.UserID = ?
        """, user_id)


        wishlist_items = cursor.fetchall()

        if wishlist_items:
            wishlist_items_list = [
                {
                    "id": item[0],
                    "name": item[1],
                    "price": item[2],
                    "image": f"http://127.0.0.1:5000/images/{os.path.basename(item[3])}",
                }
                for item in wishlist_items
            ]
            return jsonify({"wishlistItems": wishlist_items_list}), 200
        else:
            return jsonify({"wishlistItems": []}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500



@wishlist_bp.route('/api/remove_from_wishlist', methods=['POST'])
def remove_from_wishlist():
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
            DELETE FROM WishList
            WHERE UserID = ? AND ProductID = ?
        """, (user_id, product_id))

        conn.commit()
        conn.close()

        return jsonify({"message": "Item removed from wishlist"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500
