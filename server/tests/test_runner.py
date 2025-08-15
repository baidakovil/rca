"""Unit tests for subprocess runner."""
from __future__ import annotations

import sys
from pathlib import Path

# Add the server directory to the Python path
server_path = Path(__file__).parent.parent
if str(server_path) not in sys.path:
    sys.path.insert(0, str(server_path))

from src.executor.runner import run_script  # Now src is in the path


def test_runner_stdout() -> None:
    out = run_script("print('ok')")
    assert out.strip().startswith("ok")


def test_runner_stderr_and_nonzero() -> None:
    # This will raise NameError; stderr should be returned if no stdout
    out = run_script("raise NameError('boom')")
    assert "boom" in out


def test_runner_timeout() -> None:
    # Busy loop to exceed tiny timeout and trigger timeout handling
    out = run_script("import time; time.sleep(2)", timeout=0)
    assert "timeout" in out.lower()
