import sqlite3
import hashlib
import os
from database import get_connection

# Core Auth Functions:
def hash_password(password):
    """Hash a password with a randomly generated salt."""
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt, hashed_password

def verify_password(salt, stored_hash, password):
    """Verify a password against a stored hash and salt."""
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return hashed_password == stored_hash


# User Management Functions:
def register_user(username, first_name, last_name, password, age):
    """Register a new user."""
    salt, hashed_password = hash_password(password)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Users (username, first_name, last_name, password, salt, age, is_admin, password_changed) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, first_name, last_name, hashed_password, salt, age, 0, 1))
        user_id = cursor.lastrowid
        conn.commit()
        return True, user_id, "Registration successful."
    except sqlite3.IntegrityError:
        return False, None, "Username already exists."
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate a user by username and password."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password, salt, is_admin, password_changed, first_name, last_name FROM Users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return False, None, None, None, None, None  # No user found

    if len(result) != 7:
        raise ValueError(f"Expected 7 values, got {len(result)}: {result}")

    user_id, stored_hash, stored_salt, is_admin, password_changed, first_name, last_name = result
    if verify_password(stored_salt, stored_hash, password):
        return True, bool(is_admin), bool(password_changed), first_name, last_name, user_id
    return False, None, None, None, None, None

def update_user_password(username, new_password):
    """Update user password and mark as changed."""
    salt, hashed_password = hash_password(new_password)
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Users 
            SET password = ?, 
                salt = ?, 
                password_changed = 1 
            WHERE username = ?
        """, (hashed_password, salt, username))
        conn.commit()
        return True, "Password updated successfully!"
    except sqlite3.Error as e:
        return False, f"Failed to update password: {str(e)}"
    finally:
        conn.close()

def validate_user_edit(first_name, last_name, age, is_admin):
    """Validate user edit fields."""
    if not first_name or not last_name:
        return False, "Name fields cannot be empty"
    
    try:
        age = int(age)
        if age < 18:
            return False, "User must be 18 or older"
    except ValueError:
        return False, "Age must be a number"
        
    return True, ""