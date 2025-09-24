# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "employees.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS employee (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        dob DATE,
        address TEXT,
        join_date DATE,
        basic_salary REAL,
        da REAL
      )
    """)
    conn.commit()
    conn.close()

def compute_gratuity(join_date: datetime, exit_date: datetime, basic: float, da: float) -> float:
    """Compute gratuity based on join and exit date, basic salary + DA."""
    # compute difference in years and months
    total_days = (exit_date - join_date).days
    # approximate years and months
    years = exit_date.year - join_date.year
    months = exit_date.month - join_date.month
    days = exit_date.day - join_date.day
    if days < 0:
        months -= 1
    if months < 0:
        years -= 1
        months += 12

    # rounding: if months >= 6, round up one more year
    if months >= 6:
        years += 1

    # only eligible if years >= 5
    if years < 5:
        return 0.0

    b = basic + da
    gratuity = years * b * (15.0 / 26.0)
    return gratuity

@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employee")
    rows = cur.fetchall()
    conn.close()
    return render_template("index.html", employees=rows)

@app.route("/add", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        name = request.form["name"]
        dob = request.form["dob"]  # yyyy-mm-dd
        address = request.form["address"]
        join_date = request.form["join_date"]
        basic = float(request.form["basic_salary"])
        da = float(request.form["da"])
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
          INSERT INTO employee (name, dob, address, join_date, basic_salary, da)
          VALUES (?, ?, ?, ?, ?, ?)
        """, (name, dob, address, join_date, basic, da))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/view/<int:emp_id>")
def view_employee(emp_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employee WHERE id = ?", (emp_id,))
    emp = cur.fetchone()
    conn.close()
    if not emp:
        return "Employee not found", 404

    join_date = datetime.strptime(emp["join_date"], "%Y-%m-%d")
    exit_date = datetime.today()  # or you may allow entering an exit/leave date
    gratuity = compute_gratuity(join_date, exit_date, emp["basic_salary"], emp["da"])
    return render_template("view.html", emp=emp, gratuity=gratuity)

if __name__ == "__main__":
    init_db()
    app.run(host = "0.0.0.0", port = 5001)