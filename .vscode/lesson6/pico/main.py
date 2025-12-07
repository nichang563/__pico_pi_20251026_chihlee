"""
Pico W MQTT 感測器監控
發送溫濕度和電燈狀態到 Flask 監控系統
"""
import json
import network
import time
from machine import Pin
import dht

# 簡化版 MQTT 客戶端（如果沒有 umqtt 模組）
try:
    from umqtt.simple import MQTTClient
except ImportError:
    print("⚠️  umqtt 模組未安裝")
    print("請在 Thonny 中安裝: Tools -> Manage packages -> micropython-umqtt.simple")
    import sys
    sys.exit()

# ========== WiFi 設定 ==========
WIFI_SSID = "你的WiFi名稱"
WIFI_PASSWORD = "你的WiFi密碼"

# ========== MQTT 設定 ==========
MQTT_BROKER = "192.168.1.100"  # 替換成你的電腦 IP
MQTT_PORT = 1883
MQTT_TOPIC = "客廳/感測器"
CLIENT_ID = "pico_sensor"

# ========== 硬體設定 ==========
led = Pin(15, Pin.OUT)  # LED 控制腳位
sensor = dht.DHT11(Pin(16))  # DHT11 感測器腳位（或使用 DHT22）

def connect_wifi():
    """連接 WiFi"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    print("正在連接 WiFi...")
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("等待連線...")
        time.sleep(1)
    
    if wlan.status() != 3:
        raise RuntimeError("WiFi 連線失敗")
    else:
        print("✅ WiFi 已連接")
        status = wlan.ifconfig()
        print(f"   IP: {status[0]}")
        return status[0]

def connect_mqtt():
    """連接 MQTT Broker"""
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, MQTT_PORT)
    client.connect()
    print("✅ MQTT 已連接")
    return client

def main():
    """主程式"""
    # 連接 WiFi
    connect_wifi()
    
    # 連接 MQTT
    client = connect_mqtt()
    
    print(f"開始發送數據到主題: {MQTT_TOPIC}")
    
    while True:
        try:
            # 讀取感測器數據
            sensor.measure()
            temp = sensor.temperature()
            humi = sensor.humidity()
            light = "開" if led.value() else "關"
            
            # 建立 JSON 訊息
            payload = json.dumps({
                "temperature": temp,
                "humidity": humi,
                "light_status": light
            })
            
            # 發送 MQTT 訊息
            client.publish(MQTT_TOPIC, payload)
            print(f"📤 已發送: 溫度={temp}°C, 濕度={humi}%, 電燈={light}")
            
            # 每 5 秒發送一次
            time.sleep(5)
            
        except OSError as e:
            print(f"感測器讀取錯誤: {e}")
            time.sleep(2)
        except Exception as e:
            print(f"發生錯誤: {e}")
            # 嘗試重新連接
            try:
                client = connect_mqtt()
            except:
                print("MQTT 重連失敗，等待 10 秒後重試...")
                time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程式已停止")
    except Exception as e:
        print(f"錯誤: {e}")
