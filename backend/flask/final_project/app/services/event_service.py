"""
EventService — orchestrates event ingestion (business logic layer).

Follows the same pattern as SensorsService:
- Validates input via Marshmallow schema.
- Persists via EventRepository.
- Delegates state transitions to AlarmStateManager.
- Notifies EventObservers (Observer Pattern #2).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.models.entities.event import Event
from app.models.schemas.event_schemas import (
    EventIngestResponseSchema,
    EventIngestSchema,
)
from app.repositories.event_repository import EventRepository
from app.services.alarm_state_manager import AlarmStateManager
from app.services.event_observer import EventObserver
from app.utils.ids import new_event_id


class EventService:
    """Orchestrates event ingestion, persistence, state transitions,
    and observer notification."""

    def __init__(
        self,
        event_repository: EventRepository,
        alarm_state_manager: AlarmStateManager,
    ) -> None:
        self._repository = event_repository
        self._alarm_state_manager = alarm_state_manager
        self._observers: list[EventObserver] = []
        self._ingest_schema = EventIngestSchema()
        self._response_schema = EventIngestResponseSchema()

    # ── Observer management ───────────────────────────────────────────────────

    def attach(self, observer: EventObserver) -> None:
        self._observers.append(observer)

    def detach(self, observer: EventObserver) -> None:
        self._observers.remove(observer)

    def notify_observers(self, event: Event) -> None:
        for observer in self._observers:
            observer.on_new_event(event)

    # ── Ingestion ─────────────────────────────────────────────────────────────

    def ingest(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate, persist, handle state transition, notify observers.
        Returns a serialized EventIngestResponse dict.
        Raises marshmallow.ValidationError on invalid input.
        """
        data = self._ingest_schema.load(raw_data)

        event = Event(
            event_id=new_event_id(),
            type=data["type"],
            device_id=data["device_id"],
            payload=data["payload"],
            occurred_at=data.get("occurred_at"),
            received_at=datetime.now(timezone.utc),
        )

        self._repository.add(event)
        self._alarm_state_manager.handle_event(event)
        self.notify_observers(event)

        return self._response_schema.dump(
            {"event_id": event.event_id, "received_at": event.received_at}
        )

    def list_events(
        self,
        limit: int = 50,
        offset: int = 0,
        type_: str | None = None,
        device_id: str | None = None,
        from_: datetime | None = None,
        to: datetime | None = None,
    ) -> tuple[list[Event], int]:
        return self._repository.list(
            limit=limit,
            offset=offset,
            type_=type_,
            device_id=device_id,
            from_=from_,
            to=to,
        )
