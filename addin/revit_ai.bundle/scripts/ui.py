"""pyRevit Forms UI scaffold for chat dialog.

Provides minimal placeholders for chat prompt and response display.

TODO:
- Implement actual input loop and display logic (Prompt 2).
"""
from __future__ import annotations

# pyRevit imports (available inside Revit environment)
from pyrevit import forms  # type: ignore


def prompt_chat(session_id: str) -> str:
    """Display chat dialog and return user input.

    Args:
        session_id: Unique session identifier.

    Returns:
        The user input string.
    """
    # TODO: use forms.ask_for_string in a loop; return latest message.
    return ""


def display_response(response: str) -> None:
    """Display AI-generated response in dialog.

    Args:
        response: The text response to show.
    """
    # TODO: use forms.alert or custom form to display AI output.
    pass
