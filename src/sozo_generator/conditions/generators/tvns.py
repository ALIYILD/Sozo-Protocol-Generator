"""
Transcutaneous Vagus Nerve Stimulation (tVNS) — Standalone Protocol Generator.
Window 4: Preventive & Adjunct tVNS Protocol.

Primary indications: Subthreshold depression/anxiety, stress resilience, older adults,
Treatment-Resistant Depression (TRD) adjunct.

Key references:
- Hein E et al. (2013) Auricular transcutaneous electrical nerve stimulation in depressed patients —
  a randomized controlled pilot study. J Neural Transm. PMID: 23754493
- Rong P et al. (2016) Effect of transcutaneous auricular vagus nerve stimulation on major depressive
  disorder: A nonrandomized controlled pilot study. J Affect Disord. PMID: 26707088
- Burger AM et al. (2020) Transcutaneous vagus nerve stimulation reduces anxious thinking — Biol Psychol.
  PMID: 31786127
- Jacobs HI et al. (2015) Comfort and efficacy of transcutaneous vagal nerve stimulation in older adults.
  J Geriatr Psychiatry Neurol. PMID: 26491100
- Clancy JA et al. (2014) Non-invasive vagus nerve stimulation in healthy humans reduces sympathetic
  nerve activity. Brain Stimul. PMID: 24909661
- Ylikoski A et al. (2017) Transcutaneous vagus nerve stimulation in tinnitus — Auton Neurosci.
  PMID: 28434889
- Frangos E & Bhatt DL (2017) Non-invasive access to the vagus nerve central projections via electrical
  stimulation of the auricular branch — Bioelectron Med. PMID: 31338118
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
    make_network, make_safety,
    SHARED_ABSOLUTE_CONTRAINDICATIONS, SHARED_SAFETY_NOTES, SHARED_GOVERNANCE_RULES
)

logger = logging.getLogger(__name__)


def build_tvns_condition() -> ConditionSchema:
    """Build the complete tVNS standalone protocol schema."""
    return ConditionSchema(
        slug="tvns",
        display_name="Transcutaneous Vagus Nerve Stimulation — Anxiety, Stress & Preventive Protocol",
        icd10="F41.9",
        aliases=["tVNS", "taVNS", "auricular VNS", "transcutaneous VNS", "non-invasive VNS",
                 "vagus nerve stimulation", "auricular nerve stimulation"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Transcutaneous Vagus Nerve Stimulation (tVNS) delivers low-intensity electrical stimulation "
            "to the auricular branch of the vagus nerve (ABVN) at the cymba concha of the outer ear, or "
            "alternatively via mastoid process electrodes, providing non-invasive access to vagal afferent "
            "pathways without surgical implantation. The ABVN is the sole peripheral branch of the vagus "
            "nerve accessible at the skin surface, projecting centrally via the nucleus tractus solitarius "
            "(NTS) to activate the locus coeruleus (LC), parabrachial nucleus, and limbic structures.\n\n"
            "tVNS has demonstrated preventive and therapeutic utility across anxiety disorders, subthreshold "
            "depression, stress resilience, and as an adjunct in Treatment-Resistant Depression (TRD). "
            "A key advantage over implanted cervical VNS is complete non-invasiveness, enabling home-based "
            "daily use with commercially available devices (Monarch eTNS, Neuvana Xen, Parasym). "
            "FDA breakthrough device designation has been granted for tVNS in depression (Monarch eTNS). "
            "RCT-level evidence supports anxiety reduction (GAD-7), stress biomarker improvement (PSS, HRV), "
            "and early-phase antidepressant effects, particularly in older adults and medication-naive patients."
        ),

        pathophysiology=(
            "The vagus nerve carries approximately 80% afferent (sensory) fibers projecting from the "
            "periphery to the brainstem. The auricular branch (Arnold's nerve) innervates the cymba concha "
            "of the outer ear and projects centrally to the NTS in the dorsal medulla. From NTS, second-order "
            "projections activate:\n\n"
            "1. Locus Coeruleus (LC) — the primary noradrenergic nucleus, projecting widely to prefrontal "
            "cortex, hippocampus, and amygdala. LC activation increases synaptic noradrenaline (NA) at "
            "prefrontal alpha-2A receptors, improving cognitive control and stress resilience. This "
            "replicates the mechanism of noradrenergic antidepressants (venlafaxine, atomoxetine).\n\n"
            "2. Raphe Nuclei — serotonergic nuclei activated by NTS projections, contributing to mood "
            "stabilization and anxiolytic effects. Serotonin release in limbic circuits modulates "
            "amygdala reactivity.\n\n"
            "3. Amygdala and Hippocampus — direct and indirect NTS projections modulate fear circuitry "
            "and hippocampal neuroplasticity. tVNS has been shown to enhance memory consolidation "
            "(Clark et al. 2011) and reduce amygdala hyperreactivity in anxiety.\n\n"
            "4. Default Mode Network (DMN) and Salience Network (SN) — fMRI studies (Frangos et al. 2017) "
            "demonstrate tVNS modulates insular cortex, ACC, and DMN nodes, reducing ruminative activity.\n\n"
            "The parasympathetic/autonomic pathway: tVNS increases HRV (vagal tone marker), reduces "
            "sympathetic hyperactivity, and lowers cortisol — validated stress biomarkers that correlate "
            "with clinical anxiety and depression symptom reduction."
        ),

        core_symptoms=[
            "Anxiety — generalized worry, anticipatory anxiety, somatic anxiety symptoms",
            "Subthreshold depression — persistent low mood below MDD criteria, anhedonia, fatigue",
            "Stress dysregulation — excessive perceived stress, reduced stress resilience, HRV reduction",
            "Autonomic dysregulation — elevated resting heart rate, reduced HRV, sympathetic dominance",
            "Sleep disturbance — anxiety-driven insomnia, hyperarousal, difficulty falling asleep",
            "Emotional dysregulation — irritability, emotional lability, reduced distress tolerance",
            "Cognitive symptoms — concentration difficulties, ruminative thinking, decision fatigue",
        ],

        non_motor_symptoms=[
            "Somatic anxiety manifestations — palpitations, muscle tension, GI symptoms",
            "Fatigue and low energy secondary to chronic stress/anxiety",
            "Social withdrawal and reduced occupational functioning",
            "Anticipatory avoidance behaviors",
            "Comorbid depressive features in generalized anxiety disorder (50-60% co-occurrence)",
        ],

        key_brain_regions=[
            "Nucleus Tractus Solitarius (NTS) — primary brainstem target of auricular VNS afferents",
            "Locus Coeruleus (LC) — noradrenergic nucleus; stress and arousal regulation",
            "Amygdala — fear and anxiety processing; hyperactive in GAD/anxiety disorders",
            "Anterior Cingulate Cortex (ACC) — conflict monitoring, worry regulation",
            "Prefrontal Cortex (PFC) — top-down emotion regulation; NA-dependent",
            "Hippocampus — stress-related neuroplasticity; cortisol-mediated damage in chronic stress",
            "Insular Cortex — interoceptive processing; dysregulated in anxiety and somatic symptoms",
        ],

        brain_region_descriptions={
            "Nucleus Tractus Solitarius (NTS)": "Primary brainstem relay for ABVN afferents. Mediates the central effects of tVNS via ascending projections to LC, raphe, and limbic system. Frangos et al. (2017) confirmed NTS activation on fMRI during auricular tVNS.",
            "Locus Coeruleus (LC)": "Noradrenergic hub activated by NTS. Projects to PFC, hippocampus, and amygdala. LC-NA signaling underlies stress resilience, attention regulation, and the mechanism of noradrenergic antidepressants. Primary mechanistic target of tVNS in depression.",
            "Amygdala": "Hyperactive in anxiety and subthreshold depression. Receives vagal projections via NTS and parabrachial nucleus. tVNS reduces amygdala hyperreactivity and improves fear extinction. Burger et al. (2020) showed tVNS-reduced amygdala-driven anxious thinking.",
            "Anterior Cingulate Cortex (ACC)": "Mediates worry, rumination, and conflict monitoring. Dysregulated in GAD. Receives prefrontal-vagal circuit modulation via tVNS. Relevant to reducing ruminative anxiety.",
            "Prefrontal Cortex (PFC)": "Top-down emotion regulation impaired in anxiety/depression. NA upregulation via LC activation restores PFC inhibitory control over amygdala and limbic hyperreactivity.",
            "Hippocampus": "Stress and HPA axis regulation. Chronic stress causes glucocorticoid-mediated hippocampal neuroplasticity impairment. tVNS may support hippocampal neurogenesis via BDNF upregulation (indirect, animal data).",
            "Insular Cortex": "Interoceptive awareness; dysregulated in anxiety (hypervigilance to bodily sensations). fMRI evidence of insular modulation during tVNS. Relevant to somatic anxiety symptom reduction.",
        },

        network_profiles=[
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN ANXIETY/STRESS. Amygdala-hippocampal-cingulate hyperactivity "
                "drives anxiety, fear, and rumination. tVNS modulates limbic hyperactivity via NTS-LC-amygdala "
                "pathways, reducing threat reactivity and emotional dysregulation. Core mechanism in "
                "anxiety and subthreshold depression.",
                primary=True, severity="severe",
                evidence_note="Burger et al. (2020) Biol Psychol; Frangos et al. (2017) Bioelectron Med",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "Salience network hyperactivity in anxiety causes excessive threat detection and "
                "misattribution of neutral stimuli as threatening. Insular and ACC dysregulation "
                "contribute to autonomic hyperarousal. tVNS modulates SN via insular cortex and "
                "ACC projections, reducing hypervigilance.",
                severity="moderate",
                evidence_note="Insular/ACC modulation during tVNS on fMRI",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation in anxiety and depression drives ruminative, self-referential "
                "negative thought patterns. tVNS demonstrated to reduce DMN hyperconnectivity "
                "in fMRI studies. Key mechanism for reducing worry and ruminative anxiety.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "CEN hypofunction impairs top-down cognitive control over emotional reactivity. "
                "NA upregulation via LC activation partially restores prefrontal executive control "
                "over amygdala and DMN. Relevant to improving cognitive aspects of anxiety.",
                severity="mild",
            ),
        ],

        primary_network=NetworkKey.LIMBIC,

        fnon_rationale=(
            "In anxiety and stress disorders, the primary dysfunctional network is the Limbic System, "
            "with amygdala-hippocampal-cingulate hyperactivity driving fear, worry, and autonomic "
            "dysregulation. tVNS targets this network via the NTS-LC-amygdala pathway — upregulating "
            "noradrenaline and serotonin in limbic circuits without pharmacological side effects. "
            "The FNON framework positions tVNS as a neuromodulatory intervention targeting the "
            "limbic-SN hyperactivation cluster, complementary to CBT (cognitive reframing via CEN "
            "restoration) and medication (pharmacological monoamine upregulation)."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="gad",
                label="Generalized Anxiety Disorder",
                description="Persistent, excessive worry across multiple domains. GAD-7 ≥10. "
                            "Autonomic hyperarousal with reduced HRV. Responds well to tVNS "
                            "cymba concha protocol with daily dosing.",
                key_features=["Persistent worry", "Muscle tension", "Autonomic hyperarousal",
                               "Sleep difficulty", "Concentration impairment", "Reduced HRV"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                preferred_modalities=[Modality.TAVNS, Modality.CES],
                tdcs_target=None,
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="subthreshold_dep",
                label="Subthreshold Depression / Stress Resilience",
                description="Persistent low mood below MDD criteria (PHQ-9 5-9), elevated perceived "
                            "stress (PSS ≥14), fatigue, and reduced hedonic capacity. Preventive "
                            "indication — tVNS suitable before progression to clinical MDD.",
                key_features=["Low mood", "Fatigue", "Elevated PSS", "Reduced hedonic capacity",
                               "Sleep disruption", "Subthreshold anhedonia"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.DMN],
                secondary_networks=[NetworkKey.CEN, NetworkKey.SN],
                preferred_modalities=[Modality.TAVNS],
                tdcs_target=None,
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="trd_adjunct",
                label="Treatment-Resistant Depression — tVNS Adjunct",
                description="MDD failing ≥2 adequate antidepressant trials (TRD). tVNS as adjunct "
                            "to ongoing medication or tDCS. FDA breakthrough designation (Monarch eTNS). "
                            "Noradrenergic augmentation mechanism.",
                key_features=["TRD (≥2 failed trials)", "Prominent anhedonia",
                               "Residual depressive symptoms on medication", "Emotional blunting"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.CEN, NetworkKey.DMN],
                secondary_networks=[NetworkKey.SN],
                preferred_modalities=[Modality.TAVNS, Modality.TDCS],
                tdcs_target="Left DLPFC anodal (F3) — combine with tVNS adjunct",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="older_adult",
                label="Older Adults — Anxiety / Preventive",
                description="Adults ≥65 with anxiety, stress-related symptoms, or mild cognitive "
                            "concerns. tVNS well-tolerated in older adults (Jacobs et al. 2015). "
                            "Particularly relevant given contraindications to anxiolytics and "
                            "SSRIs in elderly.",
                key_features=["Anxiety in older adult", "Medication intolerance/contraindication",
                               "Reduced HRV", "Mild cognitive symptoms", "Social isolation-related stress"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                secondary_networks=[NetworkKey.CEN],
                preferred_modalities=[Modality.TAVNS, Modality.CES],
                tdcs_target=None,
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="gad7",
                name="Generalized Anxiety Disorder 7-item Scale",
                abbreviation="GAD-7",
                domains=["anxiety", "worry", "autonomic_arousal", "somatic_anxiety"],
                timing="baseline",
                evidence_pmid="16717171",
                notes="Primary anxiety outcome measure. Score ≥10 = moderate anxiety. Score ≥15 = severe. "
                      "Minimum clinically important difference (MCID): 4 points. Repeat at Week 4 and endpoint.",
            ),
            AssessmentTool(
                scale_key="pss",
                name="Perceived Stress Scale",
                abbreviation="PSS-10",
                domains=["stress", "perceived_control", "stress_resilience"],
                timing="baseline",
                evidence_pmid="3944710",
                notes="10-item perceived stress scale. Score 0-40. Scores ≥20 = high stress. "
                      "Key tVNS outcome measure for stress resilience indications. "
                      "Cohen et al. (1983). Validated in preventive populations.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression", "anhedonia", "neurovegetative"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Screen for comorbid or subthreshold depression. PHQ-9 5-9 = subthreshold depression "
                      "(preventive indication). Score ≥10 = moderate MDD. Monitor for TRD adjunct phenotype.",
            ),
            AssessmentTool(
                scale_key="hrv",
                name="Heart Rate Variability — SDNN/RMSSD",
                abbreviation="HRV",
                domains=["autonomic_function", "vagal_tone", "stress_biomarker"],
                timing="baseline",
                evidence_pmid="24909661",
                notes="Objective autonomic biomarker of vagal tone. RMSSD <20ms = severely reduced HRV. "
                      "Clancy et al. (2014) demonstrated tVNS increases HRV in healthy adults. "
                      "Use 5-min resting ECG recording. Correlates with tVNS response.",
            ),
            AssessmentTool(
                scale_key="psqi",
                name="Pittsburgh Sleep Quality Index",
                abbreviation="PSQI",
                domains=["sleep_quality", "sleep_latency", "sleep_disturbance"],
                timing="baseline",
                evidence_pmid="2748771",
                notes="7-component sleep quality assessment. Global PSQI >5 = poor sleep quality. "
                      "Monitors sleep improvement secondary to anxiety/stress reduction.",
            ),
        ],

        baseline_measures=[
            "GAD-7 (primary anxiety outcome — 7 items, 0-21)",
            "PSS-10 (perceived stress — preventive and stress resilience indication)",
            "PHQ-9 (comorbid/subthreshold depression screen)",
            "HRV — 5-min resting RMSSD/SDNN (objective vagal tone biomarker)",
            "PSQI (sleep quality at baseline)",
            "SOZO PRS — anxiety, mood, sleep, energy domains (0-10 each)",
            "Medication and supplement list at baseline (beta-blockers, SSRIs, anxiolytics — note interactions)",
        ],

        followup_measures=[
            "GAD-7 at Week 2, Week 4, and endpoint (primary outcome)",
            "PSS-10 at Week 4 and endpoint",
            "PHQ-9 at Week 4 and endpoint (depression monitoring)",
            "HRV at Week 4 and endpoint (if available)",
            "SOZO PRS at every session (brief) and end of block (full)",
            "Adverse event documentation at every session (skin irritation, headache, auricular discomfort)",
        ],

        inclusion_criteria=[
            "Age ≥18 years (≥16 with parental consent for adolescent anxiety)",
            "Primary anxiety (GAD-7 ≥7) OR subthreshold depression (PHQ-9 5-9) OR elevated stress (PSS ≥14)",
            "OR: MDD with ≥2 failed antidepressant trials (TRD adjunct phenotype)",
            "Capacity to provide informed consent and operate home tVNS device",
            "Adequate auricular skin integrity at cymba concha/mastoid electrode sites",
            "Stable pharmacotherapy for ≥4 weeks prior to starting (if on medication)",
        ],

        exclusion_criteria=[
            "Cardiac pacemaker or implanted cardiac defibrillator (absolute — vagal cardiac effects)",
            "Vagotomy or prior cervical VNS implant",
            "Acute psychiatric crisis (psychosis, active suicidality requiring hospitalization)",
            "Epilepsy (relative contraindication — tVNS may lower seizure threshold in susceptible individuals)",
            "Active dermatological condition or wound at electrode placement site",
            "Bradycardia (resting HR <50 bpm) or atrioventricular block (vagal cardiac safety)",
            "Carotid artery disease or carotid hypersensitivity",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS + [
            "Cardiac pacemaker or implantable cardioverter-defibrillator (absolute — vagal cardiac modulation)",
            "Bradycardia (<50 bpm) or known AV block",
            "History of vagotomy",
            "Carotid sinus hypersensitivity",
        ],

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "contraindication",
                "Cardiac pacemaker or ICD: absolute contraindication. tVNS modulates cardiac autonomic "
                "tone via vagal efferents. Risk of device interference and arrhythmia induction.",
                "absolute",
                "FDA device safety guidance; Clancy et al. (2014) autonomic effects of tVNS",
            ),
            make_safety(
                "precaution",
                "Titrate intensity to sensory threshold — slight tingling/paresthesia at electrode site. "
                "Never exceed pain threshold. Asymmetric biphasic waveform (120 Hz, 250 μs) is the "
                "standard validated waveform. Verify device parameters before each session block.",
                "moderate",
                "Burger et al. (2020); device manufacturer specifications for Monarch, Neuvana, Parasym",
            ),
            make_safety(
                "monitoring",
                "Monitor for auricular skin irritation at electrode contact sites after every session. "
                "Inspect cymba concha and surrounding auricular skin. Discontinue and allow recovery "
                "if Grade 2 or higher skin reaction observed.",
                "moderate",
                "tVNS safety monitoring consensus; home-use protocol guidelines",
            ),
            make_safety(
                "precaution",
                "In older adults (≥65): titrate intensity conservatively. Use cymba concha placement "
                "preferentially — lower impedance, more tolerable. Jacobs et al. (2015) confirmed "
                "tolerability in geriatric population.",
                "low",
                "Jacobs HI et al. (2015) J Geriatr Psychiatry Neurol. PMID: 26491100",
            ),
            make_safety(
                "precaution",
                "Sham protocol: use earlobe (non-ABVN) electrode placement at identical intensity. "
                "Ramp-up/ramp-down over 30s to blind participants. Active cymba concha vs sham earlobe "
                "is the validated sham-controlled design in published trials.",
                "low",
                "Hein et al. (2013); Burger et al. (2020) sham-controlled design",
            ),
        ],

        stimulation_targets=[
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Auricular branch of vagus nerve — cymba concha",
                target_abbreviation="ABVN-CC",
                laterality="left",
                rationale="Cymba concha of the outer ear provides the most direct and dense ABVN "
                          "innervation. Left cymba concha is the standard validated placement in "
                          "published RCTs (Hein 2013, Rong 2016, Burger 2020). ABVN projects to NTS → "
                          "LC → amygdala/PFC pathway. Primary placement for anxiety, depression, TRD.",
                protocol_label="tVNS-CC — Standard Cymba Concha Protocol",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=True,
            ),
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Auricular branch of vagus nerve — mastoid process",
                target_abbreviation="ABVN-MA",
                laterality="left",
                rationale="Mastoid process electrode placement accesses ABVN skin projections posterior "
                          "to the ear. Used in Monarch eTNS (FDA-cleared) device. Comparable clinical "
                          "outcomes to cymba concha in some trials. Alternative for patients with "
                          "auricular anatomy limitations.",
                protocol_label="tVNS-MA — Mastoid Process Protocol",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="tVNS-CC-STD",
                label="tVNS Cymba Concha — Standard Anxiety/Stress Protocol",
                modality=Modality.TAVNS,
                target_region="Cymba concha (auricular branch of vagus nerve)",
                target_abbreviation="ABVN-CC",
                phenotype_slugs=["gad", "subthreshold_dep", "older_adult"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN, NetworkKey.DMN],
                parameters={
                    "device": "Neuvana Xen or Parasym Ear",
                    "electrode_placement": "Left cymba concha (primary); right cymba concha (bilateral protocol)",
                    "waveform": "Asymmetric biphasic square wave",
                    "frequency": "120 Hz",
                    "pulse_width": "250 μs",
                    "intensity": "Sensory threshold — slight paresthesia, not painful (typically 0.5–3.0 mA)",
                    "session_duration": "30–60 min",
                    "schedule": "Daily or 5×/week × 4–8 weeks",
                    "maintenance": "3×/week after initial block for sustained benefit",
                    "titration": "Start at 0.5 mA; increase in 0.25 mA steps until paresthesia threshold",
                    "sham_control": "Earlobe (non-ABVN) placement at identical intensity — validated sham",
                },
                rationale="Left cymba concha placement activates ABVN most densely. Standard 120 Hz / 250 μs "
                          "parameters are derived from implanted cervical VNS literature (Groves & Brown 2005) "
                          "and validated in auricular tVNS RCTs. Burger et al. (2020) demonstrated reduced "
                          "anxious thinking and amygdala reactivity. Hein et al. (2013) showed significant "
                          "antidepressant effect vs sham in depressed patients. Daily dosing replicates "
                          "clinical VNS protocols and supports cumulative neuroplastic adaptation.",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=True,
                session_count=28,
                notes="Optimize intensity to consistent sensory threshold across sessions. "
                      "Document paresthesia threshold at each session — threshold may decrease as tolerance "
                      "develops (indicates electrode-skin contact change, not adaptation).",
            ),
            ProtocolEntry(
                protocol_id="tVNS-MA-FDA",
                label="tVNS Mastoid — Monarch eTNS Protocol (FDA Breakthrough)",
                modality=Modality.TAVNS,
                target_region="Mastoid process / auricular branch",
                target_abbreviation="ABVN-MA",
                phenotype_slugs=["trd_adjunct", "subthreshold_dep"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "device": "Monarch eTNS System (electroCore) — FDA Breakthrough Device",
                    "electrode_placement": "Bilateral mastoid process or left cymba concha",
                    "waveform": "Asymmetric biphasic",
                    "frequency": "120 Hz",
                    "pulse_width": "250 μs",
                    "intensity": "Sensory threshold (titrated per session)",
                    "session_duration": "60 min",
                    "schedule": "Nightly × 8 weeks (home-based)",
                    "combination": "Adjunct to ongoing antidepressant medication or tDCS block",
                    "app_supervision": "Monarch app — adherence tracking, session logging",
                },
                rationale="Monarch eTNS received FDA Breakthrough Device designation for MDD, with TRD adjunct "
                          "as primary indication. Mastoid placement provides ABVN access posterior to auricle. "
                          "Nightly home-based protocol enables high cumulative dose. Combination with DLPFC "
                          "tDCS provides dual-pathway upregulation: LC-NA (tVNS) + direct DLPFC facilitation "
                          "(tDCS). Rong et al. (2016) nonrandomized pilot: significant HAMD-17 reduction in "
                          "MDD patients vs sham.",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
                session_count=56,
                notes="FDA Breakthrough Device designation does not constitute FDA clearance/approval. "
                      "Use within clinical trial or off-label with informed consent until full clearance.",
            ),
            ProtocolEntry(
                protocol_id="tVNS-PREV",
                label="tVNS Preventive Protocol — Stress Resilience",
                modality=Modality.TAVNS,
                target_region="Cymba concha (auricular branch of vagus nerve)",
                target_abbreviation="ABVN-CC",
                phenotype_slugs=["subthreshold_dep", "older_adult"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Neuvana Xen, Parasym, or equivalent CE/FDA-cleared device",
                    "electrode_placement": "Left cymba concha",
                    "frequency": "120 Hz",
                    "pulse_width": "250 μs",
                    "intensity": "Sub-sensory to sensory threshold (0.25–1.0 mA)",
                    "session_duration": "30 min",
                    "schedule": "Daily × 4 weeks, then 3×/week maintenance",
                    "target_population": "Subthreshold stress/depression (PSS ≥14, PHQ-9 5-9)",
                    "outcome_target": "PSS reduction ≥5 points; GAD-7 prevention of escalation",
                },
                rationale="Preventive tVNS protocol targets subclinical stress/anxiety before progression to "
                          "clinical disorder. Lower intensity (sub-sensory) may be adequate for autonomic "
                          "modulation in non-clinical populations. Clancy et al. (2014) demonstrated HRV "
                          "improvement with low-intensity auricular stimulation in healthy adults. "
                          "Scalable home-based model supports preventive mental health applications. "
                          "PSS and HRV serve as biomarkers for early treatment response.",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
                session_count=20,
            ),
            ProtocolEntry(
                protocol_id="tVNS-COMB",
                label="tVNS + tDCS Combination — TRD & Severe Anxiety",
                modality=Modality.MULTIMODAL,
                target_region="Cymba concha + Left DLPFC",
                target_abbreviation="ABVN+DLPFC",
                phenotype_slugs=["trd_adjunct"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.CEN, NetworkKey.DMN],
                parameters={
                    "modality_1": "tVNS — cymba concha, 120 Hz, 250 μs, sensory threshold, 30 min",
                    "modality_2": "tDCS — left DLPFC anodal (F3), 2 mA, 20 min",
                    "sequencing": "tVNS 10 min before tDCS, continue tVNS concurrent with tDCS",
                    "schedule": "5×/week × 4 weeks, then 3×/week × 2 weeks",
                    "combination_rationale": "tVNS primes LC-NA (noradrenergic); tDCS directly upregulates DLPFC CEN",
                },
                rationale="Sequential multimodal protocol addresses both limbic hyperactivity (tVNS via "
                          "NTS-LC) and DLPFC hypofunction (tDCS direct anodal facilitation) — dual-mechanism "
                          "approach for TRD. Theoretical synergy: NA upregulation (tVNS) improves signal-to-noise "
                          "ratio in PFC during tDCS. No published RCT for this combination; mechanism-based "
                          "rationale from component evidence.",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
                session_count=30,
                notes="Combination protocol — off-label. Requires Doctor authorization and enhanced monitoring. "
                      "Document both modalities separately on session log.",
            ),
        ],

        symptom_network_mapping={
            "Anxiety": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Worry/Rumination": [NetworkKey.DMN, NetworkKey.LIMBIC],
            "Autonomic Hyperarousal": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Subthreshold Depression": [NetworkKey.LIMBIC, NetworkKey.DMN, NetworkKey.CEN],
            "Sleep Disturbance": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Stress Dysregulation": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Emotional Dysregulation": [NetworkKey.LIMBIC, NetworkKey.CEN],
        },

        symptom_modality_mapping={
            "Anxiety": [Modality.TAVNS, Modality.CES],
            "Worry/Rumination": [Modality.TAVNS],
            "Autonomic Hyperarousal": [Modality.TAVNS],
            "Subthreshold Depression": [Modality.TAVNS, Modality.TDCS],
            "Sleep Disturbance": [Modality.TAVNS, Modality.CES],
            "Stress Dysregulation": [Modality.TAVNS],
            "Emotional Dysregulation": [Modality.TAVNS, Modality.TDCS],
        },

        responder_criteria=[
            "≥50% reduction in GAD-7 from baseline at Week 4 (primary responder criterion)",
            "GAD-7 score <7 at endpoint (remission criterion)",
            "≥5-point reduction in PSS-10 from baseline",
            "Clinically meaningful HRV improvement (RMSSD increase ≥10ms) at endpoint",
            "Clinically meaningful improvement in SOZO PRS anxiety domain (≥3 points on 0-10 scale)",
        ],

        non_responder_pathway=(
            "For patients classified as non-responders at Week 4 (GAD-7 reduction <30%):\n"
            "1. Verify electrode placement accuracy — cymba concha vs earlobe (common error)\n"
            "2. Re-titrate intensity — confirm sensory paresthesia threshold at current session\n"
            "3. Verify device waveform parameters (120 Hz, 250 μs, asymmetric biphasic)\n"
            "4. Assess adherence — review session completion log\n"
            "5. Switch to bilateral placement (right + left cymba concha) for non-responders\n"
            "6. Add CES (Alpha-Stim) for comorbid insomnia/anxiety — complementary mechanism\n"
            "7. Add tDCS (DLPFC anodal) for TRD adjunct non-responders\n"
            "8. Doctor review for pharmacotherapy optimization\n"
            "9. Refer for psychological assessment if comorbid anxiety disorder not previously treated"
        ),

        evidence_summary=(
            "GRADE EVIDENCE ASSESSMENT — tVNS for Anxiety, Stress & Preventive Indications:\n\n"

            "1. tVNS for Depression (GRADE: LOW–MODERATE certainty):\n"
            "   Tan et al. (2023) meta-analysis of 12 RCTs (N=838): taVNS significantly improved "
            "   HAMD scores; comparable response rates to antidepressants; fewer side effects when "
            "   combined with medication. Li et al. (2021) sham-controlled RCT (N=107): taVNS "
            "   produced comparable HAM-D reduction to citalopram over 12 weeks, with higher remission "
            "   rates at weeks 4 and 6. Hein et al. (2013) pilot RCT (N=37): BDI improvement vs sham "
            "   (−12.6 vs −4.4 points). Rong et al. (2016) non-randomized pilot (N=160): HAMD-17 "
            "   reduction with 12-week self-administered home taVNS.\n\n"

            "2. tVNS for Anxiety (GRADE: LOW certainty):\n"
            "   Burger et al. (2020) sham-controlled RCT: reduced anxious thinking and amygdala-"
            "   prefrontal connectivity. Yap et al. (2020) critical review: effect size g=0.60 vs "
            "   sham across anxiety-related outcomes. Austelle et al. (2025) iWAVE pilot (N=10): "
            "   accelerated taVNS (9 sessions/3 days or 9 sessions/1 day) significantly reduced "
            "   GAD-7 (mean −5.9) and BAI in inpatient psychiatric setting. No large GAD-specific "
            "   sham-controlled RCT using GAD-7 as primary outcome yet published.\n\n"

            "3. Safety (GRADE: HIGH certainty for safety):\n"
            "   Kim et al. (2022) systematic review and meta-analysis (N=6,322 subjects, 177 studies): "
            "   no causal relationship between taVNS and serious adverse events; incidence rate "
            "   12.84/100,000 person-minutes; most common AEs — ear pain, headache, tingling. "
            "   Redgrave et al. (2018) systematic review (N=1,322): most common AEs skin irritation "
            "   (18.2%), headache (3.6%); only 2.6% dropout due to side effects. "
            "   Giraudier et al. (2025) pooled analysis (N=488): minimal/mild side effects only; "
            "   interval stimulation reduces AE likelihood vs continuous.\n\n"

            "4. Stimulation Site Optimization (GRADE: MODERATE for cymba concha superiority):\n"
            "   Yakunina et al. (2017) fMRI study (N=37): cymba concha produced strongest NTS and "
            "   LC activation vs tragus, ear canal, and earlobe (sham). Gerges et al. (2024) scoping "
            "   review (109 studies, 21 populations): cymba concha and tragus are primary sites; "
            "   reporting of parameters is inconsistent across the field. Kreisberg et al. (2021) "
            "   computational modelling: electrode montage is critical for target selectivity; "
            "   cymba concha montages are selective for ABVN.\n\n"

            "5. Parameter Optimization (GRADE: LOW certainty):\n"
            "   Badran et al. (2018): 500 μs/10 Hz and 500 μs/25 Hz produce greatest HR reduction. "
            "   Machetanz et al. (2021): cymba concha and fossa triangularis show strongest HRV "
            "   response; charge-dependent effect; left ear preferred. Atanackov et al. (2025) "
            "   RCT (N=78): 10 Hz/250 μs, 10 Hz/500 μs, and 25 Hz/100 μs most effective for SDNN "
            "   increase. Gerges et al. (2024) cortical excitability study: 60 min taVNS (not 30 min) "
            "   required for significant GABAergic/glutamatergic cortical modulation.\n\n"

            "6. HRV as Biomarker (GRADE: MODERATE for mechanistic validity):\n"
            "   Clancy et al. (2014): tVNS increases HRV in healthy adults — confirmed autonomic "
            "   mechanism. Ylikoski et al. (2020) tinnitus/stress cohort (N=171): test-taVNS shifted "
            "   HRV toward parasympathetic in 80% of patients. Austelle et al. (2023): taVNS attenuated "
            "   HR response to cold pressor test vs sham (Δ12.75 vs Δ16.09 bpm, p=0.044). "
            "   Tarasenko et al. (2022): LF/HF ratio reduced during taVNS stress exposure — "
            "   counters sympathetic activation. Drost et al. (2025): taVNS increased HRV during "
            "   mental stress task; improved autonomic regulation in healthy adults.\n\n"

            "Overall GRADE: MODERATE certainty for safety; LOW–MODERATE for efficacy in depression; "
            "LOW for anxiety (no powered GAD-specific RCT). Cymba concha at 25 Hz / 250–500 μs "
            "/ sensory threshold is the most evidence-grounded parameter set."
        ),

        evidence_gaps=[
            "No powered sham-controlled RCT of taVNS for GAD with GAD-7 as primary outcome (Lai 2025 trial in progress)",
            "Optimal session duration: 30 vs 60 min — Gerges 2024 shows cortical effects require ≥60 min; clinical trials used 30–60 min",
            "Optimal frequency: 10 Hz vs 25 Hz vs 120 Hz — no definitive head-to-head clinical trial in psychiatric populations",
            "Left vs right ear placement superiority: Machetanz 2021 shows right-left HRV difference; clinical significance unclear",
            "Long-term maintenance after treatment block — no RCT data beyond 3 months post-treatment",
            "tVNS + tDCS combination — no published RCT; mechanism-based rationale only (both in development)",
            "Preventive efficacy in subthreshold populations — no large RCT; pilot data only",
            "Sub-sensory vs sensory-threshold dosing for non-clinical/preventive populations not resolved",
            "Blinding validity of earlobe sham — Gerges 2024 shows 96% of participants detect active stimulation",
            "Interval vs continuous stimulation: Giraudier 2025 shows fewer AEs with interval; clinical equivalence unproven",
            "HRV as a prospective response predictor — preliminary correlation only (Ylikoski 2020)",
        ],

        references=[
            # ── Efficacy — Depression ────────────────────────────────────────
            {
                "authors": "Tan C et al.",
                "year": 2023,
                "title": "The efficacy and safety of transcutaneous auricular vagus nerve stimulation in the treatment of depressive disorder: A systematic review and meta-analysis",
                "journal": "Journal of Affective Disorders",
                "pmid": "36336092",
                "grade": "LOW–MODERATE",
                "evidence_type": "meta-analysis",
                "note": "12 RCTs, N=838; taVNS superior to sham; comparable to antidepressants",
            },
            {
                "authors": "Li S et al.",
                "year": 2021,
                "title": "Comparative Effectiveness of Transcutaneous Auricular Vagus Nerve Stimulation vs Citalopram for Major Depressive Disorder: A Randomized Trial",
                "journal": "Neuromodulation",
                "pmid": "33973320",
                "grade": "LOW",
                "evidence_type": "rct",
                "note": "N=107; taVNS comparable to citalopram; higher remission at weeks 4 and 6",
            },
            {
                "authors": "Hein E et al.",
                "year": 2013,
                "title": "Auricular transcutaneous electrical nerve stimulation in depressed patients: a randomized controlled pilot study",
                "journal": "Journal of Neural Transmission",
                "pmid": "23754493",
                "grade": "LOW",
                "evidence_type": "rct",
                "note": "N=37; BDI reduction −12.6 vs −4.4 (sham); first RCT of auricular tVNS in depression",
            },
            {
                "authors": "Rong P et al.",
                "year": 2016,
                "title": "Effect of transcutaneous auricular vagus nerve stimulation on major depressive disorder",
                "journal": "Journal of Affective Disorders",
                "pmid": "26707088",
                "grade": "LOW",
                "evidence_type": "controlled_trial",
                "note": "N=160; 12-week home taVNS; HAMD-17 improvement; non-randomized",
            },
            {
                "authors": "Kong J et al.",
                "year": 2018,
                "title": "Treating Depression with Transcutaneous Auricular Vagus Nerve Stimulation: State of the Art and Future Perspectives",
                "journal": "Frontiers in Psychiatry",
                "pmid": "29967578",
                "grade": "NARRATIVE",
                "evidence_type": "narrative_review",
                "note": "Mechanism hypotheses; symptom subscale re-analysis; future directions",
            },
            # ── Efficacy — Anxiety ────────────────────────────────────────────
            {
                "authors": "Austelle CW et al.",
                "year": 2025,
                "title": "Accelerated Transcutaneous Auricular Vagus Nerve Stimulation for Inpatient Depression and Anxiety: The iWAVE Open Label Pilot Trial",
                "journal": "Neuromodulation",
                "pmid": "39864471",
                "grade": "VERY LOW (open-label)",
                "evidence_type": "pilot_rct",
                "note": "N=10; accelerated taVNS (9 sessions); GAD-7 −5.9, PHQ-9 −6.0; inpatient setting",
            },
            {
                "authors": "Yap JYY et al.",
                "year": 2020,
                "title": "Critical Review of Transcutaneous Vagus Nerve Stimulation: Challenges for Translation to Clinical Practice",
                "journal": "Frontiers in Neuroscience",
                "pmid": "32116503",
                "grade": "NARRATIVE",
                "evidence_type": "critical_review",
                "note": "Effect size g=0.60 for anxiety outcomes vs sham across tVNS trials",
            },
            # ── Safety ────────────────────────────────────────────────────────
            {
                "authors": "Kim AY et al.",
                "year": 2022,
                "title": "Safety of transcutaneous auricular vagus nerve stimulation (taVNS): a systematic review and meta-analysis",
                "journal": "Scientific Reports",
                "pmid": "35236887",
                "grade": "HIGH (safety)",
                "evidence_type": "systematic_review_meta-analysis",
                "note": "N=6322, 177 studies; AE rate 12.84/100k person-min; no serious AEs caused by taVNS",
            },
            {
                "authors": "Redgrave J et al.",
                "year": 2018,
                "title": "Safety and tolerability of Transcutaneous Vagus Nerve stimulation in humans; a systematic review",
                "journal": "Brain Stimulation",
                "pmid": "29289458",
                "grade": "HIGH (safety)",
                "evidence_type": "systematic_review",
                "note": "N=1322; skin irritation 18.2%, headache 3.6%; 2.6% dropout; no SAEs attributed to tVNS",
            },
            {
                "authors": "Giraudier M et al.",
                "year": 2025,
                "title": "A pooled analysis of the side effects of non-invasive Transcutaneous Auricular Vagus Nerve Stimulation (taVNS)",
                "journal": "Frontiers in Human Neuroscience",
                "pmid": "39882501",
                "grade": "HIGH (safety)",
                "evidence_type": "pooled_analysis",
                "note": "N=488; interval stimulation reduces AEs; side effects mild and transient",
            },
            # ── Stimulation Site Optimization ─────────────────────────────────
            {
                "authors": "Yakunina N et al.",
                "year": 2017,
                "title": "Optimization of Transcutaneous Vagus Nerve Stimulation Using Functional MRI",
                "journal": "Neuromodulation",
                "pmid": "27535566",
                "grade": "MODERATE",
                "evidence_type": "rct_fmri",
                "note": "N=37; cymba concha produces strongest NTS and LC activation vs tragus/ear canal/earlobe",
            },
            {
                "authors": "Gerges ANH et al.",
                "year": 2024,
                "title": "Clinical application of transcutaneous auricular vagus nerve stimulation: a scoping review",
                "journal": "Disability and Rehabilitation",
                "pmid": "38551133",
                "grade": "MODERATE (scoping)",
                "evidence_type": "scoping_review",
                "note": "109 studies, 21 populations; cymba concha + tragus primary sites; parameter reporting inconsistent",
            },
            {
                "authors": "Kreisberg E et al.",
                "year": 2021,
                "title": "High-resolution computational modeling of the current flow in the outer ear during transcutaneous auricular Vagus Nerve Stimulation (taVNS)",
                "journal": "Brain Stimulation",
                "pmid": "33892191",
                "grade": "MECHANISTIC",
                "evidence_type": "computational_model",
                "note": "Cymba concha montage selective for ABVN; electrode size/placement critical for targeting",
            },
            # ── Parameter Optimization ────────────────────────────────────────
            {
                "authors": "Badran BW et al.",
                "year": 2018,
                "title": "Short trains of transcutaneous auricular vagus nerve stimulation (taVNS) have parameter-specific effects on heart rate",
                "journal": "Brain Stimulation",
                "pmid": "29174580",
                "grade": "LOW–MODERATE",
                "evidence_type": "rct",
                "note": "N=35; 500μs/10Hz and 500μs/25Hz produce greatest HR reduction vs sham",
            },
            {
                "authors": "Machetanz K et al.",
                "year": 2021,
                "title": "Transcutaneous auricular vagus nerve stimulation and heart rate variability: Analysis of parameters and targets",
                "journal": "Autonomic Neuroscience",
                "pmid": "34243032",
                "grade": "LOW",
                "evidence_type": "controlled_crossover",
                "note": "N=13; 6 sites tested; cymba concha and fossa triangularis strongest HRV effect; charge-dependent; left ear preferred",
            },
            {
                "authors": "Atanackov P et al.",
                "year": 2025,
                "title": "The Acute Effects of Varying Frequency and Pulse Width of Transcutaneous Auricular Vagus Nerve Stimulation on Heart Rate Variability in Healthy Adults: A Randomized Crossover Controlled Trial",
                "journal": "Biomedicines",
                "pmid": "40002776",
                "grade": "LOW",
                "evidence_type": "rct_crossover",
                "note": "N=78; 10Hz/250μs, 10Hz/500μs, 25Hz/100μs most effective for SDNN; no RMSSD changes",
            },
            {
                "authors": "Badran BW et al.",
                "year": 2019,
                "title": "Laboratory Administration of Transcutaneous Auricular Vagus Nerve Stimulation (taVNS): Technique, Targeting, and Considerations",
                "journal": "Journal of Visualized Experiments",
                "pmid": "31107453",
                "grade": "GUIDANCE",
                "evidence_type": "methods_paper",
                "note": "Standard technique, targeting, and intensity titration protocol reference",
            },
            # ── HRV Biomarker ─────────────────────────────────────────────────
            {
                "authors": "Clancy JA et al.",
                "year": 2014,
                "title": "Non-invasive vagus nerve stimulation in healthy humans reduces sympathetic nerve activity",
                "journal": "Brain Stimulation",
                "pmid": "24909661",
                "grade": "MODERATE",
                "evidence_type": "controlled_trial",
                "note": "HRV increase confirmed; sympathetic suppression; validated autonomic mechanism of tVNS",
            },
            {
                "authors": "Ylikoski J et al.",
                "year": 2020,
                "title": "Stress and Tinnitus; Transcutaneous Auricular Vagal Nerve Stimulation Attenuates Tinnitus-Triggered Stress Reaction",
                "journal": "Frontiers in Psychology",
                "pmid": "32153454",
                "grade": "LOW",
                "evidence_type": "retrospective_cohort",
                "note": "N=171; 80% shifted toward parasympathetic HRV; best effect in low-baseline-HRV group",
            },
            {
                "authors": "Austelle CW et al.",
                "year": 2023,
                "title": "Transcutaneous Auricular Vagus Nerve Stimulation Attenuates Early Increases in Heart Rate Associated With the Cold Pressor Test",
                "journal": "Neuromodulation",
                "pmid": "36806124",
                "grade": "LOW",
                "evidence_type": "rct_crossover",
                "note": "N=24; taVNS attenuated acute sympathetic HR response vs sham (p=0.044)",
            },
            {
                "authors": "Drost L et al.",
                "year": 2025,
                "title": "Effects of taVNS on physiological responses and cognitive performance during a mental stressor",
                "journal": "Cognitive, Affective & Behavioral Neuroscience",
                "pmid": "39843766",
                "grade": "LOW",
                "evidence_type": "rct",
                "note": "N=41; taVNS increased HRV during mental stress; improved autonomic regulation in healthy adults",
            },
            # ── Cognition ─────────────────────────────────────────────────────
            {
                "authors": "Ridgewell C et al.",
                "year": 2021,
                "title": "The effects of transcutaneous auricular vagal nerve stimulation on cognition in healthy individuals: A meta-analysis",
                "journal": "Neuropsychology",
                "pmid": "34309394",
                "grade": "LOW",
                "evidence_type": "meta-analysis",
                "note": "19 studies; overall g=0.21 for cognition; significant for executive function; tragus > cymba concha for executive function",
            },
            # ── Sleep ─────────────────────────────────────────────────────────
            {
                "authors": "Yeom J et al.",
                "year": 2025,
                "title": "Transcutaneous auricular vagus nerve stimulation (taVNS) improves sleep quality in chronic insomnia disorder: A double-blind, randomized, sham-controlled trial",
                "journal": "Sleep Medicine",
                "pmid": "39879804",
                "grade": "MODERATE",
                "evidence_type": "rct",
                "note": "N=40; PSQI −4.5 vs −1.9 (sham); ISI improved; total sleep time increased; Cohen's d=−1.21",
            },
            # ── Mechanism ────────────────────────────────────────────────────
            {
                "authors": "Frangos E & Bhatt DL",
                "year": 2017,
                "title": "Non-invasive access to the vagus nerve central projections via electrical stimulation of the auricular branch",
                "journal": "Bioelectronic Medicine",
                "pmid": "31338118",
                "grade": "MECHANISTIC",
                "evidence_type": "narrative_review",
                "note": "fMRI evidence of NTS, LC, ACC, insular modulation during auricular tVNS",
            },
            {
                "authors": "Jacobs HI et al.",
                "year": 2015,
                "title": "Comfort and efficacy of transcutaneous vagal nerve stimulation in older adults",
                "journal": "Journal of Geriatric Psychiatry and Neurology",
                "pmid": "26491100",
                "grade": "LOW",
                "evidence_type": "pilot_study",
                "note": "Older adult tolerability confirmed; conservative titration recommended",
            },
            # ── Subthreshold / Preventive ─────────────────────────────────────
            {
                "authors": "Jackowska M et al.",
                "year": 2025,
                "title": "Effects of transcutaneous vagus nerve stimulation on subthreshold affective symptoms and perceived stress: Findings from a single-blinded randomized trial in community-dwelling adults",
                "journal": "Biological Psychology",
                "pmid": "41290087",
                "grade": "LOW",
                "evidence_type": "rct",
                "note": "N=70, mean age 49 years; left tragus vs earlobe sham; 4h/day × 28 days; "
                        "active tVNS superior to sham for anxiety and perceived stress in early phase "
                        "(days 0-13) but NOT late phase; NO effect on depression. "
                        "Supports preventive anxiety/stress indication; does not support depression indication.",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        review_flags=[
            "GRADE LOW–MODERATE for depression: meta-analysis signal present but heterogeneous RCTs; most Asian clinical trial populations",
            "GRADE LOW for anxiety: no powered GAD-specific RCT; Lai 2025 protocol trial in progress",
            "GRADE HIGH for safety: two large systematic reviews (N=6322, N=1322) with no serious AEs attributed to taVNS",
            "Parameter variability: 120 Hz/250μs (Monarch), 25 Hz/250μs (most RCTs), 10 Hz/500μs (Badran 2018) — no consensus for psychiatry",
            "Cymba concha confirmed superior to other sites by fMRI (Yakunina 2017) and HRV (Machetanz 2021) — use as primary placement",
            "Sham validity: earlobe sham is validated but 96% of participants detect active stimulation (Gerges 2024) — blinding is incomplete",
            "Interval vs continuous: interval stimulation has fewer AEs (Giraudier 2025) — prefer interval protocols",
            "Home taVNS (Rong 2016): patient self-administration feasible after training; supports home-use model",
        ],

        clinical_tips=[
            "Cymba concha electrode placement is the validated target — verify anatomy at first session; "
            "earlobe placement produces no therapeutic effect and is the validated sham",
            "Titrate intensity to the sensory threshold at every session — do not assume previous "
            "threshold is reproducible; electrode-skin contact varies",
            "For older adults: start at lower intensity (0.25 mA), titrate slowly; tolerance is high "
            "but initial tolerability requires careful introduction",
            "HRV measurement before and after a single session can demonstrate acute autonomic effect "
            "and improve patient engagement (visible physiological response)",
            "Combination with tDCS (DLPFC anodal) for TRD: administer tVNS 10 min before tDCS to "
            "prime the noradrenergic system before direct cortical stimulation",
            "Home-based protocols require device verification at first in-clinic session — confirm "
            "waveform parameters match 120 Hz / 250 μs specification",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES,
    )
