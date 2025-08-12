"""Unit tests for subprocess runner."""
from __future__ import annotations

from server.src.executor.runner import run_script


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
