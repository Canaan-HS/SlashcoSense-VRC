# Original Author : https://github.com/arcxingye/SlasherSense-VRC/

from Modules import (
    sys,
    Path,
    Optional,
    Any,
    udp_client,
    SimpleUDPClient,
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QUrl,
    QSize,
    QTimer,
    QThread,
    QNetworkRequest,
    # 以下為 自訂模塊數據
    transl,
    setLang,
    parse_items,
    LogProcessor,
    GameStatusWidget,
    LogDisplayWidget,
    OscSettingsWidget,
    GeneratorStatusWidget,
    VRC_LOG_DIR,
    WINDOWS_ICON_URL,
    UDP_CLIENT_AVAILABLE,
)


class SlashcoSenseMainWindow(QMainWindow):
    """主視窗類 - 負責協調 UI 組件和後端邏輯"""

    def __init__(self):
        super().__init__()

        self.osc_enabled = False
        self.osc_client: Optional[SimpleUDPClient] = None
        self.session_key = ""

        self._setup_ui()
        self._apply_dark_theme()
        self._setup_logic_thread()

    def _setup_ui(self):
        """設定使用者介面 - 建立並組合UI組件"""
        self.setWindowTitle("SlashCoSense")
        self.setMinimumSize(QSize(500, 700))
        self.resize(QSize(800, 800))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 建立UI組件實例
        self.game_status_widget = GameStatusWidget()
        self.generator_status_widget = GeneratorStatusWidget()
        self.osc_settings_widget = OscSettingsWidget()
        self.log_display_widget = LogDisplayWidget()

        # 將組件新增到主佈局
        main_layout.addWidget(self.game_status_widget)
        main_layout.addWidget(self.generator_status_widget)
        main_layout.addWidget(self.osc_settings_widget)
        main_layout.addWidget(self.log_display_widget)

        # 連接UI組件的信號
        self.osc_settings_widget.settings_changed.connect(self._toggle_osc)
        self.game_status_widget.window_icon_ready.connect(self.setWindowIcon)

    def _setup_logic_thread(self):
        """設定並啟動後端邏輯處理執行緒"""
        log_dir = VRC_LOG_DIR
        if not log_dir.exists():
            log_dir = (
                Path(sys.executable if getattr(sys, "frozen", False) else __file__).parent / "TEST"
            )

        self.logic_thread = QThread()
        self.log_processor = LogProcessor(log_dir)
        self.log_processor.moveToThread(self.logic_thread)

        # 連接後端處理器的信號到主視窗的槽
        self.logic_thread.started.connect(self.log_processor.run)
        self.log_processor.log_message_generated.connect(self.log_display_widget.append_message)
        self.log_processor.game_info_updated.connect(self._on_game_info_updated)
        self.log_processor.session_info_updated.connect(self._on_session_info_updated)
        self.log_processor.generator_updated.connect(self._on_generator_updated)
        self.log_processor.generators_reset.connect(self._on_generators_reset)

        # 統一延遲啟動 IO 密集型任務
        QTimer.singleShot(300, self._start_tasks)

    def _start_tasks(self):
        """啟動日誌監控和圖示載入"""

        # 1. 啟動日誌監控執行緒
        self.logic_thread.start()

        # 2. 請求視窗圖示 (由 GameStatusWidget 的 network_manager 處理)
        request = QNetworkRequest(QUrl(WINDOWS_ICON_URL))
        request.setAttribute(QNetworkRequest.Attribute.User, WINDOWS_ICON_URL)
        self.game_status_widget.network_manager.get(request)

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
                border: 2px solid #555555; background-color: #404040;
                border-radius: 8px; color: #888888; font-size: 12px;
            }
            QLabel#warningText { color: #888888; font-size: 10px; }
        """
        )

    def _on_game_info_updated(
        self, map_name: str, slasher_name: str, slasher_icon: str, slasher_id: int
    ):
        self.game_status_widget.update_info(map_name, slasher_name, parse_items(""))

        self.game_status_widget.set_image_url(slasher_icon if slasher_icon else "")

        if self._send_osc("SlasherID", slasher_id) and self.osc_settings_widget.is_log_enabled():
            self.log_display_widget.append_message(
                f"{transl('[OSC] 傳送 SlasherID')}: {slasher_id}"
            )

    def _on_session_info_updated(self, session_key: str):
        """當遊戲局內資訊更新時記錄日誌"""
        if session_key != self.session_key:
            self.session_key = session_key

            try:
                items_part = session_key.split(f"{transl('物品')}: ")[1]
                self.game_status_widget.items_label.setText(f"{transl('生成物品')}: \n{items_part}")
            except IndexError:
                pass

            self.log_display_widget.append_message(session_key)

    def _on_generator_updated(self, gen_name: str, var_type: str, new_value: str):
        """更新發電機UI"""
        self.generator_status_widget.update_generator(gen_name, var_type, new_value)

        # OSC 發送邏輯
        if var_type == "REMAINING":
            filled = 4 - int(new_value)
            param = f"GENERATOR{gen_name[-1]}_FUEL"
            if self._send_osc(param, filled) and self.osc_settings_widget.is_log_enabled():
                self.log_display_widget.append_message(f"{transl('[OSC] 傳送 ' + param)}: {filled}")
        elif var_type == "HAS_BATTERY":
            battery_value = 1 if new_value.lower() == "true" else 0
            param = f"GENERATOR{gen_name[-1]}_BATTERY"
            if self._send_osc(param, battery_value) and self.osc_settings_widget.is_log_enabled():
                self.log_display_widget.append_message(
                    f"{transl('[OSC] 傳送 ' + param)}: {battery_value}"
                )

    def _on_generators_reset(self):
        """重置發電機UI"""
        self.generator_status_widget.reset_generators()

        if self.osc_enabled:
            self._send_osc("GENERATOR1_FUEL", 0)
            self._send_osc("GENERATOR1_BATTERY", 0)
            self._send_osc("GENERATOR2_FUEL", 0)
            self._send_osc("GENERATOR2_BATTERY", 0)

    def _toggle_osc(self, enabled: bool, port: int):
        """切換 OSC 狀態"""
        if enabled:
            if 1 <= port <= 65535 and UDP_CLIENT_AVAILABLE:
                try:
                    self.osc_client = udp_client.SimpleUDPClient("127.0.0.1", port)
                    self.osc_enabled = True
                    self.log_display_widget.append_message(
                        f"{transl('OSC 已啟用')}（{transl('埠')}：{port}）"
                    )
                    return
                except Exception as e:
                    self.log_display_widget.append_message(f"{transl('錯誤：OSC 啟用失敗')}: {e}")
            else:
                self.log_display_widget.append_message(transl("錯誤：埠號無效或 OSC 不可用"))
        else:
            self.osc_client = None
            self.osc_enabled = False
            self.log_display_widget.append_message(transl("OSC 已停用"))

        # 如果啟用失敗或要禁用，則更新UI checkbox
        self.osc_settings_widget.set_enabled(False)

    def _send_osc(self, param: str, value: Any) -> bool:
        """快速傳送OSC引數"""
        if self.osc_enabled and self.osc_client:
            try:
                self.osc_client.send_message(f"/avatar/parameters/{param}", value)
                return True
            except Exception:
                return False
        return False

    def closeEvent(self, event):
        """關閉視窗時，確保後台執行緒也停止"""
        self.log_processor.stop()
        self.logic_thread.quit()
        self.logic_thread.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SlashcoSenseMainWindow()
    window.show()
    sys.exit(app.exec())
