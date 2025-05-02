from db import connect_db
from datetime import datetime

def add_item(name, price, quantity, supplier=None, category=None):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id, quantity FROM items WHERE name = ?', (name,))
    result = cursor.fetchone()

    if result:
        item_id, current_quantity = result
        new_quantity = current_quantity + quantity
        cursor.execute('UPDATE items SET quantity = ?, price = ? WHERE id = ?', 
                      (new_quantity, price, item_id))
    else:
        cursor.execute('''
            INSERT INTO items (name, price, quantity, supplier, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, price, quantity, supplier, category))
        item_id = cursor.lastrowid

    cursor.execute('''
        INSERT INTO receipts (item_id, quantity, receipt_date, supplier)
        VALUES (?, ?, ?, ?)
    ''', (item_id, quantity, datetime.now().isoformat(), supplier))

    conn.commit()
    conn.close()

def get_total_stock():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(quantity) FROM items')
    total_stock = cursor.fetchone()[0] or 0
    conn.close()
    return total_stock

def get_total_value():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(price * quantity) FROM items')
    total_value = cursor.fetchone()[0] or 0.0
    conn.close()
    return total_value

def update_item_quantity(name, new_quantity):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM items WHERE name = ?', (name,))
    result = cursor.fetchone()

    if result:
        item_id = result[0]
        cursor.execute('UPDATE items SET quantity = ? WHERE id = ?', (new_quantity, item_id))
        conn.commit()
    conn.close()

def check_low_stock():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.name, i.quantity, i.min_stock_level 
        FROM items i 
        WHERE i.quantity <= i.min_stock_level
    ''')
    low_stock_items = cursor.fetchall()
    conn.close()
    return low_stock_items

def search_items(name='', category=None, supplier=None, min_price=None, max_price=None, stock_level=None):
    conn = connect_db()
    cursor = conn.cursor()
    
    query = "SELECT id, name, price, quantity, supplier, category, min_stock_level FROM items"
    conditions = []
    params = []
    
    if name:
        conditions.append("name LIKE ?")
        params.append(f'%{name}%')
    
    if category:
        conditions.append("category = ?")
        params.append(category)
        
    if supplier:
        conditions.append("supplier LIKE ?")
        params.append(f'%{supplier}%')
    
    if min_price is not None:
        conditions.append("price >= ?")
        params.append(float(min_price))
    
    if max_price is not None:
        conditions.append("price <= ?")
        params.append(float(max_price))
    
    if stock_level:
        if stock_level == "Low":
            conditions.append("quantity <= min_stock_level")
        elif stock_level == "Medium":
            conditions.append("quantity BETWEEN min_stock_level+1 AND min_stock_level*4")
        elif stock_level == "High":
            conditions.append("quantity > min_stock_level*4")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

def get_receipt_history():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.name, r.quantity, r.receipt_date, r.supplier
        FROM receipts r
        JOIN items i ON r.item_id = i.id
        ORDER BY r.receipt_date DESC
    ''')
    history = cursor.fetchall()
    conn.close()
    return history


def add_new_item(name, price, quantity, supplier=None, category=None):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM items WHERE name = ?', (name,))
    if cursor.fetchone():
        conn.close()
        raise ValueError(f"Item '{name}' already exists.")

    cursor.execute('''
        INSERT INTO items (name, price, quantity, supplier, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, price, quantity, supplier, category))
    
    item_id = cursor.lastrowid

    cursor.execute('''
        INSERT INTO receipts (item_id, quantity, receipt_date, supplier)
        VALUES (?, ?, ?, ?)
    ''', (item_id, quantity, datetime.now().isoformat(), supplier))

    conn.commit()
    conn.close()

def get_all_categories():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM items WHERE category IS NOT NULL ORDER BY category')
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def add_stock_to_existing_item(name, quantity, new_price=None):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id, quantity, supplier FROM items WHERE name = ?', (name,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        raise ValueError(f"Item '{name}' does not exist.")

    item_id, current_quantity, supplier = result
    new_quantity = current_quantity + quantity

    if new_price is not None:
        cursor.execute('UPDATE items SET quantity = ?, price = ? WHERE id = ?', 
                     (new_quantity, new_price, item_id))
    else:
        cursor.execute('UPDATE items SET quantity = ? WHERE id = ?', 
                     (new_quantity, item_id))

    cursor.execute('''
        INSERT INTO receipts (item_id, quantity, receipt_date, supplier)
        VALUES (?, ?, ?, ?)
    ''', (item_id, quantity, datetime.now().isoformat(), supplier))

    conn.commit()
    conn.close()

def create_purchase_order(item_name, quantity, ordered_by):
    conn = connect_db()
    cursor = conn.cursor()
    
    # 1. Get current item details
    cursor.execute('SELECT id, quantity FROM items WHERE name = ?', (item_name,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        raise ValueError(f"Item '{item_name}' does not exist.")
    
    item_id, current_quantity = result
    
    # 2. Check if enough stock exists
    if current_quantity < quantity:
        conn.close()
        raise ValueError(f"Not enough stock. Only {current_quantity} available.")
    
    # 3. Reduce current stock
    new_quantity = current_quantity - quantity
    cursor.execute('UPDATE items SET quantity = ? WHERE id = ?', (new_quantity, item_id))
    
    # 4. Create the purchase order
    cursor.execute('''
        INSERT INTO purchases (item_id, quantity, purchase_date, ordered_by, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (item_id, quantity, datetime.now().isoformat(), ordered_by, 'Pending'))
    
    conn.commit()
    conn.close()

def receive_purchase_order(purchase_id):
    conn = connect_db()
    cursor = conn.cursor()

    # Get purchase order details
    cursor.execute('''
        SELECT p.item_id, p.quantity, i.supplier, i.name
        FROM purchases p
        JOIN items i ON p.item_id = i.id
        WHERE p.id = ?
    ''', (purchase_id,))
    purchase = cursor.fetchone()

    if not purchase:
        conn.close()
        raise ValueError("Purchase order not found")

    item_id, quantity, supplier, item_name = purchase

    # Update item quantity
    cursor.execute('UPDATE items SET quantity = quantity + ? WHERE id = ?', 
                  (quantity, item_id))

    # Update purchase status
    cursor.execute('UPDATE purchases SET status = ? WHERE id = ?', 
                  ('Received', purchase_id))

    # Add to receipts
    cursor.execute('''
        INSERT INTO receipts (item_id, quantity, receipt_date, supplier)
        VALUES (?, ?, ?, ?)
    ''', (item_id, quantity, datetime.now().isoformat(), supplier))

    conn.commit()
    conn.close()
    return item_name, quantity

def get_pending_orders():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, i.name, p.quantity, p.purchase_date, p.ordered_by
        FROM purchases p
        JOIN items i ON p.item_id = i.id
        WHERE p.status = 'Pending'
        ORDER BY p.purchase_date DESC
    ''')
    orders = cursor.fetchall()
    conn.close()
    return orders

def get_purchase_history():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.name, p.quantity, p.purchase_date, p.ordered_by, p.status
        FROM purchases p
        JOIN items i ON p.item_id = i.id
        ORDER BY p.purchase_date DESC
    ''')
    history = cursor.fetchall()
    conn.close()
    return history