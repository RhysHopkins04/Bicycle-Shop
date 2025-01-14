import sqlite3
import os
import shutil

from file_manager import handle_product_directory, handle_product_image, handle_qr_code, cleanup_old_product_files, rename_product_directory, get_paths, get_absolute_path, handle_discount_qr_code, cleanup_old_discount_qr

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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ShoppingCart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(id),
            FOREIGN KEY (product_id) REFERENCES Products(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Discounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            percentage INTEGER NOT NULL,
            qr_code_path TEXT,
            uses INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1
        )
    """)

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

def get_current_user_admin_status(username):
    """
    Check if user has admin privileges
    Args:
        username (str): Username to check
    Returns:
        bool: True if user is admin, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT is_admin FROM Users WHERE username = ?", (username,))
        result = cursor.fetchone()
        return bool(result[0]) if result else False
    finally:
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

# User management functions:
def get_all_users():
    """Retrieve all users from database ordered by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, username, first_name, last_name, age, is_admin 
            FROM Users 
            ORDER BY id
        """)
        return cursor.fetchall()
    finally:
        conn.close()

def update_user_details(user_id, first_name, last_name, age, is_admin):
    """Update user details in database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Don't allow removing last admin
        if not is_admin:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE is_admin = 1")
            admin_count = cursor.fetchone()[0]
            cursor.execute("SELECT is_admin FROM Users WHERE id = ?", (user_id,))
            current_is_admin = cursor.fetchone()[0]
            if admin_count <= 1 and current_is_admin:
                return False, "Cannot remove last admin user"

        cursor.execute("""
            UPDATE Users 
            SET first_name = ?, 
                last_name = ?, 
                age = ?,
                is_admin = ?
            WHERE id = ?
        """, (first_name, last_name, age, is_admin, user_id))
        conn.commit()
        return True, "User updated successfully"
    except sqlite3.Error as e:
        return False, f"Error updating user: {str(e)}"
    finally:
        conn.close()

def delete_user(user_id):
    """Delete user if not last admin."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT is_admin FROM Users WHERE id = ?", (user_id,))
        is_admin = cursor.fetchone()[0]
        
        if is_admin:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE is_admin = 1")
            admin_count = cursor.fetchone()[0]
            if admin_count <= 1:
                return False, "Cannot delete last admin user"
        
        cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))
        conn.commit()
        return True, "User deleted successfully"
    except sqlite3.Error as e:
        return False, f"Error deleting user: {str(e)}"
    finally:
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

# Cart Functioanlity
def add_to_cart(user_id, product_id, quantity=1):
    """Add or update product quantity in user's cart"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if product already in cart
    cursor.execute("""
        SELECT quantity FROM ShoppingCart 
        WHERE user_id = ? AND product_id = ?
    """, (user_id, product_id))
    result = cursor.fetchone()
    
    # Get current stock
    cursor.execute("SELECT stock FROM Products WHERE id = ?", (product_id,))
    stock = cursor.fetchone()[0]
    
    if result:
        new_quantity = result[0] + quantity
        if new_quantity > stock:
            conn.close()
            return False, "Cannot add more than available stock"
            
        cursor.execute("""
            UPDATE ShoppingCart 
            SET quantity = ?
            WHERE user_id = ? AND product_id = ?
        """, (new_quantity, user_id, product_id))
    else:
        if quantity > stock:
            conn.close() 
            return False, "Cannot add more than available stock"
            
        cursor.execute("""
            INSERT INTO ShoppingCart (user_id, product_id, quantity)
            VALUES (?, ?, ?)
        """, (user_id, product_id, quantity))
    
    conn.commit()
    conn.close()
    return True, "Product added to cart"

def get_cart_items(user_id):
    """Get all items in user's cart with product details"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.*, c.quantity 
        FROM ShoppingCart c
        JOIN Products p ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (user_id,))
    
    items = cursor.fetchall()
    conn.close()
    return items

def update_cart_quantity(user_id, product_id, quantity):
    """Update quantity of item in cart"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if quantity <= 0:
        cursor.execute("""
            DELETE FROM ShoppingCart 
            WHERE user_id = ? AND product_id = ?
        """, (user_id, product_id))
    else:
        # Check stock
        cursor.execute("SELECT stock FROM Products WHERE id = ?", (product_id,))
        stock = cursor.fetchone()[0]
        
        if quantity > stock:
            conn.close()
            return False, "Quantity exceeds available stock"
            
        cursor.execute("""
            UPDATE ShoppingCart 
            SET quantity = ?
            WHERE user_id = ? AND product_id = ?
        """, (quantity, user_id, product_id))
    
    conn.commit()
    conn.close()
    return True, "Cart updated"

# Discounts
def add_discount(name, percentage):
    """Add new discount with QR code"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Generate QR code and get path
        qr_path = handle_discount_qr_code(name, percentage)
        
        cursor.execute("""
            INSERT INTO Discounts (name, percentage, qr_code_path)
            VALUES (?, ?, ?)
        """, (name, percentage, qr_path))
        conn.commit()
        return True, "Discount added successfully"
    except sqlite3.IntegrityError:
        return False, "A discount with this name already exists"
    except Exception as e:
        return False, f"Error adding discount: {str(e)}"
    finally:
        conn.close()

def update_discount(discount_id, name, percentage):
    """Update discount and regenerate QR code"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get old QR code path
        cursor.execute("SELECT qr_code_path FROM Discounts WHERE id = ?", (discount_id,))
        old_qr = cursor.fetchone()
        if old_qr:
            # Generate new QR code
            new_qr_path = handle_discount_qr_code(name, percentage)
            # Delete old QR code
            cleanup_old_discount_qr(old_qr[0])
            
            cursor.execute("""
                UPDATE Discounts 
                SET name = ?, percentage = ?, qr_code_path = ?
                WHERE id = ?
            """, (name, percentage, new_qr_path, discount_id))
            conn.commit()
            return True, "Discount updated successfully"
        return False, "Discount not found"
    except sqlite3.IntegrityError:
        return False, "A discount with this name already exists"
    except Exception as e:
        return False, f"Error updating discount: {str(e)}"
    finally:
        conn.close()

def toggle_discount_status(discount_id):
    """Toggle discount active status"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Discounts SET active = NOT active WHERE id = ?", (discount_id,))
        conn.commit()
        return True, "Discount status updated successfully"
    except Exception as e:
        return False, f"Error updating discount status: {str(e)}"
    finally:
        conn.close()

def delete_discount(discount_id):
    """Delete discount and its QR code"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get QR code path before deletion
        cursor.execute("SELECT qr_code_path FROM Discounts WHERE id = ?", (discount_id,))
        result = cursor.fetchone()
        if result:
            qr_path = result[0]
            # Delete QR code file
            cleanup_old_discount_qr(qr_path)
            
            # Delete from database
            cursor.execute("DELETE FROM Discounts WHERE id = ?", (discount_id,))
            conn.commit()
            return True, "Discount deleted successfully"
        return False, "Discount not found"
    except Exception as e:
        return False, f"Error deleting discount: {str(e)}"
    finally:
        conn.close()

def get_all_discounts():
    """Get all discounts"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Discounts")  # Remove the WHERE clause
    discounts = cursor.fetchall()
    conn.close()
    return discounts

def increment_discount_uses(discount_id):
    """Increment the number of times a discount has been used"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Discounts SET uses = uses + 1 WHERE id = ? AND active = 1", (discount_id,))
        conn.commit()
        return True, "Discount use recorded"
    except Exception as e:
        return False, f"Error recording discount use: {str(e)}"
    finally:
        conn.close()

def verify_discount_qr(qr_data):
    """Verify QR code data and return discount if valid"""
    if not qr_data.startswith("DISCOUNT:"):
        return None
    
    try:
        _, name, percentage = qr_data.split(":")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, percentage 
            FROM Discounts 
            WHERE name = ? AND percentage = ? AND active = 1
        """, (name, int(percentage)))
        result = cursor.fetchone()
        conn.close()
        return result if result else None
    except:
        return None