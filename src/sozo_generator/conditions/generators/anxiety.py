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
                eeg_canonical=["F4", "F3"],
            ),
            StimulationTarget(
                modality=Modality.CES,
                target_region="Bilateral earlobe electrodes (CES)",
                target_abbreviation="CES",
                laterality="bilateral",
                rationale="Alpha-Stim CES (0.5 Hz, 100-300 µA) has FDA clearance for anxiety. "
                          "Modulates serotonin, beta-endorphin, and cortisol. Provides immediate anxiolytic "
                          "effect as adjunct to tDCS. Systematic review evidence (Kirsch 2010). "
                          "Effective for GAD sleep disturbance component.",
                protocol_label="CES-ANX — Alpha-Stim Anxiety & Sleep",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
                eeg_canonical=["bilateral earlobes"],
            ),
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Left auricular vagus nerve",
                target_abbreviation="taVNS",
                laterality="left",
                rationale="taVNS modulates NTS-amygdala pathways via vagal afferent activation, "
                          "reducing limbic hyperreactivity. Benevides et al. (2020) and Fang et al. (2021) "
                          "demonstrate anxiolytic effects. Adjunct to tDCS for GAD and panic features.",
                protocol_label="TAVNS-ANX — Anxiety Adjunct",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=True,
                eeg_canonical=["left ear (cymba conchae)"],
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
                # Extended protocol fields
                protocol_name='TDCS-ANX — Right DLPFC Cathodal / Left Anodal Anxiety Protocol',
                clinical_objective='Reduce right hemispheric anxiogenic dominance and enhance left prefrontal cognitive control',
                primary_targets=['Right DLPFC (F4) — cathodal', 'Left DLPFC (F3) — anodal'],
                secondary_targets=['Amygdala (indirect via prefrontal-amygdala connectivity)'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Anode (+): F3 (L-DLPFC). Cathode (-): F4 (R-DLPFC). 1.5-2.0 mA, 20-30 min.',
                frequency='1 session/day, 5 days/week',
                duration='20-30 min per session',
                intensity_dose='1.5-2.0 mA',
                montage_roi='Anode (+): F3 (L-DLPFC). Cathode (-): F4 (R-DLPFC)',
                laterality='Left-anodal / Right-cathodal (bilateral asymmetric)',
                treatment_course='10-15 sessions over 2-3 weeks',
                monitoring='Impedance check; GAD-7 biweekly; HAM-A at baseline and Week 8; skin integrity',
                expected_response='Anxiety reduction beginning Week 2-3; GAD-7 >=50% reduction by end of block',
                evidence_status='Moderate — Palm et al. 2012; Bystritsky et al. 2008; systematic review support',
                cautions='Paradoxical anxiety increase in first 1-3 sessions is common — warn patient. Screen for bipolar disorder before treatment.',
                when_to_escalate='If <20% improvement after 10 sessions, reassess targeting; add taVNS adjunct',
                when_to_stop_modify='Stop if burning, skin lesion, or neurological change',
                clinical_notes_extended='Unlike MDD, GAD may benefit more from right-cathodal than purely left-anodal approaches. Opposite to standard depression montage.',
                key_citations=['Palm et al., 2012', 'Bystritsky et al., 2008', 'Etkin & Wager, 2007'],
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
                # Extended protocol fields
                protocol_name='CES-ANX — Alpha-Stim Anxiety & Sleep Protocol',
                clinical_objective='Immediate anxiolytic effect and sleep improvement via cranial electrotherapy stimulation',
                primary_targets=['Bilateral earlobe electrodes (cranial nerve modulation)'],
                secondary_targets=['Serotonergic/endorphin modulation'],
                device_name='Alpha-Stim® CS',
                session_structure='Bilateral earlobe clip electrodes; 0.5 Hz, 100-300 µA; 40-60 min',
                frequency='Daily',
                duration='40-60 min per session',
                intensity_dose='100-300 µA at 0.5 Hz',
                montage_roi='Bilateral earlobe clip electrodes',
                laterality='Bilateral',
                treatment_course='Daily for treatment block; then as-needed maintenance',
                monitoring='GAD-7 weekly; PSQI; skin integrity at earlobes',
                expected_response='Immediate anxiolytic effect from session 1; sleep improvement within 1-2 weeks',
                evidence_status='Moderate — FDA-cleared for anxiety; systematic review evidence (Kirsch 2010)',
                cautions='Adjunctive only — not primary treatment for severe GAD. Well-tolerated.',
                when_to_escalate='If insufficient anxiolytic effect, add tDCS or taVNS',
                when_to_stop_modify='Stop if ear skin irritation or dizziness during use',
                clinical_notes_extended='Start CES from session 1 in GAD for immediate anxiolytic benefit alongside tDCS ramp-up.',
                key_citations=['Kirsch DL, 2010'],
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
                # Extended protocol fields
                protocol_name='TAVNS-ANX — Vagal Anxiety Adjunct',
                clinical_objective='Reduce limbic hyperreactivity via vagal afferent modulation',
                primary_targets=['Left auricular vagus nerve (cymba conchae)'],
                secondary_targets=['NTS-amygdala pathway', 'LC-noradrenergic system'],
                device_name='NEMOS (tVNS Technologies) or Parasym',
                session_structure='Electrode on left cymba conchae; 25 Hz, 250 µs pulse width; below pain threshold; 30 min',
                frequency='Daily adjunct',
                duration='30 min per session',
                intensity_dose='Below pain threshold (typically 0.5-3.0 mA)',
                montage_roi='Left cymba conchae auricular electrode',
                laterality='Left ear',
                treatment_course='Daily for treatment block duration',
                monitoring='Heart rate; skin integrity; tolerability; GAD-7',
                expected_response='Reduced autonomic arousal and panic symptoms within 1-2 weeks',
                evidence_status='Moderate — Benevides et al. 2020; Fang et al. 2021; emerging controlled trial evidence',
                cautions='Monitor heart rate. Left ear only (right vagus innervates sinoatrial node). OFF-LABEL.',
                when_to_escalate='If insufficient effect, increase stimulation duration or combine with tDCS',
                when_to_stop_modify='Stop if bradycardia, ear pain, or skin irritation',
                clinical_notes_extended='Particularly effective for panic features and autonomic hyperreactivity in GAD.',
                key_citations=['Benevides et al., 2020', 'Fang et al., 2021'],
            ),

            # ── C4-C6: Expanded tDCS protocols ──────────────────────
            ProtocolEntry(
                protocol_id="C4", label="vmPFC — Fear Extinction", modality=Modality.TDCS,
                target_region="Ventromedial Prefrontal Cortex", target_abbreviation="vmPFC",
                phenotype_slugs=["gad", "pan", "sa"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.DMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "Fp1 (left medial prefrontal — vmPFC proxy)",
                    "cathode": "Right mastoid or shoulder reference",
                    "intensity": "1.5 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                    "note": "Combine with exposure therapy or fear extinction exercises during stimulation for optimal effect",
                },
                rationale="vmPFC is the critical node for fear extinction learning — its hypoactivation in anxiety disorders impairs extinction consolidation. Anodal vmPFC tDCS combined with exposure therapy may enhance fear extinction. Milad & Quirk (2012) framework. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # Extended protocol fields
                protocol_name='TDCS-ANX-VMPFC — vmPFC Fear Extinction Protocol',
                clinical_objective='Enhance fear extinction learning via vmPFC anodal stimulation',
                primary_targets=['Ventromedial PFC (Fp1 proxy)'],
                secondary_targets=['Amygdala (via vmPFC-amygdala extinction circuit)'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Anode (+): Fp1 (left medial prefrontal / vmPFC proxy). Cathode (-): Right mastoid. 1.5 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='1.5 mA',
                montage_roi='Anode (+): Fp1 (vmPFC proxy). Cathode (-): Right mastoid or shoulder',
                laterality='Left medial prefrontal',
                treatment_course='10-15 sessions over 2-3 weeks',
                monitoring='Impedance check; GAD-7; exposure therapy progress; skin integrity',
                expected_response='Enhanced fear extinction during concurrent exposure therapy',
                evidence_status='Low — rationale from Milad & Quirk 2012 extinction neuroscience; limited tDCS data',
                cautions='OFF-LABEL. Combine with exposure therapy for optimal effect. Low intensity (1.5 mA) for frontal pole.',
                when_to_escalate='If <20% improvement after 10 sessions, switch to standard bilateral DLPFC protocol',
                when_to_stop_modify='Stop if burning, skin lesion, or neurological change',
                clinical_notes_extended='vmPFC is the critical node for fear extinction learning. Best combined with concurrent exposure or CBT.',
                key_citations=['Milad & Quirk, 2012'],
            ),
            ProtocolEntry(
                protocol_id="C5", label="Right DLPFC Cathodal — Reduce Hyperactivity", modality=Modality.TDCS,
                target_region="Right Dorsolateral Prefrontal Cortex (cathodal)", target_abbreviation="R-DLPFC-cat",
                phenotype_slugs=["gad", "ha", "sa"],
                network_targets=[NetworkKey.SN, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "cathode": "F4 (right DLPFC — cathodal inhibition)",
                    "anode": "Left shoulder or mastoid reference",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                    "note": "Pure cathodal right DLPFC — distinct from C-ANX bilateral montage. Targets right-hemispheric hyperactivation specifically.",
                },
                rationale="Pure cathodal right DLPFC tDCS reduces right-hemispheric anxiogenic hyperactivation without concurrent left anodal. May be preferable when left DLPFC activation is not desired (e.g., health anxiety with somatic amplification). OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # Extended protocol fields
                protocol_name='TDCS-ANX-RDLPFC — Pure Right DLPFC Cathodal',
                clinical_objective='Reduce right hemispheric anxiogenic hyperactivation without concurrent left anodal',
                primary_targets=['Right DLPFC (F4) — cathodal'],
                secondary_targets=['Right amygdala (indirect)'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Cathode (-): F4 (R-DLPFC). Anode (+): Left shoulder or mastoid reference. 2.0 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='2.0 mA',
                montage_roi='Cathode (-): F4 (R-DLPFC). Anode (+): Left shoulder or mastoid reference',
                laterality='Right cathodal (unilateral)',
                treatment_course='10-15 sessions over 2-3 weeks',
                monitoring='Impedance check; GAD-7 biweekly; skin integrity',
                expected_response='Reduced right-hemispheric anxiogenic drive; anxiety reduction',
                evidence_status='Low — rationale from anxiety lateralization literature; limited controlled data',
                cautions='OFF-LABEL. Pure cathodal — distinct from bilateral C-ANX. May be preferable for health anxiety with somatic amplification.',
                when_to_escalate='If <20% improvement after 10 sessions, switch to bilateral C-ANX protocol',
                when_to_stop_modify='Stop if burning, skin lesion, or neurological change',
                clinical_notes_extended='Targets right-hemispheric hyperactivation specifically without concurrent left activation.',
                key_citations=['Palm et al., 2012'],
            ),
            ProtocolEntry(
                protocol_id="C6", label="Temporal/Insula — Interoception/Panic", modality=Modality.TDCS,
                target_region="Right Anterior Insula / Temporal Cortex", target_abbreviation="rAI/TC",
                phenotype_slugs=["pan", "ha", "gad"],
                network_targets=[NetworkKey.SN, NetworkKey.LIMBIC],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "cathode": "T4 (right temporal — anterior insula proxy)",
                    "anode": "F3 (left DLPFC)",
                    "intensity": "1.5 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                    "note": "Cathodal right temporal targets insular hyperactivity. Reduced intensity (1.5 mA) due to temporal cortex sensitivity.",
                },
                rationale="Right anterior insula is the SN hub driving interoceptive amplification and somatic anxiety in panic and health anxiety. Cathodal inhibition over right temporal/insular cortex combined with left DLPFC anodal aims to reduce visceral threat signaling. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # Extended protocol fields
                protocol_name='TDCS-ANX-INSULA — Temporal/Insula Interoception/Panic Protocol',
                clinical_objective='Reduce insular hyperactivity driving interoceptive amplification and somatic anxiety',
                primary_targets=['Right Anterior Insula / Temporal Cortex (T4) — cathodal'],
                secondary_targets=['Left DLPFC (F3) — anodal'],
                device_name='Newronika HDCkit (2-channel)',
                session_structure='Cathode (-): T4 (right temporal / insula proxy). Anode (+): F3 (L-DLPFC). 1.5 mA, 20 min.',
                frequency='1 session/day, 5 days/week',
                duration='20 min per session',
                intensity_dose='1.5 mA',
                montage_roi='Cathode (-): T4 (R temporal / insula proxy). Anode (+): F3 (L-DLPFC)',
                laterality='Right temporal cathodal / Left prefrontal anodal',
                treatment_course='10-15 sessions over 2-3 weeks',
                monitoring='Impedance check; GAD-7; panic frequency log; skin integrity',
                expected_response='Reduced somatic anxiety and panic frequency',
                evidence_status='Low — rationale from SN/insula neuroimaging; limited tDCS data for temporal placement',
                cautions='OFF-LABEL. Reduced intensity (1.5 mA) due to temporal cortex sensitivity. Monitor for ear/temporal discomfort.',
                when_to_escalate='If <20% improvement after 10 sessions, switch to standard bilateral DLPFC',
                when_to_stop_modify='Stop if burning, skin lesion, or neurological change',
                clinical_notes_extended='Right anterior insula is the SN hub driving interoceptive amplification in panic and health anxiety.',
                key_citations=['Etkin & Wager, 2007'],
            ),

            # ── T3-T4: TPS protocols ──────────────────────────────
            ProtocolEntry(
                protocol_id="T3", label="TPS — DLPFC Deep Prefrontal", modality=Modality.TPS,
                target_region="Dorsolateral Prefrontal Cortex (deep)", target_abbreviation="DLPFC-deep",
                phenotype_slugs=["gad", "sa"],
                network_targets=[NetworkKey.CEN, NetworkKey.SN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Left DLPFC deep layers (neuronavigation-guided)",
                    "pulses": "300-400 per session",
                    "frequency": "5 Hz",
                    "energy": "0.20-0.25 mJ/mm2",
                    "sessions": "6-9 over 3 weeks",
                },
                rationale="TPS deep DLPFC stimulation enhances prefrontal top-down control over amygdala and SN hyperactivation in GAD. Acoustic energy reaches deeper prefrontal layers than surface tDCS, potentially engaging prefrontal-amygdala regulatory circuits. OFF-LABEL — no GAD-specific TPS data.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=9,
                # Extended protocol fields
                protocol_name='TPS-ANX-DLPFC — Deep Prefrontal TPS for GAD',
                clinical_objective='Enhance prefrontal top-down control over amygdala and SN via deep acoustic stimulation',
                primary_targets=['Left DLPFC deep layers'],
                secondary_targets=['Prefrontal-amygdala regulatory circuits'],
                device_name='NEUROLITH® TPS System (Storz Medical)',
                session_structure='Neuronavigation setup → Holocranial priming (2,000 pulses) → Targeted DLPFC stimulation (4,000 pulses) → Secondary targets (2,000 pulses)',
                frequency='3 sessions/week',
                duration='30-45 min per session',
                intensity_dose='0.20-0.25 mJ/mm²; 5 Hz',
                montage_roi='Neuronavigation-guided left DLPFC; scalp entry near F3',
                laterality='Left DLPFC',
                treatment_course='6-9 sessions over 3 weeks',
                monitoring='GAD-7 pre/post block; tolerability log',
                expected_response='Improved prefrontal regulation and anxiety reduction',
                evidence_status='Low — no GAD-specific TPS data; rationale extrapolated from depression TPS literature',
                cautions='TPS is investigational/off-label for GAD. Neuronavigation recommended.',
                when_to_escalate='If no improvement, consider adding tDCS bilateral DLPFC protocol',
                when_to_stop_modify='Stop if persistent headache or neurological change',
                clinical_notes_extended='Acoustic energy reaches deeper prefrontal layers than surface tDCS. Exploratory application.',
                key_citations=['Beisteiner et al., 2020'],
            ),
            ProtocolEntry(
                protocol_id="T4", label="TPS — ACC Worry/Rumination Circuit", modality=Modality.TPS,
                target_region="Anterior Cingulate Cortex (deep)", target_abbreviation="ACC-deep",
                phenotype_slugs=["gad", "pan", "ha"],
                network_targets=[NetworkKey.SN, NetworkKey.DMN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Dorsal ACC (neuronavigation-guided — deep target)",
                    "pulses": "300-400 per session",
                    "frequency": "5 Hz",
                    "energy": "0.20-0.25 mJ/mm2",
                    "sessions": "6-9 over 3 weeks",
                },
                rationale="TPS targeting dACC addresses the hyperactive SN hub driving persistent threat monitoring and worry in GAD. dACC is the critical node linking SN hyperactivation to DMN perseverative worry. Deep acoustic stimulation may normalize ACC hyperactivity. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=9,
                # Extended protocol fields
                protocol_name='TPS-ANX-ACC — ACC Worry/Rumination Circuit',
                clinical_objective='Normalize hyperactive dACC driving persistent threat monitoring and worry',
                primary_targets=['Dorsal ACC (deep target)'],
                secondary_targets=['SN-DMN interface'],
                device_name='NEUROLITH® TPS System (Storz Medical)',
                session_structure='Neuronavigation setup → Holocranial priming (2,000 pulses) → Targeted dACC stimulation (4,000 pulses) → Secondary DLPFC (2,000 pulses)',
                frequency='3 sessions/week',
                duration='30-45 min per session',
                intensity_dose='0.20-0.25 mJ/mm²; 5 Hz',
                montage_roi='Neuronavigation-guided dACC; scalp entry near Fz',
                laterality='Midline',
                treatment_course='6-9 sessions over 3 weeks',
                monitoring='GAD-7 pre/post block; worry diary; tolerability log',
                expected_response='Reduced perseverative worry and threat monitoring',
                evidence_status='Low — no GAD-specific TPS data for ACC targeting',
                cautions='TPS is investigational/off-label for GAD. Neuronavigation recommended. Deep target requires careful planning.',
                when_to_escalate='If no improvement, consider DLPFC TPS or bilateral tDCS',
                when_to_stop_modify='Stop if persistent headache or neurological change',
                clinical_notes_extended='dACC is the critical SN node linking hyperactivation to DMN perseverative worry in GAD.',
                key_citations=['Etkin & Wager, 2007'],
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
            "taVNS: emerging controlled trial evidence. No published TPS data for GAD specifically. "
            "| Evidence counts (published papers): CES=40, TMS=20, tDCS=15, taVNS=10, PEMF=5, PBM=5, tACS=5. "
            "Best modalities: CES (Alpha-Stim), taVNS."
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


        # --- Auto-enriched: PlatoScience Variants ---
        platoscience_variants=[
            PlatoScienceVariant(
                variant_id="C-ANX-PS", protocol_id="C-ANX",
                label="PlatoScience Anxiety — Right DLPFC Cathodal / Left Anodal",
                parameters={"program": "Think", "electrode_config": "F3 (left DLPFC)", "intensity": "1.5-2.0 mA", "duration": "20-30 min", "ramp": "30 sec"},
                notes="Maps to C-ANX protocol. PlatoScience Think program.",
            ),
            PlatoScienceVariant(
                variant_id="C4-PS", protocol_id="C4",
                label="PlatoScience vmPFC — Fear Extinction",
                parameters={"program": "Relax", "electrode_config": "Fp1 (vmPFC proxy)", "intensity": "1.5 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C4 protocol. PlatoScience Relax program. Combine with exposure exercises.",
            ),
            PlatoScienceVariant(
                variant_id="C5-PS", protocol_id="C5",
                label="PlatoScience Right DLPFC Cathodal — Reduce Hyperactivity",
                parameters={"program": "Relax", "electrode_config": "F4 (right DLPFC cathode)", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C5 protocol. PlatoScience Relax program.",
            ),
            PlatoScienceVariant(
                variant_id="C6-PS", protocol_id="C6",
                label="PlatoScience Temporal/Insula — Interoception/Panic",
                parameters={"program": "Relax", "electrode_config": "T4 (right temporal — insula proxy cathode)", "intensity": "1.5 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C6 protocol. PlatoScience Relax program.",
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
                "role": 'Anodal excitatory — cognitive control enhancement',
                "protocols_using": ['C-ANX', 'C4', 'C6'],
            },
            {
                "position": 'F4',
                "brain_region": 'Right DLPFC',
                "role": 'Cathodal inhibitory — reduce anxiogenic right-hemispheric dominance',
                "protocols_using": ['C-ANX', 'C5'],
            },
            {
                "position": 'T4',
                "brain_region": 'Right Temporal / Anterior Insula proxy',
                "role": 'Cathodal — interoceptive/panic reduction',
                "protocols_using": ['C6'],
            },
            {
                "position": 'Fp1',
                "brain_region": 'Left vmPFC proxy',
                "role": 'Anodal — fear extinction enhancement',
                "protocols_using": ['C4'],
            },
            {
                "position": 'Fz',
                "brain_region": 'ACC / Midline Frontal',
                "role": 'TPS target — worry/rumination circuit',
                "protocols_using": ['T4'],
            },
        ],
        adverse_event_grades=SHARED_ADVERSE_EVENT_GRADES,
        side_effects=SHARED_SIDE_EFFECTS,
        governance_rules=SHARED_GOVERNANCE_RULES,
    )
