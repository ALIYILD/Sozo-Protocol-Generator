"""Condition data: Stroke Rehab, TBI, Chronic Pain, PTSD"""

CDATA = {}

# ─── STROKE REHAB ─────────────────────────────────────────────────────────────
CDATA["stroke_rehab"] = dict(
    slug="stroke_rehab", cover_title="POST-STROKE REHABILITATION",
    name="Post-Stroke Rehabilitation", short="Stroke", abbr="Stroke",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in Post-Stroke Rehabilitation is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not currently extend to stroke rehabilitation. Mandatory off-label "
        "disclosure and Doctor sign-off are required before TPS treatment for stroke."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for Post-Stroke Rehabilitation requires specific, documented off-label disclosure with Doctor sign-off."
    ),
    prs_domain_label="Post-Stroke Symptom Domains",
    prs_domain_header_line="Post-Stroke Symptom Domains \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
    exam_step_heading="4.1 Neurological & Motor Examination",
    exam_step_desc=(
        "Conduct a systematic neurological and motor examination using the Clinical Examination Checklist. "
        "Score each domain using the Fugl-Meyer Assessment (FMA) and standardised neurological tools:"
    ),
    exam_checklist_item="\u2610 Neurological & motor examination completed (FMA scored, deficit domains documented)",
    med_check_item="Record antithrombotic/antiplatelet medication compliance and BP reading (last dose timing)",
    session_med_doc="medication compliance (antiplatelets, statins, antihypertensives; BP at session start)",
    false_class_body=(
        "Standardise neurological assessment conditions between baseline and follow-up. Motor performance "
        "in stroke rehabilitation shows significant diurnal and fatigue-related variation. Ensure assessments "
        "occur at the same time of day and following comparable rest periods to avoid false responder or "
        "false non-responder classification."
    ),
    modality_table=[
        ["Modality", "Device", "Classification", "Stroke Evidence Status"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Level A evidence (motor; Elsner 2016 Cochrane review)"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL \u2014 OFF-LABEL for Stroke"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Level B evidence; VNS-paired rehabilitation (Engineer 2011)"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Level C (mood/sleep comorbidity; post-stroke depression)"],
    ],
    offlabel_table=[
        ["Modality", "Regulatory Status", "Stroke Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Level A evidence; well-established stroke motor protocol", "Standard informed consent"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Level B; VNS-paired limb rehabilitation evidence", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety/depression/insomnia)", "Post-stroke depression/anxiety comorbidity", "Standard informed consent"],
    ],
    prs_table=[
        ["Motor & Sensory Symptoms (0\u201310)", "Cognitive & Functional Symptoms (0\u201310)"],
        ["Upper limb weakness / paresis", "Memory difficulties (post-stroke)"],
        ["Lower limb weakness / gait impairment", "Attention / concentration deficits"],
        ["Hand/finger dexterity impairment", "Word-finding / speech difficulties"],
        ["Spasticity / muscle stiffness", "Depression / emotional lability"],
        ["Sensory loss (touch, proprioception)", "Fatigue (post-stroke)"],
        ["Balance / coordination deficits", "Anxiety (post-stroke)"],
        ["Dysphagia / swallowing difficulty", "Activities of daily living (independence)"],
        ["Hemispatial neglect", "Overall quality of life / participation"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["Upper Limb Motor (FMA-UE)", "Fugl-Meyer Assessment \u2014 Upper Extremity (66 items)", "0\u201366; <50 = severe impairment"],
        ["Lower Limb / Gait (FMA-LE)", "Fugl-Meyer Assessment \u2014 Lower Extremity (34 items)", "0\u201334; Timed 10m Walk Test"],
        ["Hand Dexterity", "9-Hole Peg Test (9HPT); grip dynamometry", "Time in seconds; force in kg"],
        ["Neurological Deficit (NIHSS)", "NIH Stroke Scale (15 domains)", "0=no deficit; 42=maximal"],
        ["Cognitive Screen", "MoCA; Trail Making A/B; digit span", "Standard thresholds"],
        ["Post-Stroke Depression/Anxiety", "PHQ-9; GAD-7; HADS", "Score + clinical decision"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["Fugl-Meyer Assessment UE (FMA-UE)", "___ / 66", "<10 = severe; 10\u201322 = marked; 23\u201352 = moderate; 53\u201366 = mild"],
        ["NIHSS (NIH Stroke Scale)", "___ / 42", "0\u20131=minimal; 2\u20134=mild; 5\u201315=moderate; 16\u201320=severe"],
        ["mRS (Modified Rankin Scale)", "0\u20136", "0=no symptoms; 3=moderate disability; 5=severe; 6=death"],
        ["Action Research Arm Test (ARAT)", "___ / 57", "Lower score = greater impairment; MCID = 5\u20136 points"],
        ["PHQ-9 (Post-stroke depression)", "___ / 27", "\u226510 = significant post-stroke depression"],
        ["MoCA (Cognitive post-stroke)", "___ / 30", "<26 = post-stroke cognitive impairment"],
        ["Barthel Index (Functional)", "___ / 100", "<60 = moderate disability; <40 = severe; 100 = independent"],
        ["Timed Up and Go (TUG) Test", "___ seconds", ">12s = fall risk; >20s = requires assistance"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Motor \u2014 Upper Limb Dominant", "Hemiplegia/paresis affecting arm/hand; FMA-UE <52; primary motor cortex deficit; contralateral M1 targeting"],
        ["Motor \u2014 Lower Limb / Gait", "Gait impairment, balance deficits, fall risk; FMA-LE impaired; M1 bilateral + supplementary motor area"],
        ["Aphasia / Language", "Expressive (Broca\u2019s area); receptive (Wernicke\u2019s); global; speech-language therapy concurrent essential"],
        ["Hemispatial Neglect", "Right hemisphere stroke; left-sided inattention; TPS + DLPFC targeting; prism adaptation concurrent"],
        ["Cognitive Impairment", "Post-stroke cognitive impairment (PSCI); attention, working memory, processing speed; DLPFC targeting"],
        ["Post-Stroke Depression", "Depression in 30\u201340% of stroke survivors; PHQ-9 \u226510; bifrontal tDCS + taVNS + CES"],
        ["Spasticity-Dominant", "Velocity-dependent resistance; FMA muscle tone items elevated; cathodal C1/C2 tDCS; TPS motor cortex"],
        ["Mixed Motor + Cognitive", "Combined motor and cognitive deficits; combined M1 + DLPFC tDCS protocol; longest treatment course"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["M1 (C3/C4)", "Motor Rehabilitation", "Active/passive upper limb motor exercises; robot-assisted therapy; constraint-induced movement therapy (CIMT)"],
        ["L-DLPFC (F3)", "Cognitive / Mood", "Attention training; working memory tasks; post-stroke cognitive rehabilitation programme"],
        ["M1 + SMA (TPS)", "Motor Sequence / Gait", "Gait training (parallel bars/treadmill); repetitive upper limb task practice; functional electrical stimulation pairing"],
        ["taVNS", "VNS-Paired Rehabilitation", "Paired limb movement during taVNS (VNS-paired rehabilitation protocol); active task concurrent with stimulation"],
        ["CES (Alpha-Stim)", "Sleep / Mood / Fatigue", "Sleep hygiene education; fatigue management; relaxation for post-stroke anxiety"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["FMA-UE (Primary motor)", "MCID \u22655.25 points improvement; clinically meaningful \u226510 points"],
        ["NIHSS", "\u22654-point reduction or 1-point on mRS = clinically meaningful"],
        ["ARAT / Dexterity", "ARAT MCID = 5\u20136 points; 9HPT \u226520% improvement in time"],
        ["PHQ-9 (post-stroke depression)", "\u226550% reduction or score \u22644 = remission"],
        ["Barthel / mRS (Functional)", "\u22661-point mRS improvement or \u226510-point Barthel improvement"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "Confirmed ischaemic or haemorrhagic stroke (radiological + clinical criteria)"],
        ["2", "Post-acute phase: \u22661 month post-stroke; stable neurological status"],
        ["3", "Residual motor, cognitive, or language deficit amenable to rehabilitation"],
        ["4", "Age 18\u201385; capable of informed consent or has appropriate surrogate"],
        ["5", "Stable antithrombotic/antihypertensive medication for \u22654 weeks"],
        ["6", "Haemorrhagic stroke: \u22654 months post-event; neurosurgical clearance obtained"],
        ["7", "Able to participate in concurrent physical/occupational rehabilitation"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Acute stroke (<4 weeks); unstable neurological status"],
        ["2", "Metallic implants in head/neck stimulation field"],
        ["3", "Uncontrolled seizure disorder (post-stroke epilepsy)"],
        ["4", "Cardiac pacemaker or ICD"],
        ["5", "Severe cognitive impairment precluding engagement (MMSE <10)"],
        ["6", "Active malignancy or systemic illness limiting participation"],
        ["7", "Haemorrhagic transformation or new haemorrhage on recent imaging"],
        ["8", "Pregnancy"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Haemorrhagic stroke (<4 months)", "Neurosurgical clearance required; TPS deferred; tDCS low intensity only"],
        ["Epilepsy post-stroke", "Anti-epileptic medication confirmed; neurology clearance; reduce tDCS intensity"],
        ["Severe aphasia", "Adapted consent procedure; surrogate consent where needed; non-verbal outcome measures"],
        ["Atrial fibrillation", "INR monitoring if anticoagulated; taVNS cardiac safety assessment"],
        ["Dysphagia", "Speech-language therapy concurrent essential; choking risk during sessions"],
        ["Severe spasticity (MAS \u22653)", "Spasticity management before NIBS; botulinum toxin coordination"],
        ["Depression comorbidity", "Treat concurrently; bifrontal tDCS protocol adaptation"],
        ["Elderly (\u226575)", "Reduce intensities; longer rest between sessions; fall prevention essential"],
        ["Large cortical lesion volume", "Reduced cortical excitability; may require higher session frequency; neuroplasticity assessment"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Motor \u2014 Upper Limb", "Anodal M1 ipsilesional (C3/C4) 2\u202fmA 20\u202fmin", "M1 motor cortex: 300 pulses, 0.25\u202fHz", "taVNS paired with motor task; CES fatigue/mood"],
        ["Motor \u2014 Lower Limb/Gait", "Anodal M1 bilateral or ipsilesional 2\u202fmA", "M1 + SMA: 300 pulses", "taVNS gait-paired; CES sleep/fatigue"],
        ["Aphasia/Language", "Anodal left IFG (F7) 1\u202fmA; cathodal right IFG", "Left IFG (Broca): 200 pulses", "taVNS paired with speech tasks; SLT concurrent"],
        ["Hemispatial Neglect", "Cathodal right posterior parietal; anodal left PPC", "Right parietal: 200 pulses", "Prism adaptation concurrent; CES adjunct"],
        ["Cognitive Impairment", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "DLPFC BA46: 250 pulses", "taVNS cognitive pairing; CES sleep"],
        ["Post-Stroke Depression", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "DLPFC + sgACC: 250 pulses", "taVNS 30min; CES nightly 60min"],
        ["Spasticity-Dominant", "Cathodal M1 contralesional 1.5\u202fmA", "M1: 200 pulses low intensity", "taVNS antispastic adjunct; physiotherapy concurrent"],
        ["Mixed Motor + Cognitive", "Sequential M1 (20min) + L-DLPFC (20min)", "M1 + DLPFC: 400 pulses total", "taVNS paired; CES nightly; intensive rehab"],
    ],
)

# ─── TBI ──────────────────────────────────────────────────────────────────────
CDATA["tbi"] = dict(
    slug="tbi", cover_title="TRAUMATIC BRAIN INJURY (TBI)",
    name="Traumatic Brain Injury (TBI)", short="TBI", abbr="TBI",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in Traumatic Brain Injury is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not currently extend to TBI. Mandatory off-label disclosure and Doctor "
        "sign-off are required before TPS treatment for TBI."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for TBI requires specific, documented off-label disclosure with Doctor sign-off. "
        "Post-traumatic seizure risk must be formally assessed before initiating any NIBS."
    ),
    prs_domain_label="Post-TBI Symptom Domains",
    prs_domain_header_line="Post-TBI Symptom Domains \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
    exam_step_heading="4.1 Post-TBI Neurological Examination",
    exam_step_desc=(
        "Conduct a systematic post-TBI neurological examination using the Clinical Examination Checklist. "
        "Score each domain; integrate with GOSE, RPQ, and neuropsychological test data:"
    ),
    exam_checklist_item="\u2610 Post-TBI neurological examination completed (all deficit domains documented)",
    med_check_item="Record TBI medication compliance (methylphenidate, amantadine, anti-epileptics if prescribed; last dose timing)",
    session_med_doc="medication compliance (stimulants, amantadine, anti-epileptics; dose and timing)",
    false_class_body=(
        "Standardise neuropsychological assessment conditions between baseline and follow-up. "
        "Post-TBI cognitive performance is highly sensitive to fatigue, sleep quality, and pain. "
        "Ensure assessments occur at the same time of day, with comparable fatigue levels, to avoid "
        "false responder or false non-responder classification."
    ),
    modality_table=[
        ["Modality", "Device", "Classification", "TBI Evidence Status"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Level B evidence (cognitive; Kuo 2014; DLPFC/M1 protocols)"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL \u2014 OFF-LABEL for TBI"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Level C (neuroprotective; anti-inflammatory mechanism)"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Level B (PTSD/insomnia in TBI; Lande 2018)"],
    ],
    offlabel_table=[
        ["Modality", "Regulatory Status", "TBI Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Level B evidence; DLPFC and motor cortex protocols established", "Standard informed consent"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Neuroprotective mechanism; Level C for TBI", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety/depression/insomnia)", "PTSD/insomnia comorbidity in TBI; Level B", "Standard informed consent"],
    ],
    prs_table=[
        ["Cognitive Symptoms (0\u201310)", "Somatic & Psychological Symptoms (0\u201310)"],
        ["Concentration / attention difficulty", "Headache (post-traumatic)"],
        ["Memory impairment (working/episodic)", "Sleep disturbance (insomnia/hypersomnia)"],
        ["Executive dysfunction (planning, organising)", "Fatigue (post-traumatic; disproportionate)"],
        ["Processing speed reduction", "Depression / low mood"],
        ["Word-finding difficulty", "Anxiety / irritability / emotional lability"],
        ["Cognitive fatigue (mental exhaustion)", "Dizziness / balance problems"],
        ["Difficulty multitasking", "Sensitivity to light/noise (post-concussion)"],
        ["Return-to-work/study impairment", "Overall quality of life / participation"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["Cognitive Function (RBANS)", "RBANS total scale index; memory, attention, language, visuospatial", "Age-corrected index score; impairment <80"],
        ["Executive Function", "Trail Making B; FAS verbal fluency; BRIEF-A self-report", "Time; T-score; errors"],
        ["Processing Speed", "Trail Making A; SDMT; WAIS-IV Processing Speed Index", "Time; raw score; scaled score"],
        ["Post-Concussion Symptoms (RPQ)", "Rivermead Post-Concussion Questionnaire (16 items)", "Total 0\u201364; >12 = significant burden"],
        ["Mood & Anxiety", "PHQ-9; GAD-7; PTSD screen (PC-PTSD-5)", "Standard thresholds"],
        ["Global Outcome (GOSE)", "Glasgow Outcome Scale \u2014 Extended (structured interview)", "1=death; 8=upper good recovery"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["RBANS (Repeatable Battery for Assessment of Neuropsychological Status)", "___ Index", "<80 = impaired; <70 = moderately impaired; <55 = severely impaired"],
        ["GOSE (Glasgow Outcome Scale \u2014 Extended)", "1\u20138", "5\u20136 = moderate disability; 7\u20138 = good recovery (target)"],
        ["RPQ (Rivermead Post-Concussion Questionnaire)", "___ / 64", ">12 = significant post-concussion symptom burden"],
        ["NSI (Neurobehavioral Symptom Inventory)", "___ / 88", ">25 = moderate symptom burden; >50 = severe"],
        ["PHQ-9 (TBI depression)", "___ / 27", "\u226510 = comorbid depression present"],
        ["GAD-7 (TBI anxiety)", "___ / 21", "\u226510 = comorbid anxiety"],
        ["PC-PTSD-5 (PTSD screen)", "___ / 5", "\u22653 = PTSD screening positive; full CAPS-5 if positive"],
        ["MoCA (Cognitive)", "___ / 30", "<26 = cognitive impairment screen positive"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Mild TBI / Concussion", "GCS 13\u201315 at injury; post-concussion symptoms (RPQ >12); normal MRI; often normal CT; CTE risk monitoring"],
        ["Moderate-Severe TBI", "GCS <13; structural lesions on imaging; longer PTA; more significant neurological deficits; complex protocol"],
        ["Executive Dysfunction Dominant", "Frontal lobe damage; BRIEF-A elevated; planning/initiation deficits; perseveration; DLPFC primary target"],
        ["Post-Traumatic Cognitive Impairment", "RBANS <80; attention/processing/memory; white matter injury; TBI-specific neuroplasticity protocol"],
        ["Post-Traumatic Headache", "New-onset headache post-TBI; most common chronic symptom; CGRP pathway; CES primary; TPS investigational"],
        ["TBI + PTSD Comorbidity", "TBI + trauma-related PTSD; dual protocol; taVNS + tDCS DLPFC + CES; trauma-focused therapy required"],
        ["TBI + Depression", "PHQ-9 \u226510; post-TBI depression; neurobiological + psychological; bifrontal tDCS + CES + taVNS"],
        ["Chronic Phase TBI (\u22661 year)", "Chronic symptoms; plateau in natural recovery; NIBS augments remaining neuroplasticity; intensive protocol"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["L-DLPFC (F3)", "Executive / Working Memory", "N-back tasks; working memory computerised training; executive function worksheets; goal management training"],
        ["M1 (C3/C4)", "Motor Recovery (if deficit)", "Active upper/lower limb exercises; gait training; functional task practice"],
        ["DLPFC + Processing Speed (TPS)", "Processing Speed / Attention", "Timed computerised attention tasks; SDMT practice; paced information processing"],
        ["taVNS", "Arousal / Anti-Inflammatory", "Cognitive engagement tasks during taVNS; mindful attention pairing; neuroprotective protocol"],
        ["CES (Alpha-Stim)", "Sleep / PTSD / Headache", "Sleep hygiene; PTSD relaxation protocol; headache management education"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["RBANS Total Index (Primary)", "\u22658-point improvement = clinically meaningful (1 SD improvement)"],
        ["GOSE (Global Outcome)", "\u22661-point GOSE improvement = clinically meaningful progress"],
        ["RPQ (Post-concussion)", "\u226550% reduction in RPQ total score = clinical response"],
        ["PHQ-9 / GAD-7 (Comorbid mood)", "\u226550% reduction = response; score \u22644 = remission"],
        ["NSI (Symptom Burden)", "\u226530% reduction in NSI total score"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "Confirmed TBI diagnosis (any severity); post-acute phase (\u22661 month post-injury)"],
        ["2", "Residual cognitive, behavioural, or functional deficit amenable to rehabilitation"],
        ["3", "Age 18\u201370; capable of informed consent"],
        ["4", "Stable neurological status; no new lesions on recent imaging"],
        ["5", "Seizure risk assessed: post-traumatic epilepsy controlled or excluded"],
        ["6", "Stable medication for \u22654 weeks (if on stimulants/amantadine)"],
        ["7", "Motivated for rehabilitation and cognitive training participation"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Acute TBI phase (<4 weeks post-injury; <6 months for moderate-severe)"],
        ["2", "Metallic implants in head/neck stimulation field"],
        ["3", "Uncontrolled post-traumatic epilepsy"],
        ["4", "Cardiac pacemaker or ICD"],
        ["5", "Active intracranial bleeding or recent neurosurgery (<6 months)"],
        ["6", "Severe psychiatric comorbidity precluding engagement (active psychosis)"],
        ["7", "Active substance use disorder confounding presentation"],
        ["8", "Pending legal proceedings where NIBS may create assessment confound (case-by-case)"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Post-traumatic epilepsy", "Neurological clearance; anti-epileptic confirmation; reduce tDCS intensity"],
        ["Skull defect / cranioplasty", "TPS and tDCS: safety assessment of stimulation field; may require protocol modification"],
        ["Active litigation", "Document carefully; independent neuropsychological assessment baseline"],
        ["PTSD comorbidity", "Dual protocol; trauma-focused therapy concurrent; taVNS primary for hyperarousal"],
        ["Substance use (self-medication)", "Detox first if required; NIBS after stable abstinence"],
        ["Cervical spine injury (concurrent)", "taVNS ear clip: check neck positioning; CES may be preferable"],
        ["Visual/hearing impairment", "Adapt cognitive testing; communication adjustments"],
        ["Sleep apnoea comorbidity", "CPAP adherence required; CES adjunct"],
        ["Chronic pain comorbidity", "Refer to combined TBI-pain protocol; M1 + DLPFC combined approach"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Mild TBI / Concussion", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "DLPFC: 200 pulses, 0.2\u202fHz (low intensity)", "CES primary (headache/sleep); taVNS 30min"],
        ["Moderate-Severe TBI", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin + M1 if motor deficit", "DLPFC + M1: 300 pulses", "taVNS neuroprotective; CES sleep/mood"],
        ["Executive Dysfunction", "Anodal L-DLPFC (F3) 2\u202fmA + executive tasks", "DLPFC BA46: 300 pulses", "taVNS 30min; structured executive training"],
        ["Post-TBI Cognitive Impairment", "Anodal L-DLPFC (F3) + bilateral DLPFC", "DLPFC + right PFC: 300 pulses", "taVNS 30min; cognitive rehab concurrent"],
        ["Post-Traumatic Headache", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "None initial (headache caution)", "CES primary 60min; taVNS 30min"],
        ["TBI + PTSD", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "DLPFC + vmPFC: 250 pulses", "taVNS 30min; CES nightly; trauma therapy"],
        ["TBI + Depression", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "DLPFC + sgACC: 250 pulses", "taVNS 30min; CES nightly 60min"],
        ["Chronic Phase TBI", "Anodal L-DLPFC (F3) 2\u202fmA; higher frequency (5\u00d7/week)", "DLPFC + M1 if motor: 350 pulses", "taVNS 2\u00d7 daily; CES nightly; intensive programme"],
    ],
)

# ─── CHRONIC PAIN ─────────────────────────────────────────────────────────────
CDATA["chronic_pain"] = dict(
    slug="chronic_pain", cover_title="CHRONIC PAIN SYNDROME",
    name="Chronic Pain Syndrome", short="Chronic Pain", abbr="Pain",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in Chronic Pain is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not currently extend to chronic pain. Mandatory off-label "
        "disclosure and Doctor sign-off are required before TPS treatment for chronic pain."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for Chronic Pain requires specific, documented off-label disclosure with Doctor sign-off."
    ),
    prs_domain_label="Pain & Functional Symptom Domains",
    prs_domain_header_line="Pain & Functional Symptom Domains \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
    exam_step_heading="4.1 Pain & Sensory Examination",
    exam_step_desc=(
        "Conduct a systematic pain and sensory examination using the Clinical Examination Checklist. "
        "Score each domain; document pain distribution, quality, and associated sensory findings:"
    ),
    exam_checklist_item="\u2610 Pain & sensory examination completed (NRS documented; sensory signs noted)",
    med_check_item="Record analgesic medication compliance (last opioid/anticonvulsant/SNRI dose and timing)",
    session_med_doc="medication compliance (analgesics, anticonvulsants, SNRIs; dose and timing relative to session)",
    false_class_body=(
        "Standardise pain assessment conditions between baseline and follow-up. Pain intensity is "
        "highly variable across the day and is influenced by recent activity, sleep quality, and "
        "weather. Ensure NRS ratings are collected at the same time of day and after comparable "
        "activity levels to avoid false responder or false non-responder classification."
    ),
    modality_table=[
        ["Modality", "Device", "Classification", "Chronic Pain Evidence Status"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Level A evidence (M1 anodal; Lefaucheur 2016 guidelines)"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL \u2014 OFF-LABEL for Chronic Pain"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Level B evidence (descending inhibition; Busch 2013)"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Level A evidence (pain; Lande 2018 meta-analysis)"],
    ],
    offlabel_table=[
        ["Modality", "Regulatory Status", "Chronic Pain Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Level A evidence; M1 anodal gold standard protocol", "Standard informed consent"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Level B; descending inhibition enhancement", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety/depression/insomnia)", "Level A analgesic; also addresses comorbid sleep/anxiety", "Standard informed consent"],
    ],
    prs_table=[
        ["Core Pain Symptoms (0\u201310)", "Functional & Psychological Symptoms (0\u201310)"],
        ["Spontaneous pain intensity (NRS 0\u201310)", "Sleep disturbance due to pain"],
        ["Allodynia (pain from light touch/pressure)", "Depression / low mood"],
        ["Hyperalgesia (exaggerated pain response)", "Anxiety / fear of movement (kinesiophobia)"],
        ["Pain distribution / spread", "Fatigue (pain-related)"],
        ["Neuropathic features (burning, electric, shooting)", "Cognitive difficulties (pain fog)"],
        ["Pain catastrophising severity", "Social/occupational function impairment"],
        ["Activity avoidance / fear-avoidance", "Medication overuse / dependence concern"],
        ["Pain variability (fluctuation frequency)", "Overall quality of life / wellbeing"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["Pain Intensity & Distribution", "NRS (0\u201310) at rest/movement; pain body diagram", "NRS score; area affected"],
        ["Sensory Testing (QST-screen)", "Von Frey touch threshold; pressure pain threshold (PPT)", "g-force; kPa; central sensitisation indicators"],
        ["Allodynia / Hyperalgesia", "Mechanical allodynia (cotton wool); temporal summation", "Present / absent; +/\u2212 central sensitisation"],
        ["Motor Function (if affected)", "Grip strength (dynamometry); functional mobility", "Force in kg; Timed Up and Go"],
        ["Psychological Assessment", "PCS (Pain Catastrophising Scale); FABQ (fear-avoidance)", "PCS total; FABQ-PA and FABQ-W subscales"],
        ["Global Function", "Brief Pain Inventory (BPI) interference subscale; PROMIS Physical Function", "BPI 0\u201310; PROMIS T-score"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["NRS Pain Score (Numeric Rating Scale)", "___ / 10", "\u22644 = mild; 5\u20136 = moderate; \u22657 = severe (primary outcome)"],
        ["Brief Pain Inventory (BPI)", "Severity: ___ / 10; Interference: ___ / 10", "MCID: \u22652-point reduction in BPI worst pain"],
        ["Pain Catastrophising Scale (PCS)", "___ / 52", "\u226530 = high catastrophising; MCID = \u22656.5 points"],
        ["PROMIS Pain Interference T-score", "___ T-score", "T-score \u226560 = above-average interference; MCID = 5 points"],
        ["PHQ-9 (Depression comorbidity)", "___ / 27", "\u226510 = comorbid depression present"],
        ["PSQI (Sleep quality)", "___ / 21", ">5 = pain-related sleep disruption"],
        ["DASS-21 (Depression/Anxiety/Stress)", "___ / 42", "Subscale >7 = mild; >10 = moderate; >17 = severe"],
        ["Patient Global Impression of Change (PGIC)", "1\u20137", "\u22655 = much improved (responder threshold)"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Neuropathic Dominant", "Burning, lancinating, electric pain; positive sensory signs (allodynia, hyperalgesia); peripheral nerve or CNS lesion identified"],
        ["Central Sensitisation Dominant", "Widespread pain; fatigue; cognitive fog; allodynia without peripheral lesion; fibromyalgia features; thalamic dysrhythmia"],
        ["Affective-Pain Dominant", "High catastrophising (PCS \u226530); depression-pain comorbidity; affective suffering disproportionate to nociception"],
        ["Musculoskeletal-Central Mixed", "Structural pathology (MSK) plus central amplification; inconsistent response to local treatment; mixed nociceptive-nociplastic"],
        ["Catastrophising Dominant", "High PCS; extreme disability relative to objective findings; fear-avoidance; helplessness; magnification"],
        ["Sleep-Pain Comorbid", "Insomnia driving pain amplification (bidirectional); non-restorative sleep; fatigue cycle; CES primary modality"],
        ["CRPS Features", "Complex Regional Pain Syndrome features; autonomic changes (oedema, colour, temperature); specialist evaluation required"],
        ["Post-Surgical / Post-Procedural", "Persistent post-surgical pain; sensitisation post-operatively; tDCS DLPFC + M1; taVNS + CES"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["M1 (C3/C4)", "Pain Threshold / Motor", "Active or passive movement of painful body region; graded motor imagery; mirror therapy"],
        ["L-DLPFC (F3)", "Catastrophising / Cognition", "Pain neuroscience education; cognitive restructuring; acceptance-based pain coping; PCS review"],
        ["ACC (TPS)", "Affective Pain / Suffering", "Mindfulness of pain; compassion-focused pain acceptance; positive emotion induction"],
        ["taVNS", "Descending Inhibition / Autonomic", "Paced breathing concurrent with taVNS; HRV biofeedback; relaxation response activation"],
        ["CES (Alpha-Stim)", "Sleep / Central Sensitisation", "Sleep hygiene for pain; relaxation; pain management education; activity pacing instruction"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["NRS Pain Score (Primary)", "\u226530% reduction from baseline = clinical response; \u226550% = excellent response"],
        ["BPI Interference", "MCID \u22652-point improvement in BPI interference subscale"],
        ["PCS (Catastrophising)", "\u226530% reduction or \u22656.5-point reduction in PCS total"],
        ["PSQI (Sleep)", "PSQI \u22645 or \u22653-point improvement in global score"],
        ["PGIC (Global)", "PGIC \u22655 (much improved or better) = responder"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "Chronic pain \u22653 months duration meeting IASP criteria (G89.29)"],
        ["2", "NRS pain score \u22654/10 at baseline on \u22653 consecutive days"],
        ["3", "Age 18\u201375; capable of informed consent"],
        ["4", "Inadequate response to \u22652 pharmacological treatments (anticonvulsants, SNRIs, opioids)"],
        ["5", "Stable analgesic regimen for \u22654 weeks prior to enrolment"],
        ["6", "No active malignancy or cancer-related pain (separate pathway)"],
        ["7", "Willing to engage with concurrent pain psychology / physiotherapy"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Active malignancy or cancer-related pain"],
        ["2", "Metallic implants in head/neck stimulation field"],
        ["3", "Cardiac pacemaker or ICD (CES / taVNS contraindication)"],
        ["4", "Pregnancy"],
        ["5", "Implanted spinal cord stimulator or neurostimulator"],
        ["6", "Active substance dependence (opioid/alcohol)"],
        ["7", "Severe psychiatric comorbidity (active psychosis, suicide attempt <6 months)"],
        ["8", "Fibromyalgia as sole diagnosis without central sensitisation evidence confirmed"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Opioid dependence", "Opioid-induced hyperalgesia possible; consider structured opioid taper concurrent"],
        ["CRPS features", "Specialist pain physician review; sympathetically maintained pain considerations"],
        ["Psychiatric comorbidity (MDD/anxiety)", "Combined protocol; treat depression/anxiety concurrently; DLPFC addition"],
        ["Fibromyalgia diagnosis", "Central sensitisation protocol; CES primary; tDCS DLPFC + M1; sleep optimisation"],
        ["Cervical / thoracic radiculopathy", "Peripheral pain source confirmed; adjunctive NIBS only; pain specialist concurrent"],
        ["Chronic opioid use", "Document dose carefully; opioid equivalence; taper planning"],
        ["Cardiovascular disease", "CES + taVNS: cardiac clearance; ECG recommended"],
        ["Elderly (\u226570)", "Reduce intensities; fall risk; cognitive screening before tDCS DLPFC"],
        ["Pregnancy planning", "CES safety in pregnancy: limited data; taVNS: data insufficient; halt if pregnant"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Neuropathic Dominant", "Anodal M1 contralateral (C3/C4) 2\u202fmA 20\u202fmin", "ACC + S1: 300 pulses, 0.25\u202fHz", "taVNS 30min; CES nightly 60min"],
        ["Central Sensitisation", "Anodal DLPFC (F3) 2\u202fmA 20\u202fmin", "ACC + S1: 400 pulses", "CES primary (anti-sensitisation); taVNS 30min"],
        ["Affective-Pain", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "ACC: 300 pulses", "taVNS 30min; CES nightly; CBT pain concurrent"],
        ["Musculoskeletal-Central", "Anodal M1 (C3) + DLPFC sequential", "S1/M1: 300 pulses", "CES 3\u00d7/week; physiotherapy concurrent"],
        ["Catastrophising Dominant", "Anodal DLPFC (F3) 2\u202fmA 20\u202fmin", "ACC: 300 pulses", "taVNS + CES; pain psychology essential"],
        ["Sleep-Pain Comorbid", "Anodal M1 (1.5\u202fmA, 20\u202fmin)", "None initial", "CES primary nightly 60min; taVNS 30min"],
        ["CRPS Features", "Anodal M1 contralateral 2\u202fmA; mirror cortex", "M1 + S1: 250 pulses", "taVNS 30min; CES + specialist referral"],
        ["Maintenance", "Anodal M1/DLPFC 1.5\u202fmA 20\u202fmin 2\u00d7/week", "None", "CES 3\u00d7/week; taVNS daily home"],
    ],
)

# ─── PTSD ─────────────────────────────────────────────────────────────────────
CDATA["ptsd"] = dict(
    slug="ptsd", cover_title="POST-TRAUMATIC STRESS DISORDER (PTSD)",
    name="Post-Traumatic Stress Disorder (PTSD)", short="PTSD", abbr="PTSD",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in PTSD is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not currently extend to PTSD. Mandatory off-label disclosure and Doctor "
        "sign-off are required before TPS treatment for PTSD."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for PTSD requires specific, documented off-label disclosure with Doctor sign-off. "
        "NIBS is used as augmentation to trauma-focused psychotherapy, not as monotherapy."
    ),
    prs_domain_label="PTSD Symptom Clusters",
    prs_domain_header_line="PTSD Symptom Clusters \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
    exam_step_heading="4.1 PTSD Clinical & Psychiatric Examination",
    exam_step_desc=(
        "Conduct a systematic PTSD psychiatric examination using the Clinical Examination Checklist. "
        "Rate symptom clusters (re-experiencing, avoidance, cognitions/mood, hyperarousal) per DSM-5:"
    ),
    exam_checklist_item="\u2610 PTSD clinical examination completed (all 4 DSM-5 clusters rated; suicidality assessed)",
    med_check_item="Record PTSD medication compliance (last SSRI/prazosin/other dose; any PRN taken today)",
    session_med_doc="medication compliance (SSRI/SNRI dose, prazosin, PRN medications; timing)",
    false_class_body=(
        "Standardise PTSD assessment conditions between baseline and follow-up. CAPS-5 and PCL-5 "
        "scores can fluctuate significantly with recent trauma cue exposure or life stressors. "
        "Ensure assessments occur in a consistent, safe clinical environment to avoid false "
        "responder or false non-responder classification."
    ),
    modality_table=[
        ["Modality", "Device", "Classification", "PTSD Evidence Status"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Level B evidence (DLPFC; Boggio 2010; Fregni 2006)"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL \u2014 OFF-LABEL for PTSD"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Level A evidence (VNS PTSD; FDA Breakthrough Therapy)"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Level A evidence (PTSD sleep/anxiety; Lande 2018)"],
    ],
    offlabel_table=[
        ["Modality", "Regulatory Status", "PTSD Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Level B evidence; DLPFC fear extinction protocol", "Standard informed consent"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Level A; FDA Breakthrough Therapy for PTSD; VNS-paired therapy", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety/depression/insomnia)", "Level A; PTSD hyperarousal and sleep; FDA-cleared anxiety", "Standard informed consent"],
    ],
    prs_table=[
        ["Re-experiencing & Avoidance (0\u201310)", "Hyperarousal & Cognitions (0\u201310)"],
        ["Intrusive memories / flashbacks", "Hypervigilance (threat scanning)"],
        ["Nightmares / trauma-related dreams", "Exaggerated startle response"],
        ["Distress at trauma cue exposure", "Sleep disturbance (onset/maintenance)"],
        ["Avoidance of trauma reminders (external)", "Irritability / angry outbursts"],
        ["Avoidance of trauma thoughts/feelings", "Difficulty concentrating"],
        ["Emotional numbing / detachment", "Negative beliefs about self/world"],
        ["Dissociative episodes", "Guilt / shame / self-blame"],
        ["Trauma-related functional impairment", "Overall distress / quality of life"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["Re-experiencing Cluster", "CAPS-5 Criterion B items (5 symptoms); flashback assessment", "0\u20134 per item; cluster total"],
        ["Avoidance Cluster", "CAPS-5 Criterion C items (2 symptoms); behavioural avoidance mapping", "0\u20134 per item; cluster total"],
        ["Cognitions & Mood Cluster", "CAPS-5 Criterion D items (7 symptoms); guilt/shame assessment", "0\u20134 per item; cluster total"],
        ["Hyperarousal Cluster", "CAPS-5 Criterion E items (6 symptoms); startle assessment", "0\u20134 per item; cluster total"],
        ["Dissociation Screen", "MDD-3/DES-II screen; dissociative subtype identification", "DES-II >20 = significant dissociation"],
        ["Suicidality Assessment", "C-SSRS; safety plan review; protective factors", "Score + action plan required"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["CAPS-5 (Clinician-Administered PTSD Scale)", "___ / 80", "\u226533 = PTSD diagnosis; 23\u201332 = subthreshold; <11 = remission"],
        ["PCL-5 (PTSD Checklist for DSM-5)", "___ / 80", "\u226533 = PTSD screening positive; \u226410 = remission (primary)"],
        ["PHQ-9 (Depression comorbidity)", "___ / 27", "\u226510 = comorbid depression (common in PTSD)"],
        ["GAD-7 (Anxiety comorbidity)", "___ / 21", "\u226510 = comorbid anxiety"],
        ["PSQI (Sleep quality)", "___ / 21", ">5 = PTSD-related sleep disruption"],
        ["IES-R (Impact of Event Scale)", "___ / 88", ">24 = PTSD-level impact; >32 = severe"],
        ["DES-II (Dissociative Experiences)", "___ / 100", ">20 = clinically significant dissociation"],
        ["C-SSRS (Suicidality)", "See scale", "\u22653 = active ideation requiring safety plan"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Hyperarousal Dominant", "Hypervigilance, exaggerated startle, insomnia, irritability dominant; LC/noradrenergic overdrive; CES + taVNS primary"],
        ["Re-experiencing Dominant", "Intrusions, flashbacks, nightmares primary; amygdala-vmPFC dysfunction; TPS vmPFC + tDCS DLPFC; PE/EMDR concurrent"],
        ["Avoidance / Emotional Numbing", "Emotional constriction, social withdrawal; blunted amygdala-DLPFC; tDCS DLPFC + taVNS; behavioural activation"],
        ["Cognitive / Negative Cognition", "Guilt, shame, hopelessness dominant; DLPFC-DMN dysfunction; tDCS DLPFC + TPS ACC; CPT concurrent"],
        ["Complex PTSD (C-PTSD)", "Prolonged/repeated trauma; affect dysregulation, identity disturbance; all 4 modalities; intensive trauma therapy"],
        ["Dissociative Subtype", "Depersonalisation/derealisation; prefrontal over-suppression; specialised protocol: cathodal DLPFC + TPS insula"],
        ["PTSD + TBI Comorbidity", "Dual diagnosis; TBI protocol elements + PTSD; taVNS primary; cognitive rehabilitation concurrent"],
        ["Veteran / Military PTSD", "Combat trauma; moral injury; high C-PTSD features; integrated veteran-specific pathway"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["L-DLPFC (F3)", "Fear Extinction / Cognitive Control", "Cognitive Processing Therapy (CPT) worksheets; thought challenging; safety cue learning tasks"],
        ["vmPFC (TPS)", "Extinction Memory / Safety Encoding", "Safety signal conditioning exercises; exposure hierarchy review; extinction recall practice"],
        ["taVNS", "Hyperarousal / LC Downregulation", "Paced breathing (slow exhalation); HRV biofeedback; polyvagal grounding exercises"],
        ["CES (Alpha-Stim)", "Sleep / Nightmares / Hyperarousal", "Sleep hygiene; imagery rehearsal therapy for nightmares; progressive muscle relaxation"],
        ["ACC (TPS)", "Conflict Monitoring / Affect Regulation", "Emotion regulation exercises; mindfulness of emotions; DBT distress tolerance skills"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["PCL-5 (Primary)", "\u226510-point reduction = clinically meaningful; score <33 = no PTSD; <11 = remission"],
        ["CAPS-5", "\u226515-point reduction = response; score <11 = remission"],
        ["PHQ-9 (Depression)", "\u226550% reduction = response; score \u22644 = remission"],
        ["PSQI (Sleep / Nightmares)", "PSQI \u22645 or \u22653-point improvement; nightmare frequency reduction"],
        ["IES-R (Impact of Event)", "\u226530% reduction in total IES-R score"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "DSM-5 PTSD diagnosis confirmed by structured interview (CAPS-5 \u226533)"],
        ["2", "PCL-5 \u226533 at baseline; trauma exposure \u22653 months prior"],
        ["3", "Age 18\u201370; capable of informed consent"],
        ["4", "Inadequate response to \u22651 evidence-based psychotherapy (PE, CPT, EMDR) or SSRI"],
        ["5", "Stable medication regimen for \u22654 weeks"],
        ["6", "Able to engage with concurrent trauma-focused psychotherapy"],
        ["7", "Safety plan in place if suicidal ideation present (C-SSRS <4)"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Active suicidality with intent/plan (C-SSRS \u22654); recent attempt <3 months"],
        ["2", "Metallic implants in head/neck stimulation field"],
        ["3", "Cardiac pacemaker or ICD (CES / taVNS contraindication)"],
        ["4", "Pregnancy"],
        ["5", "Active psychosis or dissociative identity disorder (frequent switching)"],
        ["6", "Active substance dependence (alcohol, stimulants)"],
        ["7", "Inability to tolerate trauma-focused content (extreme dissociation; DES-II >50)"],
        ["8", "Severe TBI as primary diagnosis (refer to TBI protocol)"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Dissociative subtype (DES-II >20)", "Specialised protocol; cathodal DLPFC; TPS insula; no trauma processing until stabilised"],
        ["Active substance use", "Detox support concurrent; NIBS after 4-week abstinence; document carefully"],
        ["Chronic pain comorbidity", "Combined PTSD-pain protocol; taVNS + tDCS M1 + DLPFC"],
        ["Depression comorbidity (PHQ-9 >14)", "Prioritise antidepressant effect; bifrontal tDCS; taVNS + CES"],
        ["Military/veteran trauma", "Moral injury considerations; peer support integration; veteran-specific resources"],
        ["Borderline Personality comorbidity", "DBT backbone; careful trauma processing pacing; dissociation monitoring"],
        ["Refugee/asylum seeker", "Interpreter available; cultural formulation; legal stress assessment"],
        ["Cardiac history", "CES/taVNS: ECG and cardiac clearance; ANS monitoring"],
        ["Childhood sexual abuse (CSA) history", "Complex PTSD pathway; long-term therapy concurrent; trauma-informed care"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Hyperarousal Dominant", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "None initial", "taVNS primary 30min 2\u00d7/day; CES nightly 60min"],
        ["Re-experiencing Dominant", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "vmPFC: 300 pulses, 0.25\u202fHz", "taVNS before session; PE/EMDR concurrent"],
        ["Avoidance / Numbing", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "ACC: 250 pulses", "taVNS 30min; behavioural activation concurrent"],
        ["Cognitive / Negative", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "ACC + vmPFC: 300 pulses", "taVNS 30min; CPT concurrent"],
        ["Complex PTSD", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "ACC + vmPFC: 400 pulses", "taVNS + CES nightly; intensive trauma therapy"],
        ["Dissociative Subtype", "Cathodal L-DLPFC (F3) 1.5\u202fmA (calming)", "Insula: 200 pulses (low)", "taVNS only; specialised trauma programme"],
        ["PTSD + TBI", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "vmPFC: 250 pulses", "taVNS 30min; CES nightly; TBI rehab concurrent"],
        ["Veteran PTSD", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "vmPFC + ACC: 350 pulses", "taVNS 30min; CES nightly; peer support integration"],
    ],
)
