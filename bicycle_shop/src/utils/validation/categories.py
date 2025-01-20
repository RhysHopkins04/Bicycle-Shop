from src.database.core.connection import get_connection

def validate_category_name(name):
    """Validate category name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Categories WHERE name = ?", (name,))
    exists = cursor.fetchone() is not None
    conn.close()
    
    if exists:
        return False, "Category name already exists."
    return True, "Valid"