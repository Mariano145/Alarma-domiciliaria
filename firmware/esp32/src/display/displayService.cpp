#include "display/displayService.hpp"

#include <Arduino.h>

namespace display {

namespace {

    constexpr bool DIGITS[10][7] = {
        // A      B      C      D      E      F      G
        { true,  true,  true,  true,  true,  true,  false }, // 0
        { false, true,  true,  false, false, false, false }, // 1
        { true,  true,  false, true,  true,  false, true  }, // 2
        { true,  true,  true,  true,  false, false, true  }, // 3
        { false, true,  true,  false, false, true,  true  }, // 4
        { true,  false, true,  true,  false, true,  true  }, // 5
        { true,  false, true,  true,  true,  true,  true  }, // 6
        { true,  true,  true,  false, false, false, false }, // 7
        { true,  true,  true,  true,  true,  true,  true  }, // 8
        { true,  true,  true,  true,  false, true,  true  }, // 9
    };

    constexpr unsigned long DIGIT_PERSISTENCE_US = 2000;

}  // namespace

    DisplayService::DisplayService(const DisplayConfig& config)
        : config_(config)
    {
    }

    void DisplayService::begin()
    {
        const uint8_t segPins[7] = {
            config_.segA, config_.segB, config_.segC, config_.segD,
            config_.segE, config_.segF, config_.segG,
        };
        const uint8_t enablePins[4] = {
            config_.enable0, config_.enable1, config_.enable2, config_.enable3,
        };

        for (uint8_t pin : segPins) {
            pinMode(pin, OUTPUT);
            digitalWrite(pin, LOW);
        }
        for (uint8_t pin : enablePins) {
            pinMode(pin, OUTPUT);
            digitalWrite(pin, LOW);
        }
    }

    void DisplayService::update()
    {
        if (pinMode_) {
            renderDigits(pinDigits_[0], pinDigits_[1], pinDigits_[2], pinDigits_[3]);
        }
    }

    void DisplayService::showDigits(int d0, int d1, int d2, int d3)
    {
        pinMode_ = true;
        pinDigits_[0] = d0;
        pinDigits_[1] = d1;
        pinDigits_[2] = d2;
        pinDigits_[3] = d3;
    }

    void DisplayService::exitPinMode()
    {
        pinMode_ = false;

        // Apagar todos los segmentos y enables al salir
        const uint8_t segPins[7] = {
            config_.segA, config_.segB, config_.segC, config_.segD,
            config_.segE, config_.segF, config_.segG,
        };
        const uint8_t enablePins[4] = {
            config_.enable0, config_.enable1, config_.enable2, config_.enable3,
        };
        for (uint8_t pin : segPins)   digitalWrite(pin, LOW);
        for (uint8_t pin : enablePins) digitalWrite(pin, LOW);
    }

    void DisplayService::setNumberDisplay(int number) const
    {
        const uint8_t segPins[7] = {
            config_.segA, config_.segB, config_.segC, config_.segD,
            config_.segE, config_.segF, config_.segG,
        };

        if (number < 0 || number > 9) {
            for (uint8_t pin : segPins) digitalWrite(pin, LOW);
            return;
        }

        for (int i = 0; i < 7; i++) {
            digitalWrite(segPins[i], DIGITS[number][i] ? HIGH : LOW);
        }
    }

    void DisplayService::renderDigits(int d3, int d2, int d1, int d0) const
    {
        const uint8_t enablePins[4] = {
            config_.enable0, config_.enable1, config_.enable2, config_.enable3,
        };
        const int digits[4] = { d0, d1, d2, d3 };

        for (int i = 0; i < 4; i++) {
            for (uint8_t pin : enablePins) digitalWrite(pin, LOW);
            setNumberDisplay(digits[i]);
            digitalWrite(enablePins[i], HIGH);
            delayMicroseconds(DIGIT_PERSISTENCE_US);
        }

        for (uint8_t pin : enablePins) digitalWrite(pin, LOW);
    }

}  // namespace display