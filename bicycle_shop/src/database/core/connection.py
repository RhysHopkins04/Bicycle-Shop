import sqlite3
import os

from src.file_system.config.config_manager import get_absolute_path

DB_PATH = get_absolute_path('bicycle_shop.db')

def get_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)