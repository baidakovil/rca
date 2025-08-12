"""Unit tests for LangChatAgent placeholder behavior."""
from __future__ import annotations

from server.src.agent.langchat_agent import LangChatAgent


def test_agent_echo() -> None:
    agent = LangChatAgent(provider="fake")
    out = agent.chat("Ping", session_id="abc")
    assert "provider=fake" in out
    assert "Ping" in out
