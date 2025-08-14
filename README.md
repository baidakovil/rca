# Revit Chat Assistant: LangChain‑first AI Agent for Autodesk Revit

## Overview

This project is a Python-based proof-of-concept AI agent that automates Autodesk Revit workflows using natural language prompts. The agent is built with LangChain (Python) and interprets user instructions to generate step-by-step guidance and code snippets for the Revit API.

## Features

- **Natural Language Automation:** Users describe tasks in plain English; the agent generates and executes Revit API code.
- **pyRevit Add-in:** Provides a native chat dialog UI within Revit using pyRevit Forms.
- **FastAPI Server:** Handles chat, code generation, and execution requests.
- **LLM Orchestration (LangChain):** Built on LangChain Runnables with per-session memory. Supports OpenAI, Anthropic Claude, and local models (Ollama). A deterministic "fake" provider is available for tests/offline.
- **Ansible Deployment:** Automated provisioning for Ubuntu servers.

## User Interaction Flow

1. **User in Revit** clicks a ribbon button and sees a **chat dialog** (pyRevit Forms).
2. User enters a task description as chat input.
3. The add-in sends this message to the **FastAPI server**.
4. The server’s **LangChain agent** (RunnableWithMessageHistory) processes the conversation, retrieves context, and generates step-by-step instructions or code.
5. The server returns the response; the add-in displays it in the same chat dialog.
6. User confirms execution; the add-in posts an execution request, and `subprocess.run()` applies changes in Revit.

## Project Structure

Project is split into two cooperating components.

## Architecture (short)

- Server (FastAPI + LangChain)
   - App: `server/src/main.py` (startup logging, includes router)
   - Routes: `server/src/api/routes.py` (`/health`, `/chat`, `/execute`)
   - Agent: `server/src/agent/langchat_agent.py` (LangChain Runnable agent with per-session memory)
   - Executor: `server/src/executor/runner.py` (subprocess runner with timeout)
   - Logger: `server/src/utils/logger.py` (env-driven log level, optional .env)
   - Models: `server/src/models/schema.py` (SQLModel stubs)
   - Ansible: `server/ansible/` (roles: fastapi, nginx)

- pyRevit Add-in
   - Bundle: `addin/revit_ai.bundle`
   - UI: `.../scripts/ui.py` (pyRevit Forms stubs)
   - HTTP client: `.../scripts/run_via_http.py` (basic `httpx` POSTs)
   - Resources: `.../resources/`

## LLM (LangChain providers)

Providers are configurable via environment variables. Install provider-specific packages as needed:

- OpenAI: `langchain-openai` (requires `OPENAI_API_KEY`)
- Anthropic (Claude): `langchain-anthropic` (requires `CLAUDE_API_KEY`)
- Ollama (local): `langchain-ollama` (or `langchain-community` fallback)
- Fake (tests/offline): no keys; uses a deterministic echo

### Why LangChain and how we use it

This project is “LangChain‑first” to avoid reinventing core LLM plumbing and to stay portable across model providers.

- Core building blocks: LangChain Runnables (Prompt | Model | Parser) with RunnableWithMessageHistory for per‑session memory.
- Prompting: ChatPromptTemplate combines a system message, history, and the human input.
- Memory: InMemoryChatMessageHistory keyed by session_id; can be swapped for a persistent store later.
- Tools: Implemented as first‑class LangChain Tools using the `@tool` decorator. The agent can optionally bind tools to the model at runtime (set `RCA_ENABLE_TOOLS=1`).
- Providers: Selected via `RCA_PROVIDER`. We use the split integrations (`langchain-openai`, `langchain-anthropic`, `langchain-ollama`) for clean, explicit dependencies.
- Deterministic development path: a built‑in “fake” provider provides predictable outputs for tests and offline work.

See the LangChain docs for details: https://python.langchain.com/docs/introduction/

## Configuration

- `LOG_LEVEL` — default `INFO` (logger)
- `RCA_SERVER_URL` — default `http://127.0.0.1:8000` (add-in HTTP client)
- `.env` files are supported on the server if `python-dotenv` is available
- `RCA_PROVIDER` — `openai` | `anthropic` | `ollama` | `fake` (default: `fake`)
- `RCA_TEMPERATURE` — float, model temperature (default `0`)
- `RCA_ENABLE_TOOLS` — `1` to enable tool binding (default `0`)
- `OPENAI_MODEL` — default `gpt-4o-mini`
- `CLAUDE_MODEL` — default `claude-3-5-sonnet-latest`
- `OLLAMA_MODEL` — default `llama3.1:8b`
- `OLLAMA_BASE_URL` — optional base URL for a local Ollama server

Ollama quick sample (server-side connector used in /chat when RCA_PROVIDER=ollama):

```python
import os
os.environ["RCA_PROVIDER"] = "ollama"
os.environ["OLLAMA_MODEL"] = "deepseek-coder-v2:16b"
# POST /chat with {"message":"Write a pyrevit script to delete all walls","session_id":"s1"}
```

## How to run (server)

On Ubuntu, from `server`:

```bash
./install.sh
```

This installs Python, creates a virtualenv, installs requirements, and runs the Ansible playbook.

Local development (Windows/WSL):

```bash
# activate your env, then
python -m uvicorn server.src.main:app --host 0.0.0.0 --port 8000 --reload
```

Provider env vars (set only what you need):
- `OPENAI_API_KEY` (for OpenAI)
- `CLAUDE_API_KEY` (for Anthropic/Claude)
- none (for `fake`), or local Ollama if using `ollama`

## Ansible role usage

The playbook `server/ansible/playbook.yml` includes roles `fastapi` and optional `nginx`. Fill role tasks to clone the repo, create a systemd service for Uvicorn, and configure Nginx.

## Install the pyRevit bundle (Windows 11)

See `addin/README-ADDIN.md` for steps to place `revit_ai.bundle` into the pyRevit extensions folder and load it in Revit.

Note: This POC currently returns code or instructions via chat; applying changes inside Revit requires the add-in to execute confirmed steps (future work). The server’s `/execute` runs Python code out-of-process for dry runs; it does not act inside a live Revit document yet.

### Tools

Tools are implemented as LangChain Tools. A sample tool is provided:

- `server/src/agent/tools/sample_select_elements.py` — `@tool("select_elements_by_category")` placeholder

Enable tool binding by setting `RCA_ENABLE_TOOLS=1`. Tools will be discovered and bound to the model in the agent at runtime.

### Architecture details (LangChain)

- Runnable pipeline: `Prompt(system + history + human) | ChatModel | StrOutputParser`.
- Memory wrapper: `RunnableWithMessageHistory` manages per‑session chat buffers.
- Provider factory: selects the chat model based on `RCA_PROVIDER` and related env vars.
- Tool binding: when `RCA_ENABLE_TOOLS=1`, the selected model is bound with discovered tools for function‑calling.
- Testability: the `fake` provider uses a `RunnableLambda` echo to keep unit tests deterministic.

## Run tests (server)

From `server` with your virtualenv active:

```bash
pytest
```

To see coverage:

```bash
pytest --cov=server.src --cov-report=term-missing
```

What’s covered:
- FastAPI endpoints: /health, /chat, /execute
- Agent behavior via LangChain Runnable (fake provider path)
- Subprocess runner success, error, and timeout paths
- Logger utility basics

## Roadmap: what should be done next (comprehensive)

Agent and orchestration
- Migrate the simple Runnable agent to a LangGraph workflow for robust tool‑use, retries, and human‑in‑the‑loop.
- Add structured outputs (pydantic) for code blocks, action plans, and parameters for tools.
- Implement streaming responses and partial updates to the add‑in UI.

Tools and Revit capabilities
- Add safe, read‑only Revit tools first (selectors, queries): categories, families, parameters, views, schedules.
- Implement write tools with guardrails: element creation, modification, deletion, parameter updates, view/filters.
- Standardize tool schemas, input validation, and error surfaces for reliable calling.
- Add a simple tool registry module to aggregate `get_tools()` from multiple modules.

In‑Revit execution
- Bridge from chat output to in‑process Revit execution via pyRevit (execute confirmed steps inside the active document).
- Sandboxing strategy for code execution; limit API surface; require explicit user confirmation.
- Transaction management helpers and dry‑run/preview paths.

Memory, state, and retrieval
- Replace in‑memory chat history with a persistent store (e.g., SQLite/SQLModel, Redis) per session/user.
- Add lightweight RAG: project standards, Revit API docs, internal BIM guides; create retrievers and citations.
- Implement session metadata (project id, Revit version, active doc context) for better grounding.

Safety and governance
- Add content filters and allow/deny lists for commands/tools.
- Add rate limits, timeouts, and circuit breakers per provider/tool.
- Require approvals for dangerous ops (bulk deletes, irreversible changes).

Observability and evaluation
- Integrate LangSmith traces for debugging and production visibility.
- Create evaluation sets (golden prompts) to track regressions and quality.

Testing and quality gates
- Expand unit tests for the agent, tools, and routes; include tool‑calling tests.
- Add integration tests for provider paths (mocked) and end‑to‑end tests with the add‑in client.
- Enforce linting, typing, and coverage in CI.

Performance and deployment
- Add configurable caching for prompts/embeddings where relevant.
- Optimize model selection (latency/cost), introduce small models for tool‑routing.
- Harden the Ansible roles; add systemd service, logs rotation, and optional Nginx reverse proxy/SSL.

Developer experience
- Provide `.env.example` and richer README snippets per provider.
- Add Makefile/Tasks for run, test, format, and lint.
- Document tool authoring guidelines and examples.