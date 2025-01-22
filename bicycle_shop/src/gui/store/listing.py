import tkinter as tk
from tkinter import ttk

from src.database.users.user_manager import get_current_user_admin_status
from src.database.products.product_manager import get_products
from src.database.categories.category_manager import get_category_name
from src.utils.display import (
    display_error, display_success, clear_frame,
    show_dropdown, hide_dropdown, hide_dropdown_on_click,
    setup_search_widget, create_user_info_display,
    center_window
)
from src.utils.display.dropdown import update_dropdown_position
from src.utils.frames import (
    create_scrollable_frame, setup_product_grid, create_product_listing_frame
)
from src.utils.theme import get_style_config
from ..auth.profile import show_manage_user_screen
from ..auth.logout import logout
from .cart import show_cart

from src.gui.store.product import show_product_page

def switch_to_store_listing(global_state):
    """Navigate to the store listing.
    
    Creates main store interface with:
    - Header with store title
    - User info display with dropdown
    - Search functionality
    - Categorized product grid
    - Responsive layout
    
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
            - switch_to_admin_panel: Admin panel callback
    """
    global_state['current_screen'] = switch_to_store_listing
    window = global_state['window']
    main_frame = global_state['main_frame']
    window_state = global_state['window_state']
    icons = global_state['icons']
    current_username = global_state['current_username']
    current_first_name = global_state['current_first_name']
    current_last_name = global_state['current_last_name']
    current_user_id = global_state['current_user_id']
    switch_to_admin_panel = global_state['switch_to_admin_panel']
    
    window.minsize(1280, 720)
    
    if not window_state['is_fullscreen']:
        if window_state['is_maximized']:
            window.state('zoomed')
        else:
            window.state('normal')
            window.geometry("1920x1080")
            center_window(window, 1920, 1080)
    
    clear_frame(main_frame)

    # Check admin status
    is_admin = get_current_user_admin_status(current_username)

    # Get icons from state
    user_icn = icons['user']
    admin_icn = icons['admin']
    eye_open_image = icons['eye_open']
    eye_closed_image = icons['eye_closed']

    # Unbind existing events 
    window.unbind("<Configure>")
    window.unbind("<Button-1>")

    styles = get_style_config()['store_listing']

    # Create top bar
    top_bar = tk.Frame(main_frame, height=100, bg=styles['top_bar']['bg'])
    top_bar.pack(side="top", fill="x")
    top_bar.pack_propagate(False)

    tk.Label(top_bar, text="Store Listing", **styles['top_bar']['title']).pack(side="left", padx=20, pady=10)

    # Create button frame for right side of header
    button_frame = tk.Frame(top_bar, bg=styles['top_bar']['bg'])
    button_frame.pack(side="right", padx=20, pady=10)

    user_info_frame, icon_label, name_label, username_label, dropdown_indicator = create_user_info_display(
        button_frame,
        current_username,
        current_first_name,
        current_last_name,
        is_admin,
        user_icn,
        admin_icn
    )
    user_info_frame.pack(side="left", padx=20, pady=10)

    # Create dropdown frame
    dropdown_frame = tk.Frame(main_frame, **styles['dropdown']['frame'])
    dropdown_frame.place_forget()  # Initially hide the dropdown frame

    # Adds the options for a normal user/admin to the dropdown on store listing page (since only inner_content_frame is really setup in other further screens)
    if is_admin:
        tk.Button(dropdown_frame, text="Back to Admin Panel", command=lambda: switch_to_admin_panel(global_state), **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)
    tk.Button(dropdown_frame, text="View Cart", command=lambda: show_cart(global_state), **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)
    tk.Button(dropdown_frame, text="Manage Account", command=lambda: show_manage_user_screen(global_state), **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)
    tk.Button(dropdown_frame, text="Logout", command=lambda: logout(global_state), **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)

    def update_dropdown_position_handler(event=None):
        """Update dropdown menu position when window changes.
        
        Ensures dropdown stays properly aligned with user info display
        during window resize/move events.
        """
        update_dropdown_position(window, user_info_frame, dropdown_frame)

    def show_dropdown_handler(event):
        """Show dropdown menu and update its position.
        
        Shows dropdown when hovering over user info elements
        Updates position after showing to ensure proper alignment.
        """
        show_dropdown(event, user_info_frame, dropdown_frame)
        window.after(1, update_dropdown_position_handler)

    # Bind events for dropdown behavior
    window.bind("<Configure>", update_dropdown_position_handler)
    for widget in user_info_frame.winfo_children():
        widget.bind("<Enter>", show_dropdown_handler)
    user_info_frame.bind("<Enter>", show_dropdown_handler)
    icon_label.bind("<Enter>", show_dropdown_handler)
    name_label.bind("<Enter>", show_dropdown_handler)
    username_label.bind("<Enter>", show_dropdown_handler)
    dropdown_indicator.bind("<Enter>", show_dropdown_handler)

    # Bind hide events to specific areas
    user_info_frame.bind("<Leave>", lambda event: hide_dropdown(event, user_info_frame, dropdown_frame))
    dropdown_frame.bind("<Leave>", lambda event: hide_dropdown(event, user_info_frame, dropdown_frame))

    # Hide dropdown when clicking outside
    window.bind("<Button-1>", lambda event: hide_dropdown_on_click(event, user_info_frame, dropdown_frame))

    # Create the content frame with the dark background for future addition of dynamic product listings
    content_frame = tk.Frame(main_frame, bg=styles['content']['frame_bg'])
    content_frame.pack(side="right", fill="both", expand=True)

    # Creates an inner content frame for the dynamic widgets
    content_inner_frame = tk.Frame(content_frame, bg=styles['content']['inner_frame']['bg'], padx=50, pady=10)
    content_inner_frame.pack(fill="both", expand=True, padx=30, pady=30)

    # Create container frame for search that will properly expand/contract
    search_container = tk.Frame(top_bar, bg=styles['top_bar']['bg'])
    search_container.pack(side="left", fill="x", expand=True, padx=(20, 0))

    # Create search widget with dynamic width and capture enable/disable functions
    search_frame, search_entry, disable_search, enable_search = setup_search_widget(search_container)
    search_frame.pack(expand=True)

    # Enable search when returning to store
    enable_search()

    # Configure search entry to expand within its frame
    search_entry.pack(fill="x", expand=True, padx=100)

    global_state.update({
        'content_frame': content_frame,
        'content_inner_frame': content_inner_frame,
        'disable_search': disable_search,
        'enable_search': enable_search,
        'user_info_frame': user_info_frame,
        'dropdown_frame': dropdown_frame
    })

    def remove_focus(event):
        """Remove focus from search when clicking elsewhere.
        
        Args:
            event: Click event to check widget clicked
            
        Returns:
            str: "break" to prevent event propagation if focus removed
        """
        # Check if the event's widget is not the search entry widget or a child of dropdown frame or the frame itself
        if (event.widget != search_entry and event.widget not in dropdown_frame.winfo_children() and event.widget != dropdown_frame):
            window.focus_set() # Set the focus to the main window
            return "break" # Stop the event from propagating further

    # Bind the search entry to the filter function
    search_entry.bind("<KeyRelease>", lambda event: filter_products())

    # Create a canvas (which allows scrolling) and a scrollbar
    wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_frame(content_inner_frame)
    wrapper.pack(fill="both", expand=True, pady=(30, 0))
    canvas.pack(side="left", fill="both", expand=True)

    # Bind to all frames to catch clicks to remove the focus from the dropdown
    main_frame.bind('<Button-1>', remove_focus)
    top_bar.bind('<Button-1>', remove_focus)
    content_frame.bind('<Button-1>', remove_focus)
    content_inner_frame.bind('<Button-1>', remove_focus)
    wrapper.bind('<Button-1>', remove_focus)
    canvas.bind('<Button-1>', remove_focus)
    scrollable_frame.bind('<Button-1>', remove_focus)

    def filter_products():
        """Filter products based on search input.
        
        Filters by product name or price matching search text
        Updates display with filtered results
        Handles widget destruction gracefully
        """
        try:
            # Get the search query from the search entry widget and convert it to lowercase
            search_query = search_entry.get().lower()
            filtered_products = [
                # Iterate over each product returned by get_products function
                product for product in get_products(listed_only=True)
                # Check if the search query is in the product name (product[1]) or product description (product[2])
                if search_query in product[1].lower() or search_query in str(product[2])
            ]
            # Display the filtered products
            display_products(filtered_products)
        except tk.TclError:
            # Handle case where frame is destroyed
            pass

    def display_products(products):
        """Display products grouped by category in store listing.
        
        Creates responsive grid layout:
        - Products grouped by category
        - Category headers with separators
        - Dynamic number of columns
        - Scrolling for overflow
        
        Args:
            products: List of product tuples to display
        """
        unbind_wheel()
        clear_frame(scrollable_frame)

        if not products:
            message_label = tk.Label(scrollable_frame, text="", **styles['message'])
            message_label.pack(pady=10)
            display_error(message_label, "No products available.")
            return

        # Get number of columns for grid layout
        num_columns = setup_product_grid(scrollable_frame, canvas, products)
        if not num_columns:
            return

        # Group products by category
        categorized_products = {}
        
        for product in products:
            # Retrieve the category name for the product using its category ID
            category_name = get_category_name(product[6])
            # Check if the category name is not already a key in the categorized_products dictionary
            if category_name not in categorized_products:
                # If not, initialize an empty list for this category
                categorized_products[category_name] = []
            # Append the product to the list of products under the corresponding category
            categorized_products[category_name].append(product)

        row_count = 0

        # Display categorized products
        for category_name, category_products in categorized_products.items():
            # Create category header
            category_frame = tk.Frame(scrollable_frame, **styles['frame'])
            category_frame.pack(fill="x", pady=(20, 10))
            
            category_label = tk.Label(
                category_frame, 
                text=category_name,
                font=("Arial", 14, "bold"),
                bg=styles['frame']['bg'],
                fg=styles['category_labels']['fg']
            )
            category_label.pack(side="left", padx=10)
            
            # Built in separater line horizontal thin bar
            separator = ttk.Separator(category_frame, orient="horizontal")
            separator.pack(side="left", fill="x", expand=True, padx=10)

            # Display products in this category
            col = 0
            row_frame = None
            
            for product in category_products:
                if col % num_columns == 0:
                    row_frame = tk.Frame(scrollable_frame, **styles['frame'])
                    row_frame.pack(fill="x", pady=10, padx=20)
                    row_count += 1

                product_frame = create_product_listing_frame(
                    row_frame, 
                    product, 
                    290,
                    lambda p=product[0]: show_product_page(p, global_state)
                )

                col += 1
                if col >= num_columns:
                    col = 0

        # Enable scrolling if needed
        if row_count > 1:
            bind_wheel()
            scrollbar.pack(side="right", fill="y")
        else:
            scrollbar.pack_forget()

    # Initial display
    display_products(get_products(listed_only=True))

    # If this was called from show_product_page, update the cart button
    if hasattr(content_inner_frame, 'update_cart_callback'):
        try:
            content_inner_frame.update_cart_callback(global_state)
        except tk.TclError:
            pass  # Handle case where widgets are destroyed