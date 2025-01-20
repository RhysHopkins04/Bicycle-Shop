from PIL import Image, ImageTk

def resize_product_image(image_path, max_width=800, max_height=600, min_width=200, min_height=150):
    """Resize product image maintaining aspect ratio within constraints"""
    try:
        img = Image.open(image_path)
        orig_width, orig_height = img.size
        
        aspect_ratio = orig_width / orig_height
        
        new_width = min(max_width, orig_width)
        new_height = new_width / aspect_ratio
        
        if new_height > max_height:
            new_height = max_height
            new_width = new_height * aspect_ratio
            
        if new_width < min_width:
            new_width = min_width
            new_height = new_width / aspect_ratio
        if new_height < min_height:
            new_height = min_height
            new_width = new_height * aspect_ratio
            
        resized = img.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(resized)
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

def resize_qr_code(qr_path, size=(150, 150)):
    """Resize QR code to specified dimensions while maintaining square aspect ratio"""
    try:
        qr_img = Image.open(qr_path)
        # Force square aspect ratio by using the smaller dimension
        dimension = min(size[0], size[1])
        qr_resized = qr_img.resize((dimension, dimension), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(qr_resized)
    except Exception as e:
        print(f"Error resizing QR code: {e}")
        return None