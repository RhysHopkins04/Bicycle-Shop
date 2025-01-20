import sqlite3
from src.database.core.connection import get_connection

def add_discount(name, percentage):
    """Add new discount with QR code."""
    from src.file_system.discounts.discounts_manager import handle_discount_qr_code
    conn = get_connection()
    cursor = conn.cursor()
    try:
        qr_path = handle_discount_qr_code(name, percentage)
        cursor.execute("""
            INSERT INTO Discounts (name, percentage, qr_code_path)
            VALUES (?, ?, ?)
            """, (name, percentage, qr_path))
        new_discount_id = cursor.lastrowid
        conn.commit()
        return True, new_discount_id, "Discount added successfully"
    except sqlite3.IntegrityError:
        return False, None, "A discount with this name already exists"
    except Exception as e:
        return False, None, f"Error adding discount: {str(e)}"
    finally:
        conn.close()

def get_all_discounts():
    """Get all discounts from database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, percentage, qr_code_path, uses, active
        FROM Discounts
    """)
    discounts = cursor.fetchall()
    conn.close()
    return discounts

def update_discount(discount_id, name, percentage):
    """Update discount and regenerate QR code."""
    from src.file_system.discounts.discounts_manager import handle_discount_qr_code, cleanup_old_discount_qr
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get old QR path
        cursor.execute("SELECT qr_code_path FROM Discounts WHERE id = ?", (discount_id,))
        old_qr = cursor.fetchone()
        if old_qr:
            try:
                # Try update first
                cursor.execute("""
                    UPDATE Discounts 
                    SET name = ?, percentage = ?
                    WHERE id = ?
                """, (name, percentage, discount_id))
                
                # If successful, handle QR code changes
                new_qr_path = handle_discount_qr_code(name, percentage)
                cleanup_old_discount_qr(old_qr[0])
                
                # Update QR path
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
    """Delete discount and its QR code."""
    from src.file_system.discounts.discounts_manager import cleanup_old_discount_qr
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
    """Toggle active status of discount."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Discounts SET active = NOT active WHERE id = ?", (discount_id,))
        conn.commit()
        return True, "Discount status toggled successfully"
    except Exception as e:
        return False, f"Error toggling discount status: {str(e)}"
    finally:
        conn.close()

def increment_discount_uses(discount_id):
    """Increment the use count of a discount."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
    """Verify QR code data and return discount details."""
    if not qr_data.startswith("DISCOUNT:"):
        return False, None, "Invalid QR code format"
    
    try:
        _, name, percentage = qr_data.split(":")
        percentage = int(percentage)
        
        conn = get_connection()
        cursor = conn.cursor()
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