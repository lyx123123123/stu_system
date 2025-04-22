# jetson_streamer.py
from flask import Flask, Response
from flask_socketio import SocketIO
import cv2
import base64
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def get_camera():
    # NVIDIA Jetson摄像头GStreamer管道
    return cv2.VideoCapture(
        "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720, framerate=30/1, format=NV12 ! "
        "nvvidconv ! video/x-raw, width=640, height=480, format=BGRx ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink",
        cv2.CAP_GSTREAMER)

def video_stream():
    camera = get_camera()
    while True:
        success, frame = camera.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        socketio.emit('video_frame', jpg_as_text)
        time.sleep(0.03)  # 控制帧率

@app.route('/')
def index():
    return "Jetson Video Stream Server"

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    threading.Thread(target=video_stream).start()

if __name__ == '__main__':
    print("Starting video stream server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    