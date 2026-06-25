#ifndef FIRMWARE_ESP32_INCLUDE_DISPLAY_DISPLAY_TYPES_HPP
#define FIRMWARE_ESP32_INCLUDE_DISPLAY_DISPLAY_TYPES_HPP

#include <stdint.h>

namespace display {

/**
 * @brief Pin assignment for the 7-segment displays.
 */
struct DisplayConfig {
  uint8_t segA;
  uint8_t segB;
  uint8_t segC;
  uint8_t segD;
  uint8_t segE;
  uint8_t segF;
  uint8_t segG;
  uint8_t enable0;
  uint8_t enable1;
  uint8_t enable2;
  uint8_t enable3;
};

}  // namespace display

#endif  // FIRMWARE_ESP32_INCLUDE_DISPLAY_DISPLAY_TYPES_HPP