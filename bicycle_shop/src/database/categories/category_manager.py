import sqlite3
from src.database.core.connection import get_connection

def add_category(name):
    """Add a new category to the database.
    
    Args:
        name: Name of the category to add
        
    Returns:
        tuple: (success, message)
            - success: True if operation succeeded
            - message: Success/error message
            
    Raises:
        sqlite3.IntegrityError: If category name already exists
        sqlite3.Error: If database operation fails
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Use parameterized query to prevent SQL injection
        cursor.execute("INSERT INTO Categories (name) VALUES (?)", (name,))
        conn.commit()
        return True, "Category added successfully!"
    except sqlite3.IntegrityError:
        # Return specific error for duplicate category names
        return False, "Category name already exists."
    except sqlite3.Error as e:
        return False, f"Failed to add category: {str(e)}"
    finally:
        conn.close()

def get_categories():
    """Retrieve all categories from the database.
    
    Returns:
        list: List of category names
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Return just category names for UI display purposes
    cursor.execute("SELECT name FROM Categories")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def get_category_id(name):
    """Retrieve the ID of a category by its name.
    
    Args:
        name: Name of the category to look up
        
    Returns:
        int | None: Category ID if found, None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Use parameterized query for safe lookup
    cursor.execute("SELECT id FROM Categories WHERE name = ?", (name,))
    category = cursor.fetchone()
    conn.close()
    return category[0] if category else None

def get_category_name(category_id):
    """"Retrieve the name of a category by its ID.
    
    Args:
        category_id: ID of the category to look up
        
    Returns:
        str | None: Category name if found, None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Use parameterized query for safe lookup
    cursor.execute("SELECT name FROM Categories WHERE id = ?", (category_id,))
    category = cursor.fetchone()
    conn.close()
    return category[0] if category else None

def update_category(category_id, new_name):
    """Update category name in database.
    
    Args:
        category_id: ID of category to update
        new_name: New name for the category
        
    Returns:
        tuple: (success, message)
            - success: True if operation succeeded  
            - message: Success/error message
            
    Raises:
        sqlite3.Error: If database operation fails
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Use parameterized query to prevent SQL injection
        cursor.execute("UPDATE Categories SET name = ? WHERE id = ?", (new_name, category_id))
        conn.commit()
        return True, "Category updated successfully!"
    except sqlite3.Error as e:
        return False, f"Failed to update category: {str(e)}"
    finally:
        conn.close()

def delete_category(category_id):
    """Delete category from database and unlist associated products.
    
    Args:
        category_id: ID of category to delete
        
    Returns:
        tuple: (success, message)
            - success: True if operation succeeded
            - message: Success/error message
            
    Notes:
        All products in the deleted category will be unlisted and have their
        category_id set to NULL
            
    Raises:
        sqlite3.Error: If database operation fails
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # First update all products in this category to maintain data consistency
        # Products are unlisted and category reference removed
        cursor.execute("""
            UPDATE Products 
            SET listed = 0, category_id = NULL 
            WHERE category_id = ?
        """, (category_id,))
        
        # Then delete the category after products are updated
        cursor.execute("DELETE FROM Categories WHERE id = ?", (category_id,))
        conn.commit()
        return True, "Category deleted successfully and associated products unlisted!"
    except sqlite3.Error as e:
        return False, f"Failed to delete category: {str(e)}"
    finally:
        conn.close()