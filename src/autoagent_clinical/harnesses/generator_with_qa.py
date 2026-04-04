"""Harness variant that appends a minimal post-hoc QA stub (simulated pipeline)."""
from __future__ import annotations

from ..schemas import BenchmarkCase, HarnessMetadata, HarnessResult
from .baseline_generator import BaselineFixtureHarness


class QAStubHarness(BaselineFixtureHarness):
    """Baseline fixture plus an internal QA appendix for pipeline comparison experiments."""

    @property
    def harness_id(self) -> str:
        return "generator_with_qa_stub"

    def run(self, case: BenchmarkCase) -> HarnessResult:
        base = super().run(case)
        appendix = (
            "\n\n## Internal QA appendix\n\n"
            "- Positioning: for internal drafting and clinician review only.\n"
            "- Spot-check: modality, montage, citations, and audience alignment.\n"
        )
        return HarnessResult(
            case_id=base.case_id,
            output_text=base.output_text + appendix,
            structured_protocol=base.structured_protocol,
            metadata=HarnessMetadata(
                harness_id=self.harness_id,
                notes=base.metadata.notes
                + ["Appended deterministic QA stub (not a full QA engine run)."],
            ),
        )
