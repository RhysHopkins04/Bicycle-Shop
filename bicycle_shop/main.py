from src.file_system.directory.directory_manager import initialize
from src.database.core.schema import create_tables
from src.database.users.user_manager import initialize_admin
from src.gui.core import start_app

def main():
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