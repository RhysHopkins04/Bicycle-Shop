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
    # Use a cryptographically secure 16-byte random salt
    salt = os.urandom(16)
    # Use PBKDF2 with SHA256 and 100k iterations for strong password hashing
    # This provides good security against brute force and rainbow table attacks,
    # 100k itterations meets the python recommended minimal for 16 byte, however 600k itterations would be better for security.
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
    # Hash the provided password with same parameters and salt
    # This allows comparing against the stored hash
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
    # Fetch all required user details in one query for efficiency
    # Using parameterized query to prevent SQL injection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password, salt, is_admin, password_changed, first_name, last_name FROM Users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        # Return None values if user not found
        return False, None, None, None, None, None

    # Validate expected number of columns to catch database schema changes
    if len(result) != 7:
        raise ValueError(f"Expected 7 values, got {len(result)}: {result}")

    # Unpack all user details for verification and return
    user_id, stored_hash, stored_salt, is_admin, password_changed, first_name, last_name = result

    # Verify password and return full user context if valid
    if verify_password(stored_salt, stored_hash, password):
        return True, bool(is_admin), bool(password_changed), first_name, last_name, user_id
    return False, None, None, None, None, None