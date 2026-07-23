"""
Background task to automatically clean up old events.

Prevents unbounded growth of the events table, especially useful for
public demos where data should not persist indefinitely.

Configuration via environment variables:
- EVENT_TTL_HOURS: Events older than this are deleted (default: 24)
- EVENT_CLEANUP_INTERVAL_MINUTES: How often to run cleanup (default: 60)
"""

from __future__ import annotations

import logging
import os
import threading
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

_cleanup_thread: threading.Thread | None = None
_stop_event = threading.Event()


def _cleanup_old_events(app) -> None:
    """Delete events older than EVENT_TTL_HOURS."""
    from app.extensions import db
    from app.models.entities.event import Event

    ttl_hours = int(os.getenv("EVENT_TTL_HOURS", "24"))
    cutoff = datetime.now(timezone.utc) - timedelta(hours=ttl_hours)

    with app.app_context():
        deleted = (
            db.session.query(Event)
            .filter(Event.received_at < cutoff)
            .delete(synchronize_session=False)
        )
        db.session.commit()
        if deleted > 0:
            logger.info("Event cleanup: deleted %d events older than %dh", deleted, ttl_hours)


def _run_cleanup_loop(app) -> None:
    """Background loop that runs cleanup periodically."""
    interval_minutes = int(os.getenv("EVENT_CLEANUP_INTERVAL_MINUTES", "60"))
    interval_seconds = interval_minutes * 60

    logger.info(
        "Event cleanup started: TTL=%dh, interval=%dm",
        int(os.getenv("EVENT_TTL_HOURS", "24")),
        interval_minutes,
    )

    while not _stop_event.is_set():
        _stop_event.wait(timeout=interval_seconds)
        if _stop_event.is_set():
            break
        try:
            _cleanup_old_events(app)
        except Exception:
            logger.exception("Event cleanup failed")


def start_cleanup_task(app) -> None:
    """Start the background cleanup thread. Call once from create_app()."""
    global _cleanup_thread

    if os.getenv("EVENT_CLEANUP_ENABLED", "true").lower() in ("false", "0", "no"):
        logger.info("Event cleanup disabled via EVENT_CLEANUP_ENABLED=false")
        return

    if _cleanup_thread is not None and _cleanup_thread.is_alive():
        return  # Already running

    _stop_event.clear()
    _cleanup_thread = threading.Thread(
        target=_run_cleanup_loop,
        args=(app,),
        daemon=True,
        name="event-cleanup",
    )
    _cleanup_thread.start()


def stop_cleanup_task() -> None:
    """Signal the cleanup thread to stop."""
    _stop_event.set()
