import re
import sqlite3
from database import get_connection

# Core Validation Functions:
def validate_empty_fields(*fields):
    """Validate that none of the fields are empty."""
    for field in fields:
        if not field:
            return False, "All fields are required."
    return True, "Valid"

# Password Validation Functions:
def validate_password(username, password):
    """Validate password complexity."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if username.lower() in password.lower():
        return False, "Password must not contain the username."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, "Valid"

def validate_password_match(password, confirm_password):
    """Validate that the password and confirm password match."""
    if password != confirm_password:
        return False, "Passwords do not match."
    return True, "Valid"

# User Validation Functions:
def validate_username_uniqueness(username):
    """Validate that the username is unique."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return False, "Username already exists."
    return True, "Valid"

def validate_age(age):
    """Validate that the age is a number and at least 18."""
    try:
        age = int(age)
    except ValueError:
        return False, "Age must be a number."
    if age < 18:
        return False, "User must be 18 years or older to register."
    return True, "Valid"

# Combined Validation Function:
def validate_registration_fields(username, first_name, last_name, password, confirm_password, age):
    """Validate registration fields."""
    is_valid, message = validate_empty_fields(username, first_name, last_name, password, confirm_password, age)
    if not is_valid:
        return False, message
    
    is_valid, message = validate_username_uniqueness(username)
    if not is_valid:
        return False, message

    is_valid, message = validate_password_match(password, confirm_password)
    if not is_valid:
        return False, message

    is_valid, message = validate_password(username, password)
    if not is_valid:
        return False, message

    is_valid, message = validate_age(age)
    if not is_valid:
        return False, message

    return True, "Valid"