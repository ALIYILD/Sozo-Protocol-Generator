"""Builder for clinical overview and pathophysiology sections."""
from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent
from ...core.enums import ConfidenceLabel


def build_overview_section(condition: ConditionSchema) -> SectionContent:
    """Build the clinical overview section."""
    return SectionContent(
        section_id="clinical_overview",
        title="Condition Overview",
        content=condition.overview,
        confidence_label=ConfidenceLabel.HIGH.value if condition.overview else None,
        is_placeholder=not bool(condition.overview),
        evidence_pmids=[ref.get("pmid", "") for ref in condition.references[:5] if ref.get("pmid")],
    )


def build_pathophysiology_section(condition: ConditionSchema) -> SectionContent:
    """Build pathophysiology section."""
    return SectionContent(
        section_id="pathophysiology",
        title="Pathophysiology, Symptoms & Standard Guidelines",
        content=condition.pathophysiology,
        is_placeholder=not bool(condition.pathophysiology),
        subsections=[
            SectionContent(
                section_id="core_symptoms",
                title="Core Symptoms",
                content="\n".join(f"• {s}" for s in condition.core_symptoms) if condition.core_symptoms else "[REVIEW REQUIRED: No core symptoms defined]",
                is_placeholder=not bool(condition.core_symptoms),
            ),
            SectionContent(
                section_id="non_motor_symptoms",
                title="Non-Motor Symptoms",
                content="\n".join(f"• {s}" for s in condition.non_motor_symptoms) if condition.non_motor_symptoms else "",
            ),
        ],
    )
