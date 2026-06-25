from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.alarm_state_manager import (
    AlarmStateManager,
    AlarmTriggeredState,
)


def make_event(event_type: str, payload: dict | None = None, event_id: str = "evt-001"):
    evt = MagicMock()
    evt.type = event_type
    evt.event_id = event_id
    evt.payload = payload or {}
    return evt

def make_observer(*, extended: bool = True) -> MagicMock:
    obs = MagicMock()
    if not extended:
        del obs._last_event_id
    return obs

class TestAlarmStateManagerInit:
    def test_initial_state_is_disarmed(self):
        mgr = AlarmStateManager()
        assert mgr.current_state_code == "DISARMED"

    def test_initial_observer_list_is_empty(self):
        mgr = AlarmStateManager()
        assert mgr._observers == []

    def test_two_instances_are_independent(self):
        mgr1, mgr2 = AlarmStateManager(), AlarmStateManager()
        obs = make_observer()
        mgr1.attach(obs)
        assert obs not in mgr2._observers

class TestObserverManagement:
    def test_attach_adds_observer(self):
        mgr = AlarmStateManager()
        obs = make_observer()
        mgr.attach(obs)
        assert obs in mgr._observers

    def test_detach_removes_observer(self):
        mgr = AlarmStateManager()
        obs = make_observer()
        mgr.attach(obs)
        mgr.detach(obs)
        assert obs not in mgr._observers

class TestNotifyObservers:
    def test_extended_observer_receives_event_kwargs(self):
        mgr = AlarmStateManager()
        obs = make_observer(extended=True)
        mgr.attach(obs)
        mgr.notify_observers("DISARMED", "ALARM", "evt-42", "PANIC_BUTTON_PRESSED")
        obs.on_alarm_state_changed.assert_called_once()

    def test_timestamp_is_utc_datetime(self):
        mgr = AlarmStateManager()
        obs = make_observer(extended=True)
        mgr.attach(obs)
        fixed = datetime(2026, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
        with patch("app.services.alarm_state_manager.datetime") as mock_dt:
            mock_dt.now.return_value = fixed
            mgr.notify_observers("DISARMED", "ALARM")
        args, _ = obs.on_alarm_state_changed.call_args
        assert args[2] == fixed

class TestAlarmScenarios:
    def test_normal_arm_intrusion_and_disarm(self):
        mgr = AlarmStateManager()
        mgr.handle_event(make_event("ARM_BUTTON_PRESSED"))
        assert mgr.current_state_code == "ARMING_WAIT"
        mgr.handle_event(make_event("DOOR_STATE_CHANGED", {"state": "OPEN"}))
        assert mgr.current_state_code == "ARMED_COUNTDOWN"
        mgr.handle_event(make_event("MOTION_DETECTED"))
        assert mgr.current_state_code == "ALARM"
        mgr.handle_event(make_event("PIN_ATTEMPT", {"result": "SUCCESS"}))
        assert mgr.current_state_code == "DISARMED"

    def test_multiple_wrong_pins_keep_alarm_active(self):
        mgr = AlarmStateManager()
        mgr._state = AlarmTriggeredState()
        for _ in range(5):
            mgr.handle_event(make_event("PIN_ATTEMPT", {"result": "FAILURE"}))
        assert mgr.current_state_code == "ALARM"


