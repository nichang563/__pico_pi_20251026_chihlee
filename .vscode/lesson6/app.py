"""
Streamlit MQTT 監控應用程式
即時顯示電燈狀態、溫濕度數據，並將數據儲存為 Excel 檔案
"""
# 必須先導入 streamlit
import streamlit as st

# 然後導入標準庫
import sys
from pathlib import Path
from datetime import datetime
import logging

# 確保可以導入同目錄下的模組
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# pandas 將在需要時才導入（延遲導入）
pd = None

# 導入自定義模組
try:
    from mqtt_client import MQTTClient
    from data_storage import save_to_excel, read_excel_data
    from config import TOPICS, MAX_HISTORY_RECORDS
except ImportError as e:
    st.error(f"❌ 導入模組時發生錯誤: {e}")
    st.error("請確認以下檔案存在於同一目錄：")
    st.error("- mqtt_client.py")
    st.error("- data_storage.py")
    st.error("- config.py")
    st.stop()

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 Session State
if 'mqtt_client' not in st.session_state:
    st.session_state.mqtt_client = None
if 'light_status' not in st.session_state:
    st.session_state.light_status = "未知"
if 'temperature' not in st.session_state:
    st.session_state.temperature = None
if 'humidity' not in st.session_state:
    st.session_state.humidity = None
if 'history_data' not in st.session_state:
    st.session_state.history_data = []
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = "未連線"
if 'data_updated' not in st.session_state:
    st.session_state.data_updated = False

def on_mqtt_message(topic, data):
    """
    MQTT 訊息回調函數
    處理接收到的訊息並更新 Session State
    注意：此函數在背景執行緒中執行，需要安全地更新 session_state
    """
    try:
        # 記錄收到的訊息（用於調試）
        logger.info("收到 MQTT 訊息 - Topic: %s, Data: %s", topic, data)
        
        timestamp = datetime.now()
        data_updated = False
        
        # 根據 topic 處理不同的數據
        if topic == TOPICS["temperature"]:
            # 處理溫度數據
            if isinstance(data, dict):
                temp_value = data.get("temperature") or data.get("value") or data.get("temp")
            else:
                try:
                    temp_value = float(data) if data is not None else None
                except (ValueError, TypeError):
                    temp_value = None
            
            if temp_value is not None:
                st.session_state.temperature = float(temp_value)
                data_updated = True
                st.session_state.data_updated = True  # 標記需要刷新
                logger.info("更新溫度: %.1f°C", st.session_state.temperature)
                print(f"[DEBUG] 溫度已更新: {st.session_state.temperature}°C")
        
        elif topic == TOPICS["humidity"]:
            # 處理濕度數據
            if isinstance(data, dict):
                hum_value = data.get("humidity") or data.get("value") or data.get("hum")
            else:
                try:
                    hum_value = float(data) if data is not None else None
                except (ValueError, TypeError):
                    hum_value = None
            
            if hum_value is not None:
                st.session_state.humidity = float(hum_value)
                data_updated = True
                st.session_state.data_updated = True  # 標記需要刷新
                logger.info("更新濕度: %.1f%%", st.session_state.humidity)
                print(f"[DEBUG] 濕度已更新: {st.session_state.humidity}%")
        
        elif topic == TOPICS["light"]:
            # 處理電燈狀態數據
            if isinstance(data, dict):
                light_value = data.get("status") or data.get("state") or data.get("light")
            else:
                light_value = str(data).lower() if data is not None else None
            
            # 標準化電燈狀態
            if light_value in ["on", "開", "1", "true", "開燈"]:
                st.session_state.light_status = "開"
                data_updated = True
            elif light_value in ["off", "關", "0", "false", "關燈"]:
                st.session_state.light_status = "關"
                data_updated = True
            elif light_value:
                st.session_state.light_status = str(light_value)
                data_updated = True
            
            if data_updated:
                st.session_state.data_updated = True  # 標記需要刷新
                logger.info("更新電燈狀態: %s", st.session_state.light_status)
                print(f"[DEBUG] 電燈狀態已更新: {st.session_state.light_status}")
        
        # 當有完整數據時，儲存到 Excel 和歷史記錄
        if (st.session_state.temperature is not None and 
            st.session_state.humidity is not None and 
            st.session_state.light_status != "未知"):
            
            # 儲存到 Excel（在背景執行緒中執行，需要處理錯誤）
            try:
                save_to_excel(
                    timestamp,
                    st.session_state.light_status,
                    st.session_state.temperature,
                    st.session_state.humidity
                )
            except Exception as e:
                logger.error("儲存數據時發生錯誤: %s", e)
            
            # 更新歷史數據（限制記錄數量）
            history_record = {
                "時間": timestamp,
                "電燈狀態": st.session_state.light_status,
                "溫度": st.session_state.temperature,
                "濕度": st.session_state.humidity
            }
            st.session_state.history_data.append(history_record)
            
            # 限制歷史記錄數量
            if len(st.session_state.history_data) > MAX_HISTORY_RECORDS:
                st.session_state.history_data = st.session_state.history_data[-MAX_HISTORY_RECORDS:]
            
            # 標記需要重新渲染
            st.session_state.data_updated = True
    
    except Exception as e:
        logger.error("處理 MQTT 訊息時發生錯誤: %s", e)

def init_mqtt():
    """初始化 MQTT 連線"""
    try:
        if st.session_state.mqtt_client is None:
            st.session_state.mqtt_client = MQTTClient(on_message_callback=on_mqtt_message)
            st.session_state.mqtt_client.connect()
            st.session_state.connection_status = "連線中..."
            # 等待一下讓連線建立
            import time
            time.sleep(0.3)
        elif not st.session_state.mqtt_client.is_connected:
            st.session_state.mqtt_client.connect()
            st.session_state.connection_status = "重新連線中..."
            import time
            time.sleep(0.3)
    except Exception as e:
        logger.error("初始化 MQTT 連線時發生錯誤: %s", e)
        st.session_state.connection_status = f"連線錯誤: {str(e)}"
        st.error(f"❌ MQTT 連線失敗: {e}")

def disconnect_mqtt():
    """斷開 MQTT 連線"""
    if st.session_state.mqtt_client:
        st.session_state.mqtt_client.disconnect()
        st.session_state.connection_status = "已斷線"

# 主應用程式
st.set_page_config(
    page_title="MQTT 監控系統",
    page_icon="📊",
    layout="wide"
)

st.title("📊 MQTT 感測器監控系統")

# 連線控制區域
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    if st.button("🔌 連線 MQTT", type="primary"):
        init_mqtt()

with col2:
    if st.button("❌ 斷開連線"):
        disconnect_mqtt()

with col3:
    # 顯示連線狀態
    if st.session_state.connection_status == "未連線":
        st.error("❌ 未連線")
    elif st.session_state.mqtt_client and st.session_state.mqtt_client.is_connected:
        st.success("✅ 已連線")
        st.session_state.connection_status = "已連線"
    else:
        st.warning("⚠️ " + st.session_state.connection_status)

st.divider()

# 自動初始化連線（首次載入時）
if st.session_state.mqtt_client is None:
    init_mqtt()

# 使用 Streamlit 的定時刷新功能（每1秒刷新一次以顯示最新數據）
if st.session_state.mqtt_client and st.session_state.mqtt_client.is_connected:
    import time
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    current_time = time.time()
    # 每1秒自動刷新一次，或當數據更新時立即刷新
    should_refresh = False
    
    # 如果數據已更新，立即刷新
    if st.session_state.get('data_updated', False):
        should_refresh = True
        st.session_state.data_updated = False
        st.session_state.last_refresh = current_time
        print("[DEBUG] 數據已更新，觸發刷新")
    elif current_time - st.session_state.last_refresh > 1:
        should_refresh = True
        st.session_state.last_refresh = current_time
    
    if should_refresh:
        st.rerun()

# 顯示調試資訊（開發用）
with st.expander("🔍 調試資訊", expanded=True):
    st.write("**MQTT 連線狀態：**")
    if st.session_state.mqtt_client:
        st.write(f"- 客戶端物件: {'已建立' if st.session_state.mqtt_client else '未建立'}")
        st.write(f"- 連線狀態: {st.session_state.mqtt_client.is_connected}")
        st.write(f"- 連線狀態字串: {st.session_state.connection_status}")
    else:
        st.write("- 客戶端物件: 未建立")
    
    st.write("**當前數據：**")
    st.write(f"- 溫度: {st.session_state.temperature}")
    st.write(f"- 濕度: {st.session_state.humidity}")
    st.write(f"- 電燈狀態: {st.session_state.light_status}")
    st.write(f"- 歷史記錄數: {len(st.session_state.history_data)}")
    st.write(f"- 數據更新標記: {st.session_state.get('data_updated', False)}")
    
    st.write("**訂閱的 Topics：**")
    from config import TOPICS
    for name, topic_name in TOPICS.items():
        st.write(f"- {name}: `{topic_name}`")
    
    # 添加控制按鈕
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 手動刷新頁面"):
            st.rerun()
    with col2:
        if st.button("📊 清除數據"):
            st.session_state.temperature = None
            st.session_state.humidity = None
            st.session_state.light_status = "未知"
            st.session_state.history_data = []
            st.success("數據已清除")

# 主要顯示區域
col1, col2, col3 = st.columns(3)

# 電燈狀態顯示
with col1:
    st.subheader("💡 電燈狀態")
    light_status = st.session_state.light_status
    
    if light_status == "開":
        st.markdown("### 🟢 **開**")
        st.success("電燈目前是開啟狀態")
    elif light_status == "關":
        st.markdown("### ⚫ **關**")
        st.info("電燈目前是關閉狀態")
    else:
        st.markdown("### ⚪ **未知**")
        st.warning("尚未收到電燈狀態數據")

# 溫度顯示
with col2:
    st.subheader("🌡️ 客廳溫度")
    temp = st.session_state.temperature
    
    if temp is not None:
        st.markdown(f"### **{temp:.1f} °C**")
        # 溫度指示器
        if temp < 20:
            st.info("溫度較低")
        elif temp > 28:
            st.warning("溫度較高")
        else:
            st.success("溫度正常")
    else:
        st.markdown("### **-- °C**")
        st.warning("尚未收到溫度數據")

# 濕度顯示
with col3:
    st.subheader("💧 客廳濕度")
    hum = st.session_state.humidity
    
    if hum is not None:
        st.markdown(f"### **{hum:.1f} %**")
        # 濕度指示器
        if hum < 30:
            st.warning("濕度較低")
        elif hum > 70:
            st.warning("濕度較高")
        else:
            st.success("濕度正常")
    else:
        st.markdown("### **-- %**")
        st.warning("尚未收到濕度數據")

st.divider()

# 溫濕度歷史趨勢圖
st.subheader("📈 溫濕度歷史趨勢圖")

if len(st.session_state.history_data) > 0:
    # 延遲導入 pandas
    if pd is None:
        try:
            import pandas as pd
        except ImportError as e:
            st.error(f"❌ 無法導入 pandas: {e}")
            st.error("請執行: uv pip install pandas")
            st.stop()
    
    # 建立 DataFrame
    df = pd.DataFrame(st.session_state.history_data)
    df["時間"] = pd.to_datetime(df["時間"])
    df = df.set_index("時間")
    
    # 顯示圖表
    chart_data = df[["溫度", "濕度"]]
    st.line_chart(chart_data, use_container_width=True)
    
    # 顯示數據表格（可選）
    with st.expander("查看歷史數據"):
        st.dataframe(df.reset_index(), use_container_width=True)
else:
    st.info("尚未有歷史數據，等待 MQTT 訊息...")

st.divider()

# 數據管理區域
st.subheader("💾 數據管理")

col1, col2 = st.columns(2)

with col1:
    if st.button("📥 載入 Excel 歷史數據"):
        try:
            # 延遲導入 pandas
            if pd is None:
                try:
                    import pandas as pd
                except ImportError as e:
                    st.error(f"❌ 無法導入 pandas: {e}")
                    st.error("請執行: uv pip install pandas")
                    st.stop()
            
            excel_df = read_excel_data()
            if not excel_df.empty:
                st.success(f"成功載入 {len(excel_df)} 筆記錄")
                st.dataframe(excel_df, use_container_width=True)
                
                # 更新歷史數據到 Session State（用於圖表顯示）
                if "時間戳記" in excel_df.columns:
                    excel_df["時間"] = pd.to_datetime(excel_df["時間戳記"])
                    recent_data = excel_df.tail(MAX_HISTORY_RECORDS)
                    
                    history_list = []
                    for _, row in recent_data.iterrows():
                        history_list.append({
                            "時間": row["時間"],
                            "電燈狀態": row.get("電燈狀態", "未知"),
                            "溫度": row.get("溫度 (°C)", row.get("溫度", None)),
                            "濕度": row.get("濕度 (%)", row.get("濕度", None))
                        })
                    
                    st.session_state.history_data = history_list
            else:
                st.warning("Excel 檔案中沒有數據")
        except Exception as e:
            st.error(f"載入 Excel 數據時發生錯誤: {e}")

with col2:
    st.info(f"📊 當前記憶體中的歷史記錄數: {len(st.session_state.history_data)}")

# 頁尾資訊
st.divider()
st.caption(f"最後更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
