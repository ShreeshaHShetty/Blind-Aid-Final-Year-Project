import firebase_admin
from firebase_admin import credentials, db
import time

from ocr_reader import process_ocr  # Handles the OCR logic

# 🔹 Firebase Setup
cred = credentials.Certificate("firebase_admin.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://blindaid-c26f8-default-rtdb.firebaseio.com/'
})

# 🔹 Firebase Refs
commands_ref = db.reference("commands")
objects_ref = db.reference("objects")
user_ref = db.reference("user_direction")
instructions_ref = db.reference("navigation_instructions")
ocr_response_ref = db.reference("ocr_result")

seen_commands = set()

def guide_user_to_object(object_name):
    object_data = objects_ref.child(object_name).get()
    user_direction = user_ref.get()

    if not object_data or "direction" not in object_data:
        print(f"❌ Object '{object_name}' not found in Firebase.")
        return

    object_direction = float(object_data["direction"])
    if user_direction is None:
        print("❌ User direction not found.")
        return

    user_direction = float(user_direction)

    diff = (object_direction - user_direction + 360) % 360

    if 10 <= diff <= 180:
        instructions_ref.push().set("Turn right by {:.0f} degrees".format(diff))
    elif 180 < diff <= 350:
        instructions_ref.push().set("Turn left by {:.0f} degrees".format(360 - diff))
    else:
        instructions_ref.push().set("You're aligned!")

    print(f"🧭 User: {user_direction}°, Object: {object_direction}°, Diff: {diff:.0f}°")

def listen_to_commands():
    print("🔄 Listening for Firebase commands...")

    while True:
        commands = commands_ref.get()
        if commands:
            for key, value in commands.items():
                if key not in seen_commands:
                    seen_commands.add(key)

                    command = value.get("command", "").lower()
                    cmd_type = value.get("type", "").lower()

                    print(f"📥 Received Command: {command} | Type: {cmd_type}")

                    if cmd_type == "ocr":
                        text = process_ocr()
                        ocr_response_ref.set(text)
                        print("✅ OCR result sent to Firebase.")

                    elif cmd_type == "object":
                        object_name = command.replace("find my ", "").strip()
                        guide_user_to_object(object_name)

                    else:
                        print("⚠️ Unknown command type.")

        time.sleep(1)

if __name__ == "__main__":
    listen_to_commands()
