from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
import pyodbc
from flask import Flask, request, jsonify
from flask import Blueprint, request, jsonify, session
import pyodbc
import os

# Create a Blueprint for the login functionality
orderhistory_bp = Blueprint('orderhistory', __name__)

# Path to the folder containing your images
IMAGE_FOLDER = os.path.abspath("C:/Users/mohamed mahmoud emam/Desktop/Seif/myapp/src/assets")

# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn

@orderhistory_bp.route('/api/order-history', methods=['GET'])
def order_history():
    user_email = request.args.get('email')

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the user ID from Users table using the email
    cursor.execute("SELECT UserID FROM Users WHERE Email = ?", user_email)
    user = cursor.fetchone()

    if not user:
        return jsonify({'message': 'User not found'}), 400

    user_id = user[0]

    # Fetch the user's orders and associated products
    cursor.execute('''
        SELECT o.OrderID, o.TotalPrice, o.OrderDate, od.ProductID, p.ProductName, p.ProdcutPrice, od.Quantity, p.ImageURL
        FROM Orders o
        JOIN OrderDetails od ON o.OrderID = od.OrderID
        JOIN Products p ON od.ProductID = p.ProductID
        WHERE o.UserID = ?
        ORDER BY o.OrderDate DESC
    ''', user_id)

    rows = cursor.fetchall()

    # Process the data into a more usable format
    orders = []
    for row in rows:
        order = next((order for order in orders if order['orderId'] == row.OrderID), None)
        if not order:
            order = {
                'orderId': row.OrderID,
                'orderDate': row.OrderDate,
                'totalPrice': row.TotalPrice,
                'products': []
            }
            orders.append(order)
        
        product = {
            'productId': row.ProductID,
            'productName': row.ProductName,
            'price': row.ProdcutPrice,
            'quantity': row.Quantity,
            'imageUrl': f"http://127.0.0.1:5000/images/{os.path.basename(row.ImageURL)}"
        }
        order['products'].append(product)

    conn.close()
    return jsonify({'orders': orders})
