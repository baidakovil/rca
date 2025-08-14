"""Unit tests for logger utility."""
from __future__ import annotations

import logging
import os

from server.src.utils.logger import get_logger


def test_get_logger_basic() -> None:
    os.environ["LOG_LEVEL"] = "WARNING"
    logger = get_logger("x")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "x"
