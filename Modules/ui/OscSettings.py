from ..language import transl
from ..bootstrap import (
    Qt,
    QFont,
    QCursor,
    QLabel,
    QGroupBox,
    Optional,
    QWidget,
    QHBoxLayout,
    QCheckBox,
    QLineEdit,
    Signal,
    DEFAULT_OSC_PORT,
)


class OscSettingsWidget(QGroupBox):
    settings_changed = Signal(bool, int)
    log_visibility_changed = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(transl("OSC 設定"), parent)
        self.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self._setup_ui()

    def _setup_ui(self):
        osc_layout = QHBoxLayout(self)
        osc_layout.setSpacing(15)

        self.osc_enabled_checkbox = QCheckBox(transl("啟用 OSC"))
        self.osc_enabled_checkbox.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.osc_enabled_checkbox.toggled.connect(self._on_settings_changed)

        self.osc_log_enabled_checkbox = QCheckBox(transl("顯示 OSC 日誌"))
        self.osc_log_enabled_checkbox.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.osc_log_enabled_checkbox.setChecked(True)
        self.osc_log_enabled_checkbox.toggled.connect(self.log_visibility_changed)

        self.port_input = QLineEdit(str(DEFAULT_OSC_PORT))
        self.port_input.setMaximumWidth(80)

        osc_layout.addWidget(self.osc_enabled_checkbox)
        osc_layout.addWidget(self.osc_log_enabled_checkbox)
        osc_layout.addStretch()
        osc_layout.addWidget(QLabel(transl("埠號:")))
        osc_layout.addWidget(self.port_input)

    def _on_settings_changed(self):
        is_enabled = self.osc_enabled_checkbox.isChecked()
        try:
            port = int(self.port_input.text())
        except ValueError:
            port = DEFAULT_OSC_PORT
        self.settings_changed.emit(is_enabled, port)

    def set_enabled(self, enabled: bool):
        self.osc_enabled_checkbox.blockSignals(True)
        self.osc_enabled_checkbox.setChecked(enabled)
        self.osc_enabled_checkbox.blockSignals(False)

    def is_log_enabled(self) -> bool:
        return self.osc_log_enabled_checkbox.isChecked()
