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
            "Confirmed MDD diagnosis (DSM-5/ICD-11 criteria) by qualified clinician",
            "Treatment resistance: failure of ≥2 adequate antidepressant trials (adequate dose, ≥6 weeks each, documented compliance)",
            "PHQ-9 ≥10 (moderate depression) or MADRS ≥20 at baseline",
            "Age 18–75 years",
            "Capacity to provide informed consent",
            "Stable medication regimen (≥4 weeks, no dose change planned during treatment)",
        ],

        exclusion_criteria=[
            "Intracranial metallic hardware in stimulation path",
            "Cochlear implant",
            "Skull defects, craniectomy, or recent craniotomy",
            "Active psychosis or psychotic features",
            "Pregnancy or breastfeeding",
            "Substance use disorder (moderate–severe, active, within 3 months)",
            "Active suicidal intent with plan (refer to crisis pathway)",
            "Inability to tolerate device placement",
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

        eeg_reference_table=[
            {"position": "Fp1", "brain_region": "Left Prefrontal Pole", "role": "Medial prefrontal — vmPFC proxy for anhedonia/reward", "protocols_using": ["C6"]},
            {"position": "Fp2", "brain_region": "Right Prefrontal Pole", "role": "Right supraorbital reference electrode", "protocols_using": ["C4-STD", "C4-TRD"]},
            {"position": "F3", "brain_region": "Left DLPFC", "role": "PRIMARY tDCS anodal target — CEN upregulation; most-evidenced depression target", "protocols_using": ["C4-STD", "C4-TRD", "C5", "C7", "C8", "T-DEP", "T3"]},
            {"position": "F4", "brain_region": "Right DLPFC", "role": "Cathodal target in bilateral montage — dampens right-lateralised anxiety/negative affect", "protocols_using": ["C4-STD", "C4-TRD", "C5", "C8"]},
            {"position": "F7", "brain_region": "Left Inferior Frontal / Broca's area", "role": "Language/verbal fluency — relevant for psychomotor-retarded phenotype", "protocols_using": []},
            {"position": "F8", "brain_region": "Right Inferior Frontal", "role": "Emotional prosody / social cognition", "protocols_using": []},
            {"position": "Fz", "brain_region": "Midline Frontal / ACC", "role": "Anterior cingulate access — error monitoring, conflict, mood regulation; TPS target", "protocols_using": ["T-DEP", "T4"]},
            {"position": "FCz", "brain_region": "Supplementary Motor Area (SMA)", "role": "Executive-motor coupling — psychomotor retardation phenotype", "protocols_using": []},
            {"position": "C3", "brain_region": "Left Primary Motor Cortex (M1)", "role": "Motor cortex — psychomotor retardation; pain-dominant phenotype", "protocols_using": []},
            {"position": "C4", "brain_region": "Right Primary Motor Cortex (M1)", "role": "Contralateral motor — pain pathway modulation", "protocols_using": []},
            {"position": "Cz", "brain_region": "Midline Central / Vertex", "role": "Supplementary motor area; midline reference", "protocols_using": []},
            {"position": "T3", "brain_region": "Left Temporal / Amygdala region", "role": "Amygdala access for TPS — emotional regulation, threat detection", "protocols_using": ["T-DEP"]},
            {"position": "T4", "brain_region": "Right Temporal / Amygdala region", "role": "Bilateral amygdala targeting for TPS", "protocols_using": ["T-DEP"]},
            {"position": "T5", "brain_region": "Left Posterior Temporal / Hippocampus entry", "role": "Hippocampal TPS target — memory consolidation, neuroplasticity", "protocols_using": ["T5"]},
            {"position": "T6", "brain_region": "Right Posterior Temporal / Hippocampus entry", "role": "Bilateral hippocampal TPS targeting", "protocols_using": ["T5"]},
            {"position": "P3", "brain_region": "Left Posterior Parietal Cortex (PPC)", "role": "Visuospatial processing; cognitive TRD phenotype target", "protocols_using": []},
            {"position": "P4", "brain_region": "Right Posterior Parietal Cortex (PPC)", "role": "Bilateral PPC for cognitive enhancement", "protocols_using": []},
            {"position": "Pz", "brain_region": "Midline Parietal / PCC/Precuneus", "role": "Posterior DMN hub — cathodal target for rumination reduction", "protocols_using": ["C7"]},
            {"position": "O1", "brain_region": "Left Occipital", "role": "Visual cortex — not primary target in MDD protocols", "protocols_using": []},
            {"position": "O2", "brain_region": "Right Occipital", "role": "Visual cortex — not primary target in MDD protocols", "protocols_using": []},
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Left Dorsolateral Prefrontal Cortex", "L-DLPFC", "left",
                "Left DLPFC is the primary tDCS target for MDD, supported by the DLPFC lateralization model. "
                "Anodal stimulation increases left DLPFC excitability, restoring CEN-DMN balance and improving "
                "emotion regulation. Multiple RCTs (Brunoni 2013, Blumberger 2018) confirm antidepressant efficacy.",
                "C4 — Depression & Mood",
                EvidenceLevel.HIGH, off_label=True,
                eeg_canonical=["F3"],
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
                eeg_canonical=["F3", "Pz"],
            ),
            make_tdcs_target(
                "Anterior Cingulate Cortex", "ACC", "bilateral",
                "ACC targeting addresses DMN hyperactivation and ruminative processing. "
                "Cathodal ACC placement can reduce sgACC hyperactivity. Emerging evidence only.",
                "ACC — Rumination Protocol",
                EvidenceLevel.LOW, off_label=True,
                eeg_canonical=["Fz", "AFz", "Cz"],
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
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="C4-STD — tDCS Standard DLPFC Protocol for MDD",
                clinical_objective="Restore left DLPFC excitability and enhance top-down control of DMN rumination",
                primary_targets=["F3 (Left DLPFC — anodal)"],
                secondary_targets=["F4 (Right DLPFC — cathodal) or Fp2 (right supraorbital)"],
                device_name="Newronika HDCkit (2-channel)",
                session_structure="Ch1: Anodal F3 (L-DLPFC); Cathode: F4 or Fp2. 2 mA per channel, 30 min.",
                frequency="1–2 sessions/day, 5 days/week",
                duration="30 min per session",
                intensity_dose="2 mA per channel",
                montage_roi="Anode (+): F3 (L-DLPFC). Cathode (−): F4 or Fp2",
                laterality="Left anodal dominant",
                treatment_course="10–30 sessions over 2–6 weeks",
                monitoring="Impedance; PHQ-9/MADRS weekly; skin integrity",
                expected_response="Improved mood and motivation; reduced anhedonia; enhanced cognitive control",
                evidence_status="Level A for depression (Fregni et al., 2021); tDCS + SSRI most effective (g = −0.855; Wang et al., 2021)",
                cautions="tDCS + SSRI combination recommended; avoid benzodiazepines if possible",
                when_to_escalate="If non-response after 10 sessions, add TPS or multimodal combination",
                when_to_stop_modify="Standard tDCS stop criteria",
                clinical_notes_extended="Pair with behavioural activation or psychotherapy. tDCS + psychotherapy shows 50% response / 75% remission (Sack et al., 2023)",
                key_citations=["Fregni et al., 2021", "Wang et al., 2021", "Sack et al., 2023", "Brunoni et al., 2013"],
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
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="C4-TRD — tDCS Intensive Protocol for Treatment-Resistant Depression",
                clinical_objective="Extended neuromodulation block for treatment-resistant cases requiring higher session count",
                primary_targets=["F3 (Left DLPFC — anodal)"],
                secondary_targets=["F4 (Right DLPFC — cathodal)"],
                device_name="Newronika HDCkit (2-channel)",
                session_structure="Ch1: Anodal F3; Ch2: Cathodal F4. 2 mA per channel, 30 min. Consider twice-daily with 4h gap.",
                frequency="1–2 sessions/day, 5 days/week",
                duration="30 min per session",
                intensity_dose="2 mA per channel",
                montage_roi="Anode (+): F3 (L-DLPFC). Cathode (−): F4 (R-DLPFC)",
                laterality="Left anodal / Right cathodal (bilateral asymmetric)",
                treatment_course="20–25 sessions over 4–6 weeks; reassess at session 10 and 20",
                monitoring="Impedance check (<15 kΩ); PHQ-9 + MADRS weekly; skin integrity; medication timing",
                expected_response="Reduced depression scores; improved executive function; reduced rumination",
                evidence_status="Level A for depression; extended blocks show cumulative benefit for TRD (Fregni et al., 2021)",
                cautions="Concurrent benzodiazepines may reduce efficacy. Frame as adjunctive to pharmacotherapy.",
                when_to_escalate="If <20% PHQ-9 improvement after 10 sessions, consider adding TPS or switching to iTBS",
                when_to_stop_modify="Stop if burning, skin lesion. Modify: adjust to unilateral if bilateral causes discomfort.",
                clinical_notes_extended="TRD requires 20+ sessions. Combination with SSRI shows strongest combined efficacy. Consider accelerated iTBS if non-response.",
                key_citations=["Fregni et al., 2021", "Wang et al., 2021", "McIntyre et al., 2023"],
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
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="C4-ATBS — Accelerated iTBS (TTT Protocol) for TRD",
                clinical_objective="Rapid-onset antidepressant neuromodulation via compressed iTBS schedule targeting left DLPFC",
                primary_targets=["F3 (Left DLPFC)"],
                secondary_targets=["sgACC (indirect via DLPFC-sgACC anti-correlation)"],
                device_name="MagVenture MagPro or MagStim Rapid2",
                session_structure="3 sessions/day, 30-min ISI; 600 pulses/session (2s on / 8s off x 20 trains); 80% AMT",
                frequency="3 sessions/day, 5–10 days",
                duration="3 min per session (600 pulses iTBS pattern)",
                intensity_dose="80% active motor threshold (AMT)",
                montage_roi="Left DLPFC — F3 (5.5 cm rule or Beam F3 neuronavigation)",
                laterality="Left unilateral",
                treatment_course="15–30 sessions over 5–10 days; reassess at day 5",
                monitoring="AMT re-check each day-block; C-SSRS every session; seizure checklist; HAM-D weekly",
                expected_response="54.7% HAM-D reduction (vs 31.87% sham); rapid onset within 5 days",
                evidence_status="Level A — triple-blind RCT (Williams et al., 2023; PMID 36894537); SAINT/SNT predecessor (Cole et al., 2022)",
                cautions="Seizure risk (low but non-zero); AMT re-calibration mandatory; TMS-trained operator required; resuscitation equipment on-site",
                when_to_escalate="If <30% HAM-D improvement after full 5-day block, consider extending to 10 days or switching to tDCS + TPS combination",
                when_to_stop_modify="Stop immediately if seizure, severe headache, or new neurological symptoms. Reduce intensity if significant scalp pain.",
                clinical_notes_extended="Accelerated iTBS is the fastest-acting non-pharmacological antidepressant intervention. Ideal for acute TRD requiring rapid response. Requires dedicated TMS suite and trained operator.",
                key_citations=["Williams et al., 2023", "Cole et al., 2022", "Huang et al., 2005", "Blumberger et al., 2018"],
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
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="taVNS-DEP — taVNS Adjunct for Depression",
                clinical_objective="Engage anti-inflammatory pathway; support mood regulation via NTS-LC noradrenergic pathway",
                primary_targets=["Auricular branch of vagus nerve → NTS → LC noradrenergic pathway"],
                secondary_targets=["Limbic network (indirect via NTS-LC-cortical projections)"],
                device_name="NEMOS (tVNS Technologies) or Parasym",
                session_structure="Electrode placement on left cymba conchae; 25 Hz, 200–250 µs pulse width; 30 min",
                frequency="Daily adjunct during tDCS block",
                duration="30 min per session",
                intensity_dose="Below pain threshold (0.5–5.0 mA); 25 Hz; 200–250 µs pulse width",
                montage_roi="Left cymba conchae (auricular vagus branch)",
                laterality="Left auricular",
                treatment_course="15 sessions over 3 weeks (concurrent with tDCS block)",
                monitoring="Heart rate; skin integrity; tolerability",
                expected_response="Modest antidepressant augmentation; reduced inflammatory markers; improved vagal tone",
                evidence_status="Emerging — multiple RCTs show modest antidepressant effect as adjunct",
                cautions="Not primary antidepressant. Adjust intensity for comfort. Monitor HR.",
                when_to_escalate="If no subjective benefit after 10 sessions, consider switching to CES or adding TPS",
                when_to_stop_modify="Stop if skin irritation at electrode site, bradycardia, or significant discomfort",
                clinical_notes_extended="Best used as adjunct to tDCS or pharmacotherapy. Anti-inflammatory mechanism may benefit patients with elevated CRP/IL-6.",
                key_citations=["Song et al., 2025", "Shan et al., 2025", "Rong et al., 2016"],
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
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="CES-DEP — Alpha-Stim CES for Depression/Anxiety/Insomnia",
                clinical_objective="Support sleep and reduce anxiety that maintain depressive treatment resistance",
                primary_targets=["Limbic and autonomic networks via transcranial microcurrent"],
                secondary_targets=["SN downregulation (indirect)"],
                device_name="Alpha-Stim® CS",
                session_structure="Bilateral earlobe clip electrodes; 0.5 Hz; 100–300 µA; 40–60 min",
                frequency="Daily during treatment block",
                duration="40–60 min per session",
                intensity_dose="100–300 µA; 0.5 Hz",
                montage_roi="Bilateral earlobe electrodes",
                laterality="Bilateral",
                treatment_course="20 sessions over 4 weeks (concurrent with tDCS block)",
                monitoring="Self-reported sleep quality; anxiety VAS; tolerability",
                expected_response="Improved sleep onset and quality; reduced anxiety symptoms; modest mood improvement",
                evidence_status="Limited — Morriss et al. (2023; n=236) showed no superiority for primary MDD. Real-world benefit for comorbid anxiety-depression and insomnia.",
                cautions="Not primary antidepressant device. Adjunctive only for sleep/anxiety support.",
                when_to_escalate="If sleep/anxiety not improving after 10 sessions, consider pharmacological adjunct",
                when_to_stop_modify="Stop if skin irritation at earlobe sites or dizziness",
                clinical_notes_extended="Best suited for anxious-depressive or insomnia-predominant phenotypes. FDA-cleared — no off-label consent needed.",
                key_citations=["Morriss et al., 2023", "Maravic da Silva et al., 2025", "Kirsch, 2002"],
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
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="T-DEP — TPS Protocol for MDD/TRD (DLPFC-sgACC Network)",
                clinical_objective="Modulate DLPFC-sgACC anti-correlation circuit; restore CEN-DMN balance via focused acoustic pulse energy",
                primary_targets=["F3 (Left DLPFC)", "Fz (ACC)"],
                secondary_targets=["T3/T4 (amygdala region)", "T5/T6 (hippocampus)"],
                device_name="NEUROLITH® TPS System (Storz Medical)",
                session_structure="Neuronavigation setup → Holocranial priming (2,000 pulses) → Targeted DLPFC/ACC (4,000 pulses) → Secondary amygdala/hippocampus (2,000 pulses). Total 8,000–10,000 pulses.",
                frequency="2–3 sessions/week",
                duration="30–45 min per session",
                intensity_dose="0.25–0.5 mJ/mm²; 1–4 Hz",
                montage_roi="F3 (DLPFC), Fz (ACC). Secondary: T3/T4 (amygdala), T5/T6 (hippocampus). Total 8,000–10,000 pulses",
                laterality="Left-dominant for DLPFC; bilateral for amygdala and hippocampal regions",
                treatment_course="10–12 sessions / 2–4 weeks; then maintenance 1–2/week",
                monitoring="PHQ-9 weekly; anhedonia scale; tolerability log",
                expected_response="29–40% BDI-II reduction; fMRI functional connectivity normalization; improved mood and cognitive control",
                evidence_status="Emerging — Qin et al. (2025) demonstrated DLPFC-mPFC connectivity enhancement with TPS",
                cautions="TPS is investigational/off-label. Neuronavigation recommended for deep targets.",
                when_to_escalate="If <20% BDI-II improvement after 6 sessions, increase energy to 0.5 mJ/mm² or add tDCS combination",
                when_to_stop_modify="Stop if persistent headache, scalp lesion, or neurological symptoms. Modify: reduce energy if discomfort.",
                clinical_notes_extended="TPS add-on to antidepressants is the evidence-aligned strategy. DLPFC-sgACC anti-correlation mapping from fcMRI can guide individual target optimization.",
                key_citations=["Cheung et al., 2023", "Qin et al., 2025", "Günes et al., 2025"],
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
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="T-DEP-AD — TPS for AD-Related Depression (Comorbid)",
                clinical_objective="Target depressive component in AD/MCI via reduced-parameter DLPFC TPS",
                primary_targets=["F3 (Left DLPFC)"],
                secondary_targets=["Hippocampal formation (if MoCA <24 — combine with T-AD)"],
                device_name="NEUROLITH® TPS System (Storz Medical)",
                session_structure="Neuronavigation setup → DLPFC targeted (200–300 pulses) → Optional hippocampal add-on",
                frequency="2 sessions/week",
                duration="20–30 min per session",
                intensity_dose="0.25 mJ/mm²; 1–2 Hz",
                montage_roi="F3 (DLPFC). Optional: T5/T6 (hippocampal) if dual cognitive/mood targeting",
                laterality="Left DLPFC dominant",
                treatment_course="8 sessions over 4 weeks (2x/week); minimum 72h spacing",
                monitoring="PHQ-9 weekly; MoCA at baseline and endpoint; caregiver report; tolerability log",
                expected_response="Modest mood improvement; reduced apathy; potential cognitive stabilization if combined with hippocampal targeting",
                evidence_status="Very low — extrapolated from TPS AD data (Benussi 2020) and tDCS DLPFC depression literature",
                cautions="Capacity assessment mandatory. Caregiver presence required. Reduced pulse count for cognitively vulnerable patients.",
                when_to_escalate="If no mood improvement after 8 sessions, refer to psychiatrist for medication review",
                when_to_stop_modify="Stop if confusion, agitation, or caregiver reports worsening. Reduce pulses if discomfort.",
                clinical_notes_extended="Depression in AD has distinct network profile. Dual DLPFC + hippocampal targeting addresses both mood and cognitive components. OFF-LABEL — cognitive capacity assessment mandatory before consent.",
                key_citations=["Benussi et al., 2020", "Helfrich et al., 2022"],
            ),

            # ── C5-C8: Expanded tDCS protocols ──────────────────────
            ProtocolEntry(
                protocol_id="C5", label="Anxiety/Worry — Right DLPFC Cathodal", modality=Modality.TDCS,
                target_region="Right Dorsolateral Prefrontal Cortex (cathodal) / Left Temporal (anodal)",
                target_abbreviation="R-DLPFC/L-T",
                phenotype_slugs=["anx", "mel", "aty"],
                network_targets=[NetworkKey.SN, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "T3 (left temporal)",
                    "cathode": "F4 (right DLPFC)",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                },
                rationale="Right DLPFC cathodal tDCS reduces anxiogenic right-hemispheric dominance in MDD with comorbid anxiety. Bilateral temporal placement engages SN downregulation. Addresses the 60-70% GAD-MDD comorbidity subgroup. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="C5 — tDCS Anxiety/Worry Protocol (Right DLPFC Cathodal)",
                clinical_objective="Reduce anxiogenic right-hemispheric dominance and SN hyperactivation in anxious MDD",
                primary_targets=["F4 (Right DLPFC — cathodal)"],
                secondary_targets=["T3 (Left temporal — anodal)", "F3 (Left DLPFC — indirect benefit)"],
                device_name="Newronika HDCkit (2-channel)",
                session_structure="Ch1: Cathode F4 (R-DLPFC); Anode T3 (L-temporal). 2 mA, 20 min.",
                frequency="5 days/week",
                duration="20 min per session",
                intensity_dose="2 mA",
                montage_roi="Cathode (−): F4 (R-DLPFC). Anode (+): T3 (L-temporal)",
                laterality="Right cathodal dominant",
                treatment_course="10–15 sessions over 2–3 weeks",
                monitoring="GAD-7 weekly; PHQ-9 weekly; skin integrity; anxiety VAS",
                expected_response="Reduced anxiety and worry; improved emotional regulation; decreased psychomotor agitation",
                evidence_status="Low — based on lateralization model of anxiety; limited direct RCT evidence for this specific montage",
                cautions="OFF-LABEL montage. May not address core depressive symptoms — combine with C4-STD if needed.",
                when_to_escalate="If anxiety persists after 10 sessions, add CES (Alpha-Stim) or taVNS adjunct",
                when_to_stop_modify="Standard tDCS stop criteria. Switch to C4-STD if depression worsens without anxiety improvement.",
                clinical_notes_extended="Best suited for anxious MDD phenotype (ANX). Consider combining with CES from Day 1 for comprehensive anxiety-depression targeting.",
                key_citations=["Fregni et al., 2021", "Brunoni et al., 2016"],
            ),
            ProtocolEntry(
                protocol_id="C6", label="Anhedonia/Reward — vmPFC / NAcc Proxy", modality=Modality.TDCS,
                target_region="Ventromedial Prefrontal Cortex (Fp1/Fp2)", target_abbreviation="vmPFC",
                phenotype_slugs=["mel", "aty", "trd"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.DMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "Fp1 (left medial prefrontal — vmPFC proxy)",
                    "cathode": "Right mastoid or shoulder reference",
                    "intensity": "1.5 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                },
                rationale="vmPFC anodal tDCS targets the medial reward circuit (vmPFC-NAcc axis) implicated in anhedonia. Surface stimulation provides partial modulation of deep reward structures via cortical-subcortical connectivity. OFF-LABEL — experimental montage.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="C6 — tDCS Anhedonia/Reward Protocol (vmPFC Proxy)",
                clinical_objective="Upregulate medial reward circuit (vmPFC-NAcc axis) to address anhedonia and reward processing deficits",
                primary_targets=["Fp1 (Left medial prefrontal — vmPFC proxy, anodal)"],
                secondary_targets=["Right mastoid or shoulder reference (cathodal)"],
                device_name="Newronika HDCkit (2-channel)",
                session_structure="Ch1: Anode Fp1 (vmPFC proxy); Cathode: right mastoid or shoulder reference. 1.5 mA, 20 min.",
                frequency="5 days/week",
                duration="20 min per session",
                intensity_dose="1.5 mA",
                montage_roi="Anode (+): Fp1 (vmPFC proxy). Cathode (−): Right mastoid or shoulder",
                laterality="Left medial prefrontal dominant",
                treatment_course="10–15 sessions over 2–3 weeks",
                monitoring="Anhedonia scale (SHAPS); PHQ-9 weekly; reward motivation diary; skin integrity",
                expected_response="Improved reward sensitivity; reduced anhedonia; enhanced motivation",
                evidence_status="Low — experimental montage based on vmPFC-NAcc connectivity model; no dedicated RCT for this montage",
                cautions="OFF-LABEL experimental montage. Reduced intensity (1.5 mA) for prefrontal pole proximity to orbits. Not first-line — use after C4-STD trial.",
                when_to_escalate="If anhedonia persists after 10 sessions, combine with taVNS or switch to C4-STD + behavioral activation",
                when_to_stop_modify="Standard tDCS stop criteria. Discontinue if orbital/eye discomfort due to Fp1 proximity.",
                clinical_notes_extended="Targets the core anhedonia circuit. Best for melancholic or atypical phenotypes with prominent anhedonia. Pair with behavioral activation therapy targeting reward engagement.",
                key_citations=["Fregni et al., 2021", "Brunoni et al., 2016"],
            ),
            ProtocolEntry(
                protocol_id="C7", label="Rumination/DMN — Posterior Cingulate / Precuneus", modality=Modality.TDCS,
                target_region="Posterior Cingulate Cortex / Precuneus", target_abbreviation="PCC/Prec",
                phenotype_slugs=["mel", "trd", "cog"],
                network_targets=[NetworkKey.DMN, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "Pz (posterior midline — PCC/precuneus proxy)",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                },
                rationale="Cathodal inhibition of PCC/precuneus (posterior DMN hub) combined with anodal left DLPFC targets the DMN hyperactivation-CEN hypoactivation signature of rumination in MDD. Aims to restore CEN-DMN anticorrelation. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="C7 — tDCS Rumination/DMN Protocol (PCC/Precuneus Cathodal)",
                clinical_objective="Suppress posterior DMN hub (PCC/precuneus) while upregulating left DLPFC to restore CEN-DMN anticorrelation",
                primary_targets=["F3 (Left DLPFC — anodal)"],
                secondary_targets=["Pz (PCC/Precuneus — cathodal)"],
                device_name="Newronika HDCkit (2-channel)",
                session_structure="Ch1: Anode F3 (L-DLPFC); Cathode Pz (PCC/Precuneus). 2 mA, 20 min.",
                frequency="5 days/week",
                duration="20 min per session",
                intensity_dose="2 mA",
                montage_roi="Anode (+): F3 (L-DLPFC). Cathode (−): Pz (PCC/Precuneus — posterior DMN hub)",
                laterality="Left anodal / Posterior midline cathodal",
                treatment_course="10–15 sessions over 2–3 weeks",
                monitoring="Rumination Response Scale (RRS); PHQ-9 weekly; skin integrity; self-reported rumination diary",
                expected_response="Reduced ruminative thinking; improved cognitive flexibility; better task engagement",
                evidence_status="Low — based on DMN hyperactivation model of rumination; emerging evidence for PCC cathodal placement",
                cautions="OFF-LABEL montage. Posterior electrode placement requires careful positioning. May cause mild posterior scalp discomfort.",
                when_to_escalate="If rumination persists after 10 sessions, consider adding TPS (T-DEP) for deeper network modulation",
                when_to_stop_modify="Standard tDCS stop criteria. Adjust electrode position if posterior discomfort.",
                clinical_notes_extended="Targets the rumination-specific DMN signature. Best for patients with prominent ruminative thinking (melancholic, TRD, cognitive subtypes). Pair with mindfulness-based cognitive therapy (MBCT).",
                key_citations=["Fregni et al., 2021", "Hamilton et al., 2011", "Brunoni et al., 2016"],
            ),
            ProtocolEntry(
                protocol_id="C8", label="Sleep/Circadian — Right DLPFC Evening Session", modality=Modality.TDCS,
                target_region="Right Dorsolateral Prefrontal Cortex", target_abbreviation="R-DLPFC",
                phenotype_slugs=["mel", "anx", "sad"],
                network_targets=[NetworkKey.SN, NetworkKey.LIMBIC],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "F4 (right DLPFC)",
                    "intensity": "1.5 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                    "note": "Evening session timing (18:00-20:00) to modulate pre-sleep arousal and circadian HPA axis downregulation",
                },
                rationale="Evening-timed right DLPFC cathodal tDCS targets pre-sleep hyperarousal and HPA axis overactivation contributing to MDD insomnia. Reduced intensity (1.5 mA) for evening application. Addresses insomnia as core MDD symptom. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="C8 — tDCS Sleep/Circadian Protocol (Evening DLPFC Session)",
                clinical_objective="Reduce pre-sleep hyperarousal and HPA axis overactivation via evening-timed bilateral DLPFC modulation",
                primary_targets=["F3 (Left DLPFC — anodal)"],
                secondary_targets=["F4 (Right DLPFC — cathodal)"],
                device_name="Newronika HDCkit (2-channel)",
                session_structure="Ch1: Anode F3 (L-DLPFC); Cathode F4 (R-DLPFC). 1.5 mA, 20 min. Evening timing 18:00–20:00.",
                frequency="5 days/week (evening sessions)",
                duration="20 min per session",
                intensity_dose="1.5 mA (reduced for evening application)",
                montage_roi="Anode (+): F3 (L-DLPFC). Cathode (−): F4 (R-DLPFC)",
                laterality="Left anodal / Right cathodal (bilateral)",
                treatment_course="10–15 sessions over 2–3 weeks",
                monitoring="Pittsburgh Sleep Quality Index (PSQI); PHQ-9 weekly; sleep diary; skin integrity",
                expected_response="Improved sleep onset latency; reduced nocturnal arousal; better sleep quality; secondary mood improvement",
                evidence_status="Low — based on HPA axis and circadian rhythm models of MDD insomnia; limited direct RCT evidence for evening-timed protocol",
                cautions="OFF-LABEL. Reduced intensity for evening safety. Avoid caffeine within 4h of session. Session timing critical for circadian benefit.",
                when_to_escalate="If insomnia persists after 10 sessions, add CES (Alpha-Stim) for sleep or refer for CBT-I",
                when_to_stop_modify="Standard tDCS stop criteria. If increased alertness/insomnia paradoxically, switch to morning sessions.",
                clinical_notes_extended="Targets the sleep-depression bidirectional pathway. Best for MDD with prominent insomnia (melancholic, anxious, SAD phenotypes). Pair with sleep hygiene psychoeducation.",
                key_citations=["Fregni et al., 2021", "Brunoni et al., 2016"],
            ),

            # ── T3-T5: Expanded TPS protocols ──────────────────────
            ProtocolEntry(
                protocol_id="T3", label="TPS — DLPFC Deep Prefrontal", modality=Modality.TPS,
                target_region="Dorsolateral Prefrontal Cortex (deep)", target_abbreviation="DLPFC-deep",
                phenotype_slugs=["trd", "mel", "cog"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Left DLPFC deep layers (neuronavigation-guided)",
                    "pulses": "300-400 per session",
                    "frequency": "5 Hz",
                    "energy": "0.20-0.25 mJ/mm2",
                    "sessions": "6-9 over 3 weeks",
                },
                rationale="TPS deep prefrontal stimulation reaches DLPFC layers inaccessible to surface tDCS, targeting CEN hypoactivation at greater cortical depth. Complementary to surface tDCS for treatment-resistant cases. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=9,
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="T3 — TPS Deep Prefrontal Protocol (DLPFC Deep Layers)",
                clinical_objective="Reach deep DLPFC layers inaccessible to surface tDCS for enhanced CEN upregulation in TRD",
                primary_targets=["F3 (Left DLPFC — deep layers)"],
                secondary_targets=["Fz (ACC — indirect network modulation)"],
                device_name="NEUROLITH® TPS System (Storz Medical)",
                session_structure="Neuronavigation setup → Holocranial priming (2,000 pulses) → Targeted deep DLPFC (4,000 pulses) → Secondary ACC (2,000 pulses). Total 8,000–10,000 pulses.",
                frequency="2–3 sessions/week",
                duration="30–45 min per session",
                intensity_dose="0.20–0.25 mJ/mm²; 5 Hz",
                montage_roi="F3 (DLPFC), Fz (ACC). Secondary: deep prefrontal layers via neuronavigation. Total 8,000–10,000 pulses",
                laterality="Left-dominant for DLPFC",
                treatment_course="10–12 sessions / 2–4 weeks; then maintenance 1–2/week",
                monitoring="PHQ-9 weekly; anhedonia scale; tolerability log",
                expected_response="Enhanced CEN activation; improved executive function; reduced treatment resistance",
                evidence_status="Emerging — Qin et al. (2025) demonstrated DLPFC-mPFC connectivity enhancement with TPS",
                cautions="TPS is investigational/off-label. Neuronavigation recommended for deep targets. Enforce 48–72h session spacing.",
                when_to_escalate="If non-response after 6 sessions, consider combining with tDCS (C4-TRD) or switching to accelerated iTBS",
                when_to_stop_modify="Stop if persistent headache or neurological symptoms. Reduce energy if discomfort.",
                clinical_notes_extended="Complementary to surface tDCS — TPS acoustic energy reaches deeper cortical layers. Best for TRD/melancholic/cognitive phenotypes requiring depth penetration beyond tDCS capability.",
                key_citations=["Cheung et al., 2023", "Qin et al., 2025", "Günes et al., 2025"],
            ),
            ProtocolEntry(
                protocol_id="T4", label="TPS — ACC/Subgenual Deep Limbic", modality=Modality.TPS,
                target_region="Anterior Cingulate Cortex / Subgenual ACC", target_abbreviation="ACC/sgACC",
                phenotype_slugs=["trd", "mel"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.DMN],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "sgACC / Cg25 (neuronavigation-guided — deep target)",
                    "pulses": "300-400 per session",
                    "frequency": "5 Hz",
                    "energy": "0.20-0.25 mJ/mm2",
                    "sessions": "6-9 over 3 weeks",
                },
                rationale="TPS targeting sgACC (Cg25) — the critical limbic-cortical hub hyperactive in MDD — aims to directly modulate the node identified by Mayberg et al. as the key depression circuit switch. Deep acoustic energy reaches sgACC depth (~25-30 mm). OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=9,
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="T4 — TPS ACC/Subgenual Deep Limbic Protocol",
                clinical_objective="Directly modulate sgACC (Cg25) hyperactivation — the key depression circuit switch identified by Mayberg",
                primary_targets=["Fz (ACC / sgACC region)"],
                secondary_targets=["F3 (DLPFC — indirect via ACC-DLPFC connectivity)"],
                device_name="NEUROLITH® TPS System (Storz Medical)",
                session_structure="Neuronavigation setup → Holocranial priming (2,000 pulses) → Targeted ACC/sgACC (4,000 pulses) → Secondary DLPFC (2,000 pulses). Total 8,000–10,000 pulses.",
                frequency="2–3 sessions/week",
                duration="30–45 min per session",
                intensity_dose="0.20–0.25 mJ/mm²; 5 Hz",
                montage_roi="Fz (ACC/sgACC), F3 (DLPFC secondary). Deep target: sgACC/Cg25 (~25–30 mm depth). Total 8,000–10,000 pulses",
                laterality="Midline (ACC) with left DLPFC secondary",
                treatment_course="10–12 sessions / 2–4 weeks; then maintenance 1–2/week",
                monitoring="PHQ-9 weekly; anhedonia scale; tolerability log",
                expected_response="Reduced sgACC hyperactivation; improved mood regulation; decreased rumination",
                evidence_status="Emerging — Qin et al. (2025) demonstrated DLPFC-mPFC connectivity enhancement with TPS",
                cautions="TPS is investigational/off-label. Neuronavigation recommended for deep targets. sgACC is a deep target — acoustic energy must traverse cortical layers.",
                when_to_escalate="If non-response after 6 sessions, combine with T-DEP (DLPFC primary) or add tDCS adjunct",
                when_to_stop_modify="Stop if persistent headache, mood destabilization, or neurological symptoms.",
                clinical_notes_extended="Targets the Mayberg depression circuit switch directly. Most investigational of TPS depression protocols. Best for TRD/melancholic phenotypes with confirmed sgACC hyperactivation on fMRI.",
                key_citations=["Cheung et al., 2023", "Qin et al., 2025", "Günes et al., 2025", "Mayberg et al., 2005"],
            ),
            ProtocolEntry(
                protocol_id="T5", label="TPS — Temporal/Hippocampal Memory Consolidation", modality=Modality.TPS,
                target_region="Hippocampus / Temporal Cortex", target_abbreviation="HC/TC",
                phenotype_slugs=["cog", "mel", "trd"],
                network_targets=[NetworkKey.DMN, NetworkKey.LIMBIC],
                parameters={
                    "device": "NEUROLITH (Storz Medical)",
                    "target": "Hippocampal formation bilateral (neuronavigation-guided)",
                    "pulses": "300-400 per session",
                    "frequency": "5 Hz",
                    "energy": "0.20-0.25 mJ/mm2",
                    "sessions": "6-9 over 3 weeks",
                },
                rationale="Hippocampal TPS targets the memory consolidation and neuroplasticity deficits in MDD. Hippocampal volume loss is a hallmark of recurrent depression; TPS-induced neuroplasticity may support hippocampal recovery alongside cognitive rehabilitation. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=9,
                # -- SOZO TRD Fellow Protocol Handbook fields --
                protocol_name="T5 — TPS Temporal/Hippocampal Memory Consolidation Protocol",
                clinical_objective="Target hippocampal neuroplasticity deficits and memory consolidation impairment in recurrent/cognitive MDD",
                primary_targets=["T5 (Left posterior temporal — hippocampal entry)", "T6 (Right posterior temporal — hippocampal entry)"],
                secondary_targets=["F3 (DLPFC — CEN upregulation adjunct)"],
                device_name="NEUROLITH® TPS System (Storz Medical)",
                session_structure="Neuronavigation setup → Holocranial priming (2,000 pulses) → Targeted hippocampal bilateral T5/T6 (4,000 pulses) → Secondary DLPFC (2,000 pulses). Total 8,000–10,000 pulses.",
                frequency="2–3 sessions/week",
                duration="30–45 min per session",
                intensity_dose="0.20–0.25 mJ/mm²; 5 Hz",
                montage_roi="T5/T6 (hippocampus entry bilateral), F3 (DLPFC secondary). Total 8,000–10,000 pulses",
                laterality="Bilateral hippocampal; left DLPFC secondary",
                treatment_course="10–12 sessions / 2–4 weeks; then maintenance 1–2/week",
                monitoring="PHQ-9 weekly; anhedonia scale; tolerability log; MoCA at baseline and endpoint",
                expected_response="Improved memory consolidation; enhanced neuroplasticity; reduced cognitive MDD symptoms",
                evidence_status="Emerging — Qin et al. (2025) demonstrated DLPFC-mPFC connectivity enhancement with TPS",
                cautions="TPS is investigational/off-label. Neuronavigation recommended for deep targets. Hippocampal targeting requires precise acoustic focus.",
                when_to_escalate="If no cognitive improvement after 6 sessions, combine with T3 (deep DLPFC) or add tDCS (C7)",
                when_to_stop_modify="Stop if persistent headache, memory worsening, or neurological symptoms.",
                clinical_notes_extended="Targets hippocampal volume loss and neuroplasticity deficits hallmark of recurrent MDD. Best for cognitive/pseudodementia phenotype. Pair with cognitive rehabilitation exercises.",
                key_citations=["Cheung et al., 2023", "Qin et al., 2025", "Günes et al., 2025"],
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
            "Works as add-on to standard pharmacotherapy. Comorbid AD-related depression: see T-DEP-AD. "
            "| Evidence counts (published papers): TMS=500, tDCS=200, taVNS=80, DBS=30, CES=30, TPS=14, "
            "PEMF=15, LIFU=12, tACS=20, PBM=10, tRNS=3. "
            "Best modalities: TMS (rTMS/iTBS), tDCS."
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


        # --- Auto-enriched: PlatoScience Variants ---
        platoscience_variants=[
            PlatoScienceVariant(
                variant_id="C4-STD-PS", protocol_id="C4-STD",
                label="PlatoScience Depression — Standard DLPFC Protocol",
                parameters={"program": "Think", "electrode_config": "F3 (left DLPFC)", "intensity": "2.0 mA", "duration": "30 min", "ramp": "30 sec"},
                notes="Maps to C4-STD protocol. PlatoScience Think program.",
            ),
            PlatoScienceVariant(
                variant_id="C4-TRD-PS", protocol_id="C4-TRD",
                label="PlatoScience Treatment-Resistant Depression — Intensive Protocol",
                parameters={"program": "Think", "electrode_config": "F3 (left DLPFC)", "intensity": "2.0 mA", "duration": "30 min", "ramp": "30 sec"},
                notes="Maps to C4-TRD protocol. PlatoScience Think program.",
            ),
            PlatoScienceVariant(
                variant_id="C5-PS", protocol_id="C5",
                label="PlatoScience Anxiety/Worry — Right DLPFC Cathodal",
                parameters={"program": "Relax", "electrode_config": "F4 (right DLPFC cathode)", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C5 protocol. PlatoScience Relax program for anxiety reduction.",
            ),
            PlatoScienceVariant(
                variant_id="C6-PS", protocol_id="C6",
                label="PlatoScience Anhedonia/Reward — vmPFC",
                parameters={"program": "Think", "electrode_config": "Fp1 (vmPFC proxy)", "intensity": "1.5 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C6 protocol. PlatoScience Think program.",
            ),
            PlatoScienceVariant(
                variant_id="C7-PS", protocol_id="C7",
                label="PlatoScience Rumination/DMN — PCC/Precuneus",
                parameters={"program": "Focus", "electrode_config": "F3 (left DLPFC anode) / Pz (PCC cathode)", "intensity": "2.0 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C7 protocol. PlatoScience Focus program.",
            ),
            PlatoScienceVariant(
                variant_id="C8-PS", protocol_id="C8",
                label="PlatoScience Sleep/Circadian — Evening Session",
                parameters={"program": "Relax", "electrode_config": "F3/F4 bilateral DLPFC", "intensity": "1.5 mA", "duration": "20 min", "ramp": "30 sec"},
                notes="Maps to C8 protocol. PlatoScience Relax program — evening timing recommended.",
            ),
        ],

        # --- Auto-enriched: Multimodal Combinations ---
        multimodal_combos=[
            MultimodalCombo(
                combo_id="F1", label="Depression — Standard DLPFC Protocol + TPS — Left DLPFC/sgACC Network (MDD/TRD)",
                phenotype_slugs=['mel'],
                tps_protocol_id="T-DEP",
                non_tps_protocol_ids=["C4-STD"],
                sequencing_notes="Week 1-3: tDCS C4-STD daily. Week 2-3: Add TPS T-DEP (2-3x/week).",
                rationale="Combined TDCS + TPS targeting for enhanced cortical modulation.",
            ),
            MultimodalCombo(
                combo_id="F2", label="Treatment-Resistant Depression — Intensive Protocol + TPS — Left DLPFC/sgACC Network (MDD/TRD)",
                phenotype_slugs=['trd'],
                tps_protocol_id="T-DEP",
                non_tps_protocol_ids=["C4-TRD"],
                sequencing_notes="Week 1-3: tDCS C4-TRD daily. Week 2-3: Add TPS T-DEP (2-3x/week).",
                rationale="Combined TDCS + TPS targeting for enhanced cortical modulation.",
            ),
            MultimodalCombo(
                combo_id="F3", label="Treatment-Resistant Depression — Intensive Protocol + TPS — DLPFC (AD-Related Depression, Comorbid)",
                phenotype_slugs=['trd'],
                tps_protocol_id="T-DEP-AD",
                non_tps_protocol_ids=["C4-TRD"],
                sequencing_notes="Week 1-3: tDCS C4-TRD daily. Week 2-3: Add TPS T-DEP-AD (2-3x/week).",
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

        adverse_event_grades=SHARED_ADVERSE_EVENT_GRADES,
        side_effects=SHARED_SIDE_EFFECTS,
        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Bipolar disorder must be screened and exclusion documented in patient record before first session",
            "C-SSRS suicidality assessment is mandatory at every session — failure to administer is a protocol violation",
            "Any active suicidal ideation with intent or plan requires same-day Doctor review and crisis protocol activation",
            "TPS for MDD is explicitly OFF-LABEL — off-label consent documentation required",
        ],
    )
