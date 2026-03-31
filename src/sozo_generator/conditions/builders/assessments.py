"""Builder for assessment tool sections."""
from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent


def build_assessments_section(condition: ConditionSchema) -> SectionContent:
    scale_rows = []
    for tool in condition.assessment_tools:
        scale_rows.append([
            tool.abbreviation,
            tool.name,
            ", ".join(tool.domains),
            tool.timing,
            tool.evidence_pmid or "—",
        ])

    baseline_content = "\n".join(f"• {m}" for m in condition.baseline_measures) if condition.baseline_measures else ""
    followup_content = "\n".join(f"• {m}" for m in condition.followup_measures) if condition.followup_measures else ""

    return SectionContent(
        section_id="assessments",
        title="Assessment Framework & Validated Scales",
        content=(
            f"The following validated assessment instruments are recommended for baseline "
            f"evaluation, treatment monitoring, and outcome measurement in {condition.display_name}."
        ),
        tables=[{
            "headers": ["Abbreviation", "Full Scale Name", "Domains Assessed", "Timing", "Reference (PMID)"],
            "rows": scale_rows,
            "caption": "Validated assessment scales for this condition",
        }] if scale_rows else [],
        subsections=[
            SectionContent(
                section_id="baseline_measures",
                title="Baseline Measures",
                content=baseline_content or "[REVIEW REQUIRED: Baseline measures not defined]",
                is_placeholder=not bool(condition.baseline_measures),
            ),
            SectionContent(
                section_id="followup_measures",
                title="Follow-Up & Outcome Measures",
                content=followup_content or "[REVIEW REQUIRED: Follow-up measures not defined]",
                is_placeholder=not bool(condition.followup_measures),
            ),
        ],
        review_flags=["No validated scales defined"] if not condition.assessment_tools else [],
    )
