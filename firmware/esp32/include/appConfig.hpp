#ifndef FIRMWARE_ESP32_INCLUDE_APP_CONFIG_HPP
#define FIRMWARE_ESP32_INCLUDE_APP_CONFIG_HPP

#include <Arduino.h>
#include <stdint.h>

#include "display/displayTypes.hpp"
#include "input/keypadTypes.hpp"

namespace app {

/**
 * @brief Runtime configuration for the ESP32 firmware.
 */
struct AppConfig {
  const char*   wifiSsid;
  const char*   wifiPassword;
  const char*   backendBaseUrl;
  const char*   deviceId;
  const char*   sensorId;
  uint8_t       doorPin;          // Sensor magnético de puerta (LOW=cerrada, HIGH=abierta)
  uint8_t       proximityPin;     // Sensor de proximidad ADC (potenciómetro)
  int           proximityThreshold; // Umbral ADC (0-4095) para activar MOTION_DETECTED
  uint8_t       alarmLedPin;      // LED de alarma (encendido fijo en estado ALARM)
  uint8_t       buzzerLedPin;     // LED buzzer (titila durante countdowns)
  unsigned long telemetryIntervalMs;
  unsigned long ledPollIntervalMs;
};

inline constexpr AppConfig CONFIG{
    "Jupiter",
    "+1980-2016",
    "http://192.168.100.2:5000",
    "esp32-alarma",
    "temperature-sensor-01",
    7,     // doorPin            — sensor magnético
    1,     // proximityPin       — ADC1_0, sensor de proximidad (potenciómetro)
    2048,  // proximityThreshold — umbral ADC (mitad del rango 12-bit)
    20,    // alarmLedPin        — LED alarma
    21,    // buzzerLedPin       — LED buzzer titilante
    10000UL,
    3000UL,
};

inline constexpr display::DisplayConfig DISPLAY_CONFIG{
    45,  // segA  me equivoque con el pinout, el segA es el 45 (GPIO45) que está al lado del 46 que es el DAC1
    48,  // segB  
    2,   // segC
    3,   // segD
    4,   // segE
    5,   // segF
    6,   // segG
    8,   // enable0
    9,   // enable1
    10,  // enable2
    11,  // enable3
};

inline constexpr input::KeypadConfig KEYPAD_CONFIG{
    12,  // row0
    13,  // row1
    14,  // row2
    15,  // row3
    16,  // col0
    17,  // col1
    18,  // col2
    19,  // col3
};

}  // namespace app

#endif  // FIRMWARE_ESP32_INCLUDE_APP_CONFIG_HPP