#include "input/keypadService.hpp"

#include <Arduino.h>

namespace input {

constexpr char KeypadService::KEY_MAP[4][4];

KeypadService::KeypadService(const KeypadConfig& config)
    : config_(config)
{
}

void KeypadService::begin()
{
    const uint8_t rows[4] = { config_.row0, config_.row1, config_.row2, config_.row3 };
    const uint8_t cols[4] = { config_.col0, config_.col1, config_.col2, config_.col3 };

    for (uint8_t pin : rows) {
        pinMode(pin, OUTPUT);
        digitalWrite(pin, HIGH);
    }
    for (uint8_t pin : cols) {
        pinMode(pin, INPUT_PULLUP);
    }
}

char KeypadService::scan()
{
    const uint8_t rows[4] = { config_.row0, config_.row1, config_.row2, config_.row3 };
    const uint8_t cols[4] = { config_.col0, config_.col1, config_.col2, config_.col3 };

    for (int r = 0; r < 4; r++) {
        // Pull current row LOW
        digitalWrite(rows[r], LOW);

        for (int c = 0; c < 4; c++) {
            if (digitalRead(cols[c]) == LOW) {
                // Key pressed — wait for debounce
                const unsigned long now = millis();
                if (now - lastPressAt_ >= DEBOUNCE_MS) {
                    lastPressAt_ = now;

                    // Wait for release
                    while (digitalRead(cols[c]) == LOW) {
                        delay(10);
                    }

                    digitalWrite(rows[r], HIGH);
                    return KEY_MAP[r][c];
                }
            }
        }

        digitalWrite(rows[r], HIGH);
    }

    return 0;
}

}  // namespace input