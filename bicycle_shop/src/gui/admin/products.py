import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from src.database import (
    get_products, get_product_by_id, get_category_name, list_product,
    update_product, delete_product as db_delete_product, get_categories,
    get_category_id, add_product
)
from src.utils import (
    display_error, display_success, clear_frame, get_style_config,
    create_scrollable_frame, setup_product_grid, create_product_management_frame,
    log_action, resize_product_image, resize_qr_code, setup_search_widget,
    validate_product_fields
)

def add_no_category_option(categories):
    """Add 'No Category' option to category list.
    
    Args:
        categories: List of category names
        
    Returns:
        List with "No Category" as first option followed by categories
    """
    return ["No Category"] + categories

def show_add_product_screen(global_state):
    """Display the add product screen.
    
    Creates interface for adding new products with:
    - Name entry
    - Price entry
    - Description text box
    - Image upload/preview
    - Stock entry
    - Category selection
    - Listed status toggle
    
    Args:
        global_state: Application state containing:
            - window: Main window instance
            - content_inner_frame: Main content frame
            - current_admin_id: Current admin's ID
            
    Note:
        Images are resized responsively based on window size
        Validates all required fields before saving
    """
    global_state['current_screen'] = show_add_product_screen
    window = global_state['window']
    content_inner_frame = global_state['content_inner_frame']
    current_admin_id = global_state['current_admin_id']

    clear_frame(content_inner_frame)
    styles = get_style_config()['add_product']

    window.unbind("<Configure>")
    window.unbind("<Button-1>")
    content_inner_frame.unbind("<Configure>")

    # Add title label at the top
    title_label = tk.Label(content_inner_frame, text="Add New Product", **styles['title'])
    title_label.pack(pady=(20, 5))

    # Create outer container
    container_frame = tk.Frame(content_inner_frame, **styles['frame'])
    container_frame.pack(fill="both", expand=True)

    # Create scrollable frame setup
    wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_frame(container_frame)
    wrapper.pack(fill="both", expand=True, padx=10, pady=(0, 20))

    # Create main content frame with padding
    content_frame = tk.Frame(scrollable_frame, **styles['frame'])
    content_frame.pack(fill="both", expand=True, padx=15, pady=15)

    # Move name entry to top of content frame
    name_container = tk.Frame(content_frame, **styles['frame'])
    name_container.pack(fill="x", pady=(0, 5))

    # Create inner frame to help with centering
    name_inner_container = tk.Frame(name_container, **styles['frame'])
    name_inner_container.pack(expand=True)

    tk.Label(name_inner_container, text="Product Name:", **styles['labels']).pack(side="left", pady=(0, 5))
    name_entry = tk.Entry(name_inner_container, width=30, **styles['entries'])
    name_entry.pack(side="left")

    # Details container frame
    details_frame = tk.Frame(content_frame, **styles['frame'])
    details_frame.pack(fill="both", expand=True, pady=2)

    # Left side - Product image
    left_frame = tk.Frame(details_frame, **styles['frame'])
    left_frame.pack(side="left", fill="both", expand=True, padx=(5, 15))

    # Right side
    right_frame = tk.Frame(details_frame, width=300, **styles['frame'])
    right_frame.pack(side="right", fill="y", padx=(0, 5))
    right_frame.pack_propagate(False)

    # Inner right frame with padding
    inner_right_frame = tk.Frame(right_frame, **styles['frame'])
    inner_right_frame.pack(fill="both", expand=True, padx=10, pady=2)

    # Price frame with label
    price_frame = tk.Frame(inner_right_frame, **styles['frame'])
    price_frame.pack(fill="x", pady=5)
    tk.Label(price_frame, text="Price (£):", **styles['labels']).pack(side="left", padx=(0, 5))
    price_entry = tk.Entry(price_frame, width=12, **styles['entries'])
    price_entry.pack(side="left")

    # Description section
    desc_frame = tk.Frame(inner_right_frame, **styles['frame'])
    desc_frame.pack(fill="x", pady=5)
    tk.Label(desc_frame, text="Description:", **styles['labels']).pack(anchor="w")
    description_text = tk.Text(desc_frame, height=4, width=30, wrap="word", **styles['entries'])
    description_text.pack(pady=5)

    # Stock entry with label
    stock_frame = tk.Frame(inner_right_frame, **styles['frame'])
    stock_frame.pack(fill="x", pady=5)
    tk.Label(stock_frame, text="Stock:", **styles['labels']).pack(side="left", padx=(0, 5))
    stock_entry = tk.Entry(stock_frame, width=10, **styles['entries'])
    stock_entry.pack(side="left")

    def select_image():
        """Handle image selection dialog and update preview."""
        # Open file dialog to select an image file, only allow .jpg, .jpeg, .png extensions to be seen
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            image_path.set(file_path)
            resize_content()

    def clear_image():
        """Clear selected image and show placeholder."""
        image_path.set("")
        resize_content()

    # Add placeholder for image
    image_path = tk.StringVar()
    image_frame = tk.Frame(left_frame, **styles['frame'])
    image_frame.pack(fill="both", expand=True, pady=(0, 5))

    # Placeholder text for image replacement when no image is set
    placeholder_text = "No Image Selected\n\nClick 'Select Image'\nto add a product image"
    placeholder_label = tk.Label(image_frame, text=placeholder_text, **styles['placeholder'])
    placeholder_label.pack(expand=True, fill="both", pady=10)

    # Create button container frame
    button_container = tk.Frame(left_frame, **styles['frame'])
    button_container.pack()

    # Add select image button
    select_image_button = tk.Button(button_container, text="Select Image", command=select_image, **styles['buttons'])
    select_image_button.pack(side="left", padx=2)

    # Add remove image button
    button_style = dict(styles['buttons']) # Create a copy so it doesnt affect other buttons
    button_style['fg'] = "red" # Override fg color for button to be red.
    remove_image_button = tk.Button(button_container, text="X", command=lambda: clear_image(), width=2, **button_style)
    remove_image_button.pack(side="left", padx=2)

    # Bottom section
    bottom_frame = tk.Frame(content_frame, **styles['frame'])
    bottom_frame.pack(fill="x", expand=True, pady=2)

    controls_container = tk.Frame(bottom_frame, **styles['frame'])
    controls_container.pack(expand=True)

    # Category selection
    category_container = tk.Frame(controls_container, **styles['frame'])
    category_container.pack(side="left", padx=20)
    
    # Label for category selection
    tk.Label(category_container, text="Category:", **styles['labels']).pack()
    categories = get_categories()
    
    # Create combobox for category selection with "No Category" as default
    category_combobox = ttk.Combobox(
        category_container, 
        values=add_no_category_option(categories), 
        style='Add.TCombobox',
        width=25
    )
    category_combobox.set("No Category")
    category_combobox.pack(pady=2)

    # Listed status
    listed_container = tk.Frame(controls_container, **styles['frame'])
    listed_container.pack(side="left", padx=20)
    tk.Label(listed_container, text="Listed:", **styles['labels']).pack()
    listed_var = tk.StringVar(value="No")
    listed_combobox = ttk.Combobox(
        listed_container, 
        textvariable=listed_var, 
        values=["Yes", "No"], # Allows only yes or no selections for listing since checkbox is broken
        style='Add.TCombobox',
        width=25
    )
    listed_combobox.pack(pady=2)

    resize_timer = None

    def debounced_resize(event=None):
        """Debounced version of resize_content to prevent excessive updates."""
        nonlocal resize_timer  # Use nonlocal to modify the outer scope variable
        if resize_timer is not None:
            window.after_cancel(resize_timer)  # Cancel any existing timer
        resize_timer = window.after(150, lambda: resize_content(event))  # Set a new timer to call resize_content after 150ms

    def resize_content(event=None):
        """Handle responsive resizing of images based on window size.
        
        Calculates appropriate image dimensions based on:
        - Window width/height
        - Minimum/maximum size constraints
        - Screen resolution breakpoints
        
        Updates image preview maintaining aspect ratio
        """
        if not left_frame.winfo_exists():
            return

        image_to_resize = image_path.get()

        # Get window dimensions first
        window_width = window.winfo_width()
        window_height = window.winfo_height()
            
        # Force geometry updates
        window.update_idletasks()
        
        try:
            left_height = left_frame.winfo_reqheight()
            right_height = right_frame.winfo_reqheight()
        except tk.TclError:
            return

        # Set minimum heights and get current heights
        MIN_RIGHT_HEIGHT = 300  # Slightly smaller than edit screen
        MIN_QR_PADDING = 5
        
        left_height = left_frame.winfo_reqheight()
        right_height = right_frame.winfo_reqheight()
        
        # Enforce minimum right frame height
        final_right_height = max(MIN_RIGHT_HEIGHT, right_height)
        right_frame.configure(height=final_right_height)
        inner_right_frame.configure(height=final_right_height)
        
        # Calculate padding based on available space
        if left_height > right_height:
            bottom_padding = max(MIN_QR_PADDING, (left_height - right_height) // 2)
        else:
            bottom_padding = MIN_QR_PADDING
        
        # Calculate responsive dimensions based on window size (very janky, need to build better solution but works in a pinch, mostly for testing)
        if window_width <= 1280:
            width_factor = 0.3
            height_factor = 0.3
            min_width_factor = 0.2
            min_height_factor = 0.2
        elif window_width <= 1366:
            width_factor = 0.35
            height_factor = 0.35
            min_width_factor = 0.25
            min_height_factor = 0.25
        elif window_width <= 1600:
            width_factor = 0.4
            height_factor = 0.4
            min_width_factor = 0.3
            min_height_factor = 0.3
        elif window_width <= 1920:
            width_factor = 0.45
            height_factor = 0.45
            min_width_factor = 0.35
            min_height_factor = 0.35
        elif window_width <= 2560:
            width_factor = 0.5
            height_factor = 0.5
            min_width_factor = 0.4
            min_height_factor = 0.4
        else:
            width_factor = 0.6
            height_factor = 0.6
            min_width_factor = 0.5
            min_height_factor = 0.5

        # Calculate image dimensions
        max_img_width = min(int(window_width * width_factor), 1800)
        max_img_height = min(int(window_height * height_factor), 1600)
        min_img_width = max(int(window_width * min_width_factor), 75)
        min_img_height = max(int(window_height * min_height_factor), 50)
        
        if not image_to_resize:
            # Show placeholder with fixed minimum size
            for widget in image_frame.winfo_children():
                widget.destroy()
            placeholder_frame = tk.Frame(image_frame, width=min_img_width, height=min_img_height, **styles['frame'])
            placeholder_frame.pack(expand=True, fill="both", pady=10)
            placeholder_frame.pack_propagate(False)
            tk.Label(placeholder_frame, text=placeholder_text, **styles['placeholder']).pack(expand=True)
            return

        # Resize product image with fixed constraints
        resized_image = resize_product_image(
            image_to_resize,
            max_width=max_img_width,
            max_height=max_img_height,
            min_width=min_img_width,
            min_height=min_img_height
        )

        if resized_image:
            for widget in image_frame.winfo_children():
                widget.destroy()
            image_label = tk.Label(image_frame, image=resized_image)
            image_label.image = resized_image
            image_label.pack()

    # Add bottom frame for buttons and messages
    bottom_frame = tk.Frame(content_frame, **styles['frame'])
    bottom_frame.pack(fill="x", expand=True)

    # Message label
    message_label = tk.Label(bottom_frame, text="", **styles['message'])
    message_label.pack()

    # Action buttons
    button_frame = tk.Frame(bottom_frame, **styles['frame'])
    button_frame.pack()
    
    tk.Button(
        button_frame, 
        text="Add Product", 
        command=lambda: handle_add_product(),
        **styles['buttons']
    ).pack(side="left", padx=5)
    
    tk.Button(
        button_frame, 
        text="Cancel", 
        command=lambda: show_manage_products_screen(global_state),
        **styles['buttons']
    ).pack(side="left", padx=5)

    def handle_add_product():
        """Handle adding a new product with validation.
        
        Validates:
        - Required fields are filled
        - Price is valid number
        - Stock is valid integer
        - Category is selected if product is listed
        
        Creates product and logs action on success
        Shows error message on failure
        """
        name = name_entry.get().strip()
        price = price_entry.get().strip()
        description = description_text.get("1.0", "end-1c").strip()
        category = category_combobox.get()
        image = image_path.get()
        stock = stock_entry.get().strip()
        listed = 1 if listed_var.get() == "Yes" else 0

        is_valid, message = validate_product_fields(
            name, price, stock, listed, category, image, description
        )
        
        if not is_valid:
            display_error(message_label, message)
            return

        # Convert values after validation
        price = float(price)
        stock = int(stock) if stock else 0
        category_id = get_category_id(category) if category != "No Category" else None

        # Add product
        success, product_id, message = add_product(
            name, price, None, listed, description, 
            category_id, image, stock
        )

        if success:
            display_success(message_label, "Product added successfully!")
            log_action(
                'CREATE_PRODUCT', 
                is_admin=True, 
                admin_id=current_admin_id,
                target_type='product', 
                target_id=product_id,
                details=f"Created product: {name} (Price: £{price}, Stock: {stock}, Listed: {listed})"
            )
            show_manage_products_screen(global_state)
        else:
            display_error(message_label, message)
            log_action(
                'CREATE_PRODUCT', 
                is_admin=True, 
                admin_id=current_admin_id,
                target_type='product', 
                target_id=None,
                details=f"Failed to create product: {message}", 
                status='failed'
            )

    # Bind resize event
    window.bind("<Configure>", debounced_resize)
    window.update_idletasks()

    # Enable mouse wheel scrolling
    bind_wheel()

def show_manage_products_screen(global_state):
    """Display the manage products screen.
    
    Shows grid of all products grouped by category with:
    - Search functionality
    - Edit/delete actions per product
    - Responsive grid layout
    - Scrolling for overflow
    
    Args:
        global_state: Application state containing window/frame refs
    """
    global_state['current_screen'] = show_manage_products_screen
    window = global_state['window']
    content_inner_frame = global_state['content_inner_frame']
    current_admin_id = global_state['current_admin_id']

    clear_frame(content_inner_frame)
    styles = get_style_config()['manage_products']

    # # TEMP DEBUG COLOR
    # content_inner_frame.configure(bg='pink')

    window.unbind("<Configure>")
    window.unbind("<Button-1>")
    
    title_label = tk.Label(content_inner_frame, text="Manage Products", **styles['title'])
    title_label.pack(pady=(20, 5))

    # Create container frame for search that will properly expand/contract
    search_container = tk.Frame(content_inner_frame, bg=styles['frame']['bg'])
    search_container.pack(fill="x", pady=(5, 10))

    # Create search widget with dynamic width
    search_frame, search_entry, disable_search, enable_search = setup_search_widget(search_container)
    search_frame.pack(expand=True)
    search_entry.pack(fill="x", expand=True, padx=100)

    # Add message label for feedback
    message_label = tk.Label(content_inner_frame, text="", **styles['message'])
    message_label.pack(pady=5)

    # Bind the search entry to the filter function
    search_entry.bind("<KeyRelease>", lambda event: filter_products())

    def remove_focus(event):
        """Remove focus from search when clicking elsewhere."""
        if event.widget != search_entry:
            window.focus_set()
            return "break"

    def filter_products():
        """Filter products based on search input.
        
        Filters by product name or price matching search text
        Updates display with filtered results
        """
        search_query = search_entry.get().lower()
        filtered_products = [
            product for product in get_products(listed_only=False)
            if search_query in product[1].lower() or search_query in str(product[2])
        ]
        display_products(filtered_products)

    # Create scrollable frame setup
    wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_frame(content_inner_frame)
    wrapper.pack(fill="both", expand=True, padx=10, pady=(10, 20)) # Match bottom padding to the other screens, categories, discounts and users.
    canvas.pack(side="left", fill="both", expand=True)

    # Ensure scrollable_frame uses full width
    scrollable_frame.pack(fill="both", expand=True)

    # # TEMP: Add more debug colors
    # wrapper.configure(bg='yellow')        # Wrapper frame
    # canvas.configure(bg='lightblue')      # Canvas
    # scrollable_frame.configure(bg='lightgreen')  # Content frame

    # Bind click handlers for focus management
    main_frame = content_inner_frame.master.master  # Get reference to main_frame
    main_frame.bind('<Button-1>', remove_focus)
    content_frame = content_inner_frame.master  # Get reference to content_frame
    content_frame.bind('<Button-1>', remove_focus)
    content_inner_frame.bind('<Button-1>', remove_focus)
    wrapper.bind('<Button-1>', remove_focus)
    canvas.bind('<Button-1>', remove_focus)
    scrollable_frame.bind('<Button-1>', remove_focus)

    def handle_delete_product(product_id):
        """Handle product deletion with confirmation.
        
        Shows confirmation dialog
        Deletes product and logs action on confirmation
        Updates display after successful deletion
        """
        product = get_product_by_id(product_id)
        if product:
            product_name = product[1]
            if messagebox.askyesno("Confirm Delete", 
                                f"Are you sure you want to delete the product '{product_name}'?"):
                success, msg = db_delete_product(product_id)
                if success:
                    display_success(message_label, msg)
                    log_action('DELETE_PRODUCT', is_admin=True, admin_id=current_admin_id,
                            target_type='product', target_id=product_id,
                            details=f"Deleted product: {product_name}")
                    display_products(get_products(listed_only=False))
                else:
                    display_error(message_label, msg)
                    log_action('DELETE_PRODUCT', is_admin=True, admin_id=current_admin_id,
                            target_type='product', target_id=product_id,
                            details=f"Failed to delete product: {msg}", status='failed')

    def display_products(products):
        """Display products grouped by category in grid layout.
        
        Groups products by category
        Creates category headers with separators
        Displays products in responsive grid
        Enables scrolling if content overflows
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
        uncategorized_products = []
        
        for product in products:
            if product[6]:  # If product has a category
                category_name = get_category_name(product[6])
                if category_name not in categorized_products:
                    categorized_products[category_name] = []
                categorized_products[category_name].append(product)
            else:
                uncategorized_products.append(product)

        row_count = 0

        # First display uncategorized products under "Unlisted" section
        if uncategorized_products:
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
            
            separator = ttk.Separator(category_frame, orient="horizontal")
            separator.pack(side="left", fill="x", expand=True, padx=10)

            col = 0
            row_frame = None
            
            for product in uncategorized_products:
                if col % num_columns == 0:
                    row_frame = tk.Frame(scrollable_frame, **styles['frame'])
                    row_frame.pack(fill="x", pady=5)
                    row_count += 1

                create_product_management_frame(
                    row_frame, 
                    product,
                    290,  # product_width
                    lambda p_id=product[0]: show_edit_product_screen(global_state, p_id),
                    lambda p=product: handle_delete_product(p[0])
                )
                col += 1

        # Then display categorized products
        for category_name, category_products in categorized_products.items():
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
            
            separator = ttk.Separator(category_frame, orient="horizontal")
            separator.pack(side="left", fill="x", expand=True, padx=10)

            col = 0
            row_frame = None
            
            for product in category_products:
                if col % num_columns == 0:
                    row_frame = tk.Frame(scrollable_frame, **styles['frame'])
                    row_frame.pack(fill="x", pady=5)
                    row_count += 1

                create_product_management_frame(
                    row_frame, 
                    product,
                    290,  # product_width
                    lambda p_id=product[0]: show_edit_product_screen(global_state, p_id),  # Pass product ID directly
                    lambda p_id=product[0]: handle_delete_product(p_id)
                )
                col += 1

        # Enable scrolling if needed
        if row_count > 1:
            bind_wheel()
            scrollbar.pack(side="right", fill="y")
        else:
            scrollbar.pack_forget()

        # Update scroll region
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Bind the resize event to update product display
    content_inner_frame.bind("<Configure>", lambda event: display_products(get_products(listed_only=False)))

    # Initial display
    display_products(get_products(listed_only=False))

# Lots of copy paste between add product and show edit product screens for time saving
def show_edit_product_screen(global_state, product_id):
    """Display the edit product screen with preview layout.
    
    Shows form to edit existing product:
    - Current values pre-filled
    - Image/QR preview
    - Responsive layout
    - Field validation
    
    Args:
        global_state: Application state dict
        product_id: ID of product to edit
    """
    window = global_state['window']
    content_inner_frame = global_state['content_inner_frame']
    current_admin_id = global_state['current_admin_id']

    clear_frame(content_inner_frame)
    styles = get_style_config()['edit_product']
    
    window.unbind("<Configure>")
    window.unbind("<Button-1>")
    content_inner_frame.unbind("<Configure>")


    product = get_product_by_id(product_id)
    if product:
        # Create title container frame to hold title
        title_container = tk.Frame(content_inner_frame, **styles['frame'])
        title_container.pack(fill="x", pady=(20, 5))

        name_entry = tk.Entry(title_container, **styles['entries'])
        name_entry.insert(0, product[1])
        name_entry.pack(side="left", expand=True)

        # Create outer container
        container_frame = tk.Frame(content_inner_frame, **styles['frame'])
        container_frame.pack(fill="both", expand=True)

        # Create scrollable frame setup
        wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_frame(container_frame)
        wrapper.pack(fill="both", expand=True, padx=10, pady=(0, 20))

        # Create main content frame
        content_frame = tk.Frame(scrollable_frame, **styles['frame'])
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Details container frame
        details_frame = tk.Frame(content_frame, **styles['frame'])
        details_frame.pack(fill="both", expand=True, pady=10)

        # Left side - Product image
        left_frame = tk.Frame(details_frame, **styles['frame'])
        left_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))

        # Right side setup with fixed width and minimum height
        right_frame = tk.Frame(details_frame, width=250, **styles['frame'])
        right_frame.pack(side="right", fill="both", padx=(10, 0))
        right_frame.pack_propagate(False)

        # Create inner frame with minimum height
        inner_right_frame = tk.Frame(right_frame, **styles['frame'])
        inner_right_frame.pack(fill="both", expand=True, padx=10, pady=5)

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

        # Stock entry with container for centering
        stock_frame = tk.Frame(inner_right_frame, **styles['frame'])
        stock_frame.pack(fill="x", pady=(0, 5))
        stock_container = tk.Frame(stock_frame, **styles['frame'])
        stock_container.pack(expand=True)
        tk.Label(stock_container, text="Stock:", **styles['labels']).pack(side="left")
        stock_entry = tk.Entry(stock_container, width=10, **styles['entries'])
        stock_entry.insert(0, product[8])
        stock_entry.pack(side="left", padx=5)

        # Bottom frame spanning full width
        bottom_frame = tk.Frame(content_frame, **styles['frame'])
        bottom_frame.pack(fill="x", expand=True)

        # Category and Listed status (side by side)
        settings_frame = tk.Frame(bottom_frame, **styles['frame'])
        settings_frame.pack(expand=True, pady=(2, 2))

        # Container for horizontal layout
        controls_container = tk.Frame(settings_frame, **styles['frame'])
        controls_container.pack(expand=True)

        # Add combobox style configuration
        combo_style = ttk.Style()
        combo_style.configure('Edit.TCombobox',
            background=styles['combobox']['bg'],
            fieldbackground=styles['combobox']['fieldbackground'],
            foreground=styles['combobox']['fg'],
            selectbackground=styles['combobox']['selectbackground'],
            selectforeground=styles['combobox']['selectforeground']
        )

        # Category on the left
        category_container = tk.Frame(controls_container, **styles['frame'])
        category_container.pack(side="left", padx=10)
        tk.Label(category_container, text="Category:", **styles['labels']).pack()
        categories = get_categories()
        category_combobox = ttk.Combobox(
            category_container, 
            values=add_no_category_option(categories), 
            style='Edit.TCombobox', 
            width=20
        )
        # Set current category or "No Category" if none
        if get_category_name(product[6]):
            category_combobox.set(get_category_name(product[6]))
        else:
            category_combobox.set("No Category")
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
        tk.Button(button_frame, text="Cancel", 
                command=lambda: show_manage_products_screen(global_state), 
                **styles['buttons']).pack(side="left", padx=5)

        def select_image():
            """Handle selecting new product image."""
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
            if file_path:
                image_path.set(file_path)
                resize_content()

        def clear_image():
            """Remove current product image."""
            image_path.set("")
            resize_content()

        # Modify existing image handling:
        image_path = tk.StringVar(value=product[7])
        image_frame = tk.Frame(left_frame, **styles['frame'])
        image_frame.pack(pady=(0, 5))

        # Create button container frame
        button_container = tk.Frame(left_frame, **styles['frame'])
        button_container.pack()

        # Add select image button
        select_image_button = tk.Button(button_container, text="Change Image", command=select_image, **styles['buttons'])
        select_image_button.pack(side="left", padx=2)

        # Add remove image button
        button_style = dict(styles['buttons']) # Create a copy so it doesnt affect other buttons
        button_style['fg'] = "red" # Override fg color for button to be red.
        remove_image_button = tk.Button(button_container, text="X", command=lambda: clear_image(), width=2, **button_style)
        remove_image_button.pack(side="left", padx=2)

        resize_timer = None

        def debounced_resize(event=None):
            """Debounced resize handler."""
            nonlocal resize_timer
            if resize_timer is not None:
                window.after_cancel(resize_timer)
            resize_timer = window.after(150, lambda: resize_content(event))

        def resize_content(event=None):
            """Handle responsive resizing of image/QR previews.
            
            Resizes based on window dimensions
            Maintains minimum/maximum size constraints
            Updates both product image and QR code
            """
            if not left_frame.winfo_exists():
                return
            
            # Get window dimensions first
            window_width = window.winfo_width()
            window_height = window.winfo_height()
                
            # Force geometry updates
            window.update_idletasks()
            
            try:
                left_height = left_frame.winfo_reqheight()
                right_height = right_frame.winfo_reqheight()
            except tk.TclError:
                return

            # Set minimum heights and get current heights
            MIN_RIGHT_HEIGHT = 330
            MIN_QR_PADDING = 5
            
            left_height = left_frame.winfo_reqheight()
            right_height = right_frame.winfo_reqheight()
            
            # Enforce minimum right frame height
            final_right_height = max(MIN_RIGHT_HEIGHT, right_height)
            right_frame.configure(height=final_right_height)
            inner_right_frame.configure(height=final_right_height)
            
            # Calculate QR padding based on available space
            if left_height > right_height:
                bottom_padding = max(MIN_QR_PADDING, (left_height - right_height) // 2)
            else:
                bottom_padding = MIN_QR_PADDING
            
            # Calculate responsive dimensions based on window size
            if window_width <= 1280:
                width_factor = 0.3
                height_factor = 0.3
                min_width_factor = 0.2
                min_height_factor = 0.2
                qr_factor = 0.1
                qr_max_size = 150
                qr_min_size = 100
            elif window_width <= 1366:
                width_factor = 0.35
                height_factor = 0.35
                min_width_factor = 0.25
                min_height_factor = 0.25
                qr_factor = 0.12
                qr_max_size = 200
                qr_min_size = 120
            elif window_width <= 1600:
                width_factor = 0.4
                height_factor = 0.4
                min_width_factor = 0.3
                min_height_factor = 0.3
                qr_factor = 0.15
                qr_max_size = 250
                qr_min_size = 150
            elif window_width <= 1920:
                width_factor = 0.45
                height_factor = 0.45
                min_width_factor = 0.35
                min_height_factor = 0.35
                qr_factor = 0.15
                qr_max_size = 300
                qr_min_size = 150
            elif window_width <= 2560:
                width_factor = 0.5
                height_factor = 0.5
                min_width_factor = 0.4
                min_height_factor = 0.4
                qr_factor = 0.15
                qr_max_size = 300
                qr_min_size = 150
            else:
                width_factor = 0.6
                height_factor = 0.6
                min_width_factor = 0.5
                min_height_factor = 0.5
                qr_factor = 0.15
                qr_max_size = 300
                qr_min_size = 150

            # Calculate image dimensions
            max_img_width = min(int(window_width * width_factor), 1800)
            max_img_height = min(int(window_height * height_factor), 1600)
            min_img_width = max(int(window_width * min_width_factor), 100)
            min_img_height = max(int(window_height * min_height_factor), 75)
            
            # Simplified QR sizing with fixed min/max per resolution
            qr_base_size = min(int(window_width * qr_factor), qr_max_size)
            qr_size = max(qr_min_size, min(qr_base_size, qr_max_size))

            image_to_resize = image_path.get()# or product[7]
        
            # Use placeholder if no image exists
            if not image_to_resize:
                # Clear existing content
                for widget in image_frame.winfo_children():
                    widget.destroy()
                # Create placeholder frame with minimum size constraints
                placeholder_frame = tk.Frame(image_frame, width=min_img_width, height=min_img_height, **styles['frame'])
                placeholder_frame.pack(expand=True, fill="both", pady=10)
                placeholder_frame.pack_propagate(False)
                # Add placeholder text
                placeholder_text = "No Image\nClick 'Change Image'\nto add one"
                tk.Label(placeholder_frame, text=placeholder_text, **styles['placeholder']).pack(expand=True)
                return

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
                for widget in image_frame.winfo_children():
                    widget.destroy()
                image_label = tk.Label(image_frame, image=resized_image)
                image_label.image = resized_image
                image_label.pack()

            # Update QR code with dynamic padding based on window size
            if product[3]:  # Check if QR code exists
                # Calculate available width in the right frame
                available_width = inner_right_frame.winfo_width()
                # Use the smaller of available width * factor or max_size
                qr_size = min(int(available_width * 0.8), qr_max_size)
                # Ensure it doesn't go below minimum size
                qr_size = max(qr_min_size, qr_size)
                
                resized_qr = resize_qr_code(product[3], size=(qr_size, qr_size))
                if resized_qr:
                    if hasattr(inner_right_frame, 'qr_label'):
                        inner_right_frame.qr_label.configure(image=resized_qr)
                        inner_right_frame.qr_label.image = resized_qr
                    else:
                        inner_right_frame.qr_label = tk.Label(inner_right_frame, image=resized_qr, **styles['image_frame'])
                        inner_right_frame.qr_label.image = resized_qr
                        inner_right_frame.qr_label.pack(pady=2)

        def save_edit_product():
            """Handle product updates with validation.
            
            Validates all fields
            Checks for changes requiring file updates
            Updates product and logs changes
            Shows success/error messages
            """
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

            # If product is marked as listed, validate all required fields
            if new_values['listed']:
                missing_requirements = []
                if not new_values['category'] or new_values['category'] == "No Category":
                    missing_requirements.append("category")
                if not new_values['description']:
                    missing_requirements.append("description")
                if not new_values['image']:
                    missing_requirements.append("image")
                if new_values['stock'] <= 0:
                    missing_requirements.append("stock")

                if missing_requirements:
                    # Force product to unlisted and show warning if requirements are not met
                    new_values['listed'] = 0
                    listed_var.set("No")
                    requirements_list = ", ".join(missing_requirements)
                    messagebox.showwarning(
                        "Product Unlisted",
                        f"The product has been automatically unlisted because the following required content was removed: {requirements_list}"
                    )

            # Continue with regular validation
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
            
            current_product = get_product_by_id(product_id)
            category_id = get_category_id(new_values['category']) if new_values['category'] else None
            
            # Check what needs updating
            needs_name_price_update = (
                new_values['name'] != current_product[1] or 
                abs(float(new_values['price']) - float(current_product[2])) > 0.001
            )
            needs_image_update = (
                (new_values['image'] and new_values['image'] != current_product[7]) or
                (not new_values['image'] and current_product[7]) # Image was removed
            )

            # If image was removed (new_values['image'] is empty), force it to None
            if not new_values['image']:
                new_values['image'] = None
                needs_image_update = True  # Force update when image is removed


            # Update product with appropriate file handling
            try:
                success = update_product(
                    product_id=product_id,
                    name=new_values['name'],
                    price=new_values['price'],
                    qr_code=True,
                    description=new_values['description'],
                    category_id=category_id,
                    image=new_values['image'],
                    stock=new_values['stock'],
                    listed=new_values['listed'],
                    keep_qr=not needs_name_price_update,
                    keep_image=not needs_image_update
                )

                if success:
                    display_success(message_label, "Product updated successfully!")
                    log_action('UPDATE_PRODUCT', is_admin=True, admin_id=current_admin_id, 
                            target_type='product', target_id=product_id,
                            details=f"Updated product: {new_values['name']} (Price: £{new_values['price']}, Stock: {new_values['stock']}, Listed: {new_values['listed']})")
                    show_manage_products_screen(global_state)
                else:
                    display_error(message_label, "Failed to update product")
                    log_action('UPDATE_PRODUCT', is_admin=True, admin_id=current_admin_id,
                            target_type='product', target_id=product_id,
                            details="Failed to update product", status='failed')
            except Exception as e:
                display_error(message_label, f"Error updating product: {str(e)}")
                log_action('UPDATE_PRODUCT', is_admin=True, admin_id=current_admin_id,
                        target_type='product', target_id=product_id,
                        details=f"Error updating product: {str(e)}", status='failed')

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