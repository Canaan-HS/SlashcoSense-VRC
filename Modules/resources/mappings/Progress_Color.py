PROGRESS_COLORS = {
    (0, 25): "#555555",  # 灰色
    (25, 50): "#e74c3c",  # 紅色
    (50, 75): "#f39c12",  # 黃色
    (75, 100): "#27ae60",  # 綠色
}


def GetProgressColor(value: int) -> str:
    """獲取進度條顏色"""
    for (min_val, max_val), color in PROGRESS_COLORS.items():
        if min_val <= value <= max_val:
            return color
    return "#2c2c2c"  # 預設
