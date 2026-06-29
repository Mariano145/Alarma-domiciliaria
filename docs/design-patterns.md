# Design Patterns — Home Alarm System

This document describes the GoF design patterns used in the system architecture, their purpose, and where they are applied in the code.

---

## 1. State Pattern

**Type:** Behavioral

**Purpose:** Allow the alarm system to change its behavior when its internal state changes. The alarm appears to change its class.

### Where it is applied

**Component:** `backend/services/alarm_state_manager.py`

**Context:** The alarm system has 4 distinct states with different behaviors:
- `DISARMED` — System deactivated, events are logged but do not trigger actions
- `ARMING_WAIT` — System arming, waiting for the user to leave
- `ARMED_COUNTDOWN` — System armed, countdown before full activation
- `ALARM` — Alarm triggered

**Behavior per state on MOTION_DETECTED:**
- `DisarmedState` — Ignores the event (you can move freely in your home)
- `ArmingWaitState` — Ignores the event (you are still leaving)
- `ArmedCountdownState` — Transitions to `ALARM` (intruder detection)
- `AlarmTriggeredState` — Ignores the event (already in alarm)

**Behavior per state on ARMING_TIMEOUT:**
- `DisarmedState` — Ignores the event (not applicable in this state)
- `ArmingWaitState` — Transitions to `DISARMED` (the user did not leave within the grace period)
- `ArmedCountdownState` — Ignores the event (not applicable in this state)
- `AlarmTriggeredState` — Ignores the event (not applicable in this state)

**Behavior per state on ENTRY_TIMEOUT:**
- `DisarmedState` — Ignores the event (not applicable in this state)
- `ArmingWaitState` — Ignores the event (not applicable in this state)
- `ArmedCountdownState` — Transitions to `ALARM` (the user did not enter the PIN within the countdown)
- `AlarmTriggeredState` — Ignores the event (already in alarm)

### Implementation Structure

```
AlarmStateManager (Context)
  ├─ state: AlarmState
  ├─ transition_to(new_state)
  └─ handle_event(event)

AlarmState (State Interface)
  ├─ handle_door_state_changed(context, event)
  ├─ handle_arm_button(context, event)
  ├─ handle_panic_button(context, event)
  ├─ handle_pin_attempt(context, event)
  ├─ handle_motion_detected(context, event)
  ├─ handle_arming_timeout(context, event)
  └─ handle_entry_timeout(context, event)

Concrete States:
  ├─ DisarmedState
  ├─ ArmingWaitState
  ├─ ArmedCountdownState
  └─ AlarmTriggeredState
```

### Why this pattern

- Each state encapsulates its own transition logic (e.g., `ArmedCountdownState` transitions to `AlarmTriggeredState` when the door opens, but `DisarmedState` ignores it)
- Adding new states (e.g., `MAINTENANCE_MODE`) does not require modifying existing state classes
- Eliminates large conditional blocks (`if state == X and event == Y`)
- State transitions are explicit and testable

---

## 2. Strategy Pattern

**Type:** Behavioral

**Purpose:** Define a family of analytics algorithms, encapsulate each one, and make them interchangeable. The client can choose which algorithm to use independently of the service that orchestrates them.

### Where it is applied

**Component:** `backend/services/analytics_service.py`

**Context:** The system needs to compute metrics derived from persisted events using different algorithms:
- **Windowed Counts** — Counts events by type within a 10-minute window (includes `motionDetections`)
- **PIN Fail Suspicious** — Hysteresis-based detection (activates with 3 failures, deactivates with 1 success)
- **Door Open Anomaly** — Threshold-based detection (activates if there are >6 openings in 10 min)

### Implementation Structure

```
AnalyticsService (Context)
  ├─ algorithms: list[AnalyticsAlgorithm]
  └─ calculate_metrics(events) -> dict

AnalyticsAlgorithm (Strategy Interface)
  └─ process(events: list[Event]) -> dict

Concrete Strategies:
  ├─ WindowedCountsAlgorithm
  ├─ PinFailHysteresisAlgorithm
  └─ DoorOpenAnomalyAlgorithm
```

### Why this pattern

- Each algorithm is independently testable and modifiable
- Adding new analytics (e.g., `MovementPatternDetector`) only requires creating a new strategy class
- The service does not need to know the details of each algorithm
- Algorithms can be configured at runtime (e.g., enable/disable specific analytics)

---

## 3. Observer Pattern — Implementation #1: Alarm State Changes

**Type:** Behavioral

**Purpose:** Define a one-to-many dependency between the alarm state manager and its observers, so that when the state changes, all dependent components are notified and updated automatically.

### Where it is applied

**Component:** `backend/services/alarm_state_manager.py` (Subject) + `backend/services/alarm_state_observer.py` (Observers)

**Context:** When the alarm transitions between states (e.g., `DISARMED` -> `ARMING_WAIT`), multiple components need to react:
- **Live state cache** — Update the cached state for fast responses to `/api/v1/alarm/state`
- **Event logger** — Log state transitions for auditing/debugging
- **Future: WebSocket Broadcaster** — Send state changes to connected frontend clients

### Implementation Structure

```
AlarmStateManager (Subject)
  ├─ observers: list[AlarmStateObserver]
  ├─ attach(observer)
  ├─ detach(observer)
  └─ notify_observers(previous_state, new_state)

AlarmStateObserver (Observer Interface)
  └─ on_alarm_state_changed(previous_state, new_state, timestamp)

Concrete Observers:
  ├─ LiveStateCacheObserver
  ├─ StateTransitionLoggerObserver
  └─ (future) WebSocketBroadcasterObserver
```

### Why this pattern

- The state manager does not need to know which components are interested in changes
- New observers can be added without modifying the subject (Open/Closed Principle)
- Decouples state transition logic from side effects (cache, logging, broadcasting)
- Observers can be enabled/disabled at runtime

---

## 4. Observer Pattern — Implementation #2: New Event Ingestion

**Type:** Behavioral

**Purpose:** Notify interested components when new events are ingested from the ESP32, enabling real-time processing and analytics updates.

### Where it is applied

**Component:** `backend/services/event_service.py` (Subject) + `backend/services/event_observer.py` (Observers)

**Context:** When a new event arrives via `POST /api/v1/events`, multiple components need to react:
- **Analytics cache invalidator** — Mark cached analytics as stale so the next request recalculates
- **Event stream logger** — Log the event for debugging/monitoring
- **Future: Real-time alert system** — Trigger immediate alerts for critical events (e.g., panic button)

### Implementation Structure

```
EventService (Subject)
  ├─ observers: list[EventObserver]
  ├─ attach(observer)
  ├─ detach(observer)
  └─ notify_observers(event)

EventObserver (Observer Interface)
  └─ on_new_event(event)

Concrete Observers:
  ├─ AnalyticsCacheInvalidatorObserver
  ├─ EventStreamLoggerObserver
  └─ (future) RealTimeAlertObserver
```

### Why this pattern

- Event ingestion logic is decoupled from subsequent processing
- New event handlers can be added without modifying `EventService`
- Observers can process events asynchronously if needed
- Critical events (panic button) can trigger immediate actions without waiting for polling

---

## Pattern Interaction

The patterns work together in the event processing flow:

```
ESP32 -> POST /events -> EventService.ingest()
                          ├─> Persist in PostgreSQL
                          ├─> AlarmStateManager.handle_event()
                          │     ├─> State Pattern: transition if applicable
                          │     └─> Observer #1: notify state change observers
                          └─> Observer #2: notify event ingestion observers

Frontend -> GET /alarm/state -> LiveStateCacheObserver (fed by Observer #1)
Frontend -> GET /analytics -> AnalyticsService
                              └─> Strategy Pattern: execute all analytics algorithms
```

---

## Summary Table

| Pattern | Component | Purpose | Key Classes |
|---------|-----------|---------|-------------|
| **State** | AlarmStateManager | Manage alarm state transitions (7 events: door, arm, panic, PIN, motion, arming_timeout, entry_timeout) | AlarmState, DisarmedState, ArmingWaitState, ArmedCountdownState, AlarmTriggeredState |
| **Strategy** | AnalyticsService | Encapsulate analytics algorithms | AnalyticsAlgorithm, WindowedCountsAlgorithm, PinFailHysteresisAlgorithm, DoorOpenAnomalyAlgorithm |
| **Observer #1** | AlarmStateManager | Notify state changes | AlarmStateObserver, LiveStateCacheObserver, StateTransitionLoggerObserver |
| **Observer #2** | EventService | Notify new events | EventObserver, AnalyticsCacheInvalidatorObserver, EventStreamLoggerObserver |
