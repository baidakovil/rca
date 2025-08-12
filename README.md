# Proof-of-Concept AI Agent for Revit

This document outlines a Python-based proof-of-concept AI agent that automates Revit workflows by cloning the core ideas of ArchiLabs. It is split into two cooperating components:

1. **Server** (Ubuntu deployment via Ansible)  
   - FastAPI application with Uvicorn  
   - SQLite (SQLModel) for lightweight persistence  
   - Direct LLM calls (OpenAI, Anthropic Claude, or local via Ollama/MLX)  
   - `subprocess.run()` for dry-run script execution  
   - Ansible playbook and roles for provisioning and deployment  

2. **pyRevit Add-in** (Windows 11 development, VS Code IDE)  
   - pyRevit bundle (`*.bundle`)  
   - pyRevit Forms for native prompt dialogs and result display  
   - HTTP client scripts to call FastAPI endpoints  
   - Executed in-context via RevitPythonShell  

Supported LLM providers must be configurable via environment variables:  
- `OPENAI_API_KEY`  
- `CLAUDE_API_KEY`  
- Local model endpoint for Ollama (`ollama`) or MLX (`mlx`)
