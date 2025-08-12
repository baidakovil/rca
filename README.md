# Revit Chat Assistant: Proof-of-Concept AI Agent for Autodesk Revit

## Overview

This project is a Python-based proof-of-concept AI agent that automates Autodesk Revit workflows using natural language prompts. The agent interprets user instructions and generates the necessary code snippets to achieve the desired outcome in Revit.

## Features

- **Natural Language Automation:** Users describe tasks in plain English; the agent generates and executes Revit API code.
- **pyRevit Add-in:** Provides a native chat dialog UI within Revit using pyRevit Forms.
- **FastAPI Server:** Handles chat, code generation, and execution requests.
- **LLM Orchestration:** Supports OpenAI, Anthropic Claude, and local models (Ollama/MLX) via LangChain.
- **Ansible Deployment:** Automated provisioning for Ubuntu servers.

## User Interaction Flow

1. **User in Revit** clicks a ribbon button and sees a **chat dialog** (pyRevit Forms).
2. User enters a task description as chat input.
3. The add-in sends this message to the **FastAPI server**.
4. The server’s **LangChain agent** processes the conversation, retrieves context, and generates step-by-step instructions or code.
5. The server returns the response; the add-in displays it in the same chat dialog.
6. User confirms execution; the add-in posts an execution request, and `subprocess.run()` applies changes in Revit.

## Project Structure

Project is split into two cooperating components:

1. **Server** (Ubuntu deployment via Ansible)  
   - FastAPI application with Uvicorn  
   - LangChain for LLM orchestration  
   - SQLite for lightweight persistence  
   - Direct LLM calls (OpenAI, Anthropic Claude, or local via Ollama/MLX)  
   - `subprocess.run()` for dry-run script execution  
   - Ansible playbook and roles for provisioning and deployment  

2. **pyRevit Add-in** (Windows 11 ARM development, VS Code IDE)  
   - pyRevit bundle (`*.bundle`)  
   - pyRevit Forms for native prompt dialogs and result display  
   - HTTP client scripts to call FastAPI endpoints  
   - Executed in-context via RevitPythonShell  

## LLM

Supported LLM providers must be configurable via environment variables:  
- `OPENAI_API_KEY`  
- `CLAUDE_API_KEY`  
- Local model endpoint for Ollama (`ollama`) or MLX (`mlx`)