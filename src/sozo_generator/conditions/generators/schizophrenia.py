"""
Schizophrenia — Complete condition generator.

Key references:
- Hoffman RE et al. (2003) Transcranial magnetic stimulation of left temporal-parietal cortex
  and medication-resistant auditory hallucinations. PMID: 12695316
- Brunelin J et al. (2012) Examining transcranial direct-current stimulation (tDCS) as a treatment
  for hallucinations in schizophrenia. PMID: 22948059
- Mondino M et al. (2015) Cathodal tDCS over the left temporoparietal cortex decreases symptom
  severity in refractory schizophrenia. PMID: 25498221
- Kay SR et al. (1987) The positive and negative syndrome scale (PANSS). PMID: 3616518
- Andreasen NC (1983) Scale for the Assessment of Negative Symptoms (SANS).
- Cordes J et al. (2015) Frontoparietal tDCS in schizophrenia.
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


def build_schizophrenia_condition() -> ConditionSchema:
    """Build the complete Schizophrenia condition schema."""
    return ConditionSchema(
        slug="schizophrenia",
        display_name="Schizophrenia",
        icd10="F20",
        aliases=["schizophrenia", "psychosis", "first episode psychosis"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Schizophrenia is a severe, chronic psychiatric disorder characterized by disturbances "
            "in thought, perception, emotion, and behavior. Lifetime prevalence is approximately "
            "0.7-1%, affecting approximately 21 million people worldwide. Onset typically occurs "
            "in late adolescence to early adulthood. Schizophrenia carries significant morbidity: "
            "cognitive deficits, social and occupational disability, reduced life expectancy "
            "(10-20 years), and high suicide risk (5-10% lifetime).\n\n"
            "Despite antipsychotic medication, 20-30% of patients have persistent positive symptoms "
            "(auditory hallucinations, delusions), and negative symptoms (avolition, anhedonia, "
            "flat affect) and cognitive deficits are poorly addressed by current pharmacotherapy.\n\n"
            "Neuromodulation in schizophrenia is adjunctive to antipsychotics. The strongest "
            "evidence is for 1 Hz inhibitory TMS or cathodal tDCS over left temporal-parietal "
            "cortex (Broca's/Wernicke's area) to reduce medication-resistant auditory hallucinations. "
            "tDCS with bifrontal montage (anodal L-DLPFC + cathodal temporoparietal) addresses "
            "both cognitive deficits and positive symptoms. CONTRAINDICATED in acute psychosis."
        ),

        pathophysiology=(
            "Schizophrenia pathophysiology is multifactorial and network-based:\n\n"
            "(1) Dopamine dysregulation: Mesolimbic hyperdopaminergia drives positive symptoms "
            "(hallucinations, delusions). Mesocortical hypodopaminergia (especially DLPFC) drives "
            "negative symptoms and cognitive deficits. D2 receptor blockade is the basis of "
            "antipsychotic action.\n\n"
            "(2) Glutamate/NMDA receptor hypofunction: NMDA receptor hypofunction on GABAergic "
            "interneurons (particularly PV+ fast-spiking interneurons) disrupts cortical "
            "synchronization and gamma oscillations. This generates cognitive deficits and "
            "disorganized thinking.\n\n"
            "(3) Auditory hallucinations neural model: Aberrant activation of left temporal "
            "language cortex (Broca's/Wernicke's area, superior temporal gyrus, temporoparietal "
            "junction) generates self-attributed misperceptions. Abnormal inner speech monitoring "
            "leads to hallucinated voices. Low-frequency (1 Hz) TMS inhibits this hyperactive "
            "language cortex.\n\n"
            "(4) Default Mode Network (DMN) hyperactivation: Failure to suppress DMN during "
            "cognitive tasks drives intrusive self-referential processing, delusion formation, "
            "and disorganized thinking.\n\n"
            "(5) CEN/DLPFC hypoactivation: DLPFC hypofunction drives working memory deficits, "
            "executive dysfunction, and poor functional outcome — the cognitive phenotype."
        ),

        core_symptoms=[
            "Auditory hallucinations — hearing voices, commentary, conversations",
            "Delusions — fixed false beliefs (persecutory, referential, grandiose)",
            "Negative symptoms — avolition, anhedonia, flat affect, alogia, asociality",
            "Cognitive deficits — working memory, attention, processing speed, executive function",
            "Disorganized thinking and speech (loose associations, tangentiality)",
        ],

        non_motor_symptoms=[
            "Depression (25-50% comorbid — independently predicts poor outcome)",
            "Anxiety (30-40% comorbid)",
            "Social withdrawal and isolation",
            "Poor insight (anosognosia) — common and impairs treatment adherence",
        ],

        key_brain_regions=[
            "Left Temporal-Parietal Cortex (Wernicke's / Superior Temporal Gyrus)",
            "Left Broca's Area (inferior frontal gyrus)",
            "Dorsolateral Prefrontal Cortex (bilateral)",
            "Anterior Cingulate Cortex",
            "Striatum / Nucleus Accumbens",
            "Thalamus (mediodorsal nucleus)",
        ],

        brain_region_descriptions={
            "Left Temporal-Parietal Cortex (Wernicke's / Superior Temporal Gyrus)": "Hyperactive "
                "during auditory hallucinations — primary TMS/tDCS inhibition target. "
                "Cathodal tDCS or 1 Hz rTMS reduces hallucination frequency and severity.",
            "Left Broca's Area (inferior frontal gyrus)": "Inner speech production area; "
                "hyperactivation contributes to voice misattribution. Secondary inhibition target.",
            "Dorsolateral Prefrontal Cortex (bilateral)": "Hypoactivated in schizophrenia — "
                "drives cognitive deficits and negative symptoms. Left DLPFC anodal tDCS "
                "target for cognitive enhancement.",
            "Anterior Cingulate Cortex": "Error monitoring and salience processing disrupted "
                "in schizophrenia. Contributes to poor insight and negative symptom burden.",
            "Striatum / Nucleus Accumbens": "Hyperdopaminergic — drives positive symptoms. "
                "Primary target of antipsychotic medication.",
            "Thalamus (mediodorsal nucleus)": "Reduced thalamo-cortical connectivity contributes "
                "to sensory gating deficits and hallucination generation.",
        },

        network_profiles=[
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN SCHIZOPHRENIA (positive symptoms). DMN hyperactivation "
                "and failure of task-appropriate DMN suppression drives intrusive self-referential "
                "processing, delusion formation, and hallucination generation. Abnormal DMN-CEN "
                "anticorrelation is a core neuroimaging finding.",
                primary=True, severity="severe",
                evidence_note="Whitfield-Gabrieli & Ford (2012) — DMN in schizophrenia",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "CEN (DLPFC-parietal) hypoactivation drives cognitive deficits — working memory, "
                "executive function, processing speed. Cognitive impairment is the strongest "
                "predictor of functional outcome in schizophrenia. DLPFC anodal tDCS target.",
                severity="severe",
                evidence_note="Weinberger et al. (1986) — hypofrontality in schizophrenia",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "Salience network dysregulation drives aberrant salience attribution — assigning "
                "significance to irrelevant stimuli, generating delusions and paranoid ideation. "
                "AIC and ACC hyperactivation in positive symptom states.",
                severity="moderate-severe",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Limbic hyperactivation contributes to affective dysregulation, depression "
                "comorbidity, and emotional blunting. Amygdala hyperreactivity to faces in "
                "paranoid schizophrenia.",
                severity="moderate",
            ),
        ],

        primary_network=NetworkKey.DMN,

        fnon_rationale=(
            "In schizophrenia, neuromodulation targets two distinct mechanisms: "
            "(1) Inhibitory approach — cathodal tDCS or 1 Hz TMS over left temporoparietal "
            "cortex to reduce auditory hallucination-generating hyperactivity; "
            "(2) Excitatory approach — anodal tDCS over left DLPFC to upregulate CEN and "
            "address cognitive deficits and negative symptoms. "
            "Bifrontal-temporal montage (anodal L-DLPFC + cathodal L-temporoparietal) "
            "is the most rational dual-target approach. "
            "ADJUNCT TO ANTIPSYCHOTICS ONLY — neuromodulation should not replace medication."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="positive_predominant",
                label="SCZ-POS — Positive Symptom Predominant",
                description="Auditory hallucinations and/or delusions are the primary burden. Negative symptoms mild. Antipsychotics partially effective. Medication-resistant hallucinations most responsive to temporoparietal TMS/tDCS.",
                key_features=["Persistent auditory hallucinations despite antipsychotics", "Delusions", "PANSS positive subscale dominant", "Variable insight"],
                primary_networks=[NetworkKey.DMN, NetworkKey.SN],
                secondary_networks=[NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.TMS],
                tdcs_target="Cathodal L-temporoparietal (T3/CP5) + anodal L-DLPFC (F3)",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="negative_predominant",
                label="SCZ-NEG — Negative Symptom Predominant",
                description="Flat affect, avolition, asociality, alogia, anhedonia dominate. Positive symptoms controlled. Functional impairment severe. DLPFC anodal tDCS targets negative symptoms.",
                key_features=["Flat affect", "Avolition", "Social withdrawal", "PANSS negative subscale dominant", "Antipsychotics only partially effective"],
                primary_networks=[NetworkKey.CEN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS],
                tdcs_target="Anodal L-DLPFC (F3) — CEN upregulation",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="cognitive_predominant",
                label="SCZ-COG — Cognitive Deficit Predominant",
                description="Working memory, attention, and executive function deficits dominate and drive functional disability. Target DLPFC with excitatory stimulation combined with cognitive training.",
                key_features=["Severe working memory deficit", "Poor processing speed", "Executive dysfunction", "Impaired occupational function"],
                primary_networks=[NetworkKey.CEN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.TMS],
                tdcs_target="Anodal L-DLPFC (F3) + cognitive remediation concurrent",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="panss",
                name="Positive and Negative Syndrome Scale",
                abbreviation="PANSS",
                domains=["positive_symptoms", "negative_symptoms", "general_psychopathology"],
                timing="baseline",
                evidence_pmid="3616518",
                notes="Gold standard schizophrenia severity measure. 30 items, 3 subscales: Positive (7 items), Negative (7 items), General (16 items). MCID = 15% reduction. Administer at baseline, 4 weeks, 8 weeks.",
            ),
            AssessmentTool(
                scale_key="bprs",
                name="Brief Psychiatric Rating Scale",
                abbreviation="BPRS",
                domains=["psychosis", "depression", "anxiety", "disorganization"],
                timing="baseline",
                evidence_pmid="5910697",
                notes="18-item global psychiatric symptom severity. Useful for monitoring session-by-session symptom changes. MCID = 20% reduction.",
            ),
            AssessmentTool(
                scale_key="cgi_sch",
                name="Clinical Global Impression — Schizophrenia",
                abbreviation="CGI-SCH",
                domains=["positive_symptoms", "negative_symptoms", "depressive_symptoms", "cognitive_symptoms", "overall_severity"],
                timing="baseline",
                evidence_pmid="15741537",
                notes="Clinician-rated global impression scale. 5 subscales. Useful for rapid clinical monitoring.",
            ),
            AssessmentTool(
                scale_key="sans",
                name="Scale for the Assessment of Negative Symptoms",
                abbreviation="SANS",
                domains=["affective_flattening", "alogia", "avolition", "anhedonia", "attention"],
                timing="baseline",
                evidence_pmid=None,
                notes="25-item negative symptom severity scale. Critical for negative symptom predominant phenotype monitoring.",
            ),
        ],

        baseline_measures=[
            "PANSS (Positive and Negative Syndrome Scale — primary severity measure)",
            "CGI-SCH (global impression — clinician-rated)",
            "SANS (for negative symptom predominant phenotype)",
            "PHQ-9 (depression comorbidity)",
            "SOZO PRS (mood, daily function — 0-10)",
        ],

        followup_measures=[
            "PANSS at 4-week and 8-week intervals",
            "BPRS at each session (brief monitoring)",
            "SOZO PRS at each session",
        ],

        inclusion_criteria=[
            "DSM-5 diagnosis of schizophrenia spectrum disorder confirmed by psychiatrist",
            "Clinically stable — no acute psychotic exacerbation (minimum 4 weeks stability)",
            "On stable antipsychotic medication for >=4 weeks",
            "Persistent target symptoms despite adequate antipsychotic trial (for positive symptoms protocol)",
            "Age 18-60 years",
            "Capacity to provide informed consent",
        ],

        exclusion_criteria=[
            "Acute psychotic exacerbation — CONTRAINDICATED until stabilized",
            "Clozapine use (relative exclusion — seizure risk; requires psychiatrist clearance)",
            "Active substance use disorder (confounds outcome assessment)",
            "Severe suicidal ideation requiring inpatient hospitalization",
            "History of seizures or epilepsy",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS,

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "precaution",
                "ADJUNCT TO ANTIPSYCHOTICS ONLY. Neuromodulation must not replace antipsychotic medication. Any medication changes must be communicated immediately and documented.",
                "high",
                "Clinical safety requirement — antipsychotic adjunct policy",
            ),
            make_safety(
                "contraindication",
                "Acute psychosis is a contraindication to neuromodulation. Patient must be clinically stable with psychiatrist clearance before starting.",
                "absolute",
                "Clinical safety — acute psychosis contraindication",
            ),
            make_safety(
                "monitoring",
                "Monitor for worsening positive symptoms at every session. BPRS global assessment at each session. Any increase in BPRS >=20% triggers psychiatric review before next session.",
                "high",
                "Symptom monitoring protocol for schizophrenia",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Left Temporoparietal Cortex (Wernicke's Area)", "L-TPC", "left",
                "Cathodal tDCS over left temporoparietal cortex inhibits the hyperactive "
                "language cortex generating auditory hallucinations. Brunelin et al. (2012) "
                "demonstrated cathodal tDCS over left temporoparietal + anodal L-DLPFC "
                "significantly reduced auditory hallucinations and negative symptoms. "
                "Mondino et al. (2015) confirmed in refractory schizophrenia. OFF-LABEL.",
                "C-SCZ-TPC — Auditory Cortex Inhibition",
                EvidenceLevel.MEDIUM, off_label=True,
                eeg_canonical=["T3", "CP5"],
            ),
            make_tdcs_target(
                "Left Dorsolateral Prefrontal Cortex", "L-DLPFC", "left",
                "Anodal tDCS over left DLPFC upregulates hypofrontal circuits driving "
                "negative symptoms and cognitive deficits. Part of the bifrontal-temporal "
                "montage (anodal F3 + cathodal temporoparietal). Brunelin et al. (2012) "
                "demonstrated negative symptom improvement with this montage. OFF-LABEL.",
                "C-SCZ-DLPFC — Frontal Upregulation",
                EvidenceLevel.MEDIUM, off_label=True,
                eeg_canonical=["F3"],
            ),
            StimulationTarget(
                modality=Modality.TMS,
                target_region="Left Temporal-Parietal Cortex",
                target_abbreviation="L-TPC rTMS",
                laterality="left",
                rationale="1 Hz inhibitory rTMS over left temporal-parietal cortex "
                          "reduces medication-resistant auditory hallucinations. "
                          "Hoffman et al. (2003) landmark RCT demonstrated significant "
                          "hallucination reduction vs. sham. Multiple replications. "
                          "Most evidence-based neuromodulation approach for hallucinations. OFF-LABEL.",
                protocol_label="TMS-SCZ-INHIB — 1Hz Temporal Inhibition",
                evidence_level=EvidenceLevel.HIGH,
                off_label=True,
                eeg_canonical=["T3", "CP5"],
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-SCZ-BIFRONTAL-TEMPORAL",
                label="Bifrontal-Temporal tDCS — Hallucination & Negative Symptom Protocol",
                modality=Modality.TDCS,
                target_region="L-DLPFC (anode) + L-Temporoparietal (cathode)",
                target_abbreviation="F3+T3/CP5",
                phenotype_slugs=["positive_predominant", "negative_predominant"],
                network_targets=[NetworkKey.CEN, NetworkKey.DMN, NetworkKey.SN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "T3 or CP5 (left temporoparietal cortex)",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10 sessions over 2 weeks (5 days/week)",
                    "note": "Brunelin et al. (2012) protocol — 2 sessions per day for 5 days",
                },
                rationale="The Brunelin et al. (2012) bifrontal-temporal tDCS protocol — anodal "
                          "F3 (DLPFC upregulation) + cathodal temporoparietal (auditory cortex "
                          "inhibition) — demonstrated significant reduction in hallucinations "
                          "and negative symptoms vs. sham in a double-blind RCT. "
                          "Mondino et al. (2015) replicated in refractory schizophrenia. "
                          "ADJUNCT TO ANTIPSYCHOTICS ONLY. OFF-LABEL.",
                evidence_level=EvidenceLevel.HIGH, off_label=True, session_count=10,
                notes="Psychiatrist clearance required. Stable antipsychotic regimen mandatory.",
            ),
            ProtocolEntry(
                protocol_id="TMS-SCZ-1HZ",
                label="1 Hz rTMS — Medication-Resistant Auditory Hallucinations",
                modality=Modality.TMS,
                target_region="Left Temporoparietal Cortex",
                target_abbreviation="L-TPC 1Hz",
                phenotype_slugs=["positive_predominant"],
                network_targets=[NetworkKey.DMN, NetworkKey.SN],
                parameters={
                    "frequency": "1 Hz (inhibitory)",
                    "intensity": "90% RMT",
                    "pulses_per_session": "1200 (20 min)",
                    "sessions": "10-20 sessions over 2-4 weeks",
                    "target_localization": "T3/CP5 or neuronavigation",
                },
                rationale="Hoffman et al. (2003) landmark RCT: 1 Hz inhibitory rTMS over "
                          "left temporal-parietal cortex reduced medication-resistant auditory "
                          "hallucinations significantly vs. sham. Multiple replications confirm "
                          "this as the most evidence-based TMS target for hallucinations. "
                          "ADJUNCT TO ANTIPSYCHOTICS. OFF-LABEL.",
                evidence_level=EvidenceLevel.HIGH, off_label=True, session_count=15,
                notes="For medication-resistant auditory hallucinations only. Psychiatric clearance required.",
            ),
            ProtocolEntry(
                protocol_id="C-SCZ-DLPFC-COG",
                label="L-DLPFC Anodal tDCS — Cognitive Enhancement",
                modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex",
                target_abbreviation="L-DLPFC",
                phenotype_slugs=["cognitive_predominant", "negative_predominant"],
                network_targets=[NetworkKey.CEN, NetworkKey.ATTENTION],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "Right shoulder or Fp2",
                    "intensity": "1.5-2.0 mA",
                    "duration": "20 min",
                    "sessions": "15-20 over 4 weeks",
                    "concurrent_training": "Cognitive remediation during stimulation recommended",
                },
                rationale="Anodal tDCS over left DLPFC upregulates hypofrontal circuits driving "
                          "cognitive deficits and negative symptoms. Cordes et al. (2015) "
                          "demonstrated working memory improvement. Best combined with cognitive "
                          "remediation training during stimulation. ADJUNCT TO ANTIPSYCHOTICS.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=20,
            ),
        ],

        symptom_network_mapping={
            "Auditory Hallucinations": [NetworkKey.DMN, NetworkKey.SN],
            "Delusions": [NetworkKey.DMN, NetworkKey.SN],
            "Negative Symptoms": [NetworkKey.CEN, NetworkKey.LIMBIC],
            "Cognitive Deficits": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Disorganized Thinking": [NetworkKey.DMN, NetworkKey.CEN],
        },

        symptom_modality_mapping={
            "Auditory Hallucinations": [Modality.TMS, Modality.TDCS],
            "Delusions": [Modality.TDCS, Modality.TMS],
            "Negative Symptoms": [Modality.TDCS],
            "Cognitive Deficits": [Modality.TDCS, Modality.TMS],
            "Disorganized Thinking": [Modality.TDCS],
        },

        responder_criteria=[
            ">=15% reduction in PANSS total score (MCID for schizophrenia trials)",
            ">=20% reduction in PANSS positive subscale (for hallucination/delusion protocol)",
            "Clinically meaningful improvement in CGI-SCH global severity rating",
        ],

        non_responder_pathway=(
            "For non-responders at 4-week block:\n"
            "1. Verify antipsychotic stability — medication changes confound response\n"
            "2. Switch from tDCS to TMS 1 Hz for persistent hallucinations\n"
            "3. Reassess PANSS subscales — target dominant symptom cluster\n"
            "4. Psychiatry referral for medication optimization (clozapine consideration)\n"
            "5. Cognitive remediation therapy referral for cognitive-predominant phenotype"
        ),

        evidence_summary=(
            "Schizophrenia neuromodulation: best evidence for 1 Hz rTMS and bifrontal-temporal tDCS. "
            "Hoffman et al. (2003): landmark RCT for 1 Hz rTMS reducing medication-resistant "
            "auditory hallucinations. Brunelin et al. (2012): double-blind RCT bifrontal-temporal "
            "tDCS reduced hallucinations and negative symptoms. Mondino et al. (2015) confirmed "
            "cathodal temporoparietal tDCS in refractory schizophrenia. "
            "Cognitive enhancement via DLPFC tDCS: emerging evidence. "
            "| Evidence counts: TMS=120, tDCS=50. Best modalities: TMS (1 Hz), tDCS."
        ),

        evidence_gaps=[
            "Optimal TMS target localization — T3 vs. CP5 vs. neuronavigation-guided",
            "Long-term durability beyond treatment block — maintenance protocols needed",
            "Negative symptom protocols — limited dedicated RCTs",
            "Cognitive enhancement with tDCS — need for larger controlled trials",
            "Safety and dosing with clozapine (seizure risk — relative contraindication)",
        ],

        references=[
            {
                "authors": "Brunelin J et al.",
                "year": 2012,
                "title": "Examining transcranial direct-current stimulation (tDCS) as a treatment for hallucinations in schizophrenia",
                "journal": "American Journal of Psychiatry",
                "pmid": "22948059",
                "evidence_type": "rct",
            },
            {
                "authors": "Hoffman RE et al.",
                "year": 2003,
                "title": "Transcranial magnetic stimulation of left temporoparietal cortex and medication-resistant auditory hallucinations",
                "journal": "Archives of General Psychiatry",
                "pmid": "12695316",
                "evidence_type": "rct",
            },
            {
                "authors": "Mondino M et al.",
                "year": 2015,
                "title": "Cathodal transcranial direct current stimulation over the left temporoparietal cortex decreases symptom severity in refractory schizophrenia",
                "journal": "Brain Stimulation",
                "pmid": "25498221",
                "evidence_type": "rct",
            },
            {
                "authors": "Kay SR et al.",
                "year": 1987,
                "title": "The positive and negative syndrome scale (PANSS) for schizophrenia",
                "journal": "Schizophrenia Bulletin",
                "pmid": "3616518",
                "evidence_type": "cohort_study",
            },
        ],

        overall_evidence_quality=EvidenceLevel.HIGH,

        clinical_tips=[
            "Always adjunct to antipsychotics — obtain written psychiatrist clearance before starting",
            "Acute psychosis is an absolute contraindication — minimum 4 weeks clinical stability required",
            "Brunelin bifrontal-temporal montage: 2 sessions per day for 5 days (10 total) — this intensive schedule is the published protocol",
            "Monitor BPRS at every session — any significant worsening requires psychiatric review before continuing",
            "Medication-resistant hallucinations: 1 Hz TMS has stronger evidence than tDCS — discuss with psychiatrist",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Written psychiatrist clearance mandatory before initiating any neuromodulation for schizophrenia",
            "Acute psychosis is an absolute contraindication — treatment must be deferred until clinical stability",
            "Antipsychotic medication must remain unchanged during treatment block unless psychiatrist authorizes",
        ],
    )
