# MQTT 使用說明

## 📋 概述

主程式已整合 `umqtt.simple` 套件，可以每 10 秒發送一次 MQTT 訊息到指定的 Broker。

## 🔧 設定步驟

### 1. 修改 config.py

開啟 `config.py`，修改以下設定：

```python
MQTT_BROKER = "192.168.1.100"  # 改為 Raspberry Pi 的 IP 位址
MQTT_PORT = 1883
MQTT_TOPIC = "客廳/感測器"      # 可改為其他主題名稱
CLIENT_ID = "pico_lesson7"      # 可改為其他唯一 ID
```

**如何查詢 Raspberry Pi 的 IP？**
在 Raspberry Pi 終端機執行：
```bash
hostname -I
```

### 2. 確認 MQTT Broker 運行

在 Raspberry Pi 上確認 mosquitto 正在運行：
```bash
sudo systemctl status mosquitto
```

如果沒運行，啟動它：
```bash
sudo systemctl start mosquitto
```

## 📤 MQTT 訊息格式

程式會發送以下 JSON 格式的訊息：

```json
{
  "temperature": 25.5,
  "humidity": 60.0,
  "light_status": "開",
  "device": "Pico W Lesson7",
  "counter": 1,
  "ip": "192.168.1.50",
  "internet_ok": true
}
```

## 🔄 執行流程

```
啟動程式
    ↓
連線 WiFi
    ↓
連線 MQTT Broker
    ↓
進入主迴圈（每 10 秒）
    ↓
檢查 WiFi 狀態
    ↓
測試外部網路
    ↓
發送 MQTT 訊息
    ↓
等待 10 秒
    ↓
重複執行...
```

## 🛠️ 自訂數據內容

在 `main.py` 中，可以修改 `payload` 字典來發送不同的數據：

```python
payload = {
    "temperature": 25.5,  # 改為實際感測器讀取
    "humidity": 60.0,      # 改為實際感測器讀取
    "light_status": "開",  # 改為實際 LED 狀態
    "device": "Pico W Lesson7",
    "counter": counter,
    "ip": wifi.get_ip(),
    "internet_ok": internet_ok
}
```

### 範例：讀取實際感測器數據

```python
import machine

# 讀取內建溫度感測器
sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)

def read_temperature():
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706) / 0.001721
    return round(temperature, 1)

# 在主迴圈中使用
payload = {
    "temperature": read_temperature(),  # 使用實際讀取的值
    "humidity": 60.0,
    "light_status": "開",
    # ... 其他欄位
}
```

## 🧪 測試 MQTT 接收

在 Raspberry Pi 上測試是否收到訊息：

```bash
mosquitto_sub -h localhost -t "客廳/感測器" -v
```

應該會看到類似以下的輸出：
```
客廳/感測器 {"temperature": 25.5, "humidity": 60.0, ...}
```

## ⚠️ 錯誤處理

程式包含以下錯誤處理機制：

1. **WiFi 斷線**：自動嘗試重新連線
2. **MQTT 斷線**：自動嘗試重新連線
3. **發送失敗**：顯示錯誤訊息並繼續執行

## 📝 注意事項

1. **Topic 名稱**：必須與接收端（Flask 應用程式）的 Topic 完全一致
2. **Client ID**：每個 Pico W 應該使用不同的 Client ID
3. **JSON 格式**：確保使用 `json.dumps()` 序列化數據
4. **網路連線**：確保 WiFi 和 MQTT Broker 都在同一網路

## 🔍 除錯技巧

如果 MQTT 訊息無法發送：

1. **檢查連線狀態**：確認程式輸出顯示 "✅ MQTT 連線成功"
2. **測試 MQTT Broker**：使用 `mosquitto_sub` 測試是否能接收訊息
3. **檢查 IP 位址**：確認 `config.py` 中的 IP 是否正確
4. **檢查防火牆**：確認 Raspberry Pi 的防火牆允許 1883 端口

