import configparser
import os

def get_absolute_path(relative_path):
    """Convert relative path to absolute path."""
    if os.path.isabs(relative_path):
        return relative_path
    
    # Get the project root directory (bicycle_shop folder)
    current_dir = os.path.dirname(os.path.abspath(__file__))  # config folder
    src_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # up to bicycle_shop root
    
    # Join with the relative path
    absolute_path = os.path.abspath(os.path.join(src_dir, relative_path))
    return absolute_path

# Constants
CONFIG_PATH = get_absolute_path('config.ini')

# Config Comments
CONFIG_COMMENTS = """
# Application Configuration File
# This file controls various aspects of the Bicycle Shop application
# Warning: Modifying this file incorrectly may cause the application to malfunction
"""

SECTION_COMMENTS = {
    'Application': [
        '# Window and page title settings',
        '# start_maximized: True to start in maximized window mode',
    ],
    'Logging': "# Logging configuration settings",
    'Theme': "# Color scheme settings for the application interface",
    'DefaultAdmin': [
        "# Default administrator account settings (only used on first setup)",
        "# IT IS INSECURE, DO NOT EXPOSE SENSITIVE PASSWORDS HERE YOU WILL BE FORCED TO CHANGE IT"
    ],
    'Paths': "# Directory paths for application resources",
    'Icons': "# Icon filenames used in the application"
}

# Default Configuration
DEFAULT_CONFIG = {
    'Application': {
        'window_title': 'Bicycle Shop Management',
        'store_title': 'Store Listing',
        'admin_title': 'Dashboard',
        'start_max_windowed': 'True',
    },
    'Logging': {
        'user_logging_enabled': 'True'
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
        'admin_icon': 'admin_icon_thumbnail.png',
        'placeholder': 'placeholder.png'
    }
}

# Initialize config parser
config = configparser.ConfigParser()

def get_paths():
    """Get directory paths from config."""
    if not os.path.exists(CONFIG_PATH):
        create_initial_config()
    config.read(CONFIG_PATH)
    return {
        'products_dir': get_absolute_path(config['Paths']['products_dir']),
        'icons_dir': get_absolute_path(config['Paths']['icons_dir'])
    }

def get_icon_paths():
    """Get icon file paths from config."""
    if not os.path.exists(CONFIG_PATH):
        create_initial_config()
    config.read(CONFIG_PATH)
    paths = get_paths()
    return {
        'password_show': os.path.join(paths['icons_dir'], config['Icons']['password_show']),
        'password_hide': os.path.join(paths['icons_dir'], config['Icons']['password_hide']),
        'user_icon': os.path.join(paths['icons_dir'], config['Icons']['user_icon']),
        'admin_icon': os.path.join(paths['icons_dir'], config['Icons']['admin_icon']),
        'placeholder': os.path.join(paths['icons_dir'], config['Icons']['placeholder'])
    }

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
        
        config.read(CONFIG_PATH)
        
        if not verify_config():
            raise ValueError("Config file is missing required sections")
            
        return True
        
    except (IOError, ValueError) as e:
        print(f"Error creating config file: {e}")
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
        return False

def verify_config():
    """Verify config has all required sections and values."""
    required_sections = ['Application', 'Theme', 'DefaultAdmin', 'Paths', 'Icons']
    if not os.path.exists(CONFIG_PATH):
        return False
    config.read(CONFIG_PATH)
    return all(section in config.sections() for section in required_sections)

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
        'window_state': 'zoomed' if config['Application'].getboolean('use_maximized', fallback=True) else 'normal'
    }

def get_logging_settings():
    """Get logging configuration settings"""
    if not os.path.exists(CONFIG_PATH):
        create_initial_config()
    config.read(CONFIG_PATH)
    return {
        'user_logging_enabled': config['Logging'].getboolean('user_logging_enabled', fallback=True)
    }

def get_user_logging_status():
    """Get user logging status from config"""
    if not os.path.exists(CONFIG_PATH):
        create_initial_config()
    config.read(CONFIG_PATH)
    return config['Logging'].getboolean('user_logging_enabled', fallback=True)

def set_user_logging_status(enabled):
    """Set user logging status in config"""
    if not os.path.exists(CONFIG_PATH):
        create_initial_config()
    config.read(CONFIG_PATH)
    config['Logging']['user_logging_enabled'] = str(enabled).lower()
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)

def get_theme():
    """Get theme color settings."""
    if not os.path.exists(CONFIG_PATH):
        create_initial_config()
    config.read(CONFIG_PATH)
    return {
        'dark_primary': config['Theme']['color_primary'],
        'dark_secondary': config['Theme']['color_secondary'],
        'dark_surface': config['Theme']['color_background'],
        'light_text': config['Theme']['color_text'],
        'med_text': config['Theme']['color_text_secondary'],
        'med_primary': config['Theme']['color_login_register'],
        'light_primary': config['Theme']['color_login_register_secondary'],
        'dark_text': config['Theme']['color_text_login_register']
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