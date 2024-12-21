from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime
from flask import Blueprint

# Create a Blueprint for the payment functionality
payment_bp = Blueprint('payment', __name__)

# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn

from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime
from flask import Blueprint

# Create a Blueprint for the payment functionality
payment_bp = Blueprint('payment', __name__)

# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn

@payment_bp.route('/api/checkout', methods=['POST'])
def checkout():
    order_data = request.json
    user_email = order_data['userEmail']
    total_price = order_data['totalPrice']
    card_number = order_data['cardNumber']
    billing_address = order_data['billingAddress']
    
    # Get database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch user ID from the Users table
    cursor.execute("SELECT UserID FROM Users WHERE Email = ?", user_email)
    user = cursor.fetchone()

    if not user:
        return jsonify({'message': 'User not found'}), 400
    
    user_id = user[0]
    order_date = datetime.now()

    # Fetch cart items for the user from ShoppingCarts
    cursor.execute("""
        SELECT sc.ProductID, sc.Quantity, p.ProdcutPrice 
        FROM ShoppingCarts sc
        JOIN Products p ON sc.ProductID = p.ProductID
        WHERE sc.UserID = ?
    """, user_id)
    cart_items = cursor.fetchall()

    # Check if there are items in the cart
    if not cart_items:
        return jsonify({'message': 'No items found in cart'}), 400

    # Insert into Orders table
    cursor.execute('''
        INSERT INTO Orders (UserID, TotalPrice, OrderDate, CardNumber, OrderLocation)
        VALUES (?, ?, ?, ?, ?)
    ''', user_id, total_price, order_date, card_number, billing_address)

# Fetch the last inserted OrderID using SELECT TOP 1
    cursor.execute('''
        SELECT TOP 1 OrderID
        FROM Orders
        ORDER BY OrderID DESC
    ''')
    order_id = cursor.fetchone()[0]  # Retrieve the OrderID


    # Insert into OrderDetails table for each cart item
    for item in cart_items:
        product_id = item.ProductID
        quantity = item.Quantity
        price = item.ProdcutPrice  # Correcting this line to use 'ProductPrice'

        cursor.execute('''
            INSERT INTO OrderDetails (OrderID, ProductID, Quantity, Price)
            VALUES (?, ?, ?, ?)
        ''', order_id, product_id, quantity, price)


    # Clear the user's cart
    cursor.execute('''
        DELETE FROM ShoppingCarts
        WHERE UserID = ?
    ''', user_id)

    # Commit the transaction
    conn.commit()

    # Close the connection
    conn.close()

    return jsonify({'message': 'Payment successful! Your order has been placed.'}), 200
