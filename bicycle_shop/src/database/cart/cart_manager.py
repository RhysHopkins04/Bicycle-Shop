from src.database.core.connection import get_connection

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