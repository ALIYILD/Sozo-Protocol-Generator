"""SOZO Generator — outline planner.

Produces a structured list of outline entries that describes every section a
long clinical document should contain, including per-section word-count
targets, required tables, required figures, allowed claim categories, and
variant tags.  No external API calls are made here; all planning is driven
by document-type rules encoded directly in this module.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Per-words-per-page constant used throughout word → page budgeting
# ---------------------------------------------------------------------------
_WORDS_PER_PAGE: int = 500


# ---------------------------------------------------------------------------
# Shared building-block helpers
# ---------------------------------------------------------------------------

def _entry(
    title: str,
    purpose: str,
    section_type: str,
    target_word_count: int,
    ordering: int,
    *,
    variant_tags: list[str] | None = None,
    required_tables: list[str] | None = None,
    required_figures: list[str] | None = None,
    allowed_claim_categories: list[str] | None = None,
    subsections: list[dict] | None = None,
) -> dict[str, Any]:
    """Construct a single outline entry dict with sensible defaults."""
    page_budget = round(target_word_count / _WORDS_PER_PAGE, 1) if target_word_count else 0.0
    return {
        "title": title,
        "purpose": purpose,
        "section_type": section_type,
        "target_word_count": target_word_count,
        "target_page_budget": page_budget,
        "ordering": ordering,
        "variant_tags": variant_tags or [],
        "required_tables": required_tables or [],
        "required_figures": required_figures or [],
        "allowed_claim_categories": allowed_claim_categories or [],
        "subsections": subsections or [],
    }


def _sub(title: str, purpose: str, target_word_count: int) -> dict[str, Any]:
    """Construct a subsection stub dict."""
    return {
        "title": title,
        "purpose": purpose,
        "target_word_count": target_word_count,
    }


# ---------------------------------------------------------------------------
# Outline definitions — one function per document type
# ---------------------------------------------------------------------------

def _handbook_outline(variant: str) -> list[dict[str, Any]]:
    """Return the full 21-section handbook outline.

    Partners variant includes an extra FNON Advanced Protocols section that is
    tagged ``["partners"]``; fellows receive a simplified language note via the
    generation hints embedded in purposes.
    """
    fellow = variant == "fellow"

    outline: list[dict[str, Any]] = [
        _entry(
            title="Title Page",
            purpose="Formal title page with condition name, document type, version, and date.",
            section_type="intro",
            target_word_count=0,
            ordering=0,
        ),
        _entry(
            title="Table of Contents",
            purpose="Auto-generated table of contents with section titles and page numbers.",
            section_type="toc",
            target_word_count=0,
            ordering=1,
        ),
        _entry(
            title="Introduction & Overview",
            purpose=(
                "Provide a concise condition overview including prevalence, clinical impact, "
                "and the purpose of this handbook. "
                + ("Use accessible language appropriate for fellows." if fellow else "Include FNON positioning and rationale for advanced practitioners.")
            ),
            section_type="body",
            target_word_count=800,
            ordering=2,
            allowed_claim_categories=["pathophysiology", "brain_regions"],
            subsections=[
                _sub("Condition Overview", "Epidemiology, burden of disease, and clinical context.", 400),
                _sub("Purpose of This Handbook", "How to use this document in clinical practice.", 200),
                _sub("Scope & Limitations", "What is and is not covered; off-label status.", 200),
            ],
        ),
        _entry(
            title="Neuroanatomy & Pathophysiology",
            purpose=(
                "Describe the key brain regions implicated in the condition, their normal function, "
                "and the nature of their dysfunction. Ground stimulation rationale in neuroanatomy."
            ),
            section_type="body",
            target_word_count=1200,
            ordering=3,
            allowed_claim_categories=["pathophysiology", "brain_regions", "network_involvement"],
            required_figures=["neuroanatomy_diagram"],
            subsections=[
                _sub("Key Brain Regions", "Enumerate and describe implicated regions.", 400),
                _sub("Pathophysiological Mechanisms", "Circuit-level dysfunction and cascade effects.", 500),
                _sub("Implications for Neuromodulation", "How anatomy informs target selection.", 300),
            ],
        ),
        _entry(
            title="Functional Network Overview",
            purpose=(
                "Explain the FNON (Functional Network Overlay Neuromodulation) framework as it applies "
                "to this condition. Map condition-specific symptoms to network dysfunctions."
            ),
            section_type="body",
            target_word_count=1000,
            ordering=4,
            allowed_claim_categories=["network_involvement", "pathophysiology"],
            required_figures=["fnon_network_map"],
            required_tables=["network_dysfunction_summary"],
            subsections=[
                _sub("FNON Framework Primer", "Core concepts of functional network targeting.", 300),
                _sub("Network Involvement in This Condition", "Which networks are affected and how.", 400),
                _sub("Symptom-to-Network Mapping", "Table of symptoms mapped to network dysfunction.", 300),
            ],
        ),
        _entry(
            title="Clinical Phenotypes & Subtypes",
            purpose=(
                "Characterise the recognised clinical subtypes and phenotype variants. "
                "Link each phenotype to preferred modalities and stimulation targets."
            ),
            section_type="body",
            target_word_count=1000,
            ordering=5,
            allowed_claim_categories=["clinical_phenotypes", "stimulation_targets"],
            required_tables=["phenotype_classification"],
            subsections=[
                _sub("Phenotype Definitions", "Diagnostic criteria and distinguishing features per subtype.", 500),
                _sub("Clinical Presentation Patterns", "How subtypes present differently at intake.", 300),
                _sub("Phenotype-to-Modality Bridge", "Which subtypes respond to which modalities.", 200),
            ],
        ),
        _entry(
            title="Assessment & Outcome Measurement",
            purpose=(
                "Describe the validated assessment tools used at baseline and follow-up. "
                "Specify timing, domains assessed, and scoring interpretation."
            ),
            section_type="body",
            target_word_count=900,
            ordering=6,
            allowed_claim_categories=["assessment_tools"],
            required_tables=["assessment_tools_summary"],
            subsections=[
                _sub("Baseline Assessment Battery", "Tools administered before treatment begins.", 350),
                _sub("Follow-up & Endpoint Measures", "Timing and tools for ongoing monitoring.", 350),
                _sub("Score Interpretation", "Clinically meaningful change thresholds.", 200),
            ],
        ),
        _entry(
            title="Stimulation Modalities Overview",
            purpose=(
                "Provide a comparative overview of all modalities used for this condition "
                "(tDCS, TPS, taVNS, CES, TMS, NFB, iTBS). "
                + ("Focus on the three most-used modalities for fellows." if fellow else "Cover all modalities including multimodal stacking for partners.")
            ),
            section_type="body",
            target_word_count=1200,
            ordering=7,
            allowed_claim_categories=["stimulation_targets", "modality_rationale"],
            required_tables=["modality_comparison"],
            required_figures=["modality_overview_diagram"],
            subsections=[
                _sub("Modality Mechanisms of Action", "How each modality works at the neural level.", 500),
                _sub("Comparative Efficacy Summary", "Side-by-side evidence snapshot per modality.", 400),
                _sub("Modality Selection Guide", "Decision framework for choosing modalities.", 300),
            ],
        ),
        _entry(
            title="Evidence Summary",
            purpose=(
                "Summarise the clinical evidence base for neuromodulation in this condition. "
                "Organise by modality. Highlight RCTs, systematic reviews, and meta-analyses."
            ),
            section_type="body",
            target_word_count=1500,
            ordering=8,
            allowed_claim_categories=["pathophysiology", "stimulation_targets", "modality_rationale"],
            required_tables=["evidence_by_modality", "key_trials_summary"],
            subsections=[
                _sub("Evidence by Modality", "Tabulated evidence per modality with levels.", 700),
                _sub("Key Trials & Findings", "Narrative of landmark studies.", 500),
                _sub("Evidence Gaps", "Areas where evidence is lacking or conflicting.", 300),
            ],
        ),
        _entry(
            title="Treatment Protocols",
            purpose=(
                "Provide full stimulation parameter sets for each protocol. "
                "Include dose, frequency, session count, and target for each modality-protocol combination."
                + (" Simplified for fellow implementation." if fellow else " Include multimodal stacking and advanced parameter variants for partners.")
            ),
            section_type="body",
            target_word_count=2000,
            ordering=9,
            allowed_claim_categories=["stimulation_parameters", "stimulation_targets", "modality_rationale"],
            required_tables=["protocol_parameters", "session_schedule"],
            subsections=[
                _sub("Protocol Selection Criteria", "How to match protocol to phenotype.", 300),
                _sub("Parameter Tables by Modality", "Full parameter sets for each protocol.", 900),
                _sub("Session Sequencing", "Ordering of sessions and inter-session intervals.", 400),
                _sub("Protocol Modifications", "Adjustments for comorbidities and non-responders.", 400),
            ],
        ),
        _entry(
            title="Stimulation Targets & Montages",
            purpose=(
                "Specify EEG electrode positions, tDCS montages, and TPS/TMS coil placements "
                "for each protocol. Include diagrams."
            ),
            section_type="body",
            target_word_count=800,
            ordering=10,
            allowed_claim_categories=["stimulation_targets"],
            required_tables=["eeg_positions_by_protocol"],
            required_figures=["montage_diagram", "qeeg_topomap"],
            subsections=[
                _sub("EEG 10-20 Reference Positions", "Canonical positions used per protocol.", 300),
                _sub("Montage Diagrams", "Visual reference for electrode placement.", 200),
                _sub("Target Verification", "Clinical checks for target accuracy.", 300),
            ],
        ),
        _entry(
            title="Session Structure & Schedule",
            purpose=(
                "Define the typical session structure, total course duration, "
                "and recommended inter-session intervals."
            ),
            section_type="body",
            target_word_count=700,
            ordering=11,
            allowed_claim_categories=["stimulation_parameters"],
            required_tables=["session_timeline"],
            required_figures=["session_timeline_chart"],
            subsections=[
                _sub("Single Session Structure", "Pre-session checks, stimulation, post-session review.", 300),
                _sub("Treatment Course Schedule", "Week-by-week plan and session count.", 250),
                _sub("Maintenance & Booster Schedule", "Post-course follow-up and maintenance sessions.", 150),
            ],
        ),
        _entry(
            title="Safety, Contraindications & Precautions",
            purpose=(
                "List all absolute and relative contraindications, safety precautions, "
                "and stopping rules for this condition and its associated protocols."
            ),
            section_type="body",
            target_word_count=900,
            ordering=12,
            allowed_claim_categories=["safety", "contraindications"],
            required_tables=["contraindications", "safety_checklist"],
            subsections=[
                _sub("Absolute Contraindications", "Conditions under which treatment must not proceed.", 300),
                _sub("Relative Contraindications & Precautions", "Conditions requiring modified approach.", 300),
                _sub("Stopping Rules & Adverse Event Protocol", "When to stop and how to respond.", 300),
            ],
        ),
        _entry(
            title="Medication Interactions",
            purpose=(
                "Document known and potential interactions between neuromodulation protocols "
                "and pharmacological treatments relevant to this condition."
            ),
            section_type="body",
            target_word_count=600,
            ordering=13,
            allowed_claim_categories=["safety", "contraindications"],
            required_tables=["medication_interactions"],
            subsections=[
                _sub("Medications Affecting Cortical Excitability", "Drugs that modulate plasticity thresholds.", 300),
                _sub("Condition-Specific Medications", "Interaction notes for condition-specific pharmacotherapy.", 300),
            ],
        ),
        _entry(
            title="Monitoring & Responder Tracking",
            purpose=(
                "Describe the clinical monitoring framework, including how to track response, "
                "when to reassess, and which outcome measures trigger protocol changes."
            ),
            section_type="body",
            target_word_count=800,
            ordering=14,
            allowed_claim_categories=["responder_criteria", "assessment_tools"],
            required_tables=["monitoring_schedule", "responder_criteria_table"],
            subsections=[
                _sub("Response Criteria", "Operational definition of clinically meaningful response.", 300),
                _sub("Monitoring Schedule", "When and what to assess across the treatment course.", 300),
                _sub("Documentation Requirements", "Records, scores, and clinician notes required.", 200),
            ],
        ),
        _entry(
            title="Non-Responder Pathways",
            purpose=(
                "Provide a structured decision framework for patients who do not respond "
                "to first-line protocol. Include protocol switching, parameter adjustment, "
                "and escalation options."
            ),
            section_type="body",
            target_word_count=600,
            ordering=15,
            allowed_claim_categories=["responder_criteria", "stimulation_parameters"],
            required_figures=["non_responder_decision_tree"],
            subsections=[
                _sub("Non-Response Definition", "Criteria for declaring non-response.", 200),
                _sub("Protocol Switching Options", "Second-line protocol alternatives.", 200),
                _sub("Referral & Escalation Criteria", "When to refer on or escalate to higher-intensity treatment.", 200),
            ],
        ),
        _entry(
            title="Clinician Workflow",
            purpose=(
                "Summarise the end-to-end clinical workflow from intake assessment to "
                "treatment completion, including administrative and documentation touchpoints."
            ),
            section_type="body",
            target_word_count=700,
            ordering=16,
            allowed_claim_categories=["assessment_tools"],
            required_figures=["clinician_workflow_diagram"],
            subsections=[
                _sub("Intake & Assessment Workflow", "Steps from referral to treatment start.", 250),
                _sub("Session-by-Session Workflow", "Checklist for each treatment session.", 250),
                _sub("Discharge & Follow-up Workflow", "Post-treatment steps and handover.", 200),
            ],
        ),
    ]

    # Partners-only section: FNON Advanced Protocols
    if not fellow:
        outline.append(
            _entry(
                title="Partner-Specific: FNON Advanced Protocols",
                purpose=(
                    "Describe advanced multimodal and FNON-stack protocols available exclusively "
                    "to licensed SOZO partners. Include parameter sets for stacked protocols, "
                    "advanced montage variants, and FNON-guided personalisation."
                ),
                section_type="body",
                target_word_count=1000,
                ordering=17,
                variant_tags=["partners"],
                allowed_claim_categories=["stimulation_parameters", "stimulation_targets", "modality_rationale", "network_involvement"],
                required_tables=["advanced_protocol_parameters", "multimodal_comparison"],
                required_figures=["fnon_stack_diagram"],
                subsections=[
                    _sub("Multimodal Stacking Rationale", "Why combined modalities are used and evidence basis.", 300),
                    _sub("Advanced Parameter Sets", "Full parameter tables for partner protocols.", 400),
                    _sub("FNON-Guided Personalisation", "How to adjust protocols based on FNON profile.", 300),
                ],
            )
        )

    outline.extend([
        _entry(
            title="Patient Journey",
            purpose=(
                "Describe the patient's experience from first contact through treatment completion. "
                "Highlight key communication, consent, and psychoeducation touchpoints."
            ),
            section_type="body",
            target_word_count=500,
            ordering=18,
            required_figures=["patient_journey_diagram"],
            subsections=[
                _sub("Pre-Treatment Journey", "Initial contact, assessment, consent, and expectations.", 200),
                _sub("During Treatment", "Patient experience during the treatment course.", 150),
                _sub("Post-Treatment Follow-up", "Maintenance, review, and discharge journey.", 150),
            ],
        ),
        _entry(
            title="Appendices",
            purpose="Supporting materials, forms, and reference tables.",
            section_type="appendix",
            target_word_count=0,
            ordering=19,
        ),
        _entry(
            title="References",
            purpose="Complete reference list for all cited evidence.",
            section_type="references",
            target_word_count=0,
            ordering=20,
        ),
    ])

    return outline


def _protocol_outline(variant: str) -> list[dict[str, Any]]:
    """Return the 9-section protocol outline."""
    fellow = variant == "fellow"

    return [
        _entry(
            title="Cover",
            purpose="Protocol cover page with condition, version, and date.",
            section_type="intro",
            target_word_count=0,
            ordering=0,
        ),
        _entry(
            title="Table of Contents",
            purpose="Auto-generated TOC.",
            section_type="toc",
            target_word_count=0,
            ordering=1,
        ),
        _entry(
            title="Clinical Rationale",
            purpose=(
                "Summarise the evidence base and clinical rationale for neuromodulation in this condition. "
                + ("Concise rationale for fellows." if fellow else "Include FNON network rationale for partners.")
            ),
            section_type="body",
            target_word_count=600,
            ordering=2,
            allowed_claim_categories=["pathophysiology", "modality_rationale"],
            subsections=[
                _sub("Condition & Target Justification", "Why this condition is treated with neuromodulation.", 300),
                _sub("Evidence Summary", "Key evidence supporting protocol parameters.", 300),
            ],
        ),
        _entry(
            title="Stimulation Parameters",
            purpose=(
                "Provide comprehensive stimulation parameter tables for all applicable protocols. "
                "This is the core reference section for clinical use."
            ),
            section_type="body",
            target_word_count=1000,
            ordering=3,
            allowed_claim_categories=["stimulation_parameters", "stimulation_targets"],
            required_tables=["protocol_parameters", "contraindications"],
            subsections=[
                _sub("Parameter Tables by Modality", "Full parameter specifications.", 600),
                _sub("Dosing Notes & Tolerability", "Adjustments for tolerability and side effects.", 250),
                _sub("Off-Label Status & Consent", "Documentation requirements for off-label use.", 150),
            ],
        ),
        _entry(
            title="Session Protocol",
            purpose="Step-by-step session structure and full treatment course schedule.",
            section_type="body",
            target_word_count=800,
            ordering=4,
            allowed_claim_categories=["stimulation_parameters"],
            required_tables=["session_schedule"],
            subsections=[
                _sub("Pre-Session Checklist", "Safety and readiness checks before each session.", 250),
                _sub("Session Steps", "Numbered procedural steps for the clinician.", 300),
                _sub("Treatment Course Timeline", "Full course schedule with session counts.", 250),
            ],
        ),
        _entry(
            title="Target Selection & Montage",
            purpose="Specify electrode/coil targets, EEG positions, and placement diagrams.",
            section_type="body",
            target_word_count=600,
            ordering=5,
            allowed_claim_categories=["stimulation_targets"],
            required_tables=["eeg_positions_by_protocol"],
            required_figures=["montage_diagram"],
            subsections=[
                _sub("Target Regions", "Anatomical and EEG-referenced targets per protocol.", 300),
                _sub("Montage Diagrams", "Visual electrode placement reference.", 300),
            ],
        ),
        _entry(
            title="Safety Checklist",
            purpose="Complete safety and contraindication checklist for clinical use.",
            section_type="body",
            target_word_count=500,
            ordering=6,
            allowed_claim_categories=["safety", "contraindications"],
            required_tables=["safety_checklist", "contraindications"],
            subsections=[
                _sub("Contraindication Screen", "Pre-treatment contraindication checklist.", 250),
                _sub("Adverse Event Response", "Steps to take if adverse events occur.", 250),
            ],
        ),
        _entry(
            title="Outcome Measures",
            purpose="Specify which validated outcome scales to use and when to administer them.",
            section_type="body",
            target_word_count=400,
            ordering=7,
            allowed_claim_categories=["assessment_tools", "responder_criteria"],
            required_tables=["outcome_measures_schedule"],
            subsections=[
                _sub("Baseline Measures", "Scales administered before treatment.", 200),
                _sub("Follow-up Measures", "Scales administered during and after treatment.", 200),
            ],
        ),
        _entry(
            title="References",
            purpose="Evidence references supporting protocol parameters.",
            section_type="references",
            target_word_count=0,
            ordering=8,
        ),
    ]


def _assessment_outline(variant: str) -> list[dict[str, Any]]:
    """Return the 5-section assessment outline."""
    return [
        _entry(
            title="Cover",
            purpose="Assessment document cover page.",
            section_type="intro",
            target_word_count=0,
            ordering=0,
        ),
        _entry(
            title="Clinical Examination Checklist",
            purpose=(
                "Structured clinical examination checklist for systematic intake assessment. "
                "Includes motor, cognitive, psychiatric, and autonomic domains as relevant."
            ),
            section_type="body",
            target_word_count=600,
            ordering=1,
            allowed_claim_categories=["assessment_tools", "clinical_phenotypes"],
            required_tables=["clinical_examination_checklist"],
            subsections=[
                _sub("History & Presenting Complaint", "Structured history items.", 150),
                _sub("Examination Domains", "Domain-by-domain examination checklist.", 300),
                _sub("Red Flags & Exclusion Criteria", "Items triggering exclusion or referral.", 150),
            ],
        ),
        _entry(
            title="Phenotype Classification",
            purpose=(
                "Clinical decision table for classifying the patient into a recognised "
                "phenotype or subtype. Drives protocol selection."
            ),
            section_type="body",
            target_word_count=500,
            ordering=2,
            allowed_claim_categories=["clinical_phenotypes", "stimulation_targets"],
            required_tables=["phenotype_decision_table"],
            required_figures=["phenotype_decision_tree"],
            subsections=[
                _sub("Decision Criteria", "Step-by-step classification logic.", 300),
                _sub("Phenotype Summary Table", "Quick-reference classification table.", 200),
            ],
        ),
        _entry(
            title="Outcome Scales",
            purpose=(
                "Full scoring tables and administration instructions for all validated "
                "outcome scales used for this condition."
            ),
            section_type="body",
            target_word_count=700,
            ordering=3,
            allowed_claim_categories=["assessment_tools"],
            required_tables=["outcome_scales_full"],
            subsections=[
                _sub("Scale Administration Instructions", "How to administer each scale correctly.", 300),
                _sub("Scoring & Interpretation", "Scoring keys and clinically meaningful change thresholds.", 250),
                _sub("Scale Selection Guide", "Which scales to use for which clinical questions.", 150),
            ],
        ),
        _entry(
            title="References",
            purpose="Validation references for included scales.",
            section_type="references",
            target_word_count=0,
            ordering=4,
        ),
    ]


def _all_in_one_outline(variant: str) -> list[dict[str, Any]]:
    """Return the combined all-in-one outline merging handbook + protocol + assessment.

    Sections from each component are deduplicated and re-ordered into a coherent
    master document flow.  Ordering restarts from 0 across the merged set.
    """
    handbook = _handbook_outline(variant)
    protocol = _protocol_outline(variant)
    assessment = _assessment_outline(variant)

    # Collect all unique titles across the three sources, with handbook as
    # the canonical version when titles overlap.
    seen_titles: set[str] = set()
    merged: list[dict[str, Any]] = []

    for entry in handbook:
        merged.append(entry)
        seen_titles.add(entry["title"].lower())

    # Insert protocol-specific sections not already in handbook
    protocol_only_sections = [
        "Clinical Rationale",
        "Stimulation Parameters",
        "Session Protocol",
        "Safety Checklist",
        "Outcome Measures",
    ]
    for entry in protocol:
        if entry["title"] in protocol_only_sections and entry["title"].lower() not in seen_titles:
            merged.append(entry)
            seen_titles.add(entry["title"].lower())

    # Insert assessment-specific sections not already present
    assessment_only_sections = [
        "Clinical Examination Checklist",
        "Phenotype Classification",
        "Outcome Scales",
    ]
    for entry in assessment:
        if entry["title"] in assessment_only_sections and entry["title"].lower() not in seen_titles:
            merged.append(entry)
            seen_titles.add(entry["title"].lower())

    # Re-order: intro/toc first, then body (sorted by original ordering), appendix/references last
    intro = [e for e in merged if e["section_type"] in ("intro", "toc")]
    body = [e for e in merged if e["section_type"] == "body"]
    tail = [e for e in merged if e["section_type"] in ("appendix", "references")]

    ordered: list[dict[str, Any]] = []
    for i, entry in enumerate(intro + body + tail):
        entry = dict(entry)  # shallow copy so we don't mutate shared dicts
        entry["ordering"] = i
        ordered.append(entry)

    return ordered


def _partner_compendium_outline(variant: str) -> list[dict[str, Any]]:
    """Return a partners-only compendium outline — superset of all_in_one with extra partner sections."""
    base = _all_in_one_outline("partners")

    # Add a partner-specific compendium section at the end (before appendix/references)
    extra = _entry(
        title="Partner Clinical Governance & Certification",
        purpose=(
            "Document governance requirements for SOZO partner clinics including certification, "
            "audit, quality assurance, and incident reporting procedures."
        ),
        section_type="body",
        target_word_count=800,
        ordering=999,  # Will be re-ordered below
        variant_tags=["partners"],
        required_tables=["governance_checklist"],
        subsections=[
            _sub("Certification Requirements", "SOZO partner certification conditions.", 250),
            _sub("Audit & Quality Assurance", "Clinical audit schedule and QA procedures.", 300),
            _sub("Incident Reporting", "Mandatory reporting and adverse event escalation.", 250),
        ],
    )

    # Insert before appendix/references
    insert_idx = next(
        (i for i, e in enumerate(base) if e["section_type"] in ("appendix", "references")),
        len(base),
    )
    base.insert(insert_idx, extra)

    # Re-number ordering
    for i, entry in enumerate(base):
        entry["ordering"] = i

    return base


# ---------------------------------------------------------------------------
# OutlinePlanner class
# ---------------------------------------------------------------------------

class OutlinePlanner:
    """Plans the high-level outline of a long clinical document.

    All planning is deterministic and offline — no external API calls are made.
    """

    # Map document_type → outline builder function
    _OUTLINE_BUILDERS = {
        "handbook": _handbook_outline,
        "protocol": _protocol_outline,
        "assessment": _assessment_outline,
        "all_in_one": _all_in_one_outline,
        "partner_compendium": _partner_compendium_outline,
    }

    def plan(
        self,
        condition_slug: str,
        variant: str,
        document_type: str,
        target_page_count: int = 60,
    ) -> list[dict[str, Any]]:
        """Return a list of outline entries for the specified document type and variant.

        Args:
            condition_slug: Slug of the condition (used only for logging / future
                per-condition overrides; not currently used to alter structure).
            variant: ``"fellow"`` or ``"partners"``.  Controls which sections are
                included and the complexity of language guidance embedded in
                ``purpose`` strings.
            document_type: One of the values returned by
                :meth:`get_supported_document_types`.
            target_page_count: Soft target total page count.  Currently used only
                to scale a ``"body"`` word-count multiplier when the default
                outline total word count would substantially undershoot the target.

        Returns:
            A list of outline-entry dicts ready for consumption by
            :class:`~sozo_generator.planning.section_planner.SectionPlanner`.

        Raises:
            ValueError: If ``document_type`` is not supported.
        """
        if document_type not in self._OUTLINE_BUILDERS:
            raise ValueError(
                f"Unsupported document_type '{document_type}'. "
                f"Supported types: {self.get_supported_document_types()}"
            )

        # Normalise variant — any unknown value defaults to "fellow"
        normalised_variant = variant if variant in ("fellow", "partners") else "fellow"

        outline = self._OUTLINE_BUILDERS[document_type](normalised_variant)

        # Optional: scale body section word counts proportionally when the
        # default outline would hit less than 80 % of the page target.
        outline = self._scale_to_page_target(outline, target_page_count)

        return outline

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_supported_document_types(self) -> list[str]:
        """Return the list of supported document type identifiers."""
        return list(self._OUTLINE_BUILDERS.keys())

    def estimate_word_count(self, outline: list[dict[str, Any]]) -> int:
        """Sum ``target_word_count`` across all top-level sections.

        Args:
            outline: A list of outline entry dicts as returned by :meth:`plan`.

        Returns:
            Total integer word count.
        """
        return sum(entry.get("target_word_count", 0) for entry in outline)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _scale_to_page_target(
        self,
        outline: list[dict[str, Any]],
        target_page_count: int,
    ) -> list[dict[str, Any]]:
        """Proportionally scale body-section word counts to meet *target_page_count*.

        If the sum of all ``target_word_count`` values already reaches at least
        80 % of the target, no scaling is applied.

        Args:
            outline: Raw outline list.
            target_page_count: Desired page count.

        Returns:
            The same list (mutated in-place) with scaled word counts.
        """
        target_words = target_page_count * _WORDS_PER_PAGE
        current_words = self.estimate_word_count(outline)
        body_words = sum(
            e.get("target_word_count", 0)
            for e in outline
            if e.get("section_type") == "body"
        )

        if current_words == 0 or body_words == 0:
            return outline

        # Only scale if we're below 80 % of target
        if current_words >= target_words * 0.8:
            return outline

        scale_factor = (target_words - (current_words - body_words)) / body_words

        for entry in outline:
            if entry.get("section_type") == "body" and entry.get("target_word_count", 0) > 0:
                new_wc = round(entry["target_word_count"] * scale_factor)
                entry["target_word_count"] = new_wc
                entry["target_page_budget"] = round(new_wc / _WORDS_PER_PAGE, 1)

                # Scale subsections proportionally
                sub_total = sum(s.get("target_word_count", 0) for s in entry.get("subsections", []))
                if sub_total > 0:
                    sub_scale = new_wc / sub_total
                    for sub in entry.get("subsections", []):
                        if sub.get("target_word_count", 0) > 0:
                            sub["target_word_count"] = round(sub["target_word_count"] * sub_scale)

        return outline
