"""Pytest fixtures for FastAPI app and test client."""
from __future__ import annotations

import os
import sys
import typing as t
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add the parent directory to Python path to resolve imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Ensure app import path works relative to server folder
os.environ.setdefault("LOG_LEVEL", "DEBUG")


@pytest.fixture(scope="session")
def client() -> t.Iterator[TestClient]:
    """Provide a TestClient for the FastAPI app."""
    from server.src.main import app  # import inside to honor pythonpath

    with TestClient(app) as c:
        yield c
