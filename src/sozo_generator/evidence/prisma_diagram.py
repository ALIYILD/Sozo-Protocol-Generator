"""
PRISMA 2020 flow diagram generator — auto-generates PRISMA-compliant
flow diagrams from PipelineTracker data.

Outputs:
- Text-based diagram (for terminal/log display)
- Structured data (for rendering in DOCX or HTML)
- Mermaid diagram syntax (for web rendering)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from .pipeline_tracker import PipelineTracker, PRISMAFlowCounts

logger = logging.getLogger(__name__)


@dataclass
class PRISMADiagramData:
    """Structured data for rendering a PRISMA flow diagram."""

    condition_slug: str = ""
    condition_name: str = ""
    counts: Optional[PRISMAFlowCounts] = None

    # Boxes
    identification_box: str = ""
    dedup_box: str = ""
    screening_box: str = ""
    eligibility_box: str = ""
    included_box: str = ""

    # Side boxes (exclusion reasons)
    screening_exclusions: list[str] = field(default_factory=list)
    eligibility_exclusions: list[str] = field(default_factory=list)

    # Renderings
    text_diagram: str = ""
    mermaid_diagram: str = ""


class PRISMADiagramGenerator:
    """Generates PRISMA 2020 flow diagrams from pipeline tracker data."""

    def generate(
        self,
        tracker: PipelineTracker,
        condition_slug: str = "",
        condition_name: str = "",
    ) -> PRISMADiagramData:
        """Generate PRISMA diagram data from a pipeline tracker."""
        counts = tracker.get_prisma_counts()

        diagram = PRISMADiagramData(
            condition_slug=condition_slug,
            condition_name=condition_name,
            counts=counts,
        )

        # Build box labels
        diagram.identification_box = self._identification_text(counts)
        diagram.dedup_box = self._dedup_text(counts)
        diagram.screening_box = self._screening_text(counts)
        diagram.eligibility_box = self._eligibility_text(counts)
        diagram.included_box = self._included_text(counts)

        # Exclusion side boxes
        diagram.screening_exclusions = [
            f"{reason}: {count}"
            for reason, count in sorted(
                counts.screening_exclusion_reasons.items(),
                key=lambda x: x[1], reverse=True,
            )[:5]
        ]
        diagram.eligibility_exclusions = [
            f"{reason}: {count}"
            for reason, count in sorted(
                counts.eligibility_exclusion_reasons.items(),
                key=lambda x: x[1], reverse=True,
            )[:5]
        ]

        # Generate text rendering
        diagram.text_diagram = self._render_text(diagram)

        # Generate Mermaid rendering
        diagram.mermaid_diagram = self._render_mermaid(diagram, counts)

        return diagram

    @staticmethod
    def _identification_text(counts: PRISMAFlowCounts) -> str:
        sources = ", ".join(
            f"{source}: {n}" for source, n in counts.records_by_source.items()
        )
        return (
            f"Records identified through database searching\n"
            f"(n = {counts.records_identified})\n"
            f"Sources: {sources}"
        )

    @staticmethod
    def _dedup_text(counts: PRISMAFlowCounts) -> str:
        return (
            f"Records after duplicates removed\n"
            f"(n = {counts.records_after_dedup})\n"
            f"Duplicates removed: {counts.duplicates_removed}"
        )

    @staticmethod
    def _screening_text(counts: PRISMAFlowCounts) -> str:
        return (
            f"Records screened\n"
            f"(n = {counts.records_screened})\n"
            f"Excluded: {counts.records_excluded_screening}"
        )

    @staticmethod
    def _eligibility_text(counts: PRISMAFlowCounts) -> str:
        return (
            f"Full-text articles assessed for eligibility\n"
            f"(n = {counts.reports_assessed})\n"
            f"Excluded: {counts.reports_excluded_eligibility}"
        )

    @staticmethod
    def _included_text(counts: PRISMAFlowCounts) -> str:
        return (
            f"Studies included in evidence synthesis\n"
            f"(n = {counts.studies_included})\n"
            f"Parameters extracted: {counts.studies_extracted}\n"
            f"Evidence scored: {counts.studies_scored}\n"
            f"Grounded to protocol: {counts.studies_grounded}"
        )

    def _render_text(self, diagram: PRISMADiagramData) -> str:
        """Render a text-based PRISMA flow diagram."""
        width = 60
        hr = "=" * width

        lines = [
            hr,
            f"PRISMA 2020 Flow Diagram — {diagram.condition_name or diagram.condition_slug}",
            hr,
            "",
            "IDENTIFICATION",
            self._box(diagram.identification_box, width),
            "      │",
            "      ▼",
            "DEDUPLICATION",
            self._box(diagram.dedup_box, width),
            "      │",
            "      ▼",
            "SCREENING",
            self._box(diagram.screening_box, width),
        ]

        if diagram.screening_exclusions:
            lines.append(f"      │{'':>10}→  Excluded:")
            for reason in diagram.screening_exclusions:
                lines.append(f"      │{'':>14}{reason}")
        lines.extend([
            "      │",
            "      ▼",
            "ELIGIBILITY",
            self._box(diagram.eligibility_box, width),
        ])

        if diagram.eligibility_exclusions:
            lines.append(f"      │{'':>10}→  Excluded:")
            for reason in diagram.eligibility_exclusions:
                lines.append(f"      │{'':>14}{reason}")
        lines.extend([
            "      │",
            "      ▼",
            "INCLUDED",
            self._box(diagram.included_box, width),
            "",
            hr,
        ])

        return "\n".join(lines)

    @staticmethod
    def _box(text: str, width: int = 60) -> str:
        """Wrap text in an ASCII box."""
        lines_in = text.split("\n")
        inner_width = width - 4
        box_lines = ["┌" + "─" * (width - 2) + "┐"]
        for line in lines_in:
            box_lines.append(f"│ {line:<{inner_width}} │")
        box_lines.append("└" + "─" * (width - 2) + "┘")
        return "\n".join(box_lines)

    @staticmethod
    def _render_mermaid(
        diagram: PRISMADiagramData,
        counts: PRISMAFlowCounts,
    ) -> str:
        """Render a Mermaid flowchart for web display."""
        sources_str = ", ".join(
            f"{s}: {n}" for s, n in counts.records_by_source.items()
        )

        return f"""graph TD
    ID["Records identified<br/>(n={counts.records_identified})<br/>{sources_str}"]
    DD["Records after dedup<br/>(n={counts.records_after_dedup})"]
    SC["Records screened<br/>(n={counts.records_screened})"]
    EL["Eligibility assessed<br/>(n={counts.reports_assessed})"]
    IN["Studies included<br/>(n={counts.studies_included})"]

    EX_DD["Duplicates removed<br/>(n={counts.duplicates_removed})"]
    EX_SC["Excluded at screening<br/>(n={counts.records_excluded_screening})"]
    EX_EL["Excluded at eligibility<br/>(n={counts.reports_excluded_eligibility})"]

    ID --> DD
    DD --> SC
    SC --> EL
    EL --> IN

    DD -.-> EX_DD
    SC -.-> EX_SC
    EL -.-> EX_EL

    style ID fill:#e1f5fe
    style IN fill:#c8e6c9
    style EX_DD fill:#ffcdd2
    style EX_SC fill:#ffcdd2
    style EX_EL fill:#ffcdd2"""
