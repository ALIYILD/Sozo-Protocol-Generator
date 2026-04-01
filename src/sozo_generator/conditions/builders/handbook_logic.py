"""Builder for clinical handbook sections."""
from __future__ import annotations

from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent


PATIENT_JOURNEY_STAGES = {
    "stage_1": "Stage 1: Appointment Scheduling & Pre-Screening",
    "stage_2": "Stage 2: Informed Consent",
    "stage_3": "Stage 3: Psychological Intake & Baseline Assessment",
    "stage_4": "Stage 4: Clinical Examination & Phenotyping",
    "stage_5": "Stage 5: Treatment Protocol Selection",
    "stage_6": "Stage 6: Treatment Delivery & Session Monitoring",
    "stage_7": "Stage 7: Response Tracking & Adjustment",
    "stage_8": "Stage 8: Long-Term Follow-Up & Maintenance",
}

STAGE_DEFAULTS = {
    "stage_1": "Screen for basic eligibility. Collect demographic information. Schedule comprehensive assessment appointment. Confirm absence of absolute contraindications.",
    "stage_2": "Obtain written informed consent for neuromodulation. Provide off-label disclosure for TPS if applicable. Document consent in patient record. Clinician and patient signatures required.",
    "stage_3": "Conduct structured psychological intake. Administer SOZO PRS baseline ratings. Document chief complaints, psychiatric history, and functional limitations. Establish baseline measures.",
    "stage_4": "Complete condition-specific clinical examination. Administer validated assessment scales. Determine clinical phenotype. Document findings for protocol selection.",
    "stage_5": "Apply phenotype-to-protocol algorithm. Select tDCS montage, TPS target if indicated, and adjunct modalities. Document rationale. Obtain Doctor sign-off.",
    "stage_6": "Deliver selected protocols per session plan. Monitor for adverse events throughout session. Document session details. Adjust if intolerance occurs.",
    "stage_7": "Administer outcome measures at Week 4 and Week 8–10. Classify as Responder/Partial/Non-Responder. Adjust protocol or initiate Level 5 FNON pathway as indicated.",
    "stage_8": "Plan maintenance protocol for responders. Set follow-up schedule (monthly/quarterly). Document long-term outcome tracking. Reassess at significant change in clinical status.",
}


def build_handbook_sections(condition: ConditionSchema) -> list[SectionContent]:
    """Build all 8 stages of the patient journey for the clinical handbook."""
    sections = []
    for stage_key, stage_title in PATIENT_JOURNEY_STAGES.items():
        custom_content = condition.patient_journey_notes.get(stage_key, "")
        default_content = STAGE_DEFAULTS.get(stage_key, "")
        content = custom_content if custom_content else default_content
        sections.append(SectionContent(
            section_id=stage_key,
            title=stage_title,
            content=content,
        ))

    # Add clinical tips
    if condition.clinical_tips:
        tips_content = "\n".join(f"CLINICAL TIP: {tip}" for tip in condition.clinical_tips)
        sections.append(SectionContent(
            section_id="clinical_tips",
            title="Clinical Tips & Governance Rules",
            content=tips_content,
        ))

    return sections
