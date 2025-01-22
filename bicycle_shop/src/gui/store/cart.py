import tkinter as tk
from tkinter import ttk, filedialog
import cv2

from src.database.cart.cart_manager import (
    get_cart_items, update_cart_quantity
)
from src.database.discounts.discount_manager import (
    verify_discount_qr, increment_discount_uses
)
from src.utils.display import (
    display_error, display_success, clear_frame
)
from src.utils.theme import get_style_config
from src.utils.logging import log_action
from src.utils.qr import (
    scan_qr_code, scan_qr_code_from_file
)
from src.utils.frames.scrollable import create_scrollable_frame
from src.utils.images.processors import resize_product_image

def show_cart(global_state):
    """Display user's shopping cart with product details and checkout options.
    
    Creates interface showing:
    - Cart items with images, prices, and quantities
    - Quantity adjustment controls
    - Remove item buttons
    - Cart summary with subtotal
    - Discount coupon functionality
    - Checkout button
    
    Args:
        global_state: Application state dictionary containing:
            - window: Main window instance
            - content_frame: Main content frame
            - current_user_id: ID of logged in user
            - disable_search: Function to disable search bar
    """
    global_state['current_screen'] = show_cart
    window = global_state['window']
    content_frame = global_state.get('content_frame')  
    current_user_id = global_state['current_user_id']
    disable_search = global_state.get('disable_search')
    
    from .listing import switch_to_store_listing

    window.unbind("<Configure>")
    window.unbind("<Button-1>")

    disable_search()
    
    clear_frame(content_frame)
    styles = get_style_config()['cart'] # Uses a lot of other pages styles since im lazy
    image_styles = get_style_config()['product_page']['image_frame']
    
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
        """Cleanup function when leaving cart view.
        
        Removes event bindings and wheel scrolling
        to prevent errors when switching views.
        """
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
            switch_to_store_listing(global_state)
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

    # For each item in cart, create a row
    for item in cart_items:
        item_frame = tk.Frame(scrollable_frame, **styles['frame'])
        item_frame.pack(fill="x", pady=5, padx=20)
        
        info_frame = tk.Frame(item_frame, **styles['frame'])
        info_frame.pack(side="left", fill="x", expand=True)
        
        if item[7]:  # If image exists make it small icon size that is static
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
        
        # Allows adding or reducing quantity of an item with + - button while showing quantity in the middle
        tk.Button(qty_frame, text="-", 
            command=lambda pid=item[0], qty=item[-1]: update_quantity(pid, qty, -1), 
            width=2, **button_styles).pack(side="left", padx=2)

        tk.Label(qty_frame, text=str(item[-1]), width=3, fg="white", **label_styles).pack(side="left", padx=5)

        tk.Button(qty_frame, text="+", 
            command=lambda pid=item[0], qty=item[-1]: update_quantity(pid, qty, 1), 
            width=2, **button_styles).pack(side="left", padx=2)

        item_total = item[2] * item[-1]
        total_price += item_total
        tk.Label(
            item_frame,
            text=f"£{item_total:.2f}",
            font=("Arial", 11, "bold"),
            fg="white",
            **label_styles
        ).pack(side="left", padx=(50, 10))
        
        # Allows removal of all of an item no matter quantity
        remove_button = tk.Button(
            item_frame,
            text="×",
            command=lambda pid=item[0]: (
                update_cart_quantity(current_user_id, pid, 0),
                show_cart(global_state)
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

    def update_quantity(pid, current_qty, delta):
        """Update quantity of item in cart.
        
        Args:
            pid: Product ID to update
            current_qty: Current quantity in cart
            delta: Amount to change quantity by (+1/-1)
            
        Note:
            Removes item if quantity becomes 0
            Validates against available stock
            Logs all cart updates
            Refreshes cart display after update
        """
        new_qty = current_qty + delta
        if new_qty <= 0:
            # Remove item from cart if new quantity is 0 or less
            success, message = update_cart_quantity(current_user_id, pid, 0)
            if success:
                log_action('CART_UPDATE', user_id=current_user_id, details=f"Removed product {pid} from cart")
                show_cart(global_state)  # Refresh cart view
            else:
                log_action('CART_UPDATE', user_id=current_user_id, details=f"Failed to remove product {pid}: {message}", status='failed')
        else:
            # Update item quantity in cart
            success, message = update_cart_quantity(current_user_id, pid, new_qty)
            if success:
                log_action('CART_UPDATE', user_id=current_user_id, details=f"Updated product {pid} quantity to {new_qty}")
                show_cart(global_state)  # Refresh cart view
            else:
            # Log failure to update quantity
                log_action('CART_UPDATE', user_id=current_user_id, details=f"Failed to update product {pid} quantity: {message}", status='failed')
        show_cart(global_state)  # Refresh cart view after any update too

    def handle_webcam_scan():
        """Handle QR code scanning via webcam.
        
        Opens webcam view to scan discount QR codes
        Processes detected codes automatically
        Shows error if no code found or webcam fails
        Cleans up webcam resources after scan
        """
        # Seems to work since it opens and closes and uses the camera correctly, however havent tested scanning a proper qr code with it.
        try:
            qr_found = False
            cap = cv2.VideoCapture(0)
            cv2.namedWindow("QR Code Scanner")
                
            while True:
                ret, frame = cap.read()  # Read frame from webcam
                if not ret:
                    break  # Break loop if frame not read correctly
                        
                qr_data = scan_qr_code()  # Scan for QR code in the frame
                if qr_data:
                    qr_found = True
                    process_discount(qr_data)  # Process the scanned QR code
                    break 
                
                # cv2.waitKey(1) waits for 1 millisecond for a key event and returns the ASCII value of the key pressed.
                # The bitwise AND operation (& 0xFF) ensures that we only consider the lower 8 bits of the result.
                # ord('q') returns the ASCII value of the character 'q'.
                # If the 'q' key is pressed, the condition becomes True, allowing break out of loop or close window.
                cv2.imshow("QR Code Scanner", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # Stops video capture then destroys the windows created for it
            cap.release()
            cv2.destroyAllWindows()
                
            if not qr_found:
                display_error(message_label, "No QR code detected")
                    
        except Exception as e:
            cv2.destroyAllWindows()
            display_error(message_label, f"Error accessing webcam: {str(e)}")

    import logging

    def handle_file_upload():
        """Handle QR code image upload.
        
        Opens file dialog for QR code image
        Validates and processes uploaded QR code
        Shows success/error messages
        """
        # Open file dialog to select QR code image file
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            try:
                qr_data = scan_qr_code_from_file(file_path)
                if qr_data:
                    success, discount_id, message = verify_discount_qr(qr_data)
                    if success:
                        process_discount(discount_id)  # Pass discount_id instead of qr_data
                    else:
                        display_error(message_label, message)
                else:
                    display_error(message_label, "No valid QR code found in image")
            except Exception as e:
                logging.error(f"Error processing QR code: {e}")
                display_error(message_label, "Error processing QR code")

    def process_discount(discount_id):
        """Process verified discount ID.
        
        Args:
            discount_id: ID of the verified discount
            
        Note:
            Updates total price display
            Shows discount amount
            Logs discount application
            Increments discount usage
        """
        from src.database.core.connection import get_connection
        from src.database.discounts.discount_manager import increment_discount_uses

        # Fetch discount details using discount_id
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT name, percentage 
                FROM Discounts 
                WHERE id = ?
            """, (discount_id,))
            
            result = cursor.fetchone()
            if result:
                name, percentage = result
                # Calculate the discount amount and the new total price after applying the discount
                discount_amount = total_price * (percentage / 100)
                discounted_total = total_price - discount_amount
                
                # Update the discount label to show the discount applied
                discount_label.configure(text=f"Discount applied: {percentage}% (-£{discount_amount:.2f})")
                discount_label.pack(pady=(0, 5), before=coupon_button)
                
                # Update the total price label
                total_label.configure(text=f"Total: £{discounted_total:.2f}")
                
                # Change the coupon button text
                coupon_button.configure(text="Change Coupon")
                
                display_success(message_label, "Discount applied successfully!")
                log_action('APPLY_DISCOUNT', user_id=current_user_id, details=f"Applied {percentage}% discount to cart")
                
                # Increment discount usage
                success, message = increment_discount_uses(discount_id)
                if not success:
                    logging.error(f"Error incrementing discount usage: {message}")
            else:
                display_error(message_label, "Invalid discount ID")
        except Exception as e:
            logging.error(f"Error processing discount: {e}")
            display_error(message_label, "Error processing discount")
        finally:
            conn.close()

    def show_coupon_options():
        """Show dialog for selecting discount input method.
        
        Creates modal window with options:
        - Scan QR code with webcam
        - Upload QR code image
        
        Clears any existing discount when changing
        """
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
        
        # Shows the 2 buttons of 2 different options for qr code discount addition.
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
        """Check if scrollbar is needed and toggle accordingly.
        
        Shows scrollbar only when content exceeds visible area
        Enables/disables mouse wheel scrolling
        """
        # Update the canvas to ensure it has the latest dimensions
        canvas.update_idletasks()
        
        # Get the bounding box of all items in the canvas
        bbox = canvas.bbox("all")
        
        if bbox:
            # Calculate the total scrollable height
            scroll_height = bbox[3] - bbox[1]
            # Get the visible height of the canvas
            visible_height = canvas.winfo_height()
            
            if scroll_height > visible_height:
                # If the content is taller than the visible area, enable scrolling
                bind_wheel()
                scrollbar.pack(side="right", fill="y")
            else:
                # If the content fits within the visible area, disable scrolling
                unbind_wheel()
                scrollbar.pack_forget()

    # Bind the canvas configuration event to check if scrollbar is needed
    canvas.bind('<Configure>', check_scroll_needed)