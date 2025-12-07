# 解決 config 模組導入錯誤

## 問題說明

錯誤訊息：`ImportError: no module named 'config'`

這表示 Pico W 上找不到 `config.py` 檔案。

## 解決方案

### 方案 1：上傳 config.py 檔案（推薦）

1. **確認 config.py 存在**
   - 檢查 `lesson7/config.py` 檔案是否存在

2. **上傳到 Pico W**
   - 在 Thonny 中，將 `config.py` 上傳到 Pico W
   - 確保檔案名稱是 `config.py`（不是 `config.py.txt`）

3. **修改 IP 位址**
   - 在 `config.py` 中修改 `MQTT_BROKER` 為 Raspberry Pi 的實際 IP

### 方案 2：使用獨立版本（更簡單）

使用 `main_standalone.py`，這個版本不需要 `config.py`：

1. **使用 main_standalone.py**
   - 所有設定都寫在檔案開頭
   - 只需要修改檔案中的 IP 位址即可

2. **修改設定**
   ```python
   MQTT_BROKER = "192.168.1.100"  # 改為你的 Raspberry Pi IP
   MQTT_PORT = 1883
   MQTT_TOPIC = "客廳/感測器"
   CLIENT_ID = "pico_lesson7"
   ```

3. **上傳並執行**
   - 上傳 `main_standalone.py` 到 Pico W
   - 執行即可

### 方案 3：修改 main.py（已自動處理）

我已經修改了 `main.py`，如果找不到 `config.py`，會使用預設值：

```python
try:
    from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, CLIENT_ID
except ImportError:
    # 使用預設值
    MQTT_BROKER = "192.168.1.XXX"  # 請修改這裡
    MQTT_PORT = 1883
    MQTT_TOPIC = "客廳/感測器"
    CLIENT_ID = "pico_lesson7"
```

**使用方式**：
- 如果看到「⚠️ 未找到 config.py，使用預設設定」訊息
- 請在 `main.py` 中直接修改預設值（第 10-13 行）

## 快速解決步驟

### 最簡單的方法：

1. **使用 main_standalone.py**
   ```bash
   # 在 Thonny 中
   # 1. 開啟 main_standalone.py
   # 2. 修改第 10 行的 MQTT_BROKER IP
   # 3. 上傳到 Pico W
   # 4. 執行
   ```

2. **或修改 main.py 中的預設值**
   - 找到 `except ImportError:` 區塊
   - 修改 `MQTT_BROKER = "192.168.1.XXX"` 為實際 IP

## 確認檔案已上傳

在 Thonny 中檢查 Pico W 上的檔案：
- 點擊「檢視」→「檔案」
- 確認是否有 `config.py` 或 `main_standalone.py`

## 測試

執行後應該會看到：
```
初始化 WiFi 連線...
✅ IP 位址: 192.168.1.50
初始化 MQTT 連線...
MQTT Broker: 192.168.1.100:1883
✅ MQTT 連線成功
📤 MQTT Publisher 模式
每 10 秒發布一次訊息...
```

如果還有錯誤，請檢查：
1. WiFi 是否連線成功
2. MQTT Broker IP 是否正確
3. MQTT Broker 是否正在運行

