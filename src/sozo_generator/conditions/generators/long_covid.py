"""
Long COVID / Post-Acute Sequelae SARS-CoV-2 (PASC) — Complete condition generator.

Key references:
- Taquet M et al. (2021) 6-month neurological and psychiatric outcomes in 236,379 survivors — The Lancet Psychiatry. PMID: 33836148
- Fernandez-de-las-Penas C et al. (2021) Prevalence of post-COVID-19 symptoms — Journal of Infection. PMID: 34023307
- Sollini M et al. (2021) Brain imaging in long COVID — Journal of Nuclear Medicine. PMID: 34362823
- Chalder T et al. (1993) Development of a fatigue scale — Journal of Psychosomatic Research. PMID: 8463991

NOTE: Long COVID is a new condition with rapidly evolving evidence. Most neuromodulation evidence is from
case series and small pilot studies as of 2024-2026. Clinical teams should monitor the literature actively.
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


def build_long_covid_condition() -> ConditionSchema:
    """Build the complete Long COVID / PASC condition schema."""
    return ConditionSchema(
        slug="long_covid",
        display_name="Long COVID / Post-Acute Sequelae SARS-CoV-2",
        icd10="U09.9",
        aliases=["Long COVID", "PASC", "post-COVID", "post-COVID-19", "post-acute COVID", "COVID brain fog"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Long COVID (Post-Acute Sequelae SARS-CoV-2, PASC) describes a range of persistent "
            "symptoms lasting beyond 4-12 weeks after acute SARS-CoV-2 infection, not explained by "
            "an alternative diagnosis. Estimated prevalence is 10-30% of COVID-19 survivors. The most "
            "prevalent and disabling symptoms include: brain fog/cognitive impairment, fatigue, "
            "dyspnea, post-exertional malaise (PEM), sleep disturbance, and dysautonomia.\n\n"
            "Neurological manifestations affect 30-80% of long COVID patients. Taquet et al. (2021, "
            "Lancet Psychiatry) documented 6-month neurological and psychiatric sequelae in 236,379 "
            "COVID-19 survivors. Neuroimaging studies (FDG-PET, MRI) reveal widespread metabolic "
            "hypometabolism in frontal-parietal regions consistent with CEN hypofunction.\n\n"
            "IMPORTANT: Long COVID is a new condition (2020-present) with rapidly evolving evidence. "
            "Neuromodulation evidence is limited to case series and small pilot studies. "
            "Clinical approach should be cautious, individualized, and involve treating physician."
        ),

        pathophysiology=(
            "Long COVID pathophysiology is multifactorial and incompletely understood. Proposed "
            "mechanisms include:\n\n"
            "(1) Persistent viral reservoir/antigen: SARS-CoV-2 RNA detected in GI tract, lymph nodes, "
            "and potentially CNS months after acute infection — driving ongoing immune activation.\n\n"
            "(2) Neuroinflammation: microglial activation and neuroinflammatory mediators (IL-6, "
            "TNF-alpha, IL-1beta) documented in CNS via CSF and PET studies. Similar pattern to "
            "post-infectious encephalitis.\n\n"
            "(3) Autonomic dysregulation (dysautonomia): autonomic nervous system dysfunction produces "
            "POTS (postural orthostatic tachycardia), orthostatic intolerance, and impaired HRV. "
            "Small fiber neuropathy documented in subset.\n\n"
            "(4) Vascular endothelial dysfunction: persistent micro-thrombi and endothelial damage "
            "impair cerebral microvascular perfusion, contributing to cognitive symptoms.\n\n"
            "(5) Mitochondrial dysfunction and bioenergetic failure: impaired cellular energy production "
            "drives the disproportionate post-exertional fatigue and exercise intolerance.\n\n"
            "(6) Immune dysregulation: T-cell exhaustion, NK cell dysfunction, B-cell and antibody "
            "abnormalities, and autoantibody formation (ACE2, beta-adrenergic receptor antibodies) "
            "documented in long COVID."
        ),

        core_symptoms=[
            "Brain fog — cognitive slowing, memory difficulties, concentration impairment",
            "Post-exertional malaise (PEM) — symptom worsening after physical or cognitive exertion",
            "Fatigue — disproportionate, not relieved by rest",
            "Dyspnea — breathlessness at rest or on exertion",
            "Sleep disturbance — insomnia, hypersomnia, non-restorative sleep",
            "Headache",
            "Sensory changes — tinnitus, parosmia, taste disturbance",
        ],

        non_motor_symptoms=[
            "Depression and anxiety (highly prevalent)",
            "PTSD-like symptoms from acute COVID hospitalization (ICU patients)",
            "Dysautonomia / POTS — orthostatic intolerance, palpitations, sweating",
            "Chest pain and cardiac symptoms",
            "GI symptoms (nausea, diarrhea, dyspepsia)",
            "Pain hypersensitivity and fibromyalgia-like features",
        ],

        key_brain_regions=[
            "Dorsolateral Prefrontal Cortex (DLPFC)",
            "Anterior Cingulate Cortex (ACC)",
            "Thalamus",
            "Hippocampus",
            "Olfactory Bulb",
            "Brainstem",
        ],

        brain_region_descriptions={
            "Dorsolateral Prefrontal Cortex (DLPFC)": "FDG-PET and fMRI hypometabolism in frontal regions correlates with brain fog and cognitive impairment. Primary tDCS target for long COVID cognitive rehabilitation.",
            "Anterior Cingulate Cortex (ACC)": "ACC hypometabolism documented in long COVID imaging. Contributes to fatigue, motivational impairment, and attention dysfunction.",
            "Thalamus": "Thalamic hypometabolism documented in long COVID FDG-PET. Thalamo-cortical connectivity disruption drives fatigue and cognitive impairment.",
            "Hippocampus": "Potential direct SARS-CoV-2 neurotropism via ACE2 receptors in hippocampus. Contributes to memory impairment. Stress-induced hippocampal volume loss from prolonged illness.",
            "Olfactory Bulb": "Direct SARS-CoV-2 infection and olfactory epithelium degeneration — explains parosmia/anosmia. Potential central spread via olfactory pathway.",
            "Brainstem": "Brainstem involvement in SARS-CoV-2 — autonomic dysregulation, autonomic reflex abnormalities, and cardiorespiratory symptoms may reflect brainstem pathology.",
        },

        network_profiles=[
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN LONG COVID BRAIN FOG. DMN hyperactivation and failure to suppress "
                "during cognitive demands drives brain fog, mental fatigue, and intrusive thoughts. "
                "Abnormal DMN-CEN anticorrelation parallels ADHD, TBI, and MDD patterns. "
                "DMN hyperactivation correlates with cognitive symptom severity.",
                primary=True, severity="severe",
                evidence_note="Long COVID neuroimaging studies; resting-state fMRI in PASC",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "CEN hypofunction correlates with brain fog severity. FDG-PET hypometabolism in "
                "frontal-parietal regions — particularly DLPFC — is among the most consistent "
                "neuroimaging findings in long COVID. DLPFC anodal tDCS is the primary cognitive "
                "rehabilitation target.",
                severity="severe",
                evidence_note="Frontal-parietal hypometabolism in long COVID PET studies",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "SN hyperactivation drives dysautonomia, interoceptive hypersensitivity, and fatigue "
                "in long COVID. Anterior insula hyperactivation may contribute to bodily symptom "
                "amplification. taVNS targets vagal-SN modulation for autonomic regulation.",
                severity="moderate-severe",
                evidence_note="Autonomic dysregulation (dysautonomia/POTS) prevalent in long COVID",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Sustained and divided attention deficits are core brain fog complaints. Attention "
                "network hypofunction parallels TBI and ADHD patterns. Correlates with occupational "
                "disability and return-to-work barriers.",
                severity="severe",
                evidence_note="Neuropsychological testing in long COVID; attention deficits documented",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "High prevalence of depression, anxiety, and PTSD-like symptoms in long COVID. "
                "Neuroinflammatory mediators directly modulate limbic circuits. Illness-related "
                "psychological distress amplifies limbic hyperactivity. HPA axis dysregulation.",
                severity="moderate",
                evidence_note="Psychiatric sequelae of long COVID; Taquet et al. 2021",
            ),
        ],

        primary_network=NetworkKey.DMN,

        fnon_rationale=(
            "In long COVID, the primary neurological mechanism is brain fog — driven by CEN hypofunction "
            "(frontal-parietal hypometabolism) and DMN hyperactivation, paralleling TBI and ADHD "
            "network patterns. The FNON framework targets left DLPFC anodal tDCS to upregulate CEN "
            "and restore CEN-DMN anticorrelation. taVNS addresses dysautonomia and autonomic "
            "hyperarousal via vagal-NTS-mediated autonomic regulation. CES addresses comorbid "
            "sleep disturbance and mood symptoms."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="brain_fog",
                label="BRAIN-FOG — Cognitive / Brain Fog Dominant",
                description="Dominant cognitive symptoms: brain fog, memory difficulties, processing speed impairment, word-finding difficulties. Most common long COVID neuromodulation presentation.",
                key_features=["Brain fog", "Memory difficulties", "Slowed processing", "Word-finding problems", "Cognitive fatigue"],
                primary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.ATTENTION, NetworkKey.SN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal (F3) — cognitive rehabilitation protocol",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="fatigue",
                label="FATIGUE — Fatigue-Dominant",
                description="Severe post-exertional malaise and fatigue as primary burden. Disproportionate exhaustion after minimal exertion. Similar to myalgic encephalomyelitis/chronic fatigue syndrome (ME/CFS) presentation.",
                key_features=["Post-exertional malaise", "Disproportionate fatigue", "Not relieved by rest", "Exercise intolerance", "Reduced activity"],
                primary_networks=[NetworkKey.SN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.LIMBIC, NetworkKey.DMN],
                preferred_modalities=[Modality.CES, Modality.TAVNS, Modality.TDCS],
                tdcs_target="Left DLPFC anodal — low-intensity protocol. IMPORTANT: avoid exertion models during stimulation in PEM-prone patients",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="dysauto",
                label="DYSAUTO — Dysautonomia / POTS",
                description="Autonomic nervous system dysregulation — POTS (postural orthostatic tachycardia), orthostatic intolerance, palpitations, sweating. taVNS primary modality.",
                key_features=["Orthostatic intolerance", "POTS", "Palpitations", "Dizziness on standing", "Heat intolerance"],
                primary_networks=[NetworkKey.SN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TAVNS, Modality.CES],
                tdcs_target="Adjunct DLPFC if cognitive symptoms present",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="mixed_lc",
                label="MIXED-LC — Mixed Neurological Long COVID",
                description="Multiple concurrent long COVID symptom domains: cognitive, fatigue, autonomic, and mood. Most complex presentation requiring multi-modal approach.",
                key_features=["Brain fog", "Fatigue", "Autonomic symptoms", "Mood changes", "Sleep disturbance"],
                primary_networks=[NetworkKey.DMN, NetworkKey.SN],
                secondary_networks=[NetworkKey.CEN, NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.TAVNS, Modality.CES],
                tdcs_target="Left DLPFC anodal for cognitive and mood symptoms",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="mh_lc",
                label="MH-LC — Mental Health Long COVID",
                description="Long COVID with dominant depression, anxiety, or PTSD-like features from acute illness trauma.",
                key_features=["Depression", "Anxiety", "Sleep disturbance", "PTSD-like symptoms (ICU survivors)", "Social withdrawal"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.DMN],
                secondary_networks=[NetworkKey.SN, NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal — MDD protocol adapted for long COVID depression",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="moca",
                name="Montreal Cognitive Assessment",
                abbreviation="MoCA",
                domains=["cognition", "memory", "attention", "executive_function"],
                timing="baseline",
                evidence_pmid="15817019",
                notes="Primary cognitive screen. Score <26 = possible impairment. Useful for tracking brain fog trajectory.",
            ),
            AssessmentTool(
                scale_key="fss",
                name="Fatigue Severity Scale",
                abbreviation="FSS",
                domains=["fatigue_severity", "fatigue_impact"],
                timing="baseline",
                evidence_pmid="2803071",
                notes="Primary fatigue measure in long COVID. Score >=36 = clinically significant fatigue.",
            ),
            AssessmentTool(
                scale_key="cfq11",
                name="Chalder Fatigue Questionnaire — 11 item",
                abbreviation="CFQ-11",
                domains=["physical_fatigue", "mental_fatigue"],
                timing="baseline",
                evidence_pmid="8463991",
                notes="Validated fatigue scale used extensively in long COVID research. Bimodal scoring. Widely used in long COVID clinical trials.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Depression monitoring — highly prevalent in long COVID.",
            ),
            AssessmentTool(
                scale_key="psqi",
                name="Pittsburgh Sleep Quality Index",
                abbreviation="PSQI",
                domains=["sleep_quality", "sleep_latency", "sleep_duration"],
                timing="baseline",
                evidence_pmid="2748771",
                notes="Sleep disturbance monitoring — prevalent in long COVID. Score >5 = poor sleep quality.",
            ),
            AssessmentTool(
                scale_key="gad7",
                name="Generalized Anxiety Disorder 7-item Scale",
                abbreviation="GAD-7",
                domains=["anxiety", "worry"],
                timing="baseline",
                evidence_pmid="16717171",
                notes="Anxiety comorbidity monitoring in long COVID.",
            ),
        ],

        baseline_measures=[
            "MoCA (primary cognitive screen)",
            "FSS (fatigue severity)",
            "CFQ-11 (Chalder Fatigue Questionnaire — long COVID fatigue research measure)",
            "PHQ-9 (depression)",
            "GAD-7 (anxiety)",
            "PSQI (sleep quality)",
            "SOZO PRS (cognitive, fatigue, mood, sleep, pain — 0-10)",
            "Vital signs including orthostatic blood pressure and heart rate (POTS screening)",
        ],

        followup_measures=[
            "MoCA at Week 8-10",
            "FSS and CFQ-11 at Week 4 and Week 8-10",
            "PHQ-9 at every session",
            "SOZO PRS at each session and end of block",
            "Adverse event documentation — post-exertional malaise monitoring at every session",
        ],

        inclusion_criteria=[
            "Confirmed or probable COVID-19 (PCR, antigen, or clinical diagnosis) with persistent symptoms >12 weeks",
            "Symptoms not explained by alternative diagnosis",
            "Age 18-70 years",
            "Capacity to provide informed consent",
            "Medically stable — no active acute COVID-19 or severe organ dysfunction",
            "Treating physician aware of and supportive of neuromodulation trial",
        ],

        exclusion_criteria=[
            "Active acute COVID-19 infection",
            "Severe cardiorespiratory long COVID complications (active heart failure, severe pulmonary fibrosis)",
            "Active thrombotic complications from COVID-19",
            "Severe myalgic encephalomyelitis/CFS (bedbound) — insufficient capacity for sessions",
            "Active psychiatric crisis",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS,

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "precaution",
                "POST-EXERTIONAL MALAISE (PEM): Monitor carefully for symptom worsening in the 12-48 hours following sessions. PEM is a characteristic long COVID feature. If PEM is triggered, reduce session duration (start with 15 min tDCS) and intensity (1.5 mA) and avoid concurrent cognitive tasks that increase exertion.",
                "high",
                "PEM is a defining long COVID feature; exertion-based protocols must be adapted",
            ),
            make_safety(
                "precaution",
                "DYSAUTONOMIA MONITORING: Measure sitting and standing blood pressure and heart rate before each session (POTS screening). Patients with orthostatic hypotension should remain seated or supine during stimulation. Avoid prolonged standing immediately after sessions.",
                "moderate",
                "POTS and dysautonomia in long COVID — safety monitoring for hypotension",
            ),
            make_safety(
                "monitoring",
                "Long COVID is a new condition — monitor for any unexpected adverse effects and report to treating physician. This is an evolving clinical field; case observations should inform clinical practice development.",
                "moderate",
                "New condition — ongoing clinical observation required",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Dorsolateral Prefrontal Cortex", "DLPFC", "left",
                "Left DLPFC anodal tDCS targets CEN hypofunction — the primary neurological mechanism "
                "of long COVID brain fog. Rationale extrapolated from TBI, ADHD, and MDD tDCS evidence "
                "(same CEN hypofunction pattern). No dedicated long COVID tDCS RCT as of 2024. "
                "Case series and pilot evidence emerging.",
                "C-LC-COG — Cognitive Brain Fog Protocol",
                EvidenceLevel.LOW, off_label=True,
            ),
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve",
                target_abbreviation="taVNS",
                laterality="left",
                rationale="taVNS modulates autonomic nervous system via NTS-mediated vagal pathways. "
                          "In long COVID dysautonomia, taVNS may restore vagal tone, improve HRV, and "
                          "reduce POTS-related orthostatic intolerance. Also modulates neuroinflammatory "
                          "pathways (VNS anti-inflammatory effect via spleen). Investigational.",
                protocol_label="TAVNS-LC — Autonomic Regulation Protocol",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-LC-COG", label="Cognitive Brain Fog — DLPFC tDCS", modality=Modality.TDCS,
                target_region="Dorsolateral Prefrontal Cortex", target_abbreviation="DLPFC",
                phenotype_slugs=["brain_fog", "mixed_lc"],
                network_targets=[NetworkKey.CEN, NetworkKey.ATTENTION],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC) or F3+F4 bilateral",
                    "cathode": "Fp2 (right supraorbital) or right shoulder",
                    "intensity": "1.5-2.0 mA (start 1.5 mA; PEM-caution: no concurrent cognitive tasks initially)",
                    "duration": "15-20 min (start 15 min — PEM management)",
                    "sessions": "10-15 over 3-4 weeks",
                    "note": "Monitor for PEM 24-48h post-session. Avoid cognitive exertion during early sessions. Gradual protocol escalation.",
                },
                rationale="Left DLPFC anodal tDCS targets CEN hypofunction documented in long COVID "
                          "neuroimaging. Rationale extrapolated from TBI, ADHD, and fatigue tDCS evidence "
                          "with similar network pattern. No dedicated long COVID tDCS RCT published as of "
                          "2024. Emerging case series support feasibility. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                notes="Investigational for long COVID. Monitor PEM carefully. Gradual escalation protocol recommended.",
            ),
            ProtocolEntry(
                protocol_id="TAVNS-LC", label="taVNS — Autonomic & Dysautonomia Protocol", modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve", target_abbreviation="taVNS",
                phenotype_slugs=["dysauto", "fatigue", "mixed_lc"],
                network_targets=[NetworkKey.SN, NetworkKey.LIMBIC],
                parameters={
                    "device": "NEMOS (tVNS Technologies) or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "250 us",
                    "intensity": "Below pain threshold (0.5-3.0 mA)",
                    "duration": "30-60 min",
                    "sessions": "Daily during treatment block",
                    "electrode_placement": "Left cymba conchae",
                    "note": "Seated or supine position during stimulation. Monitor BP before session.",
                },
                rationale="taVNS restores vagal tone and autonomic regulation in long COVID dysautonomia. "
                          "Parasympathetic upregulation addresses POTS-related sympathetic hyperactivation. "
                          "VNS anti-inflammatory mechanism may reduce neuroinflammatory burden. "
                          "Investigational in long COVID — rationale from autonomic medicine literature.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=20,
                notes="Investigational. Dysautonomia patients must have BP checked before each session.",
            ),
            ProtocolEntry(
                protocol_id="CES-LC", label="CES — Sleep, Anxiety & Mood", modality=Modality.CES,
                target_region="Bilateral earlobe electrodes", target_abbreviation="CES",
                phenotype_slugs=["brain_fog", "mh_lc", "fatigue", "mixed_lc"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim AID",
                    "frequency": "0.5 Hz",
                    "intensity": "100-200 uA",
                    "duration": "40-60 min",
                    "sessions": "Daily during treatment block",
                },
                rationale="Alpha-Stim CES FDA-cleared for anxiety, depression, and insomnia — all highly "
                          "prevalent in long COVID. Addresses sleep disturbance (which worsens brain fog and fatigue), "
                          "anxiety, and mood symptoms. Non-pharmacological adjunct.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
            ),
        ],

        symptom_network_mapping={
            "Brain Fog": [NetworkKey.CEN, NetworkKey.DMN],
            "Fatigue / PEM": [NetworkKey.SN, NetworkKey.CEN],
            "Depression": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "Anxiety": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Sleep Disturbance": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Dysautonomia / POTS": [NetworkKey.SN],
            "Attention Deficit": [NetworkKey.CEN, NetworkKey.ATTENTION],
        },

        symptom_modality_mapping={
            "Brain Fog": [Modality.TDCS],
            "Fatigue / PEM": [Modality.CES, Modality.TAVNS],
            "Depression": [Modality.TDCS, Modality.CES],
            "Anxiety": [Modality.CES, Modality.TAVNS],
            "Sleep Disturbance": [Modality.CES],
            "Dysautonomia / POTS": [Modality.TAVNS],
            "Attention Deficit": [Modality.TDCS],
        },

        responder_criteria=[
            ">=30% reduction in CFQ-11 total score from baseline",
            "MoCA score improvement or stabilization",
            "Clinically meaningful SOZO PRS improvement (>=3 points) in primary symptom domains",
            "PHQ-9 >=50% reduction (mental health subtype)",
        ],

        non_responder_pathway=(
            "For non-responders at Week 4:\n"
            "1. Review PEM management — reduce session intensity if post-exertional worsening documented\n"
            "2. Optimize sleep with CES before escalating tDCS\n"
            "3. Add taVNS for dysautonomia and fatigue components\n"
            "4. Treating physician review — assess for treatable medical contributors\n"
            "5. Extend treatment block cautiously — avoid triggering PEM cycle\n"
            "6. Consider ME/CFS specialist referral if PEM-dominant presentation"
        ),

        evidence_summary=(
            "Long COVID neuromodulation has very limited evidence — this is an emerging field. "
            "Taquet et al. (2021) documented neurological sequelae at scale. Neuroimaging studies "
            "confirm frontal hypometabolism. tDCS for long COVID cognitive symptoms: emerging case "
            "series and pilot studies only — no published RCT as of 2024. taVNS for dysautonomia: "
            "investigational — rationale from autonomic medicine literature. CES: best-evidenced "
            "component via FDA clearance for comorbid symptoms."
        ),

        evidence_gaps=[
            "No published RCT of tDCS or any neuromodulation specifically for long COVID as of early 2024",
            "Most evidence from case series — selection bias and absence of control conditions",
            "Long-term outcomes and safety in long COVID population — entirely unknown",
            "Optimal dose and frequency in PEM-prone patients — risk of symptom exacerbation",
            "taVNS for long COVID dysautonomia/POTS — no published controlled data",
        ],

        references=[
            {
                "authors": "Taquet M et al.",
                "year": 2021,
                "title": "6-month neurological and psychiatric outcomes in 236,379 survivors of COVID-19",
                "journal": "The Lancet Psychiatry",
                "pmid": "33836148",
                "evidence_type": "cohort_study",
            },
            {
                "authors": "Fernandez-de-las-Penas C et al.",
                "year": 2021,
                "title": "Prevalence of post-COVID-19 symptoms in hospitalized and non-hospitalized COVID-19 survivors",
                "journal": "Journal of Infection",
                "pmid": "34023307",
                "evidence_type": "cohort_study",
            },
            {
                "authors": "Chalder T et al.",
                "year": 1993,
                "title": "Development of a fatigue scale",
                "journal": "Journal of Psychosomatic Research",
                "pmid": "8463991",
                "evidence_type": "cohort_study",
            },
        ],

        overall_evidence_quality=EvidenceLevel.LOW,

        clinical_tips=[
            "Post-exertional malaise (PEM) monitoring is critical — assess for symptom worsening 24-48h after each session",
            "Start with shorter, lower-intensity sessions (15 min, 1.5 mA) and escalate gradually based on tolerance",
            "Screen for POTS before every session — measure sitting and standing BP and HR",
            "Treating physician must be involved — long COVID is complex, multisystem, and rapidly evolving",
            "Inform patients this is investigational — limited evidence exists and outcomes are uncertain",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Treating physician coordination mandatory for long COVID cases",
            "Post-exertional malaise (PEM) monitoring protocol must be documented and followed",
            "Informed consent must acknowledge investigational status and evolving evidence",
        ],
    )
