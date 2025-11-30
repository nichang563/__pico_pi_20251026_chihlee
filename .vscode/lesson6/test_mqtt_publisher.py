"""
MQTT 測試發布腳本
用於測試 Streamlit MQTT 監控應用程式
"""
import paho.mqtt.client as mqtt
import time
import json
import random

def main():
    """發送測試 MQTT 訊息"""
    print("正在連線到 MQTT Broker...")
    client = mqtt.Client()
    
    try:
        client.connect("localhost", 1883, 60)
        print("✅ 已連線到 MQTT Broker")
    except Exception as e:
        print(f"❌ 連線失敗: {e}")
        print("請確認 MQTT Broker 正在運行")
        return
    
    print("\n開始發送測試數據...")
    print("=" * 50)
    
    # 發送測試數據
    for i in range(10):
        # 溫度：20-30°C
        temp = round(20 + random.random() * 10, 1)
        temp_msg = json.dumps({"temperature": temp})
        client.publish("sensor/temperature", temp_msg)
        print(f"[{i+1}/10] 溫度: {temp}°C")
        
        time.sleep(0.5)
        
        # 濕度：40-70%
        hum = round(40 + random.random() * 30, 1)
        hum_msg = json.dumps({"humidity": hum})
        client.publish("sensor/humidity", hum_msg)
        print(f"      濕度: {hum}%")
        
        time.sleep(0.5)
        
        # 電燈狀態：輪流開關
        light_status = "on" if i % 2 == 0 else "off"
        light_msg = json.dumps({"status": light_status})
        client.publish("light/status", light_msg)
        print(f"      電燈: {light_status}")
        
        print("-" * 50)
        time.sleep(1)  # 每組數據間隔1秒
    
    client.disconnect()
    print("\n✅ 測試數據發送完成！")
    print("請檢查 Streamlit 應用程式是否正確接收並顯示數據")

if __name__ == "__main__":
    main()

