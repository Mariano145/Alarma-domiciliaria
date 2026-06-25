"""
Integration tests simulating real firmware (ESP32) event submissions.

These tests verify that the exact JSON format sent by the firmware
(via networkClient.cpp postEvent) is correctly processed by the backend.
"""

from datetime import datetime, timezone

import pytest

import app.services.dependencies as deps
from app import create_app
from app.extensions import db
from app.services.alarm_state_manager import DisarmedState


@pytest.fixture
def client():
    """Create Flask test client with in-memory SQLite database."""
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


class TestFirmwareEventSubmission:
    """Test events sent from ESP32 firmware to backend."""

    def test_door_state_changed_from_firmware(self, client):
        """
        Firmware sends:
        {
            "type": "DOOR_STATE_CHANGED",
            "deviceId": "esp32-001",
            "payload": {"state": "OPEN"}
        }
        """
        response = client.post(
            "/api/v1/events",
            json={
                "type": "DOOR_STATE_CHANGED",
                "deviceId": "esp32-001",
                "payload": {"state": "OPEN"},
            },
        )
        assert response.status_code == 201
        data = response.get_json()
        assert "eventId" in data
        assert "receivedAt" in data

    def test_arm_button_pressed_from_firmware(self, client):
        """
        Firmware sends:
        {
            "type": "ARM_BUTTON_PRESSED",
            "deviceId": "esp32-001",
            "payload": {}
        }
        """
        response = client.post(
            "/api/v1/events",
            json={
                "type": "ARM_BUTTON_PRESSED",
                "deviceId": "esp32-001",
                "payload": {},
            },
        )
        assert response.status_code == 201
        data = response.get_json()
        assert "eventId" in data

    def test_panic_button_pressed_from_firmware(self, client):
        """
        Firmware sends:
        {
            "type": "PANIC_BUTTON_PRESSED",
            "deviceId": "esp32-001",
            "payload": {}
        }
        """
        response = client.post(
            "/api/v1/events",
            json={
                "type": "PANIC_BUTTON_PRESSED",
                "deviceId": "esp32-001",
                "payload": {},
            },
        )
        assert response.status_code == 201

    def test_pin_attempt_success_from_firmware(self, client):
        """
        Firmware sends:
        {
            "type": "PIN_ATTEMPT",
            "deviceId": "esp32-001",
            "payload": {"result": "SUCCESS"}
        }
        """
        response = client.post(
            "/api/v1/events",
            json={
                "type": "PIN_ATTEMPT",
                "deviceId": "esp32-001",
                "payload": {"result": "SUCCESS"},
            },
        )
        assert response.status_code == 201

    def test_pin_attempt_fail_from_firmware(self, client):
        """
        Firmware sends:
        {
            "type": "PIN_ATTEMPT",
            "deviceId": "esp32-001",
            "payload": {"result": "FAIL"}
        }
        """
        response = client.post(
            "/api/v1/events",
            json={
                "type": "PIN_ATTEMPT",
                "deviceId": "esp32-001",
                "payload": {"result": "FAIL"},
            },
        )
        assert response.status_code == 201

    def test_motion_detected_from_firmware(self, client):
        """
        Firmware sends:
        {
            "type": "MOTION_DETECTED",
            "deviceId": "esp32-001",
            "payload": {}
        }
        """
        response = client.post(
            "/api/v1/events",
            json={
                "type": "MOTION_DETECTED",
                "deviceId": "esp32-001",
                "payload": {},
            },
        )
        assert response.status_code == 201

    def test_arming_timeout_from_firmware(self, client):
        """
        Firmware sends:
        {
            "type": "ARMING_TIMEOUT",
            "deviceId": "esp32-001",
            "payload": {}
        }
        """
        response = client.post(
            "/api/v1/events",
            json={
                "type": "ARMING_TIMEOUT",
                "deviceId": "esp32-001",
                "payload": {},
            },
        )
        assert response.status_code == 201

    def test_entry_timeout_from_firmware(self, client):
        """
        Firmware sends:
        {
            "type": "ENTRY_TIMEOUT",
            "deviceId": "esp32-001",
            "payload": {}
        }
        """
        response = client.post(
            "/api/v1/events",
            json={
                "type": "ENTRY_TIMEOUT",
                "deviceId": "esp32-001",
                "payload": {},
            },
        )
        assert response.status_code == 201

    def test_full_alarm_flow_from_firmware(self, client):
        """
        Simulate complete alarm flow as it would happen from real firmware:
        1. ARM_BUTTON_PRESSED (user presses arm button)
        2. DOOR_STATE_CHANGED OPEN (door opens during arming)
        3. MOTION_DETECTED (motion detected)
        4. PIN_ATTEMPT FAIL (wrong PIN)
        5. PIN_ATTEMPT SUCCESS (correct PIN to disarm)
        """
        events = [
            {"type": "ARM_BUTTON_PRESSED", "deviceId": "esp32-001", "payload": {}},
            {
                "type": "DOOR_STATE_CHANGED",
                "deviceId": "esp32-001",
                "payload": {"state": "OPEN"},
            },
            {"type": "MOTION_DETECTED", "deviceId": "esp32-001", "payload": {}},
            {
                "type": "PIN_ATTEMPT",
                "deviceId": "esp32-001",
                "payload": {"result": "FAIL"},
            },
            {
                "type": "PIN_ATTEMPT",
                "deviceId": "esp32-001",
                "payload": {"result": "SUCCESS"},
            },
        ]

        for event in events:
            response = client.post("/api/v1/events", json=event)
            assert response.status_code == 201, f"Failed for event: {event['type']}"

        # Verify all events were persisted
        response = client.get("/api/v1/events?deviceId=esp32-001")
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] >= 5
