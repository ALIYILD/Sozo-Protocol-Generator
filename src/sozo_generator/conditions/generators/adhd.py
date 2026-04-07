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

        eeg_reference_table=[
            {"position": "F3", "brain_region": "Left DLPFC", "role": "PRIMARY anodal target — CEN upregulation, working memory, sustained attention", "protocols_using": ["C-ADHD", "C-ADHD-INH", "T3"]},
            {"position": "F4", "brain_region": "Right DLPFC", "role": "Bilateral anodal target (combined type); cathodal target for inhibitory control protocol", "protocols_using": ["C-ADHD", "C-ADHD-INH"]},
            {"position": "Fz", "brain_region": "Midline Frontal / ACC", "role": "ACC proxy — error monitoring, conflict detection, sustained attention switching", "protocols_using": ["C7", "T4"]},
            {"position": "Cz", "brain_region": "Midline Central / Vertex", "role": "SMA/midline motor — hyperactivity modulation; reference electrode site", "protocols_using": ["C7"]},
            {"position": "P3", "brain_region": "Left Posterior Parietal Cortex", "role": "Dorsal attention network node — sustained attention, attentional reorienting", "protocols_using": ["C6"]},
            {"position": "P4", "brain_region": "Right Posterior Parietal Cortex", "role": "Bilateral parietal attention network target", "protocols_using": ["C6"]},
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
                eeg_canonical=["F3", "F4"],
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
                eeg_canonical=["Ear"],
            ),
            StimulationTarget(
                modality=Modality.CES,
                target_region="Bilateral earlobe electrodes (CES)",
                target_abbreviation="CES",
                laterality="bilateral",
                rationale="Alpha-Stim CES FDA-cleared for anxiety, depression, and insomnia. In ADHD, "
                          "addresses sleep disturbance (present in 25-55%), comorbid anxiety, and emotional "
                          "dysregulation. Non-pharmacological adjunct that does not interact with stimulant "
                          "medications. Supports focus and reduces hyperarousal.",
                protocol_label="CES-ADHD — Sleep, Focus & Anxiety Adjunct",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
                eeg_canonical=["bilateral earlobes"],
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
                # -- SOZO Protocol Handbook fields --
                protocol_name="C-ADHD — tDCS Attention & Executive Function DLPFC Protocol",
                clinical_objective="Upregulate CEN excitability to restore sustained attention, working memory, and CEN-DMN anticorrelation",
                primary_targets=["F3 (Left DLPFC — anodal)"],
                secondary_targets=["F4 (Right DLPFC — anodal for combined type)", "Fp2 (right supraorbital — cathodal)"],
                device_name="Newronika HDCkit (2-channel)",
                session_structure="Anodal F3 (or F3+F4 bilateral for combined type); Cathode Fp2 or right shoulder. 2 mA, 20 min. Concurrent cognitive training task.",
                frequency="5 sessions/week",
                duration="20 min per session",
                intensity_dose="2.0 mA (current density 0.057 mA/cm2 with 35 cm2 electrodes)",
                montage_roi="Anode (+): F3 (L-DLPFC). Cathode (−): Fp2 or right shoulder",
                laterality="Left anodal dominant (bilateral for combined type)",
                treatment_course="10–15 sessions over 3 weeks",
                monitoring="ASRS-v1.1 weekly; CPT-3 at baseline and endpoint; medication state documentation; skin integrity",
                expected_response="Improved sustained attention, reduced distractibility, enhanced working memory, reduced DMN intrusion",
                evidence_status="Level B (probable) — Westwood et al. 2021 systematic review (N=310); Sotnikova 2017 RCT; Breitling 2010 RCT",
                cautions="Document stimulant medication timing; monitor for behavioral activation in bipolar spectrum",
                when_to_escalate="If <30% ASRS improvement after 10 sessions, switch montage or add taVNS",
                when_to_stop_modify="Standard tDCS stop criteria; modify to 1.5 mA if skin discomfort",
                clinical_notes_extended="Always co-administer cognitive training task during stimulation for activity-dependent neuroplasticity. Idle sessions reduce efficacy.",
                key_citations=["Westwood et al., 2021", "Sotnikova et al., 2017", "Breitling et al., 2010"],
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
                # -- SOZO Protocol Handbook fields --
                protocol_name="C-ADHD-INH — tDCS Inhibitory Control Right DLPFC Protocol",
                clinical_objective="Modulate rIFG inhibitory control circuitry to reduce impulsivity and hyperactivity",
                primary_targets=["F3 (Left DLPFC — anodal)"],
                secondary_targets=["F4 (Right DLPFC — cathodal)", "AF8 (right IFG approximation)"],
                device_name="Newronika HDCkit (2-channel)",
                session_structure="Anodal F3; Cathodal F4 or AF8. 2 mA, 20 min. Combine with Stop Signal Task.",
                frequency="5 sessions/week",
                duration="20 min per session",
                intensity_dose="2.0 mA",
                montage_roi="Anode (+): F3 (L-DLPFC). Cathode (−): F4 (R-DLPFC) or AF8 (rIFG)",
                laterality="Left anodal / Right cathodal (bilateral asymmetric)",
                treatment_course="10–15 sessions over 3 weeks",
                monitoring="ASRS-v1.1 impulsivity subscale; CPT-3 commission errors; medication state",
                expected_response="Reduced impulsivity, improved response inhibition, decreased hyperactivity",
                evidence_status="Low — emerging pilot evidence for right DLPFC cathodal in ADHD impulsivity",
                cautions="Bilateral montage reverses polarity from standard depression — verify electrode placement",
                when_to_escalate="If no improvement in impulsivity after 10 sessions, consider medication optimization",
                when_to_stop_modify="Standard tDCS stop criteria",
                clinical_notes_extended="Combine with Stop Signal Task or Go/No-Go during stimulation for activity-dependent inhibitory control training.",
                key_citations=["Aron et al., 2004", "Westwood et al., 2021"],
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
                # -- SOZO Protocol Handbook fields --
                protocol_name="TAVNS-ADHD — taVNS Emotional Dysregulation Adjunct",
                clinical_objective="Upregulate noradrenergic tone via NTS-LC pathway; address emotional dysregulation and comorbid anxiety",
                primary_targets=["Auricular branch of vagus nerve → NTS → LC noradrenergic pathway"],
                secondary_targets=["Limbic network (indirect via NTS-LC-cortical projections)"],
                device_name="NEMOS (tVNS Technologies) or Parasym",
                session_structure="Electrode placement on left cymba conchae; 25 Hz, 200–250 µs pulse width; 30 min",
                frequency="Daily adjunct during tDCS block",
                duration="30 min per session",
                intensity_dose="Below pain threshold (0.5–4.0 mA)",
                montage_roi="Left cymba conchae (auricular vagus branch)",
                laterality="Left auricular",
                treatment_course="Daily for duration of tDCS block (3–5 weeks)",
                monitoring="Pain threshold check; heart rate monitoring; emotional dysregulation self-report",
                expected_response="Reduced emotional lability, improved frustration tolerance, reduced comorbid anxiety",
                evidence_status="Low — investigational in ADHD; mechanism parallels atomoxetine (NA upregulation)",
                cautions="No dedicated ADHD RCT; off-label use requires informed consent",
                when_to_escalate="If no emotional dysregulation improvement after 2 weeks, consider pharmacological NA augmentation",
                when_to_stop_modify="Stop if vagal side effects (bradycardia, cough, throat pain)",
                clinical_notes_extended="Mechanism parallels atomoxetine — non-pharmacological NA upregulation via NTS-LC pathway. Particularly relevant for stimulant non-responders.",
                key_citations=["Rong et al., 2016", "Frangos et al., 2015"],
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
                # -- SOZO Protocol Handbook fields --
                protocol_name="CES-ADHD — Alpha-Stim CES Sleep, Focus & Anxiety Adjunct",
                clinical_objective="Address comorbid sleep disturbance, anxiety, and hyperarousal in ADHD",
                primary_targets=["Limbic and autonomic networks via transcranial microcurrent"],
                secondary_targets=["SN downregulation (indirect)"],
                device_name="Alpha-Stim® CS",
                session_structure="Bilateral earlobe clip electrodes; 0.5 Hz; 100–200 µA; 40–60 min",
                frequency="Daily during treatment block or home use",
                duration="40–60 min per session",
                intensity_dose="100–200 µA",
                montage_roi="Bilateral earlobe clip electrodes",
                laterality="Bilateral",
                treatment_course="Daily for 4–6 weeks; maintenance 3×/week",
                monitoring="PSQI sleep quality; GAD-7 anxiety; skin integrity at earlobe sites",
                expected_response="Improved sleep quality, reduced anxiety, decreased hyperarousal",
                evidence_status="Low for ADHD-specific; FDA-cleared for anxiety, depression, insomnia",
                cautions="No dedicated ADHD RCT; inferred from anxiety/insomnia clearance",
                when_to_escalate="If sleep not improving after 2 weeks, add sleep hygiene intervention",
                when_to_stop_modify="Stop if skin irritation at earlobe sites",
                clinical_notes_extended="Non-pharmacological adjunct that does not interact with stimulant medications. Supports focus via sleep and anxiety improvement.",
                key_citations=["Kirsch & Nichols, 2013", "NICE MTG, 2014"],
            ),

            # ── C5-C8: Expanded tDCS protocols ──────────────────────
            ProtocolEntry(
                protocol_id="C5", label="Right IFG/vlPFC — Response Inhibition", modality=Modality.TDCS,
                target_region="Right Inferior Frontal Gyrus / Ventrolateral PFC", target_abbreviation="rIFG/vlPFC",
                phenotype_slugs=["hyp", "com"],
                network_targets=[NetworkKey.CEN, NetworkKey.SN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F6 or AF8 (right IFG / vlPFC)",
                    "cathode": "Left shoulder or Fp1",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                    "note": "Combine with Stop Signal Task or Go/No-Go during stimulation for activity-dependent inhibitory control training",
                },
                rationale="Right IFG is the critical node for response inhibition (Aron et al. 2004). Anodal stimulation over rIFG/vlPFC directly upregulates the inhibitory control circuit hypoactive in ADHD-HI and combined type. Combine with Stop Signal Task for optimal effect. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                protocol_name="C5 — Right IFG/vlPFC Response Inhibition Protocol",
                clinical_objective="Directly upregulate the inhibitory control circuit via rIFG anodal stimulation",
                primary_targets=["F6 or AF8 (Right IFG / vlPFC — anodal)"],
                secondary_targets=["Left shoulder or Fp1 (cathodal)"],
                device_name="Newronika HDCkit (2-channel)",
                session_structure="Anodal F6/AF8 (rIFG); Cathode left shoulder or Fp1. 2 mA, 20 min. Combine with Stop Signal Task.",
                frequency="5 sessions/week",
                duration="20 min per session",
                intensity_dose="2.0 mA",
                montage_roi="Anode (+): F6/AF8 (R-IFG). Cathode (−): left shoulder or Fp1",
                laterality="Right anodal",
                treatment_course="10–15 sessions over 3 weeks",
                monitoring="CPT-3 commission errors; Stop Signal reaction time",
                expected_response="Improved response inhibition, reduced impulsivity on Go/No-Go tasks",
                evidence_status="Low — based on Aron et al. 2004 rIFG model; limited tDCS-specific ADHD data",
                cautions="Right-lateralized anodal — monitor for any mood changes",
                when_to_escalate="If no inhibitory improvement after 10 sessions, switch to bilateral DLPFC montage",
                when_to_stop_modify="Standard tDCS stop criteria",
                clinical_notes_extended="Activity-dependent: always combine with Stop Signal or Go/No-Go task during stimulation.",
                key_citations=["Aron et al., 2004"],
            ),
            ProtocolEntry(
                protocol_id="C6", label="Posterior Parietal — Sustained Attention", modality=Modality.TDCS,
                target_region="Posterior Parietal Cortex", target_abbreviation="PPC",
                phenotype_slugs=["ina", "com", "adt"],
                network_targets=[NetworkKey.ATTENTION, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "P3 or P4 (parietal — attention network node)",
                    "cathode": "Fp2 (right supraorbital)",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                },
                rationale="Posterior parietal cortex is a key dorsal attention network node. Anodal stimulation targets sustained attention deficits — the core impairment in ADHD-inattentive type. Inferior parietal lobule hypoactivation is a consistent ADHD neuroimaging finding. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                protocol_name="C6 — Posterior Parietal Sustained Attention Protocol",
                clinical_objective="Upregulate dorsal attention network via parietal node stimulation for sustained attention deficits",
                primary_targets=["P3 or P4 (Posterior Parietal Cortex — anodal)"],
                secondary_targets=["Fp2 (right supraorbital — cathodal)"],
                device_name="Newronika HDCkit (2-channel)",
                session_structure="Anodal P3/P4; Cathode Fp2. 2 mA, 20 min.",
                frequency="5 sessions/week",
                duration="20 min per session",
                intensity_dose="2.0 mA",
                montage_roi="Anode (+): P3 or P4 (PPC). Cathode (−): Fp2",
                laterality="Left or right parietal (based on dominant attention deficit)",
                treatment_course="10–15 sessions over 3 weeks",
                monitoring="CPT-3 sustained attention indices; ASRS inattention subscale",
                expected_response="Improved sustained attention, reduced distractibility, better attentional reorienting",
                evidence_status="Low — parietal hypoactivation in ADHD is well-documented; tDCS targeting is investigational",
                cautions="Investigational target; limited published ADHD-specific parietal tDCS data",
                when_to_escalate="If no attention improvement, switch to DLPFC primary protocol",
                when_to_stop_modify="Standard tDCS stop criteria",
                clinical_notes_extended="Targets the dorsal attention network directly rather than via prefrontal-parietal projections. May be more effective for pure inattentive type.",
                key_citations=["Castellanos & Proal, 2012"],
            ),
            ProtocolEntry(
                protocol_id="C7", label="ACC — Error Monitoring/Conflict", modality=Modality.TDCS,
                target_region="Anterior Cingulate Cortex / Medial Frontal", target_abbreviation="ACC/MFC",
                phenotype_slugs=["com", "ina", "hyp"],
                network_targets=[NetworkKey.SN, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "Fz (midline frontal — ACC/SMA proxy)",
                    "cathode": "Right mastoid or shoulder",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                },
                rationale="ACC is critical for error monitoring and conflict detection — functions impaired in ADHD. dACC hypoactivation during Flanker and Stroop tasks is a robust ADHD finding. Anodal Fz tDCS targets this deficit. Combine with conflict monitoring tasks. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                protocol_name="C7 — ACC Error Monitoring / Conflict Protocol",
                clinical_objective="Upregulate ACC for improved error monitoring, conflict detection, and attention switching",
                primary_targets=["Fz (Midline frontal — ACC/SMA proxy — anodal)"],
                secondary_targets=["Right mastoid or shoulder (cathodal)"],
                device_name="Newronika HDCkit (2-channel)",
                session_structure="Anodal Fz; Cathode right mastoid or shoulder. 2 mA, 20 min. Combine with Flanker/Stroop task.",
                frequency="5 sessions/week",
                duration="20 min per session",
                intensity_dose="2.0 mA",
                montage_roi="Anode (+): Fz (ACC proxy). Cathode (−): right mastoid",
                laterality="Midline",
                treatment_course="10–15 sessions over 3 weeks",
                monitoring="Flanker/Stroop error rates; ASRS total; CPT-3",
                expected_response="Improved error detection, reduced careless errors, better conflict resolution",
                evidence_status="Low — ACC hypoactivation robust ADHD finding; tDCS targeting investigational",
                cautions="Fz placement requires precise midline positioning",
                when_to_escalate="If no improvement in error monitoring, combine with DLPFC protocol",
                when_to_stop_modify="Standard tDCS stop criteria",
                clinical_notes_extended="Combine with conflict monitoring tasks (Flanker, Stroop) during stimulation for activity-dependent enhancement of ACC function.",
                key_citations=["Bush et al., 1999", "Castellanos & Proal, 2012"],
            ),
            ProtocolEntry(
                protocol_id="C8", label="Temporal/Reward — Delay Discounting", modality=Modality.TDCS,
                target_region="Orbitofrontal / Ventral Temporal (Reward Circuit)", target_abbreviation="OFC/VT",
                phenotype_slugs=["hyp", "com", "adt"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "Fp1 (left orbitofrontal / vmPFC proxy)",
                    "cathode": "Right mastoid or shoulder",
                    "intensity": "1.5 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                },
                rationale="OFC/vmPFC anodal tDCS targets the reward circuit dysfunction underlying delay aversion and excessive delay discounting in ADHD. Ventral striatum-OFC connectivity is reduced in ADHD; surface OFC stimulation modulates this circuit via cortical-subcortical pathways. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                protocol_name="C8 — Temporal/Reward Delay Discounting Protocol",
                clinical_objective="Modulate reward circuit dysfunction underlying delay aversion and motivational deficits",
                primary_targets=["Fp1 (Left OFC / vmPFC proxy — anodal)"],
                secondary_targets=["Right mastoid or shoulder (cathodal)"],
                device_name="Newronika HDCkit (2-channel)",
                session_structure="Anodal Fp1; Cathode right mastoid or shoulder. 1.5 mA, 20 min.",
                frequency="5 sessions/week",
                duration="20 min per session",
                intensity_dose="1.5 mA",
                montage_roi="Anode (+): Fp1 (OFC/vmPFC). Cathode (−): right mastoid",
                laterality="Left prefrontal",
                treatment_course="10–15 sessions over 3 weeks",
                monitoring="Delay discounting task performance; motivation self-report",
                expected_response="Reduced delay aversion, improved delayed gratification, enhanced motivation",
                evidence_status="Low — reward circuit dysfunction well-documented in ADHD; OFC tDCS investigational",
                cautions="Lower intensity (1.5 mA) due to Fp1 proximity to orbital structures; watch for phosphenes",
                when_to_escalate="If no motivational improvement, reassess for depression comorbidity",
                when_to_stop_modify="Standard tDCS stop criteria; reduce intensity if phosphenes reported",
                clinical_notes_extended="Targets the motivational deficit dimension of ADHD — delay aversion and reduced effort investment. Combine with reward-based cognitive training.",
                key_citations=["Sonuga-Barke et al., 2007"],
            ),

            # ── T3-T4: Expanded TPS protocols ──────────────────────
            ProtocolEntry(
                protocol_id="T3", label="TPS — DLPFC Executive Function", modality=Modality.TPS,
                target_region="Dorsolateral Prefrontal Cortex (deep)", target_abbreviation="DLPFC-deep",
                phenotype_slugs=["ina", "com", "adt"],
                network_targets=[NetworkKey.CEN, NetworkKey.ATTENTION],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Left DLPFC deep layers (neuronavigation-guided)",
                    "pulses": "300-400 per session",
                    "frequency": "5 Hz",
                    "energy": "0.20-0.25 mJ/mm2",
                    "sessions": "6-9 over 3 weeks",
                },
                rationale="TPS deep DLPFC stimulation targets the CEN hypoactivation central to ADHD executive dysfunction. Acoustic energy reaches deeper prefrontal layers than surface tDCS, potentially engaging prefrontal-striatal dopaminergic circuits. OFF-LABEL — no ADHD-specific TPS data.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=9,
                protocol_name="T3 — TPS DLPFC Executive Function Protocol",
                clinical_objective="Deep DLPFC stimulation via focused acoustic pulses for CEN upregulation beyond surface tDCS reach",
                primary_targets=["Left DLPFC deep layers (neuronavigation-guided)"],
                secondary_targets=["Prefrontal-striatal dopaminergic circuit (indirect)"],
                device_name="NEUROLITH® TPS System (Storz Medical)",
                session_structure="Neuronavigation setup → DLPFC targeted (300–400 pulses, 5 Hz, 0.20–0.25 mJ/mm2)",
                frequency="2–3 sessions/week",
                duration="~20 min per session (including neuronavigation setup)",
                intensity_dose="0.20–0.25 mJ/mm2, 300–400 pulses per session",
                montage_roi="Left DLPFC (neuronavigation-guided deep target)",
                laterality="Left dominant",
                treatment_course="6–9 sessions over 3 weeks",
                monitoring="ASRS-v1.1; BRIEF-2; CPT-3 at endpoint",
                expected_response="Enhanced executive function, improved working memory, reduced attention deficits",
                evidence_status="Low — no ADHD-specific TPS data; extrapolated from TPS mechanism and DLPFC target rationale",
                cautions="Off-label; Doctor authorization mandatory; no ADHD-specific safety data for TPS",
                when_to_escalate="If no improvement after 6 sessions, reassess protocol rationale",
                when_to_stop_modify="Standard TPS stop criteria; headache or discomfort triggers review",
                clinical_notes_extended="TPS reaches deeper prefrontal layers than surface tDCS — potentially engages prefrontal-striatal dopaminergic circuits. Experimental for ADHD.",
                key_citations=["Beisteiner et al., 2020"],
            ),
            ProtocolEntry(
                protocol_id="T4", label="TPS — ACC Attention/Conflict", modality=Modality.TPS,
                target_region="Anterior Cingulate Cortex (deep)", target_abbreviation="ACC-deep",
                phenotype_slugs=["com", "ina", "hyp"],
                network_targets=[NetworkKey.SN, NetworkKey.CEN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Dorsal ACC / SMA (neuronavigation-guided — deep target)",
                    "pulses": "300-400 per session",
                    "frequency": "5 Hz",
                    "energy": "0.20-0.25 mJ/mm2",
                    "sessions": "6-9 over 3 weeks",
                },
                rationale="TPS targeting dACC addresses the error monitoring and conflict detection deficits in ADHD at depth. ACC is the SN hub responsible for attention switching — its hypoactivation in ADHD drives the CEN-DMN anticorrelation failure. OFF-LABEL — experimental.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=9,
                protocol_name="T4 — TPS ACC Attention/Conflict Protocol",
                clinical_objective="Deep ACC stimulation to address error monitoring and CEN-DMN switching deficits",
                primary_targets=["Dorsal ACC / SMA (neuronavigation-guided deep target)"],
                secondary_targets=["SN hub (indirect via ACC modulation)"],
                device_name="NEUROLITH® TPS System (Storz Medical)",
                session_structure="Neuronavigation setup → dACC/SMA targeted (300–400 pulses, 5 Hz, 0.20–0.25 mJ/mm2)",
                frequency="2–3 sessions/week",
                duration="~20 min per session",
                intensity_dose="0.20–0.25 mJ/mm2, 300–400 pulses per session",
                montage_roi="Dorsal ACC (neuronavigation-guided deep target)",
                laterality="Midline",
                treatment_course="6–9 sessions over 3 weeks",
                monitoring="Flanker/Stroop task performance; ASRS-v1.1",
                expected_response="Improved attention switching, reduced error monitoring deficits, restored CEN-DMN anticorrelation",
                evidence_status="Low — experimental; ACC role in ADHD well-documented but TPS targeting is novel",
                cautions="Off-label; experimental protocol; Doctor authorization mandatory",
                when_to_escalate="If no improvement, combine with DLPFC TPS (T3) for dual-target approach",
                when_to_stop_modify="Standard TPS stop criteria",
                clinical_notes_extended="ACC is the SN hub responsible for CEN-DMN switching — its hypoactivation in ADHD drives the core network anticorrelation failure.",
                key_citations=["Beisteiner et al., 2020", "Bush et al., 1999"],
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
            "CES: no dedicated ADHD RCT — inferred from anxiety/insomnia clearance. "
            "| Evidence counts (published papers): tDCS=20, TMS=15, tACS=5, PEMF=5, TPS=2. "
            "Best modalities: tDCS (DLPFC), TMS."
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


        # --- Auto-enriched: PlatoScience Variants ---
        platoscience_variants=[
            PlatoScienceVariant(
                variant_id="C-ADHD-PS", protocol_id="C-ADHD",
                label="PlatoScience Attention & Executive Function — DLPFC Protocol",
                parameters={"program": "Think", "electrode_config": "F3 (left DLPFC) or F3+F4 bilateral for combined type", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C-ADHD protocol. PlatoScience Think program.",
            ),
            PlatoScienceVariant(
                variant_id="C-ADHD-INH-PS", protocol_id="C-ADHD-INH",
                label="PlatoScience Inhibitory Control — Right DLPFC Protocol",
                parameters={"program": "Think", "electrode_config": "F3 (left DLPFC)", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C-ADHD-INH protocol. PlatoScience Think program.",
            ),
            PlatoScienceVariant(
                variant_id="C5-PS", protocol_id="C5",
                label="PlatoScience Right IFG/vlPFC — Response Inhibition",
                parameters={"program": "Focus", "electrode_config": "F6 or AF8 (right IFG)", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C5 protocol. PlatoScience Focus program. Combine with Stop Signal Task.",
            ),
            PlatoScienceVariant(
                variant_id="C6-PS", protocol_id="C6",
                label="PlatoScience Posterior Parietal — Sustained Attention",
                parameters={"program": "Focus", "electrode_config": "P3 or P4 (parietal)", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C6 protocol. PlatoScience Focus program.",
            ),
            PlatoScienceVariant(
                variant_id="C7-PS", protocol_id="C7",
                label="PlatoScience ACC — Error Monitoring/Conflict",
                parameters={"program": "Focus", "electrode_config": "Fz (midline frontal — ACC proxy)", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C7 protocol. PlatoScience Focus program.",
            ),
            PlatoScienceVariant(
                variant_id="C8-PS", protocol_id="C8",
                label="PlatoScience Temporal/Reward — Delay Discounting",
                parameters={"program": "Think", "electrode_config": "Fp1 (left OFC/vmPFC proxy)", "intensity": "1.5 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C8 protocol. PlatoScience Think program.",
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

        adverse_event_grades=SHARED_ADVERSE_EVENT_GRADES,
        side_effects=SHARED_SIDE_EFFECTS,
        governance_rules=SHARED_GOVERNANCE_RULES,
    )
