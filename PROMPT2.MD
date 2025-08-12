
## Prompt 2/2: Populate Placeholders with Minimal Code

> **Context:** Same environment.  
> **Goal:** Populate placeholders with imports, class/function signatures, TODO comments, and docstrings.  
> **Constraints:**  
> - No full business logic.  
> - Indicate integration points: FastAPI routes, LangChat, subprocess, pyRevit Forms.

```markdown
1. **server/src/main.py**
   - Import `FastAPI`, create `app`.
   - Include routers from `api/routes.py`.
   - Add `@app.on_event("startup")` for logging.

2. **server/src/api/routes.py**
   - `@app.get("/health")` → `{"status":"ok"}`.
   - `@app.post("/chat")` → accept `{ "message": str, "session_id": str }`, call `LangChatAgent.chat(message, session_id)`.
   - `@app.post("/execute")` → accept `{ "code": str }`, call `runner.run_script(code)`.

3. **server/src/agent/langchat_agent.py**
   ```
   class LangChatAgent:
       """
       Manages chat sessions and LLM conversation using LangChat.
       """
       def __init__(self, provider: str):
           # TODO: initialize LangChain chat model
       
       def chat(self, message: str, session_id: str) -> str:
           """
           Send user message to LangChat chain and return response.
           """
           # TODO: implement chat step using LangChat
           return ""
   ```

4. **server/src/models/schema.py**
   ```
   class Project(SQLModel, table=True):
       id: int = Field(default=None, primary_key=True)
       name: str
       # TODO: add session and history fields
   ```

5. **server/src/utils/logger.py**
   ```
   def get_logger(name: str) -> logging.Logger:
       # TODO: configure logger
       return logging.getLogger(name)
   ```

6. **server/src/executor/runner.py**
   ```
   def run_script(script: str, timeout: int = 30) -> str:
       # TODO: write to temp and subprocess.run
       return ""
   ```

7. **server/ansible/playbook.yml**
   ```
   - hosts: all
     become: yes
     roles:
       - fastapi
       - nginx  # optional
   ```

8. **addin/revit_ai.bundle/scripts/ui.py**
   ```
   from pyrevit import forms

   def prompt_chat(session_id: str) -> str:
       """
       Display chat dialog and return user input.
       """
       # TODO: use forms.ask_for_string in a loop
       return ""

   def display_response(response: str) -> None:
       """
       Display AI-generated response in dialog.
       """
       # TODO: use forms.alert or custom form
   ```

9. **addin/revit_ai.bundle/scripts/run_via_http.py**
   ```
   def send_chat_and_execute(message: str, session_id: str) -> str:
       """
       Send chat message to server and return AI response.
       """
       # TODO: httpx.post to /chat, then handle follow-up actions
       return ""
   ```

10. **install.sh**
    ```
    #!/usr/bin/env bash
    sudo apt update && sudo apt install -y python3.11 python3.11-venv git
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ansible-playbook ansible/playbook.yml -i localhost,
    ```

11. **README.md**
    - How to run `install.sh` on Ubuntu  
    - Env vars for LLM provider  
    - Ansible role usage  
    - How to install the pyRevit bundle on Windows 11  

Ensure every stub has a docstring explaining its purpose and a `# TODO` placeholder.