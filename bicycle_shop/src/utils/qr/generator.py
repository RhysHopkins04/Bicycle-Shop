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
    qr = qrcode.QRCode(
        version=1, 
        error_correction=qrcode.constants.ERROR_CORRECT_L, 
        box_size=10, 
        border=4
    )
    qr.add_data(data)
    img = qr.make_image(fill="black", back_color="white")
    img.save(filename)