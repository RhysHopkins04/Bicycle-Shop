from src.utils.logging import log_action

from src.utils.logging import log_action

def logout(global_state):
    """Handle logout."""
    log_action('LOGOUT', user_id=global_state['current_user_id'], 
              details=f"User {global_state['current_username']} logged out")
    
    # Reset user state
    global_state.update({
        'current_username': None,
        'current_first_name': None,
        'current_last_name': None,
        'current_user_id': None,
        'current_admin_id': None
    })
    
    from ..auth.login import show_login_screen
    show_login_screen(global_state)