import requests
import os
import mysql.connector
import random
import string
import urllib.parse
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for the entire app
CORS(app)

# Serve HTML files — Railway pe static files ke liye zaroori hai
@app.route('/')
def index():
    return send_from_directory('.', 'landing.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# MySQL Database Configuration
# Railway may provide either individual MySQL env vars or a single connection URL.

def parse_mysql_url(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("mysql", "mysql+mysqlconnector", "mysql+pymysql"):
        raise ValueError(f"Unsupported DB URL scheme: {parsed.scheme}")

    return {
        "host": parsed.hostname,
        "user": urllib.parse.unquote(parsed.username) if parsed.username else None,
        "password": urllib.parse.unquote(parsed.password) if parsed.password else None,
        "database": parsed.path.lstrip('/') if parsed.path else None,
        "port": parsed.port or 3306,
    }


def build_db_config():
    host = os.getenv("MYSQLHOST") or os.getenv("MYSQL_HOST")
    user = os.getenv("MYSQLUSER") or os.getenv("MYSQL_USER")
    password = os.getenv("MYSQLPASSWORD") or os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DATABASE") or os.getenv("MYSQL_DB")
    port = os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT")

    if not (host and user and password and database):
        mysql_url = os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL") or os.getenv("CLEARDB_DATABASE_URL")
        if mysql_url:
            return parse_mysql_url(mysql_url)

    return {
        "host": host,
        "user": user,
        "password": password,
        "database": database,
        "port": int(port) if port else 3306,
    }


db_config = build_db_config()


def get_db_connection():
    missing = [k for k, v in db_config.items() if k != "port" and not v]
    if missing:
        raise RuntimeError(f"Missing database environment variables: {missing}")

    return mysql.connector.connect(**db_config)


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
            user_id VARCHAR(8) NOT NULL,
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
        connection = get_db_connection()
        cursor = connection.cursor()

        username = request.json.get('username')
        password = request.json.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required!"}), 400

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and user[2] == password:
            return jsonify({"message": "Login successful!", "userId": user[0]}), 200
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
        connection = get_db_connection()
        cursor = connection.cursor()

        name = request.json.get('name')
        amount = request.json.get('amount')
        category = request.json.get('category')
        date = request.json.get('date')
        user_id = request.json.get('user_id')

        if not name or not amount or not category or not date or not user_id:
            return jsonify({"error": "All fields are required!"}), 400

        cursor.execute(
            "INSERT INTO expense (user_id, name, amount, category, date) VALUES (%s, %s, %s, %s, %s)",
            (user_id, name, amount, category, date)
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
        connection = get_db_connection()
        cursor = connection.cursor()

        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id required"}), 400

        cursor.execute("SELECT * FROM expense WHERE user_id = %s", (user_id,))
        rows = cursor.fetchall()

        expenses = [
            {"id": row[0], "name": row[2], "amount": row[3], "category": row[4], "date": row[5].strftime('%Y-%m-%d')}
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
        connection = get_db_connection()
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
#Route for chatbot using Gemini API
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"You are a helpful personal finance assistant called Money Mentor. Answer only finance related questions briefly. User asked: {user_message}"
                }]
            }]
        }
        
        response = requests.post(gemini_url, json=payload)
        data = response.json()
        bot_reply = data['candidates'][0]['content']['parts'][0]['text']
        
        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"reply": "Sorry, I couldn't process that. Please try again."}), 500


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

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080))
    )