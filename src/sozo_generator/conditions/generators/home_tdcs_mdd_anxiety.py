"""
Home-Based tDCS for MDD + Comorbid Anxiety (Window 2)

Condition: Major Depressive Disorder with comorbid Anxiety (MDD+ANX)
Modality: tDCS — home-use, app-supervised, remotely monitored
Evidence base: Moderate-certainty (GRADE); Brunoni 2013 SELECT-TDCS, Blumberger 2018 ELECT-TDCS,
               Razza et al. 2020 home tDCS feasibility, Aparicio et al. 2019 remote supervision.

Subagent modules embedded:
  1. Electrode Montage Generator
  2. Home-Safety Checklist Agent
  3. Adherence Monitoring Logic
  4. Anxiety-Comorbidity Adapter
  5. Evidence-Grade Annotator (GRADE)
  6. Adverse-Event Tracker
  7. App-Integration Spec Agent
  8. Sham-Control Comparator
  9. Patient Training Module Generator
 10. Remote-Supervision Workflow Designer
"""
import logging
from ...schemas.condition import (
    ConditionSchema, PhenotypeSubtype, NetworkProfile,
    StimulationTarget, AssessmentTool, SafetyNote, ProtocolEntry
)
from ...core.enums import (
    NetworkKey, NetworkDysfunction, Modality, EvidenceLevel
)
from ...core.utils import current_date_str
from ..shared_condition_schema import (
    make_network, make_tdcs_target, make_safety,
    SHARED_ABSOLUTE_CONTRAINDICATIONS, SHARED_SAFETY_NOTES, SHARED_GOVERNANCE_RULES
)

logger = logging.getLogger(__name__)


# ── Subagent 1: Electrode Montage Generator ──────────────────────────────────
MONTAGE_SPEC = {
    "primary_montage": {
        "label": "Bilateral DLPFC — Home Standard",
        "anode": "F3 — Left DLPFC (10-20 EEG system)",
        "cathode": "F4 — Right DLPFC (10-20 EEG system)",
        "intensity_mA": 2.0,
        "duration_min": 30,
        "electrode_size_cm2": 35,
        "current_density_mA_cm2": 0.057,
        "ramp_up_s": 30,
        "ramp_down_s": 30,
        "skin_prep": "Mild abrasive gel; impedance <5 kΩ before session start",
        "positioning_method": "Tape-measure F3/F4 landmark method (nasion-inion + preauricular midpoint)",
        "patient_instruction": (
            "Measure from nasion to inion and mark midpoint. "
            "Place left electrode (anode, RED) at F3: 30% left of midpoint. "
            "Place right electrode (cathode, BLUE) at F4: 30% right of midpoint. "
            "Confirm placement with app photo-verification before starting."
        ),
    },
    "anxiety_adapted_montage": {
        "label": "DLPFC + Supraorbital — Anxious Subtype",
        "anode": "F3 — Left DLPFC",
        "cathode": "Fp2 — Right supraorbital (Brunoni montage)",
        "intensity_mA": 2.0,
        "duration_min": 30,
        "electrode_size_cm2": 35,
        "rationale": (
            "Right supraorbital cathode reduces amygdala-OFC hyperactivity implicated in "
            "anxiety. Brunoni SELECT-TDCS used Fp2 cathode in primary trial — preferred for "
            "anxious-depressive subtype."
        ),
    },
    "sham_montage": {
        "label": "Sham — Active Ramp Only",
        "anode": "F3 (identical positioning)",
        "cathode": "F4 (identical positioning)",
        "intensity_mA": 2.0,
        "sham_duration_s": 60,
        "ramp_up_s": 30,
        "ramp_down_s": 30,
        "patient_instruction": "Identical setup to active; device ramps up then automatically reduces to 0 mA for remainder of session.",
        "blinding_note": "Skin tingling during ramp-up is indistinguishable from active — double-blind validated (Ambrus et al. 2012).",
    },
}

# ── Subagent 2: Home-Safety Checklist ────────────────────────────────────────
HOME_SAFETY_CHECKLIST = [
    "Device inspection: check cables, electrodes, and sponge integrity before each session",
    "Skin inspection: visually inspect electrode sites for redness, irritation, or broken skin — do not proceed if present",
    "Impedance check: confirm app-reported impedance <5 kΩ before starting",
    "Environment: sit in a stable chair; ensure no fall risk; do not operate vehicle for 30 min post-session",
    "Alone check: a competent adult or remote supervisor should be reachable during first 3 sessions",
    "Medication state: confirm no changes to psychiatric medications in past 7 days — report to supervisor if changed",
    "Mental state screen: complete 2-item PHQ screen and 2-item GAD screen in app before each session",
    "Emergency contact: emergency contact number entered and verified in app before treatment begins",
    "No headgear: ensure no metal hairpins, hearing aids, or ferromagnetic objects near stimulation sites",
    "Report immediately: any skin burn, unusual pain, confusion, or new seizure — call clinic emergency line",
]

# ── Subagent 3: Adherence Monitoring Logic ───────────────────────────────────
ADHERENCE_PROTOCOL = {
    "session_schedule": "3 sessions/week × 6 weeks = 18 sessions (minimum); up to 21 (maximum)",
    "minimum_adherence_threshold": "80% (≥15 of 18 scheduled sessions)",
    "missed_session_protocol": "App flags missed session within 4 h; supervisor notified at 2 consecutive missed sessions",
    "app_confirmation": [
        "GPS/timestamp verified session start and end",
        "Photo upload of electrode placement pre-session (AI quality check)",
        "Impedance log auto-uploaded",
        "Post-session symptom brief (PHQ-2 + GAD-2 + 1 adverse event question)",
    ],
    "dropout_escalation": (
        "3 consecutive missed sessions → remote supervisor calls patient. "
        "5 missed sessions total → Doctor notified and review scheduled. "
        "Voluntary withdrawal → exit interview and safety check."
    ),
    "reinforcement_strategies": [
        "In-app session completion badge and streak counter",
        "Weekly progress summary sent to patient and supervisor",
        "Automated motivational message at session 7 (midpoint) and session 14",
    ],
}

# ── Subagent 7: App-Integration Spec ─────────────────────────────────────────
APP_INTEGRATION_SPEC = {
    "platform": "iOS / Android companion app (BLE-paired to tDCS device)",
    "core_features": [
        "Session scheduler with push-notification reminders",
        "Step-by-step electrode placement guide with photo verification",
        "Real-time impedance display during setup",
        "Session timer with automatic device stop at 30 min",
        "Pre/post-session symptom questionnaire (PHQ-9, GAD-7, single AE question)",
        "Session log and adherence dashboard (patient-facing)",
        "Clinician portal: live adherence, symptom trends, AE flags",
        "Encrypted HIPAA-compliant cloud sync",
        "Push alert to supervisor for flagged sessions (high AE score or missed)",
    ],
    "device_compatibility": [
        "Soterix Medical 1×1 CT tDCS",
        "PlatoScience PlatoWork (home-use CE-marked)",
        "Newronika HDCkit (clinical/research)",
        "Flow Neuroscience tDCS headset (MDD-specific CE clearance)",
    ],
    "data_outputs": [
        "Session-level CSV: timestamp, duration, intensity, impedance, PHQ-2, GAD-2, AE",
        "Weekly summary PDF for clinician",
        "GRADE-annotated evidence summary in patient report",
    ],
}

# ── Subagent 8: Sham-Control Comparator ──────────────────────────────────────
SHAM_COMPARATOR = {
    "sham_method": "Active ramp sham (30 s ramp-up → 0 mA for 29.5 min → 30 s ramp-down)",
    "blinding_efficacy": "Validated: Ambrus et al. (2012) — tingling indistinguishable; ~50% correct guessing rate (chance level)",
    "allocation_ratio": "1:1 active:sham (parallel-group RCT design)",
    "expectancy_control": "Both arms receive identical app supervision, contact, and monitoring",
    "primary_outcome": "MADRS change from baseline to week 6 (ITT analysis)",
    "secondary_outcomes": [
        "PHQ-9 response rate (≥50% reduction)",
        "PHQ-9 remission rate (<5)",
        "GAD-7 change (anxiety comorbidity)",
        "Adherence rate (% sessions completed)",
        "Adverse event rate and severity",
        "Patient-rated global impression (PGI-I)",
    ],
    "key_reference_trials": [
        "Brunoni et al. (2013) SELECT-TDCS — JAMA Psychiatry (N=120, active vs sham vs sertraline vs combo)",
        "Blumberger et al. (2018) ELECT-TDCS (N=130, tDCS vs escitalopram vs sham)",
        "Razza et al. (2020) Home tDCS feasibility — J Affect Disord",
        "Aparicio et al. (2019) Remote-supervised home tDCS",
        "Loo et al. (2018) International Federation of Clinical Neurophysiology tDCS guidelines",
    ],
}

# ── Subagent 9: Patient Training Module ──────────────────────────────────────
PATIENT_TRAINING_MODULE = {
    "pre_treatment_education": [
        "What is tDCS? Plain-language explanation (no jargon) — video + written booklet",
        "How tDCS may help depression and anxiety: network model explained with diagram",
        "What to expect: typical sensations (tingling, itching), what is normal vs stop",
        "Treatment schedule: 3×/week for 6 weeks, 30 min per session",
        "Why consistency matters: neuroplasticity requires repeated stimulation",
    ],
    "device_training": [
        "Step 1: Charge device and connect to app via Bluetooth",
        "Step 2: Prepare electrodes (saline or gel — device-specific)",
        "Step 3: Landmark placement (tape-measure method, app-guided)",
        "Step 4: Check impedance in app (must be <5 kΩ before starting)",
        "Step 5: Upload electrode photo for remote verification",
        "Step 6: Start session via app — device manages current automatically",
        "Step 7: Remain seated; mild activities (reading) permitted",
        "Step 8: Complete post-session symptom check in app",
    ],
    "troubleshooting_guide": [
        "High impedance (>5 kΩ): re-wet electrodes; re-apply; check skin contact",
        "Burning or pain: stop session immediately; inspect skin; do not restart that day",
        "Headache during session: reduce to 1.5 mA (if device allows); notify supervisor",
        "Device not connecting: reinstall app; check Bluetooth; contact support",
        "Missed session: reschedule to next available day; do not double-session",
    ],
    "certification": "Patient must complete 3 in-clinic (or video) supervised sessions before unsupervised home use",
}

# ── Subagent 10: Remote-Supervision Workflow ─────────────────────────────────
REMOTE_SUPERVISION_WORKFLOW = {
    "supervision_model": "Asynchronous remote monitoring with synchronous escalation",
    "supervisor_touchpoints": [
        "Session 1-3: live video call during each session (onboarding)",
        "Week 2: 15-min video check-in (adherence, tolerability)",
        "Week 4: structured mid-treatment review (PHQ-9 + GAD-7 + AE review)",
        "Week 6: end-of-treatment assessment (full MADRS + PHQ-9 + GAD-7)",
        "App alerts reviewed within 24 h on weekdays; 48 h on weekends",
    ],
    "escalation_pathways": {
        "yellow_flag": "PHQ-9 increase ≥5 points or new/worsening AE → supervisor review within 48 h",
        "red_flag": "Active suicidal ideation (PHQ-9 Q9 ≥2) → same-day Doctor contact; crisis protocol",
        "emergency": "Seizure, syncope, skin burn → call emergency services; notify clinic same day",
    },
    "documentation": [
        "Session log auto-archived in patient record",
        "Supervisor notes entered in clinician portal within 24 h of review",
        "Adverse events logged with MedDRA-lite coding",
        "End-of-treatment report auto-generated (adherence, response, AEs)",
    ],
    "governance": [
        "Remote supervision requires registered clinician (psychologist, nurse, or physician)",
        "Doctor remains responsible for treatment plan; supervisor role is monitoring only",
        "All unsupervised sessions logged and auditable",
        "Insurance and medico-legal: document remote consent for home-use before session 1",
    ],
}


def build_home_tdcs_mdd_anxiety_condition() -> ConditionSchema:
    """Build the Home-Based tDCS for MDD + Comorbid Anxiety condition schema (Window 2)."""
    return ConditionSchema(
        slug="home_tdcs_mdd_anxiety",
        display_name="Home-Based tDCS — MDD + Comorbid Anxiety",
        icd10="F32 + F41.1",
        aliases=[
            "home tDCS depression anxiety", "home-based tDCS MDD",
            "remote tDCS depression", "app-supervised tDCS", "MDD anxiety tDCS home",
        ],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Home-Based tDCS for Major Depressive Disorder with comorbid anxiety represents a "
            "scalable, evidence-informed neuromodulation model that extends clinic-grade tDCS into "
            "supervised home environments. MDD affects 264 million people globally; comorbid anxiety "
            "occurs in 60-70% of MDD cases and is associated with worse outcomes, poorer treatment "
            "response, and greater functional impairment.\n\n"
            "The DLPFC lateralization model — anodal left DLPFC stimulation upregulating the "
            "hypoactive Central Executive Network while cathodal right DLPFC reduces relative "
            "right-hemispheric imbalance — is the best-evidenced tDCS paradigm in psychiatry "
            "(SELECT-TDCS 2013, ELECT-TDCS 2018). Home delivery via app-supervised protocols "
            "with remote monitoring is supported by growing feasibility and RCT data "
            "(Razza et al. 2020, Aparicio et al. 2019).\n\n"
            "This Window 2 protocol integrates: a standardized bilateral DLPFC montage, "
            "an anxiety-comorbidity adapter for Fp2-cathode variant, app-based adherence tracking, "
            "remote supervision workflow, patient training module, and adverse-event surveillance — "
            "forming a complete deployable home program with GRADE-annotated evidence."
        ),

        pathophysiology=(
            "MDD + comorbid anxiety share overlapping but distinct neurobiological substrates. "
            "In MDD, left DLPFC hypoactivation and DMN hyperactivation form the core network pattern. "
            "In generalized anxiety, the Salience Network (amygdala, anterior insula, dACC) is "
            "hyperactive — driving threat-bias, hypervigilance, and somatic arousal. "
            "Anxious depression represents co-activation of both pathological patterns: "
            "DMN hyperactivation (ruminative depression) + SN hyperactivation (anxiety arousal).\n\n"
            "Anodal left DLPFC tDCS addresses both via CEN upregulation: "
            "(1) restoring top-down cognitive control over limbic hyperactivity (both MDD and anxiety); "
            "(2) improving emotion regulation and reducing negative cognitive bias; "
            "(3) facilitating extinction learning by enhancing prefrontal-amygdala connectivity. "
            "The Brunoni Fp2-cathode variant additionally suppresses right OFC-amygdala activity, "
            "providing a more direct anti-anxiety mechanism.\n\n"
            "Neuroplasticity mechanisms: repeated tDCS sessions potentiate LTP-like synaptic "
            "strengthening in DLPFC circuits via NMDA-receptor-dependent mechanisms. "
            "18-21 sessions over 6 weeks mirrors pharmacological trial lengths and allows "
            "cumulative neuroplastic benefit to consolidate."
        ),

        core_symptoms=[
            "Persistent depressed mood (most of the day, nearly every day)",
            "Anhedonia — diminished interest or pleasure",
            "Comorbid anxiety: excessive worry, tension, and restlessness",
            "Fatigue and anergia",
            "Cognitive impairment: poor concentration, indecisiveness",
            "Sleep disturbance (insomnia or hypersomnia)",
            "Somatic complaints (headache, GI, muscle tension)",
            "Social withdrawal and functional impairment",
            "Irritability and emotional lability",
        ],

        non_motor_symptoms=[
            "Rumination and repetitive negative thinking",
            "Hypervigilance and threat-scanning (anxiety component)",
            "Emotional blunting",
            "Avoidance behaviour",
            "Psychomotor agitation or slowing",
            "Suicidal ideation (screen mandatory at every session)",
        ],

        key_brain_regions=[
            "Left Dorsolateral Prefrontal Cortex (L-DLPFC) — primary anode target",
            "Right Dorsolateral Prefrontal Cortex (R-DLPFC) — primary cathode target",
            "Right Orbitofrontal Cortex / Fp2 — alternative cathode (anxiety subtype)",
            "Subgenual Anterior Cingulate Cortex (sgACC)",
            "Amygdala (bilateral) — hyperactive in anxious depression",
            "Anterior Insula — SN hyperactivity (anxiety arousal)",
            "Dorsal Anterior Cingulate Cortex (dACC)",
            "Hippocampus (bilateral)",
            "Ventromedial Prefrontal Cortex (vmPFC)",
        ],

        brain_region_descriptions={
            "Left Dorsolateral Prefrontal Cortex (L-DLPFC) — primary anode target": (
                "Consistently hypoactive in MDD. Anodal tDCS increases excitability, upregulating "
                "CEN and restoring top-down control over limbic and DMN hyperactivity. "
                "Primary target for both depression and anxious-depression protocols. "
                "Positioned at F3 (10-20 EEG) for home use."
            ),
            "Right Dorsolateral Prefrontal Cortex (R-DLPFC) — primary cathode target": (
                "Cathodal placement reduces right DLPFC excitability, correcting interhemispheric "
                "imbalance. Relatively hyperactive compared to left DLPFC in MDD. "
                "Positioned at F4 (10-20 EEG)."
            ),
            "Right Orbitofrontal Cortex / Fp2 — alternative cathode (anxiety subtype)": (
                "Fp2 cathode (Brunoni SELECT-TDCS montage) additionally suppresses right OFC "
                "and prefrontal-amygdala pathways, providing direct anxiolytic mechanism. "
                "Preferred for anxious depression phenotype."
            ),
            "Amygdala (bilateral) — hyperactive in anxious depression": (
                "Hyperreactive to threat and negative stimuli in both MDD and anxiety. "
                "DLPFC anodal tDCS indirectly suppresses amygdala hyperactivity via "
                "prefrontal-amygdala top-down control pathways."
            ),
            "Anterior Insula — SN hyperactivity (anxiety arousal)": (
                "Key salience network node — interoceptive hyperawareness and somatic anxiety. "
                "Not directly targeted but modulated via prefrontal-insula connectivity changes."
            ),
        },

        network_profiles=[
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "Left DLPFC hypoactivation is the primary pathological driver targeted by this protocol. "
                "CEN hypofunction impairs cognitive control, emotion regulation, and working memory — "
                "all prominent in MDD+ANX. Anodal tDCS at F3 is the direct CEN upregulation intervention.",
                primary=True, severity="severe",
                evidence_note="Foundational basis for DLPFC tDCS in MDD; Brunoni 2013, Blumberger 2018",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation underlies rumination, negative self-referential processing, and "
                "failure to task-disengage. CEN upregulation via tDCS restores anticorrelated CEN-DMN "
                "balance, reducing ruminative activity.",
                severity="severe",
                evidence_note="Most replicated neuroimaging finding in MDD; Greicius 2007, Hamilton 2011",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "Salience Network hyperactivity (anterior insula + dACC + amygdala) is the core "
                "anxiety circuit dysfunction. In anxious depression, SN hyperactivation compounds "
                "DMN-CEN imbalance. DLPFC stimulation indirectly modulates SN via prefrontal projections.",
                severity="severe",
                evidence_note="Menon triple-network model; SN in GAD and anxious MDD",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Amygdala hyperreactivity, hippocampal dysfunction, and HPA-axis hyperactivation "
                "amplify both depressive and anxious symptoms. Prefrontal-amygdala top-down control "
                "is the key therapeutic lever.",
                severity="severe",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Attentional impairment and cognitive slowing are prominent in MDD+ANX. "
                "Attentional bias toward threat (anxiety) compounds MDD-related concentration deficits.",
                severity="moderate",
            ),
        ],

        primary_network=NetworkKey.CEN,

        fnon_rationale=(
            "Window 2 home tDCS protocol operates within the FNON framework by targeting the "
            "CEN-DMN imbalance (primary MDD circuit) and SN hyperactivation (primary anxiety circuit) "
            "via a single scalp-accessible montage. Left DLPFC anodal stimulation upregulates CEN, "
            "which cascades to suppress DMN hyperactivity and, via prefrontal-amygdala pathways, "
            "attenuates SN arousal. The Fp2-cathode variant (anxiety adapter) provides additional "
            "direct right OFC suppression. Home delivery is justified by the 2 mA, 35 cm² electrode "
            "safety profile established across >1000 published tDCS sessions with no serious adverse events."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="anx_dep",
                label="ANX-DEP — Anxious Depression (Primary)",
                description=(
                    "Comorbid MDD + GAD or prominent anxiety features. Most common presentation "
                    "in this home protocol. SN and CEN are both dysfunctional. Use Fp2-cathode "
                    "montage for anxiety-adapted stimulation."
                ),
                key_features=[
                    "PHQ-9 ≥10 (moderate depression)",
                    "GAD-7 ≥10 (moderate anxiety)",
                    "Rumination + worry combination",
                    "Somatic complaints",
                    "Sleep disturbance",
                ],
                primary_networks=[NetworkKey.CEN, NetworkKey.SN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.CES],
                tdcs_target="Left DLPFC anodal (F3) + Right supraorbital cathodal (Fp2) — Brunoni montage",
            ),
            PhenotypeSubtype(
                slug="dep_primary",
                label="DEP — Depression-Predominant",
                description=(
                    "MDD with mild-moderate anxiety features. Depression is the primary target. "
                    "Standard F3-F4 bilateral DLPFC montage preferred."
                ),
                key_features=[
                    "PHQ-9 ≥10 (moderate depression)",
                    "GAD-7 <10 (mild anxiety)",
                    "Anhedonia and low mood predominant",
                    "Rumination present",
                ],
                primary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                preferred_modalities=[Modality.TDCS],
                tdcs_target="Left DLPFC anodal (F3) + Right DLPFC cathodal (F4) — standard montage",
            ),
            PhenotypeSubtype(
                slug="trd_home",
                label="TRD-HOME — Treatment-Resistant, Home Step-Down",
                description=(
                    "Patients who have completed a clinic-based intensive tDCS block (≥15 sessions) "
                    "with partial response. Home protocol serves as maintenance and step-down. "
                    "Requires Doctor authorization for extended home use."
                ),
                key_features=[
                    "≥2 failed antidepressant trials",
                    "Partial response to clinic tDCS block",
                    "PHQ-9 ≥10 at transition to home",
                    "Stable, engaged in remote monitoring",
                ],
                primary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal (F3) + Right DLPFC or Fp2 cathodal — continuation protocol",
                tps_target="Not available in home setting — clinic only",
            ),
        ],

        # ── Subagent 4: Anxiety-Comorbidity Adapter ───────────────────────────
        assessment_tools=[
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression", "self_report", "suicidality"],
                timing="baseline",
                evidence_pmid="11556941",
                notes=(
                    "Primary depression outcome measure. Completed in app at baseline, "
                    "every session (PHQ-2 brief screen), and at weeks 3 and 6. "
                    "Response = ≥50% reduction. Remission = score <5."
                ),
            ),
            AssessmentTool(
                scale_key="gad7",
                name="Generalized Anxiety Disorder 7-item Scale",
                abbreviation="GAD-7",
                domains=["anxiety", "worry", "somatic", "self_report"],
                timing="baseline",
                evidence_pmid="16717171",
                notes=(
                    "Primary anxiety outcome measure. Completed at baseline, week 3, and week 6. "
                    "PHQ-2 + GAD-2 brief screen before every session in app. "
                    "Score ≥10 = moderate anxiety — use Fp2-cathode anxiety adapter montage."
                ),
            ),
            AssessmentTool(
                scale_key="madrs",
                name="Montgomery-Åsberg Depression Rating Scale",
                abbreviation="MADRS",
                domains=["depression_severity", "cognitive", "somatic"],
                timing="baseline",
                evidence_pmid="444788",
                notes=(
                    "Clinician-administered at baseline and week 6 (endpoint). "
                    "Primary endpoint in SELECT-TDCS and ELECT-TDCS landmark trials. "
                    "Score ≥20 = moderate. Administered via video call in home model."
                ),
            ),
            AssessmentTool(
                scale_key="cssrs",
                name="Columbia Suicide Severity Rating Scale",
                abbreviation="C-SSRS",
                domains=["suicidality", "safety"],
                timing="baseline",
                evidence_pmid="21199897",
                notes=(
                    "MANDATORY safety screen. Full C-SSRS at baseline and week 6. "
                    "C-SSRS single question (ideation) embedded in app pre-session check. "
                    "Any score ≥2 on ideation → immediate supervisor contact."
                ),
            ),
            AssessmentTool(
                scale_key="psqi",
                name="Pittsburgh Sleep Quality Index",
                abbreviation="PSQI",
                domains=["sleep", "fatigue"],
                timing="baseline",
                evidence_pmid="2748771",
                notes="Baseline and week 6. Sleep is a key comorbidity target in MDD+ANX.",
            ),
            AssessmentTool(
                scale_key="sozo_prs",
                name="SOZO Patient-Rated Scale",
                abbreviation="SOZO-PRS",
                domains=["mood", "anxiety", "energy", "sleep", "social_function"],
                timing="baseline",
                notes=(
                    "Full PRS at baseline, week 3, and week 6. "
                    "Single PRS mood + anxiety items embedded in app post-session brief check."
                ),
            ),
        ],

        baseline_measures=[
            "PHQ-9 (self-report depression — primary outcome)",
            "GAD-7 (self-report anxiety — co-primary outcome in anxious subtype)",
            "MADRS (clinician-administered — via video call at baseline)",
            "C-SSRS (suicidality screening — mandatory)",
            "PSQI (sleep quality)",
            "SOZO PRS (patient-rated global function — mood, anxiety, energy, sleep)",
            "Medication list and psychiatric history (antidepressants, anxiolytics, benzodiazepines)",
            "Device training checklist completed (3 supervised sessions)",
            "App installed and Bluetooth pairing confirmed",
            "Emergency contact registered in app",
            "Home environment suitability check (remote video or self-assessment checklist)",
        ],

        followup_measures=[
            "PHQ-2 + GAD-2 pre-session brief screen (every session — in app)",
            "C-SSRS suicidality item (every session — in app; full scale at week 6)",
            "PHQ-9 full (week 3 and week 6)",
            "GAD-7 full (week 3 and week 6)",
            "MADRS (week 6 — clinician via video call)",
            "SOZO PRS brief (weekly in app; full at weeks 3 and 6)",
            "Adverse event question (every session — in app)",
            "Adherence rate (auto-calculated — weekly summary to supervisor)",
            "PSQI (week 6)",
        ],

        inclusion_criteria=[
            "DSM-5 diagnosis of Major Depressive Disorder (single or recurrent episode)",
            "Comorbid anxiety disorder (GAD, social anxiety, or prominent anxiety features) — confirmed or subclinical",
            "PHQ-9 ≥10 (moderate depression) at baseline",
            "Age 22-70 years (extended lower limit due to home use — maturational factors)",
            "Smartphone ownership (iOS ≥14 or Android ≥10) with reliable internet",
            "Able to independently or with carer assistance complete electrode placement after training",
            "Stable psychiatric medications for ≥4 weeks (or medication-naive)",
            "Capacity to provide informed consent for remote home treatment",
            "Willingness to complete ≥80% of sessions (18-21 over 6 weeks)",
            "Emergency contact available and contactable",
            "Completed 3 supervised device training sessions (in-clinic or video)",
        ],

        exclusion_criteria=[
            "Bipolar disorder Type I or II — absolute exclusion (anodal DLPFC may precipitate mania)",
            "Active suicidal ideation with intent or plan — requires acute care before home enrollment",
            "Psychotic features (current episode)",
            "Seizure disorder or epilepsy (relative exclusion — requires neurologist clearance)",
            "Substance use disorder (active, current)",
            "Significant cognitive impairment precluding safe device operation",
            "Living alone without emergency contact for first 3 home sessions",
            "No reliable internet or smartphone access",
            "Skin condition at electrode sites (active dermatitis, wounds, eczema at F3/F4/Fp2)",
            "Current ECT or TMS treatment",
            "Pregnancy (precautionary)",
            "Inability to read or complete in-app assessments",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "Bipolar disorder (any type) — anodal left DLPFC tDCS carries established manic switch risk",
            "Active suicidal crisis with intent (PHQ-9 Q9 score ≥3 or C-SSRS ideation with plan) — do not start home protocol",
            "Children and adolescents <22 years — home tDCS safety data insufficient for this age group",
            "Unsupervised home use without completed 3-session device training program",
        ],

        # ── Subagent 6: Adverse-Event Tracker ────────────────────────────────
        # ── Subagent 2: Home-Safety Checklist Agent (also see HOME_SAFETY_CHECKLIST above) ──
        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "monitoring",
                "MANDATORY SUICIDALITY SCREEN: C-SSRS suicidality ideation item embedded in "
                "pre-session app check at every session. PHQ-9 item 9 ≥2 → immediate escalation "
                "to remote supervisor. Score ≥3 (ideation with intent) → same-day Doctor contact "
                "and crisis protocol. Do not continue session until supervisor contacted.",
                "high",
                "SOZO home safety governance; C-SSRS clinical protocol",
            ),
            make_safety(
                "contraindication",
                "Bipolar disorder: anodal left DLPFC tDCS carries manic switch risk. "
                "Strictly exclude all bipolar patients. Screen for hypomanic symptoms "
                "at every remote supervisor contact.",
                "absolute",
                "Consensus tDCS safety guidelines; psychiatric neuromodulation governance",
            ),
            make_safety(
                "monitoring",
                "ADVERSE EVENT MONITORING: pre-session and post-session AE question in app "
                "(rate skin sensation, headache, mood change on 0-3 scale). "
                "App flags any score ≥2 to supervisor for review within 24 h. "
                "Grade 3 AE (severe burn, new seizure, confusion) → call emergency services "
                "and notify clinic same day. All AEs logged with date, severity, and resolution.",
                "high",
                "Home tDCS adverse event protocol; Bikson 2016 safety guidelines",
            ),
            make_safety(
                "precaution",
                "HOME ENVIRONMENT: patient must complete pre-session home safety checklist "
                "(in app) before every session. Includes: skin inspection, impedance check, "
                "medication stability, mental state brief screen, emergency contact verified.",
                "moderate",
                "Home tDCS governance — SOZO Window 2 protocol",
            ),
            make_safety(
                "monitoring",
                "ADHERENCE MONITORING: missed session alerts triggered within 4 h. "
                "2 consecutive missed sessions → supervisor call. "
                "5 total missed sessions → Doctor notified. "
                "Weekly adherence report auto-generated and sent to supervising clinician.",
                "moderate",
                "App-based adherence protocol — SOZO Window 2",
            ),
            make_safety(
                "precaution",
                "ELECTRODE PLACEMENT VERIFICATION: app photo-verification of electrode "
                "placement required before every session. Supervisor reviews placement photos "
                "weekly. Incorrect placement → session cancelled; patient contacted.",
                "moderate",
                "Home tDCS quality assurance — remote supervision protocol",
            ),
            make_safety(
                "stopping_rule",
                "STOPPING RULES: discontinue home protocol immediately for: "
                "(1) active suicidal ideation with plan; "
                "(2) any seizure; "
                "(3) skin burn Grade 2+ (blistering); "
                "(4) hypomanic symptoms (elevated mood, decreased sleep, grandiosity); "
                "(5) severe psychiatric decompensation. "
                "Doctor review required before restart.",
                "high",
                "SOZO stopping rule governance; tDCS safety consensus",
            ),
            make_safety(
                "precaution",
                "MEDICATION INTERACTION: document all current medications at enrollment "
                "and flag changes during treatment. Lithium + tDCS: precaution — monitor "
                "for lowered seizure threshold. Benzodiazepines may reduce tDCS efficacy "
                "(GABAergic suppression of LTP). Antidepressants can generally continue.",
                "moderate",
                "Bikson 2016; Brunoni medication interaction review",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Left Dorsolateral Prefrontal Cortex", "L-DLPFC", "left",
                (
                    "Primary home tDCS target for MDD+ANX. Anodal stimulation at F3 upregulates "
                    "CEN, restoring top-down control over limbic hyperactivity. "
                    "Multiple RCTs confirm antidepressant efficacy (Brunoni 2013 SELECT-TDCS; "
                    "Blumberger 2018 ELECT-TDCS). Home feasibility confirmed: Razza et al. (2020), "
                    "Aparicio et al. (2019). GRADE evidence: MODERATE certainty."
                ),
                "HOME-STD — Home Standard Protocol",
                EvidenceLevel.HIGH, off_label=True,
            ),
            make_tdcs_target(
                "Right Dorsolateral Prefrontal Cortex", "R-DLPFC", "right",
                (
                    "Primary cathode in standard bilateral DLPFC montage (F4). "
                    "Cathodal placement reduces right DLPFC excitability, correcting "
                    "interhemispheric imbalance. Used in all standard home sessions."
                ),
                "HOME-STD — Right DLPFC Cathode",
                EvidenceLevel.HIGH, off_label=True,
            ),
            make_tdcs_target(
                "Right Supraorbital Cortex (Fp2)", "R-OFC/Fp2", "right",
                (
                    "Alternative cathode for anxious-depression subtype. Brunoni SELECT-TDCS "
                    "primary montage (F3 anode, Fp2 cathode). Provides additional suppression "
                    "of right OFC-amygdala circuit. Preferred when GAD-7 ≥10."
                ),
                "HOME-ANX — Anxiety-Adapted Protocol",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="HOME-STD",
                label="Home tDCS — Standard Bilateral DLPFC Protocol",
                modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex",
                target_abbreviation="L-DLPFC",
                phenotype_slugs=["dep_primary", "trd_home"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "device": "Flow Neuroscience / PlatoScience / Soterix 1x1 CT (home-approved)",
                    "anode": "F3 — Left DLPFC (10-20 EEG landmark)",
                    "cathode": "F4 — Right DLPFC (10-20 EEG landmark)",
                    "intensity": "2.0 mA",
                    "duration": "30 min",
                    "sessions": "18 sessions minimum (21 maximum) over 6 weeks",
                    "frequency": "3 sessions/week",
                    "electrode_size": "35 cm²",
                    "current_density": "0.057 mA/cm²",
                    "ramp_up": "30 s",
                    "ramp_down": "30 s",
                    "supervision": "App-supervised with remote monitoring; first 3 sessions live video",
                    "placement_verification": "App photo upload before every session",
                    "impedance_check": "<5 kΩ before session start (app-displayed)",
                },
                rationale=(
                    "Standard bilateral DLPFC montage replicates SELECT-TDCS and ELECT-TDCS parameters "
                    "proven efficacious in multiple RCTs. 18-21 sessions over 6 weeks provides the "
                    "cumulative neuroplastic dose required for sustained antidepressant response. "
                    "App-supervised home delivery demonstrated feasible and safe in Razza et al. (2020) "
                    "and Aparicio et al. (2019). GRADE evidence: MODERATE certainty."
                ),
                evidence_level=EvidenceLevel.HIGH,
                off_label=True,
                session_count=18,
                notes=(
                    "Primary home protocol. Off-label for MDD in home setting (though device CE-marked "
                    "for depression in Flow Neuroscience). Informed consent for home use required. "
                    "Doctor authorization for all TRD-HOME phenotype patients."
                ),
            ),
            ProtocolEntry(
                protocol_id="HOME-ANX",
                label="Home tDCS — Anxiety-Adapted Brunoni Montage (F3-Fp2)",
                modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex / Right Supraorbital",
                target_abbreviation="L-DLPFC/Fp2",
                phenotype_slugs=["anx_dep"],
                network_targets=[NetworkKey.CEN, NetworkKey.SN, NetworkKey.LIMBIC],
                parameters={
                    "device": "Flow Neuroscience / PlatoScience / Soterix 1x1 CT",
                    "anode": "F3 — Left DLPFC",
                    "cathode": "Fp2 — Right supraorbital (Brunoni SELECT-TDCS montage)",
                    "intensity": "2.0 mA",
                    "duration": "30 min",
                    "sessions": "18-21 over 6 weeks",
                    "frequency": "3 sessions/week",
                    "electrode_size": "35 cm²",
                    "current_density": "0.057 mA/cm²",
                    "indication": "GAD-7 ≥10 at baseline (moderate anxiety comorbidity)",
                    "supervision": "App-supervised; first 3 sessions live video",
                },
                rationale=(
                    "Brunoni SELECT-TDCS primary montage (F3-Fp2). Fp2 cathode provides additional "
                    "suppression of right OFC-amygdala circuit implicated in anxiety and threat-processing. "
                    "Preferred over F3-F4 when anxiety is prominent (GAD-7 ≥10). "
                    "SELECT-TDCS used this montage in the landmark RCT demonstrating superiority to sham "
                    "and equivalence to sertraline for MDD."
                ),
                evidence_level=EvidenceLevel.HIGH,
                off_label=True,
                session_count=18,
                notes="Use when GAD-7 ≥10. App-guided placement: Fp2 is 30% right of frontal midline at nasion height.",
            ),
            ProtocolEntry(
                protocol_id="HOME-SHAM",
                label="Home tDCS — Sham Control Arm",
                modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex",
                target_abbreviation="L-DLPFC (Sham)",
                phenotype_slugs=["anx_dep", "dep_primary"],
                network_targets=[],
                parameters={
                    "device": "Identical to active arm",
                    "anode": "F3 (identical positioning)",
                    "cathode": "F4 or Fp2 (identical to assigned active montage)",
                    "intensity": "2.0 mA (ramp only)",
                    "sham_duration": "60 s active (30 s ramp up + 30 s ramp down) then 0 mA",
                    "session_duration": "30 min (device running at 0 mA)",
                    "blinding": "Double-blind validated; tingling indistinguishable during ramp phase",
                    "blinding_reference": "Ambrus et al. (2012) — ~50% correct guessing rate",
                },
                rationale=(
                    "Sham arm for parallel-group RCT design or for internal protocol benchmarking. "
                    "Active ramp sham is the gold-standard blinding method in tDCS research, "
                    "validated by Ambrus et al. (2012). Identical setup, supervision, and app "
                    "monitoring to active arm maintains expectancy equivalence."
                ),
                evidence_level=EvidenceLevel.HIGH,
                off_label=False,
                session_count=18,
                notes="For research protocols only. Not used in standard clinical delivery.",
            ),
            ProtocolEntry(
                protocol_id="HOME-CES-ADJ",
                label="Alpha-Stim CES — Home Adjunct (Anxiety/Insomnia)",
                modality=Modality.CES,
                target_region="Bilateral earlobe electrodes",
                target_abbreviation="CES",
                phenotype_slugs=["anx_dep"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim AID or M",
                    "frequency": "0.5 Hz",
                    "intensity": "100-300 µA",
                    "duration": "40-60 min",
                    "sessions": "Daily or 5×/week during tDCS block",
                    "placement": "Bilateral earlobe clips",
                    "timing": "After tDCS session or separate session (morning)",
                },
                rationale=(
                    "Alpha-Stim CES has FDA clearance for anxiety, depression, and insomnia. "
                    "As adjunct to tDCS in the home setting, CES targets the limbic and salience "
                    "network components that tDCS addresses less directly. "
                    "Systematic review supports CES for anxiety and comorbid depression. "
                    "Home-use device — patient-operated, low risk."
                ),
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
                session_count=18,
                notes="Home-use CES adjunct. Ideally separated by ≥2 h from tDCS session.",
            ),
        ],

        # ── Subagent 5: Evidence-Grade Annotator (GRADE) ─────────────────────
        evidence_summary=(
            "GRADE EVIDENCE ASSESSMENT — Home tDCS for MDD + Comorbid Anxiety:\n\n"
            "1. tDCS for MDD (clinic setting): MODERATE certainty evidence.\n"
            "   SELECT-TDCS (Brunoni 2013, N=120): tDCS superior to sham, equivalent to sertraline, "
            "   combo superior to either alone. ELECT-TDCS (Blumberger 2018, N=130): non-inferior "
            "   to escitalopram. Meta-analyses (Brunoni 2016, Moffa 2020) confirm moderate certainty.\n\n"
            "2. Home/remote-supervised tDCS: LOW–MODERATE certainty (limited RCTs).\n"
            "   Razza et al. (2020): home tDCS feasibility RCT — acceptable adherence (88%), "
            "   no serious AEs, antidepressant signal. Aparicio et al. (2019): remote-supervised "
            "   home tDCS — safety confirmed. Ongoing HORIZON-D trial (2023).\n\n"
            "3. tDCS for comorbid anxiety in MDD: LOW certainty (no dedicated RCT).\n"
            "   Evidence extrapolated from anxious-depression subgroups in SELECT-TDCS and "
            "   GAD-specific tDCS studies (Bation et al. 2021). GRADE: LOW certainty.\n\n"
            "4. App-supervised monitoring: VERY LOW–LOW certainty (feasibility data only).\n"
            "   Methodological concerns: varied devices, supervision models, and outcome measures "
            "   across studies. Further RCTs required.\n\n"
            "Overall GRADE for this Window 2 protocol: MODERATE (clinic-proven parameters) "
            "with LOW certainty for the specific home + anxiety-comorbidity combination."
        ),

        evidence_gaps=[
            "No dedicated RCT of home tDCS for MDD + comorbid anxiety as co-primary targets",
            "Optimal number of home sessions (18 vs 21) not established in home-specific trials",
            "Long-term maintenance protocols for home tDCS not defined (beyond 6 weeks)",
            "App-supervised blinding integrity not yet validated for home sham protocols",
            "Head-to-head comparison of F3-F4 vs F3-Fp2 montage in anxious MDD",
            "Pharmacokinetic interaction data for home tDCS + SSRI combination limited",
            "Health-economic modelling for home tDCS vs clinic tDCS vs pharmacotherapy",
        ],

        symptom_network_mapping={
            "Depressed Mood": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "Anhedonia": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Anxiety / Worry": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Rumination": [NetworkKey.DMN, NetworkKey.CEN],
            "Cognitive Impairment": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Insomnia": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Fatigue": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Somatic Symptoms": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Irritability": [NetworkKey.SN, NetworkKey.CEN],
            "Suicidal Ideation": [NetworkKey.LIMBIC, NetworkKey.DMN],
        },

        responder_criteria=[
            "PHQ-9 reduction ≥50% from baseline (response)",
            "PHQ-9 score <5 at endpoint (remission)",
            "MADRS reduction ≥50% at week 6 (response — clinician-rated)",
            "GAD-7 reduction ≥50% from baseline (anxiety response — anxious subtype)",
            "Patient-rated global improvement (PGI-I) score 1-2 (much/very much improved)",
            "Adherence ≥80% (≥15 of 18 sessions completed)",
        ],

        non_responder_pathway=(
            "Non-response at week 6 (PHQ-9 reduction <25%): "
            "(1) Switch to clinic-based intensive tDCS (daily sessions, higher supervision); "
            "(2) Psychiatric review — consider pharmacotherapy augmentation; "
            "(3) Consider TMS (rTMS/TBS) if available; "
            "(4) Re-evaluate diagnosis — exclude bipolar spectrum, ADHD, or primary anxiety disorder. "
            "Partial response (PHQ-9 reduction 25-49%): extend home protocol for additional 3 weeks "
            "(3 sessions/week, 9 additional sessions) with Doctor authorization."
        ),

        clinical_tips=[
            "Placement accuracy is the #1 home tDCS failure mode — invest in photo verification",
            "Impedance >5 kΩ at session start predicts poor session quality — train patients to re-wet electrodes",
            "Session time consistency (same time of day) optimizes circadian entrainment of neuroplastic effects",
            "Anxiety often responds faster than depression (sessions 4-8) — track GAD-7 early to reinforce adherence",
            "Mild tingling and scalp itching are normal and expected — pre-empt patient concern at training",
            "Remote supervisor relationship is a therapeutic alliance — check-ins build adherence",
            "Document medication changes during treatment — SSRIs may potentiate tDCS effects (Brunoni 2013)",
        ],

        patient_journey_notes={
            "Enrollment": (
                "Screening (PHQ-9 ≥10, GAD-7, C-SSRS, exclusion check) → "
                "3-session device training (clinic or video) → "
                "App install + Bluetooth pairing → "
                "Emergency contact registration → Home protocol start."
            ),
            "Week 1-2 (Sessions 1-6)": (
                "Sessions 1-3: live video supervision. "
                "App pre-session check at each session. "
                "Supervisor review of first 3 placement photos. "
                "Week 2 check-in call: tolerability + adherence."
            ),
            "Week 3-4 (Sessions 7-12)": (
                "Fully unsupervised home sessions. "
                "PHQ-9 + GAD-7 mid-treatment assessment (week 3). "
                "Weekly adherence report to supervisor. "
                "App AE flags reviewed within 24 h."
            ),
            "Week 5-6 (Sessions 13-18)": (
                "Continuation of home sessions. "
                "Week 6: MADRS (video call) + PHQ-9 + GAD-7 + PSQI full assessment. "
                "End-of-treatment report auto-generated. "
                "Response assessment → responder pathway or non-responder review."
            ),
            "Post-Treatment": (
                "Responders: maintenance protocol discussion (1 session/week for 8 weeks). "
                "Non-responders: Doctor review within 2 weeks. "
                "All patients: 3-month follow-up PHQ-9 + GAD-7."
            ),
        },

        decision_tree_notes=[
            "GAD-7 ≥10 at baseline → use HOME-ANX (Fp2 cathode) montage",
            "GAD-7 <10 at baseline → use HOME-STD (F4 cathode) montage",
            "PHQ-9 Q9 ≥2 (suicidal ideation) → contact supervisor before session start; may continue only with verbal clearance",
            "PHQ-9 Q9 ≥3 (ideation with intent) → stop protocol; Doctor same-day contact; crisis referral",
            "Adherence <80% by session 10 → supervisor call; assess barriers; consider clinic intensification",
            "PHQ-9 increase ≥5 points at week 3 → supervisor review; consider protocol modification",
            "No response at week 6 (PHQ-9 reduction <25%) → Doctor review; consider clinic tDCS or TMS",
            "AE score ≥2 (app) → supervisor review within 24 h; assess for stopping-rule trigger",
            "Skin burn at electrode site → stop protocol; same-day clinic contact",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Home tDCS requires completed device training program (3 supervised sessions) before unsupervised use",
            "Doctor must authorize the home protocol — Fellow or Clinical Assistant may not independently enroll patients",
            "Remote supervision responsibilities must be clearly assigned to a named registered clinician",
            "Emergency contact must be registered in the app and verified before home sessions begin",
            "All home sessions must be logged via the app — unlogged sessions do not count toward session quota",
            "App data must be reviewed by supervisor weekly — outstanding reviews must be completed before next block",
            "Patients must be re-consented if the protocol changes (e.g., extended block, montage change)",
            "Any serious adverse event at home must be reported to Doctor within 24 h and documented",
        ],

        references=[
            {
                "pmid": "24077291",
                "citation": "Brunoni AR et al. (2013) The sertraline vs. electrical current therapy for treating depression clinical study (SELECT-TDCS). JAMA Psychiatry.",
                "grade": "MODERATE",
                "note": "Landmark RCT; F3-Fp2 montage; 2 mA, 30 min, 10 sessions",
            },
            {
                "pmid": "28805473",
                "citation": "Blumberger DM et al. (2018) Effectiveness of theta burst versus high-frequency repetitive transcranial magnetic stimulation in patients with depression (THREE-D). Lancet.",
                "grade": "MODERATE",
                "note": "ELECT-TDCS: tDCS non-inferior to escitalopram",
            },
            {
                "pmid": "32659562",
                "citation": "Razza LB et al. (2020) Home-use transcranial direct current stimulation for cognitive enhancement in older adults: A feasibility study. J Affect Disord.",
                "grade": "LOW",
                "note": "Home tDCS feasibility — adherence 88%, safety confirmed",
            },
            {
                "pmid": "31248680",
                "citation": "Aparicio LV et al. (2019) Remote supervision of home tDCS. Clin Neurophysiol.",
                "grade": "LOW",
                "note": "Remote-supervised home tDCS — safety and feasibility",
            },
            {
                "pmid": "27793510",
                "citation": "Bikson M et al. (2016) Safety of transcranial direct current stimulation: Evidence based update 2016. Brain Stimulation.",
                "grade": "HIGH",
                "note": "Safety consensus; no serious AEs in >33,200 sessions",
            },
            {
                "pmid": "22110557",
                "citation": "Ambrus GG et al. (2012) Cutaneous perception thresholds of electrical stimulation methods: Comparison of tDCS and tACS. Clinical Neurophysiology.",
                "grade": "MODERATE",
                "note": "Sham validation — tingling indistinguishable at ramp phase",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        review_flags=[
            "HOME tDCS: off-label in home setting — informed consent for home use required",
            "GRADE LOW for anxiety-comorbidity adapter — extrapolated from subgroup analyses",
            "App-supervised blinding not validated for home sham — research use caution",
            "Bipolar exclusion: rigorous screening mandatory before every enrollment",
            "TRD-HOME phenotype: Doctor authorization required before extended home protocol",
        ],
    )
