def validate_empty_fields(*fields):
    """Validate that required fields are not empty.
    
    Args:
        *fields: Variable number of fields to check
        
    Returns:
        tuple: (is_valid, message)
            - is_valid: True if all fields have content
            - message: Error message if invalid, "Valid" if valid
            
    Note:
        Considers a field empty if:
        - It is None
        - It is an empty string
        - It contains only whitespace
    """
    for field in fields:
        if not field or str(field).strip() == "":
            return False, "All required fields must be filled."
    return True, "Valid"