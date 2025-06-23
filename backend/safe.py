# ✅ Updated safe.py with 20s cooldown per object

import os
import time
import cv2
import torch
import firebase_admin
from firebase_admin import credentials, db
import threading
from ultralytics import YOLO

# Initialize Firebase
base_dir = "E:/BlindAid"  # ✅ Update this path
cred_path = os.path.join(base_dir, "firebase_admin.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://blindaid-c26f8-default-rtdb.firebaseio.com/'
})

# YOLOv8 model
print("\U0001F539 Loading YOLOv8 model...")
model = YOLO('yolov8n.pt')
print("✅ YOLOv8 model loaded successfully!")

# Firebase Refs
objects_ref = db.reference("objects")
user_direction_ref = db.reference("user_direction")
commands_ref = db.reference("commands")

# Cooldown settings
DETECTION_COOLDOWN = 20  # seconds
last_detected = {}  # object_name: timestamp

def store_object_direction(name):
    try:
        user_deg = user_direction_ref.get() or 0
        now = time.time()

        # Apply 20s cooldown
        if name in last_detected and now - last_detected[name] < DETECTION_COOLDOWN:
            print(f"⏱️ Skipped {name} (cooldown)")
            return

        last_detected[name] = now

        objects_ref.child(name).set({
            "direction": user_deg,
            "request_direction": False
        })
        print(f"✅ Stored {name} at {user_deg}°")
    except Exception as e:
        print(f"❌ Failed to store direction: {e}")

def detect_objects():
    cap = cv2.VideoCapture("http://192.168.1.6:8080/video")
    if not cap.isOpened():
        print("❌ Cannot access the camera.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            results = model(frame, verbose=False)

            for result in results:
                for box in result.boxes:
                    confidence = float(box.conf)
                    class_id = int(box.cls)
                    if confidence > 0.6:
                        name = model.names[class_id]
                        print(f"🔍 Detected: {name}")
                        store_object_direction(name)
            time.sleep(0.1)
    finally:
        cap.release()
        cv2.destroyAllWindows()


def listen_for_commands():
    seen = set()
    while True:
        cmds = commands_ref.get()
        if cmds:
            for key, value in cmds.items():
                if key in seen:
                    continue
                seen.add(key)
                cmd = value.get("command", "").lower()
                if value.get("type") == "object":
                    obj = cmd.replace("find my ", "").strip()
                    print(f"🎯 Guiding to {obj}")
                    os.system(f"python my_guide.py {obj}")
        time.sleep(1)

if __name__ == "__main__":
    print("\n🚀 Starting YOLO detection...")
    threading.Thread(target=detect_objects).start()
    threading.Thread(target=listen_for_commands).start()


# import os
# import time
# import cv2
# import numpy as np
# import torch
# import firebase_admin
# from firebase_admin import credentials, db
# import threading
# import subprocess
# from ultralytics import YOLO  # For YOLOv8


# # 🔹 Firebase Configuration
# cred = credentials.Certificate("firebase_admin.json")
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://blindaid-c26f8-default-rtdb.firebaseio.com/'
# })

# # 🔹 Load YOLOv8 Model
# print("🔹 Loading YOLOv8 model...")
# model = YOLO('yolov8n.pt')
# print("✅ YOLOv8 model loaded successfully!")

# # Global flags
# stop_yolo = False
# stop_program = False
# frame_counter = 0
# skip_frames = 3  # Process every 4th frame

# # Firebase references
# objects_ref = db.reference("objects")
# user_direction_ref = db.reference("user_direction")
# commands_ref = db.reference("commands")
# instructions_ref = db.reference("navigation_instructions")

# # ✅ Store direction in Firebase

# def store_object_compass_direction(object_name):
#     try:
#         user_dir = user_direction_ref.get() or 0
#         objects_ref.child(object_name).set({
#             "direction": user_dir,
#             "request_direction": False
#         })
#         print(f"✅ Stored {object_name} at {user_dir}° in Firebase")
#     except Exception as e:
#         print(f"❌ Failed to update direction: {str(e)}")

# # ✅ Object Detection

# def detect_objects():
#     global stop_yolo, stop_program, frame_counter

#     cap = cv2.VideoCapture("http://192.168.214.238:8000/streaming")  # ✅ Replace with your camera IP

#     if not cap.isOpened():
#         print("❌ Error: Cannot access the camera.")
#         return

#     try:
#         while not stop_program:
#             if stop_yolo:
#                 time.sleep(1)
#                 continue

#             ret, frame = cap.read()
#             if not ret:
#                 print("❌ Warning: Couldn't read frame from the camera.")
#                 continue

#             frame_counter += 1
#             if frame_counter % (skip_frames + 1) != 0:
#                 continue

#             results = model(frame, verbose=False)

#             for result in results:
#                 for obj in result.boxes:
#                     confidence = float(obj.conf)
#                     class_id = int(obj.cls)

#                     if confidence > 0.6:
#                         object_name = model.names[class_id]
#                         print(f"🔍 Detected: {object_name}")
#                         store_object_compass_direction(object_name)

#             time.sleep(0.1)

#     finally:
#         cap.release()
#         cv2.destroyAllWindows()
#         print("✅ Camera released and detection stopped.")

# # ✅ Check Firebase Commands

# def listen_for_commands():
#     print("📡 Listening for commands in Firebase...")
#     seen = set()

#     while True:
#         commands = commands_ref.get()
#         if commands:
#             for key, value in commands.items():
#                 if key in seen:
#                     continue

#                 seen.add(key)
#                 command = value.get("command", "").lower()
#                 cmd_type = value.get("type", "").lower()

#                 print(f"📥 Received command: {command} | Type: {cmd_type}")

#                 if cmd_type == "object":
#                     object_name = command.replace("find my ", "").strip()
#                     subprocess.run(["python", "my_guide.py", object_name])
#                 else:
#                     print("⚠️ Unsupported command type")

#         time.sleep(1)

# # ✅ Main
# if __name__ == "__main__":
#     try:
#         print("🔹 Starting YOLO detection...")

#         detection_thread = threading.Thread(target=detect_objects)
#         command_thread = threading.Thread(target=listen_for_commands)

#         detection_thread.start()
#         command_thread.start()

#         detection_thread.join()
#         command_thread.join()

#     except KeyboardInterrupt:
#         print("\n🔴 Program stopped by user.")
#         stop_program = True
#     finally:
#         cv2.destroyAllWindows()


