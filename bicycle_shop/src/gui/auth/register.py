import tkinter as tk

from src.database.users.user_manager import register_user
from src.utils import (
    display_error, display_success, clear_frame, get_style_config,
    create_password_field, center_window, log_action, validate_user_fields
)

def show_register_screen(global_state):
    """Display the register screen.
    
    Creates registration form interface with:
    - Username entry
    - First/Last name entries
    - Password entry with visibility toggle
    - Password confirmation entry
    - Age entry
    - Register/Back buttons
    
    Args:
        global_state: Application state dictionary containing:
            - window: Main window instance
            - main_frame: Main content frame
            - icons: Application icons
            
    Note:
        Sets minimum window size
        Centers window on screen
        Sets initial focus to username field
        Configures tab order through fields
        Binds enter key for registration
    """
    from .login import show_login_screen

    # Extract needed values from global_state
    global_state['current_screen'] = show_register_screen
    window = global_state['window']
    main_frame = global_state['main_frame']
    icons = global_state['icons']

    window.minsize(400, 450)  # Set minimum size, dont set the max size to the same as min since it causes errors.

    window.attributes("-fullscreen", False)
    window.state('normal')
    window.geometry("400x450")
    center_window(window, 400, 450) # Register screen by standard size

    # Unbind existing events from the dropdown frame to avoid trying to configure a non existent frame
    window.unbind("<Configure>")
    window.unbind("<Button-1>")

    styles = get_style_config()['login_register_screen']

    main_frame.configure(bg=styles['background'])
    clear_frame(main_frame)

    tk.Label(main_frame, text="Register", **styles['title']).pack(pady=10)

    tk.Label(main_frame, text="Username", **styles['labels']).pack()
    username_entry = tk.Entry(main_frame, **styles['entries'])
    username_entry.pack()
    username_entry.focus_set() # Sets the focus on application start to the username field

    tk.Label(main_frame, text="First Name", **styles['labels']).pack()
    first_name_entry = tk.Entry(main_frame, **styles['entries'])
    first_name_entry.pack()

    tk.Label(main_frame, text="Last Name", **styles['labels']).pack()
    last_name_entry = tk.Entry(main_frame, **styles['entries'])
    last_name_entry.pack()

    password_entry, _, _ = create_password_field(main_frame, "Password", eye_open_image=icons['eye_open'], eye_closed_image=icons['eye_closed'], style="light")

    confirm_password_entry, _, _ = create_password_field(main_frame, "Confirm Password", eye_open_image=icons['eye_open'], eye_closed_image=icons['eye_closed'], style="light")

    tk.Label(main_frame, text="Age", **styles['labels']).pack()
    age_entry = tk.Entry(main_frame, **styles['entries'])
    age_entry.pack()

    # Message label for feedback
    message_label = tk.Label(main_frame, text="", **styles['message'])
    message_label.pack()

    def register(event=None):
        """Handle user registration attempt.
        
        Validates all input fields:
        - Required fields not empty
        - Username uniqueness
        - Password requirements
        - Password confirmation match
        - Valid age
        
        Creates new user account if validation passes
        Displays success/error messages
        Logs registration attempt result
        
        Args:
            event: Key event when triggered by enter key (optional)
        """
        username = username_entry.get()
        first_name = first_name_entry.get()
        last_name = last_name_entry.get()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()
        age = age_entry.get()
        is_valid, validation_message = validate_user_fields(username, first_name, last_name,
                                                          password, confirm_password, age, 
                                                          check_type="register")
        if not is_valid:
            display_error(message_label, validation_message)
            return

        success, user_id, message = register_user(username, first_name, last_name, password, int(age))

        if success: # Success message if all requirements are met and user is created
            display_success(message_label, message)
            log_action('REGISTER', user_id=user_id, details=f"New user registered: {username}")
        else:
            display_error(message_label, message)
            log_action('REGISTER', user_id=None, details=f"Failed registration attempt for username: {username}", status='failed')

    register_button = tk.Button(main_frame, text="Register", command=register, **styles['buttons'])
    register_button.pack(pady=10)

    back_to_login_button = tk.Button(
        main_frame, 
        text="Back to Login",
        command=lambda: show_login_screen(global_state),
        **styles['buttons']
    )
    back_to_login_button.pack()

    # Binds the enter key to the register function if either the button or the main_frame is in focus
    main_frame.bind('<Return>', register)
    register_button.bind('<Return>', register)

    # Tab order for the fields and buttons
    entries = [username_entry, first_name_entry, last_name_entry, password_entry, confirm_password_entry, age_entry, register_button, back_to_login_button]
    for i in range(len(entries) - 1):
        entries[i].bind('<Tab>', lambda e, next_entry=entries[i+1]: next_entry.focus_set())
    back_to_login_button.bind('<Tab>', lambda e: username_entry.focus_set())

    back_to_login_button.bind('<Return>', lambda event: show_login_screen(global_state))