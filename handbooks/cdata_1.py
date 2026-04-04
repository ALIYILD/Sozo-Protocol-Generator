"""Condition data: Depression, Anxiety, ADHD, Alzheimer's"""

CDATA = {}

# ─── DEPRESSION ──────────────────────────────────────────────────────────────
CDATA["depression"] = dict(
    slug="depression", cover_title="MAJOR DEPRESSIVE DISORDER (MDD)",
    name="Major Depressive Disorder (MDD)", short="Depression", abbr="MDD",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in Major Depressive Disorder is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not currently extend to MDD as a primary indication. Mandatory off-label "
        "disclosure and Doctor sign-off are required before TPS treatment for MDD."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for MDD requires specific, documented off-label disclosure with Doctor sign-off."
    ),
    prs_domain_label="Mood & Affective Symptoms Domain",
    prs_domain_header_line="Mood & Affective Symptoms Domain \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
    exam_step_heading="4.1 Mood & Affect Examination",
    exam_step_desc=(
        "Conduct a systematic examination of mood and affect using the Clinical Examination Checklist. "
        "Rate each domain using the 0\u20134 scale (0=Absent, 1=Mild, 2=Moderate, 3=Marked, 4=Severe):"
    ),
    exam_checklist_item="\u2610 Mood & affect examination completed (all domains rated)",
    med_check_item="Record current medication compliance (last antidepressant dose, any PRN taken today)",
    session_med_doc="medication and adherence (SSRI/SNRI dose, PRN anxiolytics, timing)",
    false_class_body=(
        "Standardise assessment conditions between baseline and follow-up. Ensure PHQ-9 and HDRS-17 "
        "are administered at comparable times of day and in comparable settings to avoid diurnal mood "
        "variation creating a false responder or false non-responder classification."
    ),
    modality_table=[
        ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Meta-analysis", "200+"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Pilot RCT + Multiple RCTs (2025)", "14+"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "RCT, Meta-analysis", "80+"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "RCT, Meta-analysis", "30+"],
        ["TMS", "NeuroStar / MagVenture / Magstim", "FDA-cleared (MDD)", "RCT, Meta-analysis", "500+"],
        ["tACS", "Starstim / NeuroConn", "CE Class IIa (research)", "RCT, Open-label", "20+"],
        ["PBM", "Vielight Neuro / Coronet", "CE/FDA (research)", "Open-label, Pilot RCT", "10+"],
        ["PEMF", "BrainsWay / MagPro", "CE/FDA (research)", "RCT, Open-label", "15+"],
        ["LIFU", "Sonic Concepts / FUS Instruments", "Investigational", "Pilot RCT, Open-label", "12+"],
        ["tRNS", "Starstim / NeuroConn", "CE Class IIa (research)", "Open-label, Pilot", "3+"],
        ["DBS", "Medtronic / Abbott", "FDA-cleared (TRD \u2014 Breakthrough)", "RCT, Open-label", "30+"],
    ],
    best_modality="TMS (rTMS/iTBS), tDCS",
    offlabel_table=[
        ["Modality", "Regulatory Status", "MDD Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Level A NIBS evidence for MDD; established protocol", "Standard informed consent"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Evidence-supported; CE depression indication", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety/depression/insomnia)", "Cleared indication includes depression", "Standard informed consent"],
    ],
    prs_table=[
        ["Core Mood Symptoms (0\u201310)", "Neurovegetative Symptoms (0\u201310)"],
        ["Depressed / low mood severity", "Sleep disturbance (insomnia or hypersomnia)"],
        ["Anhedonia (loss of pleasure/interest)", "Fatigue / loss of energy"],
        ["Hopelessness / pessimism", "Appetite/weight change (loss or gain)"],
        ["Worthlessness / excessive guilt", "Psychomotor retardation or agitation"],
        ["Concentration / decision-making difficulty", "Anxiety / worry (comorbid severity)"],
        ["Suicidal ideation (passive or active)", "Irritability / mood instability"],
        ["Cognitive fog / brain fog", "Social withdrawal / isolation"],
        ["Emotional reactivity / tearfulness", "Quality of life / global functioning"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["Affective State", "Observed mood, affect range, reactivity, congruence", "0\u20134 severity rating"],
        ["Psychomotor Signs", "Objective retardation (slowed speech, movement) or agitation", "0\u20134; L/R if relevant"],
        ["Cognitive Presentation", "Attention, processing speed, word-finding", "Structured bedside assessment"],
        ["Sleep Presentation", "Insomnia type, early morning awakening, hypersomnia", "Clinical interview + PSQI"],
        ["Vegetative Signs", "Appetite, weight trajectory, energy, libido", "Document change from premorbid"],
        ["Suicidality Assessment", "Columbia Suicide Severity Rating Scale (C-SSRS)", "Score + action plan if indicated"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["PHQ-9 (Patient Health Questionnaire)", "___ / 27", "\u226510 = moderate depression (primary outcome measure)"],
        ["HDRS-17 (Hamilton Depression Rating Scale)", "___ / 52", "\u22658 = mild; \u226517 = moderate; \u226524 = severe"],
        ["MADRS (Montgomery-\u00c5sberg)", "___ / 60", "\u226520 = moderate; \u226535 = severe depression"],
        ["GAD-7 (Anxiety comorbidity)", "___ / 21", "\u226510 = moderate anxiety (common comorbidity)"],
        ["MoCA (Montreal Cognitive Assessment)", "___ / 30", "\u226526 = normal; <26 = cognitive screening positive"],
        ["PSQI (Pittsburgh Sleep Quality Index)", "___ / 21", ">5 = sleep disturbance present"],
        ["BDI-II (Beck Depression Inventory)", "___ / 63", "\u226514 = mild; \u226520 = moderate; \u226529 = severe"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Melancholic", "Profound anhedonia; diurnal variation (worse AM); early morning awakening; psychomotor retardation/agitation; loss of pleasure in all activities"],
        ["Atypical", "Mood reactivity (brightens to positive events); leaden paralysis; hypersomnia; hyperphagia; rejection sensitivity; heavy feeling in limbs"],
        ["Anxious Distress", "Prominent anxiety, worry, tension; elevated GAD-7 (\u226510); somatic complaints; high HAMA; tense, keyed-up presentation"],
        ["Treatment-Resistant (TRD)", "\u22652 adequate antidepressant trials failed (\u226612 weeks each at therapeutic dose); chronicity >2 years; high HDRS-17"],
        ["Cognitive-Dominant", "Subjective/objective cognitive impairment; processing speed deficit; memory complaints; MoCA borderline; depression-dementia overlap"],
        ["Psychotic Features", "Mood-congruent delusions (worthlessness, guilt, nihilistic); requires combined pharmacotherapy; limited NIBS evidence"],
        ["Seasonal Pattern", "Onset autumn/winter; remission spring; hypersomnia + carbohydrate craving; phototherapy primary; NIBS adjunctive"],
        ["Postpartum", "Onset within 4 weeks postpartum; special safety considerations for nursing; taVNS + CES first line"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["L-DLPFC (F3)", "Mood / Cognition", "Behavioural activation scheduling; positive imagery; reward anticipation tasks; computerised cognitive training"],
        ["Bifrontal DLPFC", "Mood / Rumination", "Cognitive restructuring exercise; mindfulness induction; gratitude journaling; problem-solving worksheet"],
        ["sgACC / OFC (TPS)", "Hedonic Processing", "Reward anticipation tasks; pleasant imagery; social connection exercises; positive autobiographical recall"],
        ["taVNS", "Autonomic / Mood", "Paced breathing (4-7-8 pattern); heart rate coherence biofeedback; progressive muscle relaxation"],
        ["CES (Alpha-Stim)", "Sleep / Anxiety", "Sleep hygiene education; worry postponement scheduling; mindfulness body scan; relaxation instruction"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["PHQ-9 (Primary)", "\u226550% reduction = Responder; score \u22644 = Remission; \u226525% = Partial response"],
        ["HDRS-17", "\u226550% reduction = Responder; score \u22647 = Remission; 25\u201349% = Partial response"],
        ["MADRS", "\u226550% reduction = Responder; score \u226410 = Remission; 25\u201349% = Partial response"],
        ["PSQI / Sleep", "PSQI \u22645 (good sleeper); or \u22653-point improvement in global sleep score"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "Confirmed MDD diagnosis (DSM-5 / ICD-11 criteria)"],
        ["2", "PHQ-9 \u226510 at baseline (moderate-severe depression)"],
        ["3", "Age 18\u201375; capable of informed consent"],
        ["4", "Inadequate response to \u22651 adequate antidepressant trial OR patient preference for non-pharmacological treatment"],
        ["5", "Stable medication regimen for \u22654 weeks prior to enrolment"],
        ["6", "No planned medication change for \u22658 weeks after enrolment"],
        ["7", "Willing to maintain concurrent psychotherapy (where applicable)"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Active suicidality with intent or plan requiring hospitalisation (C-SSRS \u22654)"],
        ["2", "Recent ECT within 3 months"],
        ["3", "Metallic implants in head/neck region within stimulation field"],
        ["4", "Active psychosis or confirmed Bipolar I Disorder"],
        ["5", "Pregnancy (tDCS safety data insufficient; CES/taVNS with caution)"],
        ["6", "Uncontrolled epilepsy or seizure disorder"],
        ["7", "Cardiac pacemaker or implanted cardioverter-defibrillator (CES/taVNS)"],
        ["8", "Active substance dependence (alcohol, stimulants, benzodiazepine overuse)"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Bipolar II Disorder (depressive phase)", "Taper/absence of mood stabiliser: risk-benefit; mood destabilisation monitoring"],
        ["Borderline Personality Disorder comorbidity", "NIBS adjunctive only; primary DBT essential; assessment of self-harm risk"],
        ["Chronic pain comorbidity", "tDCS M1 + DLPFC combined approach; phenotype affects target selection"],
        ["ADHD comorbidity", "Stimulant timing relative to tDCS session: document carefully"],
        ["Thyroid dysfunction (hypothyroid)", "Ensure euthyroid status confirmed before attributing non-response to NIBS"],
        ["Elderly (\u226575 years)", "Reduce tDCS intensity (1.0\u20131.5 mA); TPS lower pulse count; CES primary"],
        ["Post-stroke depression", "Refer to stroke protocol; specialised brain target selection required"],
        ["Dementia with comorbid depression", "Refer to Alzheimer\u2019s protocol; cognitive safety monitoring essential"],
        ["Recent traumatic loss (grief)", "Distinguish complicated grief from MDD; adjustment disorder: different pathway"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Melancholic", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin; bifrontal option (F3+/F4\u2212)", "DLPFC BA46 + sgACC: 300 pulses, 0.2\u202fHz", "taVNS 25Hz 30min pre-session; CES nightly 60min"],
        ["Atypical", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "DLPFC + OFC: 250 pulses, 0.2\u202fHz", "taVNS 25Hz 30min; CES daily 60min"],
        ["Anxious Distress", "Anodal L-DLPFC (F3) 2\u202fmA; extended ramp (30s)", "DLPFC + ACC: 250 pulses, 0.2\u202fHz", "CES primary (anxiolytic) 60min; taVNS 30min"],
        ["Treatment-Resistant (TRD)", "HD-tDCS DLPFC 2\u202fmA or bifrontal enhanced (F3+/F4\u2212)", "sgACC + DLPFC intensive: 400 pulses", "taVNS 30min + CES nightly; escalate frequency"],
        ["Cognitive-Dominant", "Anodal L-DLPFC (F3) 2\u202fmA + cognitive task pairing", "DLPFC BA46 focus: 250 pulses", "taVNS 30min; CES nightly; cognitive training"],
        ["Anxious + Psychomotor Agitation", "Cathodal R-DLPFC (F4) or bifrontal calming", "ACC: 200 pulses low intensity", "CES primary; taVNS vagal calming"],
        ["Seasonal Pattern", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "DLPFC: 250 pulses", "Light therapy concurrent; CES + taVNS"],
        ["Maintenance / Relapse Prevention", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin 2\u00d7/week", "None / minimal", "CES 3\u00d7/week; taVNS daily home device"],
    ],
)

# ─── ANXIETY (GAD) ───────────────────────────────────────────────────────────
CDATA["anxiety"] = dict(
    slug="anxiety", cover_title="GENERALIZED ANXIETY DISORDER (GAD)",
    name="Generalized Anxiety Disorder (GAD)", short="Anxiety", abbr="GAD",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in Generalized Anxiety Disorder is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not currently extend to GAD. Mandatory off-label disclosure and Doctor "
        "sign-off are required before TPS treatment for GAD."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for GAD requires specific, documented off-label disclosure with Doctor sign-off."
    ),
    prs_domain_label="Anxiety & Worry Symptoms Domain",
    prs_domain_header_line="Anxiety & Worry Symptoms Domain \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
    exam_step_heading="4.1 Anxiety & Arousal Examination",
    exam_step_desc=(
        "Conduct a systematic examination of anxiety, arousal, and somatic symptoms using the "
        "Clinical Examination Checklist. Rate each domain on a 0\u20134 severity scale:"
    ),
    exam_checklist_item="\u2610 Anxiety & arousal examination completed (all domains rated)",
    med_check_item="Record current medication compliance (last anxiolytic/SSRI dose, any PRN benzodiazepine taken today)",
    session_med_doc="medication compliance (SSRI/SNRI dose, PRN benzodiazepine use, timing)",
    false_class_body=(
        "Standardise assessment conditions between baseline and follow-up. Ensure GAD-7 and HAM-A "
        "are administered at comparable times of day. Acute situational stress at follow-up can "
        "inflate scores and create false non-responder classification."
    ),
    modality_table=[
        ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Open-label", "15+"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Investigational", "0+"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "RCT, Open-label", "10+"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "RCT, Meta-analysis", "40+"],
        ["TMS", "NeuroStar / MagVenture / Magstim", "CE/FDA (research use)", "RCT, Open-label", "20+"],
        ["tACS", "Starstim / NeuroConn", "CE Class IIa (research)", "Open-label, Pilot", "5+"],
        ["PBM", "Vielight Neuro / Coronet", "CE/FDA (research)", "Open-label, Pilot", "5+"],
        ["PEMF", "BrainsWay / MagPro", "CE/FDA (research)", "Open-label, Pilot", "5+"],
    ],
    best_modality="CES (Alpha-Stim), taVNS",
    offlabel_table=[
        ["Modality", "Regulatory Status", "GAD Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Established NIBS; anxiolytic evidence Level B", "Standard informed consent"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Evidence-supported; anxiolytic mechanism established", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety)", "FDA-cleared indication: anxiety", "Standard informed consent"],
    ],
    prs_table=[
        ["Core Anxiety Symptoms (0\u201310)", "Somatic & Autonomic Symptoms (0\u201310)"],
        ["Excessive worry (uncontrollable, pervasive)", "Muscle tension / muscle aches"],
        ["Difficulty controlling worry", "Sleep disturbance (difficulty falling/staying asleep)"],
        ["Restlessness / keyed-up feeling", "Fatigue / easy tiredness"],
        ["Irritability / mood instability", "Concentration difficulties / mind going blank"],
        ["Catastrophic thinking / worst-case anticipation", "Palpitations / racing heart / chest tightness"],
        ["Avoidance behaviour (situations, tasks)", "Sweating / trembling / shakiness"],
        ["Social anxiety / performance anxiety", "Gastrointestinal symptoms (nausea, diarrhoea)"],
        ["Panic features (if comorbid)", "Overall quality of life / daily functioning"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["Autonomic Arousal", "Heart rate, blood pressure, tremor, sweating, pallor at rest", "Objective measurement + clinical observation"],
        ["Behavioural Anxiety Signs", "Restlessness, avoidance, safety behaviours, reassurance seeking", "0\u20134 severity rating"],
        ["Cognitive Anxiety Symptoms", "Concentration, mind-going-blank, decision difficulty", "Structured clinical interview"],
        ["Somatic Complaints", "GI symptoms, headache, muscle tension, fatigue", "Symptom checklist + severity rating"],
        ["Panic Evaluation", "Panic attack frequency, triggers, duration, avoidance", "Frequency log + clinical interview"],
        ["Safety Behaviour Assessment", "Reassurance seeking, checking, avoidance mapping", "Document specific behaviours"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["GAD-7 (Generalized Anxiety Disorder Scale)", "___ / 21", "\u226510 = moderate anxiety (primary outcome)"],
        ["HAM-A (Hamilton Anxiety Rating Scale)", "___ / 56", "\u226518 = mild; \u226525 = moderate anxiety"],
        ["STAI-T (State-Trait Anxiety Inventory \u2014 Trait)", "___ / 80", ">40 trait anxiety (age-/sex-normed)"],
        ["BAI (Beck Anxiety Inventory)", "___ / 63", "\u226516 = moderate; \u226526 = severe anxiety"],
        ["PHQ-9 (Depression comorbidity)", "___ / 27", "\u226510 = depression comorbidity present"],
        ["PSQI (Sleep quality)", "___ / 21", ">5 = sleep disturbance (anxiety-driven insomnia)"],
        ["MoCA (Cognitive screen)", "___ / 30", "\u226526 = normal; rules out cognitive masquerade"],
        ["Penn State Worry Questionnaire", "___ / 80", ">45 = pathological worry"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Cognitive-Worry Dominant", "Excessive uncontrollable worry as primary feature; high PSWS; rumination; catastrophising; mental hypervigilance"],
        ["Somatic-Tension Dominant", "Prominent physical symptoms: muscle tension, headache, fatigue, GI complaints; autonomic hyperarousal; HAM-A somatic subscale elevated"],
        ["Mixed Anxiety-Depression", "GAD + MDD comorbidity (40\u201360% overlap); PHQ-9 \u226510 and GAD-7 \u226510; DLPFC and limbic dual targeting required"],
        ["Panic-Prone", "GAD with comorbid panic disorder or panic attacks; amygdala hyperreactivity; avoidance; high BAI"],
        ["Social Anxiety Dominant", "GAD with prominent social anxiety features; fear of negative evaluation; performance avoidance; elevated SIAS"],
        ["Health Anxiety Dominant", "Excessive health worry, body scanning, reassurance seeking; HAI elevated; somatic amplification"],
        ["OCD Spectrum Features", "Contamination worry, symmetry, harm-obsessive features overlapping GAD; CSTC involvement"],
        ["Insomnia-Dominant", "Sleep-onset anxiety; nocturnal worry; hyperarousal in bed; PSQI elevated; CES primary modality"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["L-DLPFC (F3)", "Worry / Cognitive Control", "Worry postponement scheduling; cognitive defusion exercise; structured problem-solving worksheet"],
        ["Bilateral DLPFC", "Rumination / Arousal", "Mindfulness of thoughts; cognitive restructuring; progressive relaxation"],
        ["ACC (TPS)", "Conflict / Worry Monitoring", "Uncertainty tolerance exercises; ACT defusion; attention training technique (ATT)"],
        ["taVNS", "Autonomic / Vagal Tone", "Paced breathing (4-7-8 or box breathing); HRV biofeedback; diaphragmatic breathing training"],
        ["CES (Alpha-Stim)", "Sleep / Arousal Reduction", "Sleep hygiene education; progressive muscle relaxation; sleep restriction guidance"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["GAD-7 (Primary)", "\u226550% reduction = Responder; score \u22644 = Remission; 25\u201349% = Partial response"],
        ["HAM-A", "\u226550% reduction = Responder; score <8 = Remission; 25\u201349% = Partial"],
        ["STAI-Trait", "\u226510-point reduction in T-score = clinically meaningful change"],
        ["PHQ-9 (if comorbid)", "\u226550% reduction in comorbid depressive symptoms"],
        ["PSQI (Sleep)", "PSQI \u22645 or \u22653-point improvement in global sleep score"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "Confirmed GAD diagnosis (DSM-5 / ICD-11 criteria); symptoms \u22656 months"],
        ["2", "GAD-7 \u226510 at baseline (moderate-severe anxiety)"],
        ["3", "Age 18\u201375; capable of informed consent"],
        ["4", "Inadequate response to \u22651 SSRI/SNRI trial or CBT course OR patient preference"],
        ["5", "Stable medication for \u22654 weeks prior to enrolment"],
        ["6", "No planned medication changes for \u22658 weeks after enrolment"],
        ["7", "Willing to engage with concurrent CBT (where applicable)"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Active suicidality requiring hospitalisation"],
        ["2", "Metallic implants in head/neck region"],
        ["3", "Uncontrolled epilepsy or seizure disorder"],
        ["4", "Active psychosis or bipolar disorder (manic phase)"],
        ["5", "Pregnancy (first trimester; second/third: risk-benefit)"],
        ["6", "Cardiac pacemaker or ICD (CES / taVNS contraindication)"],
        ["7", "Benzodiazepine dependence requiring detox (acute phase)"],
        ["8", "Untreated severe medical condition causing anxiety (thyroid, cardiac)"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Benzodiazepine regular use", "Acute tolerance effects; document dose/timing; taper plan before NIBS course"],
        ["Panic disorder comorbidity", "Exposure-based therapy essential concurrent; TPS over amygdala cautiously"],
        ["OCD features", "Refer to OCD protocol for SMA/OFC targeting if obsessions prominent"],
        ["Chronic pain comorbidity", "Anxious pain phenotype; tDCS DLPFC + M1 combined approach"],
        ["Cardiovascular disease", "CES and taVNS: cardiac clearance; ECG recommended"],
        ["Elderly (\u226575 years)", "Reduce intensities; longer ramp; CES primary; medication review for iatrogenic anxiety"],
        ["ADHD comorbidity", "Stimulant timing relative to session; separate ADHD and GAD protocols"],
        ["Substance use (caffeine/stimulants)", "Advise caffeine restriction on session days; stimulant documentation"],
        ["Medically unexplained symptoms (MUS)", "Somatic symptom disorder overlap; psychoeducation essential component"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Cognitive-Worry", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "DLPFC BA46 + ACC: 250 pulses 0.2\u202fHz", "taVNS 25Hz 30min; CES 60min"],
        ["Somatic-Tension", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "ACC: 200 pulses 0.2\u202fHz", "CES primary (anxiolytic); taVNS HRV"],
        ["Mixed Anxiety-Depression", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "DLPFC + sgACC: 300 pulses", "taVNS 30min; CES nightly 60min"],
        ["Panic-Prone", "Anodal L-DLPFC (F3) 2\u202fmA; slow ramp", "Amygdala region (cautious): 150 pulses", "taVNS primary (vagal); CES 60min"],
        ["Social Anxiety", "Anodal L-DLPFC (F3) 2\u202fmA + DLPFC cognitive pairing", "DLPFC: 250 pulses", "taVNS 30min; CBT-Social concurrent"],
        ["Health Anxiety", "Anodal L-DLPFC (F3) 2\u202fmA", "OFC: 200 pulses (error monitoring)", "CES 60min; psychoeducation concurrent"],
        ["Insomnia-Dominant", "Cathodal L-DLPFC (F3) 1.5\u202fmA (reducing arousal)", "None initial", "CES primary nightly 60min; taVNS pre-sleep"],
        ["Maintenance / Relapse Prevention", "Anodal L-DLPFC (F3) 1.5\u202fmA 2\u00d7/week", "None", "CES 3\u00d7/week; taVNS daily home device"],
    ],
)

# ─── ADHD ─────────────────────────────────────────────────────────────────────
CDATA["adhd"] = dict(
    slug="adhd", cover_title="ATTENTION DEFICIT HYPERACTIVITY DISORDER (ADHD)",
    name="Attention Deficit Hyperactivity Disorder (ADHD)", short="ADHD", abbr="ADHD",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in ADHD is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not currently extend to ADHD. Mandatory off-label "
        "disclosure and Doctor sign-off are required before TPS treatment for ADHD."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for ADHD requires specific, documented off-label disclosure with Doctor sign-off."
    ),
    prs_domain_label="ADHD Symptom Domains",
    prs_domain_header_line="ADHD Symptom Domains \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
    exam_step_heading="4.1 ADHD Symptom & Cognitive Examination",
    exam_step_desc=(
        "Conduct a systematic examination of attention, executive function, and hyperactivity-impulsivity "
        "using the Clinical Examination Checklist. Rate each domain on a 0\u20134 severity scale:"
    ),
    exam_checklist_item="\u2610 ADHD symptom & cognitive examination completed (all domains rated)",
    med_check_item="Record stimulant medication timing (last methylphenidate/amphetamine dose; ON/OFF stimulant state)",
    session_med_doc="medication state (stimulant dose and timing; ON/OFF stimulant status; any PRN taken)",
    false_class_body=(
        "Standardise stimulant medication timing between baseline and follow-up assessments. If baseline "
        "was conducted OFF stimulants and follow-up ON stimulants (or vice versa), this may create a false "
        "responder or false non-responder classification independent of NIBS effects."
    ),
    modality_table=[
        ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Open-label", "20+"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Pilot RCT, Double-blind Sham-controlled", "2+"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Open-label, Pilot", "0+"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Open-label, Pilot", "0+"],
        ["TMS", "NeuroStar / MagVenture / Magstim", "CE/FDA (research use)", "RCT, Open-label", "15+"],
        ["tACS", "Starstim / NeuroConn", "CE Class IIa (research)", "Open-label, Pilot", "5+"],
        ["PEMF", "BrainsWay / MagPro", "CE/FDA (research)", "Open-label, Pilot", "5+"],
    ],
    best_modality="tDCS (DLPFC), TMS",
    offlabel_table=[
        ["Modality", "Regulatory Status", "ADHD Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Level B evidence; established use in ADHD cognitive enhancement", "Standard informed consent"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Preliminary evidence; LC noradrenergic mechanism", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety)", "Comorbidity-indicated; anxiety/sleep in ADHD", "Standard informed consent"],
    ],
    prs_table=[
        ["Inattention Symptoms (0\u201310)", "Hyperactivity-Impulsivity & Executive (0\u201310)"],
        ["Difficulty sustaining attention on tasks", "Fidgeting / restlessness / can\u2019t stay seated"],
        ["Easily distracted by external stimuli", "Talking excessively / interrupting others"],
        ["Difficulty following through on instructions", "Impulsive decision-making / acting without thinking"],
        ["Loses things needed for tasks (keys, phone)", "Difficulty waiting turn / impatience"],
        ["Forgets daily activities / appointments", "Starting tasks without adequate preparation"],
        ["Avoids tasks requiring sustained mental effort", "Emotional dysregulation / mood swings"],
        ["Difficulty organising tasks and activities", "Time blindness / chronic lateness / deadline failure"],
        ["Executive dysfunction (planning, prioritising)", "Sleep problems (delayed onset, insufficient)"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["Sustained Attention", "CPT-3 continuous performance test; digit span (forward/backward)", "Omission/commission errors; z-score"],
        ["Working Memory", "Digit span, letter-number sequencing (WAIS-IV); N-back task", "Age-corrected scaled score"],
        ["Inhibitory Control", "Stroop colour-word test; stop-signal task performance", "Interference score; SSRT"],
        ["Psychomotor Observation", "Activity level during exam; interruptions; fidgeting; impulsive responding", "0\u20134 severity rating"],
        ["Executive Function Screen", "BRIEF-2 self-report; Trail Making Test A/B", "T-score; B/A ratio"],
        ["Emotional Dysregulation", "Outburst frequency, emotional reactivity, mood lability", "Clinical interview + rating"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["ASRS v1.1 (Adult ADHD Self-Report Scale)", "___ / 72", "\u226514 = probable ADHD (screening positive)"],
        ["Conners\u2019 Adult ADHD Rating Scale (CAARS)", "___ T-score", "T-score \u226565 = clinically elevated; \u226570 = severe"],
        ["BRIEF-2 (Behaviour Rating Inventory of Executive Function)", "___ T-score", "GEC T-score \u226565 = significant impairment"],
        ["CPT-3 (Continuous Performance Test)", "Inattention index", "d-prime <1.5; high commission errors"],
        ["PHQ-9 (Depression comorbidity)", "___ / 27", "\u226510 = comorbid depression present"],
        ["GAD-7 (Anxiety comorbidity)", "___ / 21", "\u226510 = comorbid anxiety present"],
        ["PSQI (Sleep quality)", "___ / 21", ">5 = sleep disturbance (common in ADHD)"],
        ["Wender Utah Rating Scale (childhood ADHD)", "___ / 100", "\u226546 = retrospective childhood ADHD"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Inattentive Dominant", "Prominent inattention, distractibility, forgetfulness; minimal hyperactivity; often missed in childhood; predominantly female presentation"],
        ["Hyperactive-Impulsive Dominant", "Motor hyperactivity, impulsive speaking and acting, restlessness; inhibitory control deficit; predominantly male in childhood"],
        ["Combined Presentation", "Both inattention and hyperactivity-impulsivity criteria met; most common adult diagnosis; DLPFC + right IFC targeting"],
        ["Executive Dysfunction Dominant", "Prominent planning, organisation, time management deficits; high BRIEF GEC; cognitive inflexibility; DLPFC + right PFC"],
        ["Emotional Dysregulation Dominant", "Rapid mood swings, rejection-sensitive dysphoria, emotional impulsivity; DLPFC + orbital-frontal circuit involvement"],
        ["ADHD + Anxiety Comorbid", "ADHD + GAD / social anxiety; stimulant treatment exacerbates anxiety; combined NIBS protocol essential"],
        ["ADHD + Depression Comorbid", "ADHD + MDD; low frustration tolerance driving hopelessness; bifrontal tDCS approach"],
        ["ADHD + ASD (dual diagnosis)", "Executive + social-cognitive deficits; specialised combined protocol; behavioural therapy backbone"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["L-DLPFC (F3)", "Attention / Working Memory", "N-back computerised task; digit span training; sustained attention apps (Lumosity/Cogmed)"],
        ["R-DLPFC (F4)", "Inhibitory Control / Impulsivity", "Stop-signal computerised training; go/no-go task; response inhibition exercises"],
        ["Bilateral DLPFC", "Executive Function / Planning", "Task-planning worksheet; time-management training; goal-setting structured exercise"],
        ["taVNS", "Arousal / Attention Regulation", "Paced breathing; mindfulness attention training; slow down exercise"],
        ["CES (Alpha-Stim)", "Sleep / Anxiety Comorbidity", "Sleep hygiene education; bedtime routine structuring; relaxation instruction"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["ASRS v1.1 (Primary)", "\u226530% reduction in total score = clinically meaningful improvement"],
        ["Conners\u2019 CAARS", "\u22655-point T-score reduction in Inattention or Hyperactivity subscale"],
        ["BRIEF-2 (Executive)", "\u22655-point T-score reduction in GEC (Global Executive Composite)"],
        ["CPT-3 Inattention", "Normalisation of d-prime score (d-prime >1.5) or reduction in omission errors"],
        ["PHQ-9 / GAD-7 (comorbidity)", "\u226550% reduction in comorbid depression/anxiety scores"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "Confirmed ADHD diagnosis (DSM-5); adult presentation (\u226518 years)"],
        ["2", "ASRS v1.1 \u226514 or Conners\u2019 T-score \u226565 at baseline"],
        ["3", "Age 18\u201360; capable of informed consent"],
        ["4", "Inadequate response to \u22651 stimulant trial (methylphenidate or amphetamine) or intolerance/contraindication"],
        ["5", "Stable medication for \u22654 weeks (if on stimulants/atomoxetine)"],
        ["6", "Neuropsychological testing confirming executive dysfunction (BRIEF GEC T-score \u226565)"],
        ["7", "No planned stimulant dose change for \u22658 weeks after enrolment"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Metallic implants in head/neck stimulation field"],
        ["2", "Uncontrolled seizure disorder (higher seizure risk with stimulants)"],
        ["3", "Active psychosis or severe bipolar disorder"],
        ["4", "Cardiac pacemaker or ICD (CES/taVNS contraindication)"],
        ["5", "Pregnancy"],
        ["6", "Active substance use disorder (stimulant misuse concern)"],
        ["7", "Intellectual disability (IQ <70) precluding consent or task engagement"],
        ["8", "Age <18 (paediatric protocol; separate pathway with parental consent)"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Stimulant cardiovascular effects", "ECG recommended in adults >45 years; cardiac clearance"],
        ["Bipolar II comorbidity", "Stimulants may destabilise; mood stabiliser required; NIBS protocol adapted"],
        ["Substance use history", "Document carefully; stimulant prescription safety considerations"],
        ["Tic disorder / Tourette comorbidity", "Stimulants may exacerbate tics; atomoxetine preferred; SMA cathodal option"],
        ["Autism Spectrum comorbidity", "Dual diagnosis: refer to combined ASD-ADHD pathway"],
        ["Sleep disorder comorbidity", "Delayed sleep phase common; CES primary modality; melatonin timing"],
        ["Anxiety comorbidity", "Stimulant-anxiety interaction; taVNS + CES first; dose timing critical"],
        ["Traumatic Brain Injury history", "ADHD-like post-TBI symptoms; refer to TBI protocol first"],
        ["Elderly ADHD (\u226560 years)", "Reduce intensities; cardiovascular monitoring; cognitive testing"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Inattentive Dominant", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin + N-back pairing", "DLPFC BA46: 250 pulses, 0.2\u202fHz", "taVNS 30min pre-session; CES sleep if needed"],
        ["Hyperactive-Impulsive", "Anodal R-DLPFC (F4) 2\u202fmA 20\u202fmin; inhibitory pairing", "R-IFC BA44: 200 pulses, 0.2\u202fHz", "taVNS vagal calming; CES anxiolytic"],
        ["Combined Presentation", "Bifrontal: anodal L-F3 / cathodal R-F4 or sequential", "DLPFC bilateral: 300 pulses", "taVNS 30min; CES comorbidity-driven"],
        ["Executive Dysfunction", "Anodal L-DLPFC (F3) 2\u202fmA + planning tasks", "DLPFC BA46 + right PFC: 300 pulses", "taVNS 30min; structured task training"],
        ["Emotional Dysregulation", "Anodal L-DLPFC (F3) 2\u202fmA + OFC", "OFC: 200 pulses", "taVNS 30min; DBT skills concurrent"],
        ["ADHD + Anxiety", "Anodal L-DLPFC (F3) 1.5\u202fmA (lower arousal)", "DLPFC: 200 pulses", "CES primary 60min; taVNS HRV training"],
        ["ADHD + Depression", "Anodal L-DLPFC (F3) 2\u202fmA (antidepressant effect)", "DLPFC + sgACC: 250 pulses", "taVNS 30min; CES nightly"],
        ["Maintenance", "Anodal L/R-DLPFC 1.5\u202fmA 20\u202fmin 2\u00d7/week", "None", "CES 3\u00d7/week; taVNS daily home device"],
    ],
)

# ─── ALZHEIMER'S ──────────────────────────────────────────────────────────────
CDATA["alzheimers"] = dict(
    slug="alzheimers", cover_title="ALZHEIMER'S DISEASE / MILD COGNITIVE IMPAIRMENT (MCI)",
    name="Alzheimer's Disease / MCI", short="Alzheimer's", abbr="AD/MCI",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in Alzheimer\u2019s Disease is supported by CE marking \u2014 the ONLY indication "
        "within the SOZO protocol portfolio for which TPS holds a CE-marked indication. "
        "Standard off-label disclosure still applies for MCI and early AD where evidence remains "
        "investigational. Full consent discussion is required."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for Alzheimer\u2019s Disease / MCI requires full informed consent including discussion "
        "of the investigational nature of the treatment for MCI and the evolving evidence base for AD."
    ),
    prs_domain_label="Cognitive & Functional Symptoms Domain",
    prs_domain_header_line="Cognitive & Functional Symptoms Domain \u2014 score each relevant item on a 0\u201310 scale (patient/caregiver-rated):",
    exam_step_heading="4.1 Cognitive Examination",
    exam_step_desc=(
        "Conduct a systematic cognitive examination using the Clinical Examination Checklist. "
        "Rate each domain using standardised scoring tools (ADAS-Cog, MoCA, CDR). "
        "Caregiver input is essential for functional assessment:"
    ),
    exam_checklist_item="\u2610 Cognitive examination completed (all domains assessed, caregiver input recorded)",
    med_check_item="Record current cholinesterase inhibitor/memantine timing and compliance (last dose)",
    session_med_doc="medication compliance (donepezil/rivastigmine/galantamine/memantine dose and timing)",
    false_class_body=(
        "Standardise cognitive testing conditions between baseline and follow-up. Practice effects on "
        "standardised tests (ADAS-Cog, MoCA) can create false responder classification. Use alternate "
        "test forms where available. Ensure caregiver-rated measures (CDR, ADCS-ADL) are completed by "
        "the same informant at baseline and follow-up."
    ),
    modality_table=[
        ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Open-label", "20+"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 CE-MARKED for Alzheimer\u2019s Disease", "RCT, Meta-analysis, Systematic Review", "31+"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Open-label, Pilot", "5+"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Open-label, Observational", "0+"],
        ["TMS", "NeuroStar / MagVenture / Magstim", "CE/FDA (research use)", "RCT, Open-label", "30+"],
        ["tACS", "Starstim / NeuroConn", "CE Class IIa (research)", "RCT, Open-label", "15+"],
        ["PBM", "Vielight Neuro / Coronet", "CE/FDA (research)", "Open-label, Pilot RCT", "20+"],
        ["PEMF", "BrainsWay / MagPro", "CE/FDA (research)", "Open-label, Pilot", "5+"],
        ["LIFU", "Sonic Concepts / FUS Instruments", "Investigational", "Pilot RCT, Open-label", "10+"],
        ["DBS", "Medtronic / Abbott", "FDA (research \u2014 Fornix/NBM)", "RCT, Open-label", "5+"],
    ],
    best_modality="TPS, TMS + Cognitive Training",
    offlabel_table=[
        ["Modality", "Regulatory Status", "AD/MCI Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Level B evidence; memory enhancement protocol", "Standard informed consent"],
        ["TPS", "CE Class IIa \u2014 AD INDICATION", "CE-MARKED for Alzheimer\u2019s Disease", "Standard consent; MCI: discuss investigational status"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Preliminary evidence; hippocampal neuroplasticity mechanism", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety)", "Sleep/anxiety comorbidity in dementia; Level C", "Standard informed consent"],
    ],
    prs_table=[
        ["Cognitive Symptoms (0\u201310)", "Neuropsychiatric & Functional Symptoms (0\u201310)"],
        ["Memory loss (episodic; recent events)", "Depression / low mood (NPI depressive sub-scale)"],
        ["Word-finding difficulty (anomia)", "Anxiety / worry / restlessness (NPI anxiety)"],
        ["Disorientation (time, place, person)", "Apathy / lack of motivation / withdrawal"],
        ["Difficulty learning new information", "Agitation / irritability / aggression (NPI)"],
        ["Executive dysfunction (planning, organising)", "Sleep disturbance (insomnia, sundowning)"],
        ["Visuospatial difficulties", "Wandering / behavioural disturbances"],
        ["Attention / concentration deficits", "Caregiver burden / family stress"],
        ["Activities of daily living (instrumental ADL)", "Overall quality of life (patient/caregiver)"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["Episodic Memory", "ADAS-Cog word recall; Rey AVLT; WMS Logical Memory", "Number recalled; learning slope"],
        ["Language", "Confrontation naming (BNT-15); verbal fluency (FAS/animals)", "Words named/minute; error types"],
        ["Visuospatial Function", "Clock drawing test; Rey-Osterrieth copy", "CDT score 0\u201310; accuracy"],
        ["Executive Function", "Trail Making B; FAS verbal fluency; digit span backward", "Time; errors; scaled score"],
        ["Attention / Processing Speed", "Trail Making A; digit span forward; SDMT", "Time; scaled score"],
        ["Global Cognition", "MoCA; MMSE; ADAS-Cog total", "Total scores with thresholds"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["MoCA (Montreal Cognitive Assessment)", "___ / 30", "<26 = MCI screening positive; <18 = dementia range"],
        ["MMSE (Mini-Mental State Examination)", "___ / 30", "\u226524 = normal; 18\u201323 = mild; <18 = moderate"],
        ["ADAS-Cog-13 (Primary outcome)", "___ / 85", "\u22658 = MCI; \u226518 = mild AD; \u226535 = moderate AD"],
        ["CDR (Clinical Dementia Rating)", "0 / 0.5 / 1 / 2 / 3", "0=Normal; 0.5=MCI; 1=Mild AD; 2=Moderate; 3=Severe"],
        ["PHQ-9 (Depression comorbidity)", "___ / 27", "\u226510 = comorbid depression (affects cognition)"],
        ["NPI (Neuropsychiatric Inventory)", "___ / 144", "Total score; subscale severity \u00d7 frequency"],
        ["ADCS-ADL (Activities of Daily Living)", "___ / 78", "Lower scores = greater functional impairment"],
        ["Caregiver burden (ZBI)", "___ / 88", "\u226521 = mild; \u226541 = moderate-severe caregiver burden"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Amnestic MCI (Single Domain)", "Isolated memory impairment; MoCA borderline; normal ADLs; highest conversion risk to AD"],
        ["Amnestic MCI (Multi-Domain)", "Memory + executive or language deficit; broader network involvement; moderate conversion risk"],
        ["Non-Amnestic MCI", "Primary executive, language, or visuospatial impairment; possible frontotemporal or LBD pathway"],
        ["Early-Onset AD (<65)", "Younger onset; often non-amnestic or atypical presentation; more genetic risk; greater executive involvement"],
        ["Late-Onset AD (\u226565)", "Classic amnestic-dominant; medial temporal lobe atrophy; entorhinal-hippocampal circuit"],
        ["AD with Behavioural Symptoms", "Prominent agitation, apathy, wandering; NPI total \u226520; caregiving crisis risk"],
        ["AD with Depression", "Comorbid MDD; CSDD \u226510; affects cognitive testing; dual protocol required"],
        ["Vascular Cognitive Impairment", "Cerebrovascular risk factors; white matter lesions; stepwise course; DLPFC + vascular risk management"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["Temporal-Parietal (T5/P5)", "Memory / Episodic Recall", "Memory encoding tasks; face-name learning; spaced retrieval practice; reminiscence therapy"],
        ["L-DLPFC (F3)", "Executive / Working Memory", "N-back tasks; computerised cognitive training (Cogmed); category fluency exercises"],
        ["Hippocampal-Entorhinal (TPS)", "Memory Consolidation", "Episodic memory encoding tasks; autobiographical memory review; spatial navigation exercise"],
        ["taVNS", "Hippocampal Theta / Memory", "Associative learning tasks; memory palace technique; verbal recall pairing"],
        ["CES (Alpha-Stim)", "Sleep / Agitation / Anxiety", "Sleep hygiene for dementia; relaxation routine; sundowning management protocol"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["ADAS-Cog-13 (Primary)", "\u22654-point improvement = clinically meaningful; stabilisation of decline = Partial"],
        ["MoCA", "\u22652-point improvement = clinically meaningful; no decline from baseline = Partial"],
        ["CDR-SB (Sum of Boxes)", "Stabilisation or \u22650.5-point improvement in CDR-SB"],
        ["NPI (Behavioural)", "\u226530% reduction in total NPI score or \u22654-point reduction"],
        ["ADCS-ADL (Functional)", "Stabilisation of ADL score or \u22652-point improvement"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "Confirmed MCI or mild AD diagnosis (NIA-AA 2018 criteria or DSM-5)"],
        ["2", "MoCA 14\u201326 at baseline (MCI or mild-moderate range)"],
        ["3", "Age 55\u201385; capable of assent or consent with caregiver support"],
        ["4", "Stable cholinesterase inhibitor / memantine \u22653 months (if prescribed)"],
        ["5", "Reliable caregiver available for assessments and home monitoring"],
        ["6", "No planned medication changes for \u22658 weeks after enrolment"],
        ["7", "Caregiver willing to participate in home-use training and supervision"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Moderate-severe AD (MMSE <15 / CDR \u22652) without capable proxy consent"],
        ["2", "Metallic implants in head/neck stimulation field"],
        ["3", "Active delirium or acute confusional state"],
        ["4", "Uncontrolled epilepsy or seizure disorder"],
        ["5", "Cardiac pacemaker or ICD (CES / taVNS contraindication)"],
        ["6", "Severe psychiatric comorbidity (active psychosis, severe agitation requiring hospitalisation)"],
        ["7", "Terminal illness or life expectancy <6 months"],
        ["8", "Rapidly progressive dementia (prion disease screen required)"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Lewy Body Dementia (LBD) differential", "Specialist neuroradiology required before TPS; fluctuating cognition affects testing"],
        ["Frontotemporal Dementia (FTD)", "Different circuit targets (frontotemporal); refer to specialist pathway"],
        ["Vascular risk factors (hypertension, diabetes)", "Optimise vascular risk control; concurrent management essential"],
        ["Caregiver unavailable or stressed", "Assess caregiver burden (ZBI); caregiver support referral"],
        ["Depression comorbidity (CSDD \u226510)", "Treat depression first or simultaneously; confounds cognitive assessment"],
        ["Falls risk (MMSE <20)", "Physiotherapy concurrent; fall prevention protocol; home safety assessment"],
        ["Agitation / NPI \u226520", "Behavioural management strategies first; CES + taVNS primary NIBS"],
        ["Post-COVID cognitive impairment", "Consider Long COVID protocol; different pathophysiology and targets"],
        ["Visual or hearing impairment", "Adapt cognitive testing (normed versions); communication adjustments"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Amnestic MCI", "Anodal T5 (temporo-parietal) 1.5\u202fmA 20\u202fmin", "Hippocampus / entorhinal: T1 protocol 300 pulses", "taVNS theta enhancement 30min; CES sleep/agitation"],
        ["Multi-Domain MCI", "Anodal T5 + L-DLPFC (F3) sequential", "Hippocampal + DLPFC: 300 pulses", "taVNS 30min; CES nightly"],
        ["Early-Onset AD", "Anodal L-DLPFC (F3) 2\u202fmA + T5", "DLPFC + hippocampal: 350 pulses", "taVNS 30min; CES 60min"],
        ["Late-Onset AD", "Anodal T5 (bilateral if available) 1.5\u202fmA", "Hippocampal-entorhinal: 300 pulses", "taVNS 30min; CES nightly 60min"],
        ["AD with Behavioural Symptoms", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "DLPFC: 200 pulses (behavioural)", "CES primary 60min; taVNS agitation"],
        ["AD with Depression", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "DLPFC + sgACC: 250 pulses", "taVNS 30min; CES nightly"],
        ["Vascular Cognitive Impairment", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "DLPFC: 250 pulses", "taVNS cardiovascular; CES sleep"],
        ["Maintenance (stable AD)", "Anodal T5 1\u202fmA 15\u202fmin 2\u00d7/week", "None / minimal", "CES 3\u00d7/week; taVNS daily"],
    ],
)
