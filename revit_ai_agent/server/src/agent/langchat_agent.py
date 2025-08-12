"""LangChain-powered chat agent.

This module implements a LangChain-first agent with:
- Provider-backed chat model factory (OpenAI, Anthropic, Ollama, Fake).
- RunnableWithMessageHistory for per-session memory.
- Prompt → model → output parsing using LangChain Runnables.

Environment variables:
- RCA_PROVIDER: one of "openai", "anthropic"/"claude", "ollama", or "fake" (default).
- RCA_TEMPERATURE: float, model temperature (default: 0).
- RCA_ENABLE_TOOLS: "1" to bind available tools to the model (default: "0").
- OPENAI_MODEL, CLAUDE_MODEL, OLLAMA_MODEL: optional model overrides per provider.
- OLLAMA_BASE_URL: optional base URL for local Ollama server.

Notes:
- The "fake" provider uses a deterministic RunnableLambda echo for tests/offline.
- For robust multi-tool agentic control, consider migrating to LangGraph.
"""
from __future__ import annotations

import os
from typing import Dict, Optional

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableWithMessageHistory,
)
from langchain_core.chat_history import InMemoryChatMessageHistory


class LangChatAgent:
    """Chat agent built on LangChain Runnables with per-session memory.

    The agent constructs a simple chain:
    ChatPromptTemplate(system + history + human) | ChatModel | StrOutputParser
    and wraps it with RunnableWithMessageHistory to maintain conversation state
    keyed by ``session_id``.

    Args:
        provider: LLM provider identifier. One of:
            - "openai" (requires langchain-openai and OPENAI_API_KEY)
            - "anthropic" or "claude" (requires langchain-anthropic and CLAUDE_API_KEY)
            - "ollama" (requires langchain-ollama or langchain-community with a local server)
            - "fake" (deterministic echo; no network or credentials required; default)
    """

    def __init__(self, provider: str) -> None:
        self.provider = (provider or "").lower() or "fake"
        self._histories: Dict[str, InMemoryChatMessageHistory] = {}
        self._chain: Optional[Runnable] = None

    # Public API
    def chat(self, message: str, session_id: str) -> str:
        """Run the chat chain with a message and session memory.

        The method retrieves/builds the Runnable chain, adds a history wrapper,
        and invokes it with the given ``message``. The per-session history is
        fetched by a key named ``session_id`` in the Runnable config.

        Args:
            message: The user's input message.
            session_id: Unique identifier for the conversation.

        Returns:
            The assistant's response as a string (already parsed via ``StrOutputParser``).

        Raises:
            RuntimeError: If the underlying model/plugin raises synchronously. In
                practice, provider-specific packages may raise ImportError or API
                errors during initialization if not installed/configured.
        """
        chain = self._get_or_build_chain()
        with_history = self._with_history(chain)
        result = with_history.invoke({"input": message}, config={"configurable": {"session_id": session_id}})
        return str(result)

    # Chain construction
    def _get_or_build_chain(self) -> Runnable:
        """Construct or return a cached LangChain Runnable pipeline.

        Pipeline shape:
            - Prompt: system + MessagesPlaceholder("history") + human("{input}")
            - Model: provider-selected chat model
            - Parser: StrOutputParser to coerce model output into ``str``

        If ``RCA_ENABLE_TOOLS=1`` and tools are available, the model will be
        bound with ``model.bind_tools(tools)``. Tools are optional and their
        absence will not break the chain construction.

        Returns:
            A ``Runnable`` that accepts a mapping with key ``"input"`` and
            returns a parsed string response.
        """
        if self._chain is not None:
            return self._chain

        system_prompt = self._format_system_prompt()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("history"),
                ("human", "{input}"),
            ]
        )

        model = self._make_model()
        # Optionally bind tools when supported
        if os.getenv("RCA_ENABLE_TOOLS", "0") == "1":
            try:
                tools = self._get_tools()
                if tools:
                    model = model.bind_tools(tools)  # type: ignore[attr-defined]
            except Exception:
                # Tool binding is optional; continue without tools
                pass
        parser = StrOutputParser()

        # A simple prompt -> model -> text chain
        self._chain = prompt | model | parser
        return self._chain

    def _with_history(self, chain: Runnable) -> RunnableWithMessageHistory:
        """Wrap a chain with per-session memory using ``RunnableWithMessageHistory``.

        Args:
            chain: The Runnable to be wrapped with chat history support.

        Returns:
            A ``RunnableWithMessageHistory`` that expects ``config={"configurable":
            {"session_id": "..."}}`` during invocation and will maintain a
            conversation buffer for that session.
        """
        def _get_history(session_id: str) -> InMemoryChatMessageHistory:
            if session_id not in self._histories:
                self._histories[session_id] = InMemoryChatMessageHistory()
            return self._histories[session_id]

        return RunnableWithMessageHistory(
            chain,
            lambda config: _get_history(config["configurable"]["session_id"]),
            input_messages_key="input",
            history_messages_key="history",
        )

    # Model factory
    def _make_model(self):  # type: ignore[no-untyped-def]
        """Instantiate a chat model for the configured provider.

        Provider mapping:
            - openai → langchain_openai.ChatOpenAI (OPENAI_MODEL or default)
            - anthropic/claude → langchain_anthropic.ChatAnthropic (CLAUDE_MODEL)
            - ollama → langchain_ollama.ChatOllama (or community fallback)
            - fake → RunnableLambda echo (no external deps)

        Environment:
            - RCA_TEMPERATURE: controls model temperature (default: 0)
            - Provider-specific API keys are expected by their integrations.

        Returns:
            A model-like Runnable compatible with the prompt and parser.

        Raises:
            ImportError: If a chosen provider package is missing.
        """
        provider = self.provider
        temperature = float(os.getenv("RCA_TEMPERATURE", "0"))

        if provider == "openai":
            from langchain_openai import ChatOpenAI

            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            return ChatOpenAI(model=model, temperature=temperature)

        if provider in ("anthropic", "claude"):
            from langchain_anthropic import ChatAnthropic

            model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")
            return ChatAnthropic(model=model, temperature=temperature)

        if provider == "ollama":
            try:
                from langchain_ollama import ChatOllama  # preferred package
            except Exception:  # fallback to community if needed
                from langchain_community.chat_models import ChatOllama  # type: ignore

            model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            base_url = os.getenv("OLLAMA_BASE_URL")
            kwargs = {"model": model, "temperature": temperature}
            if base_url:
                kwargs["base_url"] = base_url
            return ChatOllama(**kwargs)  # type: ignore[arg-type]

        # Deterministic fake model for tests and offline dev
        def _echo(inputs: Dict[str, str]) -> str:
            text = inputs.get("input", "")
            # Keep a predictable shape for tests
            return f"[provider={provider}][echo] {text}"

        return RunnableLambda(_echo)

    # Prompts
    def _format_system_prompt(self) -> str:
        """Return the system prompt guiding assistant behavior.

        Returns:
            A concise system instruction string emphasizing Revit context and
            Python/pyRevit/Revit API for code generation.
        """
        return (
            "You are a helpful assistant for Autodesk Revit via pyRevit. "
            "Be concise. When generating code, use Python and pyRevit/Revit API."
        )

    # Tools registry (minimal)
    def _get_tools(self) -> list:  # type: ignore[no-untyped-def]
        """Discover and return available LangChain tools for binding.

        Returns:
            A list of LangChain Tool objects. Returns an empty list if tools
            cannot be imported or none are available.
        """
        try:
            from server.src.agent.tools.sample_select_elements import get_tools

            return get_tools()
        except Exception:
            return []
