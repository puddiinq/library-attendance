from flask import Flask, request
import sqlite3
from datetime import datetime
import re

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    """)
    return conn

@app.route("/")
def index():
    return """
    <h2>Library Attendance System</h2>
    <p>Enter your 8-digit Student ID</p>
    <form method="POST" action="/checkin">
        <input name="student_id" maxlength="8" required>
        <br><br>
        <button type="submit">Check In</button>
    </form>
    """

@app.route("/checkin", methods=["POST"])
def checkin():
    student_id = request.form["student_id"]

    if not re.fullmatch(r"\d{8}", student_id):
        return "<h3>Invalid Student ID. Must be 8 digits.</h3>"

    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM attendance WHERE student_id=? AND date=?",
        (student_id, today)
    )
    if cursor.fetchone():
        return "<h3>You already checked in today.</h3>"

    cursor.execute(
        "INSERT INTO attendance (student_id, date, time) VALUES (?, ?, ?)",
        (student_id, today, now_time)
    )

    conn.commit()
    conn.close()

    return "<h3>Check-in successful. Welcome to the library.</h3>"

@app.route("/admin")
def admin():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, date, time FROM attendance ORDER BY date DESC, time DESC")
    rows = cursor.fetchall()
    conn.close()

    table = ""
    for r in rows:
        table += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>"

    return f"""
    <h2>Attendance Records</h2>
    <table border="1">
        <tr><th>Student ID</th><th>Date</th><th>Time</th></tr>
        {table}
    </table>
    """

@app.route("/stats")
def stats():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM attendance")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT student_id) FROM attendance")
    unique = cursor.fetchone()[0]

    cursor.execute("SELECT date, COUNT(*) FROM attendance GROUP BY date ORDER BY date DESC")
    daily = cursor.fetchall()
    conn.close()

    rows = ""
    for d in daily:
        rows += f"<tr><td>{d[0]}</td><td>{d[1]}</td></tr>"

    return f"""
    <h2>Statistics</h2>
    <p>Total visits: {total}</p>
    <p>Unique students: {unique}</p>
    <table border="1">
        <tr><th>Date</th><th>Visits</th></tr>
        {rows}
    </table>
    """

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
