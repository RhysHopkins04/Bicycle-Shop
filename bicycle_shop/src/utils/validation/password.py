import re

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