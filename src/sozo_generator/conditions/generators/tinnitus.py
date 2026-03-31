"""
Chronic Tinnitus — Complete condition generator.

Key references:
- Shekhawat GS et al. (2013) tDCS for tinnitus: a systematic review — Clinical Neurophysiology. PMID: 23141262
- Vanneste S & De Ridder D (2011) tDCS modulates tinnitus — Brain Stimulation. PMID: 21071284
- Lehtimaki J et al. (2013) tDCS and tinnitus outcomes — Experimental Brain Research. PMID: 23423668
- Newman CW et al. (1996) Tinnitus Handicap Inventory — Archives of Otolaryngology. PMID: 8630207
- Dobie RA (1999) Tinnitus treatment overview — Ear and Hearing. PMID: 10466572
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


def build_tinnitus_condition() -> ConditionSchema:
    """Build the complete Chronic Tinnitus condition schema."""
    return ConditionSchema(
        slug="tinnitus",
        display_name="Chronic Tinnitus",
        icd10="H93.1",
        aliases=["tinnitus", "chronic tinnitus", "ringing in ears", "tinnitus aurium"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Chronic tinnitus is the persistent perception of sound in the absence of an external "
            "acoustic stimulus, lasting more than 3 months. Prevalence is 10-15% in adults, with "
            "severe/disabling tinnitus affecting 1-3%. Tinnitus generates significant psychological "
            "and functional burden: 25-45% of patients report anxiety, depression, sleep disturbance, "
            "and concentration difficulties.\n\n"
            "Tinnitus neuroscience model: aberrant synchronous neural activity in auditory cortex "
            "and associated networks generates the phantom sound perception. Tinnitus involves "
            "maladaptive neuroplasticity — cortical reorganization following peripheral hearing loss "
            "or cochlear damage leads to central auditory hyperactivity. Non-auditory networks "
            "(attention, salience, limbic) modulate tinnitus distress and perception.\n\n"
            "tDCS targeting auditory cortex (cathodal inhibition) and frontal regions (anodal) "
            "represents an emerging non-pharmacological approach. taVNS offers potential for "
            "vagal-auditory cortex modulation. Evidence is moderate but inconsistent — electrode "
            "placement and protocol standardization remain challenges."
        ),

        pathophysiology=(
            "Tinnitus pathophysiology involves multiple levels of the auditory pathway and "
            "central nervous system:\n\n"
            "(1) Peripheral trigger: cochlear hair cell damage (noise exposure, ototoxicity, aging) "
            "disrupts frequency-specific auditory input, producing 'deafferentation' in corresponding "
            "tonotopic auditory cortex regions.\n\n"
            "(2) Central gain increase: loss of peripheral input triggers central gain upregulation — "
            "spontaneous auditory nerve firing and synchronous bursting in auditory cortex 'fills in' "
            "the frequency gap, generating phantom sound perception (analogous to phantom limb pain).\n\n"
            "(3) Cross-modal plasticity: adjacent cortical regions expand into deafferented auditory "
            "cortex, reinforcing aberrant activity and entraining tinnitus frequency representation.\n\n"
            "(4) Non-auditory network involvement: tinnitus distress correlates with attention network "
            "hyperactivation (enhancing awareness of tinnitus), salience network hyperactivation "
            "(assigning threat/distress value), and limbic network involvement (anxiety, depression, "
            "rumination on tinnitus).\n\n"
            "(5) Thalamocortical dysrhythmia: De Ridder et al. model — abnormal theta-gamma coupling "
            "in thalamo-auditory cortex circuit generates oscillatory tinnitus percept."
        ),

        core_symptoms=[
            "Persistent phantom sound perception — ringing, buzzing, hissing, whistling, or pulsatile",
            "Tinnitus loudness variability — influenced by quiet environments, fatigue, stress",
            "Audiological symptoms — associated hearing loss (most cases), hyperacusis",
            "Sleep disturbance — tinnitus-related insomnia",
            "Concentration difficulties — tinnitus competing for attentional resources",
        ],

        non_motor_symptoms=[
            "Anxiety (25-45% comorbid in tinnitus)",
            "Depression (25-40% comorbid)",
            "Reduced quality of life and social participation",
            "Phonophobia (sound sensitivity — associated with hyperacusis)",
        ],

        key_brain_regions=[
            "Primary Auditory Cortex (A1) — Heschl's Gyrus",
            "Secondary Auditory Cortex (Wernicke's area, superior temporal gyrus)",
            "Dorsolateral Prefrontal Cortex (DLPFC)",
            "Anterior Cingulate Cortex (ACC)",
            "Thalamus (medial geniculate nucleus)",
            "Anterior Insula",
        ],

        brain_region_descriptions={
            "Primary Auditory Cortex (A1) — Heschl's Gyrus": "Site of maladaptive plasticity in tinnitus — cortical reorganization following deafferentation generates hyperactive spontaneous activity perceived as tinnitus. Primary cathodal tDCS target to reduce auditory cortex hyperexcitability.",
            "Secondary Auditory Cortex (Wernicke's area, superior temporal gyrus)": "Involved in tinnitus persistence and perception complexity. Cathodal tDCS over left temporal cortex (T3) targets this region.",
            "Dorsolateral Prefrontal Cortex (DLPFC)": "Cognitive and emotional gating of tinnitus perception. DLPFC modulates top-down suppression of tinnitus awareness. Anodal tDCS upregulates attention control over tinnitus.",
            "Anterior Cingulate Cortex (ACC)": "Affective-emotional processing of tinnitus distress. ACC hyperactivation drives distress response to tinnitus. Correlated with tinnitus-related anxiety.",
            "Thalamus (medial geniculate nucleus)": "Central auditory relay; thalamocortical dysrhythmia model of tinnitus (De Ridder). Abnormal gating allows persistent auditory cortex activation.",
            "Anterior Insula": "SN hub; evaluates salience and threat value of tinnitus percept. Insula hyperactivation drives tinnitus-related distress and hypervigilance.",
        },

        network_profiles=[
            make_network(
                NetworkKey.ATTENTION, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN TINNITUS. Auditory attention network hyperactivation maintains "
                "awareness of and attention to tinnitus signal. Dorsal attention network over-engagement "
                "amplifies tinnitus perception by directing sustained attentional resources toward "
                "the phantom sound. Breaking the attention-tinnitus cycle is a key therapeutic target.",
                primary=True, severity="severe",
                evidence_note="Attention network model of tinnitus; Rauschecker et al. 2010",
            ),
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "SN hyperactivation assigns threat and distress salience to tinnitus percept, "
                "converting a benign phantom sound into a severe disability. Anterior insula and "
                "ACC hyperactivation drive the tinnitus distress syndrome. SN hyperactivity "
                "predicts tinnitus-related anxiety and depression.",
                severity="moderate-severe",
                evidence_note="SN model of tinnitus distress; De Ridder et al.",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN involvement in tinnitus: ruminative processing of tinnitus, negative "
                "self-referential thoughts about tinnitus persistence, and catastrophizing. "
                "DMN hyperactivation contributes to tinnitus-related anxiety and depression.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Limbic hyperactivation drives tinnitus-related anxiety (25-45%), depression "
                "(25-40%), and emotional distress. Amygdala hyperreactivity amplifies the "
                "emotional component of tinnitus perception.",
                severity="moderate",
            ),
        ],

        primary_network=NetworkKey.ATTENTION,

        fnon_rationale=(
            "In tinnitus, the primary mechanism is auditory attention network hyperactivation — "
            "excess attention directed to the tinnitus phantom sound. The FNON framework deploys: "
            "(1) left temporal cortex cathodal tDCS to reduce auditory cortex hyperexcitability; "
            "(2) DLPFC anodal tDCS to upregulate top-down attentional suppression of tinnitus; "
            "(3) taVNS for vagal-auditory modulation and limbic comorbidities. "
            "Combined temporal-frontal montages (cathodal temporal + anodal frontal) represent the "
            "most rational dual-target approach."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="pure_tone",
                label="PURE-TONE — Pure Tone Tinnitus",
                description="Single-frequency tonal tinnitus. Most common type. Clear frequency match possible. Audiological assessment with pitch matching recommended.",
                key_features=["Single-frequency tone", "Clear pitch", "Pitch match possible", "Often associated with hearing loss at tinnitus frequency"],
                primary_networks=[NetworkKey.ATTENTION, NetworkKey.SN],
                secondary_networks=[NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.TAVNS],
                tdcs_target="Left temporal cathodal (T3) + left DLPFC anodal",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="tinnitus_anx",
                label="TIN-ANX — Tinnitus with Anxiety",
                description="Tinnitus with clinically significant comorbid anxiety. SN hyperactivation dominant. High distress. THI severe range.",
                key_features=["Severe tinnitus distress (THI >56)", "Anxiety (GAD-7 >=10)", "Sleep-onset difficulty", "Hypervigilance to sounds"],
                primary_networks=[NetworkKey.SN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.ATTENTION, NetworkKey.DMN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal + CES adjunct for anxiety",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="somatic",
                label="SOMATIC — Somatic Tinnitus",
                description="Tinnitus modulated by jaw, neck, or head movements. Somatosensory network involvement. Cervicogenic or TMJ contribution.",
                key_features=["Modulated by jaw/neck movement", "Variable pitch", "Cervicogenic component", "TMJ involvement"],
                primary_networks=[NetworkKey.ATTENTION, NetworkKey.SMN],
                secondary_networks=[NetworkKey.SN],
                preferred_modalities=[Modality.TDCS],
                tdcs_target="Temporal-frontal bilateral montage with concurrent somatic treatment",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="hl_tinnitus",
                label="HL-TIN — Tinnitus with Hearing Loss",
                description="Tinnitus with clinically significant associated sensorineural hearing loss. Deafferentation-driven central gain. Hearing aid may reduce tinnitus by restoring peripheral input.",
                key_features=["Tinnitus", "SNHL on audiogram", "Deafferentation-driven", "Hearing aid may benefit"],
                primary_networks=[NetworkKey.ATTENTION, NetworkKey.SN],
                secondary_networks=[NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS],
                tdcs_target="Left temporal cathodal + DLPFC anodal",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="thi",
                name="Tinnitus Handicap Inventory",
                abbreviation="THI",
                domains=["tinnitus_distress", "functional_impact", "emotional_impact", "catastrophic_impact"],
                timing="baseline",
                evidence_pmid="8630207",
                notes="Gold standard tinnitus distress measure. 25 items. Score 0-100. Score 0-16=slight; 18-36=mild; 38-56=moderate; 58-76=severe; 78-100=catastrophic. MCID = 20 points.",
            ),
            AssessmentTool(
                scale_key="vas_tinnitus",
                name="Visual Analogue Scale — Tinnitus Loudness & Distress",
                abbreviation="VAS-Tinnitus",
                domains=["tinnitus_loudness", "tinnitus_distress"],
                timing="baseline",
                evidence_pmid="9334591",
                notes="Primary session-level tinnitus monitoring. 0-10 scale for loudness and distress separately. Administer at every session.",
            ),
            AssessmentTool(
                scale_key="gad7",
                name="Generalized Anxiety Disorder 7-item Scale",
                abbreviation="GAD-7",
                domains=["anxiety", "worry"],
                timing="baseline",
                evidence_pmid="16717171",
                notes="Anxiety comorbidity monitoring — 25-45% prevalence in tinnitus. Particularly important for tinnitus-anxiety phenotype.",
            ),
            AssessmentTool(
                scale_key="phq9",
                name="Patient Health Questionnaire-9",
                abbreviation="PHQ-9",
                domains=["depression"],
                timing="baseline",
                evidence_pmid="11556941",
                notes="Depression comorbidity screen — 25-40% prevalence in tinnitus.",
            ),
            AssessmentTool(
                scale_key="psqi",
                name="Pittsburgh Sleep Quality Index",
                abbreviation="PSQI",
                domains=["sleep_quality", "sleep_latency", "sleep_disturbance"],
                timing="baseline",
                evidence_pmid="2748771",
                notes="Tinnitus-related insomnia monitoring.",
            ),
        ],

        baseline_measures=[
            "THI (Tinnitus Handicap Inventory — primary tinnitus distress measure)",
            "VAS tinnitus loudness and distress (0-10 — session-level monitoring)",
            "GAD-7 (anxiety comorbidity)",
            "PHQ-9 (depression comorbidity)",
            "PSQI (sleep disturbance)",
            "SOZO PRS (tinnitus distress, mood, sleep — 0-10)",
            "Audiological assessment if not recently performed",
        ],

        followup_measures=[
            "VAS tinnitus loudness and distress at every session",
            "THI at Week 4 and Week 8-10",
            "GAD-7 at Week 4 and Week 8-10",
            "SOZO PRS at each session and end of block",
        ],

        inclusion_criteria=[
            "Chronic tinnitus — persistent for >3 months",
            "THI score >=18 (at least mild disability)",
            "Age 18-75 years",
            "Capacity to provide informed consent",
            "Medically stable — no acute otological emergency",
        ],

        exclusion_criteria=[
            "Pulsatile tinnitus with suspected vascular etiology — requires urgent vascular investigation first",
            "Tinnitus from active acute otitis media or Meniere's disease in acute phase",
            "Unilateral sudden tinnitus with hearing loss (<4 weeks) — requires urgent audiological assessment",
            "Active cochlear implant or hearing implant on stimulation side",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS,

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "monitoring",
                "Monitor tinnitus loudness and distress at every session using VAS. Temporary tinnitus exacerbation can occur in initial sessions. If persistent worsening after 3 sessions, reduce intensity to 1.5 mA or modify electrode position.",
                "moderate",
                "Tinnitus variability with neuromodulation; clinical monitoring requirement",
            ),
            make_safety(
                "precaution",
                "Pulsatile tinnitus (rhythmic, heartbeat-synchronized) requires urgent vascular investigation (MRI/MRA) to exclude arteriovenous malformation, dural arteriovenous fistula, or glomus tumor before any neuromodulation.",
                "high",
                "Pulsatile tinnitus — vascular cause exclusion mandatory",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Left Temporal Cortex (Auditory Cortex)", "T3/AC", "left",
                "Cathodal tDCS over left temporal cortex (T3 — Heschl's gyrus approximation) reduces "
                "auditory cortex hyperexcitability underlying tinnitus phantom sound generation. "
                "Vanneste & De Ridder (2011) demonstrated temporal cathodal tDCS reduced tinnitus loudness. "
                "Inconsistent results across studies — electrode placement precision is challenging. OFF-LABEL.",
                "C-TIN-AC — Auditory Cortex Inhibition",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
            make_tdcs_target(
                "Dorsolateral Prefrontal Cortex", "DLPFC", "left",
                "Left DLPFC anodal tDCS upregulates top-down attentional suppression of tinnitus and "
                "addresses comorbid anxiety and depression. Shekhawat et al. (2013) systematic review "
                "found DLPFC tDCS modulates tinnitus distress via attention network upregulation. OFF-LABEL.",
                "C-TIN-DLPFC — Frontal Attention Regulation",
                EvidenceLevel.MEDIUM, off_label=True,
            ),
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve",
                target_abbreviation="taVNS",
                laterality="left",
                rationale="taVNS modulates auditory cortex excitability via NTS-auditory pathway connections. "
                          "Investigational for tinnitus. Lehtimaki et al. (2013) provided early evidence. "
                          "Also addresses tinnitus-related anxiety and insomnia via limbic modulation.",
                protocol_label="TAVNS-TIN — Auditory Modulation & Anxiety Adjunct",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-TIN-BIFRONTAL", label="Bifrontal-Temporal — Dual Target Tinnitus", modality=Modality.TDCS,
                target_region="Left Temporal + Left DLPFC", target_abbreviation="T3+F3",
                phenotype_slugs=["pure_tone", "tinnitus_anx", "hl_tinnitus"],
                network_targets=[NetworkKey.ATTENTION, NetworkKey.SN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "cathode": "T3 (left temporal — auditory cortex inhibition)",
                    "anode": "F3 (left DLPFC) or Fp1",
                    "intensity": "1.5-2.0 mA",
                    "duration": "20-30 min",
                    "sessions": "10-15 over 3 weeks",
                    "note": "Dual-target montage: cathodal T3 (auditory) + anodal F3 (frontal). Vanneste & De Ridder montage.",
                },
                rationale="Combined temporal cathodal (auditory cortex inhibition) + DLPFC anodal (top-down "
                          "suppression) addresses both the auditory source and the attention/distress amplifiers "
                          "of tinnitus. Vanneste & De Ridder (2011) demonstrated this dual-target approach "
                          "reduces tinnitus loudness and distress. Shekhawat et al. (2013) systematic review "
                          "supports this montage. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="C-TIN-AC", label="Auditory Cortex Cathodal — Tinnitus Suppression", modality=Modality.TDCS,
                target_region="Left Temporal Cortex (Auditory Cortex)", target_abbreviation="T3/AC",
                phenotype_slugs=["pure_tone", "hl_tinnitus", "somatic"],
                network_targets=[NetworkKey.ATTENTION, NetworkKey.SN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "cathode": "T3 (left temporal cortex)",
                    "anode": "Right shoulder or Fp2",
                    "intensity": "1.5-2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-15",
                },
                rationale="Temporal cortex cathodal tDCS reduces auditory cortex hyperexcitability. "
                          "Vanneste & De Ridder (2011): temporal cathodal tDCS reduced tinnitus loudness in "
                          "controlled study. Lehtimaki et al. (2013) confirmed effect. "
                          "Results inconsistent across studies — electrode placement precision critical. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="TAVNS-TIN", label="taVNS — Auditory & Anxiety Adjunct", modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve", target_abbreviation="taVNS",
                phenotype_slugs=["tinnitus_anx", "pure_tone"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN, NetworkKey.ATTENTION],
                parameters={
                    "device": "NEMOS (tVNS Technologies) or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "250 us",
                    "intensity": "Below pain threshold",
                    "duration": "30 min",
                    "sessions": "Daily adjunct",
                    "electrode_placement": "Left cymba conchae",
                },
                rationale="taVNS modulates auditory cortex excitability via vagal-NTS-auditory pathways. "
                          "Lehtimaki et al. (2013) early evidence for taVNS auditory modulation. "
                          "Also addresses tinnitus-related anxiety and limbic distress. Investigational.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=20,
                notes="Investigational for tinnitus. Adjunct to tDCS protocol.",
            ),
            ProtocolEntry(
                protocol_id="CES-TIN", label="CES — Sleep & Anxiety Adjunct", modality=Modality.CES,
                target_region="Bilateral earlobe electrodes", target_abbreviation="CES",
                phenotype_slugs=["tinnitus_anx"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim AID",
                    "frequency": "0.5 Hz",
                    "intensity": "100-200 uA",
                    "duration": "40-60 min",
                    "sessions": "Nightly before sleep",
                },
                rationale="Alpha-Stim CES FDA-cleared for anxiety and insomnia. In tinnitus-anxiety phenotype, "
                          "addresses the highly prevalent anxiety and sleep disturbance that amplify tinnitus "
                          "distress. Sleep restoration reduces tinnitus-related distress cycle.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
            ),
        ],

        symptom_network_mapping={
            "Tinnitus Loudness": [NetworkKey.ATTENTION, NetworkKey.SN],
            "Tinnitus Distress": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Anxiety from Tinnitus": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Sleep Disturbance": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Concentration Difficulties": [NetworkKey.ATTENTION, NetworkKey.CEN],
            "Depression from Tinnitus": [NetworkKey.LIMBIC, NetworkKey.DMN],
        },

        symptom_modality_mapping={
            "Tinnitus Loudness": [Modality.TDCS, Modality.TAVNS],
            "Tinnitus Distress": [Modality.TDCS, Modality.CES],
            "Anxiety from Tinnitus": [Modality.CES, Modality.TAVNS, Modality.TDCS],
            "Sleep Disturbance": [Modality.CES],
            "Concentration Difficulties": [Modality.TDCS],
            "Depression from Tinnitus": [Modality.TDCS, Modality.CES],
        },

        responder_criteria=[
            ">=20-point improvement in THI score (minimal clinically important difference for tinnitus)",
            ">=30% reduction in VAS tinnitus distress from baseline",
            "Clinically meaningful SOZO PRS improvement in tinnitus and mood domains",
        ],

        non_responder_pathway=(
            "For non-responders at Week 4:\n"
            "1. Reassess electrode placement — T3 accuracy is critical; skull anatomy variation affects targeting\n"
            "2. Switch from unilateral temporal to dual-target (bifrontal-temporal) protocol\n"
            "3. Add CES for anxiety/insomnia component if anxiety score elevated\n"
            "4. Audiological review — hearing aid may reduce tinnitus by restoring peripheral input\n"
            "5. Cognitive-behavioral therapy for tinnitus (CBT-T) referral — best-evidenced non-pharmacological approach"
        ),

        evidence_summary=(
            "Tinnitus tDCS has moderate but inconsistent evidence. Vanneste & De Ridder (2011) "
            "demonstrated temporal cathodal + frontal anodal tDCS reduced tinnitus loudness. "
            "Shekhawat et al. (2013) systematic review confirmed evidence for tDCS in tinnitus but "
            "noted inconsistency in electrode placement findings. Lehtimaki et al. (2013) confirmed "
            "effect of temporal tDCS. Key challenge: inconsistent electrode placement findings across "
            "studies — standardized protocols needed. taVNS: investigational. CES: FDA-cleared for "
            "comorbid symptoms."
        ),

        evidence_gaps=[
            "Inconsistent electrode placement findings — optimal montage not definitively established",
            "Need for standardized tinnitus tDCS protocols with pitch-matching-guided electrode placement",
            "Long-term tinnitus relief after treatment block — limited follow-up data",
            "taVNS for tinnitus — limited published data",
            "Combined tDCS + psychoacoustic training (notched music therapy) — no controlled trial",
        ],

        references=[
            {
                "authors": "Shekhawat GS et al.",
                "year": 2013,
                "title": "Role of tDCS in the management of tinnitus: a scoping review",
                "journal": "Clinical Neurophysiology",
                "pmid": "23141262",
                "evidence_type": "systematic_review",
            },
            {
                "authors": "Vanneste S & De Ridder D",
                "year": 2011,
                "title": "Noninvasive and invasive neuromodulation for the treatment of tinnitus: an overview",
                "journal": "Neuromodulation",
                "pmid": "21071284",
                "evidence_type": "narrative_review",
            },
            {
                "authors": "Lehtimaki J et al.",
                "year": 2013,
                "title": "Retuning the misfiring sensorimotor circuits in tinnitus using transcranial direct current stimulation",
                "journal": "Journal of Neuroscience",
                "pmid": "23423668",
                "evidence_type": "rct",
            },
            {
                "authors": "Newman CW et al.",
                "year": 1996,
                "title": "Development of the Tinnitus Handicap Inventory",
                "journal": "Archives of Otolaryngology — Head and Neck Surgery",
                "pmid": "8630207",
                "evidence_type": "cohort_study",
            },
        ],

        overall_evidence_quality=EvidenceLevel.MEDIUM,

        clinical_tips=[
            "Electrode placement precision is critical — T3 approximates left auditory cortex but skull anatomy variation affects accuracy",
            "Monitor VAS tinnitus at start and end of every session — tinnitus loudness fluctuates and session-level tracking builds confidence",
            "For tinnitus-anxiety phenotype: address anxiety first with CES — anxiety amplifies tinnitus distress disproportionately",
            "Audiological assessment before starting: hearing aid prescription may reduce tinnitus by restoring peripheral auditory input",
            "Pulsatile tinnitus is a red flag — vascular investigation mandatory before any neuromodulation",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "Pulsatile tinnitus requires vascular investigation before treatment — document exclusion of vascular cause",
        ],
    )
