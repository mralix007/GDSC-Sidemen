#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char *ssid = "USER1";
const char *password = "Lakshan@1705.";
const char *serverURL = "http://192.168.1.5:3000/data";

bool isIsolated = false;
unsigned long isolationStartTime = 0;
const unsigned long ISOLATION_CHECK_INTERVAL = 60000;
const unsigned long HEALTH_CHECK_INTERVAL = 5000;

void enterIsolationMode(String reason)
{
    isIsolated = true;
    isolationStartTime = millis();
    Serial.println("⚠️ ENTERING ISOLATION MODE");
    Serial.println("Reason: " + reason);
}

void performHealthCheck()
{
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    int sensorValue = random(10, 50);
    String jsonPayload = "{\"device\": \"ESP32\", \"sensor_value\": " + String(sensorValue) + "}";

    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0)
    {
        String response = http.getString();
        StaticJsonDocument<200> doc;
        deserializeJson(doc, response);

        String action = doc["action"];

        if (action == "CONTINUE")
        {
            isIsolated = false;
            Serial.println("✅ Device passed health check - Resuming normal operation");
        }
        else if (action == "ISOLATE")
        {
            String reason = doc["reason"];
            enterIsolationMode(reason);
        }
    }

    http.end();
}

void setup()
{
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("Connected!");
}

void loop()
{
    if (WiFi.status() == WL_CONNECTED)
    {
        if (isIsolated)
        {
            if (millis() - isolationStartTime >= ISOLATION_CHECK_INTERVAL)
            {
                Serial.println("🔄 Performing isolation health check...");
                performHealthCheck();
                isolationStartTime = millis();
            }
        }
        else
        {
            HTTPClient http;
            http.begin(serverURL);
            http.addHeader("Content-Type", "application/json");

            int sensorValue = random(10, 50);
            String jsonPayload = "{\"device\": \"ESP32\", \"sensor_value\": " + String(sensorValue) + "}";

            int httpResponseCode = http.POST(jsonPayload);

            if (httpResponseCode > 0)
            {
                String response = http.getString();
                StaticJsonDocument<200> doc;
                deserializeJson(doc, response);

                String action = doc["action"];

                if (action == "ISOLATE")
                {
                    String reason = doc["reason"];
                    enterIsolationMode(reason);
                }

                Serial.print("Server Response: ");
                Serial.println(response);
            }
            else
            {
                Serial.print("Error sending POST request. Error code: ");
                Serial.println(httpResponseCode);
            }

            http.end();
            delay(HEALTH_CHECK_INTERVAL);
        }
    }
    else
    {
        Serial.println("WiFi Disconnected! Attempting to reconnect...");
        WiFi.begin(ssid, password);
        delay(5000);
    }
}