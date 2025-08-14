"""Pytest fixtures for FastAPI app and test client."""
from __future__ import annotations

import os
import typing as t

import pytest
from fastapi.testclient import TestClient

# Ensure app import path works relative to server folder
os.environ.setdefault("LOG_LEVEL", "DEBUG")


@pytest.fixture(scope="session")
def client() -> t.Iterator[TestClient]:
    """Provide a TestClient for the FastAPI app."""
    from server.src.main import app  # import inside to honor pythonpath

    with TestClient(app) as c:
        yield c
