import asyncio
import socket
import json
from fastapi import FastAPI, WebSocket
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# 初始化 InfluxDB 和 FastAPI 启动influxDB： sudo systemctl start influxdb
# 创建token
# influx setup \
# >   --username admin \
# >   --password your_secure_password \
# >   --org your_org \
# >   --bucket default_bucket \
# >   --retention 7d \
# >   --force
# influx auth create --all-access --description "Super Admin Token"
client = InfluxDBClient(url="http://localhost:8086", token="VpN6AUceFSlbJEcjhMkX7AZrsrZfAn2R1c4AjPXhaalR8hxVxbBbUbwKiLxbp7C3rfCbxsLaD2FjInz72BZx9w==", org="your_org")
write_api = client.write_api(write_options=SYNCHRONOUS)
app = FastAPI()
websocket_clients = []

# 异步 TCP 服务器
async def tcp_server():
    loop = asyncio.get_event_loop()
    server = await loop.create_server(
        protocol_factory=lambda: TCPProtocol(),
        host='0.0.0.0', 
        port=8080
    )
    async with server:
        await server.serve_forever()


# TCP 协议处理器
class TCPProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        try:
            parsed = json.loads(data.decode())
            # 存储到 InfluxDB
            point = Point("sensor").field("value", parsed['value']).time(parsed['timestamp'])
            write_api.write(bucket="default_bucket", org="your_org", record=point)

            # 广播到 WebSocket
            for ws in websocket_clients:
                asyncio.create_task(ws.send_text(json.dumps(parsed)))
                
        except Exception as e:
            print(f"Error: {e}")

# WebSocket 路由
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # 保持连接
    except:
        websocket_clients.remove(websocket)

# 启动时运行 TCP 服务器
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(tcp_server())
# 启动命令： python3 -m uvicorn server:app --host 0.0.0.0 --port 8000