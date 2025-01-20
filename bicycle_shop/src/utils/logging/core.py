from src.file_system.config.config_manager import get_logging_settings
from src.database.logging.log_manager import log_user_action, log_admin_action

# User Action Types
ACTION_TYPES = {
    'user': {
        'LOGIN': 'login',
        'LOGOUT': 'logout',
        'REGISTER': 'register',
        'VIEW_PRODUCT': 'view_product',
        'CART_ADD': 'add_to_cart',
        'CART_UPDATE': 'update_cart',
        'PROFILE_UPDATE': 'update_profile',
        'PASSWORD_CHANGE': 'change_password'
    },
    'admin': {
        'ADMIN_LOGIN': 'admin_login',
        'FIRST_LOGIN_PASSWORD': 'first_login_password',
        'CREATE_PRODUCT': 'create_product',
        'UPDATE_PRODUCT': 'update_product',
        'DELETE_PRODUCT': 'delete_product',
        'CREATE_CATEGORY': 'create_category',
        'UPDATE_CATEGORY': 'update_category',
        'DELETE_CATEGORY': 'delete_category',
        'CREATE_DISCOUNT': 'create_discount',
        'UPDATE_DISCOUNT': 'update_discount',
        'TOGGLE_DISCOUNT': 'toggle_discount',
        'DELETE_DISCOUNT': 'delete_discount',
        'MANAGE_USER': 'manage_user',
        'DELETE_USER': 'delete_user',
        'TOGGLE_USER_LOGGING': 'toggle_logging'
    }
}

def log_event(event):
    """Log an event to a file."""
    with open("app.log", "a") as f:
        f.write(f"{event}\n")

def get_action_type(type_group, action):
    """Get action type string from dictionary"""
    return ACTION_TYPES[type_group][action]

def log_action(action_type, is_admin=False, **kwargs):
    """
    Generic logging function following DRY principles
    
    Args:
        action_type (str): Type of action being performed (use ACTION_TYPES keys)
        is_admin (bool): Whether this is an admin action
        **kwargs: Additional arguments based on action type
    """
    type_group = 'admin' if is_admin else 'user'
    action_string = get_action_type(type_group, action_type)
    
    if is_admin:
        log_admin_action(
            admin_id=kwargs.get('admin_id'),
            action_type=action_string,
            target_type=kwargs.get('target_type'),
            target_id=kwargs.get('target_id'),
            details=kwargs.get('details', ''),
            status=kwargs.get('status', 'success')
        )
    else:
        # Only log user actions if enabled
        if get_logging_settings()['user_logging_enabled']:
            log_user_action(
                user_id=kwargs.get('user_id'),
                action_type=action_string,
                details=kwargs.get('details', ''),
                status=kwargs.get('status', 'success')
            )