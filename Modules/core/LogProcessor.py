from ..language import transl
from ..utils import LOG_PATTERNS
from ..resources import GAME_MAPS, SLASHERS, parse_items
from ..bootstrap import Path, QThread, QObject, Optional, Signal, LOG_UPDATE_INTERVAL


class LogProcessor(QObject):
    """日誌處理器，在獨立執行緒中運行"""

    # 定義信號，用於將處理結果傳遞給主線程
    log_message_generated = Signal(str)
    game_info_updated = Signal(str, str, str, int)
    session_info_updated = Signal(str)
    generator_updated = Signal(str, str, str)
    generators_reset = Signal()

    def __init__(self, log_dir: Path):
        super().__init__()
        self.log_dir = log_dir
        self.current_log_file: Optional[Path] = None

        self.file_position = 0
        self.process_cache = {}
        self.standard_timestamp = ""

        self.reset_mark = False
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        """主處理循環"""
        while self.is_running:
            try:
                if not self.log_dir.exists():
                    QThread.msleep(LOG_UPDATE_INTERVAL)
                    continue

                log_files = list(self.log_dir.glob("output_log_*.txt"))
                if not log_files:
                    QThread.msleep(LOG_UPDATE_INTERVAL)
                    continue

                latest_file = max(log_files, key=lambda f: f.stat().st_mtime)
                if latest_file != self.current_log_file:
                    self.current_log_file = latest_file
                    self.file_position = 0
                    self.log_message_generated.emit(f"{transl('開始監控日誌')}: {latest_file.name}")

                if self.current_log_file.exists():
                    with open(self.current_log_file, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(self.file_position)
                        new_content = f.read()
                        self.file_position = f.tell()

                    if new_content:
                        self._process_log_content(new_content)
                        self._update_state()

            except Exception as e:
                self.log_message_generated.emit(f"Error in LogProcessor: {e}")

            QThread.msleep(LOG_UPDATE_INTERVAL)

    def _process_log_content(self, content: str):
        for line in content.splitlines():
            strip_line = line.strip()
            if not strip_line:
                continue

            for pattern, data_type in LOG_PATTERNS:
                match = pattern.search(strip_line)
                if not match:
                    continue

                try:
                    search_key = match.group(2) if data_type == "generator" else data_type
                    log_timestamp = match.group(1)
                    cache_timestamp = self.process_cache.get(search_key, match).group(1)

                    # 目前不一定要判斷時間戳, 基本上最終結果都是一樣的 (避免意外的寫法)
                    if log_timestamp >= cache_timestamp:
                        self.process_cache[search_key] = match
                except (ValueError, IndexError):
                    continue

    def _update_state(self):
        """根據快取解析資料並發射信號"""
        map_data = self.process_cache.pop("map", None)
        slasher_data = self.process_cache.pop("slasher", None)
        items_data = self.process_cache.pop("items", None)

        if map_data and slasher_data and items_data:
            timestamp = max(map_data.group(1), slasher_data.group(1), items_data.group(1))

            if timestamp > self.standard_timestamp:
                self.reset_mark = False
                self.standard_timestamp = timestamp

                map_val = map_data.group(2).strip()
                map_name = GAME_MAPS.get(map_val, map_val)

                slasher_id = int(slasher_data.group(2))
                slasher_info = SLASHERS.get(
                    slasher_id, {"name": f"{transl('未知')}({slasher_id})", "icon": None}
                )
                slasher_name = slasher_info["name"]
                slasher_icon = slasher_info["icon"]

                items = parse_items(items_data.group(2).strip())

                self.game_info_updated.emit(map_name, slasher_name, slasher_icon, slasher_id)

                session_key = " | ".join(
                    [
                        f"{transl('地圖')}: {map_name}",
                        f"{transl('殺手')}: {slasher_name}",
                        f"{transl('物品')}: {items}",
                    ]
                )

                self.session_info_updated.emit(session_key)

        for gen_id in ["generator1", "generator2"]:
            gen_data = self.process_cache.pop(gen_id, None)

            if gen_data and not self.reset_mark:
                timestamp, gen_name, var_type, _, _, new_value = gen_data.groups()
                if timestamp > self.standard_timestamp:
                    self.generator_updated.emit(gen_name, var_type, new_value)
                    self.log_message_generated.emit(f"{gen_name} {var_type}: {new_value}")

        reset_data = self.process_cache.pop("reset", None)
        if reset_data and reset_data.group(1) > self.standard_timestamp:
            self.reset_mark = True
            self.generators_reset.emit()
            self.log_message_generated.emit("Generators Reset")
