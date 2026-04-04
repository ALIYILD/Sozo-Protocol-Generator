"""
Autism Spectrum Disorder (ASD) — Complete condition generator.

Key references:
- D'Urso G et al. (2015) tDCS in autism spectrum disorder — Neuropsychological Rehabilitation. PMID: 25658898
- Enticott PG et al. (2014) TMS and autism — Brain Stimulation. PMID: 24034847
- Schneider HD & Hopp JP (2011) tDCS in ASD — European Journal of Neuroscience. PMID: 21692897
- Bal VH et al. (2019) Social communication and ASD — Current Opinion in Psychiatry. PMID: 31116097
- Lord C et al. (2000) ADOS: Autism Diagnostic Observation Schedule — Journal of Autism and Developmental Disorders. PMID: 11055457

IMPORTANT: tDCS in ASD is investigational/off-label. Clearly mark as research-level evidence.
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


def build_asd_condition() -> ConditionSchema:
    """Build the complete Autism Spectrum Disorder condition schema."""
    return ConditionSchema(
        slug="asd",
        display_name="Autism Spectrum Disorder",
        icd10="F84.0",
        aliases=["ASD", "autism", "autistic spectrum", "Asperger's", "high-functioning autism"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Autism Spectrum Disorder (ASD) is a neurodevelopmental condition characterized by "
            "persistent differences in social communication and interaction, and restricted or "
            "repetitive patterns of behavior, interests, or activities. ASD affects approximately "
            "1 in 54 children (CDC 2020 data). Severity is classified into three DSM-5 levels: "
            "Level 1 (requiring support), Level 2 (requiring substantial support), and Level 3 "
            "(requiring very substantial support).\n\n"
            "ASD neurobiological model: dysregulation of the social brain network, involving the "
            "temporal-parietal junction (TPJ), superior temporal sulcus (STS), amygdala, and medial "
            "prefrontal cortex (mPFC). Functional connectivity abnormalities — both local "
            "hyperconnectivity and long-range hypoconnectivity — are consistent neuroimaging findings.\n\n"
            "CLINICAL IMPORTANT NOTE: tDCS and all neuromodulation in ASD is investigational and "
            "off-label. Evidence is based on small pilot studies. It should only be delivered within "
            "a research-informed clinical framework with explicit informed consent, appropriate "
            "ethical review where indicated, and clear patient/family education about the investigational "
            "nature of the treatment."
        ),

        pathophysiology=(
            "ASD pathophysiology is heterogeneous, reflecting multiple genetic and environmental "
            "trajectories converging on shared neural phenotypes. Key mechanisms:\n\n"
            "(1) Excitation-Inhibition (E/I) imbalance: reduced GABAergic inhibition relative to "
            "glutamatergic excitation in cortical circuits — particularly sensory and prefrontal. "
            "This explains sensory hypersensitivity, repetitive behaviors, and seizure vulnerability.\n\n"
            "(2) Social brain network dysregulation: reduced functional connectivity in the 'social "
            "brain' network — TPJ, STS, amygdala, mPFC. Impaired 'theory of mind' (mentalizing) "
            "capacity, reduced social attention, and face processing deficits.\n\n"
            "(3) Default Mode Network (DMN) atypicality: DMN hyperactivation during social and "
            "mentalizing tasks is documented in ASD, reflecting atypical self-referential processing "
            "and reduced social cognition network engagement.\n\n"
            "(4) Salience Network dysregulation: reduced social salience — atypical attention to "
            "social cues (faces, eyes, voices) — drives core social communication deficits. "
            "Amygdala hypoactivation to social stimuli contrasts with hyperactivation to threat.\n\n"
            "(5) Long-range hypoconnectivity: reduced long-range cortical connectivity (fronto-temporal, "
            "fronto-parietal) limits integration of distributed processing networks needed for complex "
            "social cognition and executive function."
        ),

        core_symptoms=[
            "Social communication and interaction deficits — reduced reciprocal social-emotional engagement",
            "Reduced sharing of interest, emotion, or affect",
            "Impaired nonverbal communication — reduced eye contact, facial expression, gesture use",
            "Deficits in developing, maintaining, and understanding relationships",
            "Restricted, repetitive behaviors — stereotypies, insistence on sameness, ritualized patterns",
            "Restricted interests with abnormal intensity or focus",
            "Hyper- or hyporeactivity to sensory input (visual, auditory, tactile)",
        ],

        non_motor_symptoms=[
            "Intellectual disability (co-occurring in ~30-50% of ASD)",
            "ADHD (co-occurring in ~50-70%)",
            "Anxiety disorders (co-occurring in ~40-80%)",
            "Sleep disturbance (co-occurring in ~50-80%)",
            "Depression (particularly adolescent and adult ASD)",
            "Epilepsy (co-occurring in ~20-30%)",
            "GI disorders (functional GI complaints common)",
        ],

        key_brain_regions=[
            "Temporal-Parietal Junction (TPJ) — mentalizing",
            "Superior Temporal Sulcus (STS) — biological motion and social processing",
            "Amygdala (bilateral)",
            "Medial Prefrontal Cortex (mPFC)",
            "Dorsolateral Prefrontal Cortex (DLPFC)",
            "Mirror Neuron System (IFG, premotor cortex)",
        ],

        brain_region_descriptions={
            "Temporal-Parietal Junction (TPJ) — mentalizing": "Key node of the social brain and mentalizing network. Processes belief attribution, social perspective-taking, and 'theory of mind'. Hypoactivation in ASD during mentalizing tasks. Primary tDCS target for social cognition.",
            "Superior Temporal Sulcus (STS) — biological motion and social processing": "Processes biological motion, facial expression, joint attention, and voice processing. Hypoactivation in ASD. Connected to TPJ in social brain network.",
            "Amygdala (bilateral)": "Atypical function in ASD: reduced response to social stimuli but preserved/enhanced response to threat. Atypical social fear learning. Reduced amygdala-PFC connectivity impairs social affect regulation.",
            "Medial Prefrontal Cortex (mPFC)": "DMN hub involved in self-referential processing and mentalizing. Hyperactivated during rest in ASD; reduced task-related activation during social cognition.",
            "Dorsolateral Prefrontal Cortex (DLPFC)": "Executive function and cognitive control. DLPFC anodal tDCS targets co-occurring executive dysfunction (planning, working memory, flexibility). Also relevant for co-occurring ADHD features.",
            "Mirror Neuron System (IFG, premotor cortex)": "Atypical mirror neuron function in ASD may contribute to impaired imitation, social understanding, and empathy. IFG involvement in language and communication.",
        },

        network_profiles=[
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPO,
                "PRIMARY NETWORK IN ASD. The social brain network (a subset of SN) is dysregulated in "
                "ASD — reduced activation of TPJ, STS, and mPFC during social tasks, combined with "
                "atypical amygdala responses to social stimuli. Social salience — attention to faces, "
                "eyes, and social cues — is diminished, driving core social communication deficits. "
                "TPJ anodal tDCS is the primary social cognition target.",
                primary=True, severity="severe",
                evidence_note="Social brain network hypofunction in ASD; multiple fMRI studies",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation during social and mentalizing tasks in ASD reflects atypical "
                "self-referential processing pattern. Reduced DMN deactivation during social tasks "
                "impairs engagement of social cognition networks. DMN-SN anticorrelation is altered.",
                severity="moderate",
                evidence_note="DMN atypicality in ASD; Kennedy DP & Courchesne E 2008",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "Executive dysfunction is highly prevalent in ASD, including working memory deficits, "
                "cognitive inflexibility, and planning impairments. DLPFC hypofunction drives executive "
                "impairment and is the target of DLPFC anodal tDCS. Co-occurring ADHD amplifies CEN "
                "hypofunction.",
                severity="moderate",
                evidence_note="Executive dysfunction in ASD; BRIEF-2 profiles in ASD",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Atypical attention in ASD: reduced social attention (to faces, eyes); enhanced "
                "attention to detail (local-global processing difference); bottom-up-dominated attention "
                "with reduced top-down modulation. High co-occurrence of ADHD amplifies attention "
                "network dysfunction.",
                severity="moderate",
            ),
        ],

        primary_network=NetworkKey.SN,

        fnon_rationale=(
            "In ASD, the primary dysfunctional network is the Social Brain/Salience Network — "
            "hypoactivation of TPJ-STS-mPFC social processing circuit drives core social communication "
            "deficits. The FNON framework targets: (1) TPJ anodal tDCS for social cognition enhancement; "
            "(2) left DLPFC anodal tDCS for executive function and co-occurring ADHD features. "
            "Both applications are INVESTIGATIONAL — off-label research-level evidence. "
            "All ASD neuromodulation must be framed within a research-informed clinical context "
            "with explicit informed consent."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="l1",
                label="ASD-L1 — Level 1 (Requiring Support)",
                description="DSM-5 Level 1 ASD. Notable social communication differences and some restricted/repetitive behaviors causing functional impairment. Previously 'Asperger's' or high-functioning autism. Most adults in clinical neuromodulation settings.",
                key_features=["Social communication difficulties", "Inflexibility in routine", "Restricted interests", "Anxiety common", "Functional independence maintained"],
                primary_networks=[NetworkKey.SN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS],
                tdcs_target="Left DLPFC anodal (executive) OR right TPJ anodal (social cognition)",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="soc",
                label="ASD-SOC — Social Communication Focus",
                description="ASD with primary clinical focus on social communication impairment as functional burden. TPJ/social brain network stimulation target.",
                key_features=["Social reciprocity deficit", "Theory of mind impairment", "Reduced social motivation", "Conversation difficulties"],
                primary_networks=[NetworkKey.SN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS],
                tdcs_target="Right TPJ anodal (temporoparietal junction — social cognition) — INVESTIGATIONAL",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="exec",
                label="ASD-EXEC — Executive Function Focus",
                description="ASD with prominent executive dysfunction — working memory, planning, cognitive flexibility. Co-occurring ADHD features common. DLPFC tDCS target.",
                key_features=["Working memory deficit", "Planning impairment", "Cognitive inflexibility", "Co-occurring ADHD features", "BRIEF-2 elevated"],
                primary_networks=[NetworkKey.CEN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.CES],
                tdcs_target="Left DLPFC anodal (F3) — executive function protocol",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="adult_asd",
                label="ADULT-ASD — Adult ASD Presentation",
                description="ASD diagnosed or presenting in adulthood. Prominent executive dysfunction, anxiety, and occupational difficulties. CES for comorbid anxiety and sleep.",
                key_features=["Late diagnosis", "Compensated social difficulties", "Anxiety and burnout", "Executive dysfunction", "Depression comorbidity"],
                primary_networks=[NetworkKey.CEN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.SN, NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.CES],
                tdcs_target="Left DLPFC anodal for executive function and anxiety",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="ados2",
                name="Autism Diagnostic Observation Schedule — 2nd Edition",
                abbreviation="ADOS-2",
                domains=["social_affect", "restricted_repetitive_behavior", "diagnosis"],
                timing="baseline",
                evidence_pmid="11055457",
                notes="Gold standard ASD diagnostic observation schedule. Requires trained examiner. Not administered for monitoring — used for diagnosis confirmation only.",
            ),
            AssessmentTool(
                scale_key="srs2",
                name="Social Responsiveness Scale — 2nd Edition",
                abbreviation="SRS-2",
                domains=["social_awareness", "social_cognition", "social_communication", "social_motivation", "restricted_repetitive_behavior"],
                timing="baseline",
                evidence_pmid="18597511",
                notes="Primary ASD symptom severity monitoring tool. Self-report (adult) and informant-report. T-score >=60 = mild-moderate autism spectrum range. Suitable for treatment outcome tracking.",
            ),
            AssessmentTool(
                scale_key="brief2",
                name="Behavior Rating Inventory of Executive Function — 2nd Edition",
                abbreviation="BRIEF-2",
                domains=["inhibition", "cognitive_flexibility", "working_memory", "planning", "organization"],
                timing="baseline",
                evidence_pmid="11385981",
                notes="Essential for ASD executive function profile. Captures daily-life executive difficulties not always evident on standardized neuropsychological tests.",
            ),
            AssessmentTool(
                scale_key="vabs",
                name="Vineland Adaptive Behavior Scales",
                abbreviation="VABS",
                domains=["communication", "daily_living_skills", "socialization", "motor_skills"],
                timing="baseline",
                evidence_pmid="6609763",
                notes="Adaptive behavior — key functional outcome measure in ASD. Captures real-world functional impact beyond symptom scores.",
            ),
            AssessmentTool(
                scale_key="gad7",
                name="Generalized Anxiety Disorder 7-item Scale",
                abbreviation="GAD-7",
                domains=["anxiety", "worry"],
                timing="baseline",
                evidence_pmid="16717171",
                notes="Anxiety is highly prevalent in ASD (~40-80%). GAD-7 useful for ASD Level 1 adults with insight.",
            ),
        ],

        baseline_measures=[
            "SRS-2 (primary ASD symptom monitoring — self or informant report)",
            "BRIEF-2 (executive function profile)",
            "VABS (adaptive behavior and functional outcomes)",
            "GAD-7 (anxiety comorbidity)",
            "PHQ-9 (depression — adult ASD)",
            "SOZO PRS (social function, executive, anxiety, mood — 0-10)",
        ],

        followup_measures=[
            "SRS-2 at Week 8-10",
            "BRIEF-2 at Week 8-10",
            "GAD-7 at every session (anxiety monitoring)",
            "SOZO PRS at each session and end of block",
        ],

        inclusion_criteria=[
            "Confirmed DSM-5 ASD diagnosis (Level 1 or 2 — requires support but can engage in sessions)",
            "Age 16 and above (adult neuromodulation settings)",
            "Capacity to provide informed consent (self or guardian for adults with intellectual disability)",
            "Cognitive ability sufficient to understand and participate in sessions (IQ >70 preferred)",
            "Stable medication regimen for >=4 weeks",
            "Explicit informed consent including understanding of investigational status",
        ],

        exclusion_criteria=[
            "Uncontrolled epilepsy (elevated seizure risk in ASD — ~20-30% prevalence)",
            "ASD Level 3 (requiring very substantial support) without capacity to engage",
            "Active psychosis",
            "Severe intellectual disability precluding informed consent",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "Epilepsy / uncontrolled seizures — elevated seizure risk in ASD requires neurologist clearance",
        ],

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "precaution",
                "INVESTIGATIONAL STATUS: All tDCS and neuromodulation in ASD is investigational and off-label. Informed consent must explicitly include: (1) investigational status; (2) absence of large-scale RCT evidence; (3) unknown long-term effects in neurodevelopmental populations. Document consent thoroughly.",
                "high",
                "Clinical governance and ethical requirement for investigational ASD neuromodulation",
            ),
            make_safety(
                "precaution",
                "Elevated epilepsy risk in ASD (~20-30% prevalence). Screen for current or historical seizures before treatment. Require neurology clearance for any history of seizures before initiating tDCS. Lower starting intensity (1.5 mA) recommended.",
                "high",
                "ASD epilepsy comorbidity; seizure risk in neurodevelopmental conditions",
            ),
            make_safety(
                "precaution",
                "Sensory sensitivity: many ASD patients have tactile hypersensitivity that may cause electrode placement distress. Use preparation strategies: show electrodes, allow handling, use saline sponge (not gel) if gel texture aversive. Allow extra time for electrode preparation.",
                "moderate",
                "ASD sensory sensitivity and tactile intolerance",
            ),
            make_safety(
                "monitoring",
                "Behavioral monitoring during sessions: ASD patients may not reliably verbalize discomfort. Monitor behavioral cues (increased stereotypies, self-injury, vocal distress) as indicators of adverse response.",
                "moderate",
                "Communication and behavioral monitoring in ASD neuromodulation",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Left Dorsolateral Prefrontal Cortex", "L-DLPFC", "left",
                "Left DLPFC anodal tDCS targets executive function in ASD — working memory, cognitive "
                "flexibility, and planning. D'Urso et al. (2015) demonstrated DLPFC tDCS improvements "
                "in repetitive behaviors and social affect in ASD. OFF-LABEL INVESTIGATIONAL.",
                "C-ASD-EXEC — Executive Function Protocol",
                EvidenceLevel.LOW, off_label=True,
                eeg_canonical=["F3"],
            ),
            make_tdcs_target(
                "Temporoparietal Junction", "TPJ", "right",
                "Right TPJ anodal tDCS targets social cognition and mentalizing in ASD. "
                "TPJ is a key node of the social brain network. Anodal tDCS may enhance "
                "theory of mind and social perspective-taking. PURELY INVESTIGATIONAL — very limited evidence.",
                "C-ASD-SOC — Social Cognition Protocol",
                EvidenceLevel.LOW, off_label=True,
                eeg_canonical=["P4"],
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-ASD-EXEC", label="Executive Function — Left DLPFC tDCS (INVESTIGATIONAL)", modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex", target_abbreviation="L-DLPFC",
                phenotype_slugs=["exec", "l1", "adult_asd"],
                network_targets=[NetworkKey.CEN, NetworkKey.ATTENTION],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "Fp2 (right supraorbital) or right shoulder",
                    "intensity": "1.5-2.0 mA (start 1.5 mA — sensory sensitivity)",
                    "duration": "20 min",
                    "sessions": "10-15",
                    "note": "INVESTIGATIONAL / OFF-LABEL. Concurrent cognitive training (working memory) recommended. Allow extra electrode preparation time.",
                },
                rationale="Left DLPFC anodal tDCS targets executive dysfunction in ASD. D'Urso et al. (2015) "
                          "demonstrated improvements in repetitive behaviors and social affect with DLPFC "
                          "tDCS. Schneider & Hopp (2011) showed language improvements. INVESTIGATIONAL — "
                          "small pilot studies only. OFF-LABEL. Explicit informed consent mandatory.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                notes="INVESTIGATIONAL. Informed consent must specify off-label investigational status and absence of large-scale RCT evidence.",
            ),
            ProtocolEntry(
                protocol_id="C-ASD-SOC", label="Social Cognition — Right TPJ tDCS (INVESTIGATIONAL)", modality=Modality.TDCS,
                target_region="Temporoparietal Junction (right)", target_abbreviation="TPJ",
                phenotype_slugs=["soc", "l1"],
                network_targets=[NetworkKey.SN, NetworkKey.DMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "P4 (right TPJ approximation)",
                    "cathode": "F3 (left DLPFC) or Fp1",
                    "intensity": "1.5 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                    "note": "INVESTIGATIONAL. Concurrent social skills or perspective-taking training recommended. Very limited evidence.",
                },
                rationale="TPJ anodal tDCS aims to upregulate social brain network nodes involved in "
                          "mentalizing and social perspective-taking. Rationale from neuroimaging models "
                          "of ASD social brain dysfunction. Enticott et al. (2014) TMS social cognition "
                          "work provided mechanistic basis. PURELY INVESTIGATIONAL — very limited published data.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                notes="PURELY INVESTIGATIONAL — very limited evidence. Requires Doctor authorization and explicit informed consent.",
            ),
            ProtocolEntry(
                protocol_id="CES-ASD", label="CES — Anxiety & Sleep Adjunct", modality=Modality.CES,
                target_region="Bilateral earlobe electrodes", target_abbreviation="CES",
                phenotype_slugs=["adult_asd", "l1"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim AID",
                    "frequency": "0.5 Hz",
                    "intensity": "100-200 uA",
                    "duration": "40-60 min",
                    "sessions": "Daily during treatment block",
                },
                rationale="Alpha-Stim CES FDA-cleared for anxiety, depression, and insomnia. In adult ASD, "
                          "targets the highly prevalent anxiety (40-80%) and sleep disturbance (50-80%). "
                          "Non-pharmacological adjunct. Particularly relevant for autistic burnout and anxiety.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
            ),
        ],

        symptom_network_mapping={
            "Social Communication Deficit": [NetworkKey.SN, NetworkKey.DMN],
            "Executive Dysfunction": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Repetitive Behaviors": [NetworkKey.CEN, NetworkKey.SN],
            "Anxiety": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Sleep Disturbance": [NetworkKey.LIMBIC],
            "Sensory Sensitivity": [NetworkKey.SN, NetworkKey.ATTENTION],
        },

        symptom_modality_mapping={
            "Social Communication Deficit": [Modality.TDCS],
            "Executive Dysfunction": [Modality.TDCS],
            "Repetitive Behaviors": [Modality.TDCS],
            "Anxiety": [Modality.CES, Modality.TAVNS],
            "Sleep Disturbance": [Modality.CES],
            "Sensory Sensitivity": [Modality.CES],
        },

        responder_criteria=[
            ">=10% improvement in SRS-2 T-score from baseline",
            "Clinically meaningful improvement in BRIEF-2 domains (executive function)",
            "Clinically meaningful SOZO PRS improvement (>=3 points) in relevant domains",
        ],

        non_responder_pathway=(
            "For non-responders:\n"
            "1. Reassess ASD level and co-occurring conditions — ADHD, anxiety, depression may dominate\n"
            "2. Add CES for anxiety and sleep comorbidity\n"
            "3. Ensure sensory comfort with electrode placement — discomfort limits engagement\n"
            "4. Consider DLPFC vs TPJ protocol selection based on primary deficit\n"
            "5. Doctor review — consider ADHD-focused treatment if co-occurring ADHD predominates"
        ),

        evidence_summary=(
            "ASD neuromodulation is INVESTIGATIONAL with very limited evidence. D'Urso et al. (2015) "
            "pilot study demonstrated DLPFC tDCS improvements in ASD symptoms. Schneider & Hopp (2011) "
            "showed tDCS effects on language in ASD. All studies are small (N<20) pilot studies. "
            "No adequately powered RCT exists. All tDCS applications in ASD are off-label research. "
            "CES: FDA-cleared for comorbid symptoms (anxiety, insomnia) — best-evidenced component. "
            "| Evidence counts (published papers): TMS=5, tDCS=5, TPS=2. "
            "Best modalities: TMS, TPS (emerging)."
        ),

        evidence_gaps=[
            "No adequately powered RCT of tDCS in ASD — all evidence is pilot/feasibility level",
            "Optimal tDCS target for ASD (DLPFC vs TPJ vs other) — no comparative data",
            "Long-term effects and safety in neurodevelopmental populations — entirely unknown",
            "taVNS in ASD — no published data",
            "Age-specific protocols (child vs adolescent vs adult ASD) — no established guidelines",
        ],

        references=[
            {
                "authors": "D'Urso G et al.",
                "year": 2015,
                "title": "Transcranial direct current stimulation for hyperactivity and noncompliance in autistic disorder",
                "journal": "World Journal of Biological Psychiatry",
                "pmid": "25658898",
                "evidence_type": "pilot_study",
            },
            {
                "authors": "Schneider HD & Hopp JP",
                "year": 2011,
                "title": "The use of the Bilingual Aphasia Test for assessment and transcranial direct current stimulation to modulate language acquisition in minimally verbal children with autism",
                "journal": "Clinical Linguistics and Phonetics",
                "pmid": "21692897",
                "evidence_type": "case_series",
            },
            {
                "authors": "Enticott PG et al.",
                "year": 2014,
                "title": "A double-blind, randomized trial of deep repetitive transcranial magnetic stimulation (rTMS) for autism spectrum disorder",
                "journal": "Brain Stimulation",
                "pmid": "24034847",
                "evidence_type": "rct",
            },
        ],

        overall_evidence_quality=EvidenceLevel.LOW,

        clinical_tips=[
            "INVESTIGATIONAL: Ensure informed consent explicitly covers off-label investigational status — do not imply established treatment efficacy",
            "Allow extra time for electrode preparation — sensory sensitivity requires gradual introduction of equipment",
            "Screen for epilepsy before treatment — ASD has 20-30% epilepsy comorbidity requiring neurology clearance",
            "For adult ASD: anxiety and sleep are often the primary functional burden — CES is the best-evidenced component",
            "Co-occurring ADHD is common — if executive dysfunction predominates, ADHD protocols may be more appropriate",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "All ASD neuromodulation is investigational — Doctor authorization mandatory for every patient",
            "Informed consent must explicitly specify investigational/off-label status",
            "Seizure history screening and neurology clearance required before treatment",
        ],
    )
