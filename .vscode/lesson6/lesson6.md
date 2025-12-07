# Lesson6 Flask MQTT 監控專案 - 完整分析文檔

## 📋 專案概述

這是一個基於 Flask 的 MQTT 感測器監控系統，用於即時顯示和記錄電燈狀態、溫度、濕度等感測器數據。專案採用 Flask + Socket.IO 架構，提供 WebSocket 即時推送功能，替代了原本的 Streamlit 版本以解決 Raspberry Pi ARM64 相容性問題。

---

## 🏗️ 專案架構

### 檔案結構

```
lesson6/
├── app_flask.py              # Flask 主應用程式（核心檔案）
├── templates/
│   └── index.html            # 前端網頁介面
├── sensor_data.csv           # CSV 格式數據儲存
├── sensor_data.xlsx          # Excel 格式數據儲存
├── generate_test_data.py     # 測試數據生成工具
├── test_mqtt_publish.py      # MQTT 測試發布工具
├── start.sh                  # 啟動腳本
└── README.md                 # 專案說明文檔
```

### 技術棧

- **後端框架**: Flask 3.1.2
- **即時通訊**: Flask-SocketIO 5.5.1
- **MQTT 客戶端**: paho-mqtt 2.1.0+
- **數據儲存**: CSV（標準庫）+ Excel（openpyxl）
- **前端技術**: HTML5 + JavaScript + Chart.js
- **WebSocket**: Socket.IO 4.5.4

---

## 🔄 程式邏輯流程

### 1. 應用程式啟動流程

```
啟動 app_flask.py
    ↓
載入歷史數據 (load_from_csv)
    ↓
初始化 MQTT 客戶端
    ↓
在背景執行緒啟動 MQTT 連線 (start_mqtt)
    ↓
啟動 Flask 伺服器 (socketio.run)
    ↓
監聽 HTTP 請求與 WebSocket 連線
```

### 2. MQTT 數據接收流程

```
MQTT Broker 收到訊息
    ↓
on_message 回調函數觸發
    ↓
解析 JSON 格式的 payload
    ↓
提取數據（溫度、濕度、電燈狀態）
    ↓
更新 latest_data（最新數據）
    ↓
追加到 sensor_data 列表（歷史數據）
    ↓
限制歷史數據數量（最多 100 筆）
    ↓
儲存到 CSV 檔案 (save_to_csv)
    ↓
透過 WebSocket 推送到前端 (socketio.emit)
```

### 3. 前端數據更新流程

```
網頁載入 (index.html)
    ↓
初始化 Socket.IO 連線
    ↓
初始化 Chart.js 圖表
    ↓
發送 HTTP GET /api/latest 請求
    ↓
發送 HTTP GET /api/history 請求
    ↓
顯示初始數據
    ↓
監聽 WebSocket 'new_data' 事件
    ↓
收到新數據時自動更新顯示
    ↓
每 5 秒更新一次歷史圖表
```

### 4. API 端點說明

| 端點 | 方法 | 功能 | 回傳格式 |
|------|------|------|----------|
| `/` | GET | 主頁面 | HTML |
| `/api/latest` | GET | 取得最新數據 | JSON |
| `/api/history` | GET | 取得歷史數據 | JSON |

---

## 🔧 可手動修改的部分

### 1. MQTT 設定（app_flask.py）

**位置**: 第 18-21 行

```python
# MQTT 設定
MQTT_BROKER = "localhost"      # 可改為其他 IP 或主機名
MQTT_PORT = 1883               # 可改為其他端口
MQTT_TOPIC = "客廳/感測器"      # 可改為其他主題名稱
```

**修改建議**:
- 如果 MQTT Broker 在其他機器，修改 `MQTT_BROKER` 為該機器的 IP 地址
- 如果使用非標準端口，修改 `MQTT_PORT`
- 如果使用不同的主題名稱，修改 `MQTT_TOPIC`（注意：必須與發送端一致）

### 2. 數據儲存設定（app_flask.py）

**位置**: 第 34 行

```python
CSV_FILE = 'sensor_data.csv'   # 可改為其他檔案名稱或路徑
```

**修改建議**:
- 可改為絕對路徑，例如：`/home/pi/data/sensor_data.csv`
- 可改為其他檔案名稱，例如：`room1_sensor_data.csv`

### 3. 歷史數據保留數量（app_flask.py）

**位置**: 第 54 行和第 119 行

```python
# 只保留最近 100 筆
sensor_data = loaded_data[-100:]  # 載入時
if len(sensor_data) > 100:        # 運行時
    sensor_data.pop(0)
```

**修改建議**:
- 可改為其他數量，例如：`[-200:]` 和 `> 200` 保留 200 筆
- 注意：保留太多數據會增加記憶體使用

### 4. Flask 伺服器設定（app_flask.py）

**位置**: 第 187 行

```python
socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)
```

**修改建議**:
- `host='0.0.0.0'`: 允許外部訪問（改為 `'127.0.0.1'` 僅允許本機）
- `port=8080`: 可改為其他端口，例如：`5000`, `3000`
- `debug=False`: 改為 `True` 可啟用除錯模式（開發時使用）

### 5. 前端更新頻率（templates/index.html）

**位置**: 第 330 行

```javascript
// 定期更新歷史圖表
setInterval(fetchHistory, 5000);  // 每 5 秒更新一次
```

**修改建議**:
- 可改為其他間隔，例如：`3000`（3 秒）或 `10000`（10 秒）
- 注意：更新太頻繁會增加伺服器負載

### 6. 圖表顯示設定（templates/index.html）

**位置**: 第 200-251 行

**可修改項目**:
- **圖表類型**: `type: 'line'` 可改為 `'bar'`, `'scatter'` 等
- **顏色設定**: 
  - 溫度線：`borderColor: '#ef4444'`（紅色）
  - 濕度線：`borderColor: '#3b82f6'`（藍色）
- **Y 軸範圍**: 可添加 `min` 和 `max` 限制顯示範圍

**範例修改**:
```javascript
scales: {
    y: {
        min: 20,  // 溫度最低顯示 20°C
        max: 30   // 溫度最高顯示 30°C
    }
}
```

### 7. 數據欄位名稱對應（app_flask.py）

**位置**: 第 103-105 行

```python
temperature = data_dict.get('temperature', data_dict.get('temp', 0))
humidity = data_dict.get('humidity', data_dict.get('humi', 0))
light_status = data_dict.get('light_status', data_dict.get('light', '未知'))
```

**修改建議**:
- 如果 MQTT 訊息使用不同的欄位名稱，可在此添加更多對應
- 例如：`data_dict.get('temperature', data_dict.get('temp', data_dict.get('T', 0)))`

### 8. 電燈狀態判斷邏輯（templates/index.html）

**位置**: 第 257 行

```javascript
if (data.light_status === '開' || data.light_status === 'on') {
```

**修改建議**:
- 可添加更多狀態判斷，例如：`|| data.light_status === '1' || data.light_status === 'true'`
- 可修改顯示圖示，例如：`'🟢'` 改為 `'💡'`

### 9. 測試數據生成參數（generate_test_data.py）

**位置**: 第 18 行和第 123 行

```python
def generate_test_data(count=50):  # 預設生成 50 筆
    # ...
    data = generate_test_data(count=50)  # 實際生成數量
```

**修改建議**:
- 可改為其他數量，例如：`count=100` 生成 100 筆
- 可修改時間範圍：第 29 行 `timedelta(hours=count//2)` 改為其他時間
- 可修改數據範圍：
  - 溫度基礎值：第 32 行 `base_temp = 25.0`
  - 濕度基礎值：第 33 行 `base_humi = 60.0`
  - 波動範圍：第 41 行和第 45 行的 `random.uniform(-3, 3)` 和 `random.uniform(-5, 5)`

### 10. MQTT 測試發布設定（test_mqtt_publish.py）

**位置**: 第 12-15 行和第 82 行

```python
BROKER = "localhost"
PORT = 1883
TOPIC = "客廳/感測器"
# ...
publish_test_data(client, count=10, interval=2)  # 發布 10 筆，間隔 2 秒
```

**修改建議**:
- 可修改發布數量：`count=20` 發布 20 筆
- 可修改發布間隔：`interval=5` 每 5 秒發布一次
- 可修改測試數據範圍：第 40-41 行的溫度濕度範圍

### 11. 前端樣式自訂（templates/index.html）

**位置**: 第 9-150 行（CSS 樣式區塊）

**可修改項目**:
- **背景顏色**: 第 18 行 `background: linear-gradient(...)`
- **卡片樣式**: 第 72-82 行的 `.sensor-card` 樣式
- **字體大小**: 第 92 行的 `.sensor-value` 字體大小
- **顏色主題**: 修改各種顏色值以符合需求

### 12. 啟動腳本設定（start.sh）

**位置**: 第 24 行

```bash
echo "   - http://172.20.10.3:8080"
```

**修改建議**:
- 可改為實際的 IP 地址
- 可添加更多提示資訊

---

## 📊 數據流程詳解

### 數據儲存機制

1. **記憶體儲存**:
   - `latest_data`: 儲存最新一筆數據（字典格式）
   - `sensor_data`: 儲存最近 100 筆歷史數據（列表格式）

2. **檔案儲存**:
   - `sensor_data.csv`: CSV 格式，所有歷史數據（無限制）
   - `sensor_data.xlsx`: Excel 格式，方便人工查看

3. **數據同步**:
   - 應用程式啟動時從 CSV 載入歷史數據
   - 收到新 MQTT 訊息時立即追加到 CSV
   - 記憶體中的數據會定期清理（保留最近 100 筆）

### 數據格式

**MQTT 訊息格式**（JSON）:
```json
{
  "temperature": 25.5,
  "humidity": 60.0,
  "light_status": "開"
}
```

**CSV 檔案格式**:
```csv
時間戳記,電燈狀態,溫度,濕度
2025-11-30 14:30:00,開,25.5,60.0
```

**記憶體數據格式**:
```python
{
    'timestamp': '2025-11-30 14:30:00',
    'light_status': '開',
    'temperature': 25.5,
    'humidity': 60.0
}
```

---

## 🔌 MQTT 整合說明

### 連線流程

1. 應用程式啟動時自動建立 MQTT 連線
2. 連線成功後訂閱指定主題
3. 在背景執行緒中持續監聽訊息
4. 收到訊息時觸發回調函數處理

### 錯誤處理

- 連線失敗時會在終端機顯示錯誤訊息
- 訊息解析失敗時會記錄錯誤但不中斷程式
- CSV 寫入失敗時會顯示警告

### 擴展建議

如需添加更多感測器數據：
1. 在 `on_message` 函數中添加新的數據提取邏輯
2. 在 `latest_data` 和 CSV 欄位中添加新欄位
3. 在前端 HTML 中添加新的顯示卡片
4. 在圖表中添加新的數據集

---

## 🎨 前端介面說明

### 主要元件

1. **狀態列**:
   - MQTT 連線指示燈（綠色=已連線）
   - 最後更新時間
   - 總記錄數

2. **感測器卡片**:
   - 電燈狀態：大型圓形指示器
   - 溫度：數值顯示（°C）
   - 濕度：數值顯示（%）

3. **歷史圖表**:
   - 雙 Y 軸折線圖
   - 左 Y 軸：溫度
   - 右 Y 軸：濕度
   - X 軸：時間

### 即時更新機制

- **WebSocket 推送**: 收到新 MQTT 訊息時立即推送
- **定期輪詢**: 每 5 秒更新一次歷史圖表
- **自動重連**: Socket.IO 自動處理連線中斷

---

## 🛠️ 擴展開發指南

### 添加新的感測器

1. **後端修改**（app_flask.py）:
   ```python
   # 在 latest_data 中添加新欄位
   latest_data = {
       'light_status': '未知',
       'temperature': 0,
       'humidity': 0,
       'pressure': 0,  # 新增：氣壓
       'timestamp': None
   }
   
   # 在 on_message 中提取新數據
   pressure = data_dict.get('pressure', 0)
   latest_data['pressure'] = pressure
   ```

2. **前端修改**（templates/index.html）:
   ```html
   <!-- 添加新的感測器卡片 -->
   <div class="sensor-card">
       <div class="sensor-title">🌡️ 氣壓</div>
       <div>
           <span class="sensor-value" id="pressure">--</span>
           <span class="sensor-unit">hPa</span>
       </div>
   </div>
   ```

3. **更新圖表**:
   ```javascript
   // 在 datasets 中添加新數據集
   {
       label: '氣壓 (hPa)',
       data: [],
       borderColor: '#10b981',
       yAxisID: 'y2',
   }
   ```

### 添加數據篩選功能

可在 `/api/history` 端點添加查詢參數：
```python
@app.route('/api/history')
def get_history():
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    # 根據時間範圍篩選數據
    filtered_data = [d for d in sensor_data if start_time <= d['timestamp'] <= end_time]
    return jsonify(filtered_data)
```

### 添加數據匯出功能

可添加新的 API 端點：
```python
@app.route('/api/export')
def export_data():
    # 生成 CSV 或 Excel 檔案
    # 返回下載連結
    pass
```

---

## ⚙️ 配置建議

### 生產環境配置

1. **關閉除錯模式**:
   ```python
   socketio.run(app, host='0.0.0.0', port=8080, debug=False)
   ```

2. **使用環境變數**:
   ```python
   import os
   MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
   MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
   ```

3. **添加日誌記錄**:
   ```python
   import logging
   logging.basicConfig(
       filename='app.log',
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s'
   )
   ```

### 效能優化

1. **限制歷史數據**: 已實作（保留最近 100 筆）
2. **使用資料庫**: 可改用 SQLite 或 PostgreSQL 替代 CSV
3. **快取機制**: 可添加 Redis 快取最新數據
4. **負載平衡**: 多個實例時使用 Nginx 反向代理

---

## 🐛 常見問題與解決方案

### 問題 1: MQTT 無法連線

**可能原因**:
- MQTT Broker 未運行
- 防火牆阻擋
- IP 地址或端口錯誤

**解決方案**:
```bash
# 檢查 mosquitto 狀態
sudo systemctl status mosquitto

# 測試 MQTT 連線
mosquitto_sub -h localhost -t "客廳/感測器" -v
```

### 問題 2: 數據未顯示

**可能原因**:
- CSV 檔案不存在或格式錯誤
- MQTT 訊息格式不正確
- WebSocket 連線失敗

**解決方案**:
1. 檢查終端機日誌
2. 確認 CSV 檔案存在且格式正確
3. 使用瀏覽器開發者工具檢查 WebSocket 連線

### 問題 3: 圖表不顯示

**可能原因**:
- Chart.js 載入失敗
- 數據格式錯誤
- JavaScript 錯誤

**解決方案**:
1. 檢查瀏覽器控制台錯誤
2. 確認網路連線（需要載入 Chart.js CDN）
3. 檢查數據格式是否正確

---

## 📝 總結

### 核心功能

✅ MQTT 訂閱與即時接收  
✅ WebSocket 即時推送  
✅ 數據自動儲存（CSV + Excel）  
✅ 歷史數據視覺化  
✅ 響應式網頁介面  

### 可修改重點

1. **MQTT 設定**: Broker、Port、Topic
2. **數據保留**: 歷史數據數量限制
3. **伺服器設定**: Host、Port、Debug 模式
4. **前端樣式**: CSS 樣式、顏色、布局
5. **更新頻率**: 圖表更新間隔
6. **數據欄位**: 添加新感測器數據

### 擴展方向

- 添加更多感測器類型
- 實現數據篩選與查詢
- 添加警報通知功能
- 實現多房間監控
- 添加用戶認證
- 實現數據匯出功能

---

**最後更新**: 2025-11-30  
**版本**: 1.0  
**維護者**: Lesson6 專案團隊

