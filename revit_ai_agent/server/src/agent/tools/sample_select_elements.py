"""Sample LangChain Tool: select elements by category (placeholder).

This is only a shape example; the real implementation should run inside Revit.
"""
from __future__ import annotations

from typing import Any, Dict

from langchain_core.tools import tool


@tool("select_elements_by_category")
def select_elements_by_category(category: str) -> Dict[str, Any]:
    """Return IDs of elements for a given Revit category (placeholder).

    Args:
        category: Revit BuiltInCategory name (e.g., OST_Walls).
    Returns:
        Dict with placeholder ids list.
    """
    # TODO: Implement via Revit API in-process; this placeholder echoes input.
    return {"ok": True, "data": {"category": str(category), "ids": []}}


def get_tools() -> list:
    """Factory for this module's tools.

    Returns a list of LangChain Tool objects that can be bound to models.
    """
    return [select_elements_by_category]
