from flask import Flask, render_template_string, request, redirect, url_for
import os
from dotenv import load_dotenv
import aiosqlite
import asyncio

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this

# Simple auth (replace with proper auth)
ADMIN_PASSWORD = 'admin'  # Change this

HTML_LOGIN = """
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <form method="post">
        Password: <input type="password" name="password">
        <input type="submit">
    </form>
</body>
</html>
"""

HTML_DASHBOARD = """
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
    <h1>ChefBot Dashboard</h1>
    <p>Uptime: {{ uptime }}</p>
    <p>Latency: {{ latency }}ms</p>
    <h2>Recent Logs</h2>
    <ul>
    {% for log in logs %}
        <li>{{ log[0] }}: {{ log[1] }}</li>
    {% endfor %}
    </ul>
    <h2>Infractions</h2>
    <ul>
    {% for inf in infractions %}
        <li>{{ inf[0] }}: {{ inf[1] }}</li>
    {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            return redirect(url_for('main'))
        return render_template_string(HTML_LOGIN)
    return render_template_string(HTML_LOGIN)

@app.route('/main')
def main():
    # Mock data - in real, fetch from DB
    uptime = '10:30:45'
    latency = 50
    logs = [('ban', 'User banned'), ('warn', 'User warned')]
    infractions = [('warn', 'Spam'), ('mute', 'Bad language')]
    return render_template_string(HTML_DASHBOARD, uptime=uptime, latency=latency, logs=logs, infractions=infractions)

if __name__ == '__main__':
    app.run(debug=True)