import os
from src.utils.qr.generator import generate_qr_code

def get_discounts_dir():
    """Create and return discounts directory path.
    
    Creates a Discounts directory in the root application folder
    if it doesn't exist.
    
    Returns:
        Absolute path to the discounts directory
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    discounts_dir = os.path.join(root_dir, 'Discounts')
    os.makedirs(discounts_dir, exist_ok=True)
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
    qr_code = f"discount_{name}_{percentage}.png"
    qr_code_path = os.path.join(get_discounts_dir(), qr_code)
    generate_qr_code(f"DISCOUNT:{name}:{percentage}", qr_code_path)
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