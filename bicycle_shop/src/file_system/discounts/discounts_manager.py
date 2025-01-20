import os
from src.utils.qr.generator import generate_qr_code

def get_discounts_dir():
    """Create and return discounts directory path"""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    discounts_dir = os.path.join(root_dir, 'Discounts')
    os.makedirs(discounts_dir, exist_ok=True)
    return discounts_dir

def handle_discount_qr_code(name, percentage):
    """Generate QR code for discount"""
    qr_code = f"discount_{name}_{percentage}.png"
    qr_code_path = os.path.join(get_discounts_dir(), qr_code)
    generate_qr_code(f"DISCOUNT:{name}:{percentage}", qr_code_path)
    return qr_code_path

def cleanup_old_discount_qr(qr_code_path):
    """Remove old discount QR code file"""
    if qr_code_path and os.path.exists(qr_code_path):
        os.remove(qr_code_path)