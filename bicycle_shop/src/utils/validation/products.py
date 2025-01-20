from src.database.categories.category_manager import get_category_id

def validate_product_fields(name, price, stock, listed=False, category=None, image=None, description=None):
    """Validate product fields."""
    if not name:
        return False, "Product name is required."
    
    try:
        price = float(price)
        if price <= 0:
            return False, "Price must be greater than 0."
    except ValueError:
        return False, "Price must be a valid number."
    
    if not listed:
        return True, "Valid"
        
    if listed:
        if not category or category == "No Category":
            return False, "Category is required for listed products."
        
        if not description:
            return False, "Description is required for listed products."
            
        if not image:
            return False, "Image is required for listed products."
        
        category_id = get_category_id(category)
        if category_id is None and category != "No Category":
            return False, "Invalid category."
        
        try:
            stock = int(stock) if stock else 0
            if stock <= 0:
                return False, "Listed products must have stock greater than 0."
        except ValueError:
            return False, "Stock must be a valid number for listed products."
    
    return True, "Valid"