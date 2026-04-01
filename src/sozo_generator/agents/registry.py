"""Agent registry — maps agent names to implementations."""
from __future__ import annotations
from typing import Optional
from .base import BaseAgent

_AGENTS: dict[str, type[BaseAgent]] = {}

def register_agent(cls: type[BaseAgent]) -> type[BaseAgent]:
    _AGENTS[cls.name] = cls
    return cls

def get_agent(name: str) -> Optional[BaseAgent]:
    cls = _AGENTS.get(name)
    return cls() if cls else None

def list_agents() -> list[str]:
    return list(_AGENTS.keys())
