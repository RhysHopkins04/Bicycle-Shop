import os
import shutil
from src.utils.qr.generator import generate_qr_code
from src.file_system.config.config_manager import get_paths

def handle_product_directory(name, old_name=None):
    """Create and manage product directory.
    
    Args:
        name: Name of product directory to create
        old_name: Previous name if renaming directory
        
    Returns:
        Path to product directory
        
    Note:
        Creates new directory if it doesn't exist
        Removes old directory if renaming
    """
    paths = get_paths()
    product_dir = os.path.join(paths['products_dir'], name)
    old_dir = os.path.join(paths['products_dir'], old_name) if old_name else None
    
    os.makedirs(product_dir, exist_ok=True)
    
    if old_dir and os.path.exists(old_dir) and old_dir != product_dir:
        try:
            shutil.rmtree(old_dir)
        except OSError as e:
            print(f"Error removing old directory: {e}")
            
    # print(f"Handling product directory for: {name}, old name: {old_name}")
    return product_dir

def handle_qr_code(name, price, product_dir):
    """Handle QR code file operations.
    
    Args:
        name: Product name for QR code
        price: Product price for QR code
        product_dir: Directory to save QR code
        
    Returns:
        Path to generated QR code file
        
    Note:
        Generates QR code with format "name_price"
        Saves as PNG file in product directory
    """
    qr_code = f"{name}_{price}.png"
    qr_code_path = os.path.join(product_dir, qr_code)
    generate_qr_code(f"{name}_{price}", qr_code_path)
    # print(f"Generating QR code for: {name}, price: {price}, directory: {product_dir}")
    return qr_code_path

def handle_product_image(image_path, product_dir):
    """Handle product image file operations.
    
    Args:
        image_path: Path to source image file
        product_dir: Directory to copy image to
        
    Returns:
        Path to copied image file, None if no image
        
    Note:
        Copies image to product directory
        Preserves original filename
    """
    if image_path and os.path.exists(image_path):
        image_dest = os.path.join(product_dir, os.path.basename(image_path))
        if os.path.abspath(image_path) != os.path.abspath(image_dest):
            shutil.copy(image_path, image_dest)
        # print(f"Handling product image: {image_path}, directory: {product_dir}")
        return image_dest
    return None

def rename_product_directory(old_name, new_name):
    """Rename product directory when product name changes.
    
    Args:
        old_name: Current directory name
        new_name: New directory name
        
    Returns:
        Path to renamed directory
        
    Note:
        Only renames if old directory exists and names differ
    """
    paths = get_paths()
    old_dir = os.path.join(paths['products_dir'], old_name)
    new_dir = os.path.join(paths['products_dir'], new_name)
    if os.path.exists(old_dir) and old_name != new_name:
        os.rename(old_dir, new_dir)
    return new_dir

def cleanup_old_product_files(old_name, old_qr_code, old_image, new_name=None, keep_files=False, clean_qr_only=False):
    """Clean up old product files when updating/deleting.
    
    Args:
        old_name: Name of product being updated/deleted
        old_qr_code: Path to old QR code file
        old_image: Path to old image file
        new_name: New product name if renaming
        keep_files: If True, skip cleanup
        clean_qr_only: If True, only remove QR code
        
    Note:
        Removes old QR code and image files
        Renames directory if product name changed
    """
    # print(f"Cleaning up old product files for: {old_name}")
    # print(f"Old QR code: {old_qr_code}, Old image: {old_image}")
    # print(f"New name: {new_name}, Keep files: {keep_files}, Clean QR only: {clean_qr_only}")

    if keep_files:
        return
        
    paths = get_paths()
    old_product_dir = os.path.join(paths['products_dir'], old_name)
    
    try:
        if old_qr_code and os.path.exists(old_qr_code):
            # print(f"Removing old QR code: {old_qr_code}")
            os.remove(old_qr_code)
            
        if not clean_qr_only and old_image and os.path.exists(old_image):
            # print(f"Removing old image: {old_image}")
            os.remove(old_image)
            
        if new_name and old_name != new_name:
            new_product_dir = os.path.join(paths['products_dir'], new_name)
            if os.path.exists(old_product_dir):
                # print(f"Renaming directory from {old_product_dir} to {new_name}")
                os.rename(old_product_dir, new_product_dir)
            else:
                print(f"Old directory {old_product_dir} does not exist")
                
    except OSError as e:
        print(f"Error during file cleanup: {e}")