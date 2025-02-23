import os
import time
import re
from datetime import datetime
from pythonosc import udp_client

DEFAULT_PORT = 9000

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
    
    map_match = re.search(r"Played Map:\s*([^,]+)", line)
    if map_match:
        map_val = map_match.group(1).strip()
        result["map"] = PLAYED_MAP.get(int(map_val), map_val) if map_val.isdigit() else map_val
    
    slasher_match = re.search(r"Slasher:\s*(\d+)", line)
    if slasher_match:
        slasher_id = int(slasher_match.group(1))
        result["slasher"] = {
            "id": slasher_id,
            "name": SLASHER_MAP.get(slasher_id, f"Unknown({slasher_id})")
        }
    
    items_match = re.search(r"Selected Items:\s*(.+?)(?=,\s*\w+:|$)", line)
    if items_match:
        result["items"] = items_match.group(1).strip()
    
    return result

def get_user_config():
    """获取用户配置"""
    config = {"enable_osc": False, "osc_port": DEFAULT_PORT}
    
    # OSC启用询问
    while True:
        osc_choice = input("Enable OSC output? (Y/n): ").strip().lower()
        if osc_choice in ['y', '']:
            config["enable_osc"] = True
            break
        elif osc_choice == 'n':
            config["enable_osc"] = False
            break
        print("Invalid input, please enter Y/n")
    
    # 如果启用OSC则获取端口
    if config["enable_osc"]:
        while True:
            port_input = input(f"Enter OSC port [default {DEFAULT_PORT}]: ").strip()
            if not port_input:
                config["osc_port"] = DEFAULT_PORT
                break
            try:
                port = int(port_input)
                if 1 <= port <= 65535:
                    config["osc_port"] = port
                    break
                print("Port must be between 1-65535")
            except ValueError:
                print("Invalid port number")
    
    return config

def init_osc_client(port):
    """初始化OSC客户端"""
    try:
        return udp_client.SimpleUDPClient("127.0.0.1", port)
    except Exception as e:
        print(f"[OSC] Initialization failed: {str(e)}")
        return None

def monitor_logs(config):
    """主监控函数"""
    log_dir = os.path.expandvars(r'%USERPROFILE%\AppData\LocalLow\VRChat\VRChat')
    osc_client = init_osc_client(config["osc_port"]) if config["enable_osc"] else None
    
    current_file = None
    file_pos = 0
    
    print("\n[System] Starting monitoring...")
    if osc_client:
        print(f"[OSC] Ready on port {config['osc_port']}")
    else:
        print("[OSC] Output disabled")
    
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
                    
                    if 'map' in data:
                        output.append(f"Map: {data['map']}")
                    if 'slasher' in data:
                        output.append(f"Slasher: {data['slasher']['name']}")
                    if 'items' in data:
                        output.append(f"Items: {data['items']}")
                    
                    if output:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {' | '.join(output)}")
                    
                    # OSC发送逻辑
                    if osc_client and 'slasher' in data:
                        try:
                            osc_client.send_message("/avatar/parameters/SlasherID", data['slasher']['id'])
                            print(f"[OSC] Sent ID:{data['slasher']['id']}")
                        except Exception as e:
                            print(f"[OSC Error] {str(e)}")
                        
        except Exception as e:
            print(f"[Error] {datetime.now().strftime('%H:%M:%S')} - {str(e)}")
            time.sleep(1)

if __name__ == "__main__":
    print("=== SlasherSense By:arcxingye ===")
    user_config = get_user_config()
    monitor_logs(user_config)
