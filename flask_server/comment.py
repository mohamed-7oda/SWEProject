from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime
from flask import Flask, request, jsonify
from flask import Blueprint, request, jsonify, session
import pyodbc
import os


comment_bp = Blueprint('comment', __name__)


# Database connection setup
server = 'LAPTOP-BQ4FQFIA\\SQLEXPRESS'
database = 'SWE'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

def get_db_connection():
    conn = pyodbc.connect(conn_str)
    return conn


@comment_bp.route('/api/add_comment', methods=['POST'])
def add_comment():
    data = request.get_json()

    product_id = data.get('productId')
    user_email = data.get('userEmail')
    comment = data.get('comment')
    rating = data.get('rating', 5)  # Default rating to 5 if not provided
    date_posted = datetime.now()

    # Get UserID based on the userEmail
    conn = get_db_connection()
    cursor = conn.cursor()

    # Assuming you have a Users table to get UserID by Email
    cursor.execute("SELECT UserID FROM Users WHERE Email = ?", user_email)
    user = cursor.fetchone()

    if user:
        user_id = user.UserID
        # Insert comment into Reviews table
        cursor.execute("""
            INSERT INTO Reviews (ProductID, UserID, Rating, Comment, DatePosted)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, user_id, rating, comment, date_posted))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True}), 200
    else:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "User not found"}), 400


@comment_bp.route('/api/get_comments', methods=['GET'])
def get_comments():
    product_id = request.args.get('productId')  # Get productId from query parameters

    if not product_id:
        return jsonify({"success": False, "message": "Product ID is required"}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch comments for the given productId
    cursor.execute("""
        SELECT u.UserName, r.Comment, r.Rating, r.DatePosted
        FROM Reviews r
        JOIN Users u ON r.UserID = u.UserID
        WHERE r.ProductID = ?
        ORDER BY r.DatePosted DESC
    """, (product_id,))
    
    comments = cursor.fetchall()
    cursor.close()
    conn.close()

    # Prepare comments data for frontend
    comment_list = [
        {
            "userName": comment.UserName,
            "comment": comment.Comment,
            "rating": comment.Rating,
            "datePosted": comment.DatePosted.strftime("%Y-%m-%d %H:%M:%S")
        }
        for comment in comments
    ]
    
    return jsonify({"success": True, "comments": comment_list}), 200
