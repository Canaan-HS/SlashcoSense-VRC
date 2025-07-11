# Original Author : https://github.com/arcxingye/SlasherSense-VRC/

import os
import re
import sys
import locale
import ctypes
import platform

from pathlib import Path
from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTextEdit,
    QCheckBox,
    QLineEdit,
    QGroupBox,
)
from PySide6.QtCore import Qt, QUrl, QSize, QTimer, Signal
from PySide6.QtGui import QFont, QIcon, QCursor, QPixmap, QPainter, QPixmapCache, QPainterPath
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

try:
    from pythonosc import udp_client

    UDP_CLIENT_AVAILABLE = True
except ImportError:
    udp_client = None
    UDP_CLIENT_AVAILABLE = False

if TYPE_CHECKING:
    from pythonosc.udp_client import SimpleUDPClient

# 資源 URL
ASSETS = "https://github.com/Canaan-HS/SlashcoSense-VRC/raw/refs/heads/main/IMG"

DEFAULT_OSC_PORT = 9000  # 預設埠號
LOG_UPDATE_INTERVAL = 500  # 日誌更新間隔 (毫秒)
WINDOWS_ICON_URL = f"{ASSETS}/SlashCo.ico"  # 窗口圖標
VRC_LOG_DIR = Path.home() / "AppData/LocalLow/VRChat/VRChat"  # VRChat 日誌目錄

# 進度條顏色對應
PROGRESS_COLORS = {
    (0, 25): "#555555",  # 灰色
    (25, 50): "#e74c3c",  # 紅色
    (50, 75): "#f39c12",  # 黃色
    (75, 100): "#27ae60",  # 綠色
}


def Language(Lang=None):
    """翻譯對照 (by: AI translation)"""
    Word = {
        "zh_TW": {"": ""},
        "zh_CN": {
            "舊 SlashCo 總部": "旧 SlashCo 总部",
            "馬龍斯農場": "马龙斯农场",
            "菲利普斯•書斯特伍德高中": "菲利普斯·舒斯特伍德高中",
            "伊斯特伍德綜合醫院": "伊斯特伍德综合医院",
            "德爾塔科研機構": "德尔塔科研机构",
            "巴巴布伊 【肌肉男 / 隱形怪】": "巴巴布伊【肌肉男 / 隐形怪】",
            "席德 【手槍怪 / 餅乾怪】": "席德【手枪怪 / 饼干怪】",
            "特羅勒格巨魔【笑臉男 / 火柴人】": "特罗勒格巨魔【笑脸男 / 火柴人】",
            "博格梅爾【機器人】": "博格梅尔【机器人】",
            "阿博米納特【憎惡者 / 外星人】": "阿博米纳特【憎恶者 / 外星人】",
            "口渴 【爬行者 / 牛奶怪】": "口渴【爬行者 / 牛奶怪】",
            "埃爾默神父 【霰彈槍 / 神父】": "埃尔默神父【霰弹枪 / 神父】",
            "觀察者 【高個子】": "观察者【高个子】",
            "野獸 【貓貓 / 貓老太】": "野兽【猫猫 / 猫老太】",
            "海豚人": "海豚人",
            "伊戈爾【DJ / 創造者 / 毀滅者】": "伊戈尔【DJ / 创造者 / 毁灭者】",
            "牢騷者【乞丐】": "牢骚者【乞丐】",
            "公主【狗】": "公主【狗】",
            "極速奔跑者": "极速奔跑者",
            "定位器": "定位器",
            "皇家漢堡": "皇家汉堡",
            "餅乾": "饼干",
            "啤酒桶": "啤酒桶",
            "美乃滋": "美乃滋",
            "橙色果凍": "橙色果冻",
            "COSTCO速凍披薩": "COSTCO速冻披萨",
            "機場的烈性酒": "机场的烈性酒",
            "犀牛丸": "犀牛丸",
            "岩石": "岩石",
            "人造肉": "人造肉",
            "沙袋": "沙袋",
            "巫毒娃娃": "巫毒娃娃",
            "紐波特薄荷": "纽波特薄荷",
            "B-GONE蘇打水": "B-GONE苏打水",
            "40號紅色染劑": "40号红色染剂",
            "桶裝牛奶": "桶装牛奶",
            "貪婪之壺": "贪婪之壶",
            "不死圖騰": "不死图腾",
            "邪惡的瓊克爾•卡特": "邪恶的琼克尔·卡特",
            "25克苯海拉明": "25克苯海拉明",
            "巴爾幹激素": "巴尔干激素",
            "遊戲狀態": "游戏状态",
            "未知": "未知",
            "地圖": "地图",
            "殺手": "杀手",
            "物品": "物品",
            "生成物品": "生成物品",
            "生成物品: 無": "生成物品：无",
            "發電機狀態": "发电机状态",
            "發電機": "发电机",
            "發電機監控僅限非房主有效": "发电机监控仅限非房主有效",
            "OSC 設定": "OSC 设置",
            "啟用 OSC": "启用 OSC",
            "錯誤：OSC 啟用失敗": "错误：OSC 启用失败",
            "OSC 已啟用": "OSC 已启用",
            "OSC 已停用": "OSC 已停用",
            "顯示 OSC 日誌": "显示 OSC 日志",
            "埠": "端口",
            "埠號:": "端口号：",
            "日誌監控": "日志监控",
            "開始監控日誌": "开始监控日志",
            "載入失敗": "加载失败",
            "錯誤：埠號無效或 OSC 不可用": "错误：端口号无效或 OSC 不可用",
            "[OSC] 傳送 SlasherID": "[OSC] 传送 SlasherID",
            "[OSC] 傳送 GENERATOR1_FUEL": "[OSC] 传送 GENERATOR1_FUEL",
            "[OSC] 傳送 GENERATOR2_FUEL": "[OSC] 传送 GENERATOR2_FUEL",
            "[OSC] 傳送 GENERATOR1_BATTERY": "[OSC] 传送 GENERATOR1_BATTERY",
            "[OSC] 傳送 GENERATOR2_BATTERY": "[OSC] 传送 GENERATOR2_BATTERY",
        },
        "en_US": {
            "舊 SlashCo 總部": "SlashCo HQ",
            "馬龍斯農場": "Malones Farmyard",
            "菲利普斯•書斯特伍德高中": "Philips Westwood HighSchool",
            "伊斯特伍德綜合醫院": "Eastwood General Hospital",
            "德爾塔科研機構": "Research Facility Delta",
            "巴巴布伊 【肌肉男 / 隱形怪】": "Bababooey [Muscle Man / Invisible Freak]",
            "席德 【手槍怪 / 餅乾怪】": "Cid [Pistol Freak / Cookie Monster]",
            "特羅勒格巨魔【笑臉男 / 火柴人】": "Trollag [Smiley / Stickman]",
            "博格梅爾【機器人】": "Borgmire [Robot]",
            "阿博米納特【憎惡者 / 外星人】": "Abomigant [Abomination / Alien]",
            "口渴 【爬行者 / 牛奶怪】": "Thirsty [Crawler / Milk Freak]",
            "埃爾默神父 【霰彈槍 / 神父】": "Father Elmer [Shotgun / Priest]",
            "觀察者 【高個子】": "The Watcher [Tall One]",
            "野獸 【貓貓 / 貓老太】": "The Beast [Kitty / Cat Lady]",
            "海豚人": "Dolphin Man",
            "伊戈爾【DJ / 創造者 / 毀滅者】": "Igor [DJ / Creator / Destroyer]",
            "牢騷者【乞丐】": "The Grouch [Beggar]",
            "公主【狗】": "Princess [Dog]",
            "極速奔跑者": "Speed Runner",
            "定位器": "Proxy-Locator",
            "皇家漢堡": "Royal Burger",
            "餅乾": "Cookie",
            "啤酒桶": "Beer Keg",
            "美乃滋": "Mayonnaise",
            "橙色果凍": "Orange Jello",
            "COSTCO速凍披薩": "Costco Frozen Pizza",
            "機場的烈性酒": "Airport Jungle Juice",
            "犀牛丸": "Rhino Pill",
            "岩石": "The Rock",
            "人造肉": "Lab-Grown Meat",
            "沙袋": "Pocket Sand",
            "巫毒娃娃": "The Baby",
            "紐波特薄荷": "Newport Menthols",
            "B-GONE蘇打水": "B-GONE Soda",
            "40號紅色染劑": "Red 40 Vial",
            "桶裝牛奶": "Milk Jug",
            "貪婪之壺": "Pot of Greed",
            "不死圖騰": "Deathward",
            "邪惡的瓊克爾•卡特": "Evil Jonkler Cart",
            "25克苯海拉明": "25 Gram Benadryl",
            "巴爾幹激素": "Balkan Boost",
            "遊戲狀態": "Game Status",
            "未知": "Unknown",
            "地圖": "Map",
            "殺手": "Slasher",
            "物品": "Item",
            "生成物品": "Generated Item",
            "生成物品: 無": "Generated Item: None",
            "發電機狀態": "Generator Status",
            "發電機": "Generator",
            "發電機監控僅限非房主有效": "Generator monitoring works for non-hosts only",
            "OSC 設定": "OSC Settings",
            "啟用 OSC": "Enable OSC",
            "錯誤：OSC 啟用失敗": "Error: Failed to Enable OSC",
            "OSC 已啟用": "OSC Enabled",
            "OSC 已停用": "OSC Disabled",
            "顯示 OSC 日誌": "Show OSC Logs",
            "埠": "Port",
            "埠號:": "Port:",
            "日誌監控": "Log Monitor",
            "開始監控日誌": "Start Log Monitoring",
            "載入失敗": "Failed to Load",
            "錯誤：埠號無效或 OSC 不可用": "Error: Invalid Port or OSC Unavailable",
            "[OSC] 傳送 SlasherID": "[OSC] Send SlasherID",
            "[OSC] 傳送 GENERATOR1_FUEL": "[OSC] Send GENERATOR1_FUEL",
            "[OSC] 傳送 GENERATOR2_FUEL": "[OSC] Send GENERATOR2_FUEL",
            "[OSC] 傳送 GENERATOR1_BATTERY": "[OSC] Send GENERATOR1_BATTERY",
            "[OSC] 傳送 GENERATOR2_BATTERY": "[OSC] Send GENERATOR2_BATTERY",
        },
        "ja_JP": {
            "舊 SlashCo 總部": "旧SlashCo本部",
            "馬龍斯農場": "マーロンズ農場",
            "菲利普斯•書斯特伍德高中": "フィリップス・シュスタウッド高校",
            "伊斯特伍德綜合醫院": "イーストウッド総合病院",
            "德爾塔科研機構": "デルタ研究施設",
            "巴巴布伊 【肌肉男 / 隱形怪】": "ババブーイ【筋肉男 / 透明モンスター】",
            "席德 【手槍怪 / 餅乾怪】": "シド【ピストル怪 / クッキーモンスター】",
            "特羅勒格巨魔【笑臉男 / 火柴人】": "トロレッグ・トロール【スマイル男 / スティックマン】",
            "博格梅爾【機器人】": "ボーグメル【ロボット】",
            "阿博米納特【憎惡者 / 外星人】": "アボミネート【忌まわしい者 / エイリアン】",
            "口渴 【爬行者 / 牛奶怪】": "のどが渇いた【這い者 / ミルクモンスター】",
            "埃爾默神父 【霰彈槍 / 神父】": "エルマー神父【ショットガン / 神父】",
            "觀察者 【高個子】": "観察者【背高男】",
            "野獸 【貓貓 / 貓老太】": "ビースト【ネコちゃん / ネコ婆】",
            "海豚人": "イルカ人間",
            "伊戈爾【DJ / 創造者 / 毀滅者】": "イゴール【DJ / 創造者 / 破壊者】",
            "牢騷者【乞丐】": "ぐち男【乞食】",
            "公主【狗】": "プリンセス【犬】",
            "極速奔跑者": "超速ランナー",
            "定位器": "ロケーター",
            "皇家漢堡": "ロイヤルバーガー",
            "餅乾": "クッキー",
            "啤酒桶": "ビール樽",
            "美乃滋": "マヨネーズ",
            "橙色果凍": "オレンジゼリー",
            "COSTCO速凍披薩": "COSTCO冷凍ピザ",
            "機場的烈性酒": "空港の強い酒",
            "犀牛丸": "サイの丸薬",
            "岩石": "岩",
            "人造肉": "人工肉",
            "沙袋": "サンドバッグ",
            "巫毒娃娃": "ブードゥー人形",
            "紐波特薄荷": "ニューポートミント",
            "B-GONE蘇打水": "B-GONEソーダ",
            "40號紅色染劑": "赤色40号染料",
            "桶裝牛奶": "ミルクの桶",
            "貪婪之壺": "欲望の壺",
            "不死圖騰": "不死のトーテム",
            "邪惡的瓊克爾•卡特": "邪悪なジョンクル・カーター",
            "25克苯海拉明": "25gジフェンヒドラミン",
            "巴爾幹激素": "バルカンホルモン",
            "遊戲狀態": "ゲーム状態",
            "未知": "不明",
            "地圖": "マップ",
            "殺手": "スラッシャー",
            "物品": "アイテム",
            "生成物品": "生成アイテム",
            "生成物品: 無": "生成アイテム：なし",
            "發電機狀態": "発電機の状態",
            "發電機": "発電機",
            "發電機監控僅限非房主有效": "発電機の監視はホスト以外のみ有効",
            "OSC 設定": "OSC設定",
            "啟用 OSC": "OSCを有効化",
            "錯誤：OSC 啟用失敗": "エラー：OSCの有効化に失敗しました",
            "OSC 已啟用": "OSCが有効になりました",
            "OSC 已停用": "OSCが無効になりました",
            "顯示 OSC 日誌": "OSCログを表示",
            "埠": "ポート",
            "埠號:": "ポート番号：",
            "日誌監控": "ログ監視",
            "開始監控日誌": "ログ監視を開始",
            "載入失敗": "読み込み失敗",
            "錯誤：埠號無效或 OSC 不可用": "エラー：ポート番号が無効またはOSCが使用不可",
            "[OSC] 傳送 SlasherID": "[OSC] SlasherIDを送信",
            "[OSC] 傳送 GENERATOR1_FUEL": "[OSC] GENERATOR1_FUELを送信",
            "[OSC] 傳送 GENERATOR2_FUEL": "[OSC] GENERATOR2_FUELを送信",
            "[OSC] 傳送 GENERATOR1_BATTERY": "[OSC] GENERATOR1_BATTERYを送信",
            "[OSC] 傳送 GENERATOR2_BATTERY": "[OSC] GENERATOR2_BATTERYを送信",
        },
    }

    Locale = {
        "950": "zh_TW",
        "936": "zh_CN",
        "932": "ja_JP",
        "1252": "en_US",
    }

    ML = {}
    Default = "en_US"
    SysPlat = platform.system()

    try:
        if Lang is None:
            if SysPlat == "Windows":
                buffer = ctypes.create_unicode_buffer(85)
                ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, len(buffer))
                Lang = buffer.value.replace("-", "_")
            elif SysPlat in ("Linux", "Darwin"):
                Lang = os.environ.get("LANG", "").split(".")[0]
            else:
                locale.setlocale(locale.LC_ALL, "")
                Lang = locale.getlocale()[1].replace("cp", "")
    except Exception:
        Lang = Default

    ML = (
        Word.get(Lang)
        if isinstance(Lang, str) and Lang in Word
        else Word.get(Locale.get(Lang)) if Lang in Locale else Word.get(Default)
    )

    return lambda text: ML.get(text, text)


Transl = Language()

# 地圖對應
GAME_MAPS = {
    "0": Transl('舊 SlashCo 總部'),
    "SlashCoHQ": Transl('舊 SlashCo 總部'),
    "1": Transl('馬龍斯農場'),
    "MalonesFarmyard": Transl('馬龍斯農場'),
    "2": Transl('菲利普斯•書斯特伍德高中'),
    "PhilipsWestwoodHighSchool": Transl('菲利普斯•書斯特伍德高中'),
    "3": Transl('伊斯特伍德綜合醫院'),
    "EastwoodGeneralHospital": Transl('伊斯特伍德綜合醫院'),
    "4": Transl('德爾塔科研機構'),
    "ResearchFacilityDelta": Transl('德爾塔科研機構'),
}

# 殺手對應
SLASHERS = {
    0: {
        "name": Transl('巴巴布伊 【肌肉男 / 隱形怪】'),
        "icon": f"{ASSETS}/BABABOOEY.webp",
    },
    1: {
        "name": Transl('席德 【手槍怪 / 餅乾怪】'),
        "icon": f"{ASSETS}/SID.webp",
    },
    2: {
        "name": Transl('特羅勒格巨魔【笑臉男 / 火柴人】'),
        "icon": f"{ASSETS}/TROLLAG.webp",
    },
    3: {
        "name": Transl('博格梅爾【機器人】'),
        "icon": f"{ASSETS}/BORGMIRE.webp",
    },
    4: {
        "name": Transl('阿博米納特【憎惡者 / 外星人】'),
        "icon": f"{ASSETS}/ABOMIGNAT.webp",
    },
    5: {
        "name": Transl('口渴 【爬行者 / 牛奶怪】'),
        "icon": f"{ASSETS}/THIRSTY.webp",
    },
    6: {
        "name": Transl('埃爾默神父 【霰彈槍 / 神父】'),
        "icon": f"{ASSETS}/FATHER_ELMER.webp",
    },
    7: {
        "name": Transl('觀察者 【高個子】'),
        "icon": f"{ASSETS}/THE_WATCHER.webp",
    },
    8: {
        "name": Transl('野獸 【貓貓 / 貓老太】'),
        "icon": f"{ASSETS}/THE_BEAST.webp",
    },
    9: {
        "name": Transl('海豚人'),
        "icon": f"{ASSETS}/DOLPHINMAN.webp",
    },
    10: {
        "name": Transl('伊戈爾【DJ / 創造者 / 毀滅者】'),
        "icon": f"{ASSETS}/IGOR.webp",
    },
    11: {
        "name": Transl('牢騷者【乞丐】'),
        "icon": f"{ASSETS}/THE_GROUCH.webp",
    },
    12: {
        "name": Transl('公主【狗】'),
        "icon": f"{ASSETS}/PRINCESS.webp",
    },
    13: {
        "name": Transl('極速奔跑者'),
        "icon": f"{ASSETS}/SPEEDRUNNER.webp",
    },
}

# 物品對應
ITEMS = {
    "Proxy-Locator": Transl('定位器'),
    "Royal Burger": Transl('皇家漢堡'),
    "Cookie": Transl('餅乾'),
    "Beer Keg": Transl('啤酒桶'),
    "Mayonnaise": Transl('美乃滋'),
    "Orange Jello": Transl('橙色果凍'),
    "Costco Frozen Pizza": Transl('COSTCO速凍披薩'),
    "Airport Jungle Juice": Transl('機場的烈性酒'),
    "Rhino Pill": Transl('犀牛丸'),
    "The Rock": Transl('岩石'),
    "Lab-Grown Meat": Transl('人造肉'),
    "Pocket Sand": Transl('沙袋'),
    "The Baby": Transl('巫毒娃娃'),
    "Newport Menthols": Transl('紐波特薄荷'),
    "B-GONE Soda": Transl('B-GONE蘇打水'),
    "Red40": Transl('40號紅色染劑'),
    "Red40 Vial": Transl('40號紅色染劑'),
    "Milk Jug": Transl('桶裝牛奶'),
    "Pot of Greed": Transl('貪婪之壺'),
    "Deathward": Transl('不死圖騰'),
    "Evil Jonkler Cart": Transl('邪惡的瓊克爾•卡特'),
    "25 Gram Benadryl": Transl('25克苯海拉明'),
    "Balkan Boost": Transl('巴爾幹激素'),
}

# 編譯物品解析正則
ITEMS_PATTERN = re.compile(
    "|".join(re.escape(key) for key in sorted(ITEMS.keys(), key=len, reverse=True)), re.IGNORECASE
)

# 編譯型別解析正則
LOG_PATTERNS = (
    (re.compile(r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*?Played Map:\s*([^,]+)"), "map"),
    (re.compile(r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*?Slasher:\s*(\d+)"), "slasher"),
    (
        re.compile(
            r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*?Selected Items:\s*(.+?)(?=,\s*\w+:|$)"
        ),
        "items",
    ),
    (
        re.compile(
            r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*?SC_(generator\d+) Progress check\. Last (\w+) value: (.*?), updated (\w+) value: (.*)"
        ),
        "generator",
    ),
)


def parse_items(items: str) -> str:
    """解析物品列表"""
    if not items:
        return ""

    matches = list(ITEMS_PATTERN.finditer(items))
    if not matches:
        return items

    result = []
    last_end = 0

    for match in matches:
        start, end = match.span()

        if start > last_end:
            unmatched = items[last_end:start].strip()
            if unmatched:
                result.append(unmatched)

        result.append(ITEMS[match.group()])
        last_end = end

    if last_end < len(items):
        unmatched = items[last_end:].strip()
        if unmatched:
            result.append(unmatched)

    return " / ".join(result)


def get_progress_color(value: int) -> str:
    """獲取進度條顏色"""
    for (min_val, max_val), color in PROGRESS_COLORS.items():
        if min_val <= value <= max_val:
            return color
    return "#2c2c2c"  # 預設


class ProgressBar(QProgressBar):
    """進度條 - 減少樣式更新開銷"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(25)
        self.setTextVisible(True)
        self.setRange(0, 100)
        self._current_color = "#555555"
        self._apply_style(self._current_color)

    def setValue(self, value: int):
        super().setValue(value)
        new_color = get_progress_color(value)
        if new_color != self._current_color:
            self._current_color = new_color
            self._apply_style(new_color)

    def _apply_style(self, color: str):
        self.setStyleSheet(
            f"""
            QProgressBar {{
                border: 2px solid #3c3c3c; border-radius: 8px; background-color: #2c2c2c;
                text-align: center; font-weight: bold; font-size: 12px; color: white;
            }}
            QProgressBar::chunk {{ background-color: {color}; border-radius: 6px; margin: 1px; }}
        """
        )


class SlashcoSenseMainWindow(QMainWindow):
    """主視窗類"""

    log_message = Signal(str)

    def __init__(self):
        super().__init__()

        self.log_dir = VRC_LOG_DIR

        # 開發測試用 (我本人沒玩 Slashco，所以沒有日誌目錄)
        if not self.log_dir.exists():
            self.log_dir = Path(__file__).parent / "TEST"

        # 初始化網路管理器（用於載入圖片）
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._on_image_loaded)

        self.info_cache = ""  # 資訊快取
        self.reset_mark = False  # 重置標記
        self.record_timestamp = {}  # 紀錄每種型別的最新時間戳

        self.gen1_progress: Optional[ProgressBar] = None
        self.gen1_label: Optional[QLabel] = None
        self.gen1_battery: Optional[QLabel] = None
        self.gen2_progress: Optional[ProgressBar] = None
        self.gen2_label: Optional[QLabel] = None
        self.gen2_battery: Optional[QLabel] = None

        self.osc_enabled = False
        self.osc_client: Optional[SimpleUDPClient] = None

        self.file_position = 0
        self.current_log_file: Optional[Path] = None

        # 立即初始化基本UI讓視窗快速顯示
        self._setup_ui()
        self._apply_dark_theme()

        # 延遲載入圖示和啟動日誌監控，避免阻塞UI顯示
        QTimer.singleShot(
            300,
            lambda: (
                (
                    lambda req: (  # 請求圖示
                        req.setAttribute(QNetworkRequest.Attribute.User, "icon"),
                        self.network_manager.get(req),
                    )
                )(QNetworkRequest(QUrl(WINDOWS_ICON_URL))),
                # 啟動監控
                setattr(self, "log_timer", QTimer()),
                self.log_timer.timeout.connect(self._monitor_logs),
                self.log_timer.start(LOG_UPDATE_INTERVAL),
                self.log_message.connect(self._append_log_message),
            ),
        )

    def _setup_ui(self):
        """設定使用者介面"""
        self.setWindowTitle("SlashCoSense")
        self.setMinimumSize(QSize(500, 700))
        self.resize(QSize(800, 800))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 遊戲狀態群組
        game_group = QGroupBox(Transl('遊戲狀態'))
        game_group.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))

        # 修改為水平佈局，左邊是遊戲資訊，右邊是圖片
        game_main_layout = QHBoxLayout(game_group)
        game_main_layout.setSpacing(15)

        # 左側：遊戲資訊
        game_info_widget = QWidget()
        game_layout = QVBoxLayout(game_info_widget)
        game_layout.setContentsMargins(0, 0, 0, 0)

        # 上方彈性空間 - 把內容推到中間
        game_layout.addStretch()

        self.map_label = QLabel(f"{Transl('地圖')}: {Transl('未知')}")
        self.slasher_label = QLabel(f"{Transl('殺手')}: {Transl('未知')}")
        self.items_label = QLabel(Transl('生成物品: 無'))

        font = QFont("Microsoft YaHei", 11)
        for label in [self.map_label, self.slasher_label, self.items_label]:
            label.setFont(font)

        # 手動新增文字和間距
        game_layout.addWidget(self.map_label)
        game_layout.addSpacing(20)  # 手動設定間距
        game_layout.addWidget(self.slasher_label)
        game_layout.addSpacing(20)  # 手動設定間距
        game_layout.addWidget(self.items_label)

        # 下方彈性空間 - 平衡上方空間
        game_layout.addStretch()

        # 右側：影像框
        image_widget = QWidget()
        image_layout = QVBoxLayout(image_widget)
        image_layout.setContentsMargins(0, 0, 5, 0)

        # 圖片顯示標籤
        self.image_label = QLabel()
        self.image_label.setObjectName("imageDisplay")
        self.image_label.setFixedSize(200, 200)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText(Transl('未知'))
        self.image_label.setScaledContents(True)

        image_layout.addWidget(self.image_label)

        # 將左右兩側新增到主佈局
        game_main_layout.addWidget(game_info_widget, 1)  # 權重1，可以伸縮
        game_main_layout.addWidget(image_widget, 0)  # 權重0，固定大小

        # 發電機狀態群組 - 直接建立，避免迴圈開銷
        gen_group = QGroupBox(Transl('發電機狀態'))
        gen_group.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        gen_layout = QVBoxLayout(gen_group)
        gen_layout.setSpacing(10)

        # 發電機 1
        gen1_layout = QHBoxLayout()
        gen1_layout.setSpacing(10)
        self.gen1_label = QLabel(f"{Transl('發電機')} 1")
        self.gen1_label.setMinimumWidth(20)
        self.gen1_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.gen1_progress = ProgressBar()
        self.gen1_progress.setMinimumWidth(250)
        self.gen1_progress.setFont(QFont("Microsoft YaHei", 10))
        self.gen1_battery = QLabel("🪫")
        self.gen1_battery.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))

        gen1_layout.addWidget(self.gen1_label)
        gen1_layout.addWidget(self.gen1_progress)
        gen1_layout.addWidget(self.gen1_battery)

        # 發電機 2
        gen2_layout = QHBoxLayout()
        gen2_layout.setSpacing(10)
        self.gen2_label = QLabel(f"{Transl('發電機')} 2")
        self.gen2_label.setMinimumWidth(20)
        self.gen2_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.gen2_progress = ProgressBar()
        self.gen2_progress.setMinimumWidth(250)
        self.gen2_progress.setFont(QFont("Microsoft YaHei", 10))
        self.gen2_battery = QLabel("🪫")
        self.gen2_battery.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))

        gen2_layout.addWidget(self.gen2_label)
        gen2_layout.addWidget(self.gen2_progress)
        gen2_layout.addWidget(self.gen2_battery)

        gen_widget1 = QWidget()
        gen_widget1.setLayout(gen1_layout)
        gen_widget2 = QWidget()
        gen_widget2.setLayout(gen2_layout)

        gen_layout.addWidget(gen_widget1)
        gen_layout.addWidget(gen_widget2)

        warning = QLabel(Transl('發電機監控僅限非房主有效'))
        warning.setObjectName("warningText")
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gen_layout.addWidget(warning)

        # OSC 設定群組
        osc_group = QGroupBox(Transl('OSC 設定'))
        osc_group.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        osc_layout = QHBoxLayout(osc_group)
        osc_layout.setSpacing(15)

        self.osc_enabled_checkbox = QCheckBox(Transl('啟用 OSC'))
        self.osc_enabled_checkbox.toggled.connect(self._toggle_osc)
        self.osc_enabled_checkbox.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.osc_log_enabled_checkbox = QCheckBox(Transl('顯示 OSC 日誌'))
        self.osc_log_enabled_checkbox.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.osc_log_enabled_checkbox.setChecked(True)

        self.port_input = QLineEdit(str(DEFAULT_OSC_PORT))
        self.port_input.setMaximumWidth(80)

        osc_layout.addWidget(self.osc_enabled_checkbox)
        osc_layout.addWidget(self.osc_log_enabled_checkbox)
        osc_layout.addStretch()
        osc_layout.addWidget(QLabel(Transl('埠號:')))
        osc_layout.addWidget(self.port_input)

        # 日誌顯示群組
        log_group = QGroupBox(Transl('日誌監控'))
        log_group.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        log_layout = QVBoxLayout(log_group)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 10))
        log_layout.addWidget(self.log_display)

        # 新增所有群組到主佈局
        main_layout.addWidget(game_group)
        main_layout.addWidget(gen_group)
        main_layout.addWidget(osc_group)
        main_layout.addWidget(log_group)

    def _apply_dark_theme(self):
        """應用暗黑主題"""
        self.setStyleSheet(
            """
            QMainWindow { background-color: #2b2b2b; color: #ffffff; }
            QGroupBox {
                font-weight: bold; border: 2px solid #3c3c3c; border-radius: 8px;
                margin-top: 1ex; padding-top: 10px; background-color: #333333;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; color: #ffffff;
            }
            QLabel { color: #ffffff; background-color: transparent; }
            QCheckBox { color: #ffffff; spacing: 5px; }
            QCheckBox::indicator { width: 18px; height: 18px; }
            QCheckBox::indicator:unchecked {
                border: 2px solid #555555; background-color: #2b2b2b; border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #27ae60; background-color: #27ae60; border-radius: 3px;
            }
            QLineEdit {
                background-color: #404040; border: 2px solid #555555; border-radius: 4px;
                padding: 5px; color: #ffffff;
            }
            QLineEdit:focus { border-color: #3498db; }
            QTextEdit {
                background-color: #1e1e1e; border: 2px solid #3c3c3c; border-radius: 8px;
                color: #ffffff; selection-background-color: #3498db;
            }
            QLabel#imageDisplay {
                border: 2px solid #555555;
                background-color: #404040;
                border-radius: 8px;
                color: #888888;
                font-size: 12px;
            }
            QLabel#warningText {
                color: #888888;
                font-size: 10px;
            }
        """
        )

    def _rounded_pixmap(self, pixmap: QPixmap, radius: int) -> QPixmap:
        size = pixmap.size()
        mask = QPixmap(size)
        mask.fill(Qt.GlobalColor.transparent)

        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, size.width(), size.height(), radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return mask

    def _on_image_loaded(self, reply: QNetworkReply):
        """圖片載入完成的回撥"""
        url = reply.request().attribute(QNetworkRequest.Attribute.User)
        self.image_label.setStyleSheet("")  # 恢復原本樣式

        if reply.error() == QNetworkReply.NetworkError.NoError:
            pixmap = QPixmap()
            image_data = reply.readAll()

            if url == "icon" and pixmap.loadFromData(image_data):  # 載入圖示
                # 裁出圖片中心的正方形區域
                w, h = pixmap.width(), pixmap.height()
                side = min(w, h)
                x = (w - side) // 2
                y = (h - side) // 2
                center_crop = pixmap.copy(x, y, side, side)

                # 圖示大小
                icon_size = 64
                scaled = center_crop.scaled(
                    icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )

                # 製作圓形遮罩
                circular = QPixmap(icon_size, icon_size)
                circular.fill(Qt.transparent)

                painter = QPainter(circular)
                painter.setRenderHint(QPainter.Antialiasing)
                path = QPainterPath()
                path.addEllipse(0, 0, icon_size, icon_size)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, scaled)
                painter.end()

                # 設定視窗圖示
                self.setWindowIcon(QIcon(circular))
            elif pixmap.loadFromData(image_data):  # 載入殺手圖片

                if url:
                    QPixmapCache.insert(url, pixmap)  # 存入 QPixmapCache

                # 縮放圖片以適應標籤大小
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

                # radius 與 QLabel 的 border-radius 相同
                self.image_label.setPixmap(self._rounded_pixmap(scaled_pixmap, radius=8))
            elif url != "icon":
                self.image_label.setText(Transl('載入失敗'))
        elif url != "icon":
            self.image_label.setText(Transl('載入失敗'))

        reply.deleteLater()

    def _set_image_url(self, url: str):
        """設定圖片URL（程式介面）"""
        if url:
            # 先從 QPixmapCache 快取找
            pixmap = QPixmap()
            if QPixmapCache.find(url, pixmap):
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.image_label.setPixmap(self._rounded_pixmap(scaled_pixmap, radius=8))
                self.image_label.setStyleSheet("")
                return

            # 如果快取中沒有，才進行網路請求
            request = QNetworkRequest(QUrl(url))
            # 將URL儲存到請求中，方便回撥時使用
            request.setAttribute(QNetworkRequest.Attribute.User, url)
            self.network_manager.get(request)

            # 設定載入中的樣式和文字
            self.image_label.clear()  # 清除之前的圖片
            self.image_label.setText("?")
            self.image_label.setStyleSheet(
                """
                    QLabel#imageDisplay {
                        color: red;
                        font-size: 100px;
                        font-weight: bold;
                        border-radius: 8px;
                        border: 5px solid red;
                        background-color: #404040;
                    }
                """
            )
        else:
            self.image_label.clear()
            self.image_label.setText(Transl('未知'))
            self.image_label.setStyleSheet("")

    def _toggle_osc(self, enabled: bool):
        """切換 OSC 狀態"""
        if enabled:
            try:
                port = int(self.port_input.text())
                if 1 <= port <= 65535 and UDP_CLIENT_AVAILABLE:
                    self.osc_client = udp_client.SimpleUDPClient("127.0.0.1", port)
                    self.osc_enabled = True
                    self.log_message.emit(f"{Transl('OSC 已啟用')}（{Transl('埠')}：{port}）")
                else:
                    self.log_message.emit(Transl('錯誤：埠號無效或 OSC 不可用'))
                    self.osc_enabled_checkbox.setChecked(False)
            except (ValueError, Exception):
                self.log_message.emit(Transl('錯誤：OSC 啟用失敗'))
                self.osc_enabled_checkbox.setChecked(False)
        else:
            self.osc_client = None
            self.osc_enabled = False
            self.log_message.emit(Transl('OSC 已停用'))

    def _send_osc(self, param: str, value: Any) -> bool:
        """快速傳送OSC引數"""
        if self.osc_enabled and self.osc_client:
            try:
                self.osc_client.send_message(f"/avatar/parameters/{param}", value)
                return True
            except Exception:
                pass
        return False

    def _append_log_message(self, message: str):
        """新增日誌訊息"""
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_display.append(f"{timestamp} {message}")

        # 保持日誌在底部
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _monitor_logs(self):
        """日誌監控"""
        try:
            # 檢查新檔案
            if not self.log_dir.exists():
                return

            log_files = list(self.log_dir.glob("output_log_*.txt"))
            if not log_files:
                return

            latest_file = max(log_files, key=lambda f: f.stat().st_mtime)
            if latest_file != self.current_log_file:
                self.current_log_file = latest_file
                self.file_position = 0
                self.log_message.emit(f"{Transl('開始監控日誌')}: {latest_file.name}")

            # 讀取新行
            if self.current_log_file.exists():
                with open(self.current_log_file, "r", encoding="utf-8", errors="ignore") as file:
                    file.seek(self.file_position)
                    new_content = file.read()
                    self.file_position = file.tell()

                if new_content:
                    for line in reversed(new_content.splitlines()):
                        if line.strip():
                            self._process_log_line(line.strip())
        except Exception:
            pass

    def _process_log_line(self, line: str):
        """最佳化後的日誌處理"""
        log_parts = []
        new_game_info = False

        # 單次遍歷所有模式，避免重複搜尋
        for pattern, data_type in LOG_PATTERNS:
            match = pattern.search(line)

            if not match:
                continue

            try:
                # 根據相同資料型別, 篩選掉舊的時間戳
                search_key = match.group(2) if data_type == "generator" else data_type
                log_timestamp = match.group(1)
                record_timestamp = self.record_timestamp.get(search_key, log_timestamp)

                if log_timestamp < record_timestamp:
                    continue

                self.record_timestamp[search_key] = log_timestamp

            except (ValueError, IndexError):
                pass

            if data_type == "map":
                new_game_info = True

                map_val = match.group(2).strip()
                map_name = GAME_MAPS.get(map_val, map_val)

                info = Transl('地圖')
                self.map_label.setText(f"{info}: \n{map_name}")
                log_parts.append(f"{info}: {map_name}")

            elif data_type == "slasher":
                new_game_info = True

                slasher_id = int(match.group(2))

                # 獲取殺手對應
                slasher_data = SLASHERS.get(
                    slasher_id,
                    {"name": f"{Transl('未知')}{Transl('殺手')}({slasher_id})", "icon": None},
                )

                name = slasher_data["name"]
                icon = slasher_data["icon"]

                info = Transl('殺手')
                self.slasher_label.setText(f"{info}: \n{name}")
                log_parts.append(f"{info}: {name}")

                # 更新圖片
                self._set_image_url(icon if icon else "")

                # 直接傳送OSC
                if (
                    self._send_osc("SlasherID", slasher_id)
                    and self.osc_log_enabled_checkbox.isChecked()
                ):
                    self.log_message.emit(f"{Transl('[OSC] 傳送 SlasherID')}: {slasher_id}")

            elif data_type == "items":
                items = parse_items(match.group(2).strip())
                self.items_label.setText(f"{Transl('生成物品')}: \n{items}")
                log_parts.append(f"{Transl('物品')}: {items}")
                new_game_info = True

            elif data_type == "generator" and not self.reset_mark:  # 重置標記時禁止更新
                _, gen_name, var_type, _, _, new_value = match.groups()
                self._update_generator(gen_name, var_type, new_value)
                log_parts.append(f"{gen_name} {var_type}: {new_value}")

        if log_parts:
            message = " | ".join(log_parts)

            if new_game_info:
                if message == self.info_cache:
                    # 重複的遊戲資訊 = 遊戲結束，執行重置邏輯
                    if not self.reset_mark:
                        self._reset_generators()
                        self.reset_mark = True
                    return
                else:
                    # 新的遊戲資訊 = 新遊戲開始
                    self.reset_mark = False
                    self.info_cache = message

            # 重置狀態下禁止傳送日誌
            if self.reset_mark:
                return

            self.log_message.emit(message)

    def _reset_generators(self):
        """重置所有發電機狀態 (不透過 _update_generator 更新, 減少效能開銷)"""

        # 重置發電機1
        self.gen1_progress.setValue(0)
        self.gen1_battery.setText("🪫")

        # 重置發電機2
        self.gen2_progress.setValue(0)
        self.gen2_battery.setText("🪫")

        # 直接傳送OSC訊息
        if self.osc_enabled:
            self._send_osc("GENERATOR1_FUEL", 0)
            self._send_osc("GENERATOR1_BATTERY", 0)
            self._send_osc("GENERATOR2_FUEL", 0)
            self._send_osc("GENERATOR2_BATTERY", 0)

    def _update_generator(self, gen_name: str, var_type: str, new_value: str):
        """發電機更新 - 直接訪問UI元素"""
        try:
            if var_type == "REMAINING":
                filled = 4 - int(new_value)
                progress = (filled * 100) // 4  # 使用整數除法

                # 直接更新對應的發電機，避免字典查詢
                if gen_name == "generator1":
                    self.gen1_progress.setValue(progress)
                    if (
                        self._send_osc("GENERATOR1_FUEL", filled)
                        and self.osc_log_enabled_checkbox.isChecked()
                    ):
                        self.log_message.emit(f"{Transl('[OSC] 傳送 GENERATOR1_FUEL')}: {filled}")
                elif gen_name == "generator2":
                    self.gen2_progress.setValue(progress)
                    if (
                        self._send_osc("GENERATOR2_FUEL", filled)
                        and self.osc_log_enabled_checkbox.isChecked()
                    ):
                        self.log_message.emit(f"{Transl('[OSC] 傳送 GENERATOR2_FUEL')}: {filled}")

            elif var_type == "HAS_BATTERY":
                has_battery = new_value.lower() == "true"
                battery_text = "🔋" if has_battery else "🪫"
                battery_value = 1 if has_battery else 0

                if gen_name == "generator1":
                    self.gen1_battery.setText(battery_text)
                    if (
                        self._send_osc("GENERATOR1_BATTERY", battery_value)
                        and self.osc_log_enabled_checkbox.isChecked()
                    ):
                        self.log_message.emit(
                            f"{Transl('[OSC] 傳送 GENERATOR1_BATTERY')}: {battery_value}"
                        )
                elif gen_name == "generator2":
                    self.gen2_battery.setText(battery_text)
                    if (
                        self._send_osc("GENERATOR2_BATTERY", battery_value)
                        and self.osc_log_enabled_checkbox.isChecked()
                    ):
                        self.log_message.emit(
                            f"{Transl('[OSC] 傳送 GENERATOR2_BATTERY')}: {battery_value}"
                        )
        except ValueError:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SlashcoSenseMainWindow()
    window.show()
    sys.exit(app.exec())
