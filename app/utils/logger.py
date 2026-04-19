"""
Centralised logging configuration.

Usage anywhere in the codebase::

    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Something happened")
"""

import logging
import sys
from typing import Optional


_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Track whether root configuration has been applied
_configured = False


def configure_logging(level: int = logging.INFO) -> None:
    """Apply root-level logging configuration once.

    Called once from app startup.  Safe to call multiple times – subsequent
    calls are ignored so test fixtures cannot accidentally reconfigure.
    """
    global _configured
    if _configured:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger()
    root.setLevel(level)
    # Remove any pre-existing handlers (e.g. from basicConfig in tests)
    root.handlers.clear()
    root.addHandler(handler)

    # Quieten noisy third-party loggers
    for noisy in ("pymongo", "passlib", "multipart"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _configured = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a named logger.  configure_logging() is called lazily if needed."""
    configure_logging()
    return logging.getLogger(name)
