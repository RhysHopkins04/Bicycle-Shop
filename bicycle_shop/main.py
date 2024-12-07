from gui import start_app
from database import create_tables, initialize_admin
from file_manager import initialize

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