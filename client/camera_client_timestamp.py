# -*- coding: utf-8 -*-
import cv2
import socket
import struct
import pickle
import time

# 服务器IP和端口
server_ip = '192.168.0.113'
server_port = 9999

# 打开摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

# 调小分辨率，减轻负担
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 连接服务器
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_server():
    while True:
        try:
            client_socket.connect((server_ip, server_port))
            print("连接服务器成功！")
            break
        except Exception as e:
            print(f"连接失败，重试中... {e}")
            time.sleep(2)

connect_server()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头画面")
            break

        # 添加时间戳
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # 编码为JPEG，减小传输体积
        result, encoded_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        data = pickle.dumps(encoded_frame)

        # 发送数据长度+数据
        try:
            client_socket.sendall(struct.pack(">L", len(data)) + data)
        except (BrokenPipeError, ConnectionResetError):
            print("服务器断开，尝试重连...")
            client_socket.close()
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connect_server()
except KeyboardInterrupt:
    print("手动停止")

finally:
    cap.release()
    client_socket.close()
