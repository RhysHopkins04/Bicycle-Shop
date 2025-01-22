from src.database.core.connection import get_connection

def validate_category_name(name):
    """Validate category name uniqueness in database.
    
    Args:
        name: Name of category to validate
        
    Returns:
        tuple: (is_valid, message)
            - is_valid: True if name is unique
            - message: Success/error message
            
    Note:
        Uses parameterized query for SQL injection protection
        Returns False if category name already exists
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Execute a query to check if the category name exists
    cursor.execute("SELECT 1 FROM Categories WHERE name = ?", (name,))
    exists = cursor.fetchone() is not None # If not None, category name exists
    conn.close()
    
    # Return False and a message if the category name exists, else True and "Valid" hence allow creation
    if exists:
        return False, "Category name already exists."
    return True, "Valid"