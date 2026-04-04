"""Harness that prepends a conservative evidence-discipline banner."""
from __future__ import annotations

from ..schemas import BenchmarkCase, HarnessMetadata, HarnessResult
from .baseline_generator import BaselineFixtureHarness


class EvidenceGuardHarness(BaselineFixtureHarness):
    """Baseline plus an explicit internal evidence / review banner."""

    @property
    def harness_id(self) -> str:
        return "generator_with_evidence_banner"

    def run(self, case: BenchmarkCase) -> HarnessResult:
        base = super().run(case)
        banner = (
            "> **Internal drafting only.** Verify claims against PMID-backed sources "
            "before any clinical use.\n\n"
        )
        return HarnessResult(
            case_id=base.case_id,
            output_text=banner + base.output_text,
            structured_protocol=base.structured_protocol,
            metadata=HarnessMetadata(
                harness_id=self.harness_id,
                notes=base.metadata.notes
                + ["Prepended evidence-discipline banner for comparative scoring."],
            ),
        )
