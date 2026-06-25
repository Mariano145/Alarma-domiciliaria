"""
HTTP controllers for event ingestion and history.

Delegates all business logic to EventService (injected via dependencies).
"""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.models.schemas.event_schemas import EventItemSchema, EventPageSchema
from app.services.dependencies import get_event_service

events_bp = Blueprint("events", __name__)

_page_schema = EventPageSchema()
_item_schema = EventItemSchema()


@events_bp.post("")
def ingest_event():
    json_body = request.get_json(silent=True)
    if json_body is None:
        return jsonify({"error": "Invalid JSON body."}), 400

    try:
        result = get_event_service().ingest(json_body)
    except ValidationError as exc:
        return jsonify({"error": "Validation failed.", "details": exc.messages}), 400

    return jsonify(result), 201


@events_bp.get("")
def list_events():
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"error": "limit and offset must be integers."}), 400

    if not (1 <= limit <= 200):
        return jsonify({"error": "limit must be between 1 and 200."}), 400
    if offset < 0:
        return jsonify({"error": "offset must be >= 0."}), 400

    type_ = request.args.get("type")
    device_id = request.args.get("deviceId")
    from_raw = request.args.get("from")
    to_raw = request.args.get("to")

    try:
        from_ = datetime.fromisoformat(from_raw) if from_raw else None
        to_ = datetime.fromisoformat(to_raw) if to_raw else None
    except ValueError:
        return jsonify({"error": "from/to must be ISO 8601 date-times."}), 400

    items, total = get_event_service().list_events(
        limit=limit,
        offset=offset,
        type_=type_,
        device_id=device_id,
        from_=from_,
        to=to_,
    )

    page = {
        "items": [
            {
                "event_id": e.event_id,
                "received_at": e.received_at,
                "type": e.type,
                "payload": e.payload,
            }
            for e in items
        ],
        "limit": limit,
        "offset": offset,
        "total": total,
    }
    return jsonify(_page_schema.dump(page)), 200
