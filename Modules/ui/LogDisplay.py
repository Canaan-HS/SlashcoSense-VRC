from ..language import transl
from ..bootstrap import QGroupBox, QFont, Optional, QWidget, QVBoxLayout, QTextEdit, datetime


class LogDisplayWidget(QGroupBox):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(transl("日誌監控"), parent)
        self.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self._setup_ui()

    def _setup_ui(self):
        log_layout = QVBoxLayout(self)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 10))
        log_layout.addWidget(self.log_display)

    def append_message(self, message: str):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_display.append(f"{timestamp} {message}")
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
