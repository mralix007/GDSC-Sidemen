from flask import Flask, request, jsonify
import time
import os
import platform
from datetime import datetime
from collections import deque

app = Flask(__name__)

THRESHOLD_FREQUENCY = 15
THRESHOLD_SENSOR = 100
BLOCKED_DEVICES = {}
DEVICE_ACTIVITY = {}
LAST_MESSAGES = {}
ISOLATED_DEVICES = {}
REQUIRED_HEALTH_CHECKS = 5
ISOLATION_PERIOD = 300
NETWORK_STATUS = {
    'under_attack': False,
    'attack_start_time': None,
    'pause_duration': 60,
    'attack_type': None
}

def block_ip(ip_address):
    if ip_address not in BLOCKED_DEVICES:
        BLOCKED_DEVICES[ip_address] = time.time()
        print(f"🚨 BLOCKED IP: {ip_address} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def unblock_ip(ip_address):
    if ip_address in BLOCKED_DEVICES:
        del BLOCKED_DEVICES[ip_address]
        print(f"✅ Unblocked IP: {ip_address} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def pause_network(reason, attack_type):
    NETWORK_STATUS['under_attack'] = True
    NETWORK_STATUS['attack_start_time'] = time.time()
    NETWORK_STATUS['attack_type'] = attack_type
    print(f"🛑 NETWORK-WIDE PAUSE: {reason}")
    print(f"⚠️ Attack Type: {attack_type}")
    print(f"⏳ All devices paused for {NETWORK_STATUS['pause_duration']} seconds")

def check_network_status():
    if NETWORK_STATUS['under_attack']:
        elapsed = time.time() - NETWORK_STATUS['attack_start_time']
        if elapsed < NETWORK_STATUS['pause_duration']:
            remaining = NETWORK_STATUS['pause_duration'] - elapsed
            print(f"⏳ Network pause: {remaining:.0f} seconds remaining (Attack Type: {NETWORK_STATUS['attack_type']})")
            return False
        else:
            NETWORK_STATUS['under_attack'] = False
            NETWORK_STATUS['attack_type'] = None
            print("✅ Network pause lifted - resuming normal operations")
    return True

def isolate_device(device_id, reason, attack_type):
    ISOLATED_DEVICES[device_id] = {
        'timestamp': time.time(),
        'reason': reason,
        'check_count': 0,
        'last_check': 0,
        'consecutive_normal': 0,
        'attack_type': attack_type
    }
    print(f"🔒 Device {device_id} isolated: {reason}")
    pause_network(f"Attack detected from {device_id}: {reason}", attack_type)

def check_device_health(device_id, sensor_value):
    if device_id not in ISOLATED_DEVICES:
        return True
        
    device = ISOLATED_DEVICES[device_id]
    current_time = time.time()
    
    if current_time - device['timestamp'] < ISOLATION_PERIOD:
        print(f"⏳ Device {device_id} must remain isolated for {ISOLATION_PERIOD - (current_time - device['timestamp']):.0f} more seconds")
        return False
        
    if current_time - device['last_check'] < 60:
        print(f"⏳ Wait {60 - (current_time - device['last_check']):.0f} seconds before next health check")
        return False
        
    device['last_check'] = current_time
    device['check_count'] += 1
    
    if sensor_value <= THRESHOLD_SENSOR:
        device['consecutive_normal'] += 1
        print(f"✅ Health check {device['consecutive_normal']}/{REQUIRED_HEALTH_CHECKS} passed for {device_id}")
    else:
        device['consecutive_normal'] = 0
        print(f"❌ Health check failed for {device_id}: abnormal value detected")
        
    if device['consecutive_normal'] >= REQUIRED_HEALTH_CHECKS:
        del ISOLATED_DEVICES[device_id]
        print(f"🎉 Device {device_id} passed all health checks and is now un-isolated")
        return True
        
    return False

def is_replay_attack(device_id, sensor_value):
    if device_id in LAST_MESSAGES:
        last_data = LAST_MESSAGES[device_id]
        time_diff = time.time() - last_data['time']
        
        if sensor_value == last_data['value'] and time_diff < 2:
            repeat_count = last_data.get('repeat_count', 1)
            repeat_count += 1
            
            LAST_MESSAGES[device_id] = {
                'value': sensor_value,
                'time': time.time(),
                'repeat_count': repeat_count
            }
            
            if repeat_count > 3:
                print(f"🔄 Repeated value {sensor_value} detected {repeat_count} times in {time_diff:.1f} seconds")
                return True
        else:
            LAST_MESSAGES[device_id] = {
                'value': sensor_value,
                'time': time.time(),
                'repeat_count': 1
            }
    else:
        LAST_MESSAGES[device_id] = {
            'value': sensor_value,
            'time': time.time(),
            'repeat_count': 1
        }
    
    return False

def is_ddos_attack(device_id, timestamp):
    if device_id not in DEVICE_ACTIVITY:
        DEVICE_ACTIVITY[device_id] = {
            "request_times": deque(maxlen=THRESHOLD_FREQUENCY),
            "last_seen": timestamp
        }
    
    activity = DEVICE_ACTIVITY[device_id]
    current_time = timestamp
    
    activity["request_times"].append(current_time)
    activity["last_seen"] = current_time
    
    recent_requests = [t for t in activity["request_times"] if current_time - t <= 10]
    request_count = len(recent_requests)
    
    if request_count >= 2:
        time_span = recent_requests[-1] - recent_requests[0]
        if time_span > 0:
            request_rate = request_count / time_span
            print(f"📊 Rate: {request_rate:.1f} requests/second over {time_span:.1f} seconds")
            if request_rate > 5:
                return True
    
    return request_count >= THRESHOLD_FREQUENCY

def is_spoofing_attack(device_id):
    if "_" in device_id and device_id != "ESP32":
        return True
    return False

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json  
    device_id = data.get("device", "Unknown")
    sensor_value = data.get("sensor_value", 0)
    client_ip = request.remote_addr
    timestamp = time.time()

    print(f"\n📝 Request from {device_id} ({client_ip}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not check_network_status():
        return jsonify({
            "status": "PAUSED",
            "message": f"Network-wide security pause in effect - {NETWORK_STATUS['attack_type']}",
            "action": "WAIT"
        }), 403

    if device_id in ISOLATED_DEVICES:
        if not check_device_health(device_id, sensor_value):
            return jsonify({
                "status": "ISOLATED",
                "message": "Device is in isolation mode",
                "reason": ISOLATED_DEVICES[device_id]['reason'],
                "action": "WAIT"
            }), 403

    if client_ip in BLOCKED_DEVICES:
        if time.time() - BLOCKED_DEVICES[client_ip] > 300:
            unblock_ip(client_ip)
        else:
            print(f"❌ Rejected request from blocked IP: {client_ip}")
            return jsonify({
                "status": "BLOCKED",
                "message": "Your IP is quarantined",
                "action": "ISOLATE"
            }), 403

    if is_ddos_attack(device_id, timestamp):
        print(f"🔥 DDoS ATTACK DETECTED from {device_id} ({client_ip})!")
        block_ip(client_ip)
        isolate_device(device_id, "DDoS attack detected", "DDOS")
        return jsonify({
            "status": "BLOCKED",
            "reason": "DDoS detected",
            "action": "ISOLATE"
        }), 403

    if is_replay_attack(device_id, sensor_value):
        print(f"⚠️ Replay Attack Detected from {device_id} ({client_ip})")
        block_ip(client_ip)
        isolate_device(device_id, "Replay attack detected", "REPLAY")
        return jsonify({
            "status": "BLOCKED",
            "reason": "Replay attack detected",
            "action": "ISOLATE"
        }), 403

    if sensor_value > THRESHOLD_SENSOR:
        print(f"⚠️ Malicious data detected from {device_id} ({client_ip}) (Value: {sensor_value})")
        block_ip(client_ip)
        isolate_device(device_id, "Malicious data detected", "MALICIOUS")
        return jsonify({
            "status": "BLOCKED",
            "reason": "Malicious data detected",
            "action": "ISOLATE"
        }), 403

    if is_spoofing_attack(device_id):
        print(f"🎭 SPOOFING ATTACK DETECTED from {device_id} ({client_ip})!")
        block_ip(client_ip)
        isolate_device(device_id, "Device spoofing detected", "SPOOFING")
        return jsonify({
            "status": "BLOCKED",
            "reason": "Device spoofing detected",
            "action": "ISOLATE"
        }), 403

    response = {
        "device": device_id,
        "sensor_value": sensor_value,
        "status": "NORMAL",
        "action": "CONTINUE"
    }

    print(f"✅ Normal request processed: {response}")
    return jsonify(response), 200

if __name__ == '__main__':
    print(f"🚀 Starting server on port 3000...")
    print(f"⚙️ DDoS threshold: {THRESHOLD_FREQUENCY} requests per 10 seconds")
    print(f"⚙️ Malicious sensor threshold: {THRESHOLD_SENSOR}")
    app.run(host='0.0.0.0', port=3000, debug=True)

    