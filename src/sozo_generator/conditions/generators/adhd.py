"""
Attention Deficit Hyperactivity Disorder (ADHD) — Complete condition generator.

Key references:
- Westwood SJ et al. (2021) Systematic review of tDCS in ADHD — Frontiers in Human Neuroscience. PMID: 33568986
- Sotnikova A et al. (2017) tDCS modulates neuronal networks in ADHD — Frontiers in Human Neuroscience. PMID: 28261072
- Breitling C et al. (2010) Anodal tDCS over DLPFC in adult ADHD — Journal of Attention Disorders. PMID: 20354211
- Kessler RC et al. (2006) The prevalence and correlates of adult ADHD in the US — American Journal of Psychiatry. PMID: 16585449
- Barkley RA (1997) Behavioral inhibition, sustained attention, and executive functions. Psychological Bulletin. PMID: 9000892
- Castellanos FX & Proal E (2012) Large-scale brain systems in ADHD. Trends in Cognitive Sciences. PMID: 22575726
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


def build_adhd_condition() -> ConditionSchema:
    """Build the complete ADHD condition schema."""
    return ConditionSchema(
        slug="adhd",
        display_name="Attention Deficit Hyperactivity Disorder",
        icd10="F90",
        aliases=["ADHD", "ADD", "attention deficit", "attention deficit disorder", "ADHD-I", "ADHD-C"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Attention-Deficit/Hyperactivity Disorder (ADHD) is a neurodevelopmental disorder "
            "characterized by persistent, impairing patterns of inattention, hyperactivity, and "
            "impulsivity that are inconsistent with developmental level. Lifetime prevalence is "
            "approximately 5% in children (Polanczyk et al. 2007) and 2.5-3% in adults globally. "
            "ADHD is among the most heritable psychiatric conditions (heritability ~75%). "
            "Neurobiologically, ADHD involves hypofunction of mesocortical dopamine and noradrenaline "
            "circuits projecting to the prefrontal cortex, impairing executive control, working memory, "
            "and response inhibition (Barkley's inhibitory control model).\n\n"
            "Non-invasive neuromodulation — particularly tDCS targeting the left DLPFC — represents "
            "an emerging adjunct to pharmacotherapy and behavioral interventions. A 2021 systematic "
            "review (Westwood et al.) of tDCS in ADHD (N=310 across trials) confirmed moderate effect "
            "sizes for attention and executive function outcomes. taVNS is under investigation for "
            "ADHD-related emotional dysregulation via noradrenergic upregulation."
        ),

        pathophysiology=(
            "ADHD pathophysiology centers on hypofunction of the mesocortical dopamine (DA) and "
            "noradrenaline (NA) systems. Dopamine depletion in the prefrontal-striatal axis impairs "
            "the signal-to-noise ratio in DLPFC circuits, reducing inhibitory control and working "
            "memory capacity. The catecholamine hypothesis (Arnsten) proposes that suboptimal DA/NA "
            "levels impair postsynaptic signaling at prefrontal D1 and alpha-2A adrenoreceptors.\n\n"
            "Neuroimaging reveals: (1) reduced volume and cortical thickness in DLPFC, ACC, caudate, "
            "and cerebellar vermis (Shaw et al. 2007 — delayed cortical maturation by ~3 years); "
            "(2) DLPFC and right inferior frontal gyrus (rIFG) hypoactivation during tasks demanding "
            "response inhibition (Stop Signal, Go/No-Go); (3) Default Mode Network (DMN) failure to "
            "deactivate during cognitive tasks, causing attentional intrusions (Sonuga-Barke & "
            "Castellanos 2007 — DMN interference model).\n\n"
            "The triple network model in ADHD identifies: CEN hypofunction (DLPFC/parietal), "
            "DMN hyperactivation/intrusion, and SN impaired switching. Abnormal CEN-DMN "
            "anticorrelation is a robust ADHD neuroimaging biomarker. Reward circuit dysfunction "
            "(ventral striatum, OFC) underlies motivational deficits and delay aversion."
        ),

        core_symptoms=[
            "Inattention — failure to sustain attention, easily distracted by extraneous stimuli",
            "Disorganization — poor planning, losing materials, difficulty with multi-step tasks",
            "Hyperactivity — fidgeting, excessive motor activity, difficulty remaining seated (prominent in children, internalized in adults)",
            "Impulsivity — blurting out answers, difficulty waiting turn, interrupting",
            "Executive dysfunction — poor planning, working memory deficits, cognitive inflexibility",
            "Emotional dysregulation — low frustration tolerance, irritability, mood lability (prominent in adult ADHD)",
            "Delay aversion and motivation deficits — difficulty sustaining effort without immediate reward",
        ],

        non_motor_symptoms=[
            "Sleep disturbance — delayed sleep phase, circadian dysregulation (prevalence ~70% in ADHD)",
            "Emotional lability and rejection-sensitive dysphoria",
            "Low self-esteem and demoralization from chronic underperformance",
            "Social relationship difficulties — impulsive social behavior, poor turn-taking",
            "Academic and occupational underachievement disproportionate to intellectual ability",
            "Comorbid anxiety (50%), depression (30%), substance use disorders (elevated risk in adult ADHD)",
        ],

        key_brain_regions=[
            "Dorsolateral Prefrontal Cortex (DLPFC) — bilateral",
            "Anterior Cingulate Cortex (ACC) / Supplementary Motor Area (SMA)",
            "Right Inferior Frontal Gyrus (rIFG) — response inhibition",
            "Caudate Nucleus / Striatum",
            "Inferior Parietal Lobule (IPL)",
            "Cerebellum (vermis) — timing and attention",
        ],

        brain_region_descriptions={
            "Dorsolateral Prefrontal Cortex (DLPFC) — bilateral": "Primary dysfunction site in ADHD. DLPFC mediates working memory and top-down cognitive control. DA/NA hypofunction impairs prefrontal signal quality. Primary tDCS anodal target.",
            "Anterior Cingulate Cortex (ACC) / Supplementary Motor Area (SMA)": "ACC mediates conflict monitoring, error detection, and sustained attention. Hypoactive in ADHD. SMA involved in motor inhibition — relevant to hyperactive symptoms.",
            "Right Inferior Frontal Gyrus (rIFG) — response inhibition": "Hypoactive in ADHD during Stop Signal tasks. Mediates inhibitory control. Cathodal stimulation has been trialed for impulsivity reduction.",
            "Caudate Nucleus / Striatum": "Dopamine-depleted in ADHD. Impaired reward prediction and response selection. Explains delay aversion and motivation deficits. Reduced caudate volume on MRI is a replicated biomarker.",
            "Inferior Parietal Lobule (IPL)": "Part of dorsal attention network. Hypoactive in inattentive ADHD. Mediates attentional reorienting and stimulus detection.",
            "Cerebellum (vermis)": "Timing and temporal processing. Volume reduction documented in ADHD. Contributes to impaired internal timing and motor sequence learning.",
        },

        network_profiles=[
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "PRIMARY NETWORK IN ADHD. DLPFC and inferior parietal hypofunction impair working memory, "
                "cognitive control, response inhibition, and sustained attention. Mesocortical dopamine "
                "depletion directly reduces prefrontal signal quality. CEN upregulation via anodal tDCS "
                "is the primary therapeutic mechanism of neuromodulation in ADHD.",
                primary=True, severity="severe",
                evidence_note="Castellanos et al. 2002; multiple fMRI studies of inhibitory control in ADHD",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN fails to deactivate during cognitive demands in ADHD, producing attentional intrusions "
                "and mind-wandering. Abnormal CEN-DMN anticorrelation is a key ADHD biomarker on resting-state fMRI. "
                "Sonuga-Barke & Castellanos (2007) DMN interference model explains inattentive symptoms.",
                severity="severe",
                evidence_note="Sonuga-Barke & Castellanos (2007) Neuroscience & Biobehavioral Reviews. PMID: 17764092",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPO,
                "Impaired salience detection and network switching. SN normally gates transitions between "
                "DMN (rest) and CEN (task). SN hypofunction in ADHD allows DMN to persist during task "
                "demands. ACC hypoactivity contributes to impaired conflict monitoring and error correction.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Dorsal attention network (DLPFC-IPS) and ventral attention network (rTPJ-rIFG) both "
                "hypoactive in ADHD. Impaired voluntary attention orientation (dorsal) and alerting to "
                "novel stimuli (ventral). Explains inattentive and distractibility symptoms.",
                severity="severe",
                evidence_note="Attention network dysfunction in ADHD; Fan et al. attention network test",
            ),
        ],

        primary_network=NetworkKey.CEN,

        fnon_rationale=(
            "In ADHD, the primary dysfunctional network is the Central Executive Network (CEN), "
            "driven by mesocortical dopamine/noradrenaline hypofunction impairing DLPFC-mediated "
            "cognitive control. The FNON framework directs primary tDCS stimulation at the DLPFC "
            "(bilateral anodal for combined type; left DLPFC for inattentive type) to upregulate CEN "
            "excitability and restore CEN-DMN anticorrelation. Cognitive training performed concurrently "
            "with tDCS exploits activity-dependent neuroplasticity (Staresina et al.). "
            "taVNS is an adjunct modality targeting noradrenergic upregulation via NTS-LC pathways, "
            "with particular relevance for emotional dysregulation and comorbid anxiety."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="ina",
                label="ADHD-I — Predominantly Inattentive",
                description="Inattention dominant; difficulty sustaining focus, easily distracted, chronic disorganization. Hypo-dopaminergic prefrontal-parietal circuit dysfunction.",
                key_features=["Inattention", "Disorganization", "Poor working memory", "Forgetfulness", "Slow cognitive tempo"],
                primary_networks=[NetworkKey.CEN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.CES],
                tdcs_target="Left DLPFC anodal (F3) + right supraorbital or shoulder cathode",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="hyp",
                label="ADHD-HI — Predominantly Hyperactive/Impulsive",
                description="Hyperactivity and impulsivity dominant; motor restlessness, poor inhibitory control, impulsive decision-making. More prominent in children; often transitions to combined type.",
                key_features=["Hyperactivity", "Impulsivity", "Poor inhibition", "Motor restlessness", "Risk-taking behavior"],
                primary_networks=[NetworkKey.CEN, NetworkKey.SN],
                secondary_networks=[NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.CES],
                tdcs_target="Right DLPFC/rIFG cathodal for impulsivity + left DLPFC anodal",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="com",
                label="ADHD-C — Combined Presentation",
                description="Both inattention and hyperactivity/impulsivity criteria fully met. Most common adult ADHD presentation. Greatest functional impairment.",
                key_features=["Mixed inattention + hyperactivity", "Executive dysfunction", "Emotional dysregulation", "Motivational deficits"],
                primary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.ATTENTION, NetworkKey.SN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Bilateral DLPFC anodal (F3/F4) — combined protocol",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="adt",
                label="Adult ADHD — Late Presentation",
                description="ADHD diagnosed in adulthood with prominent executive dysfunction, emotional dysregulation, and occupational/relational impairment. Hyperactivity often internalized as restlessness and mental overactivity.",
                key_features=["Executive dysfunction", "Emotional dysregulation", "Chronic underachievement", "Internalized restlessness", "Comorbid anxiety or depression"],
                primary_networks=[NetworkKey.CEN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.DMN, NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.TAVNS, Modality.CES],
                tdcs_target="Left DLPFC anodal; add taVNS for emotional dysregulation",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="asrs",
                name="Adult ADHD Self-Report Scale v1.1",
                abbreviation="ASRS-v1.1",
                domains=["inattention", "hyperactivity", "impulsivity", "executive_function"],
                timing="baseline",
                evidence_pmid="15841682",
                notes="WHO-developed 18-item self-report scale. 6-item screener (Part A) highly specific. Primary ADHD symptom monitoring tool in adults.",
            ),
            AssessmentTool(
                scale_key="caars",
                name="Conners' Adult ADHD Rating Scales",
                abbreviation="CAARS",
                domains=["inattention", "hyperactivity", "impulsivity", "self_concept"],
                timing="baseline",
                evidence_pmid="10591285",
                notes="Clinician-administered and self-report versions. Normative data for adults. Includes observer-report form for partner/supervisor rating.",
            ),
            AssessmentTool(
                scale_key="brief2",
                name="Behavior Rating Inventory of Executive Function — 2nd Edition",
                abbreviation="BRIEF-2",
                domains=["inhibition", "cognitive_flexibility", "working_memory", "planning", "organization"],
                timing="baseline",
                evidence_pmid="11385981",
                notes="Ecological assessment of executive function in daily life. Critical for capturing ADHD impact on real-world functioning.",
            ),
            AssessmentTool(
                scale_key="cpt3",
                name="Conners' Continuous Performance Test — 3rd Edition",
                abbreviation="CPT-3",
                domains=["sustained_attention", "impulsivity", "vigilance", "detectability"],
                timing="baseline",
                evidence_pmid="16939757",
                notes="Objective neuropsychological measure of sustained attention. Useful for pre/post stimulation cognitive tracking. Not diagnostic alone.",
            ),
            AssessmentTool(
                scale_key="moca",
                name="Montreal Cognitive Assessment",
                abbreviation="MoCA",
                domains=["cognition", "attention", "executive_function", "working_memory"],
                timing="baseline",
                evidence_pmid="15817019",
                notes="Cognitive screening; useful to exclude MCI/dementia mimicking ADHD in adults >=50 years. Score <26 warrants further evaluation.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Screen for comorbid depression — prevalent in adult ADHD (30%). Score >=10 = moderate depression.",
            ),
        ],

        baseline_measures=[
            "ASRS-v1.1 (primary ADHD self-report measure — 18 items)",
            "CAARS (Conners' Adult ADHD Rating Scales — clinician + self-report)",
            "BRIEF-2 (executive function in daily life)",
            "CPT-3 (objective sustained attention assessment)",
            "PHQ-9 and GAD-7 (comorbid mood/anxiety screen)",
            "SOZO PRS (attention, executive function, mood, sleep — 0-10)",
            "Medication state documentation at baseline",
        ],

        followup_measures=[
            "ASRS-v1.1 at Week 4 and Week 8-10",
            "BRIEF-2 at Week 8-10",
            "CPT-3 at Week 8-10 (objective attention)",
            "SOZO PRS at each session (brief) and end of block (full)",
            "PHQ-9 monitoring at each session (comorbid depression)",
            "Adverse event documentation at every session",
        ],

        inclusion_criteria=[
            "DSM-5 diagnosis of ADHD (any presentation: inattentive, hyperactive-impulsive, combined)",
            "Age 16-65 years",
            "ASRS-v1.1 score in clinically significant range (Part A >=4/6 items positive)",
            "Stable stimulant or non-stimulant medication regimen for >=4 weeks (or medication-naive)",
            "Capacity to provide informed consent",
            "Adequate skin integrity at electrode placement sites",
        ],

        exclusion_criteria=[
            "Active psychosis or psychotic features",
            "Bipolar disorder Type I (relative exclusion — Doctor assessment required; anodal tDCS risk of behavioral activation)",
            "Intellectual disability (IQ <70)",
            "Active substance use disorder (current use of illicit stimulants)",
            "Significant traumatic brain injury history affecting electrode placement regions",
            "Currently receiving ECT",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS,

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "precaution",
                "Stimulant medications (methylphenidate, dexamphetamine) modulate cortical excitability and may interact with tDCS-induced neuroplasticity. Document medication type and dose at every session. Maintain consistent dosing schedule during treatment block.",
                "moderate",
                "Nitsche MA et al. (2006) methylphenidate and tDCS interaction; pharmacological interaction literature",
            ),
            make_safety(
                "monitoring",
                "Monitor for activation of hypomanic or manic symptoms, particularly in patients with subthreshold bipolar features. Discontinue and refer if behavioral activation or mood elevation emerges beyond baseline.",
                "moderate",
                "Clinical precaution for frontal tDCS in patients with bipolar spectrum features",
            ),
            make_safety(
                "precaution",
                "Administer tDCS during or immediately before cognitive training task to maximize activity-dependent neuroplasticity effects. Idle sessions without concurrent cognitive engagement reduce protocol efficacy.",
                "low",
                "Staresina et al. activity-dependent tDCS neuroplasticity principles",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Dorsolateral Prefrontal Cortex", "DLPFC", "bilateral",
                "Bilateral DLPFC anodal tDCS enhances mesocortical dopaminergic/noradrenergic signaling, "
                "improving working memory, attention, and response inhibition. Multiple pilot RCTs "
                "(Sotnikova 2017, Breitling 2010) demonstrate attention improvements in adult ADHD. "
                "Left DLPFC anodal (F3) + right cathode is standard; bilateral F3/F4 anodal for combined type.",
                "C-ADHD — Attention & Executive Protocol",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve",
                target_abbreviation="taVNS",
                laterality="left",
                rationale="taVNS activates NTS-LC-prefrontal noradrenergic pathways, upregulating NA at "
                          "prefrontal alpha-2A receptors (same receptor target as atomoxetine). Relevant for "
                          "adult ADHD with emotional dysregulation and comorbid anxiety. Investigational in ADHD.",
                protocol_label="TAVNS-ADHD — Noradrenergic Adjunct",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-ADHD", label="Attention & Executive Function — DLPFC Protocol", modality=Modality.TDCS,
                target_region="Dorsolateral Prefrontal Cortex", target_abbreviation="DLPFC",
                phenotype_slugs=["ina", "com", "adt"],
                network_targets=[NetworkKey.CEN, NetworkKey.ATTENTION],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC) or F3+F4 bilateral for combined type",
                    "cathode": "Fp2 (right supraorbital) or Fz or right shoulder reference",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15 over 3 weeks",
                    "electrode_size": "35 cm2",
                    "current_density": "0.057 mA/cm2",
                    "note": "Administer concurrently with cognitive training task (attention/working memory) for activity-dependent enhancement",
                },
                rationale="Left DLPFC anodal tDCS upregulates CEN excitability, reducing DMN intrusion and "
                          "improving sustained attention and working memory. Westwood et al. (2021) systematic "
                          "review (N=310): moderate effect for attention outcomes. Sotnikova et al. (2017) "
                          "demonstrated DLPFC tDCS improvements in executive function in children with ADHD. "
                          "Breitling et al. (2010) demonstrated improvements in adult ADHD. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="C-ADHD-INH", label="Inhibitory Control — Right DLPFC Protocol", modality=Modality.TDCS,
                target_region="Right Inferior Frontal Gyrus / Right DLPFC", target_abbreviation="rIFG/rDLPFC",
                phenotype_slugs=["hyp", "com"],
                network_targets=[NetworkKey.CEN, NetworkKey.SN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "F4 (right DLPFC) or AF8 (right IFG approximation)",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                    "note": "Right DLPFC cathodal targets impulsivity via rIFG inhibitory control circuit. Combine with Stop Signal Task during stimulation.",
                },
                rationale="Right DLPFC cathodal tDCS may reduce hyperactivity and impulsivity by modulating "
                          "rIFG inhibitory control circuitry. Emerging pilot evidence. "
                          "Bilateral montage (anodal left + cathodal right) is the standard for combined type. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="TAVNS-ADHD", label="taVNS — Emotional Dysregulation Adjunct", modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve", target_abbreviation="taVNS",
                phenotype_slugs=["adt", "com"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN, NetworkKey.CEN],
                parameters={
                    "device": "NEMOS (tVNS Technologies) or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "200-250 us",
                    "intensity": "Below pain threshold (0.5-4.0 mA)",
                    "duration": "30 min",
                    "sessions": "Daily adjunct during tDCS block",
                    "electrode_placement": "Left cymba conchae",
                },
                rationale="taVNS modulates NTS-LC-prefrontal noradrenergic pathways, replicating the "
                          "mechanism of atomoxetine (non-stimulant ADHD treatment) via non-pharmacological means. "
                          "Relevant for adult ADHD with emotional dysregulation, anxiety comorbidity, and "
                          "stimulant non-responders. Investigational in ADHD — limited published data.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=20,
                notes="Investigational in ADHD. Off-label. May be particularly beneficial as adjunct for "
                      "adult ADHD with prominent emotional dysregulation.",
            ),
            ProtocolEntry(
                protocol_id="CES-ADHD", label="CES — Sleep, Focus & Anxiety Adjunct", modality=Modality.CES,
                target_region="Bilateral earlobe electrodes", target_abbreviation="CES",
                phenotype_slugs=["ina", "hyp", "com", "adt"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim AID",
                    "frequency": "0.5 Hz",
                    "intensity": "100-200 uA",
                    "duration": "40-60 min",
                    "sessions": "Daily during treatment block or home use",
                },
                rationale="Alpha-Stim CES has FDA clearance for anxiety, depression, and insomnia. In ADHD, "
                          "addresses comorbid sleep disturbance (prevalent ~70%), anxiety, and hyperarousal. "
                          "Reduces emotional dysregulation as adjunct to DLPFC tDCS. Limited ADHD-specific RCT data; "
                          "inferred from anxiety/insomnia evidence base.",
                evidence_level=EvidenceLevel.LOW, off_label=False, session_count=20,
            ),
        ],

        symptom_network_mapping={
            "Inattention": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Hyperactivity": [NetworkKey.CEN, NetworkKey.SN],
            "Impulsivity": [NetworkKey.CEN, NetworkKey.SN],
            "Working Memory Deficit": [NetworkKey.CEN, NetworkKey.DMN],
            "Emotional Dysregulation": [NetworkKey.LIMBIC, NetworkKey.CEN],
            "Sleep Disturbance": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Motivation Deficit / Delay Aversion": [NetworkKey.LIMBIC, NetworkKey.CEN],
        },

        symptom_modality_mapping={
            "Inattention": [Modality.TDCS],
            "Hyperactivity": [Modality.TDCS, Modality.CES],
            "Impulsivity": [Modality.TDCS],
            "Working Memory Deficit": [Modality.TDCS],
            "Emotional Dysregulation": [Modality.CES, Modality.TAVNS, Modality.TDCS],
            "Sleep Disturbance": [Modality.CES, Modality.TAVNS],
            "Motivation Deficit / Delay Aversion": [Modality.TDCS],
        },

        responder_criteria=[
            ">=30% reduction in ASRS-v1.1 total score from baseline",
            ">=30% improvement in CAARS primary ADHD subscale",
            "Clinically meaningful improvement in SOZO PRS attention domain (>=3 points on 0-10 scale)",
            "Improvement in CPT-3 sustained attention indices at Week 8-10",
        ],

        non_responder_pathway=(
            "For patients classified as non-responders at Week 4:\n"
            "1. Re-evaluate ADHD phenotype — confirm DSM-5 criteria; rule out mimics (anxiety, mood disorder, sleep disorder)\n"
            "2. Confirm consistent medication state during sessions\n"
            "3. Ensure concurrent cognitive training is being performed during tDCS\n"
            "4. Switch montage if suboptimal: bilateral for combined type, unilateral for inattentive\n"
            "5. Add taVNS for adult ADHD with emotional dysregulation component\n"
            "6. Add CES for sleep and anxiety comorbidity\n"
            "7. Doctor review for medication optimization before second treatment block\n"
            "8. Refer to neuropsychologist if cognitive assessment reveals alternative primary diagnosis"
        ),

        evidence_summary=(
            "ADHD has emerging evidence for tDCS — classified as Level B (probable efficacy) in emerging "
            "neuromodulation guidelines. Westwood et al. (2021) systematic review (N=310 across multiple trials): "
            "moderate effect sizes for attention and executive function outcomes. Sotnikova et al. (2017) "
            "RCT in children demonstrated significant DLPFC tDCS improvements on neuropsychological measures. "
            "Breitling et al. (2010) adult ADHD tDCS study showed working memory improvements. "
            "No large multi-site RCT for adult ADHD with ASRS primary outcome. taVNS in ADHD: "
            "investigational — rationale supported by noradrenergic mechanism overlap with atomoxetine. "
            "CES: no dedicated ADHD RCT — inferred from anxiety/insomnia clearance."
        ),

        evidence_gaps=[
            "No large multi-site sham-controlled RCT of tDCS for adult ADHD using ASRS as primary outcome",
            "Stimulant-tDCS pharmacological interaction — limited systematic study",
            "Optimal montage for hyperactive-impulsive vs inattentive subtypes not definitively established",
            "Long-term maintenance of attention improvements after treatment block — no data beyond 1 month",
            "taVNS in ADHD — no published RCT; mechanism-based rationale only",
            "tDCS dose optimization (intensity, duration, sessions) for ADHD — no dose-finding study",
        ],

        references=[
            {
                "authors": "Westwood SJ et al.",
                "year": 2021,
                "title": "A Systematic Review of Transcranial Direct Current Stimulation in Attention-Deficit/Hyperactivity Disorder",
                "journal": "Frontiers in Human Neuroscience",
                "pmid": "33568986",
                "evidence_type": "systematic_review",
            },
            {
                "authors": "Sotnikova A et al.",
                "year": 2017,
                "title": "Transcranial Direct Current Stimulation Modulates Neuronal Networks in Attention Deficit Hyperactivity Disorder",
                "journal": "Frontiers in Human Neuroscience",
                "pmid": "28261072",
                "evidence_type": "rct",
            },
            {
                "authors": "Breitling C et al.",
                "year": 2010,
                "title": "Anodal transcranial direct current stimulation temporarily enhances working memory in adult ADHD",
                "journal": "Journal of Attention Disorders",
                "pmid": "20354211",
                "evidence_type": "rct",
            },
            {
                "authors": "Castellanos FX & Proal E",
                "year": 2012,
                "title": "Large-scale brain systems in ADHD: beyond the prefrontal-striatal model",
                "journal": "Trends in Cognitive Sciences",
                "pmid": "22575726",
                "evidence_type": "narrative_review",
            },
            {
                "authors": "Sonuga-Barke EJ & Castellanos FX",
                "year": 2007,
                "title": "Spontaneous attentional fluctuations in impaired states and pathological conditions: A neurobiological hypothesis",
                "journal": "Neuroscience & Biobehavioral Reviews",
                "pmid": "17764092",
                "evidence_type": "narrative_review",
            },
            {
                "authors": "Kessler RC et al.",
                "year": 2006,
                "title": "The prevalence and correlates of adult ADHD in the United States: Results from the National Comorbidity Survey Replication",
                "journal": "American Journal of Psychiatry",
                "pmid": "16585449",
                "evidence_type": "cohort_study",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        clinical_tips=[
            "Always co-administer a cognitive training task (working memory, sustained attention) during tDCS sessions — activity-dependent neuroplasticity significantly improves outcomes",
            "Document stimulant medication type, dose, and timing at every session — maintain consistent medication state across the treatment block",
            "In adult ADHD with emotional dysregulation, add taVNS as adjunct — addresses the noradrenergic component not directly targeted by DLPFC tDCS",
            "Use CPT-3 at baseline and endpoint to objectively quantify attention changes beyond self-report",
            "Distinguish adult ADHD from bipolar disorder carefully — mood-related behavioral activation during tDCS requires immediate monitoring",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES,
    )
