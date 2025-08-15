"""FastAPI routes for health, chat, and execution endpoints.

Minimal, non-destructive business logic to demonstrate wiring.

Integration points:
- LangChatAgent for LLM chat.
- runner.run_script for code execution.
"""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import os
import logging
from server.src.agent.langchat_agent import LangChatAgent
from server.src.executor import runner


router = APIRouter()

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """Schema for chat requests.

    Attributes:
        message: User input to send to the agent.
        session_id: Identifier to track the conversation.
    """

    message: str
    session_id: str


class ExecuteRequest(BaseModel):
    """Schema for execution requests containing code to run."""

    code: str


@router.get("/health")
def health() -> Dict[str, str]:
    """Liveness probe endpoint.

    Returns:
        A simple status dictionary.
    """
    return {"status": "ok"}


@router.post("/chat")
def chat(req: ChatRequest) -> Dict[str, Any]:
    """Send a message to the LangChatAgent and return the response.

    Args:
        req: ChatRequest containing message and session_id.

    Returns:
        A dictionary with the agent response.

    Raises:
        HTTPException: If the agent invocation fails, with appropriate status codes:
            - 400: Invalid request parameters
            - 404: Resource not found (e.g., provider not available)
            - 500: Internal server error
    """
    try:
        # Get provider from environment with fallback to "fake"
        provider: str = os.getenv("RCA_PROVIDER", "fake")
        
        # Validate request parameters
        if not req.message.strip():
            logger.warning("Empty message received")
            raise HTTPException(status_code=400, detail="Message cannot be empty")
            
        if not req.session_id.strip():
            logger.warning("Empty session_id received")
            raise HTTPException(status_code=400, detail="Session ID cannot be empty")
        
        # Initialize agent with configured provider
        agent = LangChatAgent(provider=provider)
        
        # Process the message
        response: str = agent.chat(message=req.message, session_id=req.session_id)
        
        # Return successful response
        return {"response": response}
        
    except ValueError as exc:
        # Handle invalid inputs (like invalid provider)
        logger.warning("Invalid input: %s", exc)
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(exc)}")
        
    except ImportError as exc:
        # Handle missing dependencies (provider packages)
        logger.error("Missing dependency: %s", exc)
        raise HTTPException(status_code=404, detail=f"Provider not available: {str(exc)}")
        
    except Exception as exc:
        # Handle all other errors
        logger.exception("Error in /chat handler: %s", exc)
        # Return a sanitized error to the client
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(exc)}")


@router.post("/execute")
def execute(req: ExecuteRequest) -> Dict[str, Any]:
    """Execute provided code using the runner and return output.

    Args:
        req: ExecuteRequest containing code.

    Returns:
        A dictionary with the captured output.

    Raises:
        HTTPException: If execution fails.
    """
    try:
        output: Any = runner.run_script(script=req.code)
        return {"output": output}
    except Exception as exc:
        logger.exception("Error in /execute handler: %s", exc)
        raise HTTPException(status_code=500, detail="Execution failed")
