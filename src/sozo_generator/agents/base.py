"""Base agent interface — all SOZO agents inherit from this."""
from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)

@dataclass
class AgentResult:
    """Result from an agent execution."""
    success: bool = False
    artifacts: list[dict] = field(default_factory=list)  # [{type, path, description}]
    output_data: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    error: str = ""
    log_lines: list[str] = field(default_factory=list)

class BaseAgent(ABC):
    """Abstract base for all SOZO document agents."""

    name: str = "base"
    role: str = ""
    requires_human_review: bool = False
    max_attempts: int = 2

    def __init__(self):
        self.logger = logging.getLogger(f"agent.{self.name}")

    @abstractmethod
    def execute(self, input_data: dict, workspace_path: str, **kwargs) -> AgentResult:
        """Run the agent's task. Returns AgentResult."""
        ...

    def _log(self, workspace_path: str, message: str) -> None:
        """Write to agent log in workspace."""
        from ..jobs.workspace import JobWorkspace
        # Simple file append
        from pathlib import Path
        log_file = Path(workspace_path) / "logs" / f"{self.name}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        with open(log_file, "a") as f:
            f.write(f"[{ts}] {message}\n")
