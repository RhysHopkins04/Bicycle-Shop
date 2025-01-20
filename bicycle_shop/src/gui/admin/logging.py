import tkinter as tk
from tkinter import ttk
import os

from src.database.users.user_manager import get_current_user_admin_status
from src.database.logging.log_manager import export_logs_to_temp_file
from src.utils.display import display_error, display_success, clear_frame
from src.utils.theme import get_style_config
from src.utils.logging import log_action
from src.file_system.config import get_user_logging_status, set_user_logging_status

def show_logging_screen(global_state):
    """Display the logging management screen"""
    global_state['current_screen'] = show_logging_screen
    window = global_state['window']
    content_inner_frame = global_state['content_inner_frame']
    current_username = global_state['current_username']
    current_admin_id = global_state['current_admin_id']

    if not get_current_user_admin_status(current_username):
        from ..store.listing import switch_to_store_listing
        switch_to_store_listing(is_admin=False)
        return

    clear_frame(content_inner_frame)
    styles = get_style_config()['logging']

    window.unbind("<Configure>")
    window.unbind("<Button-1>")
    
    # Create title
    tk.Label(content_inner_frame, text="System Logs", **styles['title']).pack(pady=20)

    # Create container frame for log controls
    controls_frame = tk.Frame(content_inner_frame, **styles['frame'])
    controls_frame.pack(fill="x", padx=20, pady=(0, 10))
    
    # Create filters frame
    filters_frame = tk.Frame(controls_frame, **styles['frame'])
    filters_frame.pack(side="left", fill="x")

    # User logging enable/disable combobox
    tk.Label(filters_frame, text="User Action Logging:", **styles['labels']).pack(side="left", padx=5)
    
    # Create and style the comboboxes
    combo_style = ttk.Style()
    combo_style.configure('Logging.TCombobox', 
        background=styles['frame']['bg'],
        fieldbackground=styles['text']['bg'],
        foreground=styles['text']['fg']
    )
    
    # User logging toggle combobox
    user_logging_var = tk.StringVar(value="Enabled" if get_user_logging_status() else "Disabled")
    user_logging_combo = ttk.Combobox(
        filters_frame,
        textvariable=user_logging_var,
        values=["Enabled", "Disabled"],
        state="readonly",
        style='Logging.TCombobox',
        width=10
    )
    user_logging_combo.pack(side="left", padx=5)

    def on_logging_change(event):
        """Handle logging enable/disable"""
        enabled = user_logging_var.get() == "Enabled"
        success = set_user_logging_status(enabled)
        if success:
            if enabled:
                log_action('TOGGLE_USER_LOGGING', is_admin=True, admin_id=current_admin_id, 
                          target_type='setting', target_id=None, 
                          details="Enabled user action logging")
            else:
                log_action('TOGGLE_USER_LOGGING', is_admin=True, admin_id=current_admin_id, 
                          target_type='setting', target_id=None, 
                          details="Disabled user action logging")
        else:
            log_action('TOGGLE_USER_LOGGING', is_admin=True, admin_id=current_admin_id,
                      target_type='setting', target_id=None,
                      details="Failed to toggle user logging", status='failed')

    user_logging_combo.bind('<<ComboboxSelected>>', on_logging_change)

    # Log type selection combobox
    tk.Label(filters_frame, text="View Logs:", **styles['labels']).pack(side="left", padx=(20, 5))
    log_type_var = tk.StringVar(value="User Actions")
    log_type_combo = ttk.Combobox(
        filters_frame,
        textvariable=log_type_var,
        values=["Admin Actions", "User Actions"],
        state="readonly",
        style='Logging.TCombobox',
        width=15
    )
    log_type_combo.pack(side="left", padx=5)
    log_type_combo.bind('<<ComboboxSelected>>', lambda e: refresh_logs())

    # Create main log display frame
    log_frame = tk.Frame(content_inner_frame, **styles['frame'])
    log_frame.pack(fill="both", expand=True, padx=10, pady=(10,20))

    # Create text widget for log display
    log_text = tk.Text(log_frame, wrap="word", **styles['text'])
    log_text.pack(side="left", fill="both", expand=True)

    # Add scrollbar
    scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=log_text.yview)
    scrollbar.pack(side="right", fill="y")
    log_text.configure(yscrollcommand=scrollbar.set)

    # Make text widget read-only
    log_text.configure(state="disabled")


    def cleanup_temp_files():
        """Clean up temporary log files"""
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                if file.endswith('.log'):
                    try:
                        os.remove(os.path.join(temp_dir, file))
                    except:
                        pass

    def refresh_logs():
        """Refresh logs based on selected type"""
        try:
            cleanup_temp_files()  # Clean old files first
            admin_only = log_type_var.get() == "Admin Actions"
            log_file = export_logs_to_temp_file(admin_only=admin_only)
            
            log_text.configure(state="normal")
            log_text.delete(1.0, tk.END)
            
            with open(log_file, 'r') as f:
                log_text.insert(tk.END, f.read())
                
            log_text.configure(state="disabled")
            
            # Clean up after reading
            try:
                os.remove(log_file)
            except:
                pass
                
            display_success(message_label, "Logs refreshed successfully")
        except Exception as e:
            display_error(message_label, f"Failed to load logs: {str(e)}")

    # Add cleanup to window destroy binding
    window.bind("<Destroy>", lambda e: cleanup_temp_files())

    # Create a container for the message and refresh button
    right_controls = tk.Frame(controls_frame, **styles['frame'])
    right_controls.pack(side="right", fill="x")

    # Add message label to right controls
    message_label = tk.Label(right_controls, text="", width=30, **styles['message'])
    message_label.pack(side="left", padx=10)

    # Update refresh button to pack in right_controls instead of controls_frame
    tk.Button(right_controls, text="Refresh Logs", 
            command=refresh_logs,
            **styles['buttons']).pack(side="right", padx=5)
    
    # Initial load
    refresh_logs()