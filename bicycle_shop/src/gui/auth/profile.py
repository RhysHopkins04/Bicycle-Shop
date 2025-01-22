import tkinter as tk

from src.database.core import get_connection
from src.database.users.user_manager import (
    update_user_details, get_user_id_by_username,
    update_user_password
)
from src.auth.core import authenticate_user
from src.utils.display import (
    display_error, display_success, clear_frame
)
from src.utils.theme.styles import get_style_config
from src.utils.display.components import create_password_field
from src.utils.logging import log_action
from src.utils.validation.users import validate_user_fields

def show_manage_user_screen(global_state):
    """Show dialog for users to manage their own profile.
    
    Creates modal dialog with fields for editing:
    - First name
    - Last name
    - Age
    Also provides options to:
    - Change password
    - Save changes
    
    Args:
        global_state: Application state containing:
            - window: Main window instance
            - icons: Application icons
            - current_username: Current user's username
            - current_user_id: Current user's ID
    """
    # Extract needed values from global_state
    window = global_state['window']
    icons = global_state['icons']
    username = global_state['current_username']
    user_id = global_state['current_user_id']
    current_user_id = global_state['current_user_id']
    eye_open_image = icons['eye_open']
    eye_closed_image = icons['eye_closed']

    # Check if dialog already exists for this user
    for child_window in window.winfo_children():
        if isinstance(child_window, tk.Toplevel) and hasattr(child_window, 'editing_user_id'):
            if child_window.editing_user_id == user_id:
                child_window.lift()
                return

    styles = get_style_config()['manage_user']
    dialog = tk.Toplevel(window)
    dialog.editing_user_id = user_id
    dialog.title("My Profile")
    dialog.configure(**styles['frame'])
    
    # Center dialog
    dialog_width, dialog_height = 400, 350
    dialog.minsize(dialog_width, dialog_height)
    x = (dialog.winfo_screenwidth() - dialog_width) // 2
    y = (dialog.winfo_screenheight() - dialog_height) // 2
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    # Make dialog modal
    dialog.transient(window)
    dialog.grab_set()
    
    # Ensure dialog stays on top
    dialog.focus_set()
    dialog.lift()
    dialog.attributes('-topmost', True)

    # Create container for user info
    form_frame = tk.Frame(dialog, **styles['frame'])
    form_frame.pack(fill='both', expand=True, padx=20, pady=20)

    tk.Label(form_frame, text="Your Profile", **styles['title']).pack(pady=(0, 20))

    message_label = tk.Label(form_frame, text="", **styles['message'])
    message_label.pack(pady=(0, 10))

    # Get current user details from database, bad practice will clean up later
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, first_name, last_name, age, is_admin 
        FROM Users WHERE id = ?
    """, (user_id,))
    user_data = cursor.fetchone()
    conn.close()

    if not user_data:
        display_error(message_label, "Error loading user data")
        return

    # Create entry fields
    fields = {
        'First Name': user_data[1],
        'Last Name': user_data[2],
        'Age': user_data[3]
    }

    entries = {}
    for label, value in fields.items():
        field_frame = tk.Frame(form_frame, **styles['frame'])
        field_frame.pack(pady=5, fill='x')
        
        tk.Label(
            field_frame,
            text=label + ":",
            width=12,
            anchor='w',
            **styles['labels']
        ).pack(side='left', padx=5)
        
        entry = tk.Entry(field_frame, width=20, **styles['entries'])
        entry.insert(0, str(value))
        entry.pack(side='left', padx=5, expand=True, fill='x')
        entries[label.lower().replace(' ', '_')] = entry

    def save_profile_changes():
        """Save user profile changes.
        
        Validates input fields:
        - First/Last name not empty
        - Age is valid number
        
        Updates user details in database
        Logs the action success/failure
        Closes dialog after successful update
        Shows error message on validation/update failure
        """
        first_name = entries['first_name'].get()
        last_name = entries['last_name'].get()
        age = entries['age'].get()
        
        is_valid, validation_message = validate_user_fields(
            username, first_name, last_name, "", "", age, check_type="edit"
        )
        
        if not is_valid:
            display_error(message_label, validation_message)
            return

        success, message = update_user_details(
            user_id,
            first_name,
            last_name,
            int(age),
            user_data[4]  # Keep existing admin status
        )

        if success:
            display_success(message_label, "Profile updated successfully")
            log_action('PROFILE_UPDATE', user_id=current_user_id, 
                      details=f"Updated profile: {first_name}, {last_name}, {age}")

            dialog.after(1500, dialog.destroy)
        else:
            display_error(message_label, message)
            log_action('PROFILE_UPDATE', user_id=current_user_id, 
                      details="Failed to update profile", status='failed')

    # Button frame
    button_frame = tk.Frame(form_frame, **styles['frame'])
    button_frame.pack(pady=20)

    # Save button
    tk.Button(
        button_frame,
        text="Save Changes",
        command=save_profile_changes,
        **styles['buttons']
    ).pack(side='left', padx=5)

    # Change Password button
    tk.Button(
        button_frame,
        text="Change Password",
        command=lambda: switch_to_change_password(
            username=username,
            from_source="self",
            parent_dialog=dialog,
            window=window,
            eye_open_image=eye_open_image,
            eye_closed_image=eye_closed_image,
            current_user_id=current_user_id
        ),
        **styles['buttons']
    ).pack(side='left', padx=5)

    # Close button
    tk.Button(
        button_frame,
        text="Close",
        command=dialog.destroy,
        **styles['buttons']
    ).pack(side='left', padx=5)

def switch_to_change_password(username, from_source="login", parent_dialog=None,
                            window=None, eye_open_image=None, eye_closed_image=None,
                            main_frame=None, current_admin_id=None, current_user_id=None,
                            switch_to_admin_panel=None, global_state=None):
    """Show password change screen based on context.
    
    Handles password changes for:
    - First time admin login
    - Self-initiated password change
    - Admin changing other user's password
    
    Args:
        username: Username of account to change password
        from_source: Source of change request ('login', 'self', 'admin')
        parent_dialog: Parent dialog if called from another modal
        window: Main window instance
        eye_open_image: Password show icon
        eye_closed_image: Password hide icon
        main_frame: Main content frame for login context
        current_admin_id: ID of admin making change
        current_user_id: ID of user whose password is changing
        switch_to_admin_panel: Callback to admin panel
        
    Note:
        Different layouts/fields based on context:
        - Login: Simple two field form (first time admin password change)
        - Self: Requires current password verification (self user change)
        - Admin: No current password needed (Admin change of another user)
    """
    # Get the values from global_state if not passed
    if window is None and global_state is not None:
        window = global_state.get('window')
    if main_frame is None and global_state is not None:
        main_frame = global_state.get('main_frame')
    if eye_open_image is None and global_state is not None:
        eye_open_image = global_state.get('icons', {}).get('eye_open')
    if eye_closed_image is None and global_state is not None:
        eye_closed_image = global_state.get('icons', {}).get('eye_closed')

    if from_source == "login":
        if window is None:
            raise ValueError("Window object is required for login password change")
        window.geometry("400x300")
        clear_frame(main_frame)
        styles = get_style_config()['change_password']['light']
        window.unbind("<Configure>")
        window.unbind("<Button-1>")
        
        main_frame.configure(bg=styles['title']['bg'])
        tk.Label(main_frame, text="Change Password", **styles['title']).pack(pady=10)
        
        new_password_entry, _, _ = create_password_field(
            main_frame, "New Password", 
            eye_open_image=eye_open_image, 
            eye_closed_image=eye_closed_image, 
            style="light"
        )
        
        confirm_password_entry, _, _ = create_password_field(
            main_frame, "Confirm Password",
            eye_open_image=eye_open_image, 
            eye_closed_image=eye_closed_image,
            style="light"
        )

        message_label = tk.Label(main_frame, text="", **styles['message'])
        message_label.pack(pady=(0, 10))

        def change_password():
            """Handle password change validation and update.
            
            Validates:
            - Current password if self-change
            - Password requirements
            - Password confirmation match
            
            Updates password in database
            Logs action success/failure
            Shows success/error message
            Handles appropriate navigation after success
            """
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()
            current_password = current_password_entry.get() if from_source == "self" else None

            if from_source == "self":
                success, *_ = authenticate_user(username, current_password)
                if not success:
                    display_error(message_label, "Current password is incorrect")
                    return

            is_valid, validation_message = validate_user_fields(
                username=username,
                first_name="",
                last_name="",
                password=new_password,
                confirm_password=confirm_password,
                age="",
                check_type="password"
            )
            
            if not is_valid:
                display_error(message_label, validation_message)
                return

            success, message = update_user_password(username, new_password)
            if success:
                display_success(message_label, message)
                if from_source == "login":
                    log_action('FIRST_LOGIN_PASSWORD', is_admin=True, admin_id=current_admin_id,
                             target_type='user', target_id=current_user_id,
                             details=f"Changed initial admin password")
                elif from_source == "admin":
                    log_action('MANAGE_USER', is_admin=True, admin_id=current_admin_id,
                             target_type='user', target_id=get_user_id_by_username(username),
                             details=f"Admin changed password for user: {username}")
                else:
                    log_action('PASSWORD_CHANGE', user_id=current_user_id,
                             details="Password changed successfully")
                    
                def on_success():
                    if from_source == "login":
                        switch_to_admin_panel(global_state)
                    else:
                        on_close()

                if from_source == "login":
                    main_frame.after(1500, on_success)
                else:
                    dialog.after(1500, on_success)
            else:
                display_error(message_label, message)
                if from_source == "login":
                    log_action('FIRST_LOGIN_PASSWORD', is_admin=True, admin_id=current_admin_id,
                             target_type='user', target_id=current_user_id,
                             details=f"Failed to change initial admin password: {message}",
                             status='failed')
                elif from_source == "admin":
                    log_action('MANAGE_USER', is_admin=True, admin_id=current_admin_id,
                             target_type='user', target_id=get_user_id_by_username(username),
                             details=f"Failed to change password for user {username}: {message}",
                             status='failed')
                else:
                    log_action('PASSWORD_CHANGE', user_id=current_user_id,
                             details="Failed to change password",
                             status='failed')
        
        change_button = tk.Button(
            main_frame,
            text="Change Password",
            command=change_password,
            **styles['buttons']
        )
        change_button.pack(pady=20)
        
        main_frame.bind('<Return>', lambda event: change_password())
        change_button.bind('<Return>', lambda event: change_password())
    else:
        styles = get_style_config()['manage_user']
        dialog = tk.Toplevel(window)
        dialog.title("Change Password")
        dialog.configure(**styles['frame'])
        
        if parent_dialog:
            dialog.transient(parent_dialog)
            parent_dialog.attributes('-disabled', True)
        else:
            dialog.transient(window)
            
        dialog.grab_set()
        dialog.focus_set()

        dialog_width = 400
        dialog_height = 350 if from_source == "self" else 300
        dialog.minsize(dialog_width, dialog_height)
        x = (dialog.winfo_screenwidth() - dialog_width) // 2
        y = (dialog.winfo_screenheight() - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        dialog.transient(window)
        dialog.grab_set()
        dialog.focus_set()
        dialog.attributes('-topmost', True)

        def on_close():
            """Handle dialog closure cleanup.
            
            Re-enables parent dialog if exists
            Destroys current dialog
            """
            if parent_dialog:
                parent_dialog.attributes('-disabled', False)
                parent_dialog.focus_set()
            dialog.destroy()

        form_frame = tk.Frame(dialog, **styles['frame'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(form_frame, text="Change Password", **styles['title']).pack(pady=(0, 20))
        
        message_label = tk.Label(form_frame, text="", **styles['message'])
        message_label.pack(pady=(0, 10))

        current_password_entry = None
        if from_source == "self":
            current_password_entry, _, _ = create_password_field(
                form_frame, "Current Password",
                eye_open_image=eye_open_image,
                eye_closed_image=eye_closed_image,
                style="dark"
            )

        new_password_entry, _, _ = create_password_field(
            form_frame, "New Password",
            eye_open_image=eye_open_image,
            eye_closed_image=eye_closed_image,
            style="dark"
        )
        
        confirm_password_entry, _, _ = create_password_field(
            form_frame, "Confirm Password",
            eye_open_image=eye_open_image,
            eye_closed_image=eye_closed_image,
            style="dark"
        )
        
        # Action when x on window is clicked (built into tkinter)
        dialog.protocol("WM_DELETE_WINDOW", on_close)

        button_frame = tk.Frame(form_frame, **styles['frame'])
        button_frame.pack(pady=20)

        change_button = tk.Button(
            button_frame,
            text="Change Password",
            command=change_password,
            **styles['buttons']
        )
        change_button.pack(side='left', padx=5)

        if from_source != "login":
            tk.Button(
                button_frame,
                text="Cancel",
                command=on_close,
                **styles['buttons']
            ).pack(side='left', padx=5)

        if from_source == "login":
            main_frame.bind('<Return>', lambda event: change_password())
            change_button.bind('<Return>', lambda event: change_password())