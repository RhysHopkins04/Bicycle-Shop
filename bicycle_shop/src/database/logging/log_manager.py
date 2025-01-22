import tempfile
import os
from src.database.core.connection import get_connection

def log_user_action(user_id, action_type, details, status="success"):
    """Log user action to database.
    
    Args:
        user_id: ID of the user performing the action
        action_type: Type of action being performed
        details: Additional details about the action
        status: Action status (default: "success")
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Use parameterized query to prevent SQL injection
    cursor.execute("""
        INSERT INTO UserActions (user_id, action_type, details, status)
        VALUES (?, ?, ?, ?)
    """, (user_id, action_type, details, status))
    conn.commit()
    conn.close()

def log_admin_action(admin_id, action_type, target_type, target_id, details, status="success"):
    """Log admin action to database.
    
    Args:
        admin_id: ID of the admin performing the action
        action_type: Type of action being performed
        target_type: Type of entity being acted upon
        target_id: ID of the target entity
        details: Additional details about the action
        status: Action status (default: "success")
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Use parameterized query to prevent SQL injection
    cursor.execute("""
        INSERT INTO AdminActions (admin_id, action_type, target_type, target_id, details, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (admin_id, action_type, target_type, target_id, details, status))
    conn.commit()
    conn.close()

def export_logs_to_temp_file(admin_only=False):
    """Export logs to temporary file for viewing.
    
    Args:
        admin_only: If True, export only admin actions; if False, export user actions
        
    Returns:
        str: Path to the temporary log file
        
    Note:
        Creates temporary file in application's temp directory.
        File should be deleted after use.
    """
    from src.file_system.config.config_manager import get_absolute_path

   # Create temp directory in application directory for log files
    temp_dir = get_absolute_path('temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create temporary file that will be cleaned up after use
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        delete=False,
        suffix='.log',
        dir=temp_dir
    )
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if admin_only:
            # Admin logs include additional target information
            cursor.execute("""
                SELECT timestamp, 
                       COALESCE(Users.username, 'Unknown User') as username,
                       action_type, 
                       target_type, 
                       details, 
                       status 
                FROM AdminActions 
                LEFT JOIN Users ON AdminActions.admin_id = Users.id
                ORDER BY timestamp DESC
            """)
        else:
            # User logs have simpler structure
            cursor.execute("""
                SELECT timestamp,
                       COALESCE(Users.username, 'Unknown User') as username,
                       action_type,
                       details,
                       status 
                FROM UserActions 
                LEFT JOIN Users ON UserActions.user_id = Users.id
                ORDER BY timestamp DESC
            """)
        
        # Write logs to temp file in pipe-delimited format
        for row in cursor:
            temp_file.write(" | ".join(map(str, row)) + "\n")
            
        temp_file.close()
        return temp_file.name
    finally:
        conn.close()

def get_dashboard_stats():
    """Get statistics for admin dashboard.
    
    Returns:
        dict: Dashboard statistics containing:
            - total_users: Total number of users
            - total_admins: Total number of admin users
            - total_products: Total number of products
            - listed_products: Number of listed products
            - total_categories: Total number of categories
            - active_discounts: Number of active discounts
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        stats = {}

        # Gather system-wide statistics in single database connection
        # Total users
        cursor.execute("SELECT COUNT(*) FROM Users")
        stats['total_users'] = cursor.fetchone()[0]
        
        # Total admins
        cursor.execute("SELECT COUNT(*) FROM Users WHERE is_admin = 1")
        stats['total_admins'] = cursor.fetchone()[0]
        
        # Total products
        cursor.execute("SELECT COUNT(*) FROM Products")
        stats['total_products'] = cursor.fetchone()[0]
        
        # Listed products
        cursor.execute("SELECT COUNT(*) FROM Products WHERE listed = 1")
        stats['listed_products'] = cursor.fetchone()[0]
        
        # Total categories
        cursor.execute("SELECT COUNT(*) FROM Categories")
        stats['total_categories'] = cursor.fetchone()[0]
        
        # Active discounts
        cursor.execute("SELECT COUNT(*) FROM Discounts WHERE active = 1")
        stats['active_discounts'] = cursor.fetchone()[0]

        return stats
    finally:
        conn.close()

def get_dashboard_alerts():
    """Get current system alerts for admin dashboard.
    
    Returns:
        list: List of (alert_type, message) tuples where:
            - alert_type: Type of alert (e.g., "Warning")
            - message: Alert message details
            
    Note:
        Checks for:
        - Failed admin logins in last hour
        - Failed user logins in last 30 minutes
        - Low stock products (less than 5)
        - High discount usage in last hour
    """
    conn = get_connection()
    cursor = conn.cursor()
    alerts = []
    
    # Check recent failed admin login attempts (last hour)
    cursor.execute("""
        SELECT COUNT(*) FROM AdminActions 
        WHERE action_type = 'admin_login' 
        AND status = 'failed'
        AND timestamp >= datetime('now', '-1 hour')
    """)
    admin_failed_logins = cursor.fetchone()[0]
    if admin_failed_logins >= 2:
        alerts.append(("Warning", f"{admin_failed_logins} failed admin login attempts in last hour"))

    # Check recent failed user login attempts (last 30 minutes)
    cursor.execute("""
        SELECT COUNT(*) FROM UserActions 
        WHERE action_type = 'login' 
        AND status = 'failure'
        AND timestamp >= datetime('now', '-30 minutes')
    """)
    user_failed_logins = cursor.fetchone()[0]
    if user_failed_logins >= 3:
        alerts.append(("Warning", f"{user_failed_logins} failed user login attempts in last 30 minutes"))

    # Check for products with low stock
    cursor.execute("""
        SELECT COUNT(*) FROM Products 
        WHERE stock < 5 AND listed = 1
    """)
    low_stock = cursor.fetchone()[0]
    if low_stock > 0:
        alerts.append(("Warning", f"{low_stock} products low on stock"))

    # Check for unusual discount usage patterns
    cursor.execute("""
        SELECT SUM(uses) FROM Discounts 
        WHERE last_used >= datetime('now', '-1 hour')
    """)
    recent_discount_uses = cursor.fetchone()[0] or 0  # Use 0 if None
    if recent_discount_uses >= 10:
        alerts.append(("Warning", f"High discount usage: {recent_discount_uses} uses in last hour"))

    conn.close()
    return alerts