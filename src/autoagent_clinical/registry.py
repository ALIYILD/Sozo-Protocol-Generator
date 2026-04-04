"""Harness variant registry and metadata for benchmark comparisons."""
from __future__ import annotations

from typing import Callable

from .harnesses import (
    AgentHarness,
    BaselineFixtureHarness,
    EvidenceGuardHarness,
    GenerationServiceHarness,
    QAStubHarness,
)

HarnessFactory = Callable[[], AgentHarness]

_REGISTRY: dict[str, HarnessFactory] = {
    "baseline_fixture": BaselineFixtureHarness,
    "generator_with_qa_stub": QAStubHarness,
    "generator_with_evidence_banner": EvidenceGuardHarness,
    "generation_service": GenerationServiceHarness,
}


def register_harness(harness_id: str, factory: HarnessFactory) -> None:
    """Register a custom harness for experiments/meta-agent loops."""
    _REGISTRY[harness_id] = factory


def get_harness(harness_id: str) -> AgentHarness:
    if harness_id not in _REGISTRY:
        known = ", ".join(sorted(_REGISTRY))
        raise KeyError(f"Unknown harness {harness_id!r}. Known: {known}")
    return _REGISTRY[harness_id]()


def list_harnesses() -> list[str]:
    return sorted(_REGISTRY)
