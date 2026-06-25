"""
HTTP controller for GET /api/v1/analytics.

Fetches all events from the repository, runs the AnalyticsService,
and returns the aggregated metrics dict.
"""

from __future__ import annotations

from flask import Blueprint, jsonify

from app.services.dependencies import get_analytics_service

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("")
def get_analytics():
    metrics = get_analytics_service().calculate_metrics_from_db()
    return jsonify(metrics), 200
