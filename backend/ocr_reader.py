import cv2
import time
import pytesseract
from firebase_admin import db
from firebase_setup import *  # Ensures Firebase is initialized once

# ✅ Path to Tesseract OCR executable (Windows-specific)
pytesseract.pytesseract.tesseract_cmd = r"C:\\Users\\College.DELL\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe"

# 🔗 Firebase reference
ocr_result_ref = db.reference("ocr_result")

# 📸 Raspberry Pi stream URL
STREAM_URL = "http://192.168.234.238:8000/streaming"  # Update as needed

def capture_frame():
    cap = cv2.VideoCapture(STREAM_URL)
    time.sleep(1)
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        print("❌ Failed to capture frame.")
        return None

    return frame

def extract_text(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text.strip()

def process_ocr():
    image = capture_frame()
    if image is not None:
        text = extract_text(image)
        print("📄 Extracted OCR text:", text)
        return text  # No Firebase push here
    else:
        print("⚠️ OCR failed - no image captured.")
        return "OCR failed"


if __name__ == "__main__":
    print("🔍 Running OCR test from Pi stream...")
    result = process_ocr()
    print("📃 OCR Output:\n", result)