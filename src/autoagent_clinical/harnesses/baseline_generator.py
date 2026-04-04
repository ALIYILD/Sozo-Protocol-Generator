"""Baseline: emit fixture markdown + optional structured protocol from benchmark case."""
from __future__ import annotations

from ..schemas import BenchmarkCase, HarnessMetadata, HarnessResult
from .base_harness import AgentHarness


class BaselineFixtureHarness(AgentHarness):
    """Passes through curated benchmark fixtures (deterministic MVP)."""

    @property
    def harness_id(self) -> str:
        return "baseline_fixture"

    def run(self, case: BenchmarkCase) -> HarnessResult:
        text = case.fixture_markdown.strip()
        if case.internal_note and case.internal_note not in text:
            text = f"<!-- {case.internal_note} -->\n\n{text}"
        return HarnessResult(
            case_id=case.id,
            output_text=text,
            structured_protocol=case.optional_protocol_json,
            metadata=HarnessMetadata(
                harness_id=self.harness_id,
                notes=["Fixture passthrough — no live LLM call."],
            ),
        )
