import os
import shutil
import qr_code_util

PRODUCTS_DIR = "./bicycle_shop/Products"
ICONS_DIR = "./bicycle_shop/Icons"

def ensure_directories_exist():
    """Ensure required directories exist"""
    os.makedirs(PRODUCTS_DIR, exist_ok=True)
    os.makedirs(ICONS_DIR, exist_ok=True)

def handle_product_directory(name):
    """Create and manage product directory"""
    product_dir = os.path.join(PRODUCTS_DIR, name)
    os.makedirs(product_dir, exist_ok=True)
    return product_dir

def handle_product_image(image_path, product_dir):
    """Handle product image file operations"""
    if image_path and os.path.exists(image_path):
        image_dest = os.path.join(product_dir, os.path.basename(image_path))
        shutil.copy(image_path, image_dest)
        return image_dest
    return None

def handle_qr_code(name, price, product_dir):
    """Handle QR code file operations"""
    qr_code = f"{name}_{price}.png"
    qr_code_path = os.path.join(product_dir, qr_code)
    qr_code_util.generate_qr_code(f"{name}_{price}", qr_code_path)
    return qr_code_path

def cleanup_old_product_files(old_name, old_qr_code, old_image):
    """Clean up old product files when updating/deleting"""
    old_product_dir = os.path.join(PRODUCTS_DIR, old_name)
    if old_qr_code and os.path.exists(old_qr_code):
        os.remove(old_qr_code)
    if old_image and os.path.exists(old_image):
        os.remove(old_image)
    if os.path.exists(old_product_dir):
        if not os.listdir(old_product_dir):
            os.rmdir(old_product_dir)

def rename_product_directory(old_name, new_name):
    """Rename product directory when product name changes"""
    old_dir = os.path.join(PRODUCTS_DIR, old_name)
    new_dir = os.path.join(PRODUCTS_DIR, new_name)
    if os.path.exists(old_dir) and old_name != new_name:
        os.rename(old_dir, new_dir)
    return new_dir