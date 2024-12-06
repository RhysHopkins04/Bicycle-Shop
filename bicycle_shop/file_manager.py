import configparser
import os
import shutil
import qr_code_util

# Initialize config parser
config = configparser.ConfigParser()
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(CONFIG_PATH)

# Creates comments at start of config and in each section.
CONFIG_COMMENTS = """
# Application Configuration File
# This file controls various aspects of the Bicycle Shop application
# Warning: Modifying this file incorrectly may cause the application to malfunction
"""

SECTION_COMMENTS = {
    'Application': "# Window and page title settings",
    'Theme': "# Color scheme settings for the application interface",
    'DefaultAdmin': [
        "# Default administrator account settings (only used on first setup)",
        "# IT IS INSECURE, DO NOT EXPOSE SENSITIVE PASSWORDS HERE YOU WILL BE FORCED TO CHANGE IT"
    ],
    'Paths': "# Directory paths for application resources",
    'Icons': "# Icon filenames used in the application"
}

# Add fallback values in case config read fails
DEFAULT_CONFIG = {
    'Application': {
        'window_title': 'Bicycle Shop Management',
        'store_title': 'Store Listing',
        'admin_title': 'Dashboard'
    },
    'Theme': {
        'color_primary': '#171d22',
        'color_secondary': '#2a2f35',
        'color_background': 'black',
        'color_text': 'white',
        'color_text_secondary': 'darkgrey',
        'color_login_register': 'SystemButtonFace',
        'color_login_register_secondary': 'white',
        'color_text_login_register': 'SystemButtonText'
    },
    'DefaultAdmin': {
        'username': 'admin',
        'password': 'admin123',
        'first_name': 'Admin',
        'last_name': 'User',
        'age': '30'
    },
    'Paths': {
        'products_dir': './bicycle_shop/Products',
        'icons_dir': './bicycle_shop/Icons'
    },
    'Icons': {
        'password_show': 'visible.png',
        'password_hide': 'hidden.png',
        'user_icon': 'user_icon_thumbnail.png',
        'admin_icon': 'admin_icon_thumbnail.png'
    }
}

# Try to read config file, use defaults if fails including the comments in there.
if not os.path.exists(CONFIG_PATH):
    # Start with main comments
    with open(CONFIG_PATH, 'w') as configfile:
        configfile.write(CONFIG_COMMENTS)
    
    # Add each section with its comments and values
    for section, values in DEFAULT_CONFIG.items():
        with open(CONFIG_PATH, 'a') as configfile:
            # Write section comment(s)
            comments = SECTION_COMMENTS[section]
            if isinstance(comments, list):
                for comment in comments:
                    configfile.write(f"\n{comment}")
            else:
                configfile.write(f"\n{comments}")
            
            # Write section header
            configfile.write(f"\n[{section}]\n")
            
            # Write section values
            for key, value in values.items():
                configfile.write(f"{key} = {value}\n")
            
            # Add newline between sections
            configfile.write("\n")

    # Initialize config with defaults after creating file
    config.read(CONFIG_PATH)

# Pull the values from the config file
def get_application_settings():
    """Get application window and title settings."""
    return {
        'window_title': config['Application']['window_title'],
        'store_title': config['Application']['store_title'],
        'admin_title': config['Application']['admin_title']
    }

def get_theme():
    """Get theme color settings."""
    return {
        'dark_primary': config['Theme']['color_primary'],         # #171d22 - Main dark color for nav/headers
        'dark_secondary': config['Theme']['color_secondary'],     # #2a2f35 - Secondary dark color for content
        'dark_surface': config['Theme']['color_background'],      # black - Main background color
        'light_text': config['Theme']['color_text'],              # white - Main text color
        'med_text': config['Theme']['color_text_secondary'],      # darkgrey - Secondary text color
        'med_primary': config['Theme']['color_login_register'],   # SystemButtonFace - Input container color
        'light_primary': config['Theme']['color_login_register_secondary'], # white - Input background color
        'dark_text': config['Theme']['color_text_login_register'] # SystemButtonText - Input text color
    }

def get_default_admin():
    """Get default admin user settings."""
    return {
        'username': config['DefaultAdmin']['username'],
        'password': config['DefaultAdmin']['password'],
        'first_name': config['DefaultAdmin']['first_name'],
        'last_name': config['DefaultAdmin']['last_name'],
        'age': int(config['DefaultAdmin']['age'])
    }

def get_paths():
    """Get application directory paths."""
    return {
        'products_dir': config['Paths']['products_dir'],
        'icons_dir': config['Paths']['icons_dir']
    }

def get_icon_paths():
    """Get full paths to icon files."""
    icons_dir = config['Paths']['icons_dir']
    return {
        'password_show': os.path.join(icons_dir, config['Icons']['password_show']),
        'password_hide': os.path.join(icons_dir, config['Icons']['password_hide']),
        'user_icon': os.path.join(icons_dir, config['Icons']['user_icon']),
        'admin_icon': os.path.join(icons_dir, config['Icons']['admin_icon'])
    }

paths = get_paths()
PRODUCTS_DIR = paths['products_dir']
ICONS_DIR = paths['icons_dir']

def ensure_directories_exist():
    """Ensure required directories exist"""
    paths = get_paths()
    os.makedirs(paths['products_dir'], exist_ok=True)
    os.makedirs(paths['icons_dir'], exist_ok=True)

def handle_product_directory(name):
    """Create and manage product directory"""
    paths = get_paths()
    product_dir = os.path.join(paths['products_dir'], name)
    os.makedirs(product_dir, exist_ok=True)
    return product_dir

def handle_product_image(image_path, product_dir):
    """Handle product image file operations"""
    if image_path and os.path.exists(image_path):
        image_dest = os.path.join(product_dir, os.path.basename(image_path))
        if os.path.abspath(image_path) != os.path.abspath(image_dest):
            shutil.copy(image_path, image_dest)
        return image_dest
    return None

def handle_qr_code(name, price, product_dir):
    """Handle QR code file operations"""
    qr_code = f"{name}_{price}.png"
    qr_code_path = os.path.join(product_dir, qr_code)
    if not os.path.exists(qr_code_path):
        qr_code_util.generate_qr_code(f"{name}_{price}", qr_code_path)
    return qr_code_path

def cleanup_old_product_files(old_name, old_qr_code, old_image, new_name=None):
    """Clean up old product files when updating/deleting"""
    paths = get_paths()
    old_product_dir = os.path.join(paths['products_dir'], old_name)
    if old_qr_code and os.path.exists(old_qr_code) and old_name != new_name:
        os.remove(old_qr_code)
    if old_image and os.path.exists(old_image):
        os.remove(old_image)
    if os.path.exists(old_product_dir):
        if not os.listdir(old_product_dir):
            os.rmdir(old_product_dir)

def rename_product_directory(old_name, new_name):
    """Rename product directory when product name changes"""
    paths = get_paths()
    old_dir = os.path.join(paths['products_dir'], old_name)
    new_dir = os.path.join(paths['products_dir'], new_name)
    if os.path.exists(old_dir) and old_name != new_name:
        os.rename(old_dir, new_dir)
    return new_dir