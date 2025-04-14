import serial
import hashlib

def send_file(port, filename, baudrate=115200):
    ser = serial.Serial(port, baudrate, timeout=1)
    
    with open(filename, 'rb') as f:
        data = f.read()
        file_hash = hashlib.sha256(data).hexdigest()
    
    # 生成数据头并发送
    header = f"{filename}|{len(data)}|{file_hash}\n"
    ser.write(header.encode())
    ser.flush()  # 强制立即发送
    
    # 分块发送文件内容
    chunk_size = 1024
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        ser.write(chunk)
        ack = ser.read(3)
        if ack != b'ACK':
            print("传输中断！")
            break
    ser.close()

if __name__ == "__main__":
    send_file('/dev/pts/2', 'sensor_data.json')