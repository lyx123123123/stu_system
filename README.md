# stu_system

# 使用说明
本项目建立在两块英伟达显卡之上，通过接收串口数据，实现转发功能

## 一、板卡端代码（Jetson 运行）
# 功能：
1. 从 USB 虚拟串口读取传感器数据。
2. 添加微秒级时间戳。
3. 本地存储（CSV/SQLite）。
4. 通过 TCP 发送到云端。
# 依赖安装
pip install pyserial sqlite3 influxdb_client fastapi websockets
## 运行
python3 client.py

## 二、云端代码（服务器运行）
# 功能：
1. 接收板卡端 TCP 数据。
2. 存储到 InfluxDB（或 MySQL）。
3. 提供 WebSocket 实时推送。

# influxDB2 在ubuntu安装：i

curl --silent --location -O \
https://repos.influxdata.com/influxdata-archive.key
echo "943666881a1b8d9b849b74caebf02d3465d6beb716510d86a39f6c8e8dac7515  influxdata-archive.key" \
 sha256sum --check - && cat influxdata-archive.key \
 gpg --dearmor \
 sudo tee /etc/apt/trusted.gpg.d/influxdata-archive.gpg > /dev/null \
&& echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive.gpg] https://repos.influxdata.com/debian stable main' \
 sudo tee /etc/apt/sources.list.d/influxdata.list

sudo apt-get update && sudo apt-get install influxdb2

# 启动influxDB： 
sudo systemctl start influxdb

# 使用命令创建一个时效为7天的 token
 influx setup \
   --username admin \
   --password your_secure_password \
   --org your_org \
   --bucket default_bucket \
   --retention 7d \
   --force

influx auth create --all-access --description "Super Admin Token"

# 启动：
 python3 -m uvicorn server:app --host 0.0.0.0 --port 8000

##  客户端测试（WebSocket）
./client.html
 