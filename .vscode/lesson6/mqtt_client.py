"""
MQTT 客戶端模組 - 處理 MQTT 連線和訂閱
"""
import json
import logging
import threading
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from config import MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE, TOPICS

logger = logging.getLogger(__name__)

class MQTTClient:
    """MQTT 客戶端類別，處理連線、訂閱和訊息接收"""
    
    def __init__(self, on_message_callback=None):
        """
        初始化 MQTT 客戶端
        
        Args:
            on_message_callback: 當收到訊息時的回調函數，接收 (topic, payload) 參數
        """
        self.client = None
        self.is_connected = False
        self.on_message_callback = on_message_callback
        self.reconnect_delay = 5  # 重連延遲（秒）
        self.reconnect_thread = None
        self.stop_reconnect = False
        
    def on_connect(self, client, userdata, flags, rc):
        """連線回調函數"""
        if rc == 0:
            self.is_connected = True
            logger.info(f"成功連線到 MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
            
            # 訂閱所有 topics（使用 QoS 1 確保訊息送達）
            for topic_name, topic_path in TOPICS.items():
                result = client.subscribe(topic_path, qos=1)
                if result[0] == 0:
                    logger.info(f"✅ 已訂閱 Topic: {topic_path}")
                else:
                    logger.error(f"❌ 訂閱失敗 Topic: {topic_path}, 錯誤代碼: {result[0]}")
        else:
            self.is_connected = False
            logger.error(f"連線失敗，錯誤代碼: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """斷線回調函數"""
        self.is_connected = False
        logger.warning(f"MQTT 連線已斷開，錯誤代碼: {rc}")
        
        # 如果不是正常斷線，啟動自動重連
        if rc != 0:
            self._start_reconnect_thread()
    
    def on_message(self, client, userdata, msg):
        """訊息接收回調函數"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.info(f"收到訊息 - Topic: {topic}, Payload: {payload}")
            print(f"[MQTT] 收到訊息 - Topic: {topic}, Payload: {payload}")  # 確保輸出到終端機
            
            # 解析 JSON 格式的 payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                # 如果不是 JSON，嘗試直接使用 payload
                data = payload
            
            # 調用自定義回調函數
            if self.on_message_callback:
                try:
                    self.on_message_callback(topic, data)
                    print(f"[MQTT] 回調函數執行完成")  # 確認回調被調用
                except Exception as callback_error:
                    logger.error(f"執行回調函數時發生錯誤: {callback_error}")
                    print(f"[MQTT] 回調函數錯誤: {callback_error}")
                
        except Exception as e:
            logger.error(f"處理 MQTT 訊息時發生錯誤: {e}")
            print(f"[MQTT] 處理訊息錯誤: {e}")
    
    def connect(self):
        """建立 MQTT 連線"""
        try:
            if self.client is None:
                self.client = mqtt.Client()
                self.client.on_connect = self.on_connect
                self.client.on_disconnect = self.on_disconnect
                self.client.on_message = self.on_message
            
            if not self.is_connected:
                self.client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
                # 啟動背景執行緒處理 MQTT 訊息
                self.client.loop_start()
                logger.info(f"正在連線到 MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
                
        except Exception as e:
            logger.error(f"連線 MQTT Broker 時發生錯誤: {e}")
            self._start_reconnect_thread()
    
    def disconnect(self):
        """斷開 MQTT 連線"""
        self.stop_reconnect = True
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
            logger.info("MQTT 連線已斷開")
    
    def _start_reconnect_thread(self):
        """啟動自動重連執行緒"""
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            return
        
        self.stop_reconnect = False
        self.reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True)
        self.reconnect_thread.start()
    
    def _reconnect_loop(self):
        """自動重連循環"""
        while not self.stop_reconnect and not self.is_connected:
            try:
                logger.info(f"等待 {self.reconnect_delay} 秒後嘗試重新連線...")
                time.sleep(self.reconnect_delay)
                
                if not self.stop_reconnect:
                    logger.info("嘗試重新連線到 MQTT Broker...")
                    self.connect()
                    
                    # 等待一下確認連線狀態
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"自動重連時發生錯誤: {e}")

