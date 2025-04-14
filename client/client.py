# 文件名：jetson_client.py
import serial
import socket
import csv
import json
import sqlite3
from datetime import datetime, timezone
from threading import Thread
import re
# 创建一对虚拟串口： socat -d -d pty,raw,echo=0 pty,raw,echo=0
# 配置参数
SERIAL_PORT = '/dev/pts/2'  # USB虚拟串口设备
BAUDRATE = 115200
CLOUD_IP = '192.168.0.107'    # 云端服务器IP
CLOUD_PORT = 8080
LOCAL_DB = 'local_sensor.db'  # 本地SQLite数据库

# 初始化串口和Socket
ser = serial.Serial(SERIAL_PORT, BAUDRATE,  bytesize=8, parity='N', stopbits=1, timeout=1)
cloud_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 本地存储（SQLite）
def init_local_db():
    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                 (timestamp TEXT, value REAL)''')
    conn.commit()
    conn.close()

# 带时间戳的数据打包
def pack_data(raw_data):
    timestamp = datetime.now(timezone.utc).isoformat(timespec='microseconds')
    return {
        "timestamp": timestamp,
        "value": parse_sensor_data(raw_data)
    }
    
def parse_sensor_data(raw_data):
    try:
        data_str = raw_data.decode().strip()
        # 提取第一个匹配的数值
        match = re.search(r'[-+]?\d+\.?\d*', data_str)
        if match:
            return float(match.group())
        else:
            print(f"无有效数值: {data_str}")
            return None
    except UnicodeDecodeError:
        print(f"解码失败: {raw_data}")
        return None
    
# TCP发送到云端（自动重连）
def send_to_cloud(data):
    try:
        if not hasattr(send_to_cloud, 'conn'):
            cloud_socket.connect((CLOUD_IP, CLOUD_PORT))
            send_to_cloud.conn = cloud_socket
        send_to_cloud.conn.sendall(json.dumps(data).encode())
    except (ConnectionResetError, BrokenPipeError):
        print("云端连接断开，尝试重连...")
        send_to_cloud.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_to_cloud.conn.connect((CLOUD_IP, CLOUD_PORT))
        send_to_cloud.conn.sendall(json.dumps(data).encode())

# 主循环
def main():
    init_local_db()
    while True:
        try:
            raw_data = ser.readline()
            # print("原始字节:", raw_data)
            if raw_data:
                data = pack_data(raw_data)
                
                # 本地存储（SQLite）
                conn = sqlite3.connect(LOCAL_DB)
                c = conn.cursor()
                c.execute('INSERT INTO sensor_data VALUES (?, ?)', 
                         (data['timestamp'], data['value']))
                conn.commit()
                conn.close()
                
                # 发送到云端
                send_to_cloud(data)
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    main()