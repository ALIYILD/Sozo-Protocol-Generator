"""Abstract harness — implement `run` for each agent variant under test."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..schemas import BenchmarkCase, HarnessResult


class AgentHarness(ABC):
    """Internal lab interface; not a clinical agent."""

    @property
    @abstractmethod
    def harness_id(self) -> str: ...

    @abstractmethod
    def run(self, case: BenchmarkCase) -> HarnessResult:
        """Produce draft output for validator/evaluator pipeline."""
