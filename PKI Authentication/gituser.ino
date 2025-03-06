#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include <Crypto.h>
#include <SHA3.h>
#include <uECC.h>
#include <ESP8266HTTPClient.h>

#define SSID ""
#define PASSWORD ""
#define SERVER_URL "http://192.168.x.xxx:5000"

const uint8_t privateKey[32] = {0x7F, 0x11, 0x78, 0xFA, 0x26, 0x4E, 0xAF, 0xAB, 0xDF, 0xB2, 0xDD, 0x88, 0x6B, 0x97, 0xE2, 0x2B, 0x71, 0x2B, 0x8E, 0x80, 0x2D, 0x0D, 0x62, 0xC8, 0x45, 0xC4, 0xC9, 0x2E, 0x14, 0x0D, 0xB3, 0x01};

WiFiClient client;

int RNG(uint8_t *dest, unsigned size) {
    while (size--) {
        *dest++ = (uint8_t)random(0, 256);
    }
    return 1;
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.print("Connecting to WiFi...");
    WiFi.begin(SSID, PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected");
    Serial.print("ESP IP Address: ");
    Serial.println(WiFi.localIP());

    uECC_set_rng(&RNG);
    authenticate();
}

void authenticate() {
    Serial.println("\n[1] Connecting to authentication server...");

    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(client, SERVER_URL "/authenticate");

        int httpCode = http.GET();

        if (httpCode == HTTP_CODE_OK) {
            String response = http.getString();
            Serial.println("Raw Response: " + response);

            StaticJsonDocument<200> doc;
            DeserializationError error = deserializeJson(doc, response);
            if (error) {
                Serial.print("❌ JSON Parsing Failed: ");
                Serial.println(error.f_str());
                return;
            }

            String challengeHex = doc["challenge"];
            Serial.print("✅ Received Challenge: ");
            Serial.println(challengeHex);

            processChallenge(challengeHex);
        } else {
            Serial.print("❌ HTTP GET Error: ");
            Serial.println(httpCode);
        }
        http.end();
    } else {
        Serial.println("❌ Not connected to WiFi!");
    }
}

void processChallenge(String challengeHex) {
    Serial.println("🔒 Signing the challenge...");

    uint8_t challenge[16];
    for (int i = 0; i < 16; i++) {
        challenge[i] = strtol(challengeHex.substring(i * 2, i * 2 + 2).c_str(), NULL, 16);
    }

    SHA3_256 sha3;
    uint8_t hashDigest[32];
    sha3.reset();
    sha3.update(challenge, sizeof(challenge));
    sha3.finalize(hashDigest, sizeof(hashDigest));

    Serial.print("Computed SHA3-256 Hash: ");
    for (int i = 0; i < 32; i++) {
        if (hashDigest[i] < 16) Serial.print("0");
        Serial.print(hashDigest[i], HEX);
    }
    Serial.println();

    Serial.print("🔑 Private Key: ");
    for (int i = 0; i < 32; i++) {
        if (privateKey[i] < 16) Serial.print("0");
        Serial.print(privateKey[i], HEX);
    }
    Serial.println();

    uint8_t signature[64];
    const struct uECC_Curve_t *curve = uECC_secp256r1();

    if (!uECC_sign(privateKey, hashDigest, sizeof(hashDigest), signature, curve)) {
        Serial.println("❌ Failed to sign the challenge! Check RNG or private key.");
        return;
    }

    String signatureHex;
    for (int i = 0; i < 64; i++) {
        if (signature[i] < 16) signatureHex += "0";
        signatureHex += String(signature[i], HEX);
    }

    Serial.print("✅ Signature: ");
    Serial.println(signatureHex);

    sendSignature(challengeHex, signatureHex);
}

void sendSignature(String challengeHex, String signatureHex) {
    Serial.println("\n[3] Sending signed challenge to server...");

    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(client, SERVER_URL "/verify");
        http.addHeader("Content-Type", "application/json");

        String payload = "{\"challenge\": \"" + challengeHex + "\", \"signature\": \"" + signatureHex + "\"}";
        Serial.println("📤 Payload: " + payload);

        int httpCode = http.POST(payload);

        if (httpCode > 0) {
            String response = http.getString();
            Serial.println("✅ Server Response: " + response);
        } else {
            Serial.println("❌ HTTP POST Error");
        }
        http.end();
    } else {
        Serial.println("❌ Not connected to WiFi!");
    }
}

void loop() {}
