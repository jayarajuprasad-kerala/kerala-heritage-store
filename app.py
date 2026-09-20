import os
from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
DATABASE_URL = os.environ.get("DATABASE_URL")


def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            product TEXT NOT NULL,
            price TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price TEXT NOT NULL,
            category TEXT NOT NULL,
            image TEXT
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

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO orders (name, phone, address, product, price)
            VALUES (%s, %s, %s, %s, %s)
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

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM orders
        ORDER BY id DESC
    """)

    orders = cursor.fetchall()

    conn.close()

    return render_template("admin.html", orders=orders)


@app.route("/admin/products/add", methods=["POST"])
def add_product():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    price = request.form.get("price", "").strip()
    category = request.form.get("category", "").strip()
    image = request.form.get("image", "").strip()

    if not name or not description or not price or not category:
        return "Please fill in all required fields.", 400

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (name, description, price, category, image)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, description, price, category, image))

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)



