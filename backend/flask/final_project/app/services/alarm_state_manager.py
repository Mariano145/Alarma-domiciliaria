"""
AlarmStateManager — Context class for the State pattern.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from app.models.entities.event import Event
from app.services.alarm_state_observer import AlarmStateObserver


class AlarmState(ABC):
    @abstractmethod
    def handle_door_state_changed(
        self, context: "AlarmStateManager", event: Event
    ) -> None: ...
    @abstractmethod
    def handle_arm_button(
        self, context: "AlarmStateManager", event: Event
    ) -> None: ...
    @abstractmethod
    def handle_panic_button(
        self, context: "AlarmStateManager", event: Event
    ) -> None: ...
    @abstractmethod
    def handle_pin_attempt(
        self, context: "AlarmStateManager", event: Event
    ) -> None: ...
    @abstractmethod
    def handle_motion_detected(
        self, context: "AlarmStateManager", event: Event
    ) -> None: ...
    @abstractmethod
    def handle_arming_timeout(
        self, context: "AlarmStateManager", event: Event
    ) -> None: ...
    @abstractmethod
    def handle_entry_timeout(
        self, context: "AlarmStateManager", event: Event
    ) -> None: ...

    @property
    @abstractmethod
    def state_code(self) -> str: ...


class DisarmedState(AlarmState):
    state_code = "DISARMED"

    def handle_door_state_changed(self, context, event): pass
    def handle_arm_button(self, context, event):
        context.transition_to(ArmingWaitState(), event)
    def handle_panic_button(self, context, event):
        context.transition_to(AlarmTriggeredState(), event)
    def handle_pin_attempt(self, context, event): pass
    def handle_motion_detected(self, context, event): pass
    def handle_arming_timeout(self, context, event): pass
    def handle_entry_timeout(self, context, event): pass


class ArmingWaitState(AlarmState):
    state_code = "ARMING_WAIT"

    def handle_door_state_changed(self, context, event):
        if event.payload.get("state") == "OPEN":
            context.transition_to(ArmedCountdownState(), event)
    def handle_arm_button(self, context, event):
        context.transition_to(DisarmedState(), event)
    def handle_panic_button(self, context, event):
        context.transition_to(AlarmTriggeredState(), event)
    def handle_pin_attempt(self, context, event):
        if event.payload.get("result") == "SUCCESS":
            context.transition_to(DisarmedState(), event)
    def handle_motion_detected(self, context, event): pass
    def handle_arming_timeout(self, context, event):
        context.transition_to(ArmedCountdownState(), event)
    def handle_entry_timeout(self, context, event): pass


class ArmedCountdownState(AlarmState):
    state_code = "ARMED_COUNTDOWN"

    def handle_door_state_changed(self, context, event): pass
    def handle_arm_button(self, context, event):
        context.transition_to(DisarmedState(), event)
    def handle_panic_button(self, context, event):
        context.transition_to(AlarmTriggeredState(), event)
    def handle_pin_attempt(self, context, event):
        if event.payload.get("result") == "SUCCESS":
            context.transition_to(DisarmedState(), event)
        else:
            context.transition_to(AlarmTriggeredState(), event)
    def handle_motion_detected(self, context, event):
        context.transition_to(AlarmTriggeredState(), event)
    def handle_arming_timeout(self, context, event): pass
    def handle_entry_timeout(self, context, event):
        context.transition_to(AlarmTriggeredState(), event)


class AlarmTriggeredState(AlarmState):
    state_code = "ALARM"

    def handle_door_state_changed(self, context, event): pass
    def handle_arm_button(self, context, event): pass
    def handle_panic_button(self, context, event): pass
    def handle_pin_attempt(self, context, event):
        if event.payload.get("result") == "SUCCESS":
            context.transition_to(DisarmedState(), event)
    def handle_motion_detected(self, context, event): pass
    def handle_arming_timeout(self, context, event): pass
    def handle_entry_timeout(self, context, event): pass


class AlarmStateManager:
    _EVENT_HANDLERS = {
        "DOOR_STATE_CHANGED":   "handle_door_state_changed",
        "ARM_BUTTON_PRESSED":   "handle_arm_button",
        "PANIC_BUTTON_PRESSED": "handle_panic_button",
        "PIN_ATTEMPT":          "handle_pin_attempt",
        "MOTION_DETECTED":      "handle_motion_detected",
        "ARMING_TIMEOUT":       "handle_arming_timeout",
        "ENTRY_TIMEOUT":        "handle_entry_timeout",
    }

    def __init__(self) -> None:
        self._state: AlarmState = DisarmedState()
        self._observers: list[AlarmStateObserver] = []

    def attach(self, observer: AlarmStateObserver) -> None:
        self._observers.append(observer)

    def detach(self, observer: AlarmStateObserver) -> None:
        self._observers.remove(observer)

    def notify_observers(
        self,
        prev_state: str,
        new_state: str,
        last_event_id: str | None = None,
        last_event_type: str | None = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        for observer in self._observers:
            if hasattr(observer, "_last_event_id"):
                observer.on_alarm_state_changed(
                    prev_state, new_state, now,
                    last_event_id=last_event_id,
                    last_event_type=last_event_type,
                )
            else:
                observer.on_alarm_state_changed(prev_state, new_state, now)

    def transition_to(self, new_state: AlarmState, event: Event | None = None) -> None:
        prev_code = self._state.state_code
        new_code = new_state.state_code
        if prev_code == new_code:
            return
        print(f"[AlarmStateManager] Transition: {prev_code} -> {new_code}")
        self._state = new_state
        self.notify_observers(
            prev_code,
            new_code,
            last_event_id=event.event_id if event else None,
            last_event_type=event.type if event else None,
        )

    def handle_event(self, event: Event) -> None:
        handler_name = self._EVENT_HANDLERS.get(event.type)
        if handler_name is None:
            print(f"[AlarmStateManager] Unknown event type: {event.type}")
            return
        getattr(self._state, handler_name)(self, event)

    @property
    def current_state_code(self) -> str:
        return self._state.state_code
