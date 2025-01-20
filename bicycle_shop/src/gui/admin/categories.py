import tkinter as tk
from tkinter import messagebox

from src.database import get_current_user_admin_status
from src.database.categories.category_manager import (
    get_categories, add_category, update_category, 
    delete_category, get_category_id, get_category_name
)
from src.utils.display import (
    display_error, display_success, clear_frame
)
from src.utils.frames.scrollable import create_scrollable_grid_frame
from src.utils.logging import log_action
from src.utils.theme import get_style_config
from src.utils.validation import validate_category_name


def show_manage_categories_screen(global_state):
    """Display the manage categories screen."""
    global_state['current_screen'] = show_manage_categories_screen
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
    styles = get_style_config()['manage_categories']

    content_inner_frame.grid_columnconfigure(0, weight=1)
    content_inner_frame.grid_rowconfigure(0, weight=1)

    # Create container frame using grid
    category_list_frame = tk.Frame(content_inner_frame, **styles['frame'])
    category_list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # Configure main container frame
    category_list_frame.grid_columnconfigure(0, weight=1)  # Make single column expand
    category_list_frame.grid_rowconfigure(3, weight=1)     # Make scrollable content expand

    # Force the frame to expand
    category_list_frame.grid_propagate(False) # Changed to False to force size

    # Set minimum size for user_list_frame
    min_width = content_inner_frame.winfo_width() - 20  # Account for padding
    min_height = content_inner_frame.winfo_height() - 20  # Account for padding
    category_list_frame.configure(width=min_width, height=min_height)

    # Header section using grid
    title_label = tk.Label(category_list_frame, text="Category Management", **styles['title'])
    title_label.grid(row=0, column=0, pady=10)

    # Create new category frame with grid
    new_category_frame = tk.Frame(category_list_frame, **styles['frame'])
    new_category_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 20))
    new_category_frame.grid_columnconfigure(0, weight=1)

    # Input frame
    input_frame = tk.Frame(new_category_frame, **styles['frame'])
    input_frame.grid(row=0, column=0)

    # Category name entry
    name_frame = tk.Frame(input_frame, **styles['frame'])
    name_frame.grid(row=0, column=0, padx=5)
    tk.Label(name_frame, text="Name:", **styles['labels']).grid(row=0, column=0, padx=(0, 5))
    category_entry = tk.Entry(name_frame, width=30, **styles['entries'])
    category_entry.grid(row=0, column=1)

    def handle_add_category():
        """Handle adding new category"""
        name = category_entry.get().strip()
        if not name:
            display_error(message_label, "Category name is required")
            log_action('CREATE_CATEGORY', is_admin=True, admin_id=current_admin_id, 
                      target_type='category', target_id=None, 
                      details="Failed to create category: Name required", status='failed')
            return

        is_valid, message = validate_category_name(name)
        if not is_valid:
            display_error(message_label, message)
            log_action('CREATE_CATEGORY', is_admin=True, admin_id=current_admin_id,
                      target_type='category', target_id=None,
                      details=f"Failed to create category: {message}", status='failed')
            return

        success, message = add_category(name)
        if success:
            category_id = get_category_id(name)
            category_entry.delete(0, tk.END)
            display_success(message_label, message)
            log_action('CREATE_CATEGORY', is_admin=True, admin_id=current_admin_id,
                      target_type='category', target_id=category_id,
                      details=f"Created category: {name}")
            display_categories()
        else:
            display_error(message_label, message)
            log_action('CREATE_CATEGORY', is_admin=True, admin_id=current_admin_id,
                      target_type='category', target_id=None,
                      details=f"Failed to create category: {message}", status='failed')

    # Add category button
    tk.Button(
        input_frame,
        text="Add Category",
        command=handle_add_category,
        **styles['buttons']
    ).grid(row=0, column=1, padx=5)

    # Message label for feedback
    message_label = tk.Label(new_category_frame, text="", **styles['message'])
    message_label.grid(row=1, column=0, pady=(10, 0))

    # Store resize timer
    content_inner_frame.resize_timer = None

    def handle_resize(event=None):
        """Handle window resize events with debouncing"""
        if hasattr(content_inner_frame, 'resize_timer') and content_inner_frame.resize_timer is not None:
            window.after_cancel(content_inner_frame.resize_timer)
        content_inner_frame.resize_timer = window.after(150, display_categories)

    # Bind resize event
    content_inner_frame.bind("<Configure>", handle_resize)

    # Headers frame
    scrollbar_width = 10
    headers_frame = tk.Frame(category_list_frame, **styles['frame'])
    headers_frame.grid(row=2, column=0, sticky="ew", padx=(5, scrollbar_width + 10))

    # Headers and weights
    headers = ["ID", "Name", "Actions"]
    weights = [1, 4, 2]

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
    wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_grid_frame(category_list_frame)
    wrapper.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
    wrapper.grid_columnconfigure(0, weight=1)
    wrapper.grid_rowconfigure(0, weight=1)

    def display_categories():
        """Display categories in scrollable grid layout"""
        # Clear existing content
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        # Configure scrollable_frame columns
        for col, weight in enumerate(weights):
            scrollable_frame.grid_columnconfigure(col, weight=weight)

        categories = get_categories()
        for row, category in enumerate(categories):
            category_id = get_category_id(category)

            # ID cell
            id_frame = tk.Frame(scrollable_frame, **styles['frame'], height=30)
            id_frame.grid(row=row, column=0, padx=5, pady=2, sticky="nsew")
            id_frame.grid_propagate(False)
            id_frame.grid_columnconfigure(0, weight=1)
            
            tk.Label(
                id_frame,
                text=str(category_id),
                **styles['cell']
            ).grid(row=0, column=0, sticky="nsew")

            # Name cell
            name_frame = tk.Frame(scrollable_frame, **styles['frame'], height=30)
            name_frame.grid(row=row, column=1, padx=5, pady=2, sticky="nsew")
            name_frame.grid_propagate(False)
            name_frame.grid_columnconfigure(0, weight=1)
            
            tk.Label(
                name_frame,
                text=category,
                **styles['cell']
            ).grid(row=0, column=0, sticky="nsew")

            # Actions cell
            actions_frame = tk.Frame(scrollable_frame, **styles['frame'], height=30)
            actions_frame.grid(row=row, column=2, padx=5, pady=2, sticky="nsew")
            actions_frame.grid_propagate(False)
            actions_frame.grid_columnconfigure(0, weight=1)

            buttons_frame = tk.Frame(actions_frame, **styles['frame'])
            buttons_frame.place(relx=0.5, rely=0.5, anchor="center")

            edit_btn = tk.Button(
                buttons_frame,
                text="Edit",
                command=lambda c=category, cid=category_id: handle_edit_category(cid, c),
                **styles['buttons']
            )
            edit_btn.pack(side="left", padx=2)

            delete_btn = tk.Button(
                buttons_frame,
                text="Delete",
                command=lambda cid=category_id: handle_delete_category(cid),
                **styles['buttons']
            )
            delete_btn.pack(side="left", padx=2)

        # Update scroll region
        canvas.configure(scrollregion=canvas.bbox("all"))

    def handle_edit_category(category_id, old_name):
        """Handle editing of a category in a popup dialog"""
        dialog = tk.Toplevel(window)
        dialog.title("Edit Category")
        dialog.configure(**styles['frame'])
        
        # Set size and center dialog
        dialog_width = 400
        dialog_height = 300
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
        tk.Label(form_frame, text="Edit Category", **styles['title']).pack(pady=(0, 20))

        # Message label
        edit_message_label = tk.Label(form_frame, text="", **styles['message'])
        edit_message_label.pack(pady=(0, 10))

        # Create field
        field_frame = tk.Frame(form_frame, **styles['frame'])
        field_frame.pack(pady=5, fill='x')
        
        tk.Label(
            field_frame,
            text="Name:",
            width=12,
            anchor='w',
            **styles['labels']
        ).pack(side='left', padx=5)
        
        name_entry = tk.Entry(field_frame, width=30, **styles['entries'])
        name_entry.insert(0, old_name)
        name_entry.pack(side='left', padx=5, expand=True, fill='x')

        def save_changes():
            """Save category changes"""
            new_name = name_entry.get().strip()
            
            if not new_name:
                display_error(edit_message_label, "Category name is required")
                return

            if new_name == old_name:
                display_error(edit_message_label, "No changes made")
                return

            is_valid, validation_message = validate_category_name(new_name)
            if not is_valid:
                display_error(edit_message_label, validation_message)
                return

            success, message = update_category(category_id, new_name)
            if success:
                display_success(edit_message_label, message)
                log_action('UPDATE_CATEGORY', is_admin=True, admin_id=current_admin_id,
                        target_type='category', target_id=category_id,
                        details=f"Updated category name from {old_name} to {new_name}")
                dialog.after(1500, dialog.destroy)
                display_categories()
            else:
                display_error(edit_message_label, message)
                log_action('UPDATE_CATEGORY', is_admin=True, admin_id=current_admin_id,
                        target_type='category', target_id=category_id,
                        details=f"Failed to update category: {message}", status='failed')

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

    def handle_delete_category(category_id):
        """Handle deletion of a category"""
        category_name = get_category_name(category_id)
        if messagebox.askyesno("Confirm Delete",
                            f"Are you sure you want to delete the category '{category_name}'?\n\nNote: All products in this category will be unlisted."):
            success, message = delete_category(category_id)
            if success:
                display_success(message_label, message)
                log_action('DELETE_CATEGORY', is_admin=True, admin_id=current_admin_id,
                        target_type='category', target_id=category_id,
                        details=f"Deleted category: {category_name}")
                display_categories()
            else:
                display_error(message_label, message)
                log_action('DELETE_CATEGORY', is_admin=True, admin_id=current_admin_id,
                        target_type='category', target_id=category_id,
                        details=f"Failed to delete category: {message}", status='failed')

    # Initial display
    display_categories()