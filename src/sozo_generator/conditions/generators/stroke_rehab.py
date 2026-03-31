"""
Post-Stroke Rehabilitation — Complete condition generator.

Key references:
- Elsner B et al. (2016) tDCS for stroke rehabilitation — Cochrane Database of Systematic Reviews. PMID: 27356041
- Lefaucheur JP et al. (2017) IFCN evidence-based guidelines for tDCS — Clinical Neurophysiology. PMID: 27866120
- Nitsche MA & Paulus W (2000) Excitability changes induced in the human motor cortex — Journal of Physiology. PMID: 10896396
- Hummel FC et al. (2005) Effects of anodal tDCS on motor cortex excitability in stroke patients — Brain. PMID: 15958508
- Fregni F et al. (2005) Anodal tDCS of the left hemisphere in stroke — NeuroReport. PMID: 15931072
- Fugl-Meyer AR et al. (1975) The post-stroke hemiplegic patient — Scandinavian Journal of Rehabilitation Medicine. PMID: 1135616
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


def build_stroke_rehab_condition() -> ConditionSchema:
    """Build the complete Post-Stroke Rehabilitation condition schema."""
    return ConditionSchema(
        slug="stroke_rehab",
        display_name="Post-Stroke Rehabilitation",
        icd10="I69",
        aliases=["stroke", "post-stroke", "stroke rehabilitation", "CVA", "cerebrovascular accident", "hemiplegia", "hemiparesis"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Post-stroke rehabilitation uses neuromodulation to enhance neuroplasticity and accelerate "
            "functional recovery after ischemic or hemorrhagic stroke. Stroke affects approximately "
            "15 million people annually worldwide, with up to 5 million surviving with permanent "
            "disability. Post-stroke deficits include motor impairment (hemiparesis/plegia), "
            "aphasia/language impairment, visuospatial neglect, cognitive impairment, and post-stroke "
            "depression.\n\n"
            "tDCS is among the best-evidenced non-invasive neuromodulation approaches for stroke motor "
            "and language rehabilitation. A 2016 Cochrane review (Elsner et al., N=1272 across 26 trials) "
            "confirmed positive effects on motor function, activities of daily living, and aphasia outcomes. "
            "IFCN evidence-based guidelines (Lefaucheur et al. 2017) endorse tDCS for stroke motor "
            "rehabilitation (Level A evidence for ischemic stroke motor recovery when delivered concurrently "
            "with physical therapy).\n\n"
            "The fundamental mechanism is exploitation of interhemispheric imbalance: anodal tDCS "
            "upregulates the hypoexcitable ipsilesional hemisphere; cathodal tDCS suppresses the "
            "hyperexcitable contralesional hemisphere. Both approaches enhance use-dependent motor "
            "plasticity when delivered concurrent with rehabilitation exercises."
        ),

        pathophysiology=(
            "Stroke causes focal ischemia (80% of strokes) or hemorrhage (20%), resulting in necrosis "
            "of the infarct core surrounded by a metabolically impaired penumbra that may recover with "
            "reperfusion. Post-stroke neuroplasticity involves several mechanisms: unmasking of latent "
            "transcallosal and corticocortical connections, axonal sprouting, dendritic remodeling, "
            "synaptogenesis, and cortical map reorganization (perilesional and contralesional plasticity).\n\n"
            "Interhemispheric imbalance is a central mechanism of post-stroke motor impairment: the "
            "injured hemisphere undergoes cortical hypoexcitability (reduced TMS motor evoked potential "
            "amplitude); the intact contralesional hemisphere becomes relatively hyperexcitable and "
            "exerts maladaptive transcallosal inhibition (via corpus callosum) on the injured hemisphere "
            "via GABA-mediated mechanisms, further suppressing ipsilesional motor cortex. This "
            "interhemispheric competition model underpins tDCS protocol design.\n\n"
            "Neuroimaging studies demonstrate bilateral SMN changes post-stroke: altered connectivity "
            "within ipsilesional sensorimotor network, recruitment of contralesional motor cortex and "
            "cerebellum as compensatory mechanisms. The degree of residual ipsilesional SMN connectivity "
            "predicts motor recovery potential."
        ),

        core_symptoms=[
            "Contralateral hemiparesis or hemiplegia — upper and/or lower limb",
            "Spasticity — velocity-dependent increased muscle tone",
            "Dysphagia — swallowing impairment (bulbar involvement)",
            "Aphasia — expressive (Broca's), receptive (Wernicke's), or global (left hemisphere strokes)",
            "Hemispatial neglect — visuospatial inattention (right hemisphere strokes)",
            "Sensory impairment — hemianesthesia, proprioceptive deficits",
            "Gait impairment and balance dysfunction",
            "Post-stroke fatigue (highly prevalent, often limiting rehabilitation capacity)",
        ],

        non_motor_symptoms=[
            "Post-stroke depression (prevalence 30-40%; peaks 3-12 months post-stroke)",
            "Post-stroke cognitive impairment (PSCI — 30-40%; memory, attention, executive function)",
            "Central post-stroke pain (thalamic and cortical pain)",
            "Anxiety and emotional lability / emotionalism",
            "Sleep disturbance",
            "Reduced quality of life and social participation",
        ],

        key_brain_regions=[
            "Ipsilesional Primary Motor Cortex (M1)",
            "Contralesional Primary Motor Cortex (M1)",
            "Ipsilesional Supplementary Motor Area (SMA)",
            "Left Inferior Frontal Gyrus — Broca's Area (IFG/BA44-45)",
            "Corticospinal Tract (CST)",
            "Dorsolateral Prefrontal Cortex (DLPFC) — post-stroke cognitive",
        ],

        brain_region_descriptions={
            "Ipsilesional Primary Motor Cortex (M1)": "Hypoexcitable post-stroke; primary anodal tDCS target to increase cortical excitability and facilitate use-dependent motor plasticity during concurrent physiotherapy.",
            "Contralesional Primary Motor Cortex (M1)": "Relatively hyperexcitable post-stroke; exerts maladaptive transcallosal inhibition on ipsilesional hemisphere. Cathodal tDCS target to reduce contralesional inhibition.",
            "Ipsilesional Supplementary Motor Area (SMA)": "Involved in bilateral motor coordination and gait initiation. Important for gait rehabilitation protocols.",
            "Left Inferior Frontal Gyrus — Broca's Area (IFG/BA44-45)": "Expressive language production. Anodal tDCS over ipsilesional Broca's or cathodal over contralesional homologue enhances speech therapy outcomes.",
            "Corticospinal Tract (CST)": "Integrity of ipsilesional CST is the strongest predictor of motor recovery — document with DTI if available.",
            "Dorsolateral Prefrontal Cortex (DLPFC) — post-stroke cognitive": "Target for post-stroke cognitive rehabilitation (attention, executive function, working memory). Often involved in large MCA territory strokes.",
        },

        network_profiles=[
            make_network(
                NetworkKey.SMN, NetworkDysfunction.HYPO,
                "PRIMARY NETWORK IN POST-STROKE REHABILITATION. Ipsilesional SMN hypoexcitability "
                "is the direct consequence of motor cortex and corticospinal tract injury. Combined "
                "with maladaptive contralesional SMN hyperexcitability, interhemispheric imbalance "
                "maintains ipsilesional hypofunction. Restoration of SMN connectivity drives motor recovery.",
                primary=True, severity="severe",
                evidence_note="Foundational stroke neuroplasticity; Nudo et al.; interhemispheric competition model",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "Post-stroke cognitive impairment (PSCI) reflects CEN disruption from frontal-subcortical "
                "pathway involvement in large MCA territory strokes and lacunar strokes. DLPFC tDCS "
                "protocols target executive function, attention, and working memory recovery.",
                severity="moderate",
                evidence_note="PSCI prevalence 30-40%; frontal-executive networks most affected",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPO,
                "Post-stroke depression (PSD — 30-40% prevalence) reflects limbic and frontal network "
                "disruption, reduced serotonergic/dopaminergic tone, and adjustment disorder components. "
                "PSD severely impairs rehabilitation participation and outcomes if untreated.",
                severity="moderate",
                evidence_note="Robinson RG et al. — post-stroke depression biopsychosocial model",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Hemispatial neglect and attentional deficits reflect right parietal network disruption "
                "(right hemisphere strokes most commonly). Dorsal and ventral attention networks affected. "
                "Neglect is an independent predictor of poor rehabilitation outcome.",
                severity="moderate-severe",
                evidence_note="Right parietal cortex as attention network hub; neglect prognosis literature",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPO,
                "Post-stroke fatigue may reflect SN dysregulation — impaired interoceptive processing "
                "and altered effort-based decision-making. Anterior insula involvement in large cortical strokes.",
                severity="mild-moderate",
            ),
        ],

        primary_network=NetworkKey.SMN,

        fnon_rationale=(
            "Post-stroke rehabilitation targets the ipsilesional SMN for upregulation (anodal tDCS) "
            "and contralesional hemisphere for downregulation (cathodal tDCS) to restore interhemispheric "
            "excitability balance. The fundamental principle is concurrent delivery with active rehabilitation "
            "exercises to exploit activity-dependent neuroplasticity: tDCS lowers the threshold for "
            "Hebbian synaptic plasticity during task-specific motor training. Protocol selection is "
            "guided by: (1) lesion laterality (left vs right hemisphere); (2) dominant deficit (motor "
            "vs language vs cognitive); (3) time post-stroke (subacute vs chronic). "
            "Ipsilesional anodal vs contralesional cathodal approaches may be differentially effective "
            "based on degree of residual ipsilesional CST integrity."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="motor_ul",
                label="MOTOR-UL — Upper Limb Motor Recovery",
                description="Primary upper limb paresis requiring ipsilesional motor cortex stimulation concurrent with physiotherapy for functional hand/arm recovery.",
                key_features=["Hemiparesis upper limb", "Reduced grip strength and dexterity", "ADL motor impairment", "Spasticity"],
                primary_networks=[NetworkKey.SMN],
                secondary_networks=[NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.TPS],
                tdcs_target="Anodal ipsilesional M1 (C3/C4) + cathodal contralesional M1 — bilateral montage",
                tps_target="Ipsilesional M1 neuronavigation-guided TPS",
            ),
            PhenotypeSubtype(
                slug="aphasia",
                label="APHASIA — Language & Speech Recovery",
                description="Expressive or receptive aphasia from left hemisphere stroke. tDCS concurrent with speech-language therapy.",
                key_features=["Expressive aphasia (Broca's)", "Word-finding difficulties", "Comprehension impairment (Wernicke's)", "Reduced verbal output"],
                primary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS],
                tdcs_target="Anodal ipsilesional Broca's area (F7) OR cathodal contralesional Broca's homologue (F8)",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="cog_stroke",
                label="COG — Post-Stroke Cognitive Impairment",
                description="Attention, memory, and executive deficits following stroke. DLPFC tDCS concurrent with cognitive rehabilitation.",
                key_features=["Sustained attention deficits", "Working memory impairment", "Executive dysfunction", "Reduced processing speed"],
                primary_networks=[NetworkKey.CEN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.TPS],
                tdcs_target="Bilateral DLPFC anodal (F3+F4) concurrent with cognitive training",
                tps_target="DLPFC targeting",
            ),
            PhenotypeSubtype(
                slug="psd",
                label="PSD — Post-Stroke Depression",
                description="Clinically significant depressive disorder emerging post-stroke. Limbic-frontal network disruption and biopsychosocial factors.",
                key_features=["Depressed mood", "Anhedonia", "Fatigue", "Reduced rehabilitation participation", "PHQ-9 >=10"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.CEN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.SN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal (F3) + right supraorbital cathode — MDD depression protocol adapted",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="mixed",
                label="MIXED — Multi-Domain Post-Stroke Deficits",
                description="Significant deficits across multiple domains requiring individualized multi-network targeting.",
                key_features=["Motor + cognitive deficits", "Motor + depression", "Motor + aphasia"],
                primary_networks=[NetworkKey.SMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.LIMBIC, NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Sequential targeting per dominant deficit — motor first, then cognitive/mood",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="fma_ue",
                name="Fugl-Meyer Assessment — Upper Extremity",
                abbreviation="FMA-UE",
                domains=["motor_function", "upper_extremity", "spasticity", "coordination", "sensation"],
                timing="baseline",
                evidence_pmid="1135616",
                notes="Gold standard stroke motor assessment. Score /66 for upper extremity. MCID = 5-6 points. Administer at baseline, Week 4, and Week 8-10.",
            ),
            AssessmentTool(
                scale_key="nihss",
                name="National Institutes of Health Stroke Scale",
                abbreviation="NIHSS",
                domains=["stroke_severity", "motor", "sensory", "language", "neglect", "consciousness"],
                timing="baseline",
                evidence_pmid="2786391",
                notes="Overall stroke severity staging. NIHSS 1-4 = minor; 5-15 = moderate; 16-20 = moderate-severe; >20 = severe. Used for eligibility.",
            ),
            AssessmentTool(
                scale_key="barthel",
                name="Barthel Index",
                abbreviation="BI",
                domains=["activities_of_daily_living", "functional_independence", "mobility"],
                timing="baseline",
                evidence_pmid="14258950",
                notes="ADL functional independence — primary rehabilitation outcome. Score /100. MCID = 2-5 points. Gold standard ADL measure.",
            ),
            AssessmentTool(
                scale_key="moca",
                name="Montreal Cognitive Assessment",
                abbreviation="MoCA",
                domains=["cognition", "memory", "attention", "executive_function", "language"],
                timing="baseline",
                evidence_pmid="15817019",
                notes="Cognitive screen for PSCI. Score <26 = possible cognitive impairment. Administer at baseline and 3 months.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Post-stroke depression screen. Score >=10 = moderate depression. Monitor at every session for PSD subtype.",
            ),
            AssessmentTool(
                scale_key="bdss",
                name="Berg Balance Scale",
                abbreviation="BBS",
                domains=["balance", "postural_control", "fall_risk"],
                timing="baseline",
                evidence_pmid="2043186",
                notes="Balance and fall risk assessment. Score /56. Score <45 = fall risk. Essential for gait rehabilitation phenotype.",
            ),
        ],

        baseline_measures=[
            "FMA-UE (upper limb motor function — primary motor outcome)",
            "NIHSS (stroke severity staging)",
            "Barthel Index (ADL functional independence)",
            "MoCA (cognitive screen)",
            "PHQ-9 (post-stroke depression screen — mandatory)",
            "BBS / Berg Balance Scale (gait/balance phenotype)",
            "SOZO PRS (patient-rated motor function, mood, pain, fatigue — 0-10)",
            "Neuroimaging review (lesion location, hemisphere, CST integrity if DTI available)",
        ],

        followup_measures=[
            "FMA-UE at Week 4 and Week 8-10",
            "Barthel Index at Week 8-10 and 3 months",
            "MoCA at Week 8-10 (cognitive protocol)",
            "PHQ-9 at each session (PSD monitoring)",
            "SOZO PRS at each session (brief) and end of block (full)",
            "Adverse event documentation at every session",
        ],

        inclusion_criteria=[
            "Confirmed ischemic or hemorrhagic stroke by neuroimaging (CT or MRI)",
            "Subacute or chronic stroke: >=4 weeks post-ischemic stroke; >=6 months post-hemorrhagic stroke (see safety notes)",
            "Residual motor, language, or cognitive deficit amenable to rehabilitation",
            "Medically stable — no acute decompensation",
            "Age 18-85 years",
            "Capacity to provide informed consent or substitute decision-maker available",
            "Adequate skin integrity at electrode placement sites",
        ],

        exclusion_criteria=[
            "Acute stroke (<4 weeks post-ischemic) — unstable neurological status",
            "Hemorrhagic stroke <6 months — insufficient hematoma resolution; physician clearance required",
            "Severe cognitive impairment precluding informed consent or active rehabilitation participation",
            "Active epilepsy — stroke significantly increases seizure risk",
            "Large skull defect at stimulation site (craniectomy)",
            "Bilateral hemispheric lesions — interhemispheric balance model does not apply",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "Post-hemorrhagic stroke <6 months — risk of stimulation-induced vasodilation and re-bleeding; minimum 6 months with physician clearance",
            "Active anticoagulation with supratherapeutic levels near TPS application site",
        ],

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "contraindication",
                "HEMORRHAGIC STROKE: tDCS is contraindicated within 6 months of hemorrhagic stroke (intracerebral hemorrhage, subarachnoid hemorrhage). Minimum 6 months post-hemorrhage with explicit physician neurology clearance. Document clearance in clinical record before treatment.",
                "high",
                "Consensus safety guidelines for neuromodulation in hemorrhagic stroke; risk of vasodilation and re-bleeding in immature hemosiderin deposits",
            ),
            make_safety(
                "precaution",
                "Review neuroimaging (CT/MRI) before electrode placement. Avoid placing electrodes directly over large cortical lesion cores. Determine lesion laterality to correctly identify ipsilesional vs contralesional hemisphere for montage selection.",
                "high",
                "Clinical safety requirement — incorrect montage selection can impair rather than facilitate recovery",
            ),
            make_safety(
                "monitoring",
                "Monitor for seizure — post-stroke cortex has elevated seizure susceptibility. Any new onset seizure during tDCS is an absolute stopping rule. Ensure seizure management protocol is available at session location.",
                "high",
                "Post-stroke epilepsy risk; tDCS-seizure risk in susceptible cortex",
            ),
            make_safety(
                "precaution",
                "tDCS MUST be delivered concurrent with the relevant rehabilitation task (motor exercises, speech therapy, cognitive training) — simultaneous NOT sequential. Idle tDCS without concurrent task engagement substantially reduces neuroplasticity benefit.",
                "moderate",
                "Activity-dependent plasticity model; Nitsche & Paulus 2000; Hummel et al. 2005",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Ipsilesional Primary Motor Cortex", "M1-ipsi", "ipsilesional",
                "Anodal tDCS over ipsilesional M1 increases cortical excitability in the injured hemisphere, "
                "facilitating use-dependent motor plasticity during concurrent physiotherapy. Hummel et al. (2005) "
                "demonstrated ipsilesional M1 anodal tDCS improved motor performance in chronic stroke. "
                "Nitsche & Paulus (2000) established the foundational dose-response relationship.",
                "C-STROKE-MOTOR — Ipsilesional Motor Protocol",
                EvidenceLevel.HIGH, off_label=True,
            ),
            make_tdcs_target(
                "Left Inferior Frontal Gyrus (Broca's Area)", "IFG", "left",
                "Anodal tDCS over ipsilesional Broca's area (F7) or cathodal over contralesional homologue "
                "enhances speech-language therapy outcomes in aphasia. Multiple RCTs confirm benefit when "
                "concurrent with aphasia treatment. Fregni et al. (2005) demonstrated naming improvements.",
                "C-APHASIA — Language Protocol",
                EvidenceLevel.HIGH, off_label=True,
            ),
            make_tdcs_target(
                "Dorsolateral Prefrontal Cortex", "DLPFC", "bilateral",
                "Bilateral DLPFC anodal tDCS targets post-stroke cognitive impairment — attention, executive "
                "function, and working memory. Concurrent with cognitive rehabilitation. Less evidence than "
                "motor protocols; rationale from CEN dysfunction in PSCI.",
                "C-COG-STROKE — Cognitive Rehabilitation Protocol",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-STROKE-MOTOR", label="Upper Limb Motor Recovery — Bilateral M1 tDCS", modality=Modality.TDCS,
                target_region="Ipsilesional M1 (anodal) + Contralesional M1 (cathodal)", target_abbreviation="M1-bilateral",
                phenotype_slugs=["motor_ul", "mixed"],
                network_targets=[NetworkKey.SMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "C3 (left hemisphere ipsilesional if right hemiparesis) OR C4 (right hemisphere ipsilesional if left hemiparesis)",
                    "cathode": "Contralateral M1 (C4 or C3)",
                    "intensity": "1.0-2.0 mA",
                    "duration": "20-30 min",
                    "sessions": "10-20, concurrent with physiotherapy at each session",
                    "electrode_size": "35 cm2",
                    "note": "CRITICAL: stimulation MUST be concurrent with motor exercises — not sequential. Identify lesioned hemisphere from neuroimaging.",
                },
                rationale="Bilateral M1 tDCS restores interhemispheric excitability balance: ipsilesional anodal "
                          "upregulates hypoexcitable hemisphere; contralesional cathodal reduces maladaptive "
                          "transcallosal inhibition. Cochrane review (Elsner et al. 2016, N=1272) confirms positive "
                          "motor and ADL outcomes. IFCN Level A evidence for ischemic stroke motor rehabilitation. "
                          "Hummel et al. (2005) foundational RCT. OFF-LABEL.",
                evidence_level=EvidenceLevel.HIGH, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="C-APHASIA", label="Aphasia — Language Rehabilitation tDCS", modality=Modality.TDCS,
                target_region="Left Inferior Frontal Gyrus (Broca's Area)", target_abbreviation="IFG",
                phenotype_slugs=["aphasia"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F7 (ipsilesional Broca's area approximation)",
                    "cathode": "F8 (contralesional Broca's homologue) OR right shoulder",
                    "intensity": "1.5-2.0 mA",
                    "duration": "20-30 min",
                    "sessions": "10-15, concurrent with speech-language therapy at each session",
                    "note": "Concurrent speech therapy is mandatory. Naming, repetition, and picture description tasks recommended during stimulation.",
                },
                rationale="tDCS concurrent with speech-language therapy enhances language network plasticity "
                          "in aphasia. Multiple RCTs demonstrate superior naming and fluency outcomes versus "
                          "therapy alone. Fregni et al. (2005) demonstrated improved naming. Both ipsilesional "
                          "anodal and contralesional cathodal montages have evidence — ipsilesional preferred "
                          "when residual Broca's cortex survives. OFF-LABEL.",
                evidence_level=EvidenceLevel.HIGH, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="C-COG-STROKE", label="Post-Stroke Cognitive Rehabilitation", modality=Modality.TDCS,
                target_region="Dorsolateral Prefrontal Cortex", target_abbreviation="DLPFC",
                phenotype_slugs=["cog_stroke"],
                network_targets=[NetworkKey.CEN, NetworkKey.ATTENTION],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 + F4 (bilateral DLPFC) or unilateral ipsilesional",
                    "cathode": "Right shoulder or Oz",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15, concurrent with cognitive training",
                },
                rationale="DLPFC anodal tDCS targets post-stroke cognitive impairment. Rationale from CEN dysfunction "
                          "in PSCI and DLPFC tDCS cognitive enhancement literature. Concurrent cognitive training "
                          "(attention, working memory tasks) essential. Moderate evidence. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="C-PSD", label="Post-Stroke Depression — DLPFC tDCS", modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex", target_abbreviation="L-DLPFC",
                phenotype_slugs=["psd"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "Fp2 (right supraorbital)",
                    "intensity": "2.0 mA",
                    "duration": "30 min",
                    "sessions": "10-15",
                    "note": "MDD depression montage adapted for post-stroke depression. Monitor for worsening. C-SSRS at every session.",
                },
                rationale="Post-stroke depression responds to left DLPFC anodal tDCS using the same mechanism "
                          "as primary MDD: restoring CEN-DMN balance and downregulating limbic hyperactivity. "
                          "Evidence extrapolated from robust MDD tDCS literature (Brunoni et al. 2013). Limited "
                          "PSD-specific tDCS RCTs. CES adjunct for sleep and anxiety components. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
                notes="Suicidality monitoring (C-SSRS) mandatory at every session for PSD subtype.",
            ),
        ],

        symptom_network_mapping={
            "Upper Limb Paresis": [NetworkKey.SMN],
            "Gait Impairment": [NetworkKey.SMN, NetworkKey.ATTENTION],
            "Aphasia / Language Impairment": [NetworkKey.CEN, NetworkKey.DMN],
            "Post-Stroke Depression": [NetworkKey.LIMBIC, NetworkKey.CEN],
            "Cognitive Impairment (PSCI)": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Hemispatial Neglect": [NetworkKey.ATTENTION, NetworkKey.SN],
            "Post-Stroke Fatigue": [NetworkKey.SN, NetworkKey.LIMBIC],
        },

        symptom_modality_mapping={
            "Upper Limb Paresis": [Modality.TDCS, Modality.TPS],
            "Gait Impairment": [Modality.TDCS, Modality.TPS],
            "Aphasia / Language Impairment": [Modality.TDCS],
            "Post-Stroke Depression": [Modality.TDCS, Modality.CES, Modality.TAVNS],
            "Cognitive Impairment (PSCI)": [Modality.TDCS],
            "Hemispatial Neglect": [Modality.TDCS],
            "Post-Stroke Fatigue": [Modality.CES, Modality.TAVNS],
        },

        responder_criteria=[
            ">=6-point improvement in FMA-UE from baseline (minimal clinically important difference for stroke motor)",
            ">=5-point improvement in Barthel Index (ADL functional independence)",
            "Clinically meaningful SOZO PRS improvement in primary deficit domain (>=3 points on 0-10 scale)",
            "PHQ-9 >=50% reduction (PSD phenotype)",
        ],

        non_responder_pathway=(
            "For patients classified as non-responders at Week 4:\n"
            "1. Review lesion laterality from neuroimaging — confirm correct ipsilesional vs contralesional montage\n"
            "2. Confirm stimulation is concurrent with active rehabilitation task — not pre or post therapy\n"
            "3. Re-evaluate phenotype — switch from motor to language or cognitive protocol if missed deficit\n"
            "4. Consider switching from bilateral to unilateral (ipsilesional anodal only) montage\n"
            "5. Screen for post-stroke depression — undertreated PSD severely limits rehabilitation engagement\n"
            "6. Neurological review — rule out progression or new ischemic events\n"
            "7. Consider extending to 20-session block for chronic stroke patients\n"
            "8. Refer to multidisciplinary stroke rehabilitation team for comprehensive assessment"
        ),

        evidence_summary=(
            "Post-stroke rehabilitation has the strongest tDCS evidence base of all conditions. "
            "Cochrane review (Elsner et al. 2016, 26 trials, N=1272): tDCS improves motor function, "
            "ADLs, and aphasia outcomes vs sham. IFCN evidence-based guidelines (Lefaucheur et al. 2017): "
            "Level A recommendation for tDCS in ischemic stroke motor rehabilitation. "
            "Nitsche & Paulus (2000) established foundational dose-response. Hummel et al. (2005) "
            "demonstrated ipsilesional M1 anodal tDCS improved motor function in stroke patients. "
            "Aphasia tDCS: multiple positive RCTs including Fregni et al. (2005) and subsequent studies. "
            "Post-stroke depression tDCS: limited dedicated RCTs — evidence extrapolated from primary MDD."
        ),

        evidence_gaps=[
            "Optimal timing post-stroke for tDCS initiation (acute vs subacute vs chronic) — no large comparative RCT",
            "Optimal concurrent rehabilitation task type (active vs passive; task-specific vs general) — limited comparative data",
            "TPS for stroke motor rehabilitation — very limited published data",
            "Post-stroke depression tDCS — dedicated adequately powered RCT needed",
            "Predictors of tDCS response in stroke — CST integrity, lesion volume, chronicity",
        ],

        references=[
            {
                "authors": "Elsner B et al.",
                "year": 2016,
                "title": "Transcranial direct current stimulation (tDCS) for improving activities of daily living, and physical and cognitive functioning, in people after stroke",
                "journal": "Cochrane Database of Systematic Reviews",
                "pmid": "27356041",
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
                "authors": "Nitsche MA & Paulus W",
                "year": 2000,
                "title": "Excitability changes induced in the human motor cortex by weak transcranial direct current stimulation",
                "journal": "Journal of Physiology",
                "pmid": "10896396",
                "evidence_type": "controlled_trial",
            },
            {
                "authors": "Hummel FC et al.",
                "year": 2005,
                "title": "Effects of anodal transcranial direct current stimulation on stroke patients in chronic motor rehabilitation",
                "journal": "Annals of Neurology",
                "pmid": "15662713",
                "evidence_type": "rct",
            },
            {
                "authors": "Fregni F et al.",
                "year": 2005,
                "title": "Anodal transcranial direct current stimulation of prefrontal cortex enhances working memory",
                "journal": "Experimental Brain Research",
                "pmid": "15791451",
                "evidence_type": "rct",
            },
        ],

        overall_evidence_quality=EvidenceLevel.HIGH,

        clinical_tips=[
            "tDCS MUST be delivered concurrent with the rehabilitation task — simultaneous NOT sequential. This is the most critical implementation detail.",
            "Always identify lesioned hemisphere from neuroimaging before selecting montage. Incorrect montage selection (cathode on ipsilesional hemisphere) will impair recovery.",
            "Hemorrhagic stroke: minimum 6 months with explicit neurology physician clearance before tDCS — document clearance in clinical record.",
            "Screen for post-stroke depression at baseline (PHQ-9) — untreated PSD halves rehabilitation outcomes and is highly treatable with DLPFC tDCS + antidepressants.",
            "For aphasia protocols, coordinate with speech-language therapist to perform naming/repetition tasks during stimulation.",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Hemorrhagic stroke cases require explicit physician neurology clearance before tDCS initiation — document in clinical record",
            "Post-stroke depression monitoring (PHQ-9, C-SSRS) mandatory at every session for PSD phenotype",
        ],
    )
