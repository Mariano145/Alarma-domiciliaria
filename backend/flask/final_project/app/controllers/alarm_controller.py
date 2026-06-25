"""
HTTP controller for GET /api/v1/alarm/state.

Returns the current alarm state from the LiveStateCacheObserver.
"""

from __future__ import annotations

from flask import Blueprint, jsonify

from app.services.dependencies import get_live_state_cache

alarm_bp = Blueprint("alarm", __name__)


@alarm_bp.get("/state")
def get_alarm_state():
    return jsonify(get_live_state_cache().get_state()), 200
