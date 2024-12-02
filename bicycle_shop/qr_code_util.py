import qrcode
import cv2

def generate_qr_code(data, filename):
    """Generate a QR code and save it to a file."""
    qr = qrcode.QRCode()
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save(filename)

def scan_qr_code():
    """Scan a QR code using the webcam."""
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    while True:
        _, frame = cap.read()
        data, _, _ = detector.detectAndDecode(frame)
        if data:
            print("QR Code Data:", data)
            break
        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()