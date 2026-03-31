"""Builder for safety sections."""
from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent


def build_safety_section(condition: ConditionSchema) -> SectionContent:
    safety_rows = []
    for note in condition.safety_notes:
        safety_rows.append([
            note.category.replace("_", " ").title(),
            note.severity.upper(),
            note.description,
            note.source or "SOZO clinical protocol",
        ])

    return SectionContent(
        section_id="safety",
        title="Side Effects, Contraindications & Safety Monitoring",
        content=(
            "All neuromodulation treatments must be preceded by a comprehensive safety screening. "
            "Adverse events must be documented at every session. Grade 3+ events require immediate "
            "discontinuation and escalation to the treating Doctor."
        ),
        tables=[{
            "headers": ["Category", "Severity", "Description", "Source"],
            "rows": safety_rows,
            "caption": "Safety notes and monitoring requirements",
        }] if safety_rows else [],
        review_flags=["Safety section incomplete — clinical review required"] if not condition.safety_notes else [],
        is_placeholder=not bool(condition.safety_notes),
    )
