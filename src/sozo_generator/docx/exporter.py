"""High-level document export coordinator."""
import logging
from pathlib import Path
from ..schemas.condition import ConditionSchema
from ..schemas.documents import DocumentSpec, SectionContent
from ..core.enums import DocumentType, Tier
from ..core.utils import ensure_dir, current_month_year
from ..conditions.builders.clinical_overview import build_overview_section, build_pathophysiology_section
from ..conditions.builders.anatomy import build_anatomy_section
from ..conditions.builders.networks import build_networks_section, build_symptom_network_section
from ..conditions.builders.phenotype import build_phenotype_section
from ..conditions.builders.assessments import build_assessments_section
from ..conditions.builders.protocols import build_protocols_section, build_inclusion_exclusion_section
from ..conditions.builders.safety import build_safety_section
from ..conditions.builders.responder_logic import build_responder_section
from ..conditions.builders.handbook_logic import build_handbook_sections
from ..conditions.builders.common import build_references_section, build_evidence_gaps_section
from .renderer import DocumentRenderer

logger = logging.getLogger(__name__)


class DocumentExporter:
    """Builds and exports all documents for a condition."""

    def __init__(
        self,
        output_dir: str = "outputs/documents/",
        output_base: str = None,
        with_visuals: bool = True,
    ):
        # Support both 'output_dir' and legacy 'output_base' param
        base = output_base or output_dir
        self.output_base = Path(base)
        self.renderer = DocumentRenderer(output_dir=base)
        self.with_visuals = with_visuals

    def export_condition(
        self,
        condition: ConditionSchema,
        tiers=None,
        doc_types=None,
        with_visuals: bool = True,
        visuals_dir: str = "outputs/visuals/",
    ) -> dict:
        """Export all documents for a condition. Returns dict of doc_key -> output path."""
        if tiers is None:
            tiers = [Tier.FELLOW, Tier.PARTNERS]
        if doc_types is None:
            doc_types = list(DocumentType)

        outputs = {}
        visuals_path = Path(visuals_dir)

        for tier in tiers:
            for doc_type in doc_types:
                if doc_type == DocumentType.NETWORK_ASSESSMENT and tier == Tier.FELLOW:
                    continue
                try:
                    spec = self._build_spec(condition, doc_type, tier)
                    out_path = self.renderer.render(spec)
                    key = f"{tier.value}_{doc_type.value}"
                    outputs[key] = out_path
                    logger.info(f"Exported: {key} -> {out_path.name}")
                except Exception as e:
                    logger.error(
                        f"Failed to render {tier.value}/{doc_type.value} for {condition.slug}: {e}",
                        exc_info=True,
                    )
        return outputs

    def export_all(self, condition: ConditionSchema, tier: Tier = Tier.BOTH) -> list:
        """Generate all documents for a condition in the specified tier(s). Returns list of paths."""
        output_paths = []
        tiers = [Tier.FELLOW, Tier.PARTNERS] if tier == Tier.BOTH else [tier]

        for t in tiers:
            for doc_type in DocumentType:
                if doc_type == DocumentType.NETWORK_ASSESSMENT and t == Tier.FELLOW:
                    continue
                try:
                    spec = self._build_spec(condition, doc_type, t)
                    path = self._get_output_path(condition.slug, t, doc_type)
                    rendered = self.renderer.render(spec, path)
                    output_paths.append(rendered)
                except Exception as e:
                    logger.error(
                        f"Failed to render {doc_type.value} ({t.value}): {e}", exc_info=True
                    )
        return output_paths

    def export_single(self, condition: ConditionSchema, doc_type: DocumentType, tier: Tier) -> Path:
        """Export a single document."""
        spec = self._build_spec(condition, doc_type, tier)
        path = self._get_output_path(condition.slug, tier, doc_type)
        return self.renderer.render(spec, path)

    def _build_spec(self, condition: ConditionSchema, doc_type: DocumentType, tier: Tier) -> DocumentSpec:
        """Build a DocumentSpec for one document type."""
        title, sections = self._get_content(condition, doc_type, tier)
        return DocumentSpec(
            document_type=doc_type,
            tier=tier,
            condition_slug=condition.slug,
            condition_name=condition.display_name,
            title=title,
            version=condition.version,
            date_label=current_month_year(),
            audience="Fellow clinician" if tier == Tier.FELLOW else "Partner clinician",
            confidentiality_mark="CONFIDENTIAL",
            sections=sections,
            references=condition.references,
            review_flags=condition.review_flags,
            output_filename=self._get_output_path(condition.slug, tier, doc_type).name,
        )

    def _get_content(self, condition: ConditionSchema, doc_type: DocumentType, tier: Tier):
        """Return (title, sections) for a document type."""
        condition_name = condition.display_name

        if doc_type == DocumentType.EVIDENCE_BASED_PROTOCOL:
            title = f"SOZO Evidence-Based Protocol \u2014 {condition_name}"
            sections = [
                self._build_document_control(condition, tier),
                build_inclusion_exclusion_section(condition),
                build_overview_section(condition),
                build_pathophysiology_section(condition),
                build_anatomy_section(condition),
            ]
            if tier == Tier.PARTNERS:
                sections.append(build_networks_section(condition))
                sections.append(build_symptom_network_section(condition))
            sections += [
                build_phenotype_section(condition),
                build_protocols_section(condition),
                build_safety_section(condition),
                SectionContent(
                    section_id="followup",
                    title="Follow-Up Assessments and Decision-Making",
                    content=(
                        "Follow-up assessments are conducted at Week 4 and Week 8\u201310. "
                        "Response classification uses SOZO criteria. "
                        "See Responder Tracking document for full decision pathway."
                    ),
                ),
                build_references_section(condition),
                build_evidence_gaps_section(condition),
            ]

        elif doc_type == DocumentType.ALL_IN_ONE_PROTOCOL:
            title = f"{'FNON ' if tier == Tier.PARTNERS else ''}All-in-One Protocol \u2014 {condition_name}"
            sections = [
                self._build_document_control(condition, tier),
                build_protocols_section(condition),
                build_inclusion_exclusion_section(condition),
                build_safety_section(condition),
                build_references_section(condition),
            ]

        elif doc_type == DocumentType.HANDBOOK:
            title = f"SOZO {'FNON ' if tier == Tier.PARTNERS else ''}Clinical Handbook \u2014 {condition_name}"
            handbook_sections = build_handbook_sections(condition)
            sections = (
                [self._build_document_control(condition, tier), self._build_handbook_intro(condition, tier)]
                + handbook_sections
                + [build_references_section(condition)]
            )

        elif doc_type == DocumentType.CLINICAL_EXAM:
            title = f"Clinical Examination Checklist \u2014 {condition_name}"
            sections = [
                self._build_document_control(condition, tier),
                self._build_patient_info_section(),
                build_assessments_section(condition),
                build_phenotype_section(condition),
            ]
            if tier == Tier.PARTNERS:
                sections.insert(2, build_networks_section(condition))

        elif doc_type == DocumentType.PHENOTYPE_CLASSIFICATION:
            title = f"{'FNON ' if tier == Tier.PARTNERS else ''}Phenotype Classification \u2014 {condition_name}"
            sections = [
                self._build_document_control(condition, tier),
                build_phenotype_section(condition),
                build_networks_section(condition) if tier == Tier.PARTNERS else build_anatomy_section(condition),
                build_protocols_section(condition),
            ]

        elif doc_type == DocumentType.RESPONDER_TRACKING:
            title = f"Responder Tracking \u2014 {condition_name}"
            sections = [
                self._build_document_control(condition, tier),
                build_responder_section(condition),
                build_assessments_section(condition),
            ]

        elif doc_type == DocumentType.PSYCH_INTAKE:
            title = f"Psychological Intake & PRS Baseline \u2014 {condition_name}"
            sections = [
                self._build_document_control(condition, tier),
                self._build_patient_info_section(),
                self._build_psych_intake_sections(condition, tier),
                build_assessments_section(condition),
            ]

        elif doc_type == DocumentType.NETWORK_ASSESSMENT:
            title = f"6-Network Bedside Assessment \u2014 {condition_name}"
            sections = [
                self._build_document_control(condition, tier),
                self._build_patient_info_section(),
                build_networks_section(condition),
                build_symptom_network_section(condition),
                build_phenotype_section(condition),
            ]

        else:
            title = f"{doc_type.value.replace('_', ' ').title()} \u2014 {condition_name}"
            sections = [self._build_document_control(condition, tier)]

        return title, sections

    def _build_document_control(self, condition: ConditionSchema, tier: Tier) -> SectionContent:
        tier_desc = (
            "For use by SOZO Fellow clinicians under Doctor supervision"
            if tier == Tier.FELLOW
            else "PARTNERS TIER: This document contains the complete FNON framework. For authorized SOZO Partners."
        )
        return SectionContent(
            section_id="document_control",
            title="Document Control & Clinical Responsibility",
            content=(
                f"Organization: SOZO Brain Center\n"
                f"Condition: {condition.display_name} ({condition.icd10})\n"
                f"Version: {condition.version}\n"
                f"Date: {current_month_year()}\n"
                f"Tier: {tier.value.upper()}\n"
                f"{tier_desc}\n\n"
                f"\u00a9 2026 SOZO Brain Center. All rights reserved. CONFIDENTIAL.\n\n"
                f"GOVERNANCE RULE: This document is for authorized SOZO personnel only. "
                f"No Fellow or Clinical Assistant may independently modify treatment protocols "
                f"without Doctor authorization."
            ),
        )

    def _build_patient_info_section(self) -> SectionContent:
        return SectionContent(
            section_id="patient_info",
            title="Patient Information",
            tables=[{
                "headers": ["Field", "Value"],
                "rows": [
                    ["Patient Name", ""],
                    ["Date of Birth", ""],
                    ["Date of Assessment", ""],
                    ["Clinician", ""],
                    ["Assessment Type", "\u2610 Baseline  \u2610 Follow-Up  \u2610 End of Block"],
                    ["Medication State at Assessment", "\u2610 ON-State  \u2610 OFF-State"],
                    ["Notes", ""],
                ],
                "caption": "Patient administrative information",
            }],
        )

    def _build_handbook_intro(self, condition: ConditionSchema, tier: Tier) -> SectionContent:
        fnon_text = ""
        if tier == Tier.PARTNERS:
            fnon_text = (
                "\n\nThis handbook incorporates the Functional Network-Oriented Neuromodulation (FNON) "
                "framework, which targets dysfunctional large-scale brain networks rather than isolated "
                "symptom-based regions. Core principle: Do NOT stimulate symptoms \u2014 stimulate dysfunctional NETWORKS."
            )
        return SectionContent(
            section_id="introduction",
            title="Introduction & Available Modalities",
            content=(
                f"This clinical handbook provides step-by-step guidance for the evidence-based "
                f"neuromodulation treatment of {condition.display_name} at SOZO Brain Center. "
                f"It integrates tDCS (Newronika HDCkit & PlatoScience), TPS (NEUROLITH\u00ae), "
                f"taVNS, and CES (Alpha-Stim\u00ae) within a structured 8-stage patient journey."
                f"{fnon_text}"
            ),
        )

    def _build_psych_intake_sections(self, condition: ConditionSchema, tier: Tier) -> SectionContent:
        core_symptoms = condition.core_symptoms[:6] if condition.core_symptoms else [
            "Core symptom 1", "Core symptom 2", "Core symptom 3"
        ]
        return SectionContent(
            section_id="psych_intake",
            title="Structured Clinical Interview",
            subsections=[
                SectionContent(
                    section_id="chief_complaints",
                    title="A1. Chief Complaints (Patient-Reported)",
                    tables=[{
                        "headers": ["Complaint", "Severity (0\u201310)", "Duration", "Impact"],
                        "rows": [["", "", "", ""] for _ in range(5)],
                        "caption": "Patient-reported chief complaints",
                    }],
                ),
                SectionContent(
                    section_id="psychiatric_history",
                    title="A2. Psychiatric History",
                    content=(
                        "\u26a0 SAFETY FLAG: Screen for suicidal ideation at this stage. "
                        "If patient reports active suicidal ideation, STOP intake and escalate immediately."
                    ),
                    tables=[{
                        "headers": ["History Item", "Yes / No / Unknown", "Details"],
                        "rows": [
                            ["Previous psychiatric diagnosis", "", ""],
                            ["Prior neuromodulation treatment", "", ""],
                            ["Current pharmacological treatment", "", ""],
                            ["History of self-harm or suicidal ideation", "", "\u26a0 ESCALATE IF ACTIVE"],
                            ["Seizure history", "", ""],
                            ["Substance use (current/past)", "", ""],
                        ],
                        "caption": "Psychiatric history checklist",
                    }],
                ),
                SectionContent(
                    section_id="sozo_prs",
                    title="B. SOZO PRS \u2014 Patient Rating System (Baseline)",
                    content=(
                        "Patient rates severity of symptoms on a 0\u201310 scale "
                        "(0 = not present, 10 = maximally severe). "
                        "Document before first treatment session."
                    ),
                    tables=[{
                        "headers": ["Symptom Domain", "Patient Rating (0\u201310)", "Clinician Notes"],
                        "rows": [[symptom, "", ""] for symptom in core_symptoms],
                        "caption": "SOZO PRS Baseline \u2014 Motor and Non-Motor Domains",
                    }],
                ),
            ],
        )

    def _get_output_path(self, condition_slug: str, tier: Tier, doc_type: DocumentType) -> Path:
        """Compute the output file path for a document."""
        tier_folder = tier.value.capitalize()
        doc_folder_map = {
            DocumentType.CLINICAL_EXAM: "Assessments",
            DocumentType.PHENOTYPE_CLASSIFICATION: "Assessments",
            DocumentType.RESPONDER_TRACKING: "Assessments",
            DocumentType.PSYCH_INTAKE: "Assessments",
            DocumentType.NETWORK_ASSESSMENT: "Assessments",
            DocumentType.HANDBOOK: "Handbook",
            DocumentType.ALL_IN_ONE_PROTOCOL: "Protocols",
            DocumentType.EVIDENCE_BASED_PROTOCOL: "Protocols",
        }
        subfolder = doc_folder_map.get(doc_type, "Documents")

        filename_map = {
            DocumentType.CLINICAL_EXAM: f"Clinical_Examination_Checklist_{tier_folder}.docx",
            DocumentType.PHENOTYPE_CLASSIFICATION: f"Phenotype_Classification_{tier_folder}.docx",
            DocumentType.RESPONDER_TRACKING: f"Responder_Tracking_{tier_folder}.docx",
            DocumentType.PSYCH_INTAKE: f"Psychological_Intake_PRS_Baseline_{tier_folder}.docx",
            DocumentType.NETWORK_ASSESSMENT: f"6Network_Bedside_Assessment_{tier_folder}.docx",
            DocumentType.HANDBOOK: f"SOZO_Clinical_Handbook_{tier_folder}.docx",
            DocumentType.ALL_IN_ONE_PROTOCOL: f"All_In_One_Protocol_{tier_folder}.docx",
            DocumentType.EVIDENCE_BASED_PROTOCOL: f"Evidence_Based_Protocol_{tier_folder}.docx",
        }
        filename = filename_map.get(doc_type, f"{doc_type.value}_{tier_folder}.docx")

        condition_display = condition_slug.replace("_", " ").title().replace(" ", "_")
        return self.output_base / condition_display / tier_folder / subfolder / filename
