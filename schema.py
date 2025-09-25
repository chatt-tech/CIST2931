import sqlite3
from pathlib import Path

def create_schema(db_path: Path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            email TEXT,
            address TEXT,
            role TEXT NOT NULL DEFAULT 'customer'
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            guest_name TEXT,
            guest_email TEXT,
            guest_address TEXT,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    conn.close()

def seed_data(db_path: Path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Staff account (plaintext password for class demo)
    cur.execute(
        "INSERT OR IGNORE INTO users(username, password, name, email, address, role) VALUES(?,?,?,?,?,?)",
        ("staff", "staff", "Order Processor", "staff@example.com", "Warehouse Lane", "staff"),
    )

    products = [
        ("Laptop Pro 14", "14-inch laptop with 16GB RAM, 512GB SSD", 1299.00, 10),
        ("Gaming Desktop X", "Ryzen 7, RTX 4070, 32GB RAM, 1TB SSD", 1899.99, 5),
        ("27\" 4K Monitor", "IPS, 60Hz, HDR10", 329.00, 15),
        ("Laser Printer 2000", "Fast B/W laser printer", 149.99, 20),
        ("Wireless Mouse", "Ergonomic 2.4GHz mouse", 24.99, 50),
        ("Mechanical Keyboard", "RGB backlit, blue switches", 79.99, 30),
    ]
    cur.executemany(
        "INSERT INTO products(name, description, price, stock) VALUES(?,?,?,?)",
        products,
    )
    conn.commit()
    conn.close()
