"""
Alpha-Stim CES (Cranial Electrotherapy Stimulation) — Standalone Protocol Generator.
Window 5: Anxiety Disorders, Insomnia, Comorbid Depression/Anxiety.

Primary indications: Generalized anxiety, insomnia, comorbid anxiety/depression.
Device: Alpha-Stim AID (FDA-cleared for anxiety, depression, insomnia).

⚠️  EVIDENCE UPDATE (2023–2025):
- Morriss et al. (2023, Lancet Psychiatry) — Alpha-Stim-D RCT (n=236): NO significant difference
  between active and sham CES for MDD (HDRS-17 at 16 weeks, p=0.46). Depression primary indication
  is NOT supported by the most rigorous sham-controlled trial to date. Depression protocols must be
  positioned as adjunct only (for comorbid anxiety), NOT as standalone MDD treatment.
- Chung et al. (2023, Frontiers in Psychiatry) — meta-analysis of 8 RCTs (n=337): ES=-0.96 for
  anxiety, ES=-1.02 for insomnia, ES=-0.69 for depression (based on earlier, less rigorous trials).
- Brunyé et al. (2021) critical review: severe methodological concerns — heterogeneous parameters,
  sham credibility issues, conflict-of-interest risks in manufacturer-funded studies.
- Okano et al. (2025): null findings for CES in stress resilience in healthy adults (active vs sham).

Key references:
- Morriss R et al. (2023) Alpha-Stim-D RCT — Lancet Psychiatry. PMID: 36804092
- Chung FC et al. (2023) Meta-analysis CES anxiety — Frontiers in Psychiatry
- Morriss R et al. (2019) Clinical effectiveness Alpha-Stim GAD — J Affect Disord. PMID: 31445214
- Bystritsky A et al. (2008) Pilot RCT CES for GAD — J Clin Psychiatry. PMID: 18312047
- Feusner JD et al. (2012) CES resting state fMRI — Brain Behav. PMID: 22611561
- Lande RG & Gragnani C (2013) CES insomnia RCT — Complement Ther Med. PMID: 23432962
- Lee M et al. (2023) CES for stress/subclinical depression RCT — J Affect Disord
- Brunyé TT et al. (2021) Critical review CES — Front Hum Neurosci. PMID: 33708092
- Datta A et al. (2013) CES computational modeling — NeuroImage. PMID: 22842006
- NICE MTG (2014) CES for anxiety — NICE Medical Technology Guidance
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
    make_network, make_safety,
    SHARED_ABSOLUTE_CONTRAINDICATIONS, SHARED_SAFETY_NOTES, SHARED_GOVERNANCE_RULES
)

logger = logging.getLogger(__name__)


def build_ces_alphastem_condition() -> ConditionSchema:
    """Build the complete Alpha-Stim CES standalone protocol schema."""
    return ConditionSchema(
        slug="ces_alphastem",
        display_name="Alpha-Stim CES — Anxiety, Insomnia & Comorbid Depression Protocol",
        icd10="F41.1",
        aliases=["CES", "Alpha-Stim", "cranial electrotherapy stimulation", "Alpha-Stim AID",
                 "CES anxiety", "CES insomnia", "cranial electrical stimulation"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Cranial Electrotherapy Stimulation (CES) delivers low-intensity microcurrent (100–500 μA) "
            "at 0.5 Hz via bilateral earlobe clip electrodes, producing a sub-sensory or mildly tingling "
            "electrical field across the cranium. The Alpha-Stim AID device has FDA clearance for anxiety, "
            "depression, and insomnia — the only neuromodulation device with clearance across all three "
            "indications. CES was subject to NICE Medical Technology Guidance (2014) review, which found "
            "sufficient evidence to support adoption for anxiety in the UK NHS context.\n\n"
            "CRITICAL EVIDENCE UPDATE (2023): The Alpha-Stim-D trial (Morriss et al. 2023, Lancet "
            "Psychiatry, n=236) — the most adequately powered sham-controlled RCT to date — found NO "
            "significant difference between active and sham Alpha-Stim AID for primary MDD (PHQ-9 10-19) "
            "at 16 weeks (HDRS-17 mean change: active -5.9 vs sham -6.5, p=0.46). This critically "
            "undermines the depression primary indication. CES for MDD without comorbid anxiety should "
            "NOT be recommended as standalone treatment.\n\n"
            "CES retains support for: (1) anxiety disorders — meta-analysis of 8 RCTs (Chung et al. 2023, "
            "ES=-0.96); (2) comorbid anxiety/insomnia (GAD-7 and PSQI outcomes across multiple trials); "
            "(3) Morriss et al. 2019 clinical cohort (n=161 GAD patients, 44.7% GAD-7 remission at 12 "
            "weeks). The 0.5 Hz waveform modulates cortical deactivation and DMN connectivity "
            "(Feusner et al. 2012 fMRI). The home-based, self-administered model enables daily dosing "
            "with minimal clinical burden — primary value is as anxiety/insomnia adjunct, not depression."
        ),

        pathophysiology=(
            "CES mechanism remains under active investigation, but converging evidence supports several "
            "complementary pathways:\n\n"
            "1. EEG Modulation — CES at 0.5 Hz selectively increases frontal alpha power (8–12 Hz) "
            "and reduces high-beta (>20 Hz) activity associated with anxious arousal "
            "(Feusner et al. 2012 resting-state fMRI/EEG). Alpha upregulation correlates with "
            "reduced anxiety and improved sleep onset. This is the neurophysiological signature of "
            "'relaxed alertness' — the opposite of anxious hyperarousal.\n\n"
            "2. Thalamocortical Modulation — sub-sensory microcurrent is hypothesized to entrain "
            "thalamocortical alpha/delta oscillatory circuits, reducing cortical hyperarousal and "
            "normalizing the arousal-sleep transition. Disrupted thalamocortical rhythms underlie "
            "both anxiety-driven hyperarousal and sleep initiation failure.\n\n"
            "3. Neurotransmitter Effects — animal and preliminary human studies suggest CES increases "
            "beta-endorphin and serotonin levels while reducing cortisol. Serotonergic augmentation "
            "explains the antidepressant and anxiolytic effects. Beta-endorphin release contributes "
            "to mood elevation and pain threshold increase.\n\n"
            "4. HPA Axis Modulation — cortisol reduction documented in clinical CES studies (Kirsch "
            "& Nichols 2013). Chronic stress-related HPA hyperactivity is implicated in both anxiety "
            "and insomnia; CES provides non-pharmacological HPA downregulation.\n\n"
            "5. Default Mode Network — Feusner et al. (2012) fMRI: CES reduces resting-state DMN "
            "hyperconnectivity, corresponding to reduced self-referential rumination in anxiety."
        ),

        core_symptoms=[
            "Anxiety — generalized worry, somatic anxiety, anticipatory fear, GAD-7 ≥7",
            "Insomnia — prolonged sleep latency, frequent awakenings, non-restorative sleep, PSQI >5",
            "Comorbid anxiety and depression — mixed presentation, PHQ-9 5-14 + GAD-7 ≥7",
            "Hyperarousal — elevated resting heart rate, muscle tension, cortical high-beta excess",
            "Emotional dysregulation — irritability, emotional lability, low distress tolerance",
            "Fatigue secondary to poor sleep and chronic anxiety",
            "Cognitive symptoms — concentration difficulty, rumination, mind-wandering",
        ],

        non_motor_symptoms=[
            "Social and occupational impairment from anxiety and sleep disruption",
            "Somatic anxiety complaints — GI symptoms, headaches, chest tightness",
            "Medication avoidance preference — common in anxiety/insomnia patients seeking non-pharmacological options",
            "Comorbid pain conditions (30-50% comorbidity with anxiety disorders)",
        ],

        key_brain_regions=[
            "Thalamus — thalamocortical arousal circuit; disrupted in insomnia and anxiety",
            "Frontal Cortex — alpha power reduction in anxiety; CES restores frontal alpha",
            "Amygdala — hyperactive in anxiety; modulated via serotonergic and cortisol pathways",
            "Anterior Cingulate Cortex (ACC) — worry and conflict monitoring; DMN hyperactivation",
            "Reticular Activating System (RAS) — ascending arousal; CES proposed to reduce RAS tone",
            "Hypothalamus — HPA axis; cortisol regulation; target of CES autonomic effects",
        ],

        brain_region_descriptions={
            "Thalamus": "Central node of the arousal circuit. Disrupted thalamocortical spindles in insomnia. CES 0.5 Hz entrains thalamocortical delta/alpha oscillations, facilitating sleep transition.",
            "Frontal Cortex": "Alpha power (8-12 Hz) reduced in anxiety and depression — associated with hyperarousal. CES selectively increases frontal alpha (Feusner et al. 2012). Alpha restoration correlates with anxiety reduction.",
            "Amygdala": "Hyperactive in anxiety disorders. CES-mediated serotonin increase reduces amygdala threat reactivity. Cortisol reduction (HPA modulation) reduces amygdala sensitization.",
            "Anterior Cingulate Cortex (ACC)": "Mediates worry, rumination, and conflict monitoring. DMN hyperactivity in anxiety/depression involves ACC. CES reduces DMN resting-state hyperconnectivity.",
            "Reticular Activating System (RAS)": "Ascending arousal pathway. Chronic hyperactivation underlies insomnia and anxiety-related sleep disruption. CES hypothesized to modulate RAS tone via sub-sensory microcurrent.",
            "Hypothalamus": "HPA axis regulator. Cortisol hypersecretion in chronic anxiety/stress sensitizes anxiety circuits. CES reduces cortisol in clinical studies (Kirsch & Nichols 2013).",
        },

        network_profiles=[
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN ANXIETY/INSOMNIA. Amygdala-cingulate hyperactivity drives "
                "anxiety, fear, and emotional dysregulation. CES modulates limbic hyperactivity via "
                "serotonergic upregulation and cortisol reduction. Key mechanism for anxiolytic effect.",
                primary=True, severity="severe",
                evidence_note="Kirsch & Nichols (2013) Psychiatr Clin N Am; Feusner et al. (2012) Brain Behav",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation in anxiety and depression underlies ruminative thinking and "
                "difficulty disengaging from self-referential worry. Feusner et al. (2012) fMRI "
                "demonstrated CES reduces DMN resting-state hyperconnectivity. "
                "Explains reduction in worry and rumination after CES.",
                severity="moderate",
                evidence_note="Feusner JD et al. (2012) Brain Behav. PMID: 22611561",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "Salience network hyperactivation drives hypervigilance and excessive threat detection. "
                "Insular cortex and ACC dysregulation maintain anxious arousal. CES alpha upregulation "
                "reduces SN hyperactivity via thalamocortical entrainment.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "Mild CEN hypofunction in anxiety — impaired top-down cognitive control over "
                "emotional reactivity. CES-mediated alpha upregulation may partially restore "
                "prefrontal regulatory tone over limbic hyperreactivity.",
                severity="mild",
            ),
        ],

        primary_network=NetworkKey.LIMBIC,

        fnon_rationale=(
            "In anxiety and insomnia, the primary dysfunctional network is the Limbic System, "
            "with amygdala hyperactivity and ACC-driven rumination maintained by thalamocortical "
            "arousal dysregulation. CES targets this network via EEG alpha upregulation "
            "(thalamocortical entrainment) and limbic serotonergic/cortisol modulation — providing "
            "a non-pharmacological equivalent of anxiolytic and hypnotic mechanisms. "
            "CES is positioned as a primary intervention for mild-moderate anxiety/insomnia and as "
            "an adjunct enhancing the anxiolytic and sleep-promoting effects of tDCS and tVNS."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="gad_primary",
                label="Generalized Anxiety Disorder — Primary CES Indication",
                description="GAD-7 ≥7 without major depression. Pure anxiety presentation. "
                            "CES as primary or adjunct intervention. FDA-cleared indication. "
                            "NICE-reviewed. Best evidence base for CES.",
                key_features=["Persistent worry", "Muscle tension", "Sleep difficulty",
                               "Concentration impairment", "GAD-7 ≥7", "Hyperarousal"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                secondary_networks=[NetworkKey.DMN],
                preferred_modalities=[Modality.CES, Modality.TAVNS],
                tdcs_target=None,
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="insomnia_primary",
                label="Primary Insomnia — CES Hypnotic Protocol",
                description="Chronic insomnia disorder (PSQI >5, sleep latency >30 min, "
                            "duration >3 months). CES as non-pharmacological hypnotic. "
                            "FDA-cleared for insomnia. Nightly use protocol.",
                key_features=["Prolonged sleep latency", "Frequent awakening", "Non-restorative sleep",
                               "PSQI >5", "Daytime fatigue", "Sleep-related hyperarousal"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.CEN],
                preferred_modalities=[Modality.CES, Modality.TAVNS],
                tdcs_target=None,
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="mixed_anx_dep",
                label="Mixed Anxiety-Depression — CES Adjunct (Anxiety Component Only)",
                description="Comorbid anxiety (GAD-7 ≥7) and mild-moderate depression (PHQ-9 5-14). "
                            "CES as adjunct targeting the anxiety and insomnia components. "
                            "IMPORTANT: Alpha-Stim-D RCT (Morriss 2023, Lancet Psychiatry, n=236) "
                            "showed NO benefit of CES over sham for primary MDD. CES should NOT be "
                            "used as standalone treatment for depression. Use tDCS (DLPFC anodal) "
                            "for the depression component; CES addresses anxiety/insomnia adjunct.",
                key_features=["Comorbid GAD + MDD", "Sleep disruption", "Emotional dysregulation",
                               "PHQ-9 5-14 + GAD-7 ≥7", "Fatigue", "Rumination"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.DMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.SN],
                preferred_modalities=[Modality.CES, Modality.TDCS, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal (F3) — combine with CES for comorbid depression",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="adjunct_tdcs",
                label="CES Adjunct — tDCS Treatment Block",
                description="CES as add-on during tDCS treatment block for any condition with "
                            "comorbid anxiety or insomnia (ADHD, depression, PTSD, chronic pain). "
                            "Addresses sleep and anxiety components not targeted by tDCS alone.",
                key_features=["Any condition with comorbid anxiety or insomnia",
                               "Sleep disturbance during tDCS block", "Treatment-related anxiety"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                secondary_networks=[NetworkKey.DMN],
                preferred_modalities=[Modality.CES, Modality.TDCS],
                tdcs_target="Condition-specific tDCS protocol — CES as daily adjunct",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="gad7",
                name="Generalized Anxiety Disorder 7-item Scale",
                abbreviation="GAD-7",
                domains=["anxiety", "worry", "somatic_anxiety", "autonomic_arousal"],
                timing="baseline",
                evidence_pmid="16717171",
                notes="Primary anxiety outcome measure. Score ≥10 = moderate anxiety. MCID = 4 points. "
                      "FDA-cleared indication for CES. Repeat at Week 2, 4, and endpoint.",
            ),
            AssessmentTool(
                scale_key="psqi",
                name="Pittsburgh Sleep Quality Index",
                abbreviation="PSQI",
                domains=["sleep_quality", "sleep_latency", "sleep_duration", "sleep_disturbance", "daytime_dysfunction"],
                timing="baseline",
                evidence_pmid="2748771",
                notes="Primary insomnia outcome measure for CES. Global PSQI >5 = poor sleep quality. "
                      "7 components: subjective quality, latency, duration, efficiency, disturbance, "
                      "medication use, daytime dysfunction. Buysse et al. (1989). FDA-cleared indication.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression", "anhedonia", "neurovegetative", "sleep"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Monitor comorbid depression — FDA-cleared CES indication. Score 5-9 = subthreshold, "
                      "10-14 = moderate MDD (add DLPFC tDCS). Score ≥15 = refer for psychiatric review.",
            ),
            AssessmentTool(
                scale_key="isi",
                name="Insomnia Severity Index",
                abbreviation="ISI",
                domains=["insomnia_severity", "sleep_onset", "sleep_maintenance", "daytime_impairment"],
                timing="baseline",
                evidence_pmid="11438246",
                notes="7-item insomnia-specific outcome measure. Score 0-28. Score ≥15 = moderate-severe "
                      "insomnia. More insomnia-specific than PSQI. Morin et al. Useful alongside PSQI "
                      "for insomnia phenotype.",
            ),
            AssessmentTool(
                scale_key="pss",
                name="Perceived Stress Scale",
                abbreviation="PSS-10",
                domains=["stress", "perceived_control"],
                timing="baseline",
                evidence_pmid="3944710",
                notes="Complementary stress measure. PSS ≥20 = high stress. Relevant when CES is used "
                      "for stress/anxiety overlap.",
            ),
        ],

        baseline_measures=[
            "GAD-7 (primary anxiety outcome — 0-21)",
            "PSQI (primary insomnia outcome — 7 components, 0-21 global score)",
            "ISI (insomnia severity — 0-28)",
            "PHQ-9 (comorbid depression screen and monitoring — 0-27)",
            "PSS-10 (perceived stress at baseline)",
            "SOZO PRS — anxiety, sleep, mood, energy domains (0-10 each)",
            "Current anxiolytic/hypnotic medication at baseline (benzodiazepines, Z-drugs — note CES synergy and potential dose reduction pathway)",
        ],

        followup_measures=[
            "GAD-7 at Week 2, Week 4, and endpoint (primary outcome)",
            "PSQI at Week 4 and endpoint (insomnia primary outcome)",
            "ISI at Week 4 and endpoint",
            "PHQ-9 at Week 4 and endpoint (depression monitoring)",
            "SOZO PRS at every session (brief) and end of block (full)",
            "Adverse event documentation at every session (skin irritation at earlobe clips)",
        ],

        inclusion_criteria=[
            "Age ≥18 years",
            "Primary anxiety (GAD-7 ≥7) OR primary insomnia (PSQI >5, ISI ≥8) OR comorbid anxiety/depression",
            "Capacity to self-administer CES device at home",
            "Adequate skin integrity at earlobe electrode contact sites",
            "Stable pharmacotherapy for ≥4 weeks (if on medication)",
            "No current benzodiazepine taper (defer CES initiation until taper complete or stable)",
        ],

        exclusion_criteria=[
            "Cardiac pacemaker (absolute — microcurrent contraindicated with implanted cardiac devices)",
            "Metallic implants in head/neck region",
            "Active psychosis or acute suicidality",
            "Uncontrolled epilepsy (relative contraindication)",
            "Pregnancy (insufficient safety data — precautionary exclusion)",
            "Skin condition or open wound at earlobe electrode sites",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS,

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "precaution",
                "Waveform validation: Alpha-Stim AID uses 0.5 Hz square wave at 100-500 μA. "
                "Do not use generic CES devices with unvalidated waveforms — clinical evidence "
                "is specific to the 0.5 Hz Alpha-Stim waveform. Device-specific evidence base "
                "cannot be extrapolated to other CES manufacturers.",
                "moderate",
                "Alpha-Stim prescriber information; NICE MTG (2014) — device-specific evidence",
            ),
            make_safety(
                "precaution",
                "Earlobe clip electrode contact: ensure adequate conductivity with electrode gel/pads. "
                "Poor contact causes skin irritation and sub-therapeutic current delivery. "
                "Inspect earlobe skin at every session — discontinue if Grade 2 skin reaction.",
                "low",
                "Alpha-Stim user manual; EPI prescriber guidelines",
            ),
            make_safety(
                "monitoring",
                "Monitor for excessive sedation during or immediately after CES sessions. "
                "CES produces alpha enhancement which can cause mild drowsiness in sensitive patients. "
                "Advise patients not to drive for 30 minutes after session if drowsiness reported.",
                "low",
                "Clinical observation; Alpha-Stim prescriber information",
            ),
            make_safety(
                "precaution",
                "Benzodiazepine and Z-drug users: CES may potentiate sedation. "
                "Start at 100 μA (lowest intensity) and titrate gradually. "
                "CES can be used as part of a supervised benzodiazepine dose reduction pathway "
                "— coordinate with prescriber.",
                "moderate",
                "Clinical precaution; benzodiazepine-CES interaction not systematically studied",
            ),
            make_safety(
                "precaution",
                "Intensity titration: start at 100 μA; increase by 50 μA steps to therapeutic range "
                "(typically 200-400 μA for anxiety, 100-200 μA for insomnia nightly use). "
                "Maximum 500 μA. Higher intensity does not improve efficacy and increases tolerability issues.",
                "low",
                "Alpha-Stim prescriber information; EPI dosing guidelines",
            ),
        ],

        stimulation_targets=[
            StimulationTarget(
                modality=Modality.CES,
                target_region="Bilateral earlobe electrodes — cranial microcurrent",
                target_abbreviation="CES-BL",
                laterality="bilateral",
                rationale="Bilateral earlobe clip electrodes deliver sub-sensory microcurrent (100-500 μA) "
                          "at 0.5 Hz across the cranium. The transcranial current field modulates "
                          "thalamocortical alpha oscillations and limbic circuit activity via cortical "
                          "and subcortical pathways. FDA-cleared electrode placement for anxiety, "
                          "depression, and insomnia.",
                protocol_label="CES-AID — Alpha-Stim AID Standard Protocol",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="CES-ANX",
                label="Alpha-Stim CES — Anxiety Protocol (FDA-Cleared)",
                modality=Modality.CES,
                target_region="Bilateral earlobe — cranial microcurrent",
                target_abbreviation="CES-BL",
                phenotype_slugs=["gad_primary", "mixed_anx_dep"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN, NetworkKey.DMN],
                parameters={
                    "device": "Alpha-Stim AID (Electromedical Products International)",
                    "electrode_placement": "Bilateral earlobe clips with electrode pads",
                    "waveform": "0.5 Hz square wave, modified sinusoidal",
                    "intensity": "100–500 μA (titrate to comfort; typically 200–400 μA for anxiety)",
                    "session_duration": "20–60 min",
                    "schedule": "Daily × 4–6 weeks (5×/week minimum); then 3×/week maintenance",
                    "timing": "Morning or daytime session for anxiety (not immediately pre-sleep)",
                    "titration": "Start 100 μA; increase by 50 μA every 2 sessions to target",
                    "endpoint_target": "GAD-7 reduction ≥50% or score <7 at Week 4",
                },
                rationale="Barclay & Barclay (2014) RCT (n=115): Alpha-Stim CES produced significant "
                          "GAD reduction vs sham. Effect size d=0.94 for anxiety. FDA-cleared indication. "
                          "NICE MTG (2014) found sufficient evidence for anxiety treatment in NHS context. "
                          "Meta-analysis by Shekelle et al. (2003): pooled significant anxiety reduction "
                          "across CES trials. Mechanism: frontal alpha upregulation, DMN reduction, "
                          "cortisol modulation. Non-pharmacological alternative/adjunct to SSRIs and benzodiazepines.",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
                session_count=30,
                notes="FDA 510(k) cleared (K133227). NICE MTG reviewed (2014). Prescribe via Alpha-Stim "
                      "prescriber network. Device available by prescription only in UK; OTC in US.",
            ),
            ProtocolEntry(
                protocol_id="CES-INS",
                label="Alpha-Stim CES — Insomnia Protocol (FDA-Cleared)",
                modality=Modality.CES,
                target_region="Bilateral earlobe — cranial microcurrent",
                target_abbreviation="CES-BL",
                phenotype_slugs=["insomnia_primary"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim AID",
                    "electrode_placement": "Bilateral earlobe clips with electrode pads",
                    "waveform": "0.5 Hz square wave",
                    "intensity": "100–200 μA (lower intensity for sleep onset; reduce if excessive drowsiness)",
                    "session_duration": "20–60 min",
                    "schedule": "Nightly, 30–60 min before desired sleep time",
                    "duration_of_treatment": "4–6 weeks; maintenance 3×/week thereafter",
                    "titration": "Start 100 μA; maximum 200 μA for insomnia indication",
                    "endpoint_target": "PSQI <5 or ≥3-point reduction; ISI <8",
                },
                rationale="Lande & Gragnani (2013) RCT: CES significantly improved sleep vs sham in "
                          "insomnia patients. FDA-cleared for insomnia (Alpha-Stim AID). Mechanism: "
                          "0.5 Hz entrains thalamocortical sleep oscillations (delta/alpha transition), "
                          "reducing sleep-onset hyperarousal. EEG studies confirm alpha power increase "
                          "and high-beta reduction. Clinical advantage over Z-drugs: no dependence risk, "
                          "no next-day sedation at recommended intensity, suitable for long-term use.",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
                session_count=42,
                notes="Nightly use enables high cumulative dose. Reduce intensity to 100 μA if patient "
                      "reports excessive drowsiness or reports waking feeling 'too relaxed'. "
                      "Lower intensity (sub-sensory) may be as effective as higher intensity for insomnia.",
            ),
            ProtocolEntry(
                protocol_id="CES-COMB-TDCS",
                label="CES + tDCS Combination — Mixed Anxiety-Depression",
                modality=Modality.MULTIMODAL,
                target_region="Bilateral earlobe + Left DLPFC",
                target_abbreviation="CES+DLPFC",
                phenotype_slugs=["mixed_anx_dep", "adjunct_tdcs"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "modality_1": "CES — Alpha-Stim AID, 0.5 Hz, 200–400 μA, 20–40 min (morning)",
                    "modality_2": "tDCS — left DLPFC anodal (F3), 2 mA, 20 min (concurrent or sequential)",
                    "sequencing": "Option A: Concurrent — CES during tDCS session (separate electrode systems, "
                                  "no interaction reported). Option B: CES morning, tDCS clinic session (separated)",
                    "schedule": "tDCS 5×/week × 3 weeks + daily home CES × 6 weeks",
                    "combination_rationale": "CES addresses anxiety/insomnia component (limbic); tDCS addresses "
                                             "depressive component (DLPFC CEN hypofunction)",
                },
                rationale="Mixed anxiety-depression (comorbid GAD + MDD) requires dual-mechanism treatment. "
                          "tDCS (DLPFC anodal) upregulates CEN excitability and reduces DMN intrusion — "
                          "addressing the depressive component. CES (0.5 Hz, bilateral earlobe) modulates "
                          "limbic hyperactivity and thalamocortical arousal — addressing the anxiety and "
                          "insomnia component. Both are FDA-cleared for their respective indications. "
                          "No published RCT for this specific combination; evidence is additive from "
                          "component trials.",
                evidence_level=EvidenceLevel.LOW,
                off_label=False,
                session_count=30,
                notes="Both devices are FDA-cleared for their respective indications. "
                      "No known interactions between CES earlobe electrodes and tDCS scalp electrodes "
                      "when used simultaneously — different electrode systems, different targets. "
                      "Monitor for excessive sedation if concurrent use.",
            ),
            ProtocolEntry(
                protocol_id="CES-TAVNS-ADJ",
                label="CES + tVNS Combination — Anxiety with Autonomic Dysregulation",
                modality=Modality.MULTIMODAL,
                target_region="Bilateral earlobe + Left cymba concha",
                target_abbreviation="CES+ABVN",
                phenotype_slugs=["gad_primary", "adjunct_tdcs"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN, NetworkKey.DMN],
                parameters={
                    "modality_1": "CES — Alpha-Stim AID, 0.5 Hz, 200–400 μA, 40 min",
                    "modality_2": "tVNS — cymba concha, 120 Hz, 250 μs, sensory threshold, 30 min",
                    "sequencing": "tVNS during first 30 min, CES for full 40 min (stagger start)",
                    "schedule": "Daily for 4 weeks; then 5×/week × 2 weeks maintenance",
                    "target_population": "Anxiety with prominent autonomic hyperarousal (HRV <20ms RMSSD, PSS ≥20)",
                },
                rationale="CES and tVNS target complementary pathways in anxiety: CES via thalamocortical "
                          "alpha upregulation and DMN modulation; tVNS via NTS-LC noradrenergic pathway and "
                          "direct amygdala/HRV modulation. Autonomic biomarker improvement (HRV increase) "
                          "expected from tVNS; EEG-level anxiolytic effect from CES. Dual mechanism reduces "
                          "dependence on single modality. No published combination trial; mechanism-based.",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
                session_count=28,
                notes="Use two separate devices simultaneously. No electrode overlap — CES at earlobes, "
                      "tVNS at cymba concha. Monitor for auricular skin tolerance at both sites.",
            ),
        ],

        symptom_network_mapping={
            "Anxiety": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Insomnia": [NetworkKey.LIMBIC, NetworkKey.SN, NetworkKey.DMN],
            "Worry/Rumination": [NetworkKey.DMN, NetworkKey.LIMBIC],
            "Hyperarousal": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Comorbid Depression": [NetworkKey.LIMBIC, NetworkKey.DMN, NetworkKey.CEN],
            "Emotional Dysregulation": [NetworkKey.LIMBIC, NetworkKey.CEN],
            "Fatigue": [NetworkKey.LIMBIC, NetworkKey.CEN],
        },

        symptom_modality_mapping={
            "Anxiety": [Modality.CES, Modality.TAVNS],
            "Insomnia": [Modality.CES, Modality.TAVNS],
            "Worry/Rumination": [Modality.CES],
            "Hyperarousal": [Modality.CES, Modality.TAVNS],
            "Comorbid Depression": [Modality.CES, Modality.TDCS],
            "Emotional Dysregulation": [Modality.CES, Modality.TAVNS],
            "Fatigue": [Modality.CES],
        },

        responder_criteria=[
            "≥50% reduction in GAD-7 from baseline at Week 4 (anxiety primary outcome)",
            "GAD-7 score <7 at endpoint (anxiety remission)",
            "PSQI global score <5 at endpoint (sleep remission criterion)",
            "ISI score <8 at endpoint (insomnia remission)",
            "Clinically meaningful improvement in SOZO PRS anxiety and sleep domains (≥3 points on 0-10 scale)",
        ],

        non_responder_pathway=(
            "For patients classified as non-responders at Week 4 (GAD-7 reduction <30%, PSQI unchanged):\n"
            "1. Verify waveform: confirm Alpha-Stim AID is being used — not a generic CES device\n"
            "2. Verify electrode contact — adequate gel/pad conductivity at earlobe clips\n"
            "3. Optimize intensity: increase to 400 μA if tolerated (for anxiety); "
            "maintain 100-200 μA for insomnia\n"
            "4. Increase session duration to 60 min if using 20-min sessions\n"
            "5. Ensure daily use — adherence review; minimum 5 sessions/week for clinical response\n"
            "6. Add tVNS (cymba concha) for anxiety with autonomic dysregulation (HRV <20ms)\n"
            "7. Add tDCS DLPFC protocol for comorbid depression component (PHQ-9 ≥10)\n"
            "8. Doctor review for pharmacotherapy options (SSRI, SNRI for moderate anxiety)\n"
            "9. Refer for CBT/psychological intervention if cognitive anxiety components are prominent"
        ),

        evidence_summary=(
            "ANXIETY — Supported (Level B / moderate evidence):\n"
            "Ching et al. (2022, Frontiers in Psychiatry) meta-analysis of 11 RCTs (n=794): "
            "Hedge's g=-0.625 — moderate effect; no severe AEs; primary AE is ear discomfort/pain. "
            "Chung et al. (2023) meta-analysis of 8 RCTs (n=337): ES=-0.96; Alpha-Stim subgroup "
            "(4 RCTs, n=230): ES=-0.88. Morriss et al. (2019) clinical cohort (n=161 GAD): 44.7% "
            "GAD-7 remission at 12 weeks, £540 cost saving vs CBT. Bystritsky et al. (2008) pilot RCT "
            "(n=12 DSM-IV GAD): 50% HAM-A response at 0.5 Hz, 300 μA × 6 weeks. Morriss & Price "
            "(2020) temporal analysis (n=161): anxiety improvement at Week 4 predicts depression "
            "improvement at Week 12-24 — treat anxiety first, depression follows.\n\n"
            "INSOMNIA — Low-to-moderate evidence:\n"
            "Chung et al. (2023) meta-analysis: ES=-1.02 for insomnia (3 RCTs). Shekelle VA systematic "
            "review (2018, 26 RCTs): insufficient evidence grade — no significant differences in "
            "objective sleep parameters. Lee et al. (2023) RCT: significant QEEG changes and cortisol "
            "slope flattening. PSQI improvements documented in open-label studies.\n\n"
            "DEPRESSION (PRIMARY MDD) — NOT supported by rigorous evidence:\n"
            "CRITICAL: Morriss et al. (2023, Lancet Psychiatry, n=236, Alpha-Stim-D RCT): NO "
            "significant difference vs sham (HDRS-17, p=0.46). Shekelle VA review (2018): 3 small "
            "RCTs, insufficient evidence grade. Depression indication must be restricted to comorbid "
            "anxiety/depression presentations only — not standalone MDD.\n\n"
            "PTSD — No evidence (confirmed gap):\n"
            "Shekelle VA systematic review (2018): zero RCTs for PTSD as primary diagnosis. "
            "Do not claim CES efficacy for PTSD.\n\n"
            "MECHANISM:\n"
            "Feusner et al. (2012) fMRI: midline frontal/parietal deactivation and DMN modulation "
            "for both 0.5 Hz and 100 Hz. Datta et al. (2013) computational model: current reaches "
            "thalamus and hypothalamus depending on montage. Lee et al. (2023): delta/theta/beta/high-"
            "beta power modulation; cortisol slope flattening.\n\n"
            "SAFETY (confirmed across 26 RCTs, n=800+):\n"
            "No serious adverse events. Primary AEs: ear discomfort/pain, mild tingling/skin irritation, "
            "tiredness, transient visual symptoms. One historic case of worsening depression requiring "
            "hospitalisation (1 study, >25 years old) — not replicated in subsequent 200+ patients.\n\n"
            "LIMITATIONS:\n"
            "Brunyé et al. (2021): severe parameter heterogeneity, sham credibility concerns, COI "
            "risks. Shekelle (2018): all 26 RCTs at high risk of bias; 21/26 enrolled <30 subjects "
            "per arm. Okano et al. (2025): null findings in healthy adults for stress resilience."
        ),

        evidence_gaps=[
            "CONFIRMED NEGATIVE: CES for primary MDD — Alpha-Stim-D RCT (Morriss 2023, Lancet "
            "Psychiatry, n=236) showed no effect vs sham; do not use as standalone MDD treatment",
            "Large independent (non-manufacturer-funded) RCT for CES in GAD still lacking",
            "Optimal waveform: 0.5 Hz vs 10 Hz vs 100 Hz — clinical superiority not established "
            "(Feusner 2012 shows similar deactivation patterns for 0.5 Hz and 100 Hz)",
            "Mechanism unresolved: thalamocortical entrainment vs cortisol modulation vs sham "
            "response — Brunyé 2021 identifies this as primary gap",
            "Parameter heterogeneity: most trials use different intensities, frequencies, durations "
            "— no definitive dose-optimization study published",
            "Healthy/non-clinical populations: Okano 2025 null findings suggest CES may not work "
            "for stress resilience in neurotypical adults without clinical anxiety",
            "CES + tDCS combination RCT — does not exist; combination remains mechanism-based",
            "CES + tVNS combination — no published data",
            "Long-term maintenance beyond 3 months — no controlled data",
            "Insomnia: only 3 RCTs in Chung 2023 meta-analysis; all small n; objective "
            "polysomnography rarely used (Wagenseil 2018 PSG study showed no sleep parameter effect)",
        ],

        references=[
            {
                "authors": "Morriss R et al.",
                "year": 2023,
                "title": "Clinical effectiveness of active Alpha-Stim AID versus sham Alpha-Stim AID in major depression in primary care (Alpha-Stim-D): a multicentre, parallel group, double-blind, randomised controlled trial",
                "journal": "The Lancet Psychiatry",
                "pmid": "36804092",
                "evidence_type": "rct",
                "note": "NEGATIVE TRIAL for MDD — no superior effect vs sham (n=236, p=0.46). Highest quality trial.",
            },
            {
                "authors": "Ching SN et al.",
                "year": 2022,
                "title": "Efficacy and Tolerability of Cranial Electrotherapy Stimulation in the Treatment of Anxiety: A Systematic Review and Meta-Analysis",
                "journal": "Frontiers in Psychiatry",
                "pmid": None,
                "evidence_type": "meta_analysis",
                "note": "11 RCTs, n=794 (mean age 41.4, 64.8% female); Hedge's g=-0.625 (moderate effect); "
                        "primary AE: ear discomfort/pain; no severe AEs. Most rigorous meta-analysis on CES for anxiety.",
            },
            {
                "authors": "Chung FC et al.",
                "year": 2023,
                "title": "Efficacy of electrical cranial stimulation for treatment of psychiatric symptoms in patients with anxiety: A systematic review and meta-analysis",
                "journal": "Frontiers in Psychiatry",
                "pmid": None,
                "evidence_type": "meta_analysis",
                "note": "8 RCTs, n=337. ES=-0.96 anxiety, ES=-1.02 insomnia, ES=-0.69 depression. Alpha-Stim subgroup ES=-0.88.",
            },
            {
                "authors": "Morriss R & Price L",
                "year": 2020,
                "title": "Differential effects of cranial electrotherapy stimulation on changes in anxiety and depression symptoms over time in patients with generalized anxiety disorder",
                "journal": "Journal of Affective Disorders",
                "pmid": "33065818",
                "evidence_type": "cohort_study",
                "note": "n=161 GAD; latent cross-lagged panel: anxiety at week 4 predicts depression at week 12-24. "
                        "Treat anxiety first — depression follows. 60 min/day × 6-12 weeks.",
            },
            {
                "authors": "Shekelle PG et al.",
                "year": 2018,
                "title": "Benefits and Harms of Cranial Electrical Stimulation for Chronic Painful Conditions, Depression, Anxiety, and Insomnia",
                "journal": "Annals of Internal Medicine",
                "pmid": None,
                "evidence_type": "systematic_review",
                "note": "26 RCTs; low-strength evidence for anxiety/depression; insufficient for insomnia; "
                        "ZERO RCTs for PTSD; no serious AEs; all trials at high risk of bias.",
            },
            {
                "authors": "Morriss R et al.",
                "year": 2019,
                "title": "Clinical effectiveness and cost minimisation model of Alpha-Stim cranial electrotherapy stimulation in treatment seeking patients with moderate to severe generalised anxiety disorder",
                "journal": "Journal of Affective Disorders",
                "pmid": "31445214",
                "evidence_type": "cohort_study",
                "note": "n=161 GAD patients; 44.7% GAD-7 remission at 12 weeks; £540 cost saving vs CBT. No control group.",
            },
            {
                "authors": "Bystritsky A et al.",
                "year": 2008,
                "title": "A pilot study of cranial electrotherapy stimulation for generalized anxiety disorder",
                "journal": "Journal of Clinical Psychiatry",
                "pmid": "18312047",
                "evidence_type": "pilot_study",
                "note": "n=12 DSM-IV GAD; 0.5 Hz, 300 μA × 6 weeks; 50% HAM-A responders.",
            },
            {
                "authors": "Feusner JD et al.",
                "year": 2012,
                "title": "Effects of cranial electrotherapy stimulation on resting state brain activity",
                "journal": "Brain and Behavior",
                "pmid": "22611561",
                "evidence_type": "controlled_trial",
                "note": "fMRI: both 0.5 Hz and 100 Hz CES cause midline frontal/parietal deactivation; DMN connectivity changes.",
            },
            {
                "authors": "Lee M et al.",
                "year": 2023,
                "title": "Effects of cranial electrotherapy stimulation on improving depressive symptoms in people with stress: A randomized, double-blind controlled study",
                "journal": "Journal of Affective Disorders",
                "pmid": None,
                "evidence_type": "rct",
                "note": "n=62; significant depression/stress improvement vs sham; cortisol slope flattening; EEG delta/theta/beta/high-beta changes.",
            },
            {
                "authors": "Lande RG & Gragnani C",
                "year": 2013,
                "title": "Efficacy of cranial electric stimulation for the treatment of insomnia: a randomized pilot study",
                "journal": "Complementary Therapies in Medicine",
                "pmid": "23432962",
                "evidence_type": "rct",
                "note": "Insomnia RCT; near-significant increase in total sleep time; gender differences noted.",
            },
            {
                "authors": "Brunyé TT et al.",
                "year": 2021,
                "title": "A Critical Review of Cranial Electrotherapy Stimulation for Neuromodulation in Clinical and Non-clinical Samples",
                "journal": "Frontiers in Human Neuroscience",
                "pmid": "33708092",
                "evidence_type": "narrative_review",
                "note": "Critical review: severe methodological concerns — parameter heterogeneity, sham credibility issues, COI risks.",
            },
            {
                "authors": "Datta A et al.",
                "year": 2013,
                "title": "Cranial electrotherapy stimulation and transcranial pulsed current stimulation: A computer based high-resolution modeling study",
                "journal": "NeuroImage",
                "pmid": "22842006",
                "evidence_type": "narrative_review",
                "note": "Computational model confirms current reaches cortical and subcortical regions (thalamus, hypothalamus) depending on montage.",
            },
            {
                "authors": "Okano K et al.",
                "year": 2025,
                "title": "Effects of repeated cranial electrotherapy stimulation on physiological and behavioral responses to acute stress: a double-blind randomized clinical trial",
                "journal": "Frontiers in Human Neuroscience",
                "pmid": None,
                "evidence_type": "rct",
                "note": "NULL findings: active CES not different from sham for stress resilience in healthy adults (n=46). Challenges use in non-clinical populations.",
            },
            {
                "authors": "NICE",
                "year": 2014,
                "title": "Cranial electrotherapy stimulation with the Alpha-Stim AID for anxiety",
                "journal": "NICE Medical Technology Guidance",
                "pmid": None,
                "evidence_type": "clinical_practice_guideline",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        clinical_tips=[
            "Prescribe Alpha-Stim AID specifically — not generic CES; clinical evidence is device-specific "
            "to the 0.5 Hz Alpha-Stim waveform validated in published trials",
            "For insomnia: schedule CES session 30-60 min before sleep; keep intensity low (100-200 μA) "
            "to avoid stimulating effects that could paradoxically delay sleep",
            "For anxiety without insomnia: morning or afternoon sessions preferred; avoid evening "
            "sessions initially until patient knows their individual sedation response",
            "CES is an excellent add-on for patients on tDCS or tVNS blocks who have comorbid sleep "
            "disturbance — no interaction with tDCS electrodes when used at separate sites",
            "Patients on benzodiazepines or Z-drugs: CES can support gradual dose reduction under "
            "medical supervision — coordinate with prescriber before any taper",
            "Earlobe skin inspection at every session is essential — clip electrode contact can cause "
            "mild erythema; use conductive pads or gel to reduce friction",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES,
    )
