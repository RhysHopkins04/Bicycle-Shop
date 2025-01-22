import configparser
import os

def get_absolute_path(relative_path):
    """Convert relative path to absolute path.
    
    Args:
        relative_path: Path to convert to absolute path
        
    Returns:
        Absolute path based on project root directory
    """
    if os.path.isabs(relative_path):
        # If the path is already absolute, return it as is
        return relative_path
    
    # Get the current directory of this file (config folder)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate up to the project root directory (bicycle_shop folder)
    src_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
    # Join the project root directory with the relative path to form an absolute path
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
    """Get directory paths from config.
    
    Returns:
        dict: Directory paths with keys:
            - products_dir: Path to products directory
            - icons_dir: Path to icons directory
    """
    if not os.path.exists(CONFIG_PATH):
        # Create initial config file if it doesn't exist
        create_initial_config()
    # Read the config file
    config.read(CONFIG_PATH)
    # Return the absolute paths for products and icons directories
    return {
        'products_dir': get_absolute_path(config['Paths']['products_dir']),
        'icons_dir': get_absolute_path(config['Paths']['icons_dir'])
    }

def get_icon_paths():
    """Get icon file paths from config.
    
    Returns:
        dict: Full paths to icon files with keys:
            - password_show: Path to password show icon
            - password_hide: Path to password hide icon 
            - user_icon: Path to user icon
            - admin_icon: Path to admin icon
            - placeholder: Path to placeholder image
    """
    if not os.path.exists(CONFIG_PATH):
        # Create initial config file if it doesn't exist
        create_initial_config()
    # Read the config file
    config.read(CONFIG_PATH)
    # Get the directory paths from the config
    paths = get_paths()
    # Return the full paths to the icon files
    return {
        'password_show': os.path.join(paths['icons_dir'], config['Icons']['password_show']),
        'password_hide': os.path.join(paths['icons_dir'], config['Icons']['password_hide']),
        'user_icon': os.path.join(paths['icons_dir'], config['Icons']['user_icon']),
        'admin_icon': os.path.join(paths['icons_dir'], config['Icons']['admin_icon']),
        'placeholder': os.path.join(paths['icons_dir'], config['Icons']['placeholder'])
    }

def create_initial_config():
    """Create initial config.ini file.
    
    Returns:
        bool: True if config created successfully, False otherwise
        
    Note:
        Creates config with default values if it doesn't exist.
        Will not overwrite existing config file.
    """
    try:
        if os.path.exists(CONFIG_PATH):
            # If the config file already exists, do not create a new one
            return False
            
        with open(CONFIG_PATH, 'w') as configfile:
            # Write the general comments at the top of the config file
            configfile.write(CONFIG_COMMENTS)
            
            for section, values in DEFAULT_CONFIG.items():
                # Write section-specific comments
                comments = SECTION_COMMENTS[section]
                if isinstance(comments, list):
                    for comment in comments:
                        configfile.write(f"\n{comment}")
                else:
                    configfile.write(f"\n{comments}")
                
                # Write the section header
                configfile.write(f"\n[{section}]\n")
                # Write each key-value pair in the section
                for key, value in values.items():
                    configfile.write(f"{key} = {value}\n")
                configfile.write("\n")
        
        # Read the newly created config file
        config.read(CONFIG_PATH)
        
        # Verify the config file has all required sections
        if not verify_config():
            raise ValueError("Config file is missing required sections")
            
        return True
        
    except (IOError, ValueError) as e:
        # Handle any errors that occur during file creation
        print(f"Error creating config file: {e}")
        if os.path.exists(CONFIG_PATH):
            # Remove the config file if an error occurred
            os.remove(CONFIG_PATH)
        return False

def verify_config():
    """Verify config has all required sections and values.
    
    Returns:
        bool: True if config is valid, False otherwise
        
    Note:
        Checks for required sections:
        - Application
        - Theme
        - DefaultAdmin  
        - Paths
        - Icons
    """
    required_sections = ['Application', 'Theme', 'DefaultAdmin', 'Paths', 'Icons']
    
    if not os.path.exists(CONFIG_PATH):
        # If the config file does not exist, return False
        return False
    
    # Read the config file
    config.read(CONFIG_PATH)
    
    # Check if all required sections are present in the config file
    return all(section in config.sections() for section in required_sections)

def get_application_settings():
    """Get application window and title settings.
    
    Returns:
        dict: Application settings with keys:
            - window_title: Main window title
            - store_title: Store page title
            - admin_title: Admin dashboard title 
            - use_maximized: Whether to start maximized
            - window_state: Initial window state
    """
    if not os.path.exists(CONFIG_PATH):
        # Create initial config file if it doesn't exist
        create_initial_config()
    # Read the config file
    config.read(CONFIG_PATH)
    # Return application settings from the config file
    return {
        'window_title': config['Application']['window_title'],
        'store_title': config['Application']['store_title'],
        'admin_title': config['Application']['admin_title'],
        'use_maximized': config['Application'].getboolean('start_max_windowed', fallback=True),
        'window_state': 'zoomed' if config['Application'].getboolean('use_maximized', fallback=True) else 'normal'
    }

def get_logging_settings():
    """Get logging configuration settings.
    
    Returns:
        dict: Logging settings with keys:
            - user_logging_enabled: Whether user logging is enabled
    """
    if not os.path.exists(CONFIG_PATH):
        # Create initial config file if it doesn't exist
        create_initial_config()
    # Read the config file
    config.read(CONFIG_PATH)
    # Return logging settings from the config file
    return {
        'user_logging_enabled': config['Logging'].getboolean('user_logging_enabled', fallback=True)
    }

def get_user_logging_status():
    """Get user logging status from config.
    
    Returns:
        bool: True if user logging enabled, False otherwise
    """
    if not os.path.exists(CONFIG_PATH):
        # Create initial config file if it doesn't exist
        create_initial_config()
    # Read the config file
    config.read(CONFIG_PATH)
    # Return the user logging status from the config file
    return config['Logging'].getboolean('user_logging_enabled', fallback=True)

def set_user_logging_status(enabled):
    """Set user logging status in config.
    
    Args:
        enabled: True to enable logging, False to disable
    """
    if not os.path.exists(CONFIG_PATH):
        # Create initial config file if it doesn't exist
        create_initial_config()
    # Read the config file
    config.read(CONFIG_PATH)
    # Update the user logging status in the config
    config['Logging']['user_logging_enabled'] = str(enabled).lower()
    # Write the updated config back to the file
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)

def get_theme():
    """Get theme color settings.
    
    Returns:
        dict: Theme colors with keys:
            - dark_primary: Primary dark theme color
            - dark_secondary: Secondary dark theme color 
            - dark_surface: Background color
            - light_text: Light text color
            - med_text: Medium text color
            - med_primary: Medium primary color
            - light_primary: Light primary color
            - dark_text: Dark text color
    """
    if not os.path.exists(CONFIG_PATH):
        # Create initial config file if it doesn't exist
        create_initial_config()
    # Read the config file
    config.read(CONFIG_PATH)
    # Return theme color settings from the config file
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
    """Get default admin user settings.
    
    Returns:
        dict: Default admin settings with keys:
            - username: Admin username
            - password: Admin password
            - first_name: Admin first name
            - last_name: Admin last name 
            - age: Admin age
    """
    if not os.path.exists(CONFIG_PATH):
        # Create initial config file if it doesn't exist
        create_initial_config()
    # Read the config file
    config.read(CONFIG_PATH)
    # Return default admin settings from the config file
    return {
        'username': config['DefaultAdmin']['username'],
        'password': config['DefaultAdmin']['password'],
        'first_name': config['DefaultAdmin']['first_name'],
        'last_name': config['DefaultAdmin']['last_name'],
        'age': int(config['DefaultAdmin']['age'])  # Convert age to integer
    }