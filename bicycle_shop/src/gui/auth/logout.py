from src.utils.logging import log_action

def logout(global_state):
    """Handle user logout process.
    
    Logs the logout action, resets all user-related state variables,
    and redirects to the login screen.
    
    Args:
        global_state: Application state dictionary containing:
            - current_user_id: ID of logged in user
            - current_username: Username of logged in user
            - current_first_name: User's first name
            - current_last_name: User's last name
            - current_admin_id: Admin ID if user is admin
            
    Note:
        Logs the logout action before clearing state
        Handles cleanup of user session data
        Redirects to login screen after logout
    """
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