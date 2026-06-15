import mysql.connector
import random
import string
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import Flask-CORS

app = Flask(__name__)

# Enable CORS for the entire app
CORS(app)

# MySQL Database Configuration
db_config = {
import os

db_config = {
    "host": os.getenv("mysql.railway.internal"),
    "user": os.getenv("root"),
    "password": os.getenv("CoApIQHWDEUjQTFEMAhodpmeOuTpxNmn"),
    "database": os.getenv("railway"),
    "port": int(os.getenv("MYSQLPORT", 3306))
}
}

# Function to create the database if it doesn't exist
def create_database(cursor):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        print(f"Database {db_config['database']} created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")

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
        if cursor.fetchone()[0] == 0:  # Ensure it's unique
            return user_id

# Signup route
@app.route('/signup', methods=['POST'])
def signup():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Create the table if it doesn't exist
        create_users_table(cursor)

        # Retrieve form data
        username = request.json.get('username')
        password = request.json.get('password')
        birthdate = request.json.get('birthdate')

        # Validate inputs
        if not username or not password or not birthdate:
            return jsonify({"error": "All fields are required!"}), 400

        # Check if username already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        if cursor.fetchone()[0] > 0:
            return jsonify({"error": "Username already exists!"}), 400

        # Generate unique user ID
        user_id = generate_user_id(cursor)

        # Insert user into database
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
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Retrieve form data
        username = request.json.get('username')
        password = request.json.get('password')

        # Validate inputs
        if not username or not password:
            return jsonify({"error": "Username and password are required!"}), 400

        # Check if username exists and password matches
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and user[2] == password:  # Compare passwords
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
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Retrieve form data
        name = request.json.get('name')
        amount = request.json.get('amount')
        category = request.json.get('category')
        date = request.json.get('date')

        # Validate inputs
        if not name or not amount or not category or not date:
            return jsonify({"error": "All fields are required!"}), 400

        # Insert the expense into the database
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
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Retrieve all expenses from the database
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
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Delete the expense from the database
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
    try:
        # Connect to MySQL and create database and tables if they don't exist
        connection = mysql.connector.connect(host=db_config['host'], user=db_config['user'], password=db_config['password'])
        cursor = connection.cursor()

        # Create the database if it doesn't exist
        create_database(cursor)

        # Select the database explicitly
        cursor.execute(f"USE {db_config['database']}")

        # Create the users and expenses tables if they don't exist
        create_users_table(cursor)
        create_expenses_table(cursor)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    # Run the Flask application
    app.run(debug=True)
