"""
Observer interface for alarm state transitions (Observer Pattern #1).

Any component that needs to react when the alarm state changes must
implement this interface and register itself with ``AlarmStateManager``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime


class AlarmStateObserver(ABC):
    """Abstract base for components observing alarm state transitions."""

    @abstractmethod
    def on_alarm_state_changed(
        self,
        prev_state: str,
        new_state: str,
        timestamp: datetime,
        last_event_id: str | None = None,
        last_event_type: str | None = None,
    ) -> None:
        """Called by AlarmStateManager after every state transition."""
        ...


class StateTransitionLoggerObserver(AlarmStateObserver):
    """Logs every alarm state transition to the console."""

    def on_alarm_state_changed(
        self,
        prev_state: str,
        new_state: str,
        timestamp: datetime,
        last_event_id: str | None = None,
        last_event_type: str | None = None,
    ) -> None:
        print(
            f"[AlarmState] {timestamp.isoformat()} "
            f"{prev_state} -> {new_state}"
        )


class LiveStateCacheObserver(AlarmStateObserver):
    """
    Caches the current alarm state for fast responses to
    GET /api/v1/alarm/state without hitting the database.
    """

    def __init__(self) -> None:
        from datetime import timezone
        self._state_code: str = "DISARMED"
        self._state_label: str = "Desarmada"
        self._updated_at: datetime = datetime.now(timezone.utc)
        self._last_event_id: str | None = None
        self._last_event_type: str | None = None

    def on_alarm_state_changed(
        self,
        prev_state: str,
        new_state: str,
        timestamp: datetime,
        last_event_id: str | None = None,
        last_event_type: str | None = None,
    ) -> None:
        self._state_code = new_state
        self._state_label = self._label_for(new_state)
        self._updated_at = timestamp
        self._last_event_id = last_event_id
        self._last_event_type = last_event_type

    def get_state(self) -> dict:
        return {
            "stateCode": self._state_code,
            "stateLabel": self._state_label,
            "updatedAt": self._updated_at.isoformat(),
            "lastEventId": self._last_event_id,
            "lastEventType": self._last_event_type,
        }

    @staticmethod
    def _label_for(state_code: str) -> str:
        return {
            "DISARMED": "Desarmada",
            "ARMING_WAIT": "Armando...",
            "ARMED_COUNTDOWN": "Armada",
            "ALARM": "Alarma",
        }.get(state_code, state_code)
