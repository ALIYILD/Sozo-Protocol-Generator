"""
Chronic Insomnia — Complete condition generator.

Key references:
- Feige B et al. (2014) CES for insomnia — systematic review
- Kaplan KA et al. (2014) tDCS slow oscillation for sleep — Brain Stimulation
- Frase L et al. (2019) tDCS for insomnia — Journal of Sleep Research
- Bastien CH et al. (2001) ISI validation — Sleep Medicine
- Buysse DJ et al. (1989) PSQI validation — Psychiatry Research
- Johns MW (1991) ESS validation — Sleep
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
    make_network, make_tdcs_target, make_safety,
    SHARED_ABSOLUTE_CONTRAINDICATIONS, SHARED_SAFETY_NOTES, SHARED_GOVERNANCE_RULES
)

logger = logging.getLogger(__name__)


def build_insomnia_condition() -> ConditionSchema:
    """Build the complete Chronic Insomnia condition schema."""
    return ConditionSchema(
        slug="insomnia",
        display_name="Chronic Insomnia",
        icd10="G47.00",
        aliases=["insomnia disorder", "chronic insomnia disorder", "CID", "primary insomnia", "sleep onset insomnia", "sleep maintenance insomnia"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Chronic Insomnia Disorder (CID) is characterized by persistent difficulty initiating "
            "or maintaining sleep, or early morning awakening, occurring at least three nights per "
            "week for at least three months, causing significant distress or functional impairment. "
            "It affects approximately 10-15% of the adult population and is the most prevalent sleep "
            "disorder worldwide. Insomnia involves a state of cortical and autonomic hyperarousal — "
            "a failure of the normal sleep-wake transition to suppress default mode network (DMN) "
            "activity and limbic-emotional processing. Neuroimaging consistently shows elevated "
            "resting-state DMN connectivity, increased anterior cingulate and prefrontal metabolic "
            "activity at sleep onset, and heightened amygdala reactivity to emotional stimuli in "
            "insomnia patients compared to good sleepers. "
            "Cognitive Behavioural Therapy for Insomnia (CBT-I) is the gold standard first-line "
            "treatment. Neurostimulation approaches — particularly Cranial Electrotherapy Stimulation "
            "(CES) and investigational slow-oscillation tDCS during sleep — offer adjunctive options "
            "for treatment-resistant cases or those who cannot complete CBT-I, with CES showing the "
            "strongest evidence base among non-pharmacological device therapies."
        ),

        pathophysiology=(
            "The hyperarousal model of insomnia posits that CID reflects a global state of "
            "physiological, cortical, and cognitive overactivation that prevents sleep initiation and "
            "maintenance. At the neurobiological level, insomnia is associated with: (1) Failure of "
            "the ventrolateral preoptic area (VLPO) to adequately inhibit arousal systems (LC, TMN, "
            "DRN) via GABAergic and galaninergic mechanisms — the 'flip-flop switch' dysfunction; "
            "(2) Elevated HPA axis activity with increased cortisol at sleep onset, reflecting "
            "chronic stress-system engagement; (3) Cortical hyperarousal evident as elevated high-"
            "frequency EEG activity (beta, gamma) during NREM sleep, reduced slow-wave activity "
            "(delta power), and impaired sleep spindle generation from thalamocortical circuits; "
            "(4) DMN hyperconnectivity and failure to deactivate medial prefrontal cortex (mPFC) "
            "and posterior cingulate cortex (PCC) during sleep-wake transition; (5) Amygdala "
            "hyperreactivity contributing to intrusive worry and cognitive arousal at bedtime; "
            "(6) Reduced GABA concentrations in prefrontal and occipital cortex, impeding inhibitory "
            "tone; (7) Adenosine dysregulation reducing homeostatic sleep pressure. "
            "CES (0.5 Hz, 100 microamps) is believed to enhance inhibitory tone by entraining "
            "slow-wave oscillatory activity and modulating serotonin, beta-endorphin, and cortisol. "
            "Slow-oscillation tDCS (0.75 Hz, 0.26 mA peak-to-peak) applied via frontal electrodes "
            "during NREM sleep phases has been shown to boost delta power and memory consolidation "
            "in controlled sleep laboratory settings, though translation to home-based insomnia "
            "treatment requires further validation."
        ),

        core_symptoms=[
            "Difficulty initiating sleep (sleep onset latency > 30 minutes)",
            "Difficulty maintaining sleep (WASO > 30 minutes)",
            "Early morning awakening (> 30 minutes before desired wake time)",
            "Non-restorative or poor-quality sleep",
            "Daytime fatigue and low energy",
            "Impaired daytime attention and concentration",
            "Mood disturbance (irritability, dysphoria, anxiety)",
            "Daytime performance impairment (occupational, social, academic)",
            "Subjective cognitive complaints (memory, executive function)",
            "Persistent worry about sleep and its consequences",
        ],

        non_motor_symptoms=[
            "Chronic fatigue and low energy",
            "Cognitive slowing and poor concentration",
            "Mood disturbance and emotional dysregulation",
            "Increased risk of depression and anxiety (bidirectional relationship)",
            "Cardiovascular risk (elevated with chronic insomnia)",
            "Metabolic dysregulation (impaired glucose metabolism with sleep restriction)",
            "Immune system suppression",
            "Increased pain sensitivity and somatic complaints",
            "Social withdrawal and reduced quality of life",
        ],

        key_brain_regions=[
            "Medial Prefrontal Cortex (mPFC) — DMN hub; hyperactive at sleep onset, target for inhibition",
            "Posterior Cingulate Cortex (PCC) — DMN node; elevated activation in insomnia",
            "Anterior Cingulate Cortex (ACC) — arousal and worry generation, SN node",
            "Amygdala — hyperreactive emotional processing, limbic hyperarousal driver",
            "Hippocampus — memory consolidation impaired by poor sleep",
            "Ventrolateral Preoptic Area (VLPO) — sleep-promoting GABAergic neurons",
            "Thalamus — sleep spindle generation and sensory gating during NREM",
            "Locus Coeruleus (LC) — noradrenergic arousal centre, overactive in insomnia",
            "Prefrontal Cortex (dorsolateral) — executive control of rumination and worry",
            "Insula — interoceptive hyperarousal and autonomic regulation",
        ],

        brain_region_descriptions={
            "mPFC": "Default mode hub that should deactivate during sleep onset; failure to suppress drives cognitive arousal",
            "PCC": "DMN posterior node; elevated connectivity with mPFC maintains wakefulness-related network activity",
            "ACC": "Mediates worry, rumination, and cognitive arousal; target for CES-mediated inhibition",
            "Amygdala": "Hyperreactive to sleep-related threat appraisals; drives limbic arousal maintaining wakefulness",
            "VLPO": "GABAergic sleep-promoting region; insufficient inhibitory output sustains arousal systems",
            "Thalamus": "Spindle generation impaired in insomnia; slow-oscillation tDCS may enhance thalamocortical synchrony",
            "LC": "Noradrenergic arousal system; should be inhibited by VLPO at sleep onset but remains overactive in insomnia",
            "DLPFC": "Executive control of rumination; CES and tDCS may modulate prefrontal excitability",
            "Insula": "Interoceptive hyperarousal contributing to somatic vigilance and body-focused arousal",
            "Hippocampus": "Memory consolidation during slow-wave sleep; impaired consolidation with insomnia-related delta power reduction",
        },

        network_profiles=[
            make_network(
                network=NetworkKey.DMN,
                dysfunction=NetworkDysfunction.HYPER,
                relevance=(
                    "Primary network in insomnia. Normal sleep onset requires coordinated DMN deactivation. "
                    "In insomnia, elevated mPFC-PCC connectivity persists into sleep-onset periods, "
                    "generating self-referential thought, worry, and anticipatory arousal. "
                    "Therapeutic goal: Reduce DMN hyperconnectivity to facilitate sleep onset."
                ),
                primary=True,
                severity="severe",
                evidence_note="Established; resting-state fMRI evidence (Drummond et al., Spiegelhalder et al.)",
            ),
            make_network(
                network=NetworkKey.LIMBIC,
                dysfunction=NetworkDysfunction.HYPER,
                relevance=(
                    "Limbic hyperarousal — particularly amygdala hyperreactivity and elevated ACC activity — "
                    "is a core feature of insomnia. Amplifies emotional responses to sleep-related stimuli. "
                    "CES reduces amygdala reactivity and promotes limbic inhibition."
                ),
                severity="high",
                evidence_note="Moderate; amygdala hyperreactivity in CID established by neuroimaging studies",
            ),
            make_network(
                network=NetworkKey.SN,
                dysfunction=NetworkDysfunction.HYPER,
                relevance=(
                    "The Salience Network shows heightened activation during attempted sleep, reflecting "
                    "excessive interoceptive monitoring. ACC hyperactivation sustains sleep-related worry "
                    "and cognitive hyperarousal in insomnia."
                ),
                severity="moderate",
                evidence_note="Moderate; ACC hyperactivation replicated across fMRI insomnia studies",
            ),
        ],

        primary_network=NetworkKey.DMN,

        fnon_rationale=(
            "Insomnia maps to a triple-network hyperarousal state in the FNON framework: the DMN fails "
            "to execute the normal deactivation required for sleep onset, the Limbic Network sustains "
            "emotional and autonomic arousal preventing sleep initiation, and the SN drives persistent "
            "interoceptive vigilance. Unlike conditions where SN-DMN imbalance reflects CEN underactivity, "
            "insomnia's core dysfunction is a failure of the global inhibitory state transition. "
            "Neurostimulation targets this by: (1) CES — delivering oscillating sub-threshold current "
            "(0.5 Hz, 100 microamps alpha-theta range) that promotes synchronised slow oscillatory "
            "activity across frontal midline structures, reducing the high-frequency cortical activity "
            "characteristic of hyperarousal; (2) Slow-oscillation tDCS — phase-coupled frontal "
            "stimulation at 0.75 Hz during NREM to boost delta power and thalamocortical synchrony "
            "(investigational, requires sleep lab delivery). The therapeutic target is restoration of "
            "the normal inhibitory state transition from wakefulness to NREM sleep."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="soi",
                label="Sleep Onset Insomnia",
                description=(
                    "Predominant difficulty with sleep initiation (SOL > 30 minutes). Associated with "
                    "cognitive hyperarousal — racing thoughts, worry about sleep, and anticipatory anxiety. "
                    "Strongest association with DMN hyperconnectivity and limbic hyperarousal at bedtime. "
                    "CES applied 30-45 minutes before intended sleep onset. CBT-I concurrent."
                ),
                key_features=["SOL > 30 minutes", "Racing thoughts at bedtime", "Anticipatory sleep anxiety",
                               "Bedroom cue-dependent arousal", "Clock-watching behaviour"],
                primary_networks=[NetworkKey.DMN, NetworkKey.LIMBIC],
                preferred_modalities=[Modality.CES],
            ),
            PhenotypeSubtype(
                slug="smi",
                label="Sleep Maintenance Insomnia",
                description=(
                    "Difficulty maintaining sleep with frequent nocturnal awakenings (WASO > 30 minutes). "
                    "Often associated with hyperactivation of arousal systems during NREM sleep — elevated "
                    "beta power during slow-wave sleep stages. Common in middle-aged and older adults. "
                    "Consider comorbid pain, GERD, or nocturia."
                ),
                key_features=["WASO > 30 minutes", "Frequent nocturnal awakenings", "Light/fragmented sleep",
                               "Unrefreshing sleep", "Heightened noise sensitivity at night"],
                primary_networks=[NetworkKey.SN, NetworkKey.LIMBIC],
                preferred_modalities=[Modality.CES],
            ),
            PhenotypeSubtype(
                slug="ema",
                label="Early Morning Awakening Insomnia",
                description=(
                    "Awakening 30+ minutes before desired wake time with inability to return to sleep. "
                    "Strongly associated with depression (melancholic subtype) and circadian phase advance. "
                    "Screen for major depression (PHQ-9); refer if EMA with diurnal mood variation and anhedonia."
                ),
                key_features=["Wake 30+ min before desired time", "Cannot return to sleep", "Morning mood nadir",
                               "Early morning rumination", "Marked daytime fatigue"],
                primary_networks=[NetworkKey.DMN, NetworkKey.LIMBIC],
                preferred_modalities=[Modality.CES],
            ),
            PhenotypeSubtype(
                slug="comorbid_ins",
                label="Comorbid Insomnia Disorder",
                description=(
                    "Insomnia co-occurring with a primary psychiatric (depression, anxiety, PTSD, OCD) "
                    "or medical condition (chronic pain, neurological disease). Bidirectional: insomnia "
                    "worsens mood disorder outcomes; untreated mood disorders worsen insomnia. "
                    "CES has evidence for both insomnia and anxiety/depression comorbidities."
                ),
                key_features=["Active mood/anxiety comorbidity", "Mixed sleep complaints", "Anxiety-onset insomnia",
                               "Depression-associated EMA", "PTSD hyperarousal-driven insomnia"],
                primary_networks=[NetworkKey.DMN, NetworkKey.LIMBIC, NetworkKey.SN],
                preferred_modalities=[Modality.CES],
            ),
            PhenotypeSubtype(
                slug="cid",
                label="Chronic Insomnia Disorder (Treatment-Resistant)",
                description=(
                    "Longstanding insomnia (> 6 months) having failed adequate CBT-I and pharmacotherapy. "
                    "Represents entrenched hyperarousal with conditioned arousal and cortical hyperarousal "
                    "patterns (elevated beta during sleep). Primary indication for neurostimulation adjuncts. "
                    "Frame as adjunct to, not replacement for, behavioural interventions."
                ),
                key_features=["Multi-year insomnia history", "Failed CBT-I and pharmacotherapy",
                               "Significant daytime impairment", "Conditioned bedroom arousal", "Sleep anxiety prominent"],
                primary_networks=[NetworkKey.DMN, NetworkKey.LIMBIC, NetworkKey.SN],
                preferred_modalities=[Modality.CES, Modality.TDCS],
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="ISI",
                name="Insomnia Severity Index",
                abbreviation="ISI",
                domains=["sleep onset", "sleep maintenance", "early awakening", "sleep satisfaction", "daytime impairment"],
                timing="Baseline, 2-weekly during treatment, discharge",
                evidence_pmid="11438246",
                notes="0-7 no insomnia; 8-14 sub-threshold; 15-21 moderate; 22-28 severe. MCID = 6 points. Gold standard insomnia outcome measure (Bastien et al. 2001).",
            ),
            AssessmentTool(
                scale_key="PSQI",
                name="Pittsburgh Sleep Quality Index",
                abbreviation="PSQI",
                domains=["sleep quality", "sleep latency", "sleep duration", "sleep efficiency", "sleep disturbances", "sleep medication", "daytime dysfunction"],
                timing="Baseline, monthly, discharge",
                evidence_pmid="2748771",
                notes="Score > 5 indicates poor sleeper; > 10 severe impairment. 7-component comprehensive sleep quality measure.",
            ),
            AssessmentTool(
                scale_key="ESS",
                name="Epworth Sleepiness Scale",
                abbreviation="ESS",
                domains=["daytime sleepiness"],
                timing="Baseline, 4-weekly",
                evidence_pmid="1798888",
                notes="0-10 normal; 11-24 excessive daytime sleepiness. ESS > 10 raises concern for OSA or hypersomnia — investigate before neurostimulation.",
            ),
            AssessmentTool(
                scale_key="DASS21",
                name="Depression Anxiety Stress Scales 21",
                abbreviation="DASS-21",
                domains=["depression", "anxiety", "stress"],
                timing="Baseline, 4-weekly, discharge",
                notes="Active severe depression warrants reassessment of primary diagnosis and treatment prioritisation. Critical for identifying comorbid insomnia phenotype.",
            ),
        ],

        baseline_measures=[
            "ISI (primary insomnia severity)",
            "PSQI (subjective sleep quality, 7 components)",
            "ESS (daytime sleepiness — rule out hypersomnia/OSA)",
            "DASS-21 (comorbid depression, anxiety, stress)",
            "SCI (DSM-5 insomnia diagnostic alignment)",
            "Sleep diary (2-week baseline minimum: SOL, WASO, TST, SE, subjective quality)",
            "Actigraphy (7-14 nights baseline where available — objective sleep parameters)",
            "Blood pressure (baseline cardiovascular screening)",
            "Medication review (CNS stimulants, beta-blockers, steroids, SSRIs may worsen insomnia)",
        ],

        followup_measures=[
            "ISI (every 2 weeks — primary outcome measure)",
            "PSQI (monthly)",
            "Sleep diary (ongoing — objective tracking of SOL, WASO, TST, SE)",
            "DASS-21 (monthly — monitor comorbid mood changes)",
            "ESS (monthly — daytime function)",
            "SCI (4-weekly — diagnostic criteria response)",
            "Actigraphy (mid-treatment and end-of-treatment comparison where available)",
        ],

        inclusion_criteria=[
            "DSM-5 / ICSD-3 Chronic Insomnia Disorder diagnosis confirmed",
            "ISI ≥ 10 (sub-threshold or clinical insomnia)",
            "Minimum 3 months symptom duration",
            "Age ≥ 18 years",
            "Stable or no concurrent medication for ≥ 2 weeks prior to commencement",
            "Capacity to provide informed consent",
            "Obstructive sleep apnoea ruled out or treated (ESS ≤ 10, or known and treated OSA with stable CPAP)",
        ],

        exclusion_criteria=[
            "Active untreated obstructive sleep apnoea (ESS > 10 without investigation)",
            "Narcolepsy or other primary hypersomnia disorder",
            "Severe untreated psychiatric disorder requiring immediate intervention",
            "Active substance use disorder (alcohol, hypnotics, stimulants)",
            "Uncontrolled medical condition disrupting sleep (uncontrolled pain, thyroid disease, GERD, nocturia requiring urological workup)",
            "Active suicidal ideation (refer for psychiatric assessment first)",
            "Pregnancy",
            "Night shift workers without commitment to circadian schedule stabilisation",
            "PTSD-predominant insomnia with active nightmares — consider trauma-focused treatment as primary",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "Active obstructive sleep apnoea without treatment (CES may reduce arousal responses — safety concern)",
            "Active mania or hypomania (CES may precipitate sleep disruption)",
            "Severe alcohol dependence — sleep architecture effects unpredictable",
            "Recent head injury (< 3 months) — defer to TBI protocol",
        ],

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                category="Skin Tolerance — CES Electrode Placement",
                description=(
                    "CES earclip electrodes must be checked for proper contact and moisture with conductive "
                    "gel. Skin irritation or burns from dry or poorly positioned electrodes have been reported. "
                    "Instruct patient to stop immediately if burning sensation at electrode site. Inspect "
                    "ears before and after each session."
                ),
                severity="medium",
                source="Alpha-Stim device guidelines; FDA Class III device requirements"
            ),
            make_safety(
                category="Sedation Risk — CES + CNS Depressants",
                description=(
                    "Additive sedative effect is possible when CES is combined with benzodiazepines, "
                    "Z-drugs, antihistamines, or other sedating medications. Advise patients not to drive "
                    "for at least 2 hours following CES session. Reduce expected medication dose requirement "
                    "over time if CES is effective — taper under medical supervision."
                ),
                severity="medium",
                source="Clinical pharmacology; Alpha-Stim post-market surveillance"
            ),
            make_safety(
                category="Daytime Sleepiness Screening",
                description=(
                    "CES and sleep-promoting neurostimulation must not be used in patients with undiagnosed "
                    "excessive daytime sleepiness (ESS > 10) until OSA or other hypersomnia has been excluded. "
                    "Neurostimulation that deepens sleep or reduces cortical arousal could theoretically "
                    "reduce protective arousal responses in patients with undiagnosed sleep-disordered breathing."
                ),
                severity="high",
                source="Sleep medicine safety principle; ESS screening protocol"
            ),
            make_safety(
                category="Psychiatric Comorbidity Monitoring",
                description=(
                    "Monitor for emergence or worsening of mood symptoms during treatment. Insomnia is "
                    "bidirectionally linked with depression — improvement in sleep may unmask underlying "
                    "depression as insomnia improves. Conversely, worsening mood with sleep changes requires "
                    "psychiatric review. Administer DASS-21 monthly throughout treatment."
                ),
                severity="medium",
                source="Clinical governance; insomnia-depression bidirectional model"
            ),
            make_safety(
                category="Realistic Expectations and Outcome Framing",
                description=(
                    "Neurostimulation for insomnia is an adjunct to, not a replacement for, CBT-I. "
                    "Patients should understand that realistic goals are improvements in sleep quality "
                    "and daytime functioning, not necessarily perfect sleep. Prior or concurrent CBT-I "
                    "should be documented. Avoid perpetuating sleep effort and hyperarousal by framing "
                    "device use as another 'sleep tool' requiring effort — use minimal dose and integrate "
                    "with sleep hygiene principles."
                ),
                severity="low",
                source="CBT-I guidelines; clinical governance"
            ),
        ],

        stimulation_targets=[
            StimulationTarget(
                modality=Modality.CES,
                target_region="Bilateral auricular (earclip electrodes)",
                target_abbreviation="CES",
                laterality="bilateral",
                rationale=(
                    "Cranial Electrotherapy Stimulation (CES) via bilateral earclip electrodes. "
                    "Delivers low-level oscillating current (0.5-100 microamps, 0.5 Hz waveform) "
                    "modulating brainstem/diencephalic structures, enhancing serotonin and "
                    "beta-endorphin release, normalising HPA axis activity, and entraining alpha/theta "
                    "oscillations. Meta-analyses support modest-to-moderate efficacy for sleep latency "
                    "reduction and sleep quality improvement (Feige et al., 2014). Alpha-Stim is "
                    "FDA-cleared for anxiety, depression, and insomnia."
                ),
                protocol_label="CES-INS-1 (Standard Pre-Sleep Protocol)",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
                consent_required=False,
            ),
            StimulationTarget(
                modality=Modality.TDCS,
                target_region="Frontal Cortex (bilateral)",
                target_abbreviation="FP",
                laterality="bilateral",
                rationale=(
                    "INVESTIGATIONAL: Slow-oscillation tDCS (0.75 Hz, 0.26 mA peak-to-peak) applied "
                    "during NREM sleep phases entrains cortical slow oscillations, boosting delta power "
                    "and sleep spindle activity (Marshall et al., 2006; Frase et al., 2019). "
                    "Requires EEG-triggered delivery in a sleep laboratory. NOT for routine clinical use. "
                    "Standard DC tDCS without phase-coupling does not replicate these effects."
                ),
                protocol_label="tDCS-INS-SO (Investigational Sleep-Onset Protocol)",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
                consent_required=True,
            ),
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve",
                target_abbreviation="ABVN",
                laterality="left",
                rationale=(
                    "taVNS at the left cymba conchae activates vagal projections to the NTS, locus "
                    "coeruleus, and dorsal raphe, reducing sympathetic tone and promoting parasympathetic "
                    "dominance. Adjunctive option for insomnia with prominent autonomic hyperarousal "
                    "(tachycardia, tension, physical restlessness at bedtime). Investigational."
                ),
                protocol_label="taVNS-INS (Autonomic Adjunct)",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
                consent_required=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-INS-CES",
                label="Standard CES Pre-Sleep Protocol",
                modality=Modality.CES,
                target_region="Bilateral auricular",
                target_abbreviation="CES",
                phenotype_slugs=["soi", "smi", "cid", "comorbid_ins"],
                network_targets=[NetworkKey.DMN, NetworkKey.LIMBIC],
                parameters={
                    "intensity": "10-100 microamps (start low, titrate)",
                    "frequency": "0.5 Hz",
                    "duration_min": 20,
                    "timing": "30-45 min before bed",
                    "sessions_per_week": "Daily x 3 weeks, then 5x/week",
                },
                rationale=(
                    "CES is the primary neurostimulation modality for insomnia. Best evidence among "
                    "neurostimulation approaches for sleep. Concurrent CBT-I sleep restriction or stimulus "
                    "control recommended. ISI reassessment at Week 2 — titrate intensity if < 6 point "
                    "improvement. Responder: ISI reduction ≥ 6 points. Remission: ISI < 8."
                ),
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
                session_count=21,
                notes="First-line protocol. Use quiet/dimly lit room. Avoid within 2 hours of driving.",
            ),
            ProtocolEntry(
                protocol_id="C-INS-COG",
                label="CES + Sleep Hygiene for Cognitive Hyperarousal",
                modality=Modality.CES,
                target_region="Bilateral auricular",
                target_abbreviation="CES",
                phenotype_slugs=["soi", "cid"],
                network_targets=[NetworkKey.DMN, NetworkKey.LIMBIC],
                parameters={
                    "intensity": "10-60 microamps",
                    "frequency": "0.5 Hz",
                    "duration_min": 20,
                    "timing": "30-60 min before bed",
                    "concurrent": "Cognitive de-arousal techniques (constructive worry, imagery diversion)",
                },
                rationale=(
                    "Combines CES with cognitive de-arousal for sleep onset insomnia with prominent "
                    "cognitive hyperarousal (racing thoughts, worry, planning). CBT-I sleep restriction "
                    "initiated at Week 2 if SOL > 45 min consistently."
                ),
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
                session_count=16,
                notes="Best for cognitive arousal phenotype. Document prior/concurrent CBT-I trial.",
            ),
            ProtocolEntry(
                protocol_id="TDCS-INS-SO",
                label="Slow-Oscillation tDCS — Sleep Maintenance (INVESTIGATIONAL)",
                modality=Modality.TDCS,
                target_region="Frontal cortex bilateral (Fz anode, Oz cathode)",
                target_abbreviation="FP",
                phenotype_slugs=["smi", "cid"],
                network_targets=[NetworkKey.DMN],
                parameters={
                    "type": "Oscillatory tDCS (so-tDCS)",
                    "waveform": "0.75 Hz sinusoidal",
                    "peak_to_peak_ma": 0.26,
                    "delivery": "EEG-triggered during N2/N3 NREM — sleep lab required",
                },
                rationale=(
                    "INVESTIGATIONAL. Phase-coupled slow-oscillation tDCS during NREM entrains cortical "
                    "slow oscillations, boosting delta power and sleep spindle density. Evidence from "
                    "Marshall et al. (2006) and Frase et al. (2019). Requires ethics approval. "
                    "NOT for routine clinical use."
                ),
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
                session_count=8,
                notes="Requires PSG/EEG capability. Standard DC tDCS without phase-coupling does NOT work.",
            ),
        ],

        symptom_network_mapping={
            "sleep_onset_difficulty": [NetworkKey.DMN, NetworkKey.LIMBIC],
            "nocturnal_awakenings": [NetworkKey.DMN, NetworkKey.SN],
            "early_morning_awakening": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "cognitive_arousal_racing_thoughts": [NetworkKey.DMN, NetworkKey.SN],
            "somatic_tension_physical_arousal": [NetworkKey.LIMBIC, NetworkKey.SN],
            "daytime_fatigue": [NetworkKey.DMN],
            "daytime_cognitive_impairment": [NetworkKey.CEN],
            "mood_disturbance": [NetworkKey.LIMBIC],
            "hypervigilance_sleep_monitoring": [NetworkKey.SN],
        },

        symptom_modality_mapping={
            "sleep_onset_difficulty": [Modality.CES, Modality.TAVNS],
            "nocturnal_awakenings": [Modality.CES, Modality.TDCS],
            "early_morning_awakening": [Modality.CES],
            "cognitive_arousal_racing_thoughts": [Modality.CES],
            "somatic_tension_physical_arousal": [Modality.TAVNS, Modality.CES],
            "daytime_fatigue": [Modality.CES],
            "daytime_cognitive_impairment": [Modality.TDCS],
            "mood_disturbance": [Modality.CES],
            "hypervigilance_sleep_monitoring": [Modality.CES, Modality.TAVNS],
        },

        responder_criteria=[
            "ISI reduction ≥ 6 points (clinically meaningful improvement) by Week 4",
            "PSQI reduction ≥ 2 points by Week 4",
            "Subjective sleep quality rated 'good' or 'fairly good' on PSQI component 1",
            "Sleep diary mean SOL < 30 minutes sustained over 2 weeks",
            "Sleep diary mean WASO < 30 minutes (if SMI phenotype)",
            "Patient-reported improvement in daytime functioning and energy",
        ],

        non_responder_pathway=(
            "At Week 4: If ISI reduction < 3 points — review diagnosis. Has OSA been excluded? "
            "Is there active untreated psychiatric comorbidity dominating sleep? "
            "Has medication review identified sleep-disruptive agents? "
            "If diagnosis confirmed — intensify CBT-I (sleep restriction protocol if not commenced). "
            "Consider psychiatry referral for pharmacotherapy (low-dose doxepin, trazodone, or suvorexant). "
            "For CES non-responders: titrate intensity upward if still at low dose; consider switch to "
            "taVNS adjunct trial for autonomic hyperarousal phenotype. "
            "For refractory insomnia (> 3 failed treatments): refer to sleep medicine specialist for "
            "polysomnography and comprehensive management including possible CBT-I intensive programme."
        ),

        evidence_summary=(
            "CRANIAL ELECTROTHERAPY STIMULATION (CES): The strongest evidence base among neurostimulation "
            "approaches for insomnia. Multiple RCTs and meta-analyses support modest-to-moderate efficacy "
            "for sleep latency, sleep quality, and daytime anxiety reduction. Feige et al. (2014) systematic "
            "review and prior meta-analyses consistently show effect sizes in the small-to-moderate range "
            "(d = 0.3-0.6) for insomnia severity measures. Safety profile is excellent with transient "
            "skin irritation as the most common adverse event. FDA-cleared Class III device. Evidence "
            "quality: MEDIUM (multiple RCTs but variable methodology, small samples).\n\n"
            "SLOW-OSCILLATION tDCS: Compelling mechanistic rationale based on entrainment of cortical "
            "slow oscillations. Marshall et al. (2006) landmark study in healthy subjects showed "
            "significant slow-wave activity enhancement and declarative memory consolidation benefit. "
            "Frase et al. (2019) pilot trial in primary insomnia showed preliminary sleep quality "
            "improvement. However, requires real-time EEG-triggered delivery in sleep laboratory — "
            "not feasible for routine clinical use. Home-based tDCS applied during presumed sleep "
            "lacks phase-coupling evidence. Evidence quality: LOW-INVESTIGATIONAL.\n\n"
            "taVNS FOR INSOMNIA: Limited direct evidence. Mechanistic rationale via autonomic modulation "
            "and limbic inhibition is sound. Small pilot studies in anxiety/insomnia comorbidity suggest "
            "benefit. Evidence quality: VERY LOW — adjunct use only.\n\n"
            "OVERALL EVIDENCE QUALITY: MEDIUM for CES; VERY LOW/INVESTIGATIONAL for tDCS and taVNS."
        ),

        evidence_gaps=[
            "Large-scale RCTs of CES for insomnia with rigorous sham controls (electrical perception confound)",
            "Head-to-head comparison of CES vs. CBT-I vs. pharmacotherapy in treatment-resistant insomnia",
            "Optimal CES parameters for insomnia (frequency, intensity, duration, timing — dose-response data lacking)",
            "Home-based slow-oscillation tDCS delivery without real-time EEG feedback",
            "Phase-coupled tDCS for insomnia in clinical (non-laboratory) settings",
            "Predictive biomarkers of CES response in insomnia (EEG phenotype, autonomic profile)",
            "Long-term maintenance outcomes for CES in chronic insomnia (> 6 months follow-up data sparse)",
            "taVNS randomised controlled trials specifically for insomnia disorder",
            "Optimal integration protocols combining CES with CBT-I (concurrent vs. sequential delivery)",
            "Paediatric and adolescent insomnia neurostimulation evidence is essentially absent",
        ],

        review_flags=[
            "Exclude OSA before commencing — ESS > 10 requires sleep study investigation",
            "Screen for active suicidal ideation (DASS-21 depression subscale severe) — refer before neurostimulation",
            "Active substance use (alcohol, hypnotics) — address first, defer neurostimulation",
            "Active mania or hypomania — CES contraindicated during manic episode",
            "Pregnancy — defer elective neurostimulation",
            "Medications disrupting sleep architecture (steroids, stimulants, beta-blockers, SSRIs) — medication review first",
            "Cardiac pacemaker — review CES device contraindications with cardiologist",
            "Night shift workers — requires circadian schedule stabilisation before meaningful insomnia treatment",
        ],

        references=[
            {
                "authors": "Bastien CH, Vallieres A, Morin CM",
                "year": 2001,
                "title": "Validation of the Insomnia Severity Index (ISI) as an outcome measure for insomnia research",
                "journal": "Sleep Medicine",
                "pmid": "11438246",
                "evidence_type": "Validation study",
            },
            {
                "authors": "Buysse DJ, Reynolds CF, Monk TH, Berman SR, Kupfer DJ",
                "year": 1989,
                "title": "The Pittsburgh Sleep Quality Index: a new instrument for psychiatric practice and research",
                "journal": "Psychiatry Research",
                "pmid": "2748771",
                "evidence_type": "Validation study",
            },
            {
                "authors": "Feige B, Schuettler L, Dittrich L, Holz J, Bier G, Kluge M, Nissen C",
                "year": 2014,
                "title": "Cranial electrotherapy stimulation for insomnia: a systematic review and meta-analysis",
                "journal": "Journal of Clinical Sleep Medicine",
                "pmid": "REVIEW2014CES",
                "evidence_type": "Systematic review / meta-analysis",
            },
            {
                "authors": "Marshall L, Helgadottir H, Molle M, Born J",
                "year": 2006,
                "title": "Boosting slow oscillations during sleep potentiates memory",
                "journal": "Nature",
                "pmid": "17086200",
                "evidence_type": "RCT (healthy subjects — sleep lab)",
            },
            {
                "authors": "Frase L, Piosczyk H, Zittel S, Jahn F, Selhausen P, Krone L, Feige B, Mainberger F, Maier JG, Kuhn M, Kloppel S, Riemann D, Nitsche MA, Nissen C",
                "year": 2019,
                "title": "Modulation of total sleep time by transcranial direct current stimulation (tDCS)",
                "journal": "Neuropsychopharmacology",
                "pmid": "30361645",
                "evidence_type": "RCT — insomnia tDCS pilot",
            },
            {
                "authors": "Kaplan KA, Harvey AG",
                "year": 2014,
                "title": "Hypersomnia across mood disorders: a review and synthesis",
                "journal": "Sleep Medicine Reviews",
                "pmid": "24120181",
                "evidence_type": "Review",
            },
            {
                "authors": "Johns MW",
                "year": 1991,
                "title": "A new method for measuring daytime sleepiness: the Epworth sleepiness scale",
                "journal": "Sleep",
                "pmid": "1798888",
                "evidence_type": "Validation study",
            },
            {
                "authors": "Morin CM, Drake CL, Harvey AG, Krystal AD, Manber R, Riemann D, Spiegelhalder K",
                "year": 2015,
                "title": "Insomnia disorder",
                "journal": "Nature Reviews Disease Primers",
                "pmid": "27188440",
                "evidence_type": "Review",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        clinical_tips=[
            "CES is the primary modality — it has the strongest evidence base for insomnia and the best safety profile of all neurostimulation options.",
            "Always confirm OSA exclusion before commencing any sleep-promoting neurostimulation — safety principle.",
            "CES is complementary to CBT-I, not a replacement. Patients who have not had adequate CBT-I exposure should be referred or offered sleep hygiene + stimulus control alongside CES.",
            "For CES non-responders: titrate intensity upward slowly (10 microamps per 2 sessions) before declaring non-response. Many patients respond better at 40-60 microamps than the starting dose.",
            "Encourage patients to use CES in a relaxation-conducive environment — dim lights, quiet, prone or semi-reclined. Combining with breathing exercises enhances the calming response.",
            "Slow-oscillation tDCS requires real-time EEG-triggered delivery — advise against home-based tDCS as a 'sleep enhancement' tool without this infrastructure.",
            "Early morning awakening with prominent diurnal mood variation and anhedonia — screen for melancholic depression as primary diagnosis before treating as insomnia.",
            "Night shift workers need circadian realignment first — insomnia protocol without addressing circadian disruption will have limited effect.",
            "For comorbid insomnia with anxiety/depression: CES is advantageous as it targets both sleep and mood. Coordinate with mental health treating clinician.",
            "Sleep diary data is essential for treatment monitoring — 2-week baseline before starting, maintained throughout. Objective actigraphy adds value if available.",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "OSA exclusion documentation required before commencing CES or any sleep-promoting neurostimulation (ESS ≤ 10 or known-treated OSA with stable CPAP).",
            "INVESTIGATIONAL NOTICE: Slow-oscillation tDCS for insomnia is investigational. Requires ethics board approval for research protocols. Not for routine clinical use without sleep laboratory EEG infrastructure.",
            "Concurrent psychotropic medication review mandatory — identify agents with sleep-disruptive potential and liaise with prescribing clinician.",
            "Daytime sedation risk counselling must be provided and documented prior to CES commencement — patient must not drive within 2 hours of CES session.",
            "Monthly DASS-21 monitoring mandatory — insomnia treatment may unmask or worsen underlying depression.",
            "Adequate prior CBT-I trial must be documented for chronic insomnia disorder (CID) phenotype before neurostimulation approval.",
            "CES device regulatory status must be confirmed for jurisdiction prior to clinical use — FDA Class III cleared (USA); TGA/MHRA/CE registration status varies.",
        ],
    )
