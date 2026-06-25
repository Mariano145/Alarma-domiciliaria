"""
Shared service instances (application-level singletons).

All controllers import from here to share the same AlarmStateManager,
LiveStateCacheObserver, EventService, and AnalyticsService instances
across requests.
"""

from __future__ import annotations

from app.repositories.event_repository import EventRepository
from app.services.alarm_state_manager import AlarmStateManager
from app.services.alarm_state_observer import (
    LiveStateCacheObserver,
    StateTransitionLoggerObserver,
)
from app.services.analytics_service import (
    AnalyticsService,
    DoorOpenAnomalyAlgorithm,
    PinFailHysteresisAlgorithm,
    WindowedCountsAlgorithm,
)
from app.services.event_observer import (
    AnalyticsCacheInvalidatorObserver,
    EventStreamLoggerObserver,
)
from app.services.event_service import EventService

# ── Alarm state observers ─────────────────────────────────────────────────────
_live_state_cache = LiveStateCacheObserver()
_state_transition_logger = StateTransitionLoggerObserver()

# ── AlarmStateManager (with observers attached) ───────────────────────────────
_alarm_state_manager = AlarmStateManager()
_alarm_state_manager.attach(_live_state_cache)
_alarm_state_manager.attach(_state_transition_logger)

# ── Event observers ───────────────────────────────────────────────────────────
_analytics_cache_invalidator = AnalyticsCacheInvalidatorObserver()
_event_stream_logger = EventStreamLoggerObserver()

# ── EventService (with observers attached) ────────────────────────────────────
_event_repository = EventRepository()

_event_service = EventService(
    event_repository=_event_repository,
    alarm_state_manager=_alarm_state_manager,
)
_event_service.attach(_analytics_cache_invalidator)
_event_service.attach(_event_stream_logger)

# ── AnalyticsService (Strategy pattern) ──────────────────────────────────────
_analytics_service = AnalyticsService(
    event_repository=_event_repository,
    algorithms=[
        WindowedCountsAlgorithm(),
        PinFailHysteresisAlgorithm(),
        DoorOpenAnomalyAlgorithm(),
    ]
)


# ── Accessors ─────────────────────────────────────────────────────────────────

def get_event_service() -> EventService:
    return _event_service


def get_live_state_cache() -> LiveStateCacheObserver:
    return _live_state_cache


def get_analytics_cache_invalidator() -> AnalyticsCacheInvalidatorObserver:
    return _analytics_cache_invalidator


def get_analytics_service() -> AnalyticsService:
    return _analytics_service
