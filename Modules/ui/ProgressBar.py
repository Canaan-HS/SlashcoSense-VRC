from ..bootstrap import QProgressBar
from ..resources import GetProgressColor


class ProgressBarWidget(QProgressBar):
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
