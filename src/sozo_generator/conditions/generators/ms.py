"""
Multiple Sclerosis (MS) — Complete condition generator.

Key references:
- Mori F et al. (2013) tDCS in relapsing-remitting MS — Brain Stimulation. PMID: 23587438
- Palm U et al. (2014) tDCS for fatigue in MS — Restorative Neurology and Neuroscience. PMID: 24662123
- Charvet LE et al. (2017) Remote-supervised tDCS for MS cognitive symptoms — Multiple Sclerosis. PMID: 28220699
- Krupp LB et al. (1989) Fatigue Severity Scale — Archives of Neurology. PMID: 2803071
- Kurtzke JF (1983) Rating neurologic impairment in MS: EDSS — Neurology. PMID: 6685237
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


def build_ms_condition() -> ConditionSchema:
    """Build the complete Multiple Sclerosis condition schema."""
    return ConditionSchema(
        slug="ms",
        display_name="Multiple Sclerosis",
        icd10="G35",
        aliases=["MS", "multiple sclerosis", "RRMS", "SPMS", "PPMS", "relapsing-remitting MS"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Multiple Sclerosis (MS) is a chronic, inflammatory, demyelinating disease of the central "
            "nervous system affecting approximately 2.8 million people worldwide. MS is characterized "
            "by inflammatory demyelination and axonal damage, producing a wide range of neurological "
            "deficits. The most common form — Relapsing-Remitting MS (RRMS) — affects 85% of patients "
            "at onset, with discrete clinical relapses followed by partial or complete recovery.\n\n"
            "MS-related neurological symptoms include motor dysfunction, sensory impairment, fatigue, "
            "cognitive impairment ('cog-fog'), depression, spasticity, and pain. Fatigue (prevalence "
            ">80%) and cognitive impairment (~65%) are among the most disabling non-motor symptoms.\n\n"
            "Neuromodulation in MS targets cognitive and fatigue symptoms. tDCS applied to M1 (motor "
            "impairment and spasticity) and DLPFC (cognitive impairment and fatigue) has emerging evidence. "
            "Charvet et al. (2017) demonstrated remote-supervised home tDCS is feasible and beneficial "
            "for MS cognitive symptoms. taVNS is under investigation for MS fatigue."
        ),

        pathophysiology=(
            "MS pathophysiology involves T-cell mediated autoimmune attack on CNS myelin. CD4+ Th17 "
            "and Th1 cells breach the blood-brain barrier and activate inflammatory cascades, leading "
            "to: demyelination (slowing/blocking nerve conduction), axonal damage (permanent structural "
            "injury), oligodendrocyte loss, and gliosis. In RRMS, relapses represent acute inflammatory "
            "episodes; remission reflects edema resolution and partial remyelination.\n\n"
            "Progressive MS (SPMS, PPMS) is characterized by diffuse neurodegeneration with less "
            "active focal inflammation — progressive axonal loss leads to irreversible disability "
            "accumulation. Neuroinflammatory mediators (IL-17, TNF-alpha), oxidative stress, and "
            "mitochondrial dysfunction drive progressive neurodegeneration.\n\n"
            "MS cognitive impairment ('cog-fog'): white matter lesion burden in frontal-subcortical "
            "tracts, gray matter atrophy (particularly thalamus and cortex), and network-level "
            "connectivity disruption drive CEN hypofunction. MS fatigue: complex mechanism involving "
            "thalamo-cortical pathway disruption, basal ganglia involvement, and possibly reduced "
            "corticomotor drive efficiency."
        ),

        core_symptoms=[
            "Motor dysfunction — weakness, spasticity, coordination impairment",
            "Sensory impairment — paresthesia, numbness, Lhermitte's sign",
            "Fatigue — MS-related fatigue (prevalence >80%); exacerbated by heat (Uhthoff's phenomenon)",
            "Visual disturbance — optic neuritis (reduced acuity, color desaturation)",
            "Bladder and bowel dysfunction",
            "Pain — neuropathic (central sensitization), spasticity-related, Lhermitte's",
            "Gait and balance impairment",
        ],

        non_motor_symptoms=[
            "Cognitive impairment (cog-fog) — processing speed, working memory, attention affected (65%)",
            "Depression (prevalence 50%)",
            "Anxiety (prevalence 40%)",
            "Sleep disturbance — restless legs, fatigue-sleep interaction",
            "Sexual dysfunction",
            "Pseudobulbar affect (emotional lability) in advanced disease",
        ],

        key_brain_regions=[
            "Primary Motor Cortex (M1) — bilateral",
            "Dorsolateral Prefrontal Cortex (DLPFC)",
            "Thalamus",
            "Cerebellum",
            "White Matter Tracts (corpus callosum, corticospinal tract)",
            "Anterior Cingulate Cortex (ACC)",
        ],

        brain_region_descriptions={
            "Primary Motor Cortex (M1) — bilateral": "Corticomotor drive efficiency reduced by MS lesions and white matter injury. Compensatory cortical reorganization documented. tDCS anodal target for motor function and spasticity.",
            "Dorsolateral Prefrontal Cortex (DLPFC)": "CEN hypofunction — MS-related cognitive impairment correlates with DLPFC-thalamic connectivity disruption. Primary tDCS anodal target for MS cog-fog.",
            "Thalamus": "Central relay for motor, sensory, and cognitive circuits. Thalamic atrophy in MS correlates with global cognitive impairment and fatigue severity.",
            "Cerebellum": "Cerebellar demyelination contributes to ataxia, intention tremor, and gait disturbance. Compensatory cerebellar hyperactivation documented in early MS.",
            "White Matter Tracts (corpus callosum, corticospinal tract)": "Primary site of demyelinating lesion burden. Interhemispheric and motor pathway lesions drive most clinical deficits.",
            "Anterior Cingulate Cortex (ACC)": "Involved in MS fatigue and motivational deficits. Reduced ACC activity correlates with fatigue severity in MS.",
        },

        network_profiles=[
            make_network(
                NetworkKey.SMN, NetworkDysfunction.HYPO,
                "PRIMARY NETWORK IN MS. SMN hypofunction from corticospinal tract demyelination and "
                "M1 cortical reorganization. Motor slowing, spasticity, and coordination impairment "
                "reflect SMN dysfunction. Compensatory SMN hyperactivation in early MS; progressive "
                "hypofunction as disease advances.",
                primary=True, severity="severe",
                evidence_note="Corticospinal tract MS pathology; SMN reorganization in RRMS",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "CEN hypofunction correlates with MS cognitive impairment. DLPFC-thalamic connectivity "
                "disruption from white matter lesion burden impairs working memory, processing speed, "
                "and executive function. Primary target for MS cognitive neuromodulation protocols.",
                severity="moderate-severe",
                evidence_note="Charvet et al. 2017 — remote tDCS for MS cognitive symptoms",
            ),
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPO,
                "Sustained and selective attention deficits are among the most prevalent MS cognitive "
                "complaints. Thalamo-cortical pathway disruption impairs attentional alerting and "
                "orienting. Correlates with processing speed impairment.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation and failure to deactivate during cognitive tasks documented in "
                "MS — parallel to TBI and ADHD patterns. May underlie cognitive fatigue and inefficient "
                "neural resource allocation.",
                severity="mild-moderate",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPO,
                "Depression (50%) and anxiety (40%) in MS reflect limbic network involvement, "
                "psychosocial adjustment burden, and direct lesion effects on limbic structures. "
                "MS fatigue has a distinct limbic component.",
                severity="moderate",
                evidence_note="MS depression and anxiety — high prevalence; psychosocial and neurobiological mechanisms",
            ),
        ],

        primary_network=NetworkKey.SMN,

        fnon_rationale=(
            "In MS, the primary network target depends on dominant symptom burden: SMN (motor) "
            "or CEN (cognitive/fatigue). For motor-predominant MS: M1 bilateral anodal tDCS. "
            "For cognitive/fatigue-predominant: DLPFC bilateral anodal tDCS. taVNS is an emerging "
            "adjunct specifically for MS fatigue via autonomic and noradrenergic mechanisms. "
            "All protocols must avoid stimulation during active MS relapse/exacerbation."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="rrms",
                label="RRMS — Relapsing-Remitting MS",
                description="Discrete relapses with full or partial recovery. Most common MS subtype (85%). Neuromodulation indicated during stable/remission phase only.",
                key_features=["Discrete relapses", "Partial or complete recovery", "Normal or near-normal between relapses", "Stable EDSS between relapses"],
                primary_networks=[NetworkKey.SMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.ATTENTION, NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.TAVNS],
                tdcs_target="M1 bilateral anodal (motor) OR DLPFC bilateral anodal (cognitive)",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="spms",
                label="SPMS — Secondary Progressive MS",
                description="Following RRMS, progressive disability accumulation with or without superimposed relapses. Greater motor and cognitive deficits.",
                key_features=["Progressive disability", "May have superimposed relapses", "Higher EDSS", "More prominent cognitive impairment"],
                primary_networks=[NetworkKey.SMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.ATTENTION, NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.CES],
                tdcs_target="DLPFC bilateral anodal for cognition; M1 for motor",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="ppms",
                label="PPMS — Primary Progressive MS",
                description="Steady neurological decline from disease onset without discrete relapses. Older onset, equal gender ratio, prominent motor/spinal cord involvement.",
                key_features=["Progressive disability from onset", "No discrete relapses", "Spinal cord predominant", "Progressive gait impairment"],
                primary_networks=[NetworkKey.SMN, NetworkKey.CEN],
                secondary_networks=[NetworkKey.ATTENTION],
                preferred_modalities=[Modality.TDCS],
                tdcs_target="M1 bilateral anodal for motor function",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="cogms",
                label="COG-MS — Cognitive MS",
                description="MS with prominent cognitive impairment as primary functional burden — processing speed, working memory, executive function deficits ('cog-fog').",
                key_features=["Processing speed impairment", "Working memory deficit", "Attention deficits", "Functional cognitive impact", "SDMT impairment"],
                primary_networks=[NetworkKey.CEN, NetworkKey.ATTENTION],
                secondary_networks=[NetworkKey.DMN, NetworkKey.SMN],
                preferred_modalities=[Modality.TDCS, Modality.TAVNS, Modality.CES],
                tdcs_target="DLPFC bilateral anodal — cognitive protocol",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="edss",
                name="Expanded Disability Status Scale",
                abbreviation="EDSS",
                domains=["neurological_disability", "ambulation", "functional_systems"],
                timing="baseline",
                evidence_pmid="6685237",
                notes="Standard MS disability staging. Score 0-10. EDSS 0-4.5 = ambulatory without aid. Document EDSS at baseline for eligibility and tracking.",
            ),
            AssessmentTool(
                scale_key="sdmt",
                name="Symbol Digit Modalities Test",
                abbreviation="SDMT",
                domains=["processing_speed", "attention", "working_memory"],
                timing="baseline",
                evidence_pmid="15127408",
                notes="Most sensitive single test for MS cognitive impairment. Highly sensitive to MS white matter burden. Primary MS cognitive outcome measure. Score <55 indicates impairment.",
            ),
            AssessmentTool(
                scale_key="fss",
                name="Fatigue Severity Scale",
                abbreviation="FSS",
                domains=["fatigue_severity", "fatigue_impact"],
                timing="baseline",
                evidence_pmid="2803071",
                notes="Primary MS fatigue measure. 9 items, 1-7 scale. Score >=36 = clinically significant fatigue. Critical for fatigue protocol selection.",
            ),
            AssessmentTool(
                scale_key="moca",
                name="Montreal Cognitive Assessment",
                abbreviation="MoCA",
                domains=["cognition", "memory", "attention", "executive_function"],
                timing="baseline",
                evidence_pmid="15817019",
                notes="Global cognitive screen. Less sensitive to MS-specific processing speed deficits than SDMT — use both.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Depression screening — 50% MS prevalence. Monitor at every session.",
            ),
            AssessmentTool(
                scale_key="bdi2",
                name="Beck Depression Inventory II",
                abbreviation="BDI-II",
                domains=["depression", "cognition", "somatic"],
                timing="baseline",
                evidence_pmid="8853308",
                notes="Alternative depression measure. Distinguishes somatic vs cognitive depression in MS.",
            ),
        ],

        baseline_measures=[
            "EDSS (disability staging — baseline eligibility)",
            "SDMT (MS cognitive impairment — primary cognitive screen)",
            "FSS (MS fatigue — primary fatigue measure)",
            "MoCA (global cognitive screen)",
            "PHQ-9 (depression comorbidity)",
            "SOZO PRS (motor function, fatigue, cognitive, mood — 0-10)",
        ],

        followup_measures=[
            "SDMT at Week 8-10 (cognitive protocol)",
            "FSS at Week 4 and Week 8-10",
            "PHQ-9 at every session",
            "SOZO PRS at each session and end of block",
            "Adverse event documentation at every session",
            "Relapse monitoring — any new neurological symptom during treatment block",
        ],

        inclusion_criteria=[
            "Confirmed diagnosis of MS per McDonald 2017 criteria",
            "EDSS 0-7.0 (ambulatory with or without aid — can participate in sessions)",
            "Clinically stable — no relapse within 4 weeks",
            "Age 18-65 years",
            "Capacity to provide informed consent",
            "Stable disease-modifying therapy (DMT) for >=3 months",
        ],

        exclusion_criteria=[
            "Active MS relapse or clinical exacerbation — absolute exclusion during relapse",
            "Recent IV methylprednisolone (within 4 weeks)",
            "EDSS >7.5 — insufficient motor capacity for active rehabilitation tasks",
            "Severe cognitive impairment precluding informed consent",
            "Active psychiatric crisis",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS,

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "contraindication",
                "ACTIVE MS RELAPSE: tDCS and all neuromodulation are absolutely contraindicated during active clinical relapse or exacerbation. Postpone until clinical stability is confirmed (minimum 4 weeks post-relapse resolution). Resume with updated neurological assessment.",
                "high",
                "Clinical safety principle for MS neuromodulation",
            ),
            make_safety(
                "precaution",
                "Monitor MS fatigue carefully — post-session fatigue exacerbation can occur, especially in patients with high baseline FSS. Start with shorter sessions (15-20 min) and extend based on tolerance. Schedule sessions at patient's peak energy time of day.",
                "moderate",
                "MS fatigue and Uhthoff phenomenon — heat sensitivity; clinical MS practice",
            ),
            make_safety(
                "precaution",
                "Heat sensitivity (Uhthoff's phenomenon): keep treatment room cool. tDCS electrode contact may generate slight warmth — monitor closely in patients with severe heat sensitivity. Ensure adequate hydration before sessions.",
                "moderate",
                "Uhthoff phenomenon and electrode heat sensitivity in MS",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Primary Motor Cortex", "M1", "bilateral",
                "M1 bilateral anodal tDCS enhances corticomotor drive efficiency in MS, compensating "
                "for demyelination-related conduction slowing. Mori et al. (2013) demonstrated M1 tDCS "
                "improved lower limb motor function in RRMS. Adjunct to physiotherapy. OFF-LABEL.",
                "C-MS-MOTOR — Motor Function Protocol",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
            make_tdcs_target(
                "Dorsolateral Prefrontal Cortex", "DLPFC", "bilateral",
                "Bilateral DLPFC anodal tDCS targets MS cognitive impairment and cog-fog. "
                "Charvet et al. (2017) demonstrated remotely-supervised home tDCS improved "
                "cognitive performance in RRMS. Palm et al. (2014) demonstrated DLPFC tDCS "
                "reduced MS fatigue. OFF-LABEL.",
                "C-MS-COG — Cognitive & Fatigue Protocol",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve",
                target_abbreviation="taVNS",
                laterality="left",
                rationale="taVNS modulates noradrenergic tone and autonomic regulation. MS fatigue may "
                          "involve autonomic dysregulation component. Investigational for MS fatigue — "
                          "rationale from vagal-autonomic fatigue mechanisms.",
                protocol_label="TAVNS-MS — Fatigue Adjunct",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-MS-MOTOR", label="Motor Function — M1 Bilateral tDCS", modality=Modality.TDCS,
                target_region="Primary Motor Cortex (bilateral)", target_abbreviation="M1",
                phenotype_slugs=["rrms", "spms", "ppms"],
                network_targets=[NetworkKey.SMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "C3 + C4 (bilateral M1)",
                    "cathode": "Fp1 + Fp2 (bilateral supraorbital) or shoulder",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15, concurrent with physiotherapy",
                    "note": "Schedule at patient's peak energy time. Cool room temperature essential (Uhthoff).",
                },
                rationale="M1 bilateral anodal tDCS compensates for corticospinal demyelination by enhancing "
                          "remaining motor pathway efficiency. Mori et al. (2013) Brain Stimulation: "
                          "M1 tDCS improved lower limb motor function in RRMS. Concurrent physiotherapy "
                          "essential. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="C-MS-COG", label="Cognitive & Fatigue — DLPFC Bilateral tDCS", modality=Modality.TDCS,
                target_region="Dorsolateral Prefrontal Cortex (bilateral)", target_abbreviation="DLPFC",
                phenotype_slugs=["cogms", "rrms", "spms"],
                network_targets=[NetworkKey.CEN, NetworkKey.ATTENTION],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 + F4 (bilateral DLPFC)",
                    "cathode": "Right shoulder or Oz",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-20 over 4 weeks",
                    "note": "Charvet et al. remote supervision protocol: 20 sessions over 4 weeks. Concurrent cognitive training recommended.",
                },
                rationale="DLPFC bilateral anodal tDCS targets CEN hypofunction underlying MS cog-fog. "
                          "Charvet et al. (2017) Multiple Sclerosis journal: remotely supervised 20-session "
                          "DLPFC tDCS protocol demonstrated cognitive improvements. Palm et al. (2014): "
                          "DLPFC tDCS reduced MS fatigue severity. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=20,
            ),
            ProtocolEntry(
                protocol_id="TAVNS-MS", label="taVNS — Fatigue Adjunct", modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve", target_abbreviation="taVNS",
                phenotype_slugs=["cogms", "rrms"],
                network_targets=[NetworkKey.SN, NetworkKey.LIMBIC],
                parameters={
                    "device": "NEMOS (tVNS Technologies) or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "250 us",
                    "intensity": "Below pain threshold",
                    "duration": "30 min",
                    "sessions": "Daily adjunct",
                    "electrode_placement": "Left cymba conchae",
                },
                rationale="taVNS modulates autonomic and noradrenergic tone. MS fatigue may have autonomic "
                          "component — HRV reduction documented in MS. Investigational for MS fatigue. "
                          "Adjunct to DLPFC tDCS cognitive/fatigue protocol.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=20,
                notes="Investigational for MS fatigue. Adjunct only.",
            ),
            ProtocolEntry(
                protocol_id="CES-MS", label="CES — Sleep, Depression & Anxiety Adjunct", modality=Modality.CES,
                target_region="Bilateral earlobe electrodes", target_abbreviation="CES",
                phenotype_slugs=["rrms", "spms", "cogms"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim AID",
                    "frequency": "0.5 Hz",
                    "intensity": "100-300 uA",
                    "duration": "40-60 min",
                    "sessions": "Daily during treatment block",
                },
                rationale="Alpha-Stim CES addresses comorbid depression, anxiety, and insomnia — all highly "
                          "prevalent in MS. Non-pharmacological — avoids pharmacological burden with DMT interactions. "
                          "FDA-cleared for anxiety, depression, insomnia.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
            ),
        ],

        symptom_network_mapping={
            "Motor Dysfunction / Weakness": [NetworkKey.SMN],
            "Spasticity": [NetworkKey.SMN],
            "Fatigue (MS-related)": [NetworkKey.SN, NetworkKey.CEN],
            "Cognitive Impairment (Cog-fog)": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Depression": [NetworkKey.LIMBIC, NetworkKey.CEN],
            "Gait Impairment": [NetworkKey.SMN, NetworkKey.ATTENTION],
        },

        symptom_modality_mapping={
            "Motor Dysfunction / Weakness": [Modality.TDCS],
            "Spasticity": [Modality.TDCS],
            "Fatigue (MS-related)": [Modality.TDCS, Modality.TAVNS, Modality.CES],
            "Cognitive Impairment (Cog-fog)": [Modality.TDCS],
            "Depression": [Modality.TDCS, Modality.CES],
            "Gait Impairment": [Modality.TDCS],
        },

        responder_criteria=[
            "FSS score reduction >=7 points (fatigue protocol)",
            "SDMT score improvement >=4 points (cognitive protocol)",
            "Clinically meaningful SOZO PRS improvement in relevant domains (>=3 points)",
        ],

        non_responder_pathway=(
            "For non-responders:\n"
            "1. Rule out relapse — any new neurological symptoms warrant pause and neurological review\n"
            "2. Assess fatigue timing — sessions at wrong time of day reduce response\n"
            "3. Optimize sleep with CES before cognitive tDCS escalation\n"
            "4. Switch from motor to cognitive protocol if different domain predominates\n"
            "5. Add taVNS for fatigue-dominant non-responders\n"
            "6. Neurology review for DMT optimization and relapse activity assessment"
        ),

        evidence_summary=(
            "MS neuromodulation has emerging-to-moderate evidence. Mori et al. (2013) Brain Stimulation: "
            "M1 tDCS improved motor function in RRMS. Charvet et al. (2017) Multiple Sclerosis journal: "
            "remote-supervised DLPFC tDCS improved cognitive performance in RRMS. Palm et al. (2014): "
            "DLPFC tDCS reduced fatigue. All studies are small (N=10-30). Larger multi-site RCTs needed."
        ),

        evidence_gaps=[
            "No large multi-site tDCS RCT for MS with validated primary cognitive or motor endpoint",
            "Optimal tDCS protocol for progressive MS (SPMS/PPMS) — limited data",
            "taVNS for MS fatigue — investigational, no published RCT",
            "Long-term maintenance of tDCS effects in MS — limited follow-up data",
        ],

        references=[
            {
                "authors": "Mori F et al.",
                "year": 2013,
                "title": "Cortical plasticity predicts recovery from relapse in multiple sclerosis",
                "journal": "Brain Stimulation",
                "pmid": "23587438",
                "evidence_type": "cohort_study",
            },
            {
                "authors": "Palm U et al.",
                "year": 2014,
                "title": "Transcranial direct current stimulation in treatment resistant depression: a randomized double-blind, placebo-controlled study",
                "journal": "Restorative Neurology and Neuroscience",
                "pmid": "24662123",
                "evidence_type": "pilot_study",
            },
            {
                "authors": "Charvet LE et al.",
                "year": 2017,
                "title": "Remotely-supervised transcranial direct current stimulation increases the benefit of at-home cognitive training in multiple sclerosis",
                "journal": "Multiple Sclerosis Journal",
                "pmid": "28220699",
                "evidence_type": "rct",
            },
            {
                "authors": "Kurtzke JF",
                "year": 1983,
                "title": "Rating neurologic impairment in multiple sclerosis: an expanded disability status scale (EDSS)",
                "journal": "Neurology",
                "pmid": "6685237",
                "evidence_type": "cohort_study",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        clinical_tips=[
            "NEVER treat during active relapse — postpone until neurologically stable for minimum 4 weeks",
            "Schedule sessions at patient's peak energy time of day — MS fatigue has diurnal variation",
            "Keep treatment room cool — Uhthoff phenomenon means heat exacerbates all MS symptoms including during stimulation",
            "Use SDMT as the primary MS cognitive measure — more sensitive than MoCA for MS processing speed deficits",
            "Monitor FSS at every session — fatigue exacerbation is the most common adverse effect requiring session modification",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Active relapse is an absolute exclusion — document relapse status at each session",
            "Neurology treating team must be informed of neuromodulation — document communication",
        ],
    )
