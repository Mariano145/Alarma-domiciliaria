"""
Observer interface for new event ingestion (Observer Pattern #2).

Any component that needs to react when a new event arrives must implement
this interface and register itself with ``EventService``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.entities.event import Event


class EventObserver(ABC):
    """Abstract base for components observing new ingested events."""

    @abstractmethod
    def on_new_event(self, event: Event) -> None:
        """Called by EventService after a new event is persisted."""
        ...


class EventStreamLoggerObserver(EventObserver):
    """Logs every ingested event to the console for debugging/monitoring."""

    def on_new_event(self, event: Event) -> None:
        print(
            f"[EventStream] {event.received_at.isoformat()} "
            f"type={event.type} device={event.device_id} "
            f"payload={event.payload}"
        )


class AnalyticsCacheInvalidatorObserver(EventObserver):
    """Marks the analytics cache as stale when a new event arrives."""

    def __init__(self) -> None:
        self._cache_valid = False

    def on_new_event(self, event: Event) -> None:
        self._cache_valid = False
        print(f"[AnalyticsCache] Invalidated by event type={event.type}")

    @property
    def cache_valid(self) -> bool:
        return self._cache_valid

    def mark_valid(self) -> None:
        self._cache_valid = True
