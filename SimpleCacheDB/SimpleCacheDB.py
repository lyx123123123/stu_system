import json
import os
import threading
import time
from datetime import datetime, timedelta

class SimpleCacheDB:
    def __init__(self, storage_file='cache_data.json', autosave_interval=60):
        self.data = {}  # 内存存储：{key: (value, expiration_time)}
        
        self.lock = threading.Lock()
        self.storage_file = storage_file
        self.autosave_interval = autosave_interval
        self.running = True
        
        # 加载持久化数据
        self._load_from_disk()
        
        # 启动后台线程
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired)
        self.autosave_thread = threading.Thread(target=self._autosave)
        self.cleanup_thread.daemon = True
        self.autosave_thread.daemon = True
        
        self.cleanup_thread.start()
        self.autosave_thread.start()

    def set(self, key, value, ttl=None):
        """存储键值对，支持过期时间（单位：秒）"""
        with self.lock:
            expiration = datetime.now() + timedelta(seconds=ttl) if ttl else None
            self.data[key] = (value, expiration.timestamp() if expiration else None)

    def get(self, key):
        """获取键值，如果过期或不存在返回None"""
        with self.lock:
            item = self.data.get(key)
            if not item:
                return None
            
            value, expiration = item
            if expiration and datetime.now().timestamp() > expiration:
                del self.data[key]
                return None
            return value

    def delete(self, key):
        """删除键"""
        with self.lock:
            if key in self.data:
                del self.data[key]

    def _cleanup_expired(self):
        """后台清理过期键"""
        while self.running:
            time.sleep(1)
            with self.lock:
                now = datetime.now().timestamp()
                expired_keys = [k for k, v in self.data.items() if v[1] and v[1] < now]
                for k in expired_keys:
                    del self.data[k]

    def _autosave(self):
        """定期持久化到磁盘"""
        while self.running:
            time.sleep(self.autosave_interval)
            self._save_to_disk()

    def _save_to_disk(self):
        """保存数据到文件"""
        with self.lock, open(self.storage_file, 'w') as f:
            serializable_data = {
                k: (v[0], v[1]) 
                for k, v in self.data.items()
            }
            json.dump(serializable_data, f)

    def _load_from_disk(self):
        """从文件加载数据"""
        if not os.path.exists(self.storage_file):
            return
            
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.data = {
                    k: (v[0], v[1])
                    for k, v in data.items()
                }
        except:
            pass  # 忽略加载错误

    def close(self):
        """关闭数据库"""
        self.running = False
        self._save_to_disk()

# 使用示例
if __name__ == "__main__":
    db = SimpleCacheDB(autosave_interval=5)
    
    # 设置数据（带10秒过期时间）
    db.set("user:1001", {"name": "Alice", "email": "alice@example.com"}, ttl=10)
    
    # 获取数据
    print(db.get("user:1001"))  # 输出数据
    
    # 10秒后再次获取
    time.sleep(11)
    print(db.get("user:1001"))  # 输出 None
    
    db.close()