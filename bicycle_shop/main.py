from src.file_system.directory.directory_manager import initialize
from src.database.core.schema import create_tables
from src.database.users.user_manager import initialize_admin
from src.gui.core import start_app

"""Main entry point for the Bicycle Shop Management application.

This module initializes the application by:
1. Checking for first-time setup
2. Creating database tables
3. Ensuring admin user exists
4. Starting the GUI

The application will exit after creating config.ini on first run.
"""

def main():
    """Initialize and start the Bicycle Shop Management application.
    
    Returns:
        None: If first-time setup (exits after config creation)
        
    Note:
        Performs initialization in specific order:
        1. First-time setup check/config creation
        2. Database table creation
        3. Admin user initialization
        4. GUI startup
    """
    # Check if first run
    if initialize():
        return  # Exit after creating config.ini

    # Ensure database tables are created before starting the app
    create_tables()

    # Ensure an admin user exists on startup
    initialize_admin()

    # Start the GUI application
    start_app()

if __name__ == "__main__":
    main()