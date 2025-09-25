import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pathlib import Path
from functools import wraps
from datetime import datetime

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "ecommerce.db"

app = Flask(__name__)
app.secret_key = "dev-please-change"  # simple for class demo

# ---------------------- Helpers ----------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db_if_missing():
    if not DB_PATH.exists():
        from schema import create_schema, seed_data
        create_schema(DB_PATH)
        seed_data(DB_PATH)

def login_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = session.get("user")
            if not user:
                flash("Please log in first.", "warning")
                return redirect(url_for("login", next=request.path))
            if role and user.get("role") != role:
                flash("You do not have permission to view that page.", "danger")
                return redirect(url_for("index"))
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# ---------------------- Routes ----------------------
@app.route("/")
def index():
    init_db_if_missing()
    q = request.args.get("q", "").strip()
    conn = get_db()
    if q:
        rows = conn.execute(
            "SELECT * FROM products WHERE name LIKE ? OR description LIKE ? ORDER BY id DESC",
            (f"%{q}%", f"%{q}%"),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    return render_template("index.html", products=rows, q=q)

# --- Auth (super simple, plaintext for class only) ---
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]  # PLAINTEXT ON PURPOSE (class demo)
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        address = request.form.get("address","").strip()
        if not username or not password:
            flash("Username and password are required.", "warning")
            return redirect(url_for("signup"))
        conn = get_db()
        cur = conn.cursor()
        exists = cur.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone()
        if exists:
            flash("Username already taken.", "danger")
            return redirect(url_for("signup"))
        cur.execute(
            "INSERT INTO users(username, password, name, email, address, role) VALUES(?,?,?,?,?,?)",
            (username, password, name, email, address, "customer"),
        )
        conn.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        conn = get_db()
        row = conn.execute(
            "SELECT id, username, role, name, email, address FROM users WHERE username=? AND password=?",
            (username, password),
        ).fetchone()
        if row:
            session["user"] = dict(row)
            flash(f"Welcome, {row['username']}!", "success")
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
        flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

# --- Account management (customer) ---
@app.route("/account", methods=["GET", "POST"])
def account():
    user = session.get("user")
    if not user:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    conn = get_db()
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        address = request.form.get("address","").strip()
        conn.execute(
            "UPDATE users SET name=?, email=?, address=? WHERE id=?",
            (name, email, address, user["id"]),
        )
        conn.commit()
        # refresh session copy
        row = conn.execute(
            "SELECT id, username, role, name, email, address FROM users WHERE id=?",
            (user["id"],),
        ).fetchone()
        session["user"] = dict(row)
        flash("Account updated.", "success")
    return render_template("account.html", user=session["user"])

# --- Cart ---
def _get_cart():
    return session.setdefault("cart", {})

@app.route("/add_to_cart/<int:pid>")
def add_to_cart(pid):
    cart = _get_cart()
    cart[str(pid)] = cart.get(str(pid), 0) + 1
    session["cart"] = cart
    flash("Added to cart.", "success")
    return redirect(request.referrer or url_for("index"))

@app.route("/cart")
def cart():
    cart = _get_cart()
    if not cart:
        return render_template("cart.html", items=[], total=0.0)
    conn = get_db()
    ids = tuple(int(k) for k in cart.keys())
    qmarks = ",".join(["?"] * len(ids))
    rows = conn.execute(f"SELECT * FROM products WHERE id IN ({qmarks})", ids).fetchall()
    items = []
    total = 0.0
    for r in rows:
        qty = cart.get(str(r["id"]), 0)
        line_total = qty * r["price"]
        total += line_total
        items.append({"product": r, "qty": qty, "line_total": line_total})
    return render_template("cart.html", items=items, total=total)

@app.route("/remove_from_cart/<int:pid>")
def remove_from_cart(pid):
    cart = _get_cart()
    cart.pop(str(pid), None)
    session["cart"] = cart
    return redirect(url_for("cart"))

# --- Checkout (guest or logged-in) ---
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = _get_cart()
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("index"))
    conn = get_db()
    # Build cart display
    ids = tuple(int(k) for k in cart.keys())
    qmarks = ",".join(["?"] * len(ids))
    rows = conn.execute(f"SELECT * FROM products WHERE id IN ({qmarks})", ids).fetchall()
    items = []
    total = 0.0
    for r in rows:
        qty = cart.get(str(r["id"]), 0)
        line_total = qty * r["price"]
        total += line_total
        items.append({"product": r, "qty": qty, "line_total": line_total})

    if request.method == "POST":
        # If logged-in, prefer stored info unless form overrides
        user = session.get("user")
        name = request.form.get("name", user["name"] if user else "").strip()
        email = request.form.get("email", user["email"] if user else "").strip()
        address = request.form.get("address", user["address"] if user else "").strip()

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders(user_id, guest_name, guest_email, guest_address, status, created_at) VALUES(?,?,?,?,?,?)",
            (user["id"] if user else None, name, email, address, "Open", datetime.utcnow().isoformat()),
        )
        order_id = cur.lastrowid
        # Items
        for r in rows:
            qty = cart.get(str(r["id"]), 0)
            if qty <= 0:
                continue
            cur.execute(
                "INSERT INTO order_items(order_id, product_id, quantity, unit_price) VALUES(?,?,?,?)",
                (order_id, r["id"], qty, r["price"]),
            )
        conn.commit()
        session["cart"] = {}
        flash(f"Order #{order_id} placed! You'll get an email (pretend) when it ships.", "success")
        return redirect(url_for("index"))

    # GET
    user = session.get("user")
    return render_template("checkout.html", items=items, total=total, user=user)

# --- Staff order processing ---
@app.route("/fulfill")
def fulfill():
    user = session.get("user")
    if not (user and user.get("role") == "staff"):
        flash("Staff only.", "danger")
        return redirect(url_for("index"))
    conn = get_db()
    rows = conn.execute(
        "SELECT o.*, COALESCE(u.username, '(guest)') AS username FROM orders o LEFT JOIN users u ON o.user_id = u.id ORDER BY o.id DESC"
    ).fetchall()
    return render_template("fulfill.html", orders=rows)

@app.route("/advance/<int:order_id>")
def advance(order_id):
    user = session.get("user")
    if not (user and user.get("role") == "staff"):
        flash("Staff only.", "danger")
        return redirect(url_for("index"))
    conn = get_db()
    row = conn.execute("SELECT id, status FROM orders WHERE id=?", (order_id,)).fetchone()
    if not row:
        flash("Order not found.", "warning")
        return redirect(url_for("fulfill"))
    next_map = {"Open": "Ready", "Ready": "Shipped", "Shipped": "Picked-up", "Picked-up": "Picked-up"}
    new_status = next_map.get(row["status"], "Open")
    conn.execute("UPDATE orders SET status=? WHERE id=?", (new_status, order_id))
    conn.commit()
    flash(f"Order {order_id} moved to {new_status}.", "success")
    return redirect(url_for("fulfill"))

# --- My Orders (customer) ---
@app.route("/my_orders")
def my_orders():
    user = session.get("user")
    if not user:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    conn = get_db()
    rows = conn.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (user["id"],)).fetchall()
    return render_template("my_orders.html", orders=rows)

if __name__ == "__main__":
    init_db_if_missing()
    app.run(debug=True)
