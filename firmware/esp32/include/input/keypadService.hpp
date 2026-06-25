#ifndef FIRMWARE_ESP32_INCLUDE_INPUT_KEYPAD_SERVICE_HPP
#define FIRMWARE_ESP32_INCLUDE_INPUT_KEYPAD_SERVICE_HPP

#include <Arduino.h>

#include "input/keypadTypes.hpp"

namespace input {

/**
 * @brief Reads a 4x4 matrix keypad without blocking the main loop.
 *
 * Key layout:
 *   1 2 3 A
 *   4 5 6 B
 *   7 8 9 C
 *   * 0 # D
 *
 * Key mapping for alarm system:
 *   0-9  → PIN digit input
 *   *    → confirm PIN
 *   #    → clear PIN
 *   A    → ARM_BUTTON_PRESSED
 *   B    → PANIC_BUTTON_PRESSED
 *   C    → DOOR_STATE_CHANGED (OPEN)
 *   D    → DOOR_STATE_CHANGED (CLOSED)
 */
class KeypadService {
public:
    explicit KeypadService(const KeypadConfig& config);

    /**
     * @brief Configures GPIO pins for rows and columns.
     */
    void begin();

    /**
     * @brief Scans the keypad and returns the pressed key, or 0 if none.
     *
     * Must be called frequently from the main loop.
     * Returns a char: '0'-'9', 'A'-'D', '*', '#', or 0 (no key).
     */
    char scan();

private:
    const KeypadConfig& config_;

    static constexpr char KEY_MAP[4][4] = {
        { '1', '2', '3', 'A' },
        { '4', '5', '6', 'B' },
        { '7', '8', '9', 'C' },
        { '*', '0', '#', 'D' },
    };

    unsigned long lastPressAt_ = 0;
    static constexpr unsigned long DEBOUNCE_MS = 200;
};

}  // namespace input

#endif  // FIRMWARE_ESP32_INCLUDE_INPUT_KEYPAD_SERVICE_HPP