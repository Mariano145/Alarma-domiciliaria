"""
Marshmallow schemas for POST/GET /api/v1/events.

``EventIngestSchema`` validates the top-level envelope and delegates
payload validation to a per-``type`` schema, matching the ``oneOf``
polymorphism defined in the OpenAPI contract.
"""

from marshmallow import Schema, ValidationError, fields, validates_schema

EVENT_TYPES = (
    "DOOR_STATE_CHANGED",
    "ARM_BUTTON_PRESSED",
    "PANIC_BUTTON_PRESSED",
    "PIN_ATTEMPT",
    "MOTION_DETECTED",
    "ARMING_TIMEOUT",
    "ENTRY_TIMEOUT",
)


class DoorStateChangedPayloadSchema(Schema):
    class Meta:
        unknown = "raise"

    state = fields.String(required=True, validate=lambda v: v in ("OPEN", "CLOSED"))


class ArmButtonPressedPayloadSchema(Schema):
    class Meta:
        unknown = "raise"


class PanicButtonPressedPayloadSchema(Schema):
    class Meta:
        unknown = "raise"


class PinAttemptPayloadSchema(Schema):
    class Meta:
        unknown = "raise"

    result = fields.String(required=True, validate=lambda v: v in ("SUCCESS", "FAIL"))


class MotionDetectedPayloadSchema(Schema):
    class Meta:
        unknown = "raise"


class ArmingTimeoutPayloadSchema(Schema):
    class Meta:
        unknown = "raise"


class EntryTimeoutPayloadSchema(Schema):
    class Meta:
        unknown = "raise"


PAYLOAD_SCHEMAS: dict[str, Schema] = {
    "DOOR_STATE_CHANGED":   DoorStateChangedPayloadSchema(),
    "ARM_BUTTON_PRESSED":   ArmButtonPressedPayloadSchema(),
    "PANIC_BUTTON_PRESSED": PanicButtonPressedPayloadSchema(),
    "PIN_ATTEMPT":          PinAttemptPayloadSchema(),
    "MOTION_DETECTED":      MotionDetectedPayloadSchema(),
    "ARMING_TIMEOUT":       ArmingTimeoutPayloadSchema(),
    "ENTRY_TIMEOUT":        EntryTimeoutPayloadSchema(),
}


class EventIngestSchema(Schema):
    class Meta:
        unknown = "raise"

    type = fields.String(required=True, validate=lambda v: v in EVENT_TYPES)
    device_id = fields.String(
        data_key="deviceId", required=True, validate=lambda v: len(v) >= 1
    )
    occurred_at = fields.DateTime(
        data_key="occurredAt", required=False, allow_none=True
    )
    payload = fields.Dict(required=True)

    @validates_schema
    def validate_payload_shape(self, data, **kwargs):
        event_type = data.get("type")
        payload = data.get("payload")
        schema = PAYLOAD_SCHEMAS.get(event_type)

        if schema is None:
            raise ValidationError({"type": ["Unsupported event type."]})

        errors = schema.validate(payload if payload is not None else {})
        if errors:
            raise ValidationError({"payload": errors})


class EventIngestResponseSchema(Schema):
    event_id = fields.String(data_key="eventId", required=True)
    received_at = fields.DateTime(data_key="receivedAt", required=True)


class EventItemSchema(Schema):
    event_id = fields.String(data_key="eventId", required=True)
    received_at = fields.DateTime(data_key="receivedAt", required=True)
    type = fields.String(required=True)
    payload = fields.Dict(required=True)


class EventPageSchema(Schema):
    items = fields.List(fields.Nested(EventItemSchema), required=True)
    limit = fields.Integer(required=True)
    offset = fields.Integer(required=True)
    total = fields.Integer(required=False)
