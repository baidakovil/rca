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
import logging
from enum import Enum
from typing import (
    Any, 
    Dict, 
    Generic, 
    List, 
    Literal, 
    Optional, 
    Protocol, 
    TypedDict, 
    TypeVar, 
    Union, 
    cast
)

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableWithMessageHistory,
    RunnableConfig,
)
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

# Set up module logger
logger = logging.getLogger(__name__)

# Type variables for generics
T_in = TypeVar("T_in")
T_out = TypeVar("T_out")

# Type definitions for configuration
class ConfigurableDict(TypedDict, total=False):
    """Type definition for the configurable section of RunnableConfig."""
    
    session_id: str

class AgentConfig(TypedDict, total=False):
    """Type definition for the configuration passed to Runnable.invoke."""
    
    configurable: ConfigurableDict

# Protocol definitions
class MessageHistoryProvider(Protocol):
    """Protocol for classes that can provide message history."""
    
    def __call__(self, config: AgentConfig) -> BaseChatMessageHistory:
        """Get message history from configuration.
        
        Args:
            config: Configuration containing session information.
            
        Returns:
            A chat message history object.
        """
        ...

class ProviderEnum(str, Enum):
    """Supported LLM providers."""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CLAUDE = "claude"  # Alias for ANTHROPIC
    OLLAMA = "ollama"
    FAKE = "fake"

# Custom exceptions
class AgentConfigError(Exception):
    """Raised when there's an issue with agent configuration."""
    pass

class SessionHistoryError(Exception):
    """Raised when there's an issue with session history management."""
    pass

class ModelProviderError(Exception):
    """Raised when there's an issue with the model provider."""
    pass


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
            
    Raises:
        ValueError: If an invalid provider is specified.
    """

    def __init__(self, provider: str) -> None:
        """Initialize the chat agent with the specified provider.
        
        Args:
            provider: LLM provider identifier (openai, anthropic/claude, ollama, fake).
            
        Raises:
            ValueError: If the provider is invalid or empty.
        """
        # Normalize and validate provider
        normalized_provider = (provider or "").lower().strip()
        if not normalized_provider:
            normalized_provider = "fake"
            
        # Validate against enum
        try:
            if normalized_provider == "claude":
                # Handle alias
                self.provider = ProviderEnum.ANTHROPIC
            else:
                self.provider = ProviderEnum(normalized_provider)
        except ValueError:
            valid_providers = [p.value for p in ProviderEnum]
            raise ValueError(
                f"Invalid provider '{provider}'. Valid options: {', '.join(valid_providers)}"
            )
            
        self._histories: Dict[str, InMemoryChatMessageHistory] = {}
        self._chain: Optional[Runnable[Dict[str, Any], str]] = None
        
        # Set up logging
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._logger.debug(f"Initialized with provider: {self.provider}")

    # Public API
    def chat(self, message: str, session_id: str) -> str:
        """Process a chat message and return an AI response.

        The method retrieves/builds the Runnable chain and manages conversation history
        for the given session.

        Args:
            message: The user's input message.
            session_id: Unique identifier for the conversation.

        Returns:
            The assistant's response as a string.

        Raises:
            AgentConfigError: If there is an issue with agent configuration.
            SessionHistoryError: If there is an issue managing session history.
            ModelProviderError: If the underlying model provider fails.
            ValueError: If message or session_id are invalid.
        """
        # Input validation
        if not message or not isinstance(message, str):
            raise ValueError("Message must be a non-empty string")
        
        if not session_id or not isinstance(session_id, str):
            raise ValueError("Session ID must be a non-empty string")
            
        self._logger.debug(f"Processing message for session: {session_id}")
        
        # Use robust method with proper error handling
        try:
            # Get or create session history
            history = self._get_or_create_history(session_id)
            
            # Add the user message to history
            history.add_user_message(message)
            
            # Get the runnable chain
            chain = self._get_or_build_chain()
            
            # For the fake provider, handle directly
            if self.provider == ProviderEnum.FAKE:
                # Simplest possible response for testing
                result = f"[provider=fake][echo] {message}"
                self._logger.debug(f"Created fake response for session: {session_id}")
            else:
                # For real providers, use the chain
                try:
                    # Create input dict with the required keys for our chain
                    # The keys must match what the prompt template expects
                    inputs = {
                        "input": message,
                        "history": history.messages
                    }
                    
                    # Process the message with the chain
                    self._logger.debug(f"Invoking chain for session: {session_id}")
                    result = chain.invoke(inputs)
                    self._logger.debug(f"Chain invocation successful for session: {session_id}")
                except Exception as chain_error:
                    self._logger.error(
                        f"Error invoking chain: {str(chain_error)}",
                        exc_info=True
                    )
                    raise ModelProviderError(f"Failed to process message: {str(chain_error)}")
            
            # Validate result - result should be a string from StrOutputParser
            response = str(result) if result is not None else ""
            if not response:
                raise ModelProviderError("Model returned empty response")
                
            # Store the AI response in history
            history.add_ai_message(response)
            
            self._logger.debug(f"Successfully processed message for session: {session_id}")
            return response
            
        except ImportError as e:
            # Provider package missing
            self._logger.error(f"Provider package missing: {str(e)}", exc_info=True)
            raise ModelProviderError(f"Provider '{self.provider.value}' not available: {str(e)}")
            
        except (KeyError, TypeError) as e:
            # Configuration or type errors
            self._logger.error(f"Configuration error: {str(e)}", exc_info=True)
            raise AgentConfigError(f"Invalid agent configuration: {str(e)}")
            
        except Exception as e:
            # Catch-all for other errors
            self._logger.error(f"Unexpected error in chat: {str(e)}", exc_info=True)
            raise ModelProviderError(f"Error processing message: {str(e)}")
            
    def _get_or_create_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """Get or create a message history for the given session ID.
        
        Args:
            session_id: Unique identifier for the conversation.
            
        Returns:
            Chat message history for the session.
            
        Raises:
            SessionHistoryError: If history creation fails.
        """
        try:
            if session_id not in self._histories:
                self._logger.debug(f"Creating new history for session: {session_id}")
                self._histories[session_id] = InMemoryChatMessageHistory()
            return self._histories[session_id]
        except Exception as e:
            self._logger.error(f"Error managing session history: {str(e)}", exc_info=True)
            raise SessionHistoryError(f"Failed to manage history for session {session_id}: {str(e)}")

    # Chain construction
    def _get_or_build_chain(self) -> Runnable[Dict[str, Any], str]:
        """Construct or return a cached LangChain Runnable pipeline.

        Pipeline shape:
            - Prompt: system + MessagesPlaceholder("history") + human("{input}")
            - Model: provider-selected chat model
            - Parser: StrOutputParser to coerce model output into ``str``

        If ``RCA_ENABLE_TOOLS=1`` and tools are available, the model will be
        bound with ``model.bind_tools(tools)``. Tools are optional and their
        absence will not break the chain construction.

        Returns:
            A ``Runnable`` that accepts a mapping with keys ``"input"`` and ``"history"``
            and returns a parsed string response.
            
        Raises:
            AgentConfigError: If chain construction fails due to configuration issues.
        """
        # Return cached chain if available
        if self._chain is not None:
            return self._chain

        try:
            # Create system prompt
            system_prompt = self._format_system_prompt()
            
            # Build prompt template with explicit variable names
            # The keys in this template must match the keys in the input dict
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    MessagesPlaceholder(variable_name="history"),
                    ("human", "{input}"),
                ]
            )

            # Get the appropriate model for the configured provider
            model = self._make_model()
            
            # Optionally bind tools when supported
            if os.getenv("RCA_ENABLE_TOOLS", "0") == "1":
                try:
                    tools = self._get_tools()
                    if tools:
                        # Type ignore is necessary as model types vary by provider
                        # and not all support bind_tools, but we check at runtime
                        model = model.bind_tools(tools)  # type: ignore[attr-defined]
                except Exception as e:
                    # Tool binding is optional; continue without tools
                    self._logger.warning(f"Failed to bind tools: {str(e)}")
                    
            # Create output parser
            parser = StrOutputParser()

            # Just build a direct chain - simple is better
            # The LangChain core classes should handle input validation
            chain = prompt | model | parser
            
            # Cast to expected return type
            typed_chain = cast(Runnable[Dict[str, Any], str], chain)
            
            # Cache the chain
            self._chain = typed_chain
            return typed_chain
            
        except Exception as e:
            self._logger.error(f"Failed to build chain: {str(e)}", exc_info=True)
            raise AgentConfigError(f"Failed to build agent chain: {str(e)}")

    def _with_history(self, chain: Runnable[Dict[str, Any], str]) -> RunnableWithMessageHistory:
        """Wrap a chain with per-session memory using ``RunnableWithMessageHistory``.

        This method is kept for reference but is no longer used in the main workflow,
        as we manage history manually for better error handling and type safety.

        Args:
            chain: The Runnable to be wrapped with chat history support.

        Returns:
            A ``RunnableWithMessageHistory`` that maintains conversation buffers
            per session.
            
        Raises:
            SessionHistoryError: If history management fails.
        """
        try:
            # Define a history getter that safely extracts session_id from config
            def get_session_history(config: AgentConfig) -> BaseChatMessageHistory:
                """Get message history for a session from config.
                
                Args:
                    config: Configuration dict with session information.
                    
                Returns:
                    Message history for the session.
                """
                try:
                    # Default session ID as fallback
                    session_id = "default"
                    
                    # Extract session_id from config dict if available
                    if (
                        isinstance(config, dict) 
                        and "configurable" in config 
                        and isinstance(config["configurable"], dict)
                        and "session_id" in config["configurable"]
                    ):
                        extracted_id = config["configurable"]["session_id"]
                        if isinstance(extracted_id, str) and extracted_id:
                            session_id = extracted_id
                    
                    # Get or create history for this session
                    return self._get_or_create_history(session_id)
                    
                except Exception as e:
                    self._logger.error(f"Error in get_session_history: {str(e)}", exc_info=True)
                    # Return a default history as fallback
                    if "default" not in self._histories:
                        self._histories["default"] = InMemoryChatMessageHistory()
                    return self._histories["default"]
            
            # Create and return the history-wrapped chain
            return RunnableWithMessageHistory(
                chain,
                get_session_history,
                input_messages_key="input",
                history_messages_key="history",
            )
            
        except Exception as e:
            self._logger.error(f"Failed to create history wrapper: {str(e)}", exc_info=True)
            raise SessionHistoryError(f"Failed to create message history wrapper: {str(e)}")

    # Model factory
    def _make_model(self) -> Any:
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
            ModelProviderError: If the model cannot be created or initialized.
            ImportError: If a chosen provider package is missing.
        """
        try:
            # Get model temperature from environment
            temperature_str = os.getenv("RCA_TEMPERATURE", "0")
            try:
                temperature = float(temperature_str)
            except ValueError:
                self._logger.warning(f"Invalid temperature '{temperature_str}', using default 0.0")
                temperature = 0.0

            # Create model based on provider
            if self.provider == ProviderEnum.OPENAI:
                from langchain_openai import ChatOpenAI

                model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                self._logger.debug(f"Creating OpenAI model: {model_name}")
                return ChatOpenAI(model=model_name, temperature=temperature)

            if self.provider == ProviderEnum.ANTHROPIC:
                from langchain_anthropic import ChatAnthropic

                model_name = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")
                self._logger.debug(f"Creating Anthropic model: {model_name}")
                # Using model_name parameter as per latest langchain-anthropic API
                return ChatAnthropic(model_name=model_name, temperature=temperature)

            if self.provider == ProviderEnum.OLLAMA:
                # Try preferred package first, fall back to community if needed
                self._logger.debug("Setting up Ollama model")
                try:
                    from langchain_ollama import ChatOllama
                    self._logger.debug("Using langchain_ollama package")
                except ImportError:
                    self._logger.debug("Falling back to langchain_community.chat_models")
                    from langchain_community.chat_models import ChatOllama  # type: ignore

                model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
                base_url = os.getenv("OLLAMA_BASE_URL")
                
                # Build kwargs dict for Ollama
                kwargs: Dict[str, Any] = {"model": model_name, "temperature": temperature}
                if base_url:
                    kwargs["base_url"] = base_url
                    
                self._logger.debug(f"Creating Ollama model: {model_name}")
                return ChatOllama(**kwargs)

            # Fake model (default) for testing or development
            if self.provider == ProviderEnum.FAKE:
                self._logger.debug("Creating fake echo model")
                
                # Use a simple RunnableLambda instead of a full model
                # This avoids all the complex model interfaces
                def fake_chat_fn(inputs: Dict[str, Any]) -> str:
                    """Simple echo function for testing."""
                    # Extract input from messages or text
                    if isinstance(inputs, dict):
                        if "input" in inputs:
                            text = str(inputs["input"])
                        elif "messages" in inputs:
                            messages = inputs["messages"]
                            if messages and hasattr(messages[-1], "content"):
                                text = str(messages[-1].content)
                            else:
                                text = "No message content"
                        else:
                            text = str(inputs)
                    else:
                        text = str(inputs)
                    
                    # Return a deterministic response
                    return f"[provider=fake][echo] {text}"
                
                return RunnableLambda(fake_chat_fn)
                
            # Should not reach here due to validation in __init__
            raise ValueError(f"Unsupported provider: {self.provider}")
            
        except ImportError as e:
            # Package missing
            self._logger.error(f"Provider package missing: {str(e)}", exc_info=True)
            raise ImportError(f"Provider '{self.provider.value}' package not available: {str(e)}")
            
        except Exception as e:
            # Other errors
            self._logger.error(f"Failed to create model: {str(e)}", exc_info=True)
            raise ModelProviderError(f"Failed to create model for {self.provider.value}: {str(e)}")

    # Prompts
    def _format_system_prompt(self) -> str:
        """Generate the system prompt guiding assistant behavior.

        Returns:
            A system instruction string emphasizing Revit context and
            Python/pyRevit/Revit API for code generation.
        """
        return (
            "You are a helpful assistant for Autodesk Revit via pyRevit. "
            "Be concise. When generating code, use Python and pyRevit/Revit API."
        )

    # Tools registry
    def _get_tools(self) -> List[Any]:
        """Discover and return available LangChain tools for binding.

        Returns:
            A list of LangChain Tool objects.
            
        Raises:
            AgentConfigError: If tools are enabled but cannot be loaded.
        """
        try:
            from server.src.agent.tools.sample_select_elements import get_tools

            tools = get_tools()
            if not isinstance(tools, list):
                self._logger.warning("get_tools() did not return a list")
                return []
                
            self._logger.debug(f"Loaded {len(tools)} tools")
            return tools
            
        except ImportError as e:
            # Tools module not found
            self._logger.warning(f"Tools module not found: {str(e)}")
            return []
            
        except Exception as e:
            # Other errors
            self._logger.error(f"Error loading tools: {str(e)}", exc_info=True)
            return []
