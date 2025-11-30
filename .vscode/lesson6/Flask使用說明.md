# Flask MQTT 監控應用程式 - 使用說明

## 安裝依賴

```bash
cd /home/pi/pico_pi_20251026_chihlee
uv pip install flask pandas openpyxl paho-mqtt
```

## 啟動應用程式

```bash
cd /home/pi/pico_pi_20251026_chihlee/.vscode/lesson6
/home/pi/pico_pi_20251026_chihlee/.venv/bin/python app_flask.py
```

或使用 uv：

```bash
cd /home/pi/pico_pi_20251026_chihlee/.vscode/lesson6
uv run python app_flask.py
```

## 訪問應用程式

在瀏覽器中打開：
```
http://localhost:5000
```

或從其他設備訪問（使用樹莓派的 IP 地址）：
```
http://<樹莓派IP>:5000
```

## 功能說明

### 1. 連線控制
- 點擊「🔌 連線 MQTT」按鈕連線到 MQTT Broker
- 點擊「❌ 斷開連線」按鈕斷開連線
- 連線狀態會顯示在頁面上

### 2. 數據顯示
- **電燈狀態**：顯示開/關狀態
- **溫度**：顯示當前溫度（°C）
- **濕度**：顯示當前濕度（%）
- 數據會每1秒自動更新

### 3. 歷史趨勢圖
- 使用 Chart.js 顯示溫濕度歷史趨勢
- 自動更新圖表數據

### 4. 調試資訊
- 顯示連線狀態、當前數據值、歷史記錄數等資訊

## API 端點

### GET /api/data
獲取當前數據
```json
{
  "temperature": 25.5,
  "humidity": 60,
  "light_status": "開",
  "connection_status": "已連線",
  "is_connected": true,
  "history_count": 10
}
```

### GET /api/history
獲取歷史數據（最近100筆）

### POST /api/connect
連線 MQTT

### POST /api/disconnect
斷開 MQTT 連線

### GET /api/excel
獲取 Excel 檔案中的數據

## 測試

### 1. 確認 MQTT Broker 運行
```bash
sudo systemctl status mosquitto
```

### 2. 發送測試訊息
```bash
# 發送溫度
mosquitto_pub -h localhost -t sensor/temperature -m '{"temperature": 25.5}'

# 發送濕度
mosquitto_pub -h localhost -t sensor/humidity -m '{"humidity": 60}'

# 發送電燈狀態
mosquitto_pub -h localhost -t light/status -m '{"status": "on"}'
```

### 3. 檢查結果
- 網頁應該會自動更新顯示數據
- 圖表應該會顯示歷史趨勢
- Excel 檔案會自動生成並儲存數據

## 與 Streamlit 版本的差異

1. **架構**：使用 Flask + HTML/CSS/JavaScript 替代 Streamlit
2. **即時更新**：使用 JavaScript 輪詢（每1秒）替代 Streamlit 的自動刷新
3. **UI**：使用自定義 HTML/CSS 設計，更靈活
4. **API**：提供 RESTful API 端點，可以與其他應用程式整合

## 故障排除

### 問題：無法訪問網頁
- 確認 Flask 應用程式正在運行
- 檢查防火牆設定
- 確認端口 5000 未被占用

### 問題：收不到 MQTT 數據
- 確認 MQTT Broker 正在運行
- 點擊「連線 MQTT」按鈕
- 檢查瀏覽器控制台是否有錯誤
- 檢查 Flask 終端機輸出

### 問題：圖表不顯示
- 確認網路連線正常（需要載入 Chart.js）
- 檢查瀏覽器控制台是否有 JavaScript 錯誤

