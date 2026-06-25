#ifndef FIRMWARE_ESP32_INCLUDE_NETWORK_NETWORK_TYPES_HPP
#define FIRMWARE_ESP32_INCLUDE_NETWORK_NETWORK_TYPES_HPP

namespace network {

/**
 * @brief Result of the LED control query against the backend.
 */
struct LedState {
  bool enabled;
  bool known;
};

/**
 * @brief Alarm event types accepted by POST /api/v1/events.
 */
enum class EventType {
  ArmButtonPressed,
  PanicButtonPressed,
  DoorStateChanged,
  PinAttempt,
  MotionDetected,
  ArmingTimeout,
  EntryTimeout,
};

/**
 * @brief Converts an EventType to its wire string representation.
 *
 * @param type Event type to convert.
 * @return const char* String matching the backend's EventType enum.
 */
inline const char* toString(EventType type) {
  switch (type) {
    case EventType::ArmButtonPressed:   return "ARM_BUTTON_PRESSED";
    case EventType::PanicButtonPressed: return "PANIC_BUTTON_PRESSED";
    case EventType::DoorStateChanged:   return "DOOR_STATE_CHANGED";
    case EventType::PinAttempt:         return "PIN_ATTEMPT";
    case EventType::MotionDetected:     return "MOTION_DETECTED";
    case EventType::ArmingTimeout:      return "ARMING_TIMEOUT";
    case EventType::EntryTimeout:       return "ENTRY_TIMEOUT";
  }
  return "";
}

}  // namespace network

#endif  // FIRMWARE_ESP32_INCLUDE_NETWORK_NETWORK_TYPES_HPP