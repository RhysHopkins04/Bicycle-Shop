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
        conn.commit()
        return "Registration successful."
    except sqlite3.IntegrityError:
        return "Username already exists."
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

def promote_user_to_admin(user_id):
    """Promote a user to admin."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET is_admin = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def demote_user_from_admin(user_id, current_admin_id):
    """Demote a user from admin."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if the user to be demoted is the current admin
    if user_id == current_admin_id:
        conn.close()
        return "You cannot demote yourself."

    # Check if there is more than one admin
    cursor.execute("SELECT COUNT(*) FROM Users WHERE is_admin = 1")
    admin_count = cursor.fetchone()[0]
    if admin_count <= 1:
        conn.close()
        return "There must be at least one admin."

    cursor.execute("UPDATE Users SET is_admin = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return "User demoted successfully."