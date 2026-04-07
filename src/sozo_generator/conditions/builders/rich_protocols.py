"""Builders for rich protocol sections — per-protocol parameters, side effects,
adverse events, PlatoScience variants, multimodal combos, etc.

Each function returns Optional[SectionContent]: None when the relevant data
is empty so the exporter can filter it out silently.
"""
from __future__ import annotations

from typing import Optional

from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent
from ...core.enums import EvidenceLevel


# ---------------------------------------------------------------------------
# 1. Evidence Level Definitions (static — same for all conditions)
# ---------------------------------------------------------------------------

_EVIDENCE_ROWS = [
    [EvidenceLevel.HIGHEST.value, "Highest",
     "Guideline, systematic review, meta-analysis, or large RCT (n > 100)"],
    [EvidenceLevel.HIGH.value, "High",
     "Randomised controlled trial or well-designed controlled trial"],
    [EvidenceLevel.MEDIUM.value, "Medium",
     "Cohort study, narrative review, or expert consensus statement"],
    [EvidenceLevel.LOW.value, "Low",
     "Pilot study, feasibility trial, or small case series"],
    [EvidenceLevel.VERY_LOW.value, "Very Low",
     "Case report, expert opinion, or mechanistic rationale only"],
    [EvidenceLevel.MISSING.value, "Missing",
     "No published evidence found — clinical judgement required"],
]


def build_evidence_level_definitions_section() -> SectionContent:
    """Static table explaining the SOZO evidence grading scheme."""
    return SectionContent(
        section_id="evidence_level_definitions",
        title="Evidence Level Definitions",
        content=(
            "All protocols in this document are graded using the SOZO evidence "
            "classification system. The table below defines each level."
        ),
        tables=[{
            "headers": ["Level Code", "Label", "Definition"],
            "rows": _EVIDENCE_ROWS,
            "caption": "SOZO evidence level classification",
        }],
    )


# ---------------------------------------------------------------------------
# 2. Per-Protocol Detailed Parameter Tables
# ---------------------------------------------------------------------------

def _proto_field(protocol, attr: str, fallback: str = "N/A") -> str:
    """Safely retrieve a protocol field, returning fallback if None/empty."""
    val = getattr(protocol, attr, None)
    if val is None:
        return fallback
    if isinstance(val, list):
        parts = [str(v).strip() for v in val if str(v).strip()]
        return ", ".join(parts) if parts else fallback
    s = str(val).strip()
    return s if s else fallback


def _proto_param(protocol, key: str, fallback: str = "N/A") -> str:
    """Get a value from protocol.parameters dict with fallback."""
    params = protocol.parameters or {}
    val = params.get(key)
    if val is None:
        return fallback
    if isinstance(val, list):
        parts = [str(v).strip() for v in val if str(v).strip()]
        return ", ".join(parts) if parts else fallback
    s = str(val).strip()
    return s if s else fallback


def _build_montage_from_params(protocol) -> str:
    """Build montage string from anode/cathode parameters if montage_roi is absent."""
    params = protocol.parameters or {}
    anode = params.get("anode") or params.get("anode_position")
    cathode = params.get("cathode") or params.get("cathode_position")
    if anode and cathode:
        return f"Anode (+): {anode}; Cathode (−): {cathode}"
    if anode:
        return f"Anode (+): {anode}"
    return "N/A"


def build_per_protocol_parameter_tables(condition: ConditionSchema) -> Optional[SectionContent]:
    """Rich per-protocol tables: full 20-field two-column format matching SOZO Fellow Handbook."""
    if not condition.protocols:
        return None

    subsections = []
    for protocol in condition.protocols:
        params = protocol.parameters or {}

        # --- Table 1: Full 20-field Parameter/Value table ---
        # 1. Protocol Name
        protocol_name = _proto_field(protocol, "protocol_name") if getattr(protocol, "protocol_name", None) else _proto_field(protocol, "label")
        # 2. Intended Phenotype
        phenotypes_str = ", ".join(p.upper() for p in protocol.phenotype_slugs) if protocol.phenotype_slugs else "N/A"
        # 3. Clinical Objective
        clinical_objective = _proto_field(protocol, "clinical_objective") if getattr(protocol, "clinical_objective", None) else _proto_field(protocol, "rationale")
        # 4. Primary Target(s)
        primary_targets = _proto_field(protocol, "primary_targets") if getattr(protocol, "primary_targets", None) else _proto_field(protocol, "target_region")
        # 5. Secondary Target(s)
        secondary_targets = _proto_field(protocol, "secondary_targets")
        # 6. Device / Modality
        device_modality = _proto_field(protocol, "device_name") if getattr(protocol, "device_name", None) else protocol.modality.value.upper()
        # 7. Session Structure
        session_structure = _proto_field(protocol, "session_structure") if getattr(protocol, "session_structure", None) else _proto_param(protocol, "session_structure")
        # 8. Frequency
        frequency = _proto_field(protocol, "frequency") if getattr(protocol, "frequency", None) else _proto_param(protocol, "frequency")
        # 9. Duration
        duration = _proto_field(protocol, "duration") if getattr(protocol, "duration", None) else _proto_param(protocol, "duration")
        # 10. Intensity / Dose
        intensity_dose = _proto_field(protocol, "intensity_dose") if getattr(protocol, "intensity_dose", None) else _proto_param(protocol, "intensity")
        # 11. Montage / ROI
        montage_roi = _proto_field(protocol, "montage_roi") if getattr(protocol, "montage_roi", None) else _build_montage_from_params(protocol)
        # 12. Laterality
        laterality = _proto_field(protocol, "laterality")
        # 13. Treatment Course
        treatment_course = _proto_field(protocol, "treatment_course") if getattr(protocol, "treatment_course", None) else (f"{protocol.session_count} sessions" if protocol.session_count else "N/A")
        # 14. Monitoring
        monitoring = _proto_field(protocol, "monitoring")
        # 15. Expected Response
        expected_response = _proto_field(protocol, "expected_response")
        # 16. Evidence Status
        evidence_status = _proto_field(protocol, "evidence_status") if getattr(protocol, "evidence_status", None) else protocol.evidence_level.value.upper()
        # 17. Cautions
        cautions = _proto_field(protocol, "cautions")
        # 18. When to Escalate
        when_to_escalate = _proto_field(protocol, "when_to_escalate")
        # 19. When to Stop/Modify
        when_to_stop_modify = _proto_field(protocol, "when_to_stop_modify")
        # 20. Clinical Notes
        clinical_notes = _proto_field(protocol, "clinical_notes_extended") if getattr(protocol, "clinical_notes_extended", None) else _proto_field(protocol, "notes")
        # 21. Key Citation(s)
        key_citations = _proto_field(protocol, "key_citations")

        rows = [
            ["Protocol Name", protocol_name],
            ["Intended Phenotype", phenotypes_str],
            ["Clinical Objective", clinical_objective],
            ["Primary Target(s)", primary_targets],
            ["Secondary Target(s)", secondary_targets],
            ["Device / Modality", device_modality],
            ["Session Structure", session_structure],
            ["Frequency", frequency],
            ["Duration", duration],
            ["Intensity / Dose", intensity_dose],
            ["Montage / ROI", montage_roi],
            ["Laterality", laterality],
            ["Treatment Course", treatment_course],
            ["Monitoring", monitoring],
            ["Expected Response", expected_response],
            ["Evidence Status", evidence_status],
            ["Cautions", cautions],
            ["When to Escalate", when_to_escalate],
            ["When to Stop/Modify", when_to_stop_modify],
            ["Clinical Notes", clinical_notes],
            ["Key Citation(s)", key_citations],
        ]

        tables = [{
            "headers": ["Parameter", "Value"],
            "rows": rows,
            "caption": f"Detailed parameters — {protocol.protocol_id} ({protocol.label})",
        }]

        # --- Table 2: S-O-Z-O stage mapping ---
        phenotypes_str = ", ".join(p.upper() for p in protocol.phenotype_slugs) if protocol.phenotype_slugs else "All"
        networks_str = ", ".join(n.value.upper() for n in protocol.network_targets) if protocol.network_targets else "—"
        sozo_rows = [
            ["S — Stabilise", f"Initiate {protocol.protocol_id} ({protocol.target_abbreviation}) for {phenotypes_str} phenotype(s)"],
            ["O — Optimise", f"Combine with adjunct modality targeting {networks_str} network(s)"],
            ["Z — Zone", "Adjust parameters based on Week 4 response. Transition to maintenance frequency."],
            ["O — Outcome", "Formal assessment at Week 8-10. Apply responder classification."],
        ]
        tables.append({
            "headers": ["S-O-Z-O Stage", f"Application for {protocol.protocol_id}"],
            "rows": sozo_rows,
            "caption": f"S-O-Z-O sequencing — {protocol.protocol_id}",
        })

        # --- Table 3: Evidence-based combination recommendations ---
        combo_rows = []
        for other in condition.protocols:
            if other.protocol_id == protocol.protocol_id:
                continue
            if other.modality == protocol.modality:
                continue
            # Check for overlapping phenotypes or networks
            shared_pheno = set(protocol.phenotype_slugs) & set(other.phenotype_slugs)
            shared_net = set(protocol.network_targets) & set(other.network_targets)
            if shared_pheno or shared_net:
                combo_rows.append([
                    f"{protocol.protocol_id} + {other.protocol_id}",
                    f"{protocol.modality.value.upper()} {protocol.target_abbreviation} + {other.modality.value.upper()} {other.target_abbreviation}",
                    "Sequential: primary daily, adjunct 2-3×/week",
                    ", ".join(p.upper() for p in shared_pheno) if shared_pheno else phenotypes_str,
                    f"{protocol.evidence_level.value} + {other.evidence_level.value}",
                ])
        if combo_rows:
            tables.append({
                "headers": ["Combination", "Modalities", "Timing", "Indication", "Evidence"],
                "rows": combo_rows[:5],  # Limit to top 5 combinations
                "caption": f"Evidence-based combinations for {protocol.protocol_id}",
            })

        callouts = []
        if protocol.off_label:
            callouts.append({
                "text": f"Protocol {protocol.protocol_id} is OFF-LABEL. "
                        "Requires explicit Doctor authorisation and documented patient consent.",
                "box_type": "offlabel",
            })

        content = protocol.rationale
        if protocol.notes:
            content += f"\n\nNote: {protocol.notes}"

        subsections.append(SectionContent(
            section_id=f"params_{protocol.protocol_id}",
            title=f"Protocol {protocol.protocol_id}: {protocol.label}",
            content=content,
            tables=tables,
            callout_boxes=callouts,
        ))

    return SectionContent(
        section_id="per_protocol_parameters",
        title="Per-Protocol Detailed Parameters",
        content=(
            "The following tables provide full parameter specifications for each "
            f"neuromodulation protocol recommended for {condition.display_name}. "
            "Each protocol includes S-O-Z-O stage mapping and evidence-based combination recommendations."
        ),
        subsections=subsections,
    )


# ---------------------------------------------------------------------------
# 2b. Phenotype-Protocol Cross-Reference Matrix
# ---------------------------------------------------------------------------

def build_phenotype_protocol_matrix(condition: ConditionSchema) -> Optional[SectionContent]:
    """Cross-reference table: phenotypes × protocols showing which apply."""
    if not condition.phenotypes or not condition.protocols:
        return None

    headers = ["Phenotype"] + [p.protocol_id for p in condition.protocols]
    rows = []
    for pheno in condition.phenotypes:
        row = [pheno.label]
        for proto in condition.protocols:
            if pheno.slug in proto.phenotype_slugs:
                row.append("✓")
            else:
                row.append("—")
        rows.append(row)

    return SectionContent(
        section_id="phenotype_protocol_matrix",
        title="Phenotype–Protocol Cross-Reference",
        content=(
            "The following matrix shows which neuromodulation protocols are recommended "
            f"for each clinical phenotype of {condition.display_name}."
        ),
        tables=[{
            "headers": headers,
            "rows": rows,
            "caption": "Phenotype–protocol assignment matrix",
        }],
    )


# ---------------------------------------------------------------------------
# 2c. Device Specification Tables
# ---------------------------------------------------------------------------

def build_device_specifications_section(condition: ConditionSchema) -> Optional[SectionContent]:
    """Device specification tables for each modality used in this condition."""
    if not condition.protocols:
        return None

    # Collect unique devices
    devices_seen = set()
    modalities_used = set()
    for p in condition.protocols:
        modalities_used.add(p.modality.value)
        device = p.parameters.get("device", "")
        if device:
            devices_seen.add(device)

    subsections = []

    # tDCS devices
    from ...core.enums import Modality
    if Modality.TDCS.value in modalities_used:
        subsections.append(SectionContent(
            section_id="device_tdcs",
            title="tDCS Device Specifications",
            tables=[{
                "headers": ["Specification", "Newronika HDCkit", "PlatoScience"],
                "rows": [
                    ["Type", "Clinical tDCS system", "Wireless consumer/clinical tDCS"],
                    ["Channels", "Up to 8 (HD capability)", "1-2"],
                    ["Current Range", "0.1–4.0 mA", "0.5–2.0 mA"],
                    ["Max Current Density", "Configurable per electrode", "Fixed based on electrode"],
                    ["Electrode Size", "Standard 35 cm² or HD 1 cm²", "Standard sponge"],
                    ["Session Timer", "Programmable 1-40 min", "Pre-set 20/30 min programs"],
                    ["Ramp Up/Down", "Configurable 10-60 sec", "30 sec automatic"],
                    ["Programs", "Custom clinician-programmed", "Focus, Think, Relax, Create"],
                    ["Impedance Check", "Real-time with abort", "Pre-session check"],
                    ["Clinical Setting", "In-clinic (primary)", "In-clinic or home-based"],
                ],
                "caption": "tDCS device comparison — Newronika HDCkit vs PlatoScience",
            }],
        ))

    # TPS device
    if Modality.TPS.value in modalities_used:
        subsections.append(SectionContent(
            section_id="device_tps",
            title="TPS Device Specifications — NEUROLITH®",
            tables=[{
                "headers": ["Specification", "Value"],
                "rows": [
                    ["Manufacturer", "Storz Medical AG (Switzerland)"],
                    ["Device", "NEUROLITH® TPS System"],
                    ["Technology", "Transcranial Pulse Stimulation (focused shockwave)"],
                    ["Penetration Depth", "Up to 8 cm (deep brain structures)"],
                    ["Pulse Energy", "0.10–0.40 mJ/mm²"],
                    ["Frequency", "1–8 Hz (typical: 4–5 Hz)"],
                    ["Pulses per Session", "200–1000 (typical: 300–600)"],
                    ["Navigation", "Neuronavigation-guided (MRI-based)"],
                    ["Session Duration", "20–30 min"],
                    ["Regulatory Status", "CE marked (EU). OFF-LABEL for non-Alzheimer's conditions."],
                ],
                "caption": "NEUROLITH® TPS system specifications",
            }],
            callout_boxes=[{
                "text": "TPS use for this condition is INVESTIGATIONAL and OFF-LABEL. "
                        "Requires Doctor authorisation and documented informed consent for every treatment block.",
                "box_type": "offlabel",
            }],
        ))

    # CES device
    if Modality.CES.value in modalities_used:
        subsections.append(SectionContent(
            section_id="device_ces",
            title="CES Device Specifications — Alpha-Stim®",
            tables=[{
                "headers": ["Specification", "Value"],
                "rows": [
                    ["Manufacturer", "Electromedical Products International"],
                    ["Device", "Alpha-Stim® AID / M"],
                    ["Technology", "Cranial Electrotherapy Stimulation"],
                    ["Waveform", "Modified square wave, biphasic"],
                    ["Frequency", "0.5 Hz (fixed)"],
                    ["Current Range", "10–600 µA (typical: 100–300 µA)"],
                    ["Electrode", "Earclip electrodes (bilateral earlobe)"],
                    ["Session Duration", "20–60 min"],
                    ["Regulatory Status", "FDA cleared for anxiety, depression, insomnia"],
                ],
                "caption": "Alpha-Stim® CES device specifications",
            }],
        ))

    if not subsections:
        return None

    return SectionContent(
        section_id="device_specifications",
        title="Device Specifications & Technical Information",
        content=(
            "The following tables provide technical specifications for the neuromodulation "
            f"devices used in {condition.display_name} protocols at SOZO Brain Center."
        ),
        subsections=subsections,
    )


# ---------------------------------------------------------------------------
# 2d. Per-Phenotype S-O-Z-O Treatment Tables
# ---------------------------------------------------------------------------

def build_per_phenotype_sozo_tables(condition: ConditionSchema) -> Optional[SectionContent]:
    """For each phenotype, generate a treatment plan table showing protocol assignments."""
    if not condition.phenotypes or not condition.protocols:
        return None

    subsections = []
    for pheno in condition.phenotypes:
        # Find protocols that target this phenotype
        matching = [p for p in condition.protocols if pheno.slug in p.phenotype_slugs]
        if not matching:
            continue

        # Build protocol assignment table
        proto_rows = []
        for p in matching:
            proto_rows.append([
                p.protocol_id, p.label, p.modality.value.upper(),
                p.target_abbreviation, p.evidence_level.value,
            ])

        # Build S-O-Z-O plan for this phenotype
        primary = matching[0] if matching else None
        adjuncts = matching[1:] if len(matching) > 1 else []
        sozo_rows = [
            ["S — Stabilise", f"Initiate {primary.protocol_id} ({primary.label})" if primary else "—",
             "Week 1-2"],
            ["O — Optimise", f"Add {', '.join(p.protocol_id for p in adjuncts[:2])}" if adjuncts else "Maintain primary protocol",
             "Week 3-5"],
            ["Z — Zone", "Fine-tune parameters based on response data", "Week 4-6"],
            ["O — Outcome", "Formal assessment and response classification", "Week 8-10"],
        ]

        subsections.append(SectionContent(
            section_id=f"sozo_{pheno.slug}",
            title=f"S-O-Z-O Plan: {pheno.label}",
            content=pheno.description,
            tables=[
                {
                    "headers": ["Protocol", "Label", "Modality", "Target", "Evidence"],
                    "rows": proto_rows,
                    "caption": f"Protocol assignments for {pheno.label}",
                },
                {
                    "headers": ["S-O-Z-O Stage", "Action", "Timeline"],
                    "rows": sozo_rows,
                    "caption": f"S-O-Z-O treatment plan — {pheno.label}",
                },
            ],
        ))

    if not subsections:
        return None

    return SectionContent(
        section_id="per_phenotype_sozo",
        title="Per-Phenotype S-O-Z-O Treatment Plans",
        content=(
            "The following section provides phenotype-specific treatment plans "
            "with protocol assignments and S-O-Z-O sequencing."
        ),
        subsections=subsections,
    )


# ---------------------------------------------------------------------------
# 3. PlatoScience Protocol Variants
# ---------------------------------------------------------------------------

def build_platoscience_variants_section(condition: ConditionSchema) -> Optional[SectionContent]:
    if not condition.platoscience_variants:
        return None

    rows = []
    for v in condition.platoscience_variants:
        params_str = "; ".join(f"{k}: {val}" for k, val in v.parameters.items())
        rows.append([v.variant_id, v.protocol_id, v.label, params_str, v.notes or "—"])

    return SectionContent(
        section_id="platoscience_variants",
        title="PlatoScience Protocol Variants",
        content=(
            "The following table lists PlatoScience-specific protocol variants. "
            "These use PlatoScience device programs mapped to the parent tDCS protocol."
        ),
        tables=[{
            "headers": ["Variant ID", "Parent Protocol", "Label", "Parameters", "Notes"],
            "rows": rows,
            "caption": "PlatoScience protocol variants",
        }],
    )


# ---------------------------------------------------------------------------
# 4. Multimodal S-O-Z-O Combinations
# ---------------------------------------------------------------------------

def build_multimodal_combos_section(condition: ConditionSchema) -> Optional[SectionContent]:
    if not condition.multimodal_combos:
        return None

    subsections = []
    for combo in condition.multimodal_combos:
        phenotypes_str = ", ".join(combo.phenotype_slugs) if combo.phenotype_slugs else "All phenotypes"
        rows = [
            ["Combination ID", combo.combo_id],
            ["Target Phenotype(s)", phenotypes_str],
            ["TPS Protocol", combo.tps_protocol_id or "None"],
            ["Non-TPS Protocol(s)", ", ".join(combo.non_tps_protocol_ids) if combo.non_tps_protocol_ids else "None"],
            ["Sequencing", combo.sequencing_notes or "See clinician guidance"],
        ]

        subsections.append(SectionContent(
            section_id=f"combo_{combo.combo_id}",
            title=f"{combo.combo_id}: {combo.label}",
            content=combo.rationale,
            tables=[{
                "headers": ["Field", "Value"],
                "rows": rows,
                "caption": f"Multimodal combination — {combo.combo_id}",
            }],
        ))

    return SectionContent(
        section_id="multimodal_combos",
        title="S-O-Z-O Multimodal Combinations",
        content=(
            "The following combinations integrate multiple neuromodulation modalities "
            "within the Stabilise–Optimise–Zone–Outcome (S-O-Z-O) framework. "
            "Each combination is matched to specific clinical phenotype(s)."
        ),
        subsections=subsections,
    )


# ---------------------------------------------------------------------------
# 5. S-O-Z-O Sequencing Framework
# ---------------------------------------------------------------------------

def build_sequencing_framework_section(condition: ConditionSchema) -> Optional[SectionContent]:
    if not condition.sequencing_framework:
        return None

    rows = [[stage, desc] for stage, desc in condition.sequencing_framework.items()]

    return SectionContent(
        section_id="sequencing_framework",
        title="S-O-Z-O Sequencing Framework",
        content=(
            "Treatment delivery follows the four-stage Stabilise–Optimise–Zone–Outcome "
            f"(S-O-Z-O) sequencing framework adapted for {condition.display_name}."
        ),
        tables=[{
            "headers": ["Stage", "Description"],
            "rows": rows,
            "caption": "S-O-Z-O sequencing framework",
        }],
    )


# ---------------------------------------------------------------------------
# 6. Modality-Specific Contraindications (split table)
# ---------------------------------------------------------------------------

def build_modality_contraindications_section(condition: ConditionSchema) -> Optional[SectionContent]:
    if not condition.modality_specific_contraindications:
        return None

    # Build comparison table: rows = contraindication text, columns = modalities
    modalities = sorted(condition.modality_specific_contraindications.keys())
    # Collect all unique contraindications across modalities
    all_contras: dict[str, dict[str, str]] = {}
    for mod, contras in condition.modality_specific_contraindications.items():
        for c in contras:
            if c not in all_contras:
                all_contras[c] = {m: "—" for m in modalities}
            all_contras[c][mod] = "⚠ YES"

    headers = ["Contraindication"] + [m.upper() for m in modalities]
    rows = []
    for contra_text, mod_map in all_contras.items():
        rows.append([contra_text] + [mod_map[m] for m in modalities])

    return SectionContent(
        section_id="modality_contraindications",
        title="Contraindications by Modality",
        content=(
            "The following table shows which contraindications apply to each "
            "neuromodulation modality. Clinicians must check modality-specific "
            "exclusions before initiating treatment."
        ),
        tables=[{
            "headers": headers,
            "rows": rows,
            "caption": "Contraindications split by modality",
        }],
    )


# ---------------------------------------------------------------------------
# 7. Common Side Effects
# ---------------------------------------------------------------------------

def build_side_effects_section(condition: ConditionSchema) -> Optional[SectionContent]:
    if not condition.side_effects:
        return None

    rows = []
    for se in condition.side_effects:
        mods = ", ".join(m.value.upper() for m in se.modalities) if se.modalities else "All"
        rows.append([se.effect, se.frequency, mods, se.severity.title(), se.management])

    return SectionContent(
        section_id="side_effects",
        title="Common Side Effects",
        content=(
            "The following table describes commonly reported side effects of "
            "neuromodulation procedures, their frequency, and recommended management."
        ),
        tables=[{
            "headers": ["Side Effect", "Frequency", "Modalities", "Severity", "Management"],
            "rows": rows,
            "caption": "Common side effects and management",
        }],
    )


# ---------------------------------------------------------------------------
# 8. Adverse Event Grading
# ---------------------------------------------------------------------------

def build_adverse_event_grading_section(condition: ConditionSchema) -> Optional[SectionContent]:
    if not condition.adverse_event_grades:
        return None

    rows = []
    for ae in condition.adverse_event_grades:
        examples_str = "; ".join(ae.examples) if ae.examples else "—"
        rows.append([
            f"Grade {ae.grade}",
            ae.label,
            ae.description,
            examples_str,
            ae.action,
        ])

    return SectionContent(
        section_id="adverse_event_grading",
        title="Adverse Event Grading System",
        content=(
            "All adverse events during neuromodulation treatment are classified "
            "using the following 4-grade severity scale. Grade 3+ events require "
            "immediate treatment discontinuation."
        ),
        tables=[{
            "headers": ["Grade", "Label", "Description", "Examples", "Required Action"],
            "rows": rows,
            "caption": "Adverse event severity grading",
        }],
        callout_boxes=[{
            "text": "Grade 3 or 4 adverse events require IMMEDIATE treatment discontinuation "
                    "and escalation to the supervising Doctor. Document the event in the patient "
                    "record within 24 hours.",
            "box_type": "critical",
        }],
    )


# ---------------------------------------------------------------------------
# 9. Home-Based Treatment
# ---------------------------------------------------------------------------

def build_home_based_treatment_section(condition: ConditionSchema) -> Optional[SectionContent]:
    if not condition.home_based_protocols:
        return None

    subsections = []
    for hp in condition.home_based_protocols:
        param_rows = [[k.replace("_", " ").title(), str(v)] for k, v in hp.parameters.items()]

        eligibility_text = "\n".join(f"• {c}" for c in hp.eligibility_criteria) if hp.eligibility_criteria else "See clinician assessment"
        safety_text = "\n".join(f"• {n}" for n in hp.safety_notes) if hp.safety_notes else "Standard safety precautions apply"
        monitoring_text = "\n".join(f"• {r}" for r in hp.monitoring_requirements) if hp.monitoring_requirements else "Weekly clinician review"

        subsections.append(SectionContent(
            section_id=f"home_{hp.protocol_id}",
            title=f"Home Protocol: {hp.label}",
            content=f"Device: {hp.device}\nModality: {hp.modality.value.upper()}",
            tables=[
                {
                    "headers": ["Parameter", "Value"],
                    "rows": param_rows,
                    "caption": f"Home-based parameters — {hp.label}",
                },
                {
                    "headers": ["Requirement Type", "Details"],
                    "rows": [
                        ["Eligibility", eligibility_text],
                        ["Safety Notes", safety_text],
                        ["Monitoring", monitoring_text],
                    ],
                    "caption": f"Eligibility and monitoring — {hp.label}",
                },
            ],
            callout_boxes=[{
                "text": "Home-based treatment requires completion of at least 5 supervised "
                        "in-clinic sessions before initiation. Remote monitoring must be active.",
                "box_type": "governance",
            }],
        ))

    return SectionContent(
        section_id="home_based_treatment",
        title="Home-Based Treatment Protocols",
        content=(
            "Selected patients who meet eligibility criteria may transition to "
            "home-based neuromodulation under remote clinical supervision."
        ),
        subsections=subsections,
    )


# ---------------------------------------------------------------------------
# 10. Governance Rules
# ---------------------------------------------------------------------------

def build_governance_section(condition: ConditionSchema) -> Optional[SectionContent]:
    if not condition.governance_rules:
        return None

    callouts = [
        {"text": rule, "box_type": "governance"}
        for rule in condition.governance_rules
    ]

    return SectionContent(
        section_id="governance",
        title="Governance Rules",
        content=(
            "The following governance rules are mandatory for all clinicians "
            f"delivering neuromodulation treatment for {condition.display_name}. "
            "Violations must be reported to the supervising Doctor."
        ),
        callout_boxes=callouts,
    )
