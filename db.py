import sqlite3

def connect_db():
    return sqlite3.connect('data/inventory.db')

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        supplier TEXT,
        category TEXT,
        min_stock_level INTEGER DEFAULT 5
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        quantity INTEGER,
        receipt_date TEXT,
        supplier TEXT,
        FOREIGN KEY (item_id) REFERENCES items(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        quantity INTEGER,
        purchase_date TEXT,
        ordered_by TEXT,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (item_id) REFERENCES items(id)
    )
    ''')

    conn.commit()
    conn.close()