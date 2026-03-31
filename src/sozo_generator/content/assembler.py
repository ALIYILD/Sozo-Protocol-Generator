"""
Content assembler — builds DocumentSpec objects from ConditionSchema using section builders,
and orchestrates full document export.
"""
import logging
from pathlib import Path
from ..schemas.condition import ConditionSchema
from ..schemas.documents import DocumentSpec, SectionContent
from ..core.enums import DocumentType, Tier
from ..core.utils import ensure_dir, current_date_str, current_month_year, write_json
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

logger = logging.getLogger(__name__)


class ContentAssembler:
    """
    Assembles all sections for a given document type and tier,
    and can also orchestrate full document export via the exporter.
    """

    def __init__(
        self,
        output_base: str = "outputs/documents/",
        with_visuals: bool = True,
    ):
        self.output_base = Path(output_base)
        self._with_visuals = with_visuals

    def assemble(
        self,
        condition: ConditionSchema,
        doc_type: DocumentType,
        tier: Tier,
    ) -> list:
        """Return ordered list of SectionContent for the document."""
        assemblers = {
            DocumentType.EVIDENCE_BASED_PROTOCOL: self._assemble_evidence_based_protocol,
            DocumentType.ALL_IN_ONE_PROTOCOL: self._assemble_all_in_one_protocol,
            DocumentType.HANDBOOK: self._assemble_handbook,
            DocumentType.CLINICAL_EXAM: self._assemble_clinical_exam,
            DocumentType.PHENOTYPE_CLASSIFICATION: self._assemble_phenotype_classification,
            DocumentType.RESPONDER_TRACKING: self._assemble_responder_tracking,
            DocumentType.PSYCH_INTAKE: self._assemble_psych_intake,
            DocumentType.NETWORK_ASSESSMENT: self._assemble_network_assessment,
        }
        fn = assemblers.get(doc_type)
        if not fn:
            logger.error(f"No assembler for document type: {doc_type}")
            return []
        return fn(condition, tier)

    def assemble_condition(
        self,
        condition: ConditionSchema,
        tier: Tier = Tier.BOTH,
        write_json_output: bool = True,
    ) -> dict:
        """
        Assemble and export all documents for one condition.
        Returns a summary dict.
        """
        from ..docx.exporter import DocumentExporter

        logger.info(f"Assembling documents for condition: {condition.display_name} ({tier.value})")
        exporter = DocumentExporter(output_base=str(self.output_base), with_visuals=self._with_visuals)
        output_paths = exporter.export_all(condition, tier=tier)

        summary = {
            "condition_slug": condition.slug,
            "condition_name": condition.display_name,
            "tier": tier.value,
            "generated_at": current_date_str(),
            "documents_generated": len(output_paths),
            "output_paths": [str(p) for p in output_paths],
            "review_flags": condition.review_flags,
            "evidence_gaps": condition.evidence_gaps,
        }

        if write_json_output:
            json_dir = ensure_dir(Path("outputs/condition_json/"))
            write_json(summary, json_dir / f"{condition.slug}_generation_summary.json")

        logger.info(f"Assembled {len(output_paths)} documents for {condition.display_name}")
        return summary

    # ── Section assemblers by document type ─────────────────────────────

    def _assemble_evidence_based_protocol(self, condition: ConditionSchema, tier: Tier) -> list:
        sections = [
            build_inclusion_exclusion_section(condition),
            build_overview_section(condition),
            build_pathophysiology_section(condition),
            build_anatomy_section(condition),
            build_networks_section(condition),
            build_phenotype_section(condition),
            build_symptom_network_section(condition),
            build_protocols_section(condition),
            build_safety_section(condition),
            build_evidence_gaps_section(condition),
            build_references_section(condition),
        ]
        if tier == Tier.PARTNERS:
            sections.insert(4, self._build_fnon_application_section(condition))
        return sections

    def _assemble_all_in_one_protocol(self, condition: ConditionSchema, tier: Tier) -> list:
        sections = [build_protocols_section(condition)]
        if tier == Tier.PARTNERS:
            sections.insert(0, self._build_sozo_sequencing_section(condition))
        sections.append(build_references_section(condition))
        return sections

    def _assemble_handbook(self, condition: ConditionSchema, tier: Tier) -> list:
        intro = SectionContent(
            section_id="introduction",
            title="Introduction & SOZO Platform Overview",
            content=(
                f"This Clinical Handbook guides {tier.value.title()} clinicians through the complete "
                f"8-stage patient journey for {condition.display_name}. "
                "It integrates evidence-based neuromodulation protocols with the SOZO Functional "
                "Network-Oriented Neuromodulation (FNON) framework."
            ),
        )
        modalities_section = self._build_modalities_overview()
        handbook_stages = build_handbook_sections(condition)

        sections = [intro, modalities_section] + handbook_stages
        if tier == Tier.PARTNERS:
            sections.insert(1, self._build_fnon_overview_section())
        sections.append(build_references_section(condition))
        return sections

    def _assemble_clinical_exam(self, condition: ConditionSchema, tier: Tier) -> list:
        sections = [
            self._build_patient_info_section(),
            build_assessments_section(condition),
            build_phenotype_section(condition),
        ]
        if tier == Tier.PARTNERS:
            sections.insert(1, build_networks_section(condition))
        return sections

    def _assemble_phenotype_classification(self, condition: ConditionSchema, tier: Tier) -> list:
        sections = [
            build_phenotype_section(condition),
            build_symptom_network_section(condition),
            build_protocols_section(condition),
        ]
        if tier == Tier.PARTNERS:
            sections.insert(0, self._build_fnon_core_principle())
            sections.insert(2, build_networks_section(condition))
        return sections

    def _assemble_responder_tracking(self, condition: ConditionSchema, tier: Tier) -> list:
        return [
            build_responder_section(condition),
            build_evidence_gaps_section(condition),
            build_references_section(condition),
        ]

    def _assemble_psych_intake(self, condition: ConditionSchema, tier: Tier) -> list:
        sections = [
            self._build_patient_info_section(),
            self._build_clinical_interview_section(condition),
            self._build_sozo_prs_section(condition),
            self._build_clinical_summary_section(condition),
        ]
        if tier == Tier.PARTNERS:
            sections.append(self._build_network_impression_section(condition))
        return sections

    def _assemble_network_assessment(self, condition: ConditionSchema, tier: Tier) -> list:
        return [
            self._build_patient_info_section(),
            build_networks_section(condition),
            self._build_network_scoring_section(condition),
            self._build_network_hypothesis_section(condition),
        ]

    # ── Helper section builders ──────────────────────────────────────────

    def _build_patient_info_section(self) -> SectionContent:
        return SectionContent(
            section_id="patient_info",
            title="Patient Information",
            tables=[{
                "headers": ["Field", "Value"],
                "rows": [
                    ["Patient Name", ""],
                    ["Date of Birth", ""],
                    ["Assessment Date", ""],
                    ["Clinician", ""],
                    ["Assessment Type", "\u2610 Baseline  \u2610 Follow-Up  \u2610 End of Block"],
                    ["Medication State", "\u2610 ON  \u2610 OFF  \u2610 Not applicable"],
                    ["Levodopa Last Dose Time", ""],
                ],
                "caption": "Patient identification and session metadata",
            }],
        )

    def _build_clinical_interview_section(self, condition: ConditionSchema) -> SectionContent:
        return SectionContent(
            section_id="clinical_interview",
            title="Structured Clinical Interview",
            subsections=[
                SectionContent(
                    section_id="chief_complaints",
                    title="A1. Chief Complaints (Patient-Reported)",
                    tables=[{
                        "headers": ["Symptom Domain", "Patient Rating (0\u201310)", "Duration", "Notes"],
                        "rows": [
                            [s, "", "", ""]
                            for s in (condition.core_symptoms[:5] if condition.core_symptoms else ["", "", "", "", ""])
                        ],
                        "caption": "Chief complaint domains",
                    }],
                ),
                SectionContent(
                    section_id="psychiatric_history",
                    title="A2. Psychiatric History",
                    content=(
                        "Previous psychiatric diagnoses:\n"
                        "Previous neuromodulation treatments:\n"
                        "Current medications (psychotropic):\n"
                        "\u26a0 SAFETY FLAG: Suicidal Ideation — Screen at every intake. "
                        "If present, escalate immediately per clinic safety protocol."
                    ),
                ),
            ],
        )

    def _build_sozo_prs_section(self, condition: ConditionSchema) -> SectionContent:
        motor_rows = [
            [s, "", "", ""]
            for s in (condition.core_symptoms[:4] if condition.core_symptoms else ["", "", ""])
        ]
        nonmotor_rows = [
            [s, "", "", ""]
            for s in (condition.non_motor_symptoms[:4] if hasattr(condition, "non_motor_symptoms") and condition.non_motor_symptoms else ["", "", ""])
        ]
        return SectionContent(
            section_id="sozo_prs",
            title="B. SOZO PRS \u2014 Patient Rating System (Baseline)",
            content="Rate each domain 0 (no symptom) to 10 (worst imaginable). Patient self-report with clinician guidance.",
            subsections=[
                SectionContent(
                    section_id="prs_motor",
                    title="B1. Motor Symptoms",
                    tables=[{
                        "headers": ["Symptom", "Baseline (0\u201310)", "Week 4 (0\u201310)", "End of Block (0\u201310)"],
                        "rows": motor_rows,
                        "caption": "Motor symptom ratings",
                    }],
                ),
                SectionContent(
                    section_id="prs_nonmotor",
                    title="B2. Non-Motor Symptoms",
                    tables=[{
                        "headers": ["Symptom", "Baseline (0\u201310)", "Week 4 (0\u201310)", "End of Block (0\u201310)"],
                        "rows": nonmotor_rows,
                        "caption": "Non-motor symptom ratings",
                    }],
                ),
            ],
        )

    def _build_clinical_summary_section(self, condition: ConditionSchema) -> SectionContent:
        return SectionContent(
            section_id="clinical_summary",
            title="C. Baseline Summary & Clinical Impression",
            tables=[{
                "headers": ["Assessment Area", "Summary", "Clinical Impression"],
                "rows": [
                    ["Primary Diagnosis", condition.display_name, ""],
                    ["Dominant Symptom Cluster", "", ""],
                    ["Identified Phenotype", "", ""],
                    ["Network Hypothesis", "", ""],
                    ["Proposed Treatment Approach", "", ""],
                    ["Safety Flags", "", ""],
                    ["Clinician Signature", "", ""],
                ],
                "caption": "Clinical impression and treatment planning summary",
            }],
        )

    def _build_network_impression_section(self, condition: ConditionSchema) -> SectionContent:
        return SectionContent(
            section_id="network_impression",
            title="D. Network-Level Clinical Impression (FNON \u2014 Partners Tier)",
            content=(
                "Based on the clinical interview and baseline assessment, identify the dominant "
                "network dysfunction hypothesis for this patient:"
            ),
            tables=[{
                "headers": ["Network", "Dysfunction Hypothesis (HYPO/NORMAL/HYPER)", "Clinical Basis"],
                "rows": [
                    ["Default Mode Network (DMN)", "", ""],
                    ["Central Executive Network (CEN)", "", ""],
                    ["Salience Network (SN)", "", ""],
                    ["Sensorimotor Network (SMN)", "", ""],
                    ["Limbic / Emotional Network", "", ""],
                    ["Attention Networks (DAN/VAN)", "", ""],
                ],
                "caption": "Network dysfunction hypothesis for FNON treatment targeting",
            }],
        )

    def _build_network_scoring_section(self, condition: ConditionSchema) -> SectionContent:
        return SectionContent(
            section_id="network_scoring",
            title="6-Network Bedside Assessment Scoring",
            content="Score each test: HYPO (1) | NORMAL (0) | HYPER (2). Maximum total score: 88 across 6 networks.",
            tables=[{
                "headers": ["Network", "Test Battery", "Score (0/1/2)", "Notes"],
                "rows": [
                    ["DMN", "Memory recall, self-reference, mind-wandering", "", ""],
                    ["CEN", "Working memory, executive function, inhibition", "", ""],
                    ["SN", "Interoception, emotion recognition, switching", "", ""],
                    ["SMN", "Motor speed, coordination, gait assessment", "", ""],
                    ["Limbic", "Affect regulation, reward, mood screening", "", ""],
                    ["Attention", "Sustained attention, vigilance, dual-task", "", ""],
                    ["TOTAL SCORE", "", "", "/88"],
                ],
                "caption": "6-Network scoring summary",
            }],
        )

    def _build_network_hypothesis_section(self, condition: ConditionSchema) -> SectionContent:
        return SectionContent(
            section_id="network_hypothesis",
            title="Network Hypothesis & Treatment Targeting",
            content=(
                "Based on the 6-Network Assessment, identify primary (most impaired), "
                "secondary, and tertiary network targets for the FNON treatment protocol:"
            ),
            tables=[{
                "headers": ["Priority", "Network", "Dysfunction", "Proposed Target", "Modality"],
                "rows": [
                    ["Primary", "", "", "", ""],
                    ["Secondary", "", "", "", ""],
                    ["Tertiary", "", "", "", ""],
                ],
                "caption": "FNON network prioritization for treatment targeting",
            }],
        )

    def _build_fnon_application_section(self, condition: ConditionSchema) -> SectionContent:
        primary_network = ""
        if hasattr(condition, "primary_network") and condition.primary_network:
            primary_network = condition.primary_network.value.upper() if hasattr(condition.primary_network, "value") else str(condition.primary_network)
        fnon_rationale = getattr(condition, "fnon_rationale", "")
        return SectionContent(
            section_id="fnon_application",
            title="Applying NIBS According to the SOZO FNON Framework",
            content=(
                f"In {condition.display_name}, the FNON framework moves beyond symptom-based "
                f"stimulation to target dysfunctional large-scale brain networks.\n\n"
                f"Primary network: {primary_network or '[REVIEW]'}\n\n"
                f"{fnon_rationale}\n\n"
                "The Five-Level FNON Clinical Decision Pathway applies as follows:\n"
                "Level 1: Phenotype identification\n"
                "Level 2: Network prioritization (primary \u2192 secondary \u2192 tertiary)\n"
                "Level 3: Montage/target selection based on network dysfunction pattern\n"
                "Level 4: Response evaluation at Week 4 \u2014 reassess network function\n"
                "Level 5: Non-responder pathway \u2014 FNON-based protocol adjustment"
            ),
        )

    def _build_fnon_overview_section(self) -> SectionContent:
        return SectionContent(
            section_id="fnon_overview",
            title="FNON Framework \u2014 Overview",
            content=(
                "The Functional Network-Oriented Neuromodulation (FNON) framework is the SOZO "
                "Partners Tier clinical methodology.\n\n"
                "Core Principle: Do NOT stimulate symptoms. Stimulate dysfunctional NETWORKS.\n\n"
                "Unlike traditional phenotype-based approaches that target specific symptoms, "
                "FNON identifies the underlying large-scale brain network dysfunction and directs "
                "stimulation at the dysfunctional network node(s). This approach is informed by "
                "resting-state fMRI research, network neuroscience, and the understanding that "
                "most neurological and psychiatric conditions represent distributed network "
                "dysregulations rather than focal lesions.\n\n"
                "The 6 FNON Networks:\n"
                "1. Default Mode Network (DMN)\n"
                "2. Central Executive Network (CEN/FPN)\n"
                "3. Salience Network (SN)\n"
                "4. Sensorimotor Network (SMN)\n"
                "5. Limbic / Emotional Network\n"
                "6. Attention Networks (DAN/VAN)"
            ),
        )

    def _build_fnon_core_principle(self) -> SectionContent:
        return SectionContent(
            section_id="fnon_core",
            title="FNON Core Principle",
            content="Do NOT stimulate symptoms. Stimulate dysfunctional NETWORKS.",
        )

    def _build_sozo_sequencing_section(self, condition: ConditionSchema) -> SectionContent:
        return SectionContent(
            section_id="sozo_sequencing",
            title="SOZO S-O-Z-O Sequencing Framework",
            content=(
                "The S-O-Z-O multimodal sequencing framework organizes treatment delivery:\n\n"
                "S \u2014 Stabilize: CES/taVNS first to reduce hyperarousal, anxiety, or autonomic dysregulation\n"
                "O \u2014 Optimize: tDCS to modulate primary network excitability\n"
                "Z \u2014 Zone target: TPS for focal deep-target stimulation (Doctor-authorized, off-label)\n"
                "O \u2014 Outcome: Response evaluation and protocol adjustment\n\n"
                "Not all patients require all 4 elements. Protocol selection is phenotype and network-dependent."
            ),
        )

    def _build_modalities_overview(self) -> SectionContent:
        return SectionContent(
            section_id="modalities_overview",
            title="Available Neuromodulation Modalities",
            tables=[{
                "headers": ["Modality", "Device(s)", "Mechanism", "Status"],
                "rows": [
                    ["tDCS", "Newronika HDCkit, PlatoScience/PlatoWork",
                     "Low-intensity DC to modulate cortical excitability", "CE-marked medical device"],
                    ["TPS", "NEUROLITH\u00ae (Storz Medical)", "Focused transcranial pulse stimulation",
                     "CE-marked (Alzheimer\u2019s); \u26a0 OFF-LABEL for other conditions"],
                    ["taVNS", "Transcutaneous auricular electrodes", "Auricular vagus nerve stimulation",
                     "CE-marked (epilepsy); off-label neuro use"],
                    ["CES", "Alpha-Stim\u00ae", "Microcurrent cranial electrotherapy",
                     "FDA-cleared (anxiety, depression, insomnia)"],
                ],
                "caption": "Available neuromodulation modalities at SOZO Brain Center",
            }],
        )
