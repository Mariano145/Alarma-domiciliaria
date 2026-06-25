"""
End-to-end integration tests for the IoT Alarm Flask backend.

Uses Flask test client with an in-memory SQLite database and resets
application-level singletons between tests to guarantee independence.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

import app.services.dependencies as deps
from app import create_app
from app.extensions import db
from app.models.entities.event import Event
from app.services.alarm_state_manager import DisarmedState

# ─── SHARED HELPERS ─────────────────────────────────────────────────────────

def _post_event(
    client,
    event_type,
    payload=None,
    device_id="test-device",
    occurred_at=None,
):
    """Helper to POST a single event and return the parsed response."""
    body = {
        "type": event_type,
        "deviceId": device_id,
        "payload": payload or {},
    }
    if occurred_at is not None:
        body["occurredAt"] = occurred_at
    resp = client.post(
        "/api/v1/events",
        data=json.dumps(body),
        content_type="application/json",
    )
    return resp, resp.get_json()


# ─── PYTEST FIXTURES ─────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Create a Flask test client with an empty SQLite in-memory DB.

    Yields a ``FlaskClient`` instance.  Resets the global AlarmStateManager
    and LiveStateCacheObserver so that every test starts from a known DISARMED
    baseline.
    """
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()

        # Reset singletons to a known DISARMED baseline
        deps._alarm_state_manager._state = DisarmedState()
        deps._live_state_cache._state_code = "DISARMED"
        deps._live_state_cache._state_label = "Desarmada"
        deps._live_state_cache._updated_at = datetime.now(timezone.utc)
        deps._live_state_cache._last_event_id = None
        deps._live_state_cache._last_event_type = None

        yield app.test_client()

        # Clean-up
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def clean_events(client):
    """Truncate the ``events`` table before every test function.

    ``autouse=True`` guarantees this runs even when a test does not request
    the ``client`` fixture explicitly.
    """
    # Ensure we are inside the application context
    with client.application.app_context():
        db.session.query(Event).delete()
        db.session.commit()
        # Reset state again after truncation (belt-and-suspenders)
        deps._alarm_state_manager._state = DisarmedState()
        deps._live_state_cache._state_code = "DISARMED"
        deps._live_state_cache._state_label = "Desarmada"
        deps._live_state_cache._updated_at = datetime.now(timezone.utc)
        deps._live_state_cache._last_event_id = None
        deps._live_state_cache._last_event_type = None


# ─── TEST CLASSES ────────────────────────────────────────────────────────────

class TestEventIngestion:
    """Integration tests for POST /api/v1/events."""

    def test_post_door_state_changed_returns_201_with_event_id_and_received_at(
        self,
        client,
    ):
        resp, data = _post_event(
            client,
            "DOOR_STATE_CHANGED",
            {"state": "OPEN"},
        )
        assert resp.status_code == 201, "Expected 201 Created for valid event"
        assert "eventId" in data, "Response must contain eventId"
        assert "receivedAt" in data, "Response must contain receivedAt"
        assert isinstance(data["eventId"], str), "eventId must be a string"
        assert len(data["eventId"]) > 0, "eventId must not be empty"

    def test_event_is_persisted_in_database(self, client):
        resp, data = _post_event(
            client,
            "DOOR_STATE_CHANGED",
            {"state": "OPEN"},
            device_id="door-sensor-01",
        )
        event_id = data["eventId"]

        with client.application.app_context():
            persisted = db.session.get(Event, event_id)
        assert persisted is not None, "Event should be persisted in DB"
        assert persisted.type == "DOOR_STATE_CHANGED"
        assert persisted.device_id == "door-sensor-01"
        assert persisted.payload == {"state": "OPEN"}

    def test_alarm_state_manager_processes_door_state_changed(self, client):
        # Baseline
        resp = client.get("/api/v1/alarm/state")
        assert resp.get_json()["stateCode"] == "DISARMED"

        # In a real system DOOR_STATE_CHANGED in DISARMED does nothing,
        # but we can verify the state endpoint is still consistent.
        _post_event(client, "DOOR_STATE_CHANGED", {"state": "OPEN"})
        resp = client.get("/api/v1/alarm/state")
        assert resp.status_code == 200
        assert resp.get_json()["stateCode"] == "DISARMED"


class TestAlarmStateFlow:
    """End-to-end flow tests that exercise AlarmStateManager via HTTP."""

    def test_full_arm_timeout_motion_disarm_flow(self, client):
        # 1. Verify initial state
        resp = client.get("/api/v1/alarm/state")
        assert (
            resp.get_json()["stateCode"] == "DISARMED"
        ), "Initial state must be DISARMED"

        # 2. ARM_BUTTON_PRESSED → ARMING_WAIT
        _post_event(client, "ARM_BUTTON_PRESSED", {})
        resp = client.get("/api/v1/alarm/state")
        assert (
            resp.get_json()["stateCode"] == "ARMING_WAIT"
        ), "ARM_BUTTON_PRESSED should transition to ARMING_WAIT"

        # 3. ARMING_TIMEOUT → ARMED_COUNTDOWN
        _post_event(client, "ARMING_TIMEOUT", {})
        resp = client.get("/api/v1/alarm/state")
        assert (
            resp.get_json()["stateCode"] == "ARMED_COUNTDOWN"
        ), "ARMING_TIMEOUT should transition to ARMED_COUNTDOWN"

        # 4. MOTION_DETECTED in ARMED_COUNTDOWN → ALARM
        _post_event(client, "MOTION_DETECTED", {})
        resp = client.get("/api/v1/alarm/state")
        assert (
            resp.get_json()["stateCode"] == "ALARM"
        ), "MOTION_DETECTED in ARMED_COUNTDOWN should trigger ALARM"

        # 5. PIN_ATTEMPT (SUCCESS) → DISARMED
        _post_event(client, "PIN_ATTEMPT", {"result": "SUCCESS"})
        resp = client.get("/api/v1/alarm/state")
        assert (
            resp.get_json()["stateCode"] == "DISARMED"
        ), "Successful PIN should disarm the system"

    def test_door_open_in_arming_wait_transitions_to_armed_countdown(self, client):
        _post_event(client, "ARM_BUTTON_PRESSED", {})
        _post_event(client, "DOOR_STATE_CHANGED", {"state": "OPEN"})
        resp = client.get("/api/v1/alarm/state")
        assert resp.get_json()["stateCode"] == "ARMED_COUNTDOWN"

    def test_panic_button_triggers_alarm_from_any_state(self, client):
        _post_event(client, "PANIC_BUTTON_PRESSED", {})
        resp = client.get("/api/v1/alarm/state")
        assert resp.get_json()["stateCode"] == "ALARM"

    def test_wrong_pin_in_armed_countdown_triggers_alarm(self, client):
        _post_event(client, "ARM_BUTTON_PRESSED", {})
        _post_event(client, "ARMING_TIMEOUT", {})
        _post_event(client, "PIN_ATTEMPT", {"result": "FAIL"})
        resp = client.get("/api/v1/alarm/state")
        assert resp.get_json()["stateCode"] == "ALARM"

    def test_entry_timeout_in_armed_countdown_triggers_alarm(self, client):
        _post_event(client, "ARM_BUTTON_PRESSED", {})
        _post_event(client, "ARMING_TIMEOUT", {})
        _post_event(client, "ENTRY_TIMEOUT", {})
        resp = client.get("/api/v1/alarm/state")
        assert resp.get_json()["stateCode"] == "ALARM"

    def test_arm_button_in_armed_countdown_returns_to_disarmed(self, client):
        _post_event(client, "ARM_BUTTON_PRESSED", {})
        _post_event(client, "ARMING_TIMEOUT", {})
        _post_event(client, "ARM_BUTTON_PRESSED", {})
        resp = client.get("/api/v1/alarm/state")
        assert resp.get_json()["stateCode"] == "DISARMED"


class TestAlarmStateEndpoint:
    """Tests for GET /api/v1/alarm/state."""

    def test_returns_correct_structure(self, client):
        resp = client.get("/api/v1/alarm/state")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "stateCode" in data, "Response must contain stateCode"
        assert "stateLabel" in data, "Response must contain stateLabel"
        assert "updatedAt" in data, "Response must contain updatedAt"
        assert "lastEventId" in data, "Response must contain lastEventId"
        assert "lastEventType" in data, "Response must contain lastEventType"
        assert data["stateCode"] == "DISARMED"
        assert data["stateLabel"] == "Desarmada"

    def test_state_updates_after_each_event(self, client):
        resp = client.get("/api/v1/alarm/state")
        initial_updated_at = resp.get_json()["updatedAt"]

        _post_event(client, "ARM_BUTTON_PRESSED", {})
        resp = client.get("/api/v1/alarm/state")
        data = resp.get_json()
        assert data["stateCode"] == "ARMING_WAIT"
        assert data["lastEventType"] == "ARM_BUTTON_PRESSED"
        assert (
            data["updatedAt"] != initial_updated_at
        ), "updatedAt should change after state transition"


class TestEventsEndpoint:
    """Tests for GET /api/v1/events with filtering and pagination."""

    def _seed_events(self, client):
        """Insert a small predictable set of events for list tests.

        Events are inserted directly so that ``received_at`` can be controlled
        precisely; this makes time-range filtering deterministic.
        """
        from app.utils.ids import new_event_id
        now = datetime.now(timezone.utc)
        events = [
            Event(
                event_id=new_event_id(),
                type="DOOR_STATE_CHANGED",
                device_id="device-a",
                payload={"state": "OPEN"},
                received_at=now - timedelta(minutes=5),
            ),
            Event(
                event_id=new_event_id(),
                type="DOOR_STATE_CHANGED",
                device_id="device-a",
                payload={"state": "CLOSED"},
                received_at=now - timedelta(minutes=4),
            ),
            Event(
                event_id=new_event_id(),
                type="MOTION_DETECTED",
                device_id="device-b",
                payload={},
                received_at=now - timedelta(minutes=3),
            ),
            Event(
                event_id=new_event_id(),
                type="PIN_ATTEMPT",
                device_id="keypad-01",
                payload={"result": "FAIL"},
                received_at=now - timedelta(minutes=2),
            ),
            Event(
                event_id=new_event_id(),
                type="PIN_ATTEMPT",
                device_id="keypad-01",
                payload={"result": "SUCCESS"},
                received_at=now - timedelta(minutes=1),
            ),
        ]
        db.session.add_all(events)
        db.session.commit()

    def test_get_events_returns_paginated_structure(self, client):
        self._seed_events(client)
        resp = client.get("/api/v1/events?limit=2&offset=0")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "items" in data
        assert "limit" in data
        assert "offset" in data
        assert "total" in data
        assert len(data["items"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0
        assert data["total"] == 5

    def test_get_events_filter_by_type(self, client):
        self._seed_events(client)
        resp = client.get("/api/v1/events?type=DOOR_STATE_CHANGED")
        data = resp.get_json()
        assert all(item["type"] == "DOOR_STATE_CHANGED" for item in data["items"])
        assert data["total"] == 2

    def test_get_events_filter_by_device_id(self, client):
        self._seed_events(client)
        resp = client.get("/api/v1/events?deviceId=device-b")
        data = resp.get_json()
        # The endpoint does not include deviceId in the response schema,
        # but the filter must still work.
        assert data["total"] == 1
        assert data["items"][0]["type"] == "MOTION_DETECTED"

    def test_get_events_filter_by_time_range(self, client):
        from urllib.parse import quote
        self._seed_events(client)
        now = datetime.now(timezone.utc)
        # Use a 2-minute window so that only the 2 most recent events match.
        from_iso = quote((now - timedelta(minutes=2, seconds=30)).isoformat())
        to_iso = quote(now.isoformat())
        resp = client.get(f"/api/v1/events?from={from_iso}&to={to_iso}")
        data = resp.get_json()
        assert data["total"] == 2  # last 2 events (PIN_ATTEMPT FAIL and SUCCESS)

    def test_get_events_offset_pagination(self, client):
        self._seed_events(client)
        resp = client.get("/api/v1/events?limit=2&offset=2")
        data = resp.get_json()
        assert len(data["items"]) == 2
        assert data["offset"] == 2


class TestAnalyticsEndpoint:
    """Tests for GET /api/v1/analytics."""

    def test_returns_openapi_structure(self, client):
        resp = client.get("/api/v1/analytics")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "windowMinutes" in data, "Response must contain windowMinutes"
        assert "counts" in data, "Response must contain counts"
        assert "pinFailSuspicious" in data, "Response must contain pinFailSuspicious"
        assert "doorOpenAnomaly" in data, "Response must contain doorOpenAnomaly"
        assert "calculatedAt" in data, "Response must contain calculatedAt"

        counts = data["counts"]
        assert "doorOpens" in counts
        assert "doorStateChanges" in counts
        assert "pinFails" in counts
        assert "panicPresses" in counts
        assert "motionDetections" in counts

    def test_counts_reflect_persisted_events(self, client):
        now = datetime.now(timezone.utc)
        # Seed events
        _post_event(
            client, "DOOR_STATE_CHANGED", {"state": "OPEN"}, "door-01", now.isoformat()
        )
        _post_event(
            client,
            "DOOR_STATE_CHANGED",
            {"state": "CLOSED"},
            "door-01",
            now.isoformat(),
        )
        _post_event(
            client, "MOTION_DETECTED", {}, "motion-01", now.isoformat()
        )
        _post_event(
            client,
            "PIN_ATTEMPT",
            {"result": "FAIL"},
            "keypad-01",
            now.isoformat(),
        )
        _post_event(client, "PANIC_BUTTON_PRESSED", {}, "panic-01", now.isoformat())

        resp = client.get("/api/v1/analytics")
        data = resp.get_json()
        counts = data["counts"]
        assert counts["doorOpens"] == 1
        assert counts["doorStateChanges"] == 2
        assert counts["motionDetections"] == 1
        assert counts["pinFails"] == 1
        assert counts["panicPresses"] == 1

    def test_pin_fail_suspicious_detects_consecutive_failures(self, client):
        now = datetime.now(timezone.utc)
        for _ in range(3):
            _post_event(
                client,
                "PIN_ATTEMPT",
                {"result": "FAIL"},
                "keypad-01",
                now.isoformat(),
            )
        resp = client.get("/api/v1/analytics")
        data = resp.get_json()
        assert data["pinFailSuspicious"]["active"] is True

    def test_door_open_anomaly_detects_excessive_opens(self, client):
        now = datetime.now(timezone.utc)
        for _ in range(7):
            _post_event(
                client,
                "DOOR_STATE_CHANGED",
                {"state": "OPEN"},
                "door-01",
                now.isoformat(),
            )
        resp = client.get("/api/v1/analytics")
        data = resp.get_json()
        assert data["doorOpenAnomaly"]["active"] is True
        assert data["doorOpenAnomaly"]["threshold"] == 6
