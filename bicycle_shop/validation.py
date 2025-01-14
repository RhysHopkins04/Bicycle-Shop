import re
from database import get_connection, get_category_id

# Core Validation Functions:
def validate_empty_fields(*fields):
    """Validate that required fields are not empty."""
    for field in fields:
        if not field or str(field).strip() == "":
            return False, "All required fields must be filled."
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

# Combined User Validation Function:
def validate_user_fields(username, first_name, last_name, password, confirm_password, age, check_type="register"):
    """
    Validate user fields for registration, editing, and password changes.
    
    Args:
        username: Username to validate
        first_name: First name to validate
        last_name: Last name to validate
        password: Password to validate (if required)
        confirm_password: Password confirmation (if required)
        age: Age to validate
        check_type: Type of validation ("register", "edit", or "password")
    """
    # Basic field validation based on operation type
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

    # Password validation when required
    if check_type in ["register", "password"]:
        is_valid, message = validate_password_match(password, confirm_password)
        if not is_valid:
            return False, message

        is_valid, message = validate_password(username, password)
        if not is_valid:
            return False, message

    # Age validation always required except for password changes
    if check_type in ["register", "edit"]:
        is_valid, message = validate_age(age)
        if not is_valid:
            return False, message

    return True, "Valid"

# Product Validation Functions:
def validate_product_fields(name, price, stock, listed=False, category=None, image=None, description=None):
    """Validate product fields."""
    # Basic validation for all products (listed or unlisted)
    if not name:
        return False, "Product name is required."
    
    # Validate price is numeric
    try:
        price = float(price)
        if price <= 0:
            return False, "Price must be greater than 0."
    except ValueError:
        return False, "Price must be a valid number."
    
    # Skip all other validations if product is unlisted
    if not listed:
        return True, "Valid"
        
    # Additional validations only for listed products
    if listed:
        if not category:
            return False, "Category is required for listed products."
        
        if not description:
            return False, "Description is required for listed products."
            
        if not image:
            return False, "Image is required for listed products."
        
        category_id = get_category_id(category)
        if category_id is None:
            return False, "Invalid category."
        
        try:
            stock = int(stock) if stock else 0
            if stock <= 0:
                return False, "Listed products must have stock greater than 0."
        except ValueError:
            return False, "Stock must be a valid number for listed products."
    
    return True, "Valid"

# Category Validation Functions:
def validate_category_name(name):
    """Validate category name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Categories WHERE name = ?", (name,))
    exists = cursor.fetchone() is not None
    conn.close()
    
    if exists:
        return False, "Category name already exists."
    return True, "Valid"