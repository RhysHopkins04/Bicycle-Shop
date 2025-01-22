import sqlite3
from src.database.core.connection import get_connection

def add_discount(name, percentage):
    """Add new discount with QR code.
    
    Args:
        name: Name of the discount
        percentage: Discount percentage value
        
    Returns:
        tuple: (success, discount_id, message)
            - success: True if operation succeeded
            - discount_id: ID of new discount if successful, None otherwise
            - message: Success/error message
            
    Raises:
        sqlite3.IntegrityError: If discount name already exists
    """
    from src.file_system.discounts.discounts_manager import handle_discount_qr_code
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Generate QR code for new discount before database insertion
        qr_path = handle_discount_qr_code(name, percentage)
        
        # Use parameterized query to prevent SQL injection
        cursor.execute("""
            INSERT INTO Discounts (name, percentage, qr_code_path)
            VALUES (?, ?, ?)
            """, (name, percentage, qr_path))
        new_discount_id = cursor.lastrowid
        conn.commit()
        return True, new_discount_id, "Discount added successfully"
    except sqlite3.IntegrityError:
        # Handle duplicate discount names
        return False, None, "A discount with this name already exists"
    except Exception as e:
        return False, None, f"Error adding discount: {str(e)}"
    finally:
        conn.close()

def get_all_discounts():
    """Get all discounts from database.
    
    Returns:
        list: List of discount tuples containing:
            (id, name, percentage, qr_code_path, uses, active)
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Fetch all relevant discount fields for display and management
    cursor.execute("""
        SELECT id, name, percentage, qr_code_path, uses, active
        FROM Discounts
    """)
    discounts = cursor.fetchall()
    conn.close()
    return discounts

def update_discount(discount_id, name, percentage):
    """Update discount and regenerate QR code.
    
    Args:
        discount_id: ID of discount to update
        name: New discount name
        percentage: New discount percentage
        
    Returns:
        tuple: (success, message)
            - success: True if operation succeeded
            - message: Success/error message
            
    Raises:
        sqlite3.IntegrityError: If new name already exists
    """
    from src.file_system.discounts.discounts_manager import handle_discount_qr_code, cleanup_old_discount_qr
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get old QR path for cleanup
        cursor.execute("SELECT qr_code_path FROM Discounts WHERE id = ?", (discount_id,))
        old_qr = cursor.fetchone()
        if old_qr:
            try:
                # Update discount details first
                cursor.execute("""
                    UPDATE Discounts 
                    SET name = ?, percentage = ?
                    WHERE id = ?
                """, (name, percentage, discount_id))
                
                # Generate new QR code and clean up old one
                new_qr_path = handle_discount_qr_code(name, percentage)
                cleanup_old_discount_qr(old_qr[0])
                
                # Update QR path in database
                cursor.execute("UPDATE Discounts SET qr_code_path = ? WHERE id = ?", 
                             (new_qr_path, discount_id))
                             
                conn.commit()
                return True, "Discount updated successfully"
            except sqlite3.IntegrityError:
                return False, "A discount with this name already exists"
        return False, "Discount not found"
    except Exception as e:
        return False, f"Error updating discount: {str(e)}"
    finally:
        conn.close()

def delete_discount(discount_id):
    """Delete discount and its QR code.
    
    Args:
        discount_id: ID of discount to delete
        
    Returns:
        tuple: (success, message)
            - success: True if operation succeeded
            - message: Success/error message
    """
    from src.file_system.discounts.discounts_manager import cleanup_old_discount_qr
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get QR path for cleanup before deletion
        cursor.execute("SELECT qr_code_path FROM Discounts WHERE id = ?", (discount_id,))
        result = cursor.fetchone()
        if result:
            qr_path = result[0]
            cleanup_old_discount_qr(qr_path)
            cursor.execute("DELETE FROM Discounts WHERE id = ?", (discount_id,))
            conn.commit()
            return True, "Discount deleted successfully"
        return False, "Discount not found"
    except Exception as e:
        return False, f"Error deleting discount: {str(e)}"
    finally:
        conn.close()

def toggle_discount_status(discount_id):
    """Toggle active status of discount.
    
    Args:
        discount_id: ID of discount to toggle
        
    Returns:
        tuple: (success, message)
            - success: True if operation succeeded
            - message: Success/error message
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Use NOT operator to flip boolean active status
        cursor.execute("UPDATE Discounts SET active = NOT active WHERE id = ?", (discount_id,))
        conn.commit()
        return True, "Discount status toggled successfully"
    except Exception as e:
        return False, f"Error toggling discount status: {str(e)}"
    finally:
        conn.close()

def increment_discount_uses(discount_id):
    """Increment the use count of a discount.
    
    Args:
        discount_id: ID of discount to increment
        
    Returns:
        tuple: (success, message)
            - success: True if operation succeeded
            - message: Success/error message
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Update usage count and last used timestamp
        cursor.execute("""
            UPDATE Discounts 
            SET uses = uses + 1, last_used = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (discount_id,))
        conn.commit()
        return True, "Discount usage incremented"
    except Exception as e:
        return False, f"Error incrementing discount usage: {str(e)}"
    finally:
        conn.close()

def verify_discount_qr(qr_data):
    """Verify QR code data and return discount details.
    
    Args:
        qr_data: QR code data to verify
        
    Returns:
        tuple: (success, discount_id, message)
            - success: True if discount is valid
            - discount_id: ID of valid discount, None if invalid
            - message: Success/error message
    """
    # Validate QR code format (DISCOUNT:name:percentage)
    if not qr_data.startswith("DISCOUNT:"):
        return False, None, "Invalid QR code format"
    
    try:
        # Parse QR code data
        _, name, percentage = qr_data.split(":")
        percentage = int(percentage)
        
        conn = get_connection()
        cursor = conn.cursor()

        # Check discount exists and is active
        cursor.execute("""
            SELECT id, active, uses 
            FROM Discounts 
            WHERE name = ? AND percentage = ?
        """, (name, percentage))
        
        result = cursor.fetchone()
        if not result:
            return False, None, "Discount not found"
            
        discount_id, active, uses = result
        
        if not active:
            return False, None, "Discount is not active"
            
        return True, discount_id, f"Valid discount: {percentage}% off"
            
    except ValueError:
        return False, None, "Invalid QR code data"
    except Exception as e:
        return False, None, f"Error verifying discount: {str(e)}"
    finally:
        conn.close()