# 🔍 BlindAid - Final Year Project

**An assistive AI system for the visually impaired that provides real-time object detection, voice-guided navigation, and text reading using YOLOv5, Flutter, Raspberry Pi, and Firebase.**

## 🌐 Live Demo

📎 [GitHub Repository](https://github.com/ShreeshaHShetty/Blind-Aid-Final-Year-Project)

---

## 📌 Features

- 🎯 **Real-Time Object Detection**: YOLOv5 detects objects using the Pi camera.
- 🧭 **Directional Guidance**: Guides users using compass alignment logic (e.g., “Rotate left by 20 degrees”).
- 🗣️ **Voice Commands**: Flutter app listens for "read" and "find my <object>" commands and sends to Firebase.
- 📷 **OCR Text Reading**: Tesseract OCR extracts text from the environment.
- 🔊 **Text-to-Speech Feedback**: Flutter TTS reads out OCR and navigation instructions.
- ☁️ **Firebase Sync**: Live updates between Pi and Flutter app using Firebase Realtime Database.

---

## 🖥️ Technologies Used

| Module        | Technologies                              |
|---------------|--------------------------------------------|
| Frontend App  | Flutter, Flutter Compass, Flutter TTS     |
| Backend       | Python, OpenCV, Tesseract OCR, Firebase Admin SDK |
| Object Detection | YOLOv5 (PyTorch), IP Camera Stream     |
| Navigation    | Compass Angle Matching, Python Logic      |
| Database      | Firebase Realtime Database                |
| Hardware      | Raspberry Pi 4 + Pi Camera                |

---

## 🗂️ Folder Structure

```
BlindAid - Final Year Project/
│
├── backend/
│   ├── firebase_sync.py
│   ├── main_controller.py
│   ├── my_guide.py
│   ├── object_detector.py
│   ├── ocr_reader.py
│   ├── voice_command.py
│   └── firebase_admin.json
│
├── flutter_app/
│   ├── lib/
│   │   └── home_screen.dart
│   └── pubspec.yaml
│
├── yolov5/
│   ├── detect.py
│   └── yolov5s.pt
│
├── README.md
└── .gitignore
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ShreeshaHShetty/Blind-Aid-Final-Year-Project.git
cd Blind-Aid-Final-Year-Project
```

### 2. Setup Firebase

- Add `firebase_admin.json` to `backend/`
- Create your Firebase Realtime Database
- Update database URL in Python files

### 3. Setup Python Backend

```bash
cd backend/
pip install -r requirements.txt
python main_controller.py
```

### 4. Run Flutter App

```bash
cd flutter_app/
flutter pub get
flutter run
```

---

## 📸 Screenshots


---

## 👨‍💻 Authors

- **Shreesha H Shetty** – [GitHub](https://github.com/ShreeshaHShetty)

---

## 📄 License

This project is for educational purposes only.
