# 檢查 MQTT 連線問題

## 問題診斷

如果 Web 頁面沒有更新數據，請檢查以下項目：

### 1. 確認 MQTT Broker 設定

**Flask 應用程式** (`app_flask.py`):
```python
MQTT_BROKER = "localhost"  # 第 19 行
```

**Pico W** (`main.py`):
```python
MQTT_BROKER = "192.168.137.196"  # 第 8 行
```

**問題**：如果 Flask 應用程式和 Pico W 連接到不同的 MQTT Broker，就不會收到訊息。

### 2. 確認 MQTT Broker 正在運行

在 Raspberry Pi 上執行：
```bash
sudo systemctl status mosquitto
```

如果沒運行，啟動它：
```bash
sudo systemctl start mosquitto
```

### 3. 測試 MQTT 訊息接收

在 Raspberry Pi 上執行（測試是否能收到訊息）：
```bash
mosquitto_sub -h localhost -t "客廳/感測器" -v
```

如果能看到訊息，表示 MQTT Broker 正常運作。

### 4. 檢查 Flask 應用程式日誌

查看 Flask 應用程式的輸出，應該會看到：
```
✅ MQTT 連線成功
✅ 已訂閱主題: 客廳/感測器
📨 收到訊息: {"temperature": 25.5, ...}
```

如果沒有看到這些訊息，表示：
- MQTT 連線失敗
- 沒有收到訊息

### 5. 確認 Topic 名稱一致

**Flask 應用程式**:
```python
MQTT_TOPIC = "客廳/感測器"
```

**Pico W**:
```python
TOPIC = "客廳/感測器"
```

必須**完全相同**（包括中文字元）。

## 解決方案

### 方案 1：確認 MQTT Broker 在同一台機器

如果 MQTT Broker 在 Raspberry Pi 上（localhost），則：
- Flask 應用程式：`MQTT_BROKER = "localhost"` ✅
- Pico W：`MQTT_BROKER = "192.168.137.196"` ✅（Raspberry Pi 的 IP）

### 方案 2：確認 Flask 應用程式連線狀態

檢查 Flask 應用程式啟動時的輸出：
```
✅ MQTT 連線成功
✅ 已訂閱主題: 客廳/感測器
```

如果看到 `❌ MQTT 連線失敗`，請檢查：
1. MQTT Broker 是否正在運行
2. 防火牆是否允許 1883 端口

### 方案 3：手動測試 MQTT

在 Raspberry Pi 上發布測試訊息：
```bash
mosquitto_pub -h localhost -t "客廳/感測器" -m '{"temperature": 25.5, "humidity": 60.0, "light_status": "開"}'
```

然後檢查 Flask 應用程式是否收到訊息。

### 方案 4：檢查 WebSocket 連線

打開瀏覽器開發者工具（F12），查看 Console 是否有錯誤訊息。

檢查 Network 標籤，確認 WebSocket 連線是否建立。

## 常見問題

### Q1: Flask 應用程式顯示 "MQTT 連線成功" 但沒有收到訊息？

**可能原因**：
- Topic 名稱不一致
- MQTT Broker 設定錯誤
- 訊息格式不正確

**解決方法**：
1. 確認 Topic 名稱完全一致
2. 使用 `mosquitto_sub` 測試是否能收到訊息
3. 檢查訊息格式是否為有效的 JSON

### Q2: 看到 "收到訊息" 但 Web 頁面沒有更新？

**可能原因**：
- WebSocket 連線問題
- 前端 JavaScript 錯誤

**解決方法**：
1. 檢查瀏覽器 Console 是否有錯誤
2. 重新整理頁面
3. 檢查 `socketio.emit('new_data', latest_data)` 是否正常執行

### Q3: 如何確認訊息是否真的發送到 MQTT Broker？

在 Raspberry Pi 上執行：
```bash
mosquitto_sub -h localhost -t "客廳/感測器" -v
```

如果能看到 Pico W 發送的訊息，表示 MQTT 發布正常。

