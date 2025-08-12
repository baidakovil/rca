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
app: FastAPI = FastAPI(title="Revit AI Server (POC)")

logger = get_logger(__name__)


@app.on_event("startup")
async def on_startup() -> None:
	"""Log a basic startup message.

	Raises:
		None
	"""
	# TODO: Add environment checks, DB init, etc.
	logger.info("Starting Revit AI Server (POC)")

# Include API routes.
app.include_router(api_router)
