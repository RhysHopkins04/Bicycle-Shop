import tkinter as tk

from src.database import (
    get_product_by_id, add_to_cart
)
from src.utils import (
    display_error, display_success, clear_frame, get_style_config,
    create_scrollable_frame, log_action, resize_product_image,
    resize_qr_code, show_dropdown, hide_dropdown
)

def show_product_page(product_id, global_state):
    """Display the product page for the given product ID.
    
    Shows detailed product view with:
    - Product image
    - Title and price
    - Description
    - Stock level
    - Add to cart functionality
    - Responsive layout
    
    Args:
        product_id: ID of product to display
        global_state: Application state containing:
            - window: Main window instance
            - content_inner_frame: Content frame
            - current_user_id: Current user's ID
    """
    global_state['current_screen'] = show_product_page
    window = global_state['window']
    content_inner_frame = global_state['content_inner_frame']
    current_user_id = global_state['current_user_id']
    user_info_frame = global_state.get('user_info_frame')
    dropdown_frame = global_state.get('dropdown_frame')

    clear_frame(content_inner_frame)
    styles = get_style_config()['product_page']

    window.unbind("<Configure>")
    window.unbind("<Button-1>")

    product = get_product_by_id(product_id)
    if product:
        log_action('VIEW_PRODUCT', user_id=current_user_id, 
                  details=f"Viewed product: {product[1]}")

        # Create title container frame to hold both title and back button
        title_container = tk.Frame(content_inner_frame, **styles['frame'])
        title_container.pack(fill="x", pady=(0, 8))

        # Back button on the left
        from .listing import switch_to_store_listing  # Local import to avoid circular dependency
        back_button = tk.Button(
            title_container, 
            text="← Back", 
            command=lambda: switch_to_store_listing(global_state),
            **styles['buttons']
        )
        back_button.pack(side="left", padx=10)

        # Title in center
        tk.Label(title_container, text=product[1], **styles['title']).pack(side="left", expand=True)

        # Create outer container
        container_frame = tk.Frame(content_inner_frame, **styles['frame'])
        container_frame.pack(fill="both", expand=True)

        # Create scrollable frame setup
        wrapper, canvas, scrollbar, scrollable_frame, bind_wheel, unbind_wheel = create_scrollable_frame(container_frame)
        wrapper.pack(fill="both", expand=True)

        # Create main content frame
        content_frame = tk.Frame(scrollable_frame, **styles['frame'])
        content_frame.pack(fill="both", expand=True, padx=40, pady=28)

        global_state.update({
            'content_frame': content_frame,
            'content_inner_frame': content_inner_frame,
            'user_info_frame': global_state.get('user_info_frame'),
            'dropdown_frame': global_state.get('dropdown_frame')
        })

        # Details container frame
        details_frame = tk.Frame(content_frame, **styles['frame'])
        details_frame.pack(fill="both", expand=True, pady=10)

        # Left side - Product image 
        left_frame = tk.Frame(details_frame, **styles['frame'])
        left_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))

        # Right side setup with fixed width
        right_frame = tk.Frame(details_frame, width=300, **styles['frame'])
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)

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
            """Debounce window resize events.
            
            Prevents excessive updates during continuous resize
            by delaying resize_content call by 150ms.
            """
            nonlocal resize_timer
            if resize_timer is not None:
                window.after_cancel(resize_timer)
            resize_timer = window.after(150, lambda: resize_content(event))

        def debounced_wraplength(event=None):
            """Debounce text wrapping updates.
            
            Prevents excessive updates during continuous resize
            by delaying update_wraplength call by 150ms.
            """
            nonlocal wraplength_timer
            if wraplength_timer is not None:
                window.after_cancel(wraplength_timer)
            wraplength_timer = window.after(150, lambda: update_wraplength(event))

        def resize_content(event=None):
            """Handle responsive resizing of product images.
            
            Calculates appropriate dimensions based on:
            - Window width/height
            - Minimum/maximum size constraints
            - Screen resolution breakpoints
            
            Updates both product image and QR code maintaining aspect ratios
            """
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

        def update_wraplength(event=None):
            """Update description text wrapping based on container width.
            
            Adjusts description text wrapping to fit container
            while maintaining readability.
            """
            # Update description wraplength based on frame width
            new_width = right_frame.winfo_width() - 40
            description_label.configure(wraplength=new_width)

        def add_to_cart_handler():
            """Handle adding product to cart.
            
            Validates user is logged in
            Adds product to cart
            Shows success/error message
            Logs action result
            Shows dropdown notification
            """
            if not global_state['current_user_id']:
                display_error(message_label, "Please log in to add items to cart")
                return
            
            success, message = add_to_cart(global_state['current_user_id'], product_id)
            if success:
                display_success(message_label, message)
                log_action('CART_ADD', user_id=global_state['current_user_id'], 
                        details=f"Added product {product[1]} to cart")
                
                # Show dropdown to indicate where cart button is
                try:
                    show_dropdown(None, global_state['user_info_frame'], global_state['dropdown_frame'])
                    window.after(5000, lambda: safe_hide_dropdown())
                except tk.TclError:
                    pass  # Ignore if widgets are destroyed
            else:
                display_error(message_label, message)
                log_action('CART_ADD', user_id=global_state['current_user_id'],
                        details=f"Failed to add product {product[1]} to cart: {message}",
                        status='failed')

        def safe_hide_dropdown():
            """Safely hide dropdown menu handling widget destruction.
            
            Attempts to hide dropdown, catches and handles any
            widget destruction errors.
            """
            try:
                hide_dropdown(None, user_info_frame, dropdown_frame)
            except tk.TclError:
                pass

        # Initial image loading
        resize_content()

        # Bind resize events with debouncing
        window.bind("<Configure>", debounced_resize)
        desc_frame.bind('<Configure>', debounced_wraplength)
        
        # Enable mouse wheel scrolling
        bind_wheel()

    else:
        message_label = tk.Label(content_inner_frame, text="", **styles['message'])
        message_label.pack()
        display_error(message_label, "Product not found!")