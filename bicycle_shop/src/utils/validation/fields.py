def validate_empty_fields(*fields):
    """Validate that required fields are not empty."""
    for field in fields:
        if not field or str(field).strip() == "":
            return False, "All required fields must be filled."
    return True, "Valid"