"""
Epilepsy / Drug-Resistant Epilepsy — Complete condition generator.

Key references:
- DeGiorgio CM et al. (2013) Randomized controlled trial of trigeminal nerve stimulation for
  drug-resistant epilepsy — Neurology. PMID: 23966253
- Bauer S et al. (2016) Transcutaneous vagus nerve stimulation (taVNS) for treatment of
  drug-resistant epilepsy — Epilepsia. PMID: 26919778
- Fregni F et al. (2006) Transcranial direct current stimulation of the unaffected hemisphere
  in stroke patients — Neuroreport. PMID: 16794473
- Tergau F et al. (1999) Low-frequency repetitive transcranial magnetic stimulation improves
  intractable epilepsy — Lancet. PMID: 10376627
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
    make_network, make_tdcs_target, make_safety,
    SHARED_ABSOLUTE_CONTRAINDICATIONS, SHARED_SAFETY_NOTES, SHARED_GOVERNANCE_RULES
)

logger = logging.getLogger(__name__)


def build_epilepsy_condition() -> ConditionSchema:
    """Build the complete Epilepsy / Drug-Resistant Epilepsy condition schema."""
    return ConditionSchema(
        slug="epilepsy",
        display_name="Epilepsy / Drug-Resistant Epilepsy",
        icd10="G40.9",
        aliases=["epilepsy", "DRE", "drug-resistant epilepsy", "focal epilepsy", "TLE",
                 "temporal lobe epilepsy", "seizure disorder"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Epilepsy affects ~50 million people globally. Drug-resistant epilepsy (DRE) is defined "
            "as failure of ≥2 adequate trials of tolerated antiepileptic drugs (AEDs). Approximately "
            "30–40% of patients with epilepsy have DRE. Non-invasive neuromodulation (taVNS, cathodal "
            "tDCS, low-frequency rTMS, neurofeedback) offers adjunctive seizure reduction and "
            "quality-of-life improvement for DRE patients who are not surgical candidates or who "
            "decline surgery. taVNS is the best-evidenced non-invasive approach with multiple RCTs "
            "demonstrating 20–40% seizure frequency reduction in focal DRE."
        ),

        pathophysiology=(
            "Epilepsy involves abnormal hypersynchronous neuronal discharge arising from imbalance "
            "between excitatory (glutamate/AMPA/NMDA) and inhibitory (GABA) neurotransmission. Focal "
            "epilepsy arises from a localized epileptogenic zone (EZ); generalized epilepsy involves "
            "network-wide synchronization. Temporal lobe epilepsy (TLE) — the most common form of "
            "focal DRE — involves hippocampal sclerosis, limbic network hyperexcitability, and "
            "disrupted hippocampal-entorhinal-cortical connectivity. DRE involves multi-drug "
            "transporter upregulation (P-glycoprotein) and pharmacodynamic resistance.\n\n"
            "Neuromodulation targets: (1) taVNS activates the auricular branch of the vagus nerve "
            "→ NTS → locus coeruleus → GABAergic/noradrenergic modulation → reduced cortical "
            "excitability; (2) cathodal tDCS over epileptogenic focus reduces cortical excitability "
            "via membrane hyperpolarization; (3) 1 Hz rTMS reduces cortical excitability at "
            "epileptogenic zone; (4) neurofeedback (SCP training) directly trains inhibitory "
            "cortical control."
        ),

        core_symptoms=[
            "Recurrent unprovoked seizures (focal aware, focal impaired awareness, focal-to-bilateral tonic-clonic)",
            "Post-ictal confusion, fatigue, and transient neurological deficits",
            "Sudden unexpected death in epilepsy (SUDEP) risk in DRE",
            "Cognitive impairment (memory, attention, processing speed — especially in TLE)",
            "Depression and anxiety (comorbidity prevalence ~35–50%)",
        ],

        non_motor_symptoms=[
            "Interictal depression (most common psychiatric comorbidity — 30–50%)",
            "Anxiety disorders (25–40%)",
            "Sleep disturbance and excessive daytime sleepiness",
            "Cognitive decline (especially verbal memory in left TLE)",
            "Social stigma and reduced quality of life",
        ],

        key_brain_regions=[
            "Hippocampus (bilateral) — primary site of TLE and hippocampal sclerosis",
            "Temporal Cortex (mesial and neocortical) — TLE epileptogenic zone",
            "Prefrontal Cortex — epileptogenic zone in frontal lobe epilepsy; DLPFC for comorbid depression",
            "Insula — insular epilepsy; autonomic regulation",
            "Cerebellum — modulated by VNS for seizure control",
            "Locus Coeruleus / NTS — taVNS mechanism pathway",
        ],

        brain_region_descriptions={
            "Hippocampus (bilateral) — primary site of TLE and hippocampal sclerosis": (
                "Primary site of mesial TLE. Hippocampal sclerosis (neuron loss and gliosis in CA1, "
                "CA3, and dentate gyrus) is found in 60–70% of TLE surgical specimens. Hyperexcitability "
                "within hippocampal circuits drives ictal discharge propagation via the Papez circuit."
            ),
            "Temporal Cortex (mesial and neocortical) — TLE epileptogenic zone": (
                "Mesial temporal structures (parahippocampal gyrus, entorhinal cortex, amygdala) form the "
                "core TLE network. Neocortical temporal cortex may also be involved in neocortical TLE. "
                "Cathodal tDCS targets temporal electrodes (T3/T4) to reduce cortical excitability."
            ),
            "Prefrontal Cortex — epileptogenic zone in frontal lobe epilepsy; DLPFC for comorbid depression": (
                "Frontal lobe epilepsy (FLE) — second most common focal epilepsy — arises from prefrontal "
                "and supplementary motor cortex. DLPFC hypoactivation drives comorbid depression in DRE; "
                "anodal left DLPFC tDCS adjunct used in EPI-DEP phenotype."
            ),
            "Insula — insular epilepsy; autonomic regulation": (
                "Insular epilepsy presents with autonomic, laryngeal, or sensory symptoms and is frequently "
                "misdiagnosed as TLE. The insula is also critical for interoception and autonomic regulation — "
                "relevant to taVNS mechanism via vagal-insular projections."
            ),
            "Cerebellum — modulated by VNS for seizure control": (
                "Cerebellar circuits participate in seizure suppression networks. Implanted and transcutaneous "
                "VNS modulate cerebellar-thalamo-cortical pathways, contributing to seizure threshold elevation."
            ),
            "Locus Coeruleus / NTS — taVNS mechanism pathway": (
                "The nucleus tractus solitarius (NTS) is the primary brainstem relay of vagal afferents. "
                "NTS projects to locus coeruleus (LC), which releases noradrenaline broadly to cortex, "
                "increasing GABA-mediated inhibition and reducing seizure susceptibility. The LC-NE system "
                "is the primary mechanistic pathway of taVNS anti-seizure effect."
            ),
        },

        network_profiles=[
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN TLE. Hippocampal-entorhinal-limbic circuit hyperexcitability is the "
                "hallmark of TLE. Seizures propagate via the Papez circuit. Amygdala hyperexcitability "
                "drives ictal and interictal limbic dysregulation.",
                primary=True, severity="severe",
                evidence_note="Hippocampal-limbic hyperexcitability as the core pathophysiology of TLE; established by lesion studies, iEEG, and surgical outcomes",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "Salience network hyperactivation drives seizure propagation and interictal dysphoria. "
                "SN nodes (anterior insula, ACC) show abnormal connectivity in DRE.",
                severity="moderate",
                evidence_note="Salience network involvement in DRE; fMRI connectivity studies",
            ),
            make_network(
                NetworkKey.SMN, NetworkDysfunction.HYPER,
                "Sensorimotor network hyperexcitability in frontal lobe epilepsy; motor cortex suppression "
                "targets. Focal motor seizures arise from primary motor cortex hyperexcitability.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "Interictal executive dysfunction and cognitive impairment; DLPFC hypoactivation contributes "
                "to comorbid depression and attention deficits in DRE.",
                severity="moderate",
                evidence_note="CEN hypofunction and cognitive comorbidity in DRE; neuropsychological studies in TLE",
            ),
        ],

        primary_network=NetworkKey.LIMBIC,

        fnon_rationale=(
            "In epilepsy/DRE, the primary dysfunctional network is the LIMBIC system, with focal "
            "hyperexcitability in hippocampal-entorhinal-limbic circuits (TLE) or frontal-cortical "
            "circuits (FLE). The FNON framework targets this hyperexcitable network for inhibitory "
            "neuromodulation: taVNS via LC/NTS-mediated GABAergic suppression; cathodal tDCS via "
            "membrane hyperpolarization of the epileptogenic focus; 1 Hz rTMS via long-term depression "
            "(LTD) of cortical excitability at the EZ. For the EPI-DEP phenotype, CEN hypofunction "
            "is addressed adjunctively via left DLPFC anodal tDCS."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="dre_focal",
                label="DRE-F — Drug-Resistant Focal Epilepsy",
                description=(
                    "Drug-resistant focal epilepsy — failure of ≥2 AEDs. Most relevant for neuromodulation. "
                    "Includes TLE and neocortical focal DRE. 30–40% of all epilepsy."
                ),
                key_features=[
                    "Focal seizures",
                    "AED failure ≥2 drugs",
                    "Identifiable EEG focus",
                    "Potential surgical candidate",
                ],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                preferred_modalities=[Modality.TAVNS, Modality.TDCS, Modality.TMS],
                tdcs_target="Cathodal over epileptogenic focus (EEG/MRI-guided)",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="tle",
                label="TLE — Temporal Lobe Epilepsy",
                description=(
                    "Commonest focal DRE; hippocampal sclerosis in 60–70%. Distinctive auras (déjà vu, "
                    "epigastric rising). High comorbid depression."
                ),
                key_features=[
                    "Mesial temporal onset",
                    "Hippocampal sclerosis",
                    "Auras",
                    "Comorbid depression >50%",
                ],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.DMN],
                preferred_modalities=[Modality.TAVNS, Modality.TDCS],
                tdcs_target="Cathodal temporal cortex (T3/T4 bilateral)",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="gen_epilepsy",
                label="GE — Generalized Epilepsy (non-surgical)",
                description=(
                    "Generalized epilepsy not amenable to focal resection. Includes juvenile myoclonic "
                    "epilepsy (JME), absence epilepsy. NFB and taVNS as adjuncts."
                ),
                key_features=[
                    "Generalized EEG pattern",
                    "Multiple seizure types",
                    "No focal resection candidate",
                    "AED-responsive or partially responsive",
                ],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                preferred_modalities=[Modality.TAVNS, Modality.TMS],
                tdcs_target="Bilateral cathodal frontal montage",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="epi_dep",
                label="EPI-DEP — Epilepsy with Comorbid Depression",
                description=(
                    "Epilepsy with clinically significant interictal depression (PHQ-9 ≥10). Requires "
                    "dual-target neuromodulation strategy: seizure reduction + mood improvement."
                ),
                key_features=[
                    "Interictal depression",
                    "PHQ-9 ≥10",
                    "Reduced QoL",
                    "SSRI interaction monitoring",
                ],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.CEN],
                preferred_modalities=[Modality.TAVNS, Modality.TDCS],
                tdcs_target="taVNS primary + left DLPFC anodal tDCS adjunct",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="seizure_diary",
                name="Seizure Frequency Diary",
                abbreviation="SFD",
                domains=["seizure_frequency", "seizure_type", "duration"],
                timing="baseline",
                evidence_pmid=None,
                notes=(
                    "Primary outcome measure. Baseline 3-month seizure diary mandatory before treatment. "
                    "Responder = ≥50% seizure frequency reduction from baseline."
                ),
            ),
            AssessmentTool(
                scale_key="qolie31",
                name="Quality of Life in Epilepsy — 31 item",
                abbreviation="QOLIE-31",
                domains=["qol", "seizure_worry", "emotional_wellbeing", "energy", "cognitive", "social"],
                timing="baseline",
                evidence_pmid="7859970",
                notes=(
                    "Primary QoL outcome. Administer at baseline and 3 months. "
                    "Score 0–100; higher = better QoL."
                ),
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes=(
                    "Depression screen — high comorbidity in epilepsy (30–50%). "
                    "Score ≥10 = clinically significant depression; initiate dual-target protocol."
                ),
            ),
            AssessmentTool(
                scale_key="gad7",
                name="Generalised Anxiety Disorder Assessment — 7 item",
                abbreviation="GAD-7",
                domains=["anxiety"],
                timing="baseline",
                evidence_pmid="16717171",
                notes="Anxiety screen. Co-administer with PHQ-9.",
            ),
            AssessmentTool(
                scale_key="moca",
                name="Montreal Cognitive Assessment",
                abbreviation="MoCA",
                domains=["cognition", "memory", "executive_function"],
                timing="baseline",
                evidence_pmid="15817019",
                notes=(
                    "Cognitive baseline — especially for TLE with memory impairment. "
                    "Administer at baseline and 6 months."
                ),
            ),
        ],

        baseline_measures=[
            "Seizure Frequency Diary — 3-month baseline mandatory before treatment initiation",
            "QOLIE-31 (primary QoL outcome — baseline and 3 months)",
            "PHQ-9 and GAD-7 (depression and anxiety screen — high comorbidity)",
            "MoCA (cognitive baseline — especially TLE; baseline and 6 months)",
            "EEG report confirming epileptogenic zone localization (mandatory for tDCS/TMS)",
            "MRI brain (structural — for EZ localization and hippocampal sclerosis assessment)",
            "Current AED regimen documented in full (drug, dose, duration)",
            "SOZO PRS (patient-rated seizure impact, mood, cognitive function — 0–10)",
        ],

        followup_measures=[
            "Seizure Frequency Diary — continuous; compare to 3-month baseline at Week 12",
            "QOLIE-31 at Week 12 and 6 months",
            "PHQ-9 monthly (EPI-DEP phenotype)",
            "MoCA at 6 months (TLE phenotype)",
            "Adverse event monitoring and AED documentation at every session",
            "SOZO PRS at each session (brief) and end of block (full)",
        ],

        inclusion_criteria=[
            "Confirmed epilepsy diagnosis by neurologist with EEG confirmation",
            "DRE = ≥2 failed adequate trials of tolerated AEDs",
            "Baseline seizure diary completed (3 months prior to treatment)",
            "MRI/EEG data available for epileptogenic zone localization",
            "Age 16–70 years",
            "Capacity to consent",
            "Stable AED regimen for ≥3 months",
        ],

        exclusion_criteria=[
            "Status epilepticus within 4 weeks",
            "Metallic intracranial implants",
            "Active psychosis",
            "Pregnancy",
            "Cardiac pacemaker or implanted defibrillator",
            "Active suicidality",
            "Active uncontrolled epilepsy with frequent tonic-clonic seizures during session — must achieve some baseline seizure control before treatment",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "High-frequency TMS (>1 Hz) — absolute contraindication in all epilepsy patients",
            "Anodal tDCS over cortex in epilepsy — absolute contraindication (increases excitability; risk of triggering seizure)",
            "Recent status epilepticus within 4 weeks",
            "Active uncontrolled epilepsy without baseline seizure control — defer neuromodulation until stabilized",
        ],

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "contraindication",
                "ABSOLUTE: Anodal tDCS is CONTRAINDICATED in epilepsy — must never apply anodal tDCS over "
                "motor cortex or epileptogenic zone; risk of triggering seizure. Doctor authorization "
                "mandatory for any tDCS application.",
                "absolute",
                "Consensus safety statement; cathodal tDCS reduces excitability, anodal increases it",
            ),
            make_safety(
                "precaution",
                "Seizure first aid protocol must be established before treatment initiation. All clinical "
                "staff must be trained in seizure management. Emergency equipment (benzodiazepines, "
                "resuscitation) must be available at all treatment sessions.",
                "high",
                "Clinical governance requirement for epilepsy neuromodulation",
            ),
            make_safety(
                "precaution",
                "1 Hz rTMS requires precise EZ targeting — neuronavigation mandatory. High-frequency rTMS "
                "(>1 Hz) is an ABSOLUTE CONTRAINDICATION in DRE and epilepsy. Doctor authorization required.",
                "high",
                "Consensus safety statement for rTMS in epilepsy; Rossi et al. safety guidelines",
            ),
            make_safety(
                "monitoring",
                "All AED changes during treatment block must be reported to treating neurologist and SOZO "
                "clinician — medication changes confound response assessment and may alter seizure threshold.",
                "moderate",
                "Clinical practice requirement; AED changes are a major confounder in DRE neuromodulation trials",
            ),
            make_safety(
                "precaution",
                "Inform patients that neuromodulation is an ADJUNCT to AED therapy — do not discontinue "
                "AEDs. Document current AED regimen at every session.",
                "moderate",
                "Patient safety and informed consent requirement",
            ),
            make_safety(
                "stopping_rule",
                "Any increase in seizure frequency ≥50% above baseline within first 4 weeks → immediate "
                "treatment pause and Doctor neurologist review.",
                "high",
                "DRE-specific stopping rule; seizure worsening is a recognized adverse event in neuromodulation",
            ),
        ],

        stimulation_targets=[
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Left cymba conchae",
                target_abbreviation="TAVNS",
                laterality="left",
                rationale=(
                    "taVNS activates the Arnold's nerve (auricular branch of CN X) at the left cymba "
                    "conchae, projecting to NTS → locus coeruleus → noradrenergic/GABAergic cortical "
                    "modulation → reduced seizure threshold. DeGiorgio 2013 (RPED trial, N=47) demonstrated "
                    "40.5% seizure reduction vs 21.8% sham (p=0.02). Bauer 2016 provided confirmatory "
                    "evidence. This is the best-evidenced non-invasive modality for DRE."
                ),
                protocol_label="TAVNS-EPI — Seizure Reduction (Drug-Resistant Focal Epilepsy)",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
            ),
            make_tdcs_target(
                "Epileptogenic Focus", "EZ", "targeted (EEG-guided)",
                "Cathodal tDCS reduces neuronal excitability via membrane hyperpolarization at the "
                "epileptogenic zone. Fregni et al. (2006) demonstrated seizure reduction after cathodal "
                "tDCS over epileptogenic focus. EEG localization is mandatory before electrode placement. "
                "CRITICAL: Anodal tDCS is absolutely contraindicated in epilepsy — cathodal only.",
                "C-EPI-CAT — Cathodal tDCS Epileptogenic Focus Inhibition",
                EvidenceLevel.LOW, off_label=True,
            ),
            StimulationTarget(
                modality=Modality.TMS,
                target_region="Epileptogenic Zone",
                target_abbreviation="EZ-TMS",
                laterality="targeted",
                rationale=(
                    "1 Hz rTMS is a well-established inhibitory paradigm; application over the epileptogenic "
                    "zone reduces ictal discharge frequency via long-term depression (LTD) of cortical "
                    "excitability. Tergau 1999 and Cantello 2007 confirm seizure reduction. Neuronavigation "
                    "required for accurate EZ targeting. Low-frequency (1 Hz) only — high-frequency rTMS "
                    "is absolutely contraindicated."
                ),
                protocol_label="TMS-EPI — 1 Hz rTMS Epileptogenic Zone Inhibition",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="TAVNS-EPI",
                label="taVNS — Seizure Reduction (Drug-Resistant Focal Epilepsy)",
                modality=Modality.TAVNS,
                target_region="Left cymba conchae (auricular branch of vagus nerve)",
                target_abbreviation="TAVNS",
                phenotype_slugs=["dre_focal", "tle", "gen_epilepsy", "epi_dep"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "NEMOS (tVNS Technologies) or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "250 µs",
                    "intensity": "0.5–3.0 mA (below pain threshold)",
                    "duration": "4 hours/day (continuous low-level) or 30 min sessions x2/day",
                    "sessions": "Daily for 12 weeks (minimum)",
                    "electrode": "Left cymba conchae",
                },
                rationale=(
                    "taVNS activates the Arnold's nerve (auricular branch of CN X), projecting to "
                    "NTS → locus coeruleus → noradrenergic/GABAergic cortical modulation → reduced "
                    "seizure threshold. DeGiorgio 2013 (RPED trial, N=47): 40.5% seizure reduction "
                    "vs 21.8% sham; p=0.02. Bauer 2016: confirmatory. taVNS devices used as adjunct; "
                    "implanted VNS is FDA-approved — taVNS is the non-invasive version."
                ),
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
                session_count=84,
            ),
            ProtocolEntry(
                protocol_id="C-EPI-CAT",
                label="Cathodal tDCS — Epileptogenic Focus Inhibition",
                modality=Modality.TDCS,
                target_region="Epileptogenic focus (EEG/MRI-guided)",
                target_abbreviation="EZ",
                phenotype_slugs=["dre_focal", "tle"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Newronika HDCkit or Soterix",
                    "cathode": "Over epileptogenic focus (EEG-guided, typically temporal T3/T4 or frontal F7/F8)",
                    "anode": "Contralateral shoulder or Cz",
                    "intensity": "1.0–2.0 mA (start 1 mA)",
                    "duration": "20–30 min",
                    "sessions": "10–15 over 3 weeks",
                    "electrode_size": "35 cm2",
                    "note": (
                        "EEG localization required before treatment — cathode placement must target "
                        "confirmed EZ. CRITICAL: Anodal tDCS is CONTRAINDICATED in epilepsy."
                    ),
                },
                rationale=(
                    "Cathodal tDCS reduces neuronal excitability via membrane hyperpolarization. "
                    "Fregni et al. (2006, Epilepsia, N=6) demonstrated seizure reduction after "
                    "cathodal tDCS over epileptogenic focus. Multiple pilots confirm the principle. "
                    "CRITICAL: Anodal tDCS is CONTRAINDICATED in epilepsy (increases excitability). "
                    "Doctor authorization mandatory. OFF-LABEL."
                ),
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
                session_count=15,
            ),
            ProtocolEntry(
                protocol_id="TMS-EPI",
                label="1 Hz rTMS — Epileptogenic Zone Inhibition",
                modality=Modality.TMS,
                target_region="Epileptogenic focus",
                target_abbreviation="EZ-TMS",
                phenotype_slugs=["dre_focal", "tle"],
                network_targets=[NetworkKey.LIMBIC],
                parameters={
                    "device": "MagVenture or Magstim",
                    "frequency": "1 Hz (inhibitory)",
                    "intensity": "80–90% rMT",
                    "pulses": "900–1200 per session",
                    "sessions": "10 over 2 weeks",
                    "target": "EEG/MRI-guided epileptogenic zone (figure-8 coil)",
                    "note": (
                        "Neuronavigation required for accurate EZ targeting. "
                        "Low-frequency only — high-frequency rTMS is contraindicated."
                    ),
                },
                rationale=(
                    "1 Hz rTMS is a well-established inhibitory paradigm; application over the "
                    "epileptogenic zone reduces ictal discharge frequency. Tergau 1999, Cantello 2007 "
                    "confirm seizure reduction. Neuronavigation required for precise EZ targeting. "
                    "Low-frequency (1 Hz) only — high-frequency rTMS is an absolute contraindication "
                    "in all epilepsy patients. OFF-LABEL."
                ),
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
                session_count=10,
            ),
            ProtocolEntry(
                protocol_id="TAVNS-EPI-DEP",
                label="taVNS — Epilepsy + Comorbid Depression",
                modality=Modality.TAVNS,
                target_region="Left cymba conchae",
                target_abbreviation="TAVNS",
                phenotype_slugs=["epi_dep"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.CEN, NetworkKey.SN],
                parameters={
                    "device": "NEMOS (tVNS Technologies) or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "250 µs",
                    "intensity": "0.5–3.0 mA (below pain threshold)",
                    "duration": "4 hours/day or 30 min x2/day",
                    "sessions": "Daily for 12 weeks",
                    "adjunct_tdcs": "Left DLPFC anodal tDCS — 1.5 mA, 20 min, 3×/week after taVNS session",
                    "monitoring": "PHQ-9 monthly; monitor for mood improvement",
                    "note": "Consider SSRI interaction. Monitor PHQ-9 monthly.",
                },
                rationale=(
                    "Dual-target protocol for EPI-DEP phenotype. taVNS addresses limbic hyperexcitability "
                    "and seizure frequency via NTS/LC pathway. Adjunct left DLPFC anodal tDCS targets CEN "
                    "hypofunction and interictal depression. Evidence extrapolated from taVNS anti-seizure "
                    "RCTs and DLPFC tDCS depression trials — no dedicated combined RCT exists. "
                    "OFF-LABEL (adjunct tDCS). Very low combined evidence — requires clinical justification "
                    "and treating neurologist co-authorization."
                ),
                evidence_level=EvidenceLevel.VERY_LOW,
                off_label=True,
                session_count=36,
            ),
        ],

        symptom_network_mapping={
            "Seizures": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Interictal Depression": [NetworkKey.LIMBIC, NetworkKey.CEN],
            "Anxiety": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Cognitive Impairment": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Sleep Disturbance": [NetworkKey.LIMBIC, NetworkKey.DMN],
        },

        symptom_modality_mapping={
            "Seizures": [Modality.TAVNS, Modality.TMS, Modality.TDCS],
            "Interictal Depression": [Modality.TAVNS, Modality.TDCS],
            "Anxiety": [Modality.TAVNS, Modality.CES],
            "Cognitive Impairment": [Modality.TDCS],
            "Sleep Disturbance": [Modality.TAVNS, Modality.CES],
        },

        responder_criteria=[
            "≥50% reduction in seizure frequency from 3-month baseline (standard responder criterion used in AED trials)",
            "Clinically meaningful improvement in QOLIE-31 (≥10-point improvement from baseline)",
            "≥50% reduction in PHQ-9 score (EPI-DEP phenotype)",
        ],

        non_responder_pathway=(
            "For patients classified as non-responders at 12-week assessment:\n"
            "1. Confirm accurate epileptogenic zone localization — misplaced electrodes are the most "
            "common cause of failure\n"
            "2. Review AED regimen with treating neurologist — recent AED change may have confounded response\n"
            "3. Consider alternative taVNS parameters (increase duration, adjust intensity to titrate "
            "just below discomfort)\n"
            "4. For TLE non-responders: discuss surgical evaluation with neurologist "
            "(resection, laser ablation)\n"
            "5. Doctor neurologist review mandatory at 4-week interim assessment\n"
            "6. If no seizure response after 12 weeks taVNS: document as DRE non-responder to "
            "neuromodulation; explore implanted VNS with neurologist referral"
        ),

        evidence_summary=(
            "taVNS has the strongest non-invasive evidence for DRE: DeGiorgio 2013 (RPED trial, N=47) "
            "demonstrated 40.5% seizure reduction vs 21.8% sham (p=0.02; MEDIUM quality). Bauer 2016 "
            "provided confirmatory RCT evidence. Cathodal tDCS has pilot-level evidence (Fregni 2006, "
            "N=6 — LOW quality). 1 Hz rTMS has pilot RCT evidence (Tergau 1999 — LOW quality). All "
            "tDCS and rTMS applications are OFF-LABEL in epilepsy. The TAVNS-EPI-DEP combined protocol "
            "is extrapolated from separate taVNS and tDCS literatures — VERY LOW combined evidence."
        ),

        evidence_gaps=[
            "No large multi-site RCT of tDCS in DRE; optimal taVNS stimulation parameters not established",
            "rTMS targeting precision with vs without neuronavigation in DRE — no controlled comparison",
            "Long-term seizure-modifying effects >6 months for any non-invasive modality",
            "Safety and efficacy of combined taVNS + tDCS in DRE — no dedicated trial",
            "Predictors of neuromodulation response in DRE — biomarker, seizure network, or genetics not established",
        ],

        references=[
            {
                "authors": "DeGiorgio CM et al.",
                "year": 2013,
                "title": "Randomized controlled trial of trigeminal nerve stimulation for drug-resistant epilepsy",
                "journal": "Neurology",
                "pmid": "23966253",
                "evidence_type": "rct",
            },
            {
                "authors": "Bauer S et al.",
                "year": 2016,
                "title": "Transcutaneous vagus nerve stimulation (taVNS) for treatment of drug-resistant epilepsy",
                "journal": "Epilepsia",
                "pmid": "26919778",
                "evidence_type": "rct",
            },
            {
                "authors": "Fregni F et al.",
                "year": 2006,
                "title": "Transcranial direct current stimulation of the unaffected hemisphere in stroke patients",
                "journal": "Neuroreport",
                "pmid": "16794473",
                "evidence_type": "pilot_study",
            },
            {
                "authors": "Tergau F et al.",
                "year": 1999,
                "title": "Low-frequency repetitive transcranial magnetic stimulation improves intractable epilepsy",
                "journal": "Lancet",
                "pmid": "10376627",
                "evidence_type": "pilot_study",
            },
        ],

        overall_evidence_quality=EvidenceLevel.LOW,

        clinical_tips=[
            "taVNS is the preferred first-line neuromodulation for DRE — it has the strongest evidence "
            "and the most favourable safety profile. Confirm device availability before protocol design.",
            "Cathodal tDCS electrode placement MUST be guided by EEG-confirmed epileptogenic zone — "
            "never apply without neurophysiological localization data.",
            "Establish a seizure emergency protocol with the patient and family before first session. "
            "Every session must have trained staff and emergency benzodiazepines accessible.",
            "The 50% responder criterion (≥50% seizure frequency reduction) is the standard endpoint "
            "for antiepileptic trials — use 3-month baseline seizure diary to establish accurate baseline.",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "All epilepsy neuromodulation requires joint approval from SOZO clinician AND treating "
            "neurologist before protocol initiation",
            "Seizure emergency protocol must be documented and signed before first session",
            "High-frequency TMS is absolutely prohibited in all epilepsy patients — enforce at protocol selection",
            "Anodal tDCS is absolutely prohibited in epilepsy patients without explicit treating neurologist authorization",
        ],
    )
