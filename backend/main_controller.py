import sys
import time
import os
import threading
import subprocess
from firebase_admin import credentials, db
import firebase_admin
from firebase_setup import *  # Assuming this sets up Firebase
from firebase_admin import storage
from ocr_reader import process_ocr
from ultralytics import YOLO
import cv2


# ✅ Firebase references
root_ref = db.reference("/")
objects_ref = root_ref.child("objects")
user_dir_ref = root_ref.child("user_direction")
instructions_ref = root_ref.child("navigation_instructions")
commands_ref = root_ref.child("commands")
ocr_result_ref = root_ref.child("ocr_result")

# Global flags
stop_program = False
frame_counter = 0
skip_frames = 3
last_detection_time = {}

# ✅ Object Detection with suppression
model = YOLO('yolov8n.pt')

def store_object_compass_direction(object_name):
    try:
        current_time = time.time()
        if object_name in last_detection_time and (current_time - last_detection_time[object_name] < 20):
            return
        last_detection_time[object_name] = current_time

        user_dir = user_dir_ref.get() or 0
        objects_ref.child(object_name).set({
            "direction": user_dir,
            "request_direction": False
        })
        print(f"✅ Stored {object_name} at {user_dir}° in Firebase")
    except Exception as e:
        print(f"❌ Failed to update direction: {str(e)}")

def detect_objects():
    global frame_counter, stop_program
    cap = cv2.VideoCapture("http://192.168.234.238:8000/streaming")  # Replace with your camera IP
    if not cap.isOpened():
        print("❌ Error: Cannot access the camera.")
        return

    try:
        while not stop_program:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Warning: Couldn't retrieve frame from camera.")
                continue

            frame_counter += 1
            if frame_counter % (skip_frames + 1) != 0:
                continue

            results = model(frame, verbose=False)
            for result in results:
                for box in result.boxes:
                    confidence = float(box.conf)
                    class_id = int(box.cls)
                    if confidence > 0.6:
                        object_name = model.names[class_id]
                        print(f"🔍 Detected: {object_name}")
                        store_object_compass_direction(object_name)

            time.sleep(0.1)
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Camera released and detection stopped.")

# ✅ Command Listener
seen_commands = set()
def listen_for_commands():
    global stop_program
    print("📡 Listening for commands in Firebase...")
    while not stop_program:
        commands = commands_ref.get()
        if commands:
            for key, value in commands.items():
                if key not in seen_commands:
                    seen_commands.add(key)
                    command = value.get("command", "").lower()
                    cmd_type = value.get("type", "").lower()
                    print(f"📥 Received command: {command} | Type: {cmd_type}")

                    if cmd_type == "ocr":
                        text = process_ocr()
                        ocr_result_ref.set({
                            "text": text,
                            "timestamp": int(time.time())
                        })
                        print("✅ OCR result uploaded to Firebase.")

                    elif cmd_type == "object":
                        object_name = command.replace("find my ", "").strip()
                        print(f"🚀 Launching guidance subprocess for: {object_name}")
                        subprocess.run(["python", "my_guide.py", object_name])

        time.sleep(1)

# 🏁 Main
if __name__ == "__main__":
    try:
        detection_thread = threading.Thread(target=detect_objects)
        command_thread = threading.Thread(target=listen_for_commands)

        detection_thread.start()
        command_thread.start()

        detection_thread.join()
        command_thread.join()

    except KeyboardInterrupt:
        print("\n🛑 Program stopped by user.")
        stop_program = True
        cv2.destroyAllWindows()
