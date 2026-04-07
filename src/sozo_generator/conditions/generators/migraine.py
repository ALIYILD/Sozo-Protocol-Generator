"""
Migraine -- Complete condition generator.
Follows the gold standard template established by parkinsons.py.

Key references:
- Shirahige L et al. (2017) tDCS migraine systematic review & meta-analysis
- Stilling JM et al. (2019) NIBS migraine Cochrane review
- Grazzi L et al. (2020) tDCS migraine prevention RCT
- ICHD-3: International Classification of Headache Disorders, 3rd edition
- FNON framework: SOZO Brain Center (2026)
"""
import logging
from ...schemas.condition import (
    PlatoScienceVariant, MultimodalCombo,
    ConditionSchema, PhenotypeSubtype, NetworkProfile,
    StimulationTarget, AssessmentTool, SafetyNote, ProtocolEntry
)
from ...core.enums import (
    NetworkKey, NetworkDysfunction, Modality, EvidenceLevel
)
from ...core.utils import current_date_str
from ..shared_condition_schema import (
    make_network, make_tdcs_target, make_tps_target, make_safety,
    SHARED_ABSOLUTE_CONTRAINDICATIONS, SHARED_SAFETY_NOTES, SHARED_GOVERNANCE_RULES, SHARED_ADVERSE_EVENT_GRADES, SHARED_SIDE_EFFECTS
)

logger = logging.getLogger(__name__)


def build_migraine_condition() -> ConditionSchema:
    """Build the complete Migraine condition schema."""
    return ConditionSchema(
        slug="migraine",
        display_name="Migraine",
        icd10="G43",
        aliases=["Migraine headache", "Migraine disorder", "Common migraine", "Classic migraine"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Migraine is a common disabling primary neurological disorder with a global "
            "prevalence of approximately 12%, a female-to-male ratio of 3:1, and is the "
            "second leading cause of years lived with disability (YLD) globally. The "
            "pathophysiology centres on the trigeminovascular system, cortical spreading "
            "depression (CSD), and central sensitisation. Transcranial direct current "
            "stimulation (tDCS) targeting M1 and DLPFC has Level B evidence for migraine "
            "prevention. Transcranial pulse stimulation (TPS) remains experimental with "
            "no published RCTs specific to migraine."
        ),

        pathophysiology=(
            "(1) Cortical Spreading Depression (CSD): A wave of neuronal and glial "
            "depolarisation propagating across the cortex at 2-5 mm/min, the electrophysiological "
            "substrate for migraine aura. CSD activates trigeminal afferents and triggers "
            "downstream inflammatory cascades.\n\n"
            "(2) Trigeminovascular activation: Activation of the trigeminovascular system leads "
            "to release of calcitonin gene-related peptide (CGRP), substance P, and neurokinin A "
            "from trigeminal afferents, causing neurogenic inflammation and vasodilation of "
            "meningeal vessels.\n\n"
            "(3) Central sensitisation: Sensitisation of the trigeminal nucleus caudalis (TNC) "
            "and higher-order neurons leads to allodynia and contributes to chronification of "
            "migraine.\n\n"
            "(4) Altered cortical excitability: Occipital and somatosensory cortex show "
            "hyperexcitability between attacks, with reduced habituation to repetitive stimuli "
            "— a hallmark of the migrainous brain.\n\n"
            "(5) Brainstem involvement: The periaqueductal grey (PAG) and locus coeruleus are "
            "implicated in migraine generation and descending pain modulation failure.\n\n"
            "(6) Thalamocortical dysrhythmia: Abnormal thalamic oscillations contribute to "
            "sensory hypersensitivity and deficient habituation."
        ),

        core_symptoms=[
            "Unilateral pulsating headache (moderate to severe intensity)",
            "Photophobia (sensitivity to light)",
            "Phonophobia (sensitivity to sound)",
            "Nausea and/or vomiting",
            "Aura (visual, sensory, or language disturbance) — present in ~30% of patients",
            "Worsening with routine physical activity",
            "Prodromal symptoms (yawning, food cravings, mood changes, neck stiffness)",
            "Postdromal symptoms (fatigue, cognitive impairment, mood changes)",
            "Allodynia (cutaneous pain hypersensitivity)",
            "Osmophobia (sensitivity to odours)",
            "Neck pain",
            "Cognitive slowing during attacks",
        ],

        non_motor_symptoms=[
            "Cognitive dysfunction (brain fog) — impaired concentration, word-finding difficulty",
            "Fatigue and postdrome (post-attack exhaustion lasting 24-48 hours)",
            "Mood changes (irritability, depression, anxiety — interictal and peri-ictal)",
            "Neck pain (present in >75% of attacks, often prodromal)",
            "Allodynia (cutaneous — central sensitisation marker, prevalence 40-60%)",
            "Sleep disturbance (insomnia, poor sleep quality — bidirectional trigger)",
            "Dizziness and vestibular symptoms (vertigo, motion intolerance)",
        ],

        key_brain_regions=[
            "Trigeminal Nucleus Caudalis (TNC)",
            "Thalamus (VPM/VPL nuclei)",
            "Somatosensory Cortex (S1/S2)",
            "Dorsolateral Prefrontal Cortex (DLPFC)",
            "Occipital Cortex (V1/V2)",
            "Primary Motor Cortex (M1)",
            "Insula",
            "Periaqueductal Grey (PAG)",
        ],

        brain_region_descriptions={
            "Trigeminal Nucleus Caudalis (TNC)": "Central relay station for trigeminal nociceptive input; site of peripheral and central sensitisation; convergence of dural and cutaneous afferents",
            "Thalamus (VPM/VPL nuclei)": "Relays trigeminovascular pain signals to cortex; VPM processes head/face pain; thalamocortical dysrhythmia contributes to sensory hypersensitivity",
            "Somatosensory Cortex (S1/S2)": "Hyperexcitable in migraineurs; reduced habituation to repetitive stimuli; target of CSD propagation; allodynia substrate",
            "Dorsolateral Prefrontal Cortex (DLPFC)": "Cognitive pain modulation; prefrontal-PAG descending inhibitory pathway; impaired during attacks contributing to brain fog and reduced pain coping",
            "Occipital Cortex (V1/V2)": "Substrate for visual aura; hyperexcitable between attacks; reduced phosphene threshold; cathodal tDCS target for aura prevention",
            "Primary Motor Cortex (M1)": "Descending pain inhibition via corticothalamic projections; anodal M1 tDCS modulates pain processing; Level B evidence for migraine prevention",
            "Insula": "Pain perception and interoception; integrates sensory, affective, and autonomic components of migraine; nausea and visceral symptoms",
            "Periaqueductal Grey (PAG)": "Master switch for descending pain modulation; dysfunction leads to failure of endogenous pain suppression; iron deposition in chronic migraine",
        },

        network_profiles=[
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN MIGRAINE. Pain salience and sensory hypersensitivity. "
                "Anterior insula and ACC hyperactivation amplifies pain signals and drives "
                "photophobia, phonophobia, and osmophobia. Heightened interoceptive awareness "
                "of attack onset.",
                primary=True, severity="moderate",
                evidence_note="Functional imaging during and between migraine attacks",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "Cognitive symptoms (brain fog) and impaired top-down pain modulation reflect "
                "CEN hypofunction. DLPFC hypoactivation reduces prefrontal-PAG descending "
                "inhibitory drive, contributing to pain persistence.",
                severity="moderate",
                evidence_note="fMRI studies of DLPFC during migraine; cognitive testing interictal",
            ),
            make_network(
                NetworkKey.SMN, NetworkDysfunction.HYPER,
                "Somatosensory cortex hyperexcitability, reduced habituation, and allodynia "
                "reflect SMN hyperfunction. CSD propagates through sensorimotor cortex. "
                "M1 involvement in descending pain inhibition pathways.",
                severity="moderate",
                evidence_note="VEP/SEP habituation studies; CSD imaging",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Concentration impairment and distractibility during and between attacks. "
                "Reduced attentional capacity contributes to functional disability.",
                severity="mild",
                evidence_note="Neuropsychological testing in chronic migraine",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "Pain rumination and catastrophising associated with DMN hyperactivation. "
                "Failure to suppress DMN during goal-directed activity contributes to "
                "cognitive impairment during attacks.",
                severity="mild",
                evidence_note="Resting-state fMRI in chronic migraine",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Affective pain processing, anxiety, and depression comorbidity. Amygdala "
                "hyperactivation amplifies pain affect. High prevalence of anxiety (50%) "
                "and depression (25%) comorbidity in migraine.",
                severity="moderate",
                evidence_note="Psychiatric comorbidity studies; amygdala fMRI",
            ),
        ],

        primary_network=NetworkKey.SN,

        fnon_rationale=(
            "In Migraine, the primary dysfunctional network is the Salience Network (SN), "
            "driven by trigeminovascular pain signalling and sensory hypersensitivity. The "
            "FNON framework directs primary stimulation efforts at modulating pain salience "
            "(M1 corticothalamic projections, DLPFC prefrontal-PAG pathway) while addressing "
            "secondary networks — SMN for aura and allodynia, CEN for cognitive symptoms, "
            "and limbic network for affective comorbidities. Phenotype classification (MWA, "
            "MWOA, CM, VM) determines the specific protocol and target selection."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="mwa",
                label="MWA — Migraine With Aura",
                description="Migraine with preceding aura (visual, sensory, or language). CSD is the electrophysiological substrate. Occipital cortex hyperexcitability is the hallmark.",
                key_features=["Visual aura (scintillating scotoma, fortification spectra)", "Sensory aura (paraesthesia)", "CSD on imaging", "Occipital hyperexcitability", "Reduced phosphene threshold"],
                primary_networks=[NetworkKey.SN, NetworkKey.SMN],
                secondary_networks=[NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.TPS],
                tdcs_target="Occipital cathodal (Oz) — reduce CSD threshold",
                tps_target="Occipital cortex + trigeminal region",
            ),
            PhenotypeSubtype(
                slug="mwoa",
                label="MWOA — Migraine Without Aura",
                description="Most common migraine phenotype (~70% of patients). Trigeminovascular activation without CSD. Pain modulation via M1 and DLPFC targets.",
                key_features=["Unilateral pulsating headache", "Photophobia and phonophobia", "Nausea/vomiting", "No preceding aura", "Worsening with activity"],
                primary_networks=[NetworkKey.SN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.SMN],
                preferred_modalities=[Modality.TDCS, Modality.TPS],
                tdcs_target="M1 anodal (C3/C4) or L-DLPFC anodal (F3)",
                tps_target="M1 / DLPFC bilateral",
            ),
            PhenotypeSubtype(
                slug="chronic",
                label="CM — Chronic Migraine",
                description=">=15 headache days/month for >=3 months, with >=8 migraine days. Central sensitisation, allodynia, and medication overuse headache (MOH) risk. Multi-target approach required.",
                key_features=[">=15 headache days/month", "Central sensitisation", "Allodynia", "MOH risk", "Functional disability", "Psychiatric comorbidity"],
                primary_networks=[NetworkKey.SN, NetworkKey.SMN],
                secondary_networks=[NetworkKey.CEN, NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.TPS, Modality.TAVNS, Modality.CES],
                tdcs_target="M1 anodal + DLPFC anodal (multi-target sequential)",
                tps_target="Trigeminal + DLPFC + occipital",
            ),
            PhenotypeSubtype(
                slug="vestibular",
                label="VM — Vestibular Migraine",
                description="Migraine with vestibular symptoms: episodic vertigo, dizziness, balance impairment, motion intolerance. Overlap with BPPV and Meniere's.",
                key_features=["Episodic vertigo", "Dizziness", "Balance impairment", "Motion intolerance", "Nystagmus during attacks"],
                primary_networks=[NetworkKey.SMN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.SN],
                preferred_modalities=[Modality.TDCS, Modality.CES],
                tdcs_target="Parietal / vestibular cortex + DLPFC",
                tps_target="Parietal + DLPFC",
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="hit6",
                name="Headache Impact Test-6",
                abbreviation="HIT-6",
                domains=["headache_impact", "disability", "function"],
                timing="baseline",
                evidence_pmid="14596936",
                notes="Primary migraine outcome measure. Score >=60 indicates severe impact. Validated, self-administered.",
            ),
            AssessmentTool(
                scale_key="midas",
                name="Migraine Disability Assessment",
                abbreviation="MIDAS",
                domains=["disability", "lost_productivity"],
                timing="baseline",
                evidence_pmid="11135029",
                notes="Grade I (0-5) minimal, II (6-10) mild, III (11-20) moderate, IV (>=21) severe disability.",
            ),
            AssessmentTool(
                scale_key="vas_pain",
                name="Visual Analogue Scale — Pain",
                abbreviation="VAS Pain",
                domains=["pain_intensity"],
                timing="baseline",
                evidence_pmid="1619654",
                notes="0-100mm scale. Assess at each session and during attacks. Simple, reliable.",
            ),
            AssessmentTool(
                scale_key="headache_diary",
                name="Headache Diary",
                abbreviation="Headache Diary",
                domains=["headache_frequency", "duration", "severity", "medication_use"],
                timing="baseline",
                notes="4-week minimum baseline required before treatment. Document frequency, duration, severity, rescue medication use, and triggers.",
            ),
            AssessmentTool(
                scale_key="allodynia_12",
                name="Allodynia Symptom Checklist-12",
                abbreviation="Allodynia-12",
                domains=["allodynia", "central_sensitisation"],
                timing="baseline",
                notes="Central sensitisation marker. Scores >=6 indicate clinically significant allodynia. Important for chronification risk.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Depression screening. Score >=10 = moderate depression. High comorbidity with chronic migraine.",
            ),
            AssessmentTool(
                scale_key="gad7",
                name="Generalised Anxiety Disorder-7",
                abbreviation="GAD-7",
                domains=["anxiety"],
                timing="baseline",
                evidence_pmid="16717171",
                notes="Anxiety screening. Score >=10 = moderate anxiety. High comorbidity with migraine.",
            ),
            AssessmentTool(
                scale_key="msq",
                name="Migraine-Specific Quality of Life Questionnaire",
                abbreviation="MSQ v2.1",
                domains=["quality_of_life", "role_restrictive", "role_preventive", "emotional"],
                timing="baseline",
                notes="Migraine-specific QoL. Three domains: role-restrictive, role-preventive, emotional function.",
            ),
        ],

        baseline_measures=[
            "HIT-6 (Headache Impact Test-6)",
            "MIDAS (Migraine Disability Assessment)",
            "VAS Pain (0-100mm)",
            "Headache diary (4-week minimum baseline)",
            "Allodynia-12 (central sensitisation screening)",
            "PHQ-9 (depression screening)",
            "GAD-7 (anxiety screening)",
            "MSQ v2.1 (migraine-specific quality of life)",
            "SOZO PRS — Patient Rating System (patient-reported, 0-10 scale)",
        ],

        followup_measures=[
            "HIT-6 at Week 4 and Week 8-10",
            "MIDAS at Week 8-10",
            "Headache diary throughout treatment (continuous)",
            "VAS Pain at each session",
            "Allodynia-12 at Week 4",
            "PHQ-9 at Week 8-10",
            "GAD-7 at Week 8-10",
            "Adverse event monitoring at every session",
        ],

        inclusion_criteria=[
            "ICHD-3 confirmed migraine diagnosis (with or without aura)",
            ">=4 migraine days per month",
            "Age 18-65 years",
            "Stable prophylactic medication regimen for >=4 weeks prior to treatment",
            "Informed consent obtained and documented",
            "Completed 4-week headache diary baseline",
        ],

        exclusion_criteria=[
            "Hemiplegic migraine (motor aura) — risk of CSD-related adverse effects",
            "Medication overuse headache (MOH) unresolved — must detox first",
            "Secondary headache disorder not excluded (imaging/workup required)",
            "Active seizure disorder or history of epilepsy",
            "Chronic daily headache of non-migraine aetiology",
            "Unstable psychiatric comorbidity requiring acute intervention",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "Hemiplegic migraine — motor aura phenotype must be excluded before occipital or motor cortex stimulation",
            "Secondary headache disorder not excluded — complete diagnostic workup required before neuromodulation",
        ],

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "precaution",
                "Do NOT stimulate during an active migraine attack. Schedule all sessions interictally. If a patient develops an attack during a session, discontinue immediately.",
                "moderate",
            ),
            make_safety(
                "monitoring",
                "Headache diary compliance is mandatory throughout treatment. 4-week baseline diary required before initiating any protocol.",
                "low",
            ),
            make_safety(
                "precaution",
                "Screen for medication overuse headache (MOH) — defined as acute medication use on >=15 days/month. MOH must be addressed before attributing poor response to treatment failure.",
                "moderate",
            ),
            make_safety(
                "precaution",
                "Cathodal occipital stimulation (Oz cathode) may provoke phosphenes in susceptible patients. Warn patient before first session and document any visual phenomena.",
                "moderate",
            ),
            make_safety(
                "stopping_rule",
                "Discontinue treatment if migraine frequency increases >=50% over any 4-week period compared to baseline. Reassess diagnosis and phenotype classification.",
                "high",
            ),
            make_safety(
                "precaution",
                "Screen for hemiplegic migraine (motor aura) before any occipital or motor cortex stimulation. Hemiplegic migraine is an absolute exclusion criterion.",
                "high",
            ),
            make_safety(
                "monitoring",
                "Track rescue medication use (triptans, NSAIDs, CGRP antagonists) throughout treatment. Document timing relative to stimulation sessions.",
                "moderate",
            ),
            make_safety(
                "precaution",
                "Vestibular migraine phenotype: assess balance (Romberg, tandem gait) before and after each stimulation session.",
                "moderate",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Primary Motor Cortex", "M1", "bilateral",
                "Pain modulation via corticothalamic projections. Anodal M1 tDCS modulates "
                "descending pain inhibitory pathways and has Level B evidence for migraine "
                "prevention from multiple meta-analyses.",
                "MIG-C1 — M1 Pain Modulation",
                EvidenceLevel.MEDIUM, off_label=False,
                eeg_canonical=["C3", "C4"],
            ),
            make_tdcs_target(
                "Dorsolateral Prefrontal Cortex", "DLPFC", "left",
                "Cognitive pain modulation via prefrontal-PAG descending inhibitory pathway. "
                "DLPFC anodal tDCS enhances top-down pain control and addresses cognitive "
                "symptoms (brain fog).",
                "MIG-C2 — DLPFC Migraine Prevention",
                EvidenceLevel.MEDIUM, off_label=False,
                eeg_canonical=["F3"],
            ),
            make_tdcs_target(
                "Occipital Cortex", "V1", "midline",
                "Cathodal stimulation reduces cortical excitability and raises the CSD "
                "threshold. Aura prevention target. CRITICAL: cathodal polarity only — "
                "do NOT use anodal over occipital in migraine with aura.",
                "MIG-C3 — Occipital Aura Prevention",
                EvidenceLevel.MEDIUM, off_label=False,
                eeg_canonical=["Oz"],
            ),
            make_tps_target(
                "Trigeminal Region / DLPFC", "TG/DLPFC", "bilateral",
                "Pain modulation via trigeminal and prefrontal targets. Off-label application "
                "— no migraine-specific RCTs published. Requires informed consent.",
                "MIG-T1 — TPS Trigeminal/DLPFC",
                EvidenceLevel.LOW,
                eeg_canonical=["F3", "F4", "C3"],
            ),
            make_tps_target(
                "Occipital Cortex", "V1/V2", "bilateral",
                "CSD threshold modulation via mechanical stimulation of occipital cortex. "
                "Experimental aura prevention application. Off-label.",
                "MIG-T2 — TPS Occipital (Aura)",
                EvidenceLevel.LOW,
                eeg_canonical=["Oz", "O1", "O2"],
            ),
        ],

        protocols=[
            # ── tDCS protocols ──────────────────────────────────────
            ProtocolEntry(
                protocol_id="MIG-C1", label="M1 Pain Modulation", modality=Modality.TDCS,
                target_region="Primary Motor Cortex", target_abbreviation="M1",
                phenotype_slugs=["mwoa", "chronic"],
                network_targets=[NetworkKey.SMN, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "C3 (M1, contralateral to dominant pain side)",
                    "cathode": "Fp2 (supraorbital)",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10 over 2-3 weeks",
                    "electrode_size": "35 cm2",
                },
                rationale="Anodal M1 tDCS modulates descending pain inhibition via corticothalamic projections. Systematic review and meta-analysis (Shirahige 2017) demonstrates significant reduction in migraine frequency and intensity.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=10,
                notes="PMID 28068857. Level B evidence from meta-analysis.",
                # Extended protocol fields
                protocol_name='TDCS-MIG-M1 — M1 Pain Modulation',
                clinical_objective='Reduce migraine frequency and intensity via M1 anodal top-down pain modulation',
                primary_targets=['Left Primary Motor Cortex (C3)'],
                secondary_targets=['Descending pain modulation circuits'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Anode (+): C3 (left M1). Cathode (-): Fp2 (right supraorbital). 2 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='2 mA',
                montage_roi='Anode (+): C3 (L-M1). Cathode (-): Fp2 (R supraorbital)',
                laterality='Left M1 (contralateral to dominant pain side if unilateral)',
                treatment_course='10-15 sessions over 2-3 weeks',
                monitoring='Impedance check; migraine diary (frequency, intensity, duration); HIT-6; skin integrity',
                expected_response='Reduced migraine frequency and intensity by 30-50% after treatment block',
                evidence_status='Moderate — Antal et al. 2010; Auvichayapat et al. 2012; meta-analysis support for M1 tDCS in migraine',
                cautions='OFF-LABEL. Do not administer during active migraine attack. Prophylactic use only.',
                when_to_escalate='If <30% reduction after 10 sessions, add DLPFC protocol or consider occipital targeting for aura',
                when_to_stop_modify='Stop if migraine frequency increases or skin lesion',
                clinical_notes_extended='M1 anodal tDCS activates descending pain inhibition pathways. Prophylactic use between attacks.',
                key_citations=['Antal et al., 2010', 'Auvichayapat et al., 2012'],
            ),
            ProtocolEntry(
                protocol_id="MIG-C2", label="DLPFC Migraine Prevention", modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex", target_abbreviation="L-DLPFC",
                phenotype_slugs=["chronic", "mwoa"],
                network_targets=[NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "Fp2 (supraorbital)",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10 over 2-3 weeks",
                },
                rationale="Left DLPFC anodal tDCS enhances prefrontal-PAG descending pain inhibition and addresses cognitive pain modulation. RCT evidence supports preventive efficacy in chronic migraine.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=10,
                notes="PMID 33316392. Grazzi et al. (2020) RCT.",
                # Extended protocol fields
                protocol_name='TDCS-MIG-DLPFC — DLPFC Migraine Prevention',
                clinical_objective='Reduce migraine frequency via prefrontal pain appraisal modulation',
                primary_targets=['Left DLPFC (F3)'],
                secondary_targets=['Prefrontal-thalamic pain circuits'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Anode (+): F3 (L-DLPFC). Cathode (-): Fp2 (R supraorbital). 2 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='2 mA',
                montage_roi='Anode (+): F3 (L-DLPFC). Cathode (-): Fp2 (R supraorbital)',
                laterality='Left prefrontal',
                treatment_course='10-15 sessions over 2-3 weeks',
                monitoring='Impedance check; migraine diary; HIT-6; skin integrity',
                expected_response='Reduced migraine frequency and improved function',
                evidence_status='Low-moderate — DLPFC tDCS for pain less studied than M1; rationale from chronic pain literature',
                cautions='OFF-LABEL. Prophylactic use only.',
                when_to_escalate='If <20% improvement after 10 sessions, switch to M1 protocol',
                when_to_stop_modify='Stop if burning, skin lesion, or neurological change',
                clinical_notes_extended='DLPFC targets cognitive-affective pain dimension. May address comorbid depression/anxiety in migraine patients.',
                key_citations=['Antal et al., 2010'],
            ),
            ProtocolEntry(
                protocol_id="MIG-C3", label="Occipital Aura Prevention", modality=Modality.TDCS,
                target_region="Occipital Cortex", target_abbreviation="V1",
                phenotype_slugs=["mwa"],
                network_targets=[NetworkKey.SMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "cathode": "Oz (occipital — CATHODAL polarity critical)",
                    "anode": "Cz (vertex)",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10 over 2-3 weeks",
                    "note": "CATHODAL polarity over occipital is critical — reduces cortical excitability and CSD threshold. Do NOT use anodal over occipital.",
                },
                rationale="Cathodal tDCS over occipital cortex reduces cortical excitability and raises the CSD threshold, targeting the electrophysiological substrate for visual aura. Cathodal polarity is critical.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=10,
                notes="Cathodal occipital — polarity reversal would be contraindicated.",
                # Extended protocol fields
                protocol_name='TDCS-MIG-OCC — Occipital Aura Prevention',
                clinical_objective='Reduce visual cortex hyperexcitability and cortical spreading depression (aura prevention)',
                primary_targets=['Visual Cortex (O1/O2)'],
                secondary_targets=['Cortical spreading depression circuits'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Cathode (-): O1/O2 (bilateral occipital). Anode (+): Cz or right shoulder. 1.5 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='1.5 mA',
                montage_roi='Cathode (-): O1/O2 (bilateral occipital). Anode (+): Cz or right shoulder',
                laterality='Bilateral occipital',
                treatment_course='10-15 sessions over 2-3 weeks',
                monitoring='Impedance check; aura diary; migraine diary; visual field check; skin integrity',
                expected_response='Reduced aura frequency and duration',
                evidence_status='Low — rationale from CSD hypothesis; limited controlled data for occipital tDCS',
                cautions='OFF-LABEL. Cathodal only over occipital cortex (anodal may provoke CSD). Monitor visual symptoms. Lower intensity (1.5 mA).',
                when_to_escalate='If no improvement after 10 sessions, add M1 protocol or consider anti-CGRP medications',
                when_to_stop_modify='Stop if visual disturbance or migraine worsening',
                clinical_notes_extended='Cathodal occipital tDCS targets CSD mechanism. Specific to migraine with aura.',
                key_citations=['Antal et al., 2010'],
            ),
            ProtocolEntry(
                protocol_id="MIG-C4", label="Multi-Target Chronic Migraine", modality=Modality.TDCS,
                target_region="M1 + DLPFC (sequential)", target_abbreviation="M1/DLPFC",
                phenotype_slugs=["chronic"],
                network_targets=[NetworkKey.SMN, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "C3 (sessions 1-5), F3 (sessions 6-10) — sequential targeting",
                    "cathode": "Fp2 (supraorbital)",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10 over 3-4 weeks",
                    "note": "Sequential multi-target: M1 first 5 sessions, DLPFC last 5 sessions",
                },
                rationale="Sequential multi-target approach for chronic migraine addresses both pain modulation (M1) and cognitive pain control (DLPFC). Targets patients with both pain and cognitive dysfunction.",
                evidence_level=EvidenceLevel.LOW, off_label=False, session_count=10,
                # Extended protocol fields
                protocol_name='TDCS-MIG-MULTI — Multi-Target Chronic Migraine',
                clinical_objective='Address chronic migraine with multi-target tDCS approach combining M1 and DLPFC',
                primary_targets=['Left M1 (C3)', 'Left DLPFC (F3)'],
                secondary_targets=['Descending pain modulation', 'Prefrontal regulation'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Ch1 Anode (+): C3 (L-M1). Ch2 Anode (+): F3 (L-DLPFC). Cathode (-): Fp2. 2 mA per channel, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='2 mA per channel',
                montage_roi='Ch1 Anode (+): C3 (L-M1). Ch2 Anode (+): F3 (L-DLPFC). Cathode (-): Fp2',
                laterality='Left-dominant',
                treatment_course='15-20 sessions over 3-4 weeks',
                monitoring='Impedance check; migraine diary; HIT-6; MIDAS; skin integrity',
                expected_response='Significant reduction in chronic migraine frequency (>50%)',
                evidence_status='Low — multi-target rationale; limited controlled data for dual-target migraine tDCS',
                cautions='OFF-LABEL. Chronic migraine (>=15 days/month). Higher session count needed. Coordinate with neurologist.',
                when_to_escalate='If <30% improvement after 15 sessions, reassess medication; consider anti-CGRP',
                when_to_stop_modify='Stop if migraine worsening or skin lesion',
                clinical_notes_extended='Multi-target approach for refractory chronic migraine. Combines M1 analgesic with DLPFC cognitive-affective modulation.',
                key_citations=['Antal et al., 2010'],
            ),
            ProtocolEntry(
                protocol_id="MIG-C5", label="Bilateral M1 Pain", modality=Modality.TDCS,
                target_region="Bilateral Primary Motor Cortex", target_abbreviation="M1-bilat",
                phenotype_slugs=["mwoa", "chronic"],
                network_targets=[NetworkKey.SMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "C3 (left M1)",
                    "cathode": "C4 (right M1)",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10 over 2-3 weeks",
                },
                rationale="Bilateral M1 montage for bilateral or side-shifting headache. Interhemispheric modulation may address bilateral pain processing.",
                evidence_level=EvidenceLevel.LOW, off_label=False, session_count=10,
                # Extended protocol fields
                protocol_name='TDCS-MIG-BILAT-M1 — Bilateral M1 Pain Protocol',
                clinical_objective='Bilateral M1 pain modulation for bilateral or non-lateralized migraine',
                primary_targets=['Bilateral M1 (C3/C4)'],
                secondary_targets=['Bilateral descending pain modulation'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Ch1 Anode (+): C3 (L-M1). Ch2 Anode (+): C4 (R-M1). Cathode (-): bilateral supraorbital. 2 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='2 mA per channel',
                montage_roi='Anode (+): C3 (L-M1), C4 (R-M1). Cathode (-): bilateral supraorbital',
                laterality='Bilateral',
                treatment_course='10-15 sessions over 2-3 weeks',
                monitoring='Impedance check; migraine diary; HIT-6; skin integrity',
                expected_response='Reduced migraine frequency in bilateral/non-lateralized patterns',
                evidence_status='Low — bilateral M1 extrapolated from unilateral data',
                cautions='OFF-LABEL. Requires dual-channel device.',
                when_to_escalate='If <30% improvement, consider adding occipital or DLPFC protocol',
                when_to_stop_modify='Stop if skin lesion or migraine worsening',
                clinical_notes_extended='For bilateral/non-lateralized migraine where unilateral M1 is insufficient.',
                key_citations=['Antal et al., 2010'],
            ),
            ProtocolEntry(
                protocol_id="MIG-C6", label="Vestibular Migraine", modality=Modality.TDCS,
                target_region="Parietal + DLPFC", target_abbreviation="P3/F3",
                phenotype_slugs=["vestibular"],
                network_targets=[NetworkKey.SMN, NetworkKey.ATTENTION, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "P3 (parietal / vestibular cortex)",
                    "cathode": "F3 (DLPFC)",
                    "intensity": "1.5 mA",
                    "duration": "20 min",
                    "sessions": "10 over 3-4 weeks (3x/week)",
                    "note": "Reduced intensity (1.5 mA) for vestibular phenotype; assess balance before/after",
                },
                rationale="Parietal-DLPFC montage targets vestibular cortex processing and cognitive integration. Reduced intensity (1.5 mA) as vestibular patients may be more sensitive to stimulation effects.",
                evidence_level=EvidenceLevel.LOW, off_label=False, session_count=10,
                # Extended protocol fields
                protocol_name='TDCS-MIG-VEST — Vestibular Migraine Protocol',
                clinical_objective='Address vestibular migraine symptoms via temporal-parietal and cerebellar targeting',
                primary_targets=['Temporal-parietal junction', 'Cerebellar areas'],
                secondary_targets=['Vestibular processing circuits'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Cathode (-): temporal-parietal (T4/P4). Anode (+): Cz or contralateral shoulder. 1.5 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='1.5 mA',
                montage_roi='Cathode (-): T4/P4 (temporal-parietal). Anode (+): Cz or shoulder',
                laterality='Right-dominant or bilateral',
                treatment_course='10-15 sessions over 2-3 weeks',
                monitoring='Impedance check; DHI (Dizziness Handicap Inventory); migraine diary; skin integrity',
                expected_response='Reduced vestibular symptoms and migraine frequency',
                evidence_status='Very low — vestibular migraine tDCS is exploratory; rationale from vestibular neuroimaging',
                cautions='OFF-LABEL. Exploratory protocol. Lower intensity (1.5 mA). Monitor vestibular symptoms carefully.',
                when_to_escalate='If no improvement, consider vestibular rehabilitation or anti-CGRP medications',
                when_to_stop_modify='Stop if vertigo worsening or neurological change',
                clinical_notes_extended='Vestibular migraine is underdiagnosed. Temporal-parietal targeting addresses vestibular processing.',
                key_citations=['Antal et al., 2010'],
            ),

            # ── TPS protocols ──────────────────────────────────────
            ProtocolEntry(
                protocol_id="MIG-T1", label="TPS Trigeminal/DLPFC", modality=Modality.TPS,
                target_region="Trigeminal Region / DLPFC", target_abbreviation="TG/DLPFC",
                phenotype_slugs=["mwoa", "chronic"],
                network_targets=[NetworkKey.SN, NetworkKey.CEN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Trigeminal region + DLPFC bilateral (neuronavigation-guided)",
                    "pulses": "3000 per session",
                    "frequency": "5 Hz",
                    "energy": "0.2 mJ/mm2",
                    "sessions": "6 over 2-3 weeks",
                },
                rationale="TPS targeting trigeminal and DLPFC regions for pain modulation in migraine without aura and chronic migraine. OFF-LABEL — no migraine-specific RCTs published. Requires Doctor authorization and informed consent.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=6,
                notes="OFF-LABEL application. No migraine-specific RCTs. Requires explicit patient consent and Doctor authorization.",
                # Extended protocol fields
                protocol_name='TPS-MIG-TRIG — TPS Trigeminal/DLPFC Protocol',
                clinical_objective='Modulate trigeminal pain pathways and prefrontal regulation via TPS',
                primary_targets=['Trigeminal nerve cortical representation', 'DLPFC'],
                secondary_targets=['Trigeminovascular system'],
                device_name='NEUROLITH® TPS System (Storz Medical)',
                session_structure='Neuronavigation setup → Holocranial priming (2,000 pulses) → Targeted trigeminal/DLPFC stimulation (4,000 pulses) → Secondary targets (2,000 pulses)',
                frequency='3 sessions/week',
                duration='30-45 min per session',
                intensity_dose='0.20-0.25 mJ/mm²; 1-4 Hz',
                montage_roi='Neuronavigation-guided trigeminal cortical area and DLPFC',
                laterality='Bilateral or dominant pain side',
                treatment_course='10-12 sessions over 2-4 weeks; then maintenance',
                monitoring='Migraine diary; HIT-6; tolerability log',
                expected_response='Reduced migraine frequency and intensity',
                evidence_status='Low — TPS for migraine is investigational',
                cautions='TPS is investigational/off-label for migraine. Neuronavigation recommended.',
                when_to_escalate='If no improvement, add tDCS M1 protocol',
                when_to_stop_modify='Stop if persistent headache worsening or neurological change',
                clinical_notes_extended='TPS reaches deeper trigeminal pathways than surface tDCS.',
                key_citations=['Beisteiner et al., 2020'],
            ),
            ProtocolEntry(
                protocol_id="MIG-T2", label="TPS Occipital (Aura)", modality=Modality.TPS,
                target_region="Occipital Cortex", target_abbreviation="V1/V2",
                phenotype_slugs=["mwa"],
                network_targets=[NetworkKey.SMN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Occipital cortex bilateral (neuronavigation-guided)",
                    "pulses": "3000 per session",
                    "frequency": "5 Hz",
                    "energy": "0.2 mJ/mm2",
                    "sessions": "6 over 2-3 weeks",
                },
                rationale="TPS targeting occipital cortex for CSD threshold modulation in migraine with aura. Experimental aura prevention application.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=6,
                notes="OFF-LABEL. Experimental aura prevention. Requires consent and Doctor authorization.",
                # Extended protocol fields
                protocol_name='TPS-MIG-OCC — TPS Occipital Aura Protocol',
                clinical_objective='Modulate visual cortex excitability for aura prevention via TPS',
                primary_targets=['Occipital cortex'],
                secondary_targets=['Visual cortex CSD circuits'],
                device_name='NEUROLITH® TPS System (Storz Medical)',
                session_structure='Neuronavigation setup → Holocranial priming (2,000 pulses) → Targeted occipital stimulation (4,000 pulses) → Secondary targets (2,000 pulses)',
                frequency='3 sessions/week',
                duration='30-45 min per session',
                intensity_dose='0.20-0.25 mJ/mm²; 1-4 Hz',
                montage_roi='Neuronavigation-guided occipital cortex; scalp near O1/O2',
                laterality='Bilateral occipital',
                treatment_course='10-12 sessions over 2-4 weeks',
                monitoring='Aura diary; migraine diary; tolerability log',
                expected_response='Reduced aura frequency',
                evidence_status='Very low — TPS occipital for aura is purely investigational',
                cautions='TPS is investigational/off-label for migraine aura. Monitor visual symptoms.',
                when_to_escalate='If no improvement, consider anti-CGRP medications',
                when_to_stop_modify='Stop if visual disturbance or headache worsening',
                clinical_notes_extended='Targets cortical spreading depression mechanism. Specific to migraine with aura.',
                key_citations=['Beisteiner et al., 2020'],
            ),
            ProtocolEntry(
                protocol_id="MIG-T3", label="TPS Multi-Region Chronic", modality=Modality.TPS,
                target_region="Trigeminal + DLPFC + Occipital", target_abbreviation="TG/DLPFC/Occ",
                phenotype_slugs=["chronic"],
                network_targets=[NetworkKey.CEN, NetworkKey.SMN, NetworkKey.SN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Trigeminal + DLPFC + Occipital (neuronavigation-guided)",
                    "pulses": "5000 per session",
                    "frequency": "5 Hz",
                    "energy": "0.2 mJ/mm2",
                    "sessions": "6 over 2-3 weeks",
                },
                rationale="Multi-region TPS for treatment-resistant chronic migraine. Extended pulse count targeting multiple pain-relevant regions. Maximum coverage protocol.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=6,
                notes="OFF-LABEL. Extended protocol for chronic migraine. Doctor authorization required.",
                # Extended protocol fields
                protocol_name='TPS-MIG-MULTI — TPS Multi-Region Chronic Migraine',
                clinical_objective='Multi-region TPS for refractory chronic migraine',
                primary_targets=['DLPFC', 'M1', 'Temporal regions'],
                secondary_targets=['Trigeminovascular system'],
                device_name='NEUROLITH® TPS System (Storz Medical)',
                session_structure='Neuronavigation setup → Holocranial priming (2,000 pulses) → Multi-region targeted stimulation (6,000 pulses across DLPFC/M1/temporal) → Final scan',
                frequency='3-5 sessions/week',
                duration='30-45 min per session',
                intensity_dose='0.20-0.25 mJ/mm²; 1-4 Hz',
                montage_roi='Neuronavigation-guided multi-region: DLPFC, M1, temporal cortex',
                laterality='Bilateral',
                treatment_course='10-12 sessions over 2-4 weeks; then maintenance',
                monitoring='Migraine diary; MIDAS; HIT-6; tolerability log',
                expected_response='Significant reduction in chronic migraine frequency',
                evidence_status='Very low — multi-region TPS for chronic migraine is investigational',
                cautions='TPS is investigational/off-label for migraine. Neuronavigation recommended. Higher pulse count.',
                when_to_escalate='If no improvement, reassess with headache specialist; consider CGRP pathway',
                when_to_stop_modify='Stop if persistent headache worsening',
                clinical_notes_extended='Multi-region approach for refractory chronic migraine. Higher total pulse count per session.',
                key_citations=['Beisteiner et al., 2020'],
            ),
            ProtocolEntry(
                protocol_id="MIG-T4", label="TPS Vestibular", modality=Modality.TPS,
                target_region="Parietal + DLPFC", target_abbreviation="Par/DLPFC",
                phenotype_slugs=["vestibular"],
                network_targets=[NetworkKey.SMN, NetworkKey.ATTENTION, NetworkKey.CEN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Parietal vestibular cortex + DLPFC (neuronavigation-guided)",
                    "pulses": "3000 per session",
                    "frequency": "5 Hz",
                    "energy": "0.2 mJ/mm2",
                    "sessions": "6 over 2-3 weeks",
                },
                rationale="TPS targeting parietal vestibular cortex and DLPFC for vestibular migraine. Addresses balance and vestibular processing dysfunction.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=6,
                notes="OFF-LABEL. Vestibular migraine application. Assess balance before/after.",
                # Extended protocol fields
                protocol_name='TPS-MIG-VEST — TPS Vestibular Migraine',
                clinical_objective='Address vestibular migraine symptoms via TPS targeting vestibular cortex',
                primary_targets=['Vestibular cortex (temporal-parietal)'],
                secondary_targets=['Cerebellar vestibular areas'],
                device_name='NEUROLITH® TPS System (Storz Medical)',
                session_structure='Neuronavigation setup → Holocranial priming (2,000 pulses) → Vestibular cortex targeted stimulation (4,000 pulses) → Secondary cerebellar (2,000 pulses)',
                frequency='3 sessions/week',
                duration='30-45 min per session',
                intensity_dose='0.20-0.25 mJ/mm²; 1-4 Hz',
                montage_roi='Neuronavigation-guided temporal-parietal vestibular cortex',
                laterality='Bilateral or dominant side',
                treatment_course='10-12 sessions over 2-4 weeks',
                monitoring='DHI; migraine diary; vestibular assessment; tolerability log',
                expected_response='Reduced vestibular symptoms and migraine frequency',
                evidence_status='Very low — TPS for vestibular migraine is purely investigational',
                cautions='TPS is investigational/off-label. Monitor vestibular symptoms carefully.',
                when_to_escalate='If no improvement, consider vestibular rehabilitation',
                when_to_stop_modify='Stop if vertigo worsening',
                clinical_notes_extended='Vestibular migraine-specific TPS targeting. Investigational.',
                key_citations=['Beisteiner et al., 2020'],
            ),

            # ── C7-C8: Expanded tDCS protocols ──────────────────────
            ProtocolEntry(
                protocol_id="MIG-C7", label="Cervical/Brainstem Proxy — Descending Pain Modulation", modality=Modality.TDCS,
                target_region="C2 Cervical / Brainstem Proxy", target_abbreviation="C2/BSt",
                phenotype_slugs=["chronic", "mwoa"],
                network_targets=[NetworkKey.SMN, NetworkKey.SN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "C2 area (posterior neck — cervicomedullary junction proxy)",
                    "cathode": "Fp2 (right supraorbital)",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                    "note": "Targets descending pain modulation pathway via cervicomedullary junction. Electrode placement requires careful anatomical landmarking.",
                },
                rationale="C2 area tDCS targets the trigeminocervical complex and descending pain modulation pathways (PAG-RVM-TNC axis). Addresses cervicogenic migraine triggers and brainstem sensitization. Particularly relevant for chronic migraine with prominent neck pain and medication overuse. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # Extended protocol fields
                protocol_name='TDCS-MIG-CERV — Cervical/Brainstem Descending Pain Protocol',
                clinical_objective='Modulate descending pain modulation pathways via cervicomedullary junction targeting',
                primary_targets=['C2 area (cervicomedullary junction proxy)'],
                secondary_targets=['PAG-RVM-TNC descending pain pathway'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Anode (+): C2 area (posterior neck). Cathode (-): Fp2 (R supraorbital). 2 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='2 mA',
                montage_roi='Anode (+): C2 area (posterior neck). Cathode (-): Fp2 (R supraorbital)',
                laterality='Midline cervical',
                treatment_course='10-15 sessions over 2-3 weeks',
                monitoring='Impedance check; migraine diary; neck pain VAS; skin integrity',
                expected_response='Reduced chronic migraine frequency and cervicogenic triggers',
                evidence_status='Low — rationale from trigeminocervical complex neuroanatomy; limited tDCS data',
                cautions='OFF-LABEL. Requires careful anatomical landmarking for cervical electrode. Monitor neck pain.',
                when_to_escalate='If <30% improvement, add M1 or DLPFC protocol',
                when_to_stop_modify='Stop if neck pain worsening, skin lesion, or neurological change',
                clinical_notes_extended='Targets trigeminocervical complex and brainstem sensitization. Relevant for chronic migraine with neck pain.',
                key_citations=['Antal et al., 2010'],
            ),
            ProtocolEntry(
                protocol_id="MIG-C8", label="Bilateral Temporal — Vestibular/Photophobia", modality=Modality.TDCS,
                target_region="Bilateral Temporal Cortex", target_abbreviation="T3/T4",
                phenotype_slugs=["vestibular", "mwa", "chronic"],
                network_targets=[NetworkKey.SN, NetworkKey.SMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "T3 (left temporal)",
                    "cathode": "T4 (right temporal)",
                    "intensity": "1.5 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                    "note": "Bilateral temporal montage for vestibular migraine with photophobia. Reduced intensity (1.5 mA) due to temporal cortex sensitivity.",
                },
                rationale="Bilateral temporal tDCS targets vestibular cortex processing and multimodal sensory integration areas disrupted in vestibular migraine. Addresses photophobia and phonophobia via temporal-insular cortex modulation. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # Extended protocol fields
                protocol_name='TDCS-MIG-TEMP — Bilateral Temporal Vestibular/Photophobia Protocol',
                clinical_objective='Modulate vestibular cortex and multimodal sensory integration for vestibular migraine symptoms',
                primary_targets=['Left Temporal (T3)', 'Right Temporal (T4)'],
                secondary_targets=['Temporal-insular cortex'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Anode (+): T3 (L temporal). Cathode (-): T4 (R temporal). 1.5 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='1.5 mA',
                montage_roi='Anode (+): T3 (L temporal). Cathode (-): T4 (R temporal)',
                laterality='Bilateral temporal',
                treatment_course='10-15 sessions over 2-3 weeks',
                monitoring='Impedance check; DHI; photophobia/phonophobia log; migraine diary; skin integrity',
                expected_response='Reduced vestibular symptoms and sensory hypersensitivity',
                evidence_status='Low — rationale from vestibular cortex neuroimaging; limited tDCS data',
                cautions='OFF-LABEL. Reduced intensity (1.5 mA) due to temporal cortex sensitivity. Monitor vestibular symptoms.',
                when_to_escalate='If no improvement, consider vestibular rehabilitation',
                when_to_stop_modify='Stop if vertigo worsening, skin lesion, or neurological change',
                clinical_notes_extended='Bilateral temporal montage for vestibular migraine with photophobia/phonophobia.',
                key_citations=['Antal et al., 2010'],
            ),

            # ── T5: Expanded TPS protocol ──────────────────────────
            ProtocolEntry(
                protocol_id="MIG-T5", label="TPS Brainstem — Trigeminal Nucleus Caudalis", modality=Modality.TPS,
                target_region="Brainstem / Trigeminal Nucleus Caudalis", target_abbreviation="TNC/BSt",
                phenotype_slugs=["chronic", "mwoa", "mwa"],
                network_targets=[NetworkKey.SN, NetworkKey.SMN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Trigeminal nucleus caudalis / upper cervical brainstem (neuronavigation-guided)",
                    "pulses": "300-400 per session",
                    "frequency": "5 Hz",
                    "energy": "0.20-0.25 mJ/mm2",
                    "sessions": "6-9 over 3 weeks",
                },
                rationale="TPS targeting the trigeminal nucleus caudalis (TNC) — the primary relay for trigeminal nociceptive input — aims to modulate central sensitization at the brainstem level. Deep acoustic energy can reach TNC depth. Addresses the core pathophysiological node in migraine chronification. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=9,
                # Extended protocol fields
                protocol_name='TPS-MIG-TNC — TPS Brainstem Trigeminal Nucleus Protocol',
                clinical_objective='Modulate central sensitization at brainstem trigeminal relay',
                primary_targets=['Trigeminal Nucleus Caudalis / upper cervical brainstem'],
                secondary_targets=['PAG-RVM descending modulation'],
                device_name='NEUROLITH\u00ae TPS System (Storz Medical)',
                session_structure='Neuronavigation setup \u2192 Holocranial priming (2,000 pulses) \u2192 Targeted TNC brainstem stimulation (4,000 pulses) \u2192 Secondary targets (2,000 pulses)',
                frequency='3 sessions/week',
                duration='30-45 min per session',
                intensity_dose='0.20-0.25 mJ/mm\u00b2; 5 Hz',
                montage_roi='Neuronavigation-guided brainstem/TNC target; posterior fossa entry',
                laterality='Midline brainstem',
                treatment_course='6-9 sessions over 3 weeks',
                monitoring='Migraine diary; brainstem symptom check; tolerability log',
                expected_response='Reduced central sensitization and chronic migraine frequency',
                evidence_status='Low — TPS brainstem targeting is purely investigational for migraine',
                cautions='TPS is investigational/off-label for brainstem targeting. Neuronavigation mandatory. Careful safety monitoring.',
                when_to_escalate='If no improvement, consider anti-CGRP medications',
                when_to_stop_modify='Stop if brainstem symptoms, persistent headache worsening, or neurological change',
                clinical_notes_extended='Targets the core pathophysiological node in migraine chronification at brainstem level.',
                key_citations=['Beisteiner et al., 2020'],
            ),

            # ── CES protocol ──────────────────────────────────────
            ProtocolEntry(
                protocol_id="MIG-CES1", label="Alpha-Stim CES — Anxiety/Sleep (Adjunct)", modality=Modality.CES,
                target_region="Bilateral earlobe (alpha wave entrainment)", target_abbreviation="CES",
                phenotype_slugs=["chronic", "vestibular"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim",
                    "frequency": "0.5 Hz",
                    "intensity": "100-300 uA",
                    "duration": "40 min",
                    "sessions": "Daily or alternate day",
                },
                rationale="CES has FDA clearance for anxiety, depression, and insomnia. As adjunct therapy, supports limbic network regulation and sleep quality in migraine patients with anxiety and sleep disturbance comorbidity.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
                # Extended protocol fields
                protocol_name='CES-MIG — Alpha-Stim Migraine Anxiety/Sleep Adjunct',
                clinical_objective='Address anxiety and sleep comorbidities in migraine patients',
                primary_targets=['Bilateral earlobe electrodes'],
                secondary_targets=['Limbic/arousal modulation'],
                device_name='Alpha-Stim\u00ae CS',
                session_structure='Bilateral earlobe clip electrodes; 0.5 Hz, 100-300 \u00b5A; 40 min',
                frequency='Daily or alternate day',
                duration='40 min per session',
                intensity_dose='100-300 \u00b5A at 0.5 Hz',
                montage_roi='Bilateral earlobe clip electrodes',
                laterality='Bilateral',
                treatment_course='Daily or alternate day during treatment block; then as-needed',
                monitoring='GAD-7; PSQI; migraine diary; skin integrity',
                expected_response='Improved sleep quality and reduced anxiety within 1-2 weeks',
                evidence_status='Moderate — CES FDA-cleared for anxiety, depression, insomnia',
                cautions='Adjunctive only — not primary migraine treatment.',
                when_to_escalate='If symptoms persist, review migraine prophylaxis',
                when_to_stop_modify='Stop if skin irritation at earlobes',
                clinical_notes_extended='Supports limbic regulation and sleep quality as adjunct to primary migraine protocols.',
                key_citations=['Kirsch DL, 2010'],
            ),
        ],

        symptom_network_mapping={
            "Headache (unilateral pulsating)": [NetworkKey.SN, NetworkKey.SMN],
            "Photophobia / Phonophobia": [NetworkKey.SN],
            "Aura (visual/sensory)": [NetworkKey.SMN],
            "Nausea / Vomiting": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Cognitive dysfunction (brain fog)": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Allodynia": [NetworkKey.SMN, NetworkKey.SN],
            "Depression / Anxiety comorbidity": [NetworkKey.LIMBIC, NetworkKey.CEN],
            "Vestibular symptoms": [NetworkKey.SMN, NetworkKey.ATTENTION],
            "Sleep disturbance": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "Fatigue": [NetworkKey.SN, NetworkKey.LIMBIC],
        },

        symptom_modality_mapping={
            "Headache": [Modality.TDCS, Modality.TPS],
            "Aura": [Modality.TDCS, Modality.TPS],
            "Cognitive dysfunction": [Modality.TDCS],
            "Allodynia": [Modality.TDCS, Modality.TPS],
            "Depression / Anxiety": [Modality.TDCS, Modality.CES, Modality.TAVNS],
            "Vestibular symptoms": [Modality.TDCS, Modality.CES],
            "Sleep disturbance": [Modality.CES, Modality.TAVNS],
            "Fatigue": [Modality.CES, Modality.TAVNS],
        },

        responder_criteria=[
            ">=50% reduction in monthly migraine days from baseline",
            ">=5 point improvement on HIT-6 from baseline",
            ">=1 grade improvement on MIDAS (e.g. Grade IV to Grade III)",
            ">=30% reduction on VAS pain intensity from baseline",
        ],

        non_responder_pathway=(
            "For patients classified as non-responders after 10 sessions (<50% reduction "
            "in monthly migraine days):\n"
            "1. Review diagnosis and phenotype classification — reassess ICHD-3 criteria\n"
            "2. Screen for medication overuse headache (MOH) — detox if confirmed\n"
            "3. Add taVNS or CES as adjunct modality\n"
            "4. Optimise prophylactic medication in coordination with neurologist\n"
            "5. Refer for CGRP monoclonal antibody therapy or botulinum toxin (onabotulinumtoxinA) if not yet trialled\n"
            "6. Consider phenotype reassignment (e.g. MWOA to CM if frequency warrants)\n"
            "7. Doctor review and approval mandatory before any protocol modification\n"
            "8. If still non-responder after second treatment block: discontinue and document"
        ),

        evidence_summary=(
            "Migraine represents an emerging neuromodulation evidence base with moderate overall quality. "
            "tDCS: Level B evidence from systematic review and meta-analysis (Shirahige et al. 2017, PMID 28068857), "
            "Cochrane review (Stilling et al. 2019, PMID 31278046), and RCT (Grazzi et al. 2020, PMID 33316392). "
            "M1 anodal and DLPFC anodal montages have the strongest support for preventive efficacy. "
            "Cathodal occipital tDCS for aura prevention has moderate evidence. "
            "TPS: Experimental — no migraine-specific RCTs published. Application is extrapolated from "
            "pain and Alzheimer's literature. "
            "CES: FDA-cleared for anxiety, depression, and insomnia — adjunct role. "
            "Overall quality: MEDIUM (emerging)."
        ),

        evidence_gaps=[
            "TPS-specific RCTs for migraine — no published trials",
            "Optimal stimulation target for migraine subtypes — head-to-head comparisons lacking",
            "Long-term preventive efficacy of tDCS beyond 3 months — limited follow-up data",
            "tDCS vs other NIBS modalities (rTMS, tACS) in migraine — no direct comparisons",
            "Responder biomarkers — no validated predictors of tDCS response in migraine",
            "Multi-target vs single-target protocols — no comparative data",
        ],

        review_flags=[
            "TPS protocols require explicit off-label consent documentation at every treatment block",
            "4-week headache diary baseline must be verified before treatment initiation",
            "Screen for hemiplegic migraine before occipital or motor cortex stimulation",
        ],

        references=[
            {
                "authors": "Shirahige L et al.",
                "year": 2017,
                "title": "Efficacy of tDCS for migraine: systematic review and meta-analysis",
                "journal": "Journal of Headache and Pain",
                "pmid": "28068857",
                "evidence_type": "systematic_review",
                "notes": "Level B evidence. High quality. Primary tDCS migraine reference.",
            },
            {
                "authors": "Stilling JM et al.",
                "year": 2019,
                "title": "Non-invasive brain stimulation for migraine",
                "journal": "Cochrane Database of Systematic Reviews",
                "pmid": "31278046",
                "evidence_type": "systematic_review",
                "notes": "Cochrane review. Highest quality. Covers all NIBS modalities.",
            },
            {
                "authors": "Grazzi L et al.",
                "year": 2020,
                "title": "tDCS for migraine prevention: randomised controlled trial",
                "journal": "Cephalalgia",
                "pmid": "33316392",
                "evidence_type": "rct",
                "notes": "DLPFC anodal tDCS RCT. Medium quality.",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        patient_journey_notes={
            "stage_1": (
                "Confirm ICHD-3 migraine diagnosis. Exclude secondary headache disorders "
                "(imaging if red flags present). Review 4-week headache diary for baseline "
                "frequency, severity, and medication use. Screen for medication overuse "
                "headache (MOH). Exclude hemiplegic migraine. Screen for psychiatric "
                "comorbidity (depression, anxiety)."
            ),
            "stage_3": (
                "Administer HIT-6, MIDAS, VAS Pain, Allodynia-12. Document migraine "
                "frequency (days/month), current prophylactic medication, and rescue "
                "medication use (type, frequency, timing). Identify predominant phenotype "
                "(MWA/MWOA/CM/VM). Document aura characteristics if present."
            ),
            "stage_4": (
                "Apply migraine phenotype classification: MWA (aura), MWOA (no aura), "
                "CM (chronic >=15 days), VM (vestibular). Conduct 6-Network Bedside "
                "Assessment (Partners tier). Document aura characteristics (visual, sensory, "
                "language). Assess allodynia severity."
            ),
            "stage_5": (
                "Apply FNON phenotype-to-protocol selection: identify primary network (SN). "
                "Select tDCS montage based on phenotype (MIG-C1 through MIG-C6). Assess "
                "TPS suitability (off-label — Doctor authorization required). Determine "
                "CES/taVNS adjunct need for anxiety, sleep, or vestibular comorbidities. "
                "Confirm 4-week headache diary baseline is complete."
            ),
        },

        clinical_tips=[
            "Require 4-week headache diary baseline before initiating any treatment protocol",
            "Schedule all stimulation sessions interictally — do NOT stimulate during active migraine attack",
            "Screen for MOH before attributing poor treatment response to protocol failure",
            "For MWA: cathodal occipital (Oz) is first-line — do NOT use anodal over occipital cortex",
            "Assess allodynia (Allodynia-12) at each session — worsening allodynia indicates central sensitisation progression",
            "Document triptan and CGRP medication timing relative to stimulation sessions",
            "Chronic migraine: extend assessment period to 8 weeks to capture true treatment effect",
            "Screen PHQ-9 and GAD-7 for comorbid depression and anxiety — high prevalence in chronic migraine",
        ],


        # --- Auto-enriched: PlatoScience Variants ---
        platoscience_variants=[
            PlatoScienceVariant(
                variant_id="MIG-C1-PS", protocol_id="MIG-C1",
                label="PlatoScience M1 Pain Modulation",
                parameters={"program": "Focus", "electrode_config": "C3 (M1, contralateral to dominant pain side)", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to MIG-C1 protocol. PlatoScience Focus program.",
            ),
            PlatoScienceVariant(
                variant_id="MIG-C2-PS", protocol_id="MIG-C2",
                label="PlatoScience DLPFC Migraine Prevention",
                parameters={"program": "Think", "electrode_config": "F3 (left DLPFC)", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to MIG-C2 protocol. PlatoScience Think program.",
            ),
            PlatoScienceVariant(
                variant_id="MIG-C3-PS", protocol_id="MIG-C3",
                label="PlatoScience Occipital Aura Prevention",
                parameters={"program": "Focus", "electrode_config": "Cz (vertex)", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to MIG-C3 protocol. PlatoScience Focus program.",
            ),
            PlatoScienceVariant(
                variant_id="MIG-C4-PS", protocol_id="MIG-C4",
                label="PlatoScience Multi-Target Chronic Migraine",
                parameters={"program": "Focus", "electrode_config": "C3 (sessions 1-5), F3 (sessions 6-10) — sequential targeting", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to MIG-C4 protocol. PlatoScience Focus program.",
            ),
            PlatoScienceVariant(
                variant_id="MIG-C5-PS", protocol_id="MIG-C5",
                label="PlatoScience Bilateral M1 Pain",
                parameters={"program": "Focus", "electrode_config": "C3 (left M1)", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to MIG-C5 protocol. PlatoScience Focus program.",
            ),
            PlatoScienceVariant(
                variant_id="MIG-C6-PS", protocol_id="MIG-C6",
                label="PlatoScience Vestibular Migraine",
                parameters={"program": "Focus", "electrode_config": "P3 (parietal / vestibular cortex)", "intensity": "1.5 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to MIG-C6 protocol. PlatoScience Focus program.",
            ),
            PlatoScienceVariant(
                variant_id="MIG-C7-PS", protocol_id="MIG-C7",
                label="PlatoScience Cervical/Brainstem Proxy",
                parameters={"program": "Focus", "electrode_config": "C2 area (posterior neck)", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to MIG-C7 protocol. PlatoScience Focus program. Requires careful electrode placement.",
            ),
            PlatoScienceVariant(
                variant_id="MIG-C8-PS", protocol_id="MIG-C8",
                label="PlatoScience Bilateral Temporal — Vestibular/Photophobia",
                parameters={"program": "Relax", "electrode_config": "T3/T4 (bilateral temporal)", "intensity": "1.5 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to MIG-C8 protocol. PlatoScience Relax program.",
            ),
        ],

        # --- Auto-enriched: Multimodal Combinations ---
        multimodal_combos=[
            MultimodalCombo(
                combo_id="F1", label="M1 Pain Modulation + TPS Trigeminal/DLPFC",
                phenotype_slugs=['mwoa', 'chronic'],
                tps_protocol_id="MIG-T1",
                non_tps_protocol_ids=["MIG-C1"],
                sequencing_notes="Week 1-3: tDCS MIG-C1 daily. Week 2-3: Add TPS MIG-T1 (2-3x/week).",
                rationale="Combined TDCS + TPS targeting for enhanced cortical modulation.",
            ),
            MultimodalCombo(
                combo_id="F2", label="DLPFC Migraine Prevention + TPS Trigeminal/DLPFC",
                phenotype_slugs=['mwoa', 'chronic'],
                tps_protocol_id="MIG-T1",
                non_tps_protocol_ids=["MIG-C2"],
                sequencing_notes="Week 1-3: tDCS MIG-C2 daily. Week 2-3: Add TPS MIG-T1 (2-3x/week).",
                rationale="Combined TDCS + TPS targeting for enhanced cortical modulation.",
            ),
            MultimodalCombo(
                combo_id="F3", label="Occipital Aura Prevention + TPS Occipital (Aura)",
                phenotype_slugs=['mwa'],
                tps_protocol_id="MIG-T2",
                non_tps_protocol_ids=["MIG-C3"],
                sequencing_notes="Week 1-3: tDCS MIG-C3 daily. Week 2-3: Add TPS MIG-T2 (2-3x/week).",
                rationale="Combined TDCS + TPS targeting for enhanced cortical modulation.",
            ),
        ],

        # --- Auto-enriched: S-O-Z-O Framework ---
        sequencing_framework={
            "S — Stabilise": "Address the most acute clinical burden first. Initiate primary tDCS protocol. Goal: establish baseline symptom control.",
            "O — Optimise": "Introduce secondary protocols or adjunct modalities. Add TPS if Doctor-authorised. Concurrent rehabilitation enhances outcomes.",
            "Z — Zone": "Fine-tune stimulation parameters based on Week 4 response. Adjust intensity, placement, or frequency. Transition to maintenance.",
            "O — Outcome": "Formal outcome assessment at Week 8-10. Apply responder/non-responder classification. Plan maintenance or escalation.",
        },

        # --- Auto-enriched: Modality-Specific Contraindications ---
        modality_specific_contraindications={
            "tdcs": [
                "Active DBS system (unless cleared by managing neurologist)",
                "Skull defect or craniectomy at electrode placement sites",
                "Metallic implants in the head within stimulation field",
                "Skin lesions or wounds at electrode sites",
            ],
            "tps": [
                "Active DBS system (mechanical resonance risk)",
                "Skull defect or craniectomy (acoustic impedance mismatch)",
                "Metallic implants in the head (ultrasound reflection risk)",
                "Anticoagulation therapy (bleeding risk at deep targets)",
                "Intracranial aneurysm or AVM",
            ],
            "ces": [
                "Implanted neurostimulator in head/neck",
                "Skin lesions at earlobe electrode sites",
            ],
        },

        # 10-20 EEG Reference Table
        eeg_reference_table=[
            {
                "position": 'C3',
                "brain_region": 'Left Primary Motor Cortex',
                "role": 'Anodal — M1 pain modulation (top-down analgesic)',
                "protocols_using": ['MIG-C1', 'MIG-C5'],
            },
            {
                "position": 'C4',
                "brain_region": 'Right Primary Motor Cortex',
                "role": 'Bilateral M1 pain modulation',
                "protocols_using": ['MIG-C5'],
            },
            {
                "position": 'F3',
                "brain_region": 'Left DLPFC',
                "role": 'Anodal — pain appraisal and prevention',
                "protocols_using": ['MIG-C2', 'MIG-C4'],
            },
            {
                "position": 'O1',
                "brain_region": 'Left Occipital',
                "role": 'Cathodal — visual cortex hyperexcitability (aura)',
                "protocols_using": ['MIG-C3'],
            },
            {
                "position": 'O2',
                "brain_region": 'Right Occipital',
                "role": 'Cathodal — visual cortex aura prevention',
                "protocols_using": ['MIG-C3'],
            },
        ],
        adverse_event_grades=SHARED_ADVERSE_EVENT_GRADES,
        side_effects=SHARED_SIDE_EFFECTS,
        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Do not stimulate during an active migraine attack — all sessions must be interictal",
            "TPS is off-label for migraine — off-label informed consent documentation required before every treatment block",
            "Headache diary compliance is mandatory throughout treatment — non-compliant patients must be counselled before continuing",
        ],
    )
