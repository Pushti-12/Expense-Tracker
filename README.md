# Money Mentor - Expense Tracker

A web-based expense tracking application with a built-in chatbot, 
user authentication, and MySQL database integration.

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Database:** MySQL
- **Other:** Keyword-based Chatbot

## Features
- User Registration & Login
- Expense Tracking Dashboard
- Keyword-based Chatbot Assistant
- FAQ & Blog Pages
- Forgot Password Flow

## How to Run

### Prerequisites
- Python 3.x
- MySQL
- VS Code

### Steps
1. Open `combined_operation.py` in VS Code and run it
2. Open chatbot folder → right click → Open with Terminal
3. Type: `python -m http.server 8000`
4. Open browser and go to: `http://127.0.0.1:8000`

### Database Setup (MySQL)
1. Press `Windows + R` → type `cmd` → Enter
2. Type: `mysql -u root -p`
3. Enter your MySQL password
4. Type: `USE money_mentor;`
5. View users: `SELECT * FROM users;`
6. View expenses: `SELECT * FROM expenses;`

## Project Structure
- `index.html` - Landing page
- `sign_up.html` - Registration page
- `dashboard.html` - Expense dashboard
- `chatbot.html` - Chatbot interface
- `combined_operation.py` - Backend server
