"""
app/core/logging.py
───────────────────
Structured logging setup using structlog + python-json-logger.

JSON format is used in staging/production (machine-parseable).
Human-readable console format is used in development.

Usage anywhere in the codebase:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("hotspot_detected", hotspot_id=42, eis=87.3)
"""

from __future__ import annotations

import logging
import logging.config
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import structlog

from app.core.config import settings


def _build_stdlib_handler(log_file: Optional[Path]) -> Dict[str, Any]:
    """Return handler config for stdlib logging."""
    handlers: Dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json" if settings.LOG_FORMAT == "json" else "text",
        }
    }
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(log_file),
            "maxBytes": 10 * 1024 * 1024,   # 10 MB
            "backupCount": 5,
            "formatter": "json",
            "encoding": "utf-8",
        }
    return handlers


def configure_logging() -> None:
    """
    Call once at application startup (inside create_app / lifespan).
    Configures both stdlib logging (used by FastAPI/Uvicorn/SQLAlchemy)
    and structlog (used by ParkWise application code).
    """
    log_file = settings.LOG_FILE

    handlers = _build_stdlib_handler(log_file)
    active_handlers = list(handlers.keys())

    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
            "text": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": handlers,
        "loggers": {
            # Root logger — catches everything not explicitly named
            "": {
                "handlers": active_handlers,
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            # Quiet down chatty third-party libraries
            "uvicorn": {"handlers": active_handlers, "level": "INFO", "propagate": False},
            "uvicorn.access": {"handlers": active_handlers, "level": "WARNING", "propagate": False},
            "sqlalchemy.engine": {
                "handlers": active_handlers,
                "level": "WARNING" if settings.is_production else "INFO",
                "propagate": False,
            },
            "alembic": {"handlers": active_handlers, "level": "INFO", "propagate": False},
        },
    }

    logging.config.dictConfig(logging_config)

    # ── structlog configuration ───────────────────────────────────────────────
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.LOG_FORMAT == "json" or settings.is_production:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Returns a structlog BoundLogger for the given module name.

    Example:
        logger = get_logger(__name__)
        logger.info("eis_computed", hotspot_id=7, score=92.4, category="Critical")
    """
    return structlog.get_logger(name)
