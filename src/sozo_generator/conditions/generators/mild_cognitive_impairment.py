"""
Mild Cognitive Impairment (MCI) — Complete condition generator.

Key references:
- Ferrucci L et al. (2008) Subsystems contributing to the decline in ability to walk. PMID: 18227479
- Boggio PS et al. (2012) Non-invasive brain stimulation and MCI. PMID: 22169294
- Bystad M et al. (2016) tDCS as a memory enhancer in MCI patients. PMID: 27034021
- Petersen RC (2004) Mild cognitive impairment as a diagnostic entity. PMID: 15488477
- Nasreddine ZS et al. (2005) MoCA development and validation. PMID: 15817019
- Cotelli M et al. (2012) Transcranial direct current stimulation and memory. PMID: 22571658
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


def build_mild_cognitive_impairment_condition() -> ConditionSchema:
    """Build the complete Mild Cognitive Impairment condition schema."""
    return ConditionSchema(
        slug="mild_cognitive_impairment",
        display_name="Mild Cognitive Impairment",
        icd10="G31.84",
        aliases=["MCI", "amnestic MCI", "mild cognitive impairment"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Mild Cognitive Impairment (MCI) is a clinical syndrome characterized by cognitive "
            "decline greater than expected for an individual's age and education level, but not "
            "severe enough to interfere substantially with daily activities. MCI represents a "
            "critical transitional zone between normal aging and dementia, with an annual conversion "
            "rate to dementia of approximately 10-15% per year versus 1-2% in the general population.\n\n"
            "Prevalence in adults over 65 is estimated at 15-20%. The amnestic subtype — characterized "
            "by predominant memory impairment — most commonly progresses to Alzheimer's disease. "
            "Non-amnestic subtypes (language, visuospatial, executive) may progress to other dementias "
            "(frontotemporal, Lewy body, vascular).\n\n"
            "Neuromodulation in MCI aims to enhance synaptic plasticity and compensatory network "
            "recruitment before irreversible neurodegeneration occurs. tDCS targeting the DLPFC and "
            "parietal cortex has demonstrated working memory and episodic memory improvements. "
            "TPS targeting hippocampal-adjacent temporal structures represents a promising approach. "
            "TMS (repetitive, 10-20 Hz) over left DLPFC shows evidence for memory enhancement."
        ),

        pathophysiology=(
            "MCI pathophysiology reflects early-stage neurodegeneration affecting specific neural "
            "circuits before widespread neuronal loss:\n\n"
            "(1) Hippocampal neurodegeneration: In amnestic MCI, early amyloid-beta deposition and "
            "tau pathology in entorhinal cortex and hippocampus disrupt episodic memory consolidation "
            "and retrieval. Hippocampal volume loss is detectable on structural MRI.\n\n"
            "(2) Default Mode Network (DMN) disruption: The core memory encoding and consolidation "
            "network (hippocampus — posterior cingulate — precuneus — medial prefrontal cortex) "
            "shows early hypoconnectivity in amnestic MCI. This is a neuroimaging biomarker of "
            "MCI-to-AD progression risk.\n\n"
            "(3) Central Executive Network (CEN) hypoactivation: DLPFC-parietal circuit impairment "
            "reduces working memory capacity, executive function, and attentional control.\n\n"
            "(4) Cholinergic deficit: Basal forebrain cholinergic neurons (nucleus basalis of Meynert) "
            "degenerate early, reducing acetylcholine availability in hippocampus and cortex. "
            "This drives the memory and attentional deficits.\n\n"
            "(5) Compensatory hyperactivation: Some MCI patients show paradoxical hippocampal and "
            "prefrontal hyperactivation — reflecting compensatory recruitment of additional circuits "
            "to maintain cognitive performance. Neuromodulation may augment this compensation."
        ),

        core_symptoms=[
            "Memory complaints — episodic memory difficulty (names, appointments, recent events)",
            "Word-finding difficulty (anomia) — tip-of-the-tongue states",
            "Mild executive dysfunction — planning, organization, multitasking",
            "Preserved activities of daily living (ADLs) — distinguishes MCI from dementia",
            "Mild attention deficits — reduced concentration and mental tracking",
        ],

        non_motor_symptoms=[
            "Depression and anxiety (30-50% comorbid in MCI — increase dementia risk)",
            "Sleep disturbance — REM sleep behavior disorder in some MCI subtypes",
            "Apathy (20-40% — associated with faster progression to dementia)",
            "Mild personality changes",
        ],

        key_brain_regions=[
            "Hippocampus (bilateral)",
            "Entorhinal Cortex",
            "Dorsolateral Prefrontal Cortex (DLPFC)",
            "Posterior Cingulate Cortex / Precuneus",
            "Inferior Parietal Cortex (P3/P4)",
            "Nucleus Basalis of Meynert",
        ],

        brain_region_descriptions={
            "Hippocampus (bilateral)": "Primary site of amyloid-tau pathology in amnestic MCI. "
                "Episodic memory consolidation hub. Volume loss is a structural MRI biomarker. "
                "TPS can approximate hippocampal stimulation via temporal scalp positioning.",
            "Entorhinal Cortex": "Gateway for hippocampal-cortical communication. Early tau "
                "pathology impairs memory consolidation. Anatomically adjacent to temporal cortex.",
            "Dorsolateral Prefrontal Cortex (DLPFC)": "Working memory, executive function, "
                "cognitive control. Left DLPFC anodal tDCS improves working memory in MCI. "
                "F3/F4 EEG positions.",
            "Posterior Cingulate Cortex / Precuneus": "DMN hub; connectivity loss with hippocampus "
                "is an early MCI biomarker. Passive memory consolidation and self-referential processing.",
            "Inferior Parietal Cortex (P3/P4)": "Episodic memory retrieval, visuospatial cognition. "
                "tDCS target for memory enhancement in MCI.",
            "Nucleus Basalis of Meynert": "Cholinergic projection nucleus; degenerates early in MCI/AD. "
                "Source of acetylcholine to hippocampus and neocortex.",
        },

        network_profiles=[
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPO,
                "PRIMARY NETWORK IN MCI. DMN hypoconnectivity — particularly between hippocampus, "
                "posterior cingulate cortex, and medial prefrontal cortex — is the earliest and "
                "most consistent neuroimaging marker of amnestic MCI and prodromal AD. "
                "DMN disruption impairs episodic memory encoding, consolidation, and retrieval.",
                primary=True, severity="moderate-severe",
                evidence_note="Sorg et al. (2007); Greicius et al. (2004) — DMN in MCI/AD",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "CEN (DLPFC-parietal) hypoactivation drives working memory deficits, executive "
                "dysfunction, and reduced cognitive control in MCI. tDCS and TMS targeting DLPFC "
                "aim to upregulate CEN function.",
                severity="moderate",
                evidence_note="Rossi et al. (2020) — CEN in MCI",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Attention network hypoactivation contributes to concentration difficulties and "
                "reduced working memory capacity in MCI.",
                severity="mild-moderate",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Limbic network: comorbid depression and anxiety (30-50% in MCI) involve "
                "limbic hyperactivation. Depression independently predicts faster MCI-to-dementia "
                "progression. Addressing mood comorbidities is a treatment priority.",
                severity="moderate",
            ),
        ],

        primary_network=NetworkKey.DMN,

        fnon_rationale=(
            "In MCI, the primary intervention targets DMN and CEN deficits through multi-site "
            "stimulation: (1) Left DLPFC anodal tDCS to upregulate CEN/working memory; "
            "(2) Parietal cortex (P3) anodal tDCS to enhance episodic memory retrieval; "
            "(3) TPS targeting hippocampal-adjacent temporal structures to stimulate memory circuits "
            "inaccessible to surface tDCS; (4) TMS (10-20 Hz rTMS over L-DLPFC) to upregulate "
            "prefrontal-hippocampal connectivity. Combined with cognitive training (dual-n-back, "
            "memory encoding exercises) during stimulation for synergistic neuroplasticity."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="amnestic_single",
                label="aMCI-SINGLE — Amnestic MCI, Single Domain",
                description="Memory impairment only, with normal performance in other cognitive domains. Highest conversion risk to Alzheimer's disease.",
                key_features=["Episodic memory deficit", "Normal executive function", "Normal language", "ADLs preserved", "MoCA 19-25"],
                primary_networks=[NetworkKey.DMN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.TPS, Modality.TMS],
                tdcs_target="Left DLPFC anodal (F3) + parietal (P3) anodal",
                tps_target="Temporal/hippocampal-adjacent (T3/T5)",
            ),
            PhenotypeSubtype(
                slug="amnestic_multi",
                label="aMCI-MULTI — Amnestic MCI, Multiple Domain",
                description="Memory impairment plus deficit in at least one other cognitive domain. Higher progression risk. Often represents prodromal AD.",
                key_features=["Episodic + executive deficit", "Word-finding difficulty", "Possible visuospatial deficit", "MoCA 17-24"],
                primary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.TPS, Modality.TMS],
                tdcs_target="Left DLPFC anodal + bilateral parietal",
                tps_target="Temporal-parietal junction bilateral",
            ),
            PhenotypeSubtype(
                slug="nonamnestic",
                label="naMCI — Non-Amnestic MCI",
                description="Cognitive impairment without predominant memory deficit. Language, visuospatial, or executive domain affected. May progress to non-AD dementias.",
                key_features=["Executive or language deficit dominant", "Memory relatively preserved", "Variable MoCA score", "ADLs intact"],
                primary_networks=[NetworkKey.CEN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.TMS],
                tdcs_target="Left DLPFC anodal (F3) — executive/language focus",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="moca",
                name="Montreal Cognitive Assessment",
                abbreviation="MoCA",
                domains=["memory", "attention", "executive_function", "language", "visuospatial", "orientation"],
                timing="baseline",
                evidence_pmid="15817019",
                notes="Primary MCI screening and monitoring tool. 30-point scale. Score 18-25 typical for MCI. Score <18 suggests dementia range. MCID = 2 points. Administer at baseline and every 3 months.",
            ),
            AssessmentTool(
                scale_key="mmse",
                name="Mini-Mental State Examination",
                abbreviation="MMSE",
                domains=["orientation", "memory", "attention", "language", "visuospatial"],
                timing="baseline",
                evidence_pmid="1202204",
                notes="Well-established cognitive screen. 30-point scale. Score 24-27 typical for MCI. Less sensitive than MoCA for MCI detection.",
            ),
            AssessmentTool(
                scale_key="cdr_sb",
                name="Clinical Dementia Rating Sum of Boxes",
                abbreviation="CDR-SB",
                domains=["memory", "orientation", "judgment", "community_affairs", "home_hobbies", "personal_care"],
                timing="baseline",
                evidence_pmid="11450957",
                notes="CDR global 0.5 = MCI. CDR-SB 0.5-4.0 typical for MCI range. Tracks functional impact. Useful for documenting progression.",
            ),
            AssessmentTool(
                scale_key="adas_cog",
                name="Alzheimer's Disease Assessment Scale — Cognitive Subscale",
                abbreviation="ADAS-Cog",
                domains=["memory", "language", "praxis", "orientation"],
                timing="baseline",
                evidence_pmid="6883771",
                notes="Standard cognitive outcome measure in MCI/AD trials. 70-point scale. Higher = worse. MCID = 3-4 points. Useful for tracking change over treatment block.",
            ),
        ],

        baseline_measures=[
            "MoCA (Montreal Cognitive Assessment — primary cognitive screening)",
            "CDR-SB (Clinical Dementia Rating Sum of Boxes — functional staging)",
            "ADAS-Cog (if available — cognitive outcome tracking)",
            "PHQ-9 (depression comorbidity — 30-50% prevalence in MCI)",
            "SOZO PRS (memory complaints, mood, daily function — 0-10)",
        ],

        followup_measures=[
            "MoCA at every 4-week block",
            "SOZO PRS at each session",
            "CDR-SB at 3-month follow-up",
        ],

        inclusion_criteria=[
            "Subjective and objective cognitive complaint — verified by informant and neuropsychological testing",
            "Cognitive performance 1-1.5 SD below age/education norms in one or more domains",
            "Preserved activities of daily living",
            "No dementia diagnosis (CDR global < 1)",
            "Age 55-85 years",
            "Medically stable; adequate visual/auditory function for testing",
        ],

        exclusion_criteria=[
            "Dementia (CDR global >=1, MoCA <18)",
            "Active major psychiatric illness requiring hospitalization",
            "Recent stroke or acute neurological event (<6 months)",
            "Unstable epilepsy",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS,

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "monitoring",
                "Monitor for cognitive anxiety or distress about performance — some MCI patients become distressed when cognition is tested repeatedly. Reassure and normalize.",
                "low",
                "Clinical best practice",
            ),
            make_safety(
                "precaution",
                "MCI patients on cholinesterase inhibitors (donepezil, rivastigmine) or memantine: ensure stable medication dose throughout treatment block. Document medication status at each session.",
                "moderate",
                "Drug-stimulation interaction precaution",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Left Dorsolateral Prefrontal Cortex", "L-DLPFC", "left",
                "Left DLPFC anodal tDCS enhances working memory, executive function, and "
                "top-down memory encoding control in MCI. Boggio et al. (2012) demonstrated "
                "tDCS improved working memory in MCI patients. Bystad et al. (2016) showed "
                "episodic memory enhancement. The CEN upregulation effect is synergistic "
                "with concurrent cognitive training. OFF-LABEL.",
                "C-MCI-DLPFC — Working Memory Enhancement",
                EvidenceLevel.MEDIUM, off_label=True,
                eeg_canonical=["F3"],
            ),
            make_tdcs_target(
                "Left Inferior Parietal Cortex", "P3", "left",
                "Parietal cortex anodal tDCS targets the episodic memory retrieval network. "
                "Cotelli et al. (2012) showed tDCS over parietal cortex improved associative "
                "memory in healthy older adults and MCI. P3 approximates left inferior parietal "
                "lobule — a key node in the memory retrieval circuit. OFF-LABEL.",
                "C-MCI-PARIETAL — Episodic Memory Retrieval",
                EvidenceLevel.LOW, off_label=True,
                eeg_canonical=["P3"],
            ),
            make_tps_target(
                "Hippocampal-Adjacent Temporal Cortex", "TPS-HC", "bilateral",
                "TPS (transcranial pulse stimulation) can reach deeper temporal structures "
                "approximating the hippocampus — inaccessible to tDCS. Early TPS studies "
                "in MCI/AD suggest memory network engagement via temporal stimulation. "
                "Investigational but promising for amnestic MCI. OFF-LABEL.",
                "TPS-MCI-TEMP — Hippocampal Memory Network",
                EvidenceLevel.LOW,
                eeg_canonical=["T3", "T4", "T5", "T6"],
            ),
            StimulationTarget(
                modality=Modality.TMS,
                target_region="Left Dorsolateral Prefrontal Cortex",
                target_abbreviation="L-DLPFC rTMS",
                laterality="left",
                rationale="High-frequency rTMS (10-20 Hz) over left DLPFC upregulates "
                          "prefrontal-hippocampal connectivity and working memory in MCI. "
                          "Multiple RCTs demonstrate memory enhancement. Can be combined "
                          "with tDCS for multimodal approach. OFF-LABEL.",
                protocol_label="TMS-MCI-DLPFC — rTMS Memory Enhancement",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=True,
                eeg_canonical=["F3"],
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-MCI-DLPFC-PARIETAL",
                label="Bifrontal-Parietal tDCS — Memory Enhancement",
                modality=Modality.TDCS,
                target_region="Left DLPFC + Left Parietal",
                target_abbreviation="F3+P3",
                phenotype_slugs=["amnestic_single", "amnestic_multi"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC) or P3 (left parietal)",
                    "cathode": "Right shoulder or Fp2",
                    "intensity": "1.5-2.0 mA",
                    "duration": "20-30 min",
                    "sessions": "15-20 over 4-5 weeks",
                    "concurrent_training": "Working memory or memory encoding exercises during stimulation",
                },
                rationale="Left DLPFC anodal tDCS enhances working memory and executive function, "
                          "while parietal tDCS augments episodic memory retrieval. Combined with "
                          "cognitive training during stimulation — activity-dependent plasticity "
                          "maximizes memory encoding benefit. Bystad et al. (2016) demonstrated "
                          "tDCS memory enhancement in MCI; Cotelli et al. (2012) confirmed parietal effect.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=20,
                # Extended protocol fields
                protocol_name='TDCS-MCI-DLPFC-PAR — DLPFC-Parietal Cognitive Protocol',
                clinical_objective='Enhance executive function and episodic memory via combined DLPFC and parietal stimulation',
                primary_targets=['Bilateral DLPFC (F3/F4)', 'Bilateral Parietal (P3/P4)'],
                secondary_targets=['Frontoparietal network'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Ch1 Anode (+): F3 (L-DLPFC). Ch2 Anode (+): P3/P4 (parietal). Cathode (-): right shoulder. 1.5-2.0 mA, 20-30 min.',
                frequency='1 session/day, 5 days/week',
                duration='20-30 min per session',
                intensity_dose='1.5-2.0 mA per channel',
                montage_roi='Anode (+): F3 (L-DLPFC), P3/P4 (parietal). Cathode (-): right shoulder',
                laterality='Left-dominant or bilateral',
                treatment_course='10-15 sessions over 3 weeks; reassess at Week 4',
                monitoring='Impedance check; MoCA biweekly; memory subtests; skin integrity',
                expected_response='Improved working memory and episodic recall by Week 3-4',
                evidence_status='Moderate — multiple tDCS cognitive enhancement studies in MCI; meta-analyses supportive',
                cautions='OFF-LABEL. Monitor for conversion to AD during treatment. Cognitive stimulation during sessions recommended.',
                when_to_escalate='If no improvement after 10 sessions, consider TPS hippocampal protocol',
                when_to_stop_modify='Stop if confusion, agitation, or skin lesion',
                clinical_notes_extended='Concurrent cognitive training (memory, executive tasks) during stimulation enhances activity-dependent plasticity.',
                key_citations=['Boggio et al., 2012', 'Ferrucci et al., 2008'],
            ),
            ProtocolEntry(
                protocol_id="TPS-MCI-TEMPORAL",
                label="TPS — Hippocampal-Adjacent Temporal Stimulation",
                modality=Modality.TPS,
                target_region="Hippocampal-Adjacent Temporal Cortex",
                target_abbreviation="TPS-HC",
                phenotype_slugs=["amnestic_single", "amnestic_multi"],
                network_targets=[NetworkKey.DMN, NetworkKey.LIMBIC],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Bilateral temporal — hippocampal approximation",
                    "pulses_per_session": "300 pulses",
                    "sessions": "6-8 sessions over 3-4 weeks",
                    "frequency": "0.2 Hz (standard TPS protocol)",
                },
                rationale="TPS can deliver focused pulse stimulation to deeper temporal structures "
                          "approximating hippocampus — the primary site of MCI neurodegeneration. "
                          "Early evidence for TPS in cognitive enhancement. Investigational for MCI.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=8,
                notes="Informed consent required for TPS off-label use in MCI. Investigational.",
                # Extended protocol fields
                protocol_name='TPS-MCI-TEMP — Temporal/Hippocampal TPS Memory Protocol',
                clinical_objective='Induce neuroplasticity in hippocampal-temporal memory circuits at depth',
                primary_targets=['Hippocampus / Temporal cortex bilateral'],
                secondary_targets=['Entorhinal cortex'],
                device_name='NEUROLITH® TPS System (Storz Medical)',
                session_structure='Neuronavigation setup → Holocranial priming (2,000 pulses) → Targeted temporal/hippocampal stimulation (4,000 pulses) → Secondary targets (2,000 pulses)',
                frequency='3 sessions/week',
                duration='30-45 min per session',
                intensity_dose='0.20-0.25 mJ/mm²; 4-5 Hz',
                montage_roi='MRI-neuronavigated hippocampal/temporal targets; scalp entry near T5/T6',
                laterality='Bilateral sequential',
                treatment_course='6-12 sessions over 2-4 weeks; then maintenance 1-2/month',
                monitoring='MoCA pre/post block; memory subtests; tolerability log',
                expected_response='Cognitive stabilization or improvement at 1 and 3 months',
                evidence_status='Moderate — Benussi et al. 2020 RCT in MCI/AD',
                cautions='TPS has regulatory approval for AD/MCI in some jurisdictions. Neuronavigation mandatory.',
                when_to_escalate='If no improvement, add tDCS DLPFC-parietal protocol',
                when_to_stop_modify='Stop if persistent headache or confusion',
                clinical_notes_extended='Hippocampal depth targeting is the key advantage over surface tDCS.',
                key_citations=['Benussi et al., 2020'],
            ),
            ProtocolEntry(
                protocol_id="TMS-MCI-HF-DLPFC",
                label="rTMS High-Frequency — L-DLPFC Memory Protocol",
                modality=Modality.TMS,
                target_region="Left Dorsolateral Prefrontal Cortex",
                target_abbreviation="L-DLPFC",
                phenotype_slugs=["amnestic_multi", "nonamnestic"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "frequency": "10-20 Hz",
                    "intensity": "80-100% RMT",
                    "pulses_per_session": "1500-2000",
                    "sessions": "20-30 over 4-6 weeks",
                    "target_localization": "F3 (10-20 EEG) or neuronavigation",
                },
                rationale="High-frequency rTMS over left DLPFC upregulates prefrontal-hippocampal "
                          "connectivity and enhances working memory and executive function in MCI. "
                          "Multiple RCTs support rTMS for memory enhancement in MCI.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=25,
                # Extended protocol fields
                protocol_name='TMS-MCI-DLPFC — High-Frequency DLPFC rTMS for Cognition',
                clinical_objective='Enhance executive function and attention via high-frequency rTMS to left DLPFC',
                primary_targets=['Left DLPFC'],
                secondary_targets=['Frontoparietal network'],
                device_name='MagVenture or Magstim TMS System',
                session_structure='10 Hz rTMS over left DLPFC (F3/neuronavigation); 2000-3000 pulses per session',
                frequency='5 sessions/week',
                duration='20-30 min per session',
                intensity_dose='110% resting motor threshold; 10 Hz',
                montage_roi='Left DLPFC (F3 / neuronavigation-guided)',
                laterality='Left',
                treatment_course='10-20 sessions over 2-4 weeks',
                monitoring='MoCA; cognitive battery; tolerability',
                expected_response='Improved attention and executive function',
                evidence_status='Moderate — multiple rTMS-MCI studies with positive cognitive outcomes',
                cautions='OFF-LABEL. Standard TMS safety screening. Seizure risk assessment.',
                when_to_escalate='If no improvement, consider TPS hippocampal protocol',
                when_to_stop_modify='Stop if seizure or severe headache',
                clinical_notes_extended='High-frequency (10 Hz) rTMS over left DLPFC enhances executive circuits.',
                key_citations=['Drumond Marra et al., 2015'],
            ),
        ],

        symptom_network_mapping={
            "Memory Complaints": [NetworkKey.DMN, NetworkKey.LIMBIC],
            "Word-Finding Difficulty": [NetworkKey.CEN, NetworkKey.DMN],
            "Executive Dysfunction": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Concentration Deficits": [NetworkKey.ATTENTION, NetworkKey.CEN],
            "Depression/Anxiety Comorbidity": [NetworkKey.LIMBIC, NetworkKey.DMN],
        },

        symptom_modality_mapping={
            "Memory Complaints": [Modality.TDCS, Modality.TPS, Modality.TMS],
            "Word-Finding Difficulty": [Modality.TDCS, Modality.TMS],
            "Executive Dysfunction": [Modality.TDCS, Modality.TMS],
            "Concentration Deficits": [Modality.TDCS],
            "Depression/Anxiety Comorbidity": [Modality.TDCS],
        },

        responder_criteria=[
            ">=2-point improvement in MoCA score (MCID for MCI)",
            "Clinically meaningful improvement in subjective memory complaint",
            "Stabilization or improvement in CDR-SB at 3-month follow-up",
        ],

        non_responder_pathway=(
            "For non-responders at 4-week block:\n"
            "1. Reassess MCI subtype — amnestic vs. non-amnestic may require different targets\n"
            "2. Enhance concurrent cognitive training during stimulation (activity-dependent plasticity)\n"
            "3. Add TPS temporal stimulation if hippocampal targeting justified\n"
            "4. Review medication — ensure cholinesterase inhibitor dose stable\n"
            "5. Consider referral for neuropsychological assessment and cognitive rehabilitation program"
        ),

        evidence_summary=(
            "MCI neuromodulation evidence is growing. tDCS over DLPFC and parietal cortex: "
            "multiple pilot RCTs demonstrate working memory and episodic memory improvement. "
            "Bystad et al. (2016): tDCS enhanced verbal memory in MCI patients over sham. "
            "Cotelli et al. (2012): parietal tDCS improved associative memory in aging. "
            "TMS (rTMS 10-20 Hz L-DLPFC): multiple controlled trials show memory benefit. "
            "TPS: early evidence from AD studies; extrapolated to MCI. "
            "Key limitation: heterogeneous MCI populations across studies, short follow-up. "
            "| Evidence counts: TMS=60, tDCS=40, TPS=10. Best modalities: TPS, TMS, tDCS."
        ),

        evidence_gaps=[
            "Long-term follow-up beyond 3 months — does neuromodulation slow MCI-to-dementia conversion?",
            "Optimal target selection for amnestic vs. non-amnestic MCI",
            "Synergy of tDCS + cognitive training: optimal task type during stimulation",
            "Biomarker-guided responder prediction (amyloid PET, ApoE4 status)",
        ],

        references=[
            {
                "authors": "Bystad M et al.",
                "year": 2016,
                "title": "Transcranial direct current stimulation as a memory enhancer in patients with Alzheimer's disease",
                "journal": "Neuropsychological Rehabilitation",
                "pmid": "27034021",
                "evidence_type": "rct",
            },
            {
                "authors": "Boggio PS et al.",
                "year": 2012,
                "title": "Non-invasive brain stimulation and MCI",
                "journal": "Brain Stimulation",
                "pmid": "22169294",
                "evidence_type": "pilot_study",
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
            "Combine tDCS with active cognitive training during stimulation — activity-dependent plasticity maximizes memory benefit",
            "Amnestic MCI with MoCA 20-25: best candidate for TPS temporal + tDCS DLPFC dual protocol",
            "Monitor for emotional distress around cognitive testing — normalize memory complaints to reduce performance anxiety",
            "Screen for depression (PHQ-9) — depression in MCI independently predicts faster progression; treat concurrently",
            "Document baseline MoCA carefully — ceiling effects in mild MCI require follow-up with more sensitive tools (ADAS-Cog)",
        ],


        # --- Auto-enriched: PlatoScience Variants ---
        platoscience_variants=[
            PlatoScienceVariant(
                variant_id="C-MCI-DLPFC-PARIETAL-PS", protocol_id="C-MCI-DLPFC-PARIETAL",
                label="PlatoScience Bifrontal-Parietal tDCS — Memory Enhancement",
                parameters={"program": "Focus", "electrode_config": "F3 (left DLPFC) or P3 (left parietal)", "intensity": "1.5-2.0 mA", "duration": "20-30 min", "ramp": "30 sec"},
                notes="Maps to C-MCI-DLPFC-PARIETAL protocol. PlatoScience Focus program.",
            ),
        ],

        # --- Auto-enriched: Multimodal Combinations ---
        multimodal_combos=[
            MultimodalCombo(
                combo_id="F1", label="Bifrontal-Parietal tDCS — Memory Enhancement + TPS — Hippocampal-Adjacent Temporal Stimulation",
                phenotype_slugs=['amnestic_multi', 'amnestic_single'],
                tps_protocol_id="TPS-MCI-TEMPORAL",
                non_tps_protocol_ids=["C-MCI-DLPFC-PARIETAL"],
                sequencing_notes="Week 1-3: tDCS C-MCI-DLPFC-PARIETAL daily. Week 2-3: Add TPS TPS-MCI-TEMPORAL (2-3x/week).",
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
                "role": 'Anodal — executive function and working memory',
                "protocols_using": ['C-MCI-DLPFC-PARIETAL'],
            },
            {
                "position": 'F4',
                "brain_region": 'Right DLPFC',
                "role": 'Bilateral DLPFC target',
                "protocols_using": ['C-MCI-DLPFC-PARIETAL'],
            },
            {
                "position": 'P3',
                "brain_region": 'Left Posterior Parietal',
                "role": 'Episodic memory / parietal target',
                "protocols_using": ['C-MCI-DLPFC-PARIETAL'],
            },
            {
                "position": 'P4',
                "brain_region": 'Right Posterior Parietal',
                "role": 'Episodic memory / parietal target',
                "protocols_using": ['C-MCI-DLPFC-PARIETAL'],
            },
            {
                "position": 'T5',
                "brain_region": 'Left Temporal / Hippocampal projection',
                "role": 'TPS temporal target for memory',
                "protocols_using": ['TPS-MCI-TEMPORAL'],
            },
            {
                "position": 'T6',
                "brain_region": 'Right Temporal / Hippocampal projection',
                "role": 'TPS temporal target for memory',
                "protocols_using": ['TPS-MCI-TEMPORAL'],
            },
        ],
        adverse_event_grades=SHARED_ADVERSE_EVENT_GRADES,
        side_effects=SHARED_SIDE_EFFECTS,
        governance_rules=SHARED_GOVERNANCE_RULES + [
            "MCI diagnosis must be confirmed by physician before initiating neuromodulation",
            "TPS in MCI is investigational — enhanced informed consent required",
        ],
    )
