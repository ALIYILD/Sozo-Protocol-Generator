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
            ),
            make_tdcs_target(
                "Dorsolateral Prefrontal Cortex", "DLPFC", "bilateral",
                "DLPFC anodal tDCS targets executive network residual capacity. Useful for executive/frontal "
                "variant MCI and as adjunct to temporal-parietal memory protocol. Limited AD-specific evidence; "
                "rationale extrapolated from MCI cognitive enhancement studies.",
                "C-AD-EXEC — Executive Function Protocol",
                EvidenceLevel.LOW, off_label=True,
            ),
            make_tps_target(
                "Hippocampus / Entorhinal Cortex", "HC/EC", "bilateral",
                "TPS can reach hippocampal depth (~40-50mm from scalp) using focused acoustic pulse energy. "
                "Benussi et al. (2020) Brain Stimulation RCT demonstrated cognitive improvements in MCI/AD "
                "with TPS targeting. Neuronavigation-guided placement essential for accurate hippocampal targeting. "
                "This indication is approved in some jurisdictions — verify local regulatory status.",
                "T-AD — Hippocampal/Entorhinal TPS",
                EvidenceLevel.MEDIUM,
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
            "CES: inferred from FDA clearance for anxiety/insomnia — no dedicated AD RCT."
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

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Informed consent for cognitively impaired patients requires formal capacity assessment and substitute decision-maker documentation",
            "TPS hippocampal targeting requires Partner-tier or specialist clinician with neuronavigation training",
            "Regulatory status of TPS for Alzheimer's Disease must be confirmed and documented for each patient",
        ],
    )
