"""FastAPI routes for health, chat, and execution endpoints.

Minimal, non-destructive business logic to demonstrate wiring.

Integration points:
- LangChatAgent for LLM chat.
- runner.run_script for code execution.
"""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

import os
from server.src.agent.langchat_agent import LangChatAgent
from server.src.executor import runner


router = APIRouter()


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
	"""
	# Provider configurable via env; default to 'fake' for deterministic tests
	provider = os.getenv("RCA_PROVIDER", "fake")
	agent = LangChatAgent(provider=provider)
	response = agent.chat(message=req.message, session_id=req.session_id)
	return {"response": response}


@router.post("/execute")
def execute(req: ExecuteRequest) -> Dict[str, Any]:
	"""Execute provided code using the runner and return output.

	Args:
		req: ExecuteRequest containing code.

	Returns:
		A dictionary with the captured output.
	"""
	output = runner.run_script(script=req.code)
	return {"output": output}
