import os
import shutil
import tkinter as tk
from tkinter import messagebox


from src.file_system.config.config_manager import (
    create_initial_config, 
    get_paths,
    get_absolute_path,
    CONFIG_PATH
)

INIT_MARKER_PATH = get_absolute_path('.initialized')

def mark_initialized():
    """Create initialization marker file.
    
    Creates a file that indicates the application has been initialized.
    This prevents the first-time setup from running again.
    """
    with open(INIT_MARKER_PATH, 'w') as f:
        f.write('initialized')

def is_first_run():
    """Check if this is first application run.
    
    Returns:
        bool: True if application has never been run, False otherwise
    """
    return not os.path.exists(INIT_MARKER_PATH)

def initialize():
    """Handle first-time setup and configuration.
    
    Handles initial application setup including:
    - Creating config.ini with default values
    - Showing configuration instructions to user
    - Creating required directories
    - Copying default icons
    
    Returns:
        bool: True if first-time setup completed successfully, False otherwise
    """
    if not is_first_run():
        # If not the first run, ensure config exists and directories are set up
        if not os.path.exists(CONFIG_PATH):
            create_initial_config()
        ensure_directories_exist()
        return False
        
    # First run setup
    success = create_initial_config()
    if success:
        # Hide the main Tkinter window
        root = tk.Tk()
        root.withdraw()
        
        # Show a message box with setup instructions
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
        
        # Ensure required directories exist and mark initialization complete
        if ensure_directories_exist():
            mark_initialized()
            return True
            
    return False

def ensure_directories_exist():
    """Create required directories and copy default icons.
    
    Creates the following directories if they don't exist:
    - Products directory for product files
    - Icons directory for application icons
    
    Copies default icons from default_icons/ to Icons/:
    - Password visibility icons
    - User/admin profile icons
    - Placeholder image
    
    Returns:
        bool: True if directories created successfully
        
    Note:
        Will not overwrite existing icon files
        Prints warnings if source icons are missing
    """
    # Get the paths from the configuration
    paths = get_paths()
    
    # Create the required directories if they don't exist
    os.makedirs(paths['products_dir'], exist_ok=True)
    os.makedirs(paths['icons_dir'], exist_ok=True)
    
    # Define the path to the default icons directory
    default_icons_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'default_icons'
    )
    
    # Check if the default icons directory exists
    if os.path.exists(default_icons_dir):
        # Define the icon files to be copied
        icon_files = {
            'password_show': 'visible.png',
            'password_hide': 'hidden.png',
            'user_icon': 'user_icon_thumbnail.png',
            'admin_icon': 'admin_icon_thumbnail.png',
            'placeholder': 'placeholder.png'
        }
        
        # Copy each icon file to the icons directory
        for icon_name, icon_file in icon_files.items():
            source = os.path.join(default_icons_dir, icon_file)
            destination = os.path.join(paths['icons_dir'], icon_file)
            
            # Check if the source icon file exists
            if os.path.exists(source):
                try:
                    # Copy the icon file to the destination
                    shutil.copy2(source, destination)
                    print(f"Copied {icon_file} to Icons directory")
                except shutil.SameFileError:
                    # Skip if the source and destination are the same file
                    pass
                except Exception as e:
                    print(f"Error copying {icon_file}: {e}")
            else:
                # Print a warning if the source icon file is not found
                print(f"Warning: Source icon {icon_file} not found in default_icons")
    else:
        # Print a warning if the default icons directory is not found
        print(f"Warning: default_icons directory not found at {default_icons_dir}")
    
    return True