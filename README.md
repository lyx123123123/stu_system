# stu_system

# 使用说明
本项目建立在两块英伟达显卡之上，通过接收串口数据，实现转发功能
# 创建虚拟串口
socat -d -d pty,raw,echo=0 pty,raw,echo=0
## server
启动influxDB： sudo systemctl start influxdb

# 使用命令创建一个时效为7天的 token
 influx setup \
   --username admin \
   --password your_secure_password \
   --org your_org \
   --bucket default_bucket \
   --retention 7d \
   --force

influx auth create --all-access --description "Super Admin Token"

# 服务端server.py 启动命令：
 python3 -m uvicorn server:app --host 0.0.0.0 --port 8000
 
## client
python3 client.py