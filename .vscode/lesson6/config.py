"""
MQTT 監控應用程式配置檔案
"""
import os
from pathlib import Path

# MQTT 設定
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

# MQTT Topics
TOPICS = {
    "temperature": "sensor/temperature",
    "humidity": "sensor/humidity",
    "light": "light/status"
}

# 檔案路徑設定
BASE_DIR = Path(__file__).parent
EXCEL_FILE = BASE_DIR / "sensor_data.xlsx"

# 數據儲存設定
MAX_HISTORY_RECORDS = 1000  # 在記憶體中保留的最大歷史記錄數

