"""
Local development server that simulates the demo challenge without Docker.
This allows testing the agent when Docker is not available.
"""
from flask import Flask, request, render_template_string, jsonify
import sqlite3
import os

app = Flask(__name__)

# Read or create flag
FLAG = "CTF{demo_sql_injection_flag_12345}"

# Simple vulnerable login page
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Demo CTF Challenge</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        h1 { color: #333; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; }
        input { width: 100%; padding: 8px; box-sizing: border-box; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .message { margin: 15px 0; padding: 10px; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .hint { background: #fff3cd; color: #856404; padding: 10px; margin: 15px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Demo CTF Challenge</h1>
        <p>Welcome to the demo CTF challenge! This is a simple login page.</p>
        <div class="hint">
            <strong>Hint:</strong> The admin password is stored in the database. Try to find it!
        </div>
        {% if message %}
        <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
        <p style="margin-top: 20px; font-size: 12px; color: #666;">
            Note: This is an intentionally vulnerable application for educational purposes only.
        </p>
    </div>
</body>
</html>
"""

def init_db():
    """Initialize the database with vulnerable setup"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            is_admin INTEGER DEFAULT 0
        )
    ''')

    # Insert default users (including admin)
    cursor.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                   ('admin', 'admin123', 1))
    cursor.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                   ('user', 'password', 0))

    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # VULNERABLE: Direct string concatenation (SQL injection)
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        user = cursor.fetchone()

        conn.close()

        if user:
            user_id, user_name, user_pass, is_admin = user
            if is_admin:
                return render_template_string(
                    LOGIN_TEMPLATE,
                    message=f"Welcome Admin! Here is your flag: {FLAG}",
                    message_type="success"
                )
            else:
                return render_template_string(
                    LOGIN_TEMPLATE,
                    message="Login successful, but you're not admin!",
                    message_type="success"
                )
        else:
            return render_template_string(
                LOGIN_TEMPLATE,
                message="Invalid credentials",
                message_type="error"
            )

    except Exception as e:
        return render_template_string(
            LOGIN_TEMPLATE,
            message=f"Error: {str(e)}",
            message_type="error"
        )

@app.route('/flag')
def flag():
    return "Try to login as admin to get the flag!"

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "flag_available": bool(FLAG)})

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    print("Starting local demo challenge server on http://localhost:8000")
    print("Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=8000, debug=False)
