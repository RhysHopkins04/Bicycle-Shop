import qrcode

def generate_qr_code(data, filename):
    """Generate a QR code and save it to a file.
    
    Args:
        data: Content to encode in QR code
        filename: Path where QR code image will be saved
        
    Note:
        Creates QR code with:
        - Version 1 (21x21 modules)
        - Low error correction (7%)
        - Box size of 10 pixels (210x210px)
        - Border of 4 modules
        - Black on white coloring
    """
    # Create a QRCode object with specified parameters
    qr = qrcode.QRCode(
        version=1, # Version of the QR code (1 is the smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level (L is the lowest)
        box_size=10, # Size of each box in the QR code grid
        border=4 # Width of the border (in boxes)
    )

    qr.add_data(data) # Add data to the QR code

    # Generate the QR code image with specified fill and background colors
    img = qr.make_image(fill="black", back_color="white")
    img.save(filename)