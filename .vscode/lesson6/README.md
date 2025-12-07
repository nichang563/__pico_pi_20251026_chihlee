# MQTT 感測器監控應用程式

根據 [PRD.md](PRD.md) 規格實作的感測器數據即時監控儀表板。

## 📋 專案說明

本專案實作一個基於 Web 的 MQTT 監控系統，用於即時顯示和記錄感測器數據。

### ⚠️ 技術變更說明

由於 Streamlit 及其依賴套件（pandas, pyarrow）與 Raspberry Pi ARM64 架構存在相容性問題（SIGILL 錯誤），專案改用 **Flask + Socket.IO** 實作，提供更好的效能和穩定性。

## ✨ 主要功能

- 💡 **即時電燈狀態顯示** - 大型圓形視覺化指示器
- 🌡️ **客廳溫度監控** - 即時數值顯示和歷史趨勢
- 💧 **客廳濕度監控** - 即時數值顯示和歷史趨勢
- 📈 **雙 Y 軸歷史圖表** - 互動式數據視覺化
- 💾 **自動數據儲存** - CSV 和 Excel 格式
- 🔄 **WebSocket 即時推送** - 無需手動重新整理
- 📱 **響應式設計** - 支援手機和桌面瀏覽器

## 🚀 快速開始

### 方式 1：使用啟動腳本（推薦）

```bash
cd /home/pi/Documents/GitHub/2025_10_26_chihlee_pi_pico/lesson6
./start.sh
```

### 方式 2：手動啟動

```bash
cd /home/pi/Documents/GitHub/2025_10_26_chihlee_pi_pico/lesson6
uv run python app_flask.py
```

### 開啟網頁

在瀏覽器中訪問：
- 本地：http://localhost:8080
- 區域網路：http://172.20.10.3:8080

## 📊 測試數據

專案已包含 50 筆測試數據，啟動後即可看到完整的數據和圖表。

### 重新生成測試數據

```bash
uv run python generate_test_data.py
```

### 發送即時 MQTT 測試數據

在另一個終端機中執行：

```bash
uv run python test_mqtt_publish.py
```

## 📁 檔案結構

### ✅ 主要檔案（可用）

| 檔案 | 說明 |
|------|------|
| `app_flask.py` | **Flask 主應用程式**（推薦使用） |
| `templates/index.html` | 網頁前端介面 |
| `sensor_data.csv` | CSV 格式數據檔案 |
| `sensor_data.xlsx` | Excel 格式數據檔案 |
| `test_mqtt_publish.py` | MQTT 測試發布工具 |
| `generate_test_data.py` | 測試數據生成工具 |
| `start.sh` | 應用程式啟動腳本 |
| `PRD.md` | 產品需求文件 |
| `啟動應用程式.md` | 詳細使用說明 |
| `使用說明.md` | 技術細節和故障排除 |

### ⚠️ 已棄用檔案（相容性問題）

| 檔案 | 狀態 |
|------|------|
| `app.py` | ❌ Streamlit 版本（ARM 不相容） |
| `config.py`, `data_manager.py`, `mqtt_client.py` | ⚠️ 僅供 Streamlit 版本使用 |

## 🔧 MQTT 設定

### 確認 MQTT Broker 運行中

```bash
# 檢查 mosquitto 狀態
sudo systemctl status mosquitto

# 啟動 mosquitto
sudo systemctl start mosquitto

# 設定開機自動啟動
sudo systemctl enable mosquitto
```

### MQTT 訊息格式

發送到主題 `客廳/感測器` 的訊息應為 JSON 格式：

```json
{
  "temperature": 25.5,
  "humidity": 60.0,
  "light_status": "開"
}
```

支援的欄位名稱：
- 溫度：`temperature` 或 `temp`
- 濕度：`humidity` 或 `humi`
- 電燈：`light_status` 或 `light`

## 📡 Pico W 整合指南

### 連線參數

| 參數 | 值 | 說明 |
|------|---|------|
| **MQTT Broker** | 電腦 IP 位址 | 例如：`192.168.1.100` |
| **MQTT Port** | `1883` | 預設 MQTT 埠 |
| **MQTT Topic** | `客廳/感測器` | 必須完全相同（含中文） |
| **Client ID** | `pico_sensor` | 或任意唯一名稱 |

### Pico W 範例程式碼

```python
import json
import network
import time
from umqtt.simple import MQTTClient
from machine import Pin
import dht

# WiFi 設定
WIFI_SSID = "你的WiFi名稱"
WIFI_PASSWORD = "你的WiFi密碼"

# MQTT 設定
MQTT_BROKER = "192.168.1.100"  # 替換成你的電腦 IP
MQTT_PORT = 1883
MQTT_TOPIC = "客廳/感測器"
CLIENT_ID = "pico_sensor"

# 硬體設定
led = Pin(15, Pin.OUT)  # LED 控制腳位
sensor = dht.DHT11(Pin(16))  # DHT11 感測器腳位（或使用 DHT22）

# 連接 WiFi
def connect_wifi():
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

# 連接 MQTT
def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, MQTT_PORT)
    client.connect()
    print("✅ MQTT 已連接")
    return client

# 主程式
def main():
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

# 執行主程式
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程式已停止")
    except Exception as e:
        print(f"錯誤: {e}")
```

### 📝 訊息格式說明

**方式 1：使用完整欄位名稱（推薦）**
```json
{
  "temperature": 25.6,
  "humidity": 65.2,
  "light_status": "開"
}
```

**方式 2：使用簡短欄位名稱**
```json
{
  "temp": 25.6,
  "humi": 65.2,
  "light": "開"
}
```

### 🔑 重要提醒

1. **電燈狀態必須使用中文**：`"開"` 或 `"關"`（不是 "on"/"off"）
2. **Topic 名稱必須完全相同**：包含中文字元 `客廳/感測器`
3. **數值型態**：溫度和濕度必須是數字（int 或 float）
4. **JSON 格式**：使用 `json.dumps()` 序列化，確保格式正確
5. **QoS 建議**：發布時可設定 QoS=1 確保訊息送達

### 📦 所需的 MicroPython 函式庫

在 Pico W 上需要安裝：
- `umqtt.simple` - MQTT 客戶端（通常已內建）
- DHT 感測器驅動（如果使用 DHT11/DHT22）

### 🧪 測試步驟

1. 修改程式中的 WiFi 和 MQTT Broker IP
2. 上傳程式到 Pico W
3. 啟動 Flask 應用程式
4. 執行 Pico W 程式
5. 在網頁上即可看到即時數據更新

## 📈 效能比較

| 項目 | Streamlit 版本 | Flask 版本 |
|------|---------------|-----------|
| ARM 相容性 | ❌ 不相容（SIGILL） | ✅ 完全相容 |
| 記憶體佔用 | ~300MB | ~50MB |
| 啟動速度 | 5-10 秒 | < 1 秒 |
| 即時更新 | 需重新整理 | WebSocket 自動推送 |
| CPU 佔用 | 高 | 低 |

## 🐛 常見問題

### Q1: 應用程式無法啟動

確認已安裝必要套件：
```bash
cd /home/pi/Documents/GitHub/2025_10_26_chihlee_pi_pico
uv sync
```

### Q2: 網頁無法開啟

檢查防火牆設定：
```bash
sudo ufw allow 8080
```

### Q3: 無法連線 MQTT

```bash
# 確認 mosquitto 正在運行
sudo systemctl status mosquitto

# 測試 MQTT 連線
mosquitto_sub -h localhost -t "客廳/感測器" -v
```

### Q4: 沒有顯示數據

1. 檢查測試數據檔案是否存在：`ls -lh sensor_data.csv`
2. 重新生成測試數據：`uv run python generate_test_data.py`
3. 查看應用程式日誌，確認是否成功載入數據

## 🛠️ 技術棧

- **後端框架**：Flask 3.1.2
- **即時通訊**：Flask-SocketIO 5.5.1
- **MQTT 客戶端**：paho-mqtt 2.1.0+
- **數據儲存**：CSV（標準庫）+ Excel（openpyxl）
- **前端技術**：HTML5 + JavaScript + Chart.js
- **WebSocket**：Socket.IO 4.5.4

## 📖 進階使用

詳細的使用說明和技術細節請參閱：
- [啟動應用程式.md](啟動應用程式.md) - 快速啟動指南
- [使用說明.md](使用說明.md) - 完整技術文檔和故障排除
- [PRD.md](PRD.md) - 產品需求規格

## 📝 數據儲存

數據自動儲存到以下檔案：
- `sensor_data.csv` - CSV 格式（應用程式使用）
- `sensor_data.xlsx` - Excel 格式（人工查看）

包含欄位：
- 時間戳記
- 電燈狀態
- 溫度（°C）
- 濕度（%）

## 🎯 背景運行

如需背景運行應用程式：

```bash
# 啟動
nohup uv run python app_flask.py > app.log 2>&1 &

# 查看日誌
tail -f app.log

# 停止
pkill -f "python app_flask.py"
```

## 📜 授權

本專案遵循 [LICENSE](../LICENSE) 中的授權條款。

## 🙏 致謝

感謝使用本專案！如有問題或建議，歡迎提出 Issue。

