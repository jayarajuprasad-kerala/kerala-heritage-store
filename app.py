import os
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)

app.secret_key = "kerala-store-secret-key-change-later"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
DB = "orders.db"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            product TEXT NOT NULL,
            price TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/order/<product>/<price>", methods=["GET", "POST"])
def order(product, price):
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not phone or not address:
            return "Please fill in all the fields.", 400

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO orders (name, phone, address, product, price)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, address, product, price))

        order_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return render_template(
            "confirmed.html",
            name=name,
            phone=phone,
            address=address,
            product=product,
            price=price,
            order_id=order_id
        )

    return render_template("order.html", product=product, price=price)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

        return render_template("login.html", error="Incorrect password.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("login"))

@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    orders = conn.execute("""
        SELECT * FROM orders
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template("admin.html", orders=orders)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)


