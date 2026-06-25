"""
Data-access layer for persisted alarm events.

Wraps SQLAlchemy queries for inserting and listing events with the
filters required by ``GET /api/v1/events``.
"""

from datetime import datetime

from app.extensions import db
from app.models.entities.event import Event


class EventRepository:
    def add(self, event: Event) -> Event:
        db.session.add(event)
        db.session.commit()
        return event

    def list(
        self,
        limit: int = 50,
        offset: int = 0,
        type_: str | None = None,
        device_id: str | None = None,
        from_: datetime | None = None,
        to: datetime | None = None,
    ) -> tuple[list[Event], int]:
        query = Event.query

        if type_ is not None:
            query = query.filter(Event.type == type_)
        if device_id is not None:
            query = query.filter(Event.device_id == device_id)
        if from_ is not None:
            query = query.filter(Event.received_at >= from_)
        if to is not None:
            query = query.filter(Event.received_at <= to)

        total = query.count()
        items = (
            query.order_by(Event.received_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return items, total
