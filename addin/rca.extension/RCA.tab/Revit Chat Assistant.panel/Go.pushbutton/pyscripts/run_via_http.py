"""HTTP client for communicating with the FastAPI server.

Provides basic helpers to send chat messages and optionally trigger code
execution via HTTP requests. Minimal error handling by design.
"""
from __future__ import annotations

import os
from typing import Any, Dict

try:
    import httpx  # type: ignore
except Exception:
    httpx = None  # type: ignore

DEFAULT_BASE_URL = os.environ.get("RCA_SERVER_URL", "http://127.0.0.1:8000")


def send_chat_and_execute(message: str, session_id: str) -> str:
    """Send a chat message to the server and return the AI response.

    Args:
        message: User message text.
        session_id: A unique chat session identifier.

    Returns:
        The response text from the server.
    """
    if httpx is None:  # pragma: no cover - runtime environment specific
        return "httpx is not available in this environment."

    base = DEFAULT_BASE_URL.rstrip("/")
    try:
        # Send chat
        chat_resp = httpx.post(
            f"{base}/chat", json={"message": message, "session_id": session_id}, timeout=15
        )
        chat_resp.raise_for_status()
        data: Dict[str, Any] = chat_resp.json()
        response_text = str(data.get("response", ""))

        # Optionally, demonstrate an execute call when code is present in response
        # This is a placeholder; in real flow, we'd parse and ask for confirmation.
        if response_text.strip().startswith("```python"):
            code = response_text.strip().strip("`")
            exec_resp = httpx.post(f"{base}/execute", json={"code": code}, timeout=30)
            exec_resp.raise_for_status()
            exec_data: Dict[str, Any] = exec_resp.json()
            out = str(exec_data.get("output", ""))
            return f"Chat: {response_text}\nExecute Output:\n{out}"

        return response_text
    except Exception as exc:
        return f"[error] {exc}"
