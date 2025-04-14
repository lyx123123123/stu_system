# -*- coding: utf-8 -*-
import serial
import time
import json
from datetime import datetime
import requests
import os
import logging

# 配置日志
logging.basicConfig(filename='eye_tracker.log', level=logging.INFO)

# 串口和服务端配置
port = "/dev/ttyACM0"  # 替换为实际串口
baudrate = 115200      # 根据眼动仪文档设置
server_url = "http://192.168.46.54:5000/upload" # 服务器IP
backup_file = f"eye_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
max_size = 100 * 1024 * 1024  # 100MB

def parse_eye_data(raw_data):
    # 示例：假设数据为CSV格式 "x,y,pupil_size"
    try:
        x, y, pupil_size = map(float, raw_data.split(','))
        return {"x": x, "y": y, "pupil_size": pupil_size}
    except ValueError:
        logging.warning(f"Invalid data: {raw_data}")
        return None

# 初始化串口
try:
    ser = serial.Serial(port, baudrate, timeout=1)
    logging.info(f"Connected to {port}")
except serial.SerialException as e:
    logging.error(f"Serial error: {e}")
    exit(1)

try:
    with open(backup_file, 'a') as f:

        while True:
            print(ser)
            if ser.in_waiting > 0:
                raw_data = ser.readline().decode('utf-8', errors='ignore').strip()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                parsed = parse_eye_data(raw_data)

                if parsed:
                    packed = {"timestamp": timestamp, "data": parsed}
                    logging.info(f"Packed: {packed}")
                    print(json.dumps(packed, indent=2))
                    
                    # 保存到文件
                    json.dump(packed, f)
                    f.write('\n')
                    f.flush()
                    
                    # 发送到服务器
                    try:
                        response = requests.post(server_url, json=packed, timeout=5)
                        logging.info(f"Server response: {response.status_code}")
                    except requests.RequestException as e:
                        logging.error(f"Network error: {e}")
                    
                    # 文件轮换
                    if os.path.getsize(backup_file) > max_size:
                        f.close()
                        backup_file = f"eye_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        f = open(backup_file, 'a')
            time.sleep(0.01)
except KeyboardInterrupt:
    ser.close()
    logging.info("Serial port closed")