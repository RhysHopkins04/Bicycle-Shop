import configparser
import os
import shutil
import qr_code_util
import tkinter as tk
from tkinter import messagebox

# Adds the constant for initialization marker file and config.ini file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.ini')
INIT_MARKER_PATH = os.path.join(os.path.dirname(__file__), '.initialized')

# Creates comments at start of config and in each section.
CONFIG_COMMENTS = """
# Application Configuration File
# This file controls various aspects of the Bicycle Shop application
# Warning: Modifying this file incorrectly may cause the application to malfunction
"""

SECTION_COMMENTS = {
    'Application': [
        '# Window and page title settings',
        '# start_maximized: True to start in maximized window mode',
        '# start_fullscreen: True to start in full screen mode'
    ],
    'Theme': "# Color scheme settings for the application interface",
    'DefaultAdmin': [
        "# Default administrator account settings (only used on first setup)",
        "# IT IS INSECURE, DO NOT EXPOSE SENSITIVE PASSWORDS HERE YOU WILL BE FORCED TO CHANGE IT"
    ],
    'Paths': "# Directory paths for application resources",
    'Icons': "# Icon filenames used in the application"
}

# Add fallback values in case config read fails and definines the default configuration for first time generation.
DEFAULT_CONFIG = {
    'Application': {
        'window_title': 'Bicycle Shop Management',
        'store_title': 'Store Listing',
        'admin_title': 'Dashboard',
        'start_max_windowed': 'True',
        'start_fullscreen': 'False'
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
        'products_dir': './Products',
        'icons_dir': './Icons'
    },
    'Icons': {
        'password_show': 'visible.png',
        'password_hide': 'hidden.png',
        'user_icon': 'user_icon_thumbnail.png',
        'admin_icon': 'admin_icon_thumbnail.png'
    }
}

# Initialize config parser
config = configparser.ConfigParser()

def get_absolute_path(relative_path):
    """Convert relative path to absolute path."""
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.abspath(os.path.join(os.path.dirname(__file__), relative_path))

def create_initial_config():
    """Create initial config.ini file."""
    try:
        if os.path.exists(CONFIG_PATH):
            return False
            
        with open(CONFIG_PATH, 'w') as configfile:
            configfile.write(CONFIG_COMMENTS)
            
            for section, values in DEFAULT_CONFIG.items():
                comments = SECTION_COMMENTS[section]
                if isinstance(comments, list):
                    for comment in comments:
                        configfile.write(f"\n{comment}")
                else:
                    configfile.write(f"\n{comments}")
                
                configfile.write(f"\n[{section}]\n")
                for key, value in values.items():
                    configfile.write(f"{key} = {value}\n")
                configfile.write("\n")
        
        # Read the newly created config
        config.read(CONFIG_PATH)
        
        # Verify all sections exist
        required_sections = ['Application', 'Theme', 'DefaultAdmin', 'Paths', 'Icons']
        if not all(section in config.sections() for section in required_sections):
            raise ValueError("Config file is missing required sections")
            
        return True
        
    except (IOError, ValueError) as e:
        print(f"Error creating config file: {e}")
        # Clean up partial config if it exists
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
        return False

def mark_initialized():
    """Create initialization marker file."""
    with open(INIT_MARKER_PATH, 'w') as f:
        f.write('initialized')

def is_first_run():
    """Check if this is first application run."""
    return not os.path.exists(INIT_MARKER_PATH)

def initialize():
    """Handle first-time setup and configuration."""
    if not is_first_run():
        if not os.path.exists(CONFIG_PATH):
            create_initial_config()
        config.read(CONFIG_PATH)
        ensure_directories_exist()
        return False
        
    # First run setup
    success = create_initial_config()
    if success:
        root = tk.Tk()
        root.withdraw()
        
        abs_config_path = os.path.abspath(CONFIG_PATH)
        messagebox.showinfo(
            "First Time Setup",
            f"Initial configuration file has been created at:\n{abs_config_path}\n\n"
            "Please review and edit the configuration as needed:\n"
            "1. Window titles\n"
            "2. Theme colors\n"
            "3. Default admin credentials\n"
            "4. Directory paths\n\n"
            "Then run the application again to start with your configuration."
            "\n\nNote: The admin password set here is insecure and will be changed."
            "\nNote: If you do not change the information, default values will be used."
        )
        
        # Only mark as initialized if config and directories are created successfully
        if ensure_directories_exist():
            mark_initialized()
            return True
            
    return False

def verify_config():
    """Verify config has all required sections and values."""
    required_sections = ['Application', 'Theme', 'DefaultAdmin', 'Paths', 'Icons']
    if not os.path.exists(CONFIG_PATH):
        return False
        
    config.read(CONFIG_PATH)
    return all(section in config.sections() for section in required_sections)

# Pull the values from the config file
def get_application_settings():
    """Get application window and title settings."""
    if not os.path.exists(CONFIG_PATH):
        create_initial_config()
    config.read(CONFIG_PATH)
    return {
        'window_title': config['Application']['window_title'],
        'store_title': config['Application']['store_title'],
        'admin_title': config['Application']['admin_title'],
        'use_maximized': config['Application'].getboolean('start_max_windowed', fallback=True),
        'use_fullscreen': config['Application'].getboolean('start_fullscreen', fallback=False),
        'window_state': 'zoomed' if config['Application'].getboolean('use_maximized', fallback=True) else 'normal'
    }

def get_theme():
    """Get theme color settings."""
    if not os.path.exists(CONFIG_PATH):
        create_initial_config()
    config.read(CONFIG_PATH)
    return {
        'dark_primary': config['Theme']['color_primary'],                   # #171d22 - Main dark color for nav/headers
        'dark_secondary': config['Theme']['color_secondary'],               # #2a2f35 - Secondary dark color for content
        'dark_surface': config['Theme']['color_background'],                # black - Main background color
        'light_text': config['Theme']['color_text'],                        # white - Main text color
        'med_text': config['Theme']['color_text_secondary'],                # darkgrey - Secondary text color
        'med_primary': config['Theme']['color_login_register'],             # SystemButtonFace - Input container color
        'light_primary': config['Theme']['color_login_register_secondary'], # white - Input background color
        'dark_text': config['Theme']['color_text_login_register']           # SystemButtonText - Input text color
    }

def get_default_admin():
    """Get default admin user settings."""
    if not os.path.exists(CONFIG_PATH):
        create_initial_config()
    config.read(CONFIG_PATH)
    return {
        'username': config['DefaultAdmin']['username'],
        'password': config['DefaultAdmin']['password'],
        'first_name': config['DefaultAdmin']['first_name'],
        'last_name': config['DefaultAdmin']['last_name'],
        'age': int(config['DefaultAdmin']['age'])
    }

def get_paths():
    """Get application directory paths."""
    if not os.path.exists(CONFIG_PATH):
        create_initial_config()
    config.read(CONFIG_PATH)
    return {
        'products_dir': get_absolute_path(config['Paths']['products_dir']),
        'icons_dir': get_absolute_path(config['Paths']['icons_dir'])
    }

def get_icon_paths():
    """Get full paths to icon files."""
    if not os.path.exists(CONFIG_PATH):
        create_initial_config()
    config.read(CONFIG_PATH)
    paths = get_paths()
    return {
        'password_show': os.path.join(paths['icons_dir'], config['Icons']['password_show']),
        'password_hide': os.path.join(paths['icons_dir'], config['Icons']['password_hide']),
        'user_icon': os.path.join(paths['icons_dir'], config['Icons']['user_icon']), 
        'admin_icon': os.path.join(paths['icons_dir'], config['Icons']['admin_icon'])
    }

def ensure_directories_exist():
    """Create required directories and copy default icons."""
    paths = get_paths()
    
    # Create directories
    os.makedirs(paths['products_dir'], exist_ok=True)
    os.makedirs(paths['icons_dir'], exist_ok=True)
    
    # Copy default icons
    default_icons_dir = os.path.join(os.path.dirname(__file__), 'default_icons')
    
    if os.path.exists(default_icons_dir):
        icon_files = {
            'password_show': 'visible.png',
            'password_hide': 'hidden.png',
            'user_icon': 'user_icon_thumbnail.png',
            'admin_icon': 'admin_icon_thumbnail.png'
        }
        
        for icon_name, icon_file in icon_files.items():
            source = os.path.join(default_icons_dir, icon_file)
            destination = os.path.join(paths['icons_dir'], icon_file)
            
            if os.path.exists(source):
                try:
                    shutil.copy2(source, destination)
                    print(f"Copied {icon_file} to Icons directory")
                except shutil.SameFileError:
                    pass  # File already exists
                except Exception as e:
                    print(f"Error copying {icon_file}: {e}")
            else:
                print(f"Warning: Source icon {icon_file} not found in default_icons")
    else:
        print(f"Warning: default_icons directory not found at {default_icons_dir}")
    
    return True

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