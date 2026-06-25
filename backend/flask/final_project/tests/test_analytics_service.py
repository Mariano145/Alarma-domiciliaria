from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from app.services.analytics_service import (
    AnalyticsService,
    DoorOpenAnomalyAlgorithm,
    PinFailHysteresisAlgorithm,
    WindowedCountsAlgorithm,
)


# ─── AUX CONFIG FUNCTIONS ──────────────────────────────────
def make_event(event_type: str, received_at: datetime, payload: dict | None = None) -> MagicMock:  # noqa: E501
    """Create a mock Event object with specific data for analytics testing."""
    evt = MagicMock()
    evt.type = event_type
    evt.received_at = received_at
    evt.payload = payload or {}
    return evt


# ─── WINDOWEDCOUNTSALGORITHM TESTS ───────────────────────────────────
class TestWindowedCountsAlgorithm:
    def test_process_with_empty_events_returns_empty_dict(self):
        algorithm = WindowedCountsAlgorithm()
        result = algorithm.process([])
        assert result == {
            "doorOpens": 0,
            "doorStateChanges": 0,
            "pinFails": 0,
            "panicPresses": 0,
            "motionDetections": 0,
        }

    def test_process_aggregates_counts_correctly_by_type(self):
        algorithm = WindowedCountsAlgorithm()
        now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        events = [
            make_event("MOTION_DETECTED", now - timedelta(minutes=2)),
            make_event("MOTION_DETECTED", now - timedelta(minutes=1)),
            make_event("DOOR_STATE_CHANGED", now),
        ]

        result = algorithm.process(events)
        assert result == {
            "doorOpens": 0,
            "doorStateChanges": 1,
            "pinFails": 0,
            "panicPresses": 0,
            "motionDetections": 2,
        }

    def test_process_excludes_events_older_than_ten_minutes_from_most_recent(self):
        algorithm = WindowedCountsAlgorithm()
        now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        events = [
            make_event("MOTION_DETECTED", now - timedelta(minutes=15)),  # Out of window
            make_event("MOTION_DETECTED", now - timedelta(minutes=10)),  # Window limit
            make_event("PANIC_BUTTON_PRESSED", now),                     # Most recent
        ]

        result = algorithm.process(events)
        assert result == {
            "doorOpens": 0,
            "doorStateChanges": 0,
            "pinFails": 0,
            "panicPresses": 1,
            "motionDetections": 1,
        }


# ─── PINFAILHYSTERESISALGORITHM TESTS ─────────────────────────────────
class TestPinFailHysteresisAlgorithm:
    def test_process_with_empty_events_returns_false(self):
        algorithm = PinFailHysteresisAlgorithm()
        result = algorithm.process([])
        assert result == {"active": False, "activateAt": 3, "deactivateAt": 1}

    def test_less_than_three_consecutive_fails_does_not_trigger_alert(self):
        algorithm = PinFailHysteresisAlgorithm()
        now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        events = [
            make_event("PIN_ATTEMPT", now - timedelta(minutes=2), {"result": "FAIL"}),
            make_event("PIN_ATTEMPT", now - timedelta(minutes=1), {"result": "FAIL"}),
        ]

        result = algorithm.process(events)
        assert result == {"active": False, "activateAt": 3, "deactivateAt": 1}

    def test_three_consecutive_fails_triggers_alert(self):
        algorithm = PinFailHysteresisAlgorithm()
        now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        events = [
            make_event("PIN_ATTEMPT", now - timedelta(minutes=3), {"result": "FAIL"}),
            make_event("PIN_ATTEMPT", now - timedelta(minutes=2), {"result": "FAIL"}),
            make_event("PIN_ATTEMPT", now - timedelta(minutes=1), {"result": "FAIL"}),
        ]

        result = algorithm.process(events)
        assert result == {"active": True, "activateAt": 3, "deactivateAt": 1}

    def test_success_attempt_resets_consecutive_fails_counter_and_alert(self):
        algorithm = PinFailHysteresisAlgorithm()
        now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        events = [
            make_event("PIN_ATTEMPT", now - timedelta(minutes=4), {"result": "FAIL"}),
            make_event("PIN_ATTEMPT", now - timedelta(minutes=3), {"result": "FAIL"}),
            make_event("PIN_ATTEMPT", now - timedelta(minutes=2), {"result": "SUCCESS"}),  # noqa: E501
            make_event("PIN_ATTEMPT", now - timedelta(minutes=1), {"result": "FAIL"}),
        ]

        result = algorithm.process(events)
        assert result == {"active": False, "activateAt": 3, "deactivateAt": 1}

    def test_success_after_alert_active_deactivates_alert(self):
        algorithm = PinFailHysteresisAlgorithm()
        now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        events = [
            make_event("PIN_ATTEMPT", now - timedelta(minutes=4), {"result": "FAIL"}),
            make_event("PIN_ATTEMPT", now - timedelta(minutes=3), {"result": "FAIL"}),
            make_event("PIN_ATTEMPT", now - timedelta(minutes=2), {"result": "FAIL"}),
            make_event("PIN_ATTEMPT", now - timedelta(minutes=1), {"result": "SUCCESS"})
        ]

        result = algorithm.process(events)
        assert result == {"active": False, "activateAt": 3, "deactivateAt": 1}

    def test_other_event_types_are_ignored_and_do_not_break_consecutive_count(self):
        algorithm = PinFailHysteresisAlgorithm()
        now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        events = [
            make_event("PIN_ATTEMPT", now - timedelta(minutes=4), {"result": "FAIL"}),
            make_event("MOTION_DETECTED", now - timedelta(minutes=3)),
            make_event("PIN_ATTEMPT", now - timedelta(minutes=2), {"result": "FAIL"}),
            make_event("PIN_ATTEMPT", now - timedelta(minutes=1), {"result": "FAIL"}),
        ]

        result = algorithm.process(events)
        assert result == {"active": True, "activateAt": 3, "deactivateAt": 1}

    def test_events_are_sorted_by_timestamp_before_processing(self):
        algorithm = PinFailHysteresisAlgorithm()
        now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        events = [
            make_event("PIN_ATTEMPT", now - timedelta(minutes=1), {"result": "FAIL"}),
            make_event("PIN_ATTEMPT", now - timedelta(minutes=3), {"result": "FAIL"}),
            make_event("PIN_ATTEMPT", now - timedelta(minutes=2), {"result": "FAIL"}),
        ]

        result = algorithm.process(events)
        assert result == {"active": True, "activateAt": 3, "deactivateAt": 1}


# ─── DOOROPENANOMALYALGORITHM TESTS ───────────────────────────────────
class TestDoorOpenAnomalyAlgorithm:
    def test_process_with_empty_events_returns_false(self):
        algorithm = DoorOpenAnomalyAlgorithm()
        result = algorithm.process([])
        assert result == {"active": False, "threshold": 6}

    def test_door_opens_equal_to_threshold_does_not_trigger_anomaly(self):
        algorithm = DoorOpenAnomalyAlgorithm()
        now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        events = [
            make_event("DOOR_STATE_CHANGED",
                       now - timedelta(minutes=i), {"state": "OPEN"})
            for i in range(6)
        ]

        result = algorithm.process(events)
        assert result == {"active": False, "threshold": 6}

    def test_door_opens_greater_than_threshold_triggers_anomaly(self):
        algorithm = DoorOpenAnomalyAlgorithm()
        now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        # 7 OPEN events
        events = [
            make_event("DOOR_STATE_CHANGED",
                       now - timedelta(seconds=i * 10), {"state": "OPEN"})
            for i in range(7)
        ]

        result = algorithm.process(events)
        assert result == {"active": True, "threshold": 6}

    def test_ignores_door_closed_events(self):
        algorithm = DoorOpenAnomalyAlgorithm()
        now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        events = [
            make_event("DOOR_STATE_CHANGED",
                       now - timedelta(minutes=1), {"state": "OPEN"}),
            make_event("DOOR_STATE_CHANGED",
                       now - timedelta(minutes=2), {"state": "CLOSED"}),
            make_event("DOOR_STATE_CHANGED",
                       now - timedelta(minutes=3), {"state": "CLOSED"}),
        ]

        result = algorithm.process(events)
        assert result == {"active": False, "threshold": 6}

    def test_excludes_door_open_events_outside_ten_minute_window(self):
        algorithm = DoorOpenAnomalyAlgorithm()
        now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        # 2 old events (should be excluded by the 10-minute window)
        old_events = [
            make_event("DOOR_STATE_CHANGED",
                       now - timedelta(minutes=12), {"state": "OPEN"}),
            make_event("DOOR_STATE_CHANGED",
                       now - timedelta(minutes=11), {"state": "OPEN"}),
        ]
        # 5 new events (inside window, but not enough on
        # their own to trigger anomaly threshold > 6)
        new_events = [
            make_event("DOOR_STATE_CHANGED",
                       now - timedelta(minutes=1), {"state": "OPEN"})
            for _ in range(5)
        ]

        # Total = 7 events. If window filtering fails,
        # it will count 7 and return True (bug).
        # If window filtering works, it will only count
        # 5 and return False (expected behavior).
        result = algorithm.process(old_events + new_events)
        assert result == {"active": False, "threshold": 6}


# ─── ANALYTICSSERVICE TESTS ───────────────────────────
class TestAnalyticsServiceInit:
    def test_initializes_with_algorithms_and_repository(self):
        mock_algo = MagicMock(spec=WindowedCountsAlgorithm)
        mock_repo = MagicMock()
        service = AnalyticsService(algorithms=[mock_algo], event_repository=mock_repo)

        assert service._algorithms == [mock_algo]
        assert service._repository == mock_repo

    def test_repository_defaults_to_none(self):
        mock_algo = MagicMock(spec=WindowedCountsAlgorithm)
        service = AnalyticsService(algorithms=[mock_algo])

        assert service._repository is None


class TestAnalyticsServiceCalculateMetrics:
    def test_executes_all_configured_algorithms_and_merges_results(self):
        mock_algo_1 = MagicMock(spec=WindowedCountsAlgorithm)
        mock_algo_1.process.return_value = {
            "doorOpens": 1, "doorStateChanges": 2, "pinFails": 0,
            "panicPresses": 0, "motionDetections": 3
        }
        mock_algo_2 = MagicMock(spec=PinFailHysteresisAlgorithm)
        mock_algo_2.process.return_value = {
            "active": True, "activateAt": 3, "deactivateAt": 1
        }
        mock_algo_3 = MagicMock(spec=DoorOpenAnomalyAlgorithm)
        mock_algo_3.process.return_value = {"active": False, "threshold": 6}

        service = AnalyticsService(algorithms=[mock_algo_1, mock_algo_2, mock_algo_3])
        dummy_events = [MagicMock()]

        result = service.calculate_metrics(dummy_events)

        mock_algo_1.process.assert_called_once_with(dummy_events)
        mock_algo_2.process.assert_called_once_with(dummy_events)
        mock_algo_3.process.assert_called_once_with(dummy_events)
        assert result["windowMinutes"] == 10
        assert result["counts"] == {
            "doorOpens": 1, "doorStateChanges": 2, "pinFails": 0,
            "panicPresses": 0, "motionDetections": 3
        }
        assert result["pinFailSuspicious"] == {
            "active": True, "activateAt": 3, "deactivateAt": 1
        }
        assert result["doorOpenAnomaly"] == {"active": False, "threshold": 6}
        assert "calculatedAt" in result


class TestAnalyticsServiceCalculateMetricsFromDb:
    def test_returns_empty_dict_if_repository_is_none(self):
        service = AnalyticsService(algorithms=[])
        result = service.calculate_metrics_from_db()
        assert result == {}

    def test_fetches_events_from_db_repository_and_calculates_metrics(self):
        mock_repo = MagicMock()
        mock_event_1 = MagicMock()
        mock_event_2 = MagicMock()
        mock_repo.list.return_value = ([mock_event_1, mock_event_2], 2)

        mock_algo = MagicMock(spec=WindowedCountsAlgorithm)
        mock_algo.process.return_value = {
            "doorOpens": 0, "doorStateChanges": 0, "pinFails": 0,
            "panicPresses": 0, "motionDetections": 0
        }

        service = AnalyticsService(algorithms=[mock_algo], event_repository=mock_repo)

        result = service.calculate_metrics_from_db()

        mock_repo.list.assert_called_once_with(limit=1000, offset=0)
        mock_algo.process.assert_called_once_with([mock_event_1, mock_event_2])
        assert result["windowMinutes"] == 10
        assert result["counts"] == {
            "doorOpens": 0, "doorStateChanges": 0, "pinFails": 0,
            "panicPresses": 0, "motionDetections": 0
        }
        assert "calculatedAt" in result
