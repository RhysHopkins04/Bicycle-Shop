import re

def validate_password(username, password):
    """Validate password complexity requirements.
    
    Args:
        username: Username to check against password
        password: Password to validate
        
    Returns:
        tuple: (is_valid, message)
            - is_valid: True if password meets all requirements
            - message: Error message if invalid, "Valid" if valid
            
    Note:
        Requirements:
        - Minimum 8 characters
        - Must not contain username
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character (!@#$%^&*(),.?":{}|<>)
    """

    # Checks if each requirement is met for the password, return the error message for each if not met
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
    """Validate password and confirmation match.
    
    Args:
        password: Original password
        confirm_password: Password confirmation to check
        
    Returns:
        tuple: (is_valid, message)
            - is_valid: True if passwords match
            - message: Error message if mismatch, "Valid" if match
    """
    # Ensure that password and the confirm password match
    if password != confirm_password:
        return False, "Passwords do not match."
    return True, "Valid"