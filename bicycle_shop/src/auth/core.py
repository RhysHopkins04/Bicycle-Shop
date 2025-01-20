import hashlib
import os
from src.database.core.connection import get_connection

def hash_password(password):
    """Hash a password with a randomly generated salt."""
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt, hashed_password

def verify_password(salt, stored_hash, password):
    """Verify a password against a stored hash and salt."""
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return hashed_password == stored_hash

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