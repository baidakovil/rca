# Revit AI Server (POC)

This folder contains the FastAPI server scaffolding for the Revit Chat Assistant.

## Architecture (high level)

- FastAPI application (`src/main.py`)
- API routes (`src/api/routes.py`) for health, chat, and execute
- Agent wrapper (`src/agent/langchat_agent.py`) for LLM orchestration (LangChain/LangChat)
- Models (`src/models/schema.py`) using SQLModel
- Utilities (`src/utils/logger.py`) for logging
- Executor (`src/executor/runner.py`) to run generated code via subprocess
- Ansible deployment (`ansible/`) for Ubuntu servers

## Environment Setup

- LLM provider environment variables:
  - `OPENAI_API_KEY`
  - `CLAUDE_API_KEY`
  - Optional local models via Ollama/MLX

## Install on Ubuntu

Run the bootstrap script:

```bash
./install.sh
```

This will:
- Install Python 3.11, venv, and git
- Create and activate a virtualenv
- Install requirements
- Run the Ansible playbook

## Debugging on Windows — single recommended method

Use PowerShell's Invoke-RestMethod for local testing and debugging (preferred).

POST (JSON body):
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/chat' -Method POST -ContentType 'application/json' -Body '{"message":"List steps to delete all walls","session_id":"dev1"}'
```

Health:
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'  
```

Notes:
- Use the POST endpoint for real clients; GET is a convenience for quick checks.
- Ensure the server is running: `python -m uvicorn server.src.main:app --reload`

## Ansible Usage

The playbook at `ansible/playbook.yml` invokes roles `fastapi` and optionally `nginx`.
Fill in role tasks to provision the server, create a systemd service, and configure Nginx as a reverse proxy.

## Notes

This is a scaffold only (Prompt 1). Real route handlers, logging, and execution logic will be added in Prompt 2.
