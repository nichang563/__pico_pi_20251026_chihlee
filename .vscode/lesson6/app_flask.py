"""
Flask MQTT 監控應用程式
即時顯示電燈狀態、溫濕度數據，並將數據儲存為 Excel 檔案
"""
import sys
from pathlib import Path
from datetime import datetime
import logging
import threading
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# 確保可以導入同目錄下的模組
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from mqtt_client import MQTTClient
from data_storage import save_to_excel, read_excel_data
from config import TOPICS, MAX_HISTORY_RECORDS

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 建立 Flask 應用程式
app = Flask(__name__)

# 全域數據儲存（在實際應用中可以使用 Redis 或資料庫）
data_store = {
    'temperature': None,
    'humidity': None,
    'light_status': '未知',
    'history_data': [],
    'mqtt_client': None,
    'connection_status': '未連線'
}

# 線程鎖，確保數據更新的線程安全
data_lock = threading.Lock()

def on_mqtt_message(topic, data):
    """
    MQTT 訊息回調函數
    處理接收到的訊息並更新數據儲存
    """
    try:
        logger.info("收到 MQTT 訊息 - Topic: %s, Data: %s", topic, data)
        print(f"[MQTT] 收到訊息 - Topic: {topic}, Data: {data}")
        
        timestamp = datetime.now()
        
        with data_lock:
            # 根據 topic 處理不同的數據
            if topic == TOPICS["temperature"]:
                # 處理溫度數據
                if isinstance(data, dict):
                    temp_value = data.get("temperature") or data.get("value") or data.get("temp")
                else:
                    try:
                        temp_value = float(data) if data is not None else None
                    except (ValueError, TypeError):
                        temp_value = None
                
                if temp_value is not None:
                    data_store['temperature'] = float(temp_value)
                    logger.info("更新溫度: %.1f°C", data_store['temperature'])
            
            elif topic == TOPICS["humidity"]:
                # 處理濕度數據
                if isinstance(data, dict):
                    hum_value = data.get("humidity") or data.get("value") or data.get("hum")
                else:
                    try:
                        hum_value = float(data) if data is not None else None
                    except (ValueError, TypeError):
                        hum_value = None
                
                if hum_value is not None:
                    data_store['humidity'] = float(hum_value)
                    logger.info("更新濕度: %.1f%%", data_store['humidity'])
            
            elif topic == TOPICS["light"]:
                # 處理電燈狀態數據
                if isinstance(data, dict):
                    light_value = data.get("status") or data.get("state") or data.get("light")
                else:
                    light_value = str(data).lower() if data is not None else None
                
                # 標準化電燈狀態
                if light_value in ["on", "開", "1", "true", "開燈"]:
                    data_store['light_status'] = "開"
                elif light_value in ["off", "關", "0", "false", "關燈"]:
                    data_store['light_status'] = "關"
                elif light_value:
                    data_store['light_status'] = str(light_value)
                
                logger.info("更新電燈狀態: %s", data_store['light_status'])
            
            # 當有完整數據時，儲存到 Excel 和歷史記錄
            if (data_store['temperature'] is not None and 
                data_store['humidity'] is not None and 
                data_store['light_status'] != "未知"):
                
                # 儲存到 Excel
                try:
                    save_to_excel(
                        timestamp,
                        data_store['light_status'],
                        data_store['temperature'],
                        data_store['humidity']
                    )
                except Exception as e:
                    logger.error("儲存數據時發生錯誤: %s", e)
                
                # 更新歷史數據（限制記錄數量）
                history_record = {
                    "時間": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "電燈狀態": data_store['light_status'],
                    "溫度": data_store['temperature'],
                    "濕度": data_store['humidity']
                }
                data_store['history_data'].append(history_record)
                
                # 限制歷史記錄數量
                if len(data_store['history_data']) > MAX_HISTORY_RECORDS:
                    data_store['history_data'] = data_store['history_data'][-MAX_HISTORY_RECORDS:]
    
    except Exception as e:
        logger.error("處理 MQTT 訊息時發生錯誤: %s", e)

def init_mqtt():
    """初始化 MQTT 連線"""
    try:
        if data_store['mqtt_client'] is None:
            data_store['mqtt_client'] = MQTTClient(on_message_callback=on_mqtt_message)
            data_store['mqtt_client'].connect()
            data_store['connection_status'] = "連線中..."
            import time
            time.sleep(0.5)  # 等待連線建立
            if data_store['mqtt_client'].is_connected:
                data_store['connection_status'] = "已連線"
            else:
                data_store['connection_status'] = "連線失敗"
        elif not data_store['mqtt_client'].is_connected:
            data_store['mqtt_client'].connect()
            data_store['connection_status'] = "重新連線中..."
            import time
            time.sleep(0.5)
            if data_store['mqtt_client'].is_connected:
                data_store['connection_status'] = "已連線"
    except Exception as e:
        logger.error("初始化 MQTT 連線時發生錯誤: %s", e)
        data_store['connection_status'] = f"連線錯誤: {str(e)}"

def disconnect_mqtt():
    """斷開 MQTT 連線"""
    if data_store['mqtt_client']:
        data_store['mqtt_client'].disconnect()
        data_store['connection_status'] = "已斷線"

# Flask 路由
@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """獲取當前數據的 API"""
    with data_lock:
        return jsonify({
            'temperature': data_store['temperature'],
            'humidity': data_store['humidity'],
            'light_status': data_store['light_status'],
            'connection_status': data_store['connection_status'],
            'is_connected': data_store['mqtt_client'].is_connected if data_store['mqtt_client'] else False,
            'history_count': len(data_store['history_data'])
        })

@app.route('/api/history')
def get_history():
    """獲取歷史數據的 API"""
    with data_lock:
        return jsonify({
            'history': data_store['history_data'][-100:]  # 返回最近100筆
        })

@app.route('/api/connect', methods=['POST'])
def connect_mqtt():
    """連線 MQTT"""
    init_mqtt()
    with data_lock:
        return jsonify({
            'status': 'success',
            'connection_status': data_store['connection_status'],
            'is_connected': data_store['mqtt_client'].is_connected if data_store['mqtt_client'] else False
        })

@app.route('/api/disconnect', methods=['POST'])
def disconnect_mqtt_api():
    """斷開 MQTT 連線"""
    disconnect_mqtt()
    with data_lock:
        return jsonify({
            'status': 'success',
            'connection_status': data_store['connection_status']
        })

@app.route('/api/excel', methods=['GET'])
def get_excel_data():
    """獲取 Excel 數據"""
    try:
        df = read_excel_data()
        if not df.empty:
            return jsonify({
                'status': 'success',
                'data': df.to_dict('records')
            })
        else:
            return jsonify({
                'status': 'success',
                'data': []
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # 初始化 MQTT 連線
    init_mqtt()
    
    # 啟動 Flask 應用程式
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

