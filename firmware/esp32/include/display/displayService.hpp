#ifndef FIRMWARE_ESP32_INCLUDE_DISPLAY_DISPLAY_SERVICE_HPP
#define FIRMWARE_ESP32_INCLUDE_DISPLAY_DISPLAY_SERVICE_HPP

#include "display/displayTypes.hpp"

namespace display {

class DisplayService {
public:
    explicit DisplayService(const DisplayConfig& config);

    void begin();
    void update();
    void showDigits(int d0, int d1, int d2, int d3);
    void exitPinMode();

private:
    void setNumberDisplay(int number) const;
    void renderDigits(int d3, int d2, int d1, int d0) const;

    const DisplayConfig& config_;
    bool pinMode_ = false;
    int pinDigits_[4] = { -1, -1, -1, -1 };
};

}  // namespace display

#endif  // FIRMWARE_ESP32_INCLUDE_DISPLAY_DISPLAY_SERVICE_HPP