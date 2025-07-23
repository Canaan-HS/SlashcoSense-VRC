# Original Author : https://github.com/arcxingye/SlasherSense-VRC/

from Modules import (
    re,
    sys,
    Path,
    datetime,
    Optional,
    Any,
    udp_client,
    SimpleUDPClient,
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
    Qt,
    QUrl,
    QSize,
    QTimer,
    Signal,
    QFont,
    QIcon,
    QCursor,
    QPixmap,
    QPainter,
    QPixmapCache,
    QPainterPath,
    QNetworkAccessManager,
    QNetworkRequest,
    QNetworkReply,
    # 以下為 自訂模塊數據
    Transl,
    GetProgressColor,
    GAME_MAPS,
    SLASHERS,
    ITEMS,
    ITEMS_PATTERN,
    WINDOWS_ICON_URL,
    LOG_UPDATE_INTERVAL,
    VRC_LOG_DIR,
    UDP_CLIENT_AVAILABLE,
    DEFAULT_OSC_PORT,
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
    (
        re.compile(r"(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}).*?Generators reset(?: again)?\."),
        "reset",
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
        new_color = GetProgressColor(value)
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
            self.log_dir = (
                Path(sys.executable if getattr(sys, "frozen", False) else __file__).parent / "TEST"
            )

        # 初始化網路管理器（用於載入圖片）
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._on_image_loaded)

        self.session_key = ""
        self.standard_timestamp = ""

        self.reset_mark = False  # 重置標記
        self.process_cache = {}  # 處理快取

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
                        req.setAttribute(QNetworkRequest.Attribute.User, WINDOWS_ICON_URL),
                        self.network_manager.get(req),
                    )
                )(QNetworkRequest(QUrl(WINDOWS_ICON_URL))),
                # 啟動監控
                setattr(self, "log_timer", QTimer()),
                self.log_timer.timeout.connect(self._monitor_process_logs),
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
        game_group = QGroupBox(Transl("遊戲狀態"))
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
        self.items_label = QLabel(Transl("生成物品: 無"))

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
        self.image_label.setText(Transl("未知"))
        self.image_label.setScaledContents(True)

        image_layout.addWidget(self.image_label)

        # 將左右兩側新增到主佈局
        game_main_layout.addWidget(game_info_widget, 1)  # 權重1，可以伸縮
        game_main_layout.addWidget(image_widget, 0)  # 權重0，固定大小

        # 發電機狀態群組 - 直接建立，避免迴圈開銷
        gen_group = QGroupBox(Transl("發電機狀態"))
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

        warning = QLabel(Transl("發電機監控僅限非房主有效"))
        warning.setObjectName("warningText")
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gen_layout.addWidget(warning)

        # OSC 設定群組
        osc_group = QGroupBox(Transl("OSC 設定"))
        osc_group.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        osc_layout = QHBoxLayout(osc_group)
        osc_layout.setSpacing(15)

        self.osc_enabled_checkbox = QCheckBox(Transl("啟用 OSC"))
        self.osc_enabled_checkbox.toggled.connect(self._toggle_osc)
        self.osc_enabled_checkbox.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.osc_log_enabled_checkbox = QCheckBox(Transl("顯示 OSC 日誌"))
        self.osc_log_enabled_checkbox.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.osc_log_enabled_checkbox.setChecked(True)

        self.port_input = QLineEdit(str(DEFAULT_OSC_PORT))
        self.port_input.setMaximumWidth(80)

        osc_layout.addWidget(self.osc_enabled_checkbox)
        osc_layout.addWidget(self.osc_log_enabled_checkbox)
        osc_layout.addStretch()
        osc_layout.addWidget(QLabel(Transl("埠號:")))
        osc_layout.addWidget(self.port_input)

        # 日誌顯示群組
        log_group = QGroupBox(Transl("日誌監控"))
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

        is_local = "http" not in url and Path(url).is_file()
        pixmap = QPixmap()
        loaded = False

        if is_local:
            loaded = pixmap.load(url)
        elif reply.error() == QNetworkReply.NetworkError.NoError:
            image_data = reply.readAll()
            loaded = pixmap.loadFromData(image_data)

        if not loaded:
            if not url.lower().endswith(".ico"):  # .ico 載入失敗可不顯示錯誤
                self.image_label.setText(Transl("載入失敗"))
            reply.deleteLater()
            return

        if url.lower().endswith(".ico"):
            # 裁出中心正方形
            w, h = pixmap.width(), pixmap.height()
            side = min(w, h)
            x = (w - side) // 2
            y = (h - side) // 2
            cropped = pixmap.copy(x, y, side, side)

            # 縮放至 icon 尺寸
            icon_size = 64
            scaled = cropped.scaled(
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

        else:
            if url:
                QPixmapCache.insert(url, pixmap)

            # 縮放圖片以適應標籤大小
            scaled = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

            # 顯示圓角圖片
            self.image_label.setPixmap(self._rounded_pixmap(scaled, radius=8))

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
            self.image_label.setText(Transl("未知"))
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
                    self.log_message.emit(Transl("錯誤：埠號無效或 OSC 不可用"))
                    self.osc_enabled_checkbox.setChecked(False)
            except (ValueError, Exception):
                self.log_message.emit(Transl("錯誤：OSC 啟用失敗"))
                self.osc_enabled_checkbox.setChecked(False)
        else:
            self.osc_client = None
            self.osc_enabled = False
            self.log_message.emit(Transl("OSC 已停用"))

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

    def _monitor_process_logs(self):
        """日誌監控 處理解析日誌"""
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
                    for line in new_content.splitlines():
                        strip_line = line.strip()
                        if strip_line:
                            for pattern, data_type in LOG_PATTERNS:
                                match = pattern.search(strip_line)

                                if not match:
                                    continue

                                try:
                                    # 根據相同資料型別, 篩選掉舊的時間戳
                                    search_key = (
                                        match.group(2) if data_type == "generator" else data_type
                                    )
                                    log_timestamp = match.group(1)
                                    cache_timestamp = self.process_cache.get(
                                        search_key, match
                                    ).group(1)

                                    if log_timestamp < cache_timestamp:
                                        continue

                                    self.process_cache[search_key] = match
                                except (ValueError, IndexError):
                                    continue
                    self._update_ui()
        except Exception:
            pass

    def _update_ui(self):
        """解析日誌 更新 UI"""

        # 處理 地圖, 殺手, 物品, UI
        map_data = self.process_cache.pop("map", None)
        slasher_data = self.process_cache.pop("slasher", None)
        items_data = self.process_cache.pop("items", None)

        if map_data and slasher_data and items_data:
            timestamp = max(  # 雖然基本都是一樣的, 但為了安全, 這樣寫
                map_data.group(1), slasher_data.group(1), items_data.group(1)
            )

            if timestamp > self.standard_timestamp:
                self.reset_mark = False
                self.standard_timestamp = timestamp

                # 獲取地圖資訊
                map_val = map_data.group(2).strip()
                map_name = GAME_MAPS.get(map_val, map_val)
                map_info = Transl("地圖")

                # 獲取殺手資訊
                slasher_id = int(slasher_data.group(2))
                slasher_data = SLASHERS.get(
                    slasher_id,
                    {"name": f"{Transl('未知')}{Transl('殺手')}({slasher_id})", "icon": None},
                )
                slasher_name = slasher_data["name"]
                slasher_icon = slasher_data["icon"]
                slasher_info = Transl("殺手")

                # 獲取物品資訊
                items = parse_items(items_data.group(2).strip())

                # 更新 UI
                if map_name not in self.session_key:
                    self.map_label.setText(f"{map_info}: \n{map_name}")
                if slasher_name not in self.session_key:
                    self.slasher_label.setText(f"{slasher_info}: \n{slasher_name}")
                    self._set_image_url(slasher_icon if slasher_icon else "")  # 更新圖片

                    # 直接傳送OSC
                    if (
                        self._send_osc("SlasherID", slasher_id)
                        and self.osc_log_enabled_checkbox.isChecked()
                    ):
                        self.log_message.emit(f"{Transl('[OSC] 傳送 SlasherID')}: {slasher_id}")
                if items not in self.session_key:
                    self.items_label.setText(f"{Transl('生成物品')}: \n{items}")

                session_key = " | ".join(
                    [
                        f"{map_info}: {map_name}",
                        f"{slasher_info}: {slasher_name}",
                        f"{Transl('物品')}: {items}",
                    ]
                )

                if session_key != self.session_key:
                    self.session_key = session_key
                    self.log_message.emit(self.session_key)  # 傳送日誌

        # 處理發電機 UI
        for generator_data in [
            self.process_cache.pop("generator1", None),
            self.process_cache.pop("generator2", None),
        ]:
            if generator_data and not self.reset_mark:
                timestamp, gen_name, var_type, _, _, new_value = generator_data.groups()
                if timestamp > self.standard_timestamp:
                    self._update_generator(gen_name, var_type, new_value)
                    self.log_message.emit(f"{gen_name} {var_type}: {new_value}")  # 傳送日誌

        # 處理重置
        reset = self.process_cache.pop("reset", None)
        if reset:
            timestamp = reset.group(1)
            if timestamp > self.standard_timestamp:
                self.reset_mark = True
                self._reset_generators()
                self.log_message.emit("Generators Reset")  # 傳送日誌

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
