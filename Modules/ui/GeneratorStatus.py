from ..language import transl
from .ProgressBar import ProgressBarWidget
from ..bootstrap import Qt, QFont, QGroupBox, Optional, QWidget, QVBoxLayout, QLabel, QHBoxLayout, Any


class GeneratorStatusWidget(QGroupBox):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(transl("發電機狀態"), parent)
        self.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self._setup_ui()

    def _setup_ui(self):
        gen_layout = QVBoxLayout(self)
        gen_layout.setSpacing(10)

        self.gen1_progress, self.gen1_battery = self._create_gen_ui(gen_layout, "1")
        self.gen2_progress, self.gen2_battery = self._create_gen_ui(gen_layout, "2")

        warning = QLabel(transl("發電機監控僅限非房主有效"))
        warning.setObjectName("warningText")
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gen_layout.addWidget(warning)

    def _create_gen_ui(self, layout: QVBoxLayout, num: str):
        h_layout = QHBoxLayout()
        h_layout.setSpacing(10)

        label = QLabel(f"{transl('發電機')} {num}")
        label.setMinimumWidth(20)
        label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))

        progress = ProgressBarWidget()
        progress.setMinimumWidth(250)
        progress.setFont(QFont("Microsoft YaHei", 10))

        battery = QLabel("🪫")
        battery.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))

        h_layout.addWidget(label)
        h_layout.addWidget(progress)
        h_layout.addWidget(battery)

        widget = QWidget()
        widget.setLayout(h_layout)
        layout.addWidget(widget)
        return progress, battery

    def update_generator(self, gen_name: str, var_type: str, new_value: Any):
        try:
            if var_type == "REMAINING":
                filled = 4 - int(new_value)
                progress = (filled * 100) // 4
                if gen_name == "generator1":
                    self.gen1_progress.setValue(progress)
                elif gen_name == "generator2":
                    self.gen2_progress.setValue(progress)
            elif var_type == "HAS_BATTERY":
                has_battery = str(new_value).lower() == "true"
                battery_text = "🔋" if has_battery else "🪫"
                if gen_name == "generator1":
                    self.gen1_battery.setText(battery_text)
                elif gen_name == "generator2":
                    self.gen2_battery.setText(battery_text)
        except (ValueError, TypeError):
            pass

    def reset_generators(self):
        self.gen1_progress.setValue(0)
        self.gen1_battery.setText("🪫")
        self.gen2_progress.setValue(0)
        self.gen2_battery.setText("🪫")
