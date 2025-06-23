from flask import Flask, Response
from picamera2 import Picamera2
import cv2

# 🚀 Initialize Flask app
app = Flask(__name__)

# 📸 Initialize the Raspberry Pi Camera
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()

# 🔁 Function to continuously capture frames from the camera
def generate_frames():
    while True:
        # Capture a single frame
        frame = picam2.capture_array()

        # Convert the frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        # Yield the frame as a byte stream for browser
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# 🌐 Define the route for video streaming
@app.route('/streaming')
def stream():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 🏁 Start the Flask web server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
