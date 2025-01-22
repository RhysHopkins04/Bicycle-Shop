import os
from src.utils.qr.generator import generate_qr_code

def get_discounts_dir():
    """Create and return discounts directory path.
    
    Creates a Discounts directory in the root application folder
    if it doesn't exist.
    
    Returns:
        Absolute path to the discounts directory
    """
    # Get the root directory of the application by navigating up four levels from the current file
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    # Define the path to the Discounts directory within the root directory
    discounts_dir = os.path.join(root_dir, 'Discounts')
    
    # Create the Discounts directory if it doesn't exist
    os.makedirs(discounts_dir, exist_ok=True)
    
    # Return the absolute path to the Discounts directory
    return discounts_dir

def handle_discount_qr_code(name, percentage):
    """Generate QR code for discount.
    
    Args:
        name: Name of the discount
        percentage: Discount percentage value
        
    Returns:
        Path to generated QR code file
        
    Note:
        Creates QR code with format "DISCOUNT:name:percentage"
        Saves file as "discount_name_percentage.png"
    """
    # Define the QR code file name based on discount name and percentage
    qr_code = f"discount_{name}_{percentage}.png"
    
    # Get the full path to the QR code file in the discounts directory
    qr_code_path = os.path.join(get_discounts_dir(), qr_code)
    
    # Generate the QR code with the format "DISCOUNT:name:percentage" and save it to the specified path
    generate_qr_code(f"DISCOUNT:{name}:{percentage}", qr_code_path)
    
    # Return the path to the generated QR code file
    return qr_code_path

def cleanup_old_discount_qr(qr_code_path):
    """Remove old discount QR code file.
    
    Args:
        qr_code_path: Path to QR code file to remove
        
    Note:
        Safely checks if file exists before attempting removal
        No error if file doesn't exist
    """
    if qr_code_path and os.path.exists(qr_code_path):
        os.remove(qr_code_path)