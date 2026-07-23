"""
Flask application factory.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

from app.controllers.alarm_controller import alarm_bp
from app.controllers.analytics_controller import analytics_bp
from app.controllers.events_controller import events_bp
from app.controllers.sensors_controller import sensors_bp
from app.extensions import db, migrate


def _monorepo_root() -> Path | None:
    try:
        return Path(__file__).resolve().parents[4]
    except IndexError:
        return None  # Running inside Docker


def _sqlalchemy_database_uri() -> str:
    raw = os.getenv("DATABASE_URL", "").strip()
    if raw and not raw.startswith("postgresql://${"):
        return raw

    user = quote_plus(os.getenv("POSTGRES_USER", "postgres"))
    password = quote_plus(os.getenv("POSTGRES_PASSWORD", ""))
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    name = os.getenv("POSTGRES_DB", "postgres")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


def create_app() -> Flask:
    root = _monorepo_root()
    if root is not None:
        load_dotenv(root / ".env", override=False)

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = _sqlalchemy_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-change-me")

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app.models.entities.event import Event  # noqa: F401
        from app.models.entities.sensor_reading import SensorReading  # noqa: F401
        db.create_all()

    CORS(app)

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "IoT Alarm API (Flask)",
            "description": "REST API for the IoT alarm system.",
            "version": "1.0.0",
        },
        "basePath": "/",
    }
    Swagger(app, template=swagger_template)

    app.register_blueprint(sensors_bp,   url_prefix="/sensors")
    app.register_blueprint(events_bp,    url_prefix="/api/v1/events")
    app.register_blueprint(alarm_bp,     url_prefix="/api/v1/alarm")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1/analytics")

    from app.services.event_cleanup import start_cleanup_task
    start_cleanup_task(app)

    return app
