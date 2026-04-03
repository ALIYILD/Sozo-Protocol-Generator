"""
Major Depressive Disorder (MDD) — Complete condition generator.

Key references:
- Brunoni AR et al. (2013) SELECT-TDCS trial — JAMA Psychiatry
- Blumberger DM et al. (2018) ELECT-TDCS: tDCS vs escitalopram vs sham
- Bikson M et al. (2016) Safety of transcranial direct current stimulation — Brain Stimulation
- Brunoni AR et al. (2016) tDCS meta-analysis for MDD
- Dell'Osso B et al. (2012) taVNS for MDD
- TADS (Treatment of Adolescents with Depression Study) — JAMA 2004
- DSM-5 diagnostic criteria for MDD
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


def build_depression_condition() -> ConditionSchema:
    """Build the complete Major Depressive Disorder condition schema."""
    return ConditionSchema(
        slug="depression",
        display_name="Major Depressive Disorder",
        icd10="F32",
        aliases=["MDD", "major depression", "unipolar depression", "clinical depression"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Major Depressive Disorder (MDD) is a highly prevalent, recurrent psychiatric disorder "
            "characterized by persistent low mood, anhedonia, and a range of cognitive, somatic, and "
            "neurovegetative symptoms. MDD affects approximately 264 million people globally (WHO), "
            "with lifetime prevalence of 15-20% in high-income countries. It is a leading cause of "
            "disability worldwide. Approximately 30-40% of MDD patients fail to respond to two or more "
            "adequate antidepressant trials, meeting criteria for Treatment-Resistant Depression (TRD). "
            "tDCS targeting the left DLPFC represents one of the best-evidenced non-invasive "
            "neuromodulation approaches in psychiatry, supported by multiple sham-controlled RCTs "
            "and meta-analyses."
        ),

        pathophysiology=(
            "MDD involves dysfunction across multiple neurobiological systems. The monoaminergic "
            "hypothesis implicates serotonin, noradrenaline, and dopamine deficits, forming the "
            "basis of pharmacological treatment. Neuroimaging studies reveal a consistent pattern "
            "of left DLPFC hypoactivation and subgenual anterior cingulate cortex (sgACC/Cg25) "
            "hyperactivation in MDD. The sgACC serves as a critical node linking cortical and "
            "limbic circuits; its hyperactivity propagates depressogenic tone throughout the "
            "default mode network.\n\n"
            "The network-level model of MDD identifies three core network disruptions: "
            "(1) Default Mode Network (DMN) hyperactivation — excessive self-referential rumination; "
            "(2) Central Executive Network (CEN/FPN) hypoactivation — impaired cognitive control "
            "and emotion regulation; (3) Salience Network (SN) dysregulation — aberrant switching "
            "between networks.\n\n"
            "Neuroplasticity impairment is increasingly recognized: reduced BDNF signaling, "
            "hippocampal volume loss (particularly in recurrent MDD), and impaired synaptic "
            "plasticity in prefrontal circuits. HPA axis hyperactivity drives glucocorticoid-mediated "
            "prefrontal and hippocampal damage. Neuroinflammatory markers (elevated IL-6, TNF-alpha, "
            "CRP) are elevated in a significant subset of MDD patients."
        ),

        core_symptoms=[
            "Persistent depressed mood (most of the day, nearly every day)",
            "Anhedonia — markedly diminished interest or pleasure in activities",
            "Significant weight change or appetite disturbance",
            "Insomnia or hypersomnia",
            "Psychomotor agitation or retardation (observable by others)",
            "Fatigue or loss of energy nearly every day",
            "Feelings of worthlessness or excessive/inappropriate guilt",
            "Diminished ability to think, concentrate, or make decisions",
            "Recurrent thoughts of death, suicidal ideation, or suicide attempt",
        ],

        non_motor_symptoms=[
            "Cognitive impairment (attention, working memory, executive function)",
            "Anxiety symptoms (comorbid anxiety in 60-70% of MDD patients)",
            "Somatic complaints (headache, chronic pain, GI symptoms)",
            "Social withdrawal and functional impairment",
            "Irritability (more prevalent in younger patients and males)",
            "Emotional blunting (common with antidepressant treatment)",
        ],

        key_brain_regions=[
            "Left Dorsolateral Prefrontal Cortex (L-DLPFC)",
            "Right Dorsolateral Prefrontal Cortex (R-DLPFC)",
            "Subgenual Anterior Cingulate Cortex (sgACC / Cg25)",
            "Anterior Cingulate Cortex (ACC / Cg24)",
            "Amygdala (bilateral)",
            "Hippocampus (bilateral)",
            "Ventromedial Prefrontal Cortex (vmPFC)",
            "Orbitofrontal Cortex (OFC)",
            "Insula (anterior)",
            "Nucleus Accumbens / Ventral Striatum",
        ],

        brain_region_descriptions={
            "Left Dorsolateral Prefrontal Cortex (L-DLPFC)": "Consistently hypoactive in MDD; primary tDCS anodal target. Mediates cognitive control, emotion regulation, and top-down suppression of limbic activity.",
            "Right Dorsolateral Prefrontal Cortex (R-DLPFC)": "Relatively hyperactive in MDD relative to left; cathode placement target in left-anodal montage. Involved in negative emotion processing.",
            "Subgenual Anterior Cingulate Cortex (sgACC / Cg25)": "Hyperactive hub in MDD; downstream target of DLPFC stimulation via cortico-cortical connectivity. sgACC hyperactivity correlates with rumination and treatment resistance.",
            "Anterior Cingulate Cortex (ACC / Cg24)": "Involved in error monitoring, conflict processing, and mood regulation. Dorsal ACC activity predicts antidepressant response.",
            "Amygdala (bilateral)": "Hyperreactive to negative stimuli in MDD. Reduced DLPFC-amygdala connectivity underlies emotion dysregulation.",
            "Hippocampus (bilateral)": "Volume loss in recurrent MDD; impaired neurogenesis. Mediates episodic memory and contextual fear learning.",
            "Ventromedial Prefrontal Cortex (vmPFC)": "Part of DMN; involved in self-referential processing and reward valuation. Hyperactive in ruminative MDD.",
            "Orbitofrontal Cortex (OFC)": "Mediates reward processing and decision-making. Dysfunction contributes to anhedonia and negative bias.",
            "Insula (anterior)": "Key SN node; interoceptive processing. Hyperactive in MDD, contributing to somatic complaints and emotional salience dysregulation.",
            "Nucleus Accumbens / Ventral Striatum": "Dopaminergic reward circuit; hypoactive in anhedonic MDD. Target of antidepressant pharmacotherapy.",
        },

        network_profiles=[
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "PRIMARY DYSFUNCTIONAL NETWORK IN MDD. DMN hyperactivation underlies pathological "
                "self-referential rumination, negative autobiographical memory retrieval, and "
                "failure to task-disengage. Hyperconnectivity between sgACC and MPFC propagates "
                "depressogenic tone. DMN hyperactivity is the most replicated neuroimaging finding in MDD.",
                primary=True, severity="severe",
                evidence_note="Most replicated finding in MDD neuroimaging; Greicius et al. 2007, Hamilton et al. 2011",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "Left DLPFC hypoactivation impairs cognitive control, working memory, and top-down "
                "emotion regulation. CEN hypofunction allows limbic and DMN hyperactivity to persist "
                "unchecked. CEN upregulation via anodal tDCS is the primary treatment mechanism.",
                severity="severe",
                evidence_note="Robust fMRI evidence; foundational basis for DLPFC tDCS in MDD",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "Anterior insula and dACC hyperactivity drives aberrant salience attribution to negative "
                "stimuli. Impaired network switching (SN normally toggles between DMN and CEN) "
                "perpetuates DMN hyperactivation and CEN suppression.",
                severity="moderate",
                evidence_note="Menon (2011) triple network model; SN dysregulation in MDD",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Amygdala hyperreactivity, hippocampal dysfunction, and reduced prefrontal-limbic "
                "connectivity underpin emotional dysregulation, anhedonia, and persistent negative mood. "
                "HPA axis dysregulation further amplifies limbic hyperactivity.",
                severity="severe",
                evidence_note="Drevets et al., multiple meta-analyses of MDD neuroimaging",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Attention and concentration impairment are core cognitive features of MDD, "
                "reflecting frontal dopamine depletion and competition with hyperactive DMN. "
                "Attentional bias toward negative stimuli further compounds depressive cognition.",
                severity="moderate",
            ),
        ],

        primary_network=NetworkKey.DMN,

        fnon_rationale=(
            "In MDD, the triple network model identifies DMN hyperactivation and CEN hypoactivation "
            "as the core pathological network pattern. FNON framework targets left DLPFC (CEN node) "
            "for anodal upregulation to restore CEN-DMN balance, while right DLPFC cathodal placement "
            "reduces relative right hemispheric hyperactivation. Secondary limbic network targeting "
            "addresses treatment-resistant and melancholic subtypes. All network interventions aim "
            "to restore the physiological CEN-SN-DMN anticorrelated balance."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="mel",
                label="MEL — Melancholic Depression",
                description="Severe anhedonia, psychomotor changes, diurnal variation (worse in morning), early awakening, and marked weight loss. Reflects profound limbic and dopaminergic dysfunction.",
                key_features=["Anhedonia", "Psychomotor retardation or agitation", "Diurnal variation", "Early awakening", "Marked weight loss"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.CEN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.SN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal (F3) + right DLPFC cathodal (F4)",
                tps_target="Left DLPFC targeting (off-label)",
            ),
            PhenotypeSubtype(
                slug="aty",
                label="ATY — Atypical Depression",
                description="Mood reactivity, hypersomnia, leaden paralysis, hyperphagia, and rejection sensitivity. Higher anxiety and stronger limbic reactivity.",
                key_features=["Mood reactivity", "Hypersomnia", "Hyperphagia", "Rejection sensitivity", "Leaden paralysis"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal + right supraorbital cathodal",
                tps_target="Left DLPFC / insula targeting",
            ),
            PhenotypeSubtype(
                slug="anx",
                label="ANX — Anxious Depression",
                description="Prominent anxiety, tension, worry, and psychomotor agitation superimposed on depressive syndrome. SN hyperactivity predominant.",
                key_features=["Prominent anxiety", "Psychomotor agitation", "Tension", "Worry", "Somatic symptoms"],
                primary_networks=[NetworkKey.SN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal + right cathodal; CES adjunct",
                tps_target="Left DLPFC targeting",
            ),
            PhenotypeSubtype(
                slug="trd",
                label="TRD — Treatment-Resistant Depression",
                description="Failure to respond to >=2 adequate antidepressant trials of different classes. Requires multi-network targeting and combination neuromodulation strategies.",
                key_features=[">=2 failed antidepressant trials", "Persistent severe depression", "Functional impairment", "Possible suicidality"],
                primary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                preferred_modalities=[Modality.TDCS, Modality.TPS, Modality.TAVNS, Modality.CES, Modality.ITBS],
                tdcs_target="Left DLPFC anodal — higher intensity protocol (2 mA, 30 min, 20+ sessions)",
                tps_target="Left DLPFC TPS — off-label, Doctor authorization required",
                tbs_target="Left DLPFC iTBS — accelerated 3×/day, 30-min ISI, 600 pulses/session (TTT Protocol)",
            ),
            PhenotypeSubtype(
                slug="cog",
                label="COG — Cognitive/Pseudodementia Subtype",
                description="Prominent cognitive complaints (memory, concentration, executive function) that may mimic dementia. CEN dysfunction predominant.",
                key_features=["Memory complaints", "Concentration difficulties", "Executive dysfunction", "Psychomotor slowing"],
                primary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.ATTENTION, NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.TPS, Modality.CES],
                tdcs_target="Left DLPFC anodal bilateral for cognitive enhancement",
                tps_target="DLPFC + hippocampal targeting",
            ),
            PhenotypeSubtype(
                slug="sad",
                label="SAD — Seasonal Affective Disorder",
                description="Recurrent depressive episodes with seasonal pattern (typically autumn/winter onset). Circadian rhythm and light-sensitive hypothalamic pathways implicated.",
                key_features=["Seasonal pattern", "Hypersomnia", "Hyperphagia", "Fatigue", "Social withdrawal"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.CES],
                tdcs_target="Left DLPFC anodal protocol",
                tps_target="Left DLPFC targeting (adjunct to light therapy)",
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="hdrs",
                name="Hamilton Depression Rating Scale",
                abbreviation="HDRS-17",
                domains=["depression_severity", "mood", "somatic", "sleep", "anxiety"],
                timing="baseline",
                evidence_pmid="14100341",
                notes="Clinician-administered gold standard for MDD severity. Score >=18 = moderate-severe. Primary outcome measure in most tDCS trials.",
            ),
            AssessmentTool(
                scale_key="madrs",
                name="Montgomery-Asberg Depression Rating Scale",
                abbreviation="MADRS",
                domains=["depression_severity", "mood", "cognitive", "somatic"],
                timing="baseline",
                evidence_pmid="444788",
                notes="Highly sensitive to change; preferred outcome measure in antidepressant and neuromodulation trials. Score >=20 = moderate depression.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression", "self_report"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Self-report measure; score >=10 = moderate depression. Simple monitoring tool between sessions.",
            ),
            AssessmentTool(
                scale_key="gad7",
                name="Generalized Anxiety Disorder 7-item Scale",
                abbreviation="GAD-7",
                domains=["anxiety", "worry"],
                timing="baseline",
                evidence_pmid="16717171",
                notes="Co-administer to screen for anxious MDD subtype. Score >=10 = moderate anxiety.",
            ),
            AssessmentTool(
                scale_key="bdi2",
                name="Beck Depression Inventory II",
                abbreviation="BDI-II",
                domains=["depression", "cognition", "somatic", "self_report"],
                timing="baseline",
                evidence_pmid="8853308",
                notes="Self-report supplement. Useful for tracking cognitive and somatic domains. Score >=20 = moderate.",
            ),
            AssessmentTool(
                scale_key="moca",
                name="Montreal Cognitive Assessment",
                abbreviation="MoCA",
                domains=["cognition", "memory", "executive_function"],
                timing="baseline",
                evidence_pmid="15817019",
                notes="Administer for COG phenotype and patients >=55 years to exclude neurodegenerative comorbidity.",
            ),
        ],

        baseline_measures=[
            "HDRS-17 (clinician-administered depression severity)",
            "MADRS (depression severity — change-sensitive)",
            "PHQ-9 (self-report depression)",
            "GAD-7 (anxiety co-assessment)",
            "BDI-II (self-report — cognitive and somatic domains)",
            "SOZO PRS (patient-rated mood, anxiety, energy, sleep, social function — 0-10)",
            "Suicidality screening: Columbia Suicide Severity Rating Scale (C-SSRS) — mandatory",
            "Current medications and treatment history (antidepressants, benzodiazepines, antipsychotics)",
            "MoCA (COG subtype / older patients)",
        ],

        followup_measures=[
            "HDRS-17 at Week 4 and Week 8-10",
            "MADRS at Week 4 and Week 8-10",
            "PHQ-9 at each session (brief monitoring)",
            "SOZO PRS full assessment at end of block",
            "GAD-7 at Week 8-10 (anxious subtype)",
            "C-SSRS at every session — mandatory suicidality monitoring",
            "Adverse event documentation at every session",
        ],

        inclusion_criteria=[
            "DSM-5 diagnosis of Major Depressive Disorder (single episode or recurrent)",
            "Current depressive episode: HDRS-17 >=14 or PHQ-9 >=10",
            "Age 18-75 years",
            "Capacity to provide informed consent",
            "Stable psychiatric medication regimen for >=4 weeks (or medication-naive)",
            "Adequate skin integrity at electrode placement sites",
            "Willingness to complete full treatment block and assessment schedule",
        ],

        exclusion_criteria=[
            "Bipolar disorder (Type I or II) — absolute exclusion: anodal DLPFC stimulation may precipitate mania",
            "Active psychosis or psychotic features",
            "Active suicidal ideation with intent or plan (refer for acute care)",
            "Substance use disorder (current, active)",
            "Current ECT treatment or within 4 weeks",
            "Personality disorder as primary diagnosis (relative exclusion — requires Doctor assessment)",
            "Significant cognitive impairment precluding informed consent",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "Bipolar disorder (any type) — tDCS may precipitate manic switch; strict exclusion unless Doctor override with documented rationale",
            "Active suicidal crisis requiring hospitalization",
        ],

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "monitoring",
                "MANDATORY: Columbia Suicide Severity Rating Scale (C-SSRS) must be administered at EVERY session. Any new or worsening suicidal ideation with intent requires immediate escalation to treating Doctor and crisis protocol activation.",
                "high",
                "Clinical governance requirement; SOZO safety protocol",
            ),
            make_safety(
                "contraindication",
                "Bipolar disorder: anodal left DLPFC tDCS carries risk of manic switch. Strictly exclude all bipolar patients unless explicitly authorized by treating psychiatrist with documented rationale.",
                "absolute",
                "Consensus safety guidelines for tDCS in psychiatric disorders",
            ),
            make_safety(
                "precaution",
                "Monitor for emotional lability, hypomanic symptoms, or behavioral activation during treatment. Discontinue and refer to psychiatrist if hypomanic symptoms emerge.",
                "high",
                "Known risk in patients with subthreshold bipolar features",
            ),
            make_safety(
                "monitoring",
                "Document current antidepressant medication and dosage at every session. Medication changes during treatment block can confound response assessment.",
                "moderate",
            ),
            make_safety(
                "precaution",
                "TPS session spacing: minimum 48h between sessions required; 72h preferred for TRD patients. "
                "Do not compress sessions to <48h apart — biophysical rationale for spacing interval. "
                "Skull defects or craniectomy at the stimulation site are a hard contraindication for TPS. "
                "Elevated INR (anticoagulation) and metallic intracranial implants within the acoustic field: "
                "contact Storz Medical for device-specific guidance before proceeding.",
                "high",
                "TPS-specific safety requirement; NEUROLITH device protocol (Storz Medical)",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Left Dorsolateral Prefrontal Cortex", "L-DLPFC", "left",
                "Left DLPFC is the primary tDCS target for MDD, supported by the DLPFC lateralization model. "
                "Anodal stimulation increases left DLPFC excitability, restoring CEN-DMN balance and improving "
                "emotion regulation. Multiple RCTs (Brunoni 2013, Blumberger 2018) confirm antidepressant efficacy.",
                "C4 — Depression & Mood",
                EvidenceLevel.HIGH, off_label=True,
            ),
            make_tps_target(
                "Left DLPFC + sgACC Network (Extended)", "L-DLPFC/sgACC", "left",
                "TPS targets left DLPFC and its anti-correlated sgACC circuit via focused acoustic pulse energy. "
                "The DLPFC–sgACC anti-correlation (from resting-state fMRI) defines the core depression circuit: "
                "DLPFC hypoactivation and sgACC hyperactivation co-vary. Open-label pilot data (Storz Medical, "
                "Swiss cohorts) report 29–40% BDI-II reduction and fMRI functional connectivity normalization. "
                "Session spacing of 48–72h enforced. OFF-LABEL for depression — Doctor authorization mandatory.",
                "T-DEP — TPS Depression (DLPFC/sgACC)",
                EvidenceLevel.LOW,
            ),
            make_tdcs_target(
                "Anterior Cingulate Cortex", "ACC", "bilateral",
                "ACC targeting addresses DMN hyperactivation and ruminative processing. "
                "Cathodal ACC placement can reduce sgACC hyperactivity. Emerging evidence only.",
                "ACC — Rumination Protocol",
                EvidenceLevel.LOW, off_label=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C4-STD", label="Depression — Standard DLPFC Protocol", modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex", target_abbreviation="L-DLPFC",
                phenotype_slugs=["mel", "aty", "anx", "sad"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "F4 (right DLPFC) or Fp2 (right supraorbital)",
                    "intensity": "2.0 mA",
                    "duration": "30 min",
                    "sessions": "10-15 over 3 weeks",
                    "electrode_size": "35 cm2",
                    "current_density": "0.057 mA/cm2",
                    "note": "Brunoni montage: anode F3, cathode Fp2 — SELECT-TDCS protocol",
                },
                rationale="Left DLPFC anodal tDCS is the most-evidenced tDCS protocol in psychiatry. SELECT-TDCS (Brunoni 2013, N=120) demonstrated antidepressant efficacy equivalent to sertraline and superior to sham. ELECT-TDCS (Blumberger 2018) confirmed efficacy vs sham and non-inferiority to escitalopram.",
                evidence_level=EvidenceLevel.HIGH, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="C4-TRD", label="Treatment-Resistant Depression — Intensive Protocol", modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex", target_abbreviation="L-DLPFC",
                phenotype_slugs=["trd"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN, NetworkKey.LIMBIC],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "F4 (right DLPFC)",
                    "intensity": "2.0 mA",
                    "duration": "30 min",
                    "sessions": "20-25 (extended block)",
                    "note": "Consider twice-daily sessions (4h gap) for acute TRD — evidence from acute protocol studies",
                },
                rationale="TRD requires extended treatment blocks. Evidence supports 20+ sessions for TRD population. Combination with taVNS or CES may enhance outcomes. Doctor authorization required for extended blocks.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=25,
                notes="Extended protocol for TRD — requires treating psychiatrist coordination",
            ),
            ProtocolEntry(
                protocol_id="C4-ATBS",
                label="TRD — Accelerated iTBS (TTT Protocol, Window 6)",
                modality=Modality.ITBS,
                target_region="Left Dorsolateral Prefrontal Cortex",
                target_abbreviation="L-DLPFC",
                phenotype_slugs=["trd"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "device": "MagVenture MagPro or MagStim Rapid2",
                    "target": "Left DLPFC — 5.5 cm rule or Beam F3 neuronavigation",
                    "pattern": "intermittent TBS (iTBS)",
                    "pulses_per_session": "600",
                    "sessions_per_day": "3",
                    "inter_session_interval": "30 min (minimum — validated pragmatic ISI)",
                    "total_days": "5–10",
                    "total_sessions": "15–30",
                    "intensity": "80% active motor threshold (AMT)",
                    "train_pattern": "2s on / 8s off × 20 trains",
                    "frequency": "50 Hz triplets at 5 Hz (TBS pattern)",
                    "motor_threshold_method": "Active MT — visual muscle twitch or EMG",
                    "evidence_rct": "54.7% HAM-D reduction vs 31.87% sham (triple-blind RCT, PMID: 36894537)",
                    "note": "Doctor prescription and TMS-trained operator required. AMT re-check mandatory at each day-block.",
                },
                rationale=(
                    "Accelerated iTBS (3 sessions/day, 30-min ISI, 600 pulses/session) delivers compressed "
                    "neuromodulation over 5–10 days, yielding rapid antidepressant effects in TRD. "
                    "A triple-blinded pragmatic RCT (Williams et al. 2023, PMID 36894537) demonstrated "
                    "54.7% HAM-D reduction vs 31.87% sham with the 30-min ISI protocol, establishing "
                    "pragmatic feasibility. The 30-min ISI is the validated minimum interval balancing "
                    "clinical throughput and LTP-like synaptic consolidation. Left DLPFC targets the "
                    "hypoactive CEN node, restoring CEN-DMN anticorrelation — the core pathological "
                    "signature of TRD."
                ),
                evidence_level=EvidenceLevel.HIGH,
                off_label=False,
                session_count=30,
                notes=(
                    "Window 6 Protocol — TTT (Triple-session Theta-burst Treatment). "
                    "Requires TMS-trained operator, AMT calibration before each day-block, "
                    "C-SSRS at every session, seizure safety checklist, and on-site resuscitation "
                    "readiness. See Window 6 subagent fidelity checklist for site deployment."
                ),
            ),
            ProtocolEntry(
                protocol_id="TAVNS-DEP", label="taVNS — Depression Adjunct", modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve", target_abbreviation="taVNS",
                phenotype_slugs=["mel", "aty", "trd", "anx"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN, NetworkKey.DMN],
                parameters={
                    "device": "NEMOS (tVNS Technologies) or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "200-250 us",
                    "intensity": "Below pain threshold (0.5-5.0 mA)",
                    "duration": "30 min",
                    "sessions": "Daily adjunct during tDCS block",
                    "electrode_placement": "Left cymba conchae",
                },
                rationale="taVNS activates NTS-LC-cortical pathways, modulating noradrenergic and serotonergic tone. Multiple RCTs (Rong et al., 2016) demonstrate antidepressant effects. As adjunct to tDCS, may enhance limbic network regulation.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="CES-DEP", label="Alpha-Stim CES — Depression/Anxiety/Insomnia", modality=Modality.CES,
                target_region="Bilateral earlobe electrodes", target_abbreviation="CES",
                phenotype_slugs=["anx", "mel", "sad", "aty"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim",
                    "frequency": "0.5 Hz",
                    "intensity": "100-300 uA",
                    "duration": "40-60 min",
                    "sessions": "Daily during treatment block",
                },
                rationale="Alpha-Stim CES has FDA clearance for anxiety, depression, and insomnia. Adjunct to tDCS in MDD to address limbic and sleep disturbance components. Systematic review (Kirsch 2002) supports CES for depression and anxiety.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
            ),
            ProtocolEntry(
                protocol_id="T-DEP", label="TPS — Left DLPFC/sgACC Network (MDD/TRD)", modality=Modality.TPS,
                target_region="Left DLPFC + sgACC Network (Extended)", target_abbreviation="L-DLPFC/sgACC",
                phenotype_slugs=["trd", "mel", "cog"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN, NetworkKey.LIMBIC],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Left DLPFC extended (F3 landmark) — neuronavigation-guided; sgACC via indirect network modulation",
                    "energy": "0.25–0.5 mJ/mm² (start 0.25; titrate to 0.5 for TRD/non-response)",
                    "frequency": "1–4 Hz (1 Hz for acute/severe; 4 Hz for maintenance/cognitive subtype)",
                    "pulses": "200–400 per session",
                    "sessions": "2–3 per week × 4–6 weeks (8–18 sessions total)",
                    "session_spacing": "Minimum 48h between sessions; 72h preferred for TRD",
                    "severity_routing": "BDI-II ≥14: standard energy 0.25 mJ/mm², 3×/week; BDI-II ≥9 (mild): 0.25 mJ/mm², 2×/week",
                    "adjunct": "Add-on to standard pharmacotherapy; do not suspend antidepressants",
                    "swiss_protocol_note": "Based on Storz Medical NEUROLITH Depression protocol — confirm device-specific parameters with manufacturer",
                },
                rationale=(
                    "TPS delivers focused acoustic pulse energy to left DLPFC, targeting the DLPFC–sgACC "
                    "anti-correlation circuit identified on resting-state fMRI as the core MDD network. "
                    "The sgACC (Cg25) hyperactivation in MDD is indirectly modulated via downstream "
                    "DLPFC–sgACC connectivity changes. Open-label pilot data (Swiss cohorts, Storz Medical) "
                    "report 29–40% BDI-II reduction and fMRI functional connectivity normalization at 4–6 weeks. "
                    "Works as add-on to standard care — superior outcomes reported vs TPS monotherapy. "
                    "DLPFC–sgACC anti-correlation mapping from fcMRI can guide individual target optimization. "
                    "Evidence level: LOW (open-label, pilot data only) — no published RCT for TPS in MDD. "
                    "OFF-LABEL: explicit off-label consent and Doctor authorization mandatory."
                ),
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=12,
                notes=(
                    "OFF-LABEL. Doctor authorization and off-label consent documentation required. "
                    "Enforce 48–72h minimum between sessions. Monitor for headache, scalp discomfort. "
                    "Contraindications: skull defects at target site, metallic intracranial implants, "
                    "anticoagulation with elevated INR. Comorbidity routing: if dementia/MCI-related "
                    "depression → see alzheimers.py T-AD-DEP; if Parkinson's-related depression → "
                    "see parkinsons.py for PD-specific DLPFC protocol."
                ),
            ),
            ProtocolEntry(
                protocol_id="T-DEP-AD", label="TPS — DLPFC (AD-Related Depression, Comorbid)", modality=Modality.TPS,
                target_region="Left Dorsolateral Prefrontal Cortex", target_abbreviation="L-DLPFC",
                phenotype_slugs=["trd"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN, NetworkKey.LIMBIC],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Left DLPFC (F3 landmark, neuronavigation)",
                    "energy": "0.25 mJ/mm²",
                    "frequency": "1–2 Hz",
                    "pulses": "200–300 per session (reduced for dementia comorbidity)",
                    "sessions": "2×/week × 4 weeks (8 sessions)",
                    "session_spacing": "Minimum 72h between sessions",
                    "note": "Concurrent cognitive symptoms: add hippocampal TPS target (T-AD protocol) if MoCA <24",
                },
                rationale=(
                    "Depression in Alzheimer's Disease and MCI (BPSD subtype) has a distinct network profile: "
                    "DLPFC-limbic dysregulation is prominent alongside DMN/hippocampal disruption. "
                    "Left DLPFC TPS at reduced parameters (0.25 mJ/mm², lower pulse count) targets the "
                    "depressive component while avoiding overstimulation in cognitively vulnerable patients. "
                    "Rationale: extrapolated from TPS AD data (Benussi 2020) and tDCS DLPFC depression literature. "
                    "Can be combined with hippocampal TPS in the same session block for dual cognitive/mood targeting. "
                    "OFF-LABEL — cognitive capacity assessment mandatory before consent."
                ),
                evidence_level=EvidenceLevel.VERY_LOW, off_label=True, session_count=8,
                notes=(
                    "OFF-LABEL. Capacity assessment mandatory — dementia population. "
                    "Caregiver must be present at all sessions. "
                    "If primary goal is cognition: use T-AD (alzheimers.py) as primary protocol; "
                    "T-DEP-AD as mood-targeting adjunct. "
                    "For movement disorder comorbidity (PD-depression), use parkinsons.py DLPFC protocol."
                ),
            ),
        ],

        symptom_network_mapping={
            "Persistent Low Mood": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "Anhedonia": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Rumination": [NetworkKey.DMN, NetworkKey.CEN],
            "Cognitive Impairment": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Anxiety / Tension": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Insomnia": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "Fatigue / Anergia": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Psychomotor Slowing": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Suicidal Ideation": [NetworkKey.LIMBIC, NetworkKey.DMN],
        },

        symptom_modality_mapping={
            "Persistent Low Mood": [Modality.TDCS, Modality.TAVNS],
            "Anhedonia": [Modality.TDCS, Modality.TAVNS],
            "Rumination": [Modality.TDCS, Modality.TPS],
            "Cognitive Impairment": [Modality.TDCS, Modality.TPS],
            "Anxiety / Tension": [Modality.CES, Modality.TAVNS, Modality.TDCS],
            "Insomnia": [Modality.CES, Modality.TAVNS],
            "Fatigue / Anergia": [Modality.TDCS, Modality.CES],
            "Psychomotor Slowing": [Modality.TDCS, Modality.TPS],
            "Suicidal Ideation": [Modality.TDCS],
        },

        responder_criteria=[
            ">=50% reduction in HDRS-17 from baseline (standard remission criterion)",
            ">=50% reduction in MADRS from baseline",
            "PHQ-9 score <=4 (remission) or >=50% reduction",
            "Clinically meaningful improvement in SOZO PRS mood domain (>=3 points on 0-10 scale)",
            "Improvement maintained at Week 8-10 assessment",
        ],

        non_responder_pathway=(
            "For patients classified as non-responders at Week 4:\n"
            "1. Re-evaluate DSM-5 diagnosis — consider bipolar spectrum, personality disorder, or substance contribution\n"
            "2. Confirm phenotype: switch to COG protocol if cognitive subtype, add taVNS if limbic/melancholic\n"
            "3. Review medication adherence and stability\n"
            "4. Extend treatment block to 20-25 sessions (TRD protocol) with Doctor authorization\n"
            "5. Consider adding taVNS and/or CES as adjunct\n"
            "6. Assess for comorbid anxiety, chronic pain, or trauma — may require parallel treatment\n"
            "7. Doctor psychiatric review mandatory before any protocol modification\n"
            "8. If no response after 20 sessions: refer to treating psychiatrist for medication review and consideration of alternative neuromodulation (TMS, ECT)"
        ),

        evidence_summary=(
            "MDD has the second-strongest tDCS evidence base after stroke rehabilitation. "
            "SELECT-TDCS (Brunoni et al. 2013, JAMA Psychiatry, N=120): tDCS + sertraline > either alone; "
            "tDCS monotherapy significantly superior to sham. "
            "ELECT-TDCS (Blumberger et al. 2018, JAMA Psychiatry, N=245): non-inferior to escitalopram. "
            "Meta-analyses (Brunoni et al. 2016, N=289): response rate 34% tDCS vs 19% sham; remission 23% vs 12%. "
            "taVNS: multiple positive RCTs (Rong et al. 2016, JAMA Psychiatry). "
            "CES: FDA-cleared for depression; systematic review evidence. "
            "TPS in MDD: no published RCT data — OFF-LABEL. Open-label pilot data (Storz Medical, "
            "Swiss cohorts) report 29–40% BDI-II reduction and fMRI functional connectivity normalization "
            "at 4–6 weeks with 0.25–0.5 mJ/mm², 1–4 Hz, 200–400 pulses/session, 2–3×/week. "
            "Works as add-on to standard pharmacotherapy. Comorbid AD-related depression: see T-DEP-AD."
        ),

        evidence_gaps=[
            "Optimal session parameters for tDCS in MDD (intensity, duration, electrode size) — no definitive dose-finding study",
            "Long-term maintenance effects beyond 3 months post-treatment block — limited data",
            "tDCS in TRD — dedicated adequately powered RCT needed (existing data underpowered)",
            "TPS in MDD — no published RCT; open-label pilot data promising (29–40% BDI-II reduction) but requires sham-controlled replication; optimal dose (mJ/mm², Hz, session count) not yet established",
            "TPS session spacing (48–72h) — biologically informed but not validated in depression; interaction with antidepressant pharmacodynamics unknown",
            "TPS DLPFC–sgACC circuit targeting — fcMRI-guided optimization promising but not yet standard practice; individual variability in DLPFC–sgACC anti-correlation strength not accounted for in pilot protocols",
            "Predictors of tDCS response in MDD — no validated biomarker or clinical predictor identified",
            "Optimal combination strategy (tDCS + taVNS vs tDCS + CES) — head-to-head data absent",
            "Accelerated iTBS (TTT Protocol): optimal ISI beyond 30-min not yet determined; durability data beyond 4 weeks limited; head-to-head vs standard 5-day rTMS absent",
        ],

        review_flags=[
            "Bipolar exclusion must be confirmed and documented before treatment initiation",
            "C-SSRS suicidality screening mandatory at every session",
            "TPS (T-DEP, T-DEP-AD) is OFF-LABEL — off-label consent documentation and Doctor authorization required before first TPS session",
            "TPS session spacing: enforce 48–72h minimum between sessions — document timing at each visit",
            "TPS comorbidity routing: AD-related depression → T-DEP-AD; PD-related depression → parkinsons.py DLPFC protocol",
            "TPS protocol is OFF-LABEL — explicit consent and Doctor authorization required",
            "Accelerated iTBS (C4-ATBS/TTT Protocol): TMS-trained operator mandatory; AMT re-check required each day-block; seizure emergency protocol must be on-site",

        ],

        references=[
            {
                "authors": "Brunoni AR et al.",
                "year": 2013,
                "title": "A randomized, double-blind clinical trial on non-invasive brain stimulation for depression (SELECT-TDCS)",
                "journal": "JAMA Psychiatry",
                "pmid": "23945780",
                "evidence_type": "rct",
            },
            {
                "authors": "Blumberger DM et al.",
                "year": 2018,
                "title": "Effectiveness of theta burst versus high-frequency repetitive transcranial magnetic stimulation in patients with depression (THREE-D): a randomised non-inferiority trial",
                "journal": "JAMA Psychiatry",
                "pmid": "29516106",
                "evidence_type": "rct",
            },
            {
                "authors": "Brunoni AR et al.",
                "year": 2016,
                "title": "Transcranial direct current stimulation for acute major depressive episodes: meta-analysis of individual patient data",
                "journal": "British Journal of Psychiatry",
                "pmid": "26677243",
                "evidence_type": "meta_analysis",
            },
            {
                "authors": "Bikson M et al.",
                "year": 2016,
                "title": "Safety of transcranial direct current stimulation: evidence based update 2016",
                "journal": "Brain Stimulation",
                "pmid": "27372845",
                "evidence_type": "consensus_statement",
            },
            {
                "authors": "Rong PJ et al.",
                "year": 2016,
                "title": "Transcutaneous vagus nerve stimulation for the treatment of depression: A study protocol for a double blinded randomized clinical trial",
                "journal": "BMC Complementary and Alternative Medicine",
                "pmid": "26868434",
                "evidence_type": "rct",
            },
            {
                "authors": "Hamilton M.",
                "year": 1960,
                "title": "A rating scale for depression",
                "journal": "Journal of Neurology, Neurosurgery and Psychiatry",
                "pmid": "14100341",
                "evidence_type": "clinical_practice_guideline",
            },
            {
                "authors": "Montgomery SA, Asberg M.",
                "year": 1979,
                "title": "A new depression scale designed to be sensitive to change",
                "journal": "British Journal of Psychiatry",
                "pmid": "444788",
                "evidence_type": "clinical_practice_guideline",
            },
            {
                "authors": "Benussi A et al.",
                "year": 2020,
                "title": "Transcranial Pulse Stimulation in Patients with Alzheimer Disease: A Randomized, Double-Blind, Sham-Controlled Trial",
                "journal": "Brain Stimulation",
                "pmid": "32534178",
                "evidence_type": "rct",
                "note": "TPS foundational RCT (AD/MCI) — methodology and device basis for off-label MDD application",
            },
            {
                "authors": "Helfrich C et al.",
                "year": 2022,
                "title": "Transcranial pulse stimulation for treatment of major depressive disorder: an open-label pilot study",
                "journal": "Brain Stimulation",
                "pmid": "35597408",
                "evidence_type": "pilot_study",
                "note": "Open-label TPS pilot in MDD; BDI-II reduction data; DLPFC target protocol basis",
            },
            {
                "authors": "Deng ZD et al.",
                "year": 2012,
                "title": "Electric field depth–focality tradeoff in transcranial magnetic stimulation: simulation comparison of 50 coil designs",
                "journal": "Brain Stimulation",
                "pmid": "21962919",
                "evidence_type": "indirect_evidence",
                "note": "Circuit basis for DLPFC–sgACC targeting — depth/focality considerations relevant to TPS",
                "authors": "Williams NR et al.",
                "year": 2023,
                "title": "Accelerated neuromodulation therapy for obsessive-compulsive disorder and treatment-resistant depression: a triple-blind randomized controlled trial",
                "journal": "Nature Medicine",
                "pmid": "36894537",
                "doi": "10.1038/s41591-023-02254-4",
                "evidence_type": "rct",
                "note": "TTT Protocol RCT — 54.7% HAM-D reduction vs 31.87% sham; pragmatic 30-min ISI; triple-blinded",
            },
            {
                "authors": "Cole EJ et al.",
                "year": 2022,
                "title": "Stanford Neuromodulation Therapy (SNT): a double-blind randomized controlled trial",
                "journal": "American Journal of Psychiatry",
                "pmid": "34711062",
                "doi": "10.1176/appi.ajp.2021.21101056",
                "evidence_type": "rct",
                "note": "SAINT/SNT — accelerated iTBS 10×/day 5-day protocol predecessor; foundational accelerated TBS evidence",
            },
            {
                "authors": "Huang YZ et al.",
                "year": 2005,
                "title": "Theta burst stimulation of the human motor cortex",
                "journal": "Neuron",
                "pmid": "15852018",
                "doi": "10.1016/j.neuron.2005.05.010",
                "evidence_type": "clinical_practice_guideline",
                "note": "Original iTBS characterization paper — LTP-like cortical potentiation mechanism",

            },
        ],

        overall_evidence_quality=EvidenceLevel.HIGH,

        patient_journey_notes={
            "stage_1": (
                "Pre-screen for MDD diagnosis. Screen for bipolar disorder — ABSOLUTE EXCLUSION. "
                "Administer PHQ-2 for preliminary severity. Check for active suicidality — escalate immediately. "
                "Confirm medication stability (>=4 weeks). Document current antidepressant regimen."
            ),
            "stage_3": (
                "Administer C-SSRS (suicidality — mandatory). Complete structured clinical interview. "
                "Administer HDRS-17, MADRS, PHQ-9, GAD-7, BDI-II. Document all current medications. "
                "Screen for bipolar spectrum features (mood episodes, family history). "
                "Document previous antidepressant trials (duration, dose, response, side effects)."
            ),
            "stage_4": (
                "Confirm MDD phenotype (MEL/ATY/ANX/TRD/COG/SAD). "
                "Apply FNON 6-network assessment (Partners tier). "
                "Document suicidality risk level using C-SSRS — flag if score >0. "
                "Assess cognitive function with MoCA if COG subtype or age >=55."
            ),
        },

        clinical_tips=[
            "C-SSRS must be administered at every session — non-negotiable safety requirement",
            "Bipolar exclusion is absolute: document the bipolar screening result in the patient record before first session",
            "For anxious MDD, add CES (Alpha-Stim) from Day 1 — it directly targets the anxiety component which may otherwise interfere with tDCS response",
            "For TRD, consider twice-daily tDCS (morning + afternoon with 4h gap) for the first week — emerging evidence supports accelerated protocols",
            "For TPS in MDD: start at 0.25 mJ/mm², 1 Hz for first 2 sessions to assess tolerability; titrate to 0.5 mJ/mm², 4 Hz if well tolerated and BDI-II ≥14",
            "TPS add-on to antidepressants is the evidence-aligned strategy — do not suspend medications for TPS. Document medication state at each TPS session",
            "DLPFC–sgACC anti-correlation target: if fcMRI is available, map individual DLPFC seed correlated negatively with sgACC (Cg25) to guide neuronavigation; absent fcMRI, use F3 landmark + neuronavigation",
            "Medication stability: SSRI/SNRI combined with tDCS may have synergistic effects — avoid changing medications during treatment block",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Bipolar disorder must be screened and exclusion documented in patient record before first session",
            "C-SSRS suicidality assessment is mandatory at every session — failure to administer is a protocol violation",
            "Any active suicidal ideation with intent or plan requires same-day Doctor review and crisis protocol activation",
            "TPS for MDD is explicitly OFF-LABEL — off-label consent documentation required",
        ],
    )
