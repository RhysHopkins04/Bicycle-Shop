import sqlite3
from src.database.core.connection import get_connection

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