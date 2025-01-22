from src.database.categories.category_manager import get_category_id

def validate_product_fields(name, price, stock, listed=False, category=None, image=None, description=None):
    """Validate product fields for creation and updates.
    
    Args:
        name: Product name to validate
        price: Product price to validate
        stock: Product stock quantity to validate
        listed: Whether product will be listed in store (default: False)
        category: Product category name (optional)
        image: Path to product image (optional)
        description: Product description text (optional)
        
    Returns:
        tuple: (is_valid, message)
            - is_valid: True if all validations pass
            - message: Error message if invalid, "Valid" if valid
            
    Note:
        Basic validation for all products:
        - Name cannot be empty
        - Price must be positive number
        
        Additional validation for listed products:
        - Must have category
        - Must have description
        - Must have image
        - Must have positive stock
    """
    if not name:
        return False, "Product name is required."
    
    try:
        # Convert price to a float and check if it's greater than 0
        price = float(price)
        if price <= 0:
            return False, "Price must be greater than 0."
    except ValueError:
        # Handle the case where price is not a valid float
        return False, "Price must be a valid number."
    
    # If the product is not listed, basic validation is enough (name and price)
    if not listed:
        return True, "Valid"
    
    # If the product is listed, perform additional checks
    if listed:
        # Check if category is provided and not set to "No Category"
        if not category or category == "No Category":
            return False, "Category is required for listed products."
        
         # Check if description is provided
        if not description:
            return False, "Description is required for listed products."
        
        # Check if image is provided
        if not image:
            return False, "Image is required for listed products."
        
        # Retrieve the category ID and check if it's valid
        category_id = get_category_id(category)
        if category_id is None and category != "No Category":
            return False, "Invalid category."
        
        try:
            # Convert stock to an integer and check if it's greater than 0
            stock = int(stock) if stock else 0
            if stock <= 0:
                return False, "Listed products must have stock greater than 0."
        except ValueError:
            # Handle the case where stock is not a valid integer
            return False, "Stock must be a valid number for listed products."
    
    # If all checks pass, the product is valid
    return True, "Valid"