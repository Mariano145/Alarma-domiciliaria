from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

# Direct and clean imports thanks to your pythonpath configuration
from app.services.event_observer import (
    AnalyticsCacheInvalidatorObserver,
    EventStreamLoggerObserver,
)


# ─── FIXTURES (The standard way to share data in Pytest) ────────────────────
@pytest.fixture
def mock_event():
    """Create a mocked event with fixed data to use across tests."""
    event = MagicMock()
    event.type = "MOTION_DETECTED"
    event.device_id = "sensor-patagonia-01"
    event.payload = {"status": "alert"}
    event.received_at = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    return event


# ─── TESTS FOR EventStreamLoggerObserver ─────────────────────────────────────
class TestEventStreamLoggerObserver:
    def test_on_new_event_prints_correct_format(self, capsys, mock_event):
        """Verify that the logger prints all event details to the console."""
        observer = EventStreamLoggerObserver()

        # Trigger the action
        observer.on_new_event(mock_event)
        # Capture console output
        captured = capsys.readouterr().out

        # Validate that the format matches expectations
        assert "[EventStream]" in captured
        assert "MOTION_DETECTED" in captured
        assert "sensor-patagonia-01" in captured
        assert "alert" in captured


# ─── TESTS FOR AnalyticsCacheInvalidatorObserver ─────────────────────────────
class TestAnalyticsCacheInvalidatorObserver:

    def test_cache_is_invalid_on_init(self):
        """When the observer is created, the cache must start as invalid."""
        observer = AnalyticsCacheInvalidatorObserver()
        assert observer.cache_valid is False

    def test_mark_valid_updates_cache_status(self):
        """Validate that the mark_valid method changes the status to True."""
        observer = AnalyticsCacheInvalidatorObserver()
        observer.mark_valid()

        assert observer.cache_valid is True

    def test_on_new_event_invalidates_cache_and_prints(self, capsys, mock_event):
        """A new event must invalidate the cache (False) and log to the console."""
        observer = AnalyticsCacheInvalidatorObserver()
        observer.mark_valid()  # Force it to True first

        # An event arrives
        observer.on_new_event(mock_event)

        # 1. Cache should have changed to False
        assert observer.cache_valid is False

        # 2. Should have printed the corresponding warning/log
        captured = capsys.readouterr().out
        assert "[AnalyticsCache] Invalidated" in captured
        assert "MOTION_DETECTED" in captured


# ─── INTEGRATION TEST (Combined Behavior) ───────────────────────────
def test_multiple_observers_react_to_same_event(capsys, mock_event):
    """Test that both observers run in chain without interfering with each other."""
    logger = EventStreamLoggerObserver()
    cache = AnalyticsCacheInvalidatorObserver()
    cache.mark_valid()

    # Notify both with the same event
    logger.on_new_event(mock_event)
    cache.on_new_event(mock_event)

    # Final assertions
    captured = capsys.readouterr().out
    assert "[EventStream]" in captured
    assert "[AnalyticsCache]" in captured
    assert cache.cache_valid is False
