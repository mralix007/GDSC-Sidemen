# ECC Authentication System for ESP8266 and Flask

This project implements an authentication system using **ECC (Elliptic Curve Cryptography)** with **ECDSA signatures** for secure communication between an **ESP8266 device** and a **Flask server**.

## Features

- **ECC Authentication:** Uses **ECDSA signatures** for authentication.
- **Challenge-Response Mechanism:** Ensures secure device verification.
- **WiFi Communication:** ESP8266 communicates with Flask over WiFi.
- **SHA3-256 Hashing:** For secure cryptographic signing.

## Prerequisites

### 1. Install Required Python Packages

Ensure you have Python installed, then install the required dependencies:

```sh
pip install flask cryptography ecdsa
```

### 2. Install ESP8266 Arduino Core

#### **Arduino IDE**

1. Open Arduino IDE.
2. Go to **File → Preferences**.
3. Add the following URL to **"Additional Board Manager URLs"**:
   ```
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
4. Go to **Tools → Board → Boards Manager** and install **ESP8266**.

#### **PlatformIO (VS Code)**

Install the `platformio-ide` extension and initialize an ESP8266 project:

```sh
pio project init --board esp8266
```

### 3. Install Required Arduino Libraries

Install these libraries in the **Arduino IDE**:

- **ArduinoJson**
- **ESP8266HTTPClient**
- **Crypto (For SHA3-256)**
- **uECC (For ECC signing)**

Use the **Arduino Library Manager** or install manually from ZIP files.

## Project Setup

### 1. Generate ECC Key Pair

Run the following script to generate ECC key pairs:

```sh
python generate_keys.py
```

This creates two files:

- `device_private_key.pem` (Private key for ESP8266)
- `device_public_key.pem` (Public key for Flask server)

### 2. Start Flask Server

Run the authentication server:

```sh
gitserver.py
```

By default, the Flask server runs on `http://0.0.0.0:5000`.

### 3. Upload Code to ESP8266

1. Open the `gituser.ino` file in Arduino IDE.
2. Replace the **WiFi credentials** with your network **SSID and password**.
3. Upload the sketch to your **ESP8266**.

### 4. Test the Authentication

1. Power on the ESP8266.
2. It will request a **challenge** from the server.
3. The ESP8266 will **sign the challenge** and send the **signature**.
4. The Flask server will **verify the signature** and authenticate the device.

### 5. Debugging & Logs

- **ESP8266 Serial Monitor:** Open the serial monitor (**baud rate: 115200**) to view logs.
- **Flask Server Logs:** Check the terminal output for authentication responses.

## API Endpoints

### `GET /authenticate`
Generates a random challenge for authentication.

**Response:**
```json
{
  "challenge": "<hex_encoded_challenge>"
}
```

### `POST /verify`
Verifies the signature sent by the ESP8266.

**Request Body:**
```json
{
  "challenge": "<hex_encoded_challenge>",
  "signature": "<hex_encoded_signature>"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Authentication successful"
}
```

## Troubleshooting

- **WiFi Connection Issues:** Check SSID and password.
- **Server Not Responding:** Ensure Flask is running on the correct IP.
- **Signature Verification Fails:** Ensure the correct **private and public keys** are used.

## License

This project is **open-source** and free to use.
