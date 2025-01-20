import tkinter as tk
from ..theme import get_style_config
from ..images import resize_qr_code
from ..display import display_error

def setup_product_grid(scrollable_frame, canvas, products, product_width=290, padding=5):
    """Sets up the basic grid layout for products.
    
    Args:
        scrollable_frame: Frame to display products in
        canvas: Canvas widget containing scrollable frame
        products: List of product tuples to display
        product_width: Width of each product frame
        padding: Padding between product frames
        
    Returns:
        int | None: Number of columns that fit in canvas width,
                   None if no products to display
        
    Note:
        Calculates optimal number of columns based on canvas width
        Shows error message if no products available
    """
    style = get_style_config()['product_grid']

    if not products:
        message_label = tk.Label(scrollable_frame, text="", bg=style['frame_bg'])
        message_label.pack(pady=10)
        display_error(message_label, "No products available.")
        return None
        
    canvas.update_idletasks()
    content_width = canvas.winfo_width()
    num_columns = max(1, content_width // (product_width + padding))
    return num_columns

def create_basic_product_frame(row_frame, product, product_width, buttons=None):
    """Creates standard product frame with common elements.
    
    Args:
        row_frame: Parent frame to place product in
        product: Product tuple containing details
        product_width: Width of product frame
        buttons: Optional list of (text, callback) tuples for buttons
        
    Returns:
        Frame: Created product frame with all elements
        
    Note:
        Creates frame with:
        - Product name and price labels
        - Optional action buttons
        - QR code if product has one
    """
    style = get_style_config()['product_grid']
    
    product_frame = tk.Frame(row_frame, width=product_width, padx=1, pady=1, bg=style['frame_bg'])
    product_frame.pack(side="left", padx=1, pady=1)

    tk.Label(product_frame, text=f"Name: {product[1]}", **style['text']).pack()
    tk.Label(product_frame, text=f"Price: £{product[2]:.2f}", **style['text']).pack()

    if buttons:
        button_frame = tk.Frame(product_frame, bg=style['frame_bg'])
        button_frame.pack(pady=5)

        for btn_text, btn_callback in buttons:
            def create_command(callback=btn_callback, prod_id=product[0]):
                """Create callback function for button.
                
                Args:
                    callback: Function to call when button clicked
                    prod_id: ID of product to pass to callback
                    
                Returns:
                    Function that calls callback with product ID
                """
                return lambda: callback(prod_id)
            
            tk.Button(
                button_frame,
                text=btn_text,
                command=create_command(),
                **style['buttons'],
                width=14
            ).pack(side="left", padx=2)

    if product[3]:
        qr_resized = resize_qr_code(product[3], size=(290, 290))
        if qr_resized:
            qr_label = tk.Label(product_frame, image=qr_resized, **style['qr_label'])
            qr_label.image = qr_resized
            qr_label.pack()

    return product_frame

def create_product_management_frame(row_frame, product, product_width, edit_callback, delete_callback):
    """Creates product frame with management buttons.
    
    Args:
        row_frame: Parent frame to place product in
        product: Product tuple containing details
        product_width: Width of product frame
        edit_callback: Function to call when edit clicked
        delete_callback: Function to call when delete clicked
        
    Returns:
        Frame: Product frame with edit/delete buttons
    """
    buttons = [
        ("Edit", edit_callback),
        ("Delete", delete_callback)
    ]
    return create_basic_product_frame(row_frame, product, product_width, buttons)

def create_product_listing_frame(row_frame, product, product_width, view_callback):
    """Creates product frame with view button for store listing.
    
    Args:
        row_frame: Parent frame to place product in
        product: Product tuple containing details
        product_width: Width of product frame
        view_callback: Function to call when view clicked
        
    Returns:
        Frame: Product frame with view button
    """
    buttons = [("View Product", view_callback)]
    return create_basic_product_frame(row_frame, product, product_width, buttons)