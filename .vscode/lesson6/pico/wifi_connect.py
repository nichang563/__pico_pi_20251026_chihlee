# wifi_connect.py

# 作者：ChatGPT for 徐國堂老師

# 適用：Raspberry Pi Pico W（MicroPython）

import network
import time
import socket

# -------------------------------
# 你可以設定你的 WiFi 資訊
# -------------------------------
WIFI_SSID = "F602-39 wifi"
WIFI_PASSWORD = "raspberry"

# -------------------------------
# WiFi 狀態代碼說明
# -------------------------------
WIFI_STATUS = {
    0: "IDLE - 未啟動",
    1: "CONNECTING - 連線中",
    2: "WRONG_PASSWORD - 密碼錯誤",
    3: "NO_AP_FOUND - 找不到 AP",
    4: "CONNECT_FAIL - 連線失敗",
    5: "GOT_IP - 已取得 IP（連線成功）"
}

def get_status_text(status):
    """取得 WiFi 狀態文字說明"""
    return WIFI_STATUS.get(status, f"未知狀態: {status}")

# -------------------------------
# 掃描可用 WiFi 網路
# -------------------------------
def scan_networks():
    """
    掃描可用的 WiFi 網路
    
    Returns:
        list: 找到的網路列表
    """
    print("📡 掃描 WiFi 網路...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    time.sleep(0.5)  # 等待 WLAN 啟動
    
    try:
        networks = wlan.scan()
        print(f"找到 {len(networks)} 個網路:")
        
        found_ssid = False
        for net in networks:
            ssid = net[0].decode('utf-8')
            rssi = net[3]  # 訊號強度
            bssid = ':'.join(['%02x' % b for b in net[1]])
            channel = net[2]
            security = net[4]  # 0=開放, 1=WEP, 2=WPA, 3=WPA2, 4=WPA/WPA2
            
            # 檢查是否為目標 SSID
            if ssid == WIFI_SSID:
                found_ssid = True
                print(f"  ✅ {ssid} (訊號: {rssi} dBm, 頻道: {channel}, 安全: {security})")
            else:
                print(f"     {ssid} (訊號: {rssi} dBm)")
        
        if not found_ssid:
            print(f"\n❌ 找不到目標網路: {WIFI_SSID}")
            print(f"   請確認:")
            print(f"   1. SSID 名稱是否正確（區分大小寫）")
            print(f"   2. Pico W 是否在 WiFi 訊號範圍內")
            print(f"   3. 路由器是否支援 2.4GHz（Pico W 不支援 5GHz）")
        
        return networks
    except Exception as e:
        print(f"❌ 掃描網路時發生錯誤: {e}")
        return []

# -------------------------------
# WiFi 連線函式（改進版）
# -------------------------------
def connect(ssid=WIFI_SSID, password=WIFI_PASSWORD, retry=20, scan_first=True):
    """
    連線到 WiFi（改進版，包含詳細診斷）
    
    Args:
        ssid: WiFi 名稱
        password: WiFi 密碼
        retry: 嘗試次數（每次間隔 1 秒）
        scan_first: 是否先掃描網路
    
    Returns:
        wlan: 連線後的 WLAN 物件
    
    Raises:
        RuntimeError: 連線失敗時拋出
    """
    wlan = network.WLAN(network.STA_IF)
    
    # 檢查是否已連線
    if wlan.isconnected():
        print("✅ 已經連線過 WiFi")
        ip_info = wlan.ifconfig()
        print(f"   IP 位址: {ip_info[0]}")
        print(f"   子網路遮罩: {ip_info[1]}")
        print(f"   閘道: {ip_info[2]}")
        print(f"   DNS: {ip_info[3]}")
        return wlan
    
    # 先掃描網路（可選）
    if scan_first:
        print("\n" + "="*50)
        networks = scan_networks()
        print("="*50 + "\n")
        time.sleep(1)
    
    print("🔌 啟動 WLAN...")
    wlan.active(True)
    time.sleep(1)  # 等待 WLAN 完全啟動
    
    print(f"📡 準備連線 SSID: {ssid}")
    print(f"   密碼長度: {len(password)} 字元")
    
    try:
        wlan.connect(ssid, password)
    except Exception as e:
        print(f"❌ 連線時發生錯誤: {e}")
        raise RuntimeError(f"❌ WiFi 連線失敗: {e}")
    
    print(f"⏳ 等待連線中（最多 {retry} 秒）...")
    
    for i in range(retry):
        status = wlan.status()
        status_text = get_status_text(status)
        
        # 檢查連線狀態
        if wlan.isconnected():
            print("\n✅ WiFi 連線成功！")
            ip_info = wlan.ifconfig()
            print(f"   IP 位址: {ip_info[0]}")
            print(f"   子網路遮罩: {ip_info[1]}")
            print(f"   閘道: {ip_info[2]}")
            print(f"   DNS: {ip_info[3]}")
            return wlan
        
        # 檢查錯誤狀態
        if status == 2:  # WRONG_PASSWORD
            print(f"\n❌ 密碼錯誤！")
            print(f"   請檢查 secrets.py 或程式碼中的 WIFI_PASSWORD")
            raise RuntimeError("❌ WiFi 連線失敗：密碼錯誤")
        elif status == 3:  # NO_AP_FOUND
            print(f"\n❌ 找不到 AP（存取點）！")
            print(f"   請確認 SSID 是否正確")
            raise RuntimeError("❌ WiFi 連線失敗：找不到 AP")
        elif status == 4:  # CONNECT_FAIL
            print(f"\n❌ 連線失敗！")
            print(f"   可能原因：訊號太弱、路由器拒絕連線、MAC 過濾等")
        
        # 顯示進度
        if (i + 1) % 3 == 0:  # 每 3 秒顯示一次狀態
            print(f"   ... ({i+1}/{retry} 秒) 狀態: {status_text}")
        
        time.sleep(1)
    
    # 連線超時
    final_status = wlan.status()
    final_status_text = get_status_text(final_status)
    
    print(f"\n❌ WiFi 連線失敗（已等待 {retry} 秒）")
    print(f"   最終狀態: {final_status_text}")
    
    print(f"\n💡 故障排除建議:")
    print(f"   1. 確認 SSID 是否正確: '{ssid}'")
    print(f"   2. 確認密碼是否正確（長度: {len(password)} 字元）")
    print(f"   3. 確認路由器支援 2.4GHz WiFi（Pico W 不支援 5GHz）")
    print(f"   4. 確認 Pico W 在 WiFi 訊號範圍內（靠近路由器測試）")
    print(f"   5. 檢查路由器是否限制新裝置連線（MAC 過濾、裝置限制等）")
    print(f"   6. 嘗試重啟路由器")
    print(f"   7. 確認路由器未設定隱藏 SSID")
    print(f"   8. 檢查路由器是否使用特殊認證方式（WPA3 可能不相容）")
    
    raise RuntimeError("❌ WiFi 連線失敗，請檢查 SSID/密碼或距離")

# -------------------------------
# 斷線函式
# -------------------------------
def disconnect():
    """斷開 WiFi 連線"""
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        wlan.disconnect()
        wlan.active(False)
        print("✅ 已斷線")
    else:
        print("ℹ️  目前沒有 WiFi 連線")

# -------------------------------
# 是否連線成功？
# -------------------------------
def is_connected():
    """檢查 WiFi 是否已連線"""
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()

# -------------------------------
# 取得 IP 位址
# -------------------------------
def get_ip():
    """取得當前 IP 位址"""
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        return wlan.ifconfig()[0]
    return None

# -------------------------------
# 取得完整網路資訊
# -------------------------------
def get_network_info():
    """取得完整網路資訊"""
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        return {
            'ip': wlan.ifconfig()[0],
            'subnet': wlan.ifconfig()[1],
            'gateway': wlan.ifconfig()[2],
            'dns': wlan.ifconfig()[3],
            'status': get_status_text(wlan.status())
        }
    return None

# -------------------------------
# 測試連線到外部網站（例如 Google）
# -------------------------------
def test_internet(host="8.8.8.8", port=53, timeout=3):
    """
    使用 UDP 測試外部網路是否可連線
    
    Args:
        host: 測試主機（預設 Google DNS）
        port: 測試端口
        timeout: 超時時間（秒）
    
    Returns:
        bool: 連線成功返回 True
    """
    if not is_connected():
        print("❌ WiFi 未連線，無法測試網路")
        return False
    
    try:
        print(f"🌐 測試網路連線到 {host}:{port}...")
        addr = socket.getaddrinfo(host, port)[0][-1]
        s = socket.socket()
        s.settimeout(timeout)
        s.connect(addr)
        s.close()
        print("✅ 網路連線正常")
        return True
    except Exception as e:
        print(f"❌ 網路連線失敗: {e}")
        return False

# -------------------------------
# 測試函式（用於除錯）
# -------------------------------
def test_connection():
    """完整測試 WiFi 連線"""
    print("="*50)
    print("WiFi 連線測試")
    print("="*50)
    
    try:
        wlan = connect()
        if wlan:
            print("\n✅ WiFi 連線測試成功")
            test_internet()
            return True
    except RuntimeError as e:
        print(f"\n❌ WiFi 連線測試失敗: {e}")
        return False
