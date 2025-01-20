from src.database.core.connection import get_connection

def validate_username_uniqueness(username):
    """Validate that the username is unique.
    
    Args:
        username: Username to check for uniqueness
        
    Returns:
        tuple: (is_valid, message)
            - is_valid: True if username is unique
            - message: Success/error message
            
    Note:
        Uses parameterized query for SQL injection protection
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return False, "Username already exists."
    return True, "Valid"

def validate_age(age):
    """Validate that the age is a number and at least 18.
    
    Args:
        age: Age value to validate
        
    Returns:
        tuple: (is_valid, message)
            - is_valid: True if age is valid
            - message: Success/error message
            
    Note:
        Must be integer 18 or greater
        Used for both registration and profile updates
    """
    try:
        age = int(age)
    except ValueError:
        return False, "Age must be a number."
    if age < 18:
        return False, "User must be 18 years or older to register."
    return True, "Valid"

def validate_user_fields(username, first_name, last_name, password, confirm_password, age, check_type="register"):
    """Validate user fields for registration, editing, and password changes.
    
    Performs different validations based on check_type:
    - register: All fields including uniqueness
    - edit: Names and age only
    - password: Password validation only
    
    Args:
        username: Username to validate
        first_name: First name to validate  
        last_name: Last name to validate
        password: Password to validate (if required)
        confirm_password: Password confirmation (if required) 
        age: Age to validate
        check_type: Type of validation ("register", "edit", or "password")
        
    Returns:
        tuple: (is_valid, message)
            - is_valid: True if all validations pass
            - message: Success/error message
    """
    from .fields import validate_empty_fields
    from .password import validate_password, validate_password_match
    
    if check_type == "register":
        is_valid, message = validate_empty_fields(username, first_name, last_name, password, confirm_password, age)
        if not is_valid:
            return False, message
            
        is_valid, message = validate_username_uniqueness(username)
        if not is_valid:
            return False, message
            
    elif check_type == "edit":
        is_valid, message = validate_empty_fields(first_name, last_name, age)
        if not is_valid:
            return False, message
            
    elif check_type == "password":
        is_valid, message = validate_empty_fields(password, confirm_password)
        if not is_valid:
            return False, message

    if check_type in ["register", "password"]:
        is_valid, message = validate_password_match(password, confirm_password)
        if not is_valid:
            return False, message

        is_valid, message = validate_password(username, password)
        if not is_valid:
            return False, message

    if check_type in ["register", "edit"]:
        is_valid, message = validate_age(age)
        if not is_valid:
            return False, message

    return True, "Valid"

def validate_user_edit(first_name, last_name, age, is_admin):
    """Validate fields for user detail updates.
    
    Args:
        first_name: First name to validate
        last_name: Last name to validate
        age: Age to validate
        is_admin: Admin status (unused but required for interface)
        
    Returns:
        tuple: (is_valid, message)
            - is_valid: True if all fields valid
            - message: Error message if invalid, empty if valid
            
    Note:
        Names cannot be empty
        Age must be integer >= 18
    """
    if not first_name or not last_name:
        return False, "Name fields cannot be empty"
    
    try:
        age = int(age)
        if age < 18:
            return False, "User must be 18 or older"
    except ValueError:
        return False, "Age must be a number"
        
    return True, ""