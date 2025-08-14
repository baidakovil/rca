"""Route tests for health, chat, and execute endpoints."""
from __future__ import annotations

from typing import Dict


def test_health(client) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_chat_echo(client) -> None:
    payload: Dict[str, str] = {"message": "Hello", "session_id": "s1"}
    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert "Hello" in data["response"]


def test_execute_print(client) -> None:
    code = "print('hi')"
    r = client.post("/execute", json={"code": code})
    assert r.status_code == 200
    data = r.json()
    assert data["output"].strip().startswith("hi")
