import os
import time
import cv2
import firebase_admin
from firebase_admin import credentials, db
from ultralytics import YOLO

# 🔹 Firebase Setup
cred = credentials.Certificate("firebase_admin.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://blindaid-c26f8-default-rtdb.firebaseio.com/'
})

# Firebase Refs
objects_ref = db.reference("objects")
user_ref = db.reference("user_direction")

# 🔹 Load YOLOv8 Model
yolo_model = YOLO("yolov8n.pt")  # Lightweight model for Raspberry Pi streaming

# 🔹 Connect to Raspberry Pi Live Camera Stream
cap = cv2.VideoCapture("http://192.168.179.238:8000/video")  # Update IP if needed

if not cap.isOpened():
    print("❌ Failed to connect to camera stream")
    exit()

print("✅ Object detection started...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Couldn't retrieve frame")
        continue

    # Run YOLO object detection
    results = yolo_model(frame, verbose=False)

    for result in results:
        for box in result.boxes:
            confidence = float(box.conf)
            class_id = int(box.cls)
            name = yolo_model.names[class_id]

            if confidence > 0.4:  # lowered for better detection sensitivity
                # Get user's current compass direction
                user_direction = user_ref.get()
                if user_direction is None:
                    user_direction = 0

                # Save to Firebase
                print(f"📦 Detected: {name} at {user_direction}°")
                print(f"🔥 Writing {name} to Firebase...")

                objects_ref.child(name).set({
                    "direction": user_direction,
                    "request_direction": False
                })

    time.sleep(3)  # Delay between detections
