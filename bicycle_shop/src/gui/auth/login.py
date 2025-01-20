import tkinter as tk

from src.database.users.user_manager import get_current_user_admin_status
from src.auth import authenticate_user
from src.utils.display import display_error, clear_frame, create_password_field, center_window
from src.utils.logging import log_action
from src.utils.theme import get_style_config
from src.database.users.user_manager import get_current_user_admin_status
from src.auth import authenticate_user
from src.gui.admin.dashboard import switch_to_admin_panel
from src.gui.store.listing import switch_to_store_listing
from src.gui.auth.register import show_register_screen
from src.gui.auth.profile import switch_to_change_password

def show_login_screen(global_state):
    """Display the login screen."""
    global_state['current_screen'] = show_login_screen
    window = global_state['window']
    main_frame = global_state['main_frame']
    icons = global_state['icons']
    
    window.minsize(400, 300)
    window.attributes("-fullscreen", False)
    window.state('normal')
    window.geometry("400x300") 
    center_window(window, 400, 300)

    styles = get_style_config()['login_register_screen']
    main_frame.configure(bg=styles['background'])
    clear_frame(main_frame)

    window.unbind("<Configure>")
    window.unbind("<Button-1>")

    # Remove dropdown references from global state if they exist
    if 'dropdown_frame' in global_state:
        del global_state['dropdown_frame']
    if 'user_info_frame' in global_state:
        del global_state['user_info_frame']

    tk.Label(main_frame, text="Login", **styles['title']).pack(pady=10)

    tk.Label(main_frame, text="Username", **styles['labels']).pack()
    username_entry = tk.Entry(main_frame, **styles['entries'])
    username_entry.pack()
    username_entry.focus_set()

    password_entry, _, _ = create_password_field(
        main_frame, "Password", 
        eye_open_image=icons['eye_open'],
        eye_closed_image=icons['eye_closed'],
        style="light"
    )

    def login(event=None):
        try:
            # Store values before potentially destroying widgets
            username = username_entry.get()
            password = password_entry.get()

            is_admin_account = get_current_user_admin_status(username)
            success, is_admin, password_changed, first_name, last_name, user_id = authenticate_user(username, password)
            
            if success:
                # Clear bindings before screen switch
                window.unbind('<Return>')
                main_frame.unbind('<Return>')
                login_button.unbind('<Return>')

                # Update state with user information
                global_state.update({
                    'current_username': username,
                    'current_first_name': first_name,
                    'current_last_name': last_name,
                    'current_user_id': user_id,
                    'current_admin_id': user_id if is_admin else None
                })
                
                log_action('LOGIN', user_id=global_state['current_user_id'], 
                        details=f"Successful login")
                
                if is_admin:
                    log_action('ADMIN_LOGIN', is_admin=True, 
                            admin_id=global_state['current_admin_id'],
                            target_type='user', target_id=user_id,
                            details=f"Admin login: {username}")
                            
                    if not password_changed:
                        switch_to_change_password(global_state)
                    else:
                        switch_to_admin_panel(global_state)
                else:
                    switch_to_store_listing(global_state)
            else:
                if is_admin_account:
                    log_action('ADMIN_LOGIN', is_admin=True, 
                            admin_id=None,
                            target_type='user', 
                            target_id=None,
                            details=f"Failed admin login attempt for: {username}",
                            status='failed')
                display_error(message_label, "Invalid username or password")
                username_entry.focus_set()  # Return focus to username field
        except tk.TclError:
            # Handle case where widgets are already destroyed
            pass

    # Login button
    login_button = tk.Button(main_frame, text="Login", command=login, **styles['buttons'])
    login_button.pack(pady=5)

    message_label = tk.Label(main_frame, text="", **styles['message'])
    message_label.pack(pady=(0, 5))

    # Register button
    register_button = tk.Button(
        main_frame, 
        text="Register",
        command=lambda: show_register_screen(global_state),
        **styles['buttons']
    )
    register_button.pack()



    # Bind enter key
    window.bind('<Return>', login)
    main_frame.bind('<Return>', login)
    login_button.bind('<Return>', login)