import cv2
import contextlib
import os
import sys

# Deals with MSMF warnings using context manager
@contextlib.contextmanager
def suppress_stdout_stderr():
    """Context manager to suppress stdout/stderr"""
    fd_out = sys.stdout.fileno()
    fd_err = sys.stderr.fileno()
    
    def _redirect(fd):
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, fd)
        os.close(devnull)

    with os.fdopen(os.dup(fd_out), 'wb') as old_stdout:
        with os.fdopen(os.dup(fd_err), 'wb') as old_stderr:
            _redirect(fd_out)
            _redirect(fd_err)
            try:
                yield
            finally:
                os.dup2(old_stdout.fileno(), fd_out)
                os.dup2(old_stderr.fileno(), fd_err)


def scan_qr_code():
    """Scan a QR code using the webcam."""
    window_name = "QR Code Scanner"
    scanned_data = None
    running = True

    with suppress_stdout_stderr():
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()
        cv2.namedWindow(window_name)
        
        while running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            data, _, _ = detector.detectAndDecode(frame)
            if data:
                scanned_data = data
                running = False
                
            cv2.imshow(window_name, frame)
            
            # Check for window close or 'q' key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                running = False
                
        # Clean up resources in the correct order
        cap.release()
        cv2.destroyWindow(window_name)
        cv2.waitKey(1)  # Give OpenCV a chance to clean up

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