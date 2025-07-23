from .libs import Path

# 資源 URL (如果下載完整項目，可以改成本地讀取 Path(__file__).parent / "IMG")
ASSETS = "https://github.com/Canaan-HS/SlashcoSense-VRC/raw/refs/heads/main/IMG"

DEFAULT_OSC_PORT = 9000  # 預設埠號
LOG_UPDATE_INTERVAL = 500  # 日誌更新間隔 (毫秒)
WINDOWS_ICON_URL = f"{ASSETS}/SlashCo.ico"  # 窗口圖標
VRC_LOG_DIR = Path.home() / "AppData/LocalLow/VRChat/VRChat"  # VRChat 日誌目錄
