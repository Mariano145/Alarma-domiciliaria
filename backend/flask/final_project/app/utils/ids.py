"""Helpers for generating event identifiers."""

from ulid import ULID


def new_event_id() -> str:
    """Generates a new ULID-based event identifier as a string."""
    return str(ULID())
