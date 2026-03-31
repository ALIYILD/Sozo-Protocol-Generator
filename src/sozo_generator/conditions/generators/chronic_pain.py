"""
Chronic Pain / Fibromyalgia — Complete condition generator.

Key references:
- Fregni F et al. (2006) tDCS for fibromyalgia — Arthritis & Rheumatism. PMID: 16799965
- Lefaucheur JP et al. (2017) IFCN evidence-based guidelines for tDCS — Clinical Neurophysiology. PMID: 27866120
- Marlow NM et al. (2013) tDCS meta-analysis for chronic pain — Neuromodulation. PMID: 23590951
- Knotkova H et al. (2017) Bi-cephalic tDCS for fibromyalgia — Clinical Journal of Pain. PMID: 28009763
- Jensen MP et al. (2014) Non-pharmacological pain treatments — Expert Review of Neurotherapeutics. PMID: 25346329
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


def build_chronic_pain_condition() -> ConditionSchema:
    """Build the complete Chronic Pain / Fibromyalgia condition schema."""
    return ConditionSchema(
        slug="chronic_pain",
        display_name="Chronic Pain / Fibromyalgia",
        icd10="M79.3",
        aliases=["fibromyalgia", "FMS", "chronic pain", "chronic widespread pain", "central sensitization", "CLBP", "chronic low back pain"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Chronic pain encompasses persistent pain lasting more than 3 months, including Fibromyalgia "
            "Syndrome (FMS), Chronic Low Back Pain (CLBP), and other central sensitization conditions. "
            "FMS affects 2-8% of the general population, predominantly women (7:1 ratio). Chronic pain "
            "represents a leading cause of disability globally.\n\n"
            "The transition from acute to chronic pain involves central sensitization — amplification "
            "of pain signals within the CNS — making neuromodulation particularly relevant. tDCS "
            "targeting M1 (motor cortex anodal — analgesic mechanism) and left DLPFC (emotional "
            "and cognitive aspects of pain) has the strongest evidence base among non-invasive "
            "neuromodulation for chronic pain. Fregni et al. (2006, Arthritis & Rheumatism) "
            "demonstrated significant pain reduction in fibromyalgia with M1 anodal tDCS in an RCT. "
            "CES (Alpha-Stim) provides complementary mood, anxiety, and sleep support."
        ),

        pathophysiology=(
            "Chronic pain involves central sensitization: amplification of nociceptive signals at "
            "spinal and supraspinal levels. Key mechanisms include: (1) Wind-up and long-term "
            "potentiation of dorsal horn neurons; (2) Descending facilitation from brainstem "
            "(rostroventromedial medulla — RVM); (3) Reduced descending inhibition (opioidergic, "
            "serotonergic, noradrenergic pathways); (4) Cortical reorganization — expansion of "
            "pain representations in S1 and motor cortex.\n\n"
            "Fibromyalgia pathophysiology: central sensitization is the core mechanism. fMRI studies "
            "demonstrate enhanced activity in pain-processing regions (insula, SII, anterior cingulate) "
            "with reduced descending inhibitory capacity. Abnormal DMN connectivity, with the DMN "
            "failing to suppress pain-related networks during rest, propagates chronicity. "
            "Neuroinflammatory mechanisms and glial activation contribute.\n\n"
            "tDCS M1 anodal mechanism: increases motor cortex excitability, which inhibits pain via "
            "corticospinal activation of brainstem pain modulation circuits (periaqueductal gray, "
            "nucleus raphe magnus). This 'motor cortex stimulation analgesia' mechanism is well-"
            "established from invasive MCS (motor cortex stimulation) studies."
        ),

        core_symptoms=[
            "Widespread chronic pain — diffuse, often migratory (fibromyalgia)",
            "Fatigue — disproportionate, not relieved by rest",
            "Sleep disturbance — non-restorative sleep, morning stiffness",
            "Tender points / allodynia (fibromyalgia)",
            "Hyperalgesia — amplified pain response to normally painful stimuli",
            "Cognitive difficulties — fibro-fog (attention, memory, processing speed)",
        ],

        non_motor_symptoms=[
            "Depression (comorbid in 40-50% of fibromyalgia patients)",
            "Anxiety (comorbid in 50-60%)",
            "Headache (tension and migraine-type)",
            "Irritable bowel syndrome (comorbid visceral sensitization)",
            "Reduced quality of life and social/occupational function",
        ],

        key_brain_regions=[
            "Primary Motor Cortex (M1)",
            "Primary Somatosensory Cortex (S1)",
            "Anterior Cingulate Cortex (ACC) / dACC",
            "Anterior Insula",
            "Periaqueductal Gray (PAG)",
            "Dorsolateral Prefrontal Cortex (DLPFC)",
        ],

        brain_region_descriptions={
            "Primary Motor Cortex (M1)": "Primary tDCS anodal target for analgesia. M1 anodal stimulation activates corticospinal-brainstem pain modulation circuits (PAG, RVM). Invasive MCS evidence extrapolated to non-invasive tDCS.",
            "Primary Somatosensory Cortex (S1)": "Hyperactivated in chronic pain — enhanced representation of body pain maps. Central sensitization expresses as cortical reorganization in S1.",
            "Anterior Cingulate Cortex (ACC) / dACC": "Affective-motivational component of pain. ACC hyperactivation drives the aversive emotional aspects of chronic pain. Connected to DLPFC via pain regulation circuits.",
            "Anterior Insula": "Key SN node; interoceptive processing and pain salience. Hyperactive in fibromyalgia. Bilateral anterior insula hyperactivation is a robust FMS neuroimaging finding.",
            "Periaqueductal Gray (PAG)": "Brainstem pain modulation hub. Reduced PAG-frontal connectivity in chronic pain impairs descending inhibition. M1 tDCS may activate this pathway.",
            "Dorsolateral Prefrontal Cortex (DLPFC)": "Cognitive-evaluative pain component, emotion regulation, and mood. DLPFC anodal tDCS targets depression and catastrophizing that amplify pain experience.",
        },

        network_profiles=[
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN CHRONIC PAIN. Salience Network hyperactivation — particularly "
                "anterior insula and dACC — drives aberrant pain salience, emotional amplification "
                "of nociception, and catastrophizing. SN hyperactivity is the most consistent "
                "neuroimaging finding in fibromyalgia. M1 tDCS analgesia works partly via SN modulation.",
                primary=True, severity="severe",
                evidence_note="Multiple fMRI studies in FMS; Napadow et al. — FMS brain connectivity",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation contributes to pain rumination, catastrophizing, and intrusive "
                "pain-related ideation. Reduced anticorrelation between DMN and anti-correlated network "
                "in fibromyalgia. DLPFC tDCS may reduce DMN-mediated pain rumination.",
                severity="severe",
                evidence_note="Altered DMN connectivity in FMS; Napadow et al. 2010 — DMN-pain relationship",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "High comorbidity of depression (40-50%) and anxiety (50-60%) in fibromyalgia reflects "
                "limbic hyperreactivity. HPA axis dysregulation amplifies pain and emotional processing. "
                "Amygdala hyperactivity drives affective pain component.",
                severity="severe",
                evidence_note="FMS-depression-anxiety triad; shared neurobiological mechanisms",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "CEN hypofunction impairs top-down pain inhibitory control, cognitive coping strategies, "
                "and emotional regulation of pain experience. Reduced prefrontal activity allows limbic "
                "and SN hyperactivity to dominate pain experience.",
                severity="moderate",
            ),
        ],

        primary_network=NetworkKey.SN,

        fnon_rationale=(
            "In chronic pain/fibromyalgia, the primary dysfunctional networks are the Salience Network "
            "(hyperactive — pain amplification) and the Limbic Network (hyperactive — affective pain "
            "component). The FNON framework deploys two parallel strategies: (1) M1 anodal tDCS for "
            "direct analgesic effect via corticospinal-brainstem pain modulation pathways; (2) Left DLPFC "
            "anodal tDCS to upregulate CEN pain inhibitory control and address comorbid depression. "
            "CES addresses sleep, anxiety, and mood via limbic modulation."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="fms",
                label="FMS — Fibromyalgia Syndrome",
                description="Widespread chronic musculoskeletal pain with tender points, fatigue, and sleep disturbance meeting ACR 2010 fibromyalgia criteria. Central sensitization dominant.",
                key_features=["Widespread pain", "Tender points/pressure hyperalgesia", "Fatigue", "Non-restorative sleep", "Fibro-fog"],
                primary_networks=[NetworkKey.SN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.LIMBIC, NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.CES],
                tdcs_target="M1 anodal bilateral (C3+C4) — primary analgesic protocol",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="clbp",
                label="CLBP — Chronic Low Back Pain",
                description="Chronic persistent low back pain (>3 months) with or without radiculopathy. Mixed nociceptive and central sensitization components.",
                key_features=["Low back pain", "Pain radiation", "Mobility limitation", "Sleep impairment", "Disability"],
                primary_networks=[NetworkKey.SN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.CES],
                tdcs_target="M1 anodal (C3 or C4) — contralateral to dominant pain side",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="cs",
                label="CS — Central Sensitization Syndrome",
                description="Chronic pain with prominent central sensitization features: allodynia, hyperalgesia, diffuse body pain, comorbid fatigue and sleep disturbance.",
                key_features=["Allodynia", "Hyperalgesia", "Diffuse pain", "Sensory hypersensitivity", "Comorbid fatigue"],
                primary_networks=[NetworkKey.SN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="M1 anodal + left DLPFC anodal — combined protocol",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="pain_dep",
                label="PAIN-DEP — Chronic Pain with Comorbid Depression",
                description="Chronic pain syndrome with clinically significant comorbid major depression. Limbic-frontal-pain circuit triad.",
                key_features=["Chronic pain", "Depression (PHQ-9 >=10)", "Catastrophizing", "Sleep disturbance", "Reduced quality of life"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                secondary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal (depression) + M1 anodal (pain) — sequential or alternating",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="fiqr",
                name="Revised Fibromyalgia Impact Questionnaire",
                abbreviation="FIQR",
                domains=["pain", "fatigue", "sleep", "physical_function", "stiffness", "anxiety", "depression"],
                timing="baseline",
                evidence_pmid="19604474",
                notes="Primary FMS outcome measure. Score /100. MCID = 14%. Administer at baseline and endpoint.",
            ),
            AssessmentTool(
                scale_key="nrs",
                name="Numeric Rating Scale — Pain Intensity",
                abbreviation="NRS",
                domains=["pain_intensity"],
                timing="baseline",
                evidence_pmid="9334591",
                notes="Primary pain intensity monitoring. 0-10 scale. Administer at every session for pain tracking.",
            ),
            AssessmentTool(
                scale_key="bpi",
                name="Brief Pain Inventory",
                abbreviation="BPI",
                domains=["pain_severity", "pain_interference", "location", "quality"],
                timing="baseline",
                evidence_pmid="10322439",
                notes="Comprehensive pain assessment. Pain severity (0-10) and interference subscales. Standard research tool.",
            ),
            AssessmentTool(
                scale_key="psqi",
                name="Pittsburgh Sleep Quality Index",
                abbreviation="PSQI",
                domains=["sleep_quality", "sleep_latency", "sleep_duration", "sleep_disturbance"],
                timing="baseline",
                evidence_pmid="2748771",
                notes="Critical in fibromyalgia — sleep disturbance both drives and is driven by pain. Score >5 = poor sleep.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Depression comorbidity screen. Score >=10 = moderate depression. Mandatory for pain-depression subtype.",
            ),
            AssessmentTool(
                scale_key="dass21",
                name="Depression Anxiety Stress Scale — 21 item",
                abbreviation="DASS-21",
                domains=["depression", "anxiety", "stress"],
                timing="baseline",
                evidence_pmid="9880876",
                notes="Comprehensive mood screen for chronic pain — captures depression, anxiety, and stress triad.",
            ),
        ],

        baseline_measures=[
            "FIQR (fibromyalgia — primary disease-specific measure)",
            "NRS pain intensity (0-10, at every session)",
            "BPI (comprehensive pain assessment — baseline and endpoint)",
            "PSQI (sleep quality)",
            "PHQ-9 and DASS-21 (mood and anxiety comorbidity)",
            "SOZO PRS (pain, fatigue, mood, sleep, function — 0-10)",
        ],

        followup_measures=[
            "NRS pain at every session (session-level monitoring)",
            "FIQR at Week 4 and Week 8-10",
            "BPI at Week 8-10",
            "PHQ-9 at each session (mood monitoring)",
            "PSQI at Week 4 and Week 8-10",
            "SOZO PRS at each session and end of block",
        ],

        inclusion_criteria=[
            "Confirmed diagnosis of fibromyalgia (ACR 2010/2016 criteria) OR chronic pain >3 months",
            "NRS average pain >=4/10",
            "Age 18-70 years",
            "Stable analgesic medication for >=4 weeks (or medication-naive)",
            "Capacity to provide informed consent",
            "Adequate skin integrity at electrode placement sites",
        ],

        exclusion_criteria=[
            "Active inflammatory arthritis or pain with identifiable surgical cause requiring primary surgical treatment",
            "Active malignancy or cancer-related pain",
            "Severe psychiatric disorder (psychosis, active suicidality) as primary diagnosis",
            "Uncontrolled seizure disorder",
            "Pregnancy",
            "Active substance use disorder",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS,

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "monitoring",
                "Monitor pain VAS/NRS at start and end of each session. Transient pain increase after first 1-2 sessions can occur (sensitized cortex). If pain worsening persists beyond 3 sessions, reduce intensity to 1.5 mA and reassess.",
                "moderate",
                "Clinical experience in chronic pain tDCS; sensitized cortex response",
            ),
            make_safety(
                "precaution",
                "Fibromyalgia patients commonly have medication polypharmacy (opioids, gabapentinoids, SNRIs, tricyclics). Document all analgesic medications and maintain stable regimen during treatment block to avoid confounding response assessment.",
                "moderate",
                "Pharmacological interaction and response assessment confounding",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Primary Motor Cortex", "M1", "bilateral",
                "M1 bilateral anodal tDCS is the primary analgesic protocol for fibromyalgia and chronic pain. "
                "Mechanism: activation of corticospinal tracts modulates brainstem pain-modulation circuits "
                "(PAG, RVM), enhancing descending inhibition. Fregni et al. (2006) RCT demonstrated "
                "significant pain reduction in fibromyalgia. IFCN guidelines endorse M1 tDCS for "
                "fibromyalgia (Level B probable evidence).",
                "C-PAIN-M1 — Motor Cortex Analgesic Protocol",
                EvidenceLevel.HIGH, off_label=True,
            ),
            make_tdcs_target(
                "Dorsolateral Prefrontal Cortex", "DLPFC", "left",
                "Left DLPFC anodal tDCS targets the cognitive-emotional pain matrix and comorbid depression. "
                "Reduces catastrophizing, improves pain coping, and addresses depressive symptoms that "
                "amplify pain experience. Evidence from MDD tDCS literature; limited chronic pain-specific data.",
                "C-PAIN-DLPFC — Cognitive Pain & Depression Protocol",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-PAIN-M1", label="M1 Analgesic — Fibromyalgia / Chronic Pain", modality=Modality.TDCS,
                target_region="Primary Motor Cortex (bilateral)", target_abbreviation="M1",
                phenotype_slugs=["fms", "clbp", "cs"],
                network_targets=[NetworkKey.SN, NetworkKey.DMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "C3 + C4 (bilateral M1) or C3 alone (left M1)",
                    "cathode": "Fp1 + Fp2 (bilateral supraorbital) or contralateral shoulder",
                    "intensity": "2.0 mA",
                    "duration": "20-30 min",
                    "sessions": "10-20 over 4-5 weeks",
                    "electrode_size": "35 cm2",
                    "note": "Fregni et al. montage: anode C3 (left M1), cathode right shoulder or Fp2",
                },
                rationale="M1 anodal tDCS activates descending pain inhibitory pathways via corticospinal-PAG "
                          "circuit, analogous to invasive motor cortex stimulation for pain. "
                          "Fregni et al. (2006) Arthritis & Rheumatism RCT (N=32): significant pain reduction "
                          "in fibromyalgia vs sham. Marlow et al. (2013) meta-analysis confirmed M1 tDCS "
                          "efficacy for chronic pain. IFCN Level B. OFF-LABEL.",
                evidence_level=EvidenceLevel.HIGH, off_label=True, session_count=20,
            ),
            ProtocolEntry(
                protocol_id="C-PAIN-DLPFC", label="Left DLPFC — Cognitive Pain & Depression", modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex", target_abbreviation="L-DLPFC",
                phenotype_slugs=["pain_dep", "cs"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN, NetworkKey.LIMBIC],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "Fp2 (right supraorbital)",
                    "intensity": "2.0 mA",
                    "duration": "30 min",
                    "sessions": "10-15",
                    "note": "MDD-adapted montage for pain with comorbid depression. Monitor PHQ-9 at every session.",
                },
                rationale="DLPFC anodal tDCS targets the cognitive-emotional pain matrix and comorbid "
                          "depression. Catastrophizing is a major amplifier of chronic pain — CEN upregulation "
                          "reduces catastrophizing and improves pain coping. Evidence from MDD tDCS extrapolated "
                          "to pain-depression comorbidity. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="CES-PAIN", label="Alpha-Stim CES — Sleep, Anxiety & Mood", modality=Modality.CES,
                target_region="Bilateral earlobe electrodes", target_abbreviation="CES",
                phenotype_slugs=["fms", "pain_dep", "cs"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim AID",
                    "frequency": "0.5 Hz",
                    "intensity": "100-300 uA",
                    "duration": "40-60 min",
                    "sessions": "Daily during treatment block",
                },
                rationale="Alpha-Stim CES FDA-cleared for anxiety, depression, and insomnia. In fibromyalgia, "
                          "addresses the highly prevalent triad of sleep disturbance, anxiety, and mood symptoms. "
                          "Sleep restoration reduces pain sensitization. Non-pharmacological — reduces medication burden. "
                          "Adjunct to tDCS pain protocols.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
            ),
            ProtocolEntry(
                protocol_id="TAVNS-PAIN", label="taVNS — Autonomic Pain Modulation Adjunct", modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve", target_abbreviation="taVNS",
                phenotype_slugs=["cs", "fms"],
                network_targets=[NetworkKey.SN, NetworkKey.LIMBIC],
                parameters={
                    "device": "NEMOS (tVNS Technologies) or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "250 us",
                    "intensity": "Below pain threshold",
                    "duration": "30 min",
                    "sessions": "Daily adjunct",
                    "electrode_placement": "Left cymba conchae",
                },
                rationale="taVNS modulates pain processing via NTS-brain stem connections and enhanced "
                          "descending inhibition through noradrenergic and serotonergic pathways. "
                          "Reduces autonomic hyperreactivity contributing to central sensitization. "
                          "Investigational for chronic pain — rationale from pain modulation literature.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=20,
                notes="Investigational for chronic pain. Adjunct only. Limited published data.",
            ),
        ],

        symptom_network_mapping={
            "Chronic Pain / Widespread Pain": [NetworkKey.SN, NetworkKey.DMN],
            "Fatigue": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Sleep Disturbance": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Depression": [NetworkKey.LIMBIC, NetworkKey.CEN],
            "Anxiety / Catastrophizing": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Fibro-fog / Cognitive": [NetworkKey.CEN, NetworkKey.DMN],
        },

        symptom_modality_mapping={
            "Chronic Pain / Widespread Pain": [Modality.TDCS],
            "Fatigue": [Modality.CES, Modality.TAVNS],
            "Sleep Disturbance": [Modality.CES],
            "Depression": [Modality.TDCS, Modality.CES, Modality.TAVNS],
            "Anxiety / Catastrophizing": [Modality.CES, Modality.TAVNS, Modality.TDCS],
            "Fibro-fog / Cognitive": [Modality.TDCS],
        },

        responder_criteria=[
            ">=30% reduction in NRS average pain from baseline (IMMPACT minimum clinically important difference)",
            ">=14% reduction in FIQR total score (fibromyalgia MCID)",
            "Clinically meaningful SOZO PRS pain and fatigue domain improvement (>=3 points)",
            "PHQ-9 >=50% reduction (pain-depression subtype)",
        ],

        non_responder_pathway=(
            "For non-responders at Week 4:\n"
            "1. Assess and optimize sleep — untreated insomnia severely limits pain neuromodulation response\n"
            "2. Review medication stability — analgesic changes during treatment confound response\n"
            "3. Switch from DLPFC to M1 protocol (or vice versa) based on pain vs mood dominance\n"
            "4. Add CES for sleep and anxiety components if not already prescribed\n"
            "5. Extend to 20-session block if partial responder\n"
            "6. Screen for comorbid depression — undertreated depression amplifies pain\n"
            "7. Multidisciplinary pain review — confirm absence of treatable peripheral pain generator\n"
            "8. Doctor review for psychological pain management (CBT, ACT) adjunct"
        ),

        evidence_summary=(
            "Chronic pain / fibromyalgia has the second-strongest tDCS evidence base (after stroke). "
            "M1 anodal tDCS: IFCN Level B (probable) for fibromyalgia. Fregni et al. (2006) seminal RCT. "
            "Marlow et al. (2013) meta-analysis confirms pain efficacy. Multiple subsequent positive trials. "
            "DLPFC tDCS for pain: moderate evidence — partially from MDD extrapolation. "
            "CES: FDA-cleared for anxiety, depression, insomnia — directly addressing FMS comorbidities. "
            "taVNS: investigational — limited pain-specific data."
        ),

        evidence_gaps=[
            "Long-term pain relief beyond treatment block — limited follow-up data (>3 months)",
            "Head-to-head comparison of M1 vs DLPFC vs combined montages for fibromyalgia",
            "Predictors of tDCS response for chronic pain — phenotypic, psychological, or genetic markers",
            "Optimal session parameters (number, frequency, intensity) for chronic pain",
            "taVNS for chronic pain — no dedicated fibromyalgia RCT",
        ],

        references=[
            {
                "authors": "Fregni F et al.",
                "year": 2006,
                "title": "A randomized, sham-controlled, proof of principle study of transcranial direct current stimulation for the treatment of pain in fibromyalgia",
                "journal": "Arthritis & Rheumatism",
                "pmid": "16799965",
                "evidence_type": "rct",
            },
            {
                "authors": "Marlow NM et al.",
                "year": 2013,
                "title": "Transcranial direct current stimulation for the management of chronic pain: a systematic review",
                "journal": "Neuromodulation",
                "pmid": "23590951",
                "evidence_type": "systematic_review",
            },
            {
                "authors": "Lefaucheur JP et al.",
                "year": 2017,
                "title": "Evidence-based guidelines on the therapeutic use of transcranial direct current stimulation (tDCS)",
                "journal": "Clinical Neurophysiology",
                "pmid": "27866120",
                "evidence_type": "clinical_practice_guideline",
            },
            {
                "authors": "Knotkova H et al.",
                "year": 2017,
                "title": "Bi-cephalic transcranial direct current stimulation for fibromyalgia",
                "journal": "Clinical Journal of Pain",
                "pmid": "28009763",
                "evidence_type": "rct",
            },
        ],

        overall_evidence_quality=EvidenceLevel.HIGH,

        clinical_tips=[
            "Prioritize M1 bilateral anodal protocol for primary pain reduction — this has the strongest evidence",
            "Add left DLPFC anodal protocol for patients with significant depression or catastrophizing component",
            "Prescribe CES for home use to address sleep disturbance — sleep optimization markedly improves pain treatment response",
            "Monitor NRS pain at every session — document pain trajectory for outcome tracking and responder classification",
            "Reassure patients that initial sessions may not show immediate pain reduction — cumulative effects typically emerge at Week 3-4",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES,
    )
