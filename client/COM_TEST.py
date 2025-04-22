# -*- coding: utf-8 -*-
import serial


port = '/dev/pts/3'  # 根据你的需求修改串口号
baudrate = 115200 # 根据串口设备的波特率设置

# 创建串口对象
ser = serial.Serial(port, baudrate)

while True:
    # 读取串口数据
    data = ser.readline().decode().strip()
    print(data)
    if data:
        # 处理接收到的数据
        print("Received message:", data)
        
        # 在这里添加你要进行的下一步操作代码
        
    # 如果要退出循环，可以添加一个终止条件
    # 如按下某个键盘按键后，使用 break 语句退出循环
    # if keyboard.is_pressed('q'):
    #     break

# 关闭串口连接
ser.close()
