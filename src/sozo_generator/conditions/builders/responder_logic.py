"""Builder for responder tracking sections with detailed scheduling and classification."""
from __future__ import annotations

from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent


def build_responder_section(condition: ConditionSchema) -> SectionContent:
    """Build comprehensive responder tracking with scheduling, classification, and escalation."""
    criteria_content = "\n".join(f"• {c}" for c in condition.responder_criteria) if condition.responder_criteria else "[REVIEW REQUIRED: Responder criteria not defined]"

    subsections = [
        # 1. Operational Response Definition
        SectionContent(
            section_id="response_definition",
            title="Operational Response Definition",
            tables=[{
                "headers": ["Parameter", "Definition"],
                "rows": [
                    ["Primary Outcome Measure", condition.assessment_tools[0].name if condition.assessment_tools else "Condition-specific validated scale"],
                    ["Responder Threshold", "≥30% improvement from baseline in primary measure"],
                    ["Assessment Timepoints", "Week 4 (interim), Week 8-10 (primary endpoint)"],
                    ["Medication State Requirement", "Consistent ON or OFF state across all assessments"],
                    ["Minimum Data Required", "Baseline + Week 4 + Week 8-10 assessments complete"],
                ],
                "caption": "Operational response definition parameters",
            }],
        ),

        # 2. Responder Criteria
        SectionContent(
            section_id="responder_criteria",
            title="Responder Criteria",
            content=criteria_content,
            is_placeholder=not bool(condition.responder_criteria),
        ),

        # 3. Likely Responder Profiles
        SectionContent(
            section_id="responder_profiles",
            title="Likely Responder Profiles",
            tables=[{
                "headers": ["Profile Factor", "Favourable", "Unfavourable"],
                "rows": [
                    ["Disease duration", "Shorter (<5 years)", "Longer (>10 years)"],
                    ["Medication response", "Good levodopa response", "Poor medication response"],
                    ["Cognitive status", "MoCA ≥22", "MoCA <18"],
                    ["Phenotype clarity", "Clear single phenotype", "Mixed/unclear phenotype"],
                    ["Protocol adherence", "≥80% session attendance", "<60% attendance"],
                    ["Medication consistency", "Stable regimen, consistent timing", "Frequent changes, variable timing"],
                ],
                "caption": "Clinical predictors of treatment response",
            }],
        ),

        # 4. Response Classification
        SectionContent(
            section_id="response_classification",
            title="Response Classification",
            tables=[{
                "headers": ["Category", "Definition", "Clinical Action"],
                "rows": [
                    ["Responder", "≥30% improvement in primary outcome measure AND clinically meaningful functional change", "Continue protocol; plan maintenance schedule"],
                    ["Partial Responder", "15-29% improvement OR improvement in secondary but not primary outcome", "Reassess phenotype; consider protocol adjustment at Week 8"],
                    ["Non-Responder", "<15% improvement across all domains at Week 4 AND Week 8", "Initiate FNON Non-Responder Pathway — Level 5 reassessment"],
                ],
                "caption": "SOZO response classification framework",
            }],
        ),

        # 5. Assessment Schedule
        SectionContent(
            section_id="assessment_schedule",
            title="Assessment Schedule",
            tables=[{
                "headers": ["Timepoint", "Assessments Required", "Decision Point"],
                "rows": [
                    ["Baseline (Pre-treatment)", "Full battery: primary scale, cognitive, mood, PRS", "Establish baseline; confirm phenotype"],
                    ["Session-by-session", "Brief SOZO PRS (5 min), adverse event check", "Monitor tolerance; flag safety concerns"],
                    ["Week 4 (Interim)", "Primary scale + PRS + clinician global impression", "Interim response check; continue or adjust"],
                    ["Week 8-10 (Primary)", "Full battery repeat", "Classify response; maintenance or escalation"],
                    ["Month 3 (Maintenance)", "Primary scale + PRS", "Confirm sustained response"],
                    ["Month 6 / 12 (Long-term)", "Full battery", "Long-term outcome; re-treatment decision"],
                ],
                "caption": "Assessment schedule across treatment timeline",
            }],
        ),

        # 6. Per-Session Tracking Template
        SectionContent(
            section_id="session_tracking",
            title="Per-Session Tracking Template",
            tables=[{
                "headers": ["Field", "Session __ / Date: ___"],
                "rows": [
                    ["Protocol delivered", ""],
                    ["Medication state (ON/OFF)", ""],
                    ["Last medication dose time", ""],
                    ["Session start time", ""],
                    ["Duration (actual)", ""],
                    ["Impedance (Ω)", ""],
                    ["Adverse events", "☐ None ☐ Grade 1 ☐ Grade 2 ☐ Grade 3+"],
                    ["AE description (if any)", ""],
                    ["SOZO PRS (brief)", "___/10"],
                    ["Clinician notes", ""],
                    ["Clinician signature", ""],
                ],
                "caption": "Per-session tracking record template",
            }],
        ),

        # 7. Non-Responder Pathway
        SectionContent(
            section_id="non_responder_pathway",
            title="Non-Responder Pathway (Level 5 — FNON)",
            content=condition.non_responder_pathway or (
                "For non-responders, initiate Level 5 FNON reassessment:\n"
                "1. Repeat 6-Network Bedside Assessment\n"
                "2. Re-evaluate phenotype classification\n"
                "3. Identify secondary/tertiary network targets\n"
                "4. Adjust tDCS montage and/or TPS target\n"
                "5. Consider adjunct modality addition (taVNS, CES)\n"
                "6. Doctor review mandatory before protocol change"
            ),
            tables=[{
                "headers": ["Step", "Action", "Responsible", "Timeline"],
                "rows": [
                    ["1", "Repeat full assessment battery", "Fellow clinician", "Within 1 week of non-responder classification"],
                    ["2", "Re-evaluate phenotype (may have changed)", "Fellow + Doctor", "Same session as Step 1"],
                    ["3", "Repeat 6-Network Assessment (Partners)", "Partners clinician", "If available"],
                    ["4", "Review medication consistency log", "Fellow clinician", "Before protocol change"],
                    ["5", "Propose protocol modification", "Doctor", "Within 3 working days"],
                    ["6", "Obtain patient consent for protocol change", "Fellow clinician", "Before resuming treatment"],
                    ["7", "Initiate modified protocol (Block 2)", "Fellow clinician", "After Doctor sign-off"],
                    ["8", "If still non-responder after Block 2: discontinue", "Doctor", "Week 8-10 of Block 2"],
                ],
                "caption": "Non-responder escalation pathway steps",
            }],
        ),

        # 8. Dose Adjustment Protocol
        SectionContent(
            section_id="dose_adjustment",
            title="Protocol Adjustment Guidelines",
            tables=[{
                "headers": ["Scenario", "Adjustment", "Approval Required"],
                "rows": [
                    ["Intolerance at 2.0 mA", "Reduce to 1.5 mA for 3 sessions; if tolerated, attempt 1.75 mA", "Fellow clinician"],
                    ["Skin irritation at electrode site", "Check sponge moisture; reposition slightly; reduce to 1.5 mA", "Fellow clinician"],
                    ["Non-response at Week 4", "Switch montage per non-responder pathway", "Doctor approval required"],
                    ["Partial response at Week 8", "Extend block by 5 sessions at same parameters", "Doctor approval required"],
                    ["Addition of TPS to tDCS", "Requires full consent process and Doctor authorisation", "Doctor + patient consent"],
                    ["Switch from bilateral to unilateral montage", "Target contralateral to dominant symptom side", "Doctor approval required"],
                ],
                "caption": "Protocol adjustment decision matrix",
            }],
        ),
        # 9. Maintenance Protocol Schedule
        SectionContent(
            section_id="maintenance_schedule",
            title="Maintenance Protocol Schedule",
            tables=[{
                "headers": ["Phase", "Frequency", "Duration", "Assessment"],
                "rows": [
                    ["Acute Block", "Daily (Mon-Fri) or 3×/week", "3-5 weeks (10-15 sessions)", "Baseline + Week 4"],
                    ["Transition", "2×/week", "4 weeks", "Week 8-10 assessment"],
                    ["Early Maintenance", "1×/week", "4-8 weeks", "Monthly PRS check"],
                    ["Stable Maintenance", "Fortnightly or monthly", "Ongoing", "Quarterly full assessment"],
                    ["Booster (if relapse)", "3×/week for 2 weeks", "2 weeks", "Pre/post booster assessment"],
                ],
                "caption": "Maintenance protocol frequency taper schedule",
            }],
        ),

        # 10. Regulator-Safe Language Guide
        SectionContent(
            section_id="language_guide",
            title="Regulator-Safe Language Guide",
            content="Use the following language in all documentation, reports, and patient communications.",
            tables=[{
                "headers": ["DO Use", "DO NOT Use"],
                "rows": [
                    ["Neuromodulation protocol", "Treatment / therapy / cure"],
                    ["Evidence-informed", "Proven / guaranteed"],
                    ["May improve symptoms", "Will improve / fixes"],
                    ["Investigational / exploratory", "Experimental (unless IRB context)"],
                    ["OFF-LABEL (for TPS in non-AD)", "Unapproved / unlicensed"],
                    ["Adjunct to standard care", "Replacement for medication"],
                    ["Response observed in studies", "Clinical trial results show"],
                    ["Individual results may vary", "Typical results / expected outcome"],
                ],
                "caption": "Regulator-safe language reference for clinical documentation",
            }],
        ),

        # 11. Signature Data Collection
        SectionContent(
            section_id="signature_collection",
            title="SOZO Responder Signature Data Collection",
            tables=[{
                "headers": ["Data Field", "Baseline", "Week 4", "Week 8-10", "Maintenance"],
                "rows": [
                    ["Primary outcome scale score", "", "", "", ""],
                    ["SOZO PRS total", "", "", "", ""],
                    ["Phenotype classification", "", "", "", ""],
                    ["Protocol(s) delivered", "", "", "", ""],
                    ["Total sessions completed", "", "", "", ""],
                    ["Adverse events (Grade 2+)", "", "", "", ""],
                    ["Medication changes", "", "", "", ""],
                    ["Response classification", "—", "", "", ""],
                    ["Clinician signature", "", "", "", ""],
                    ["Date", "", "", "", ""],
                ],
                "caption": "Responder signature data — longitudinal tracking",
            }],
        ),
    ]

    # Levodopa scheduling (PD-specific)
    if condition.levodopa_note:
        subsections.insert(5, SectionContent(
            section_id="levodopa_scheduling",
            title="Levodopa–Stimulation Scheduling & Documentation",
            content=condition.levodopa_note,
            tables=[
                {
                    "headers": ["State", "Definition", "When to Use", "Documentation"],
                    "rows": [
                        ["ON-State", "30-60 min after levodopa dose", "Preferred for motor protocols (C1, C2)", "Record dose, time, and 'ON' on session form"],
                        ["OFF-State", "Before first morning dose OR ≥4h after last dose", "Used for specific research protocols", "Record last dose time and 'OFF' on session form"],
                    ],
                    "caption": "ON/OFF state definitions and documentation requirements",
                },
                {
                    "headers": ["Rule", "Description"],
                    "rows": [
                        ["Consistency Rule", "Choose ONE state (ON or OFF) for the entire treatment block. Do NOT mix states across sessions."],
                        ["Timing Window", "Deliver stimulation within 30-90 min of levodopa dose (ON) or ≥4h after last dose (OFF)"],
                        ["Documentation", "Record medication name, dose, and time at EVERY session — mandatory"],
                        ["Assessment State", "Assessments (baseline, Week 4, Week 8-10) must be in SAME state as treatment sessions"],
                    ],
                    "caption": "Levodopa-stimulation scheduling rules",
                },
            ],
            callout_boxes=[{
                "text": "CRITICAL: Inconsistent ON/OFF medication state is the #1 cause of false "
                        "responder/non-responder classification in PD neuromodulation. Document medication "
                        "state at EVERY session.",
                "box_type": "critical",
            }],
        ))

    return SectionContent(
        section_id="responder_tracking",
        title="Response Tracking & Classification",
        content=(
            f"Response classification for {condition.display_name} follows the SOZO Operational "
            "Response Definition. Assessment occurs at Week 4, Week 8–10, and end-of-block."
        ),
        subsections=subsections,
    )
