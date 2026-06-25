#include <Arduino.h>
#include <ArduinoJson.h>

#include "appConfig.hpp"
#include "display/displayService.hpp"
#include "input/keypadService.hpp"
#include "network/networkClient.hpp"
#include "network/networkTypes.hpp"
#include "sensors/sensorService.hpp"

auto constexpr SERIAL_BAUD_RATE         = 115200;
auto constexpr DELAY_BETWEEN_TASKS_MS   = 10;
auto constexpr MAX_PIN_LENGTH           = 4;
auto constexpr CORRECT_PIN              = "1234";
auto constexpr ARMING_COUNTDOWN_SECS    = 30;
auto constexpr ENTRY_COUNTDOWN_SECS     = 30;
auto constexpr BUZZER_INTERVAL_START_MS = 1000;
auto constexpr BUZZER_INTERVAL_MIN_MS   = 100;
auto constexpr PROXIMITY_POLL_MS        = 200;
auto constexpr DOOR_DEBOUNCE_MS         = 500;

namespace {

    network::NetworkClient  networkClient(app::CONFIG);
    sensors::SensorService  sensorService(app::CONFIG);
    display::DisplayService displayService(app::DISPLAY_CONFIG);
    input::KeypadService    keypadService(app::KEYPAD_CONFIG);

    char pinBuffer[MAX_PIN_LENGTH + 1] = { 0 };
    int  pinLength = 0;

    unsigned long lastLedPollAt = 0;

    // ─── Estado local del firmware ───────────────────────────────────────────
    enum class LocalAlarmState {
        DISARMED,
        ARMING_WAIT,
        ARMED_COUNTDOWN,
        ALARM,
    };

    LocalAlarmState localState = LocalAlarmState::DISARMED;

    // ─── Countdown display ───────────────────────────────────────────────────
    enum class CountdownMode { NONE, ARMING, ENTRY };

    CountdownMode countdownMode     = CountdownMode::NONE;
    unsigned long countdownStartAt  = 0;
    int           countdownLastSecs = -1;

    // ─── Sensor magnético de puerta (IRQ) ───────────────────────────────────
    volatile bool doorStateChanged = false;
    volatile bool doorIsOpen       = false;
    unsigned long lastDoorEventAt  = 0;

    void IRAM_ATTR onDoorChanged()
    {
        const unsigned long now = millis();
        if (now - lastDoorEventAt < DOOR_DEBOUNCE_MS) return;
        lastDoorEventAt  = now;
        doorIsOpen       = digitalRead(app::CONFIG.doorPin) == HIGH;
        doorStateChanged = true;
    }

    // ─── Sensor de proximidad (ADC polling) ─────────────────────────────────
    bool          proximityActive     = false;
    unsigned long lastProximityPollAt = 0;

    // ─── LED buzzer titilante ────────────────────────────────────────────────
    bool          buzzerLedOn        = false;
    unsigned long buzzerLastToggleAt = 0;

    // ─── Actualizar display con PIN actual ───────────────────────────────────
    void updatePinDisplay()
    {
        int digits[4] = { -1, -1, -1, -1 };
        for (int i = 0; i < pinLength && i < 4; i++) {
            digits[i] = pinBuffer[i] - '0';
        }
        displayService.showDigits(digits[0], digits[1], digits[2], digits[3]);
    }

    // ─── Enviar evento al backend ────────────────────────────────────────────
    void sendEvent(network::EventType type, const JsonObject& payload)
    {
        networkClient.ensureWifiConnection();
        if (networkClient.isConnected()) {
            networkClient.postEvent(type, payload);
        }
    }

    // ─── Tarea sensor de puerta ──────────────────────────────────────────────
    void handleDoorTask()
    {
        if (!doorStateChanged) return;
        doorStateChanged = false;

        const bool isOpen = doorIsOpen;
        Serial.print("[ESP32] Door sensor: ");
        Serial.println(isOpen ? "OPEN" : "CLOSED");

        JsonDocument doc;
        JsonObject payload = doc.to<JsonObject>();
        payload["state"] = isOpen ? "OPEN" : "CLOSED";
        sendEvent(network::EventType::DoorStateChanged, payload);

        // FIX: solo iniciar countdown de entrada si no estaba ya corriendo
        if (isOpen && localState == LocalAlarmState::ARMED_COUNTDOWN) {
            if (countdownMode != CountdownMode::ENTRY) {
                countdownMode      = CountdownMode::ENTRY;
                countdownStartAt   = millis();
                countdownLastSecs  = -1;
                buzzerLastToggleAt = millis();
                Serial.println("[ESP32] Entry countdown started.");
            }
        }
    }

    // ─── Tarea sensor de proximidad (ADC polling) ────────────────────────────
    void handleProximityTask()
    {
        if (millis() - lastProximityPollAt < PROXIMITY_POLL_MS) return;
        lastProximityPollAt = millis();

        const int adcValue = analogRead(app::CONFIG.proximityPin);

        if (localState != LocalAlarmState::ARMED_COUNTDOWN) {
            proximityActive = false;
            return;
        }

        const bool detected = adcValue >= app::CONFIG.proximityThreshold;

        if (detected && !proximityActive) {
            proximityActive = true;
            Serial.print("[ESP32] Motion detected. ADC=");
            Serial.println(adcValue);

            JsonDocument doc;
            JsonObject payload = doc.to<JsonObject>();
            sendEvent(network::EventType::MotionDetected, payload);

            // FIX: actualizar estado local y detener el buzzer
            localState    = LocalAlarmState::ALARM;
            countdownMode = CountdownMode::NONE;
        } else if (!detected) {
            proximityActive = false;
        }
    }

    // ─── Tarea countdown display ─────────────────────────────────────────────
    void handleCountdownTask()
    {
        if (countdownMode == CountdownMode::NONE) return;

        int totalSecs = (countdownMode == CountdownMode::ARMING)
                        ? ARMING_COUNTDOWN_SECS
                        : ENTRY_COUNTDOWN_SECS;

        int elapsed   = (int)((millis() - countdownStartAt) / 1000);
        int remaining = totalSecs - elapsed;
        if (remaining < 0) remaining = 0;

        if (remaining != countdownLastSecs) {
            countdownLastSecs = remaining;
            displayService.showDigits(-1, -1, remaining / 10, remaining % 10);
        }

        if (remaining == 0) {
            network::EventType evType = (countdownMode == CountdownMode::ARMING)
                                        ? network::EventType::ArmingTimeout
                                        : network::EventType::EntryTimeout;

            countdownMode = CountdownMode::NONE;
            displayService.exitPinMode();

            if (evType == network::EventType::ArmingTimeout) {
                localState = LocalAlarmState::ARMED_COUNTDOWN;
            } else {
                localState = LocalAlarmState::ALARM;
            }

            JsonDocument doc;
            JsonObject payload = doc.to<JsonObject>();
            sendEvent(evType, payload);

            Serial.println(evType == network::EventType::ArmingTimeout
                ? "[ESP32] Arming timeout sent -> ARMED_COUNTDOWN"
                : "[ESP32] Entry timeout sent -> ALARM");
        }
    }

    // ─── Tarea LED buzzer titilante ──────────────────────────────────────────
    void handleBuzzerTask()
    {
        if (countdownMode == CountdownMode::NONE) {
            if (buzzerLedOn) {
                buzzerLedOn = false;
                digitalWrite(app::CONFIG.buzzerLedPin, LOW);
            }
            return;
        }

        int totalSecs = (countdownMode == CountdownMode::ARMING)
                        ? ARMING_COUNTDOWN_SECS
                        : ENTRY_COUNTDOWN_SECS;

        int elapsed   = (int)((millis() - countdownStartAt) / 1000);
        int remaining = totalSecs - elapsed;
        if (remaining < 0) remaining = 0;

        float progress = 1.0f - ((float)remaining / (float)totalSecs);
        int interval = (int)(BUZZER_INTERVAL_START_MS -
                       progress * (BUZZER_INTERVAL_START_MS - BUZZER_INTERVAL_MIN_MS));
        if (interval < BUZZER_INTERVAL_MIN_MS) interval = BUZZER_INTERVAL_MIN_MS;

        if (millis() - buzzerLastToggleAt >= (unsigned long)interval) {
            buzzerLastToggleAt = millis();
            buzzerLedOn = !buzzerLedOn;
            digitalWrite(app::CONFIG.buzzerLedPin, buzzerLedOn ? HIGH : LOW);
        }
    }

    // ─── Tarea LED alarma ────────────────────────────────────────────────────
    void handleAlarmLedTask()
    {
        digitalWrite(app::CONFIG.alarmLedPin,
                     localState == LocalAlarmState::ALARM ? HIGH : LOW);
    }

    // ─── Manejar tecla presionada ────────────────────────────────────────────
    void handleKey(char key)
    {
        Serial.print("[ESP32] Key pressed: ");
        Serial.println(key);

        if (key >= '0' && key <= '9') {
            if (pinLength < MAX_PIN_LENGTH) {
                pinBuffer[pinLength++] = key;
                pinBuffer[pinLength]   = '\0';
                updatePinDisplay();
            }

        } else if (key == '*') {
            bool success = (pinLength == MAX_PIN_LENGTH &&
                            strcmp(pinBuffer, CORRECT_PIN) == 0);

            JsonDocument doc;
            JsonObject payload = doc.to<JsonObject>();
            payload["result"] = success ? "SUCCESS" : "FAIL";
            sendEvent(network::EventType::PinAttempt, payload);

            Serial.println(success ? "[ESP32] PIN correct." : "[ESP32] PIN incorrect.");

            if (success) {
                countdownMode = CountdownMode::NONE;
                localState    = LocalAlarmState::DISARMED;
            } else if (localState == LocalAlarmState::ARMED_COUNTDOWN) {
                localState = LocalAlarmState::ALARM;
            }

            pinLength = 0;
            memset(pinBuffer, 0, sizeof(pinBuffer));
            displayService.exitPinMode();

        } else if (key == '#') {
            pinLength = 0;
            memset(pinBuffer, 0, sizeof(pinBuffer));
            displayService.exitPinMode();
            Serial.println("[ESP32] PIN cleared.");

        } else if (key == 'A') {
            // En estado ALARM la tecla A no hace nada, solo el PIN correcto desarma
            if (localState == LocalAlarmState::ALARM) return;

            JsonDocument doc;
            JsonObject payload = doc.to<JsonObject>();
            sendEvent(network::EventType::ArmButtonPressed, payload);

            if (localState == LocalAlarmState::DISARMED) {
                localState         = LocalAlarmState::ARMING_WAIT;
                countdownMode      = CountdownMode::ARMING;
                countdownStartAt   = millis();
                countdownLastSecs  = -1;
                buzzerLastToggleAt = millis();
                Serial.println("[ESP32] Arm button pressed -> ARMING_WAIT");
            } else {
                localState    = LocalAlarmState::DISARMED;
                countdownMode = CountdownMode::NONE;
                displayService.exitPinMode();
                Serial.println("[ESP32] Arm button pressed -> DISARMED");
            }

        } else if (key == 'B') {
            countdownMode = CountdownMode::NONE;
            localState    = LocalAlarmState::ALARM;

            JsonDocument doc;
            JsonObject payload = doc.to<JsonObject>();
            sendEvent(network::EventType::PanicButtonPressed, payload);
            Serial.println("[ESP32] Panic button pressed -> ALARM");
        }
    }

    void handleLedPollingTask()
    {
        if (millis() - lastLedPollAt < app::CONFIG.ledPollIntervalMs) return;
        lastLedPollAt = millis();
        // LED polling deshabilitado: endpoint no existe en este backend
    }

}  // namespace

void setup()
{
    Serial.begin(SERIAL_BAUD_RATE);

    // LEDs de salida
    pinMode(app::CONFIG.alarmLedPin,  OUTPUT);
    pinMode(app::CONFIG.buzzerLedPin, OUTPUT);
    digitalWrite(app::CONFIG.alarmLedPin,  LOW);
    digitalWrite(app::CONFIG.buzzerLedPin, LOW);

    // Sensor magnético de puerta con IRQ en ambos flancos
    pinMode(app::CONFIG.doorPin, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(app::CONFIG.doorPin),
                    onDoorChanged, CHANGE);

    // Sensor de proximidad ADC — resolución 12 bits (0-4095)
    analogReadResolution(12);

    delay(DELAY_BETWEEN_TASKS_MS * 10);
    Serial.println("[ESP32] Booting firmware...");

    sensorService.begin();
    displayService.begin();
    keypadService.begin();
    networkClient.begin();
}

void loop()
{
    displayService.update();
    handleDoorTask();
    handleProximityTask();
    handleCountdownTask();
    handleBuzzerTask();
    handleAlarmLedTask();

    const char key = keypadService.scan();
    if (key != 0) {
        handleKey(key);
    }

    handleLedPollingTask();
    delay(DELAY_BETWEEN_TASKS_MS);
}