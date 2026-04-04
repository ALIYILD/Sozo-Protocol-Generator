"""
Fibromyalgia — Complete condition generator.

Key references:
- Fregni F et al. (2006) A randomized, sham-controlled, proof of principle study of transcranial
  direct current stimulation for the treatment of pain in fibromyalgia. PMID: 16776781
- Riberto M et al. (2011) Efficacy of transcranial direct current stimulation coupled with a
  multidisciplinary rehabilitation program for the treatment of fibromyalgia. PMID: 21992771
- Hargrove JB et al. (2012) Transcranial stimulation in fibromyalgia. PMID: 22350798
- Clauw DJ (2014) Fibromyalgia: A clinical review. PMID: 24866610
- Wolfe F et al. (2010) The American College of Rheumatology 2010 preliminary diagnostic criteria
  for fibromyalgia. PMID: 20235902
- Gracely RH et al. (2002) Functional MRI evidence of augmented pain processing in fibromyalgia. PMID: 12098241
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


def build_fibromyalgia_condition() -> ConditionSchema:
    """Build the complete Fibromyalgia condition schema."""
    return ConditionSchema(
        slug="fibromyalgia",
        display_name="Fibromyalgia",
        icd10="M79.3",
        aliases=["fibromyalgia", "FMS", "fibromyalgia syndrome", "chronic widespread pain"],
        version="1.0",
        generated_at=current_date_str(),

        overview=(
            "Fibromyalgia (FMS) is a chronic, widespread musculoskeletal pain disorder characterized "
            "by central sensitization, fatigue, sleep disturbance, cognitive dysfunction ('fibro fog'), "
            "and mood dysregulation. It affects approximately 2-4% of the general population, with "
            "a 3:1 female-to-male ratio. It is the second most common musculoskeletal diagnosis "
            "after osteoarthritis in rheumatology practice.\n\n"
            "Fibromyalgia is now understood as a disorder of central pain processing rather than "
            "a peripheral tissue pathology — characterized by augmented central sensitization, "
            "reduced descending pain inhibition, and amplified pain signaling throughout the "
            "central nervous system. Neuroimaging studies demonstrate consistent patterns of "
            "altered functional connectivity in pain and sensorimotor networks.\n\n"
            "Current pharmacological treatments (duloxetine, pregabalin, milnacipran) provide "
            "modest benefit in approximately 30-40% of patients. Non-pharmacological approaches — "
            "particularly aerobic exercise and cognitive-behavioral therapy — have the strongest "
            "long-term evidence. Neuromodulation, specifically M1 tDCS, has growing evidence "
            "from Fregni et al. (2006) and Riberto et al. (2011). tDCS M1 anode + cognitive "
            "rehabilitation + aerobic exercise represents the optimal multimodal approach."
        ),

        pathophysiology=(
            "Fibromyalgia pathophysiology is driven by central sensitization and pain network "
            "dysregulation:\n\n"
            "(1) Central sensitization: Abnormal amplification of pain signals throughout the "
            "spinal cord and brain. Wind-up and temporal summation at dorsal horn neurons "
            "generate allodynia (pain from non-painful stimuli) and hyperalgesia "
            "(increased pain from painful stimuli). fMRI demonstrates augmented pain network "
            "activation from non-painful stimuli (Gracely et al. 2002).\n\n"
            "(2) Descending pain modulation deficit: Impaired descending inhibitory pathways "
            "(dorsolateral prefrontal cortex — periaqueductal grey — spinal cord) fail to "
            "adequately suppress pain signals. This is measurable with conditioned pain modulation "
            "(CPM) testing — CPM is impaired in fibromyalgia.\n\n"
            "(3) Thalamo-cortical dysrhythmia: Abnormal alpha-delta EEG sleep intrusions "
            "disrupt non-restorative sleep and increase pain threshold lowering. "
            "Poor sleep and pain form a bidirectional cycle.\n\n"
            "(4) Neuroinflammation: Small fiber neuropathy (SFN) found in 40-60% of FMS — "
            "may generate peripheral nociceptive input maintaining central sensitization.\n\n"
            "(5) HPA axis dysregulation and stress system abnormalities: Altered cortisol "
            "rhythms and sympathetic hyperactivation contribute to pain, fatigue, and mood symptoms.\n\n"
            "(6) M1 tDCS mechanism: Motor cortex anodal tDCS (Fregni 2006) — activates "
            "M1-mediated descending inhibitory pathways to periaqueductal grey, reducing "
            "central sensitization. This is the neurobiological basis of M1 tDCS analgesia."
        ),

        core_symptoms=[
            "Widespread musculoskeletal pain >=3 months (bilateral, above and below waist, axial)",
            "Fatigue — debilitating, non-restorative sleep",
            "Cognitive dysfunction ('fibro fog') — memory, concentration, word-finding",
            "Sleep disturbance — non-restorative sleep, frequent awakening",
            "Morning stiffness (>30 minutes)",
        ],

        non_motor_symptoms=[
            "Depression (30-50% comorbid — bidirectional with fibromyalgia)",
            "Anxiety (25-40% comorbid)",
            "Headaches (migraine or tension-type — 50% prevalence in FMS)",
            "Irritable bowel syndrome (30-50% overlap)",
            "Temporomandibular disorder overlap",
            "Allodynia and hyperalgesia (sensory amplification)",
        ],

        key_brain_regions=[
            "Primary Motor Cortex (M1, C3/C4)",
            "Dorsolateral Prefrontal Cortex (DLPFC)",
            "Anterior Cingulate Cortex (ACC)",
            "Anterior Insula",
            "Periaqueductal Grey (PAG)",
            "Thalamus (mediodorsal, posterior)",
        ],

        brain_region_descriptions={
            "Primary Motor Cortex (M1, C3/C4)": "Primary tDCS analgesia target in fibromyalgia. "
                "Fregni et al. (2006) anodal M1 tDCS significantly reduced pain vs. sham. "
                "M1 activates descending inhibitory pathways to PAG, reducing central sensitization. "
                "Contralateral M1 anode (C3 for most patients).",
            "Dorsolateral Prefrontal Cortex (DLPFC)": "Descending pain inhibition relay and "
                "cognitive function. Left DLPFC anodal tDCS addresses fibro fog and supports "
                "descending inhibitory control. Secondary tDCS target.",
            "Anterior Cingulate Cortex (ACC)": "ACC hyperactivation drives the affective-emotional "
                "component of pain — the 'suffering' dimension. Contributes to pain catastrophizing.",
            "Anterior Insula": "SN hub; central processing of interoceptive pain signals. "
                "Hyperactivation amplifies pain awareness and fibromyalgia distress.",
            "Periaqueductal Grey (PAG)": "Key hub of descending pain inhibition. M1 tDCS activates "
                "M1-PAG descending inhibitory pathway — mechanism of analgesia.",
            "Thalamus (mediodorsal, posterior)": "Central pain relay. Thalamo-cortical dysrhythmia "
                "in fibromyalgia disrupts sleep and amplifies pain signaling.",
        },

        network_profiles=[
            make_network(
                NetworkKey.SN, NetworkDysfunction.HYPER,
                "PRIMARY NETWORK IN FIBROMYALGIA. Salience network hyperactivation drives the "
                "central amplification of pain, fatigue, and distress. Anterior insula and ACC "
                "hyperactivation are consistent neuroimaging findings in FMS. The SN assigns "
                "excessive threat and distress value to afferent pain signals.",
                primary=True, severity="severe",
                evidence_note="Gracely et al. (2002) — augmented pain processing; Clauw (2014)",
            ),
            make_network(
                NetworkKey.DMN, NetworkDysfunction.HYPER,
                "DMN hyperactivation drives pain catastrophizing, ruminative thinking about pain, "
                "and negative self-referential processing. DMN-SN connectivity abnormalities "
                "are a key fibromyalgia neuroimaging signature.",
                severity="moderate-severe",
                evidence_note="Napadow et al. (2010) — DMN in fibromyalgia",
            ),
            make_network(
                NetworkKey.CEN, NetworkDysfunction.HYPO,
                "CEN hypoactivation drives 'fibro fog' — working memory, attention, and executive "
                "function deficits. DLPFC hypoactivation also reduces descending pain inhibitory "
                "control. Left DLPFC anodal tDCS targets this.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.SMN, NetworkDysfunction.HYPER,
                "SMN hyperactivation and sensorimotor cortex amplification of nociceptive input. "
                "Motor cortex M1 anodal tDCS modulates SMN to activate descending inhibitory pathways.",
                severity="moderate",
            ),
            make_network(
                NetworkKey.LIMBIC, NetworkDysfunction.HYPER,
                "Limbic hyperactivation drives depression (30-50%), anxiety (25-40%), and emotional "
                "amplification of pain. Depression and pain form a bidirectional cycle in FMS.",
                severity="moderate-severe",
            ),
        ],

        primary_network=NetworkKey.SN,

        fnon_rationale=(
            "In fibromyalgia, the primary mechanism is central sensitization driven by SN hyperactivation "
            "and impaired descending pain inhibition. The FNON framework deploys: "
            "(1) M1 anodal tDCS (primary — Fregni evidence) to activate M1-PAG descending inhibitory "
            "pathway; (2) Left DLPFC anodal tDCS for cognitive dysfunction and descending inhibition; "
            "(3) taVNS for vagal-mediated pain inhibition and mood; (4) CES for sleep and anxiety. "
            "Combined with aerobic exercise (evidence-based adjunct) for additive central sensitization reversal."
        ),

        phenotypes=[
            PhenotypeSubtype(
                slug="pain_predominant",
                label="FMS-PAIN — Pain Predominant",
                description="Widespread pain is the primary burden. Fatigue and cognitive symptoms secondary. Central sensitization dominant. M1 anodal tDCS primary target.",
                key_features=["WPI >=7, SSS>=5 (ACR 2016)", "Pain NRS >=6/10", "Allodynia", "Hyperalgesia", "Fatigue secondary"],
                primary_networks=[NetworkKey.SN, NetworkKey.SMN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.LIMBIC],
                preferred_modalities=[Modality.TDCS, Modality.TMS, Modality.TAVNS],
                tdcs_target="Contralateral M1 anodal (C3) + reference shoulder",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="fatigue_predominant",
                label="FMS-FATIGUE — Fatigue Predominant",
                description="Debilitating fatigue and non-restorative sleep are the primary complaints, with pain secondary. Sleep disturbance drives fatigue perpetuation cycle.",
                key_features=["SSS fatigue >=3/3", "Non-restorative sleep", "PSQI >10", "Pain present but secondary"],
                primary_networks=[NetworkKey.SN, NetworkKey.LIMBIC],
                secondary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.CES, Modality.TAVNS],
                tdcs_target="Left DLPFC anodal (F3) — fatigue and sleep focus",
                tps_target=None,
            ),
            PhenotypeSubtype(
                slug="mood_comorbid",
                label="FMS-MOOD — Fibromyalgia with Mood Comorbidity",
                description="Fibromyalgia with clinically significant comorbid depression and/or anxiety. Mood disorder independently amplifies pain perception and reduces treatment response. Address mood concurrently.",
                key_features=["PHQ-9 >=10", "GAD-7 >=10 (if anxiety)", "Pain amplified by mood", "Catastrophizing high (PCS)"],
                primary_networks=[NetworkKey.LIMBIC, NetworkKey.SN],
                secondary_networks=[NetworkKey.DMN, NetworkKey.CEN],
                preferred_modalities=[Modality.TDCS, Modality.TAVNS, Modality.CES],
                tdcs_target="Left DLPFC anodal (F3) primary + M1 anodal adjunct",
                tps_target=None,
            ),
        ],

        assessment_tools=[
            AssessmentTool(
                scale_key="fiq_r",
                name="Fibromyalgia Impact Questionnaire Revised",
                abbreviation="FIQ-R",
                domains=["function", "overall_impact", "symptoms"],
                timing="baseline",
                evidence_pmid="19858869",
                notes="Primary FMS outcome measure. 21 items, 3 subscales. Score 0-100. Higher = worse. MCID = 14% improvement or 8.1-point change. Administer at baseline, 4 weeks, 8 weeks.",
            ),
            AssessmentTool(
                scale_key="wpi_sss",
                name="ACR 2016 Diagnostic Criteria: WPI + SSS",
                abbreviation="WPI+SSS",
                domains=["widespread_pain_index", "symptom_severity_scale"],
                timing="baseline",
                evidence_pmid="20235902",
                notes="2010/2016 ACR diagnostic criteria. WPI 0-19 (tender areas), SSS 0-12 (fatigue, sleep, cognitive, somatic symptoms). FMS threshold: WPI>=7 and SSS>=5, or WPI 4-6 and SSS>=9.",
            ),
            AssessmentTool(
                scale_key="nrs11",
                name="Numeric Rating Scale for Pain",
                abbreviation="NRS-11",
                domains=["pain_intensity"],
                timing="baseline",
                evidence_pmid="10989895",
                notes="Primary session-level pain monitoring. 0-10 scale. Administer at every session. MCID = 2-point reduction or 30% improvement. Simple and responsive.",
            ),
            AssessmentTool(
                scale_key="promis_pain",
                name="PROMIS Pain Interference Short Form",
                abbreviation="PROMIS Pain",
                domains=["pain_interference", "functional_impact"],
                timing="baseline",
                evidence_pmid=None,
                notes="Patient-reported outcomes: captures pain interference with daily activities. T-score >60 = above average pain interference.",
            ),
        ],

        baseline_measures=[
            "FIQ-R (primary fibromyalgia outcome — pain, fatigue, function)",
            "NRS-11 pain intensity (0-10 — session-level monitoring)",
            "WPI+SSS (ACR 2016 criteria verification and severity)",
            "PHQ-9 (depression comorbidity — 30-50% prevalence)",
            "GAD-7 (anxiety comorbidity — 25-40%)",
            "PSQI (sleep quality — non-restorative sleep critical in FMS)",
            "SOZO PRS (pain, fatigue, mood, sleep — 0-10)",
        ],

        followup_measures=[
            "NRS-11 pain intensity at every session",
            "FIQ-R at 4-week and 8-week intervals",
            "PHQ-9 and PSQI at 4-week intervals",
            "SOZO PRS at each session",
        ],

        inclusion_criteria=[
            "ACR 2016 criteria for fibromyalgia (WPI>=7 and SSS>=5, or WPI 4-6 and SSS>=9)",
            "Symptoms present for >=3 months",
            "Inadequate response to standard pharmacotherapy and non-pharmacological treatment",
            "NRS pain score >=4/10 at baseline",
            "Age 18-70 years",
            "Medically stable",
        ],

        exclusion_criteria=[
            "Inflammatory arthritis or connective tissue disease with active synovitis (requires separate management)",
            "Active malignancy",
            "Neurological cause of widespread pain (neuropathy, MS — requires primary diagnosis treatment)",
            "Acute psychiatric crisis",
        ],

        contraindications=SHARED_ABSOLUTE_CONTRAINDICATIONS,

        safety_notes=SHARED_SAFETY_NOTES + [
            make_safety(
                "precaution",
                "Fibromyalgia patients may have heightened sensory sensitivity — some report skin electrode discomfort at standard 2 mA. Start at 1.5 mA and titrate up if well tolerated. Use gel electrode application technique.",
                "moderate",
                "Central sensitization and tDCS skin sensitivity in FMS",
            ),
            make_safety(
                "monitoring",
                "Monitor for post-exertional malaise — some FMS patients report symptom flare after exercise adjunct. Aerobic exercise should be initiated at low intensity and progressed gradually.",
                "moderate",
                "Post-exertional symptom management in fibromyalgia",
            ),
        ],

        stimulation_targets=[
            make_tdcs_target(
                "Contralateral Primary Motor Cortex", "M1", "left",
                "M1 anodal tDCS activates descending pain inhibitory pathways (M1-PAG) — "
                "the primary mechanism of neuromodulation analgesia in fibromyalgia. "
                "Fregni et al. (2006) RCT: M1 anodal tDCS (2 mA, 20 min x 5 days) "
                "significantly reduced pain vs. sham and DLPFC tDCS. Riberto et al. (2011) "
                "confirmed M1 tDCS with multidisciplinary rehabilitation. OFF-LABEL.",
                "C-FMS-M1 — Motor Cortex Analgesia",
                EvidenceLevel.HIGH, off_label=True,
                eeg_canonical=["C3", "C4"],
            ),
            make_tdcs_target(
                "Left Dorsolateral Prefrontal Cortex", "L-DLPFC", "left",
                "Left DLPFC anodal tDCS targets fibro fog (cognitive dysfunction) and "
                "supports descending pain inhibitory control. DLPFC modulates prefrontal "
                "contributions to pain inhibition. Secondary target after M1 or for "
                "mood-comorbid and cognitive-predominant phenotypes. OFF-LABEL.",
                "C-FMS-DLPFC — Cognitive & Descending Inhibition",
                EvidenceLevel.MEDIUM, off_label=True,
                eeg_canonical=["F3"],
            ),
            StimulationTarget(
                modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve",
                target_abbreviation="taVNS",
                laterality="left",
                rationale="taVNS activates the vagal-NTS pathway with ascending modulation of "
                          "pain processing networks and descending inhibitory control. "
                          "Also addresses comorbid depression, anxiety, and sleep in FMS. "
                          "Investigational but promising adjunct for fibromyalgia. OFF-LABEL.",
                protocol_label="TAVNS-FMS — Vagal Pain Modulation & Mood",
                evidence_level=EvidenceLevel.LOW,
                off_label=True,
                eeg_canonical=["Ear"],
            ),
            StimulationTarget(
                modality=Modality.CES,
                target_region="Bilateral earlobe electrodes",
                target_abbreviation="CES",
                laterality="bilateral",
                rationale="CES (Alpha-Stim) FDA-cleared for anxiety, depression, and insomnia — "
                          "all prominent comorbidities in fibromyalgia. Addresses the sleep-pain "
                          "cycle. CES adjunct provides clinical value for FMS-sleep and "
                          "FMS-mood phenotypes.",
                protocol_label="CES-FMS — Sleep, Anxiety & Mood Adjunct",
                evidence_level=EvidenceLevel.MEDIUM,
                off_label=False,
                eeg_canonical=["Ear"],
            ),
        ],

        protocols=[
            ProtocolEntry(
                protocol_id="C-FMS-M1-ANODAL",
                label="M1 Anodal tDCS — Primary Fibromyalgia Pain Protocol",
                modality=Modality.TDCS,
                target_region="Contralateral Primary Motor Cortex",
                target_abbreviation="M1 anodal",
                phenotype_slugs=["pain_predominant", "fatigue_predominant"],
                network_targets=[NetworkKey.SN, NetworkKey.SMN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "C3 (left M1 — contralateral to dominant hemisphere)",
                    "cathode": "Right shoulder",
                    "intensity": "2.0 mA",
                    "duration": "20 min",
                    "sessions": "10-20 over 3-5 weeks",
                    "adjunct": "Aerobic exercise (30 min moderate intensity) after each session recommended",
                    "note": "Fregni et al. (2006) protocol: 5 consecutive sessions minimum",
                },
                rationale="Fregni et al. (2006) RCT: M1 anodal tDCS (2 mA, 20 min x 5 days) "
                          "was the first sham-controlled trial showing significant pain reduction "
                          "in fibromyalgia. M1 anodal activation engages M1-PAG descending "
                          "inhibitory pathways. Riberto et al. (2011) demonstrated enhanced "
                          "efficacy combining M1 tDCS with multidisciplinary rehabilitation. "
                          "Best evidence for any tDCS protocol in fibromyalgia. OFF-LABEL.",
                evidence_level=EvidenceLevel.HIGH, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="C-FMS-DLPFC-ANODAL",
                label="L-DLPFC Anodal tDCS — Fibro Fog & Mood Protocol",
                modality=Modality.TDCS,
                target_region="Left Dorsolateral Prefrontal Cortex",
                target_abbreviation="L-DLPFC",
                phenotype_slugs=["mood_comorbid", "fatigue_predominant"],
                network_targets=[NetworkKey.CEN, NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Newronika HDCkit or PlatoScience",
                    "anode": "F3 (left DLPFC)",
                    "cathode": "Right shoulder or Fp2",
                    "intensity": "1.5-2.0 mA",
                    "duration": "20 min",
                    "sessions": "15-20 over 4 weeks",
                    "note": "For cognitive dysfunction and mood-comorbid phenotype",
                },
                rationale="Left DLPFC anodal tDCS upregulates CEN for cognitive dysfunction "
                          "(fibro fog) and supports descending pain inhibition. "
                          "Also targets comorbid depression and anxiety — driving the mood-pain "
                          "cycle. Combined approach: M1 for analgesia + DLPFC for cognitive and "
                          "mood symptoms in dual-target montage. OFF-LABEL.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=True, session_count=15,
            ),
            ProtocolEntry(
                protocol_id="TAVNS-FMS",
                label="taVNS — Vagal Pain Modulation Adjunct",
                modality=Modality.TAVNS,
                target_region="Left auricular branch of vagus nerve",
                target_abbreviation="taVNS",
                phenotype_slugs=["pain_predominant", "mood_comorbid"],
                network_targets=[NetworkKey.SN, NetworkKey.LIMBIC, NetworkKey.DMN],
                parameters={
                    "device": "NEMOS (tVNS Technologies) or Parasym",
                    "frequency": "25 Hz",
                    "pulse_width": "250 us",
                    "intensity": "Below pain threshold (0.5-3 mA)",
                    "duration": "30 min",
                    "sessions": "Daily adjunct to tDCS block",
                    "electrode_placement": "Left cymba conchae",
                },
                rationale="taVNS activates vagal-NTS ascending modulation of pain networks "
                          "and supports descending pain inhibition. Additionally addresses "
                          "comorbid depression, anxiety, and sleep disturbance in FMS. "
                          "Investigational adjunct with growing evidence for pain conditions.",
                evidence_level=EvidenceLevel.LOW, off_label=True, session_count=20,
                notes="Investigational for fibromyalgia. Adjunct to tDCS.",
            ),
            ProtocolEntry(
                protocol_id="CES-FMS",
                label="CES Alpha-Stim — Sleep & Mood Adjunct",
                modality=Modality.CES,
                target_region="Bilateral earlobe electrodes",
                target_abbreviation="CES",
                phenotype_slugs=["fatigue_predominant", "mood_comorbid"],
                network_targets=[NetworkKey.LIMBIC, NetworkKey.SN],
                parameters={
                    "device": "Alpha-Stim AID",
                    "frequency": "0.5 Hz",
                    "intensity": "100-200 uA",
                    "duration": "40-60 min",
                    "sessions": "Nightly before sleep during treatment block",
                },
                rationale="Alpha-Stim CES FDA-cleared for anxiety, depression, and insomnia. "
                          "In fibromyalgia, the sleep-pain cycle is critical: poor sleep lowers "
                          "pain threshold, worsening FMS. CES nightly improves sleep quality, "
                          "addressing the non-restorative sleep driving FMS fatigue and pain.",
                evidence_level=EvidenceLevel.MEDIUM, off_label=False, session_count=20,
            ),
        ],

        symptom_network_mapping={
            "Widespread Pain": [NetworkKey.SN, NetworkKey.SMN],
            "Fatigue": [NetworkKey.SN, NetworkKey.LIMBIC],
            "Sleep Disturbance": [NetworkKey.LIMBIC, NetworkKey.SN],
            "Fibro Fog": [NetworkKey.CEN, NetworkKey.ATTENTION],
            "Depression": [NetworkKey.LIMBIC, NetworkKey.DMN],
            "Anxiety": [NetworkKey.LIMBIC, NetworkKey.SN],
        },

        symptom_modality_mapping={
            "Widespread Pain": [Modality.TDCS, Modality.TMS, Modality.TAVNS],
            "Fatigue": [Modality.TDCS, Modality.CES, Modality.TAVNS],
            "Sleep Disturbance": [Modality.CES, Modality.TAVNS],
            "Fibro Fog": [Modality.TDCS],
            "Depression": [Modality.TDCS, Modality.TAVNS, Modality.CES],
            "Anxiety": [Modality.CES, Modality.TAVNS],
        },

        responder_criteria=[
            ">=14% improvement in FIQ-R total score (MCID)",
            ">=2-point reduction in NRS-11 pain score, or >=30% pain reduction",
            "Patient-reported meaningful improvement in fatigue and daily function",
        ],

        non_responder_pathway=(
            "For non-responders at 4-week block:\n"
            "1. Add aerobic exercise adjunct — evidence shows M1 tDCS + exercise is superior to tDCS alone\n"
            "2. Switch to dual-target protocol: M1 anodal + DLPFC anodal (for mood-cognition comorbidity)\n"
            "3. Add CES for sleep-fatigue cycle — non-restorative sleep perpetuates FMS\n"
            "4. Rheumatology/pain medicine review — optimize pharmacotherapy (duloxetine, pregabalin)\n"
            "5. Multidisciplinary pain program referral — strongest long-term evidence in FMS"
        ),

        evidence_summary=(
            "Fibromyalgia tDCS: strongest evidence from Fregni et al. (2006) RCT and Riberto et al. (2011). "
            "Fregni 2006: M1 anodal tDCS (2 mA x 5 sessions) significantly reduced pain vs. sham "
            "and DLPFC tDCS — M1 is superior to DLPFC for pain reduction in FMS. "
            "Riberto 2011: M1 tDCS + multidisciplinary rehabilitation showed enhanced benefit. "
            "TMS over M1: separate evidence base for pain reduction in chronic pain. "
            "taVNS and CES: adjunctive evidence for mood, sleep, and anxiety comorbidities. "
            "| Evidence counts: tDCS=50, TMS=40, taVNS=15, CES=20. Best modalities: tDCS (M1), TMS."
        ),

        evidence_gaps=[
            "Long-term durability of M1 tDCS analgesia beyond treatment block",
            "Optimal session frequency and number — 5, 10, or 20 sessions?",
            "Combination M1 tDCS + aerobic exercise — optimal protocol for synergy",
            "Biomarkers for tDCS responder prediction in fibromyalgia",
            "Dual-site tDCS (M1 + DLPFC) vs. single-site — direct comparison",
        ],

        references=[
            {
                "authors": "Fregni F et al.",
                "year": 2006,
                "title": "A randomized, sham-controlled, proof of principle study of transcranial direct current stimulation for the treatment of pain in fibromyalgia",
                "journal": "Arthritis & Rheumatism",
                "pmid": "16776781",
                "evidence_type": "rct",
            },
            {
                "authors": "Riberto M et al.",
                "year": 2011,
                "title": "Efficacy of transcranial direct current stimulation coupled with a multidisciplinary rehabilitation program for the treatment of fibromyalgia",
                "journal": "Open Rheumatology Journal",
                "pmid": "21992771",
                "evidence_type": "rct",
            },
            {
                "authors": "Clauw DJ",
                "year": 2014,
                "title": "Fibromyalgia: A clinical review",
                "journal": "JAMA",
                "pmid": "24866610",
                "evidence_type": "narrative_review",
            },
            {
                "authors": "Wolfe F et al.",
                "year": 2010,
                "title": "The American College of Rheumatology 2010 preliminary diagnostic criteria for fibromyalgia",
                "journal": "Arthritis Care & Research",
                "pmid": "20235902",
                "evidence_type": "consensus_statement",
            },
        ],

        overall_evidence_quality=EvidenceLevel.HIGH,

        clinical_tips=[
            "M1 anodal tDCS is the strongest evidence-based target — start here for pain-predominant FMS (Fregni 2006)",
            "Combine M1 tDCS with aerobic exercise immediately after each session — Riberto protocol; synergy is significant",
            "Central sensitivity: start at 1.5 mA and titrate to 2.0 mA over 2-3 sessions for tolerability",
            "Always screen for and address sleep (PSQI) — non-restorative sleep perpetuates FMS; CES nightly is a powerful adjunct",
            "Fibro fog often predicts poor patient engagement — explain cognitive symptoms as brain network dysfunction, not psychiatric",
        ],

        governance_rules=SHARED_GOVERNANCE_RULES + [
            "FMS diagnosis should be confirmed by rheumatologist or pain medicine physician before neuromodulation",
            "Pharmacological treatment must be optimized concurrently — neuromodulation is adjunctive",
        ],
    )
