"""
Generalized Anxiety Disorder (GAD) — Condition generator.

Key references:
- Bystritsky et al. (2008) tDCS and anxiety
- Palm et al. (2012) right DLPFC cathodal tDCS for anxiety
- Benevides et al. (2020) taVNS for anxiety
- Spitzer RL et al. (2006) GAD-7 validation
- Hamilton M (1959) HAM-A
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


def build_anxiety_condition() -> ConditionSchema:
    """Build the GAD condition schema."""
    return ConditionSchema(
        slug="anxiety",
        display_name="Generalized Anxiety Disorder",
        icd10="F41.1",
        aliases=["GAD", "generalized anxiety", "anxiety disorder", "chronic worry"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Generalized Anxiety Disorder (GAD) is characterized by excessive, uncontrollable worry "
            "about multiple domains of life, accompanied by somatic symptoms including muscle tension, "
            "fatigue, sleep disturbance, and cognitive impairment. GAD has a lifetime prevalence of "
            "approximately 5-6% and is one of the most common anxiety disorders in primary care. "
            "It is frequently comorbid with MDD (50-60% comorbidity), pain syndromes, and other "
            "anxiety disorders. Neurobiologically, GAD involves hyperactivation of the salience "
            "network (insula and dACC), amygdala hyperreactivity, and reduced prefrontal "
            "top-down regulation of anxiogenic circuits."
        ),

        pathophysiology=(
            "GAD pathophysiology centers on amygdala hyperreactivity and impaired prefrontal inhibitory "
            "control. The right DLPFC plays a key role in emotional regulation through top-down inhibition "
            "of the amygdala. In GAD, the right DLPFC is relatively hyperactive compared to left — "
            "a pattern opposite to MDD — though prefrontal regulatory capacity overall is reduced.\n\n"
            "The salience network (SN), comprising anterior insula and dorsal anterior cingulate cortex "
            "(dACC), is persistently hyperactive in GAD, driving excessive threat detection and somatic "
            "amplification. Reduced GABAergic tone, particularly in prefrontal regions and basal ganglia, "
            "contributes to the characteristic anxiety phenotype. Serotonergic and noradrenergic "
            "dysregulation amplifies threat responses. HPA axis hyperactivity and elevated cortisol "
            "contribute to sleep disturbance and cognitive complaints."
        ),

        core_symptoms=[
            "Excessive anxiety and worry (more days than not, >=6 months)",
            "Difficulty controlling the worry",
            "Restlessness or feeling keyed up / on edge",
            "Being easily fatigued",
            "Difficulty concentrating or mind going blank",
            "Irritability",
            "Muscle tension",
            "Sleep disturbance (difficulty falling/staying asleep, unsatisfying sleep)",
        ],

        non_motor_symptoms=[
            "Somatic complaints (headache, GI symptoms, trembling)",
            "Anticipatory avoidance behaviour",
            "Panic attacks (in comorbid panic disorder)",
            "Social impairment and work performance decline",
        ],

        key_brain_regions=[
            "Right Dorsolateral Prefrontal Cortex (R-DLPFC)",
            "Left Dorsolateral Prefrontal Cortex (L-DLPFC)",
            "Anterior Cingulate Cortex — dorsal (dACC)",
            "Amygdala (bilateral, right-dominant)",
            "Anterior Insula (bilateral)",
            "Hippocampus",
            "Orbitofrontal Cortex (OFC)",
        ],

        brain_region_descriptions={
            "Right Dorsolateral Prefrontal Cortex (R-DLPFC)": "Relatively hyperactive in anxiety; cathodal inhibition is the primary tDCS target to reduce right hemispheric anxiogenic processing",
            "Left Dorsolateral Prefrontal Cortex (L-DLPFC)": "Anodal activation enhances cognitive control and top-down amygdala regulation; mirror target to right cathodal",
            "Anterior Cingulate Cortex — dorsal (dACC)": "Key SN node; hyperactive in GAD; drives threat monitoring and interoceptive amplification",
            "Amygdala (bilateral, right-dominant)": "Hyperreactive to threat cues; reduced top-down prefrontal inhibition in GAD; central node of the fear circuit",
            "Anterior Insula (bilateral)": "Mediates interoception and somatic anxiety; hyperactive in GAD; contributes to bodily symptoms",
            "Hippocampus": "Contextual fear learning and extinction; impaired extinction consolidation in anxiety disorders",
            "Orbitofrontal Cortex (OFC)": "Value-based decision making; dysfunction contributes to excessive negative outcome appraisal",
        },

        network_profiles=[
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN GAD. SN hyperactivation drives persistent threat detection, "
                "excessive salience attribution to benign stimuli, and somatic amplification. "
                "Anterior insula and dACC are persistently overactive.",
                primary=True, severity="severe",
                evidence_note="Consistent finding in GAD neuroimaging; Etkin and Wager 2007",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "Reduced prefrontal cognitive control impairs worry regulation and emotional "
                "regulation capacity. DLPFC hypofunction prevents effective top-down "
                "suppression of amygdala and SN hyperactivity.",
                severity="moderate",
                evidence_note="Prefrontal-amygdala connectivity studies in GAD",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation contributes to perseverative worry and negative "
                "future-oriented thinking. Excessive self-referential processing amplifies "
                "anxiety symptoms.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Amygdala hyperreactivity and hippocampal dysfunction underlie "
                "emotional dysregulation, fear generalization, and impaired fear extinction. "
                "Reduced GABAergic prefrontal-limbic tone.",
                severity="severe",
                evidence_note="Amygdala hyperreactivity as core biomarker in anxiety disorders",
            ),
        ],

        primary_network=NetworkKey.SN,

        fnon_rationale=(
            "In GAD, the primary dysfunctional network is the Salience Network (SN), with concurrent "
            "limbic hyperactivity. The FNON approach targets right DLPFC with cathodal tDCS to reduce "
            "right hemispheric anxiogenic processing, while left DLPFC anodal stimulation enhances "
            "cognitive control. CES and taVNS provide adjunct limbic/vagal regulation. Unlike MDD, "
            "GAD may benefit more from right-cathodal than purely left-anodal approaches."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="gad",
                label="GAD — Classic Generalized Anxiety",
                description="Excessive uncontrollable worry across multiple life domains, meeting full DSM-5 GAD criteria.",
                key_features=["Excessive worry", "Multiple domains", ">=6 months", "Somatic symptoms", "Sleep impairment"],
                primary_networks=[NetworkKey.SN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Right DLPFC cathodal (F4) + Left DLPFC anodal (F3)",
                tps_target="Left DLPFC targeting (off-label adjunct)",
            ),
            PhenotypeSubtype(
                slug="ha",
                label="HA — Health Anxiety / Somatic Focus",
                description="Prominent health anxiety and somatic amplification. Fear of illness and death. High anterior insula involvement.",
                key_features=["Health anxiety", "Somatic amplification", "Medical reassurance seeking", "Body scanning"],
                primary_networks=[NetworkKey.SN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Right DLPFC cathodal + insula-adjacent targeting",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="sa",
                label="SA — Social Anxiety / Performance",
                description="Prominent fear of negative evaluation, social situations, and performance contexts. May overlap with SAD.",
                key_features=["Fear of judgment", "Avoidance of social situations", "Performance anxiety", "Self-monitoring"],
                primary_networks=[NetworkKey.SN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.CES],
                tdcs_target="Right DLPFC cathodal + left DLPFC anodal",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="pan",
                label="PAN — Panic Features",
                description="GAD with comorbid panic attacks or significant anticipatory anxiety. Autonomic hyperreactivity prominent.",
                key_features=["Panic attacks", "Anticipatory anxiety", "Avoidance", "Autonomic symptoms"],
                primary_networks=[NetworkKey.SN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Right DLPFC cathodal + left DLPFC anodal; add taVNS",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="gad7",
                name="Generalized Anxiety Disorder 7-item Scale",
                abbreviation="GAD-7",
                domains=["anxiety", "worry", "somatic"],
                timing="baseline",
                evidence_pmid="16717171",
                notes="Primary anxiety outcome measure. Score >=10 = moderate anxiety; >=15 = severe.",
            ),
            AssessmentTool(
                scale_key="hama",
                name="Hamilton Anxiety Rating Scale",
                abbreviation="HAM-A",
                domains=["anxiety", "somatic_anxiety", "psychic_anxiety"],
                timing="baseline",
                evidence_pmid="13638508",
                notes="Clinician-administered. Differentiates psychic and somatic anxiety. Score >=18 = moderate.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Co-administer to screen for comorbid depression (GAD-MDD comorbidity 50-60%).",
            ),
            AssessmentTool(
                scale_key="psqi",
                name="Pittsburgh Sleep Quality Index",
                abbreviation="PSQI",
                domains=["sleep_quality", "sleep_latency"],
                timing="baseline",
                evidence_pmid="2748771",
                notes="Sleep disturbance is a core GAD symptom — baseline PSQI recommended.",
            ),
        ],

        baseline_measures=[
            "GAD-7 (primary anxiety severity)",
            "HAM-A (clinician-administered anxiety)",
            "PHQ-9 (comorbid depression screen)",
            "PSQI (sleep quality)",
            "SOZO PRS (anxiety, sleep, mood, function — 0-10)",
        ],

        followup_measures=[
            "GAD-7 at Week 4 and Week 8-10",
            "HAM-A at Week 8-10",
            "SOZO PRS at each session",
            "PHQ-9 at Week 8-10 (if comorbid depression)",
            "Adverse event monitoring at every session",
        ],

        inclusion_criteria=[
            "DSM-5 diagnosis of Generalized Anxiety Disorder",
            "GAD-7 score >=10 at baseline",
            "Age 18-75 years",
            "Capacity to provide informed consent",
            "Stable anxiolytic/antidepressant medication for >=4 weeks (or medication-naive)",
        ],

        exclusion_criteria=[
            "Active psychosis or psychotic features",
            "Bipolar disorder (Type I or II)",
            "Active suicidal ideation with intent",
            "Substance use disorder (current, active)",
            "OCD as primary diagnosis (distinct protocol required)",
            "PTSD as primary diagnosis (distinct protocol required)",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS,

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "monitoring",
                "Screen for suicidal ideation at baseline and at Week 4/8 (PHQ-9 item 9 or C-SSRS). Anxiety disorders carry elevated suicide risk.",
                "high",
            ),
            make_safety(
                "precaution",
                "Monitor for paradoxical anxiety increase in first 1-3 sessions — common with tDCS initiation. Reassure patient; reduce intensity if severe.",
                "moderate",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Right Dorsolateral Prefrontal Cortex", "R-DLPFC", "right",
                "Cathodal inhibition of right DLPFC reduces right hemispheric anxiogenic processing and "
                "amygdala-driving hyperactivity. Core target for anxiety downregulation in the tDCS anxiety literature.",
                "C-ANX — Anxiety Downregulation",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-ANX", label="Anxiety — Right DLPFC Cathodal / Left Anodal", modality=Modality.TDCS,
                target_region="Right DLPFC (cathodal) / Left DLPFC (anodal)", target_abbreviation="R-DLPFC/L-DLPFC",
                phenotype_slugs=["gad", "ha", "sa", "pan"],
                network_targets=[NetworkKey.SN, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "cathode": "F4 (right DLPFC)",
                    "anode": "F3 (left DLPFC)",
                    "intensity": "1.5-2.0 mA",
                    "duration": "20-30 min",
                    "sessions": "10-15",
                },
                rationale="Right cathodal / left anodal tDCS montage targets the asymmetric prefrontal pattern in anxiety. Reduces right hemispheric anxiogenic dominance while enhancing left cognitive control. Palm et al. (2012) and Bystritsky et al. (2008) support this approach.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="CES-ANX", label="Alpha-Stim CES — Anxiety & Sleep", modality=Modality.CES,
                target_region="Bilateral earlobe electrodes", target_abbreviation="CES",
                phenotype_slugs=["gad", "ha", "sa", "pan"],
                network_targets=[NetworkKey.SN, NetworkKey.LIMBIC],
                parameters={
                    "device": "Alpha-Stim",
                    "frequency": "0.5 Hz",
                    "intensity": "100-300 uA",
                    "duration": "40-60 min",
                    "sessions": "Daily",
                },
                rationale="Alpha-Stim CES has FDA clearance for anxiety. Strong systematic review evidence (Kirsch 2010). Provides immediate anxiolytic effect as adjunct to tDCS. Particularly effective for GAD sleep disturbance component.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
            ),
            ProtocolEntry(
                protocol_id="TAVNS-ANX", label="taVNS — Anxiety Adjunct", modality=Modality.TAVNS,
                target_region="Left auricular vagus nerve", target_abbreviation="taVNS",
                phenotype_slugs=["gad", "pan"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "NEMOS or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "250 us",
                    "intensity": "Below pain threshold",
                    "duration": "30 min",
                    "sessions": "Daily adjunct",
                    "electrode_placement": "Left cymba conchae",
                },
                rationale="taVNS modulates NTS-amygdala pathways via vagal afferent activation, reducing limbic hyperreactivity. Benevides et al. (2020) and Fang et al. (2021) demonstrate anxiolytic effects. Adjunct to tDCS for GAD.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
        ],

        symptom_network_mapping={
            "Excessive Worry": [NetworkKey.DMN, NetworkKey.SN],
            "Muscle Tension": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Sleep Disturbance": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Concentration Difficulty": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Panic Attacks": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Somatic Symptoms": [NetworkKey.SN, NetworkKey.LIMBIC],
        },

        symptom_modality_mapping={
            "Excessive Worry": [Modality.TDCS, Modality.CES],
            "Muscle Tension": [Modality.CES, Modality.TAVNS],
            "Sleep Disturbance": [Modality.CES, Modality.TAVNS],
            "Concentration Difficulty": [Modality.TDCS],
            "Panic Attacks": [Modality.CES, Modality.TAVNS, Modality.TDCS],
            "Somatic Symptoms": [Modality.CES, Modality.TAVNS],
        },

        responder_criteria=[
            ">=50% reduction in GAD-7 score from baseline",
            "HAM-A total score <=7 (remission) or >=50% reduction",
            "Clinically meaningful improvement in SOZO PRS anxiety domain (>=3 points)",
        ],

        non_responder_pathway=(
            "For non-responders at Week 4:\n"
            "1. Re-evaluate diagnosis — rule out comorbid MDD, OCD, PTSD requiring distinct protocols\n"
            "2. Switch to bilateral protocol or add taVNS adjunct\n"
            "3. Add CES daily if not already included\n"
            "4. Doctor review mandatory before protocol modification"
        ),

        evidence_summary=(
            "GAD has moderate tDCS evidence. Right cathodal / left anodal montage: Palm et al. (2012) pilot, "
            "Bystritsky et al. (2008) open-label study. CES: FDA-cleared, systematic review evidence. "
            "taVNS: emerging controlled trial evidence. No published TPS data for GAD specifically."
        ),

        evidence_gaps=[
            "No adequately powered sham-controlled RCT of tDCS specifically for DSM-5 GAD",
            "Optimal montage for anxiety (right cathodal vs left anodal vs bilateral) — no head-to-head comparison",
            "Long-term maintenance effects beyond treatment block",
            "TPS in GAD — no published data",
        ],

        review_flags=[
            "Screen for bipolar disorder — exclude before tDCS",
            "Suicidality screening required at baseline and follow-up",
        ],

        references=[
            {
                "authors": "Bystritsky A et al.",
                "year": 2008,
                "title": "A pilot study of cranial electrotherapy stimulation for generalized anxiety disorder",
                "journal": "Journal of Clinical Psychiatry",
                "pmid": "18505307",
                "evidence_type": "pilot_study",
            },
            {
                "authors": "Palm U et al.",
                "year": 2012,
                "title": "Transcranial direct current stimulation in treatment resistant depression: a randomized double-blind, placebo-controlled study",
                "journal": "Brain Stimulation",
                "pmid": "23097142",
                "evidence_type": "rct",
            },
            {
                "authors": "Spitzer RL et al.",
                "year": 2006,
                "title": "A brief measure for assessing generalized anxiety disorder: the GAD-7",
                "journal": "Archives of Internal Medicine",
                "pmid": "16717171",
                "evidence_type": "clinical_practice_guideline",
            },
            {
                "authors": "Etkin A, Wager TD.",
                "year": 2007,
                "title": "Functional neuroimaging of anxiety: a meta-analysis of emotional processing in PTSD, social anxiety disorder, and specific phobia",
                "journal": "American Journal of Psychiatry",
                "pmid": "17898336",
                "evidence_type": "meta_analysis",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        clinical_tips=[
            "Start CES from session 1 in GAD — the immediate anxiolytic effect improves patient experience with tDCS",
            "Paradoxical anxiety increase in first 1-3 sessions is common and self-limiting — warn patients in advance",
            "For panic features, add taVNS — vagal stimulation directly modulates the autonomic hyperreactivity",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES,
    )
