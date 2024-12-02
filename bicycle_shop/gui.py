# Packages in use for the GUI of the application: tkinter, Pillow, os
import tkinter as tk
from tkinter import ttk, filedialog as filedialog, PhotoImage
from PIL import ImageTk, Image
import os

# Functions from other locations in the program: auth, database, qr_code_util
import qr_code_util
from auth import register_user, authenticate_user
from database import create_tables, initialize_admin, get_products, get_product_by_id, get_connection, list_product, add_product, update_product, delete_product as db_delete_product, promote_user_to_admin, demote_user_from_admin,add_category, get_categories, get_category_id, get_category_name
from validation import validate_password, validate_empty_fields, validate_password_match, validate_age, validate_registration_fields, validate_username_uniqueness

# Start GUI Function to be called in the main.py file post further checks for the tables and admin user.
def start_app():
    """Start the Tkinter GUI application.""" #Docstring's which i will use to help with future code documentation along with the comments.

    # Global Variables other than the main_frame 
    global main_frame, logout_button, window, is_fullscreen, current_username, current_first_name, current_last_name, current_admin_id
    logout_button = None
    is_fullscreen = False
    current_admin_id = None
    current_username = None
    current_first_name = None
    current_last_name = None

    # Redundant but a good check to ensure that the tables and an admin user are created on startup encase they do not exist.
    create_tables()
    initialize_admin()

    # Initializes the window and sets it so its title shows as "Bicycle Shop Management"
    window = tk.Tk()
    window.title("Bicycle Shop Management")

    # Creates the initial Main frame for the application used for holding the main widgets/functionality.
    main_frame = tk.Frame(window)
    main_frame.pack(fill="both", expand=True)

    # Checks if  the screen is in fullscreen mode using an event handler shown below
    def toggle_fullscreen(event=None):
        """Toggle fullscreen mode."""
        global is_fullscreen
        is_fullscreen = not is_fullscreen
        window.attributes("-fullscreen", is_fullscreen)

    window.bind("<F11>", toggle_fullscreen) # Bind the F11 key to toggle fullscreen

    # Function used to dynamically clear and update the frame that is being called for reuseability in the code.
    def clear_frame(frame):
        """Clear all widgets from the given frame."""
        for widget in frame.winfo_children():
            widget.destroy()

    # Function to display an error message for main frames to make the code more modular and easier to maintain
    def display_error(message):
            tk.Label(main_frame, text=message, fg="red").pack()

    eye_open_image = PhotoImage(file="./Icons/visible.png")
    eye_closed_image = PhotoImage(file="./Icons/hidden.png")

    def toggle_password_visibility(entry, button, show):
        """Toggle the visibility of the password."""
        if entry.cget('show') == '':
            entry.config(show=show)
            button.config(image=eye_closed_image)
        else:
            entry.config(show='')
            button.config(image=eye_open_image)

    # Creates the Login screen for the application
    def show_login_screen():
        """Display the login screen."""
        window.geometry("400x300") # Login screen by standard size
        clear_frame(main_frame)

        tk.Label(main_frame, text="Login", font=("Arial", 18)).pack(pady=10)

        tk.Label(main_frame, text="Username").pack()
        username_entry = tk.Entry(main_frame)
        username_entry.pack()
        username_entry.focus_set() # Starts with the focus on this field for fast information input

        tk.Label(main_frame, text="Password").pack()
        password_entry = tk.Entry(main_frame, show="*")
        password_entry.pack()

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
                        switch_to_change_password(username)
                    else:
                        switch_to_admin_panel() # Switch the user straight to the admin dashboard
                else:
                    switch_to_store_listing() # Switch normal user to the normal store page.
            else:
               display_error("Invalid credentials!")# Error message for if the user fails authentication

        login_button = tk.Button(main_frame, text="Login", command=login)
        login_button.pack(pady=10)

        create_account_button = tk.Button(main_frame, text="Create Account", command=show_register_screen) # switch_to_register)
        create_account_button.pack()

        # Binds the enter key to the login function if either the button or the main_frame is in focus
        main_frame.bind('<Return>', login) 
        login_button.bind('<Return>', login)

    # Shows the register screen for if you need to create a new users on the start of the application
    def show_register_screen():
        """Display the register screen."""
        window.geometry("400x400") # Register screen by standard size
        clear_frame(main_frame)

        tk.Label(main_frame, text="Register", font=("Arial", 18)).pack(pady=10)

        tk.Label(main_frame, text="Username").pack()
        username_entry = tk.Entry(main_frame)
        username_entry.pack()
        username_entry.focus_set() # Sets the focus on application start to the username field

        tk.Label(main_frame, text="First Name").pack()
        first_name_entry = tk.Entry(main_frame)
        first_name_entry.pack()

        tk.Label(main_frame, text="Last Name").pack()
        last_name_entry = tk.Entry(main_frame)
        last_name_entry.pack()

        tk.Label(main_frame, text="Password").pack()
        password_frame = tk.Frame(main_frame)
        password_frame.pack(fill="x")
        password_entry = tk.Entry(password_frame, show="*")
        password_entry.pack(side="top")
        password_button = tk.Button(password_frame, image=eye_closed_image, command=lambda: toggle_password_visibility(password_entry, password_button, '*'))
        password_button.pack()

        tk.Label(main_frame, text="Confirm Password").pack()
        confirm_password_entry = tk.Entry(main_frame, show="*")
        confirm_password_entry.pack()

        tk.Label(main_frame, text="Age").pack()
        age_entry = tk.Entry(main_frame)
        age_entry.pack()

        def register(event=None):
            username = username_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()
            age = age_entry.get()
            is_valid, validation_message = validate_registration_fields(username, first_name, last_name, password, confirm_password, age)
            if not is_valid:
                display_error(validation_message)
                return

            result = register_user(username, first_name, last_name, password, int(age))
            tk.Label(main_frame, text=result, fg="green" if "successful" in result else "red").pack() # Success message if all requirements are met and user is created

        register_button = tk.Button(main_frame, text="Register", command=register)
        register_button.pack(pady=10)

        back_to_login_button = tk.Button(main_frame, text="Back to Login", command=show_login_screen)
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

    # Adds a logout button to the bottom right corner of the screen for tag-on to the end of a function 
    def add_logout_button():
        """Add a logout button to the bottom right corner."""
        global logout_button
        if logout_button:
            logout_button.destroy()
        logout_button = tk.Button(main_frame, text="Logout", command=show_login_screen) # Button leads back to the login screen closing the other windows
        logout_button.pack(side="bottom", anchor="se", padx=10, pady=10) # Locates it at the bottom side of the screen, anchored to the bottom right (south east) padded in 10 pixels x and y

    # If the user account is a non admin (standard account) brings to this page
    def switch_to_store_listing(is_admin=False):
        """Navigate to the store listing."""
        window.attributes("-fullscreen", False) # When "True" means post login page the application will automatically fullscreen.
        window.geometry("1920x1080+0+0") # Default window size for the admin dashboard which should open at the coordinates 0,0 (top left of the screen)
        clear_frame(main_frame)

        # Create the top bar
        top_bar = tk.Frame(main_frame, height=100, bg="#171d22")
        top_bar.pack(side="top", fill="x")
        top_bar.pack_propagate(False)  # When set to "True" Prevent the frame from shrinking to fit its contents

        tk.Label(top_bar, text="Store Listing", font=("Swis721 Blk BT", 40), bg="#171d22", fg="white").pack(side="left", padx=20, pady=10)

        # Create a frame for the buttons on the right side of the header
        button_frame = tk.Frame(top_bar, bg="#171d22")
        button_frame.pack(side="right", padx=20, pady=10)

        # Add user information frame
        user_info_frame = tk.Frame(button_frame, bg="#171d22")
        user_info_frame.pack(side="left", padx=20, pady=10)

        # Load the user icon
        user_icn = ImageTk.PhotoImage(Image.open("./Icons/user_icon_thumbnail.png"))
        user_info_frame.user_icn = user_icn

        admin_icn = ImageTk.PhotoImage(Image.open("./Icons/admin_icon_thumbnail.png"))
        user_info_frame.admin_icn = admin_icn

        # Add the icon to the user_info_frame
        if is_admin:
            icon_label = tk.Label(user_info_frame, image=admin_icn, bg="#171d22")
            icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 5))
        else:
            icon_label = tk.Label(user_info_frame, image=user_icn, bg="#171d22")
            icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 5))

        # Add the first and last name from the global variables set on signin successful for the first line + username from its global variable on signin for the second line with custom size and formatting.
        name_label = tk.Label(user_info_frame, text=f"{current_first_name} {current_last_name}", font=("Arial", 20), bg="#171d22", fg="white")
        name_label.grid(row=0, column=1, sticky="w")
        username_label = tk.Label(user_info_frame, text=f"@{current_username}", font=("Arial", 12), bg="#171d22", fg="darkgrey")
        username_label.grid(row=1, column=1, sticky="w")

        # Add the dropdown indicator
        dropdown_indicator = tk.Label(user_info_frame, text="▼", font=("Arial", 12), bg="#171d22", fg="white")
        dropdown_indicator.grid(row=0, column=2, rowspan=2, padx=(5, 0))

       # Create a dropdown frame with a more visible style
        dropdown_frame = tk.Frame(main_frame, bg="#171d22", bd=1, relief="solid", highlightthickness=1, highlightbackground="white")
        dropdown_frame.place_forget()  # Initially hide the dropdown frame

        # Add buttons to the dropdown frame with consistent styling
        if is_admin:
            tk.Button(dropdown_frame, text="Back to Admin Panel", command=switch_to_admin_panel, 
                    bg="#171d22", fg="white", activebackground="#2a2f35", 
                    activeforeground="white", width=20).pack(fill="x", padx=10, pady=5)
        tk.Button(dropdown_frame, text="Logout", command=show_login_screen,
                bg="#171d22", fg="white", activebackground="#2a2f35", 
                activeforeground="white", width=20).pack(fill="x", padx=10, pady=5)

        # Prints below were for debugging process to ensure that the dropdown was working as intended after many failures
        def show_dropdown(event):
            #print("Showing dropdown")
            # Position the dropdown frame below the user_info_frame
            x = user_info_frame.winfo_rootx()
            y = user_info_frame.winfo_rooty() + user_info_frame.winfo_height() - 10
            
            # Ensure the dropdown is properly sized and visible
            dropdown_frame.lift()  # Bring to front
            dropdown_frame.update_idletasks()  # Force geometry update
            dropdown_frame.place(x=x, y=y, width=user_info_frame.winfo_width())
            
            #print(f"Placed dropdown at ({x}, {y})")
            #print(f"Dropdown dimensions: {dropdown_frame.winfo_width()}x{dropdown_frame.winfo_height()}")

        def hide_dropdown(event=None):
            #print("Hide dropdown called")
            if event is None:
                dropdown_frame.place_forget()
                return
            
            # Get the mouse coordinates relative to the screen
            mouse_x = event.x_root
            mouse_y = event.y_root
            #print(f"Mouse position: ({mouse_x}, {mouse_y})")
            
            # Check if the mouse is over either the user_info_frame or dropdown_frame
            over_user_info = (
                user_info_frame.winfo_rootx() <= mouse_x <= user_info_frame.winfo_rootx() + user_info_frame.winfo_width() and
                user_info_frame.winfo_rooty() <= mouse_y <= user_info_frame.winfo_rooty() + user_info_frame.winfo_height()
            )
            
            over_dropdown = (
                dropdown_frame.winfo_rootx() <= mouse_x <= dropdown_frame.winfo_rootx() + dropdown_frame.winfo_width() and
                dropdown_frame.winfo_rooty() <= mouse_y <= dropdown_frame.winfo_rooty() + dropdown_frame.winfo_height()
            )
            
            #print(f"Over user info: {over_user_info}")
            #print(f"Over dropdown: {over_dropdown}")
            
            if not (over_user_info or over_dropdown):
                dropdown_frame.place_forget()

        def hide_dropdown_on_click(event):
            #print("hide_dropdown_on_click called")
            # Hide the dropdown frame if clicking outside of it
            mouse_x = event.x_root
            mouse_y = event.y_root
            
            # Check if clicking within user_info_frame or dropdown_frame
            over_user_info = (
                user_info_frame.winfo_rootx() <= mouse_x <= user_info_frame.winfo_rootx() + user_info_frame.winfo_width() and
                user_info_frame.winfo_rooty() <= mouse_y <= user_info_frame.winfo_rooty() + user_info_frame.winfo_height()
            )
            
            over_dropdown = (
                dropdown_frame.winfo_rootx() <= mouse_x <= dropdown_frame.winfo_rootx() + dropdown_frame.winfo_width() and
                dropdown_frame.winfo_rooty() <= mouse_y <= dropdown_frame.winfo_rooty() + dropdown_frame.winfo_height()
            )
            
            #print(f"Click coordinates: ({mouse_x}, {mouse_y})")
            #print(f"Over user info: {over_user_info}")
            #print(f"Over dropdown: {over_dropdown}")
            
            if not (over_user_info or over_dropdown):
                dropdown_frame.place_forget()
                #print("Dropdown hidden on click")

        # Bind events to all relevant widgets
        for widget in user_info_frame.winfo_children():
            widget.bind("<Enter>", show_dropdown)
        user_info_frame.bind("<Enter>", show_dropdown)
        icon_label.bind("<Enter>", show_dropdown)
        name_label.bind("<Enter>", show_dropdown)
        username_label.bind("<Enter>", show_dropdown)
        dropdown_indicator.bind("<Enter>", show_dropdown)

        # Remove the main_frame.bind("<Leave>", hide_dropdown) as it might be causing issues
        # Instead, bind to specific areas
        user_info_frame.bind("<Leave>", hide_dropdown)
        dropdown_frame.bind("<Leave>", hide_dropdown)

        window.bind("<Button-1>", hide_dropdown_on_click)

        # Create the content frame with the dark background for future addition of dynamic product listings
        global content_frame
        content_frame = tk.Frame(main_frame, bg="#000000")
        content_frame.pack(side="right", fill="both", expand=True)  # Fills the remaining space of the window with this frame

         # Creates an inner content frame for the dynamic widgets to be added to so there is a contrast border between the header, nav bar and the widgets
        global content_inner_frame
        content_inner_frame = tk.Frame(content_frame, bg="#171d22", padx=50, pady=50)
        content_inner_frame.pack(fill="both", expand=True, padx=50, pady=50)  # Fills the remaining space of the window with this frame

        # Create a frame for the search bar
        search_frame = tk.Frame(top_bar, bg="#171d22")
        search_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Create a search entry box with placeholder text
        search_entry = tk.Entry(search_frame, width=50, fg="dark gray", font=("Arial", 20))
        search_entry.insert(0, "Search for products")
        search_entry.pack(pady=10)

        def on_focus_in(event):
            if search_entry.get() == "Search for products":
                search_entry.delete(0, tk.END)
                search_entry.config(fg="black")

        def on_focus_out(event):
            if search_entry.get() == "":
                search_entry.insert(0, "Search for products")
                search_entry.config(fg="dark gray")

        search_entry.bind("<FocusIn>", on_focus_in)
        search_entry.bind("<FocusOut>", on_focus_out)

        # Bind the search entry to the filter function
        search_entry.bind("<KeyRelease>", lambda event: filter_products())

        # Create a canvas (which allows scrolling) and a scrollbar
        canvas = tk.Canvas(content_inner_frame, bg="#171d22")
        scrollbar = tk.Scrollbar(content_inner_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#171d22")
        
        # Checks that the canvas' scroll area is encompassing all the content inside when the frame size is changed through the bounding box check
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        # Configures the canvas to have the scrollable frame inside of it and the scrollbar to the right of the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Function to allow the mouse wheel to scroll the canvas
        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        def filter_products():
            search_query = search_entry.get().lower()  # Sets the search query to the text from the search box but in full lowercase to avoid case sensitivity

            # Calls the get_products function with the limitation for only listed products and then filters the products based on the search query
            filtered_products = [
                product for product in get_products(listed_only=True)
                if search_query in product[1].lower() or search_query in str(product[2])
            ]
            display_products(filtered_products)  # Adjusts the display_products function to display only the filtered products vs the standard "products" which is all products

        def display_products(products):
            clear_frame(scrollable_frame)

            # If there are no products available it will display a message saying so in red text otherwise display the products in a grid format
            if not products:
                tk.Label(scrollable_frame, text="No products available.", fg="red", bg="#171d22").pack(pady=10)
            else:
                # Get the width of the scrollable_frame
                canvas.update_idletasks()
                content_width = canvas.winfo_width()
                product_frame_width = 290  # Set the width of each product frame (adjust as needed)
                padding = 5  # Set the padding between product frames

                # Calculate the number of columns that can fit in the available width
                num_columns = max(1, content_width // (product_frame_width + padding))

                # Initializes the variables
                row_frame = None
                col = 0
                row_count = 0

                for product in products:
                    # If the column is 0 it will create a new row frame to stack the products in a grid format
                    if col == 0:
                        row_frame = tk.Frame(scrollable_frame, bg="#171d22")
                        row_frame.pack(fill="x", pady=10)
                        row_count += 1

                    # Creates a frame for the product to be displayed in + creates the labels and content to fill out the product with information from the product tuple
                    product_frame = tk.Frame(row_frame, width=product_frame_width, padx=5, pady=5, bg="#171d22")
                    product_frame.pack(side="left", padx=5, pady=5)

                    tk.Label(product_frame, text=f"Name: {product[1]}", bg="#171d22", fg="white").pack()
                    tk.Label(product_frame, text=f"Price: £{product[2]:.2f}", bg="#171d22", fg="white").pack()

                    qr_code_image = tk.PhotoImage(file=product[3])  # Takes the qr code image from the product tuple and sets it to a local variable to be used in the label
                    tk.Label(product_frame, image=qr_code_image, bg="#171d22").pack()
                    product_frame.image = qr_code_image  # stores the image inside of product_frame to avoid garbage collection since it was previously clearing

                    col += 1
                    if col >= num_columns:
                        col = 0
                
                # Enable or disable scrolling based on the number of rows
                if row_count > 1:
                    canvas.bind_all("<MouseWheel>", on_mouse_wheel)
                    scrollbar.pack(side="right", fill="y")
                else:
                    canvas.unbind_all("<MouseWheel>")
                    scrollbar.pack_forget()

        # Call display_products initially to show all products
        display_products(get_products(listed_only=True))

    # TODO: Add the rest of the functionality required + extras and fill out the "Dashboard" screen itself for commonly used parts of the program to speed up tasks #
    # If the user account is Admin (Administrative Account) brings to the Admin Dashboard
    def switch_to_admin_panel():
        """Navigate to the admin panel."""
        window.geometry("1920x1080+0+0") # Default window size for the admin dashboard which should open at the coordinates 0,0 (top left of the screen)
        clear_frame(main_frame)

        # Create the top bar
        top_bar = tk.Frame(main_frame, height=100, bg="#171d22")
        top_bar.pack(side="top", fill="x")
        top_bar.pack_propagate(False)  # When set to "True" Prevent the frame from shrinking to fit its contents

        # Create the left navigation bar
        left_nav = tk.Frame(main_frame, width=400, bg="#171d22")
        left_nav.pack(side="left", fill="y")
        left_nav.pack_propagate(False)  # When set to "True" Prevent the frame from shrinking to fit its contents

        # Create a frame for the buttons on the right side of the header
        button_frame = tk.Frame(top_bar, bg="#171d22")
        button_frame.pack(side="right", padx=20, pady=10)

        # Add user information frame
        user_info_frame = tk.Frame(button_frame, bg="#171d22")
        user_info_frame.pack(side="left", padx=20, pady=10)

        # Load the user icon
        user_icn = ImageTk.PhotoImage(Image.open("./Icons/user_icon_thumbnail.png"))
        user_info_frame.user_icn = user_icn

        admin_icn = ImageTk.PhotoImage(Image.open("./Icons/admin_icon_thumbnail.png"))
        user_info_frame.admin_icn = admin_icn

        # Add the icon to the user_info_frame
        icon_label = tk.Label(user_info_frame, image=admin_icn, bg="#171d22")
        icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 5))

        # Add the first and last name from the global variables set on signin successful for the first line + username from its global variable on signin for the second line with custom size and formatting.
        name_label = tk.Label(user_info_frame, text=f"{current_first_name} {current_last_name}", font=("Arial", 20), bg="#171d22", fg="white")
        name_label.grid(row=0, column=1, sticky="w")
        username_label = tk.Label(user_info_frame, text=f"@{current_username}", font=("Arial", 12), bg="#171d22", fg="darkgrey")
        username_label.grid(row=1, column=1, sticky="w")

        # Add the dropdown indicator
        dropdown_indicator = tk.Label(user_info_frame, text="▼", font=("Arial", 12), bg="#171d22", fg="white")
        dropdown_indicator.grid(row=0, column=2, rowspan=2, padx=(5, 0))

       # Create a dropdown frame with a more visible style
        dropdown_frame = tk.Frame(main_frame, bg="#171d22", bd=1, relief="solid", highlightthickness=1, highlightbackground="white")
        dropdown_frame.place_forget()  # Initially hide the dropdown frame

        # Add buttons to the dropdown frame with consistent styling
        tk.Button(dropdown_frame, text="Logout", command=show_login_screen,
                bg="#171d22", fg="white", activebackground="#2a2f35", 
                activeforeground="white", width=20).pack(fill="x", padx=10, pady=5)

        # Prints below were for debugging process to ensure that the dropdown was working as intended after many failures
        def show_dropdown(event):
            #print("Showing dropdown")
            # Position the dropdown frame below the user_info_frame
            x = user_info_frame.winfo_rootx()
            y = user_info_frame.winfo_rooty() + user_info_frame.winfo_height() - 10
            
            # Ensure the dropdown is properly sized and visible
            dropdown_frame.lift()  # Bring to front
            dropdown_frame.update_idletasks()  # Force geometry update
            dropdown_frame.place(x=x, y=y, width=user_info_frame.winfo_width())
            
            #print(f"Placed dropdown at ({x}, {y})")
            #print(f"Dropdown dimensions: {dropdown_frame.winfo_width()}x{dropdown_frame.winfo_height()}")

        def hide_dropdown(event=None):
            #print("Hide dropdown called")
            if event is None:
                dropdown_frame.place_forget()
                return
            
            # Get the mouse coordinates relative to the screen
            mouse_x = event.x_root
            mouse_y = event.y_root
            #print(f"Mouse position: ({mouse_x}, {mouse_y})")
            
            # Check if the mouse is over either the user_info_frame or dropdown_frame
            over_user_info = (
                user_info_frame.winfo_rootx() <= mouse_x <= user_info_frame.winfo_rootx() + user_info_frame.winfo_width() and
                user_info_frame.winfo_rooty() <= mouse_y <= user_info_frame.winfo_rooty() + user_info_frame.winfo_height()
            )
            
            over_dropdown = (
                dropdown_frame.winfo_rootx() <= mouse_x <= dropdown_frame.winfo_rootx() + dropdown_frame.winfo_width() and
                dropdown_frame.winfo_rooty() <= mouse_y <= dropdown_frame.winfo_rooty() + dropdown_frame.winfo_height()
            )
            
            #print(f"Over user info: {over_user_info}")
            #print(f"Over dropdown: {over_dropdown}")
            
            if not (over_user_info or over_dropdown):
                dropdown_frame.place_forget()

        def hide_dropdown_on_click(event):
            #print("hide_dropdown_on_click called")
            # Hide the dropdown frame if clicking outside of it
            mouse_x = event.x_root
            mouse_y = event.y_root
            
            # Check if clicking within user_info_frame or dropdown_frame
            over_user_info = (
                user_info_frame.winfo_rootx() <= mouse_x <= user_info_frame.winfo_rootx() + user_info_frame.winfo_width() and
                user_info_frame.winfo_rooty() <= mouse_y <= user_info_frame.winfo_rooty() + user_info_frame.winfo_height()
            )
            
            over_dropdown = (
                dropdown_frame.winfo_rootx() <= mouse_x <= dropdown_frame.winfo_rootx() + dropdown_frame.winfo_width() and
                dropdown_frame.winfo_rooty() <= mouse_y <= dropdown_frame.winfo_rooty() + dropdown_frame.winfo_height()
            )
            
            #print(f"Click coordinates: ({mouse_x}, {mouse_y})")
            #print(f"Over user info: {over_user_info}")
            #print(f"Over dropdown: {over_dropdown}")
            
            if not (over_user_info or over_dropdown):
                dropdown_frame.place_forget()
                #print("Dropdown hidden on click")

        # Bind events to all relevant widgets
        for widget in user_info_frame.winfo_children():
            widget.bind("<Enter>", show_dropdown)
        user_info_frame.bind("<Enter>", show_dropdown)
        icon_label.bind("<Enter>", show_dropdown)
        name_label.bind("<Enter>", show_dropdown)
        username_label.bind("<Enter>", show_dropdown)
        dropdown_indicator.bind("<Enter>", show_dropdown)

        # Remove the main_frame.bind("<Leave>", hide_dropdown) as it might be causing issues
        # Instead, bind to specific areas
        user_info_frame.bind("<Leave>", hide_dropdown)
        dropdown_frame.bind("<Leave>", hide_dropdown)

        window.bind("<Button-1>", hide_dropdown_on_click)

        # Create the content frame with the black background for future addition of dynamic wigets
        global content_frame
        content_frame = tk.Frame(main_frame, bg="#000000")
        content_frame.pack(side="right", fill="both", expand=True) # Fills the remaining space of the window with this frame

        # Creates an inner content frame for the dynamic widgets to be added to so there is a contrast border between the header, nav bar and the widgets
        global content_inner_frame
        content_inner_frame = tk.Frame(content_frame, bg="#171d22", padx=50, pady=50)
        content_inner_frame.pack(fill="both", expand=True, padx=50, pady=50) # Fills the remaining space of the window with this frame

        # TODO: May need to be changed to a default font for distribution. #
        # Adds the Dashboard Main title on the header with a custom font. 
        tk.Label(top_bar, text="Dashboard", font=("Swis721 Blk BT", 40), bg="#171d22", fg="white").pack(side="left", padx=20, pady=30)

        # Text lable that just announces the below are for the naivgation of the application styled like a webapp site
        tk.Label(left_nav, text="Navigation", font=("Arial", 16), bg="#171d22", fg="darkgrey").pack(side="top", anchor="nw", padx=10, pady=10)

        # Defines the styles for use on multiple neatly when there is lots of styling in a dictionary
        button_style = {
            "font": ("Arial", 20),
            "bg": "#171d22",
            "fg": "white",
            "bd": 2,
            "highlightbackground": "darkgrey",
            "highlightcolor": "darkgrey",
            "highlightthickness": 2,
            "activebackground": "#171d22",
            "activeforeground": "white"
        }

        # Create buttons for the nav with that button style
        buttons = [
            tk.Button(left_nav, text="Dashboard", command=switch_to_admin_panel, **button_style), # **button_style is a dictionary unpacking to apply the style to the button
            tk.Button(left_nav, text="Add Product", command=show_add_product_screen, **button_style),
            tk.Button(left_nav, text="Manage Products", command=show_manage_products_screen, **button_style),
            tk.Button(left_nav, text="Manage Categories", command=show_manage_categories_screen, **button_style),
            tk.Button(left_nav, text="View Store as User", command=lambda: switch_to_store_listing(is_admin=True), **button_style),
            tk.Button(left_nav, text="Logout", command=show_login_screen, **button_style)
        ]

        # Calculates the width of the largest button and sets all buttons to that width with adjustments for a uniform look
        max_width = max(button.winfo_reqwidth() for button in buttons)
        for button in buttons:
            button.config(width=max_width - 10)
            button.pack(padx = 10, pady=5)

    # TODO: 
    def show_add_product_screen():
        """Display the add product screen."""
        clear_frame(content_inner_frame)

        tk.Label(content_inner_frame, text="Add Product", font=("Arial", 24, "bold"), bg="#171d22", fg="white").pack(pady=10)

        tk.Label(content_inner_frame, text="Name", bg="#171d22", fg="white").pack()
        name_entry = tk.Entry(content_inner_frame)
        name_entry.pack()

        tk.Label(content_inner_frame, text="Price", bg="#171d22", fg="white").pack()
        price_entry = tk.Entry(content_inner_frame)
        price_entry.pack()

        tk.Label(content_inner_frame, text="Description", bg="#171d22", fg="white").pack()
        description_entry = tk.Entry(content_inner_frame)
        description_entry.pack()

        tk.Label(content_inner_frame, text="Category", bg="#171d22", fg="white").pack()
        category_combobox = ttk.Combobox(content_inner_frame, values=get_categories(), width=price_entry.cget("width") - 3)
        category_combobox.pack()

        tk.Label(content_inner_frame, text="Image", bg="#171d22", fg="white").pack()
        image_path = tk.StringVar()
        image_entry = tk.Entry(content_inner_frame, textvariable=image_path, state='readonly')
        image_entry.pack()

        def select_image():
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
            if file_path:
                image_path.set(file_path)
        
        select_image_button = tk.Button(content_inner_frame, text="Select Image", command=select_image)
        select_image_button.pack()

        tk.Label(content_inner_frame, text="Stock", bg="#171d22", fg="white").pack()
        stock_entry = tk.Entry(content_inner_frame)
        stock_entry.pack()

        tk.Label(content_inner_frame, text="Listed", bg="#171d22", fg="white").pack()
        listed_var = tk.StringVar(value="No")
        listed_combobox = ttk.Combobox(content_inner_frame, textvariable=listed_var, values=["Yes", "No"], width=price_entry.cget("width") - 3)
        listed_combobox.pack()

        error_label = tk.Label(content_inner_frame, text="", fg="red", bg="#171d22")
        error_label.pack()
        
        def handle_add_product():
            # Local Variables to take out from the text boxes and check for errors before adding to the database
            name = name_entry.get()
            price = price_entry.get()
            description = description_entry.get()
            category = category_combobox.get()
            image = image_path.get()
            stock = stock_entry.get()
            listed = listed_var.get()

            # Error messages for if the fields are empty to avoid null products in the database
            if not name or not price:
                error_label.config(text="All fields are required.")
                return
            
            # Error message for entering in characters not integers for the price
            try:
                price = float(price)
                stock = int(stock) if stock else None
            except ValueError:
                error_label.config(text="Price must be a number and stock must be an integer.")
                return
            
            category_id = get_category_id(category) if category else None
            if category_id is None:
                error_label.config(text="Invalid category.")
                return
            
            qr_code = f"{name}_{price}.png" # Sets a variable for qr_code to be the name of the product price of the product and .png for file type
            qr_code_util.generate_qr_code(f"{name}_{price}", qr_code) # Calls the generate qr code function from the qr_code_util.py file and uses the data then file location/name
            add_product(name, price, qr_code, listed, description, category_id, image, stock) # Calls the database.py with the function add_product with those parameters set in this function adding it to the database

            error_label.config(text="Product added successfully!", fg="green")

        tk.Button(content_inner_frame, text="Add Product", command=handle_add_product).pack(pady=10) # Button that calls this function to add the products to the database

    # TODO: Make it so that you can change if a product is listed or not from the main manage products screen along with inside the edit product screen for easier ux due to less clicks. #
    def show_manage_products_screen():
        """Display the manage products screen."""
        clear_frame(content_inner_frame)

        title_label = tk.Label(content_inner_frame, text="Manage Products", font=("Arial", 24, "bold"), bg="#171d22", fg="white")
        title_label.pack(pady=10)

        # Creates an entry box to function as a search box for the products and aligns it so it doesnt overlap the content label
        search_entry = tk.Frame(content_inner_frame, bg="#171d22")
        search_entry.pack(fill="x", pady=10)

        # Create a search entry box with placeholder text
        search_entry = tk.Entry(search_entry, width=50, fg="dark gray")
        search_entry.insert(0, "Search for products")
        search_entry.pack(pady=10)

        def on_focus_in(event):
            if search_entry.get() == "Search for products":
                search_entry.delete(0, tk.END)
                search_entry.config(fg="black")

        def on_focus_out(event):
            if search_entry.get() == "":
                search_entry.insert(0, "Search for products")
                search_entry.config(fg="dark gray")

        search_entry.bind("<FocusIn>", on_focus_in)
        search_entry.bind("<FocusOut>", on_focus_out)

        # Uses the filter products function for every key release (while typing for products) so it dynamically updates the products shown. (Avoids the need for a search button along with box to make it look tidy and function better)
        search_entry.bind("<KeyRelease>", lambda event: filter_products())

        def filter_products():
            search_query = search_entry.get().lower() # Sets the search query to the text from the search box but in full lowercase to avoid case sensitivity

            # Calls the get_products function without the limitation for only listed products and then filters the products based on the search query
            filtered_products = [
                product for product in get_products(listed_only=False)
                if search_query in product[1].lower() or search_query in str(product[2])
            ]
            display_products(filtered_products) # Adjusts the display_products function to display the only the filtered products vs the standard "products" which is all products

        # Create a canvas (which allows scrolling) and a scrollbar
        canvas = tk.Canvas(content_inner_frame, bg="#171d22")
        scrollbar = tk.Scrollbar(content_inner_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#171d22")

        # Checks that the canvas' scroll area is encompasing all the content inside when the frame size is changed through the bounding box check
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        # Configures the canvas to have the scrollable frame inside of it and the scrollbar to the right of the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Function to allow the mouse wheel to scroll the canvas
        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units") # Calculates the num of units to scroll based on the mouse wheel movement which is divided bt 120 to normalize the scroll speed then checks the scroll direction.
        
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        def display_products(products):
            
            clear_frame(scrollable_frame) # Itterates over all of the child widgets in the scrollable_frame and destroys them if they are not the search entry or the title label to avoid destroying the search box and title label
            
            # If there are no products available it will display a message saying so in red text otherwise display the products in a grid format (Can't use grid since i am stacking it ontop of a frame to make it dynamic)
            if not products:
                tk.Label(scrollable_frame, text="No products available.", fg="red", bg="#171d22").pack(pady=10)
            else:
                # Get the width of the scrollable_frame
                canvas.update_idletasks()
                content_width = canvas.winfo_width()
                product_frame_width = 290  # Set the width of each product frame (adjust as needed)
                padding = 5  # Set the padding between product frames

                # Calculate the number of columns that can fit in the available width
                num_columns = max(1, content_width // (product_frame_width + padding))

                # Initializes the variables
                row_frame = None
                col = 0
                row_count = 0

                for product in products:
                    # If the column is 0 it will create a new row frame to stack the products in a grid format
                    if col == 0:
                        row_frame = tk.Frame(scrollable_frame, bg="#171d22")
                        row_frame.pack(fill="x", pady=10)
                        row_count += 1

                    # Creates a frame for the product to be displayed in + creates the labels and content to fill out the product with information from the product tuple
                    product_frame = tk.Frame(row_frame, width=product_frame_width, padx=5, pady=5, bg="#171d22")
                    product_frame.pack(side="left", padx=5, pady=5)

                    tk.Label(product_frame, text=f"Name: {product[1]}", bg="#171d22", fg="white").pack()
                    tk.Label(product_frame, text=f"Price: £{product[2]:.2f}", bg="#171d22", fg="white").pack()

                    qr_code_image = tk.PhotoImage(file=product[3]) # Takes the qr code image from the product tuple and sets it to a local variable to be used in the label
                    tk.Label(product_frame, image=qr_code_image, bg="#171d22").pack()
                    product_frame.image = qr_code_image  # stores the image inside of product_frame to avoid garbage collection since it was previously clearing

                    # Creates the functions and locaates the two buttons for editing / deleting products
                    def edit_product(product_id=product[0]):
                        show_edit_product_screen(product_id)

                    def delete_product(product_id=product[0]):
                        db_delete_product(product_id)
                        show_manage_products_screen()
                        
                    tk.Button(product_frame, text="Edit", command=edit_product).pack(side="left")
                    tk.Button(product_frame, text="Delete", command=delete_product).pack(side="right")
                    
                    col += 1
                    if col >= num_columns:
                        col = 0
                
                # Enable or disable scrolling based on the number of rows
                if row_count > 1:
                    canvas.bind_all("<MouseWheel>", on_mouse_wheel)
                    scrollbar.pack(side="right", fill="y")
                else:
                    canvas.unbind_all("<MouseWheel>")
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
        
        tk.Label(content_inner_frame, text="Edit Product", font=("Arial", 18), bg="#171d22", fg="white").pack(pady=10)
        product = get_product_by_id(product_id)

        # Creates the entry boxes for the name and price of the product and sets the default values to the current values of the product from the database
        tk.Label(content_inner_frame, text="Name", bg="#171d22", fg="white").pack()
        name_entry = tk.Entry(content_inner_frame)
        name_entry.insert(0, product[1])
        name_entry.pack()

        tk.Label(content_inner_frame, text="Price", bg="#171d22", fg="white").pack()
        price_entry = tk.Entry(content_inner_frame)
        price_entry.insert(0, product[2])
        price_entry.pack()

        tk.Label(content_inner_frame, text="Description", bg="#171d22", fg="white").pack()
        description_entry = tk.Entry(content_inner_frame)
        description_entry.insert(0, product[5])
        description_entry.pack()

        tk.Label(content_inner_frame, text="Category", bg="#171d22", fg="white").pack()
        category_combobox = ttk.Combobox(content_inner_frame, values=get_categories(), width=price_entry.cget("width") - 3)
        category_combobox.set(get_category_name(product[6]))
        category_combobox.pack()

        tk.Label(content_inner_frame, text="Image", bg="#171d22", fg="white").pack()
        image_path = tk.StringVar(value=product[7])
        image_entry = tk.Entry(content_inner_frame, textvariable=image_path, state='readonly')
        image_entry.pack()

        def select_image():
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
            if file_path:
                image_path.set(file_path)

        select_image_button = tk.Button(content_inner_frame, text="Select Image", command=select_image)
        select_image_button.pack()

        tk.Label(content_inner_frame, text="Stock", bg="#171d22", fg="white").pack()
        stock_entry = tk.Entry(content_inner_frame)
        stock_entry.insert(0, product[8])
        stock_entry.pack()

        tk.Label(content_inner_frame, text="Listed", bg="#171d22", fg="white").pack()
        listed_var = tk.StringVar(value="Yes" if product[4] else "No")
        listed_combobox = ttk.Combobox(content_inner_frame, textvariable=listed_var, values=["Yes", "No"], width=price_entry.cget("width") - 3)
        listed_combobox.pack()

        # Creates the empty error label to be used for error messages if the user tries to submit the form with errors
        error_label = tk.Label(content_inner_frame, text="", fg="red", bg="#171d22")
        error_label.pack()

        # Performs validation checks to ensure the product name and price are not empty and the price is a number before updating the product in the database
        def save_edit_product():
            name = name_entry.get()
            price = price_entry.get()
            description = description_entry.get()
            category = category_combobox.get()
            image = image_path.get()
            stock = stock_entry.get()
            listed = 1 if listed_var.get() == "Yes" else 0

            if not name or not price:
                error_label.config(text="All fields are required.")
                return
            try:
                price = float(price)
                stock = int(stock) if stock else None
            except ValueError:
                error_label.config(text="Price must be a number and stock must be an integer.")
                return
            
            category_id = get_category_id(category) if category else None
            if category_id is None:
                error_label.config(text="Invalid category.")
                return
            
            # Retrieve the old QR code file name 
            old_qr_code = product[3]

            # Check if the name or price has changed
            if name != product[1] or price != product[2]:
                # If validation passes then it generates a new qr code and updates the product in the database with the new product details
                qr_code = f"{name}_{price}.png"
                qr_code_util.generate_qr_code(f"{name}_{price}", qr_code)

                # Delete the old QR code file if it still exists
                if old_qr_code and os.path.exists(old_qr_code):
                    os.remove(old_qr_code)
            else:
                # If name and price have not changed, use the old QR code
                qr_code = old_qr_code

            update_product(product_id, name, price, qr_code, description, category_id, image, stock)
            list_product(product_id, listed)

            error_label.config(text="Product updated successfully!", fg="green")
            show_manage_products_screen()
        
        # Cancels the current edits from being saved by destroying all widgets in the content_inner_frame and showing the mangae users screen INSTEAD of updating any products in the database
        def cancel_edit_product():
            clear_frame(content_inner_frame)

            show_manage_products_screen()

        tk.Button(content_inner_frame, text="Save", command=save_edit_product).pack(pady=10)
        tk.Button(content_inner_frame, text="Cancel", command=cancel_edit_product).pack(pady=10)

    def show_manage_categories_screen():
        """Display the manage categories screen."""
        clear_frame(content_inner_frame)

        tk.Label(content_inner_frame, text="Manage Categories", font=("Arial", 24, "bold"), bg="#171d22", fg="white").pack(pady=10)

        tk.Label(content_inner_frame, text="Category Name", bg="#171d22", fg="white").pack(pady=5)
        category_entry = tk.Entry(content_inner_frame)
        category_entry.pack(pady=5)

        error_label = tk.Label(content_inner_frame, text="", fg="red", bg="#171d22")
        error_label.pack(pady=5)

        def handle_add_category():
            name = category_entry.get()
            if not name:
                error_label.config(text="Category name is required.")
                return

            add_category(name)
            error_label.config(text="Category added successfully!", fg="green")
            category_entry.delete(0, tk.END)
            display_categories()

        add_button = tk.Button(content_inner_frame, text="Add Category", command=handle_add_category)
        add_button.pack(pady=5)

        category_list_frame = tk.Frame(content_inner_frame, bg="#171d22")
        category_list_frame.pack(fill="both", expand=True,)

        def handle_edit_category(category_id, old_name):
            new_name = category_entry.get()
            if not new_name:
                error_label.config(text="Category name is required.")
                return

            if new_name == old_name:
                error_label.config(text="No changes made.")
                return

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Categories SET name = ? WHERE id = ?", (new_name, category_id))
            conn.commit()
            conn.close()
            error_label.config(text="Category updated successfully!", fg="green")
            category_entry.delete(0, tk.END)
            display_categories()

        def handle_delete_category(category_id):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Categories WHERE id = ?", (category_id,))
            conn.commit()
            conn.close()
            error_label.config(text="Category deleted successfully!", fg="green")
            display_categories()

        def display_categories():
            clear_frame(category_list_frame)

            categories = get_categories()
            for category in categories:
                category_frame = tk.Frame(category_list_frame, bg="#171d22")
                category_frame.pack(fill="x", pady=5)

                tk.Label(category_frame, text=category, bg="#171d22", fg="white").pack(side="left", padx=10)

                edit_button = tk.Button(category_frame, text="Edit", command=lambda c=category: handle_edit_category(get_category_id(c), c))
                edit_button.pack(side="right", padx=5)

                delete_button = tk.Button(category_frame, text="Delete", command=lambda c=category: handle_delete_category(get_category_id(c)))
                delete_button.pack(side="right", padx=5)

        # Call display_categories to show the categories initially
        display_categories()

    # TODO: Have the Manage Users screen use the same change password option for other user management OR allow users to perform this action themselves. (unsure how to implement since we are not gathering contact information for the users in the prototype) #
    # TODO: Make it so that the password is subject to the same requirements as the register screen has #
    # Change password screen that is called for when an admin account is logged into for the first time. 
    def switch_to_change_password(username):
        """Prompt admin to change their password."""
        window.geometry("400x300")
        clear_frame(main_frame)

        tk.Label(main_frame, text="Change Password", font=("Arial", 18)).pack(pady=10)

        tk.Label(main_frame, text="New Password").pack()
        new_password_entry = tk.Entry(main_frame, show="*")
        new_password_entry.pack()

        tk.Label(main_frame, text="Confirm New Password").pack()
        confirm_password_entry = tk.Entry(main_frame, show="*")
        confirm_password_entry.pack()

        def change_password():
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()

            is_valid, validation_message = validate_password_match(new_password, confirm_password)
            if not is_valid:
                display_error(validation_message)
                return

            is_valid, validation_message = validate_password(username, new_password)
            if not is_valid:
                display_error(validation_message)
                return
            
            # Update the password in db if the validation passes.
            conn = get_connection()
            cursor = conn.cursor()
            from auth import hash_password
            salt, hashed_password = hash_password(new_password)
            cursor.execute("""
                UPDATE Users SET password = ?, salt = ?, password_changed = 1 
                WHERE username = ?
            """, (hashed_password, salt, username))
            conn.commit()
            conn.close()
            tk.Label(main_frame, text="Password updated successfully!", fg="green").pack()
            switch_to_admin_panel()

        tk.Button(main_frame, text="Change Password", command=change_password).pack(pady=10)
        add_logout_button()
    
    # TODO: Implement the qr code scanning functionality for the standard user and admin for finding a product quickly for admin box management or quick purchases #
    # Allows the user to scan a qr code and navigate to the product page for the product that the qr code is linked to. 
    def scan_qr_code():
        """Scan a QR code using the webcam and navigate to the product page."""
        data = qr_code_util.scan_qr_code()
        if data:
            product_id = int(data)
            show_product_page(product_id)

    def show_product_page(product_id):
        """Display the product page for the given product ID."""
        clear_frame(main_frame)
        product = get_product_by_id(product_id)
        if product:
            tk.Label(main_frame, text=f"Name: {product[1]}", font=("Arial", 18)).pack(pady=10)
            tk.Label(main_frame, text=f"Price: £{product[2]:.2f}").pack(pady=5)
            qr_code_image = tk.PhotoImage(file=product[3])
            tk.Label(main_frame, image=qr_code_image).pack(pady=5)
            main_frame.image = qr_code_image  # Keep a reference to avoid garbage collection
        else:
            display_error("Product not found!")# If product cannot be found then it will return an error message. Useful for if a user scans an old qr code if they went into store at a later date past saving it.

    window.mainloop() # Actually starts the application and allows the user to interact with the GUI

# TODO: Explain functionality reason behind this on ONE of the files (pref main.py) #
if __name__ == "__main__":
    start_app()