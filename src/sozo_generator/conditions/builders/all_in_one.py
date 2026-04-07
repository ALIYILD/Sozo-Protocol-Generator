"""Builder for ALL_IN_ONE Protocol document — matches reference structure.

Reference structure:
  1. Classic TPS Protocols (T1-T5) — per-protocol blocks with params + image
  2. Newronika HDCkit tDCS Protocols (C1-C8) — per-protocol blocks with montage + params
  3. PlatoScience tDCS Protocols (C1-PS–C8-PS) — per-variant blocks
  4. Multimodal Combinations F1-F9 — per-phenotype with TPS + Non-TPS combo tables
  5. Safety, Side Effects & Monitoring — side effects, grading, contraindications
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent
from ...core.enums import Modality


def build_all_in_one_sections(
    condition: ConditionSchema,
    visuals_dir: Optional[str] = None,
) -> list[SectionContent]:
    """Build ALL_IN_ONE document sections matching reference structure."""
    sections = []

    # Resolve visuals directory
    vis_path = None
    if visuals_dir:
        vis_path = Path(visuals_dir)
    else:
        # Try default location
        candidate = Path("outputs/visuals") / condition.slug
        if candidate.exists():
            vis_path = candidate

    # --- Section 1: Classic TPS Protocols ---
    tps_protocols = [p for p in condition.protocols if p.modality == Modality.TPS]
    if tps_protocols:
        tps_subsections = []
        for proto in tps_protocols:
            block = _build_protocol_block(proto, condition, vis_path)
            tps_subsections.append(block)

        sections.append(SectionContent(
            section_id="tps_protocols_section",
            title=f"Classic TPS Protocols ({tps_protocols[0].protocol_id}–{tps_protocols[-1].protocol_id})",
            content=(
                "ALL TPS applications are OFF-LABEL and require explicit Doctor "
                "authorisation and documented patient consent before every treatment block."
            ),
            subsections=tps_subsections,
            callout_boxes=[{
                "text": f"⚠ TPS use in {condition.display_name} is INVESTIGATIONAL. "
                        "These protocols are based on emerging evidence and clinical rationale. "
                        "Explicit informed consent and Doctor authorisation are mandatory.",
                "box_type": "offlabel",
            }],
        ))

    # --- Section 2: Newronika HDCkit tDCS Protocols ---
    tdcs_protocols = [p for p in condition.protocols if p.modality == Modality.TDCS]
    if tdcs_protocols:
        tdcs_subsections = []
        for proto in tdcs_protocols:
            block = _build_protocol_block(proto, condition, vis_path, include_montage=True)
            tdcs_subsections.append(block)

        sections.append(SectionContent(
            section_id="tdcs_protocols_section",
            title=f"Newronika HDCkit tDCS Protocols ({tdcs_protocols[0].protocol_id}–{tdcs_protocols[-1].protocol_id})",
            content=(
                "tDCS protocols apply low-intensity direct current to modulate cortical "
                "excitability. Primary device: Newronika HDCkit (clinical-grade, multi-channel)."
            ),
            subsections=tdcs_subsections,
        ))

    # --- Section 3: PlatoScience tDCS Protocols ---
    if condition.platoscience_variants:
        ps_subsections = []
        for variant in condition.platoscience_variants:
            rows = [[k.replace("_", " ").title(), str(v)]
                    for k, v in variant.parameters.items()]
            ps_subsections.append(SectionContent(
                section_id=f"ps_{variant.variant_id.lower()}",
                title=f"{variant.variant_id} — {variant.label}",
                content=variant.notes or f"PlatoScience variant of protocol {variant.protocol_id}.",
                tables=[{
                    "headers": ["Parameter", "Value"],
                    "rows": rows,
                    "caption": f"PlatoScience parameters — {variant.variant_id}",
                }],
            ))

        first_id = condition.platoscience_variants[0].variant_id
        last_id = condition.platoscience_variants[-1].variant_id
        sections.append(SectionContent(
            section_id="platoscience_section",
            title=f"PlatoScience tDCS Protocols ({first_id} – {last_id})",
            content=(
                "PlatoScience is a wireless consumer/clinical tDCS device that maps to "
                "the Newronika HDCkit protocols above. Each PlatoScience variant uses a "
                "pre-set program (Focus, Think, Relax) corresponding to the clinical montage."
            ),
            subsections=ps_subsections,
        ))

    # --- Section 4: Multimodal Combinations — S-O-Z-O Sequencing Framework ---
    combo_section = _build_phenotype_combo_section(condition)
    if combo_section:
        sections.append(combo_section)

    # --- Section 5: Safety, Side Effects & Monitoring ---
    safety_section = _build_safety_monitoring_section(condition)
    sections.append(safety_section)

    # --- CES Protocols (if any, as appendix) ---
    ces_protocols = [p for p in condition.protocols if p.modality == Modality.CES]
    if ces_protocols:
        ces_subsections = []
        for proto in ces_protocols:
            block = _build_protocol_block(proto, condition, vis_path)
            ces_subsections.append(block)
        sections.append(SectionContent(
            section_id="ces_protocols_section",
            title="CES Protocols (Alpha-Stim®)",
            content="Cranial Electrotherapy Stimulation as adjunct for anxiety, insomnia, and mood support.",
            subsections=ces_subsections,
        ))

    return sections


def _build_protocol_block(
    proto,
    condition: ConditionSchema,
    vis_path: Optional[Path],
    include_montage: bool = False,
) -> SectionContent:
    """Build a self-contained protocol block with params + evidence + optional montage image."""
    evidence_label = {
        "highest": "Guideline", "high": "High (RCT)", "medium": "Moderate",
        "low": "Emerging", "very_low": "Experimental/Pilot", "missing": "No Evidence",
    }.get(proto.evidence_level.value, proto.evidence_level.value)

    # Parameter table
    param_rows = []
    if proto.target_region:
        param_rows.append(["Target Region", proto.target_region])
    for key, val in proto.parameters.items():
        label = key.replace("_", " ").title()
        if isinstance(val, list):
            val = ", ".join(str(v) for v in val)
        param_rows.append([label, str(val)])
    if proto.session_count:
        param_rows.append(["Total Sessions", str(proto.session_count)])
    param_rows.append(["Evidence Level", evidence_label])
    param_rows.append(["Status", "OFF-LABEL — consent required" if proto.off_label else "Approved"])

    # Phenotype applicability
    if proto.phenotype_slugs:
        pheno_str = ", ".join(p.upper() for p in proto.phenotype_slugs)
        param_rows.append(["Target Phenotypes", pheno_str])

    # Network targets
    if proto.network_targets:
        net_str = ", ".join(n.value.upper() for n in proto.network_targets)
        param_rows.append(["Network Targets", net_str])

    tables = [{
        "headers": ["Parameter", "Value"],
        "rows": param_rows,
        "caption": f"Protocol {proto.protocol_id} — {proto.label}",
    }]

    # S-O-Z-O stage table for this protocol
    sozo_rows = [
        ["S — Stabilise", f"Initiate {proto.protocol_id} as primary for target phenotype(s)"],
        ["O — Optimise", "Add adjunct modality if indicated (see Multimodal Combinations)"],
        ["Z — Zone", "Adjust parameters at Week 4 based on response data"],
        ["O — Outcome", "Formal assessment at Week 8-10; classify response"],
    ]
    tables.append({
        "headers": ["S-O-Z-O Stage", f"Application — {proto.protocol_id}"],
        "rows": sozo_rows,
        "caption": f"S-O-Z-O sequencing — {proto.protocol_id}",
    })

    # Figures (montage diagram if available)
    figures = []
    if vis_path and include_montage:
        montage_file = vis_path / f"{condition.slug}_montage_{proto.protocol_id.lower().replace('-', '_')}.png"
        if montage_file.exists():
            figures.append(str(montage_file))

    # Callout boxes
    callouts = []
    if proto.off_label:
        callouts.append({
            "text": f"Protocol {proto.protocol_id} is OFF-LABEL. Requires Doctor authorisation "
                    "and documented informed consent.",
            "box_type": "offlabel",
        })

    title_suffix = f"  [{evidence_label}]"
    return SectionContent(
        section_id=f"proto_{proto.protocol_id.lower().replace('-', '_')}",
        title=f"{proto.protocol_id} — {proto.label}{title_suffix}",
        content=proto.rationale,
        tables=tables,
        figures=figures,
        callout_boxes=callouts,
    )


def _build_phenotype_combo_section(condition: ConditionSchema) -> Optional[SectionContent]:
    """Build F1-F9 multimodal combinations organized by phenotype."""
    if not condition.phenotypes:
        return None

    phenotype_subsections = []
    tps_protocols = [p for p in condition.protocols if p.modality == Modality.TPS]
    non_tps_protocols = [p for p in condition.protocols if p.modality != Modality.TPS]

    for idx, pheno in enumerate(condition.phenotypes, start=1):
        f_id = f"F{idx}"

        # Find protocols matching this phenotype
        matching_tps = [p for p in tps_protocols if pheno.slug in p.phenotype_slugs]
        matching_non_tps = [p for p in non_tps_protocols if pheno.slug in p.phenotype_slugs]

        subsections = []

        # S-O-Z-O summary for this phenotype
        primary = (matching_non_tps[0] if matching_non_tps else
                   matching_tps[0] if matching_tps else None)
        if primary:
            sozo_rows = [
                ["S — Stabilise", f"{primary.protocol_id} ({primary.label})"],
                ["O — Optimise", ", ".join(p.protocol_id for p in (matching_tps[:1] + matching_non_tps[1:2])) or "Maintain primary"],
                ["Z — Zone", "Adjust parameters based on Week 4 response"],
                ["O — Outcome", "Week 8-10 formal assessment"],
            ]
            subsections.append(SectionContent(
                section_id=f"{f_id.lower()}_sozo",
                title=f"{f_id} — S-O-Z-O Summary",
                tables=[{
                    "headers": ["Stage", "Protocol / Action"],
                    "rows": sozo_rows,
                    "caption": f"S-O-Z-O framework — {f_id} {pheno.label}",
                }],
            ))

        # TPS Multimodal Combinations
        if matching_tps:
            tps_combo_rows = []
            for tps in matching_tps:
                for non_tps in matching_non_tps[:3]:
                    tps_combo_rows.append([
                        f"{tps.protocol_id} + {non_tps.protocol_id}",
                        f"{tps.target_abbreviation} TPS + {non_tps.target_abbreviation} {non_tps.modality.value.upper()}",
                        "TPS 2-3×/wk + tDCS daily (non-overlapping)",
                        pheno.label,
                        f"{tps.evidence_level.value} + {non_tps.evidence_level.value}",
                    ])
            if tps_combo_rows:
                subsections.append(SectionContent(
                    section_id=f"{f_id.lower()}_tps_combos",
                    title=f"{f_id} — TPS Multimodal Combinations",
                    tables=[{
                        "headers": ["Combination", "Targets", "Timing", "Indication", "Evidence"],
                        "rows": tps_combo_rows[:5],
                        "caption": f"TPS combinations — {f_id} {pheno.label}",
                    }],
                ))

        # Non-TPS Combinations
        if len(matching_non_tps) > 1:
            non_tps_rows = []
            for i, p1 in enumerate(matching_non_tps):
                for p2 in matching_non_tps[i+1:]:
                    non_tps_rows.append([
                        f"{p1.protocol_id} + {p2.protocol_id}",
                        f"{p1.modality.value.upper()} {p1.target_abbreviation} + {p2.modality.value.upper()} {p2.target_abbreviation}",
                        "Sequential or alternating daily",
                        pheno.label,
                        f"{p1.evidence_level.value} + {p2.evidence_level.value}",
                    ])
            if non_tps_rows:
                subsections.append(SectionContent(
                    section_id=f"{f_id.lower()}_non_tps_combos",
                    title=f"{f_id} — Non-TPS Combinations (Evidence-Based)",
                    tables=[{
                        "headers": ["Combination", "Modalities", "Timing", "Indication", "Evidence"],
                        "rows": non_tps_rows[:5],
                        "caption": f"Non-TPS combinations — {f_id} {pheno.label}",
                    }],
                ))

        if subsections:
            phenotype_subsections.append(SectionContent(
                section_id=f"combo_{f_id.lower()}",
                title=f"{f_id} — {pheno.label}",
                content=pheno.description,
                subsections=subsections,
            ))

    if not phenotype_subsections:
        return None

    return SectionContent(
        section_id="multimodal_combos_section",
        title="Multimodal Combinations — S-O-Z-O Sequencing Framework",
        content=(
            "Each clinical phenotype has a recommended multimodal protocol combination "
            "following the Stabilise–Optimise–Zone–Outcome (S-O-Z-O) framework."
        ),
        subsections=phenotype_subsections,
    )


def _build_safety_monitoring_section(condition: ConditionSchema) -> SectionContent:
    """Build combined Safety, Side Effects & Monitoring section."""
    subsections = []

    # Common Side Effects
    if condition.side_effects:
        rows = []
        for se in condition.side_effects:
            mods = ", ".join(m.value.upper() for m in se.modalities) if se.modalities else "All"
            rows.append([se.effect, se.frequency, se.severity.title(), mods, se.management])
        subsections.append(SectionContent(
            section_id="common_side_effects",
            title="Common Side Effects",
            tables=[{
                "headers": ["Side Effect", "Frequency", "Severity", "Modalities", "Management"],
                "rows": rows,
                "caption": "Common side effects and management",
            }],
        ))

    # Adverse Event Grading
    if condition.adverse_event_grades:
        rows = []
        for ae in condition.adverse_event_grades:
            examples = "; ".join(ae.examples[:3]) if ae.examples else "—"
            rows.append([f"Grade {ae.grade}", ae.label, ae.description, examples, ae.action])
        subsections.append(SectionContent(
            section_id="ae_grading",
            title="Adverse Event Grading",
            tables=[{
                "headers": ["Grade", "Label", "Description", "Examples", "Action"],
                "rows": rows,
                "caption": "Adverse event severity grading system",
            }],
            callout_boxes=[{
                "text": "Grade 3+ events require IMMEDIATE treatment cessation and Doctor escalation within 1 hour.",
                "box_type": "critical",
            }],
        ))

    # Contraindications (split by modality if available)
    if condition.modality_specific_contraindications:
        modalities = sorted(condition.modality_specific_contraindications.keys())
        all_contras = {}
        for mod, contras in condition.modality_specific_contraindications.items():
            for c in contras:
                if c not in all_contras:
                    all_contras[c] = {m: "—" for m in modalities}
                all_contras[c][mod] = "⚠ YES"
        headers = ["Contraindication"] + [m.upper() for m in modalities]
        rows = [[ct] + [cm[m] for m in modalities] for ct, cm in all_contras.items()]
        subsections.append(SectionContent(
            section_id="contraindications_split",
            title="Contraindications",
            tables=[{
                "headers": headers,
                "rows": rows,
                "caption": "Contraindications by modality",
            }],
        ))
    elif condition.contraindications:
        subsections.append(SectionContent(
            section_id="contraindications",
            title="Contraindications",
            content="\n".join(f"• {c}" for c in condition.contraindications),
        ))

    return SectionContent(
        section_id="safety_monitoring_section",
        title="Safety, Side Effects & Monitoring",
        content="The following safety information applies to all neuromodulation protocols in this document.",
        subsections=subsections,
    )
