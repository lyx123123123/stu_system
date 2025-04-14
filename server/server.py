from flask import Flask, request
import json
from datetime import datetime

app = Flask(__name__)

# 存储文件
backup_file = f"server_eye_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.json
        print("Received:", data)
        
        # 保存到文件
        with open(backup_file, 'a') as f:
            json.dump(data, f)
            f.write('\n')
            f.flush()
        
        return {"status": "success"}, 200
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)