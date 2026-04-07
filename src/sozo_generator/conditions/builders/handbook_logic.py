"""Builder for clinical handbook sections — 9-stage patient journey + appendices."""
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
    "stage_9": "Stage 9: Discharge & Transition Planning",
}

STAGE_DETAILS = {
    "stage_1": {
        "purpose": "Ensure patient meets basic eligibility before booking comprehensive assessment",
        "procedures": [
            "Screen for absolute contraindications (implants, active seizures, skull defects)",
            "Collect demographic information and referral details",
            "Send pre-appointment instructions (medication timing, what to bring)",
            "Schedule comprehensive assessment appointment (90 min slot)",
            "Confirm appointment 48 hours prior",
        ],
        "checklist": [
            "Referral source documented", "Contraindication pre-screen completed",
            "Appointment confirmation sent", "Pre-appointment instructions sent",
        ],
        "output": "Pre-screening record, appointment confirmation",
        "forms": "Pre-Screening Form, Appointment Confirmation Letter",
    },
    "stage_2": {
        "purpose": "Obtain legally valid informed consent for all planned neuromodulation modalities",
        "procedures": [
            "Welcome patient and explain session plan",
            "Present neuromodulation modalities and expected outcomes",
            "Disclose off-label status of TPS (if applicable)",
            "Answer patient questions — allow adequate time",
            "Obtain written consent signatures (patient + clinician)",
            "File consent in patient record",
        ],
        "checklist": [
            "General neuromodulation consent signed", "TPS off-label consent signed (if applicable)",
            "Patient information leaflet provided", "Copy given to patient",
        ],
        "output": "Signed consent forms filed in patient record",
        "forms": "General Consent Form, TPS Off-Label Consent, Patient Information Leaflet",
    },
    "stage_3": {
        "purpose": "Establish psychological baseline and patient-reported symptom profile",
        "procedures": [
            "Conduct structured clinical interview (chief complaints, psychiatric history)",
            "Screen for suicidal ideation — ESCALATE IMMEDIATELY if active",
            "Administer SOZO PRS (Patient Rating System) baseline",
            "Document treatment history and current medications",
            "Record functional limitations",
        ],
        "checklist": [
            "Structured interview completed", "Suicidal ideation screened",
            "SOZO PRS baseline recorded", "Medication list documented",
            "Treatment history documented", "Functional limitations noted",
        ],
        "output": "Psychological Intake Report, PRS Baseline Record",
        "forms": "Psychological Intake Form, SOZO PRS Baseline Form",
    },
    "stage_4": {
        "purpose": "Complete clinical assessment and determine phenotype classification",
        "procedures": [
            "Administer condition-specific assessment scales",
            "Conduct focused clinical examination",
            "Apply phenotype classification algorithm",
            "Document phenotype assignment with supporting data",
            "Conduct cognitive and mood screening (MoCA, HAM-D/PHQ-9)",
        ],
        "checklist": [
            "Primary assessment scale completed", "Clinical examination completed",
            "Cognitive screening completed", "Mood screening completed",
            "Phenotype classified", "All scores documented",
        ],
        "output": "Clinical Examination Report, Phenotype Classification Record",
        "forms": "Clinical Examination Checklist, Phenotype Classification Form",
    },
    "stage_5": {
        "purpose": "Select optimal neuromodulation protocol based on phenotype and network assessment",
        "procedures": [
            "Review phenotype classification and assessment results",
            "Apply phenotype-to-protocol selection algorithm",
            "Select tDCS montage (primary modality)",
            "Assess TPS suitability (Doctor authorisation required)",
            "Determine adjunct modalities (CES, taVNS)",
            "Apply S-O-Z-O sequencing framework",
            "Obtain Doctor sign-off on treatment plan",
        ],
        "checklist": [
            "Phenotype-protocol algorithm applied", "Primary tDCS montage selected",
            "TPS decision documented (with/without)", "Adjunct modalities decided",
            "S-O-Z-O sequence planned", "Doctor sign-off obtained",
            "Treatment plan documented and filed",
        ],
        "output": "Treatment Plan, Protocol Selection Record",
        "forms": "Protocol Selection Form, S-O-Z-O Treatment Plan Template",
    },
    "stage_6": {
        "purpose": "Deliver neuromodulation treatment safely and document each session",
        "procedures": [
            "Complete pre-session checklist (medication state, skin check, device check)",
            "Position electrodes/device per protocol specification",
            "Deliver stimulation per protocol parameters",
            "Monitor patient throughout session for adverse events",
            "Document session details (impedance, duration, adverse events)",
            "Administer brief SOZO PRS after session (if scheduled)",
        ],
        "checklist": [
            "Pre-session checklist completed", "Medication state documented",
            "Electrode placement verified", "Session delivered per protocol",
            "Adverse events monitored", "Session record completed",
        ],
        "output": "Session Record, Adverse Event Report (if applicable)",
        "forms": "Pre-Session Checklist, Session Record Form, Adverse Event Form",
    },
    "stage_7": {
        "purpose": "Evaluate treatment response and make protocol adjustment decisions",
        "procedures": [
            "Administer full assessment battery at Week 4 and Week 8-10",
            "Compare results to baseline",
            "Classify response: Responder / Partial / Non-Responder",
            "For non-responders: reassess phenotype, consider protocol switch",
            "Document decision and rationale",
            "Obtain Doctor approval for any protocol modifications",
        ],
        "checklist": [
            "Week 4 assessment completed", "Week 8-10 assessment completed",
            "Response classification applied", "Baseline comparison documented",
            "Next steps decided", "Doctor approval for modifications (if needed)",
        ],
        "output": "Response Assessment Report, Protocol Modification Record (if applicable)",
        "forms": "Responder Tracking Form, Protocol Modification Request",
    },
    "stage_8": {
        "purpose": "Plan maintenance protocol for responders and establish follow-up schedule",
        "procedures": [
            "Design maintenance protocol (frequency taper: 2×/week → 1×/week → fortnightly)",
            "Set follow-up assessment schedule (monthly for 3 months, then quarterly)",
            "Assess eligibility for home-based protocol (if applicable)",
            "Document maintenance plan",
            "Schedule next in-clinic review",
        ],
        "checklist": [
            "Maintenance frequency decided", "Follow-up schedule set",
            "Home-based eligibility assessed", "Maintenance plan documented",
            "Next review scheduled",
        ],
        "output": "Maintenance Plan, Follow-Up Schedule",
        "forms": "Maintenance Plan Template, Home-Based Eligibility Assessment",
    },
    "stage_9": {
        "purpose": "Formally close the active treatment episode and plan transition",
        "procedures": [
            "Complete end-of-episode assessment",
            "Compile treatment summary (total sessions, response, outcomes)",
            "Provide patient with discharge summary",
            "Communicate findings to referring clinician",
            "Document transition plan (self-management, GP follow-up, re-referral criteria)",
            "Archive patient folder",
        ],
        "checklist": [
            "End-of-episode assessment completed", "Treatment summary compiled",
            "Discharge summary provided to patient", "Referring clinician notified",
            "Re-referral criteria documented", "Patient folder archived",
        ],
        "output": "Discharge Summary, Treatment Episode Report",
        "forms": "Discharge Summary Template, Referral Communication Letter",
    },
}


def build_handbook_sections(condition: ConditionSchema) -> list[SectionContent]:
    """Build all 9 stages of the patient journey with structured sub-tables."""
    sections = []
    for stage_key, stage_title in PATIENT_JOURNEY_STAGES.items():
        details = STAGE_DETAILS.get(stage_key, {})
        custom_content = condition.patient_journey_notes.get(stage_key, "")

        tables = []

        # Purpose table
        purpose = details.get("purpose", "")
        if purpose:
            tables.append({
                "headers": ["Purpose"],
                "rows": [[purpose]],
                "caption": f"{stage_title} — Purpose",
            })

        # Procedure checklist table
        procedures = details.get("procedures", [])
        if procedures:
            tables.append({
                "headers": ["Step", "Procedure"],
                "rows": [[str(i + 1), proc] for i, proc in enumerate(procedures)],
                "caption": f"{stage_title} — Procedure",
            })

        # Checklist table
        checklist = details.get("checklist", [])
        if checklist:
            tables.append({
                "headers": ["Item", "Completed (☐)"],
                "rows": [[item, "☐"] for item in checklist],
                "caption": f"{stage_title} — Checklist",
            })

        # Output and forms
        output = details.get("output", "")
        forms = details.get("forms", "")
        if output or forms:
            tables.append({
                "headers": ["Requirement", "Details"],
                "rows": [
                    ["Required Output", output or "—"],
                    ["Forms Required", forms or "—"],
                ],
                "caption": f"{stage_title} — Output & Forms",
            })

        content = custom_content if custom_content else ""

        sections.append(SectionContent(
            section_id=stage_key,
            title=stage_title,
            content=content,
            tables=tables,
        ))

    # Clinical tips
    if condition.clinical_tips:
        tips_content = "\n".join(f"CLINICAL TIP: {tip}" for tip in condition.clinical_tips)
        sections.append(SectionContent(
            section_id="clinical_tips",
            title="Clinical Tips & Governance Rules",
            content=tips_content,
        ))

    return sections


def build_handbook_appendices(condition: ConditionSchema) -> list[SectionContent]:
    """Build handbook appendices — shared clinical reference tables."""
    appendices = []

    # Appendix A: Inclusion/Exclusion Quick Reference
    inc_rows = [[c] for c in condition.inclusion_criteria] if condition.inclusion_criteria else [["See clinical protocol"]]
    exc_rows = [[c] for c in condition.exclusion_criteria] if condition.exclusion_criteria else [["See clinical protocol"]]
    appendices.append(SectionContent(
        section_id="appendix_a",
        title="Appendix A: Inclusion & Exclusion Quick Reference",
        tables=[
            {"headers": ["Inclusion Criteria"], "rows": inc_rows, "caption": "Inclusion criteria"},
            {"headers": ["Exclusion Criteria"], "rows": exc_rows, "caption": "Exclusion criteria"},
        ],
    ))

    # Appendix B: Phenotype-Protocol Quick Reference
    if condition.phenotypes and condition.protocols:
        headers = ["Phenotype"] + [p.protocol_id for p in condition.protocols[:10]]
        rows = []
        for pheno in condition.phenotypes:
            row = [pheno.label]
            for proto in condition.protocols[:10]:
                row.append("✓" if pheno.slug in proto.phenotype_slugs else "—")
            rows.append(row)
        appendices.append(SectionContent(
            section_id="appendix_b",
            title="Appendix B: Phenotype–Protocol Quick Reference",
            tables=[{"headers": headers, "rows": rows, "caption": "Phenotype-protocol assignment"}],
        ))

    # Appendix C: Patient Folder Contents
    appendices.append(SectionContent(
        section_id="appendix_c",
        title="Appendix C: Patient Folder Contents Checklist",
        tables=[{
            "headers": ["Document", "Required", "Filed (☐)"],
            "rows": [
                ["Referral letter / GP summary", "✓", "☐"],
                ["Signed consent forms (general + TPS)", "✓", "☐"],
                ["Psychological Intake & PRS Baseline", "✓", "☐"],
                ["Clinical Examination Record", "✓", "☐"],
                ["Phenotype Classification Record", "✓", "☐"],
                ["Treatment Plan & Protocol Selection", "✓", "☐"],
                ["Session Records (all sessions)", "✓", "☐"],
                ["Adverse Event Reports (if any)", "As needed", "☐"],
                ["Week 4 Response Assessment", "✓", "☐"],
                ["Week 8-10 Final Assessment", "✓", "☐"],
                ["Maintenance Plan", "If responder", "☐"],
                ["Discharge Summary", "At episode close", "☐"],
            ],
            "caption": "Complete patient folder contents checklist",
        }],
    ))

    # Appendix D: Emergency Stop Criteria
    appendices.append(SectionContent(
        section_id="appendix_d",
        title="Appendix D: Emergency Stop Procedure",
        tables=[{
            "headers": ["Trigger", "Action", "Escalation"],
            "rows": [
                ["New seizure during/after session", "STOP immediately. Place patient in recovery position.", "Call emergency services. Notify Doctor within 1 hour."],
                ["Syncope / loss of consciousness", "STOP. Lower patient safely. Check vitals.", "Call emergency services if not recovering in 60 seconds."],
                ["Severe headache unresponsive to rest", "STOP session. Monitor for 30 minutes.", "Escalate to Doctor. Do not resume same day."],
                ["Skin burn at electrode site", "STOP. Remove electrodes. Apply cool compress.", "Document. Photograph. Escalate to Doctor."],
                ["Acute psychiatric crisis", "STOP. Ensure patient safety.", "Activate psychiatric emergency protocol. Escort to A&E if needed."],
                ["Patient requests to stop", "STOP immediately. No questions.", "Document reason. Reschedule or withdraw as patient prefers."],
            ],
            "caption": "Emergency stop criteria and response protocol",
        }],
        callout_boxes=[{
            "text": "MANDATORY: Any Grade 3+ adverse event requires immediate treatment cessation, "
                    "Doctor notification within 1 hour, and documented incident report within 24 hours.",
            "box_type": "critical",
        }],
    ))

    # Appendix E: Safety Limits Quick Reference
    appendices.append(SectionContent(
        section_id="appendix_e",
        title="Appendix E: Safety Limits Quick Reference",
        tables=[{
            "headers": ["Parameter", "SOZO Standard", "DO NOT EXCEED"],
            "rows": [
                ["tDCS current intensity", "2.0 mA", "4.0 mA"],
                ["tDCS session duration", "20 min", "40 min"],
                ["tDCS electrode size", "35 cm²", "25 cm² (min)"],
                ["tDCS current density", "0.057 mA/cm²", "0.08 mA/cm²"],
                ["TPS pulse energy", "0.25 mJ/mm²", "0.40 mJ/mm²"],
                ["TPS pulses per session", "300-600", "1000"],
                ["TPS frequency", "5 Hz", "8 Hz"],
                ["CES intensity", "100-300 µA", "600 µA"],
                ["Sessions per day", "1", "2 (with 4h gap)"],
                ["Treatment blocks per year", "3-4", "6"],
            ],
            "caption": "Neuromodulation safety parameter limits",
        }],
    ))

    return appendices
