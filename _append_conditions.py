#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Appends condition data to generate_fellow_protocols.py"""
import textwrap

BLOCK = r'''

# ─────────────────────────────────────────────────────────────
# CONDITION DATA  (all 15 conditions)
# ─────────────────────────────────────────────────────────────
CONDITIONS = {}

# ══════════════════════════════════════
# 1. PARKINSON'S DISEASE
# ══════════════════════════════════════
CONDITIONS["parkinsons"] = dict(
    name="Parkinson's Disease", icd10="G20",
    doc_num="SOZO-PD-FEL-001",
    tps_status="INVESTIGATIONAL / OFF-LABEL",
    tdcs_class="Established NIBS; Level B evidence",
    tps_class="INVESTIGATIONAL / OFF-LABEL",
    tavns_class="Emerging adjunctive",
    ces_class="Supportive adjunct ONLY",
    inclusion=[
        "Confirmed PD diagnosis (UK Brain Bank or MDS criteria)",
        "Hoehn and Yahr stage I\u2013IV (V with Doctor approval)",
        "Age 18+ years",
        "Able to attend sessions or comply with home-use protocols",
        "Written informed consent (including TPS off-label disclosure)",
        "Baseline outcome measures completed (MDS-UPDRS III, MoCA, PHQ-9, GAD-7, FOG-Q)",
    ],
    exclusion=[
        "Intracranial metallic hardware in stimulation path",
        "Cochlear implant",
        "Skull defects, craniectomy, or recent craniotomy",
        "Active intracranial tumour",
        "Open wounds at electrode sites",
        "Pregnancy (tDCS, TPS)",
        "Inability to provide informed consent",
    ],
    discussion=[
        "Cardiac pacemaker or defibrillator \u2014 individual risk\u2013benefit assessment",
        "Epilepsy or seizure history \u2014 formal risk\u2013benefit with documented rationale",
        "Severe cognitive impairment",
        "Unstable medical conditions",
        "Active psychosis / impulse control disorders",
        "Coagulation disorders or anticoagulants (especially TPS)",
        "Dermatological conditions at electrode sites",
        "Severe dyskinesias preventing safe device application",
    ],
    overview=[
        "Parkinson's disease (PD) is the second most common neurodegenerative disorder and affects around 1\u20132% "
        "of people over the age of 60. It is characterised by progressive degeneration of dopaminergic neurons "
        "in the substantia nigra pars compacta, with resulting dysfunction across motor and non-motor neural "
        "networks (Bloem et al., 2021; Kalia & Lang, 2015).",
        "Cardinal Motor Features: The core motor features of PD are bradykinesia, rigidity, resting tremor, and "
        "postural instability. Bradykinesia is the defining clinical feature and is required for diagnosis, while "
        "tremor and rigidity are common accompanying signs. Postural instability usually emerges later and is "
        "associated with increased fall risk and functional decline.",
        "Non-Motor Symptoms: PD also includes a wide range of non-motor symptoms, many of which may appear before "
        "the onset of clear motor signs. These include cognitive impairment, depression, apathy, fatigue, pain, "
        "sleep disturbance, and autonomic dysfunction (Chaudhuri & Schapira, 2009).",
        "NIBS Evidence in PD: tDCS has shown promising results in motor performance, gait, cognition, and fatigue "
        "when combined with rehabilitation. TPS is regarded as investigational/off-label in PD. NIBS does not "
        "replace established pharmacological therapies; its role is adjunctive and phenotype-guided (Moshayedi et al., 2025).",
    ],
    pathophysiology=[
        "PD pathophysiology involves progressive loss of dopaminergic neurons in the substantia nigra pars compacta, "
        "leading to dopamine depletion in the striatum and disruption of the basal ganglia-thalamocortical circuit, "
        "resulting in reduced thalamo-cortical drive and impaired voluntary movement initiation.",
        "Lewy body pathology (alpha-synuclein aggregation) spreads through the nervous system (Braak stages 1\u20136). "
        "Non-motor symptoms reflect pathology beyond the nigrostriatal system: cortical Lewy bodies contribute "
        "to cognitive decline; serotonergic and noradrenergic depletion underpins depression and anxiety.",
    ],
    std_treatment=[
        "Pharmacological treatment in PD is primarily symptomatic. Levodopa remains the most effective treatment "
        "for motor symptoms and is prescribed with carbidopa or benserazide. Additional options include dopamine "
        "agonists, MAO-B inhibitors, COMT inhibitors, and amantadine. In advanced disease, DBS, LCIG, and "
        "subcutaneous infusions may be considered (Armstrong & Okun, 2020).",
    ],
    symptoms=[
        ["Bradykinesia",        "Slowness of movement initiation and execution; progressive fatiguing",  "Core criterion", "Kalia & Lang 2015; Bloem 2021"],
        ["Rigidity",            "Increased resistance to passive movement; lead-pipe or cogwheel",        "Core criterion", "Kalia & Lang 2015"],
        ["Resting Tremor",      "4\u20136 Hz tremor at rest; typically asymmetric; pill-rolling",         "70\u201380%",    "Braak 2003; Bloem 2021"],
        ["Postural Instability","Impaired balance; increased fall risk; retropulsion",                    "Later stages",   "Armstrong & Okun 2020"],
        ["Gait / FOG",          "Festination, shuffling, reduced arm swing, freezing of gait",            "Up to 80%",      "Wong 2022"],
        ["ON Dyskinesia",       "Levodopa-induced involuntary movements; choreiform at peak dose",         "40\u201390% at 10y", "Armstrong & Okun 2020"],
        ["Cognitive Impairment","Executive dysfunction, attention deficits, visuospatial impairment",     "20\u201340% MCI","Ma 2025; Souto 2024"],
        ["Depression",          "Anhedonia, apathy, low mood; may precede motor symptoms",                "40\u201350%",    "Chaudhuri & Schapira 2009"],
        ["Fatigue",             "Central fatigue; exhaustion disproportionate to activity",               "Up to 70%",      "Forogh 2017"],
        ["Pain",                "Musculoskeletal, neuropathic, central, dystonic pain",                   "60\u201385%",    "Gonzalez-Zamorano 2024"],
        ["Sleep Disturbances",  "REM behavior disorder, insomnia, excessive daytime sleepiness",          "60\u201398%",    "Chaudhuri & Schapira 2009"],
    ],
    brain_regions=[
        ["Primary Motor Cortex (M1)",     "Reduced excitability due to excessive BG inhibition",            "Anodal tDCS restores cortical excitability; Level B evidence",             "Lefaucheur 2017"],
        ["Supplementary Motor Area (SMA)","Impaired motor planning, sequencing, and gait initiation",       "Stimulation improves gait initiation and reduces FOG",                     "Wong 2022"],
        ["DLPFC",                         "Executive dysfunction, depression, impaired dual-task",          "Anodal tDCS demonstrates cognitive and mood improvements",                 "Ma 2025; Souto 2024"],
        ["Cerebellum",                    "Compensatory hyperactivation; tremor circuitry",                 "Modulation may reduce dyskinesias and improve balance",                    "Ferrucci 2015"],
        ["Thalamus (VL, VIM)",            "Relay in BG\u2013thalamo\u2013cortical loops; tremor generation","TPS may access thalamic structures at depth (investigational)",            "Manganotti 2025"],
        ["Basal Ganglia (STN, GPi)",      "Pathological beta-band oscillations; disrupted circuits",        "Cortical stimulation modulates subcortical activity via connected pathways","Bange 2025"],
        ["Anterior Cingulate Cortex",     "Motivation, conflict monitoring, pain processing",               "Potential target for apathy and pain",                                     "Zhang 2023"],
        ["Nucleus Basalis of Meynert",    "Cholinergic degeneration; cognitive decline",                    "TPS deep target for cognitive symptoms (investigational)",                 "Gianlorenco 2025"],
    ],
    brainstem=[
        ["Pedunculopontine Nucleus (PPN)", "Gait initiation failure; postural instability; FOG",  "Indirect modulation via SMA/M1/DLPFC; deep TPS investigational","Thevathasan 2018"],
        ["Locus Coeruleus (LC)",           "Early noradrenergic degeneration; arousal dysfunction","taVNS modulates LC via NTS pathways",                           "Marano 2024"],
        ["Dorsal Raphe Nucleus",           "Serotonergic dysregulation; depression; fatigue",      "tDCS (DLPFC) and taVNS may influence serotonergic projections", "Chmiel 2024"],
        ["Nucleus Tractus Solitarius",     "Autonomic integration hub; vagal afferent relay",      "Primary afferent target of taVNS; influences prefrontal regions","Yakunina 2018"],
        ["Periaqueductal Gray (PAG)",      "Central pain modulation; autonomic control",           "Indirect modulation via cortical and vagal neuromodulation",     "Bange 2025"],
    ],
    phenotypes=[
        ["Tremor-Dominant (TD)",          "Resting tremor >50% of motor burden; slower progression","Tremor, rigidity, mild bradykinesia",          "Cerebellar tDCS; TPS to cerebellum/thalamus"],
        ["Akinetic-Rigid (AR)",           "Rigidity and bradykinesia dominant; faster progression", "Bradykinesia, rigidity, postural instability", "M1/SMA anodal tDCS; TPS to M1/SMA"],
        ["PIGD (Postural Instability/Gait)","Early balance loss and gait dysfunction",             "Gait freezing, balance loss, faster progression","SMA/dual-task tDCS; balance protocols"],
        ["Depression / Apathy Dominant",  "Primary mood and motivational disturbance",              "Anhedonia, apathy, low mood; psychomotor slowing","DLPFC anodal tDCS; taVNS; CES adjunct"],
        ["Cognitive / Executive Dominant","Primary cognitive impairment",                          "Executive dysfunction, attention deficits",    "DLPFC anodal tDCS; TPS to DLPFC"],
        ["Pain Dominant",                 "Central or musculoskeletal pain as primary burden",      "Neuropathic pain, dystonic pain, MSK pain",   "M1 contralateral tDCS; TPS M1/thalamus; taVNS"],
        ["Mixed / Variable",              "Balanced motor/non-motor; atypical presentation",        "Combination of tremor, rigidity, cognitive, mood","Multimodal NIBS combination per phenotype"],
    ],
    symptom_map=[
        ["Motor (Bradykinesia/Rigidity)", "M1, SMA, Premotor",          "tDCS (M1/SMA anodal) + TPS (cranial targeted + peripheral) + taVNS adjunct","Moderate (Lefaucheur 2017)"],
        ["Tremor",                        "Cerebellum, Thalamus, M1",   "TPS (cranial targeted + peripheral) + cerebellar/M1 tDCS",                  "Emerging (Ferrucci 2015)"],
        ["Gait / FOG",                    "SMA, DLPFC, Cerebellum",     "Bilateral DLPFC tDCS + TPS (cranial + peripheral soles); dual-task training","Moderate (Wong 2022)"],
        ["Cognition / Executive",         "DLPFC, Frontal-Parietal",    "Left DLPFC tDCS + TPS (cranial targeted); taVNS, CES supportive",          "Moderate\u2013strong (Ma 2025)"],
        ["Depression / Apathy",           "DLPFC, ACC",                 "Left DLPFC tDCS + TPS (cranial targeted) + taVNS + CES adjunct",            "Moderate (Chmiel 2024)"],
        ["Fatigue",                       "DLPFC, SMA, Mesolimbic",     "DLPFC tDCS + TPS (cranial targeted) + CES; taVNS for arousal",             "Limited\u2013moderate (Forogh 2017)"],
        ["Pain",                          "M1 (contralateral), Thalamus","Contralateral M1 tDCS + TPS (cranial + peripheral); taVNS, CES",           "Moderate (Gonzalez-Zamorano 2024)"],
        ["ON/OFF Dyskinesias",            "Cerebellum, SMA, M1",        "Cerebellar/SMA tDCS + TPS (cranial targeted + peripheral)",                 "Emerging (Ferrucci 2015)"],
        ["Anxiety / Autonomic",           "ACC, Brainstem (LC, NTS)",   "taVNS primary + CES; DLPFC tDCS + TPS (cranial targeted)",                 "Moderate (Marano 2024)"],
    ],
    montage=[
        ["Motor dominant (bradykinesia, rigidity)","C3/C4 contralateral M1 anodal; or Fpz+Cbz anode, Cz cathode","Cranial (global + targeted M1/SMA) + peripheral (palms and soles)","taVNS"],
        ["Tremor primary",        "C4/C3 contralateral anode + Cbz anode, Fpz cathode",     "Cranial (global + targeted cerebellum/thalamus) + peripheral (palms)","taVNS supportive"],
        ["Gait / FOG",            "Fpz + Cz anode, CervVII cathode; Cb1/Cb2 anodal",        "Cranial (global + targeted) + peripheral (soles)",                    "taVNS supportive"],
        ["Cognitive / Executive", "F3 anode + F4 anode, Pz cathode; T3/T4 options",         "Cranial (global + targeted DLPFC)",                                   "taVNS, CES supportive"],
        ["Depression / Apathy",   "F3 anode + Pz anode, F2 cathode",                        "Cranial (global + targeted DLPFC/ACC)",                               "taVNS, CES supportive"],
        ["Fatigue",               "F3 anode + P4 anode, F2 cathode; Fz + Cz options",       "Cranial (global + targeted)",                                         "taVNS, CES supportive"],
        ["Pain (central or MSK)", "C3/C4 contralateral + F3 anode, Pz cathode",             "Cranial (global + targeted) + peripheral (affected dermatomes)",      "taVNS, CES supportive"],
        ["ON/OFF Dyskinesias",    "Fpz + Cbz anode, Cz cathode; Cb1/Cb2 options",           "Cranial (global + targeted) + peripheral (affected regions)",         "taVNS, CES supportive"],
        ["Mixed motor + cognitive","Alternate blocks: M1-based (motor) and DLPFC-based (executive)","Cranial (global + targeted)",                               "taVNS, CES supportive"],
        ["No response after 8\u201310 sessions","Reassess phenotype; adjust montage or switch modality","Adjust parameters; consider different ROI targeting",     "Review all adjuncts"],
    ],
    tdcs_protocols=[
        ["C1","Motor (bradykinesia, rigidity)","C3/C4 (contra M1)","Fz/Pz/extracephalic",      "2 mA, 20\u201340 min, 1\u20132\u00d7/day","Level B; improves UPDRS-III (Lefaucheur 2017)"],
        ["C2","Gait & dual-task",              "F3 (L-DLPFC), Cz", "Cbz, extracephalic",        "2 mA, 20\u201340 min, 1\u20132\u00d7/day","Improves gait speed (Wong 2022, 2024)"],
        ["C3","Cognition / executive",         "F3, F4, T3/T4, P3/P4","F2, extracephalic",      "2 mA, 20\u201340 min, 1\u20132\u00d7/day","Significant cognitive gains (Ma 2025)"],
        ["C4","Depression / mood",             "F3, Fz",           "F2, extracephalic",          "2 mA, 20\u201340 min, 1\u20132\u00d7/day","Reduces depression/apathy (Chmiel 2024)"],
        ["C5","Fatigue",                       "F3, P4, Pz, Cb1/Cb2","Fpz, F2, extracephalic",  "2 mA, 20\u201340 min, 1\u20132\u00d7/day","Sustained fatigue reduction (Forogh 2017)"],
        ["C6","Balance / posture",             "Fpz, Cz, Cb1/Cb2, P3/P4","Extracephalic, F2",   "2 mA, 20\u201340 min, 1\u20132\u00d7/day","Improves BBS & TUG (Na 2022)"],
        ["C7","ON/OFF dyskinesia",             "Cb1/Cb2/Cbz",      "Fpz, Cz",                   "2 mA, 20\u201340 min, 1\u20132\u00d7/day","Decreases dyskinesias (Ferrucci 2015)"],
        ["C8","Motor learning",                "C3/C4, Pz, Fz, F3/Cbz","F4, extracephalic",     "2 mA during task, 20\u201340 min",         "Facilitates learning (Firouzi 2024)"],
    ],
    plato_protocols=[
        ["C1-PS","Motor (bradykinesia)","Motor (Cz area)",   "Cz","Shoulder/arm",   "1.6 mA, 20\u201330 min","Daily or 5\u00d7/wk","Single-site; use with physiotherapy"],
        ["C2-PS","Gait / FOG",          "Motor (Cz area)",   "Cz","Nape of neck",   "1.6 mA, 20\u201330 min","Daily or 5\u00d7/wk","Cz placement closest to SMA/M1"],
        ["C3-PS","Cognition",           "Frontal (F3 area)", "F3","Shoulder",        "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Left prefrontal anodal for executive"],
        ["C4-PS","Depression / mood",   "Frontal (F3 area)", "F3","Right shoulder",  "1.6 mA, 20\u201330 min","5\u00d7/wk",         "F3 anodal; adjunct to CES"],
        ["C5-PS","Fatigue",             "Frontal (F3 area)", "F3","Shoulder",        "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Morning use preferred"],
        ["C6-PS","Balance / posture",   "Motor (Cz area)",   "Cz","Nape of neck",   "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Combine with vestibular exercises"],
        ["C7-PS","Dyskinesia",          "Posterior (Pz area)","Pz","Shoulder",       "1.6 mA, 20\u201330 min","3\u20135\u00d7/wk",  "Cerebellar targeting approximation"],
        ["C8-PS","Motor learning",      "Motor (Cz area)",   "Cz","Shoulder/arm",   "1.6 mA during task",    "5\u00d7/wk",         "Apply during motor practice window"],
    ],
    tps_protocols=[
        ["T1","Motor (bradykinesia, rigidity)","Bilateral M1, SMA, Premotor",      "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz; 10 sessions/2 wks","4,000 Std \u00b1 4,000 Tgt; total 6\u201310K","Emerging (Osou 2024)"],
        ["T2","Tremor",                        "VIM Thalamus, Cerebellar Dentate \u00b1 M1","0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",       "4,000 Tgt \u00b1 2,000 PRE; total 6\u20138K", "Emerging (Manganotti 2025)"],
        ["T3","Cognition (PD-MCI)",            "DLPFC, mPFC, Hippocampal region",  "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",               "4,000 Tgt \u00b1 2,000 PRE; total 6\u20138K", "Preliminary (Gianlorenco 2025)"],
        ["T4","Depression / Apathy",           "DLPFC, ACC",                       "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",               "4,000 Tgt \u00b1 2,000 PRE; total 6\u20138K", "Preliminary secondary outcomes"],
        ["T5","Pain / Dyskinesia",             "M1 + Thalamus",                    "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",               "4,000 Std + 4,000 Tgt; total 8\u201312K",     "Review-level support (Bange 2025)"],
    ],
    ces_role=[
        ["Mood and Depression",   "Supportive for mild-to-moderate depressive symptoms alongside primary tDCS","Evening sessions; or non-tDCS days"],
        ["Sleep Disturbances",    "Enhances sleep quality; may reduce REM behavior disorder symptoms",          "Evening before bed; 20\u201340 min"],
        ["Anxiety and Autonomic", "Stabilises arousal and autonomic tone",                                      "As needed; pre-session or evening"],
        ["Fatigue",               "May improve perceived energy and motivation as adjunct",                     "Morning or midday; avoid late if sedating"],
    ],
    tavns_role="taVNS serves as an autonomic and limbic modulator in PD, priming cortical receptivity before tDCS/TPS and supporting mood, sleep, and autonomic stability via locus coeruleus modulation.",
    combinations=[
        ("1) Bradykinetic / Rigid", [
            ["tDCS + Motor Physiotherapy","Anodal M1/DLPFC tDCS + structured rehabilitation (Elsner 2016; Moshayedi 2025)","tDCS before/during rehab","Bradykinesia, rigidity, slowing"],
            ["taVNS + Standard Care","taVNS modulates autonomic tone; adjunct for fatigue overlay (Shan 2025)","Non-tDCS days","Stress-sensitive motor worsening, fatigue"],
            ["CES + Standard Care","CES supports sleep/anxiety; indirect motor benefit (Philip 2017)","Evening","Sleep/anxiety overlay on motor symptoms"],
        ]),
        ("2) Tremor-Dominant", [
            ["tDCS + Cueing / Training","Cerebellar or M1 tDCS + behavioural strategies; evidence less robust than general motor (Elsner 2016)","tDCS before tremor-management training","Action/postural tremor with attentional sensitivity"],
            ["taVNS + Standard Care","May help autonomic arousal; direct tremor evidence preliminary (Matsuoka 2025)","Before stressful functional tasks","Tremor flares with anxiety/autonomic activation"],
            ["CES + Standard Care","Reduces anxiety/insomnia that aggravate tremor (Philip 2017)","Evening","Tremor + insomnia/anxiety loop"],
        ]),
        ("3) Executive Dysfunction", [
            ["tDCS + Cognitive Training","Prefrontal tDCS + cognitive/dual-task training (Conceicao 2021; Moshayedi 2025)","tDCS before/during cognitive training","Dysexecutive PD-MCI, slowing, dual-task difficulty"],
            ["taVNS + Cognitive Training","Modulates attention networks; exploratory adjunct only (Gerges 2024; Matsuoka 2025)","Before low-load cognitive tasks","Fluctuating attention, fatigue-driven executive failures"],
            ["CES + Standard Care","Supports sleep/anxiety indirectly affecting cognition (Philip 2017)","Evening","Executive dysfunction with insomnia/anxiety"],
        ]),
        ("4) Depression / Apathy", [
            ["tDCS + Behavioural Activation","Prefrontal tDCS + broader care plan for mood/apathy (Philip 2017; Moshayedi 2025)","tDCS before activation tasks","Depression, apathy, anhedonia"],
            ["taVNS + Standard Care","Plausible mood-regulation rationale; PD-specific antidepressant evidence early (Matsuoka 2025)","On off-days or stress-sensitive periods","Depression with autonomic anxiety or rumination"],
            ["CES + Standard Care","Supportive for anxiety/sleep; evidence quality low (Philip 2017)","Evening, 4\u20137 nights/week if prescribed","Depression with insomnia, somatic tension, anxiety"],
        ]),
        ("5) Freezing of Gait", [
            ["tDCS + Gait Rehabilitation","Best-supported PD combination: prefrontal/motor tDCS + gait training (Conceicao 2021; Elsner 2016)","tDCS before/during gait training","FOG, turning hesitation, dual-task gait collapse"],
            ["taVNS + Gait Rehabilitation","Plausible; current trials show small effects; exploratory (Sigurdsson 2021, 2025; Shan 2025)","Before gait practice or on non-tDCS days","Anxiety-triggered freezing, autonomic spikes"],
            ["CES + Standard Care","Helps sleep/hyperarousal; not a gait intervention (Philip 2017)","Evening","FOG with insomnia/fatigue overlay"],
        ]),
        ("6) Pain Phenotype", [
            ["tDCS + Graded Activity","Motor/prefrontal tDCS analgesic role; PD-specific pain evidence limited (Moshayedi 2025)","tDCS before activity or mobility work","Central pain, stiffness-pain loop, MSK amplification"],
            ["taVNS + Standard Care","Reduces autonomic arousal; mechanistic relevance for pain modulation (Adair 2020; Matsuoka 2025)","Before flare-prone periods or on off-days","Pain with autonomic arousal/catastrophising"],
            ["CES + Standard Care","Supports sleep and anxiety reduction; supportive only (Philip 2017)","Evening most days if prescribed","Pain + insomnia + anxiety"],
        ]),
    ],
    combination_summary=[
        ["Bradykinetic/Rigid",    "tDCS + Physiotherapy",        "Strongest non-TPS combination: anodal tDCS over M1/DLPFC + structured rehab (Elsner 2016; Moshayedi 2025)",  "tDCS before/during rehab", "Bradykinesia, rigidity",  "Moderate"],
        ["Bradykinetic/Rigid",    "taVNS + Standard Care",       "Feasible; small/inconsistent motor benefit; better as fatigue/autonomic adjunct (Shan 2025)",                 "Non-tDCS days",            "Stress-sensitive worsening","Emerging"],
        ["Tremor-Dominant",       "tDCS + Cueing",               "Evidence less robust; frame as trial adjunct to behavioural strategies (Elsner 2016)",                        "tDCS before training",     "Action/postural tremor",    "Limited"],
        ["Executive Dysfunction", "tDCS + Cognitive Training",   "Defensible: prefrontal tDCS + cognitive/dual-task training (Conceicao 2021; Moshayedi 2025)",                 "tDCS before cognitive Rx", "Dysexecutive PD-MCI",      "Moderate"],
        ["Depression/Apathy",     "tDCS + Behavioural Activation","Prefrontal tDCS + broader care plan for mood/apathy (Philip 2017; Moshayedi 2025)",                          "tDCS before activation",   "Depression, apathy",        "Moderate"],
        ["Freezing of Gait",      "tDCS + Gait Rehabilitation",  "Best-supported PD combination; prefrontal/motor tDCS + gait training (Conceicao 2021; Elsner 2016)",          "tDCS before/during gait",  "FOG, dual-task gait",       "Moderate"],
    ],
    outcomes=[
        ["MDS-UPDRS Part III",    "Motor function (OFF-medication state)",  "Baseline, weeks 4, 8, 12",     "\u226530% improvement = meaningful response"],
        ["MoCA",                  "Global cognition",                        "Baseline, month 3",            "Score <16 suggests severe impairment"],
        ["PHQ-9",                 "Depressive symptoms",                     "Baseline, weeks 4, 8, 12",     "Score \u226510 moderate; \u226515 severe"],
        ["GAD-7",                 "Anxiety symptoms",                        "Baseline, month 3",            "Score \u226510 clinically significant"],
        ["FOG-Q",                 "Gait freezing severity",                  "Baseline, weeks 4, 8, 12",     "Score >0 some freezing; >17 severe"],
        ["10-Meter Walk Test",    "Gait speed",                              "Baseline, weeks 4, 8, 12",     "Normal >0.8 m/s; PD typically 0.4\u20130.6 m/s"],
        ["Timed Up and Go (TUG)","Balance and fall risk",                   "Baseline, months 1, 3",        ">14 seconds = high fall risk"],
        ["Hoehn & Yahr Scale",    "Disease stage",                           "Baseline, month 3",            "I\u2013IV; determines inclusion and motor response tier"],
        ["SOZO PRS",              "NIBS-specific functional outcome",        "Baseline, weeks 2, 4, 8, 12", "Proprietary; composite of motor/non-motor domains"],
    ],
    outcomes_abbrev=["MDS-UPDRS III", "MoCA", "PHQ-9", "FOG-Q", "SOZO PRS"],
)
'''

with open("C:/Users/yildi/Sozo-Protocol-Generator/generate_fellow_protocols.py", "a", encoding="utf-8") as f:
    f.write(BLOCK)

print("PD block appended OK")
