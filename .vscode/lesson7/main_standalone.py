# main_standalone.py
# 獨立版本：不需要 config.py，所有設定都在這個檔案中

import wifi_connect as wifi
import time
import json
from umqtt.simple import MQTTClient

# ============================================
# MQTT 設定（請修改這裡的 IP 位址）
# ============================================
MQTT_BROKER = "192.168.1.XXX"  # 請修改為 Raspberry Pi 的 IP 位址
MQTT_PORT = 1883
MQTT_TOPIC = "客廳/感測器"  # MQTT 主題名稱
CLIENT_ID = "pico_lesson7"  # MQTT 客戶端 ID（需唯一）

# ============================================
# 主程式
# ============================================

# 嘗試連線 WiFi
print("=" * 50)
print("初始化 WiFi 連線...")
print("=" * 50)
wifi.connect()

# 顯示 IP
ip = wifi.get_ip()
if ip:
    print(f"✅ IP 位址: {ip}")
else:
    print("❌ 無法取得 IP 位址")
    print("程式無法繼續執行")
    exit()

# 連線 MQTT Broker
print("\n" + "=" * 50)
print("初始化 MQTT 連線...")
print("=" * 50)
print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
print(f"Topic: {MQTT_TOPIC}")
print(f"Client ID: {CLIENT_ID}")

try:
    mqtt_client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    mqtt_client.connect()
    print("✅ MQTT 連線成功")
except Exception as e:
    print(f"❌ MQTT 連線失敗: {e}")
    print("請確認:")
    print("1. MQTT Broker 是否正在運行")
    print("2. MQTT_BROKER IP 是否正確（請修改檔案中的 IP）")
    print("3. 防火牆是否允許 1883 端口")
    exit()

# 主迴圈：每隔 10 秒發布一次 MQTT 訊息
print("\n" + "=" * 50)
print("📤 MQTT Publisher 模式")
print("每 10 秒發布一次訊息到 Topic: " + MQTT_TOPIC)
print("按 Ctrl+C 可停止程式")
print("=" * 50 + "\n")

counter = 0

try:
    while True:
        counter += 1
        current_time = time.time()
        timestamp = time.localtime(current_time)
        time_str = f"{timestamp[3]:02d}:{timestamp[4]:02d}:{timestamp[5]:02d}"
        
        print(f"\n[{counter}] {time_str} - 準備發布 MQTT 訊息...")
        
        # 檢查 WiFi 連線狀態
        if not wifi.is_connected():
            print("  ⚠️  WiFi 已斷線，嘗試重新連線...")
            try:
                wifi.connect()
            except Exception as e:
                print(f"  ❌ 重新連線失敗: {e}")
                print("  等待 10 秒後重試...")
                time.sleep(10)
                continue
        
        # 檢查外部網路
        internet_ok = wifi.test_internet()
        if internet_ok:
            print("  ✅ 外部網路連線正常")
        else:
            print("  ⚠️  外部網路無法連線")
        
        # 準備 MQTT 訊息
        payload = {
            "temperature": 25.5,
            "humidity": 60.0,
            "light_status": "開",
            "device": "Pico W Lesson7",
            "counter": counter,
            "ip": wifi.get_ip(),
            "internet_ok": internet_ok,
            "timestamp": time_str
        }
        
        # 發布 MQTT 訊息
        try:
            message = json.dumps(payload, ensure_ascii=False)
            result = mqtt_client.publish(MQTT_TOPIC, message)
            
            if result == 0:  # 0 表示成功
                print(f"  ✅ MQTT 訊息發布成功")
                print(f"     Topic: {MQTT_TOPIC}")
                print(f"     Payload: {message}")
            else:
                print(f"  ⚠️  MQTT 發布返回碼: {result}")
        except Exception as e:
            print(f"  ❌ MQTT 發布失敗: {e}")
            # 嘗試重新連線 MQTT
            try:
                print("  🔄 嘗試重新連線 MQTT...")
                mqtt_client.connect()
                print("  ✅ MQTT 重新連線成功")
            except Exception as e2:
                print(f"  ❌ MQTT 重新連線失敗: {e2}")
        
        print(f"  ⏳ 等待 10 秒後發布下一次訊息...")
        time.sleep(10)

except KeyboardInterrupt:
    print("\n\n程式停止中...")
    try:
        mqtt_client.disconnect()
        print("✅ MQTT 連線已斷開")
    except:
        pass
    print("程式已停止")
    
except Exception as e:
    print(f"\n❌ 發生錯誤: {e}")
    try:
        mqtt_client.disconnect()
    except:
        pass

