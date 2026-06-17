import os
import mysql.connector
import random
import string
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for the entire app
CORS(app)

# Serve HTML files — Railway pe static files ke liye zaroori hai
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# MySQL Database Configuration
db_config = {
    "host": os.getenv("MYSQLHOST"),
    "user": os.getenv("MYSQLUSER"),
    "password": os.getenv("MYSQLPASSWORD"),
    "database": os.getenv("MYSQLDATABASE"),
    "port": int(os.getenv("MYSQLPORT", 3306))
}


# Function to create the users table if it doesn't exist
def create_users_table(cursor):
    try:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(8) PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            birthdate DATE NOT NULL
        );
        """
        cursor.execute(create_table_query)
        print("Users table created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")

# Function to create the expenses table if it doesn't exist
def create_expenses_table(cursor):
    try:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS expense (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            amount FLOAT NOT NULL,
            category VARCHAR(50) NOT NULL,
            date DATE NOT NULL
        );
        """
        cursor.execute(create_table_query)
        print("Expense table created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")

# Helper function to generate a random 8-digit user ID
def generate_user_id(cursor):
    while True:
        user_id = ''.join(random.choices(string.digits, k=8))
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = %s", (user_id,))
        if cursor.fetchone()[0] == 0:
            return user_id

# Signup route
@app.route('/signup', methods=['POST'])
def signup():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        create_users_table(cursor)

        username = request.json.get('username')
        password = request.json.get('password')
        birthdate = request.json.get('birthdate')

        if not username or not password or not birthdate:
            return jsonify({"error": "All fields are required!"}), 400

        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        if cursor.fetchone()[0] > 0:
            return jsonify({"error": "Username already exists!"}), 400

        user_id = generate_user_id(cursor)

        cursor.execute(
            "INSERT INTO users (user_id, username, password, birthdate) VALUES (%s, %s, %s, %s)",
            (user_id, username, password, birthdate)
        )
        connection.commit()

        return jsonify({"message": "Account created successfully!", "user_id": user_id}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Login route
@app.route('/login', methods=['POST'])
def login():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        username = request.json.get('username')
        password = request.json.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required!"}), 400

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and user[2] == password:
            return jsonify({"message": "Login successful!"}), 200
        else:
            return jsonify({"error": "Invalid username or password!"}), 400

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Route to add an expense
@app.route('/add_expense', methods=['POST'])
def add_expense():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        name = request.json.get('name')
        amount = request.json.get('amount')
        category = request.json.get('category')
        date = request.json.get('date')

        if not name or not amount or not category or not date:
            return jsonify({"error": "All fields are required!"}), 400

        cursor.execute(
            "INSERT INTO expense (name, amount, category, date) VALUES (%s, %s, %s, %s)",
            (name, amount, category, date)
        )
        connection.commit()

        return jsonify({"message": "Expense added successfully!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Route to fetch all expenses
@app.route('/get_expenses', methods=['GET'])
def get_expenses():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM expense")
        rows = cursor.fetchall()

        expenses = [
            {"id": row[0], "name": row[1], "amount": row[2], "category": row[3], "date": row[4].strftime('%Y-%m-%d')}
            for row in rows
        ]
        return jsonify(expenses)
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Route to delete an expense
@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("DELETE FROM expense WHERE id = %s", (expense_id,))
        connection.commit()

        return jsonify({"message": "Expense deleted successfully!"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == '__main__':
    # On Railway, tables create ho jayengi automatically first request pe
    # CREATE DATABASE ki zaroorat nahi — Railway MySQL already database provide karta hai
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        create_users_table(cursor)
        create_expenses_table(cursor)
        connection.commit()
        print("Tables initialized successfully.")
    except mysql.connector.Error as err:
        print(f"Error during startup: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080))
    )