"""Logger configuration utility.

Provides a helper to get a configured logger instance with consistent
formatting and environment-driven log level.
"""
from __future__ import annotations

import logging
import os
from typing import Final

try:
    # Optional: load environment variables from a .env file if present.
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    # Silently ignore if dotenv isn't available; logging still works.
    pass

_DEFAULT_LEVEL: Final[str] = "INFO"
_LOG_FORMAT: Final[str] = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger.

    Args:
        name: Logger name.

    Returns:
        A logger instance.
    """
    # Configure root logger once.
    root = logging.getLogger()
    if not root.handlers:
        level_name = os.getenv("LOG_LEVEL", _DEFAULT_LEVEL).upper()
        level = getattr(logging, level_name, logging.INFO)
        logging.basicConfig(level=level, format=_LOG_FORMAT, datefmt=_DATE_FORMAT)

    logger = logging.getLogger(name)
    return logger
