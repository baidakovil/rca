"""Main entrypoint for the FastAPI server (proof-of-concept).

This module defines the application object used by the ASGI server and wires
API routes. It also provides a minimal startup hook for logging.

TODO:
- Expand startup/shutdown handling and structured logging as needed.
"""
from __future__ import annotations

from fastapi import FastAPI

from server.src.api.routes import router as api_router
from server.src.utils.logger import get_logger

# Create the FastAPI application instance used by Uvicorn or other ASGI servers.
import contextlib
from typing import AsyncGenerator

logger = get_logger(__name__)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
	"""Lifespan context manager for FastAPI startup and shutdown events.

	Args:
		app (FastAPI): The FastAPI application instance.

	Yields:
		None

	Raises:
		None
	"""
	# Startup logic
	logger.info("Starting Revit AI Server (POC)")
	# TODO: Add environment checks, DB init, etc.
	yield
	# Shutdown logic (if needed)

app: FastAPI = FastAPI(title="Revit AI Server (POC)", lifespan=lifespan)

# Include API routes.
app.include_router(api_router)
