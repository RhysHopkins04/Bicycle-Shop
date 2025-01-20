import tkinter as tk
from tkinter import scrolledtext
import os

from src.database.logging import get_dashboard_stats, get_dashboard_alerts, export_logs_to_temp_file
from src.utils.display import (
    create_nav_buttons, create_user_info_display, clear_frame,
    show_dropdown, hide_dropdown, hide_dropdown_on_click,
    center_window
)
from src.utils.theme import get_style_config
from src.utils.logging import log_action
from src.utils.display.dropdown import update_dropdown_position
from src.gui.auth.logout import logout
from src.gui.auth.profile import show_manage_user_screen
from src.gui.store.listing import switch_to_store_listing

def switch_to_admin_panel(global_state):
    """Navigate to the admin panel.
    
    Creates and displays the admin dashboard interface with:
    - Top bar with user info and dropdown
    - Left navigation sidebar with admin functions
    - Main content area with:
        - System statistics (products, users, etc.)
        - System alerts
        - Recent admin action logs
        
    Args:
        global_state: Application state dictionary containing:
            - window: Main window instance
            - main_frame: Main application frame
            - window_state: Window state tracking
            - icons: Application icons
            - current_username: Current user's username
            - current_first_name: User's first name
            - current_last_name: User's last name
            - current_user_id: User's ID
            - current_admin_id: Admin's ID
            
    Note:
        Updates global_state with new frame references
    """
    # Extract needed values from global_state
    global_state['current_screen'] = switch_to_admin_panel
    window = global_state['window']
    main_frame = global_state['main_frame']
    window_state = global_state['window_state']
    icons = global_state['icons']
    current_username = global_state['current_username']
    current_first_name = global_state['current_first_name']
    current_last_name = global_state['current_last_name']
    current_user_id = global_state['current_user_id']
    current_admin_id = global_state['current_admin_id']

    # Get icons
    user_icn = icons['user'] 
    admin_icn = icons['admin']
    
    window.minsize(1280, 720)
    
    if not window_state['is_fullscreen']:
        if window_state['is_maximized']:
            window.state('zoomed')
        else:
            window.state('normal')
            window.geometry("1920x1080")
            center_window(window, 1920, 1080)
    
    styles = get_style_config()['admin_panel']

    # Clear main frame and unbind events
    window.unbind("<Configure>")
    window.unbind("<Button-1>")
    clear_frame(main_frame)

    # Create top bar
    top_bar = tk.Frame(main_frame, height=100, bg=styles['top_bar']['bg'])
    top_bar.pack(side="top", fill="x")
    top_bar.pack_propagate(False)

    # Create left navigation
    left_nav = tk.Frame(main_frame, width=400, bg=styles['left_nav']['bg'])
    left_nav.pack(side="left", fill="y")
    left_nav.pack_propagate(False)

    # Create content frame
    content_frame = tk.Frame(main_frame, bg=styles['content']['frame_bg'])
    content_frame.pack(side="right", fill="both", expand=True)

    content_inner_frame = tk.Frame(content_frame, bg=styles['content']['inner_frame']['bg'])
    content_inner_frame.pack(fill="both", expand=True, padx=30, pady=30)
    
    tk.Label(top_bar, text="Dashboard", **styles['top_bar']['title']).pack(side="left", padx=20, pady=30)
    
    tk.Label(left_nav, text="Navigation", **styles['left_nav']['title']).pack(side="top", anchor="nw", padx=10, pady=10)

    # Create button frame for header
    button_frame = tk.Frame(top_bar, bg=styles['top_bar']['bg'])
    button_frame.pack(side="right", padx=20, pady=10)

    # User info display
    user_info_frame, icon_label, name_label, username_label, dropdown_indicator = create_user_info_display(
        button_frame, current_username, current_first_name, current_last_name,
        True, user_icn, admin_icn
    )
    user_info_frame.pack(side="left", padx=20, pady=10)

    # Create dropdown frame
    dropdown_frame = tk.Frame(main_frame, **styles['dropdown']['frame'])
    dropdown_frame.place_forget()

    # Add dropdown buttons
    tk.Button(dropdown_frame, text="Manage Account",
             command=lambda: show_manage_user_screen(global_state),
             **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)

    tk.Button(dropdown_frame, text="Logout",
             command=lambda: logout(global_state),
             **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)

    # Update dropdown position handler
    def update_dropdown_position_handler(event=None):
        """Update dropdown menu position when window changes.
        
        Ensures dropdown stays aligned with user info display
        when window is resized or moved.
        """
        update_dropdown_position(window, user_info_frame, dropdown_frame)

    def show_dropdown_handler(event):
        """Show dropdown menu and update its position.
        
        Shows the dropdown menu when hovering over user info
        elements and ensures correct positioning.
        """
        show_dropdown(event, user_info_frame, dropdown_frame)
        window.after(1, update_dropdown_position_handler)

    # Bind all necessary elements
    window.bind("<Configure>", update_dropdown_position_handler)
    for widget in user_info_frame.winfo_children():
        widget.bind("<Enter>", show_dropdown_handler)
    user_info_frame.bind("<Enter>", show_dropdown_handler)
    icon_label.bind("<Enter>", show_dropdown_handler)
    name_label.bind("<Enter>", show_dropdown_handler)
    username_label.bind("<Enter>", show_dropdown_handler)
    dropdown_indicator.bind("<Enter>", show_dropdown_handler)

    # Bind hide events to specific areas
    user_info_frame.bind("<Leave>", lambda e: hide_dropdown(e, user_info_frame, dropdown_frame))
    dropdown_frame.bind("<Leave>", lambda e: hide_dropdown(e, user_info_frame, dropdown_frame))

    # Hide dropdown when clicking outside
    window.bind("<Button-1>", lambda e: hide_dropdown_on_click(e, user_info_frame, dropdown_frame))

    # Create navigation buttons using the global state imported admin functions
    button_configs = [
        ("Dashboard", lambda: global_state['switch_to_admin_panel'](global_state)),
        ("Add Product", lambda: global_state['show_add_product_screen'](global_state)),
        ("Manage Products", lambda: global_state['show_manage_products_screen'](global_state)),
        ("Manage Categories", lambda: global_state['show_manage_categories_screen'](global_state)),
        ("Manage Discounts", lambda: global_state['show_manage_discounts_screen'](global_state)),
        ("Manage Users", lambda: global_state['show_manage_users_screen'](global_state)),
        ("Logging", lambda: global_state['show_logging_screen'](global_state)),
        ("View Store as User", lambda: switch_to_store_listing(global_state))
    ]
    create_nav_buttons(left_nav, button_configs)

    # Setup grid layout
    content_inner_frame.grid_columnconfigure(0, weight=1)
    content_inner_frame.grid_columnconfigure(1, weight=1) 
    content_inner_frame.grid_rowconfigure(0, weight=3)
    content_inner_frame.grid_rowconfigure(1, weight=1)

    # Create main sections
    top_left_frame = tk.Frame(content_inner_frame, **styles['dashboard']['section_frame'])
    top_right_frame = tk.Frame(content_inner_frame, **styles['dashboard']['section_frame'])
    bottom_frame = tk.Frame(content_inner_frame, **styles['dashboard']['section_frame'])

    top_left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    top_right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    bottom_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

    # Stats section
    stats_title = tk.Label(top_left_frame, text="System Statistics", **styles['dashboard']['stats_title'])
    stats_title.pack(pady=(10, 20), padx=10)

    stats_container = tk.Frame(top_left_frame, **styles['dashboard']['section_frame'])
    stats_container.pack(fill="both", expand=True, padx=10, pady=10)
    stats_container.grid_columnconfigure(0, weight=1)

    stats = get_dashboard_stats()
    stats_items = [
        ("Total Products", stats['total_products']),
        ("Listed Products", stats['listed_products']),
        ("Total Users", stats['total_users']),
        ("Active Discounts", stats['active_discounts'])
    ]

    for row, (label, value) in enumerate(stats_items):
        tk.Label(stats_container, text=f"{label}:", anchor="w", 
                **styles['dashboard']['stats_label']).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        tk.Label(stats_container, text=str(value), anchor="e",
                **styles['dashboard']['stats_value']).grid(row=row, column=1, sticky="e", padx=10, pady=5)

    # Alerts section
    alerts_title = tk.Label(top_right_frame, text="System Alerts", **styles['dashboard']['stats_title'])
    alerts_title.pack(pady=(10, 20), padx=10)

    alerts_container = tk.Frame(top_right_frame, **styles['dashboard']['section_frame'])
    alerts_container.pack(fill="both", expand=True, padx=10, pady=10)

    alerts = get_dashboard_alerts()
    if alerts:
        for alert_type, message in alerts:  # Alerts come as (type, message) tuples
            alert_frame = tk.Frame(alerts_container, **styles['dashboard']['section_frame'])
            alert_frame.pack(fill="x", padx=5, pady=2)
            
            # Create alert text with different styles for different parts
            alert_label = tk.Label(alert_frame, justify="left", anchor="w")
            alert_label.pack(fill="x", padx=5, pady=2)
            
            # Configure the label with different text styles
            alert_style = styles['dashboard']['alert_text'].copy()
            alert_style.update({
                'fg': 'red',
                'text': f"Warning: {message}"
            })
            alert_label.config(**alert_style)
    else:
        tk.Label(alerts_container, text="No current alerts",
                **styles['dashboard']['alert_text']).pack(fill="x", padx=10, pady=10)

    # Logs section
    log_frame = tk.Frame(bottom_frame, bg=styles['content']['inner_frame']['bg'])
    log_frame.pack(fill="both", expand=True)

    log_label = tk.Label(log_frame, text="Recent Admin Actions", **styles['dashboard']['log_title'])
    log_label.pack(pady=(0, 5))

    admin_log_text = scrolledtext.ScrolledText(log_frame, height=10, width=50, **styles['dashboard']['log_text'])
    admin_log_text.pack(fill="both", expand=True)

    log_file = export_logs_to_temp_file(admin_only=True)
    with open(log_file, 'r') as f:
        admin_log_text.delete('1.0', tk.END)
        admin_log_text.insert(tk.END, f.read())
    os.remove(log_file)

    # Update global state
    global_state.update({
        'content_frame': content_frame,
        'content_inner_frame': content_inner_frame,
        'user_info_frame': user_info_frame,
        'dropdown_frame': dropdown_frame
    })