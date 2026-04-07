"""
Shared helpers for building ConditionSchema instances.
All condition generators import from here.
"""
from __future__ import annotations

from ..schemas.condition import (
    ConditionSchema, PhenotypeSubtype, NetworkProfile,
    StimulationTarget, AssessmentTool, SafetyNote, ProtocolEntry,
    AdverseEventGrade, SideEffectEntry,
)
from ..core.enums import (
    NetworkKey, NetworkDysfunction, Modality, EvidenceLevel
)
from ..core.utils import current_date_str


def make_network(
    network: NetworkKey,
    dysfunction: NetworkDysfunction,
    relevance: str,
    primary: bool = False,
    severity: str = "moderate",
    evidence_note: str | None = None,
) -> NetworkProfile:
    return NetworkProfile(
        network=network,
        dysfunction=dysfunction,
        relevance=relevance,
        primary=primary,
        severity=severity,
        evidence_note=evidence_note,
    )


def make_tdcs_target(
    region: str,
    abbr: str,
    laterality: str,
    rationale: str,
    protocol_label: str | None = None,
    evidence_level: EvidenceLevel = EvidenceLevel.MEDIUM,
    off_label: bool = True,
    eeg_canonical: list[str] | None = None,
) -> StimulationTarget:
    return StimulationTarget(
        modality=Modality.TDCS,
        target_region=region,
        target_abbreviation=abbr,
        laterality=laterality,
        rationale=rationale,
        protocol_label=protocol_label,
        evidence_level=evidence_level,
        off_label=off_label,
        eeg_canonical=eeg_canonical,
    )


def make_tps_target(
    region: str,
    abbr: str,
    laterality: str,
    rationale: str,
    protocol_label: str | None = None,
    evidence_level: EvidenceLevel = EvidenceLevel.MEDIUM,
    eeg_canonical: list[str] | None = None,
) -> StimulationTarget:
    return StimulationTarget(
        modality=Modality.TPS,
        target_region=region,
        target_abbreviation=abbr,
        laterality=laterality,
        rationale=rationale,
        protocol_label=protocol_label,
        evidence_level=evidence_level,
        off_label=True,
        consent_required=True,
        eeg_canonical=eeg_canonical,
    )


def make_safety(
    category: str,
    description: str,
    severity: str = "moderate",
    source: str | None = None,
) -> SafetyNote:
    return SafetyNote(category=category, description=description, severity=severity, source=source)


SHARED_ABSOLUTE_CONTRAINDICATIONS = [
    "Active implanted devices (cochlear implants, deep brain stimulators, cardiac pacemakers/defibrillators) unless explicitly cleared by device manufacturer",
    "Metallic implants in the head or neck region within the stimulation field",
    "Active epilepsy with uncontrolled seizures (relative contraindication — requires neurologist clearance)",
    "Skull defects or craniectomy at stimulation sites",
    "Skin lesions, wounds, or dermatological conditions at electrode placement sites",
    "Active malignancy of the central nervous system",
    "Pregnancy (precautionary contraindication — insufficient safety data)",
    "Severe psychiatric crisis requiring immediate hospitalization",
]

SHARED_SAFETY_NOTES = [
    make_safety(
        "contraindication",
        "Active implanted electronic devices in the head/neck region",
        "absolute",
        "Manufacturer guidelines and consensus safety statements",
    ),
    make_safety(
        "stopping_rule",
        "Discontinue immediately for Grade 3 adverse events: new seizure, severe headache, syncope, skin burn, worsening of psychiatric symptoms requiring acute intervention",
        "high",
    ),
    make_safety(
        "monitoring",
        "Assess and document adverse events at every session using a standardized monitoring checklist",
        "moderate",
    ),
    make_safety(
        "precaution",
        "Ensure consistent medication state (ON or OFF) throughout treatment blocks to avoid false responder/non-responder classification",
        "moderate",
    ),
]

SHARED_GOVERNANCE_RULES = [
    "No Fellow or Clinical Assistant may independently modify treatment plans without Doctor authorization",
    "All TPS applications require explicit off-label informed consent and Doctor authorization",
    "Adverse events must be documented within 24 hours and escalated per clinic protocol",
    "Treatment records must be updated at every session",
    "Informed consent must be obtained and documented before initiating any modality",
]

SHARED_ADVERSE_EVENT_GRADES = [
    AdverseEventGrade(
        grade=1, label="Mild",
        description="Transient, self-resolving without intervention",
        examples=["Tingling at electrode site", "Mild headache (<30 min)", "Skin redness (resolves <1 hr)", "Slight dizziness"],
        action="Continue treatment with monitoring. Document in session record.",
    ),
    AdverseEventGrade(
        grade=2, label="Moderate",
        description="Requires intervention or protocol parameter adjustment",
        examples=["Persistent headache (>1 hr)", "Skin irritation requiring topical treatment", "Nausea", "Increased anxiety or agitation"],
        action="Pause session. Assess and adjust parameters or electrode placement. Resume only if resolved.",
    ),
    AdverseEventGrade(
        grade=3, label="Severe",
        description="Requires immediate treatment discontinuation",
        examples=["New seizure", "Severe headache unresponsive to analgesics", "Syncope", "Skin burn", "Acute psychiatric worsening"],
        action="STOP treatment immediately. Escalate to supervising Doctor. Document within 24 hours.",
    ),
    AdverseEventGrade(
        grade=4, label="Life-threatening",
        description="Emergency medical response required",
        examples=["Status epilepticus", "Cardiac event", "Severe allergic reaction", "Loss of consciousness"],
        action="Activate emergency protocol. Call emergency services. Do NOT resume treatment.",
    ),
]

SHARED_SIDE_EFFECTS = [
    SideEffectEntry(
        effect="Tingling or itching at electrode site",
        frequency="Very common (>30%)",
        modalities=[Modality.TDCS],
        management="Normal sensation; typically reduces within 2–3 minutes. Adjust electrode contact if persistent.",
        severity="mild",
    ),
    SideEffectEntry(
        effect="Mild headache",
        frequency="Common (10–20%)",
        modalities=[Modality.TDCS, Modality.TPS],
        management="Self-resolving within 1 hour. Paracetamol PRN if needed.",
        severity="mild",
    ),
    SideEffectEntry(
        effect="Skin redness at electrode site",
        frequency="Common (10–30%)",
        modalities=[Modality.TDCS],
        management="Transient erythema; resolves within 1 hour. Check electrode sponge moisture and contact quality.",
        severity="mild",
    ),
    SideEffectEntry(
        effect="Scalp discomfort during TPS pulse delivery",
        frequency="Common (15–25%)",
        modalities=[Modality.TPS],
        management="Adjust pulse energy if tolerable threshold exceeded. Brief breaks between pulse trains.",
        severity="mild",
    ),
    SideEffectEntry(
        effect="Ear discomfort or tingling (taVNS)",
        frequency="Common (10–20%)",
        modalities=[Modality.TAVNS],
        management="Adjust electrode clip position on tragus/cymba conchae. Reduce current if persistent.",
        severity="mild",
    ),
    SideEffectEntry(
        effect="Fatigue or drowsiness post-session",
        frequency="Uncommon (5–10%)",
        modalities=[Modality.TDCS, Modality.TPS, Modality.CES],
        management="Expected in some patients. Schedule sessions to accommodate. Monitor for pattern.",
        severity="mild",
    ),
]
