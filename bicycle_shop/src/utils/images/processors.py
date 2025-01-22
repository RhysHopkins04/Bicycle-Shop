from PIL import Image, ImageTk

def resize_product_image(image_path, max_width=800, max_height=600, min_width=200, min_height=150):
    """Resize product image maintaining aspect ratio within constraints.
    
    Args:
        image_path: Path to image file to resize
        max_width: Maximum allowed width in pixels
        max_height: Maximum allowed height in pixels
        min_width: Minimum allowed width in pixels
        min_height: Minimum allowed height in pixels
        
    Returns:
        PhotoImage: Resized image ready for Tkinter display
        None: If error occurs during resizing
        
    Note:
        Uses LANCZOS resampling for high quality
        Maintains original aspect ratio
        Ensures image fits within min/max constraints
    """
    try:
        img = Image.open(image_path)
        orig_width, orig_height = img.size
        
        aspect_ratio = orig_width / orig_height
        
        new_width = min(max_width, orig_width)
        new_height = new_width / aspect_ratio
        
        # If the new height exceeds the maximum height, adjust the height and width
        if new_height > max_height:
            new_height = max_height
            new_width = new_height * aspect_ratio
        
        # If the new width is less than the minimum width, adjust the width and height
        if new_width < min_width:
            new_width = min_width
            new_height = new_width / aspect_ratio
            
        # If the new height is less than the minimum height, adjust the height and width
        if new_height < min_height:
            new_height = min_height
            new_width = new_height * aspect_ratio
        
        # Resize the image to the new dimensions using the LANCZOS resampling filter
        resized = img.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(resized) 
    except Exception as e:
        # Print an error message if an exception occurs during the resizing process
        print(f"Error resizing image: {e}")
        return None

def resize_qr_code(qr_path, size=(150, 150)):
    """Resize QR code to specified dimensions while maintaining square aspect ratio.
    
    Args:
        qr_path: Path to QR code image file
        size: Tuple of (width, height) in pixels
        
    Returns:
        PhotoImage: Resized QR code ready for Tkinter display
        None: If error occurs during resizing
        
    Note:
        Forces square aspect ratio using smaller dimension
        Uses LANCZOS resampling for high quality
    """
    try:
        qr_img = Image.open(qr_path) # Open the image file from the given path

        # Force square aspect ratio by using the smaller dimension of the image
        dimension = min(size[0], size[1])

        # Resize the image to a square with the calculated dimension
        qr_resized = qr_img.resize((dimension, dimension), Image.Resampling.LANCZOS)

        # Convert the resized image to a format suitable for Tkinter
        return ImageTk.PhotoImage(qr_resized)
    except Exception as e:
        # Print an error message if any exception occurs during the process
        print(f"Error resizing QR code: {e}")
        return None