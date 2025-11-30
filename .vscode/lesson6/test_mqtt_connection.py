"""
MQTT 連線測試腳本
用於診斷 MQTT 連線和訊息接收問題
"""
import paho.mqtt.client as mqtt
import time
import json

def on_connect(client, userdata, flags, rc):
    """連線回調"""
    if rc == 0:
        print("✅ 成功連線到 MQTT Broker")
        # 訂閱所有 topics
        topics = [
            "sensor/temperature",
            "sensor/humidity", 
            "light/status"
        ]
        for topic in topics:
            client.subscribe(topic)
            print(f"✅ 已訂閱: {topic}")
    else:
        print(f"❌ 連線失敗，錯誤代碼: {rc}")

def on_message(client, userdata, msg):
    """訊息接收回調"""
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    print(f"\n📨 收到訊息:")
    print(f"   Topic: {topic}")
    print(f"   Payload: {payload}")
    try:
        data = json.loads(payload)
        print(f"   JSON 解析: {data}")
    except:
        print(f"   (非 JSON 格式)")

def test_connection():
    """測試 MQTT 連線"""
    print("=" * 50)
    print("MQTT 連線測試")
    print("=" * 50)
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        print("\n正在連線到 localhost:1883...")
        client.connect("localhost", 1883, 60)
        client.loop_start()
        
        print("\n等待 5 秒接收訊息...")
        print("請在另一個終端機執行以下命令發送測試訊息：")
        print("  mosquitto_pub -h localhost -t sensor/temperature -m '{\"temperature\": 25.5}'")
        print("\n或使用測試腳本：")
        print("  python test_mqtt_publisher.py")
        
        time.sleep(5)
        
        print("\n" + "=" * 50)
        print("測試完成")
        print("=" * 50)
        
        client.loop_stop()
        client.disconnect()
        
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        print("\n請確認：")
        print("1. MQTT Broker 正在運行: sudo systemctl status mosquitto")
        print("2. MQTT Broker 監聽在 localhost:1883")

if __name__ == "__main__":
    test_connection()

