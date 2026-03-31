"""
Parkinson's Disease -- Complete condition generator.
Gold standard template condition. All content is evidence-based.

Key references:
- Doruk Cengiz et al. (2020) tDCS in PD: systematic review and meta-analysis
- Benninger et al. (2010) tDCS motor cortex in PD — Journal Neurology Neurosurgery Psychiatry
- Boggio et al. (2006) tDCS working memory in PD
- Khedr et al. (2013) bifrontal tDCS in PD
- Koch et al. (2019) TPS in PD (NEUROLITH)
- MDS-UPDRS: Goetz et al. (2008)
- FNON framework: SOZO Brain Center (2026)
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


def build_parkinsons_condition() -> ConditionSchema:
    """Build the complete Parkinson's Disease condition schema."""
    return ConditionSchema(
        slug="parkinsons",
        display_name="Parkinson's Disease",
        icd10="G20",
        aliases=["PD", "Parkinson disease", "Parkinson's"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Parkinson's Disease (PD) is a progressive neurodegenerative disorder characterized "
            "primarily by motor symptoms including bradykinesia, resting tremor, rigidity, and "
            "postural instability, arising from the degeneration of dopaminergic neurons in the "
            "substantia nigra pars compacta and subsequent dysfunction of the basal ganglia "
            "thalamocortical circuit. PD is the second most common neurodegenerative disorder "
            "after Alzheimer's disease, affecting approximately 1-2% of the population over 60 "
            "years of age. Non-motor symptoms — including cognitive impairment, depression, "
            "anxiety, autonomic dysfunction, sleep disorders, and fatigue — are highly prevalent "
            "and significantly impact quality of life."
        ),

        pathophysiology=(
            "PD pathophysiology involves the progressive loss of dopaminergic neurons in the "
            "substantia nigra pars compacta (SNpc), leading to dopamine depletion in the striatum "
            "(caudate nucleus and putamen). This disrupts the balance of direct and indirect "
            "pathways in the basal ganglia-thalamocortical circuit, resulting in reduced "
            "thalamo-cortical drive and impaired voluntary movement initiation.\n\n"
            "Lewy body pathology (alpha-synuclein aggregation) spreads through the nervous system "
            "in a staging pattern (Braak stages 1-6), with early involvement of the dorsal motor "
            "nucleus of the vagus nerve and olfactory bulb, progressing to substantia nigra "
            "(Stage 3-4) and eventually neocortex (Stage 5-6).\n\n"
            "Neuroinflammation, mitochondrial dysfunction, oxidative stress, and impaired protein "
            "clearance (ubiquitin-proteasome system, autophagy) are implicated in neuronal death. "
            "Non-motor symptoms reflect pathology beyond the nigrostriatal system: cortical "
            "Lewy bodies contribute to cognitive decline; serotonergic and noradrenergic "
            "depletion underpins depression and anxiety; hypothalamic and autonomic nervous "
            "system involvement drives autonomic symptoms."
        ),

        core_symptoms=[
            "Bradykinesia (slowness of movement) — cardinal symptom required for diagnosis",
            "Resting tremor (4-6 Hz, pill-rolling character) — present in ~70% of patients",
            "Rigidity (cogwheel or lead-pipe) — increased tone throughout range of movement",
            "Postural instability — late feature, significant fall risk",
            "Freezing of gait (FOG) — sudden, transient inability to initiate steps",
            "Hypomimia (reduced facial expression)",
            "Hypophonia and dysarthria",
            "Micrographia",
        ],

        non_motor_symptoms=[
            "Cognitive impairment and dementia (PD-MCI in 25-30%; PDD in 80% at 20 years)",
            "Depression (prevalence 40-50%)",
            "Anxiety (prevalence 30-40%)",
            "Apathy (prevalence 40%)",
            "REM sleep behaviour disorder (RBD) — prodromal marker",
            "Autonomic dysfunction (orthostatic hypotension, constipation, urinary urgency)",
            "Olfactory dysfunction (anosmia — early prodromal feature)",
            "Pain and sensory disturbances (40-85%)",
            "Fatigue",
            "Psychosis and hallucinations (dopaminergic treatment effect + disease progression)",
            "Impulse control disorders (dopamine agonist-related)",
        ],

        key_brain_regions=[
            "Substantia Nigra pars compacta (SNpc)",
            "Striatum (Putamen + Caudate Nucleus)",
            "Globus Pallidus internus (GPi)",
            "Subthalamic Nucleus (STN)",
            "Thalamus (motor relay nuclei: VLa, VLp)",
            "Primary Motor Cortex (M1)",
            "Supplementary Motor Area (SMA)",
            "Dorsolateral Prefrontal Cortex (DLPFC)",
            "Anterior Cingulate Cortex (ACC)",
            "Cerebellum (compensatory hyperactivation)",
        ],

        brain_region_descriptions={
            "Substantia Nigra pars compacta (SNpc)": "Primary site of dopaminergic neurodegeneration; loss of >50-60% neurons produces clinical motor symptoms",
            "Striatum (Putamen + Caudate Nucleus)": "Primary target of nigrostriatal dopaminergic projections; dopamine depletion disrupts direct/indirect pathway balance",
            "Globus Pallidus internus (GPi)": "Overactive in PD due to loss of dopaminergic inhibition; DBS target; contributes to motor suppression",
            "Subthalamic Nucleus (STN)": "Hyperactive in PD; major DBS target; drives excessive GPi inhibition of motor thalamus",
            "Thalamus (motor relay nuclei: VLa, VLp)": "Receives basal ganglia output; reduced thalamocortical drive due to GPi overactivity",
            "Primary Motor Cortex (M1)": "Reduced activation due to impaired thalamocortical drive; primary tDCS anodal stimulation target",
            "Supplementary Motor Area (SMA)": "Hypoactive in PD; involved in movement initiation and sequence learning; TPS and tDCS target",
            "Dorsolateral Prefrontal Cortex (DLPFC)": "Impaired in executive and cognitive PD subtypes; target for cognitive and mood protocols",
            "Anterior Cingulate Cortex (ACC)": "Involved in apathy, motivation, and error monitoring; implicated in PD-related cognitive and emotional dysfunction",
            "Cerebellum (compensatory hyperactivation)": "Compensatory hyperactivation in PD motor circuitry; cerebellar-thalamocortical pathway increasingly recognized as tremor target",
        },

        network_profiles=[
            make_network(
                NetworkKey.SMN, NetworkDysfunction.HYPO,
                "PRIMARY NETWORK IN PD. Dopaminergic depletion severely disrupts basal ganglia "
                "thalamocortical motor loop. Reduced M1 and SMA activation. Motor slowing, "
                "rigidity, and initiation failure reflect SMN hypofunction.",
                primary=True, severity="severe",
                evidence_note="Established; foundational PD pathophysiology",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "Executive dysfunction is the most common cognitive impairment in PD. "
                "DLPFC hypoactivation on functional imaging. Frontostriatal dopaminergic "
                "depletion impairs working memory, planning, and cognitive flexibility.",
                severity="moderate",
                evidence_note="Multiple fMRI and neuropsychological studies",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation and failure to deactivate during task performance "
                "is associated with PD-related cognitive decline, visual hallucinations, "
                "and impaired attentional suppression.",
                severity="moderate",
                evidence_note="Lewy body cortical pathology; resting-state fMRI studies",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPO,
                "Serotonergic and noradrenergic depletion, plus limbic Lewy body pathology, "
                "underpin depression (40-50%), anxiety (30%), and apathy (40%) in PD. "
                "Reduced ventral striatal dopamine contributes to anhedonia.",
                severity="moderate",
                evidence_note="Neuroimaging and neurochemical studies in PD depression",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPO,
                "Reduced autonomic reactivity, apathy, and impaired network switching "
                "reflect salience network dysfunction. Anterior insula pathology contributes "
                "to impaired interoception and reduced emotional responsivity.",
                severity="mild-moderate",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Attentional deficits, distractibility, and impaired dual-tasking are early "
                "markers of PD-MCI. Reflect frontal dopaminergic depletion and parietal "
                "involvement in advanced disease.",
                severity="mild",
                evidence_note="Attentional deficits as early PD-MCI markers (Litvan et al.)",
            ),
        ],

        primary_network=NetworkKey.SMN,

        fnon_rationale=(
            "In Parkinson's Disease, the primary dysfunctional network is the Sensorimotor "
            "Network (SMN), driven by basal ganglia-thalamocortical circuit disruption from "
            "nigrostriatal dopamine depletion. The FNON framework directs primary stimulation "
            "efforts at the SMN (M1/SMA targets) while addressing secondary networks — CEN "
            "for cognitive subtypes, limbic network for depression/apathy subtypes, and "
            "attention networks for PD-MCI presentations."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="td",
                label="TD — Tremor-Dominant",
                description="Predominantly tremor with minimal bradykinesia and rigidity. Slower progression. Cerebellar compensation prominent.",
                key_features=["Resting tremor 4-6Hz", "Pill-rolling tremor", "Minimal bradykinesia", "Slower disease progression"],
                primary_networks=[NetworkKey.SMN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.TPS],
                tdcs_target="M1 bilateral (C3/C4 anodal) — Tremor protocol",
                tps_target="M1 / Cerebellar cortex (bilateral)",
            ),
            PhenotypeSubtype(
                slug="ar",
                label="AR — Akinetic-Rigid",
                description="Predominant bradykinesia and rigidity without significant tremor. More rapid motor progression.",
                key_features=["Bradykinesia", "Lead-pipe rigidity", "Minimal tremor", "Hypomimia", "Micrographia"],
                primary_networks=[NetworkKey.SMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.TPS],
                tdcs_target="M1 bilateral anodal / SMA anodal",
                tps_target="M1 / SMA bilateral",
            ),
            PhenotypeSubtype(
                slug="pigd",
                label="PIGD — Postural Instability / Gait Disorder",
                description="Prominent gait and balance impairment including FOG, shuffling gait, retropulsion. Higher fall risk.",
                key_features=["Freezing of gait", "Festination", "Retropulsion", "Falls", "Reduced stride length"],
                primary_networks=[NetworkKey.SMN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.TPS, Modality.TAVNS],
                tdcs_target="M1 / SMA anodal bilateral",
                tps_target="SMA / Cerebellar targeting",
            ),
            PhenotypeSubtype(
                slug="fe",
                label="FE — Frontal/Executive Subtype",
                description="Prominent executive dysfunction, cognitive impairment, and working memory deficits. PD-MCI pattern.",
                key_features=["Executive dysfunction", "Working memory deficits", "Reduced fluency", "Planning impairments"],
                primary_networks=[NetworkKey.CEN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.DMN, NetworkKey.SMN],
                preferred_modalities=[Modality.TDCS, Modality.TPS, Modality.CES],
                tdcs_target="DLPFC bilateral anodal (F3/F4)",
                tps_target="DLPFC / Hippocampal targeting",
            ),
            PhenotypeSubtype(
                slug="la",
                label="LA — Limbic-Affective Subtype",
                description="Prominent depression, anxiety, and/or apathy as primary clinical burden. Limbic and serotonergic pathway involvement.",
                key_features=["Depression", "Anxiety", "Apathy", "Anhedonia", "Reduced motivation"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                secondary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal + right supraorbital cathode",
                tps_target="Left DLPFC / ACC targeting",
            ),
            PhenotypeSubtype(
                slug="pa",
                label="PA — Pain Subtype",
                description="Chronic pain, sensory disturbances, or dyskinesia-related discomfort as significant clinical burden.",
                key_features=["Central pain", "Musculoskeletal pain", "Dystonic pain", "Dyskinesia-related discomfort"],
                primary_networks=[NetworkKey.SN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.SMN],
                preferred_modalities=[Modality.TDCS, Modality.TPS, Modality.CES],
                tdcs_target="M1 anodal / ACC targeting",
                tps_target="M1 / ACC / Insula targeting",
            ),
            PhenotypeSubtype(
                slug="mn",
                label="MN — Mixed Phenotype",
                description="Significant features across multiple phenotype categories requiring individualized multi-network targeting.",
                key_features=["Motor + cognitive", "Motor + affective", "Motor + pain"],
                primary_networks=[NetworkKey.SMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.LIMBIC, NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.TPS, Modality.TAVNS, Modality.CES],
                tdcs_target="Sequential targeting per dominant phenotype",
                tps_target="Per network prioritization assessment",
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="updrs",
                name="Movement Disorder Society-Unified Parkinson's Disease Rating Scale",
                abbreviation="MDS-UPDRS",
                domains=["motor", "non_motor", "activities_of_daily_living", "motor_complications"],
                timing="baseline",
                evidence_pmid="19343477",
                notes="Gold standard PD assessment. Part III (motor) most used in neuromodulation trials.",
            ),
            AssessmentTool(
                scale_key="moca",
                name="Montreal Cognitive Assessment",
                abbreviation="MoCA",
                domains=["cognition", "memory", "executive_function", "attention"],
                timing="baseline",
                evidence_pmid="15817019",
                notes="Recommended for PD-MCI screening. Score <26/30 indicates possible MCI.",
            ),
            AssessmentTool(
                scale_key="hamd",
                name="Hamilton Depression Rating Scale",
                abbreviation="HAM-D (17-item)",
                domains=["depression", "mood"],
                timing="baseline",
                evidence_pmid="14100341",
                notes="Primary mood assessment for PD depression. Score >=8 indicates clinically significant depression.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Self-report supplement to HAM-D. Score >=10 = moderate depression.",
            ),
            AssessmentTool(
                scale_key="psqi",
                name="Pittsburgh Sleep Quality Index",
                abbreviation="PSQI",
                domains=["sleep_quality", "sleep_latency", "sleep_duration"],
                timing="baseline",
                evidence_pmid="2748771",
                notes="Assess sleep quality given high prevalence of sleep disorders in PD.",
            ),
            AssessmentTool(
                scale_key="eq5d",
                name="EuroQol 5-Dimension Quality of Life",
                abbreviation="EQ-5D",
                domains=["quality_of_life", "health_utility"],
                timing="baseline",
                evidence_pmid="1634691",
                notes="Global quality of life measure for outcome tracking.",
            ),
        ],

        baseline_measures=[
            "MDS-UPDRS Part I-IV (motor and non-motor)",
            "MoCA (cognitive screening)",
            "HAM-D 17-item (depression screening)",
            "PHQ-9 (self-report depression)",
            "PSQI (sleep quality)",
            "EQ-5D (quality of life)",
            "SOZO PRS — Patient Rating System (patient-reported motor and non-motor, 0-10 scale)",
            "Timed Up and Go test (TUG) — gait and mobility",
            "10-Metre Walk Test (10MWT) — gait speed",
            "Medication state documentation (ON/OFF) at assessment",
        ],

        followup_measures=[
            "MDS-UPDRS Part III (motor) at Week 4 and Week 8-10",
            "SOZO PRS at each session (brief) and end of block (full)",
            "MoCA at Week 8-10 (cognitive protocol patients)",
            "HAM-D at Week 8-10 (limbic-affective subtype patients)",
            "Adverse event monitoring at every session",
            "EQ-5D at end of block",
        ],

        inclusion_criteria=[
            "Confirmed diagnosis of idiopathic Parkinson's Disease per MDS diagnostic criteria",
            "Hoehn & Yahr Stage 1-4 (ambulatory, without full-time nursing care)",
            "Age 40-85 years",
            "Stable dopaminergic medication regimen for >=4 weeks prior to treatment",
            "Capacity to provide informed consent",
            "Willingness to maintain consistent medication state (ON or OFF) during treatment blocks",
            "Adequate skin integrity at electrode placement sites",
        ],

        exclusion_criteria=[
            "Atypical parkinsonian syndrome (MSA, PSP, DLB, CBD) — if primary diagnosis",
            "Secondary parkinsonism (vascular, drug-induced) — unless clinician decision made",
            "Active deep brain stimulation (DBS) or spinal cord stimulator",
            "Active psychosis or severe psychiatric crisis",
            "Recent seizure within 6 months",
            "Significant cognitive impairment precluding informed consent (MMSE < 18)",
            "Skull defect or craniectomy at stimulation sites",
            "Scalp conditions (dermatitis, wound, infection) at electrode sites",
            "Pregnancy",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "Active Deep Brain Stimulation (DBS) system — unless cleared by DBS managing neurologist",
            "Hemiplegic or severe ataxic presentation (coordinate with treating neurologist)",
        ],

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "monitoring",
                "CRITICAL: Levodopa timing and ON/OFF medication state must be documented and held CONSISTENT throughout treatment blocks. Mixed ON/OFF states are the leading cause of false responder/non-responder classification.",
                "high",
                "PD-specific clinical consensus; pharmacokinetic principles of levodopa-NMDA plasticity interaction",
            ),
            make_safety(
                "precaution",
                "Motor fluctuations (wearing-off, ON-OFF phenomena) may confound outcome measures. Schedule assessments at consistent medication windows.",
                "moderate",
            ),
            make_safety(
                "monitoring",
                "Monitor for dyskinesia exacerbation following tDCS in patients on higher levodopa doses (anodal M1 stimulation may temporarily increase dyskinesia).",
                "moderate",
                "Khedr et al. (2003); Koch et al. (2009)",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Primary Motor Cortex", "M1", "bilateral",
                "M1 is hypoactive in PD due to reduced thalamocortical drive. Anodal tDCS increases cortical excitability, improving motor output. Multiple RCTs demonstrate improvements in bradykinesia, gait speed, and motor learning.",
                "C1 — Motor (Bradykinesia & Rigidity)",
                EvidenceLevel.HIGH, off_label=True,
            ),
            make_tdcs_target(
                "Dorsolateral Prefrontal Cortex", "DLPFC", "bilateral",
                "DLPFC hypoactivation underlies executive dysfunction and depression in PD. Left anodal tDCS improves working memory, cognitive flexibility, and mood.",
                "C3 — Cognition & Executive Function",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
            make_tdcs_target(
                "Supplementary Motor Area", "SMA", "bilateral",
                "SMA hypoactivity contributes to reduced movement initiation and FOG. Anodal SMA stimulation has shown benefits in gait parameters.",
                "C2 — Gait & Dual-Task",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
            make_tps_target(
                "Primary Motor Cortex", "M1", "bilateral",
                "Focused TPS on M1 delivers mechanical stimulation to the cortex-basal ganglia circuit. NEUROLITH TPS has shown significant UPDRS motor improvements in early trials.",
                "T1 — Motor",
                EvidenceLevel.LOW,
            ),
            make_tps_target(
                "Substantia Nigra / Subthalamic Region", "SN/STN", "bilateral",
                "Deep TPS targeting the midbrain region (up to 80mm depth) may directly modulate the dysfunctional basal ganglia circuit.",
                "T2 — Deep Basal Ganglia Target",
                EvidenceLevel.LOW,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C1", label="Motor — Bradykinesia & Rigidity", modality=Modality.TDCS,
                target_region="Primary Motor Cortex", target_abbreviation="M1",
                phenotype_slugs=["ar", "td", "pigd", "mn"],
                network_targets=[NetworkKey.SMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "C3 + C4 (bilateral M1)",
                    "cathode": "Fp1 + Fp2 (bilateral supraorbital)",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15 over 3 weeks",
                    "electrode_size": "35 cm2",
                    "current_density": "0.057 mA/cm2",
                },
                rationale="Anodal tDCS over M1 increases cortical excitability and facilitates dopamine-dependent motor plasticity. Multiple RCTs have demonstrated improvements in bradykinesia and gait speed in PD patients.",
                evidence_level=EvidenceLevel.HIGH, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="C2", label="Gait & Dual-Task Performance", modality=Modality.TDCS,
                target_region="Supplementary Motor Area / M1", target_abbreviation="SMA/M1",
                phenotype_slugs=["pigd", "ar", "mn"],
                network_targets=[NetworkKey.SMN, NetworkKey.ATTENTION],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "Fz (SMA) + C3/C4 (M1)",
                    "cathode": "Fp1/Fp2",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                },
                rationale="SMA hypoactivity contributes to FOG and reduced gait speed. Combined SMA+M1 anodal stimulation has shown additive benefits for gait parameters in PIGD phenotype.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="C3", label="Cognition & Executive Function", modality=Modality.TDCS,
                target_region="Dorsolateral Prefrontal Cortex", target_abbreviation="DLPFC",
                phenotype_slugs=["fe", "mn"],
                network_targets=[NetworkKey.CEN, NetworkKey.ATTENTION],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 + F4 (bilateral DLPFC)",
                    "cathode": "Fp1 + Fp2 or shoulder",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                },
                rationale="DLPFC anodal stimulation targets frontostriatal executive pathways. Evidence from multiple sham-controlled trials shows working memory and cognitive flexibility improvements.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="C4", label="Depression & Mood (Apathy)", modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex", target_abbreviation="L-DLPFC",
                phenotype_slugs=["la", "mn"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "F8 (right supraorbital or right DLPFC)",
                    "intensity": "2.0 mA",
                    "duration": "30 min",
                    "sessions": "10-15",
                    "note": "Left hemisphere bias for depression protocol",
                },
                rationale="Left DLPFC anodal stimulation is the best-evidenced tDCS montage for depression, applying the DLPFC lateralization model. Supported by robust evidence in MDD and emerging evidence in PD depression.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="T1", label="Motor (Bradykinesia & Rigidity) — TPS", modality=Modality.TPS,
                target_region="Primary Motor Cortex", target_abbreviation="M1",
                phenotype_slugs=["ar", "td", "pigd"],
                network_targets=[NetworkKey.SMN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "M1 bilateral (neuronavigation-guided)",
                    "pulses": "300-600 per session",
                    "frequency": "5 Hz",
                    "energy": "0.25 mJ/mm2",
                    "sessions": "6-9 over 3 weeks",
                },
                rationale="TPS delivers focused mechanical stimulation to motor cortex, modulating cortical-subcortical circuits. Koch et al. (2019) demonstrated significant UPDRS-III improvements with NEUROLITH in early PD. OFF-LABEL — requires Doctor authorization.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=9,
                notes="OFF-LABEL application. Requires explicit patient consent and Doctor authorization before each treatment block.",
            ),
            ProtocolEntry(
                protocol_id="T2", label="Tremor — TPS", modality=Modality.TPS,
                target_region="Primary Motor Cortex / Cerebellum", target_abbreviation="M1/CB",
                phenotype_slugs=["td"],
                network_targets=[NetworkKey.SMN],
                parameters={
                    "device": "NEUROLITH",
                    "target": "M1 contralateral to dominant tremor + optional cerebellar",
                    "pulses": "300 per session",
                    "frequency": "5 Hz",
                    "energy": "0.25 mJ/mm2",
                    "sessions": "6",
                },
                rationale="Tremor-dominant PD involves aberrant oscillatory activity in the cerebellar-thalamocortical pathway. TPS targeting of M1 and optional cerebellar cortex may modulate tremor-generating circuits.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=6,
            ),
            ProtocolEntry(
                protocol_id="CES-1", label="Alpha-Stim CES — Anxiety/Sleep (Adjunct)", modality=Modality.CES,
                target_region="Bilateral earlobe (alpha wave entrainment)", target_abbreviation="CES",
                phenotype_slugs=["la", "mn"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim",
                    "frequency": "0.5 Hz",
                    "intensity": "100-300 uA",
                    "duration": "40 min",
                    "sessions": "Daily or alternate day",
                },
                rationale="CES has FDA clearance for anxiety, depression, and insomnia. As adjunct therapy, supports limbic network regulation and sleep quality in PD patients with mood and sleep disturbances.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
            ),
        ],

        symptom_network_mapping={
            "Bradykinesia / Rigidity": [NetworkKey.SMN],
            "Tremor": [NetworkKey.SMN, NetworkKey.ATTENTION],
            "Freezing of Gait": [NetworkKey.SMN, NetworkKey.ATTENTION],
            "Executive Dysfunction": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Memory Impairment (PD-MCI)": [NetworkKey.CEN, NetworkKey.DMN],
            "Depression / Apathy": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Anxiety": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Pain": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Sleep Disturbance": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "Fatigue": [NetworkKey.SN, NetworkKey.LIMBIC],
        },

        symptom_modality_mapping={
            "Bradykinesia / Rigidity": [Modality.TDCS, Modality.TPS],
            "Tremor": [Modality.TDCS, Modality.TPS],
            "Freezing of Gait": [Modality.TDCS, Modality.TPS, Modality.TAVNS],
            "Executive Dysfunction": [Modality.TDCS, Modality.TPS],
            "Memory Impairment (PD-MCI)": [Modality.TDCS, Modality.TPS],
            "Depression / Apathy": [Modality.TDCS, Modality.CES, Modality.TAVNS],
            "Anxiety": [Modality.CES, Modality.TAVNS, Modality.TDCS],
            "Pain": [Modality.TDCS, Modality.TPS, Modality.CES],
            "Sleep Disturbance": [Modality.CES, Modality.TAVNS],
            "Fatigue": [Modality.CES, Modality.TAVNS],
        },

        responder_criteria=[
            ">=30% improvement in MDS-UPDRS Part III (motor) from baseline",
            ">=2-point improvement in SOZO PRS motor domain score (0-10 scale)",
            "Clinically meaningful functional improvement (patient and clinician rated)",
            "Improvement in >=1 secondary domain: cognition, mood, sleep, pain, or quality of life",
            "Maintenance of improvement at Week 8-10 assessment",
        ],

        non_responder_pathway=(
            "For patients classified as non-responders at Week 4 (and confirmed at Week 8):\n"
            "1. Repeat 6-Network Bedside Assessment (Partners tier) to re-evaluate network dysfunction\n"
            "2. Re-examine medication state consistency during treatment block\n"
            "3. Re-evaluate phenotype classification — mixed phenotypes may require multi-network targeting\n"
            "4. Consider switching from bilateral M1 to unilateral contralateral M1 + SMA combined montage\n"
            "5. Consider adding TPS to tDCS (if not already included) — Doctor authorization required\n"
            "6. Consider adding taVNS as adjunct for PIGD/gait phenotype\n"
            "7. Doctor review and approval mandatory before any protocol modification\n"
            "8. If still non-responder after second block adjustment: discontinue and document"
        ),

        levodopa_note=(
            "Levodopa timing is critical. Levodopa-induced dopamine release potentiates NMDA-dependent "
            "long-term potentiation (LTP), which is the mechanism of tDCS plasticity induction. "
            "Inconsistent ON/OFF timing across sessions can reverse or cancel tDCS effects. "
            "SOZO RULE: Select ONE state (ON or OFF) for the treatment block and document at every session. "
            "Preferred state: ON-state (post-levodopa) for motor protocols."
        ),

        evidence_summary=(
            "Parkinson's Disease represents the strongest neuromodulation evidence base among SOZO conditions. "
            "tDCS: Multiple sham-controlled RCTs (Benninger 2010, Boggio 2006, Khedr 2013, Doruk 2014) demonstrate "
            "significant improvements in UPDRS motor scores with M1 anodal tDCS. Meta-analyses (Doruk Cengiz et al. 2020) "
            "confirm medium effect sizes for motor outcomes. Cognitive tDCS (DLPFC): moderate evidence from smaller trials. "
            "TPS: Emerging evidence from Koch et al. (2019) and subsequent studies using NEUROLITH; OFF-LABEL for PD. "
            "taVNS and CES: Limited PD-specific evidence; broader neuropsychiatric evidence supports adjunct use."
        ),

        evidence_gaps=[
            "Head-to-head trials comparing tDCS protocols (M1 vs SMA vs DLPFC) in PD — no direct comparisons published",
            "Long-term maintenance effects of neuromodulation in PD beyond 3 months — limited data",
            "TPS in advanced PD (H&Y 4-5) — insufficient trial data",
            "Optimal tDCS montage for tremor-dominant vs akinetic-rigid phenotypes — underpowered comparative data",
            "taVNS in PD: emerging pilot data only — no adequately powered RCT completed",
            "Combined tDCS + TPS (multimodal) in PD: rationale strong, evidence limited to case series",
        ],

        review_flags=[
            "TPS protocols require explicit off-label consent documentation at every treatment block",
            "Levodopa state consistency must be verified before each treatment session",
        ],

        references=[
            {
                "authors": "Doruk Cengiz A et al.",
                "year": 2020,
                "title": "tDCS in Parkinson's Disease: A Systematic Review and Meta-analysis",
                "journal": "Neurological Sciences",
                "pmid": "32180044",
                "evidence_type": "systematic_review",
            },
            {
                "authors": "Benninger DH et al.",
                "year": 2010,
                "title": "Transcranial direct current stimulation for the treatment of Parkinson's disease",
                "journal": "Journal of Neurology, Neurosurgery & Psychiatry",
                "pmid": "20801741",
                "evidence_type": "rct",
            },
            {
                "authors": "Boggio PS et al.",
                "year": 2006,
                "title": "Effects of transcranial direct current stimulation on working memory in patients with Parkinson's disease",
                "journal": "Journal of the Neurological Sciences",
                "pmid": "16949616",
                "evidence_type": "rct",
            },
            {
                "authors": "Khedr EM et al.",
                "year": 2013,
                "title": "Therapeutic utility of bifrontal transcranial direct current stimulation in Parkinson's disease",
                "journal": "European Journal of Neurology",
                "pmid": "23421889",
                "evidence_type": "rct",
            },
            {
                "authors": "Koch G et al.",
                "year": 2019,
                "title": "TPS stimulation in Parkinson's disease — early outcomes",
                "journal": "Neuromodulation",
                "pmid": "REVIEW_REQUIRED_TPS",
                "evidence_type": "pilot_study",
                "notes": "REVIEW: Confirm specific TPS/NEUROLITH citation — update PMID",
            },
            {
                "authors": "Goetz CG et al.",
                "year": 2008,
                "title": "Movement Disorder Society-sponsored revision of the Unified Parkinson's Disease Rating Scale (MDS-UPDRS): Scale presentation and clinimetric testing results",
                "journal": "Movement Disorders",
                "pmid": "19343477",
                "evidence_type": "clinical_practice_guideline",
            },
            {
                "authors": "Nasreddine ZS et al.",
                "year": 2005,
                "title": "The Montreal Cognitive Assessment, MoCA: a brief screening tool for mild cognitive impairment",
                "journal": "Journal of the American Geriatrics Society",
                "pmid": "15817019",
                "evidence_type": "clinical_practice_guideline",
            },
        ],

        overall_evidence_quality=EvidenceLevel.HIGH,

        patient_journey_notes={
            "stage_1": (
                "Pre-screen for PD diagnosis (confirmed by neurologist). Confirm medication regimen stability (>=4 weeks). "
                "Screen for absolute contraindications. Document H&Y stage and current medications including levodopa equivalence dose (LED). "
                "Establish medication state (ON/OFF) preference for treatment block."
            ),
            "stage_3": (
                "Administer SOZO PRS (motor + non-motor domains). Document levodopa timing and last dose. "
                "Conduct structured psychiatric interview with emphasis on depression, anxiety, apathy, and impulse control. "
                "Flag suicidal ideation per protocol — escalate immediately if present. "
                "Document current pharmacological treatment including dopamine agonists, MAOIs, anticholinergics."
            ),
            "stage_4": (
                "Administer MDS-UPDRS Part I-III in consistent medication state. "
                "Apply PD phenotype classification algorithm (TD/AR/PIGD/FE/LA/PA/MN). "
                "Conduct 6-Network Bedside Assessment (Partners tier). "
                "Perform TUG and 10MWT for gait documentation. "
                "Document tremor frequency, rigidity pattern, and FOG assessment."
            ),
            "stage_5": (
                "Apply FNON phenotype-to-protocol selection: identify primary network (SMN primary for most PD), "
                "select tDCS montage (C1/C2/C3/C4), assess TPS suitability (Doctor authorization required), "
                "determine adjunct modality need (CES for sleep/anxiety, taVNS for gait/FOG). "
                "Confirm and document medication state for treatment block."
            ),
        },

        clinical_tips=[
            "Always confirm consistent medication state before treatment — document ON or OFF and levodopa dose timing at every session",
            "For tremor-dominant PD, consider cerebellar tDCS/TPS as adjunct to M1 protocols (emerging evidence)",
            "Dyskinesia monitoring: anodal M1 tDCS may temporarily increase dyskinesias in patients on high LED — reduce intensity if necessary",
            "Dual-task paradigms during tDCS delivery may enhance gait outcomes (concurrent motor task during stimulation)",
            "PIGD phenotype patients benefit from combining tDCS with active physiotherapy during the same session window",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Levodopa medication state must be documented at every PD session — this is mandatory",
            "TPS for PD is explicitly OFF-LABEL — off-label consent documentation required in patient file before every treatment block",
            "Any worsening of dyskinesia following tDCS must be documented and reported to the treating Doctor same day",
        ],
    )
