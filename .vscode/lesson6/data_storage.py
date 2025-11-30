"""
數據儲存模組 - 處理 Excel 檔案寫入
"""
from datetime import datetime
from pathlib import Path
import logging
from config import EXCEL_FILE

logger = logging.getLogger(__name__)

# pandas 將在函數內部導入，避免在模組層級導入
def _get_pandas():
    """延遲導入 pandas"""
    import pandas as pd
    return pd

def save_to_excel(timestamp, light_status, temperature, humidity):
    """
    將感測器數據追加到 Excel 檔案
    
    Args:
        timestamp: 時間戳記
        light_status: 電燈狀態 (str: "開" 或 "關")
        temperature: 溫度值 (float)
        humidity: 濕度值 (float)
    """
    try:
        pd = _get_pandas()
        
        # 準備數據
        new_data = {
            "時間戳記": [timestamp],
            "電燈狀態": [light_status],
            "溫度 (°C)": [temperature],
            "濕度 (%)": [humidity]
        }
        
        new_df = pd.DataFrame(new_data)
        
        # 如果檔案存在，讀取現有數據並追加
        if EXCEL_FILE.exists():
            try:
                existing_df = pd.read_excel(EXCEL_FILE)
                # 合併數據
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            except Exception as e:
                logger.warning(f"讀取現有 Excel 檔案時發生錯誤: {e}，將建立新檔案")
                combined_df = new_df
        else:
            combined_df = new_df
        
        # 寫入 Excel 檔案
        combined_df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        logger.info(f"數據已成功儲存到 {EXCEL_FILE}")
        
    except Exception as e:
        logger.error(f"儲存數據到 Excel 時發生錯誤: {e}")
        raise

def read_excel_data():
    """
    讀取 Excel 檔案中的所有數據
    
    Returns:
        pandas.DataFrame: 包含所有歷史數據的 DataFrame，如果檔案不存在則返回空 DataFrame
    """
    try:
        pd = _get_pandas()
        
        if EXCEL_FILE.exists():
            return pd.read_excel(EXCEL_FILE, engine='openpyxl')
        else:
            return pd.DataFrame(columns=["時間戳記", "電燈狀態", "溫度 (°C)", "濕度 (%)"])
    except Exception as e:
        logger.error(f"讀取 Excel 檔案時發生錯誤: {e}")
        pd = _get_pandas()
        return pd.DataFrame(columns=["時間戳記", "電燈狀態", "溫度 (°C)", "濕度 (%)"])

