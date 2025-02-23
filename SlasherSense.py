import os
import time
import re
from datetime import datetime
from pythonosc import udp_client

# OSC配置
OSC_Enable = False #开关True/False
OSC_ADDRESS = "127.0.0.1"
OSC_PORT = 9000


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
    result = {}
    
    # 解析地图
    map_match = re.search(r"Played Map:\s*([^,]+)", line)
    if map_match:
        map_val = map_match.group(1).strip()
        result["map"] = PLAYED_MAP.get(int(map_val), map_val) if map_val.isdigit() else map_val
    
    # 解析杀手
    slasher_match = re.search(r"Slasher:\s*(\d+)", line)
    if slasher_match:
        slasher_id = int(slasher_match.group(1))
        result["slasher"] = {
            "id": slasher_id,
            "name": SLASHER_MAP.get(slasher_id, f"Unknown({slasher_id})")
        }
    
    # 解析物品
    items_match = re.search(r"Selected Items:\s*(.+?)(?=,\s*\w+:|$)", line)
    if items_match:
        result["items"] = items_match.group(1).strip()
    
    return result

def send_slasher_osc(slasher_id):
    try:
        client = udp_client.SimpleUDPClient(OSC_ADDRESS, OSC_PORT)
        client.send_message("/avatar/parameters/SlasherID", slasher_id)
    except Exception as e:
        print(f"[OSC Error] {datetime.now().strftime('%H:%M:%S')} - {str(e)}")

def monitor_logs():
    log_dir = os.path.expandvars(r'%USERPROFILE%\AppData\LocalLow\VRChat\VRChat')
    current_file = None
    file_pos = 0
    
    while True:
        latest = get_latest_log_file(log_dir)
        if not latest:
            time.sleep(1)
            continue
        
        if latest != current_file:
            current_file = latest
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring: {os.path.basename(current_file)}")
            try:
                with open(current_file, 'rb') as f:
                    f.seek(0, os.SEEK_END)
                    file_pos = f.tell()
            except Exception as e:
                print(f"File Error: {e}")
                continue

        try:
            with open(current_file, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(file_pos)
                lines = f.readlines()
                file_pos = f.tell()
                
                for line in lines:
                    cleaned = line.strip()
                    if not any(k in cleaned for k in ["Played Map:", "Slasher:", "Selected Items:"]):
                        continue
                    
                    data = parse_log_line(cleaned)
                    output = []
                    
                    # 控制台显示所有字段
                    if 'map' in data:
                        output.append(f"Map: {data['map']}")
                    if 'slasher' in data:
                        output.append(f"Slasher: {data['slasher']['name']}")
                    if 'items' in data:
                        output.append(f"Items: {data['items']}")
                    
                    if output:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {' | '.join(output)}")
                    
                    # 仅通过OSC发送杀手ID
                    if OSC_Enable:
                      if 'slasher' in data:
                          send_slasher_osc(data['slasher']['id'])
                        
        except Exception as e:
            print(f"[Error] {datetime.now().strftime('%H:%M:%S')} - {str(e)}")
            time.sleep(1)

if __name__ == "__main__":
    if OSC_Enable :
        print(f"=== OSC SlashCo Monitor {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    monitor_logs()
