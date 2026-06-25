#include "network/networkClient.hpp"

#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WiFi.h>

auto constexpr WIFI_CONNECTION_TIMEOUT_MS = 15000UL;
auto constexpr HTTP_STATUS_OK = 200;
auto constexpr HTTP_STATUS_CREATED = 201;
auto constexpr HTTP_STATUS_MULTIPLE_CHOICES = 300;

namespace network {

    NetworkClient::NetworkClient(const app::AppConfig& config)
        : config_(config)
    {
    }

    void NetworkClient::begin()
    {
        connectToWifi();
    }

    void NetworkClient::ensureWifiConnection()
    {
        if (WiFi.status() != WL_CONNECTED)
        {
            connectToWifi();
        }
    }

    bool NetworkClient::isConnected() const
    {
        return WiFi.status() == WL_CONNECTED;
    }

    bool NetworkClient::postSensorReading(const sensors::SensorReading& reading)
    {
        if (!isConnected())
        {
            return false;
        }

        HTTPClient http;
        const String endpoint = String(config_.backendBaseUrl) + "/sensors";

        if (!http.begin(endpoint))
        {
            logMessage("Could not open telemetry endpoint.");
            return false;
        }

        http.addHeader("Content-Type", "application/json");

        JsonDocument payload;
        payload["sensorId"] = reading.sensorId;
        payload["temperature"] = reading.temperature;
        payload["humidity"] = reading.humidity;

        String body;
        serializeJson(payload, body);

        const int statusCode = http.POST(body);
        const String responseBody = http.getString();
        http.end();

        if (statusCode >= HTTP_STATUS_OK && statusCode < HTTP_STATUS_MULTIPLE_CHOICES)
        {
            logMessage("Telemetry sent. temp=" + String(reading.temperature, 1) + "C humidity=" +
                       String(reading.humidity, 1) + "%");
            return true;
        }

        logMessage("Telemetry failed. HTTP " + String(statusCode) + " body=" + responseBody);
        return false;
    }

    bool NetworkClient::postEvent(EventType type, const JsonObject& payload)
    {
        if (!isConnected())
        {
            return false;
        }

        HTTPClient http;
        const String endpoint = String(config_.backendBaseUrl) + "/api/v1/events";

        if (!http.begin(endpoint))
        {
            logMessage("Could not open events endpoint.");
            return false;
        }

        http.addHeader("Content-Type", "application/json");

        JsonDocument doc;
        doc["type"] = toString(type);
        doc["deviceId"] = config_.deviceId;
        doc["payload"] = payload;

        String body;
        serializeJson(doc, body);

        const int statusCode = http.POST(body);
        const String responseBody = http.getString();
        http.end();

        if (statusCode == HTTP_STATUS_CREATED)
        {
            logMessage("Event sent: " + String(toString(type)));
            return true;
        }

        logMessage("Event failed. HTTP " + String(statusCode) + " body=" + responseBody);
        return false;
    }

    LedState NetworkClient::fetchLedState()
    {
        LedState nextState{false, false};

        if (!isConnected())
        {
            return nextState;
        }

        HTTPClient http;
        const String endpoint = String(config_.backendBaseUrl) + "/devices/" + config_.deviceId + "/led";

        if (!http.begin(endpoint))
        {
            logMessage("Could not open LED control endpoint.");
            return nextState;
        }

        const int statusCode = http.GET();
        const String responseBody = http.getString();
        http.end();

        if (statusCode < HTTP_STATUS_OK || statusCode >= HTTP_STATUS_MULTIPLE_CHOICES)
        {
            logMessage("LED state fetch failed. HTTP " + String(statusCode) + " body=" + responseBody);
            return nextState;
        }

        JsonDocument payload;
        const DeserializationError error = deserializeJson(payload, responseBody);
        if (error)
        {
            logMessage("LED state JSON parse failed.");
            return nextState;
        }

        nextState.enabled = payload["enabled"] | false;
        nextState.known = true;
        return nextState;
    }

    void NetworkClient::connectToWifi()
    {
        if (WiFi.status() == WL_CONNECTED)
        {
            return;
        }

        // Modo AP+STA: genera su propia red y también intenta conectarse a una externa
        logMessage("Starting Access Point...");
        WiFi.mode(WIFI_AP_STA);
        WiFi.softAP("ESP32-AP", "12345678");
        logMessage("AP active. SSID: ESP32-AP | IP: " + WiFi.softAPIP().toString());

        logMessage("Connecting to Wi-Fi...");
        WiFi.begin(config_.wifiSsid, config_.wifiPassword);

        const unsigned long startedAt = millis();
        while (WiFi.status() != WL_CONNECTED && millis() - startedAt < WIFI_CONNECTION_TIMEOUT_MS)
        {
            delay(500);
            Serial.print('.');
        }
        Serial.println();

        if (WiFi.status() == WL_CONNECTED)
        {
            logMessage("Wi-Fi connected. IP: " + WiFi.localIP().toString());
            return;
        }

        logMessage("Wi-Fi connection failed. Will retry on next loop.");
    }

    void NetworkClient::logMessage(const String& message)
    {
        Serial.println(String("[ESP32] ") + message);
    }

}  // namespace network