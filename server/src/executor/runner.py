"""Execution runner.

Write a Python script to a temporary file and execute it via subprocess,
capturing stdout/stderr. Minimal and side-effect free by default.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile


def run_script(script: str, timeout: int = 30) -> str:
    """Run a given script and return its output.

    Args:
        script: The script content to execute.
        timeout: Maximum execution time in seconds.

    Returns:
        Captured output as a string.
    """
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as tmp:
            tmp.write(script)
            tmp.flush()
            tmp_path = tmp.name

        # Execute the script with the current Python interpreter.
        proc = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""

        if proc.returncode != 0 and not stdout:
            # If failed and no stdout, return stderr for visibility.
            return stderr.strip()

        # Otherwise, prefer stdout and append stderr if useful.
        output = stdout.strip()
        if stderr.strip():
            output = f"{output}\n[stderr]\n{stderr.strip()}" if output else stderr.strip()
        return output

    except subprocess.TimeoutExpired:
        return "[timeout] Script execution exceeded the configured timeout."
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                # Best-effort cleanup.
                pass
