import csv
import json
from datetime import datetime, timezone, timedelta

# # 生成 CSV 数据
# with open('sensor_data.csv', 'w') as f:
#     writer = csv.writer(f)
#     writer.writerow(["timestamp", "type", "value", "unit"])
#     for i in range(5):
#         timestamp = (datetime.now(timezone.utc) - timedelta(seconds=5-i)).isoformat()
#         writer.writerow([timestamp, "temperature", 25.0 + i*0.1, "°C"])

# 生成 JSON 数据
data = []
for i in range(3):
    timestamp = (datetime.now(timezone.utc) - timedelta(seconds=3-i)).isoformat()
    data.append({
        "timestamp": timestamp,
        "sensor_id": f"temp_sensor_{i:03d}",
        "type": "temperature",
        "value": 24.5 + i*0.5,
        "unit": "°C"
    })
with open('sensor_data.json', 'w') as f:
    json.dump(data, f, indent=2)