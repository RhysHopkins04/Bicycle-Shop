import tkinter as tk
from tkinter import ttk, filedialog as filedialog, PhotoImage, messagebox, scrolledtext
import os
import cv2

# Functions from other locations in the program: auth, database, qr_code_util
from auth import (register_user, authenticate_user, update_user_password, validate_user_edit)
from database import (create_tables, initialize_admin, get_products, get_product_by_id, get_connection, 
                      list_product, add_product, update_product, delete_product as db_delete_product, 
                      add_category, get_categories, get_category_id, get_category_name, delete_category, 
                      update_category, add_to_cart, get_cart_items, update_cart_quantity,
                      get_current_user_admin_status, get_all_users, update_user_details, delete_user, 
                      promote_user_to_admin, demote_user_from_admin, get_all_discounts, add_discount, 
                      delete_discount, update_discount, toggle_discount_status, increment_discount_uses,
                      verify_discount_qr, export_logs_to_temp_file, get_username_by_id,
                      get_user_id_by_username, get_dashboard_stats
                      )
from validation import (validate_password, validate_empty_fields, validate_password_match, validate_age, 
                        validate_user_fields, validate_username_uniqueness, validate_product_fields, 
                        validate_category_name
                        )
from utils import (display_error, display_success, clear_frame, show_dropdown, hide_dropdown, hide_dropdown_on_click, 
                   create_nav_buttons, create_user_info_display, setup_search_widget, create_scrollable_frame, 
                   create_password_field, setup_product_grid, create_product_listing_frame, create_product_management_frame, 
                   get_style_config, center_window, create_fullscreen_handler, resize_product_image, resize_qr_code,
                   create_scrollable_grid_frame, log_action, get_action_type
                   )
from file_manager import (get_application_settings, get_icon_paths, get_paths, get_user_logging_status, set_user_logging_status)

from qr_code_util import (scan_qr_code, scan_qr_code_from_file)

# Start GUI Function to be called in the main.py file post further checks for the tables and admin user.
def start_app():
    """Start the Tkinter GUI application.""" #Docstring's which i will use to help with future code documentation along with the comments.

    # Get configuration settings
    app_settings = get_application_settings()
    icon_paths = get_icon_paths()

    # Global Variables other than the main_frame 
    global main_frame, logout_button, window, current_username, current_first_name, current_last_name, current_admin_id, current_user_id, disable_search, enable_search, user_log_text, admin_log_text
    logout_button = None
    current_admin_id = None
    current_username = None
    current_first_name = None
    current_last_name = None
    current_user_id = None
    disable_search = None
    enable_search = None
    user_log_text = None
    admin_log_text = None

    # Add window state tracking
    global window_state
    window_state = {
        'is_fullscreen': False,
        'is_maximized': app_settings['use_maximized']
    }

    # Redundant but a good check to ensure that the tables and an admin user are created on startup encase they do not exist.
    create_tables()
    initialize_admin()

    # Initializes the window and sets it so its title shows as "Bicycle Shop Management"
    window = tk.Tk()
    window.title(app_settings['window_title'])

    # Creates the initial Main frame for the application used for holding the main widgets/functionality.
    main_frame = tk.Frame(window)
    main_frame.pack(fill="both", expand=True)

    # Load icons using configured paths
    eye_open_image = PhotoImage(file=icon_paths['password_show'])
    eye_closed_image = PhotoImage(file=icon_paths['password_hide'])
    user_icn = PhotoImage(file=icon_paths['user_icon'])
    admin_icn = PhotoImage(file=icon_paths['admin_icon'])

    # Checks if the screen is in fullscreen mode using an event handler shown below anmd handle the state change
    create_fullscreen_handler(window, window_state)

    # Creates the Login screen for the application
    def show_login_screen():
        """Display the login screen."""
        window.minsize(400, 300)  # Set minimum size, dont set the max size to the same as min since it causes errors.

        window.attributes("-fullscreen", False)
        window.state('normal')
        window.geometry("400x300") # Login screen size setting
        center_window(window, 400, 300) # Centers the center of the show_login_screen at the center of the screen

        # Unbind existing events from the dropdown frame to avoid trying to configure a non existent frame
        window.unbind("<Configure>")
        window.unbind("<Button-1>")

        styles = get_style_config()['login_register_screen']

        main_frame.configure(bg=styles['background']) # Sets the color of the main frame in this function to pull from the config.
        clear_frame(main_frame)

        tk.Label(main_frame, text="Login", **styles['title']).pack(pady=10)

        tk.Label(main_frame, text="Username", **styles['labels']).pack()
        username_entry = tk.Entry(main_frame, **styles['entries'])
        username_entry.pack()
        username_entry.focus_set() # Starts with the focus on this field for fast information input

        password_entry, _, _ = create_password_field(main_frame, "Password", eye_open_image=eye_open_image, eye_closed_image=eye_closed_image, style="light")

        # Login function to be called by the login button
        def login(event=None): 
            global current_username, current_first_name, current_last_name, current_admin_id, current_user_id
            username = username_entry.get()
            password = password_entry.get()

            is_admin_account = get_current_user_admin_status(username)


            success, is_admin, password_changed, first_name, last_name, user_id = authenticate_user(username, password)
            if success:
                # On successful login (all above are satisfied and user authenticates properly) set below global variables for later use in the GUI.
                current_username = username
                current_first_name = first_name
                current_last_name = last_name
                current_user_id = user_id
                
                log_action('LOGIN', user_id=current_user_id, details=f"Successful login") # Logging Statement
                if is_admin:
                    current_admin_id = user_id # Sets the global variable for later use
                    log_action('ADMIN_LOGIN', is_admin=True, admin_id=current_admin_id, target_type='user', target_id=user_id, details=f"Admin login: {username}") # Logging Statement
                    if not password_changed: # If the user is an admin but its the first login it forces the change password
                        switch_to_change_password(username, from_source="login")
                    else:
                        switch_to_admin_panel() # Switch the user straight to the admin dashboard
                else:
                    switch_to_store_listing() # Switch normal user to the normal store page.
            else:
                display_error(message_label, "Invalid credentials!")
                if is_admin_account:
                    # Log failed admin login attempt
                    log_action('ADMIN_LOGIN', is_admin=True, admin_id=None, target_type='user', target_id=None, details=f"Failed admin login attempt for admin account: {username}", status='failed') # Logging Statement
                else:
                    # Log normal failed login attempt
                    log_action('LOGIN', user_id=None, details=f"Failed login attempt for username: {username}", status='failed') # Logging Statement

        login_button = tk.Button(main_frame, text="Login", command=login, **styles['buttons'])
        login_button.pack(pady=10)

        create_account_button = tk.Button(main_frame, text="Create Account", command=show_register_screen, **styles['buttons']) # switch_to_register)
        create_account_button.pack()

        # Binds the enter key to the login function if either the button or the main_frame is in focus
        message_label = tk.Label(main_frame, text="", **styles['message']) # In this case the background is default so there is no need to define the bg as a different colour.
        message_label.pack()

        # Binds the enter key to the login function if either the button or the main_frame is in focus
        main_frame.bind('<Return>', login) 
        login_button.bind('<Return>', login)

    # Shows the register screen for if you need to create a new users on the start of the application
    def show_register_screen():
        """Display the register screen."""
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

        password_entry, _, _ = create_password_field(main_frame, "Password", eye_open_image=eye_open_image, eye_closed_image=eye_closed_image, style="light")

        confirm_password_entry, _, _ = create_password_field(main_frame, "Confirm Password", eye_open_image=eye_open_image, eye_closed_image=eye_closed_image, style="light")

        tk.Label(main_frame, text="Age", **styles['labels']).pack()
        age_entry = tk.Entry(main_frame, **styles['entries'])
        age_entry.pack()

        # Binds the enter key to the login function if either the button or the main_frame is in focus
        message_label = tk.Label(main_frame, text="", **styles['message']) # In this case the background is default so there is no need to define the bg as a different colour.
        message_label.pack()

        def register(event=None):
            username = username_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()
            age = age_entry.get()
            is_valid, validation_message = validate_user_fields(username, first_name, last_name,password, confirm_password, age, check_type="register")
            if not is_valid:
                display_error(message_label, validation_message)
                return

            success, user_id, message = register_user(username, first_name, last_name, password, int(age))

            if success: # Success message if all requirements are met and user is created
                display_success(message_label, message)
                log_action('REGISTER', user_id=user_id, details=f"New user registered: {username}") # Logging Statement
            else:
                display_error(message_label, message)
                log_action('REGISTER', user_id=None, details=f"Failed registration attempt for username: {username}", status='failed') # Logging Statement

        register_button = tk.Button(main_frame, text="Register", command=register, **styles['buttons'])
        register_button.pack(pady=10)

        back_to_login_button = tk.Button(main_frame, text="Back to Login", command=show_login_screen, **styles['buttons'])
        back_to_login_button.pack()

        # Binds the enter key to the login function if either the button or the main_frame is in focus
        main_frame.bind('<Return>', register)
        register_button.bind('<Return>', register)

        # Tab order for the fields and buttons
        entries = [username_entry, first_name_entry, last_name_entry, password_entry, confirm_password_entry, age_entry, register_button, back_to_login_button]
        for i in range(len(entries) - 1):
            entries[i].bind('<Tab>', lambda e, next_entry=entries[i+1]: next_entry.focus_set())
        back_to_login_button.bind('<Tab>', lambda e: username_entry.focus_set())

        back_to_login_button.bind('<Return>', lambda event: show_login_screen()) # If tabbed onto allows the use of the enter key to return to the login screen post registration or if register is accidentally clicked.

    # Show the Login Screen by default
    show_login_screen()

    # If the user account is a non admin (standard account) brings to this page
    def switch_to_store_listing(is_admin=False):
        """Navigate to the store listing."""
        window.minsize(1280, 720)  # Minimum size for store listing
        
        # Handle maximized state if not fullscreen, ensures that it wont bring you out of fullscreen if you pressed it again.
        if not window_state['is_fullscreen']:
            if window_state['is_maximized']:
                window.state('zoomed')
            else:
                window.state('normal')
                window.geometry("1920x1080")
                center_window(window, 1920, 1080)
        
        clear_frame(main_frame)

         # Check admin status using current user
        is_admin = get_current_user_admin_status(current_username)

        # Unbind existing events from the dropdown frame to avoid trying to configure a non existent frame
        window.unbind("<Configure>")
        window.unbind("<Button-1>")

        styles = get_style_config()['store_listing']

        # Create the top bar
        top_bar = tk.Frame(main_frame, height=100, bg=styles['top_bar']['bg'])
        top_bar.pack(side="top", fill="x")
        top_bar.pack_propagate(False)  # When set to "True" Prevent the frame from shrinking to fit its contents

        # After creating the top bar elements
        tk.Label(top_bar, text="Store Listing", **styles['top_bar']['title']).pack(side="left", padx=20, pady=10)

        # Create a frame for the buttons on the right side of the header first
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

        # Create container frame for search that will properly expand/contract
        search_container = tk.Frame(top_bar, bg=styles['top_bar']['bg'])
        search_container.pack(side="left", fill="x", expand=True, padx=(20, 0))

        # Create search widget with dynamic width and capture enable/disable functions
        global disable_search, enable_search
        search_frame, search_entry, disable_search, enable_search = setup_search_widget(search_container)
        search_frame.pack(expand=True)

        # Enable search when returning to store
        enable_search()  # Call the enable function

        # Configure search entry to expand within its frame
        search_entry.pack(fill="x", expand=True, padx=100)  # Add padding to entry itself

        def remove_focus(event):
            """Remove focus from search entry when clicking anywhere else"""
            # Check if click was not on search entry and not on dropdown
            if (event.widget != search_entry and 
                event.widget not in dropdown_frame.winfo_children() and
                event.widget != dropdown_frame):
                window.focus_set()
                return "break"  # Prevent event from propagating

        # Create a dropdown frame with a more visible style
        dropdown_frame = tk.Frame(main_frame, **styles['dropdown']['frame'])
        dropdown_frame.place_forget()  # Initially hide the dropdown frame

        current_admin_status = get_current_user_admin_status(current_username)
        if is_admin:
            tk.Button(dropdown_frame, text="Back to Admin Panel", command=switch_to_admin_panel, **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)
        tk.Button(dropdown_frame, text="View Cart", command=show_cart, **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)
        tk.Button(dropdown_frame, text="Manage Account", command=lambda: show_manage_user_screen(current_username, current_user_id),  **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)
        tk.Button(dropdown_frame, text="Logout", command=show_login_screen, **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)

        # Add update dropdown position handler
        def update_dropdown_position(event=None):
            """Update dropdown position relative to user info frame"""
            if dropdown_frame.winfo_ismapped():
                # Get window-relative coordinates for proper positioning
                x = user_info_frame.winfo_rootx() - window.winfo_rootx()
                y = (user_info_frame.winfo_rooty() + user_info_frame.winfo_height() + 20) - window.winfo_rooty()
                
                # Update position relative to main window
                dropdown_frame.place(
                    x=x,
                    y=y,
                    width=user_info_frame.winfo_width()
                )
                # Ensure dropdown stays on top
                dropdown_frame.lift()

        def show_dropdown_handler(event):
            """Show dropdown and update its position"""
            show_dropdown(event, user_info_frame, dropdown_frame)
            window.after(1, update_dropdown_position)

        # Bind events for dropdown behavior
        window.bind("<Configure>", update_dropdown_position)  # Update position on window changes
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
        global content_frame
        content_frame = tk.Frame(main_frame, bg=styles['content']['frame_bg'])
        content_frame.pack(side="right", fill="both", expand=True)  # Fills the remaining space of the window with this frame

        # Creates an inner content frame for the dynamic widgets to be added to so there is a contrast border between the header, nav bar and the widgets
        global content_inner_frame
        content_inner_frame = tk.Frame(content_frame, bg=styles['content']['inner_frame']['bg'], padx=50, pady=10)
        content_inner_frame.pack(fill="both", expand=True, padx=30, pady=30)  # Fills the remaining space of the window with this frame

        # Bind the search entry to the filter function
        search_entry.bind("<KeyRelease>", lambda event: filter_products())

        # Create a canvas (which allows scrolling) and a scrollbar
        wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_frame(content_inner_frame)
        wrapper.pack(fill="both", expand=True, pady=(30, 0)) # added 30 px padding to the top of the wrapper to accomodate for the 30 removed from the content inner frame.
        canvas.pack(side="left", fill="both", expand=True)

        # Bind to all frames to catch clicks
        main_frame.bind('<Button-1>', remove_focus)
        top_bar.bind('<Button-1>', remove_focus)
        content_frame.bind('<Button-1>', remove_focus)
        content_inner_frame.bind('<Button-1>', remove_focus)
        wrapper.bind('<Button-1>', remove_focus)  # Add wrapper binding
        canvas.bind('<Button-1>', remove_focus)   # Add canvas binding
        scrollable_frame.bind('<Button-1>', remove_focus)  # Add scrollable frame binding

        def filter_products():
            search_query = search_entry.get().lower()  # Sets the search query to the text from the search box but in full lowercase to avoid case sensitivity

            # Calls the get_products function with the limitation for only listed products and then filters the products based on the search query
            filtered_products = [
                product for product in get_products(listed_only=True)
                if search_query in product[1].lower() or search_query in str(product[2])
            ]
            display_products(filtered_products)  # Adjusts the display_products function to display only the filtered products vs the standard "products" which is all products

        def display_products(products):
            """Display products grouped by category in store listing."""
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
                category_name = get_category_name(product[6])
                if category_name not in categorized_products:
                    categorized_products[category_name] = []
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
                
                # Add separator line
                separator = ttk.Separator(category_frame, orient="horizontal")
                separator.pack(side="left", fill="x", expand=True, padx=10)

                # Display products in this category
                col = 0
                row_frame = None
                
                for product in category_products:
                    if col == 0:
                        row_frame = tk.Frame(scrollable_frame, **styles['frame'])
                        row_frame.pack(fill="x", pady=10, padx=20)
                        row_count += 1

                    product_frame = create_product_listing_frame(
                        row_frame, 
                        product, 
                        290,
                        lambda p=product[0]: show_product_page(p, user_info_frame, dropdown_frame)
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

        # Call display_products initially to show all products
        display_products(get_products(listed_only=True))

        # If this was called from show_product_page, update the cart button
        if hasattr(content_inner_frame, 'update_cart_callback'):
            content_inner_frame.update_cart_callback(user_info_frame, dropdown_frame)

    def show_product_page(product_id, user_info_frame=None, dropdown_frame=None):
        """Display the product page for the given product ID."""
        global current_user_id
        clear_frame(content_inner_frame)
        styles = get_style_config()['product_page']

        window.unbind("<Configure>")
        window.unbind("<Button-1>")

        product = get_product_by_id(product_id)
        if product:
            log_action('VIEW_PRODUCT', user_id=current_user_id, details=f"Viewed product: {product[1]}") # Logging Statement

            # Create title container frame to hold both title and back button
            title_container = tk.Frame(content_inner_frame, **styles['frame'])
            title_container.pack(fill="x", pady=(0, 8))

            # Back button on the left
            back_button = tk.Button(title_container, text="← Back", command=lambda: switch_to_store_listing(is_admin=True), **styles['buttons'])
            back_button.pack(side="left", padx=10)

            # Title in center
            tk.Label(title_container, text=product[1], **styles['title']).pack(side="left", expand=True)

            # Create outer container with reduced padding
            container_frame = tk.Frame(content_inner_frame, **styles['frame'])
            container_frame.pack(fill="both", expand=True)

            # Create scrollable frame setup
            wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_frame(container_frame)
            wrapper.pack(fill="both", expand=True)

            # Create main content frame that will be centered
            content_frame = tk.Frame(scrollable_frame, **styles['frame'])
            content_frame.pack(fill="both", expand=True, padx=40, pady=28)

            # Details container frame
            details_frame = tk.Frame(content_frame, **styles['frame'])
            details_frame.pack(fill="both", expand=True, pady=10)

            # Left side - Product image and description with reduced right padding
            left_frame = tk.Frame(details_frame, **styles['frame'])
            left_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))
            
            # Right side setup with fixed width
            right_frame = tk.Frame(details_frame, width=300, **styles['frame'])  # Set fixed width
            right_frame.pack(side="right", fill="y", padx=(10, 0))
            right_frame.pack_propagate(False)  # Maintain width

            # Create inner frame for right side content
            inner_right_frame = tk.Frame(right_frame, **styles['frame'])
            inner_right_frame.pack(fill="both", expand=True, padx=10, pady=5)

            # Price at top
            price_label = tk.Label(inner_right_frame, text=f"Price: £{product[2]:.2f}", **styles['price'])
            price_label.pack(pady=5)

            # Description box below price
            desc_frame = tk.Frame(inner_right_frame, **styles['frame'])
            desc_frame.pack(fill="x", pady=5)
            tk.Label(desc_frame, text="Description:", **styles['labels']).pack(anchor="n")
            description_label = tk.Label(desc_frame, text=product[5], wraplength=280, **styles['description'])
            description_label.pack(pady=5)

            # Create message label just above the cart button
            message_label = tk.Label(inner_right_frame, text="", **styles['message'])
            message_label.pack(pady=(5, 0))

            # Create cart button with proper user_info and dropdown frame references
            cart_button = tk.Button(
                inner_right_frame, 
                text="Add to Cart",
                command=lambda: add_to_cart_handler(user_info_frame, dropdown_frame),
                **styles['buttons']
            )
            cart_button.pack(pady=(5, 10))

            # Stock display below cart button
            stock_label = tk.Label(inner_right_frame, text=f"Stock: {product[8]}", **styles['labels'])
            stock_label.pack(pady=(0, 5))

            # Add debounce variables
            resize_timer = None
            wraplength_timer = None

            def debounced_resize(event=None):
                """Debounced version of resize_content"""
                nonlocal resize_timer
                if (resize_timer is not None):
                    window.after_cancel(resize_timer)
                resize_timer = window.after(150, lambda: resize_content(event))

            def debounced_wraplength(event=None):
                """Debounced version of update_wraplength"""
                nonlocal wraplength_timer
                if (wraplength_timer is not None):
                    window.after_cancel(wraplength_timer)
                wraplength_timer = window.after(150, lambda: update_wraplength(event))

            def resize_content(event=None):
                if (not product[7] or not left_frame.winfo_exists()):
                    return
                    
                # Calculate responsive dimensions based on window size
                window_width = window.winfo_width()
                window_height = window.winfo_height()
                
                # Scale image relative to window size
                max_img_width = min(int(window_width * 0.5), 2000)
                max_img_height = min(int(window_height * 0.6), 1600)
                min_img_width = max(int(window_width * 0.3), 600)
                min_img_height = max(int(window_height * 0.3), 400)
                
                # Scale QR code relative to window size
                qr_max_size = min(int(window_width * 0.15), 300)  # 15% of width up to 300px
                qr_min_size = 150  # Minimum 150px

                # Resize product image
                resized_image = resize_product_image(
                    product[7],
                    max_width=max_img_width,
                    max_height=max_img_height,
                    min_width=min_img_width,
                    min_height=min_img_height
                )
                
                # Update product image
                if resized_image:
                    if hasattr(left_frame, 'image_label'):
                        left_frame.image_label.configure(image=resized_image)
                        left_frame.image_label.image = resized_image
                    else:
                        left_frame.image_label = tk.Label(left_frame, image=resized_image, **styles['image_frame'])
                        left_frame.image_label.image = resized_image
                        left_frame.image_label.pack(pady=(0, 5))

                # Resize and update QR code
                if product[3]:
                    qr_size = min(max(qr_min_size, int(window_width * 0.15)), qr_max_size)
                    resized_qr = resize_qr_code(product[3], size=(qr_size, qr_size))
                    if resized_qr:
                        if hasattr(inner_right_frame, 'qr_label'):
                            inner_right_frame.qr_label.configure(image=resized_qr)
                            inner_right_frame.qr_label.image = resized_qr
                        else:
                            inner_right_frame.qr_label = tk.Label(inner_right_frame, image=resized_qr, **styles['image_frame'])
                            inner_right_frame.qr_label.image = resized_qr
                            inner_right_frame.qr_label.pack(pady=10)

            # Initial image loading
            resize_content()

            def update_wraplength(event=None):
                # Update description wraplength based on frame width
                new_width = right_frame.winfo_width() - 40
                description_label.configure(wraplength=new_width)

            # Bind resize events with debouncing
            window.bind("<Configure>", debounced_resize)
            desc_frame.bind('<Configure>', debounced_wraplength)
            
            # Enable mouse wheel scrolling
            bind_wheel()

            def add_to_cart_handler(user_info=None, dropdown=None):
                if not current_user_id:
                    display_error(message_label, "Please log in to add items to cart")
                    return
                
                success, message = add_to_cart(current_user_id, product_id)
                if success:
                    display_success(message_label, "Item added to cart")
                    log_action('CART_ADD', user_id=current_user_id, details=f"Added product {product_id} to cart") # Logging Statement
                    if user_info and dropdown:
                        try:
                            show_dropdown(None, user_info, dropdown)
                            window.after(5000, lambda: safe_hide_dropdown(user_info, dropdown))
                        except tk.TclError:
                            pass  # Ignore if widgets are destroyed
                else:
                    display_error(message_label, message)
                    log_action('CART_ADD', user_id=current_user_id, details=f"Failed to add product {product_id}", status='failed') # Logging Statement

            def safe_hide_dropdown(user_info, dropdown):
                try:
                    if user_info.winfo_exists() and dropdown.winfo_exists():
                        hide_dropdown(None, user_info, dropdown)
                except tk.TclError:
                    pass

        else:
            message_label = tk.Label(content_inner_frame, text="", **styles['message'])
            message_label.pack()
            display_error(message_label, "Product not found!")

    def show_cart():
        """Display user's shopping cart"""
        window.unbind("<Configure>")
        window.unbind("<Button-1>")

        disable_search()
        
        clear_frame(content_frame)
        styles = get_style_config()['cart']
        image_styles = get_style_config()['product_page']['image_frame']
        
        global content_inner_frame
        content_inner_frame = tk.Frame(content_frame, bg=get_style_config()['store_listing']['content']['inner_frame']['bg'], padx=50, pady=10)
        content_inner_frame.pack(fill="both", expand=True, padx=30, pady=30)

        label_styles = dict(styles['labels'])
        if 'font' in label_styles: label_styles.pop('font')
        if 'fg' in label_styles: label_styles.pop('fg')
        
        button_styles = dict(styles['buttons'])
        if 'fg' in button_styles: button_styles.pop('fg')

        cart_items = get_cart_items(current_user_id)

        nav_frame = tk.Frame(content_inner_frame, **styles['frame'])
        nav_frame.pack(fill="x", pady=(10, 0))

        wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_frame(content_inner_frame)
        wrapper.pack(fill="both", expand=True, pady=(20, 0))

        def cleanup_cart():
            unbind_wheel()
            canvas.unbind('<Configure>')
            window.unbind("<Button-1>")

        button_container = tk.Frame(nav_frame, **styles['frame'])
        button_container.pack(side="left")

        back_button = tk.Button(
            button_container, 
            text="← Back to Store", 
            command=lambda: (
                cleanup_cart(),
                switch_to_store_listing(is_admin=False)
            ), 
            **styles['buttons']
        )
        back_button.pack(side="left", padx=(0, 180))
        
        total_items = sum(item[-1] for item in cart_items)
        total_price = 0

        tk.Label(
            nav_frame,
            text=f"Your Cart ({total_items} items)",
            font=("Arial", 16, "bold"),
            fg="white",
            **label_styles
        ).pack(side="left")

        if not cart_items:
            message_label = tk.Label(scrollable_frame, text="", **styles['message'])
            message_label.pack(pady=20)
            display_error(message_label, "No items in cart")
            return

        bind_wheel()

        header_frame = tk.Frame(scrollable_frame, **styles['frame'])
        header_frame.pack(fill="x", pady=(10, 10), padx=20)
        
        tk.Label(header_frame, text="Item", width=40, anchor="w", fg="white", **label_styles).pack(side="left", padx=10)
        tk.Label(header_frame, text="Price", width=10, fg="white", **label_styles).pack(side="left", padx=10)
        tk.Label(header_frame, text="Quantity", width=15, fg="white", **label_styles).pack(side="left", padx=10)
        tk.Label(header_frame, text="Total", width=15, fg="white", **label_styles).pack(side="left", padx=10)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=20)

        def update_quantity(pid, current_qty, delta):
            new_qty = current_qty + delta
            if new_qty <= 0:
                success, message = update_cart_quantity(current_user_id, pid, 0)
                if success:
                    log_action('CART_UPDATE', user_id=current_user_id, details=f"Removed product {pid} from cart") # Logging Statement
                else:
                    log_action('CART_UPDATE', user_id=current_user_id, details=f"Failed to remove product {pid}: {message}", status='failed') # Logging Statement
            else:
                success, message = update_cart_quantity(current_user_id, pid, new_qty)
                if success:
                    log_action('CART_UPDATE', user_id=current_user_id, details=f"Updated product {pid} quantity to {new_qty}") # Logging Statement
                else:
                    log_action('CART_UPDATE', user_id=current_user_id, details=f"Failed to update product {pid}: {message}", status='failed') # Logging Statement
            show_cart()

        for item in cart_items:
            item_frame = tk.Frame(scrollable_frame, **styles['frame'])
            item_frame.pack(fill="x", pady=5, padx=20)
            
            info_frame = tk.Frame(item_frame, **styles['frame'])
            info_frame.pack(side="left", fill="x", expand=True)
            
            if item[7]:  # If image exists
                image = resize_product_image(
                    item[7],
                    max_width=100,
                    max_height=100,
                    min_width=100,
                    min_height=100
                )
                image_label = tk.Label(info_frame, image=image, **styles['frame'])
                image_label.image = image
                image_label.pack(side="left", padx=5)

            tk.Label(info_frame, text=item[1], font=("Arial", 12), fg="white", **label_styles).pack(side="left", padx=10)
            
            tk.Label(
                item_frame,
                text=f"£{item[2]:.2f}",
                font=("Arial", 11),
                fg="#666666",
                **label_styles
            ).pack(side="left", padx=(50, 10))
            
            qty_frame = tk.Frame(item_frame, **styles['frame'])
            qty_frame.pack(side="left", padx=10)
            
            tk.Button(qty_frame, text="-", command=lambda pid=item[0], qty=item[-1]: update_quantity(pid, qty, -1), width=2, **button_styles).pack(side="left", padx=2)
            tk.Label(qty_frame, text=str(item[-1]), width=3, fg="white", **label_styles).pack(side="left", padx=5)
            tk.Button(qty_frame, text="+", command=lambda pid=item[0], qty=item[-1]: update_quantity(pid, qty, 1), width=2, **button_styles).pack(side="left", padx=2)

            item_total = item[2] * item[-1]
            total_price += item_total
            tk.Label(
                item_frame,
                text=f"£{item_total:.2f}",
                font=("Arial", 11, "bold"),
                fg="white",
                **label_styles
            ).pack(side="left", padx=(50, 10))
            
            remove_button = tk.Button(
                item_frame,
                text="×",
                command=lambda pid=item[0]: (
                    update_cart_quantity(current_user_id, pid, 0),
                    show_cart()
                ),
                font=("Arial", 16, "bold"),
                fg="red",
                bd=0,
                highlightthickness=0,
                bg=styles['frame']['bg'],
                activebackground=styles['frame']['bg'],
                activeforeground="darkred",
                cursor="hand2"
            )
            remove_button.pack(side="right", padx=10)

            ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=20)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=20)

        # Summary section
        summary_frame = tk.Frame(scrollable_frame, **styles['frame'])
        summary_frame.pack(fill="x", pady=10, padx=20)

        # Subtotal label
        tk.Label(
            summary_frame,
            text=f"Subtotal: £{total_price:.2f}",
            font=("Arial", 12),
            fg="#666666",
            **label_styles
        ).pack(pady=(5, 10))

        # Create discount label but don't pack it yet
        discount_label = tk.Label(
            summary_frame,
            text="",
            fg="green",
            **label_styles
        )

        # Add Coupon button
        coupon_button = tk.Button(
            summary_frame,
            text="Add Coupon",
            command=lambda: show_coupon_options(),
            **button_styles
        )
        coupon_button.pack(pady=5)

        # Message label for feedback on coupon addition
        message_label = tk.Label(summary_frame, text="", **styles['message'])
        message_label.pack(pady=(5,0))

        # Total label after coupon button
        total_label = tk.Label(
            summary_frame,
            text=f"Total: £{total_price:.2f}",
            font=("Arial", 14, "bold"),
            fg="white",
            **label_styles
        )
        total_label.pack(pady=(0, 5))

        # Checkout button at the bottom
        tk.Button(
            summary_frame,
            text="Check Out",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            **button_styles
        ).pack(pady=10)

        def handle_webcam_scan():
            """Handle QR code scanning via webcam"""
            try:
                # Create flag for tracking if QR code was found
                qr_found = False
                cap = cv2.VideoCapture(0)
                
                # Create named window that can be closed
                cv2.namedWindow("QR Code Scanner")
                
                while True:
                    _, frame = cap.read()
                    if frame is None:
                        break
                        
                    # Detect QR code
                    detector = cv2.QRCodeDetector()
                    data, _, _ = detector.detectAndDecode(frame)
                    
                    if data:
                        qr_found = True
                        cap.release()
                        cv2.destroyAllWindows()
                        process_discount(data)
                        break
                        
                    cv2.imshow("QR Code Scanner", frame)
                    
                    # Check for window close or 'q' key
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or cv2.getWindowProperty("QR Code Scanner", cv2.WND_PROP_VISIBLE) < 1:
                        break
                
                cap.release()
                cv2.destroyAllWindows()
                
                if not qr_found:
                    display_error(message_label, "No QR code detected or scan cancelled")
                    
            except Exception as e:
                cv2.destroyAllWindows()
                display_error(message_label, f"Error accessing webcam: {str(e)}")

        def handle_file_upload():
            """Handle QR code image upload"""
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg")]
            )
            if file_path:
                try:
                    qr_data = scan_qr_code_from_file(file_path)
                    if qr_data:
                        process_discount(qr_data)
                    else:
                        display_error(message_label, "No valid QR code found in image")
                except Exception as e:
                    display_error(message_label, f"Error processing image: {str(e)}")

        def process_discount(qr_data):
            """Process the discount from QR data"""
            discount = verify_discount_qr(qr_data)
            if discount:
                discount_id, percentage = discount
                success, message = increment_discount_uses(discount_id)
                if success:
                    discounted_total = total_price * (1 - percentage/100)
                    # Clear any existing discount message
                    discount_label.pack_forget()
                    discount_label.configure(
                        text=f"Discount applied: {percentage}%"
                    )
                    # Pack after subtotal but before coupon button
                    discount_label.pack(pady=(0, 5), before=coupon_button)
                    
                    # Update total price display
                    total_label.configure(text=f"Total: £{discounted_total:.2f}")
                    
                    coupon_button.configure(text="Change Coupon")
                    display_success(message_label, "Discount applied successfully!")
            else:
                # Add error message when discount is invalid or inactive
                display_error(message_label, "Invalid or inactive discount code")

        def show_coupon_options():
            """Show dialog for coupon scanning options"""
            # Clear any existing discount message when changing coupon
            discount_label.pack_forget()
            discount_label.configure(text="")
            total_label.configure(text=f"Total: £{total_price:.2f}")

            choice_window = tk.Toplevel()
            choice_window.title("Select Scan Method")
            choice_window.configure(**styles['frame'])
            
            # Center the window
            window_width = 300
            window_height = 150
            screen_width = choice_window.winfo_screenwidth()
            screen_height = choice_window.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            choice_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            tk.Button(
                choice_window,
                text="Scan QR Code (Webcam)",
                command=lambda: (choice_window.destroy(), handle_webcam_scan()),
                **button_styles
            ).pack(pady=5)
            
            tk.Button(
                choice_window,
                text="Upload QR Code",
                command=lambda: (choice_window.destroy(), handle_file_upload()),
                **button_styles
            ).pack(pady=5)

        def check_scroll_needed(event=None):
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if bbox:
                scroll_height = bbox[3] - bbox[1]
                visible_height = canvas.winfo_height()
                
                if scroll_height > visible_height:
                    bind_wheel()
                else:
                    unbind_wheel()

        canvas.bind('<Configure>', check_scroll_needed)

    def show_manage_user_screen(username, user_id):
        """Show dialog for users to manage their own profile."""
        global window

        # Check if dialog already exists for this user
        for child_window in window.winfo_children():  # Changed variable name
            if isinstance(child_window, tk.Toplevel) and hasattr(child_window, 'editing_user_id'):
                if child_window.editing_user_id == user_id:
                    child_window.lift()
                    return

        styles = get_style_config()['manage_user']
        dialog = tk.Toplevel(window)
        dialog.editing_user_id = user_id  # Tag dialog with user ID
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

        # Message label for feedback
        message_label = tk.Label(form_frame, text="", **styles['message'])
        message_label.pack(pady=(0, 10))

        # Get current user details from database
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
            """Save user profile changes"""
            first_name = entries['first_name'].get()
            last_name = entries['last_name'].get()
            age = entries['age'].get()
            
            # Use existing validation from validation.py
            # For profile editing
            is_valid, validation_message = validate_user_fields(username, first_name, last_name, "", "", age, check_type="edit")
            
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
                log_action('PROFILE_UPDATE', user_id=current_user_id, details=f"Updated profile: {first_name}, {last_name}, {age}") # Logging Statement
                dialog.after(1500, dialog.destroy)  # Close dialog after success
            else:
                display_error(message_label, message)
                log_action('PROFILE_UPDATE', user_id=current_user_id, details="Failed to update profile", status='failed') # Logging Statement

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
            command=lambda: switch_to_change_password(username, from_source="self", parent_dialog=dialog),
            **styles['buttons']
        ).pack(side='left', padx=5)

        # Close button
        tk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy,
            **styles['buttons']
        ).pack(side='left', padx=5)


    # TODO: Add the rest of the functionality required + extras and fill out the "Dashboard" screen itself for commonly used parts of the program to speed up tasks #
    # If the user account is Admin (Administrative Account) brings to the Admin Dashboard
    def switch_to_admin_panel():
        """Navigate to the admin panel."""
        # Get current user's admin status from session or database
        current_user_is_admin = get_current_user_admin_status(current_username)  # Pass the username
    
        if not current_user_is_admin:
            # Redirect to store listing or show error
            switch_to_store_listing(is_admin=False)
            return
    
        window.minsize(1280, 720)  # Minimum size for store listing
        
        # Handle maximized state if not fullscreen, ensures that it wont bring you out of fullscreen if you pressed it again.
        if not window_state['is_fullscreen']:
            if window_state['is_maximized']:
                window.state('zoomed')
            else:
                window.state('normal')
                window.geometry("1920x1080")
                center_window(window, 1920, 1080)
                
        clear_frame(main_frame)

        styles = get_style_config()['admin_panel']

        window.unbind("<Configure>")
        window.unbind("<Button-1>")

        # Create the top bar
        top_bar = tk.Frame(main_frame, height=100, bg=styles['top_bar']['bg'])
        top_bar.pack(side="top", fill="x")
        top_bar.pack_propagate(False)  # When set to "True" Prevent the frame from shrinking to fit its contents

        # Adds the Dashboard Main title on the header with a custom font.
        tk.Label(top_bar, text="Dashboard", **styles['top_bar']['title']).pack(side="left", padx=20, pady=30)

        # Create the left navigation bar
        left_nav = tk.Frame(main_frame, width=400, bg=styles['left_nav']['bg'])
        left_nav.pack(side="left", fill="y")
        left_nav.pack_propagate(False)  # When set to "True" Prevent the frame from shrinking to fit its contents

        # Create a frame for the buttons on the right side of the header
        button_frame = tk.Frame(top_bar, bg=styles['top_bar']['bg'])
        button_frame.pack(side="right", padx=20, pady=10)

        user_info_frame, icon_label, name_label, username_label, dropdown_indicator = create_user_info_display(
            button_frame,
            current_username,
            current_first_name,
            current_last_name,
            True,
            user_icn,
            admin_icn
        )
        user_info_frame.pack(side="left", padx=20, pady=10)

        # Create a dropdown frame with a more visible style
        dropdown_frame = tk.Frame(main_frame, **styles['dropdown']['frame'])
        dropdown_frame.place_forget()  # Initially hide the dropdown frame

        # No Back to admin dashboard button since this is the admin dashboard

        # Add buttons to the dropdown frame with consistent styling
        tk.Button(dropdown_frame, text="Manage Account", command=lambda: show_manage_user_screen(current_username, current_user_id),  **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)
        tk.Button(dropdown_frame, text="Logout", command=show_login_screen, **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)

                # Add update dropdown position handler
        def update_dropdown_position(event=None):
            """Update dropdown position relative to user info frame"""
            if dropdown_frame.winfo_ismapped():
                # Get window-relative coordinates for proper positioning
                x = user_info_frame.winfo_rootx() - window.winfo_rootx()
                y = (user_info_frame.winfo_rooty() + user_info_frame.winfo_height() + 20) - window.winfo_rooty()
                
                # Update position relative to main window
                dropdown_frame.place(
                    x=x,
                    y=y,
                    width=user_info_frame.winfo_width()
                )
                # Ensure dropdown stays on top
                dropdown_frame.lift()

        def show_dropdown_handler(event):
            """Show dropdown and update its position"""
            show_dropdown(event, user_info_frame, dropdown_frame)
            window.after(1, update_dropdown_position)

        # Bind events for dropdown behavior
        window.bind("<Configure>", update_dropdown_position)  # Update position on window changes
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

        # Create the content frame with the black background for future addition of dynamic wigets
        global content_frame
        content_frame = tk.Frame(main_frame, bg=styles['content']['frame_bg'])
        content_frame.pack(side="right", fill="both", expand=True) # Fills the remaining space of the window with this frame

        # Creates an inner content frame for the dynamic widgets to be added to so there is a contrast border between the header, nav bar and the widgets
        global content_inner_frame
        content_inner_frame = tk.Frame(content_frame, bg=styles['content']['inner_frame']['bg'], padx=50, pady=10)
        content_inner_frame.pack(fill="both", expand=True, padx=30, pady=30)  # Fills the remaining space of the window with this frame
        
        # Text lable that just announces the below are for the naivgation of the application styled like a webapp site
        tk.Label(left_nav, text="Navigation", **styles['left_nav']['title']).pack(side="top", anchor="nw", padx=10, pady=10)

        # Replace the current button creation code with:
        button_configs = [
            ("Dashboard", switch_to_admin_panel),
            ("Add Product", show_add_product_screen),
            ("Manage Products", show_manage_products_screen),
            ("Manage Categories", show_manage_categories_screen),
            ("Manage Discounts", show_manage_discounts_screen),
            ("Manage Users", show_manage_users_screen),
            ("Logging", show_logging_screen),
            ("View Store as User", lambda: switch_to_store_listing(is_admin=True))
        ]
        create_nav_buttons(left_nav, button_configs)

        # Setup grid layout for dashboard main sections
        content_inner_frame.grid_columnconfigure(0, weight=1)
        content_inner_frame.grid_columnconfigure(1, weight=1)
        content_inner_frame.grid_rowconfigure(0, weight=3)  # Top section
        content_inner_frame.grid_rowconfigure(1, weight=1)  # Bottom log section

        # Create main sections using grid
        top_left_frame = tk.Frame(content_inner_frame, **styles['dashboard']['section_frame'])
        top_right_frame = tk.Frame(content_inner_frame, **styles['dashboard']['section_frame'])
        bottom_frame = tk.Frame(content_inner_frame, **styles['dashboard']['section_frame'])

        # Place frames in grid
        top_left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        top_right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Create the Stats widget on the top left of the dashboard page.
        # Add Stats Title
        stats_title = tk.Label(top_left_frame, text="System Statistics", **styles['dashboard']['stats_title'])
        stats_title.pack(pady=(10, 20), padx=10)

        # Get stats from database
        stats = get_dashboard_stats()

        # Create stats container with grid layout
        stats_container = tk.Frame(top_left_frame, **styles['dashboard']['section_frame'])
        stats_container.pack(fill="both", expand=True, padx=10, pady=10)
        stats_container.grid_columnconfigure(0, weight=1)

        # Stats items with labels and values
        stats_items = [
            ("Total Products", stats['total_products']),
            ("Listed Products", stats['listed_products']),
            ("Total Users", stats['total_users']),
            ("Active Discounts", stats['active_discounts'])
        ]

        for row, (label, value) in enumerate(stats_items):
            # Label
            tk.Label(stats_container, text=f"{label}:", anchor="w", **styles['dashboard']['stats_label']).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            # Value 
            tk.Label(stats_container, text=str(value), anchor="e", **styles['dashboard']['stats_value']).grid(row=row, column=1, sticky="e", padx=10, pady=5)

        # Create the logs widget on the bottom of the dashboard page.
        log_frame = tk.Frame(bottom_frame, bg=styles['content']['inner_frame']['bg'])
        log_frame.pack(fill="both", expand=True)

        log_label = tk.Label(log_frame, text="Recent Admin Actions", **styles['dashboard']['log_title'])
        log_label.pack(pady=(0, 5))

        # Create scrolled text area for logs
        global admin_log_text
        admin_log_text = scrolledtext.ScrolledText(log_frame, height=10, width=50, **styles['dashboard']['log_text'])
        admin_log_text.pack(fill="both", expand=True)

        # Load initial log data
        log_file = export_logs_to_temp_file(admin_only=True)
        with open(log_file, 'r') as f:
            admin_log_text.delete('1.0', tk.END)
            admin_log_text.insert(tk.END, f.read())
        os.remove(log_file)  # Clean up temp file

    def show_add_product_screen():
        """Display the add product screen."""
        clear_frame(content_inner_frame)

        styles = get_style_config()['add_product']

        window.unbind("<Configure>")
        window.unbind("<Button-1>")

        combo_style = ttk.Style()
        combo_style.configure('Add.TCombobox',
            background=styles['combobox']['bg'],
            fieldbackground=styles['combobox']['fieldbackground'],
            foreground=styles['combobox']['fg'],
            selectbackground=styles['combobox']['selectbackground'],
            selectforeground=styles['combobox']['selectforeground']
        )

        tk.Label(content_inner_frame, text="Add Product", **styles['title']).pack(pady=10)

        tk.Label(content_inner_frame, text="Name", **styles['labels']).pack()
        name_entry = tk.Entry(content_inner_frame, **styles['entries'])
        name_entry.pack()

        tk.Label(content_inner_frame, text="Price", **styles['labels']).pack()
        price_entry = tk.Entry(content_inner_frame, **styles['entries'])
        price_entry.pack()

        tk.Label(content_inner_frame, text="Description", **styles['labels']).pack()
        description_entry = tk.Entry(content_inner_frame, **styles['entries'])
        description_entry.pack()

        tk.Label(content_inner_frame, text="Category", **styles['labels']).pack()
        category_combobox = ttk.Combobox(content_inner_frame, values=get_categories(), width=price_entry.cget("width") - 3, style='Add.TCombobox')
        category_combobox.pack()

        tk.Label(content_inner_frame, text="Image", **styles['labels']).pack()
        image_path = tk.StringVar()
        image_entry = tk.Entry(content_inner_frame, textvariable=image_path, state='readonly', **styles['entries'])
        image_entry.pack()

        def select_image():
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
            if file_path:
                image_path.set(file_path)
        
        select_image_button = tk.Button(content_inner_frame, text="Select Image", command=select_image, **styles['buttons'])
        select_image_button.pack()

        tk.Label(content_inner_frame, text="Stock", **styles['labels']).pack()
        stock_entry = tk.Entry(content_inner_frame, **styles['entries'])
        stock_entry.pack()

        tk.Label(content_inner_frame, text="Listed", **styles['labels']).pack()
        listed_var = tk.StringVar(value="No")
        listed_combobox = ttk.Combobox(content_inner_frame, textvariable=listed_var, values=["Yes", "No"], width=price_entry.cget("width") - 3, style='Add.TCombobox')
        listed_combobox.pack()

        message_label = tk.Label(content_inner_frame, text="", **styles['message'])
        message_label.pack(pady=10)
        
        def handle_add_product():
            """Handle adding a new product."""
            name = name_entry.get()
            price = price_entry.get()
            description = description_entry.get()
            category = category_combobox.get()
            image = image_path.get()
            stock = stock_entry.get()
            listed = 1 if listed_var.get() == "Yes" else 0

            is_valid, message = validate_product_fields(name, price, stock, listed, category, image, description)
            if not is_valid:
                display_error(message_label, message)
                return

            # Convert values after validation
            price = float(price)
            stock = int(stock) if stock else 0
            category_id = get_category_id(category) if category else None

            # Now just pass None for qr_code - it will be generated in database.py
            success, product_id, message = add_product(name, price, None, listed, description, category_id, image, stock)
    
            if success:
                display_success(message_label, "Product added successfully!")
                log_action('CREATE_PRODUCT', is_admin=True, admin_id=current_admin_id, target_type='product', target_id=product_id, details=f"Created product: {name} (Price: £{price}, Stock: {stock}, Listed: {listed})") # Logging Statement
            else:
                display_error(message_label, message)
                log_action('CREATE_PRODUCT', is_admin=True, admin_id=current_admin_id, target_type='product', target_id=None, details=f"Failed to create product: {message}", status='failed') # Logging Statement
        
        tk.Button(content_inner_frame, text="Add Product", command=handle_add_product, **styles['buttons']).pack(pady=10) # Button that calls this function to add the products to the database

    def show_manage_products_screen():
        """Display the manage products screen."""
        clear_frame(content_inner_frame)

        styles = get_style_config()['manage_products']

        window.unbind("<Configure>")
        window.unbind("<Button-1>")

        title_label = tk.Label(content_inner_frame, text="Manage Products", **styles['title'])
        title_label.pack(pady=(10, 5))

        # Create container frame for search that will properly expand/contract
        search_container = tk.Frame(content_inner_frame, bg=styles['frame']['bg'])
        search_container.pack(fill="x", pady=(5, 10))

        # Create search widget with dynamic width and capture all return values
        global disable_search, enable_search
        search_frame, search_entry, disable_search, enable_search = setup_search_widget(search_container)
        search_frame.pack(expand=True)

        # Configure search entry to expand within its frame
        search_entry.pack(fill="x", expand=True, padx=100)  # Add padding to entry itself

        # Bind the search entry to the filter function
        search_entry.bind("<KeyRelease>", lambda event: filter_products())

        def remove_focus(event):
            """Remove focus from search entry when clicking anywhere else"""
            # Check if click was not on search entry and not on dropdown
            if (event.widget != search_entry):
                window.focus_set()
                return "break"  # Prevent event from propagating

        def filter_products():
            search_query = search_entry.get().lower() # Sets the search query to the text from the search box but in full lowercase to avoid case sensitivity

            # Calls the get_products function without the limitation for only listed products and then filters the products based on the search query
            filtered_products = [
                product for product in get_products(listed_only=False)
                if search_query in product[1].lower() or search_query in str(product[2])
            ]
            display_products(filtered_products) # Adjusts the display_products function to display the only the filtered products vs the standard "products" which is all products

        # Create a canvas (which allows scrolling) and a scrollbar
        wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_frame(content_inner_frame)
        wrapper.pack(fill="both", expand=True)
        canvas.pack(side="left", fill="both", expand=True)

        # Bind to all frames to catch clicks
        main_frame.bind('<Button-1>', remove_focus)
        content_frame.bind('<Button-1>', remove_focus)
        content_inner_frame.bind('<Button-1>', remove_focus)
        wrapper.bind('<Button-1>', remove_focus)  # Add wrapper binding
        canvas.bind('<Button-1>', remove_focus)   # Add canvas binding
        scrollable_frame.bind('<Button-1>', remove_focus)  # Add scrollable frame binding

        def handle_delete_product(product_id):
            """Handle product deletion and refresh display."""
            product = get_product_by_id(product_id)
            if product:
                    product_name = product[1]  # Get name before deletion
                    success, msg = db_delete_product(product_id)
                    if success:
                        display_products(get_products(listed_only=False))
                        log_action('DELETE_PRODUCT', is_admin=True, admin_id=current_admin_id, target_type='product', target_id=product_id, details=f"Deleted product: {product_name}") # Logging Statement
                    else:
                        messagebox.showerror("Error", msg)
                        log_action('DELETE_PRODUCT', is_admin=True, admin_id=current_admin_id, target_type='product', target_id=product_id, details=f"Failed to delete product {product_name}: {msg}", status='failed') # Logging Statement

        def display_products(products):
            """Display products grouped by category in manage products view."""
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
            uncategorized_products = []
            
            for product in products:
                if product[6]:  # If product has a category_id
                    category_name = get_category_name(product[6])
                    if category_name not in categorized_products:
                        categorized_products[category_name] = []
                    categorized_products[category_name].append(product)
                else:
                    uncategorized_products.append(product)

            row_count = 0

            # First display uncategorized products under "Unlisted" section
            if uncategorized_products:
                # Create unlisted category header
                category_frame = tk.Frame(scrollable_frame, **styles['frame'])
                category_frame.pack(fill="x", pady=(20, 10))
                
                category_label = tk.Label(
                    category_frame, 
                    text="Unlisted",
                    font=("Arial", 14, "bold"),
                    bg=styles['frame']['bg'],
                    fg=styles['category_labels']['fg']
                )
                category_label.pack(side="left", padx=10)
                
                # Add separator line
                separator = ttk.Separator(category_frame, orient="horizontal")
                separator.pack(side="left", fill="x", expand=True, padx=10)

                # Display uncategorized products
                col = 0
                row_frame = None
                
                for product in uncategorized_products:
                    if col == 0:
                        row_frame = tk.Frame(scrollable_frame, **styles['frame'])
                        row_frame.pack(fill="x", pady=10, padx=20)
                        row_count += 1

                    product_frame = create_product_management_frame(
                        row_frame, 
                        product, 
                        290,
                        lambda p=product[0]: show_edit_product_screen(p),
                        lambda p=product[0]: handle_delete_product(p)
                    )

                    col += 1
                    if col >= num_columns:
                        col = 0

            # Then display categorized products
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
                
                # Add separator line
                separator = ttk.Separator(category_frame, orient="horizontal")
                separator.pack(side="left", fill="x", expand=True, padx=10)

                # Display products in this category
                col = 0
                row_frame = None
                
                for product in category_products:
                    if col == 0:
                        row_frame = tk.Frame(scrollable_frame, **styles['frame'])
                        row_frame.pack(fill="x", pady=10, padx=20)
                        row_count += 1

                    product_frame = create_product_management_frame(
                        row_frame, 
                        product, 
                        290,
                        lambda p=product[0]: show_edit_product_screen(p),
                        lambda p=product[0]: handle_delete_product(p)
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
                # Debugging:
                # print(f"Content width: {content_width}, Canvas Width: {canvas.winfo_width()}, Number of columns: {num_columns}, Product frame width: {product_frame_width}, Padding: {padding}")

        # Bind the resize event to the content_inner_frame to update the product display dynamically
        content_inner_frame.bind("<Configure>", lambda event: display_products(get_products(listed_only=False)))

        # Call display_products initially to show all products
        display_products(get_products(listed_only=False))

    # Shows the screen for the editing of individual products based on the product id so they dont have to be deleted and readded to make changes
    def show_edit_product_screen(product_id):
        """Display the edit product screen with preview layout."""
        clear_frame(content_inner_frame)
        
        window.unbind("<Configure>")
        window.unbind("<Button-1>")
        content_inner_frame.unbind("<Configure>")
        
        styles = get_style_config()['edit_product']  # Use product_page styles for consistent look

        product = get_product_by_id(product_id)
        if product:
            # Create title container frame to hold title
            title_container = tk.Frame(content_inner_frame, **styles['frame'])
            title_container.pack(fill="x", pady=(0, 8))

            name_entry = tk.Entry(title_container, **styles['entries'])
            name_entry.insert(0, product[1])
            name_entry.pack(side="left", expand=True)

            # Create outer container
            container_frame = tk.Frame(content_inner_frame, **styles['frame'])
            container_frame.pack(fill="both", expand=True)

            # Create scrollable frame setup
            wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_frame(container_frame)
            wrapper.pack(fill="both", expand=True)

            # Create main content frame
            content_frame = tk.Frame(scrollable_frame, **styles['frame'])
            content_frame.pack(fill="both", expand=True, padx=15, pady=15)

            # Details container frame
            details_frame = tk.Frame(content_frame, **styles['frame'])
            details_frame.pack(fill="both", expand=True, pady=10)

            # Left side - Product image
            left_frame = tk.Frame(details_frame, **styles['frame'])
            left_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))

            # Right side setup with fixed width and minimum height
            right_frame = tk.Frame(details_frame, width=250, **styles['frame']) #, height=340
            right_frame.pack(side="right", fill="both", padx=(10, 0))
            right_frame.pack_propagate(False)

            # Create inner frame with minimum height
            inner_right_frame = tk.Frame(right_frame, **styles['frame'])
            inner_right_frame.pack(fill="both", expand=True, padx=10, pady=5)
            #inner_right_frame.configure(height=340)

            # Price at top
            price_frame = tk.Frame(inner_right_frame, **styles['frame'])
            price_frame.pack(pady=5)
            tk.Label(price_frame, text="Price: £", **styles['price']).pack(side="left")
            price_entry = tk.Entry(price_frame, width=10, **styles['entries'])
            price_entry.insert(0, f"{product[2]:.2f}")
            price_entry.pack(side="left")

            # Description box below price
            desc_frame = tk.Frame(inner_right_frame, **styles['frame'])
            desc_frame.pack(fill="x", pady=5)
            tk.Label(desc_frame, text="Description:", **styles['labels']).pack(anchor="n")
            description_text = tk.Text(desc_frame, height=4, wrap="word", **styles['entries'])
            description_text.insert("1.0", product[5])
            description_text.pack(fill="x", pady=5)

            # Add to Cart button
            cart_button = tk.Button(inner_right_frame, text="Add to Cart", **styles['buttons'])
            cart_button.pack(pady=(10, 0))

            # Stock entry with container for centering
            stock_frame = tk.Frame(inner_right_frame, **styles['frame'])
            stock_frame.pack(fill="x", pady=(0, 5))
            stock_container = tk.Frame(stock_frame, **styles['frame'])
            stock_container.pack(expand=True)
            tk.Label(stock_container, text="Stock:", **styles['labels']).pack(side="left")
            stock_entry = tk.Entry(stock_container, width=10, **styles['entries'])
            stock_entry.insert(0, product[8])
            stock_entry.pack(side="left", padx=5)

            # Bottom frame spanning full width (moved to after QR code)
            bottom_frame = tk.Frame(content_frame, **styles['frame'])
            bottom_frame.pack(fill="x", expand=True)

            # Category and Listed status (side by side)
            settings_frame = tk.Frame(bottom_frame, **styles['frame'])
            settings_frame.pack(expand=True, pady=(2, 2))

            # Container for horizontal layout
            controls_container = tk.Frame(settings_frame, **styles['frame'])
            controls_container.pack(expand=True)

            # Category on the left
            category_container = tk.Frame(controls_container, **styles['frame'])
            category_container.pack(side="left", padx=10)
            tk.Label(category_container, text="Category:", **styles['labels']).pack()
            category_combobox = ttk.Combobox(category_container, values=get_categories(), style='Edit.TCombobox', width=20)
            if get_category_name(product[6]):
                category_combobox.set(get_category_name(product[6]))
            category_combobox.pack(pady=2)

            # Listed status on the right
            listed_container = tk.Frame(controls_container, **styles['frame'])
            listed_container.pack(side="left", padx=10)
            tk.Label(listed_container, text="Listed:", **styles['labels']).pack()
            listed_var = tk.StringVar(value="Yes" if product[4] else "No")
            listed_combobox = ttk.Combobox(listed_container, textvariable=listed_var, values=["Yes", "No"], style='Edit.TCombobox', width=20)
            listed_combobox.pack(pady=2)

            # Message label
            message_label = tk.Label(bottom_frame, text="", **styles['message'])
            message_label.pack(pady=5)

            # Action buttons
            button_frame = tk.Frame(bottom_frame, **styles['frame'])
            button_frame.pack(pady=(2, 0))
            tk.Button(button_frame, text="Save", command=lambda: save_edit_product(), **styles['buttons']).pack(side="left", padx=5)
            tk.Button(button_frame, text="Cancel", command=lambda: show_manage_products_screen(), **styles['buttons']).pack(side="left", padx=5)

            def select_image():
                """Handle image selection"""
                file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
                if file_path:
                    image_path.set(file_path)
                    # Force immediate resize
                    resize_content()

            # Modify existing image handling:
            image_path = tk.StringVar(value=product[7])
            image_frame = tk.Frame(left_frame, **styles['frame'])
            image_frame.pack(pady=(0, 5))

            # Add select image button
            select_image_button = tk.Button(left_frame, text="Change Image", command=select_image, **styles['buttons'])
            select_image_button.pack(pady=5)

            resize_timer = None

            def debounced_resize(event=None):
                """Debounced version of resize_content"""
                nonlocal resize_timer
                if resize_timer is not None:
                    window.after_cancel(resize_timer)
                resize_timer = window.after(150, lambda: resize_content(event))

            def resize_content(event=None):
                """Handle responsive resizing of images"""
                image_to_resize = image_path.get() or product[7]
                
                # Use placeholder if no image exists
                if not image_to_resize:
                    image_to_resize = os.path.join(get_paths()['icons_dir'], 'placeholder.png')
                
                 # Get window dimensions first
                window_width = window.winfo_width()
                window_height = window.winfo_height()
                    
                # Force geometry updates
                window.update_idletasks()
                
                # Set minimum heights and get current heights
                MIN_RIGHT_HEIGHT = 330  # Increased from 340 to ensure QR visibility
                MIN_QR_PADDING = 5    # Minimum padding around QR code
                
                left_height = left_frame.winfo_reqheight()
                right_height = right_frame.winfo_reqheight()
                
                # Enforce minimum right frame height
                final_right_height = max(MIN_RIGHT_HEIGHT, right_height)
                right_frame.configure(height=final_right_height)
                inner_right_frame.configure(height=final_right_height)
                
                # Calculate QR padding based on available space
                if left_height > right_height:
                    # If left side is taller, distribute extra space
                    extra_space = left_height - right_height
                    qr_top_padding = max(MIN_QR_PADDING, extra_space // 3)
                    bottom_padding = max(MIN_QR_PADDING, extra_space // 4)
                else:
                    # Use minimum padding if heights are similar
                    qr_top_padding = MIN_QR_PADDING
                    bottom_padding = MIN_QR_PADDING
                
                # Update QR code padding
                if hasattr(inner_right_frame, 'qr_label'):
                    inner_right_frame.qr_label.pack_configure(pady=(qr_top_padding, MIN_QR_PADDING))
                
                # Update bottom frame padding
                bottom_frame.pack_configure(pady=(bottom_padding, 0))

                # Calculate responsive dimensions based on window size
                # Cant go below the minimum width and height since thats set at the start
                if window_width <= 1280:  # Small screens (1280x720)
                    width_factor = 0.25
                    height_factor = 0.3
                    min_width_factor = 0.02
                    min_height_factor = 0.02
                    qr_factor = 0.12
                    qr_min_size = 90
                    qr_max_size = 90
                elif window_width <= 1366:  # Keep existing factors for larger screens
                    width_factor = 0.35
                    height_factor = 0.45
                    min_width_factor = 0.1
                    min_height_factor = 0.1
                    qr_factor = 0.12
                    qr_min_size = 100
                    qr_max_size = 100
                elif window_width <= 1600:  # Medium screens
                    width_factor = 0.38
                    height_factor = 0.48
                    min_width_factor = 0.15
                    min_height_factor = 0.15
                    qr_factor = 0.1
                    qr_min_size = 140
                    qr_max_size = 140
                elif window_width <= 1920:  # Full HD
                    width_factor = 0.4
                    height_factor = 0.5
                    min_width_factor = 0.2
                    min_height_factor = 0.2
                    qr_factor = 0.1
                    qr_min_size = 160
                    qr_max_size = 160
                elif window_width <= 2560:  # 2K/QHD
                    width_factor = 0.45
                    height_factor = 0.55
                    min_width_factor = 0.25
                    min_height_factor = 0.25
                    qr_factor = 0.08
                    qr_min_size = 180
                    qr_max_size = 180
                else:  # 4K and larger
                    width_factor = 0.5
                    height_factor = 0.6
                    min_width_factor = 0.3
                    min_height_factor = 0.3
                    qr_factor = 0.06
                    qr_min_size = 200
                    qr_max_size = 200

                # Calculate image dimensions
                max_img_width = min(int(window_width * width_factor), 1800)
                max_img_height = min(int(window_height * height_factor), 1600)
                min_img_width = max(int(window_width * min_width_factor), 100)
                min_img_height = max(int(window_height * min_height_factor), 75)
                
                # Simplified QR sizing with fixed min/max per resolution
                qr_base_size = min(int(window_width * qr_factor), qr_max_size)
                qr_size = max(qr_min_size, min(qr_base_size, qr_max_size))

                # Resize product image
                resized_image = resize_product_image(
                    image_to_resize,
                    max_width=max_img_width,
                    max_height=max_img_height,
                    min_width=min_img_width,
                    min_height=min_img_height
                )

                # Update product image
                if resized_image:
                    if hasattr(left_frame, 'image_label'):
                        left_frame.image_label.configure(image=resized_image)
                        left_frame.image_label.image = resized_image
                    else:
                        left_frame.image_label = tk.Label(left_frame, image=resized_image, **styles['image_frame'])
                        left_frame.image_label.image = resized_image
                        left_frame.image_label.pack(pady=(0, 5))

                # Update QR code with dynamic padding based on window size
                if product[3]:
                    resized_qr = resize_qr_code(product[3], size=(qr_size, qr_size))
                    if resized_qr:
                        if hasattr(inner_right_frame, 'qr_label'):
                            inner_right_frame.qr_label.configure(image=resized_qr)
                            inner_right_frame.qr_label.image = resized_qr
                        else:
                            # Create QR container frame with minimal spacing
                            qr_container = tk.Frame(inner_right_frame, **styles['frame'])
                            qr_container.pack(fill="x", expand=False, pady=(5, 5))  # Reduced vertical padding
                            
                            inner_right_frame.qr_label = tk.Label(qr_container, image=resized_qr, **styles['image_frame'])
                            inner_right_frame.qr_label.image = resized_qr
                            inner_right_frame.qr_label.pack(pady=2)  # Minimal padding around QR code

            def save_edit_product():
                """Handle product updates with validation"""
                # Collect form values
                new_values = {
                    'name': name_entry.get().strip(),
                    'price': float(price_entry.get()),
                    'description': description_text.get("1.0", "end-1c").strip(),
                    'category': category_combobox.get(),
                    'image': image_path.get(),
                    'stock': int(stock_entry.get() or 0),
                    'listed': 1 if listed_var.get() == "Yes" else 0
                }

                # Validate inputs
                is_valid, message = validate_product_fields(
                    new_values['name'], 
                    new_values['price'],
                    new_values['stock'], 
                    new_values['listed'],
                    new_values['category'],
                    new_values['image'],
                    new_values['description']
                )
                
                if not is_valid:
                    display_error(message_label, message)
                    log_action('UPDATE_PRODUCT', is_admin=True, admin_id=current_admin_id, target_type='product', target_id=product_id, details=f"Failed to update product: {message}", status='failed') # Logging Statement
                    
                    return

                category_id = get_category_id(new_values['category']) if new_values['category'] else None
                
                # Get current product state to check what's changing
                current_product = get_product_by_id(product_id)
                
                # Only perform file operations if name, price, or image changes
                needs_name_price_update = (
                    new_values['name'] != current_product[1] or 
                    abs(float(new_values['price']) - float(current_product[2])) > 0.001
                )
                needs_image_update = (new_values['image'] and new_values['image'] != current_product[7])

                # Update product with appropriate file handling
                update_product(
                    product_id=product_id,
                    name=new_values['name'],
                    price=new_values['price'],
                    qr_code=True,  # Let database.py determine if new QR needed
                    description=new_values['description'],
                    category_id=category_id,
                    image=new_values['image'],
                    stock=new_values['stock'],
                    keep_qr=not needs_name_price_update,
                    keep_image=not needs_image_update
                )

                # Only handle listing status separately
                list_product(product_id, new_values['listed'])

                display_success(message_label, "Product updated successfully!")
                log_action('UPDATE_PRODUCT', is_admin=True, admin_id=current_admin_id, target_type='product', target_id=product_id, details=f"Updated product: {new_values['name']} (Price: £{new_values['price']}, Stock: {new_values['stock']}, Listed: {new_values['listed']})") # Logging Statement
                show_manage_products_screen()

            # Bind resize event
            window.bind("<Configure>", debounced_resize)
            window.update_idletasks()
            window.after(100, resize_content)

            # Enable mouse wheel scrolling
            bind_wheel()

        else:
            message_label = tk.Label(content_inner_frame, text="", **styles['message'])
            message_label.pack()
            display_error(message_label, "Product not found!")

    def show_manage_categories_screen():
        """Display the manage categories screen."""
        clear_frame(content_inner_frame)

        styles = get_style_config()['manage_categories']

        window.unbind("<Configure>")
        window.unbind("<Button-1>")

        tk.Label(content_inner_frame, text="Manage Categories", **styles['title']).pack(pady=10)

        tk.Label(content_inner_frame, text="Category Name", **styles['labels']).pack(pady=5)
        category_entry = tk.Entry(content_inner_frame, **styles['entries'])
        category_entry.pack(pady=5)

        message_label = tk.Label(content_inner_frame, text="", **styles['message'])
        message_label.pack(pady=10)

        def display_categories():
            clear_frame(category_list_frame)

            categories = get_categories()
            for category in categories:
                category_frame = tk.Frame(category_list_frame, **styles['category_frame'])
                category_frame.pack(fill="x", pady=5)

                tk.Label(category_frame, text=category, **styles['labels']).pack(side="left", padx=10)

                edit_button = tk.Button(category_frame, text="Edit", command=lambda c=category: handle_edit_category(get_category_id(c), c), **styles['buttons'])
                edit_button.pack(side="right", padx=5)

                delete_button = tk.Button(category_frame, text="Delete", command=lambda c=category: handle_delete_category(get_category_id(c)), **styles['buttons'])
                delete_button.pack(side="right", padx=5)

        def handle_add_category():
            name = category_entry.get()
            if not name:
                display_error(message_label, "Category name is required.")
                log_action('CREATE_CATEGORY', is_admin=True, admin_id=current_admin_id, target_type='category', target_id=None, details=f"Failed to create category: Name required", status='failed') # Logging Statement
                return

            is_valid, message = validate_category_name(name)
            if not is_valid:
                display_error(message_label, message)
                log_action('CREATE_CATEGORY', is_admin=True, admin_id=current_admin_id, target_type='category', target_id=None, details=f"Failed to create category: {message}", status='failed') # Logging Statement
                return

            success, message = add_category(name)
            if success:
                category_id = get_category_id(name)  # Get the new category's ID
                display_success(message_label, message)
                log_action('CREATE_CATEGORY', is_admin=True, admin_id=current_admin_id, target_type='category', target_id=category_id, details=f"Created category: {name}") # Logging Statement
                category_entry.delete(0, tk.END)
                display_categories()
            else:
                display_error(message_label, message)
                log_action('CREATE_CATEGORY', is_admin=True, admin_id=current_admin_id, target_type='category', target_id=None, details=f"Failed to create category {name}: {message}", status='failed') # Logging Statement

        add_button = tk.Button(content_inner_frame, text="Add Category", command=handle_add_category, **styles['buttons'])
        add_button.pack(pady=5)

        category_list_frame = tk.Frame(content_inner_frame, **styles['frame'])
        category_list_frame.pack(fill="both", expand=True,)

        def handle_edit_category(category_id, old_name):
            new_name = category_entry.get()
            if not new_name:
                display_error(message_label, "Category name is required.")
                return

            if new_name == old_name:
                display_error(message_label, "No changes made.")
                return

            success, message = update_category(category_id, new_name)
            if success:
                display_success(message_label, message)
                log_action('UPDATE_CATEGORY', is_admin=True, admin_id=current_admin_id, target_type='category', target_id=category_id, details=f"Updated category name from {old_name} to {new_name}") # Logging Statement
                category_entry.delete(0, tk.END)
                display_categories()
            else:
                display_error(message_label, message)
                log_action('UPDATE_CATEGORY', is_admin=True, admin_id=current_admin_id, target_type='category', target_id=category_id, details=f"Failed to update category {old_name}: {message}", status='failed') # Logging Statement

        def handle_delete_category(category_id):
            category_name = get_category_name(category_id)  # Get name before deletion
            success, message = delete_category(category_id)
            if success:
                display_success(message_label, message)
                log_action('DELETE_CATEGORY', is_admin=True, admin_id=current_admin_id, target_type='category', target_id=category_id, details=f"Deleted category: {category_name}") # Logging Statement
                display_categories()
            else:
                display_error(message_label, message)
                log_action('DELETE_CATEGORY', is_admin=True, admin_id=current_admin_id, target_type='category', target_id=category_id, details=f"Failed to delete category {category_name}: {message}", status='failed') # Logging Statement

        # Call display_categories to show the categories initially
        display_categories()
    
    # User Management Admin Dashboard Screen
    def show_manage_users_screen():
        """Switch to user management screen"""
        if not get_current_user_admin_status(current_username):
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
        
        # Create container frame using grid
        user_list_frame = tk.Frame(content_inner_frame, **styles['frame'])
        user_list_frame.grid(row=0, column=0, sticky="nsew", padx=10)
        content_inner_frame.grid_columnconfigure(0, weight=1)
        content_inner_frame.grid_rowconfigure(0, weight=1)

        # Header section using grid
        title_label = tk.Label(user_list_frame, text="User Management", **styles['title'])
        title_label.grid(row=0, column=0, pady=10)

        # Message label 
        message_label = tk.Label(user_list_frame, text="", **styles['message'])
        message_label.grid(row=1, column=0, pady=5)

        # Store resize timer as an attribute of the content_inner_frame
        content_inner_frame.resize_timer = None

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
        user_list_frame.grid_columnconfigure(0, weight=1)
        user_list_frame.grid_rowconfigure(3, weight=1)

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
                
                # Add data cells with debug colors
                for col, value in enumerate(display_values):
                    cell_frame = tk.Frame(
                        scrollable_frame,
                        **styles['frame'],
                        height=30
                    )
                    cell_frame.grid(row=row, column=col, padx=5, pady=2, sticky="nsew")
                    cell_frame.grid_propagate(False)
                    cell_frame.grid_columnconfigure(0, weight=1)
                    
                    # Create a copy of the style dict and remove bg if it exists
                    label_style = styles['text'].copy()
                    if 'bg' in label_style:
                        del label_style['bg']
                    
                    label = tk.Label(
                        cell_frame,
                        text=value,
                        **styles['text']
                    )
                    label.grid(row=0, column=0, sticky="nsew")
                    label.configure(anchor="center")
                    
                    # Print cell width after update
                    cell_frame.update_idletasks()
                
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
                    command=lambda u=user: open_edit_dialog(u[0], u[1], u[2], u[3], u[4], u[5]),  # Unpack user tuple
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
                
                # Print actions column width
                actions_frame.update_idletasks()
            
            # Print total frame width
            scrollable_frame.update_idletasks()
            
            # Update scroll region
            canvas.configure(scrollregion=canvas.bbox("all"))

        def open_edit_dialog(user_id, username, first_name, last_name, age, is_admin):
            """Open dialog to edit user details."""
            global window

            # Check if dialog already exists for this user
            for child_window in window.winfo_children():  # Changed from 'window' to 'child_window'
                if isinstance(child_window, tk.Toplevel) and hasattr(child_window, 'editing_user_id'):
                    if child_window.editing_user_id == user_id:
                        child_window.lift()
                        return

            styles = get_style_config()['edit_user_dialog']

            # Setup combobox style
            combo_style = ttk.Style()
            combo_style.configure('Edit.TCombobox',
                background=styles['combobox']['bg'],
                fieldbackground=styles['combobox']['fieldbackground'],
                foreground=styles['combobox']['fg'],
                selectbackground=styles['combobox']['selectbackground'],
                selectforeground=styles['combobox']['selectforeground']
            )

            dialog = tk.Toplevel(window)
            dialog.editing_user_id = user_id  # Tag dialog with user ID
            dialog.title("Edit User")
            dialog.configure(**styles['dialog'])
            
            # Center dialog
            dialog_width, dialog_height = 400, 500
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

            frame = tk.Frame(dialog, **styles['frame'])
            frame.pack(fill='both', expand=True, padx=20, pady=20)

            # Title
            tk.Label(frame, text="Edit User",**styles['title']).pack(pady=(0, 20))

            message_label = tk.Label(frame, text="", **styles['message'])
            message_label.pack(pady=(0, 10))

            is_current_user = (username == current_username)

            # Username
            tk.Label(frame, text="Username:", **styles['labels']).pack(anchor='w', padx=5)
            username_entry = tk.Entry(frame, width=25, **styles['entries'])
            username_entry.insert(0, username)
            username_entry.pack(pady=(0, 10), padx=5)

            # First name
            tk.Label(frame, text="First Name:", **styles['labels']).pack(anchor='w', padx=5)
            first_name_entry = tk.Entry(frame, width=25, **styles['entries'])
            first_name_entry.insert(0, first_name)
            first_name_entry.pack(pady=(0, 10), padx=5)

            # Last name
            tk.Label(frame, text="Last Name:", **styles['labels']).pack(anchor='w', padx=5)
            last_name_entry = tk.Entry(frame, width=25, **styles['entries'])
            last_name_entry.insert(0, last_name)
            last_name_entry.pack(pady=(0, 10), padx=5)

            # Age
            tk.Label(frame, text="Age:", **styles['labels']).pack(anchor='w', padx=5)
            age_entry = tk.Entry(frame, width=25, **styles['entries'])
            age_entry.insert(0, str(age))
            age_entry.pack(pady=(0, 10), padx=5)

            # Admin status combobox
            tk.Label(frame, text="Admin Status:", **styles['labels']).pack(anchor='w', padx=5)
            admin_var = tk.StringVar(value="Yes" if is_admin else "No")
            admin_combobox = ttk.Combobox(
                frame,
                textvariable=admin_var,
                values=["Yes", "No"],
                width=22,
                state='readonly' if username != current_username else 'disabled',
                style='Edit.TCombobox'
            )
            admin_combobox.pack(pady=(0, 10), padx=5)

            def save_changes():
                new_first_name = first_name_entry.get()
                new_last_name = last_name_entry.get()
                new_age = age_entry.get()
                new_is_admin = admin_var.get() == "Yes"  # Convert Yes/No to boolean

                # Use existing validation from validation.py
                is_valid, validation_message = validate_user_fields(username, first_name, last_name, "", "", age, check_type="edit")

                if not is_valid:
                    display_error(message_label, validation_message)
                    log_action('MANAGE_USER', is_admin=True, admin_id=current_admin_id, target_type='user', target_id=user_id, details=f"Failed to update user {username}: {validation_message}", status='failed') # Logging Statement
                    return

                # Check admin status change
                if new_is_admin != is_admin:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM Users WHERE is_admin = 1")
                    admin_count = cursor.fetchone()[0]
                    conn.close()
                    
                    if admin_count <= 1 and not new_is_admin:
                        display_error(message_label, "Cannot remove last admin user")
                        log_action('MANAGE_USER', is_admin=True, admin_id=current_admin_id, target_type='user', target_id=user_id, details=f"Failed to update user {username}: Cannot remove last admin", status='failed') # Logging Statement
                        return

                success, message = update_user_details(
                    user_id,
                    new_first_name,
                    new_last_name,
                    int(new_age),
                    new_is_admin
                )

                if success:
                    display_success(message_label, "User updated successfully")
                    log_action('MANAGE_USER', is_admin=True, admin_id=current_admin_id, target_type='user', target_id=user_id, details=f"Updated user {username}: Name={new_first_name} {new_last_name}, Age={new_age}, Admin={new_is_admin}") # Logging Statement
                    dialog.after(1000, lambda: [dialog.destroy(), show_manage_users_screen()])
                else:
                    display_error(message_label, message)
                    log_action('MANAGE_USER', is_admin=True, admin_id=current_admin_id, target_type='user', target_id=user_id, details=f"Failed to update user {username}: {message}", status='failed') # Logging Statement

            button_frame = tk.Frame(frame, **styles['frame'])
            button_frame.pack(pady=(10, 0))

            tk.Button(
                button_frame,
                text="Save",
                command=save_changes,
                width=10,
                **styles['buttons']
            ).pack(side='left', padx=5)

            # Add Change Password button
            change_pwd_btn = tk.Button(
                button_frame,
                text="Change Password",
                command=lambda: switch_to_change_password(username, from_source="admin", parent_dialog=dialog),
                **styles['buttons']
            )
            change_pwd_btn.pack(side='left', padx=5)

            tk.Button(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                width=10,
                **styles['buttons']
            ).pack(side='left', padx=5)

            dialog.transient(window)
            dialog.grab_set()

            def on_dialog_close():
                """Handle dialog closure"""
                dialog.grab_release()
                dialog.destroy()

            dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
            dialog.wait_window()

        def handle_delete_user(user_id):
            """Handle user deletion"""
            if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
                return
                
            success, message = delete_user(user_id)
            username = get_username_by_id(user_id)
            if success:
                display_success(message_label, message)
                log_action('MANAGE_USER', is_admin=True, admin_id=current_admin_id, target_type='user', target_id=user_id, details=f"Deleted user: {username}") # Logging Statement
                display_users()
            else:
                display_error(message_label, message)
                log_action('MANAGE_USER', is_admin=True, admin_id=current_admin_id, target_type='user', target_id=user_id, details=f"Failed to delete user {username}: {message}", status='failed') # Logging Statement

        # Initial display
        display_users()

    def show_manage_discounts_screen():
        """Display the discounts management screen"""
        if not get_current_user_admin_status(current_username):
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
        
        # Create container frame using grid
        user_list_frame = tk.Frame(content_inner_frame, **styles['frame'])
        user_list_frame.grid(row=0, column=0, sticky="nsew", padx=10)
        content_inner_frame.grid_columnconfigure(0, weight=1)
        content_inner_frame.grid_rowconfigure(0, weight=1)

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
            """Handle adding new discount"""
            name = name_entry.get().strip()
            percentage = percentage_entry.get().strip()

            if not name or not percentage:
                display_error(message_label, "Please fill in all fields")
                log_action('CREATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=None, details="Failed to create discount: Empty fields", status='failed') # Logging Statement
                return

            try:
                percentage = int(percentage)
                if not 0 < percentage <= 100:
                    raise ValueError
            except ValueError:
                display_error(message_label, "Percentage must be between 1-100")
                log_action('CREATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=None, details=f"Failed to create discount: Invalid percentage format", status='failed') # Logging Statement
                return

            success, new_id, msg = add_discount(name, percentage)
            if success:
                # Clear entries
                name_entry.delete(0, tk.END)
                percentage_entry.delete(0, tk.END)
                display_success(message_label, msg)
                log_action('CREATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=new_id, details=f"Created discount: {name} ({percentage}%)") # Logging Statement
                display_discounts()
            else:
                display_error(message_label, msg)
                log_action('CREATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=None, details=f"Failed to create discount: {msg}", status='failed') # Logging Statement

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
            """Handle window resize events with debouncing"""
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
        user_list_frame.grid_columnconfigure(0, weight=1)
        user_list_frame.grid_rowconfigure(3, weight=1)

        def display_discounts():
            """Display users in a scrollable grid layout."""
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
                    str(uses if uses is not None else "0"),  # Display uses, not qr_code_path
                    "Yes" if active else "No"
                ]
                
                # Add data cells
                for col, value in enumerate(display_values):
                    cell_frame = tk.Frame(
                        scrollable_frame,
                        **styles['frame'],
                        height=30
                    )
                    cell_frame.grid(row=row, column=col, padx=5, pady=2, sticky="nsew")
                    cell_frame.grid_propagate(False)
                    cell_frame.grid_columnconfigure(0, weight=1)
                    
                    # Create a copy of the style dict and remove bg if it exists
                    label_style = styles['text'].copy()
                    if 'bg' in label_style:
                        del label_style['bg']
                    
                    label = tk.Label(
                        cell_frame,
                        text=value,
                        **styles['text']
                    )
                    label.grid(row=0, column=0, sticky="nsew")
                    label.configure(anchor="center")
                    
                    cell_frame.update_idletasks()
                
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

                # Print actions column width
                actions_frame.update_idletasks()
            
            # Print total frame width
            scrollable_frame.update_idletasks()
            
            # Update scroll region
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            def handle_edit_discount(discount):
                """Handle editing of a discount"""
                global window

                # Create dialog window
                dialog = tk.Toplevel(window)
                dialog.title("Edit Discount")
                
                # Configure dialog style
                dialog.configure(**styles['frame'])
                
                # Set dialog size
                dialog_width = 400
                dialog_height = 350
                dialog.minsize(dialog_width, dialog_height)
                
                # Center dialog
                x = (dialog.winfo_screenwidth() - dialog_width) // 2
                y = (dialog.winfo_screenheight() - dialog_height) // 2
                dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

                # Make dialog modal
                dialog.transient(window)
                dialog.grab_set()
                dialog.focus_set()
                dialog.lift()
                dialog.attributes('-topmost', True)

                # Create form frame
                form_frame = tk.Frame(dialog, **styles['frame'])
                form_frame.pack(fill='both', expand=True, padx=20, pady=20)

                # Title
                tk.Label(form_frame, text="Edit Discount", **styles['title']).pack(pady=(0, 20))

                # Message label for feedback
                message_label = tk.Label(form_frame, text="", **styles['message'])
                message_label.pack(pady=(0, 10))

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
                    """Save changes to discount"""
                    name = entries['name'].get().strip()
                    percentage = entries['percentage'].get().strip()

                    if not name or not percentage:
                        display_error(message_label, "Please fill in all fields")
                        log_action('UPDATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=discount[0], details=f"Failed to update discount: Empty fields", status='failed') # Logging Statement
                        return

                    try:
                        percentage = int(percentage)
                        if not 0 < percentage <= 100:
                            raise ValueError
                    except ValueError:
                        display_error(message_label, "Percentage must be between 1-100")
                        log_action('UPDATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=discount[0], details=f"Failed to update discount: Invalid percentage value", status='failed') # Logging Statement
                        return

                    success, msg = update_discount(discount[0], name, percentage)
                    if success:
                        display_success(message_label, "Discount updated successfully")
                        log_action('UPDATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=discount[0], details=f"Updated discount {name} ({percentage}%)") # Logging Statement
                        dialog.after(1500, dialog.destroy)  # Close dialog after success
                        display_discounts()
                    else:
                        display_error(message_label, msg)
                        log_action('UPDATE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=discount[0], details=f"Failed to update discount: {msg}", status='failed') # Logging Statement

                # Button frame
                button_frame = tk.Frame(form_frame, **styles['frame'])
                button_frame.pack(pady=20)

                # Save button
                tk.Button(
                    button_frame,
                    text="Save Changes",
                    command=save_changes,
                    **styles['buttons']
                ).pack(side='left', padx=5)

                # Close button  
                tk.Button(
                    button_frame,
                    text="Close",
                    command=dialog.destroy,
                    **styles['buttons']
                ).pack(side='left', padx=5)

            def handle_toggle_discount(discount):
                """Handle toggling discount active status"""
                success, msg = toggle_discount_status(discount[0])  # discount[0] is id
                if success:
                    display_discounts()
                    display_success(message_label, msg)
                    log_action('TOGGLE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=discount[0], details=f"Toggled discount status: {discount[1]}") # Logging Statement
                else:
                    display_error(message_label, msg)
                    log_action('TOGGLE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=discount[0], details=f"Failed to toggle discount status: {msg}", status='failed') # Logging Statement

            def handle_delete_discount(discount):
                """Handle deletion of a discount"""
                # Extract the discount ID from the tuple
                discount_id = discount[0]  # The ID is the first element in the tuple
                discount_name = discount[1]  # The name is the second element

                # Call delete_discount with just the ID
                success, msg = delete_discount(discount_id)
                
                if success:
                    display_discounts()  # Refresh the display
                    log_action('DELETE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=discount_id, details=f"Deleted discount: {discount_name}") # Logging Statement
                else:
                    # Show error message if deletion failed
                    messagebox.showerror("Error", msg)
                    log_action('DELETE_DISCOUNT', is_admin=True, admin_id=current_admin_id, target_type='discount', target_id=discount_id, details=f"Failed to delete discount {discount_name}: {msg}", status='failed') # Logging Statement

        # Initial display
        display_discounts()

    def show_logging_screen():
        """Display the logging management screen"""
        global content_inner_frame, user_log_text, admin_log_text
        
        if not get_current_user_admin_status(current_username):
            switch_to_store_listing(is_admin=False)
            return

        clear_frame(content_inner_frame)
        styles = get_style_config()['logging']

        window.unbind("<Configure>")
        window.unbind("<Button-1>")
        
        # Create title
        tk.Label(content_inner_frame, text="System Logs", **styles['title']).pack(pady=10)

        # Create container frame for log controls
        controls_frame = tk.Frame(content_inner_frame, **styles['frame'])
        controls_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Create filters frame
        filters_frame = tk.Frame(controls_frame, **styles['frame'])
        filters_frame.pack(side="left", fill="x", expand=True)

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
                    log_action('TOGGLE_USER_LOGGING', is_admin=True, admin_id=current_admin_id, target_type='setting', target_id=None, details="Enabled user action logging") # Logging Statement
                else:
                    log_action('TOGGLE_USER_LOGGING', is_admin=True, admin_id=current_admin_id, target_type='setting', target_id=None, details="Disabled user action logging") # Logging Statement
            else:
                log_action('TOGGLE_USER_LOGGING', is_admin=True, admin_id=current_admin_id, target_type='setting', target_id=None, details=f"Failed to toggle user logging", status='failed') # Logging Statement

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
        # Auto refresh the logs after a change has been made to the type of logs being viewed.
        log_type_combo.bind('<<ComboboxSelected>>', lambda e: refresh_logs())

        # Create main log display frame
        log_frame = tk.Frame(content_inner_frame, **styles['frame'])
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create text widget for log display
        log_text = tk.Text(log_frame, wrap="word", **styles['text'])
        log_text.pack(side="left", fill="both", expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=log_text.yview)
        scrollbar.pack(side="right", fill="y")
        log_text.configure(yscrollcommand=scrollbar.set)

        # Make text widget read-only
        log_text.configure(state="disabled")

        # Create message label for feedback
        message_label = tk.Label(content_inner_frame, text="", **styles['message'])
        message_label.pack(pady=10)

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

        # Add refresh button
        tk.Button(controls_frame, text="Refresh Logs", 
                command=refresh_logs,
                **styles['buttons']).pack(side="right", padx=5)
        
        # Initial load
        refresh_logs()
    


    def switch_to_change_password(username, from_source="login", parent_dialog=None):
        """
        Show password change screen based on context.
        
        Args:
            username: Username of account to change password
            from_source: Source of change request ('login', 'self', 'admin')
        """
        if from_source == "login":
            # Use existing login change password screen behavior
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
            pass
        else:
            # Create dialog window for self/admin password changes
            styles = get_style_config()['manage_user']
            dialog = tk.Toplevel(window)
            dialog.title("Change Password")
            dialog.configure(**styles['frame'])
            
            if parent_dialog:
                # Make this dialog modal relative to parent
                dialog.transient(parent_dialog)
                parent_dialog.attributes('-disabled', True)
            else:
                dialog.transient(window)
                
            dialog.grab_set()
            dialog.focus_set()

            # Center dialog
            dialog_width = 400
            dialog_height = 350 if from_source == "self" else 300
            dialog.minsize(dialog_width, dialog_height)
            x = (dialog.winfo_screenwidth() - dialog_width) // 2
            y = (dialog.winfo_screenheight() - dialog_height) // 2
            dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
            
            # Make dialog modal
            dialog.transient(window)
            dialog.grab_set()
            dialog.focus_set()
            dialog.attributes('-topmost', True)

            def on_close():
                if parent_dialog:
                    parent_dialog.attributes('-disabled', False)
                    parent_dialog.focus_set()
                dialog.destroy()

            # Create form
            form_frame = tk.Frame(dialog, **styles['frame'])
            form_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            tk.Label(form_frame, text="Change Password", **styles['title']).pack(pady=(0, 20))
            
            message_label = tk.Label(form_frame, text="", **styles['message'])
            message_label.pack(pady=(0, 10))

            # Add current password field for self-change only
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

            def change_password():
                new_password = new_password_entry.get()
                confirm_password = confirm_password_entry.get()
                current_password = current_password_entry.get() if from_source == "self" else None

                # Validate based on source
                if from_source == "self":
                    # Verify current password first
                    success, *_ = authenticate_user(username, current_password)
                    if not success:
                        display_error(message_label, "Current password is incorrect")
                        return

                # Use validate_user_fields for password validation
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
                        log_action('FIRST_LOGIN_PASSWORD', is_admin=True, admin_id=current_admin_id, target_type='user', target_id=current_user_id, details=f"Changed initial admin password") # Logging Statement
                    elif from_source == "admin":
                        log_action('MANAGE_USER', is_admin=True, admin_id=current_admin_id, target_type='user', target_id=get_user_id_by_username(username), details=f"Admin changed password for user: {username}") # Logging Statement
                    else:  # self change
                        log_action('PASSWORD_CHANGE', user_id=current_user_id, details="Password changed successfully") # Logging Statement
                        
                    if from_source == "login":
                        dialog.after(1500, lambda: switch_to_admin_panel())
                    else:
                        dialog.after(1500, on_close)
                else:
                    display_error(message_label, message)
                    if from_source == "login":
                        log_action('FIRST_LOGIN_PASSWORD', is_admin=True, admin_id=current_admin_id, target_type='user', target_id=current_user_id, details=f"Failed to change initial admin password: {message}", status='failed') # Logging Statement
                    elif from_source == "admin":
                        log_action('MANAGE_USER', is_admin=True, admin_id=current_admin_id, target_type='user', target_id=get_user_id_by_username(username), details=f"Failed to change password for user {username}: {message}", status='failed') # Logging Statement
                    else:  # self change
                        log_action('PASSWORD_CHANGE', user_id=current_user_id, details="Failed to change password", status='failed') # Logging Statement
                
            dialog.protocol("WM_DELETE_WINDOW", on_close)

        # Add buttons
        button_frame = tk.Frame(form_frame if from_source != "login" else main_frame, **styles['frame'])
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

        # Bind enter key
        if from_source == "login":
            main_frame.bind('<Return>', lambda event: change_password())
            change_button.bind('<Return>', lambda event: change_password())

    # Should switch to using logout function instead of just transitioning to showing the login screen even though the login process refreshes these variables.
    def logout():
        """Handle logout."""
        global current_username, current_first_name, current_last_name, current_admin_id, current_user_id
        log_action('LOGOUT', user_id=current_user_id, details=f"User {current_username} logged out") # Logging Statement before the variables are reset hopefully.
        current_user_id = None
        current_username = None
        current_first_name = None
        current_last_name = None
        current_admin_id = None
        show_login_screen()

    window.mainloop() # Actually starts the application and allows the user to interact with the GUI

if __name__ == "__main__":
    start_app()