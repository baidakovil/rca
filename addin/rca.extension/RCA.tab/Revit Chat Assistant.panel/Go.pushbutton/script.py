#! python3

"""Revit Chat Assistant UI entrypoint.

Loads WPF XAML (ChatWindow.xaml) and wires event handlers to talk to the
FastAPI server. Provides background-threaded network calls and code execution
via pyRevit CLI to keep UI responsive.
"""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import threading
import uuid
from typing import Any, Optional

# pyRevit WPF / .NET interop (CPython-safe)
from pyrevit.framework import wpf, Windows, Interop  # type: ignore
from pyrevit.api import AdWindows  # type: ignore

# Try .NET HttpClient (works in both IronPython and pythonnet environments)
try:  # pragma: no cover - environment dependent
    import clr  # type: ignore[reportMissingImports]
    from System import Uri  # type: ignore[reportMissingModuleSource]
    from System.Text import Encoding  # type: ignore[reportMissingModuleSource]
    from System.Net.Http import (  # type: ignore[reportMissingModuleSource]
        HttpClient,
        HttpRequestMessage,
        HttpMethod,
        StringContent,
    )
    has_dotnet_http = True
except Exception:  # pragma: no cover
    HttpClient = None  # type: ignore
    has_dotnet_http = False

# Optional Python HTTP fallback (requests)
try:  # pragma: no cover - not guaranteed in pyRevit runtime
    import requests  # type: ignore
    has_requests = True
except Exception:  # pragma: no cover
    requests = None  # type: ignore
    has_requests = False


LOGGER = logging.getLogger(__name__)
if not LOGGER.handlers:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))


def _this_folder() -> str:
    """Return this script's folder path."""
    return os.path.dirname(os.path.abspath(__file__))


def _extract_last_code_block(text: str) -> str:
    """Extract the last fenced code block from text.

    Supports ```python ...``` or ``` ... ``` fences.
    """
    if not text:
        return ""
    pattern = re.compile(r"```(?:python|py)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)
    matches = pattern.findall(text)
    if not matches:
        return ""
    return matches[-1].strip()


def _ensure_no_fences(code: str) -> str:
    """Remove surrounding code fences if present."""
    if not code:
        return ""
    return re.sub(r"^```[\w]*\n?|```$", "", code.strip(), flags=re.MULTILINE)


def _load_xaml_root(xaml_path: str) -> Any:
    """Load XAML and return the root WPF element (Window or control).

    Tries pyRevit's wpf.LoadComponent when available; otherwise falls back to
    System.Windows.Markup.XamlReader to support CPython where wpf may be None.
    """
    root = None
    # Prefer wpf.LoadComponent if available
    try:
        if 'wpf' in globals() and wpf is not None:
            try:
                try:
                    root = wpf.LoadComponent(xaml_path)  # type: ignore[attr-defined]
                except TypeError:
                    # Older pyRevit/pythonnet may require explicit args
                    root = wpf.LoadComponent(None, xaml_path)  # type: ignore[attr-defined]
            except Exception:
                root = None
        if root is None:
            # Fallback to XamlReader when wpf shim is unavailable (CPython)
            from System.IO import FileStream, FileMode, FileAccess  # type: ignore
            from System.Windows.Markup import XamlReader  # type: ignore
            fs = FileStream(xaml_path, FileMode.Open, FileAccess.Read)
            try:
                root = XamlReader.Load(fs)
            finally:
                try:
                    fs.Close()
                except Exception:
                    pass
        return root
    except Exception:
        # Last-resort fallback
        from System.IO import FileStream, FileMode, FileAccess  # type: ignore
        from System.Windows.Markup import XamlReader  # type: ignore
        fs = FileStream(xaml_path, FileMode.Open, FileAccess.Read)
        try:
            root = XamlReader.Load(fs)
        finally:
            try:
                fs.Close()
            except Exception:
                pass
        return root


class ChatWindow(object):
    """Controller that loads and shows the WPF Window from XAML.

    - Loads XAML (Window-root) and treats it as the main window.
    - Binds buttons and input controls for event handling.
    - Sends chat to FastAPI server and displays responses.
    - Executes generated code via pyRevit CLI.
    """

    def __init__(self) -> None:
        xaml_path = os.path.join(_this_folder(), "ChatWindow.xaml")

        # Load XAML root; if it's a Window, use it directly; otherwise host in a new Window
        root = _load_xaml_root(xaml_path)
        if root is None:
            # Create a bare window to avoid crashes; log the error
            LOGGER.error("Failed to load XAML at %s; creating empty window", xaml_path)
            self.win = Windows.Window()  # type: ignore[misc]
        elif isinstance(root, Windows.Window):  # type: ignore[arg-type]
            self.win = root
        else:
            self.win = Windows.Window()  # type: ignore[misc]
            self.win.Content = root

        # Attach to Revit main window
        try:
            wih = Interop.WindowInteropHelper(self.win)
            wih.Owner = AdWindows.ComponentManager.ApplicationWindow
        except Exception:
            pass

        # Bind named elements for later access, regardless of namescope
        from System.Windows import LogicalTreeHelper  # type: ignore

        def _find(name: str) -> Any:
            try:
                return LogicalTreeHelper.FindLogicalNode(self.win, name)
            except Exception:
                return None

        self.btnSend = _find("btnSend")
        self.btnNewChat = _find("btnNewChat")
        self.btnExecute = _find("btnExecute")
        self.CodeSnippetExpander = _find("CodeSnippetExpander")
        self.txtPrompt = _find("txtPrompt")
        self.panelConversation = _find("panelConversation")
        self.RepliesScrollViewer = _find("RepliesScrollViewer")
        self.txtCode = _find("txtCode")

        # Config
        self.server_url: str = os.getenv("RCA_SERVER_URL", "http://127.0.0.1:8000").rstrip("/")
        self.session_id: str = uuid.uuid4().hex

        # Optional .NET HttpClient
        self._http_client: Optional[Any] = HttpClient() if has_dotnet_http else None

        # Wire events (guard for missing names)
        if self.btnSend is not None:
            self.btnSend.Click += self.btnSend_Click
        if self.btnNewChat is not None:
            self.btnNewChat.Click += self.btnNewChat_Click
        if self.btnExecute is not None:
            self.btnExecute.Click += self.btnExecute_Click

        # Initial state
        if self.CodeSnippetExpander is not None:
            self.CodeSnippetExpander.IsExpanded = False
        try:
            if self.txtPrompt is not None:
                self.txtPrompt.Focus()
        except Exception:
            pass

    def show(self) -> None:
        """Show the underlying WPF window."""
        try:
            self.win.Show()
        except Exception:
            pass

    # --- UI helpers -----------------------------------------------------
    def _set_busy(self, busy: bool) -> None:
        """Enable/disable interactive controls."""
        try:
            self.btnSend.IsEnabled = not busy
            self.btnNewChat.IsEnabled = not busy
            self.txtPrompt.IsEnabled = not busy
        except Exception:
            pass

    def _append_text(self, text: str, *, role: str = "assistant") -> None:
        """Append a paragraph of text to the conversation panel."""
        from System.Windows.Controls import TextBlock, Border  # type: ignore
        from System.Windows import Thickness, CornerRadius, TextWrapping  # type: ignore
        from System.Windows.Media import Brushes  # type: ignore

        block = TextBlock()
        block.TextWrapping = TextWrapping.Wrap
        block.Text = text or ""
        border = Border()
        border.Padding = Thickness(8)
        border.Margin = Thickness(0, 4, 0, 4)
        border.BorderThickness = Thickness(1)
        border.CornerRadius = CornerRadius(4)
        border.BorderBrush = Brushes.LightGray
        if role == "user":
            border.Background = Brushes.White
        else:
            border.Background = Brushes.FloralWhite
        border.Child = block
        if getattr(self, "panelConversation", None) is not None:
            self.panelConversation.Children.Add(border)
        try:
            if getattr(self, "RepliesScrollViewer", None) is not None:
                self.RepliesScrollViewer.ScrollToEnd()
        except Exception:
            pass

    # --- Networking -----------------------------------------------------
    def _post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        """POST JSON using .NET HttpClient or requests; return JSON dict.

        Raises an Exception on non-200 responses or parsing errors.
        """
        body = json.dumps(payload)
        if self._http_client is not None:
            # .NET HttpClient path
            req = HttpRequestMessage(HttpMethod.Post, Uri(url))
            req.Content = StringContent(body, Encoding.UTF8, "application/json")
            resp = self._http_client.SendAsync(req).Result  # synchronous wait in worker thread
            resp.EnsureSuccessStatusCode()
            content = resp.Content.ReadAsStringAsync().Result
            return json.loads(content)

        if has_requests:
            r = requests.post(url, json=payload, timeout=60)
            r.raise_for_status()
            return r.json()

        # Last-resort minimal stdlib fallback
        from urllib import request as _urlreq  # type: ignore
        data = body.encode("utf-8")
        req = _urlreq.Request(url, data=data, headers={"Content-Type": "application/json"})
        with _urlreq.urlopen(req, timeout=60) as resp:  # nosec - controlled URL
            content = resp.read().decode("utf-8")
            return json.loads(content)

    # --- Event Handlers -------------------------------------------------
    def btnSend_Click(self, sender: Any, args: Any) -> None:
        """Handle SEND: send prompt to server in a background thread."""
        if getattr(self, "txtPrompt", None) is None:
            return
        prompt = (self.txtPrompt.Text or "").strip()
        if not prompt:
            return

        # Append user message immediately
        self._append_text(prompt, role="user")
        self._set_busy(True)

        def worker() -> None:
            try:
                url = f"{self.server_url}/chat"
                payload = {"message": prompt, "session_id": self.session_id}
                LOGGER.debug("POST %s payload=%s", url, payload)
                data = self._post_json(url, payload)
                reply: str = str(data.get("response", ""))
            except Exception as exc:  # Capture errors and marshal to UI
                LOGGER.exception("Chat request failed: %s", exc)
                reply = f"[error] {exc}"

            # Update UI on dispatcher thread
            def ui_update() -> None:
                self._append_text(reply, role="assistant")
                # Try to extract code for the expander
                code = _extract_last_code_block(reply)
                if code and getattr(self, "txtCode", None) is not None:
                    self.txtCode.Text = _ensure_no_fences(code)
                    if getattr(self, "CodeSnippetExpander", None) is not None:
                        self.CodeSnippetExpander.IsExpanded = True
                self._set_busy(False)
                try:
                    if getattr(self, "txtPrompt", None) is not None:
                        self.txtPrompt.Text = ""
                        self.txtPrompt.Focus()
                except Exception:
                    pass

            self.win.Dispatcher.Invoke(ui_update)

        threading.Thread(target=worker, name="rca-chat-send", daemon=True).start()

    def btnNewChat_Click(self, sender: Any, args: Any) -> None:
        """Reset the conversation and session state."""
        try:
            if getattr(self, "panelConversation", None) is not None:
                self.panelConversation.Children.Clear()
            if getattr(self, "txtCode", None) is not None:
                self.txtCode.Text = ""
            if getattr(self, "CodeSnippetExpander", None) is not None:
                self.CodeSnippetExpander.IsExpanded = False
        except Exception:
            pass
        self.session_id = uuid.uuid4().hex
        try:
            if getattr(self, "txtPrompt", None) is not None:
                self.txtPrompt.Text = ""
                self.txtPrompt.Focus()
        except Exception:
            pass

    def btnExecute_Click(self, sender: Any, args: Any) -> None:
        """Execute the last code block via pyRevit CLI in a worker thread."""
        code = (self.txtCode.Text or "").strip() if getattr(self, "txtCode", None) is not None else ""
        if not code:
            # Nothing to execute
            self._append_text("No code available to execute.")
            return

        self._set_busy(True)

        def worker() -> None:
            tmp_path = ""
            try:
                # Write code to a temporary file
                with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as tmp:
                    tmp.write(_ensure_no_fences(code))
                    tmp_path = tmp.name

                # Run via pyrevit CLI (must be on PATH)
                cmd = ["pyrevit", "run", tmp_path]
                LOGGER.info("Executing: %s", " ".join(cmd))
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                stdout = proc.stdout.strip() if proc.stdout else ""
                stderr = proc.stderr.strip() if proc.stderr else ""
                if proc.returncode != 0:
                    result = f"[execute error]\n{stderr or stdout or 'Unknown error'}"
                else:
                    result = stdout or "[no output]"
                if stderr and stdout:
                    result += f"\n[stderr]\n{stderr}"
            except FileNotFoundError as exc:
                LOGGER.exception("pyrevit CLI not found: %s", exc)
                result = "pyrevit CLI not found on PATH. Install pyRevit CLI or add it to PATH."
            except subprocess.TimeoutExpired:
                result = "[timeout] Execution exceeded time limit."
            except Exception as exc:
                LOGGER.exception("Execution failed: %s", exc)
                result = f"[execution error] {exc}"
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

            def ui_update() -> None:
                self._append_text(result, role="assistant")
                self._set_busy(False)

            self.win.Dispatcher.Invoke(ui_update)

        threading.Thread(target=worker, name="rca-exec", daemon=True).start()


def main() -> None:
    """Entry point to show the WPF chat window."""
    app = ChatWindow()
    app.show()


 


if __name__ == "__main__":  # pragma: no cover - runtime entrypoint
    main()

