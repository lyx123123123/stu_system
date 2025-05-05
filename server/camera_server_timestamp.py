# -*- coding: utf-8 -*-
import cv2
import socket
import struct
import pickle
import threading
import os
import time

server_ip = '0.0.0.0'
server_port = 9999

# 设置每个文件的最大大小（例如100MB）
max_file_size = 100 * 1024 * 1024  # 100MB
current_file_size = 0  # 当前文件的大小
file_index = 1  # 文件编号
save_path = f"received_{time.strftime('%Y%m%d_%H%M%S')}_{file_index}.mp4"  # 初始文件名
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = None

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((server_ip, server_port))
server_socket.listen(5)

print("服务器已启动，等待连接...")

def create_new_video_file():
    global save_path, out, current_file_size, file_index
    current_file_size = 0  # 重置当前文件大小
    file_index += 1  # 增加文件编号
    save_path = f"received_{time.strftime('%Y%m%d_%H%M%S')}_{file_index}.mp4"  # 生成新的文件名
    out = cv2.VideoWriter(save_path, fourcc, 20.0, (640, 480))  # 创建新的VideoWriter

def client_handler(client_socket):
    global out, current_file_size
    data = b""
    payload_size = struct.calcsize(">L")
    try:
        while True:
            while len(data) < payload_size:
                packet = client_socket.recv(4096)
                if not packet:
                    return
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(frame_data)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

            if out is None:
                # 创建第一个视频文件
                create_new_video_file()

            # 如果文件已经超过设定大小，切换到新的文件
            current_file_size += frame.nbytes
            if current_file_size >= max_file_size:
                print(f"当前文件超过{max_file_size / (1024 * 1024)}MB，创建新文件")
                out.release()  # 关闭当前文件
                create_new_video_file()  # 创建新文件

            # 保存每一帧
            out.write(frame)

            # 同时也可以实时显示（可选）
            # cv2.imshow('Receiving...', frame)
            # if cv2.waitKey(1) == 27:  # 按ESC键退出
            #     break

    except Exception as e:
        print(f"服务器端异常: {e}")
    finally:
        client_socket.close()
        if out:
            out.release()
        cv2.destroyAllWindows()

while True:
    client_sock, addr = server_socket.accept()
    print(f"客户端 {addr} 已连接")
    t = threading.Thread(target=client_handler, args=(client_sock,))
    t.start()
