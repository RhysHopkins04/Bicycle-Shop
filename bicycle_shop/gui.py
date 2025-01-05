import tkinter as tk
from tkinter import ttk, filedialog as filedialog, PhotoImage
import os

# Functions from other locations in the program: auth, database, qr_code_util
from auth import (register_user, authenticate_user, update_user_password, promote_user_to_admin, 
                  demote_user_from_admin
                  )
from database import (create_tables, initialize_admin, get_products, get_product_by_id, get_connection, 
                      list_product, add_product, update_product, delete_product as db_delete_product, 
                      add_category, get_categories, get_category_id, get_category_name, delete_category, 
                      update_category, add_to_cart, get_cart_items, update_cart_quantity,
                      get_current_user_admin_status
                      )
from validation import (validate_password, validate_empty_fields, validate_password_match, validate_age, 
                        validate_registration_fields, validate_username_uniqueness, validate_product_fields, 
                        validate_category_name
                        )
from utils import (display_error, display_success, clear_frame, show_dropdown, hide_dropdown, hide_dropdown_on_click, 
                   create_nav_buttons, create_user_info_display, setup_search_widget, create_scrollable_frame, 
                   create_password_field, setup_product_grid, create_product_listing_frame, create_product_management_frame, 
                   get_style_config, center_window, create_fullscreen_handler, resize_product_image, resize_qr_code

                   )
from file_manager import (get_application_settings, get_icon_paths, get_paths)

# Start GUI Function to be called in the main.py file post further checks for the tables and admin user.
def start_app():
    """Start the Tkinter GUI application.""" #Docstring's which i will use to help with future code documentation along with the comments.

    # Get configuration settings
    app_settings = get_application_settings()
    icon_paths = get_icon_paths()

    # Global Variables other than the main_frame 
    global main_frame, logout_button, window, current_username, current_first_name, current_last_name, current_admin_id, current_user_id, disable_search, enable_search
    logout_button = None
    current_admin_id = None
    current_username = None
    current_first_name = None
    current_last_name = None
    current_user_id = None
    disable_search = None
    enable_search = None

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
            success, is_admin, password_changed, first_name, last_name, user_id = authenticate_user(username, password)
            if success:
                # On successful login (all above are satisfied and user authenticates properly) set below global variables for later use in the GUI.
                current_username = username
                current_first_name = first_name
                current_last_name = last_name
                current_user_id = user_id
                if is_admin:
                    current_admin_id = user_id # Sets the global variable for later use
                    if not password_changed: # If the user is an admin but its the first login it forces the change password
                        switch_to_change_password(username, from_login=True)
                    else:
                        switch_to_admin_panel() # Switch the user straight to the admin dashboard
                else:
                    switch_to_store_listing() # Switch normal user to the normal store page.
            else:
               display_error(message_label, "Invalid credentials!")

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
            is_valid, validation_message = validate_registration_fields(username, first_name, last_name, password, confirm_password, age)
            if not is_valid:
                display_error(message_label, validation_message)
                return

            result = register_user(username, first_name, last_name, password, int(age))

            if "successful" in result: # Success message if all requirements are met and user is created
                display_success(message_label, result)
            else:
                display_error(message_label, result)

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
        if is_admin and current_admin_status:  # Only show if user is admin AND came from admin panel
            tk.Button(dropdown_frame, text="Back to Admin Panel", command=switch_to_admin_panel, **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)
        tk.Button(dropdown_frame, text="View Cart", command=show_cart, **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)
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
                if resize_timer is not None:
                    window.after_cancel(resize_timer)
                resize_timer = window.after(150, lambda: resize_content(event))

            def debounced_wraplength(event=None):
                """Debounced version of update_wraplength"""
                nonlocal wraplength_timer
                if wraplength_timer is not None:
                    window.after_cancel(wraplength_timer)
                wraplength_timer = window.after(150, lambda: update_wraplength(event))

            def resize_content(event=None):
                if not product[7] or not left_frame.winfo_exists():
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
                    if user_info and dropdown:
                        try:
                            show_dropdown(None, user_info, dropdown)
                            window.after(5000, lambda: safe_hide_dropdown(user_info, dropdown))
                        except tk.TclError:
                            pass  # Ignore if widgets are destroyed
                else:
                    display_error(message_label, message)

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

        # Disable search bar when entering cart
        disable_search()  # Call the disable function
        
        clear_frame(content_frame)
        styles = get_style_config()['cart']
        image_styles = get_style_config()['product_page']['image_frame']
        
        # Create clean copies of styles to avoid conflicts
        label_styles = dict(styles['labels'])
        if 'font' in label_styles: label_styles.pop('font')
        if 'fg' in label_styles: label_styles.pop('fg')
        
        button_styles = dict(styles['buttons'])
        if 'fg' in button_styles: button_styles.pop('fg')
        
        # Create new content_inner_frame with padding
        global content_inner_frame
        content_inner_frame = tk.Frame(
            content_frame, 
            bg=get_style_config()['store_listing']['content']['inner_frame']['bg']
        )
        content_inner_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Remove font and fg from label styles to avoid conflicts
        label_styles = dict(styles['labels'])
        if 'font' in label_styles: label_styles.pop('font')
        if 'fg' in label_styles: label_styles.pop('fg')
        
        # Navigation buttons
        nav_frame = tk.Frame(content_inner_frame, **styles['frame'])
        nav_frame.pack(fill="x", pady=(20, 20), padx=20)
        
        # Left side container for buttons
        button_container = tk.Frame(nav_frame, **styles['frame'])
        button_container.pack(side="left")

        # Back button
        back_button = tk.Button(
            button_container, 
            text="← Back to Store", 
            command=lambda: (
                cleanup_cart(),
                switch_to_store_listing(is_admin=False)
            ), 
            **styles['buttons']
        )
        back_button.pack(side="left", padx=(0, 180)) # right side padding to shift the title towards the center of the checkout section below.
        
        if get_current_user_admin_status(current_username):
            admin_button = tk.Button(
                nav_frame,
                text="Back to Admin Panel", 
                command=switch_to_admin_panel, 
                **styles['buttons']
            )
            admin_button.pack(side="left")

        # Get cart items
        cart_items = get_cart_items(current_user_id)
        
        if not cart_items:
            message_label = tk.Label(content_inner_frame, text="Your cart is empty", **styles['message'])
            message_label.pack(pady=20)
            return

        total_items = sum(item[-1] for item in cart_items)
        total_price = 0
        
        # Cart title next to buttons
        tk.Label(
            nav_frame,
            text=f"Your Cart ({total_items} items)",
            font=("Arial", 16, "bold"),
            fg="white",
            **label_styles
        ).pack(side="left")

        # Create scrollable frame
        wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_frame(content_inner_frame)
        wrapper.pack(fill="both", expand=True)

        # Enable mouse wheel scrolling initially
        bind_wheel()

        # Headers
        header_frame = tk.Frame(scrollable_frame, **styles['frame'])
        header_frame.pack(fill="x", pady=(0, 10), padx=20)
        
        # Column headers
        tk.Label(header_frame, text="Item", width=40, anchor="w", fg="white", **label_styles).pack(side="left", padx=10)
        tk.Label(header_frame, text="Price", width=10, fg="white", **label_styles).pack(side="left", padx=10)
        tk.Label(header_frame, text="Quantity", width=15, fg="white", **label_styles).pack(side="left", padx=10)
        tk.Label(header_frame, text="Total", width=15, fg="white", **label_styles).pack(side="left", padx=10)

        # Add separator
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=20)

        # Cart items loop
        for item in cart_items:
            item_frame = tk.Frame(scrollable_frame, **styles['frame'])
            item_frame.pack(fill="x", pady=10, padx=20)
            
            # Product info with image
            info_frame = tk.Frame(item_frame, **styles['frame'])
            info_frame.pack(side="left", fill="x", expand=True)

            if item[7]: # 7 is the image of the product
                # Set fixed width and minimum height for consistent display locations of each item in the list.
                img = resize_product_image(item[7], 
                                        max_width=300,
                                        min_width=50),
                if img:
                    img_label = tk.Label(info_frame, 
                                    image=img,
                                    **image_styles)
                    img_label.image = img  # Keep reference to avoid garbage collection
                    img_label.pack(side="left", padx=5)
            
            # Product name
            tk.Label(info_frame, text=item[1], font=("Arial", 12), fg="white", **label_styles).pack(side="left", padx=10)
            
            # Unit price
            tk.Label(
                item_frame,
                text=f"£{item[2]:.2f}",
                font=("Arial", 11),
                fg="#666666",
                **label_styles
            ).pack(side="left", padx=(50, 10))
            
            # Quantity controls
            qty_frame = tk.Frame(item_frame, **styles['frame'])
            qty_frame.pack(side="left", padx=10)
            
            def update_quantity(pid, current_qty, delta):
                new_qty = current_qty + delta
                if new_qty <= 0:
                    update_cart_quantity(current_user_id, pid, 0)
                else:
                    update_cart_quantity(current_user_id, pid, new_qty)
                show_cart()

            # Quantity buttons and display
            tk.Button(qty_frame, text="-", command=lambda pid=item[0], qty=item[-1]: update_quantity(pid, qty, -1), width=2, **button_styles).pack(side="left", padx=2)
            tk.Label(qty_frame, text=str(item[-1]), width=3, fg="white", **label_styles).pack(side="left", padx=5)
            tk.Button(qty_frame, text="+", command=lambda pid=item[0], qty=item[-1]: update_quantity(pid, qty, 1), width=2, **button_styles).pack(side="left", padx=2)

            # Item total
            item_total = item[2] * item[-1]
            total_price += item_total
            tk.Label(
                item_frame,
                text=f"£{item_total:.2f}",
                font=("Arial", 11, "bold"),
                fg="white",
                **label_styles
            ).pack(side="left", padx=(50, 10))
            
            # Remove button (red X)
            remove_button = tk.Button(
                item_frame,
                text="×",
                command=lambda pid=item[0]: (
                    update_cart_quantity(current_user_id, pid, 0),  # Remove item
                    show_cart()  # Refresh cart display
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

            # Add separator after each item
            ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=20)

        # Add final separator after all items
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=20)

        # Summary section
        summary_frame = tk.Frame(scrollable_frame, **styles['frame'])
        summary_frame.pack(fill="x", pady=20, padx=20)
        
        # Subtotal
        tk.Label(
            summary_frame,
            text=f"Subtotal: £{total_price:.2f}",
            font=("Arial", 12),
            fg="#666666",
            **label_styles
        ).pack(pady=5)
        
        # Add coupon button
        tk.Button(
            summary_frame,
            text="Add Coupon",
            **button_styles
        ).pack(pady=10)
        
        # Grand total
        tk.Label(
            summary_frame,
            text=f"Grand Total: £{total_price:.2f}",
            font=("Arial", 14, "bold"),
            fg="white",
            **label_styles
        ).pack(pady=10)
        
        # Checkout button
        tk.Button(
            summary_frame,
            text="Check Out",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            **button_styles
        ).pack(pady=10)

        # Bind resize event to check content height
        def check_scroll_needed(event=None):
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if bbox:
                scroll_height = bbox[3] - bbox[1]  # Total scrollable height
                visible_height = canvas.winfo_height()  # Visible canvas height
                
                if scroll_height > visible_height:
                    bind_wheel()  # Enable scrolling
                else:
                    unbind_wheel()  # Disable scrolling

        # Bind to canvas resize events
        canvas.bind('<Configure>', check_scroll_needed)

        # Clean up bindings when leaving cart
        def cleanup_cart():
            unbind_wheel()  # Remove scroll wheel binding
            canvas.unbind('<Configure>')  # Remove resize check binding
            window.unbind("<Button-1>")  # Remove other bindings

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

        # Get current admin status before creating dropdown buttons
        if get_current_user_admin_status(current_username):  # Use fresh admin status check
            tk.Button(dropdown_frame, text="Back to Admin Panel", command=switch_to_admin_panel, **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)

        # Add buttons to the dropdown frame with consistent styling
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
            ("View Store as User", lambda: switch_to_store_listing(is_admin=True))
        ]
        create_nav_buttons(left_nav, button_configs)

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
            add_product(name, price, None, listed, description, category_id, image, stock)
            display_success(message_label, "Product added successfully!")
        
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

        # Create search widget with dynamic width
        search_frame, search_entry = setup_search_widget(search_container)
        search_frame.pack(expand=True)  # Allow frame to expand

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
            db_delete_product(product_id)
            display_products(get_products(listed_only=False))

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
                return

            is_valid, message = validate_category_name(name)
            if not is_valid:
                display_error(message_label, message)
                return

            success, message = add_category(name)
            if success:
                display_success(message_label, message)
                category_entry.delete(0, tk.END)
                display_categories()
            else:
                display_error(message_label, message)

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
                category_entry.delete(0, tk.END)
                display_categories()
            else:
                display_error(message_label, message)

        def handle_delete_category(category_id):
            success, message = delete_category(category_id)
            if success:
                display_success(message_label, message)
                display_categories()
            else:
                display_error(message_label, message)

        # Call display_categories to show the categories initially
        display_categories()

    # Change password screen that is called for when an admin account is logged into for the first time. 
    def switch_to_change_password(username, from_login=False):
        """Prompt admin to change their password."""
        window.geometry("400x300")
        clear_frame(main_frame)

        # Select theme based on context
        theme_type = 'light' if from_login else 'dark'
        styles = get_style_config()['change_password'][theme_type]

        window.unbind("<Configure>")
        window.unbind("<Button-1>")

        # Configure main frame background
        main_frame.configure(bg=styles['title']['bg'])

        tk.Label(main_frame, text="Change Password", **styles['title']).pack(pady=10)

        new_password_entry, _, _ = create_password_field(main_frame, "Password", eye_open_image=eye_open_image, eye_closed_image=eye_closed_image, style=theme_type)

        confirm_password_entry, _, _ = create_password_field(main_frame, "Confirm Password", eye_open_image=eye_open_image, eye_closed_image=eye_closed_image, style=theme_type)

        def change_password():
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()

            is_valid, validation_message = validate_password_match(new_password, confirm_password)
            if not is_valid:
                display_error(message_label, validation_message)
                return

            is_valid, validation_message = validate_password(username, new_password)
            if not is_valid:
                display_error(message_label, validation_message)
                return
            
            success, message = update_user_password(username, new_password)
            if success:
                display_success(message_label, message)
                switch_to_admin_panel()
            else:
                display_error(message_label, message)

        # Binds the enter key to the login function if either the button or the main_frame is in focus
        message_label = tk.Label(main_frame, text="", **styles['message'])
        message_label.pack()

        change_button = tk.Button(main_frame, text="Change Password", command=change_password, **styles['buttons'])
        change_button.pack(pady=10)
        
        # Bind enter key to both frame and button
        main_frame.bind('<Return>', lambda event: change_password())
        change_button.bind('<Return>', lambda event: change_password())

    def logout():
        """Handle logout."""
        global current_username, current_first_name, current_last_name, current_admin_id, current_user_id
        current_user_id = None
        current_username = None
        current_first_name = None
        current_last_name = None
        current_admin_id = None
        show_login_screen()

    window.mainloop() # Actually starts the application and allows the user to interact with the GUI

# TODO: Explain functionality reason behind this on ONE of the files (pref main.py) #
if __name__ == "__main__":
    start_app()