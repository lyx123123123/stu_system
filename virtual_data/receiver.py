import serial
import hashlib
import os
import re

def receive_file(port, save_path='received', baudrate=115200):
    # 创建目录并清理文件名
    os.makedirs(save_path, exist_ok=True)
    
    ser = serial.Serial(port, baudrate, timeout=5)
    try:
        header = ser.readline().decode().strip()
        filename, file_size, file_hash = header.split('|')
        file_size = int(file_size)
        
        # 清理文件名
        filename = re.sub(r'[\\/:*?"<>|]', '', filename)
        filename = os.path.basename(filename)
        
        received_data = bytearray()
        while len(received_data) < file_size:
            chunk = ser.read(min(1024, file_size - len(received_data)))
            if not chunk:
                break
            received_data.extend(chunk)
            ser.write(b'ACK')
        
        received_hash = hashlib.sha256(received_data).hexdigest()
        if received_hash != file_hash:
            print("校验失败！")
        else:
            with open(os.path.join(save_path, filename), 'wb') as f:
                f.write(received_data)
            print(f"文件 {filename} 接收成功")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        ser.close()

if __name__ == "__main__":
    receive_file('/dev/pts/3')