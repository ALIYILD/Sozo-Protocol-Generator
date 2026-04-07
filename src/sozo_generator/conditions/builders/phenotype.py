"""Builder for clinical phenotype classification sections."""
from __future__ import annotations

from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent
from ...core.enums import Modality


def build_phenotype_section(condition: ConditionSchema) -> SectionContent:
    """Basic phenotype summary table (used in Evidence-Based, ALL_IN_ONE)."""
    phenotype_rows = []
    for ph in condition.phenotypes:
        phenotype_rows.append([
            ph.label,
            ph.description,
            ", ".join(ph.key_features[:3]),
            ", ".join(n.value.upper() for n in ph.primary_networks),
            ", ".join(m.value.upper() for m in ph.preferred_modalities),
        ])

    return SectionContent(
        section_id="phenotypes",
        title=f"Clinical Phenotypes of {condition.display_name}",
        content=(
            f"{condition.display_name} presents with distinct clinical phenotypes that guide "
            "neuromodulation target selection. Phenotype identification is the first step "
            "in the FNON Five-Level Clinical Decision Pathway."
        ),
        tables=[{
            "headers": ["Phenotype", "Description", "Key Features", "Primary Network(s)", "Preferred Modality(ies)"],
            "rows": phenotype_rows,
            "caption": f"Clinical phenotype classification for {condition.display_name}",
        }] if phenotype_rows else [],
        is_placeholder=not bool(condition.phenotypes),
        review_flags=["No phenotypes defined — clinical review required"] if not condition.phenotypes else [],
    )


def build_phenotype_classification_algorithm(condition: ConditionSchema) -> SectionContent:
    """8-step phenotype classification algorithm with detailed tables (for PHENOTYPE_CLASSIFICATION doc)."""
    if not condition.phenotypes:
        return SectionContent(
            section_id="phenotype_algorithm",
            title="Phenotype Classification Algorithm",
            content="[REVIEW REQUIRED: No phenotypes defined]",
            is_placeholder=True,
        )

    steps = []

    # Step 1: Data Collection
    steps.append(SectionContent(
        section_id="step_1",
        title="Step 1: Clinical Data Collection",
        content="Collect comprehensive clinical data for phenotype determination.",
        tables=[{
            "headers": ["Data Domain", "Source", "Key Items"],
            "rows": [
                ["Motor symptoms", "Clinical examination", "Tremor, rigidity, bradykinesia, gait, posture"],
                ["Cognitive function", "MoCA / neuropsychological battery", "Executive function, memory, attention, fluency"],
                ["Mood and affect", "PHQ-9 / GAD-7 / clinical interview", "Depression, anxiety, apathy, impulse control"],
                ["Functional impact", "Patient/caregiver report", "ADL limitations, quality of life, work capacity"],
                ["Medication response", "Treatment history", "Current regimen, response pattern, side effects"],
                ["Imaging (if available)", "MRI / fMRI / QEEG", "Structural changes, network connectivity"],
            ],
            "caption": "Step 1 — Clinical data collection requirements",
        }],
    ))

    # Step 2: Phenotype Identification — summary + per-phenotype detail
    pheno_rows = []
    for ph in condition.phenotypes:
        features = "; ".join(ph.key_features[:4]) if ph.key_features else "—"
        pheno_rows.append([ph.slug.upper(), ph.label, features])

    step2_subsections = []
    for ph in condition.phenotypes:
        feature_rows = [[f, "☐ Present  ☐ Absent"] for f in ph.key_features] if ph.key_features else []
        if feature_rows:
            step2_subsections.append(SectionContent(
                section_id=f"pheno_detail_{ph.slug}",
                title=f"{ph.slug.upper()}: {ph.label}",
                content=ph.description,
                tables=[{
                    "headers": ["Feature", "Assessment"],
                    "rows": feature_rows,
                    "caption": f"Phenotype scoring — {ph.label}",
                }],
            ))

    steps.append(SectionContent(
        section_id="step_2",
        title="Step 2: Phenotype Identification",
        content="Match clinical presentation to the phenotype categories below. Score each feature.",
        tables=[{
            "headers": ["Code", "Phenotype Label", "Key Distinguishing Features"],
            "rows": pheno_rows,
            "caption": "Step 2 — Phenotype identification criteria",
        }],
        subsections=step2_subsections,
    ))

    # Step 3: Network Dysfunction Mapping — summary + per-phenotype network detail
    net_rows = []
    for ph in condition.phenotypes:
        primary = ", ".join(n.value.upper() for n in ph.primary_networks)
        secondary = ", ".join(n.value.upper() for n in ph.secondary_networks) if ph.secondary_networks else "—"
        net_rows.append([ph.slug.upper(), ph.label, primary, secondary])

    step3_tables = [{
        "headers": ["Code", "Phenotype", "Primary Network(s)", "Secondary Network(s)"],
        "rows": net_rows,
        "caption": "Step 3 — Phenotype-to-network mapping",
    }]
    # Add network dysfunction severity matrix
    if condition.network_profiles:
        severity_rows = []
        for np in condition.network_profiles:
            severity_rows.append([
                np.network.value.upper(),
                np.dysfunction.value,
                np.severity,
                "✓" if np.primary else "—",
                np.relevance[:80] if np.relevance else "—",
            ])
        step3_tables.append({
            "headers": ["Network", "Dysfunction", "Severity", "Primary?", "Clinical Relevance"],
            "rows": severity_rows,
            "caption": "Step 3 — Network dysfunction severity profile",
        })

    steps.append(SectionContent(
        section_id="step_3",
        title="Step 3: Network Dysfunction Mapping",
        content="Map each phenotype to its primary and secondary dysfunctional networks.",
        tables=step3_tables,
    ))

    # Step 4: tDCS Target Selection — with montage detail per phenotype
    tdcs_summary_rows = []
    step4_subsections = []
    for ph in condition.phenotypes:
        target = ph.tdcs_target or "See protocol selection"
        tdcs_summary_rows.append([ph.slug.upper(), ph.label, target])

        # Find matching tDCS protocols for this phenotype
        matching_tdcs = [p for p in condition.protocols
                        if p.modality.value == "tdcs" and ph.slug in p.phenotype_slugs]
        if matching_tdcs:
            montage_rows = []
            for p in matching_tdcs:
                anode = p.parameters.get("anode", "—")
                cathode = p.parameters.get("cathode", "—")
                intensity = p.parameters.get("intensity", "2.0 mA")
                duration = p.parameters.get("duration", "20 min")
                montage_rows.append([p.protocol_id, anode, cathode, intensity, duration, p.evidence_level.value])
            step4_subsections.append(SectionContent(
                section_id=f"montage_{ph.slug}",
                title=f"Montage Detail: {ph.label}",
                tables=[{
                    "headers": ["Protocol", "Anode", "Cathode", "Intensity", "Duration", "Evidence"],
                    "rows": montage_rows,
                    "caption": f"tDCS montage specifications — {ph.label}",
                }],
            ))

    steps.append(SectionContent(
        section_id="step_4",
        title="Step 4: tDCS Montage Selection by Phenotype",
        content="Select tDCS electrode montage based on identified phenotype.",
        tables=[{
            "headers": ["Code", "Phenotype", "Recommended tDCS Target / Montage"],
            "rows": tdcs_summary_rows,
            "caption": "Step 4 — Phenotype-to-tDCS montage mapping",
        }],
        subsections=step4_subsections,
    ))

    # Step 5: TPS Protocol Selection — with per-phenotype TPS detail
    tps_summary_rows = []
    step5_subsections = []
    for ph in condition.phenotypes:
        target = ph.tps_target or "Not indicated / see clinician"
        tps_summary_rows.append([ph.slug.upper(), ph.label, target])

        matching_tps = [p for p in condition.protocols
                       if p.modality.value == "tps" and ph.slug in p.phenotype_slugs]
        if matching_tps:
            tps_detail_rows = []
            for p in matching_tps:
                pulses = p.parameters.get("pulses", "—")
                energy = p.parameters.get("energy", "—")
                freq = p.parameters.get("frequency", "—")
                tps_detail_rows.append([p.protocol_id, p.target_region, pulses, energy, freq, p.evidence_level.value])
            step5_subsections.append(SectionContent(
                section_id=f"tps_{ph.slug}",
                title=f"TPS Detail: {ph.label}",
                tables=[{
                    "headers": ["Protocol", "Target Region", "Pulses", "Energy", "Frequency", "Evidence"],
                    "rows": tps_detail_rows,
                    "caption": f"TPS parameters — {ph.label}",
                }],
            ))

    steps.append(SectionContent(
        section_id="step_5",
        title="Step 5: TPS Protocol Selection",
        content="Determine TPS targeting if Doctor-authorised. All TPS is OFF-LABEL.",
        tables=[{
            "headers": ["Code", "Phenotype", "Recommended TPS Target"],
            "rows": tps_summary_rows,
            "caption": "Step 5 — Phenotype-to-TPS protocol assignment",
        }],
        subsections=step5_subsections,
        callout_boxes=[{
            "text": "All TPS applications are OFF-LABEL. Requires explicit Doctor authorisation and documented informed consent.",
            "box_type": "offlabel",
        }],
    ))

    # Step 6: Combination & Adjunct Strategy
    combo_rows = []
    for ph in condition.phenotypes:
        modalities = ", ".join(m.value.upper() for m in ph.preferred_modalities)
        combo_rows.append([ph.slug.upper(), ph.label, modalities,
                          "CES if anxiety/sleep" if Modality.CES in ph.preferred_modalities else "Per clinical need"])
    steps.append(SectionContent(
        section_id="step_6",
        title="Step 6: Combination & Adjunct Strategy",
        content="Determine multimodal combination strategy based on phenotype.",
        tables=[{
            "headers": ["Code", "Phenotype", "Primary Modalities", "Adjunct Recommendation"],
            "rows": combo_rows,
            "caption": "Step 6 — Multimodal combination strategy by phenotype",
        }],
    ))

    # Step 7: Treatment Sequencing
    steps.append(SectionContent(
        section_id="step_7",
        title="Step 7: Treatment Sequencing Algorithm",
        content="Apply S-O-Z-O framework to sequence treatment delivery.",
        tables=[{
            "headers": ["S-O-Z-O Stage", "Week", "Focus", "Key Action"],
            "rows": [
                ["S — Stabilise", "1-2", "Address most acute burden", "Initiate primary protocol"],
                ["O — Optimise", "3-5", "Add secondary modalities", "Introduce TPS / adjuncts"],
                ["Z — Zone", "4-6", "Fine-tune parameters", "Adjust based on Week 4 data"],
                ["O — Outcome", "8-10", "Formal assessment", "Classify response; plan maintenance"],
            ],
            "caption": "Step 7 — S-O-Z-O treatment sequencing timeline",
        }],
    ))

    # Step 8: Response Evaluation
    steps.append(SectionContent(
        section_id="step_8",
        title="Step 8: Response Evaluation & Maintenance",
        content="Classify response and plan next steps.",
        tables=[{
            "headers": ["Response Category", "Criteria", "Next Step"],
            "rows": [
                ["Responder", "≥30% improvement in primary measure", "Maintenance protocol: taper frequency"],
                ["Partial Responder", "15-29% improvement", "Reassess phenotype; adjust protocol; extend block"],
                ["Non-Responder", "<15% improvement at Week 8", "Level 5 FNON reassessment; protocol switch"],
            ],
            "caption": "Step 8 — Response classification and next steps",
        }],
    ))

    # Summary: Complete Protocol Assignment
    summary_headers = ["Phenotype"] + [p.protocol_id for p in condition.protocols[:10]]
    summary_rows = []
    for ph in condition.phenotypes:
        row = [ph.label]
        for proto in condition.protocols[:10]:
            row.append("✓" if ph.slug in proto.phenotype_slugs else "—")
        summary_rows.append(row)

    steps.append(SectionContent(
        section_id="protocol_summary",
        title="Complete Protocol Assignment Summary",
        tables=[{
            "headers": summary_headers,
            "rows": summary_rows,
            "caption": "Complete phenotype-to-protocol assignment matrix",
        }] if summary_rows else [],
    ))

    return SectionContent(
        section_id="phenotype_algorithm",
        title=f"Phenotype Classification Algorithm — {condition.display_name}",
        content=(
            "Follow the 8-step algorithm below to classify the patient's phenotype "
            "and map to the optimal neuromodulation protocol."
        ),
        subsections=steps,
    )
