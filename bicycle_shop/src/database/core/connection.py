import sqlite3
import os

from src.file_system.config.config_manager import get_absolute_path

DB_PATH = get_absolute_path('bicycle_shop.db')

def get_connection():
    """Establish a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: An open connection to the SQLite database
        
    Note:
        Uses the DB_PATH configured in the application settings.
        Remember to close the connection after use.
    """
    return sqlite3.connect(DB_PATH)