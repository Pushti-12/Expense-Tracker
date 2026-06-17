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
For local development you can use MySQL as usual, but for Railway deployment you should connect to Railway's MySQL addon.

### Deploying on Railway
1. Sign in to Railway and create a new project.
2. Connect your GitHub repo or deploy from this folder.
3. Add a MySQL plugin in Railway.
4. Set environment variables in Railway if not automatically provided:
   - `MYSQL_HOST`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DATABASE`
   - `MYSQL_PORT`
5. Railway will set the `PORT` env var automatically.
6. Railway detects `requirements.txt`, then uses either `Procfile` or `railway.json` to start the app.
7. Access the deployed app using the Railway project URL.

## Project Structure
- `index.html` - Landing page
- `sign_up.html` - Registration page
- `dashboard.html` - Expense dashboard
- `chatbot.html` - Chatbot interface
- `combined_operation.py` - Backend server
