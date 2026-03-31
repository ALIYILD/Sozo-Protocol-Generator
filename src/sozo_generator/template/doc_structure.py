"""
Document structure helpers — builds DocumentSpec objects from condition schemas
and document type + tier specifications.
"""
import logging
from datetime import datetime
from pathlib import Path

from ..schemas.condition import ConditionSchema
from ..schemas.documents import DocumentSpec, SectionContent
from ..core.enums import DocumentType, Tier
from ..core.utils import current_date_str, current_month_year
from .gold_standard import get_required_sections, requires_tables, is_partners_only

logger = logging.getLogger(__name__)


# Document titles by type
DOCUMENT_TITLES = {
    DocumentType.CLINICAL_EXAM: "Clinical Examination Form",
    DocumentType.PHENOTYPE_CLASSIFICATION: "Phenotype Classification & Protocol Selection",
    DocumentType.RESPONDER_TRACKING: "Responder Tracking & Response Classification",
    DocumentType.PSYCH_INTAKE: "Psychological Intake & Baseline Assessment",
    DocumentType.NETWORK_ASSESSMENT: "6-Network Bedside Assessment (FNON)",
    DocumentType.HANDBOOK: "Clinical Practitioner Handbook",
    DocumentType.ALL_IN_ONE_PROTOCOL: "All-in-One Neuromodulation Protocol Reference",
    DocumentType.EVIDENCE_BASED_PROTOCOL: "Evidence-Based Neuromodulation Protocol",
}

# Audience labels by tier
AUDIENCE_LABELS = {
    Tier.FELLOW: "SOZO Fellow Clinicians — Restricted Circulation",
    Tier.PARTNERS: "SOZO Partners & Senior Clinicians — Confidential",
    Tier.BOTH: "SOZO Clinical Staff — Internal Use",
}

# Output filename templates
FILENAME_TEMPLATES = {
    DocumentType.CLINICAL_EXAM: "{slug}_clinical_exam_{tier}.docx",
    DocumentType.PHENOTYPE_CLASSIFICATION: "{slug}_phenotype_classification_{tier}.docx",
    DocumentType.RESPONDER_TRACKING: "{slug}_responder_tracking_{tier}.docx",
    DocumentType.PSYCH_INTAKE: "{slug}_psych_intake_{tier}.docx",
    DocumentType.NETWORK_ASSESSMENT: "{slug}_network_assessment_partners.docx",
    DocumentType.HANDBOOK: "{slug}_handbook_{tier}.docx",
    DocumentType.ALL_IN_ONE_PROTOCOL: "{slug}_all_in_one_protocol_{tier}.docx",
    DocumentType.EVIDENCE_BASED_PROTOCOL: "{slug}_evidence_based_protocol_{tier}.docx",
}


def build_document_spec(
    condition: ConditionSchema,
    doc_type: DocumentType,
    tier: Tier,
    version: str = "1.0",
) -> DocumentSpec:
    """
    Build a DocumentSpec scaffold from a condition schema and document specification.
    Sections are scaffolded from the gold_standard manifest.
    Content is populated from the condition schema.

    Args:
        condition: The ConditionSchema for this condition.
        doc_type: The DocumentType to generate.
        tier: The Tier (Fellow / Partners) to generate for.
        version: Document version string.

    Returns:
        DocumentSpec ready for renderer consumption.
    """
    if is_partners_only(doc_type) and tier != Tier.PARTNERS:
        logger.warning(f"{doc_type.value} is Partners-only. Generating as Partners tier.")
        tier = Tier.PARTNERS

    title_base = DOCUMENT_TITLES.get(doc_type, "Clinical Document")
    title = f"{condition.display_name} — {title_base}"

    tier_label = "Partners Edition" if tier == Tier.PARTNERS else "Fellow Edition"
    subtitle = f"{tier_label} | {current_month_year()} | Version {version}"

    filename_tmpl = FILENAME_TEMPLATES.get(doc_type, "{slug}_{doc_type}_{tier}.docx")
    output_filename = filename_tmpl.format(
        slug=condition.slug,
        tier=tier.value,
        doc_type=doc_type.value,
    )

    required_section_ids = get_required_sections(doc_type, tier)

    # Build placeholder sections for all required sections
    sections = _build_placeholder_sections(required_section_ids, condition, doc_type, tier)

    spec = DocumentSpec(
        document_type=doc_type,
        tier=tier,
        condition_slug=condition.slug,
        condition_name=condition.display_name,
        title=title,
        subtitle=subtitle,
        version=version,
        date_label=current_date_str(),
        audience=AUDIENCE_LABELS.get(tier, ""),
        confidentiality_mark="CONFIDENTIAL — SOZO Brain Center",
        sections=sections,
        references=condition.references,
        review_flags=condition.review_flags,
        output_filename=output_filename,
    )

    logger.debug(
        f"Built DocumentSpec: {spec.title} ({len(sections)} sections)"
    )
    return spec


def _build_placeholder_sections(
    section_ids: list[str],
    condition: ConditionSchema,
    doc_type: DocumentType,
    tier: Tier,
) -> list[SectionContent]:
    """Build placeholder SectionContent objects for all required sections."""
    sections = []
    for section_id in section_ids:
        title = _section_id_to_title(section_id)
        content = _get_section_content_hint(section_id, condition, tier)
        sections.append(SectionContent(
            section_id=section_id,
            title=title,
            content=content,
            is_placeholder=not bool(content),
        ))
    return sections


def _section_id_to_title(section_id: str) -> str:
    """Convert section_id back to a human-readable title."""
    replacements = {
        "document_control": "Document Control & Version History",
        "patient_info": "Patient Information",
        "fnon_network_assessment": "FNON 6-Network Bedside Assessment",
        "fnon_core_principle": "FNON Core Principle",
        "motor_examination": "Motor Examination",
        "standard_neurological_examination": "Standard Neurological Examination",
        "cognitive_screening": "Cognitive Screening",
        "mood_behavioral_screening": "Mood & Behavioural Screening",
        "phenotype_identification": "Phenotype Identification",
        "network_hypothesis": "Network Hypothesis",
        "clinical_summary": "Clinical Summary & Recommendations",
        "inclusion_exclusion": "Inclusion & Exclusion Criteria",
        "clinical_overview": "Condition Overview",
        "pathophysiology": "Pathophysiology & Symptoms",
        "key_brain_structures": "Key Brain Structures",
        "key_brain_structures_networks": "Key Brain Structures & Networks",
        "clinical_phenotypes": "Clinical Phenotypes",
        "clinical_phenotypes_networks": "Clinical Phenotypes & Network Profiles",
        "symptom_brain_mapping": "Symptom–Brain Region Mapping",
        "symptom_network_modality_mapping": "Symptom–Network–Modality Mapping",
        "fnon_application": "FNON Framework Application",
        "tdcs_protocols": "tDCS Protocols",
        "tps_protocols": "TPS Protocols (NEUROLITH — OFF-LABEL)",
        "tavns_ces_protocols": "taVNS & CES Protocols",
        "combination_protocols": "Combination Neuromodulation Protocols",
        "side_effects_monitoring": "Side Effects & Safety Monitoring",
        "followup_decision_making": "Follow-Up & Clinical Decision Making",
        "governance_rules": "Governance Rules & Compliance",
        "references": "References & Evidence Sources",
    }
    if section_id in replacements:
        return replacements[section_id]
    # Generic: convert underscores to title case
    return section_id.replace("_", " ").title()


def _get_section_content_hint(
    section_id: str,
    condition: ConditionSchema,
    tier: Tier,
) -> str:
    """Return pre-populated content for sections that map directly to condition fields."""
    if section_id == "clinical_overview":
        return condition.overview
    if section_id == "pathophysiology":
        return condition.pathophysiology
    if section_id in ("fnon_application", "fnon_core_principle"):
        return condition.fnon_rationale
    if section_id == "governance_rules":
        return "\n".join(f"• {r}" for r in condition.governance_rules)
    if section_id == "references":
        return ""  # rendered separately
    return ""  # placeholder — will be filled by builders


def get_document_output_path(
    output_root: Path,
    condition_slug: str,
    doc_type: DocumentType,
    tier: Tier,
) -> Path:
    """Build the full output path for a generated document."""
    filename_tmpl = FILENAME_TEMPLATES.get(doc_type, "{slug}_{doc_type}_{tier}.docx")
    filename = filename_tmpl.format(
        slug=condition_slug,
        tier=tier.value,
        doc_type=doc_type.value,
    )
    return output_root / condition_slug / filename
