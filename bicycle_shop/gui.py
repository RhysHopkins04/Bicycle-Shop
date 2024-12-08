import tkinter as tk
from tkinter import ttk, filedialog as filedialog, PhotoImage

# Functions from other locations in the program: auth, database, qr_code_util
from auth import (register_user, authenticate_user, update_user_password, promote_user_to_admin, 
                  demote_user_from_admin
                  )
from database import (create_tables, initialize_admin, get_products, get_product_by_id, get_connection, 
                      list_product, add_product, update_product, delete_product as db_delete_product, 
                      add_category, get_categories, get_category_id, get_category_name, delete_category, 
                      update_category
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
from file_manager import (get_application_settings, get_icon_paths)

# Start GUI Function to be called in the main.py file post further checks for the tables and admin user.
def start_app():
    """Start the Tkinter GUI application.""" #Docstring's which i will use to help with future code documentation along with the comments.
    
    # Get configuration settings
    app_settings = get_application_settings()
    icon_paths = get_icon_paths()

    # Global Variables other than the main_frame 
    global main_frame, logout_button, window, current_username, current_first_name, current_last_name, current_admin_id
    logout_button = None
    current_admin_id = None
    current_username = None
    current_first_name = None
    current_last_name = None

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
            global current_username, current_first_name, current_last_name, current_admin_id
            username = username_entry.get()
            password = password_entry.get()
            success, is_admin, password_changed, first_name, last_name, user_id = authenticate_user(username, password)
            if success:
                # On successful login (all above are satisfied and user authenticates properly) set below global variables for later use in the GUI.
                current_username = username
                current_first_name = first_name
                current_last_name = last_name
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
        search_container.pack(side="left", fill="x", expand=True, padx=(20, 0))  # Add left padding

        # Create search widget with dynamic width
        search_frame, search_entry = setup_search_widget(search_container)
        search_frame.pack(expand=True)  # Allow frame to expand

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

        # Add buttons to the dropdown frame with consistent styling
        if is_admin:
            tk.Button(dropdown_frame, text="Back to Admin Panel", command=switch_to_admin_panel, **styles['dropdown']['buttons'], width=20).pack(fill="x", padx=10, pady=5)
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

                    product_frame = create_product_listing_frame(row_frame, product, 290, show_product_page)

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

    def show_product_page(product_id):
        """Display the product page for the given product ID."""
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

            # Add to Cart button
            cart_button = tk.Button(inner_right_frame, text="Add to Cart", **styles['buttons'])
            cart_button.pack(pady=(50, 0))

            # Stock display
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
                if not product[7]:
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

        else:
            message_label = tk.Label(content_inner_frame, text="", **styles['message'])
            message_label.pack()
            display_error(message_label, "Product not found!")

    # TODO: Add the rest of the functionality required + extras and fill out the "Dashboard" screen itself for commonly used parts of the program to speed up tasks #
    # If the user account is Admin (Administrative Account) brings to the Admin Dashboard
    def switch_to_admin_panel():
        """Navigate to the admin panel."""
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

    # TODO: Make it so that you can change if a product is listed or not from the main manage products screen along with inside the edit product screen for easier ux due to less clicks. #
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
        """Display the edit product screen."""
        clear_frame(content_inner_frame)

        styles = get_style_config()['edit_product']

        window.unbind("<Configure>")
        window.unbind("<Button-1>")

        combo_style = ttk.Style()
        combo_style.configure('Edit.TCombobox',
            background=styles['combobox']['bg'],
            fieldbackground=styles['combobox']['fieldbackground'],
            foreground=styles['combobox']['fg'],
            selectbackground=styles['combobox']['selectbackground'],
            selectforeground=styles['combobox']['selectforeground']
        )
        
        tk.Label(content_inner_frame, text="Edit Product", **styles['title']).pack(pady=10)
        product = get_product_by_id(product_id)

        # Creates the entry boxes for the name and price of the product and sets the default values to the current values of the product from the database
        tk.Label(content_inner_frame, text="Name", **styles['labels']).pack()
        name_entry = tk.Entry(content_inner_frame, **styles['entries'])
        name_entry.insert(0, product[1])
        name_entry.pack()

        tk.Label(content_inner_frame, text="Price", **styles['labels']).pack()
        price_entry = tk.Entry(content_inner_frame, **styles['entries'])
        price_entry.insert(0, product[2])
        price_entry.pack()

        tk.Label(content_inner_frame, text="Description", **styles['labels']).pack()
        description_entry = tk.Entry(content_inner_frame, **styles['entries'])
        description_entry.insert(0, product[5])
        description_entry.pack()

        tk.Label(content_inner_frame, text="Category", **styles['labels']).pack()
        category_combobox = ttk.Combobox(content_inner_frame, values=get_categories(), width=price_entry.cget("width") - 3, style='Edit.TCombobox')
        category_name = get_category_name(product[6])
        if category_name:
            category_combobox.current(get_categories().index(category_name))
        category_combobox.pack()

        tk.Label(content_inner_frame, text="Image", **styles['labels']).pack()
        image_path = tk.StringVar(value=product[7])
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
        stock_entry.insert(0, product[8])
        stock_entry.pack()

        tk.Label(content_inner_frame, text="Listed", **styles['labels']).pack()
        listed_var = tk.StringVar(value="Yes" if product[4] else "No")
        listed_combobox = ttk.Combobox(content_inner_frame, textvariable=listed_var, values=["Yes", "No"], width=price_entry.cget("width") - 3, style='Edit.TCombobox')
        listed_combobox.pack()

        message_label = tk.Label(content_inner_frame, text="", **styles['message'])
        message_label.pack(pady=10)

        def save_edit_product():
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

            keep_files = not listed  # True if unlisting (listed=0)
            update_product(product_id, name, price, None, description, category_id, image, stock, keep_files)
            list_product(product_id, listed)
            display_success(message_label, "Product updated successfully!")
            show_manage_products_screen()

        def cancel_edit_product():
            clear_frame(content_inner_frame)
            show_manage_products_screen()

        tk.Button(content_inner_frame, text="Save", command=save_edit_product, **styles['buttons']).pack(pady=10)
        tk.Button(content_inner_frame, text="Cancel", command=cancel_edit_product, **styles['buttons']).pack(pady=10)

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


    window.mainloop() # Actually starts the application and allows the user to interact with the GUI

# TODO: Explain functionality reason behind this on ONE of the files (pref main.py) #
if __name__ == "__main__":
    start_app()