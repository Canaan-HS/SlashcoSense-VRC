import os
import time
import re
from datetime import datetime
from pythonosc import udp_client

# OSC配置
OSC_Enable = False #开关True/False
OSC_ADDRESS = "127.0.0.1"
OSC_PORT = 9000


# 映射关系配置
PLAYED_MAP = {
    0: "SlashCoHQ",
    1: "MalonesFarmyard",
    2: "PhilipsWestwoodHighSchool",
    3: "EastwoodGeneralHospital",
    4: "ResearchFacilityDelta"
}

SLASHER_MAP = {
    0: "Bababooey",
    1: "Sid",
    2: "Trollge",
    3: "Borgmire",
    4: "Abomignat",
    5: "Thirsty",
    6: "Elmo",
    7: "Watcher",
    8: "Beast",
    9: "Dolphinman",
    10: "Igor",
    11: "Grouch",
    12: "Princess",
    13: "Speedrunner"
}

def get_latest_log_file(log_dir):
    """获取最新日志文件"""
    try:
        if not os.path.isdir(log_dir):
            return None
        log_files = [
            os.path.join(log_dir, f) for f in os.listdir(log_dir)
            if f.startswith('output_log_') and f.endswith('.txt')
        ]
        return max(log_files, key=os.path.getmtime) if log_files else None
    except Exception as e:
        print(f"Error finding logs: {e}")
        return None

def parse_log_line(line):
    """解析日志行并返回格式化结果"""
    result = {}
    
    # 解析地图名称
    map_match = re.search(r"Played Map:\s*([^,]+)", line)
    if map_match:
        map_value = map_match.group(1).strip()
        if map_value.isdigit():
            map_id = int(map_value)
            result["map"] = PLAYED_MAP.get(map_id, f"Unknown Map({map_id})")
        else:
            result["map"] = map_value
    
    # 匹配Slasher并转换角色
    slasher_match = re.search(r"Slasher:\s*(\d+)", line)
    if slasher_match:
        slasher_id = int(slasher_match.group(1))
        result["slasher"] = SLASHER_MAP.get(slasher_id, f"Unknown Map({slasher_id})")
    
    # 匹配Selected Items
    items_match = re.search(r"Selected Items:\s*(.+?)(?=,\s*\w+:|$)", line)
    if items_match:
        result["items"] = items_match.group(1).strip()
    
    return result

def send_osc(data_dict):
    """发送OSC数据到VRChat"""
    try:
        client = udp_client.SimpleUDPClient(OSC_ADDRESS, OSC_PORT)
        
        # 发送杀手ID（0-13）
        if 'slasher' in data_dict:
            slasher_id = SLASHER_MAP.get(data_dict['slasher'], 0)
            client.send_message("/avatar/parameters/SlasherID", slasher_id)
            
    except Exception as e:
        print(f"OSC发送失败: {e}")

def monitor_logs():
    """监控日志文件变化并检测关键内容"""
    log_dir = os.path.expandvars(r'%USERPROFILE%\AppData\LocalLow\VRChat\VRChat')
    if not os.path.exists(log_dir):
        print("VRChat log directory not found")
        return

    current_file = None
    while True:
        latest = get_latest_log_file(log_dir)
        if not latest:
            time.sleep(1)
            continue
        
        if latest != current_file:
            current_file = latest
            print(f"Monitoring new file: {current_file}")
            try:
                with open(current_file, 'rb') as f:
                    f.seek(0, os.SEEK_END)
                    file_pos = f.tell()
            except Exception as e:
                print(f"Error opening file: {e}")
                continue

        try:
            with open(current_file, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(file_pos)
                lines = f.readlines()
                file_pos = f.tell()
                
                for line in lines:
                    cleaned_line = line.strip()
                    # 同时检测三个关键词
                    if any(k in cleaned_line for k in ["Played Map:", "Slasher:", "Selected Items:"]):
                        data = parse_log_line(cleaned_line)
                        
                        if OSC_Enable :
                            send_osc(data)  # 发送OSC数据

                        # 构建输出信息
                        output = []
                        if "map" in data:
                            output.append(f"Map: {data['map']}")
                        if "slasher" in data:
                            output.append(f"Slasher: {data['slasher']}")
                        if "items" in data:
                            output.append(f"Item: {data['items']}")
                        
                        if output:
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            output_line = f"[{timestamp}] [Game Start] " + " | ".join(output)
                            print(output_line)

        except Exception as e:
            print(f"Error reading file: {e}")

        time.sleep(0.1)

if __name__ == "__main__":
    if OSC_Enable :
        print(f"=== OSC监控启动于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    monitor_logs()
