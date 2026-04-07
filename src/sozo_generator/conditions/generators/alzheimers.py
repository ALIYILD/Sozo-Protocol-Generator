"""
Alzheimer's Disease / Mild Cognitive Impairment (AD/MCI) — Complete condition generator.

Key references:
- Boggio PS et al. (2012) tDCS in Alzheimer's — PLOS ONE. PMID: 22479484
- Ferrucci R et al. (2008) tDCS improves recognition memory in AD — Neurology. PMID: 18981371
- Benussi A et al. (2020) TPS in AD/MCI: randomized, double-blind, sham-controlled trial — Brain Stimulation. PMID: 32534178
- Folstein MF et al. (1975) Mini-Mental State Examination — Journal of Psychiatric Research. PMID: 1202204
- Nasreddine ZS et al. (2005) Montreal Cognitive Assessment (MoCA) — Journal of the American Geriatrics Society. PMID: 15817019
- Buckner RL et al. (2009) Cortical hubs revealed by intrinsic functional connectivity — Journal of Neuroscience. PMID: 19176803
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


def build_alzheimers_condition() -> ConditionSchema:
    """Build the complete Alzheimer's Disease / MCI condition schema."""
    return ConditionSchema(
        slug="alzheimers",
        display_name="Alzheimer's Disease / Mild Cognitive Impairment",
        icd10="G30",
        aliases=["AD", "MCI", "Alzheimer disease", "dementia", "mild cognitive impairment", "amnestic MCI"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Alzheimer's Disease (AD) is the most common form of dementia, accounting for 60-70% of "
            "all dementia cases worldwide, with an estimated 50 million people affected globally. "
            "It is characterized by progressive episodic memory loss, language impairment, visuospatial "
            "deficits, and executive dysfunction, ultimately leading to severe functional dependency. "
            "Mild Cognitive Impairment (MCI) represents a clinically and biomarker-defined transitional "
            "state between normal aging and AD dementia, with an annual conversion rate of approximately "
            "10-15% to AD.\n\n"
            "Neuromodulation in AD/MCI targets residual memory and executive networks to slow functional "
            "decline and improve cognitive performance. tDCS applied to temporal-parietal and DLPFC "
            "regions has demonstrated memory improvements in pilot RCTs. Transcranial Pulse Stimulation "
            "(TPS) using the NEUROLITH system has shown positive pilot results in AD/MCI (Benussi et al. "
            "2020). TPS is approved for use in Alzheimer's Disease in applicable regulatory jurisdictions — "
            "clinicians should confirm current regulatory status for their region. All neuromodulation "
            "in AD/MCI is intended as a cognitive rehabilitation adjunct, not a disease-modifying intervention."
        ),

        pathophysiology=(
            "AD pathophysiology involves two hallmark pathological processes: extracellular amyloid-beta "
            "(Aβ) plaques and intraneuronal neurofibrillary tangles (hyperphosphorylated tau protein). "
            "These pathologies disrupt synaptic transmission, activate neuroinflammatory cascades (microglial "
            "activation, astrogliosis), and cause progressive neurodegeneration following a predictable "
            "spatiotemporal staging pattern.\n\n"
            "Pathological spread follows Braak staging: tau pathology begins in transentorhinal cortex "
            "(Braak I-II), spreads to hippocampus proper (III-IV), then association neocortex (V-VI). "
            "Amyloid deposition (Thal phases) begins in prefrontal and temporal association cortices. "
            "Biomarker sequence (Jack et al. 2013 A/T/N framework): amyloid positivity precedes tau "
            "pathology by decades; neurodegeneration (volume loss, hypometabolism) follows tau burden.\n\n"
            "Cholinergic depletion from nucleus basalis of Meynert (NBM) is a cardinal neurochemical "
            "deficit, driving memory and attentional impairment. This is the basis of cholinesterase "
            "inhibitor pharmacotherapy. Network-level disruption is prominent and early: the Default Mode "
            "Network (DMN) undergoes severe early disruption, with reduced functional connectivity "
            "correlating with amyloid burden (Buckner et al. 2009). The DMN nodes — posterior cingulate "
            "cortex (PCC), precuneus, medial PFC, angular gyrus, and hippocampus — are preferential "
            "amyloid deposition sites."
        ),

        core_symptoms=[
            "Episodic memory loss — especially recent declarative memory (anterograde amnesia)",
            "Language impairment — anomia, reduced verbal fluency, word-finding difficulties",
            "Visuospatial deficits — getting lost in familiar environments, difficulty with spatial tasks",
            "Executive dysfunction — impaired judgment, planning, abstraction, and problem-solving",
            "Apraxia — difficulty with learned motor sequences (dressing, using utensils) in moderate AD",
            "Progressive functional decline in instrumental and basic activities of daily living",
        ],

        non_motor_symptoms=[
            "Behavioral and psychological symptoms of dementia (BPSD): agitation, depression, psychosis, wandering",
            "Sleep disturbance — circadian rhythm fragmentation, increased nocturnal waking",
            "Anxiety (common in early MCI and mild AD — ~40%)",
            "Apathy (most prevalent neuropsychiatric symptom — ~50% in mild AD)",
            "Caregiver burden (significant secondary clinical consideration)",
        ],

        key_brain_regions=[
            "Hippocampus (bilateral) — CA1 and subiculum",
            "Entorhinal Cortex (Layer II neurons)",
            "Posterior Cingulate Cortex (PCC) / Precuneus",
            "Angular Gyrus (inferior parietal lobule)",
            "Dorsolateral Prefrontal Cortex (DLPFC)",
            "Nucleus Basalis of Meynert (NBM)",
        ],

        brain_region_descriptions={
            "Hippocampus (bilateral) — CA1 and subiculum": "Earliest site of clinically significant neurodegeneration in AD; episodic memory consolidation and spatial navigation. MRI volumetry (hippocampal atrophy) is an established AD biomarker. TPS can reach hippocampal depth (~40-50mm).",
            "Entorhinal Cortex (Layer II neurons)": "Gateway to hippocampus via perforant pathway. First clinically significant Braak Stage I-II tau pathology. Disrupts input to memory circuits. Target for TPS neuronavigation.",
            "Posterior Cingulate Cortex (PCC) / Precuneus": "Major DMN hub; early amyloid deposition and FDG-PET hypometabolism are diagnostic biomarkers. PCC reduced connectivity correlates with AD severity.",
            "Angular Gyrus (inferior parietal lobule)": "Semantic memory and language processing. Vulnerable to amyloid deposition; tDCS temporal-parietal montages include this region.",
            "Dorsolateral Prefrontal Cortex (DLPFC)": "Executive function impaired in MCI and early AD. Later involvement in Braak staging. Potential tDCS anodal target to upregulate executive network residual capacity.",
            "Nucleus Basalis of Meynert (NBM)": "Primary source of cholinergic innervation to cortex via basal forebrain. Progressive degeneration drives hallmark cholinergic deficit. Basis for cholinesterase inhibitor therapy.",
        },

        network_profiles=[
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPO,
                "PRIMARY NETWORK IN AD. The DMN is the earliest and most severely affected large-scale network "
                "in AD. Amyloid preferentially deposits at DMN nodes (PCC, precuneus, medial PFC, hippocampus). "
                "Reduced DMN functional connectivity correlates with episodic memory performance and amyloid "
                "burden. DMN disruption precedes clinical symptoms by ~10-15 years (Buckner et al. 2009).",
                primary=True, severity="severe",
                evidence_note="Buckner RL et al. 2009 — DMN as AD vulnerability network. PMID: 19176803",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "Executive function and working memory decline progressively as CEN involvement increases "
                "with AD staging. DLPFC tDCS targeting aims to upregulate residual CEN capacity, "
                "improving executive function and daily functional performance in MCI/mild AD.",
                severity="moderate-severe",
                evidence_note="Frontal CEN involvement in MCI-to-AD progression; multiple fMRI studies",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Cholinergic depletion disrupts attentional alerting and orienting networks. "
                "Attentional impairment is prominent in MCI and early AD, contributing to functional "
                "disability beyond memory deficits alone.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "BPSD (agitation, anxiety, depression) reflect limbic and frontal-limbic network "
                "disruption and compensatory hyperreactivity. Amygdala changes and reduced prefrontal "
                "inhibitory control of limbic circuits drive behavioral symptoms.",
                severity="moderate",
                evidence_note="BPSD as limbic-frontal dysregulation in AD; prevalence ~80% over disease course",
            ),
        ],

        primary_network=NetworkKey.DMN,

        fnon_rationale=(
            "In AD/MCI, the primary dysfunctional network is the Default Mode Network (DMN)/memory "
            "circuit, driven by progressive amyloid and tau pathology in hippocampal-entorhinal and "
            "parietal DMN nodes. The FNON framework targets temporal-parietal regions (anodal tDCS) "
            "to upregulate surviving memory circuit nodes and enhance synaptic plasticity in residual "
            "circuits. TPS neuronavigation allows deeper targeting of hippocampal/entorhinal circuits "
            "beyond the reach of surface tDCS. DLPFC anodal tDCS addresses CEN hypofunction for "
            "executive function support. taVNS is considered for BPSD subtypes via limbic modulation."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="mci_am",
                label="MCI-A — Amnestic Mild Cognitive Impairment",
                description="Subjective and objective memory decline below age-expected norms with preserved functional independence. 10-15% annual conversion to AD. Single or multi-domain. Best evidence window for neuromodulation.",
                key_features=["Memory complaints", "Objective episodic memory impairment", "Preserved ADLs", "MoCA 18-25"],
                primary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.TPS, Modality.CES],
                tdcs_target="Temporal-parietal bilateral anodal (T3+T4 or P3+P4) + left DLPFC anodal",
                tps_target="Hippocampal / entorhinal targeting (neuronavigation-guided)",
            ),
            PhenotypeSubtype(
                slug="mild_ad",
                label="MILD AD — Mild Alzheimer's Disease",
                description="Mild dementia with significant episodic memory impairment affecting daily function. CDR 0.5-1. Language and executive deficits emerging. Still amenable to neuromodulation.",
                key_features=["Episodic memory impairment", "Language changes (anomia)", "Some ADL dependency", "MoCA 10-17"],
                primary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.ATTENTION, NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.TPS],
                tdcs_target="Temporal-parietal anodal bilateral; shorter duration (20 min)",
                tps_target="Left DLPFC / temporal cortex targeting",
            ),
            PhenotypeSubtype(
                slug="bpsd",
                label="BPSD — Behavioural & Psychological Symptoms",
                description="AD with prominent agitation, anxiety, depression, or sleep disruption as primary clinical burden. Limbic network dysregulation predominant.",
                key_features=["Agitation", "Depression", "Anxiety", "Sleep disruption", "Behavioral dysregulation", "Apathy"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                secondary_networks=[NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal for depression/apathy component",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="cog_ad",
                label="COG-AD — Executive/Frontal Variant MCI",
                description="MCI with prominent executive dysfunction disproportionate to memory impairment. DLPFC-predominant network involvement.",
                key_features=["Executive dysfunction", "Planning impairment", "Verbal fluency decline", "Relative memory preservation"],
                primary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.TPS],
                tdcs_target="Bilateral DLPFC anodal (F3+F4) — executive enhancement protocol",
                tps_target="Left DLPFC TPS targeting",
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="moca",
                name="Montreal Cognitive Assessment",
                abbreviation="MoCA",
                domains=["cognition", "memory", "executive_function", "attention", "language", "visuospatial"],
                timing="baseline",
                evidence_pmid="15817019",
                notes="Primary cognitive screening tool. Score 18-25 = MCI range; <18 = possible dementia. Administer at baseline and every 3 months.",
            ),
            AssessmentTool(
                scale_key="mmse",
                name="Mini-Mental State Examination",
                abbreviation="MMSE",
                domains=["cognition", "orientation", "memory", "language", "visuospatial"],
                timing="baseline",
                evidence_pmid="1202204",
                notes="Widely used staging tool. Score 21-26 = mild AD; 10-20 = moderate AD; <10 = severe AD. Less sensitive to MCI than MoCA.",
            ),
            AssessmentTool(
                scale_key="adas_cog",
                name="Alzheimer's Disease Assessment Scale — Cognitive Subscale",
                abbreviation="ADAS-Cog",
                domains=["memory", "language", "praxis", "orientation", "word_recall"],
                timing="baseline",
                evidence_pmid="6610245",
                notes="Gold standard cognitive outcome measure in AD clinical trials. Higher score = greater impairment. 4-point change = clinically meaningful.",
            ),
            AssessmentTool(
                scale_key="cdr",
                name="Clinical Dementia Rating Scale",
                abbreviation="CDR",
                domains=["memory", "orientation", "judgment", "community_affairs", "home_hobbies", "personal_care"],
                timing="baseline",
                evidence_pmid="6635122",
                notes="Global severity and staging scale. CDR 0.5 = MCI; CDR 1 = mild; CDR 2 = moderate dementia. Sum of Boxes (CDR-SB) for change tracking.",
            ),
            AssessmentTool(
                scale_key="npi",
                name="Neuropsychiatric Inventory",
                abbreviation="NPI",
                domains=["agitation", "depression", "anxiety", "apathy", "delusions", "hallucinations"],
                timing="baseline",
                evidence_pmid="7861634",
                notes="Assessment of BPSD. Administered to caregiver. Frequency x Severity scoring. Essential for BPSD phenotype.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="BPSD mood screen. Administer to carer if patient cannot self-report reliably. Score >=10 = clinically significant depression in AD.",
            ),
        ],

        baseline_measures=[
            "MoCA (primary cognitive screen — administer at baseline and endpoint)",
            "MMSE (staging — baseline and 6 months)",
            "ADAS-Cog (clinical trial outcome measure — optional for research protocols)",
            "CDR / CDR Sum of Boxes (global severity staging)",
            "NPI (neuropsychiatric symptom screen — caregiver-reported)",
            "SOZO PRS (patient/carer-rated cognitive function, mood, ADLs — 0-10)",
            "PHQ-9 and GAD-7 (BPSD mood/anxiety screen)",
            "Capacity assessment documentation — mandatory",
        ],

        followup_measures=[
            "MoCA at Week 8-10 and 6 months",
            "MMSE at 6 months",
            "NPI at Week 8-10 (BPSD phenotype)",
            "SOZO PRS at each session (brief) and end of block (full)",
            "Adverse event monitoring at every session",
            "Carer observations documented at each visit",
        ],

        inclusion_criteria=[
            "Confirmed diagnosis of amnestic MCI or mild-to-moderate AD (CDR 0.5-2, MMSE >=10)",
            "MoCA 10-26 at baseline",
            "Age 55-90 years",
            "Capacity to provide informed consent, OR substitute decision-maker available and willing to provide consent",
            "Stable cholinesterase inhibitor or memantine medication for >=3 months (or medication-naive)",
            "Caregiver/carer available to accompany patient to sessions",
            "Adequate skin integrity at electrode placement sites",
        ],

        exclusion_criteria=[
            "Severe dementia (CDR 3, MMSE <10) — insufficient engagement and arousal for neuromodulation benefit",
            "Non-AD dementia as primary diagnosis (FTD, DLB, VaD) — require condition-specific protocols",
            "Active psychiatric crisis or severe agitation requiring urgent medication change",
            "History of unprovoked seizures or active epilepsy",
            "Recent falls with head injury or skull fracture",
            "Anticoagulation therapy with INR >3 (relevant for TPS safety)",
            "Metallic intracranial implants near TPS targeting site",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "TPS-specific: anticoagulation with elevated INR (>3) near skull — contact with Storz Medical for device-specific guidance",
            "TPS-specific: metallic intracranial implants (aneurysm clips, cochlear implants) within the acoustic field",
        ],

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "precaution",
                "Capacity assessment is mandatory before treatment initiation. For patients with impaired capacity, obtain substitute decision-maker (healthcare proxy/guardian) consent. Document capacity assessment and consent process in clinical records.",
                "high",
                "Legal and ethical requirement for dementia patients; Mental Health Act and Guardianship provisions",
            ),
            make_safety(
                "monitoring",
                "Monitor for behavioral changes, agitation, distress, or skin discomfort during stimulation. Patients with moderate dementia may not reliably report discomfort — observe facial expressions and behavioral cues throughout session.",
                "moderate",
                "Clinical safety precaution for cognitively impaired patients",
            ),
            make_safety(
                "precaution",
                "TPS is approved for Alzheimer's Disease in some jurisdictions (confirm current regulatory status). Even where approved, informed consent with capacity assessment remains mandatory. Document regulatory basis for TPS use.",
                "high",
                "Regulatory and clinical governance requirement",
            ),
            make_safety(
                "precaution",
                "Start with shorter session durations (15 min) in patients with moderate AD or significant behavioral symptoms. Extend to 20-30 min only after confirming tolerance. Caregiver presence throughout session recommended.",
                "moderate",
                "Clinical practice adaptation for dementia population",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Temporal-Parietal Cortex", "TP", "bilateral",
                "Temporal-parietal regions mediating episodic memory encoding, semantic processing, "
                "and language. Anodal tDCS targets residual activity in hippocampal-cortical memory circuits. "
                "Ferrucci et al. (2008) demonstrated improved recognition memory; Boggio et al. (2012) "
                "demonstrated visual and verbal memory improvements in AD. Bilateral temporal-parietal "
                "anodal montage is the most-evidenced tDCS approach in AD.",
                "C-AD-MEM — Memory Enhancement Protocol",
                EvidenceLevel.MEDIUM, off_label=True,
                eeg_canonical=["P3", "P4", "T3", "T5", "T4", "T6"],
            ),
            make_tdcs_target(
                "Dorsolateral Prefrontal Cortex", "DLPFC", "bilateral",
                "DLPFC anodal tDCS targets executive network residual capacity. Useful for executive/frontal "
                "variant MCI and as adjunct to temporal-parietal memory protocol. Limited AD-specific evidence; "
                "rationale extrapolated from MCI cognitive enhancement studies.",
                "C-AD-EXEC — Executive Function Protocol",
                EvidenceLevel.LOW, off_label=True,
                eeg_canonical=["F3", "F4"],
            ),
            make_tps_target(
                "Hippocampus / Entorhinal Cortex", "HC/EC", "bilateral",
                "TPS can reach hippocampal depth (~40-50mm from scalp) using focused acoustic pulse energy. "
                "Benussi et al. (2020) Brain Stimulation RCT demonstrated cognitive improvements in MCI/AD "
                "with TPS targeting. Neuronavigation-guided placement essential for accurate hippocampal targeting. "
                "This indication is approved in some jurisdictions — verify local regulatory status.",
                "T-AD — Hippocampal/Entorhinal TPS",
                EvidenceLevel.MEDIUM,
                eeg_canonical=["T3", "T5"],
            ),
            StimulationTarget(
                modality=Modality.CES,
                target_region="Bilateral earlobe electrodes",
                target_abbreviation="CES",
                laterality="bilateral",
                rationale="Alpha-Stim CES addresses sleep disturbance, anxiety, and mood symptoms in BPSD "
                          "subtype. CES FDA-cleared for anxiety, depression, insomnia. Adjunct to cognitive "
                          "protocols for patients with significant BPSD burden.",
                protocol_label="CES-AD-BPSD — Behavioral Symptom Adjunct",
                evidence_level=EvidenceLevel.LOW,
                off_label=False,
                eeg_canonical=["Ear"],
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-AD-MEM", label="Memory Enhancement — Temporal-Parietal tDCS", modality=Modality.TDCS,
                target_region="Temporal-Parietal Cortex", target_abbreviation="TP",
                phenotype_slugs=["mci_am", "mild_ad"],
                network_targets=[NetworkKey.DMN, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "P3 + P4 (bilateral parietal) or T5+T6 (temporal-parietal)",
                    "cathode": "Fp1 + Fp2 (bilateral supraorbital) or shoulder reference",
                    "intensity": "1.5-2.0 mA",
                    "duration": "20-30 min (start 15 min in moderate AD)",
                    "sessions": "10-15 over 3 weeks",
                    "electrode_size": "35 cm2",
                    "note": "Ferrucci montage: anodes over temporal-parietal regions. Cognitive stimulation activities during session recommended.",
                },
                rationale="Temporal-parietal anodal tDCS targets episodic memory and semantic processing nodes. "
                          "Ferrucci et al. (2008) Neurology study (N=10) demonstrated improved recognition memory "
                          "in AD. Boggio et al. (2012) PLOS ONE demonstrated visual memory improvements. "
                          "Meta-analyses of tDCS in AD confirm moderate memory effect sizes. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
                # Extended protocol fields
                protocol_name='TDCS-AD-MEM — Temporal-Parietal Memory Enhancement',
                clinical_objective='Enhance residual episodic and recognition memory in MCI/mild AD via temporal-parietal cortex anodal stimulation',
                primary_targets=['Bilateral Temporal-Parietal Cortex (T5/T6, P3/P4)'],
                secondary_targets=['Hippocampal projection zones'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Ch1 Anode (+): P3/T5 (left temporal-parietal). Ch2 Anode (+): P4/T6 (right temporal-parietal). Cathode (-): Fp1/Fp2 bilateral supraorbital. 1.5-2.0 mA, 20-30 min.',
                frequency='1 session/day, 5 days/week',
                duration='20-30 min per session',
                intensity_dose='1.5-2.0 mA per channel',
                montage_roi='Anode (+): P3/T5 (L temporal-parietal), P4/T6 (R temporal-parietal). Cathode (-): Fp1/Fp2 (bilateral supraorbital)',
                laterality='Bilateral temporal-parietal',
                treatment_course='10-15 sessions over 3 weeks; reassess at Week 4',
                monitoring='Impedance check; MoCA biweekly; MMSE at baseline and Week 8; skin integrity; caregiver report',
                expected_response='Stabilization or mild improvement in recognition memory by Week 4-6; MoCA stabilization',
                evidence_status='Moderate — Ferrucci et al. 2008 (N=10); Boggio et al. 2012 (N=12); multiple meta-analyses support moderate memory effect',
                cautions='Capacity assessment mandatory in moderate AD. Caregiver must be present. Start at 15 min in moderate AD. OFF-LABEL.',
                when_to_escalate='If no stabilization after 10 sessions, reassess AD stage; consider adding TPS hippocampal protocol',
                when_to_stop_modify='Stop if skin irritation, confusion increase, or behavioral agitation during/after sessions',
                clinical_notes_extended='Cognitive stimulation activities (picture naming, word association) during session enhance activity-dependent plasticity. Caregiver involvement critical.',
                key_citations=['Ferrucci et al., 2008', 'Boggio et al., 2012', 'Benussi et al., 2020'],
            ),
            ProtocolEntry(
                protocol_id="T-AD", label="Hippocampal TPS — Memory (MCI)", modality=Modality.TPS,
                target_region="Hippocampus / Entorhinal region", target_abbreviation="HC/EC",
                phenotype_slugs=["mci_am"],
                network_targets=[NetworkKey.DMN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Hippocampal neuronavigation target (40-50mm depth from scalp)",
                    "pulses": "300-400 per session",
                    "frequency": "5 Hz",
                    "energy": "0.25 mJ/mm2",
                    "sessions": "6-9",
                    "note": "Neuronavigation required. MRI-based targeting. Bilateral treatment applied sequentially.",
                },
                rationale="TPS delivers focused acoustic pulse energy at hippocampal depth, inducing neuroplasticity "
                          "in memory circuits inaccessible to surface tDCS. Benussi et al. (2020) Brain Stimulation "
                          "RCT (N=33) demonstrated significant cognitive improvements at 1 and 3 months in MCI/AD. "
                          "Confirm regulatory approval status for AD indication in your jurisdiction. Doctor authorization mandatory.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=9,
                notes="TPS is approved for Alzheimer's Disease in some jurisdictions — confirm regulatory status. Informed consent and capacity assessment mandatory.",
                # Extended protocol fields
                protocol_name='TPS-AD-HC — Hippocampal TPS Memory Protocol',
                clinical_objective='Induce neuroplasticity in hippocampal memory circuits via focused acoustic pulse stimulation at depth',
                primary_targets=['Hippocampus bilateral (40-50mm depth)'],
                secondary_targets=['Entorhinal cortex', 'Temporal cortex'],
                device_name='NEUROLITH® TPS System (Storz Medical)',
                session_structure='Neuronavigation setup → Holocranial priming (2,000 pulses) → Targeted hippocampal stimulation (4,000 pulses bilateral) → Temporal cortex secondary (2,000 pulses)',
                frequency='3 sessions/week',
                duration='30-45 min per session',
                intensity_dose='0.20-0.25 mJ/mm²; 5 Hz',
                montage_roi='MRI-neuronavigated hippocampal targets; scalp entry near T5/T6',
                laterality='Bilateral sequential',
                treatment_course='6-9 sessions over 2-3 weeks; then maintenance 1-2/month',
                monitoring='MoCA at baseline and post-block; MMSE; caregiver ADL report; tolerability log',
                expected_response='Cognitive stabilization or improvement at 1 and 3 months post-treatment; MoCA improvement >=2 points',
                evidence_status='Moderate — Benussi et al. 2020 RCT (N=33) demonstrated significant cognitive improvement at 1 and 3 months',
                cautions='TPS has regulatory approval for AD in some jurisdictions — confirm local status. Neuronavigation mandatory. Capacity assessment required.',
                when_to_escalate='If no improvement after full 9-session block, consider adding tDCS temporal-parietal protocol',
                when_to_stop_modify='Stop if headache persists >24h, confusion increase, or behavioral change',
                clinical_notes_extended='Most evidence-supported TPS application in AD. Hippocampal depth targeting is the key differentiator from surface tDCS.',
                key_citations=['Benussi et al., 2020', 'Beisteiner et al., 2020'],
            ),
            ProtocolEntry(
                protocol_id="C-AD-EXEC", label="Executive Function — DLPFC tDCS", modality=Modality.TDCS,
                target_region="Dorsolateral Prefrontal Cortex", target_abbreviation="DLPFC",
                phenotype_slugs=["cog_ad", "mci_am"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 + F4 (bilateral DLPFC)",
                    "cathode": "Right shoulder or Oz",
                    "intensity": "1.5-2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-12",
                },
                rationale="DLPFC anodal tDCS targets CEN executive function nodes in frontal MCI and early AD. "
                          "Rationale extrapolated from DLPFC tDCS cognitive enhancement literature. Limited "
                          "AD-specific evidence. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=12,
                # Extended protocol fields
                protocol_name='TDCS-AD-EXEC — DLPFC Executive Function Protocol',
                clinical_objective='Enhance frontal executive function in MCI and early AD',
                primary_targets=['Bilateral DLPFC (F3/F4)'],
                secondary_targets=['ACC'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Ch1 Anode (+): F3 (L-DLPFC). Ch2 Anode (+): F4 (R-DLPFC). Cathode (-): Right shoulder or Oz. 1.5-2.0 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='1.5-2.0 mA per channel',
                montage_roi='Anode (+): F3 (L-DLPFC), F4 (R-DLPFC). Cathode (-): Right shoulder or Oz',
                laterality='Bilateral prefrontal',
                treatment_course='10-12 sessions over 2-3 weeks',
                monitoring='Impedance check; MoCA biweekly; executive function subtests; skin integrity',
                expected_response='Improvement in attention and executive task performance by Week 3-4',
                evidence_status='Low — extrapolated from DLPFC tDCS cognitive enhancement literature; limited AD-specific data',
                cautions='OFF-LABEL. Lower intensity (1.5 mA) in moderate AD. Monitor for confusion.',
                when_to_escalate='If <20% improvement after 10 sessions, reassess targeting; consider temporal-parietal memory protocol instead',
                when_to_stop_modify='Stop if confusion, agitation, or skin lesion',
                clinical_notes_extended='Concurrent cognitive training exercises (Trail Making, Stroop) during stimulation recommended.',
                key_citations=['Boggio et al., 2012'],
            ),
            # ── C5-C8: Expanded tDCS protocols ──────────────────────
            ProtocolEntry(
                protocol_id="C5", label="Temporal/Hippocampal — Memory Encoding", modality=Modality.TDCS,
                target_region="Temporal Cortex / Hippocampal Proxy", target_abbreviation="TC/HC",
                phenotype_slugs=["mci_am", "mild_ad"],
                network_targets=[NetworkKey.DMN, NetworkKey.LIMBIC],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "T5 + T6 (bilateral temporal — hippocampal proxy)",
                    "cathode": "Fp1 + Fp2 (bilateral supraorbital)",
                    "intensity": "1.5 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                },
                rationale="Bilateral temporal anodal tDCS over hippocampal projection zones targets memory encoding circuits. Entorhinal-hippocampal axis is the earliest site of tau pathology (Braak I-II). Aims to enhance residual encoding capacity in MCI/mild AD. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # Extended protocol fields
                protocol_name='TDCS-AD-TEMP — Temporal/Hippocampal Memory Encoding',
                clinical_objective='Enhance residual memory encoding via bilateral temporal cortex stimulation at hippocampal projection zones',
                primary_targets=['Bilateral Temporal Cortex (T5/T6)'],
                secondary_targets=['Hippocampal formation via cortical projection'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Ch1 Anode (+): T5 (left temporal). Ch2 Anode (+): T6 (right temporal). Cathode (-): Fp1/Fp2. 1.5 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='1.5 mA per channel',
                montage_roi='Anode (+): T5 (L temporal), T6 (R temporal). Cathode (-): Fp1/Fp2 (bilateral supraorbital)',
                laterality='Bilateral temporal',
                treatment_course='10-15 sessions over 3 weeks',
                monitoring='Impedance check; MoCA biweekly; memory-specific subtests; skin integrity',
                expected_response='Memory encoding stabilization; reduced forgetting rate on delayed recall tasks',
                evidence_status='Low — rationale from neuroanatomy; limited direct evidence for temporal tDCS in AD',
                cautions='OFF-LABEL. Temporal electrodes closer to seizure-prone regions — start 1.5 mA. Monitor for any seizure-like phenomena.',
                when_to_escalate='If no improvement after 10 sessions, consider adding TPS hippocampal protocol',
                when_to_stop_modify='Stop if any seizure activity, confusion increase, or skin irritation',
                clinical_notes_extended='Entorhinal-hippocampal axis is earliest site of tau pathology (Braak I-II). Activity-dependent enhancement with memory encoding tasks during stimulation.',
                key_citations=['Ferrucci et al., 2008'],
            ),
            ProtocolEntry(
                protocol_id="C6", label="Parietal — Visuospatial/Navigation", modality=Modality.TDCS,
                target_region="Posterior Parietal Cortex", target_abbreviation="PPC",
                phenotype_slugs=["mild_ad", "cog_ad"],
                network_targets=[NetworkKey.DMN, NetworkKey.ATTENTION],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "P3 + P4 (bilateral parietal)",
                    "cathode": "Right shoulder reference",
                    "intensity": "1.5-2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                },
                rationale="Posterior parietal anodal tDCS targets visuospatial processing and navigation networks impaired in AD. Angular gyrus and precuneus are key DMN nodes showing early amyloid deposition and hypometabolism. Addresses getting-lost behaviour and spatial disorientation. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # Extended protocol fields
                protocol_name='TDCS-AD-PAR — Parietal Visuospatial/Navigation',
                clinical_objective='Support visuospatial processing and spatial navigation in AD',
                primary_targets=['Bilateral Posterior Parietal Cortex (P3/P4)'],
                secondary_targets=['Precuneus', 'Angular gyrus'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Ch1 Anode (+): P3 (left parietal). Ch2 Anode (+): P4 (right parietal). Cathode (-): Right shoulder. 1.5-2.0 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='1.5-2.0 mA per channel',
                montage_roi='Anode (+): P3 (L parietal), P4 (R parietal). Cathode (-): Right shoulder reference',
                laterality='Bilateral parietal',
                treatment_course='10-15 sessions over 3 weeks',
                monitoring='Impedance check; visuospatial testing; MoCA; skin integrity',
                expected_response='Improved spatial orientation and navigation; reduced getting-lost episodes',
                evidence_status='Low — rationale from AD neuroimaging; early amyloid deposition in parietal regions',
                cautions='OFF-LABEL. Monitor for visual disturbance during parietal stimulation.',
                when_to_escalate='If no improvement after 10 sessions, reassess AD stage and consider alternative protocol',
                when_to_stop_modify='Stop if visual disturbance, confusion, or skin lesion',
                clinical_notes_extended='Angular gyrus and precuneus show early amyloid deposition and hypometabolism in AD. Address getting-lost behaviour specifically.',
                key_citations=['Boggio et al., 2012', 'Buckner et al., 2009'],
            ),
            ProtocolEntry(
                protocol_id="C7", label="Language/Broca — Word-Finding & Semantic", modality=Modality.TDCS,
                target_region="Left Inferior Frontal Gyrus (Broca's area)", target_abbreviation="L-IFG",
                phenotype_slugs=["mild_ad", "cog_ad", "mci_am"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F5 (left IFG / Broca's area proxy)",
                    "cathode": "Right shoulder or Fp2",
                    "intensity": "1.5 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                    "note": "Combine with naming and word-finding exercises during stimulation for activity-dependent enhancement",
                },
                rationale="Left IFG anodal tDCS targets word-finding difficulties and semantic processing deficits prominent in AD. Anomia is an early language symptom; Broca's area stimulation combined with naming exercises leverages activity-dependent plasticity. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # Extended protocol fields
                protocol_name='TDCS-AD-LANG — Language/Broca Word-Finding',
                clinical_objective='Support word-finding and semantic processing in AD-related anomia',
                primary_targets=["Left Inferior Frontal Gyrus / Broca's area (F5)"],
                secondary_targets=['Left temporal language areas'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Anode (+): F5 (left IFG / Broca proxy). Cathode (-): Right shoulder or Fp2. 1.5 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='1.5 mA',
                montage_roi="Anode (+): F5 (left IFG / Broca's area proxy). Cathode (-): Right shoulder or Fp2",
                laterality='Left-dominant (language lateralization)',
                treatment_course='10-15 sessions over 3 weeks',
                monitoring='Impedance check; naming accuracy; semantic fluency; skin integrity',
                expected_response='Improved word retrieval speed and naming accuracy',
                evidence_status='Low — rationale from aphasia tDCS literature; limited AD-specific data',
                cautions='OFF-LABEL. Combine with naming exercises for activity-dependent enhancement.',
                when_to_escalate='If no improvement after 10 sessions, consider speech-language therapy adjunct',
                when_to_stop_modify='Stop if confusion, agitation, or skin lesion',
                clinical_notes_extended="Anomia is an early language symptom in AD. Broca's area stimulation + naming exercises leverages activity-dependent plasticity.",
                key_citations=['Ferrucci et al., 2008'],
            ),
            ProtocolEntry(
                protocol_id="C8", label="ACC/Attention — Sustained Attention Deficits", modality=Modality.TDCS,
                target_region="Anterior Cingulate Cortex / Medial Frontal", target_abbreviation="ACC/MFC",
                phenotype_slugs=["cog_ad", "mci_am", "mild_ad"],
                network_targets=[NetworkKey.SN, NetworkKey.ATTENTION],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "Fz (midline frontal — ACC proxy)",
                    "cathode": "Right mastoid",
                    "intensity": "1.5 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                },
                rationale="ACC/medial frontal anodal tDCS targets sustained attention deficits in AD. dACC is a key SN node regulating attention allocation; its dysfunction contributes to distractibility and apathy in AD/MCI. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # Extended protocol fields
                protocol_name='TDCS-AD-ATT — ACC/Attention Sustained Attention',
                clinical_objective='Improve sustained attention and reduce apathy via ACC/medial frontal modulation',
                primary_targets=['ACC / Medial Frontal (Fz)'],
                secondary_targets=['Dorsal attention network'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Anode (+): Fz (midline frontal / ACC proxy). Cathode (-): Right mastoid. 1.5 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='1.5 mA',
                montage_roi='Anode (+): Fz (midline frontal / ACC proxy). Cathode (-): Right mastoid',
                laterality='Midline',
                treatment_course='10-15 sessions over 3 weeks',
                monitoring='Impedance check; sustained attention tests; MoCA; apathy scale; skin integrity',
                expected_response='Improved sustained attention and reduced apathy scores',
                evidence_status='Low — rationale from SN/attention neuroimaging; limited direct evidence',
                cautions='OFF-LABEL. Monitor for headache with midline stimulation.',
                when_to_escalate='If no improvement after 10 sessions, reassess for depression/apathy-specific protocol',
                when_to_stop_modify='Stop if persistent headache, confusion, or skin lesion',
                clinical_notes_extended='dACC dysfunction contributes to distractibility and apathy in AD/MCI.',
                key_citations=['Buckner et al., 2009'],
            ),

            # ── T3-T5: Expanded TPS protocols ──────────────────────
            ProtocolEntry(
                protocol_id="T3", label="TPS — Hippocampal Deep Memory Circuit", modality=Modality.TPS,
                target_region="Hippocampus (bilateral deep target)", target_abbreviation="HC-deep",
                phenotype_slugs=["mci_am", "mild_ad"],
                network_targets=[NetworkKey.DMN, NetworkKey.LIMBIC],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Hippocampus bilateral (neuronavigation-guided — 40-50mm depth)",
                    "pulses": "300-400 per session",
                    "frequency": "5 Hz",
                    "energy": "0.20-0.25 mJ/mm2",
                    "sessions": "6-9 over 3 weeks",
                },
                rationale="Hippocampal TPS is THE primary TPS target for AD/MCI. Deep acoustic energy reaches hippocampal formation at 40-50mm depth, inducing neuroplasticity in memory circuits inaccessible to surface tDCS. Benussi et al. (2020) RCT demonstrated significant cognitive improvements. This is the most evidence-supported TPS application in AD.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=9,
                # Extended protocol fields
                protocol_name='TPS-AD-HC-DEEP — Hippocampal Deep Memory Circuit',
                clinical_objective='Deep hippocampal neuroplasticity induction via focused acoustic pulse stimulation',
                primary_targets=['Hippocampus bilateral (40-50mm depth)'],
                secondary_targets=['Entorhinal cortex'],
                device_name='NEUROLITH® TPS System (Storz Medical)',
                session_structure='Neuronavigation setup → Holocranial priming (2,000 pulses) → Targeted hippocampal stimulation (4,000 pulses) → Secondary entorhinal targets (2,000 pulses)',
                frequency='3 sessions/week',
                duration='30-45 min per session',
                intensity_dose='0.20-0.25 mJ/mm²; 5 Hz',
                montage_roi='MRI-neuronavigated hippocampal targets; scalp entry near T5/T6',
                laterality='Bilateral sequential',
                treatment_course='6-9 sessions over 2-3 weeks; then maintenance',
                monitoring='MoCA pre/post block; memory subtests; tolerability log',
                expected_response='Cognitive improvement at 1 and 3 months post-treatment',
                evidence_status='Moderate — based on Benussi et al. 2020 RCT',
                cautions='TPS is investigational/off-label for AD in some jurisdictions. Neuronavigation mandatory.',
                when_to_escalate='If no improvement after full block, add tDCS temporal-parietal protocol',
                when_to_stop_modify='Stop if persistent headache >24h or behavioral deterioration',
                clinical_notes_extended='Primary TPS target for AD/MCI — hippocampal depth is key differentiator from surface stimulation.',
                key_citations=['Benussi et al., 2020', 'Beisteiner et al., 2020'],
            ),
            ProtocolEntry(
                protocol_id="T4", label="TPS — Temporal Cortex", modality=Modality.TPS,
                target_region="Lateral Temporal Cortex", target_abbreviation="LTC",
                phenotype_slugs=["mild_ad", "cog_ad", "mci_am"],
                network_targets=[NetworkKey.DMN, NetworkKey.CEN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Lateral temporal cortex bilateral (neuronavigation-guided)",
                    "pulses": "300-400 per session",
                    "frequency": "5 Hz",
                    "energy": "0.20-0.25 mJ/mm2",
                    "sessions": "6-9 over 3 weeks",
                },
                rationale="Temporal cortex TPS targets semantic memory and language networks affected in AD. Lateral temporal regions show progressive atrophy and hypometabolism in AD; TPS may support residual function and synaptic plasticity in these areas. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=9,
                # Extended protocol fields
                protocol_name='TPS-AD-LTC — Temporal Cortex Semantic Memory',
                clinical_objective='Support semantic memory and language networks via lateral temporal cortex TPS',
                primary_targets=['Lateral Temporal Cortex bilateral'],
                secondary_targets=['Superior temporal gyrus'],
                device_name='NEUROLITH® TPS System (Storz Medical)',
                session_structure='Neuronavigation setup → Holocranial priming (2,000 pulses) → Lateral temporal targeted stimulation (4,000 pulses) → Secondary areas (2,000 pulses)',
                frequency='3 sessions/week',
                duration='30-45 min per session',
                intensity_dose='0.20-0.25 mJ/mm²; 5 Hz',
                montage_roi='MRI-neuronavigated lateral temporal targets; scalp near T3/T4',
                laterality='Bilateral',
                treatment_course='6-9 sessions over 2-3 weeks',
                monitoring='Language/naming assessments; MoCA; tolerability log',
                expected_response='Improved semantic fluency and naming',
                evidence_status='Low — extrapolated from hippocampal TPS literature',
                cautions='TPS is investigational/off-label for temporal cortex targeting in AD. Neuronavigation recommended.',
                when_to_escalate='If no improvement, consider hippocampal TPS protocol instead',
                when_to_stop_modify='Stop if headache, tinnitus, or confusion',
                clinical_notes_extended='Lateral temporal regions show progressive atrophy in AD; TPS may support residual synaptic plasticity.',
                key_citations=['Benussi et al., 2020'],
            ),
            ProtocolEntry(
                protocol_id="T5", label="TPS — Parietal / Precuneus", modality=Modality.TPS,
                target_region="Posterior Parietal / Precuneus", target_abbreviation="PPC/Prec",
                phenotype_slugs=["mild_ad", "cog_ad"],
                network_targets=[NetworkKey.DMN, NetworkKey.ATTENTION],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Posterior parietal cortex / precuneus (neuronavigation-guided)",
                    "pulses": "300-400 per session",
                    "frequency": "5 Hz",
                    "energy": "0.20-0.25 mJ/mm2",
                    "sessions": "6-9 over 3 weeks",
                },
                rationale="Parietal/precuneus TPS targets the posterior DMN hub — one of the earliest sites of amyloid deposition and functional disconnection in AD. Precuneus hypometabolism is a biomarker of prodromal AD. TPS may support residual connectivity. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=9,
                # Extended protocol fields
                protocol_name='TPS-AD-PPC — Parietal/Precuneus DMN Hub',
                clinical_objective='Support posterior DMN hub connectivity and visuospatial function',
                primary_targets=['Posterior Parietal Cortex / Precuneus'],
                secondary_targets=['Angular gyrus'],
                device_name='NEUROLITH® TPS System (Storz Medical)',
                session_structure='Neuronavigation setup → Holocranial priming (2,000 pulses) → Parietal/precuneus targeted stimulation (4,000 pulses) → Secondary areas (2,000 pulses)',
                frequency='3 sessions/week',
                duration='30-45 min per session',
                intensity_dose='0.20-0.25 mJ/mm²; 5 Hz',
                montage_roi='MRI-neuronavigated parietal/precuneus targets; scalp near Pz/P3/P4',
                laterality='Bilateral/midline',
                treatment_course='6-9 sessions over 2-3 weeks',
                monitoring='Visuospatial assessments; MoCA; tolerability log',
                expected_response='Improved visuospatial function and DMN connectivity',
                evidence_status='Low — precuneus hypometabolism is AD biomarker; TPS targeting is investigational',
                cautions='TPS is investigational/off-label for parietal targeting. Neuronavigation recommended.',
                when_to_escalate='If no improvement, consider hippocampal TPS as primary target',
                when_to_stop_modify='Stop if headache or visual disturbance',
                clinical_notes_extended='Precuneus hypometabolism is a biomarker of prodromal AD. One of earliest sites of amyloid deposition.',
                key_citations=['Buckner et al., 2009', 'Benussi et al., 2020'],
            ),

            ProtocolEntry(
                protocol_id="CES-AD-BPSD", label="CES — BPSD: Sleep, Anxiety & Mood", modality=Modality.CES,
                target_region="Bilateral earlobe electrodes", target_abbreviation="CES",
                phenotype_slugs=["bpsd"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim AID",
                    "frequency": "0.5 Hz",
                    "intensity": "100-200 uA",
                    "duration": "40-60 min",
                    "sessions": "Daily during treatment block",
                    "note": "Caregiver to supervise at-home use. Start with 40 min, extend to 60 min if tolerated.",
                },
                rationale="Alpha-Stim CES addresses BPSD symptoms: anxiety, depression, insomnia prevalent in "
                          "AD. FDA-cleared for these indications. Adjunct to memory protocols; caregiver-supervised "
                          "home use feasible. Non-pharmacological option to reduce psychotropic load in dementia.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
                # Extended protocol fields
                protocol_name='CES-AD-BPSD — Behavioral Symptom Adjunct',
                clinical_objective='Address BPSD symptoms (anxiety, depression, insomnia) as adjunct to cognitive protocols',
                primary_targets=['Bilateral earlobe electrodes (cranial nerve modulation)'],
                secondary_targets=['Limbic network via alpha-wave entrainment'],
                device_name='Alpha-Stim® AID',
                session_structure='Bilateral earlobe clip electrodes; 0.5 Hz, 100-200 µA; 40-60 min; caregiver-supervised',
                frequency='Daily during treatment block',
                duration='40-60 min per session',
                intensity_dose='100-200 µA at 0.5 Hz',
                montage_roi='Bilateral earlobe clip electrodes',
                laterality='Bilateral',
                treatment_course='Daily for treatment block; then as needed for symptom management',
                monitoring='NPI (neuropsychiatric inventory); sleep diary; caregiver report; skin integrity',
                expected_response='Reduced anxiety, improved sleep quality, stabilized mood within 2-3 weeks',
                evidence_status='Moderate — CES FDA-cleared for anxiety, depression, insomnia; limited AD-specific data',
                cautions='Adjunctive only — not primary AD treatment. Caregiver supervision required for at-home use.',
                when_to_escalate='If BPSD symptoms persist, review pharmacological management with geriatric psychiatrist',
                when_to_stop_modify='Stop if skin irritation at earlobe sites or patient agitation during use',
                clinical_notes_extended='Non-pharmacological option to reduce psychotropic load in dementia. Caregiver-supervised home use feasible.',
                key_citations=['Kirsch DL, 2010'],
            ),
        ],

        symptom_network_mapping={
            "Episodic Memory Loss": [NetworkKey.DMN, NetworkKey.CEN],
            "Executive Dysfunction": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Language Impairment": [NetworkKey.DMN, NetworkKey.CEN],
            "Behavioral Symptoms (BPSD)": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Sleep Disturbance": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "Anxiety / Agitation": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Apathy": [NetworkKey.LIMBIC, NetworkKey.CEN],
        },

        symptom_modality_mapping={
            "Episodic Memory Loss": [Modality.TDCS, Modality.TPS],
            "Executive Dysfunction": [Modality.TDCS],
            "Language Impairment": [Modality.TDCS],
            "Behavioral Symptoms (BPSD)": [Modality.TDCS, Modality.CES],
            "Sleep Disturbance": [Modality.CES, Modality.TAVNS],
            "Anxiety / Agitation": [Modality.CES, Modality.TAVNS],
            "Apathy": [Modality.TDCS],
        },

        responder_criteria=[
            "Stabilization or improvement in MoCA score (no >=2-point decline from baseline at Week 8-10)",
            ">=2-point improvement on SOZO PRS cognitive function domain",
            "Carer-reported functional improvement or stability in ADLs",
            "NPI score stabilization or reduction >=25% (BPSD phenotype)",
        ],

        non_responder_pathway=(
            "For patients classified as non-responders or showing accelerated decline:\n"
            "1. Re-evaluate AD stage — moderate-severe AD (CDR 2-3) unlikely to respond meaningfully\n"
            "2. Review capacity and carer support — inadequate session completion limits response\n"
            "3. Consider BPSD protocol if behavioral symptoms are primary burden\n"
            "4. Doctor neurological review — reassess diagnosis, rule out VaD or DLB\n"
            "5. Assess and optimize cholinesterase inhibitor or memantine regimen\n"
            "6. If MCI non-responder: repeat MoCA at 6 months — conversion to AD dementia may explain decline\n"
            "7. Refer to memory clinic for updated biomarker assessment"
        ),

        evidence_summary=(
            "AD/MCI has moderate-quality evidence for tDCS. Ferrucci et al. (2008) demonstrated "
            "recognition memory improvements with temporal-parietal tDCS. Boggio et al. (2012) confirmed "
            "visual memory improvements. Meta-analyses of tDCS in AD (Hsu et al. 2015) confirm cognitive "
            "benefits with moderate effect sizes. TPS: Benussi et al. (2020) RCT demonstrated significant "
            "cognitive improvements in MCI/AD — the strongest single study for TPS in this population. "
            "CES: inferred from FDA clearance for anxiety/insomnia — no dedicated AD RCT. "
            "| Evidence counts (published papers): TPS=31, TMS=30, tDCS=20, tACS=15, PBM=20, taVNS=5, "
            "LIFU=10, PEMF=5, DBS=5. "
            "Best modalities: TPS, TMS + Cognitive Training."
        ),

        evidence_gaps=[
            "No adequately powered, biomarker-confirmed multi-site RCT of tDCS for AD with cognitive primary endpoint",
            "Long-term disease-modifying effects of neuromodulation in AD — unknown and methodologically challenging to establish",
            "TPS in AD — Benussi et al. is promising but requires independent replication in larger samples",
            "Optimal tDCS montage for AD/MCI (temporal-parietal vs DLPFC vs combined) — no head-to-head trial",
            "Predictors of neuromodulation response in AD — biomarker, genetic (APOE ε4), or functional connectivity predictors not established",
        ],

        references=[
            {
                "authors": "Boggio PS et al.",
                "year": 2012,
                "title": "Temporal lobe cortical electrical stimulation during the encoding and retrieval phase reduces false memories",
                "journal": "PLOS ONE",
                "pmid": "22479484",
                "evidence_type": "rct",
            },
            {
                "authors": "Ferrucci R et al.",
                "year": 2008,
                "title": "Transcranial direct current stimulation improves recognition memory in Alzheimer disease",
                "journal": "Neurology",
                "pmid": "18981371",
                "evidence_type": "rct",
            },
            {
                "authors": "Benussi A et al.",
                "year": 2020,
                "title": "Transcranial Pulse Stimulation in Patients with Alzheimer Disease: A Randomized, Double-Blind, Sham-Controlled Trial",
                "journal": "Brain Stimulation",
                "pmid": "32534178",
                "evidence_type": "rct",
            },
            {
                "authors": "Buckner RL et al.",
                "year": 2009,
                "title": "Cortical hubs revealed by intrinsic functional connectivity: mapping, assessment of stability, and relation to Alzheimer's disease",
                "journal": "Journal of Neuroscience",
                "pmid": "19176803",
                "evidence_type": "cohort_study",
            },
            {
                "authors": "Nasreddine ZS et al.",
                "year": 2005,
                "title": "The Montreal Cognitive Assessment, MoCA: a brief screening tool for mild cognitive impairment",
                "journal": "Journal of the American Geriatrics Society",
                "pmid": "15817019",
                "evidence_type": "cohort_study",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        clinical_tips=[
            "Capacity assessment is a mandatory first step — document thoroughly before any consent process. Involve caregiver/healthcare proxy from the outset.",
            "Start with shorter sessions (15-20 min) in patients with moderate AD — extend to 30 min only after confirmed tolerance across multiple sessions",
            "TPS hippocampal targeting requires accurate neuronavigation and MRI-based planning — Partner-tier or specialist clinician only",
            "Perform cognitive stimulation activities (word recall, picture naming, semantic fluency) during tDCS sessions to leverage activity-dependent plasticity",
            "Engage caregiver as active participant in outcome monitoring — carer-reported functional changes are often more clinically meaningful than scale scores",
            "Document regulatory status for TPS in your jurisdiction — approval status for AD indication may affect consent requirements",
        ],


        # --- Auto-enriched: PlatoScience Variants ---
        platoscience_variants=[
            PlatoScienceVariant(
                variant_id="C-AD-MEM-PS", protocol_id="C-AD-MEM",
                label="PlatoScience Memory Enhancement — Temporal-Parietal tDCS",
                parameters={"program": "Focus", "electrode_config": "P3 + P4 (bilateral parietal) or T5+T6 (temporal-parietal)", "intensity": "1.5-2.0 mA", "duration": "20-30 min (start 15 min in moderate AD)", "ramp": "30 sec"},
                notes="Maps to C-AD-MEM protocol. PlatoScience Focus program.",
            ),
            PlatoScienceVariant(
                variant_id="C-AD-EXEC-PS", protocol_id="C-AD-EXEC",
                label="PlatoScience Executive Function — DLPFC tDCS",
                parameters={"program": "Think", "electrode_config": "F3 + F4 (bilateral DLPFC)", "intensity": "1.5-2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C-AD-EXEC protocol. PlatoScience Think program.",
            ),
            PlatoScienceVariant(
                variant_id="C5-PS", protocol_id="C5",
                label="PlatoScience Temporal/Hippocampal — Memory Encoding",
                parameters={"program": "Focus", "electrode_config": "T5 + T6 (bilateral temporal)", "intensity": "1.5 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C5 protocol. PlatoScience Focus program.",
            ),
            PlatoScienceVariant(
                variant_id="C6-PS", protocol_id="C6",
                label="PlatoScience Parietal — Visuospatial/Navigation",
                parameters={"program": "Focus", "electrode_config": "P3 + P4 (bilateral parietal)", "intensity": "1.5-2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C6 protocol. PlatoScience Focus program.",
            ),
            PlatoScienceVariant(
                variant_id="C7-PS", protocol_id="C7",
                label="PlatoScience Language/Broca — Word-Finding",
                parameters={"program": "Think", "electrode_config": "F5 (left IFG / Broca's area proxy)", "intensity": "1.5 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C7 protocol. PlatoScience Think program. Combine with naming exercises.",
            ),
            PlatoScienceVariant(
                variant_id="C8-PS", protocol_id="C8",
                label="PlatoScience ACC/Attention — Sustained Attention",
                parameters={"program": "Focus", "electrode_config": "Fz (midline frontal — ACC proxy)", "intensity": "1.5 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C8 protocol. PlatoScience Focus program.",
            ),
        ],

        # --- Auto-enriched: Multimodal Combinations ---
        multimodal_combos=[
            MultimodalCombo(
                combo_id="F1", label="Memory Enhancement — Temporal-Parietal tDCS + Hippocampal TPS — Memory (MCI)",
                phenotype_slugs=['mci_am'],
                tps_protocol_id="T-AD",
                non_tps_protocol_ids=["C-AD-MEM"],
                sequencing_notes="Week 1-3: tDCS C-AD-MEM daily. Week 2-3: Add TPS T-AD (2-3x/week).",
                rationale="Combined TDCS + TPS targeting for enhanced cortical modulation.",
            ),
            MultimodalCombo(
                combo_id="F2", label="Executive Function — DLPFC tDCS + Hippocampal TPS — Memory (MCI)",
                phenotype_slugs=['mci_am'],
                tps_protocol_id="T-AD",
                non_tps_protocol_ids=["C-AD-EXEC"],
                sequencing_notes="Week 1-3: tDCS C-AD-EXEC daily. Week 2-3: Add TPS T-AD (2-3x/week).",
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
                "position": 'F3',
                "brain_region": 'Left DLPFC',
                "role": 'Executive function anodal target',
                "protocols_using": ['C-AD-EXEC', 'C8'],
            },
            {
                "position": 'F4',
                "brain_region": 'Right DLPFC',
                "role": 'Bilateral DLPFC executive target',
                "protocols_using": ['C-AD-EXEC'],
            },
            {
                "position": 'T5',
                "brain_region": 'Left Temporal / Hippocampal projection',
                "role": 'Memory encoding anodal target',
                "protocols_using": ['C-AD-MEM', 'C5'],
            },
            {
                "position": 'T6',
                "brain_region": 'Right Temporal / Hippocampal projection',
                "role": 'Memory encoding anodal target',
                "protocols_using": ['C-AD-MEM', 'C5'],
            },
            {
                "position": 'P3',
                "brain_region": 'Left Posterior Parietal',
                "role": 'Visuospatial / episodic memory target',
                "protocols_using": ['C-AD-MEM', 'C6'],
            },
            {
                "position": 'P4',
                "brain_region": 'Right Posterior Parietal',
                "role": 'Visuospatial / navigation target',
                "protocols_using": ['C-AD-MEM', 'C6'],
            },
            {
                "position": 'Fz',
                "brain_region": 'ACC / Midline Frontal',
                "role": 'Attention / ACC modulation',
                "protocols_using": ['C8'],
            },
            {
                "position": 'Pz',
                "brain_region": 'Precuneus / PCC',
                "role": 'DMN posterior hub TPS target',
                "protocols_using": ['T5'],
            },
        ],
        adverse_event_grades=SHARED_ADVERSE_EVENT_GRADES,
        side_effects=SHARED_SIDE_EFFECTS,
        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Informed consent for cognitively impaired patients requires formal capacity assessment and substitute decision-maker documentation",
            "TPS hippocampal targeting requires Partner-tier or specialist clinician with neuronavigation training",
            "Regulatory status of TPS for Alzheimer's Disease must be confirmed and documented for each patient",
        ],
    )
