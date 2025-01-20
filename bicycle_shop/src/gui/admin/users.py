import tkinter as tk
from tkinter import ttk, messagebox

from src.database.users.user_manager import (
    get_current_user_admin_status, get_all_users, update_user_details,
    delete_user, get_username_by_id
)
from src.utils.display import (
    display_error, display_success, clear_frame
)
from src.utils.frames import create_scrollable_grid_frame
from src.utils.theme import get_style_config
from src.utils.validation import validate_user_fields
from src.utils.logging import log_action
from src.gui.auth.profile import switch_to_change_password
from src.gui.store.listing import switch_to_store_listing

def show_manage_users_screen(global_state):
    """Switch to user management screen"""
    global_state['current_screen'] = show_manage_users_screen
    window = global_state['window']
    content_inner_frame = global_state['content_inner_frame']
    current_username = global_state['current_username']
    current_admin_id = global_state['current_admin_id']

    if not get_current_user_admin_status(current_username):
        from ..store.listing import switch_to_store_listing
        switch_to_store_listing(is_admin=False)
        return
    
    # Unbind existing events before clearing frame
    window.unbind("<Configure>")
    window.unbind("<Button-1>")
    if hasattr(content_inner_frame, 'bind_ids'):
        for bind_id in content_inner_frame.bind_ids:
            content_inner_frame.unbind(bind_id)

    clear_frame(content_inner_frame)
    styles = get_style_config()['manage_users']

    content_inner_frame.grid_columnconfigure(0, weight=1)
    content_inner_frame.grid_rowconfigure(0, weight=1)

    # Create container frame using grid
    user_list_frame = tk.Frame(content_inner_frame, **styles['frame'])
    user_list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # Configure main container frame
    user_list_frame.grid_columnconfigure(0, weight=1)  # Make single column expand
    user_list_frame.grid_rowconfigure(3, weight=1)     # Make scrollable content expand

    # Force the frame to expand
    user_list_frame.grid_propagate(False)  # Changed to False to force size

    # Set minimum size for user_list_frame
    min_width = content_inner_frame.winfo_width() - 20  # Account for padding
    min_height = content_inner_frame.winfo_height() - 20  # Account for padding
    user_list_frame.configure(width=min_width, height=min_height)

    # Header section using grid
    title_label = tk.Label(user_list_frame, text="User Management", **styles['title'])
    title_label.grid(row=0, column=0, pady=10)

    # Message label 
    message_label = tk.Label(user_list_frame, text="", **styles['message'])
    message_label.grid(row=1, column=0, pady=5)

    # Store resize timer as an attribute of the content_inner_frame
    content_inner_frame.resize_timer = None

    def open_edit_dialog(user_id, username, first_name, last_name, age, is_admin):
        """Open dialog to edit user details."""
        # Check if dialog already exists for this user
        for child_window in window.winfo_children():
            if isinstance(child_window, tk.Toplevel) and hasattr(child_window, 'editing_user_id'):
                if child_window.editing_user_id == user_id:
                    child_window.lift()
                    return
                
        # Get parent styles for outer frame
        parent_styles = styles
        # Get specific styles for edit dialog
        dialog_styles = get_style_config()['edit_user_dialog']

        dialog = tk.Toplevel(window)
        dialog.editing_user_id = user_id
        dialog.title("Edit User")
        dialog.configure(**dialog_styles['frame'])
        
        # Center dialog
        dialog_width, dialog_height = 400, 500
        dialog.minsize(dialog_width, dialog_height)
        x = (dialog.winfo_screenwidth() - dialog_width) // 2
        y = (dialog.winfo_screenheight() - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # Make dialog modal
        dialog.transient(window)
        dialog.grab_set()
        dialog.focus_set()
        dialog.lift()
        dialog.attributes('-topmost', True)

        def on_dialog_close():
            """Handle dialog closure cleanup"""
            dialog.grab_release()
            display_users()
            dialog.destroy()

        # Bind dialog close button (X)
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)

        frame = tk.Frame(dialog, **dialog_styles['frame'])
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(frame, text="Edit User", **dialog_styles['title']).pack(pady=(0, 20))
        message_label = tk.Label(frame, text="", **dialog_styles['message'])
        message_label.pack(pady=(0, 10))

        is_current_user = (username == current_username)

        # Create entry fields
        tk.Label(frame, text="Username:", **dialog_styles['labels']).pack(anchor='w', padx=5)
        username_entry = tk.Entry(frame, width=25, **dialog_styles['entries'])
        username_entry.insert(0, username)
        username_entry.pack(pady=(0, 10), padx=5)
        username_entry.configure(state='disabled')  # Username cannot be changed

        tk.Label(frame, text="First Name:", **dialog_styles['labels']).pack(anchor='w', padx=5)
        first_name_entry = tk.Entry(frame, width=25, **dialog_styles['entries'])
        first_name_entry.insert(0, first_name)
        first_name_entry.pack(pady=(0, 10), padx=5)

        tk.Label(frame, text="Last Name:", **dialog_styles['labels']).pack(anchor='w', padx=5)
        last_name_entry = tk.Entry(frame, width=25, **dialog_styles['entries'])
        last_name_entry.insert(0, last_name)
        last_name_entry.pack(pady=(0, 10), padx=5)

        tk.Label(frame, text="Age:", **dialog_styles['labels']).pack(anchor='w', padx=5)
        age_entry = tk.Entry(frame, width=25, **dialog_styles['entries'])
        age_entry.insert(0, str(age))
        age_entry.pack(pady=(0, 10), padx=5)

        admin_var = tk.StringVar(value="Yes" if is_admin else "No")
        tk.Label(frame, text="Admin Status:", **dialog_styles['labels']).pack(anchor='w', padx=5)
        admin_combobox = ttk.Combobox(
            frame,
            textvariable=admin_var,
            values=["Yes", "No"],
            width=22,
            state='readonly' if username != current_username else 'disabled'
        )
        admin_combobox.pack(pady=(0, 10), padx=5)

        def save_changes():
            """Save user changes"""
            new_first_name = first_name_entry.get()
            new_last_name = last_name_entry.get()
            new_age = age_entry.get()
            new_is_admin = admin_var.get() == "Yes"

            is_valid, validation_message = validate_user_fields(
                username, new_first_name, new_last_name, "", "", new_age, check_type="edit"
            )

            if not is_valid:
                display_error(message_label, validation_message)
                return

            success, message = update_user_details(
                user_id,
                new_first_name,
                new_last_name,
                int(new_age),
                new_is_admin
            )

            if success:
                display_success(message_label, "User updated successfully!")
                log_action('MANAGE_USER', is_admin=True, admin_id=current_admin_id,
                        target_type='user', target_id=user_id,
                        details=f"Updated user {username}")
                display_users()
                dialog.after(1500, on_dialog_close)
            else:
                display_error(message_label, message)
                log_action('MANAGE_USER', is_admin=True, admin_id=current_admin_id,
                            target_type='user', target_id=user_id,
                            details=f"Failed to update user {username}: {message}",
                            status='failed')

        button_frame = tk.Frame(frame, **styles['frame'])
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Save",
            command=save_changes,
            width=10,
            **dialog_styles['buttons']
        ).pack(side='left', padx=5)

        tk.Button(
            button_frame,
            text="Change Password",
            command=lambda: switch_to_change_password(
                username=username,
                from_source="admin",
                parent_dialog=dialog,
                window=window,
                eye_open_image=global_state['icons']['eye_open'],
                eye_closed_image=global_state['icons']['eye_closed'],
                current_admin_id=global_state['current_admin_id']
            ),
            **dialog_styles['buttons']
        ).pack(side='left', padx=5)

        tk.Button(
            button_frame,
            text="Cancel",
            command=on_dialog_close,
            width=10,
            **dialog_styles['buttons']
        ).pack(side='left', padx=5)

    def handle_delete_user(user_id):
        """Handle user deletion"""
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
            return
            
        success, message = delete_user(user_id)
        username = get_username_by_id(user_id)
        if success:
            display_success(message_label, message)
            log_action('DELETE_USER', is_admin=True, admin_id=current_admin_id,
                        target_type='user', target_id=user_id,
                        details=f"Deleted user: {username}")
            # Add setTimeout to ensure UI updates after message
            window.after(100, display_users)
        else:
            display_error(message_label, message)
            log_action('DELETE_USER', is_admin=True, admin_id=current_admin_id,
                        target_type='user', target_id=user_id, 
                        details=f"Failed to delete user {username}: {message}",
                        status='failed')

    def display_users():
        """Display users in a scrollable grid layout."""
        # Clear existing content
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        # Configure scrollable_frame columns to match headers
        for col, weight in enumerate(weights):
            scrollable_frame.grid_columnconfigure(col, weight=weight)
        
        users = get_all_users()
        
        for row, user in enumerate(users):
            user_id, username, first_name, last_name, age, is_admin = user[:6]
            full_name = f"{first_name} {last_name}"
            
            display_values = [
                str(user_id),
                username,
                full_name,
                str(age),
                "Yes" if is_admin else "No"
            ]
            
            # Add data cells
            for col, value in enumerate(display_values):
                cell_frame = tk.Frame(scrollable_frame, **styles['frame'], height=30)
                cell_frame.grid(row=row, column=col, padx=5, pady=2, sticky="nsew")
                cell_frame.grid_propagate(False)
                cell_frame.grid_columnconfigure(0, weight=1)
                
                tk.Label(
                    cell_frame,
                    text=value,
                    **styles['cell']
                ).grid(row=0, column=0, sticky="nsew")
            
            # Actions column
            actions_frame = tk.Frame(
                scrollable_frame,
                **styles['frame'],
                height=30
            )
            actions_frame.grid(row=row, column=5, padx=5, pady=2, sticky="nsew")
            actions_frame.grid_propagate(False)
            actions_frame.grid_columnconfigure(0, weight=1)
            
            buttons_frame = tk.Frame(actions_frame, **styles['frame'])
            buttons_frame.place(relx=0.5, rely=0.5, anchor="center")
            
            edit_btn = tk.Button(
                buttons_frame,
                text="Edit",
                command=lambda u=user: open_edit_dialog(u[0], u[1], u[2], u[3], u[4], u[5]),
                **styles['buttons']
            )
            edit_btn.pack(side="left", padx=2)
            
            delete_btn = tk.Button(
                buttons_frame,
                text="Delete",
                command=lambda uid=user_id: handle_delete_user(uid),
                state="disabled" if username == current_username else "normal",
                **styles['buttons']
            )
            delete_btn.pack(side="left", padx=2)
        
        # Update scroll region
        canvas.configure(scrollregion=canvas.bbox("all"))


    def handle_resize(event=None):
        """Handle window resize events with debouncing"""
        if hasattr(content_inner_frame, 'resize_timer') and content_inner_frame.resize_timer is not None:
            window.after_cancel(content_inner_frame.resize_timer)
        content_inner_frame.resize_timer = window.after(150, display_users)

    # Bind the resize event with debouncing
    content_inner_frame.bind("<Configure>", handle_resize)

    # Headers frame
    scrollbar_width = 10  # Standard scrollbar width on canvas
    headers_frame = tk.Frame(user_list_frame, **styles['frame'])
    headers_frame.grid(row=2, column=0, sticky="ew", padx=(5, scrollbar_width + 10))

    headers = ['ID', 'Username', 'Name', 'Age', 'Admin', 'Actions']
    weights = [1, 2, 3, 1, 1, 2]

    # Configure column weights for headers
    for i, weight in enumerate(weights):
        headers_frame.grid_columnconfigure(i, weight=weight)

    header_labels = []
    for i, (header, weight) in enumerate(zip(headers, weights)):
        header_frame = tk.Frame(headers_frame, **styles['frame'], height=30)
        header_frame.grid(row=0, column=i, padx=5, sticky="nsew")
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        
        label = tk.Label(
            header_frame, 
            text=header,
            **styles['header']
        )
        label.grid(row=0, column=0, sticky="nsew")
        label.configure(anchor="center")
        header_labels.append(label)

    # Create scrollable frame using grid
    wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_grid_frame(user_list_frame)
    wrapper.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
    wrapper.grid_columnconfigure(0, weight=1)
    wrapper.grid_rowconfigure(0, weight=1)

    # Initial display
    display_users()