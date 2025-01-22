from .connection import get_connection

def create_tables():
    """Create necessary database tables.
    
    Creates the following tables if they don't exist:
        - Users: Store user accounts and authentication data
        - Categories: Product categories
        - Products: Store products with their details
        - ShoppingCart: User shopping cart items
        - Discounts: Store discount codes and their usage
        - UserActions: Log of user activities
        - AdminActions: Log of administrative actions
        
    Note:
        Uses SQLite foreign keys for referential integrity between tables.
        Must be called before any other database operations.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # User table with authentication and role management
    # Password and salt stored as BLOB for binary storage
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            first_name TEXT,
            last_name TEXT,
            password BLOB,
            salt BLOB,
            age INTEGER,
            is_admin INTEGER DEFAULT 0,
            password_changed INTEGER DEFAULT 0
        )
    ''')

    # Simple categories table with unique names
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')

    # Products table with category relationship
    # QR code and image paths stored as TEXT
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            qr_code TEXT,
            listed INTEGER DEFAULT 0,
            description TEXT,
            category_id INTEGER,
            image TEXT,
            stock INTEGER,
            FOREIGN KEY (category_id) REFERENCES Categories(id)
        )
    ''')
    
    # Shopping cart with user and product relationships
    # Quantity must be positive
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ShoppingCart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(id),
            FOREIGN KEY (product_id) REFERENCES Products(id)
        )
    """)

    # Discounts table for promotional features
    # Tracks usage and active status
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Discounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            percentage INTEGER NOT NULL,
            qr_code_path TEXT,
            uses INTEGER DEFAULT 0,
            last_used DATETIME DEFAULT NULL,
            active INTEGER DEFAULT 1
        )
    """)

    # Audit logging tables for user and admin actions
    # Separate tables for different detail requirements
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserActions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            action_type TEXT,
            details TEXT,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AdminActions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            admin_id INTEGER,
            action_type TEXT,
            target_type TEXT,
            target_id INTEGER,
            details TEXT,
            status TEXT,
            FOREIGN KEY (admin_id) REFERENCES Users(id)
        )
    """)

    conn.commit()
    conn.close()