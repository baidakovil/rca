
## Prompt 1/2: Project Scaffolding & Overview

> **Context:** AI assistant in VS Code on Windows 11.  
> **Goal:** Initialize a new Python project that clones ArchiLabs-style Revit automation using **pyRevit Forms** for chat UI and **LangChat** for LLM orchestration.  
> **Constraints:**  
> - No detailed business logic.  
> - Create skeleton folder structure, config files, placeholder modules.  
> - Ansible roles target Ubuntu servers.  
> - Include TODO markers and docstrings.

1. Create root directory `revit_ai_agent/`.

2. Inside, create two subdirectories:
   - `server/`
   - `addin/`

3. **server/**:
   - `src/`
     - `main.py` — stub FastAPI entrypoint
     - `api/`
       - `routes.py` — stub for `/health`, `/chat` (LangChat endpoint), `/execute`
     - `agent/`
       - `langchat_agent.py` — stub class `LangChatAgent` wrapping LangChain chat
     - `models/`
       - `schema.py` — SQLModel `Project` stub
     - `utils/`
       - `logger.py` — stub logging setup
     - `executor/`
       - `runner.py` — stub to run generated code via `subprocess`
   - `ansible/`
     - `playbook.yml` — Ansible playbook scaffold
     - `roles/`
       - `fastapi/` — install Python, venv, clone repo, systemd
       - `nginx/` (optional)
   - `requirements.txt` — include:
     ```
     fastapi
     uvicorn
     sqlmodel
     openai
     anthropic
     ollama-sdk
     mlx-sdk
     httpx
     langchain
     ```
   - `install.sh` — Ubuntu bootstrap:
     ```
     #!/usr/bin/env bash
     sudo apt update && sudo apt install -y python3.11 python3.11-venv git
     python3.11 -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ansible-playbook ansible/playbook.yml -i localhost,
     ```
   - `.pre-commit-config.yaml` — Black, isort, flake8, mypy
   - `README.md` — architecture, Ansible usage, env setup

4. **addin/**:
   - `revit_ai.bundle/`
     - `extension.json` — pyRevit manifest stub
     - `scripts/`
       - `ui.py` — stub for chat dialog using pyRevit Forms
       - `run_via_http.py` — stub HTTP client to send chat messages & execute code
     - `resources/` — placeholder icons
   - `README-ADDIN.md` — install instructions for Windows 11/pyRevit

5. `.vscode/launch.json` with:
   - FastAPI server debug
   - Add-in `ui.py` under RevitPythonShell
   - Optional pytest config

Each file must include `# TODO` and docstrings explaining its role.