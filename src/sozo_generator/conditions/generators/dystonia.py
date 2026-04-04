"""
Dystonia — Complete condition generator.

Key references:
- Albanese A et al. (2013) Phenomenology and classification of dystonia. PMID: 23630699
- Vidailhet M et al. (2005) Bilateral deep-brain stimulation of the globus pallidus in primary generalized dystonia. PMID: 15800226
- Breakefield XO et al. (2008) The pathophysiological basis of dystonias. PMID: 18426510
- Bhidayasiri R et al. (2006) Dystonia treatments and interventions. PMID: 16417588
- Contarino MF et al. (2014) GPi-DBS vs. pallidal lesioning for dystonia. PMID: 24888441
- Simpson DM et al. (2016) Practice guideline: injection of botulinum toxin for treatment of dystonia. PMID: 27164320
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


def build_dystonia_condition() -> ConditionSchema:
    """Build the complete Dystonia condition schema."""
    return ConditionSchema(
        slug="dystonia",
        display_name="Dystonia",
        icd10="G24",
        aliases=["dystonia", "cervical dystonia", "focal dystonia", "generalized dystonia"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Dystonia is a movement disorder characterized by sustained or intermittent muscle "
            "contractions causing abnormal, often repetitive movements and postures. It is the "
            "third most common movement disorder after essential tremor and Parkinson's disease. "
            "Dystonia affects approximately 16 in 100,000 people in the general population, "
            "with cervical dystonia being the most common focal form.\n\n"
            "Dystonia is classified by distribution: focal (one body region), segmental "
            "(two adjacent regions), multifocal, hemidystonia, or generalized. Cervical dystonia "
            "(torticollis) and blepharospasm are the most common focal dystonias in adults. "
            "Writer's cramp is the most prevalent task-specific focal dystonia.\n\n"
            "Treatment: Botulinum toxin injections are first-line for focal dystonia. "
            "For generalized/segmental and medication-refractory focal dystonia, "
            "GPi-DBS (globus pallidus internus deep brain stimulation) received FDA Humanitarian "
            "Device Exemption (HDE) approval in 2003 and is the most evidence-based surgical "
            "intervention. Non-invasive TMS targeting sensorimotor cortex modulates the "
            "maladaptive cortical plasticity underlying dystonia."
        ),

        pathophysiology=(
            "Dystonia pathophysiology involves abnormal basal ganglia-thalamo-cortical circuit "
            "function and maladaptive sensorimotor plasticity:\n\n"
            "(1) Basal ganglia dysfunction: Reduced inhibitory GPi/SNr output leads to "
            "disinhibition of thalamo-cortical circuits. This generates excessive, uncontrolled "
            "motor cortex activation — the neural basis of dystonic contractions. "
            "GPi-DBS works by disrupting this pathological disinhibition.\n\n"
            "(2) Maladaptive cortical plasticity: Excessive LTP-like plasticity in sensorimotor "
            "cortex leads to co-contraction of antagonist muscles. Focal dystonia is associated "
            "with cortical map expansion and representational overlap in M1 — adjacent digits "
            "lose their distinct cortical representations.\n\n"
            "(3) Sensory-motor integration deficit: Dystonia involves defective sensorimotor "
            "gating — inadequate inhibition of adjacent and antagonist muscle activation. "
            "Sensory tricks (geste antagoniste) suggest the sensory system can override "
            "dystonic contractions via top-down modulation.\n\n"
            "(4) Cerebellar contribution: Cerebellar dysfunction contributes to abnormal "
            "timing and coordination of dystonic movements — cerebellar-basal ganglia crosstalk "
            "abnormalities are increasingly recognized.\n\n"
            "(5) Genetic basis: DYT-TOR1A (DYT1) most common genetic generalized dystonia. "
            "Multiple DYT genes identified, most affecting striatal dopamine signaling or "
            "cytoskeletal function."
        ),

        core_symptoms=[
            "Sustained or intermittent involuntary muscle contractions",
            "Abnormal postures and repetitive twisting movements",
            "Task-specific dystonia triggered by specific voluntary movements (writer's cramp)",
            "Overflow — spread of dystonic contractions to adjacent muscles",
            "Sensory tricks (geste antagoniste) — tactile contact reduces dystonia temporarily",
            "Pain — particularly in cervical dystonia (60-70% report significant pain)",
        ],

        non_motor_symptoms=[
            "Anxiety and depression (25-45% in cervical dystonia — higher than in ET or PD)",
            "Social embarrassment and withdrawal",
            "Sleep disturbance (pain, abnormal postures)",
            "Fatigue from sustained muscle contractions",
        ],

        key_brain_regions=[
            "Globus Pallidus Internus (GPi)",
            "Putamen",
            "Primary Sensorimotor Cortex (M1/S1, C3/C4)",
            "Premotor and Supplementary Motor Area (SMA)",
            "Thalamus (ventral anterior/ventral lateral nuclei)",
            "Cerebellum (dentate nucleus)",
        ],

        brain_region_descriptions={
            "Globus Pallidus Internus (GPi)": "Primary DBS target for generalized and segmental dystonia. "
                "FDA HDE 2003. GPi dysfunction causes disinhibition of thalamo-cortical motor circuits. "
                "Longer pulse width (120-450 μs) required vs. Parkinson's DBS (60-90 μs) — delayed benefit.",
            "Putamen": "Part of the striatum — receives cortical motor input and projects to GPi. "
                "Putamen dysfunction in dystonia leads to abnormal indirect pathway activity.",
            "Primary Sensorimotor Cortex (M1/S1, C3/C4)": "Shows maladaptive plasticity in focal dystonia "
                "— cortical map reorganization with digit representation overlap. "
                "TMS target for sensorimotor normalization.",
            "Premotor and Supplementary Motor Area (SMA)": "SMA hyperactivation is a consistent "
                "neuroimaging finding in dystonia — contributes to co-contraction overflow.",
            "Thalamus (ventral anterior/ventral lateral nuclei)": "Relay of dystonic signals from "
                "disinhibited GPi to motor cortex. VA/VL thalamus may be secondary DBS target.",
            "Cerebellum (dentate nucleus)": "Cerebellar-basal ganglia crosstalk abnormalities in "
                "dystonia — dentate nucleus projections to thalamus contribute to dystonic patterns.",
        },

        network_profiles=[
            make_network(
                NetworkKey.SMN, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN DYSTONIA. Sensorimotor network hyperactivation drives the core "
                "symptom — excessive, uncontrolled, co-activating motor output. Maladaptive cortical "
                "plasticity (excessive LTP) in M1 generates representational overlap and overflow "
                "contractions. TMS over M1 targets this hyperplasticity.",
                primary=True, severity="severe",
                evidence_note="Breakefield et al. (2008); Albanese et al. (2013)",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "Salience network involvement in pain processing (cervical dystonia pain) and "
                "abnormal proprioceptive salience (heightened attention to sensory tricks).",
                severity="moderate",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Limbic hyperactivation: depression (25-45% in cervical dystonia) and anxiety "
                "from functional disability and social stigma of dystonic postures.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "CEN hypoactivation contributes to impaired voluntary motor inhibition — "
                "reduced ability to suppress dystonic contractions through effortful control.",
                severity="mild-moderate",
            ),
        ],

        primary_network=NetworkKey.SMN,

        fnon_rationale=(
            "In dystonia, neuromodulation targets the maladaptive sensorimotor plasticity and "
            "hyperactive motor cortex: (1) Inhibitory TMS (1 Hz or cTBS) over M1/premotor cortex "
            "to reduce cortical hyperexcitability and normalize cortical map representation; "
            "(2) Cathodal tDCS over sensorimotor cortex to reduce motor cortex excitability; "
            "(3) For generalized dystonia, GPi-DBS is the definitive treatment — neuromodulation "
            "is appropriate for focal or mild cases, or as adjunct to botulinum toxin. "
            "Sensorimotor retraining during inhibitory stimulation may reverse maladaptive plasticity."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="focal_cervical",
                label="DYT-CERV — Cervical Dystonia (Torticollis)",
                description="Most common adult focal dystonia. Abnormal head and neck posture from involuntary sternocleidomastoid and other neck muscle contractions. Pain (60-70%). Botulinum toxin is first-line; TMS adjunctive.",
                key_features=["Abnormal head position", "Neck pain (60-70%)", "Sensory trick effective", "Botulinum toxin responsive", "TWSTRS scale"],
                primary_networks=[NetworkKey.SMN, NetworkKey.SN],
                secondary_networks=[NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TMS, Modality.TDCS],
                tdcs_target="Contralateral sensorimotor cortex cathodal",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="focal_hand",
                label="DYT-HAND — Focal Hand Dystonia (Writer's Cramp)",
                description="Task-specific dystonia triggered by writing or fine motor tasks. Cortical map reorganization with digit overlap. Most amenable to sensorimotor retraining combined with inhibitory TMS.",
                key_features=["Writing-triggered dystonia", "Normal at rest", "Cortical map reorganization", "Motor retraining responsive"],
                primary_networks=[NetworkKey.SMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.SN],
                preferred_modalities=[Modality.TMS, Modality.TDCS],
                tdcs_target="Contralateral M1 cathodal (C3 for right hand)",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="segmental",
                label="DYT-SEG — Segmental Dystonia",
                description="Dystonia affecting two or more adjacent body regions. More severe functional impact. Combination of botulinum toxin for accessible regions and systemic or DBS approach for the remainder.",
                key_features=["Multiple body regions", "More severe disability", "Botulinum partially effective", "DBS consideration"],
                primary_networks=[NetworkKey.SMN],
                secondary_networks=[NetworkKey.LIMBIC, NetworkKey.CEN],
                preferred_modalities=[Modality.TMS, Modality.TDCS],
                tdcs_target="Bilateral sensorimotor cortex cathodal",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="generalized",
                label="DYT-GEN — Generalized Dystonia",
                description="Dystonia involving trunk and limbs (generalized). Often genetic (DYT1/TOR1A). GPi-DBS is gold standard for medication-refractory generalized dystonia. Neuromodulation adjunctive.",
                key_features=["Trunk and limb involvement", "Often early-onset", "Genetic (DYT1 in 30%)", "GPi-DBS gold standard"],
                primary_networks=[NetworkKey.SMN],
                secondary_networks=[NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TMS],
                tdcs_target="Bilateral sensorimotor cortex (adjunct to DBS management)",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="twstrs",
                name="Toronto Western Spasmodic Torticollis Rating Scale",
                abbreviation="TWSTRS",
                domains=["severity", "disability", "pain"],
                timing="baseline",
                evidence_pmid="1865271",
                notes="Gold standard for cervical dystonia. 3 subscales: severity (35 points), disability (30 points), pain (20 points). Total 85 points. MCID = 20% total score reduction. Administer at baseline and each 4-week interval.",
            ),
            AssessmentTool(
                scale_key="bfm_drs",
                name="Burke-Fahn-Marsden Dystonia Rating Scale",
                abbreviation="BFM-DRS",
                domains=["movement_scale", "disability_scale"],
                timing="baseline",
                evidence_pmid="3431034",
                notes="Primary outcome for generalized dystonia trials and GPi-DBS studies. Movement scale (0-120) + disability scale (0-30). Standard outcome for DBS dystonia trials.",
            ),
            AssessmentTool(
                scale_key="aims",
                name="Abnormal Involuntary Movement Scale",
                abbreviation="AIMS",
                domains=["orofacial_movements", "extremity_movements", "trunk_movements", "global_severity"],
                timing="baseline",
                evidence_pmid=None,
                notes="Developed for tardive dyskinesia; used in dystonia assessment. Useful for screening abnormal movements in antipsychotic-treated patients (tardive dystonia).",
            ),
        ],

        baseline_measures=[
            "TWSTRS (cervical dystonia — primary outcome for cervical phenotype)",
            "BFM-DRS (generalized/segmental dystonia)",
            "Video movement assessment (standardized posture and voluntary movement tasks)",
            "PHQ-9 and GAD-7 (mood comorbidity — 25-45% in cervical dystonia)",
            "SOZO PRS (pain, posture, daily function — 0-10)",
        ],

        followup_measures=[
            "TWSTRS or BFM-DRS at 4-week and 8-week intervals",
            "Video assessment at 4 weeks",
            "SOZO PRS at each session",
        ],

        inclusion_criteria=[
            "Confirmed dystonia diagnosis by neurologist/movement disorder specialist",
            "Focal, segmental, or multifocal dystonia — adequate for non-invasive neuromodulation",
            "Inadequate response or partial response to botulinum toxin and/or oral medications",
            "Age 18-75 years",
            "Medically stable",
        ],

        exclusion_criteria=[
            "Secondary dystonia from structural brain lesion (stroke, tumor, Wilson's disease) — requires underlying cause treatment",
            "Acute exacerbation requiring emergency intervention",
            "Tardive dystonia — antipsychotic medication adjustment required first",
            "DBS in situ (safety concern with TMS)",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS,

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "precaution",
                "GPi-DBS is the definitive treatment for generalized/segmental dystonia — patients with severe generalized dystonia should be referred to DBS-capable neurosurgery center. Neuromodulation alone is insufficient for severe cases.",
                "high",
                "DBS referral pathway for generalized dystonia",
            ),
            make_safety(
                "precaution",
                "Botulinum toxin injection and TMS are synergistic for focal dystonia — botulinum toxin should not be discontinued during neuromodulation course. Coordinate with injecting physician on timing.",
                "moderate",
                "Botulinum toxin — TMS coordination",
            ),
            make_safety(
                "monitoring",
                "GPi-DBS note: if patient has GPi-DBS in situ, TMS is CONTRAINDICATED. tDCS safety near DBS electrodes requires device-specific manufacturer guidance.",
                "high",
                "DBS in situ — TMS contraindication",
            ),
        ],

        stimulation_targets=[
            StimulationTarget(
                modality=Modality.TMS,
                target_region="Primary Motor Cortex / Premotor Cortex",
                target_abbreviation="M1/PMC",
                laterality="bilateral",
                rationale="Inhibitory TMS (1 Hz rTMS or cTBS) over sensorimotor cortex reduces "
                          "maladaptive cortical hyperexcitability and aims to normalize cortical "
                          "motor maps in focal dystonia. Multiple studies show short-term improvement "
                          "in task-specific dystonia. Combined with sensorimotor retraining. OFF-LABEL.",
                protocol_label="TMS-DYT-M1 — Sensorimotor Cortex Inhibition",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=True,
                eeg_canonical=["C3", "C4"],
            ),
            make_tdcs_target(
                "Primary Sensorimotor Cortex", "M1/S1", "bilateral",
                "Cathodal tDCS over sensorimotor cortex reduces motor cortex excitability "
                "and may normalize dystonic cortical plasticity. Evidence is preliminary but "
                "positive pilot data exist for focal hand dystonia. Cathodal placement over "
                "C3/C4 (contralateral to affected hand). OFF-LABEL.",
                "C-DYT-SMC — Sensorimotor Cortex Inhibition",
                EvidenceLevel.LOW, off_label=True,
                eeg_canonical=["C3", "C4"],
            ),
            make_tdcs_target(
                "Premotor Cortex", "PMC", "bilateral",
                "Premotor cortex anodal or cathodal tDCS modulates premotor-motor connectivity "
                "in dystonia. SMA/PMC hyperactivation in dystonia is a consistent neuroimaging "
                "finding. Investigational target. OFF-LABEL.",
                "C-DYT-PMC — Premotor Modulation",
                EvidenceLevel.LOW, off_label=True,
                eeg_canonical=["FC3", "FC4"],
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="TMS-DYT-INHIB",
                label="Inhibitory TMS — Sensorimotor Cortex",
                modality=Modality.TMS,
                target_region="Contralateral Primary Motor Cortex",
                target_abbreviation="M1 inhibitory",
                phenotype_slugs=["focal_hand", "focal_cervical"],
                network_targets=[NetworkKey.SMN],
                parameters={
                    "frequency": "1 Hz or cTBS (continuous theta-burst stimulation)",
                    "intensity": "90% RMT",
                    "pulses_per_session": "900-1200 (1 Hz) or 600 (cTBS)",
                    "sessions": "10-15 over 3 weeks",
                    "target_localization": "C3 or C4 (contralateral M1) or neuronavigation",
                    "concurrent_training": "Sensorimotor retraining during/after stimulation recommended",
                },
                rationale="Inhibitory TMS over contralateral M1 reduces maladaptive cortical "
                          "hyperexcitability underlying focal dystonia. Multiple studies demonstrate "
                          "short-term improvement in focal hand dystonia and cervical dystonia. "
                          "Combined with sensorimotor retraining for additive plasticity reversal. "
                          "ADJUNCT to botulinum toxin for focal dystonia. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=12,
            ),
            ProtocolEntry(
                protocol_id="C-DYT-SMC-CATHODAL",
                label="Sensorimotor Cortex Cathodal tDCS — Excitability Reduction",
                modality=Modality.TDCS,
                target_region="Contralateral Primary Sensorimotor Cortex",
                target_abbreviation="M1/S1 cathodal",
                phenotype_slugs=["focal_hand", "focal_cervical", "segmental"],
                network_targets=[NetworkKey.SMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "cathode": "C3 or C4 (contralateral sensorimotor cortex)",
                    "anode": "Contralateral shoulder or Fp2",
                    "intensity": "1.5-2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15 over 3 weeks",
                    "concurrent_training": "Motor retraining tasks during stimulation",
                },
                rationale="Cathodal tDCS over contralateral sensorimotor cortex reduces cortical "
                          "excitability and may normalize maladaptive plasticity in focal dystonia. "
                          "Pilot data support tDCS for focal hand dystonia. "
                          "ADJUNCT to botulinum toxin. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=12,
            ),
            ProtocolEntry(
                protocol_id="C-DYT-BILATERAL-SMC",
                label="Bilateral Sensorimotor tDCS — Segmental/Generalized Adjunct",
                modality=Modality.TDCS,
                target_region="Bilateral Sensorimotor Cortex",
                target_abbreviation="Bilateral M1/S1",
                phenotype_slugs=["segmental", "generalized"],
                network_targets=[NetworkKey.SMN, NetworkKey.CEN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "cathode": "C3 and C4 (bilateral sensorimotor — requires dual-channel device)",
                    "anode": "Bilateral shoulders",
                    "intensity": "1.5 mA bilateral",
                    "duration": "20 min",
                    "sessions": "15-20 over 4-5 weeks",
                    "note": "Adjunct to oral medications; GPi-DBS referral should be discussed",
                },
                rationale="Bilateral sensorimotor cathodal tDCS addresses the bilateral motor cortex "
                          "hyperexcitability in segmental/generalized dystonia. Investigational. "
                          "GPi-DBS referral is the primary recommendation for generalized dystonia. "
                          "tDCS as bridge or adjunct only. OFF-LABEL.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=15,
                notes="GPi-DBS referral required for generalized dystonia. tDCS is investigational adjunct only.",
            ),
        ],

        symptom_network_mapping={
            "Involuntary Contractions": [NetworkKey.SMN],
            "Abnormal Postures": [NetworkKey.SMN, NetworkKey.CEN],
            "Pain (Cervical Dystonia)": [NetworkKey.SN, NetworkKey.SMN],
            "Task-Specific Triggering": [NetworkKey.SMN, NetworkKey.CEN],
            "Depression/Anxiety": [NetworkKey.LIMBIC],
        },

        symptom_modality_mapping={
            "Involuntary Contractions": [Modality.TMS, Modality.TDCS],
            "Abnormal Postures": [Modality.TMS, Modality.TDCS],
            "Pain (Cervical Dystonia)": [Modality.TDCS],
            "Task-Specific Triggering": [Modality.TMS, Modality.TDCS],
        },

        responder_criteria=[
            ">=20% reduction in TWSTRS total score (for cervical dystonia phenotype)",
            ">=20% reduction in BFM-DRS (for generalized/segmental phenotype)",
            "Clinically meaningful improvement in patient-reported daily function",
        ],

        non_responder_pathway=(
            "For non-responders at 4-week block:\n"
            "1. Reassess botulinum toxin dosing and injection technique — optimize before neuromodulation repeat\n"
            "2. Neurologist review — consider oral medications (trihexyphenidyl, clonazepam) adjunct\n"
            "3. GPi-DBS referral for generalized/segmental or severe focal dystonia refractory to other treatments\n"
            "4. Sensorimotor retraining program referral — dystonia-specific occupational/physiotherapy\n"
            "5. Consider pallidotomy or thalamotomy if DBS not feasible"
        ),

        evidence_summary=(
            "Dystonia neuromodulation: GPi-DBS is FDA HDE 2003 (gold standard for generalized/segmental). "
            "Vidailhet et al. (2005) landmark RCT — GPi-DBS 50% BFM-DRS reduction. "
            "Non-invasive TMS: inhibitory rTMS over M1/premotor cortex shows short-term improvement "
            "in focal dystonia in multiple small studies. tDCS: pilot data only. "
            "Overall non-invasive evidence is limited — primarily small, uncontrolled studies. "
            "| Evidence counts: TMS=60, tDCS=15. Best modalities: TMS, tDCS."
        ),

        evidence_gaps=[
            "Sham-controlled RCTs for TMS in focal dystonia",
            "Optimal TMS parameters — 1 Hz vs. cTBS vs. premotor cortex target",
            "tDCS for dystonia — larger controlled studies needed",
            "Long-term benefit of non-invasive approaches — do they restore cortical maps?",
            "Combination neuromodulation + sensorimotor retraining — synergy protocols",
        ],

        references=[
            {
                "authors": "Vidailhet M et al.",
                "year": 2005,
                "title": "Bilateral deep-brain stimulation of the globus pallidus in primary generalized dystonia",
                "journal": "New England Journal of Medicine",
                "pmid": "15800226",
                "evidence_type": "rct",
            },
            {
                "authors": "Albanese A et al.",
                "year": 2013,
                "title": "Phenomenology and classification of dystonia",
                "journal": "Movement Disorders",
                "pmid": "23630699",
                "evidence_type": "consensus_statement",
            },
            {
                "authors": "Breakefield XO et al.",
                "year": 2008,
                "title": "The pathophysiological basis of dystonias",
                "journal": "Nature Reviews Neuroscience",
                "pmid": "18426510",
                "evidence_type": "narrative_review",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        clinical_tips=[
            "Always confirm botulinum toxin regimen is optimized before starting TMS — they are synergistic, not alternatives",
            "Generalized dystonia: GPi-DBS referral should be discussed with every patient before prolonged neuromodulation trials",
            "For focal hand dystonia: combine TMS with dystonia-specific sensorimotor retraining — task-based motor learning reverses maladaptive plasticity",
            "DBS in situ: TMS is CONTRAINDICATED — verify absence of DBS at intake",
            "Cervical dystonia: pain component often drives distress; address with tDCS + botulinum toxin combination",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Movement disorder specialist confirmation of dystonia diagnosis required",
            "GPi-DBS referral pathway must be discussed with generalized/segmental dystonia patients",
            "TMS is contraindicated if DBS in situ — verify at intake",
        ],
    )
