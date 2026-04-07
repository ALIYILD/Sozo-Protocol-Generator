"""Builder for assessment tool sections and clinical examination."""
from __future__ import annotations

from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent
from ...core.enums import Tier, NetworkKey


def build_assessments_section(condition: ConditionSchema) -> SectionContent:
    scale_rows = []
    for tool in condition.assessment_tools:
        scale_rows.append([
            tool.abbreviation,
            tool.name,
            ", ".join(tool.domains),
            tool.timing,
            tool.evidence_pmid or "—",
        ])

    baseline_content = "\n".join(f"• {m}" for m in condition.baseline_measures) if condition.baseline_measures else ""
    followup_content = "\n".join(f"• {m}" for m in condition.followup_measures) if condition.followup_measures else ""

    return SectionContent(
        section_id="assessments",
        title="Assessment Framework & Validated Scales",
        content=(
            f"The following validated assessment instruments are recommended for baseline "
            f"evaluation, treatment monitoring, and outcome measurement in {condition.display_name}."
        ),
        tables=[{
            "headers": ["Abbreviation", "Full Scale Name", "Domains Assessed", "Timing", "Reference (PMID)"],
            "rows": scale_rows,
            "caption": "Validated assessment scales for this condition",
        }] if scale_rows else [],
        subsections=[
            SectionContent(
                section_id="baseline_measures",
                title="Baseline Measures",
                content=baseline_content or "[REVIEW REQUIRED: Baseline measures not defined]",
                is_placeholder=not bool(condition.baseline_measures),
            ),
            SectionContent(
                section_id="followup_measures",
                title="Follow-Up & Outcome Measures",
                content=followup_content or "[REVIEW REQUIRED: Follow-up measures not defined]",
                is_placeholder=not bool(condition.followup_measures),
            ),
        ],
        review_flags=["No validated scales defined"] if not condition.assessment_tools else [],
    )


# ---------------------------------------------------------------------------
# Clinical Examination Sections (for CLINICAL_EXAM document type)
# ---------------------------------------------------------------------------

_NETWORK_ASSESSMENT_ITEMS = {
    NetworkKey.DMN: {
        "label": "Default Mode Network (DMN)",
        "max_score": 14,
        "tests": [
            ("Mind-wandering / daydreaming frequency", "0 = None, 1 = Occasional, 2 = Frequent"),
            ("Self-referential thought intrusion", "0 = None, 1 = Mild, 2 = Significant"),
            ("Autobiographical memory access", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
            ("Internal mentation quality", "0 = Normal, 1 = Reduced, 2 = Absent"),
            ("Task-negative activity (rest state)", "0 = Normal, 1 = Altered, 2 = Significantly altered"),
            ("Social cognition / theory of mind", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
            ("Visual hallucinations / perceptual disturbance", "0 = None, 1 = Occasional, 2 = Frequent"),
        ],
    },
    NetworkKey.CEN: {
        "label": "Central Executive Network (CEN/FPN)",
        "max_score": 14,
        "tests": [
            ("Working memory (digit span / N-back)", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
            ("Cognitive flexibility (TMT-B / card sorting)", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
            ("Planning and problem-solving", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
            ("Verbal fluency (phonemic + semantic)", "0 = Normal, 1 = Reduced, 2 = Severely reduced"),
            ("Decision-making quality", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
            ("Goal-directed behaviour", "0 = Normal, 1 = Reduced, 2 = Absent"),
            ("Multi-tasking / dual-task performance", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
        ],
    },
    NetworkKey.SN: {
        "label": "Salience Network (SN)",
        "max_score": 14,
        "tests": [
            ("Emotional reactivity to stimuli", "0 = Normal, 1 = Altered, 2 = Significantly altered"),
            ("Interoceptive awareness", "0 = Normal, 1 = Reduced, 2 = Absent"),
            ("Autonomic responsivity", "0 = Normal, 1 = Blunted, 2 = Severely blunted"),
            ("Error detection / self-monitoring", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
            ("Task switching ability", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
            ("Motivational drive", "0 = Normal, 1 = Reduced, 2 = Absent (apathy)"),
            ("Pain perception / processing", "0 = Normal, 1 = Altered, 2 = Significantly altered"),
        ],
    },
    NetworkKey.SMN: {
        "label": "Sensorimotor Network (SMN)",
        "max_score": 16,
        "tests": [
            ("Fine motor dexterity (finger tapping)", "0 = Normal, 1 = Mild reduction, 2 = Moderate, 3 = Severe"),
            ("Gait initiation and velocity", "0 = Normal, 1 = Slow, 2 = Very slow, 3 = Unable"),
            ("Postural stability (pull test)", "0 = Normal, 1 = Retropulsion, 2 = Would fall, 3 = Unable"),
            ("Movement amplitude and rhythm", "0 = Normal, 1 = Reduced, 2 = Severely reduced"),
            ("Sensorimotor integration", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
            ("Bilateral coordination", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
            ("Speech motor output (volume, clarity)", "0 = Normal, 1 = Reduced, 2 = Severely impaired"),
            ("Swallowing function", "0 = Normal, 1 = Mild difficulty, 2 = Significant difficulty"),
        ],
    },
    NetworkKey.LIMBIC: {
        "label": "Limbic / Emotional Network",
        "max_score": 14,
        "tests": [
            ("Mood state (depression screening)", "0 = Normal, 1 = Mild, 2 = Moderate-Severe"),
            ("Anxiety level", "0 = None, 1 = Mild, 2 = Moderate-Severe"),
            ("Emotional regulation", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
            ("Anhedonia / pleasure response", "0 = Normal, 1 = Reduced, 2 = Absent"),
            ("Sleep quality (subjective)", "0 = Good, 1 = Disrupted, 2 = Severely disrupted"),
            ("Appetite / reward-seeking", "0 = Normal, 1 = Altered, 2 = Significantly altered"),
            ("Impulse control", "0 = Normal, 1 = Mild issues, 2 = Significant issues"),
        ],
    },
    NetworkKey.ATTENTION: {
        "label": "Attention Networks (DAN/VAN)",
        "max_score": 16,
        "tests": [
            ("Sustained attention (continuous performance)", "0 = Normal, 1 = Mild deficit, 2 = Moderate, 3 = Severe"),
            ("Selective attention (Stroop/flanker)", "0 = Normal, 1 = Impaired, 2 = Moderate, 3 = Severe"),
            ("Divided attention (dual-task)", "0 = Normal, 1 = Impaired, 2 = Severely impaired"),
            ("Alerting / arousal", "0 = Normal, 1 = Reduced, 2 = Significantly reduced"),
            ("Visuospatial attention (line bisection)", "0 = Normal, 1 = Mild neglect, 2 = Moderate, 3 = Severe"),
            ("Orienting / target detection", "0 = Normal, 1 = Slowed, 2 = Severely slowed"),
            ("Processing speed", "0 = Normal, 1 = Slowed, 2 = Severely slowed"),
            ("Distractibility", "0 = None, 1 = Mild, 2 = Moderate, 3 = Severe"),
        ],
    },
}

# Standard Fellow motor exam sections
_FELLOW_MOTOR_SECTIONS = [
    ("A1", "Tremor Assessment", [
        ("Resting tremor — right upper limb", "0-4"),
        ("Resting tremor — left upper limb", "0-4"),
        ("Resting tremor — right lower limb", "0-4"),
        ("Resting tremor — left lower limb", "0-4"),
        ("Postural tremor — right hand", "0-4"),
        ("Postural tremor — left hand", "0-4"),
    ]),
    ("A2", "Rigidity Assessment", [
        ("Neck rigidity", "0-4"),
        ("Right upper limb", "0-4"),
        ("Left upper limb", "0-4"),
        ("Right lower limb", "0-4"),
        ("Left lower limb", "0-4"),
    ]),
    ("A3", "Bradykinesia Assessment", [
        ("Finger tapping — right", "0-4"),
        ("Finger tapping — left", "0-4"),
        ("Hand movements — right", "0-4"),
        ("Hand movements — left", "0-4"),
        ("Rapid alternating — right", "0-4"),
        ("Rapid alternating — left", "0-4"),
        ("Toe tapping — right", "0-4"),
        ("Toe tapping — left", "0-4"),
    ]),
    ("A4", "Gait Assessment", [
        ("Gait initiation", "Normal / Hesitant / FOG"),
        ("Stride length", "Normal / Reduced / Shuffling"),
        ("Arm swing", "Normal / Reduced / Absent"),
        ("Turning", "Normal / Slow / Multi-step"),
        ("Timed Up and Go (TUG)", "_____ seconds"),
        ("10-Metre Walk Test", "_____ seconds"),
    ]),
    ("A5", "Functional Gait Assessment", [
        ("Tandem gait (heel-to-toe)", "0 = Normal, 1 = Impaired, 2 = Unable"),
        ("Single leg stance — right", "_____ seconds (target >10s)"),
        ("Single leg stance — left", "_____ seconds (target >10s)"),
        ("Functional reach test", "_____ cm"),
    ]),
    ("A6", "Speech Assessment", [
        ("Volume (loudness)", "Normal / Reduced / Very quiet"),
        ("Clarity (articulation)", "Normal / Mild dysarthria / Moderate-Severe"),
        ("Rate (speed)", "Normal / Slow / Fast / Variable"),
        ("Prosody (intonation)", "Normal / Monotone"),
    ]),
]


def build_clinical_exam_sections(condition: ConditionSchema, tier: Tier) -> SectionContent:
    """Build clinical examination sections. Fellow=motor-focused, Partners=6-Network."""
    if tier == Tier.PARTNERS:
        return _build_network_assessment(condition)
    return _build_fellow_motor_exam(condition)


def _build_fellow_motor_exam(condition: ConditionSchema) -> SectionContent:
    """Fellow: Traditional motor-focused examination sections A1-A6."""
    subsections = []

    for section_id, title, items in _FELLOW_MOTOR_SECTIONS:
        rows = [[item, scale, ""] for item, scale in items]
        subsections.append(SectionContent(
            section_id=f"motor_{section_id.lower()}",
            title=f"Section {section_id}: {title}",
            tables=[{
                "headers": ["Assessment Item", "Scale / Expected", "Score / Finding"],
                "rows": rows,
                "caption": f"{section_id} — {title}",
            }],
        ))

    # Standard neurological exam
    subsections.append(SectionContent(
        section_id="neuro_exam",
        title="Section B: Standard Neurological Examination",
        tables=[{
            "headers": ["Test", "Right", "Left", "Notes"],
            "rows": [
                ["Deep tendon reflexes", "", "", ""],
                ["Plantar response", "", "", ""],
                ["Tone assessment", "", "", ""],
                ["Sensation (light touch)", "", "", ""],
                ["Cranial nerves", "", "", ""],
                ["Cerebellar signs", "", "", ""],
            ],
            "caption": "Standard neurological examination findings",
        }],
    ))

    # Cognitive screening
    subsections.append(SectionContent(
        section_id="cognitive_screen",
        title="Section C: Cognitive Screening",
        tables=[{
            "headers": ["Assessment", "Score", "Interpretation"],
            "rows": [
                ["MoCA (Montreal Cognitive Assessment)", "___/30", "Normal ≥26; MCI 18-25; Dementia <18"],
                ["Clock Drawing Test", "___/5", "Normal ≥4"],
                ["Verbal Fluency (animal naming, 60s)", "___", "Normal ≥15; Impaired <12"],
                ["Digit Span (forward / backward)", "___/___", "Forward normal ≥5; Backward ≥3"],
            ],
            "caption": "Cognitive screening results",
        }],
    ))

    # Mood screening
    subsections.append(SectionContent(
        section_id="mood_screen",
        title="Section D: Mood & Behavioural Screening",
        tables=[{
            "headers": ["Scale", "Score", "Threshold", "Action"],
            "rows": [
                ["PHQ-9 (depression)", "___/27", "≥10 = moderate", "Consider C4 mood protocol"],
                ["GAD-7 (anxiety)", "___/21", "≥10 = moderate", "Consider CES adjunct"],
                ["Apathy Evaluation Scale", "___", "≥14 = clinically significant", "Consider C5 motivation protocol"],
                ["Impulse Control (QUIP-RS)", "___", "Score-dependent", "Flag if positive — monitor"],
            ],
            "caption": "Mood and behavioural screening thresholds",
        }],
    ))

    # Phenotype identification summary
    subsections.append(SectionContent(
        section_id="phenotype_id",
        title="Section E: Phenotype Identification & Clinical Summary",
        tables=[{
            "headers": ["Domain", "Severity", "Primary Phenotype Contribution"],
            "rows": [
                ["Motor (tremor, rigidity, bradykinesia)", "☐ None ☐ Mild ☐ Moderate ☐ Severe", "☐ TD ☐ AR ☐ PIGD"],
                ["Cognitive (executive, memory, attention)", "☐ None ☐ Mild ☐ Moderate ☐ Severe", "☐ FE"],
                ["Mood / Affect (depression, anxiety, apathy)", "☐ None ☐ Mild ☐ Moderate ☐ Severe", "☐ LA"],
                ["Pain / Sensory", "☐ None ☐ Mild ☐ Moderate ☐ Severe", "☐ PA"],
                ["Autonomic / Sleep", "☐ None ☐ Mild ☐ Moderate ☐ Severe", "☐ MN"],
            ],
            "caption": "Phenotype identification summary",
        }],
    ))

    return SectionContent(
        section_id="clinical_examination",
        title=f"Clinical Examination — {condition.display_name}",
        content="Complete each section below. Score using the indicated scales.",
        subsections=subsections,
    )


def _build_network_assessment(condition: ConditionSchema) -> SectionContent:
    """Partners: 6-Network Bedside Assessment."""
    subsections = []

    for network_key, info in _NETWORK_ASSESSMENT_ITEMS.items():
        rows = [[test, scale, ""] for test, scale in info["tests"]]
        subsections.append(SectionContent(
            section_id=f"network_{network_key.value}",
            title=f"{info['label']} (Max Score: {info['max_score']})",
            tables=[{
                "headers": ["Test Item", "Scoring Guide", "Score"],
                "rows": rows,
                "caption": f"{info['label']} bedside assessment",
            }],
        ))

    # Network imbalance profile summary
    profile_rows = [[info["label"], str(info["max_score"]), "", ""]
                     for info in _NETWORK_ASSESSMENT_ITEMS.values()]
    subsections.append(SectionContent(
        section_id="network_profile",
        title="Network Imbalance Profile Summary",
        tables=[{
            "headers": ["Network", "Max Score", "Patient Score", "Dysfunction Level"],
            "rows": profile_rows,
            "caption": "6-Network imbalance profile — summary",
        }],
    ))

    return SectionContent(
        section_id="clinical_examination",
        title=f"6-Network Bedside Assessment — {condition.display_name}",
        content=(
            "Assess each of the 6 functional brain networks using the bedside tests below. "
            "Score each item using the provided scale. Sum scores per network to identify "
            "the network imbalance profile for FNON treatment targeting."
        ),
        subsections=subsections,
    )
