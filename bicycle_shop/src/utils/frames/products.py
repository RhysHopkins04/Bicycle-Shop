import tkinter as tk
from ..theme import get_style_config
from ..images import resize_qr_code
from ..display import display_error

def setup_product_grid(scrollable_frame, canvas, products, product_width=290, padding=5):
    """Sets up the basic grid layout for products"""
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
    """Creates standard product frame with common elements"""
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
    """Creates product frame with management buttons"""
    buttons = [
        ("Edit", edit_callback),
        ("Delete", delete_callback)
    ]
    return create_basic_product_frame(row_frame, product, product_width, buttons)

def create_product_listing_frame(row_frame, product, product_width, view_callback):
    """Creates product frame with view button for store listing"""
    buttons = [("View Product", view_callback)]
    return create_basic_product_frame(row_frame, product, product_width, buttons)