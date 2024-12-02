import sqlite3
import os
import shutil
import qr_code_util

DB_PATH = "./bicycle_shop/bicycle_shop.db"
PRODUCTS_DIR = "./bicycle_shop/Products"

def get_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def create_tables():
    """Create necessary database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            first_name TEXT,
            last_name TEXT,
            password BLOB,
            salt BLOB,
            age INTEGER,
            is_admin INTEGER DEFAULT 0,
            password_changed INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            qr_code TEXT,
            listed INTEGER DEFAULT 0,
            description TEXT,
            category_id INTEGER,
            image TEXT,
            stock INTEGER,
            FOREIGN KEY (category_id) REFERENCES Categories(id)
        )
    ''')
    conn.commit()
    conn.close()

def initialize_admin():
    """Create a default admin user if none exists."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Users WHERE is_admin = 1")
    if not cursor.fetchone():  # No admin user exists
        from auth import hash_password
        salt, hashed_password = hash_password("admin123")
        cursor.execute("""
            INSERT INTO Users (username, first_name, last_name, password, salt, age, is_admin, password_changed) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("admin", "Admin", "User", hashed_password, salt, 30, 1, 0))
        conn.commit()

    conn.close()

def promote_user_to_admin(user_id):
    """Promote a user to admin."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET is_admin = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def demote_user_from_admin(user_id, current_admin_id):
    """Demote a user from admin."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if the user to be demoted is the current admin
    if user_id == current_admin_id:
        conn.close()
        return "You cannot demote yourself."

    # Check if there is more than one admin
    cursor.execute("SELECT COUNT(*) FROM Users WHERE is_admin = 1")
    admin_count = cursor.fetchone()[0]
    if admin_count <= 1:
        conn.close()
        return "There must be at least one admin."

    cursor.execute("UPDATE Users SET is_admin = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return "User demoted successfully."

def add_product(name, price, qr_code, listed, description, category_id, image, stock):
    """Add a new product to the database."""
    product_dir = os.path.join(PRODUCTS_DIR, name)
    os.makedirs(product_dir, exist_ok=True)
    
    qr_code_path = os.path.join(product_dir, os.path.basename(qr_code))
    image_path = os.path.join(product_dir, os.path.basename(image)) if image else None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Products (name, price, qr_code, listed, description, category_id, image, stock) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, price, qr_code_path, listed, description, category_id, image_path, stock))
    conn.commit()
    conn.close()

def update_product(product_id, name, price, qr_code, description, category_id, image, stock):
    """Update an existing product in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, qr_code, image FROM Products WHERE id = ?", (product_id,))
    old_product = cursor.fetchone()
    old_name, old_qr_code, old_image = old_product

    old_product_dir = os.path.join(PRODUCTS_DIR, old_name)
    new_product_dir = os.path.join(PRODUCTS_DIR, name)
    
    qr_code_path = os.path.join(new_product_dir, f"{name}_{price}.png")
    
    # Delete the old QR code file if it still exists
    if old_qr_code and os.path.exists(old_qr_code):
        os.remove(old_qr_code)
    
    # Rename the product directory if the name has changed
    if old_name != name:
        os.rename(old_product_dir, new_product_dir)
    
    # Generate the new QR code
    qr_code_util.generate_qr_code(f"{name}_{price}", qr_code_path)

    # Handle the image file
    if image and os.path.exists(image):
        image_dest = os.path.join(new_product_dir, os.path.basename(image))
        if old_image and os.path.exists(old_image) and old_image != image_dest:
            os.remove(old_image)
        shutil.copy(image, image_dest)
        image = image_dest

    cursor.execute("""
        UPDATE Products SET name = ?, price = ?, qr_code = ?, description = ?, category_id = ?, image = ?, stock = ? 
        WHERE id = ?
    """, (name, price, qr_code_path, description, category_id, image, stock, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    """Delete a product from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM Products WHERE id = ?", (product_id,))
    product_name = cursor.fetchone()[0]
    product_dir = os.path.join(PRODUCTS_DIR, product_name)
    
    cursor.execute("DELETE FROM Products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    
    if os.path.exists(product_dir):
        shutil.rmtree(product_dir)

def list_product(product_id, listed):
    """List or delist a product."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Products SET listed = ? WHERE id = ?", (listed, product_id))
    conn.commit()
    conn.close()

# Add a function to retrieve all products wanted to be listed from the database
def get_products(listed_only=True):
    """Retrieve all products from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    if listed_only:
        cursor.execute("SELECT * FROM Products WHERE listed = 1")
    else:
        cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    conn.close()
    return products

def get_product_by_id(product_id):
    """Retrieve a product by its ID from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def add_category(name):
    """Add a new category to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_categories():
    """Retrieve all categories from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Categories")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def get_category_id(name):
    """Retrieve the ID of a category by its name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Categories WHERE name = ?", (name,))
    category = cursor.fetchone()
    conn.close()
    return category[0] if category else None

def get_category_name(category_id):
    """Retrieve the name of a category by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Categories WHERE id = ?", (category_id,))
    category = cursor.fetchone()
    conn.close()
    return category[0] if category else None