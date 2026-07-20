"""
Structured logging configuration.

We use structlog on top of the stdlib `logging` module so that:
  - every log line is a structured event (key/value pairs), not a free-text
    sentence — this makes logs queryable in any log aggregator without
    regex parsing.
  - request-scoped context (request_id, user_id once auth exists) can be
    bound once per request and automatically attached to every subsequent
    log line in that request (see `app/middleware/request_id.py`).
  - output format is JSON in staging/production (machine-readable) and a
    colored, readable console format in local development.
"""

import logging
import sys

import structlog

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """
    Configure stdlib logging + structlog. Call once, at process startup
    (see `app/main.py`).
    """
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.log_level,
    )

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer()
        if settings.log_json
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a named, structured logger. Use `get_logger(__name__)` per module."""
    return structlog.get_logger(name)
