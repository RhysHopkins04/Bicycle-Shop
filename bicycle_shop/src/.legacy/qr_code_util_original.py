import qrcode
import cv2

def generate_qr_code(data, filename):
    """Generate a QR code and save it to a file."""
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4) # Creates qr code with the smallest possible, and lowest 7% error correction in a standardized size 10 (210x210px) with a set border of 4 modules each side.
    qr.add_data(data)
    img = qr.make_image(fill="black", back_color="white")
    img.save(filename)

def scan_qr_code():
    """Scan a QR code using the webcam."""
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    
    scanned_data = None
    while True:
        _, frame = cap.read()
        data, _, _ = detector.detectAndDecode(frame)
        if data:
            scanned_data = data
            break
        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return scanned_data

def scan_qr_code_from_file(file_path):
    """Scan QR code from an image file"""
    try:
        image = cv2.imread(file_path)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(image)
        if data:
            return data
        return None
    except Exception as e:
        print(f"Error scanning QR code: {e}")
        return None