# IoT Security System

## Overview
This project focuses on securing IoT devices by detecting anomalies, isolating compromised devices, and mitigating cyber threats such as DDoS attacks, replay attacks, and device spoofing. It consists of:
- An ESP32-based security mechanism that monitors sensor data and reacts to threats.
- A Python-based attack simulator to test system resilience.
- A backend server that processes data and determines security actions.

## Features
- **Real-time anomaly detection**: Identifies abnormal behavior in IoT devices.
- **Self-isolation mechanism**: Devices enter isolation mode upon detection of malicious activity.
- **Security attack simulator**: Tests system resilience against various cyber threats.
- **Blockchain-based authentication** (planned): Prevents spoofing and unauthorized access.
- **AI-powered detection** (planned): Enhances accuracy in identifying cyber threats.

## Components
### 1. ESP32 Security System
The ESP32 device connects to WiFi, sends sensor data to the backend, and reacts to security responses.
- **Health checks**: Periodically verifies if the device should remain in isolation.
- **Automatic isolation**: Blocks malicious activity upon detection.
- **Reconnection mechanism**: Attempts to recover from an attack.

### 2. Attack Simulator
A Python-based tool to simulate various cyber attacks:
- **Normal Device**: Sends legitimate sensor data.
- **DDoS Attack**: Floods the server with rapid requests.
- **Replay Attack**: Repeats the same data to bypass authentication.
- **Malicious Data Injection**: Sends abnormal sensor values.
- **Device Spoofing**: Pretends to be legitimate devices.

## Installation & Usage
### ESP32 Setup
1. Install the **Arduino IDE** and the ESP32 board package.
2. Connect ESP32 to your network and upload the provided firmware.
3. Update `ssid`, `password`, and `serverURL` in the code.
4. Open the Serial Monitor to see logs.

### Running the Attack Simulator
1. Install dependencies:  
   ```bash
   pip install requests netifaces argparse
   ```
2. Run different attack simulations:
   ```bash
   python attack_simulator.py --ddos  # Simulate a DDoS attack
   python attack_simulator.py --replay  # Simulate a replay attack
   python attack_simulator.py --malicious  # Send abnormal data
   python attack_simulator.py --spoof  # Simulate device spoofing
   ```
3. To run all attacks simultaneously:
   ```bash
   python attack_simulator.py --all
   ```

## Future Enhancements
- Implement AI-based anomaly detection.
- Integrate blockchain authentication.
- Enhance self-healing mechanisms for infected devices.

## License
This project is open-source and available for modification and improvements.

---
**Contributors**: Lachu & Team 🚀

