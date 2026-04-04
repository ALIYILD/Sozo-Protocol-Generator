"""
Post-Traumatic Stress Disorder (PTSD) — Complete condition generator.

Key references:
- Isserles M et al. (2013) Effectiveness of deep TMS as adjunctive treatment for PTSD — European Neuropsychopharmacology. PMID: 23731839
- Philip NS et al. (2018) Low-intensity focused ultrasound for post-traumatic stress disorder — Neuromodulation. PMID: 29479765
- Reinholt N et al. (2019) taVNS for PTSD — A systematic review. (Conference proceedings)
- Weathers FW et al. (2013) PTSD Checklist for DSM-5 (PCL-5). National Center for PTSD.
- Blake DD et al. (1995) Development and initial psychometric properties of the Clinician Administered PTSD Scale. Behaviour Research and Therapy. PMID: 7487939
- Lanius RA et al. (2010) Default mode network in PTSD — Brain connectivity. PMID: 20565312
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


def build_ptsd_condition() -> ConditionSchema:
    """Build the complete PTSD condition schema."""
    return ConditionSchema(
        slug="ptsd",
        display_name="Post-Traumatic Stress Disorder",
        icd10="F43.1",
        aliases=["PTSD", "post-traumatic stress", "trauma disorder", "cPTSD", "complex PTSD", "combat PTSD"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Post-Traumatic Stress Disorder (PTSD) is a trauma- and stressor-related disorder "
            "characterized by four symptom clusters following exposure to actual or threatened death, "
            "serious injury, or sexual violence: (1) intrusion symptoms (flashbacks, nightmares); "
            "(2) persistent avoidance; (3) negative alterations in cognition and mood; and (4) marked "
            "alterations in arousal and reactivity (hypervigilance, exaggerated startle). Lifetime "
            "prevalence is approximately 7-8% in the general population, higher in trauma-exposed "
            "populations (combat veterans 15-30%; sexual assault survivors 30-80%).\n\n"
            "PTSD involves a failure of fear memory extinction with amygdala hyperreactivity and "
            "impaired vmPFC inhibitory control. Neuromodulation targets prefrontal upregulation to "
            "restore fear extinction capacity and improve CEN-amygdala regulation. tDCS (right or left "
            "DLPFC) and taVNS (vagal-cardiac regulation and noradrenergic modulation) represent emerging "
            "non-pharmacological adjuncts to trauma-focused psychotherapy.\n\n"
            "IMPORTANT: Neuromodulation for PTSD should always be delivered alongside trauma-focused "
            "psychological support. Standalone neuromodulation without psychological treatment framework "
            "is not recommended."
        ),

        pathophysiology=(
            "PTSD pathophysiology centers on fear memory circuit dysfunction. The amygdala — particularly "
            "the basolateral amygdala (BLA) — becomes hyperreactive and drives conditioned fear responses "
            "(hyperarousal, exaggerated startle, flashback triggering). Normally, the ventromedial "
            "prefrontal cortex (vmPFC) and infralimbic cortex inhibit amygdala activity and facilitate "
            "fear extinction via the infralimbic-BLA pathway. In PTSD, vmPFC/mPFC volume reduction and "
            "reduced activity impairs this inhibitory pathway, leaving amygdala activity unchecked.\n\n"
            "Hippocampal dysfunction (reduced volume correlating with trauma severity and PTSD duration) "
            "impairs contextual processing of fear memories — fearful responses become context-independent "
            "(generalization). Elevated noradrenaline (from LC hyperactivity) maintains the hyperarousal "
            "state, consolidates traumatic memories, and impairs fear extinction consolidation.\n\n"
            "Network-level: SN hyperactivation (amygdala, insula) dominates the intrusion and "
            "hyperarousal symptom clusters. DMN is altered — excessively activated during rest (rumination "
            "on trauma) with abnormal connectivity patterns (Lanius et al. 2010). CEN is impaired — "
            "prefrontal executive control of fear memories is reduced. Dissociative PTSD subtype shows "
            "distinct pattern: DMN-medial PFC hyperactivation serves as emotional inhibition/overmodulation."
        ),

        core_symptoms=[
            "Intrusion symptoms — unwanted traumatic memories, flashbacks, nightmares",
            "Avoidance — of trauma-related thoughts, feelings, people, places, activities",
            "Negative alterations in cognition and mood — distorted blame, persistent negative emotions, anhedonia, detachment",
            "Hyperarousal and reactivity — hypervigilance, exaggerated startle, irritability, concentration difficulties, sleep disturbance",
        ],

        non_motor_symptoms=[
            "Comorbid major depression (50-80% lifetime in PTSD)",
            "Comorbid anxiety disorders (generalized anxiety, panic)",
            "Substance use disorders (40-60% in combat PTSD)",
            "Chronic pain and somatization",
            "Social and occupational dysfunction",
            "Sleep disorders (nightmares, insomnia)",
        ],

        key_brain_regions=[
            "Amygdala (bilateral) — basolateral amygdala (BLA)",
            "Ventromedial Prefrontal Cortex (vmPFC) / Infralimbic Cortex",
            "Hippocampus (bilateral)",
            "Dorsolateral Prefrontal Cortex (DLPFC)",
            "Anterior Cingulate Cortex (ACC) — dorsal and rostral",
            "Anterior Insula",
        ],

        brain_region_descriptions={
            "Amygdala (bilateral) — basolateral amygdala (BLA)": "Hyperreactive in PTSD — drives fear conditioning, intrusions, and hyperarousal. Abnormally enhanced fear responses to trauma-related cues. Primary pathophysiological node. Target of indirect modulation via vmPFC upregulation.",
            "Ventromedial Prefrontal Cortex (vmPFC) / Infralimbic Cortex": "Reduced volume and activity in PTSD. Normally inhibits amygdala and mediates fear extinction. vmPFC hypofunction is the key mechanism of PTSD persistence. Primary target of tDCS upregulation (via DLPFC-vmPFC connectivity).",
            "Hippocampus (bilateral)": "Volume reduction correlates with PTSD severity. Impaired contextual processing allows fear generalization beyond original trauma context. Episodic memory fragmentation contributes to intrusive memory re-experiencing.",
            "Dorsolateral Prefrontal Cortex (DLPFC)": "CEN node mediating top-down regulation of amygdala via vmPFC and direct projections. DLPFC stimulation upregulates prefrontal control over limbic reactivity. Primary accessible tDCS target.",
            "Anterior Cingulate Cortex (ACC) — dorsal and rostral": "Conflict monitoring and fear extinction consolidation. rACC activity predicts PTSD treatment response. dACC hyperactivation drives arousal symptoms.",
            "Anterior Insula": "SN hub driving visceral arousal and interoceptive threat signaling. Hyperactive in PTSD — contributes to somatic fear responses and hyperarousal.",
        },

        network_profiles=[
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN PTSD. Salience Network hyperactivation — amygdala and anterior insula — "
                "drives the hallmark PTSD symptoms of hypervigilance, threat hyperdetection, emotional "
                "hyperreactivity, and intrusive re-experiencing. Amygdala hyperactivity is the most "
                "replicated PTSD neuroimaging finding. SN hyperactivity drives excessive switching to "
                "threat-detection mode at the expense of task engagement.",
                primary=True, severity="severe",
                evidence_note="Amygdala hyperreactivity in PTSD — multiple fMRI studies; Shin et al.",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Limbic hyperreactivity beyond SN: reduced hippocampal-mediated fear extinction, "
                "persistent HPA axis hyperactivation maintaining trauma-induced stress response, "
                "and high comorbidity of depression (50-80%) and anxiety. vmPFC-amygdala disconnection "
                "is the core limbic circuit dysfunction in PTSD.",
                severity="severe",
                evidence_note="vmPFC-amygdala dysconnectivity in PTSD; Rauch et al.",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "Altered DMN function in PTSD: excessive DMN activation during rest drives rumination "
                "on traumatic memories and self-blame. Lanius et al. (2010) identified distinct DMN "
                "connectivity patterns in hyperactivating vs dissociative PTSD subtypes. DMN intrusions "
                "during task performance parallel ADHD/depression DMN interference pattern.",
                severity="moderate",
                evidence_note="Lanius RA et al. (2010) — DMN in PTSD. PMID: 20565312",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "Impaired CEN — DLPFC hypofunction reduces top-down regulatory control over amygdala "
                "and SN hyperactivity. CEN hypofunction impairs emotion regulation, working memory for "
                "traumatic memories, and extinction of conditioned fear. Primary tDCS upregulation target.",
                severity="moderate",
                evidence_note="DLPFC hypofunction in PTSD; prefrontal regulatory failure model",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Attention network biases toward threat stimuli in PTSD. Hypervigilance reflects "
                "abnormal salience of threat cues. Difficulty sustaining goal-directed attention "
                "reflects competition from hyperactive SN threat detection.",
                severity="moderate",
            ),
        ],

        primary_network=NetworkKey.SN,

        fnon_rationale=(
            "In PTSD, the primary dysfunctional network is the Salience Network (SN) — hyperactive "
            "amygdala drives fear conditioning, hyperarousal, and intrusions. The FNON framework "
            "targets DLPFC (right or left) anodal tDCS to upregulate CEN regulatory control over "
            "amygdala reactivity via vmPFC-amygdala projections. taVNS provides vagal-mediated "
            "autonomic regulation (reducing cardiac hyperarousal), noradrenergic upregulation of "
            "prefrontal circuits, and may enhance fear extinction consolidation during concurrent "
            "exposure-based therapy. CES addresses comorbid insomnia and nightmares."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="classic",
                label="CLASSIC-PTSD — Single-Incident Trauma",
                description="Classic PTSD from circumscribed traumatic event (accident, assault, disaster). Full DSM-5 criteria met. All four symptom clusters present.",
                key_features=["Intrusions/flashbacks", "Avoidance", "Negative mood", "Hyperarousal"],
                primary_networks=[NetworkKey.SN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.TAVNS, Modality.CES],
                tdcs_target="Right DLPFC anodal (F4) — CEN upregulation for amygdala regulation",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="cptsd",
                label="cPTSD — Complex PTSD",
                description="Repeated/prolonged trauma (childhood abuse, captivity, domestic violence). Additional features beyond DSM-5 PTSD: persistent affect dysregulation, negative self-concept, interpersonal difficulties (ICD-11 cPTSD).",
                key_features=["Affect dysregulation", "Negative self-concept", "Relational difficulties", "Emotional flashbacks", "Somatic symptoms"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal for affect and mood; right DLPFC for fear extinction",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="combat",
                label="COMBAT — Military / Combat-Related PTSD",
                description="PTSD from military combat exposure. High comorbidity with mTBI, substance use, and suicide risk. Distinct neurobiology with extensive hyperarousal features.",
                key_features=["Combat-related intrusions", "Moral injury component", "High suicide risk", "TBI comorbidity", "Substance use"],
                primary_networks=[NetworkKey.SN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.CEN, NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.TAVNS, Modality.CES],
                tdcs_target="Right DLPFC anodal + taVNS for autonomic hyperarousal",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="mst",
                label="MST — Military Sexual Trauma",
                description="PTSD following military sexual trauma. High rates of comorbid depression, shame, and interpersonal difficulties.",
                key_features=["Sexual trauma intrusions", "Shame and self-blame", "Interpersonal avoidance", "High depression comorbidity"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.DMN],
                secondary_networks=[NetworkKey.SN, NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal for depression; right DLPFC for fear network",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="ptsd_dep",
                label="PTSD-DEP — PTSD with Comorbid Depression",
                description="PTSD meeting concurrent MDD criteria. Highest functional impairment subgroup.",
                key_features=["Full PTSD criteria", "MDD criteria met", "Anhedonia", "Suicidality risk elevated", "Severe functional impairment"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.DMN],
                secondary_networks=[NetworkKey.SN, NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal (primary depression protocol) + right DLPFC for fear",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="pcl5",
                name="PTSD Checklist for DSM-5",
                abbreviation="PCL-5",
                domains=["intrusion", "avoidance", "negative_cognition_mood", "hyperarousal"],
                timing="baseline",
                evidence_pmid=None,
                notes="Primary PTSD self-report measure. 20 items. Score >=33 = probable PTSD. MCID = 5-10 points. Administer at baseline, weekly. Developed by Weathers et al. for NCPTSD.",
            ),
            AssessmentTool(
                scale_key="caps5",
                name="Clinician-Administered PTSD Scale for DSM-5",
                abbreviation="CAPS-5",
                domains=["intrusion", "avoidance", "negative_cognition_mood", "hyperarousal", "diagnosis", "severity"],
                timing="baseline",
                evidence_pmid="7487939",
                notes="Gold standard clinician-administered PTSD assessment. Provides diagnosis and severity score. Administer at baseline and endpoint. Requires trained clinician.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Comorbid depression monitoring. Mandatory for PTSD-DEP subtype. C-SSRS mandatory at every session for PTSD patients.",
            ),
            AssessmentTool(
                scale_key="psqi",
                name="Pittsburgh Sleep Quality Index",
                abbreviation="PSQI",
                domains=["sleep_quality", "nightmares", "sleep_latency", "sleep_duration"],
                timing="baseline",
                evidence_pmid="2748771",
                notes="Sleep disturbance and nightmares are cardinal PTSD symptoms. PSQI score >5 = poor sleep. Monitor closely.",
            ),
            AssessmentTool(
                scale_key="dass21",
                name="Depression Anxiety Stress Scale — 21 item",
                abbreviation="DASS-21",
                domains=["depression", "anxiety", "stress"],
                timing="baseline",
                evidence_pmid="9880876",
                notes="Comprehensive mood screen covering depression, anxiety, and stress — all highly prevalent in PTSD.",
            ),
            AssessmentTool(
                scale_key="gad7",
                name="Generalized Anxiety Disorder 7-item Scale",
                abbreviation="GAD-7",
                domains=["anxiety", "worry", "hyperarousal"],
                timing="baseline",
                evidence_pmid="16717171",
                notes="Anxiety comorbidity monitoring. GAD is among the most common PTSD comorbidities.",
            ),
        ],

        baseline_measures=[
            "PCL-5 (primary PTSD self-report — weekly monitoring)",
            "CAPS-5 (clinician-administered — baseline and endpoint)",
            "PHQ-9 (depression comorbidity)",
            "GAD-7 (anxiety comorbidity)",
            "PSQI (sleep quality and nightmares)",
            "DASS-21 (comprehensive mood screen)",
            "SOZO PRS (trauma symptoms, mood, sleep, functioning — 0-10)",
            "C-SSRS (mandatory suicidality screen — every session)",
        ],

        followup_measures=[
            "PCL-5 at every session (weekly symptom monitoring)",
            "PHQ-9 at every session (depression and suicidality monitoring)",
            "C-SSRS at every session (mandatory — PTSD has elevated suicide risk)",
            "CAPS-5 at Week 8-10 and 3 months",
            "PSQI at Week 4 and Week 8-10",
            "SOZO PRS at each session and end of block",
        ],

        inclusion_criteria=[
            "DSM-5 diagnosis of PTSD (all four criterion clusters met)",
            "PCL-5 score >=33 at baseline",
            "Psychologically stable enough to participate — not in acute trauma processing crisis",
            "Currently engaged with or willing to engage in trauma-focused psychological support",
            "Age 18-70 years",
            "Capacity to provide informed consent",
            "Stable psychiatric medication for >=4 weeks (or medication-naive)",
        ],

        exclusion_criteria=[
            "Active suicidal ideation with intent or plan — acute psychiatric crisis (refer for acute care)",
            "Active psychosis or psychotic features",
            "Acute substance intoxication at time of session",
            "Active dissociative disorder as primary diagnosis requiring specialist management",
            "Recent (past 4 weeks) significant traumatic re-exposure without stabilization",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "Active suicidal crisis requiring hospitalization",
            "Active severe dissociation during session — safety risk",
        ],

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "monitoring",
                "MANDATORY: Columbia Suicide Severity Rating Scale (C-SSRS) at EVERY session. PTSD carries significantly elevated suicide risk (particularly combat PTSD, MST, cPTSD). Any new or worsening suicidal ideation with intent requires immediate escalation and crisis protocol.",
                "high",
                "PTSD suicide risk epidemiology; clinical governance requirement",
            ),
            make_safety(
                "precaution",
                "PTSD patients may experience trauma-related emotional responses (flashbacks, distress) during or after sessions. Brief post-session grounding check mandatory. Ensure psychological support (therapist or trauma-informed staff) is available or contactable during treatment.",
                "high",
                "Trauma-informed care principles; risk of spontaneous trauma processing during neuromodulation",
            ),
            make_safety(
                "precaution",
                "Neuromodulation should be delivered as an adjunct to trauma-focused psychotherapy (EMDR, PE, CPT), not as standalone treatment. Neuromodulation without concurrent psychological support is not recommended for PTSD.",
                "moderate",
                "Evidence-based PTSD treatment guidelines; neuromodulation as psychotherapy adjunct",
            ),
            make_safety(
                "monitoring",
                "Monitor for dissociative symptoms during and after sessions. If patient reports feeling detached, unreal, or experiences flashback during stimulation, pause session and conduct grounding exercise before continuing.",
                "moderate",
                "Dissociative symptom management in trauma neuromodulation",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Right Dorsolateral Prefrontal Cortex", "R-DLPFC", "right",
                "Right DLPFC anodal tDCS upregulates prefrontal regulatory control over left amygdala "
                "hyperreactivity via interhemispheric and vmPFC-amygdala projections. Right DLPFC "
                "activation enhances fear extinction encoding and contextual threat appraisal. "
                "Isserles et al. (2013) used deep TMS over right DLPFC with trauma exposure. OFF-LABEL.",
                "C-PTSD-R — Right DLPFC Fear Regulation Protocol",
                EvidenceLevel.MEDIUM, off_label=True,
                eeg_canonical=["F4"],
            ),
            make_tdcs_target(
                "Left Dorsolateral Prefrontal Cortex", "L-DLPFC", "left",
                "Left DLPFC anodal tDCS targets comorbid depression and mood components of PTSD. "
                "Standard MDD protocol adapted for PTSD-depression comorbidity. "
                "Upregulates CEN cognitive control and emotion regulation. OFF-LABEL.",
                "C-PTSD-L — Left DLPFC Depression Protocol",
                EvidenceLevel.MEDIUM, off_label=True,
                eeg_canonical=["F3"],
            ),
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve",
                target_abbreviation="taVNS",
                laterality="left",
                rationale="taVNS modulates NTS-amygdala connectivity, reducing amygdala hyperreactivity and "
                          "noradrenergic hyperarousal. Vagal stimulation during extinction may enhance "
                          "extinction memory consolidation (LC-NE-dependent mechanism). Autonomic cardiac "
                          "regulation via vagal tone restoration addresses hyperarousal symptom cluster. "
                          "Investigational in PTSD.",
                protocol_label="TAVNS-PTSD — Autonomic Regulation & Fear Extinction Adjunct",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
                eeg_canonical=["Ear"],
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-PTSD-R", label="Right DLPFC — Fear Regulation Protocol", modality=Modality.TDCS,
                target_region="Right Dorsolateral Prefrontal Cortex", target_abbreviation="R-DLPFC",
                phenotype_slugs=["classic", "combat", "cptsd"],
                network_targets=[NetworkKey.CEN, NetworkKey.LIMBIC],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F4 (right DLPFC)",
                    "cathode": "Fp1 (left supraorbital) or left shoulder",
                    "intensity": "2.0 mA",
                    "duration": "30 min",
                    "sessions": "10-15 over 3 weeks",
                    "electrode_size": "35 cm2",
                    "note": "May be combined with psychotherapy session — tDCS during initial psychotherapy exposure component (discuss with therapist).",
                },
                rationale="Right DLPFC anodal tDCS upregulates prefrontal control of left amygdala reactivity "
                          "via vmPFC pathway. Enhances CEN regulation of fear circuit. Rationale from "
                          "interhemispheric model and deep TMS evidence (Isserles et al. 2013 — DLPFC deep TMS "
                          "with trauma cue exposure produced PCL improvement). OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
                notes="Mandatory: C-SSRS suicidality screening at every session.",
            ),
            ProtocolEntry(
                protocol_id="C-PTSD-L", label="Left DLPFC — Depression & Mood Protocol", modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex", target_abbreviation="L-DLPFC",
                phenotype_slugs=["ptsd_dep", "mst", "cptsd"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN, NetworkKey.LIMBIC],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "Fp2 (right supraorbital)",
                    "intensity": "2.0 mA",
                    "duration": "30 min",
                    "sessions": "10-15",
                },
                rationale="Left DLPFC anodal tDCS for PTSD with comorbid depression — standard MDD "
                          "protocol applied to PTSD-depression triad. Upregulates CEN to suppress DMN rumination "
                          "and limbic hyperactivity. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
                notes="C-SSRS mandatory at every session. Suicidal ideation monitoring critical.",
            ),
            ProtocolEntry(
                protocol_id="TAVNS-PTSD", label="taVNS — Autonomic & Fear Extinction Adjunct", modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve", target_abbreviation="taVNS",
                phenotype_slugs=["classic", "combat", "mst", "cptsd"],
                network_targets=[NetworkKey.SN, NetworkKey.LIMBIC],
                parameters={
                    "device": "NEMOS (tVNS Technologies) or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "250 us",
                    "intensity": "Below pain threshold (0.5-3.0 mA)",
                    "duration": "30-60 min",
                    "sessions": "Daily adjunct during tDCS block",
                    "electrode_placement": "Left cymba conchae",
                },
                rationale="taVNS modulates amygdala reactivity via NTS projections and noradrenergic "
                          "circuits. Restores heart rate variability — a biomarker of autonomic dysregulation "
                          "in PTSD. Vagal stimulation during extinction learning may enhance consolidation "
                          "(established in animal models; translational evidence emerging). "
                          "Investigational in PTSD — limited published data.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=20,
                notes="Investigational. Combine with exposure-based psychotherapy sessions for potential extinction enhancement.",
            ),
            ProtocolEntry(
                protocol_id="CES-PTSD", label="CES — Insomnia, Nightmares & Hyperarousal", modality=Modality.CES,
                target_region="Bilateral earlobe electrodes", target_abbreviation="CES",
                phenotype_slugs=["classic", "combat", "cptsd", "mst"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim AID",
                    "frequency": "0.5 Hz",
                    "intensity": "100-300 uA",
                    "duration": "60 min",
                    "sessions": "Nightly before sleep during treatment block",
                },
                rationale="Alpha-Stim CES FDA-cleared for anxiety, insomnia, and depression. In PTSD, "
                          "addresses hyperarousal, sleep onset difficulty, and mood symptoms. "
                          "Reduces limbic hyperarousal to facilitate sleep onset. Adjunct to tDCS "
                          "and psychological treatment. Non-pharmacological — reduces medication burden.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
            ),
        ],

        symptom_network_mapping={
            "Intrusions / Flashbacks": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Avoidance": [NetworkKey.LIMBIC, NetworkKey.CEN],
            "Hyperarousal / Hypervigilance": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Negative Mood / Anhedonia": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "Sleep Disturbance / Nightmares": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Concentration Difficulties": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Emotional Dysregulation (cPTSD)": [NetworkKey.LIMBIC, NetworkKey.SN],
        },

        symptom_modality_mapping={
            "Intrusions / Flashbacks": [Modality.TDCS, Modality.TAVNS],
            "Avoidance": [Modality.TDCS],
            "Hyperarousal / Hypervigilance": [Modality.TAVNS, Modality.CES, Modality.TDCS],
            "Negative Mood / Anhedonia": [Modality.TDCS, Modality.CES],
            "Sleep Disturbance / Nightmares": [Modality.CES, Modality.TAVNS],
            "Concentration Difficulties": [Modality.TDCS],
            "Emotional Dysregulation (cPTSD)": [Modality.TDCS, Modality.TAVNS, Modality.CES],
        },

        responder_criteria=[
            ">=10-point reduction in PCL-5 from baseline (meaningful change criterion)",
            ">=50% reduction in PCL-5 or score <33 (remission)",
            "PHQ-9 >=50% reduction (PTSD-DEP subtype)",
            "Clinically meaningful SOZO PRS improvement in trauma symptoms and mood domains",
        ],

        non_responder_pathway=(
            "For non-responders at Week 4:\n"
            "1. Assess trauma processing engagement — inadequate psychotherapy adjunct limits response\n"
            "2. Re-evaluate PTSD subtype — cPTSD requires longer treatment and specialist involvement\n"
            "3. Add taVNS for hyperarousal-dominant presentation\n"
            "4. Add CES for sleep/nightmare component\n"
            "5. Switch tDCS montage: right DLPFC for fear features; left DLPFC for depression features\n"
            "6. Assess and treat comorbid substance use — significantly impairs PTSD treatment response\n"
            "7. Doctor psychiatric review for pharmacotherapy optimization (sertraline, prazosin)\n"
            "8. Refer to trauma-focused psychological treatment if not already engaged"
        ),

        evidence_summary=(
            "PTSD neuromodulation has emerging evidence. tDCS in PTSD: limited dedicated RCTs — most "
            "evidence from pilot studies and mechanistic rationale from fear circuit neuroscience. "
            "Isserles et al. (2013) deep TMS with trauma exposure showed PCL improvement in small "
            "controlled trial. taVNS in PTSD: investigational — mechanism-based rationale from "
            "vagal-amygdala connectivity and HRV restoration studies. CES: FDA-cleared for comorbid "
            "symptoms (anxiety, depression, insomnia). Overall: PTSD neuromodulation is an emerging "
            "adjunctive field; evidence quality is low to medium. Robust RCTs urgently needed. "
            "| Evidence counts (published papers): TMS=30, tDCS=10, CES=10, taVNS=5. "
            "Best modalities: TMS, CES."
        ),

        evidence_gaps=[
            "No adequately powered dedicated tDCS RCT for PTSD with PCL-5 as primary endpoint",
            "Optimal tDCS montage for PTSD — right DLPFC vs left DLPFC vs bilateral — no comparative data",
            "taVNS in PTSD — no published RCT; translational evidence from animal models only",
            "Combined neuromodulation + psychotherapy vs psychotherapy alone — no controlled trial",
            "Complex PTSD (cPTSD) — no dedicated neuromodulation study",
        ],

        references=[
            {
                "authors": "Isserles M et al.",
                "year": 2013,
                "title": "Effectiveness of deep transcranial magnetic stimulation combined with a brief exposure procedure in post-traumatic stress disorder — a pilot study",
                "journal": "European Neuropsychopharmacology",
                "pmid": "23731839",
                "evidence_type": "pilot_study",
            },
            {
                "authors": "Lanius RA et al.",
                "year": 2010,
                "title": "Default mode network connectivity as a predictor of post-traumatic stress disorder symptom severity in acutely traumatized subjects",
                "journal": "Acta Psychiatrica Scandinavica",
                "pmid": "20565312",
                "evidence_type": "cohort_study",
            },
            {
                "authors": "Blake DD et al.",
                "year": 1995,
                "title": "The development of a Clinician-Administered PTSD Scale",
                "journal": "Journal of Traumatic Stress",
                "pmid": "7487939",
                "evidence_type": "cohort_study",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        clinical_tips=[
            "C-SSRS mandatory at every session — PTSD has among the highest suicide risk of all psychiatric conditions",
            "Ensure trauma-focused psychological support is in place before initiating neuromodulation — neuromodulation is adjunct, not standalone",
            "Brief grounding check post-session — PTSD patients may experience trauma activation during stimulation",
            "For combat PTSD with mTBI comorbidity: screen for skull fractures and apply TBI safety protocol simultaneously",
            "Consider right DLPFC for predominant fear/hyperarousal features; left DLPFC for predominant depression/anhedonia features",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "C-SSRS mandatory at every session for PTSD patients — suicidality escalation protocol must be documented and accessible",
            "Trauma-focused psychological support must be documented as concurrent treatment — neuromodulation without this is not approved",
            "cPTSD and MST cases require Doctor authorization and specialist psychology coordination",
        ],
    )
