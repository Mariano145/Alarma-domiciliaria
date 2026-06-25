"""
AnalyticsService — Strategy pattern for alarm event analysis.

Implements three algorithms over persisted Event data:
- WindowedCountsAlgorithm    — counts events by type in the last 10 minutes
- PinFailHysteresisAlgorithm — detects 3+ consecutive PIN failures
- DoorOpenAnomalyAlgorithm   — detects >6 door opens in the last 10 minutes
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

from app.models.entities.event import Event
from app.repositories.event_repository import EventRepository


class AnalyticsAlgorithm(ABC):
    """Strategy interface — every algorithm must implement process()."""

    @abstractmethod
    def process(self, events: list[Event]) -> dict:
        """Process a list of events and return a metrics dict."""
        ...


class WindowedCountsAlgorithm(AnalyticsAlgorithm):
    """
    Counts events by type within the last 10 minutes relative
    to the most recent event timestamp.
    """

    WINDOW_MINUTES = 10

    def process(self, events: list[Event]) -> dict:
        counts = {
            "doorOpens": 0,
            "doorStateChanges": 0,
            "pinFails": 0,
            "panicPresses": 0,
            "motionDetections": 0,
        }

        if not events:
            return counts

        most_recent = max(e.received_at for e in events)
        cutoff = most_recent - timedelta(minutes=self.WINDOW_MINUTES)
        windowed = [e for e in events if e.received_at >= cutoff]

        for event in windowed:
            if event.type == "DOOR_STATE_CHANGED":
                counts["doorStateChanges"] += 1
                if event.payload.get("state") == "OPEN":
                    counts["doorOpens"] += 1
            elif event.type == "PIN_ATTEMPT" and event.payload.get("result") == "FAIL":
                counts["pinFails"] += 1
            elif event.type == "PANIC_BUTTON_PRESSED":
                counts["panicPresses"] += 1
            elif event.type == "MOTION_DETECTED":
                counts["motionDetections"] += 1

        return counts


class PinFailHysteresisAlgorithm(AnalyticsAlgorithm):
    """
    Detects suspicious PIN activity: 3 or more consecutive
    PIN_ATTEMPT failures without a successful attempt in between.
    """

    ACTIVATE_AT = 3
    DEACTIVATE_AT = 1

    def process(self, events: list[Event]) -> dict:
        alert_active = False

        if not events:
            return {
                "active": alert_active,
                "activateAt": self.ACTIVATE_AT,
                "deactivateAt": self.DEACTIVATE_AT,
            }

        sorted_events = sorted(events, key=lambda e: e.received_at)
        consecutive_fails = 0

        for event in sorted_events:
            if event.type != "PIN_ATTEMPT":
                continue
            result = event.payload.get("result")
            if result == "FAIL":
                consecutive_fails += 1
                if consecutive_fails >= self.ACTIVATE_AT:
                    alert_active = True
            elif result == "SUCCESS":
                consecutive_fails = 0
                alert_active = False

        return {
            "active": alert_active,
            "activateAt": self.ACTIVATE_AT,
            "deactivateAt": self.DEACTIVATE_AT,
        }


class DoorOpenAnomalyAlgorithm(AnalyticsAlgorithm):
    """
    Detects anomalous door activity: more than 6 DOOR_STATE_CHANGED
    OPEN events in the last 10 minutes.
    """

    WINDOW_MINUTES = 10
    THRESHOLD = 6

    def process(self, events: list[Event]) -> dict:
        alert_active = False

        if not events:
            return {
                "active": alert_active,
                "threshold": self.THRESHOLD,
            }

        most_recent = max(e.received_at for e in events)
        cutoff = most_recent - timedelta(minutes=self.WINDOW_MINUTES)

        door_opens = [
            e for e in events
            if e.received_at >= cutoff
            and e.type == "DOOR_STATE_CHANGED"
            and e.payload.get("state") == "OPEN"
        ]

        alert_active = len(door_opens) > self.THRESHOLD

        return {
            "active": alert_active,
            "threshold": self.THRESHOLD,
        }


class AnalyticsService:
    """
    Orchestrates analytics algorithms (Strategy pattern).
    Each algorithm is independent and returns its own metrics dict.
    """

    WINDOW_MINUTES = 10

    def __init__(
        self,
        algorithms: list[AnalyticsAlgorithm],
        event_repository: EventRepository | None = None,
    ) -> None:
        self._algorithms = algorithms
        self._repository = event_repository

    def calculate_metrics(self, events: list[Event]) -> dict:
        """Run all algorithms over a provided event list."""
        counts = {}
        pin_fail = {}
        door_anomaly = {}

        for algorithm in self._algorithms:
            if isinstance(algorithm, WindowedCountsAlgorithm):
                counts = algorithm.process(events)
            elif isinstance(algorithm, PinFailHysteresisAlgorithm):
                pin_fail = algorithm.process(events)
            elif isinstance(algorithm, DoorOpenAnomalyAlgorithm):
                door_anomaly = algorithm.process(events)

        return {
            "windowMinutes": self.WINDOW_MINUTES,
            "counts": counts,
            "pinFailSuspicious": pin_fail,
            "doorOpenAnomaly": door_anomaly,
            "calculatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def calculate_metrics_from_db(self) -> dict:
        """Fetch all events from DB and run all algorithms."""
        if self._repository is None:
            return {}
        events, _ = self._repository.list(limit=1000, offset=0)
        return self.calculate_metrics(events)
