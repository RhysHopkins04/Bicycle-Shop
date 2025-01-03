import sqlite3
import os
import shutil

from file_manager import handle_product_directory, handle_product_image, handle_qr_code, cleanup_old_product_files, rename_product_directory, get_paths, get_absolute_path

DB_PATH = get_absolute_path('./bicycle_shop.db')

# Core Functionality for the DB:
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

# User Managemnt Functions:
def initialize_admin():
    """Create a default admin user if none exists."""
    from file_manager import is_first_run

    # Only create admin if initialization is complete (second layer of checks to ensure it doesnt generate without config.ini being reviewed)
    if is_first_run():
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Users WHERE is_admin = 1")
    if not cursor.fetchone():  # No admin user exists
        from auth import hash_password
        from file_manager import get_default_admin

        # Get default admin settings from config.ini
        admin_settings = get_default_admin()

        salt, hashed_password = hash_password(admin_settings['password'])

        cursor.execute("""
            INSERT INTO Users (username, first_name, last_name, password, salt, age, is_admin, password_changed) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            admin_settings['username'],
            admin_settings['first_name'], 
            admin_settings['last_name'],
            hashed_password,
            salt,
            admin_settings['age'],
            1,  # is_admin
            0   # password_changed (force password change on first login)))
        ))
        conn.commit()
    conn.close()

# Product Management Functions:
def add_product(name, price, qr_code, listed, description, category_id, image, stock):
    """Add a new product to the database."""
    product_dir = handle_product_directory(name)
    qr_code_path = handle_qr_code(name, price, product_dir)
    image_path = handle_product_image(image, product_dir) if image else None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Products (name, price, qr_code, listed, description, category_id, image, stock) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, price, qr_code_path, listed, description, category_id, image_path, stock))
    conn.commit()
    conn.close()

def update_product(product_id, name, price, qr_code, description, category_id, image, stock, keep_image=False, keep_qr=False):
    """Update product with enhanced error handling and file management"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get current product state
        cursor.execute("SELECT * FROM Products WHERE id = ?", (product_id,))
        current_product = cursor.fetchone()
        
        if not current_product:
            raise ValueError("Product not found")

        # Check what needs updating
        needs_name_update = name != current_product[1]
        needs_price_update = abs(float(price) - float(current_product[2])) > 0.001
        needs_new_qr = (needs_name_update or needs_price_update) and not keep_qr
        needs_image_update = image and image != current_product[7] and not keep_image

        # Create new directory if name is changing
        product_dir = os.path.join(get_paths()['products_dir'], name)
        if needs_name_update:
            os.makedirs(product_dir, exist_ok=True)
        else:
            product_dir = os.path.join(get_paths()['products_dir'], current_product[1])

        # Handle new image update first
        new_image_path = current_product[7]
        if needs_image_update:
            # Don't copy old image if we're updating it
            new_image_path = handle_product_image(image, product_dir)
            # Remove old image if it exists
            if current_product[7] and os.path.exists(current_product[7]):
                try:
                    os.remove(current_product[7])
                except OSError as e:
                    print(f"Error removing old image: {e}")
        elif needs_name_update and current_product[7] and not needs_image_update:
            # Only copy existing image if we're not updating it
            old_image_name = os.path.basename(current_product[7])
            new_image_path = os.path.join(product_dir, old_image_name)
            if os.path.exists(current_product[7]):
                shutil.copy2(current_product[7], new_image_path)

        # Handle QR code
        new_qr_path = current_product[3]
        if needs_new_qr:
            new_qr_path = handle_qr_code(name, price, product_dir)
        elif not os.path.exists(current_product[3]):
            new_qr_path = handle_qr_code(name, price, product_dir)

        # Update database first
        cursor.execute("""
            UPDATE Products 
            SET name = ?, price = ?, qr_code = ?, description = ?, 
                category_id = ?, image = ?, stock = ?
            WHERE id = ?
        """, (name, price, new_qr_path, description, 
              category_id, new_image_path, stock, product_id))
        
        # Clean up old directory after successful database update
        if needs_name_update:
            old_dir = os.path.join(get_paths()['products_dir'], current_product[1])
            if os.path.exists(old_dir):
                try:
                    shutil.rmtree(old_dir)
                except OSError as e:
                    print(f"Error removing old directory: {e}")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_product(product_id):
    """Delete a product from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM Products WHERE id = ?", (product_id,))
    product_name = cursor.fetchone()[0]
    paths = get_paths()
    product_dir = os.path.join(paths['products_dir'], product_name)
    
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

# Category Management Functions:
def add_category(name):
    """Add a new category to the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Categories (name) VALUES (?)", (name,))
        conn.commit()
        return True, "Category added successfully!"
    except sqlite3.IntegrityError:
        return False, "Category name already exists."
    except sqlite3.Error as e:
        return False, f"Failed to add category: {str(e)}"
    finally:
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

def update_category(category_id, new_name):
    """Update category name in database"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Categories SET name = ? WHERE id = ?", (new_name, category_id))
        conn.commit()
        return True, "Category updated successfully!"
    except sqlite3.Error as e:
        return False, f"Failed to update category: {str(e)}"
    finally:
        conn.close()

def delete_category(category_id):
    """Delete category from database and unlist associated products."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # First update all products in this category
        cursor.execute("""
            UPDATE Products 
            SET listed = 0, category_id = NULL 
            WHERE category_id = ?
        """, (category_id,))
        
        # Then delete the category
        cursor.execute("DELETE FROM Categories WHERE id = ?", (category_id,))
        conn.commit()
        return True, "Category deleted successfully and associated products unlisted!"
    except sqlite3.Error as e:
        return False, f"Failed to delete category: {str(e)}"
    finally:
        conn.close()