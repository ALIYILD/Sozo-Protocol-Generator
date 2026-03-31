"""
Traumatic Brain Injury (mild-moderate TBI / Post-Concussion Syndrome) — Complete condition generator.

Key references:
- Pape TL et al. (2015) tDCS feasibility study for TBI — Journal of Head Trauma Rehabilitation. PMID: 24535078
- McIntire LK et al. (2017) tDCS effects on cognitive function following TBI — Brain Stimulation. PMID: 27998682
- Hoy KE et al. (2019) Safety of tDCS in cognitive rehabilitation following mTBI. PMID (conference proceedings — no PMID)
- Demirtas-Tatlidede A et al. (2012) Noninvasive brain stimulation in TBI — Journal of Head Trauma Rehabilitation. PMID: 22088972
- McCrea M et al. (2009) Post-concussion symptom scale validation — Journal of the International Neuropsychological Society. PMID: 19038066
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


def build_tbi_condition() -> ConditionSchema:
    """Build the complete TBI / Post-Concussion Syndrome condition schema."""
    return ConditionSchema(
        slug="tbi",
        display_name="Traumatic Brain Injury / Post-Concussion Syndrome",
        icd10="S09.90",
        aliases=["TBI", "mTBI", "concussion", "post-concussion syndrome", "PCS", "mild TBI", "brain injury"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Traumatic Brain Injury (TBI) encompasses a spectrum from mild concussion (mTBI) to severe "
            "injury, caused by external mechanical force to the head. Mild TBI (mTBI/concussion) is "
            "the most prevalent form, with 60-90% of all TBIs classified as mild. Post-Concussion "
            "Syndrome (PCS) describes persistent symptoms beyond the expected recovery window (>4 weeks), "
            "including cognitive impairment (brain fog, memory difficulties), headache, fatigue, sleep "
            "disturbance, emotional dysregulation, and mood disorders. PCS affects 10-30% of mTBI "
            "patients and is highly disabling.\n\n"
            "Neuromodulation in TBI/PCS targets the DLPFC to address cognitive and emotional sequelae. "
            "tDCS shows emerging evidence in several pilot studies for improving cognitive function, "
            "reducing fatigue, and improving mood post-TBI. taVNS is under investigation for vagal-"
            "mediated neuroplasticity and autonomic dysregulation (common in TBI)."
        ),

        pathophysiology=(
            "TBI pathophysiology involves two injury phases. Primary injury occurs at impact: "
            "mechanical deformation causes neuronal cell death, axonal shear injury (diffuse axonal "
            "injury — DAI), vascular disruption, and contusions. Secondary injury cascade follows: "
            "excitotoxicity (glutamate release), calcium influx, mitochondrial dysfunction, oxidative "
            "stress, neuroinflammation (microglial activation), cerebral edema, and axonal degeneration.\n\n"
            "Mild TBI/concussion produces neurometabolic dysfunction without structural damage visible "
            "on standard MRI: ionic flux disturbance, impaired glucose metabolism (FDG-PET hypometabolism), "
            "and disruption of white matter connectivity (detectable on DTI). These metabolic changes "
            "explain the clinical symptom cluster.\n\n"
            "Chronic TBI pathophysiology involves: persistent neuroinflammation; white matter tract "
            "degeneration (reduced fractional anisotropy on DTI); cholinergic and dopaminergic disruption "
            "(particularly basal forebrain and frontal circuits); and network-level connectivity changes "
            "— CEN hypofunction, DMN hyperactivation, and impaired SN network switching. "
            "Post-TBI depression and anxiety reflect HPA axis dysregulation, limbic network changes, "
            "and adjustment disorder components."
        ),

        core_symptoms=[
            "Cognitive impairment — brain fog, slowed processing speed, working memory difficulties",
            "Headache — tension-type, migraine-like, or pressure-quality post-concussive",
            "Fatigue — disproportionate physical and mental fatigability",
            "Sleep disturbance — insomnia, hypersomnia, sleep architecture changes",
            "Dizziness and vestibular symptoms",
            "Sensory sensitivity — photophobia, phonophobia",
            "Concentration and attention difficulties",
        ],

        non_motor_symptoms=[
            "Depression (25-50% post-TBI)",
            "Anxiety and irritability",
            "Emotional dysregulation — low threshold for emotional reactions",
            "Apathy and reduced motivation",
            "Pain hypersensitivity (central sensitization component)",
            "Social and occupational functional impairment",
        ],

        key_brain_regions=[
            "Dorsolateral Prefrontal Cortex (DLPFC)",
            "Anterior Cingulate Cortex (ACC)",
            "Hippocampus",
            "White Matter Tracts (corpus callosum, uncinate fasciculus)",
            "Thalamus",
            "Anterior Insula / Salience Network Hubs",
        ],

        brain_region_descriptions={
            "Dorsolateral Prefrontal Cortex (DLPFC)": "Highly vulnerable to TBI-related white matter disruption and CEN hypofunction. Working memory, executive function, and emotion regulation impaired. Primary tDCS anodal target.",
            "Anterior Cingulate Cortex (ACC)": "Impaired conflict monitoring, error detection, and arousal regulation post-TBI. Contributes to attention deficits and emotional dysregulation.",
            "Hippocampus": "Vulnerable to TBI excitotoxicity and corticosteroid-mediated damage. Memory encoding and contextual processing impaired. Volume reduction documented in moderate-severe TBI.",
            "White Matter Tracts (corpus callosum, uncinate fasciculus)": "Primary site of diffuse axonal injury (DAI) in mTBI. DTI fractional anisotropy reduction correlates with cognitive and emotional symptom severity.",
            "Thalamus": "Thalamic involvement in moderate-severe TBI disrupts sensory gating, arousal, and cortical connectivity. Central to fatigue and sensory sensitivity post-TBI.",
            "Anterior Insula / Salience Network Hubs": "Impaired interoceptive processing and network switching. Contributes to fatigue, pain sensitivity, and emotional dysregulation in PCS.",
        },

        network_profiles=[
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "PRIMARY NETWORK IN TBI. CEN hypofunction — DLPFC and parietal — is the most consistent "
                "network finding in TBI neuroimaging. Impairs working memory, attention, executive function, "
                "and top-down emotional regulation. Correlates with post-concussive cognitive symptoms. "
                "Primary tDCS target for cognitive rehabilitation.",
                primary=True, severity="severe",
                evidence_note="Multiple resting-state fMRI studies of mTBI; CEN hypofunction correlates with PCS severity",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation and failure to deactivate during task performance is documented in "
                "mTBI. Abnormal CEN-DMN anticorrelation mirrors ADHD-like network pattern. Contributes "
                "to attentional intrusions, rumination, and cognitive fatigability.",
                severity="moderate",
                evidence_note="DMN disruption post-TBI; Mayer et al. — altered resting-state connectivity",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPO,
                "SN dysregulation — reduced network switching efficiency — impairs the transition from "
                "DMN to CEN states. Anterior insula involvement drives fatigue, pain sensitivity, and "
                "altered interoceptive processing. Autonomic dysfunction reflects SN disruption.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Sustained and divided attention deficits are core PCS complaints. Dorsal and ventral "
                "attention networks disrupted by frontal white matter tract injury. Correlates with "
                "occupational disability and return-to-sport/work delays.",
                severity="severe",
                evidence_note="Attention network dysfunction in PCS; cognitive-fatigue interaction",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Post-TBI depression and anxiety reflect limbic hyperreactivity, HPA axis dysregulation, "
                "and reduced prefrontal inhibitory control. Amygdala hyperreactivity documented in TBI. "
                "Emotional dysregulation is one of the most disabling PCS consequences.",
                severity="moderate",
                evidence_note="Post-TBI limbic dysregulation; HPA axis disruption in TBI",
            ),
        ],

        primary_network=NetworkKey.CEN,

        fnon_rationale=(
            "In TBI/PCS, the primary dysfunctional network is the Central Executive Network (CEN), "
            "disrupted by diffuse axonal injury to prefrontal-parietal white matter tracts and "
            "DLPFC cortical metabolic dysfunction. The FNON framework targets left DLPFC anodal "
            "tDCS to upregulate CEN excitability and restore CEN-DMN anticorrelation, addressing "
            "cognitive-fatigue symptoms. taVNS provides complementary noradrenergic upregulation "
            "and autonomic regulation. CES addresses sleep disturbance and anxiety/mood components "
            "via limbic and SN modulation."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="cog_fat",
                label="COG-FAT — Cognitive-Fatigue Subtype",
                description="Predominant cognitive slowing, brain fog, disproportionate mental and physical fatigue. CEN hypofunction and metabolic dysfunction dominant.",
                key_features=["Brain fog", "Slowed processing", "Working memory deficit", "Mental fatigue", "Concentration impairment"],
                primary_networks=[NetworkKey.CEN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.DMN, NetworkKey.SN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal (F3) + right shoulder/supraorbital cathode",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="emo_beh",
                label="EMO-BEH — Emotional-Behavioral Subtype",
                description="Prominent emotional dysregulation, irritability, depression, anxiety, or personality change. Limbic-frontal network disruption.",
                key_features=["Irritability", "Emotional lability", "Depression", "Anxiety", "Reduced frustration tolerance"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.CEN],
                secondary_networks=[NetworkKey.SN, NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal; add CES for mood/sleep",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="pcs",
                label="PCS — Post-Concussion Syndrome",
                description="Persistent multi-symptom syndrome >4 weeks after mTBI. Mixed cognitive, emotional, somatic, and sleep symptoms. Most common neuromodulation indication in TBI.",
                key_features=["Headache", "Brain fog", "Sleep disturbance", "Dizziness", "Mood changes", "Fatigue"],
                primary_networks=[NetworkKey.CEN, NetworkKey.SN],
                secondary_networks=[NetworkKey.LIMBIC, NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal — comprehensive PCS protocol",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="chronic_tbi",
                label="CHRONIC-TBI — Chronic TBI Sequelae",
                description="Moderate-severe TBI with chronic cognitive, behavioral, and motor deficits. Multi-network dysfunction. Longer treatment blocks required.",
                key_features=["Persistent cognitive impairment", "Behavioral dysregulation", "Motor sequelae", "Chronic pain", "Reduced independence"],
                primary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.LIMBIC, NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS, Modality.CES],
                tdcs_target="DLPFC bilateral anodal — extended protocol",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="pcss",
                name="Post-Concussion Symptom Scale",
                abbreviation="PCSS",
                domains=["headache", "cognitive", "emotional", "sleep", "balance", "fatigue"],
                timing="baseline",
                evidence_pmid="19038066",
                notes="Primary PCS symptom burden measure. 22 items, 0-6 Likert scale. Total score /132. Administer at baseline, weekly monitoring.",
            ),
            AssessmentTool(
                scale_key="moca",
                name="Montreal Cognitive Assessment",
                abbreviation="MoCA",
                domains=["cognition", "memory", "attention", "executive_function"],
                timing="baseline",
                evidence_pmid="15817019",
                notes="Global cognitive screen. Score <26 = possible impairment in TBI. Administer at baseline and endpoint.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Post-TBI depression screen. Score >=10 = moderate depression. Monitor at every session.",
            ),
            AssessmentTool(
                scale_key="psqi",
                name="Pittsburgh Sleep Quality Index",
                abbreviation="PSQI",
                domains=["sleep_quality", "sleep_latency", "sleep_duration", "sleep_disturbance"],
                timing="baseline",
                evidence_pmid="2748771",
                notes="Sleep assessment critical in TBI — sleep disturbance worsens all PCS symptoms. Score >5 = poor sleep quality.",
            ),
            AssessmentTool(
                scale_key="brief2",
                name="Behavior Rating Inventory of Executive Function — 2nd Edition",
                abbreviation="BRIEF-2",
                domains=["inhibition", "cognitive_flexibility", "working_memory", "planning", "organization"],
                timing="baseline",
                evidence_pmid="11385981",
                notes="Ecological executive function assessment. Captures TBI executive deficits in daily functioning. Compare with self-report vs informant versions.",
            ),
            AssessmentTool(
                scale_key="gad7",
                name="Generalized Anxiety Disorder 7-item Scale",
                abbreviation="GAD-7",
                domains=["anxiety", "worry", "hyperarousal"],
                timing="baseline",
                evidence_pmid="16717171",
                notes="Anxiety screen — high comorbidity in PCS. Score >=10 = moderate anxiety.",
            ),
        ],

        baseline_measures=[
            "PCSS (Post-Concussion Symptom Scale — primary PCS symptom measure)",
            "MoCA (global cognitive screen)",
            "PHQ-9 and GAD-7 (mood and anxiety comorbidity)",
            "PSQI (sleep quality — critical in TBI)",
            "BRIEF-2 (executive function in daily life)",
            "SOZO PRS (cognitive, mood, pain, sleep, fatigue — 0-10)",
            "Neuroimaging review — rule out intracranial pathology (hemorrhage, skull fracture)",
        ],

        followup_measures=[
            "PCSS at every session (brief symptom monitoring)",
            "MoCA at Week 8-10",
            "PHQ-9 at every session (depression monitoring)",
            "PSQI at Week 4 and Week 8-10",
            "SOZO PRS at each session and end of block",
            "Adverse event documentation at every session",
        ],

        inclusion_criteria=[
            "Confirmed diagnosis of mild-to-moderate TBI with persistent PCS symptoms",
            "Minimum 3 months post-injury (subacute recovery window complete)",
            "Age 18-65 years",
            "PCSS total score >=20 (clinically significant symptom burden)",
            "Medically stable — no active intracranial pathology on neuroimaging",
            "No skull fracture or metallic intracranial fragments",
            "Capacity to provide informed consent",
        ],

        exclusion_criteria=[
            "Acute TBI (<3 months post-injury) — neurometabolic dysfunction phase; risk of worsening",
            "Skull fracture at electrode placement site",
            "Intracranial metallic fragments from penetrating TBI",
            "Active intracranial hypertension or unresolved subdural collection",
            "Severe TBI with significant structural damage (CDR equivalent) limiting cooperation",
            "Active alcohol or substance use disorder",
            "Current anticoagulation therapy (TPS contraindication if applicable)",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "Acute TBI (<3 months) — neurometabolic vulnerability window; avoid neuromodulation",
            "Skull fractures or cranial metallic fragments — altered current distribution risk",
            "Raised intracranial pressure — any clinical signs require immediate exclusion",
        ],

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "contraindication",
                "ACUTE TBI: Neuromodulation is contraindicated within 3 months of TBI. Neurometabolic dysfunction phase makes the brain more susceptible to stimulation-related adverse effects. Wait minimum 3 months for mTBI/PCS; consult neurologist for moderate-severe TBI timing.",
                "high",
                "Consensus safety principles for neuromodulation post-TBI",
            ),
            make_safety(
                "precaution",
                "Review neuroimaging before treatment initiation. Confirm no active intracranial pathology (hemorrhage, contusion, subdural, epidural). Rule out skull fracture or metallic fragments that would alter current distribution.",
                "high",
                "Neuroimaging safety review mandatory for TBI neuromodulation",
            ),
            make_safety(
                "precaution",
                "Start at lower stimulation intensity (1.5 mA) in TBI patients — may demonstrate increased sensitivity to stimulation due to neurometabolic disruption. Titrate to 2.0 mA only after confirmed tolerance across 2-3 sessions.",
                "moderate",
                "Clinical precaution for TBI population — altered cortical excitability threshold",
            ),
            make_safety(
                "monitoring",
                "Monitor for headache worsening during or after sessions. Post-TBI headache exacerbation is common and may indicate need to reduce intensity or duration. Document headache VAS at start and end of each session.",
                "moderate",
                "Post-TBI headache exacerbation monitoring",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Dorsolateral Prefrontal Cortex", "DLPFC", "left",
                "Left DLPFC anodal tDCS targets CEN hypofunction — the primary cognitive deficit mechanism "
                "in TBI. Upregulates prefrontal circuits impaired by diffuse axonal injury and metabolic "
                "dysfunction. Multiple pilot studies (Pape 2015, McIntire 2017) demonstrate cognitive "
                "improvements in TBI patients with DLPFC tDCS.",
                "C-TBI-COG — Cognitive Rehabilitation Protocol",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve",
                target_abbreviation="taVNS",
                laterality="left",
                rationale="taVNS modulates NTS-LC noradrenergic pathways and autonomic tone. In TBI, "
                          "addresses autonomic dysregulation (heart rate variability reduction), noradrenergic "
                          "deficiency contributing to fatigue and cognitive impairment, and vagal-mediated "
                          "neuroplasticity. Investigational in TBI — no published RCT.",
                protocol_label="TAVNS-TBI — Autonomic & Cognitive Adjunct",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-TBI-COG", label="Cognitive Rehabilitation — DLPFC tDCS", modality=Modality.TDCS,
                target_region="Dorsolateral Prefrontal Cortex", target_abbreviation="DLPFC",
                phenotype_slugs=["cog_fat", "pcs", "chronic_tbi"],
                network_targets=[NetworkKey.CEN, NetworkKey.ATTENTION],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC) or bilateral F3+F4",
                    "cathode": "Fp2 (right supraorbital) or right shoulder",
                    "intensity": "1.5-2.0 mA (start 1.5 mA for first 2-3 sessions in TBI)",
                    "duration": "20 min",
                    "sessions": "10-15 over 3 weeks",
                    "electrode_size": "35 cm2",
                    "note": "Concurrent cognitive training (working memory, attention) recommended during tDCS.",
                },
                rationale="DLPFC anodal tDCS targets CEN hypofunction — the primary cognitive mechanism in TBI. "
                          "Pape et al. (2015) pilot study demonstrated improved attention in TBI. "
                          "McIntire et al. (2017) demonstrated cognitive improvements in mTBI. "
                          "Start at 1.5 mA due to TBI-related altered cortical excitability. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="TAVNS-TBI", label="taVNS — Autonomic & Fatigue Adjunct", modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve", target_abbreviation="taVNS",
                phenotype_slugs=["cog_fat", "pcs"],
                network_targets=[NetworkKey.SN, NetworkKey.CEN, NetworkKey.LIMBIC],
                parameters={
                    "device": "NEMOS (tVNS Technologies) or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "200-250 us",
                    "intensity": "Below pain threshold (0.5-4.0 mA)",
                    "duration": "30 min",
                    "sessions": "Daily adjunct during tDCS block",
                    "electrode_placement": "Left cymba conchae",
                },
                rationale="taVNS modulates autonomic tone and noradrenergic upregulation in TBI. "
                          "Autonomic dysfunction (reduced HRV) is prevalent in TBI and correlates with "
                          "symptom severity. Vagal-mediated BDNF upregulation may enhance neuroplasticity. "
                          "Investigational in TBI — rationale from autonomic dysfunction and noradrenergic literature.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=20,
                notes="Investigational in TBI. Monitor heart rate during initial sessions — autonomic sensitivity in TBI.",
            ),
            ProtocolEntry(
                protocol_id="CES-TBI", label="CES — Sleep, Anxiety & Mood Adjunct", modality=Modality.CES,
                target_region="Bilateral earlobe electrodes", target_abbreviation="CES",
                phenotype_slugs=["pcs", "emo_beh", "cog_fat"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim AID",
                    "frequency": "0.5 Hz",
                    "intensity": "100-300 uA",
                    "duration": "40-60 min",
                    "sessions": "Daily during treatment block",
                },
                rationale="Alpha-Stim CES FDA-cleared for anxiety, depression, and insomnia. In TBI/PCS, "
                          "targets the highly prevalent triad of sleep disturbance, anxiety, and mood symptoms. "
                          "Non-pharmacological intervention that reduces medication burden in TBI patients. "
                          "Adjunct to DLPFC tDCS for comprehensive PCS treatment.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
            ),
            ProtocolEntry(
                protocol_id="C-TBI-MOOD", label="Post-TBI Depression — DLPFC tDCS", modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex", target_abbreviation="L-DLPFC",
                phenotype_slugs=["emo_beh"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "Fp2 (right supraorbital)",
                    "intensity": "2.0 mA",
                    "duration": "30 min",
                    "sessions": "10-15",
                },
                rationale="Post-TBI depression is treated with left DLPFC anodal tDCS using MDD protocol "
                          "rationale. Restores CEN-DMN balance, reducing limbic hyperactivity and depressive "
                          "tone. PHQ-9 monitoring mandatory. C-SSRS at every session. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
                notes="Mandatory: C-SSRS suicidality monitoring at every session. PHQ-9 at each visit.",
            ),
        ],

        symptom_network_mapping={
            "Brain Fog / Cognitive Slowing": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Fatigue": [NetworkKey.SN, NetworkKey.CEN],
            "Headache": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Sleep Disturbance": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Depression / Mood": [NetworkKey.LIMBIC, NetworkKey.CEN],
            "Anxiety / Irritability": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Working Memory Deficit": [NetworkKey.CEN, NetworkKey.DMN],
        },

        symptom_modality_mapping={
            "Brain Fog / Cognitive Slowing": [Modality.TDCS],
            "Fatigue": [Modality.CES, Modality.TAVNS, Modality.TDCS],
            "Headache": [Modality.CES],
            "Sleep Disturbance": [Modality.CES, Modality.TAVNS],
            "Depression / Mood": [Modality.TDCS, Modality.CES],
            "Anxiety / Irritability": [Modality.CES, Modality.TAVNS],
            "Working Memory Deficit": [Modality.TDCS],
        },

        responder_criteria=[
            ">=30% reduction in PCSS total score from baseline",
            ">=50% reduction in PHQ-9 score (depression subtype)",
            "Clinically meaningful improvement in SOZO PRS cognitive domain (>=3 points)",
            "MoCA score stabilization or improvement",
        ],

        non_responder_pathway=(
            "For non-responders at Week 4:\n"
            "1. Re-evaluate TBI severity — confirm not acute window (<3 months)\n"
            "2. Screen for untreated sleep disorder — severe insomnia limits all cognitive outcomes\n"
            "3. Optimize CES for sleep/anxiety before escalating tDCS\n"
            "4. Add taVNS for autonomic dysregulation and fatigue component\n"
            "5. Check headache worsening — reduce to 1.5 mA if exacerbating post-TBI headache\n"
            "6. Neurological review — rule out new pathology or missed moderate TBI diagnosis\n"
            "7. Doctor psychiatric review for post-TBI depression/anxiety management"
        ),

        evidence_summary=(
            "TBI/PCS has emerging evidence for tDCS. Pape et al. (2015) pilot study (J Head Trauma Rehab) "
            "demonstrated attention improvements with DLPFC tDCS in chronic TBI. McIntire et al. (2017) "
            "confirmed cognitive improvements in mTBI. Multiple small studies support feasibility and "
            "safety. No large multi-site RCT completed. taVNS: investigational — rationale from autonomic "
            "dysfunction and noradrenergic deficiency in TBI. CES: FDA-cleared for comorbid symptoms; "
            "useful adjunct."
        ),

        evidence_gaps=[
            "No adequately powered multi-site RCT of tDCS for PCS with validated primary cognitive endpoint",
            "Optimal timing of neuromodulation post-TBI — early vs late intervention window",
            "Stimulation parameters for TBI — altered threshold due to neurometabolic dysfunction",
            "taVNS in TBI — no published RCT; mechanism-based rationale only",
            "TPS in TBI — no published controlled data",
            "Distinguishing neurometabolic vs psychological contributions to PCS — affects optimal treatment targeting",
        ],

        references=[
            {
                "authors": "Pape TL et al.",
                "year": 2015,
                "title": "Preliminary findings of a feasibility study on the effects of transcranial direct current stimulation on attention and concentration in persons with traumatic brain injury",
                "journal": "Journal of Head Trauma Rehabilitation",
                "pmid": "24535078",
                "evidence_type": "pilot_study",
            },
            {
                "authors": "Demirtas-Tatlidede A et al.",
                "year": 2012,
                "title": "Noninvasive brain stimulation in traumatic brain injury",
                "journal": "Journal of Head Trauma Rehabilitation",
                "pmid": "22088972",
                "evidence_type": "narrative_review",
            },
            {
                "authors": "McCrea M et al.",
                "year": 2009,
                "title": "Reliability, sensitivity and specificity of the Standardized Assessment of Concussion and the post-concussion symptom scale",
                "journal": "Journal of the International Neuropsychological Society",
                "pmid": "19038066",
                "evidence_type": "cohort_study",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        clinical_tips=[
            "Always review neuroimaging before treatment — rule out intracranial metallic fragments, skull fractures, and active hematoma",
            "Start at 1.5 mA and monitor for headache exacerbation at each early session — TBI patients may have altered cortical excitability",
            "Prioritize sleep optimization before cognitive tDCS — severe insomnia limits neuroplasticity and cognitive treatment response",
            "Document time since injury clearly — exclude patients <3 months post-injury regardless of symptom severity",
            "Monitor post-TBI depression at every session (PHQ-9) — highly prevalent and severely impairs rehabilitation engagement",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Neuroimaging review mandatory before treatment initiation — rule out intracranial metallic fragments and active pathology",
            "Minimum 3 months post-TBI before neuromodulation — document injury date in clinical record",
        ],
    )
