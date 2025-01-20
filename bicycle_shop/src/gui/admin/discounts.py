import tkinter as tk
from tkinter import messagebox

from src.database import (
    get_all_discounts, add_discount, update_discount, 
    delete_discount, toggle_discount_status, get_current_user_admin_status
)
from src.utils import (
    display_error, display_success, clear_frame, 
    get_style_config, create_scrollable_grid_frame, log_action
)

def show_manage_discounts_screen(global_state):
    """Display the discounts management screen.
    
    Provides interface for managing discount codes including:
    - Adding new discounts with name and percentage
    - Editing existing discounts
    - Enabling/disabling discounts
    - Deleting discounts
    - Viewing all discounts in a grid layout with usage tracking
    
    Args:
        global_state: Global application state containing:
            - window: Main window instance
            - content_inner_frame: Main content frame
            - current_username: Current user's username
            - current_admin_id: Current admin's ID
            
    Note:
        Only accessible by admin users
        Non-admin users are redirected to store listing
        Creates QR codes automatically for discounts
    """
    global_state['current_screen'] = show_manage_discounts_screen
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
    styles = get_style_config()['manage_discounts']
    
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
    title_label = tk.Label(user_list_frame, text="Discount Management", **styles['title'])
    title_label.grid(row=0, column=0, pady=10)

    # Create new discount frame with grid
    new_discount_frame = tk.Frame(user_list_frame, **styles['frame'])
    new_discount_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 20))
    new_discount_frame.grid_columnconfigure(0, weight=1)

    # Create input fields frame
    input_frame = tk.Frame(new_discount_frame, **styles['frame'])
    input_frame.grid(row=0, column=0)

    # Name entry
    name_frame = tk.Frame(input_frame, **styles['frame'])
    name_frame.grid(row=0, column=0, padx=5)
    tk.Label(name_frame, text="Name:", **styles['labels']).grid(row=0, column=0, padx=(0, 5))
    name_entry = tk.Entry(name_frame, width=20, **styles['entries'])
    name_entry.grid(row=0, column=1)

    # Percentage entry
    percentage_frame = tk.Frame(input_frame, **styles['frame'])
    percentage_frame.grid(row=0, column=1, padx=5)
    tk.Label(percentage_frame, text="Percentage:", **styles['labels']).grid(row=0, column=0, padx=(0, 5))
    percentage_entry = tk.Entry(percentage_frame, width=10, **styles['entries'])
    percentage_entry.grid(row=0, column=1)

    def add_new_discount():
        """Handle adding new discount.
        
        Validates input fields and creates new discount with QR code.
        Logs action success/failure and refreshes display.
        
        Validation:
        - Name must not be empty
        - Percentage must be integer between 1-100
        """
        name = name_entry.get().strip()
        percentage = percentage_entry.get().strip()

        if not name or not percentage:
            display_error(message_label, "Please fill in all fields")
            log_action('CREATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=None, details="Failed to create discount: Empty fields", status='failed')
            return

        try:
            percentage = int(percentage)
            if not 0 < percentage <= 100:
                raise ValueError
        except ValueError:
            display_error(message_label, "Percentage must be between 1-100")
            log_action('CREATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=None, details=f"Failed to create discount: Invalid percentage format", status='failed')
            return

        success, new_id, msg = add_discount(name, percentage)
        if success:
            # Clear entries
            name_entry.delete(0, tk.END)
            percentage_entry.delete(0, tk.END)
            display_success(message_label, msg)
            log_action('CREATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=new_id, details=f"Created discount: {name} ({percentage}%)")
            display_discounts()
        else:
            display_error(message_label, msg)
            log_action('CREATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=None, details=f"Failed to create discount: {msg}", status='failed')

    # Add discount button
    tk.Button(
        input_frame,
        text="Add Discount",
        command=add_new_discount,
        **styles['buttons']
    ).grid(row=0, column=2, padx=5)

    # Message label for feedback
    message_label = tk.Label(new_discount_frame, text="", **styles['message'])
    message_label.grid(row=1, column=0, pady=(10, 0))

    # Store resize timer as an attribute of the content_inner_frame
    content_inner_frame.resize_timer = None

    def handle_resize(event=None):
        """Handle window resize events with debouncing.
        
        Prevents excessive refreshes during continuous resize
        by delaying the refresh for 150ms after last resize event.
        """
        if hasattr(content_inner_frame, 'resize_timer') and content_inner_frame.resize_timer is not None:
            window.after_cancel(content_inner_frame.resize_timer)
        content_inner_frame.resize_timer = window.after(150, display_discounts)

    # Bind the resize event with debouncing
    content_inner_frame.bind("<Configure>", handle_resize)

    # Headers frame
    scrollbar_width = 10  # Standard scrollbar width on canvas
    headers_frame = tk.Frame(user_list_frame, **styles['frame'])
    headers_frame.grid(row=2, column=0, sticky="ew", padx=(5, scrollbar_width + 10))

    # headers and weights for discounts
    headers = ["ID", "Name", "Percentage", "Uses", "Active", "Actions"]
    weights = [1, 3, 2, 1, 1, 2]

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

    # # Add debug colors
    # content_inner_frame.configure(bg='pink')  # Main container
    # user_list_frame.configure(bg='red')  # Main container
    # new_discount_frame.configure(bg='blue')  # New discount section
    # input_frame.configure(bg='green')  # Input fields container
    # headers_frame.configure(bg='yellow')  # Headers section
    # wrapper.configure(bg='purple')  # Scrollable wrapper
    # scrollable_frame.configure(bg='orange')  # Content area

    def display_discounts():
        """Display all discounts in scrollable grid layout.
        
        Shows discount information in columns:
        - ID: Unique identifier
        - Name: Discount name
        - Percentage: Discount amount
        - Uses: Number of times used
        - Active: Current status
        - Actions: Edit/Toggle/Delete buttons
        """
        # Clear existing content
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        # Configure scrollable_frame columns to match headers
        for col, weight in enumerate(weights):
            scrollable_frame.grid_columnconfigure(col, weight=weight)
        
        discounts = get_all_discounts() 
        
        for row, discount in enumerate(discounts):
            discount_id, name, percentage, qr_code_path, uses, active = discount[:6]
            
            display_values = [
                str(discount_id),
                name,
                f"{percentage}%",
                str(uses if uses is not None else "0"),
                "Yes" if active else "No"
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
                
                # # Add alternating colors to cells
                # cell_frame.configure(bg='pink' if row % 2 == 0 else 'lightblue')
            
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
                command=lambda d=discount: handle_edit_discount(d),
                **styles['buttons']
            )
            edit_btn.pack(side="left", padx=2)
            
            toggle_text = "Disable" if active else "Enable"
            toggle_btn = tk.Button(
                buttons_frame,
                text=toggle_text,
                command=lambda d=discount: handle_toggle_discount(d),
                **styles['buttons']
            )
            toggle_btn.pack(side="left", padx=2)

            delete_btn = tk.Button(
                buttons_frame,
                text="Delete",
                command=lambda d=discount: handle_delete_discount(d),
                **styles['buttons']
            )
            delete_btn.pack(side="left", padx=2)
            
            # # Color action frames
            # actions_frame.configure(bg='lightgreen')
            # buttons_frame.configure(bg='cyan')
        
        # Update scroll region
        canvas.configure(scrollregion=canvas.bbox("all"))

    def handle_edit_discount(discount):
        """Handle editing of existing discount in modal dialog.
        
        Args:
            discount: Tuple containing discount details
                (id, name, percentage, qr_path, uses, active)
                
        Creates modal dialog with:
        - Name and percentage entry fields
        - Validation of inputs
        - Success/error messages
        - Auto-generated QR code update
        """
        dialog = tk.Toplevel(window)
        dialog.title("Edit Discount")
        dialog.configure(**styles['frame'])
        
        # Set size and center dialog
        dialog_width = 400
        dialog_height = 350
        dialog.minsize(dialog_width, dialog_height)
        x = (dialog.winfo_screenwidth() - dialog_width) // 2
        y = (dialog.winfo_screenheight() - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # Make dialog modal
        dialog.transient(window)
        dialog.grab_set()
        dialog.focus_set()

        # Create form frame
        form_frame = tk.Frame(dialog, **styles['frame'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title
        tk.Label(form_frame, text="Edit Discount", **styles['title']).pack(pady=(0, 20))

        # Message label
        edit_message_label = tk.Label(form_frame, text="", **styles['message'])
        edit_message_label.pack(pady=(0, 10))

        # Create fields
        fields = {
            'Name': discount[1],
            'Percentage': str(discount[2])
        }
        
        entries = {}
        for label, value in fields.items():
            field_frame = tk.Frame(form_frame, **styles['frame'])
            field_frame.pack(pady=5, fill='x')
            
            tk.Label(
                field_frame,
                text=f"{label}:",
                width=12,
                anchor='w',
                **styles['labels']
            ).pack(side='left', padx=5)
            
            entry = tk.Entry(field_frame, width=20, **styles['entries'])
            entry.insert(0, value)
            entry.pack(side='left', padx=5, expand=True, fill='x')
            entries[label.lower()] = entry

        def save_changes():
            """Save discount changes.
            
            Validates new values and updates discount:
            - Validates name is not empty
            - Validates percentage is integer between 1-100
            - Updates discount with new values
            - Generates new QR code
            - Logs action success/failure
            - Refreshes display on success
            
            Note:
                Closes dialog after successful update
                Shows error messages in dialog for validation failures
            """
            try:
                new_name = entries['name'].get().strip()
                new_percentage = int(entries['percentage'].get().strip())
                
                if not new_name:
                    display_error(edit_message_label, "Name is required")
                    return
                    
                if not 0 < new_percentage <= 100:
                    display_error(edit_message_label, "Percentage must be between 1-100")
                    return
                    
                success, msg = update_discount(discount[0], new_name, new_percentage)
                if success:
                    display_success(edit_message_label, msg)
                    log_action('UPDATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, 
                                target_type='discount', target_id=discount[0],
                                details=f"Updated discount {discount[1]} to {new_name} ({new_percentage}%)")
                    dialog.after(1500, dialog.destroy)
                    display_discounts()
                else:
                    display_error(edit_message_label, msg)
                    log_action('UPDATE_DISCOUNT', is_admin=True, admin_id=current_admin_id,
                                target_type='discount', target_id=discount[0],
                                details=f"Failed to update discount: {msg}", status='failed')
            except ValueError:
                display_error(edit_message_label, "Invalid percentage format")

        # Button frame
        button_frame = tk.Frame(form_frame, **styles['frame'])
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Save Changes",
            command=save_changes,
            **styles['buttons']
        ).pack(side='left', padx=5)

        tk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy,
            **styles['buttons']
        ).pack(side='left', padx=5)

    def handle_toggle_discount(discount):
        """Toggle active status of discount.
        
        Args:
            discount: Tuple containing discount details
                (id, name, percentage, qr_path, uses, active)
                
        Enables/disables discount and refreshes display.
        Logs action success/failure.
        """
        success, msg = toggle_discount_status(discount[0])
        if success:
            display_success(message_label, msg)
            log_action('TOGGLE_DISCOUNT', is_admin=True, admin_id=current_admin_id,
                        target_type='discount', target_id=discount[0],
                        details=f"Toggled discount {discount[1]} active status")
            display_discounts()  # Refresh immediately
        else:
            display_error(message_label, msg)
            log_action('TOGGLE_DISCOUNT', is_admin=True, admin_id=current_admin_id,
                        target_type='discount', target_id=discount[0],
                        details=f"Failed to toggle discount status: {msg}", status='failed')

    def handle_delete_discount(discount):
        """Handle deletion of discount after confirmation.
        
        Args:
            discount: Tuple containing discount details
                (id, name, percentage, qr_path, uses, active)
                
        Shows confirmation dialog before deletion.
        Removes QR code file on successful deletion.
        Logs action success/failure.
        """
        if messagebox.askyesno("Confirm Delete", 
                                f"Are you sure you want to delete the discount '{discount[1]}'?"):
            success, msg = delete_discount(discount[0])
            if success:
                display_success(message_label, msg)
                log_action('DELETE_DISCOUNT', is_admin=True, admin_id=current_admin_id,
                            target_type='discount', target_id=discount[0],
                            details=f"Deleted discount: {discount[1]}")
                display_discounts()
            else:
                display_error(message_label, msg)
                log_action('DELETE_DISCOUNT', is_admin=True, admin_id=current_admin_id,
                            target_type='discount', target_id=discount[0],
                            details=f"Failed to delete discount: {msg}", status='failed')

    # Initial display
    display_discounts()