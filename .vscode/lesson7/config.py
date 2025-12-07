# config.py
# MQTT 設定檔

# MQTT Broker 設定
# 請使用 'hostname -I' 在 Raspberry Pi 上查詢 IP
# 例如: "192.168.1.100"
MQTT_BROKER = "192.168.1.XXX"  # 請修改為 Raspberry Pi 的 IP
MQTT_PORT = 1883
MQTT_TOPIC = "客廳/感測器"  # MQTT 主題名稱
CLIENT_ID = "pico_lesson7"  # MQTT 客戶端 ID（需唯一）

