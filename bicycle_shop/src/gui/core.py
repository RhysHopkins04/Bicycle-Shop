import tkinter as tk
from tkinter import PhotoImage

from src.database.core.schema import create_tables
from src.database.users.user_manager import initialize_admin
from src.file_system.config import get_application_settings, get_icon_paths
from src.utils.display import create_fullscreen_handler

from .auth import show_login_screen

def start_app():
    """Start the Tkinter GUI application."""
    # Get configuration settings
    app_settings = get_application_settings()
    icon_paths = get_icon_paths()

    # Create main window and frame
    window = tk.Tk()
    window.title(app_settings['window_title'])
    main_frame = tk.Frame(window)
    main_frame.pack(fill="both", expand=True)

    # Load icons
    icons = {
        'eye_open': PhotoImage(file=icon_paths['password_show']),
        'eye_closed': PhotoImage(file=icon_paths['password_hide']),
        'user': PhotoImage(file=icon_paths['user_icon']),
        'admin': PhotoImage(file=icon_paths['admin_icon'])
    }

    # Window state tracking
    window_state = {
        'is_fullscreen': False,
        'is_maximized': app_settings['use_maximized']
    }

    # Global state object
    global_state = {
        'window': window,
        'main_frame': main_frame,
        'window_state': window_state,
        'icons': icons,
        'current_username': None,
        'current_first_name': None,
        'current_last_name': None,
        'current_user_id': None, 
        'current_admin_id': None,
        'disable_search': None,
        'enable_search': None,
        'user_log_text': None,
        'admin_log_text': None,
        'current_screen': None
    }

    # Import admin modules after global_state creation to avoid circular import errors
    from .admin.categories import show_manage_categories_screen
    from .admin.discounts import show_manage_discounts_screen
    from .admin.logging import show_logging_screen
    from .admin.products import show_add_product_screen, show_manage_products_screen
    from .admin.users import show_manage_users_screen
    from .admin.dashboard import switch_to_admin_panel

    # Update global state with admin functions
    global_state.update({
        'show_add_product_screen': show_add_product_screen,
        'show_manage_products_screen': show_manage_products_screen,
        'show_manage_categories_screen': show_manage_categories_screen,
        'show_manage_discounts_screen': show_manage_discounts_screen,
        'show_manage_users_screen': show_manage_users_screen,
        'show_logging_screen': show_logging_screen,
        'switch_to_admin_panel': switch_to_admin_panel
    })

    # Initialize database
    create_tables()
    initialize_admin()

    # Create fullscreen handler
    create_fullscreen_handler(window, window_state)

    # Show initial login screen
    show_login_screen(global_state)

    # Start main event loop
    window.mainloop()

if __name__ == "__main__":
    start_app()