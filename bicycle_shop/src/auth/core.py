import hashlib
import os
from src.database.core.connection import get_connection

def hash_password(password):
    """Hash a password using PBKDF2 with a random salt.
    
    Args:
        password: The plaintext password to hash
        
    Returns:
        tuple: (salt, hashed_password)
            - salt: Random 16-byte salt used in hashing
            - hashed_password: The resulting password hash
    """
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt, hashed_password

def verify_password(salt, stored_hash, password):
    """Verify if a password matches its stored hash.
    
    Args:
        salt: The salt used in the original hash
        stored_hash: The previously generated hash to verify against
        password: The plaintext password to verify
        
    Returns:
        bool: True if password matches, False otherwise
    """
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return hashed_password == stored_hash

def authenticate_user(username, password):
    """Authenticate a user and retrieve their details.
    
    Args:
        username: Username to authenticate
        password: Password to verify
        
    Returns:
        tuple: (authenticated, is_admin, needs_password_change, first_name, last_name, user_id)
            - authenticated: True if credentials are valid
            - is_admin: True if user has admin privileges 
            - needs_password_change: True if password needs to be changed
            - first_name: User's first name
            - last_name: User's last name
            - user_id: User's database ID
            
    Raises:
        ValueError: If database returns unexpected number of columns
    """
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