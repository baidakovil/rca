"""Database models (SQLModel) scaffold.

This file declares placeholder models for future use.

TODO:
- Flesh out SQLModel entities and relationships (Prompt 2+).
"""
from __future__ import annotations

from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    """A simple project model.

    TODO: Add session and history fields in Prompt 2.
    """

    id: int = Field(default=None, primary_key=True)  # type: ignore[assignment]
    name: str
