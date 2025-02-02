import os
import shutil

from src.file_system.products.products_manager import handle_product_directory, handle_product_image, handle_qr_code
from src.file_system.config.config_manager import get_paths
from src.database.core.connection import get_connection


def add_product(name, price, qr_code, listed, description, category_id, image, stock):
    """Add a new product to the database.

    Args:
        name: Name of the product
        price: Price of the product
        qr_code: Whether to generate QR code
        listed: Whether product should be listed (1) or unlisted (0)
        description: Product description
        category_id: ID of product category, None if uncategorized
        image: Path to product image, None if no image
        stock: Amount of product in stock

    Returns:
        tuple: (success, product_id, message)
            - success: True if operation succeeded
            - product_id: ID of new product if successful, None otherwise
            - message: Success/error message
    """
    try:
        # Create directory structure and assets before database insertion
        # This ensures filesystem consistency in case of DB failure
        product_dir = handle_product_directory(name)
        qr_code_path = handle_qr_code(name, price, product_dir)
        image_path = handle_product_image(image, product_dir) if image else None

        conn = get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query for SQL injection prevention
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
    """Update product with enhanced error handling and file management.

    Args:
        product_id: ID of product to update
        name: New product name
        price: New product price
        qr_code: Whether to update QR code
        description: New product description
        category_id: New category ID, None if uncategorized
        image: New image path, None to remove image
        stock: New stock amount
        listed: New listed status (1 for listed, 0 for unlisted)
        keep_image: If True, keep existing image
        keep_qr: If True, keep existing QR code

    Returns:
        bool: True if update successful

    Raises:
        ValueError: If product not found
        Exception: If database operation fails
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get current state for smart file management decisions
        cursor.execute("SELECT * FROM Products WHERE id = ?", (product_id,))
        current_product = cursor.fetchone()
        
        if not current_product:
            raise ValueError("Product not found")

        # Track what needs updating to minimize filesystem operations
        needs_name_update = name != current_product[1]
        needs_price_update = abs(float(price) - float(current_product[2])) > 0.001
        needs_new_qr = (needs_name_update or needs_price_update) and not keep_qr

        # Handle directory structure updates
        product_dir = os.path.join(get_paths()['products_dir'], name if needs_name_update else current_product[1])
        if needs_name_update:
            os.makedirs(product_dir, exist_ok=True)

        # Smart QR code management - only remove and regenerate when needed
        new_qr_path = current_product[3]
        if needs_new_qr:
            if current_product[3] and os.path.exists(current_product[3]):
                try:
                    os.remove(current_product[3])
                except OSError as e:
                    print(f"Error removing old QR code: {e}")
            new_qr_path = handle_qr_code(name, price, product_dir)
        elif not os.path.exists(current_product[3]):
            new_qr_path = handle_qr_code(name, price, product_dir)

        # Smart image management with cleanup
        needs_image_update = image and image != current_product[7] and not keep_image
        new_image_path = current_product[7]

        if needs_image_update:
            # Handle new image upload
            new_image_path = handle_product_image(image, product_dir)
            if current_product[7] and os.path.exists(current_product[7]):
                try:
                    os.remove(current_product[7])
                except OSError as e:
                    print(f"Error removing old image: {e}")
        elif needs_name_update and current_product[7] and not needs_image_update:
            # Handle image migration for product rename
            old_image_name = os.path.basename(current_product[7])
            new_image_path = os.path.join(product_dir, old_image_name)
            if os.path.exists(current_product[7]):
                shutil.copy2(current_product[7], new_image_path)

        new_qr_path = current_product[3]
        if needs_new_qr or not os.path.exists(current_product[3]):
            new_qr_path = handle_qr_code(name, price, product_dir)

        # Handle image removal case
        if not image and current_product[7]:
            try:
                if os.path.exists(current_product[7]):
                    os.remove(current_product[7])
            except OSError as e:
                print(f"Error removing old image: {e}")
            new_image_path = None
        else:
            new_image_path = handle_product_image(image, product_dir) if image else None

        # Update database with all changes
        cursor.execute("""
            UPDATE Products 
            SET name = ?, price = ?, qr_code = ?, description = ?, 
                category_id = ?, image = ?, stock = ?, listed = ?
            WHERE id = ?
        """, (name, price, new_qr_path, description, 
              category_id, new_image_path, stock, listed, product_id))
        
        # Clean up old directory after successful database update
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
    """Delete a product from the database.

    Args:
        product_id: ID of product to delete

    Returns:
        bool: True if deletion successful
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get product info for filesystem cleanup
    cursor.execute("SELECT name FROM Products WHERE id = ?", (product_id,))
    product_name = cursor.fetchone()[0]
    paths = get_paths()
    product_dir = os.path.join(paths['products_dir'], product_name)
    
    # Delete from database first
    cursor.execute("DELETE FROM Products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    
    # Then clean up filesystem
    if os.path.exists(product_dir):
        shutil.rmtree(product_dir)

def list_product(product_id, listed):
    """List or delist a product.

    Args:
        product_id: ID of product to update
        listed: New listed status (1 for listed, 0 for unlisted)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Products SET listed = ? WHERE id = ?", (listed, product_id))
    conn.commit()
    conn.close()

def get_products(listed_only=True):
    """Retrieve all products from the database.

    Args:
        listed_only: If True, return only listed products

    Returns:
        list: List of product tuples containing all product fields
    """
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
    """Retrieve a product by its ID from the database.

    Args:
        product_id: ID of product to retrieve

    Returns:
        tuple | None: Product tuple if found, None otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product