from ..language import transl
from ..bootstrap import (
    Qt,
    QFont,
    QLabel,
    QIcon,
    Path,
    QGroupBox,
    Optional,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QNetworkAccessManager,
    QNetworkReply,
    QUrl,
    QPixmap,
    QPainter,
    QPixmapCache,
    QPainterPath,
    QNetworkRequest,
    Signal,
)


class GameStatusWidget(QGroupBox):
    window_icon_ready = Signal(QIcon)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(transl("遊戲狀態"), parent)
        self.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))

        # 網路管理器，專門給這個組件用來載入殺手圖片
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self._on_image_loaded)

        self._setup_ui()

    def _setup_ui(self):
        game_main_layout = QHBoxLayout(self)
        game_main_layout.setSpacing(15)

        # 左側：遊戲資訊
        game_info_widget = QWidget()
        game_layout = QVBoxLayout(game_info_widget)
        game_layout.setContentsMargins(0, 0, 0, 0)
        game_layout.addStretch()

        self.map_label = QLabel(f"{transl('地圖')}: {transl('未知')}")
        self.slasher_label = QLabel(f"{transl('殺手')}: {transl('未知')}")
        self.items_label = QLabel(transl("生成物品: 無"))

        font = QFont("Microsoft YaHei", 11)
        for label in [self.map_label, self.slasher_label, self.items_label]:
            label.setFont(font)

        game_layout.addWidget(self.map_label)
        game_layout.addSpacing(20)
        game_layout.addWidget(self.slasher_label)
        game_layout.addSpacing(20)
        game_layout.addWidget(self.items_label)
        game_layout.addStretch()

        # 右側：影像框
        image_widget = QWidget()
        image_layout = QVBoxLayout(image_widget)
        image_layout.setContentsMargins(0, 0, 5, 0)

        self.image_label = QLabel()
        self.image_label.setObjectName("imageDisplay")
        self.image_label.setFixedSize(200, 200)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText(transl("未知"))
        self.image_label.setScaledContents(True)
        image_layout.addWidget(self.image_label)

        game_main_layout.addWidget(game_info_widget, 1)
        game_main_layout.addWidget(image_widget, 0)

    def update_info(self, map_name: str, slasher_name: str, items: str):
        self.map_label.setText(f"{transl('地圖')}: \n{map_name}")
        self.slasher_label.setText(f"{transl('殺手')}: \n{slasher_name}")
        self.items_label.setText(f"{transl('生成物品')}: \n{items}")

    def _rounded_pixmap(self, pixmap: QPixmap, radius: int) -> QPixmap:
        size = pixmap.size()
        rounded = QPixmap(size)
        rounded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, size.width(), size.height(), radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return rounded

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
                self.image_label.setText(transl("載入失敗"))
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
            self.window_icon_ready.emit(QIcon(circular))

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

    def set_image_url(self, url: str):
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
            self.image_label.setText(transl("未知"))
            self.image_label.setStyleSheet("")
