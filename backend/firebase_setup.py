import firebase_admin
from firebase_admin import credentials

# 📁 Load Firebase Admin SDK credentials
cred = credentials.Certificate("firebase_admin.json")

# ✅ Initialize the default Firebase app (only once)
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://blindaid-c26f8-default-rtdb.firebaseio.com/'
    })
