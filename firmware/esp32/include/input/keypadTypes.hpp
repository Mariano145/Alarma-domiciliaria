#ifndef FIRMWARE_ESP32_INCLUDE_INPUT_KEYPAD_TYPES_HPP
#define FIRMWARE_ESP32_INCLUDE_INPUT_KEYPAD_TYPES_HPP

#include <stdint.h>

namespace input {

/**
 * @brief Pin assignment for the 4x4 matrix keypad.
 */
struct KeypadConfig {
  uint8_t row0;
  uint8_t row1;
  uint8_t row2;
  uint8_t row3;
  uint8_t col0;
  uint8_t col1;
  uint8_t col2;
  uint8_t col3;
};

}  // namespace input

#endif  // FIRMWARE_ESP32_INCLUDE_INPUT_KEYPAD_TYPES_HPP