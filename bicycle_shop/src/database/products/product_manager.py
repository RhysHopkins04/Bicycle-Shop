import os
import shutil

from src.file_system.products.products_manager import handle_product_directory, handle_product_image, handle_qr_code
from src.file_system.config.config_manager import get_paths
from src.database.core.connection import get_connection


def add_product(name, price, qr_code, listed, description, category_id, image, stock):
    """Add a new product to the database."""
    try:
        product_dir = handle_product_directory(name)
        qr_code_path = handle_qr_code(name, price, product_dir)
        image_path = handle_product_image(image, product_dir) if image else None

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Products (name, price, qr_code, listed, description, category_id, image, stock) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, price, qr_code_path, listed, description, category_id, image_path, stock))
        new_product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return True, new_product_id, "Product added successfully"
    except Exception as e:
        return False, None, f"Error adding product: {str(e)}"

def update_product(product_id, name, price, qr_code, description, category_id, image, stock, listed, keep_image=False, keep_qr=False):
    """Update product with enhanced error handling and file management"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM Products WHERE id = ?", (product_id,))
        current_product = cursor.fetchone()
        
        if not current_product:
            raise ValueError("Product not found")

        needs_name_update = name != current_product[1]
        needs_price_update = abs(float(price) - float(current_product[2])) > 0.001
        needs_new_qr = (needs_name_update or needs_price_update) and not keep_qr

        product_dir = os.path.join(get_paths()['products_dir'], name if needs_name_update else current_product[1])
        if needs_name_update:
            os.makedirs(product_dir, exist_ok=True)

        # Handle QR code update
        new_qr_path = current_product[3]
        if needs_new_qr:
            # Remove old QR code first
            if current_product[3] and os.path.exists(current_product[3]):
                try:
                    os.remove(current_product[3])
                except OSError as e:
                    print(f"Error removing old QR code: {e}")
            # Generate new QR code
            new_qr_path = handle_qr_code(name, price, product_dir)
        elif not os.path.exists(current_product[3]):
            new_qr_path = handle_qr_code(name, price, product_dir)

        needs_image_update = image and image != current_product[7] and not keep_image

        new_image_path = current_product[7]
        if needs_image_update:
            new_image_path = handle_product_image(image, product_dir)
            if current_product[7] and os.path.exists(current_product[7]):
                try:
                    os.remove(current_product[7])
                except OSError as e:
                    print(f"Error removing old image: {e}")
        elif needs_name_update and current_product[7] and not needs_image_update:
            old_image_name = os.path.basename(current_product[7])
            new_image_path = os.path.join(product_dir, old_image_name)
            if os.path.exists(current_product[7]):
                shutil.copy2(current_product[7], new_image_path)

        new_qr_path = current_product[3]
        if needs_new_qr or not os.path.exists(current_product[3]):
            new_qr_path = handle_qr_code(name, price, product_dir)

        # If image is None/empty and we have an old image, we need to clean it up
        if not image and current_product[7]:
            try:
                if os.path.exists(current_product[7]):
                    os.remove(current_product[7])
            except OSError as e:
                print(f"Error removing old image: {e}")
            new_image_path = None
        else:
            new_image_path = handle_product_image(image, product_dir) if image else None

        # Update database with possibly NULL image path
        cursor.execute("""
            UPDATE Products 
            SET name = ?, price = ?, qr_code = ?, description = ?, 
                category_id = ?, image = ?, stock = ?, listed = ?
            WHERE id = ?
        """, (name, price, new_qr_path, description, 
              category_id, new_image_path, stock, listed, product_id))
        
        if needs_name_update:
            old_dir = os.path.join(get_paths()['products_dir'], current_product[1])
            if os.path.exists(old_dir):
                try:
                    shutil.rmtree(old_dir)
                except OSError as e:
                    print(f"Error removing old directory: {e}")
        
        conn.commit()
        return True
        
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