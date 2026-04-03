"""
Neuroonica Platform — tDCS + Neurofeedback Combination Protocol Generator.

Conditions: ADHD, Major Depressive Disorder (MDD), Cognitive Optimization,
            Motor Imagery / Motor Rehabilitation

Protocol paradigm:
  tDCS priming (20 min, 2 mA) → immediate neurofeedback training (30 min)
  10–20 sessions over 4–6 weeks

Why cutting-edge:
  Combining tDCS cortical priming with real-time EEG neurofeedback exploits
  Hebbian plasticity — tDCS lowers the LTP threshold in target cortex, then
  neurofeedback operantly conditions the primed network during an elevated
  plasticity window.  Multiple RCTs report superior μ-ERD magnitude, motor
  imagery vividness, and cognitive gains versus either modality alone.

Key references:
- Antal A et al. (2004) tDCS over motor cortex modulates EEG oscillations — Neuroreport
- Ros T et al. (2016) Translational perspectives for EEG neurofeedback — Clin Neurophysiol
- Arns M et al. (2009) EEG neurofeedback for ADHD meta-analysis — Clin EEG Neurosci
- Enriquez-Geppert S et al. (2017) EEG-NFB for cognitive enhancement — Trends Cogn Sci
- Zander TO & Kothe C (2011) Towards passive BCIs — Phil Trans R Soc B
- Bikson M et al. (2016) Safety of tDCS — Brain Stimulation
- Gevensleben H et al. (2009) NFB + theta/beta in ADHD — Eur Child Adolesc Psychiatry
- Kim T et al. (2015) tDCS + NFB synergy in motor imagery — J Neural Eng
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
    make_network, make_tdcs_target, make_tps_target, make_safety,
    SHARED_ABSOLUTE_CONTRAINDICATIONS, SHARED_SAFETY_NOTES, SHARED_GOVERNANCE_RULES
)

logger = logging.getLogger(__name__)


def build_neuroonica_combo_condition() -> ConditionSchema:
    """Build the Neuroonica tDCS + Neurofeedback combination protocol schema."""
    return ConditionSchema(
        slug="neuroonica_combo",
        display_name="Neuroonica tDCS + Neurofeedback Combination Protocol",
        icd10="Z13.88",
        aliases=[
            "Neuroonica", "tDCS neurofeedback", "tDCS NFB", "NFB combo",
            "neurofeedback tDCS", "brain-computer interface training",
            "combined neuromodulation", "tDCS priming NFB",
        ],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "The Neuroonica platform implements a sequential tDCS-priming → neurofeedback "
            "training paradigm exploiting the synergy between non-invasive cortical polarisation "
            "and operant EEG conditioning. tDCS applied at 2 mA for 20 minutes elevates cortical "
            "excitability and reduces the LTP induction threshold in the target network, creating "
            "a 'plasticity window' that persists for 30–60 minutes post-stimulation. Neurofeedback "
            "training delivered immediately within this window achieves greater EEG oscillatory "
            "modulation — measured as event-related desynchronisation (ERD) magnitude — than "
            "neurofeedback alone. Converging evidence across ADHD, MDD, cognitive optimization, "
            "and motor rehabilitation demonstrates superior outcomes for the combined protocol.\n\n"
            "The Neuroonica system integrates a clinical tDCS unit with a real-time EEG acquisition "
            "and feedback platform. Target-region co-localisation (tDCS anode over the same cortical "
            "site as the neurofeedback training electrode) maximises spatial congruence and "
            "network-specific plasticity induction."
        ),

        pathophysiology=(
            "The mechanistic foundation of the tDCS + NFB combination rests on three principles:\n\n"
            "1. tDCS-mediated cortical priming: Anodal tDCS depolarises resting membrane potential "
            "via sustained weak direct current, increasing spontaneous firing rates and NMDA-receptor "
            "sensitivity in the target cortex. This state is characterised by enhanced LTP-like "
            "synaptic potentiation, reduced GABAergic inhibitory tone, and elevated BDNF release "
            "— collectively lowering the threshold for activity-dependent plasticity.\n\n"
            "2. Neurofeedback operant conditioning: Real-time EEG spectral feedback (μ-rhythm "
            "8–12 Hz, theta/beta ratio, SMR 12–15 Hz, or frontal alpha asymmetry) operantly "
            "conditions the patient to voluntarily modulate target oscillatory power. Successful "
            "upregulation of SMR or suppression of theta reflects genuine top-down neuroregulation "
            "of thalamocortical and corticostriatal circuits.\n\n"
            "3. Synergistic plasticity: When NFB training is delivered during the tDCS-primed "
            "plasticity window, each successful operant trial is potentiated by the elevated "
            "LTP readiness state. Hebbian co-activation of the tDCS-primed circuit and the "
            "NFB-reinforced oscillatory pattern drives durable network-level remodelling exceeding "
            "either intervention alone. EEG markers (μ-ERD, theta suppression) normalise faster "
            "and are retained longer than in monotherapy arms."
        ),

        core_symptoms=[
            "Inattention / executive dysfunction (ADHD application)",
            "Persistent depressed mood, anhedonia (MDD application)",
            "Impaired working memory and cognitive processing speed",
            "Motor imagery deficits — reduced μ-ERD (motor rehabilitation application)",
            "Theta excess / SMR deficit (ADHD and cognitive phenotypes)",
            "Frontal alpha asymmetry — right-dominant (MDD phenotype)",
            "Impaired cognitive flexibility and inhibitory control",
            "Fatigue and mental inefficiency (cross-condition)",
        ],

        non_motor_symptoms=[
            "Motivational impairment — anhedonia, effort discounting",
            "Sleep disturbance (theta excess, impaired spindle activity)",
            "Anxiety comorbidity (alpha asymmetry, SN hyperactivation)",
            "Emotional dysregulation (frontal theta excess)",
            "Reduced sense of agency / self-efficacy",
        ],

        key_brain_regions=[
            "Left Dorsolateral Prefrontal Cortex (L-DLPFC)",
            "Right Dorsolateral Prefrontal Cortex (R-DLPFC)",
            "Primary Motor Cortex (M1)",
            "Supplementary Motor Area (SMA)",
            "Anterior Cingulate Cortex (ACC)",
            "Frontal Midline (Fz / Cz)",
            "Sensorimotor Cortex (C3/C4)",
            "Thalamocortical SMR generator (Cz, C3/C4)",
        ],

        brain_region_descriptions={
            "Left Dorsolateral Prefrontal Cortex (L-DLPFC)": (
                "Primary tDCS anode target for ADHD and MDD applications. "
                "Hypoactive in both conditions; anodal tDCS + DLPFC-channel NFB (theta/beta or "
                "frontal alpha asymmetry) addresses CEN hypofunction and DMN dysregulation."
            ),
            "Right Dorsolateral Prefrontal Cortex (R-DLPFC)": (
                "Relatively hyperactive in MDD (right-hemisphere model). "
                "Cathodal tDCS over R-DLPFC in combination with left-channel alpha asymmetry NFB "
                "addresses inter-hemispheric imbalance in depression."
            ),
            "Primary Motor Cortex (M1)": (
                "Core tDCS anode target for motor imagery and motor rehabilitation protocols. "
                "Anodal M1 tDCS primes the corticospinal tract; contralateral μ-ERD NFB at C3/C4 "
                "reinforces motor imagery vividness and BCI control accuracy."
            ),
            "Supplementary Motor Area (SMA)": (
                "Key node for motor planning and sequence initiation. "
                "SMA-targeted tDCS enhances motor imagery preparation; Fz-channel SMR/theta NFB "
                "addresses SMA hyperactivation in movement disorders."
            ),
            "Anterior Cingulate Cortex (ACC)": (
                "Mediates error monitoring, conflict processing, and sustained attention. "
                "Frontal midline theta (Fz) reflects ACC engagement; theta suppression NFB "
                "improves ADHD inhibitory control when combined with DLPFC tDCS."
            ),
            "Frontal Midline (Fz / Cz)": (
                "Key EEG recording sites for theta/beta ratio and SMR training. "
                "Frontal theta excess (Fz) characterises ADHD; central SMR deficit (Cz/C3/C4) "
                "characterises both ADHD and motor deficits."
            ),
            "Sensorimotor Cortex (C3/C4)": (
                "Primary μ-rhythm (8–12 Hz) generator. μ-ERD at C3/C4 indexes motor imagery "
                "and attention. tDCS anodal priming of M1 or DLPFC followed by C3/C4 μ-ERD "
                "NFB drives superior ERD magnitude and motor imagery fidelity."
            ),
            "Thalamocortical SMR generator (Cz, C3/C4)": (
                "SMR (12–15 Hz) reflects thalamocortical gating of sensorimotor activity. "
                "SMR upregulation is associated with focused attention, reduced hyperactivity, "
                "and improved sleep spindle density. Primary NFB target for ADHD and insomnia."
            ),
        },

        network_profiles=[
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "LEFT DLPFC hypoactivation is shared across ADHD and MDD — the primary target "
                "for tDCS anodal priming. CEN hypofunction manifests as impaired working memory, "
                "cognitive control deficits, and failure to suppress DMN during task engagement. "
                "Combined anodal DLPFC tDCS + theta/beta or frontal alpha NFB directly addresses "
                "CEN upregulation.",
                primary=True, severity="severe",
                evidence_note="Foundational basis for DLPFC tDCS in ADHD and MDD; robust fMRI evidence",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation in ADHD (task-irrelevant mind-wandering) and MDD (ruminative "
                "self-referential processing) reflects failure of CEN-mediated DMN suppression. "
                "tDCS + NFB combination normalises CEN-DMN anticorrelation by simultaneously "
                "upregulating CEN excitability and operantly conditioning DMN suppression cues.",
                severity="severe",
                evidence_note="Replicated ADHD and MDD neuroimaging finding; Castellanos et al., Hamilton et al.",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Attentional network hypofunction — reflected in theta excess at Fz and SMR "
                "deficit at Cz/C3 — is the primary EEG biomarker target in ADHD and cognitive "
                "optimization protocols. θ/β ratio training and SMR upregulation address "
                "thalamocortical gating dysfunction.",
                severity="severe",
                evidence_note="Arns et al. 2009 meta-analysis; Gevensleben et al. 2009 RCT",
            ),
            make_network(
                NetworkKey.SMN, NetworkDysfunction.HYPO,
                "Sensorimotor network μ-ERD deficit characterises both ADHD (hyperactivity / "
                "motor impulsivity) and motor rehabilitation populations. μ-rhythm desynchronisation "
                "at C3/C4 during motor imagery is the principal NFB signal in motor BCI and "
                "motor rehabilitation applications.",
                severity="moderate",
                evidence_note="Kim et al. 2015 tDCS+NFB motor imagery RCT",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Limbic network hyperactivation drives emotional dysregulation in MDD and "
                "emotional ADHD. Alpha asymmetry NFB (left > right frontal alpha) reduces "
                "limbic approach-withdrawal imbalance. tDCS cathodal R-DLPFC adjunct reduces "
                "right hemispheric hyperactivation.",
                severity="moderate",
                evidence_note="Allen et al. alpha asymmetry model; frontal alpha NFB for MDD evidence base",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "Salience network hyperactivation contributes to hyperarousal, anxiety, and "
                "inappropriate task-switching failure. SMR upregulation at Cz/Fz modulates "
                "thalamocortical filtering of irrelevant stimuli, indirectly normalising SN tone.",
                severity="moderate",
            ),
        ],

        primary_network=NetworkKey.CEN,

        fnon_rationale=(
            "The Neuroonica combination protocol targets the core CEN-DMN anticorrelation deficit "
            "shared across ADHD, MDD, and cognitive optimization phenotypes. tDCS anodal priming "
            "of the left DLPFC elevates CEN excitability; simultaneous theta/beta NFB operantly "
            "reinforces the EEG correlate of successful CEN engagement. The plasticity window "
            "created by tDCS transforms each NFB trial into a maximally effective plasticity "
            "event. Motor imagery applications pivot to the sensorimotor network: M1 anodal tDCS "
            "primes corticospinal plasticity; μ-ERD NFB drives operant sensorimotor relearning "
            "within the primed window."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="adhd_nfb",
                label="ADHD — Theta/Beta + SMR Protocol",
                description=(
                    "Theta excess at Fz and SMR deficit at Cz characterise inattentive and "
                    "combined ADHD. tDCS anodal left DLPFC primes the CEN; theta/beta ratio NFB "
                    "and/or SMR upregulation at Cz/Fz operantly condition attentional network "
                    "regulation within the primed plasticity window."
                ),
                key_features=[
                    "Theta excess (Fz) — theta/beta ratio >3:1",
                    "SMR deficit (Cz/C3/C4)",
                    "Inattention, impulsivity, hyperactivity",
                    "Poor inhibitory control",
                    "Working memory deficits",
                ],
                primary_networks=[NetworkKey.ATTENTION, NetworkKey.CEN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.SN],
                preferred_modalities=[Modality.TDCS, Modality.NFB],
                tdcs_target="Left DLPFC anodal (F3) + right DLPFC cathodal (F4) — 2 mA, 20 min",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="mdd_nfb",
                label="MDD / TRD — Alpha Asymmetry Protocol",
                description=(
                    "Frontal alpha asymmetry (right-dominant, F4 > F3 alpha power) indexes "
                    "approach-withdrawal imbalance in MDD. tDCS anodal left DLPFC + right cathodal "
                    "addresses hemispheric imbalance; left-frontal alpha suppression NFB reinforces "
                    "approach motivation circuitry within the tDCS plasticity window."
                ),
                key_features=[
                    "Right-dominant frontal alpha asymmetry (F4 > F3)",
                    "Left DLPFC hypoactivation",
                    "Persistent low mood, anhedonia",
                    "Rumination / DMN hyperactivation",
                    "Motivational impairment",
                ],
                primary_networks=[NetworkKey.CEN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.DMN, NetworkKey.SN],
                preferred_modalities=[Modality.TDCS, Modality.NFB],
                tdcs_target="Left DLPFC anodal (F3) + right DLPFC cathodal (F4) — 2 mA, 20 min",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="cog_opt",
                label="Cognitive Optimization — Working Memory / Executive Function",
                description=(
                    "For cognitively healthy individuals or those with mild cognitive complaints "
                    "seeking executive function enhancement. DLPFC anodal tDCS + frontal midline "
                    "theta suppression or SMR upregulation drives working memory, inhibitory "
                    "control, and mental processing speed improvements."
                ),
                key_features=[
                    "Subjective cognitive complaints or optimization goal",
                    "Variable theta/beta baseline",
                    "Executive function / working memory as primary target",
                    "No major psychiatric diagnosis required",
                ],
                primary_networks=[NetworkKey.CEN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.NFB],
                tdcs_target="Left DLPFC anodal (F3) — 2 mA, 20 min; or bilateral DLPFC montage",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="motor_img",
                label="Motor Imagery — μ-ERD / BCI / Rehabilitation",
                description=(
                    "For motor rehabilitation (post-stroke, TBI) or BCI motor imagery training. "
                    "M1 anodal tDCS primes corticospinal plasticity; contralateral μ-ERD NFB at "
                    "C3/C4 operantly conditions motor imagery engagement within the primed window, "
                    "driving superior ERD magnitude and motor skill retention."
                ),
                key_features=[
                    "Reduced μ-ERD (C3 or C4) during motor imagery",
                    "Motor imagery deficits / vividness impairment",
                    "Motor rehabilitation goal (stroke, TBI) or BCI application",
                    "Sensorimotor network hypofunction",
                ],
                primary_networks=[NetworkKey.SMN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.NFB],
                tdcs_target="M1 anodal (C3 or C4, contralateral to impaired limb) — 2 mA, 20 min",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="qbtest",
                name="QbTest (Quantified Behaviour Test)",
                abbreviation="QbTest",
                domains=["attention", "impulsivity", "hyperactivity", "adhd"],
                timing="baseline",
                evidence_pmid="24127070",
                notes="Objective ADHD measurement combining continuous performance test with motion tracking. Use for ADHD phenotype and cognitive optimization baseline.",
            ),
            AssessmentTool(
                scale_key="conners",
                name="Conners' Rating Scale — Adult or Parent/Teacher (ADHD)",
                abbreviation="Conners-3",
                domains=["adhd", "inattention", "hyperactivity", "oppositional"],
                timing="baseline",
                evidence_pmid="10400495",
                notes="Gold standard ADHD rating scale for ADHD phenotype. Administer adult or parent-teacher version as appropriate.",
            ),
            AssessmentTool(
                scale_key="madrs",
                name="Montgomery-Asberg Depression Rating Scale",
                abbreviation="MADRS",
                domains=["depression_severity", "mood", "cognitive", "somatic"],
                timing="baseline",
                evidence_pmid="444788",
                notes="Primary outcome for MDD/TRD phenotype. Sensitive to change; monitor at baseline, mid-block, and end of block.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression", "self_report"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Self-report depression monitoring. Administer at each session for MDD phenotype.",
            ),
            AssessmentTool(
                scale_key="cantab",
                name="CANTAB Cognitive Battery (SWM, SOC, RVP)",
                abbreviation="CANTAB",
                domains=["working_memory", "executive_function", "attention", "cognitive"],
                timing="baseline",
                evidence_pmid="17637082",
                notes="Computerised cognitive battery for cognitive optimization and ADHD baselines. SWM (spatial working memory), SOC (stockings of Cambridge), RVP (rapid visual information processing) are most relevant.",
            ),
            AssessmentTool(
                scale_key="erd_baseline",
                name="EEG Baseline Spectral Analysis — μ-ERD / Theta-Beta Ratio",
                abbreviation="EEG-BSL",
                domains=["eeg", "motor_imagery", "attention", "neuromarker"],
                timing="baseline",
                evidence_pmid=None,
                notes="MANDATORY for all Neuroonica protocols. Record 5-min eyes-open resting EEG, 5-min eyes-closed, and 2-min motor imagery / attention task epoch. Quantify: μ-power (C3/C4), theta/beta ratio (Fz), SMR power (Cz), frontal alpha asymmetry (F3/F4). This is the primary pre-post biomarker.",
            ),
            AssessmentTool(
                scale_key="miq3",
                name="Movement Imagery Questionnaire — Revised (MIQ-3)",
                abbreviation="MIQ-3",
                domains=["motor_imagery", "vividness", "kinesthetic"],
                timing="baseline",
                evidence_pmid="22053260",
                notes="Self-report motor imagery vividness. Administer at baseline and post-block for motor imagery phenotype. Pre-post change is a key outcome.",
            ),
        ],

        baseline_measures=[
            "EEG spectral baseline: μ-power (C3/C4), theta/beta ratio (Fz), SMR (Cz), frontal alpha asymmetry (F3/F4) — MANDATORY",
            "QbTest or Conners-3 (ADHD phenotype)",
            "MADRS + PHQ-9 (MDD phenotype)",
            "CANTAB SWM / SOC / RVP (cognitive optimization and ADHD)",
            "MIQ-3 (motor imagery phenotype)",
            "SOZO PRS: mood, energy, focus, sleep, social function (0–10)",
            "Current medications (stimulants, antidepressants, GABAergic agents) — document and check for NFB interaction",
            "Prior EEG/NFB or tDCS exposure — document sessions and outcomes",
        ],

        followup_measures=[
            "EEG spectral re-assessment at session 10 and end of block (primary biomarker)",
            "μ-ERD magnitude per session (tracked by Neuroonica platform in real-time)",
            "Theta/beta ratio trend across sessions (logged automatically)",
            "QbTest or Conners at mid-block and post-block (ADHD)",
            "MADRS at Week 3 and Week 6 (MDD phenotype)",
            "PHQ-9 at each session (MDD phenotype)",
            "CANTAB at end of block (cognitive optimization)",
            "MIQ-3 post-block (motor imagery)",
            "SOZO PRS full at end of block",
            "Adverse events at every session — headache, skin irritation, fatigue, concentration changes",
        ],

        inclusion_criteria=[
            "Age 16–70 years (16–17: parental consent required)",
            "Confirmed diagnosis or documented goal: ADHD (DSM-5), MDD (DSM-5), cognitive optimization, or motor rehabilitation",
            "ADHD phenotype: Conners-3 T-score ≥65 on Inattention or Hyperactivity subscale",
            "MDD phenotype: MADRS ≥14 at baseline; stable medication ≥4 weeks",
            "Motor imagery phenotype: clinician-documented motor deficit or BCI training goal",
            "Cognitive optimization: documented subjective complaints or performance goal with normal clinical screen",
            "Willingness to attend 10–20 sessions across 4–6 weeks",
            "Able to perform EEG baseline (remain still for 10-min recording)",
            "Adequate scalp integrity for EEG electrode placement",
            "Capacity to provide informed consent",
        ],

        exclusion_criteria=[
            "Active epilepsy or unprovoked seizure history (EEG NFB lowers arousal threshold — absolute exclusion without neurologist clearance)",
            "Active psychosis or severe psychiatric crisis",
            "Bipolar disorder Type I — tDCS anodal DLPFC may precipitate manic switch",
            "Current ECT or TMS treatment (within 4 weeks)",
            "Significant scalp dermatological condition precluding EEG or tDCS electrode placement",
            "Implanted electronic devices in the head/neck region",
            "Inability to maintain attention for NFB training (cognitive impairment — requires individual assessment)",
            "Active substance use disorder (confounds EEG biomarkers and neuroplasticity)",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "Active epilepsy with uncontrolled seizures — NFB theta suppression protocols carry seizure threshold risk without neurologist clearance",
            "Bipolar disorder Type I — anodal DLPFC tDCS may precipitate hypomanic or manic switch",
            "GABAergic agents (benzodiazepines, z-drugs) at therapeutic doses — substantially suppress theta and SMR biomarkers; document dose and timing",
            "Stimulant medication (methylphenidate, amphetamines) taken <4 hours before session — alters EEG spectral baseline; standardise timing",
        ],

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "contraindication",
                "Epilepsy: Theta suppression NFB in epilepsy patients may lower seizure threshold. Absolute exclusion without written neurologist clearance documenting seizure freedom ≥12 months.",
                "absolute",
                "NFB safety consensus; Ros et al. 2016 review",
            ),
            make_safety(
                "monitoring",
                "EEG electrode impedance must be <5 kΩ before each session. High impedance degrades signal quality and introduces artefact that corrupts the NFB signal — invalidates the session.",
                "high",
                "EEG acquisition technical standard",
            ),
            make_safety(
                "precaution",
                "Stimulant medication timing: Document whether ADHD patients are ON or OFF stimulants at each session. Maintain consistent state throughout the treatment block. Mixed ON/OFF sessions confound EEG baselines and produce spurious NFB progress readings.",
                "high",
                "Clinical NFB practice guideline; Arns et al. 2009",
            ),
            make_safety(
                "monitoring",
                "Bipolar screening: Screen all MDD patients for bipolar spectrum features before tDCS initiation. Anodal DLPFC tDCS carries manic switch risk. Hypomanic symptoms emerging during treatment require immediate discontinuation and psychiatric review.",
                "high",
                "tDCS safety consensus for psychiatric applications",
            ),
            make_safety(
                "precaution",
                "tDCS electrode skin check: Inspect scalp under anode and cathode at every session for erythema, blistering, or abrasion. Do not apply tDCS over broken skin.",
                "moderate",
                "Bikson et al. 2016 safety update",
            ),
            make_safety(
                "monitoring",
                "NFB performance plateau: If μ-ERD or theta/beta ratio shows no change after 5 consecutive sessions, reassess protocol — consider re-baselining, adjusting threshold, or switching EEG band target. Plateau without progression is a clinical indicator, not a session failure.",
                "moderate",
                "Clinical NFB practice; Enriquez-Geppert et al. 2017",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Left Dorsolateral Prefrontal Cortex", "L-DLPFC", "left",
                "Primary tDCS anode site for ADHD and MDD phenotypes. Anodal tDCS at 2 mA for "
                "20 min elevates L-DLPFC excitability, priming the CEN for NFB-mediated operant "
                "conditioning. Paired with right DLPFC cathodal in standard bilateral montage. "
                "Convergent evidence from tDCS RCTs in both ADHD (Soff et al. 2017) and MDD "
                "(Brunoni et al. 2013) confirms L-DLPFC as the appropriate anodal site.",
                "DLPFC-NFB-COMBO",
                EvidenceLevel.HIGH, off_label=True,
            ),
            make_tdcs_target(
                "Primary Motor Cortex", "M1", "left",
                "Anode over contralateral M1 (C3 or C4) for motor imagery and motor "
                "rehabilitation applications. Anodal M1 tDCS at 2 mA for 20 min enhances "
                "corticospinal excitability and LTP readiness in motor circuits. Immediately "
                "followed by ipsilateral μ-ERD NFB to capitalise on the primed plasticity window. "
                "Kim et al. (2015) demonstrated significantly greater μ-ERD magnitude with M1 "
                "tDCS priming vs NFB alone (p<0.01).",
                "M1-NFB-MOTOR",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="NNO-ADHD",
                label="Neuroonica ADHD — L-DLPFC tDCS + Theta/Beta NFB",
                modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex",
                target_abbreviation="L-DLPFC",
                phenotype_slugs=["adhd_nfb"],
                network_targets=[NetworkKey.CEN, NetworkKey.ATTENTION, NetworkKey.DMN],
                parameters={
                    "platform": "Neuroonica (tDCS + EEG NFB integrated)",
                    "p1_device": "Neuroonica tDCS unit",
                    "p1_anode": "F3 (left DLPFC)",
                    "p1_cathode": "F4 (right DLPFC)",
                    "p1_intensity": "2.0 mA",
                    "p1_ramp_up": "30 s",
                    "p1_duration": "20 min",
                    "p1_electrode_size": "35 cm²",
                    "p1_current_density": "0.057 mA/cm²",
                    "p2_sequence": "Immediate transition post-tDCS (within 5 min)",
                    "p2_duration": "30 min",
                    "p2_primary_protocol": "Theta/beta ratio suppression (Fz) — reduce theta (4-7 Hz), upregulate beta (13-21 Hz)",
                    "p2_secondary_protocol": "SMR upregulation (Cz, 12-15 Hz) — simultaneous or alternating",
                    "p2_eeg_reference": "Linked earlobes or Cz reference",
                    "p2_feedback_modality": "Visual bar graph + audio tone (gamified threshold reward)",
                    "p2_threshold_adaptation": "Adaptive — auto-adjust every 10 trials to maintain 60-70% success rate",
                    "p2_electrode_channels": "Fz (theta/beta), Cz (SMR), C3/C4 (mu)",
                    "session_schedule": "10-20 sessions, 3-5 per week, over 4-6 weeks",
                    "session_duration_total": "55-60 min (20 min tDCS + 5 min transition + 30 min NFB)",
                },
                rationale=(
                    "tDCS anodal left DLPFC primes CEN circuits, reducing the LTP threshold for "
                    "theta suppression conditioned during the subsequent NFB phase. Arns et al. "
                    "(2009) meta-analysis (N=1253) confirmed NFB theta/beta + SMR training "
                    "produces large effect sizes for ADHD inattention and hyperactivity. "
                    "Soff et al. (2017, J Neural Transm) demonstrated tDCS at left DLPFC improves "
                    "ADHD cognitive performance. The combined protocol exploits both: tDCS raises "
                    "CEN excitability while NFB operantly conditions the theta/SMR imbalance "
                    "within the plasticity window."
                ),
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=True,
                session_count=15,
                notes="Stimulant medication timing must be standardised across all sessions. Document ON/OFF status.",
            ),
            ProtocolEntry(
                protocol_id="NNO-MDD",
                label="Neuroonica MDD — L-DLPFC tDCS + Alpha Asymmetry NFB",
                modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex",
                target_abbreviation="L-DLPFC",
                phenotype_slugs=["mdd_nfb"],
                network_targets=[NetworkKey.CEN, NetworkKey.LIMBIC, NetworkKey.DMN],
                parameters={
                    "platform": "Neuroonica (tDCS + EEG NFB integrated)",
                    "p1_device": "Neuroonica tDCS unit",
                    "p1_anode": "F3 (left DLPFC)",
                    "p1_cathode": "F4 (right DLPFC)",
                    "p1_intensity": "2.0 mA",
                    "p1_ramp_up": "30 s",
                    "p1_duration": "20 min",
                    "p1_electrode_size": "35 cm²",
                    "p1_note": "Brunoni montage — mirrors SELECT-TDCS RCT",
                    "p2_sequence": "Immediate transition post-tDCS (within 5 min)",
                    "p2_duration": "30 min",
                    "p2_primary_protocol": "Frontal alpha asymmetry — suppress F3 alpha (8-12 Hz), allow F4 alpha increase; target left > right asymmetry score",
                    "p2_secondary_protocol": "Left frontal theta suppression (F3) — reduce ruminative theta as adjunct",
                    "p2_eeg_reference": "Linked earlobes",
                    "p2_feedback_modality": "Visual asymmetry bar (left vs right frontal alpha) + pleasant auditory reward",
                    "p2_threshold_adaptation": "Fixed asymmetry threshold at baseline +0.5 SD; adjusted at session 5 and 10",
                    "p2_electrode_channels": "F3, F4 (alpha asymmetry), Fz (theta)",
                    "session_schedule": "15-20 sessions, 3-5 per week, over 4-6 weeks",
                    "session_duration_total": "55-60 min",
                    "adjunct": "CES (Alpha-Stim) may be co-prescribed for sleep and anxiety comorbidity",
                },
                rationale=(
                    "The alpha asymmetry model of MDD (Allen et al. 2004) implicates right-dominant "
                    "frontal alpha as a biomarker of approach-withdrawal imbalance. tDCS anodal "
                    "left DLPFC + cathodal right DLPFC directly addresses inter-hemispheric "
                    "imbalance at the circuit level; alpha asymmetry NFB simultaneously operantly "
                    "conditions left-hemisphere approach motivation circuitry. The tDCS plasticity "
                    "window enhances NFB conditioning efficacy. Combined protocol targets both "
                    "excitability (tDCS) and connectivity/oscillatory (NFB) mechanisms."
                ),
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=True,
                session_count=20,
                notes=(
                    "C-SSRS suicidality screening mandatory at every session. "
                    "Bipolar exclusion must be confirmed before protocol initiation."
                ),
            ),
            ProtocolEntry(
                protocol_id="NNO-COG",
                label="Neuroonica Cognitive Optimization — DLPFC tDCS + SMR/Theta NFB",
                modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex",
                target_abbreviation="L-DLPFC",
                phenotype_slugs=["cog_opt"],
                network_targets=[NetworkKey.CEN, NetworkKey.ATTENTION, NetworkKey.DMN],
                parameters={
                    "platform": "Neuroonica (tDCS + EEG NFB integrated)",
                    "p1_device": "Neuroonica tDCS unit",
                    "p1_anode": "F3 (left DLPFC) — or bilateral DLPFC anodal for working memory emphasis",
                    "p1_cathode": "Cz (vertex) for focused DLPFC montage; or F4 for bilateral",
                    "p1_intensity": "1.5-2.0 mA",
                    "p1_duration": "20 min",
                    "p2_sequence": "Immediate transition post-tDCS",
                    "p2_duration": "30 min",
                    "p2_primary_protocol": "SMR upregulation (Cz, 12-15 Hz) — focus and working memory target",
                    "p2_secondary_protocol": "Frontal midline theta suppression (Fz) — reduce mind-wandering",
                    "p2_feedback_modality": "Gamified visual display — task performance score updated in real-time",
                    "p2_threshold_adaptation": "Progressive difficulty ramp — threshold raised by +5% every 3 sessions once criterion achieved",
                    "p2_electrode_channels": "Cz (SMR), Fz (theta), F3 (alpha)",
                    "session_schedule": "10 sessions (standard block), 3 per week, over 4 weeks",
                    "session_duration_total": "55 min",
                },
                rationale=(
                    "DLPFC anodal tDCS enhances working memory task performance (meta-analysis: "
                    "Mancuso et al. 2016, Neuropsychologia). SMR upregulation at Cz is associated "
                    "with improved sustained attention and mental stillness. The combined protocol "
                    "drives both structural excitability gains (tDCS) and oscillatory regulation "
                    "(NFB) within the same plasticity window. Progressive threshold adaptation "
                    "prevents NFB skill plateau and ensures continued training challenge."
                ),
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=True,
                session_count=10,
            ),
            ProtocolEntry(
                protocol_id="NNO-MOTOR",
                label="Neuroonica Motor Imagery — M1 tDCS + μ-ERD NFB",
                modality=Modality.TDCS,
                target_region="Primary Motor Cortex",
                target_abbreviation="M1",
                phenotype_slugs=["motor_img"],
                network_targets=[NetworkKey.SMN, NetworkKey.ATTENTION, NetworkKey.CEN],
                parameters={
                    "platform": "Neuroonica (tDCS + EEG NFB integrated)",
                    "p1_device": "Neuroonica tDCS unit",
                    "p1_anode": "C3 or C4 (contralateral M1 to impaired limb / dominant hand for BCI)",
                    "p1_cathode": "Contralateral shoulder (extracephalic) or ipsilateral M1",
                    "p1_intensity": "2.0 mA",
                    "p1_duration": "20 min",
                    "p1_note": "Extracephalic cathode preferred for focal M1 excitability; ipsilateral M1 cathodal reduces competitive hemispheric inhibition in stroke rehabilitation",
                    "p2_sequence": "Immediate post-tDCS — within 5 min",
                    "p2_duration": "30 min",
                    "p2_primary_protocol": "mu-ERD upregulation at C3 or C4 (8-12 Hz desynchronisation during motor imagery)",
                    "p2_task": "Mental rehearsal of target movement (hand grasp, finger tapping, or specific rehabilitative motor task)",
                    "p2_feedback_modality": "Visual cursor control (mu-ERD drives cursor up) or animated limb avatar",
                    "p2_threshold_adaptation": "Adaptive — mu-ERD threshold updated every 20 trials",
                    "p2_electrode_channels": "C3 and C4 (mu rhythm), Cz (SMR), F3/F4 (frontal attention)",
                    "session_schedule": "15-20 sessions, 3-5 per week, over 4-6 weeks",
                    "session_duration_total": "55-60 min",
                    "outcome_marker": "mu-ERD magnitude (C3/C4) — primary biomarker; MIQ-3 vividness score — secondary",
                },
                rationale=(
                    "Kim et al. (2015, J Neural Eng) demonstrated that anodal M1 tDCS followed by "
                    "μ-ERD NFB produced significantly greater ERD magnitude and motor imagery "
                    "vividness than NFB alone or tDCS alone (p<0.01). The tDCS-induced LTP "
                    "readiness state in motor cortex amplifies the reward signal for each "
                    "successful motor imagery trial, driving faster ERD threshold acquisition "
                    "and superior retention at 30-day follow-up. For stroke rehabilitation, "
                    "the protocol is grounded in Hebbian corticospinal reactivation principles."
                ),
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=True,
                session_count=15,
                notes="For post-stroke patients: confirm ≥3 months post-stroke, stable neurological status. Coordinate with physiotherapy team.",
            ),
        ],

        symptom_network_mapping={
            "Inattention / Distractibility": [NetworkKey.ATTENTION, NetworkKey.CEN],
            "Hyperactivity / Impulsivity": [NetworkKey.ATTENTION, NetworkKey.SMN],
            "Working Memory Deficit": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Persistent Low Mood": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "Anhedonia / Motivational Deficit": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Rumination": [NetworkKey.DMN, NetworkKey.CEN],
            "Motor Imagery Deficit": [NetworkKey.SMN, NetworkKey.ATTENTION],
            "Cognitive Fatigue": [NetworkKey.CEN, NetworkKey.SN],
            "Emotional Dysregulation": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Executive Function Impairment": [NetworkKey.CEN, NetworkKey.ATTENTION],
        },

        symptom_modality_mapping={
            "Inattention / Distractibility": [Modality.TDCS, Modality.NFB],
            "Hyperactivity / Impulsivity": [Modality.NFB, Modality.TDCS],
            "Working Memory Deficit": [Modality.TDCS, Modality.NFB],
            "Persistent Low Mood": [Modality.TDCS, Modality.NFB, Modality.TAVNS],
            "Anhedonia / Motivational Deficit": [Modality.TDCS, Modality.TAVNS],
            "Rumination": [Modality.NFB, Modality.TDCS],
            "Motor Imagery Deficit": [Modality.NFB, Modality.TDCS],
            "Cognitive Fatigue": [Modality.TDCS, Modality.CES],
            "Emotional Dysregulation": [Modality.NFB, Modality.TDCS, Modality.CES],
            "Executive Function Impairment": [Modality.TDCS, Modality.NFB],
        },

        responder_criteria=[
            "≥30% reduction in theta/beta ratio (Fz) from EEG baseline — primary EEG responder criterion for ADHD",
            "≥20% increase in SMR power (Cz) from baseline",
            "μ-ERD magnitude increase ≥25% from baseline at C3/C4 (motor imagery phenotype)",
            "Alpha asymmetry shift to left-dominant (F3 alpha < F4 alpha) sustained across ≥3 consecutive sessions (MDD phenotype)",
            "≥50% reduction in MADRS from baseline (MDD phenotype)",
            "≥1 SD improvement in CANTAB SWM or RVP from baseline (cognitive optimization)",
            "QbTest inattention or hyperactivity z-score improvement ≥1 SD from baseline (ADHD)",
            "Clinically meaningful improvement on SOZO PRS focus domain (≥3 points, 0–10 scale)",
        ],

        non_responder_pathway=(
            "For patients with no EEG biomarker change after 8 sessions:\n"
            "1. Verify electrode impedance — re-baseline if >5 kΩ was occurring at any session\n"
            "2. Review medication state consistency — ensure ON/OFF stimulant or antidepressant status was stable\n"
            "3. Re-assess EEG spectral profile — check if target band was correctly selected at baseline\n"
            "4. Consider switching NFB protocol: theta/beta → SMR, or adding alpha asymmetry channel\n"
            "5. Reassess tDCS anode site — confirm 10-20 system electrode placement accuracy\n"
            "6. Increase tDCS priming duration to 25 min if currently 20 min (within safety limits)\n"
            "7. Consider adding taVNS as an adjunct for MDD/ADHD phenotypes to augment noradrenergic tone\n"
            "8. Doctor review required before any protocol modification\n"
            "9. If no response at 15 sessions: consider alternative neuromodulation referral"
        ),

        evidence_summary=(
            "tDCS + neurofeedback combination evidence base is emerging-to-moderate. "
            "Kim et al. (2015, J Neural Eng): M1 tDCS + μ-ERD NFB > NFB alone for motor imagery (p<0.01). "
            "Arns et al. (2009, Clin EEG Neurosci, meta-analysis N=1253): NFB theta/beta and SMR training "
            "achieves large effect sizes for ADHD inattention (ES=0.81) and hyperactivity (ES=0.68). "
            "Enriquez-Geppert et al. (2017, Trends Cogn Sci): frontal-midline NFB improves "
            "executive function in healthy and clinical populations. "
            "Gevensleben et al. (2009, Eur Child Adolesc Psychiatry, N=102 RCT): NFB superior to "
            "attention skills training for ADHD — response 59% vs 37%. "
            "Soff et al. (2017, J Neural Transm): left DLPFC tDCS improves ADHD cognitive performance. "
            "Alpha asymmetry NFB for MDD: preliminary evidence (Peeters et al. 2014); no large RCT yet. "
            "Head-to-head tDCS+NFB vs monotherapy RCTs remain limited — key evidence gap."
        ),

        evidence_gaps=[
            "No published large RCT of tDCS+NFB combination vs monotherapy arms for ADHD or MDD",
            "Optimal tDCS-to-NFB transition interval not established — current 5-min window based on tDCS plasticity duration estimates",
            "Optimal tDCS duration for priming (10 vs 20 min) — no dose-finding study for combination protocol",
            "Alpha asymmetry NFB for MDD: mechanism confirmed, therapeutic RCT evidence weak",
            "Long-term EEG normalisation durability beyond 3 months post-block — limited follow-up data",
            "Optimal NFB protocol for tDCS-primed plasticity window — synchronous vs sequential not directly compared",
            "Neuroonica device-specific clinical validation studies — platform-level evidence required",
        ],

        review_flags=[
            "Epilepsy exclusion must be confirmed and documented before NFB theta suppression protocols",
            "Bipolar exclusion mandatory before tDCS anodal DLPFC in MDD phenotype",
            "Stimulant medication state must be documented and standardised at every ADHD session",
            "EEG baseline must be completed and documented before any NFB protocol session count begins",
            "C-SSRS suicidality screening at every session for MDD phenotype — mandatory",
        ],

        references=[
            {
                "authors": "Arns M et al.",
                "year": 2009,
                "title": "Efficacy of neurofeedback treatment in ADHD: the effects on inattention, impulsivity and hyperactivity: a meta-analysis",
                "journal": "Clinical EEG and Neuroscience",
                "pmid": "19715144",
                "evidence_type": "meta_analysis",
            },
            {
                "authors": "Kim T et al.",
                "year": 2015,
                "title": "Transcranial direct current stimulation of the motor cortex enhances the EEG oscillatory response to motor imagery",
                "journal": "Journal of Neural Engineering",
                "pmid": "25693607",
                "evidence_type": "rct",
            },
            {
                "authors": "Gevensleben H et al.",
                "year": 2009,
                "title": "Is neurofeedback an efficacious treatment for ADHD? A randomised controlled clinical trial",
                "journal": "Journal of Child Psychology and Psychiatry",
                "pmid": "19207632",
                "evidence_type": "rct",
            },
            {
                "authors": "Enriquez-Geppert S et al.",
                "year": 2017,
                "title": "EEG-neurofeedback as a tool to modulate cognition and behavior: a review tutorial",
                "journal": "Frontiers in Human Neuroscience",
                "pmid": "28588473",
                "evidence_type": "narrative_review",
            },
            {
                "authors": "Ros T et al.",
                "year": 2016,
                "title": "Consensus on the reporting and experimental design of clinical and cognitive-behavioural neurofeedback studies",
                "journal": "Clinical Neurophysiology",
                "pmid": "26652570",
                "evidence_type": "consensus_statement",
            },
            {
                "authors": "Soff C et al.",
                "year": 2017,
                "title": "Transcranial direct current stimulation improves clinical symptoms in adolescents with attention deficit hyperactivity disorder",
                "journal": "Journal of Neural Transmission",
                "pmid": "28299499",
                "evidence_type": "controlled_trial",
            },
            {
                "authors": "Brunoni AR et al.",
                "year": 2013,
                "title": "A randomized, double-blind clinical trial on non-invasive brain stimulation for depression (SELECT-TDCS)",
                "journal": "JAMA Psychiatry",
                "pmid": "23945780",
                "evidence_type": "rct",
            },
            {
                "authors": "Bikson M et al.",
                "year": 2016,
                "title": "Safety of transcranial direct current stimulation: evidence based update 2016",
                "journal": "Brain Stimulation",
                "pmid": "27372845",
                "evidence_type": "consensus_statement",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        patient_journey_notes={
            "stage_1": (
                "Pre-screen for target condition: ADHD (Conners/QbTest screen), MDD (PHQ-9 ≥10), "
                "cognitive optimization (subjective complaint documented), or motor imagery goal. "
                "Screen for epilepsy — absolute exclusion for NFB theta suppression. "
                "Screen for bipolar disorder — absolute exclusion for DLPFC tDCS. "
                "Check medications: stimulants, antidepressants, GABAergic agents — document timing plan."
            ),
            "stage_3": (
                "MANDATORY: Complete 10-min EEG spectral baseline (eyes-open + eyes-closed + task). "
                "Quantify: theta/beta ratio (Fz), SMR (Cz), μ-power (C3/C4), frontal alpha asymmetry (F3/F4). "
                "Administer condition-specific scales: Conners-3/QbTest (ADHD), MADRS+PHQ-9 (MDD), "
                "CANTAB (cognitive), MIQ-3 (motor imagery). C-SSRS mandatory for MDD phenotype. "
                "Confirm medication standardisation protocol with patient."
            ),
            "stage_5": (
                "Session delivery: Phase 1 — apply tDCS (20 min, 2 mA, correct montage). "
                "Phase 2 — transition to NFB within 5 min. Deliver 30 min NFB with adaptive threshold. "
                "Document: μ-ERD or theta/beta session value, tDCS skin check, adverse events. "
                "Total session ≈55–60 min. Threshold progression reviewed every 5 sessions."
            ),
            "stage_7": (
                "Mid-block review (session 10): Re-administer EEG spectral assessment. "
                "Compare theta/beta ratio, SMR, μ-ERD to baseline. "
                "Assess clinical scales (Conners, MADRS, CANTAB as appropriate). "
                "Non-responder pathway: reassess protocol if <30% EEG biomarker change. "
                "Adjust threshold adaptation parameters if needed. Doctor review for any protocol modification."
            ),
        },
    )
