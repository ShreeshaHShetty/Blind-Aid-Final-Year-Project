import sys
import time
import os
import firebase_admin
from firebase_admin import credentials, db


cred = credentials.Certificate("firebase_admin.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://blindaid-c26f8-default-rtdb.firebaseio.com'
})

# ✅ Firebase references
root_ref = db.reference("/")
objects_ref = root_ref.child("objects")
user_dir_ref = root_ref.child("user_direction")
instructions_ref = root_ref.child("navigation_instructions")

# ✅ Guidance Function
def Guide_me_with_compass(object_name):
    print(f"🔍 Starting compass guidance for: {object_name}")

    # Clear previous navigation instructions
    instructions_ref.delete()

    instructions_ref.push().set(f"Starting guidance to {object_name}")

    # Fetch object direction
    object_data = objects_ref.child(object_name).get()
    if not object_data or 'direction' not in object_data:
        print("❌ Object direction not found.")
        instructions_ref.push().set("Object direction not found.")
        return

    object_direction = float(object_data['direction'])
    instructions_ref.push().set(f"Object is at {object_direction:.1f} degrees")
    print(f"🎯 Object is at {object_direction:.1f}°")

    aligned_counter = 0

    while True:
        user_snapshot = user_dir_ref.get()
        if user_snapshot is None:
            print("⏳ Waiting for user direction...")
            instructions_ref.push().set("Waiting for your direction...")
            time.sleep(2)
            continue

        try:
            user_direction = float(user_snapshot)
        except ValueError:
            instructions_ref.push().set("Invalid direction received.")
            time.sleep(2)
            continue

        # Clockwise angular difference
        diff = (object_direction - user_direction + 360) % 360

        # Generate instruction
        if 10 <= diff <= 180:
            instruction = f"Rotate right by {int(diff)} degrees"
            aligned_counter = 0
        elif 180 < diff <= 350:
            instruction = f"Rotate left by {int(360 - diff)} degrees"
            aligned_counter = 0
        elif diff < 10 or diff > 350:
            instruction = "You're aligned!"
            aligned_counter += 1
        else:
            instruction = "Hold still"
            aligned_counter = 0

        print(f"[→] User: {user_direction:.1f}°, Object: {object_direction:.1f}°, Diff: {diff:.1f}° → {instruction}")
        instructions_ref.push().set(instruction)

        if aligned_counter >= 2:
            instructions_ref.push().set("You are now perfectly aligned.")
            print("✅ Navigation completed. Stopping guidance.")
            break

        time.sleep(3)

# 🏁 Entry Point
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python my_guide.py <object_name>")
    else:
        Guide_me_with_compass(sys.argv[1])
