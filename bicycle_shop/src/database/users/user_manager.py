import sqlite3
from src.auth.core import hash_password
from src.database.core.connection import get_connection

def register_user(username, first_name, last_name, password, age):
    """Register a new user in the database.

    Args:
        username: Unique username for the new user
        first_name: User's first name
        last_name: User's last name
        password: Plain text password to be hashed
        age: User's age
        
    Returns:
        tuple: (success, user_id, message)
            - success: True if registration succeeded
            - user_id: ID of new user if successful, None otherwise
            - message: Success/error message
            
    Raises:
        sqlite3.IntegrityError: If username already exists
    """
    # Hash pasword with random salt for security
    salt, hashed_password = hash_password(password)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Use parameterized query to prevent SQL injection
        cursor.execute("""
            INSERT INTO Users (username, first_name, last_name, password, salt, age, is_admin, password_changed) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, first_name, last_name, hashed_password, salt, age, 0, 1))
        user_id = cursor.lastrowid
        conn.commit()
        return True, user_id, "Registration successful."
    except sqlite3.IntegrityError:
        # Handle duplicate username case
        return False, None, "Username already exists."
    finally:
        conn.close()

def update_user_password(username, new_password):
    """Update user's password and mark as changed.

    Args:
        username: Username of user to update
        new_password: New password to hash and store
        
    Returns:
        tuple: (success, message)
            - success: True if password was updated
            - message: Success/error message
    """
    # Generate new salt and hash for security
    salt, hashed_password = hash_password(new_password)
    
    # Establish a connection to the database
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Update the user's password, salt, and mark the password as changed
        cursor.execute("""
            UPDATE Users 
            SET password = ?, 
                salt = ?, 
                password_changed = 1 
            WHERE username = ?
        """, (hashed_password, salt, username))
        # Commit the changes to the database
        conn.commit()
        return True, "Password updated successfully!"
    except sqlite3.Error as e:
        # Handle any errors that occur during the update
        return False, f"Failed to update password: {str(e)}"
    finally:
        # Ensure the database connection is closed
        conn.close()

def initialize_admin():
    """Create default admin user if none exists.
    
    Note:
        Only runs after first-time setup is complete.
        Uses admin settings from config.ini.
        Forces password change on first login.
    """
    from src.file_system import is_first_run, get_default_admin
    from src.auth import hash_password

    # Skip if first-time setup not complete
    if is_first_run():
        return

    conn = get_connection()
    cursor = conn.cursor()

    # Check for existing admin users
    cursor.execute("SELECT * FROM Users WHERE is_admin = 1")
    if not cursor.fetchone():
        # Create default admin from config settings
        admin_settings = get_default_admin()
        salt, hashed_password = hash_password(admin_settings['password'])

        # Set password_changed to 0 to force the admin user to change the default password on first login from the one in config.ini
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
            0   # password_changed
        ))
        conn.commit()
    conn.close()

def get_current_user_admin_status(username):
    """Check if user has admin privileges.
    
    Args:
        username: Username to check
        
    Returns:
        bool: True if user is admin, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Use parameterized query to prevent SQL injection
        # Only fetch is_admin field for efficiency since we only need admin status
        cursor.execute("SELECT is_admin FROM Users WHERE username = ?", (username,))
        result = cursor.fetchone()
        # Convert SQLite integer to boolean, handle case where user doesn't exist
        return bool(result[0]) if result else False
    finally:
        # Ensure connection is always closed even if query fails
        conn.close()

def get_all_users():
    """Retrieve all users from database ordered by ID.
    
    Returns:
        list: List of user tuples containing:
            (id, username, first_name, last_name, age, is_admin)
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Exclude sensitive fields (password, salt) for security
        # Order by ID to maintain consistent listing order across calls
        cursor.execute("""
            SELECT id, username, first_name, last_name, age, is_admin 
            FROM Users 
            ORDER BY id
        """)
        return cursor.fetchall()
    finally:
        conn.close()

def update_user_details(user_id, first_name, last_name, age, is_admin):
    """Update user details in database.
    
    Args:
        user_id: ID of user to update
        first_name: New first name
        last_name: New last name
        age: New age
        is_admin: New admin status
        
    Returns:
        tuple: (success, message)
            - success: True if update succeeded
            - message: Success/error message
            
    Note:
        Will not allow removal of last admin user
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if not is_admin:
            # Check the number of admin users
            cursor.execute("SELECT COUNT(*) FROM Users WHERE is_admin = 1")
            admin_count = cursor.fetchone()[0]
            # Check if the current user is an admin
            cursor.execute("SELECT is_admin FROM Users WHERE id = ?", (user_id,))
            current_is_admin = cursor.fetchone()[0]
            # Prevent removal of the last admin user
            if admin_count <= 1 and current_is_admin:
                return False, "Cannot remove last admin user"

        # Update user details in the database
        cursor.execute("""
            UPDATE Users 
            SET first_name = ?, last_name = ?, age = ?, is_admin = ?
            WHERE id = ?
        """, (first_name, last_name, age, is_admin, user_id))
        conn.commit()
        return True, "User updated successfully"
    except sqlite3.Error as e:
        # Handle any errors that occur during the update
        return False, f"Error updating user: {str(e)}"
    finally:
        conn.close()

def get_username_by_id(user_id):
    """Retrieve username by user ID.
    
    Args:
        user_id: ID of user to look up
        
    Returns:
        str | None: Username if found, None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Execute the query to fetch the username based on user ID
    cursor.execute("SELECT username FROM Users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    # Return the username if found, otherwise return None
    return user[0] if user else None

def get_user_id_by_username(username):
    """Retrieve user ID by username.
    
    Args:
        username: Username to look up
        
    Returns:
        int | None: User ID if found, None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Execute the query to fetch the user ID based on username
    cursor.execute("SELECT id FROM Users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    conn.close()
    
    # Return the user ID if found, otherwise return None
    return user[0] if user else None

def delete_user(user_id):
    """Delete user if not last admin.
    
    Args:
        user_id: ID of user to delete
        
    Returns:
        tuple: (success, message)
            - success: True if deletion succeeded
            - message: Success/error message
            
    Note:
        Will not allow deletion of last admin user
    """
    # Retrieve the username by user ID
    username = get_username_by_id(user_id)
    if not username:
        # Return an error message if the user is not found
        return False, "User not found"


    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if the user is an admin
        cursor.execute("SELECT is_admin FROM Users WHERE id = ?", (user_id,))
        is_admin = cursor.fetchone()[0]
        
        if is_admin:
            # Check the number of admin users
            cursor.execute("SELECT COUNT(*) FROM Users WHERE is_admin = 1")
            admin_count = cursor.fetchone()[0]
            # Prevent deletion of the last admin user
            if admin_count <= 1:
                return False, "Cannot delete last admin user"
        
        # Delete the user from the database
        cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))
        conn.commit()
        return True, "User deleted successfully"
    except sqlite3.Error as e:
        return False, f"Error deleting user: {str(e)}"
    finally:
        conn.close()

def promote_user_to_admin(user_id):
    """Promote a user to admin status.
    
    Args:
        user_id: ID of user to promote
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Promote the user to admin by setting is_admin to 1
    cursor.execute("UPDATE Users SET is_admin = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def demote_user_from_admin(user_id, current_admin_id):
    """Demote a user from admin status.
    
    Args:
        user_id: ID of user to demote
        current_admin_id: ID of admin performing demotion
        
    Returns:
        str: Success/error message
        
    Note:
        Will not allow:
        - Self-demotion
        - Demotion of last admin
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Prevent self-demotion
    if user_id == current_admin_id:
        conn.close()
        return "You cannot demote yourself."

    # Check the number of admin users
    cursor.execute("SELECT COUNT(*) FROM Users WHERE is_admin = 1")
    admin_count = cursor.fetchone()[0]
    
    # Prevent demotion if it would result in no admins
    if admin_count <= 1:
        conn.close()
        return "There must be at least one admin."

    # Demote the user by setting is_admin to 0
    cursor.execute("UPDATE Users SET is_admin = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return "User demoted successfully."