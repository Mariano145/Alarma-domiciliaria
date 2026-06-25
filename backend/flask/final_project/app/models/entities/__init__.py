"""SQLAlchemy entity models."""

from app.models.entities.event import Event
from app.models.entities.sensor_reading import SensorReading

__all__ = ["Event", "SensorReading"]
