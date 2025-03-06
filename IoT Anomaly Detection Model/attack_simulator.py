import requests
import time
import threading
import random
from datetime import datetime
import argparse
import socket
import netifaces

SERVER_URL = "http://192.168.1.5:3000/data"  
NORMAL_DELAY = 5  

def get_all_ips():
    """Get all available network interface IPs"""
    ips = []
    for interface in netifaces.interfaces():
        try:
            
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ips.append(addr['addr'])
        except Exception:
            continue
    return ips

AVAILABLE_IPS = get_all_ips()
ATTACK_IP = None
for ip in AVAILABLE_IPS:
    if ip != "127.0.0.1" and ip != SERVER_URL.split("//")[1].split(":")[0]:
        ATTACK_IP = ip
        break

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_attack(attack_type, message, status_code=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = Colors.FAIL if status_code in [403, 500] else Colors.GREEN
    status = f"[{status_code}]" if status_code else ""
    print(f"{color}[{timestamp}] [{attack_type}] {message} {status}{Colors.ENDC}")

def make_request(url, json_data, source_ip=None):
    """Make HTTP request with optional source IP binding"""
    session = requests.Session()
    if source_ip:
        session.mount('http://', requests.adapters.HTTPAdapter())
        session.mount('https://', requests.adapters.HTTPAdapter())
        session.get_adapter('http://').init_poolmanager(
            connections=100,
            maxsize=100,
            source_address=(source_ip, 0)
        )
    return session.post(url, json=json_data)

def normal_device():
    """Simulate a normal IoT device sending legitimate data"""
    device_id = f"NORMAL_DEVICE_{random.randint(1, 100)}"
    while True:
        try:
            sensor_value = random.randint(10, 50)
            payload = {
                "device": device_id,
                "sensor_value": sensor_value
            }
            response = make_request(SERVER_URL, payload)
            print_attack("NORMAL", f"Device: {device_id}, Value: {sensor_value}", response.status_code)
        except Exception as e:
            print_attack("NORMAL", f"Error: {e}")
        time.sleep(NORMAL_DELAY)

def ddos_attack():
    """Simulate a DDoS attack by sending rapid requests"""
    device_id = "DDOS_ATTACKER"
    while True:
        try:
            payload = {
                "device": device_id,
                "sensor_value": random.randint(10, 50)
            }
            response = make_request(SERVER_URL, payload, ATTACK_IP)
            print_attack("DDoS", f"Flooding server with requests from {ATTACK_IP}", response.status_code)
        except Exception as e:
            print_attack("DDoS", f"Error: {e}")
        time.sleep(0.1)

def replay_attack():
    """Simulate a replay attack by sending the same data repeatedly"""
    device_id = "REPLAY_ATTACKER"
    sensor_value = random.randint(10, 50)
    payload = {
        "device": device_id,
        "sensor_value": sensor_value
    }
    
    while True:
        try:
            response = make_request(SERVER_URL, payload)
            print_attack("REPLAY", f"Replaying data: {sensor_value}", response.status_code)
        except Exception as e:
            print_attack("REPLAY", f"Error: {e}")
        time.sleep(0.5)  

def malicious_data_attack():
    """Simulate an attack sending malicious sensor values"""
    device_id = "MALICIOUS_DEVICE"
    while True:
        try:
            
            sensor_value = random.randint(150, 999)
            payload = {
                "device": device_id,
                "sensor_value": sensor_value
            }
            response = make_request(SERVER_URL, payload)
            print_attack("MALICIOUS", f"Sending abnormal value: {sensor_value}", response.status_code)
        except Exception as e:
            print_attack("MALICIOUS", f"Error: {e}")
        time.sleep(2)  

def device_spoofing():
    """Simulate device spoofing by pretending to be legitimate devices"""
    while True:
        
        device_id = f"ESP32_{random.randint(1, 10)}"
        try:
            payload = {
                "device": device_id,
                "sensor_value": random.randint(10, 50)  
            }
            response = make_request(SERVER_URL, payload)
            print_attack("SPOOFING", f"Spoofing device: {device_id}", response.status_code)
        except Exception as e:
            print_attack("SPOOFING", f"Error: {e}")
        time.sleep(1)  

def main():
    parser = argparse.ArgumentParser(description='IoT Security Attack Simulator')
    parser.add_argument('--normal', action='store_true', help='Run normal device simulation')
    parser.add_argument('--ddos', action='store_true', help='Run DDoS attack')
    parser.add_argument('--replay', action='store_true', help='Run replay attack')
    parser.add_argument('--malicious', action='store_true', help='Run malicious data attack')
    parser.add_argument('--spoof', action='store_true', help='Run device spoofing attack')
    parser.add_argument('--all', action='store_true', help='Run all attacks')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return

    if ATTACK_IP is None:
        print(f"{Colors.WARNING}Warning: Could not find a separate network interface for attacks.{Colors.ENDC}")
        print(f"{Colors.WARNING}Available IPs: {', '.join(AVAILABLE_IPS)}{Colors.ENDC}")
        print(f"{Colors.WARNING}Attacks will originate from the same IP as normal traffic.{Colors.ENDC}\n")

    threads = []
    
    if args.normal or args.all:
        threads.append(threading.Thread(target=normal_device, daemon=True))
    if args.ddos or args.all:
        threads.append(threading.Thread(target=ddos_attack, daemon=True))
    if args.replay or args.all:
        threads.append(threading.Thread(target=replay_attack, daemon=True))
    if args.malicious or args.all:
        threads.append(threading.Thread(target=malicious_data_attack, daemon=True))
    if args.spoof or args.all:
        threads.append(threading.Thread(target=device_spoofing, daemon=True))

    print(f"{Colors.HEADER}Starting IoT Security Attack Simulator{Colors.ENDC}")
    print(f"{Colors.BLUE}Target Server: {SERVER_URL}{Colors.ENDC}")
    print(f"{Colors.BLUE}Attack Source IP: {ATTACK_IP or 'Default'}{Colors.ENDC}")
    print(f"{Colors.WARNING}Press Ctrl+C to stop the simulation{Colors.ENDC}\n")

    for thread in threads:
        thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Stopping simulation...{Colors.ENDC}")

if __name__ == "__main__":
    main() 

