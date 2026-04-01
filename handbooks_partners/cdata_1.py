"""Partners Tier condition data — Set 1: Depression, Anxiety, ADHD, Alzheimer's, Stroke Rehab"""

CDATA = {
    "depression": {
        "slug": "depression",
        "cover_title": "MAJOR DEPRESSIVE DISORDER",
        "name": "Major Depressive Disorder (MDD)",
        "short": "Depression",
        "abbr": "MDD",
        "med_name": "antidepressants",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Major Depressive Disorder (MDD). For use by the treating Doctor and "
            "authorised SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Major Depressive Disorder is "
            "INVESTIGATIONAL at SOZO Brain Center. It is not CE-marked or FDA-approved for MDD. All patients "
            "must provide written informed consent inclusive of the off-label TPS disclosure. TPS use is "
            "restricted to the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in MDD treatment. Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient-rated):",
        "prs_primary_items": [
            "Depressed mood (persistent low mood, sadness)",
            "Anhedonia (loss of interest or pleasure)",
            "Guilt / worthlessness",
            "Fatigue / energy loss",
            "Psychomotor change (slowing or agitation)",
            "Concentration / decision-making difficulty",
            "Appetite / weight change",
            "Suicidal ideation (passive; assess actively if present)",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Sleep disturbance (insomnia or hypersomnia)",
            "Anxiety / worry",
            "Irritability",
            "Social withdrawal",
            "Libido / relationship function",
            "Pain (somatic complaints)",
            "Self-esteem / confidence",
            "Motivation / drive",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Melancholic, Atypical, Anxious, Treatment-Resistant, "
            "Psychomotor-Retarded, Cognitive, Insomnia-Dominant, Anhedonic, or Somatic."
        ),

        "pre_session_med_check": "☐ Record antidepressant medication (name, dose, timing of last dose, adherence, and duration of current prescription)",
        "session_med_doc": "Medication state (antidepressant adherence, timing of last dose, any recent medication changes)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: Standardise assessment conditions between baseline and "
            "follow-up. Ensure consistent evaluation timing relative to antidepressant medication cycles and "
            "circadian mood patterns. Changes in concurrent psychotherapy, significant life events, or "
            "medication adjustments must be documented and considered when interpreting SOZO PRS score changes."
        ),

        "inclusion_items": [
            "Confirmed diagnosis of Major Depressive Disorder (ICD-10 F32/F33 or DSM-5 criteria)",
            "Moderate to severe depressive episode or treatment-resistant course (PHQ-9 ≥10 or equivalent)",
            "Age 18+ years",
            "Able to attend sessions or comply with home-use protocol",
            "Written informed consent (including TPS off-label disclosure)",
            "Baseline SOZO PRS and depression outcome measures (PHQ-9 or equivalent) completed",
        ],
        "exclusion_items": [
            "Intracranial metallic hardware in stimulation path",
            "Cochlear implant",
            "Skull defects, craniectomy, or recent craniotomy",
            "Active intracranial tumour",
            "Open wounds at electrode sites",
            "Pregnancy (tDCS, TPS)",
            "Inability to provide informed consent",
        ],
        "conditional_items": [
            "Cardiac pacemaker or defibrillator",
            "Epilepsy or seizure history",
            "Active suicidal ideation with plan or intent (requires psychiatric risk assessment first)",
            "Bipolar disorder (requires mood stabiliser optimisation prior to NIBS)",
            "Active psychosis",
            "Coagulation disorders or anticoagulants (especially TPS)",
            "Dermatological conditions at electrode sites",
            "Unstable medical condition or severe systemic illness",
        ],

        "modality_table": [
            ["Modality", "Device", "Classification", "MDD Status"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Level B evidence — established NIBS for MDD"],
            ["TPS", "NEUROLITH® (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL (Off-Label)"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked", "Emerging adjunctive — vagal-mood pathway"],
            ["CES", "Alpha-Stim®", "FDA-cleared", "Cleared (FDA 510k) — depression / anxiety / insomnia indication"],
        ],
        "offlabel_table": [
            ["Modality", "Regulatory Status", "MDD Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Established NIBS; Level B evidence for MDD (L-DLPFC montage)", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Emerging adjunctive — vagal-limbic regulation for mood", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "FDA 510k cleared for depression, anxiety, and insomnia", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Melancholic", "LIMBIC hyperactivation + CEN hypofunction; pervasive anhedonia, psychomotor retardation, diurnal variation"],
            ["Atypical", "Reactive mood; LIMBIC hyperresponsivity to positive stimuli; SN over-sensitivity; rejection hypersensitivity"],
            ["Anxious", "SN hyperactivation (fear/threat amplification) + LIMBIC-SN overcoupling; prominent anxiety and tension"],
            ["Treatment-Resistant", "Multi-network dysfunction; CEN-LIMBIC-SN triad impairment; poor anterior cingulate modulation"],
            ["Psychomotor-Retarded", "SMN hypofunction (motor initiation deficit) + CEN hypoactivation; pronounced slowing"],
            ["Cognitive", "CEN fragmentation (working memory, executive function) + DMN intrusion; cognitive depression subtype"],
            ["Insomnia-Dominant", "SN hyperarousal + LIMBIC-SN sleep disruption loop; insomnia as primary driver of mood cycle"],
            ["Anhedonic", "LIMBIC reward hypofunction (nucleus accumbens-PFC disconnect) + CEN hypoactivation; flat affect"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["F3 anode / F4 cathode (L-DLPFC up)", "Mood / cognitive activation", "Cognitive activation tasks (verbal fluency, n-back), structured behavioural activation planning"],
            ["F3/F4 bilateral DLPFC", "Executive / motivation", "Motivational interviewing exercises, goal-setting, reward scheduling worksheets"],
            ["Pz cathode / F3 anode", "DMN downregulation + DLPFC up", "Mindfulness-based attention, present-moment awareness tasks, gratitude journalling"],
            ["F3 anode / Fp2 cathode", "Anhedonia / reward", "Pleasant activity scheduling, reward tracking, positive imagery exercises"],
            ["taVNS + CES combined", "Limbic stabilisation", "Relaxation response training, slow breathing (5 breaths/min), guided progressive relaxation"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Mood / Affect", "Clinically meaningful improvement in PHQ-9 or equivalent (≥50% reduction) + PRS primary domain improvement"],
            ["Anhedonia / Motivation", "Return of interest/pleasure in activities (PRS anhedonia + motivation items); patient-reported functional gain"],
            ["Cognition", "Improvement in concentration, decision-making, and executive function (PRS + MoCA or equivalent)"],
            ["Function / Sleep", "Better daily living, social participation, sleep quality, and occupational engagement (PRS secondary domains)"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Melancholic", "tDCS F3 anode / F4 cathode (L-DLPFC up) + TPS frontal + taVNS primary + CES daily"],
            ["Atypical", "tDCS F3/F4 bilateral + TPS frontal + taVNS + CES (mood reactivity stabilisation)"],
            ["Anxious", "tDCS F3 anode / F4 cathode + TPS frontal + taVNS primary (vagal calming) + CES daily"],
            ["Treatment-Resistant", "tDCS F3/F4 bilateral + Pz cathode (DMN downregulation) + TPS frontal aggressive + taVNS + CES"],
            ["Psychomotor-Retarded", "tDCS F3/C3 anode (motor-DLPFC combined) + TPS frontal + peripheral upper limb + taVNS + CES"],
            ["Cognitive", "tDCS F3/F4 bilateral DLPFC + TPS frontal + taVNS supportive; pair with cognitive rehabilitation tasks"],
            ["Insomnia-Dominant", "CES primary (pre-sleep) + taVNS (evening) + tDCS Fpz/F3 cathode + TPS frontal"],
            ["Anhedonic", "tDCS F3 anode / Fp2 cathode (reward circuit) + TPS frontal + taVNS + CES; pair with behavioural activation"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },

    "anxiety": {
        "slug": "anxiety",
        "cover_title": "GENERALIZED ANXIETY DISORDER",
        "name": "Generalized Anxiety Disorder (GAD)",
        "short": "Anxiety",
        "abbr": "GAD",
        "med_name": "anxiolytics / SSRIs",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Generalized Anxiety Disorder (GAD). For use by the treating Doctor and "
            "authorised SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Generalized Anxiety Disorder is "
            "INVESTIGATIONAL at SOZO Brain Center. It is not CE-marked or FDA-approved for GAD. All patients "
            "must provide written informed consent inclusive of the off-label TPS disclosure. TPS use is "
            "restricted to the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in GAD treatment. Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient-rated):",
        "prs_primary_items": [
            "Worry frequency (how often uncontrollable worry occurs)",
            "Worry controllability (ability to stop or redirect worry)",
            "Restlessness / feeling on edge",
            "Muscle tension (physical tension or somatic tension)",
            "Irritability",
            "Concentration difficulty",
            "Fatigue (anxiety-driven exhaustion)",
            "Panic / acute anxiety episodes",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Sleep onset / maintenance problems",
            "Depression / low mood",
            "Avoidance behaviours",
            "Social anxiety",
            "GI or cardiac somatic symptoms",
            "Catastrophising / worst-case thinking",
            "Decision-making impairment",
            "Hypervigilance / scanning for threats",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Cognitive-Worry, Somatic-Tension, Mixed, Panic-Prone, Social, "
            "Insomnia-Linked, Health Anxiety, Phobic, or Autonomic."
        ),

        "pre_session_med_check": "☐ Record anxiolytic / SSRI medication (name, dose, timing of last dose, adherence, current anxiety baseline rating)",
        "session_med_doc": "Medication state (anxiolytic or SSRI adherence, timing of last dose, current session anxiety rating)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: Anxiety symptoms fluctuate significantly with acute "
            "stressors. Standardise assessment conditions between baseline and follow-up — avoid assessment "
            "immediately following identified stressor events. Document concurrent psychotherapy, lifestyle "
            "changes, and significant life events when interpreting SOZO PRS changes."
        ),

        "inclusion_items": [
            "Confirmed diagnosis of Generalized Anxiety Disorder (ICD-10 F41.1 or DSM-5 criteria)",
            "Moderate to severe anxiety (GAD-7 ≥10 or equivalent; functionally impairing)",
            "Age 18+ years",
            "Able to attend sessions or comply with home-use protocol",
            "Written informed consent (including TPS off-label disclosure)",
            "Baseline SOZO PRS and anxiety outcome measures (GAD-7 or equivalent) completed",
        ],
        "exclusion_items": [
            "Intracranial metallic hardware in stimulation path",
            "Cochlear implant",
            "Skull defects, craniectomy, or recent craniotomy",
            "Active intracranial tumour",
            "Open wounds at electrode sites",
            "Pregnancy (tDCS, TPS)",
            "Inability to provide informed consent",
        ],
        "conditional_items": [
            "Cardiac pacemaker or defibrillator",
            "Epilepsy or seizure history",
            "Severe panic disorder with agoraphobia limiting clinic attendance",
            "Active psychosis",
            "Bipolar disorder (requires mood stabiliser optimisation first)",
            "Coagulation disorders or anticoagulants (especially TPS)",
            "Dermatological conditions at electrode sites",
            "Severe medical comorbidity driving anxiety (requires primary medical management first)",
        ],

        "modality_table": [
            ["Modality", "Device", "Classification", "GAD Status"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Investigational (Off-Label) — prefrontal anxiety modulation"],
            ["TPS", "NEUROLITH® (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL (Off-Label)"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked", "Primary adjunctive — vagal parasympathetic regulation"],
            ["CES", "Alpha-Stim®", "FDA-cleared", "Cleared (FDA 510k) — anxiety indication (primary modality)"],
        ],
        "offlabel_table": [
            ["Modality", "Regulatory Status", "GAD Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Investigational — prefrontal regulation of anxiety and worry circuits", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Primary adjunctive — parasympathetic vagal regulation for anxiety reduction", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "FDA 510k cleared for anxiety — first-line SOZO modality for GAD", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Cognitive-Worry", "DMN hyperactivation (rumination loop) + CEN hypofunction (poor worry termination), anterior cingulate dysregulation"],
            ["Somatic-Tension", "SN hyperactivation (interoceptive amplification) + SMN tension coupling; prominent body-focused anxiety"],
            ["Mixed", "DMN + SN co-hyperactivation; combined cognitive worry and somatic tension profile"],
            ["Panic-Prone", "SN hyperactivation (acute threat amplification) + LIMBIC fear circuit hypersensitivity; episodic surge pattern"],
            ["Social", "SN social threat detection over-sensitivity + LIMBIC shame/fear coupling; avoidance network activation"],
            ["Insomnia-Linked", "SN nocturnal hyperarousal + LIMBIC night-time amplification; anxiety driving sleep disruption cycle"],
            ["Health Anxiety", "SN interoceptive hyperactivation + DMN catastrophising + CEN poor threat appraisal regulation"],
            ["Autonomic", "SN-autonomic network dysregulation; prominent cardiovascular/GI symptoms; vagal tone reduction"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["F3 anode / F4 cathode (L-DLPFC up)", "Worry / cognitive control", "Cognitive defusion exercises, worry postponement protocol, structured problem-solving"],
            ["Right DLPFC inhibition (F4 cathode / F3 anode)", "Threat bias", "Attention bias modification (ABM) training, threat reappraisal exercises"],
            ["Fpz cathode / Fz (frontal inhibition)", "Hyperarousal reduction", "4-7-8 breathing, diaphragmatic breathing training, heart rate variability biofeedback"],
            ["taVNS primary (cymba conchae)", "Vagal activation", "Slow breathing protocol (5 breaths/min), progressive muscle relaxation, guided body scan"],
            ["CES + taVNS combined", "Arousal and somatic tension", "Body scan, somatic relaxation tasks, anxiety psychoeducation review"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Worry / Cognitive", "Clinically meaningful reduction in GAD-7 or equivalent (≥50%) + PRS worry items improvement"],
            ["Somatic / Autonomic", "Reduction in somatic anxiety symptoms (PRS) and improved heart rate variability or relaxation capacity"],
            ["Sleep", "Improvement in sleep onset latency and quality (PRS secondary items + sleep diary)"],
            ["Function / Avoidance", "Better social and occupational participation, reduced avoidance behaviours (PRS + patient report)"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Cognitive-Worry", "tDCS F3 anode / F4 cathode (L-DLPFC up) + TPS frontal + taVNS + CES daily"],
            ["Somatic-Tension", "CES primary + taVNS primary + tDCS Fpz/F3 cathode (frontal inhibition) + TPS frontal"],
            ["Mixed", "tDCS F3/F4 bilateral + TPS frontal + taVNS primary + CES daily"],
            ["Panic-Prone", "CES primary + taVNS primary (high priority) + tDCS F3 anode / F4 cathode + TPS frontal"],
            ["Social", "tDCS F3 anode / right TP cathode + TPS frontal + taVNS + CES; pair with social exposure tasks"],
            ["Insomnia-Linked", "CES (pre-sleep primary) + taVNS (evening) + tDCS Fpz cathode + TPS frontal"],
            ["Health Anxiety", "tDCS F3/F4 bilateral + TPS frontal + taVNS primary + CES; pair with interoceptive exposure exercises"],
            ["Autonomic", "taVNS primary (daily, high dose) + CES primary + tDCS Fpz/F3 cathode + TPS frontal supportive"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },

    "adhd": {
        "slug": "adhd",
        "cover_title": "ATTENTION DEFICIT HYPERACTIVITY DISORDER",
        "name": "Attention Deficit Hyperactivity Disorder (ADHD)",
        "short": "ADHD",
        "abbr": "ADHD",
        "med_name": "stimulant medication",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Attention Deficit Hyperactivity Disorder (ADHD). For use by the treating "
            "Doctor and authorised SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Attention Deficit Hyperactivity Disorder "
            "is INVESTIGATIONAL at SOZO Brain Center. It is not CE-marked or FDA-approved for ADHD. All "
            "patients must provide written informed consent inclusive of the off-label TPS disclosure. TPS "
            "use is restricted to the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in ADHD treatment. Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient-rated):",
        "prs_primary_items": [
            "Inattention (difficulty sustaining focus on tasks)",
            "Distractibility (ease of distraction by external stimuli)",
            "Task completion (difficulty finishing started tasks)",
            "Organisation (ability to manage tasks, materials, time)",
            "Forgetfulness (forgetting daily tasks and appointments)",
            "Hyperactivity (physical restlessness or motor overactivity)",
            "Impulsivity (acting without thinking, interrupting)",
            "Time management (chronic lateness, poor time sense)",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Emotional dysregulation (anger, frustration bursts)",
            "Frustration tolerance",
            "Sleep onset / maintenance problems",
            "Self-esteem and confidence",
            "Interpersonal relationships",
            "Motivation and initiation",
            "Procrastination",
            "Restlessness / internal hyperactivity",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Inattentive, Hyperactive-Impulsive, Combined, Executive-Dominant, "
            "Emotional Dysregulation, Sluggish Cognitive Tempo (SCT), Working Memory, Reward-Deficit, "
            "or Comorbid Anxiety."
        ),

        "pre_session_med_check": "☐ Record stimulant medication (name, dose, timing of last dose, whether today is a medication day or drug holiday)",
        "session_med_doc": "Medication state (stimulant medication adherence, timing of last dose, on-medication or drug holiday status)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: ADHD symptom expression varies significantly between "
            "on-medication and off-medication states. Standardise assessment conditions between baseline and "
            "follow-up — always assess in the same medication state (on or off). Document concurrent "
            "psychotherapy, coaching, or school/workplace accommodations when interpreting SOZO PRS changes."
        ),

        "inclusion_items": [
            "Confirmed diagnosis of ADHD (DSM-5 or ICD-11 criteria; clinical or formal neuropsychological assessment)",
            "Moderate to severe symptom impairment in at least two settings (work, school, home)",
            "Age 16+ years",
            "Able to attend sessions or comply with home-use protocol",
            "Written informed consent (including TPS off-label disclosure)",
            "Baseline SOZO PRS and ADHD outcome measures (ASRS or equivalent) completed",
        ],
        "exclusion_items": [
            "Intracranial metallic hardware in stimulation path",
            "Cochlear implant",
            "Skull defects, craniectomy, or recent craniotomy",
            "Active intracranial tumour",
            "Open wounds at electrode sites",
            "Pregnancy (tDCS, TPS)",
            "Inability to provide informed consent",
        ],
        "conditional_items": [
            "Cardiac pacemaker or defibrillator",
            "Epilepsy or seizure history",
            "Unstable comorbid bipolar disorder or psychosis",
            "Active substance abuse (stimulant misuse requiring specialist management first)",
            "Severe tic disorder (Tourette's) requiring specialist review",
            "Coagulation disorders or anticoagulants (especially TPS)",
            "Dermatological conditions at electrode sites",
            "Uncontrolled hypertension (stimulant medication interaction — Doctor review required)",
        ],

        "modality_table": [
            ["Modality", "Device", "Classification", "ADHD Status"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Investigational (Off-Label) — DLPFC/attention network modulation"],
            ["TPS", "NEUROLITH® (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL (Off-Label)"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked", "Emerging adjunctive — attention and arousal regulation"],
            ["CES", "Alpha-Stim®", "FDA-cleared", "Investigational (Off-Label) — emotional dysregulation / sleep component"],
        ],
        "offlabel_table": [
            ["Modality", "Regulatory Status", "ADHD Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Investigational — bilateral DLPFC and attention network upregulation for ADHD", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Emerging adjunctive — attention and arousal regulation via vagal pathway", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "Off-label supportive — emotional dysregulation and sleep component in ADHD", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Inattentive", "ATTENTION hypofunction (DAN hypoactivation) + CEN working memory deficit + DMN intrusion during tasks"],
            ["Hyperactive-Impulsive", "SN dysregulation (impulsivity) + CEN inhibitory control failure + prefrontal hypoactivation"],
            ["Combined", "Dual ATTENTION/CEN hypofunction + SN dysregulation; full clinical profile across all domains"],
            ["Executive-Dominant", "CEN fragmentation (planning, organisation, cognitive flexibility) + ATTENTION hypofunction"],
            ["Emotional Dysregulation", "LIMBIC hyperactivation + CEN-LIMBIC inhibitory failure; prominent frustration and anger outbursts"],
            ["Sluggish Cognitive Tempo", "Global network low arousal; slow processing speed, daydreaming; ATTENTION-CEN combined hypoactivation"],
            ["Working Memory", "CEN-specific deficit (dorsolateral PFC hypoactivation); prominent forgetfulness and task-tracking impairment"],
            ["Reward-Deficit", "LIMBIC reward circuit hyposensitivity (DA pathway); motivation failure, procrastination, novelty-seeking"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["F3/F4 bilateral DLPFC", "Executive function / working memory", "Computerised working memory training (n-back, dual-task), verbal fluency, task-switching"],
            ["F3 anode / Cz", "Attention and focus", "Sustained attention tasks (CPT), auditory vigilance, target detection tasks"],
            ["Right DLPFC (F4 anode / F3 cathode)", "Impulsivity / inhibition", "Go/no-go paradigm, stop-signal task, response inhibition drills"],
            ["Cz / FCz (attention midline)", "Hyperactivity / arousal", "Mindfulness-based attention regulation, slow pacing tasks, structured movement breaks"],
            ["taVNS + tDCS combined", "Emotional regulation", "Frustration tolerance exercises, emotion identification, CBT-based impulse management"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Attention / Focus", "Clinically meaningful improvement in ASRS or equivalent + PRS inattention items; improved task completion"],
            ["Executive Function", "Improvement in organisation, planning, and working memory (PRS + BRIEF or equivalent)"],
            ["Hyperactivity / Impulsivity", "Reduction in hyperactivity and impulsivity ratings (PRS) and clinician / teacher global impression"],
            ["Emotional / Function", "Better emotional regulation, self-esteem, and occupational or academic functioning (PRS secondary)"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Inattentive", "tDCS F3/F4 bilateral DLPFC (2 mA, 20 min) + Cz attention montage + TPS frontal + taVNS supportive"],
            ["Hyperactive-Impulsive", "tDCS F4 anode / F3 cathode (R-DLPFC inhibition) + TPS frontal SMA + taVNS + CES (arousal control)"],
            ["Combined", "tDCS F3/F4 bilateral + TPS frontal + taVNS + CES; alternate attention and inhibition montages weekly"],
            ["Executive-Dominant", "tDCS F3/F4 bilateral DLPFC + TPS frontal targeted + taVNS supportive; pair with executive training"],
            ["Emotional Dysregulation", "tDCS F3 anode / F4 cathode + TPS frontal + taVNS primary + CES daily"],
            ["Sluggish Cognitive Tempo", "tDCS F3/F4 bilateral + Cz (arousal up) + TPS frontal + taVNS; pair with high-engagement cognitive tasks"],
            ["Working Memory", "tDCS F3/F4 bilateral DLPFC high-focus + TPS frontal targeted + taVNS; pair with n-back training"],
            ["Reward-Deficit", "tDCS F3 anode / Fp2 cathode (reward circuit) + TPS frontal + taVNS; pair with motivational behavioural activation"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },

    "alzheimers": {
        "slug": "alzheimers",
        "cover_title": "ALZHEIMER'S DISEASE / MILD COGNITIVE IMPAIRMENT",
        "name": "Alzheimer's Disease / MCI (AD/MCI)",
        "short": "Alzheimer's",
        "abbr": "AD",
        "med_name": "cholinesterase inhibitors / memantine",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Alzheimer's Disease / MCI (AD/MCI). For use by the treating Doctor and "
            "authorised SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "NOTE: TPS (NEUROLITH®) is CE-marked for Alzheimer's disease — this is an approved on-label "
            "indication at SOZO Brain Center. Standard informed consent for TPS is required. For MCI (pre-AD) "
            "use, TPS is investigational and the standard off-label disclosure applies. TPS use is restricted "
            "to the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. Where the patient has reduced capacity, consent must be obtained from a "
            "legal guardian or authorised representative in accordance with applicable law. For MCI patients "
            "with preserved capacity, standard consent applies. Non-compliance is a clinical governance "
            "violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient / caregiver-rated):",
        "prs_primary_items": [
            "Short-term memory (recall of recent events and information)",
            "Long-term memory (access to established memories)",
            "Word-finding (naming objects, finding words mid-sentence)",
            "Orientation (time, place, and person)",
            "Decision-making (daily choices and planning)",
            "Problem-solving (managing novel challenges)",
            "Learning new information",
            "Recognition (faces, familiar places, objects)",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Depression / low mood",
            "Anxiety",
            "Apathy / motivation",
            "Sleep quality",
            "Agitation / restlessness",
            "Wandering / disorientation",
            "Appetite and weight",
            "Independence in activities of daily living (ADL)",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Amnestic MCI, Multi-Domain MCI, Early-Onset AD, Late-Onset AD, "
            "Posterior Cortical Atrophy, Logopenic, Behavioural/Frontal, Mixed AD-Vascular, or Apathy-Dominant."
        ),

        "pre_session_med_check": "☐ Record cholinesterase inhibitor / memantine (name, dose, timing of last dose, caregiver-confirmed adherence)",
        "session_med_doc": "Medication state (cholinesterase inhibitor / memantine adherence, timing of last dose, caregiver report of behaviour today)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: Cognitive performance in AD/MCI fluctuates with fatigue, "
            "infection, dehydration, and medication state. Standardise assessment conditions between baseline "
            "and follow-up — same time of day, same caregiver present, same medication state. Acute illness "
            "episodes (UTI, respiratory infection) in the preceding 4 weeks must be documented before "
            "interpreting SOZO PRS or cognitive screen changes."
        ),

        "inclusion_items": [
            "Confirmed diagnosis of Alzheimer's disease or MCI (NIA-AA criteria or equivalent; specialist-confirmed)",
            "MMSE ≥15 or MoCA ≥10 at baseline (sufficient for meaningful participation)",
            "Age 50+ years (early-onset AD: 40+ with specialist confirmation)",
            "Able to attend sessions with caregiver support or comply with home-use protocol",
            "Written informed consent (patient with capacity, or guardian/representative for reduced capacity)",
            "Baseline SOZO PRS and cognitive outcome measures (MoCA or MMSE) completed",
        ],
        "exclusion_items": [
            "Intracranial metallic hardware in stimulation path",
            "Cochlear implant",
            "Skull defects, craniectomy, or recent craniotomy",
            "Active intracranial tumour",
            "Open wounds at electrode sites",
            "Pregnancy (tDCS, TPS)",
            "Inability to provide informed consent and no available legal representative",
        ],
        "conditional_items": [
            "Cardiac pacemaker or defibrillator",
            "Epilepsy or seizure history (higher prevalence in AD — requires neurology review)",
            "MMSE below 15 (reduced cooperation and informed consent capacity — guardian consent required)",
            "Unstable cardiovascular disease or recent cardiac event",
            "Active psychosis or severe agitation preventing safe device application",
            "Coagulation disorders or anticoagulants (especially TPS)",
            "Dermatological conditions at electrode sites",
            "Severe behaviours requiring pharmacological sedation (stimulation not suitable until stabilised)",
        ],

        "modality_table": [
            ["Modality", "Device", "Classification", "AD/MCI Status"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Level B evidence — established NIBS for cognitive decline"],
            ["TPS", "NEUROLITH® (Storz Medical)", "CE Class IIa", "CE-marked (On-Label for AD) / Investigational for MCI"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked", "Emerging adjunctive — neuroinflammation and memory consolidation"],
            ["CES", "Alpha-Stim®", "FDA-cleared", "Investigational (Off-Label) — apathy, sleep, and mood component"],
        ],
        "offlabel_table": [
            ["Modality", "Regulatory Status", "AD/MCI Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Established NIBS; Level B evidence for memory and cognitive function in AD", "Standard informed consent"],
            ["TPS", "CE Class IIa", "CE-marked for Alzheimer's disease (on-label); investigational for MCI", "Standard for AD; off-label disclosure for MCI"],
            ["taVNS", "CE-marked", "Emerging adjunctive — neuroinflammation reduction and memory consolidation pathway", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "Off-label supportive — apathy, sleep, and anxiety comorbidity in AD", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Amnestic MCI", "Early DMN atrophy (hippocampal-PCC disconnection); episodic memory failure with preserved executive function"],
            ["Multi-Domain MCI", "DMN + CEN co-impairment; memory plus executive or language deficits; higher AD conversion risk"],
            ["Early-Onset AD", "Prominent CEN fragmentation (executive) + DMN atrophy; younger presentation; rapid progression risk"],
            ["Late-Onset AD", "Progressive DMN degeneration + widespread network disconnection; amyloid and tau co-pathology"],
            ["Posterior Cortical Atrophy", "Parieto-occipital network disruption; visuospatial impairment, dressing apraxia; SMN-ATTENTION involvement"],
            ["Logopenic", "Left temporo-parietal language network atrophy; word-finding and repetition failure; phonological loop disruption"],
            ["Behavioural / Frontal", "CEN-LIMBIC dysregulation; disinhibition, apathy, and compulsive behaviours; frontal network predominance"],
            ["Apathy-Dominant", "CEN-LIMBIC disconnection; profound motivation failure; reward circuit hypofunction; requires specific FNON targeting"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["F3/F4 bilateral DLPFC", "Executive / working memory", "Graded cognitive training (categorisation, n-back, word association); keep session short and structured"],
            ["P3/P4 (temporal-parietal)", "Memory consolidation", "Structured recall tasks, name-face association, semantic memory exercises; spaced repetition"],
            ["F3 anode / Pz cathode", "Attention / DMN modulation", "Attention-guided reality orientation therapy, present-moment grounding tasks"],
            ["Fp1/Fp2 / F3", "Apathy / motivation", "Pleasurable activity scheduling, social reminiscence therapy, caregiver-guided task engagement"],
            ["taVNS + tDCS combined", "Neuroplasticity / mood", "Music-based memory therapy, emotionally salient reminiscence, caregiver interaction tasks"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Memory", "Clinically meaningful improvement or stabilisation in MoCA memory items + PRS memory domain; caregiver global impression"],
            ["Executive / Cognition", "Maintained or improved executive and orientation scores (MoCA total, PRS items); ADL stability"],
            ["Behaviour / Apathy", "Reduction in apathy, agitation, or neuropsychiatric symptoms (PRS secondary + NPI-Q equivalent)"],
            ["Function / ADL", "Better or maintained independence in activities of daily living (caregiver-reported); reduced caregiver burden"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Amnestic MCI", "tDCS P3/P4 anode (temporal-parietal memory) + F3/F4 supportive + TPS cranial (hippocampal vicinity) + taVNS"],
            ["Multi-Domain MCI", "tDCS F3/F4 bilateral DLPFC + P3/P4 + TPS cranial comprehensive + taVNS + CES supportive"],
            ["Early-Onset AD", "tDCS F3/F4 bilateral + P3/P4 anode + TPS cranial targeted + taVNS primary (neuroinflammation)"],
            ["Late-Onset AD", "TPS cranial (CE-marked, on-label) primary + tDCS F3/F4 + P3/P4 + taVNS + CES (sleep/mood)"],
            ["Posterior Cortical Atrophy", "tDCS P3/P4/O1/O2 anode (posterior) + TPS parieto-occipital + taVNS supportive"],
            ["Logopenic", "tDCS F3/T3 (L hemisphere language) anode + TPS left frontal + temporal + taVNS supportive"],
            ["Behavioural / Frontal", "tDCS F3/F4 bilateral DLPFC + TPS frontal + taVNS + CES (behavioural stabilisation)"],
            ["Apathy-Dominant", "tDCS F3 anode / Fp2 cathode (reward circuit) + TPS frontal + taVNS + CES; pair with meaningful activity"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },

    "stroke_rehab": {
        "slug": "stroke_rehab",
        "cover_title": "POST-STROKE REHABILITATION",
        "name": "Post-Stroke Rehabilitation (Stroke)",
        "short": "Stroke",
        "abbr": "Stroke",
        "med_name": "anticoagulants / neuroprotective agents",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Post-Stroke Rehabilitation (Stroke). For use by the treating Doctor and "
            "authorised SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Post-Stroke Rehabilitation is "
            "INVESTIGATIONAL at SOZO Brain Center. It is not CE-marked or FDA-approved for stroke "
            "rehabilitation. All patients must provide written informed consent inclusive of the off-label "
            "TPS disclosure. TPS use is restricted to the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in stroke rehabilitation. Where capacity is reduced (aphasia, cognitive impairment), "
            "alternative consent pathways must be followed. Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient / caregiver-rated):",
        "prs_primary_items": [
            "Arm / hand strength (affected side)",
            "Leg strength and mobility (affected side)",
            "Hand dexterity and fine motor control",
            "Walking ability (distance, speed, safety)",
            "Balance (standing and walking balance)",
            "Speech clarity and expression (if aphasia present)",
            "Swallowing function (dysphagia severity)",
            "Facial movement (if facial palsy present)",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Post-stroke fatigue",
            "Post-stroke depression",
            "Cognitive clarity (attention, memory, processing)",
            "Central post-stroke pain",
            "Sleep quality",
            "Visual field and spatial awareness",
            "Spatial neglect (if present)",
            "Independence in activities of daily living (ADL)",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Motor Upper Limb, Motor Lower Limb, Aphasia, Spatial Neglect, "
            "Cognitive, Spasticity-Dominant, Dysphagia, Post-Stroke Depression, or Central Pain."
        ),

        "pre_session_med_check": "☐ Record anticoagulant / antithrombotic medication (name, dose, timing of last dose, INR if on warfarin); note current functional status vs. last session",
        "session_med_doc": "Medication state (anticoagulant adherence, timing of last dose, any changes in neurological status since last session)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: Post-stroke recovery includes spontaneous neurological "
            "recovery (Brunnstrom stages) that may confound treatment response attribution. Standardise "
            "assessment conditions between baseline and follow-up, documenting stroke chronicity and any "
            "intercurrent events. Clearly distinguish NIBS-attributable improvement from spontaneous recovery "
            "by anchoring response criteria to the chronic phase (>3 months post-stroke)."
        ),

        "inclusion_items": [
            "Confirmed ischaemic or haemorrhagic stroke (CT/MRI confirmed; specialist-diagnosed)",
            "Chronic stroke phase (≥3 months post-event; beyond peak spontaneous recovery window) or subacute with specialist approval",
            "Age 18+ years",
            "Able to attend sessions or comply with home-use protocol (with caregiver if needed)",
            "Written informed consent (patient with capacity, or guardian/representative for reduced capacity)",
            "Baseline SOZO PRS and functional outcome measures (Barthel or MAS) completed",
        ],
        "exclusion_items": [
            "Intracranial metallic hardware in stimulation path or in vicinity of lesion",
            "Cochlear implant",
            "Skull defects, craniectomy, or recent craniotomy (within 6 months of planned stimulation site)",
            "Active intracranial haemorrhage or unstable lesion",
            "Open wounds at electrode sites",
            "Pregnancy (tDCS, TPS)",
            "Inability to provide informed consent and no available legal representative",
        ],
        "conditional_items": [
            "Cardiac pacemaker or defibrillator",
            "Post-stroke epilepsy or seizure history",
            "Severe cognitive impairment limiting cooperation and outcome measurement",
            "Unstable cardiovascular status or recent cardiac event",
            "Spasticity so severe it prevents safe device placement",
            "Coagulation disorders or anticoagulants — TPS requires haematology clearance; check INR before each TPS session",
            "Severe aphasia limiting consent capacity — use supported consent process",
            "Active post-stroke depression with suicidal ideation — psychiatric stabilisation first",
        ],

        "modality_table": [
            ["Modality", "Device", "Classification", "Stroke Rehab Status"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Level A/B evidence — established NIBS for motor rehabilitation"],
            ["TPS", "NEUROLITH® (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL (Off-Label)"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked", "Emerging — paired with language therapy (aphasia); motor rehab adjunct"],
            ["CES", "Alpha-Stim®", "FDA-cleared", "Investigational (Off-Label) — fatigue, depression, sleep component"],
        ],
        "offlabel_table": [
            ["Modality", "Regulatory Status", "Stroke Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Established NIBS; Level A/B evidence for motor rehabilitation post-stroke", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Emerging — paired VNS for aphasia and motor rehabilitation adjunct", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "Off-label supportive — post-stroke depression, fatigue, and sleep", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Motor Upper Limb", "Contralateral SMN disruption (M1 lesion or tract damage); ipsilateral SMN compensatory recruitment"],
            ["Motor Lower Limb", "SMN-cerebellar-SMA pathway disruption; gait initiation and balance network impairment"],
            ["Aphasia", "Left hemisphere language network damage; Broca's / Wernicke's area involvement; CEN-language disconnection"],
            ["Spatial Neglect", "Right parietal-ATTENTION network damage; visuospatial network disruption; SN lateralisation failure"],
            ["Cognitive", "CEN and ATTENTION network damage; post-stroke cognitive impairment; DMN disruption"],
            ["Spasticity-Dominant", "SMN hyperexcitability (inhibitory circuit damage); upper motor neuron syndrome with reflex arc disinhibition"],
            ["Dysphagia", "Bilateral cortical swallowing network (opercular, SMA) disruption; unilateral impairment often recovers spontaneously"],
            ["Post-Stroke Depression", "LIMBIC network disruption + SN dysregulation; CEN hypofunction; emotional processing impairment"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["Contralateral M1 anode (C3 or C4)", "Motor upper limb", "Repetitive task-specific upper limb training (grasp, reach, functional tasks)"],
            ["Contralateral M1 + SMA (C3/C4 + Cz)", "Motor lower limb / gait", "Treadmill gait training, stepping exercises, physiotherapy-guided repetition"],
            ["F3/T3 (left hemisphere language)", "Aphasia", "Speech-language therapy sessions (picture naming, repetition) — paired VNS protocol preferred"],
            ["P3/P4 (parietal attention)", "Neglect / spatial awareness", "Visual scanning training, prism adaptation, visuospatial rehabilitation tasks"],
            ["F3 anode / F4 cathode (L-DLPFC)", "Cognitive / mood", "Cognitive rehabilitation tasks (attention, memory), structured behavioural activation"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Motor Function", "Clinically meaningful improvement in Fugl-Meyer or equivalent motor assessment + PRS motor items; improved MAS"],
            ["Gait / Balance", "Improved 10m walk test, TUG, and/or Berg Balance Scale + PRS walking and balance items"],
            ["Language / Communication", "Improvement in aphasia battery (WAB or equivalent) and/or PRS speech items; functional communication gain"],
            ["Function / ADL / Mood", "Better Barthel ADL score, improved post-stroke depression (PHQ-9 equivalent), and PRS secondary domain improvement"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Motor Upper Limb", "tDCS contralateral M1 anode (C3/C4) + ipsilateral M1 inhibition + TPS perilesional + peripheral (affected hand) + taVNS"],
            ["Motor Lower Limb", "tDCS Cz / SMA anode + TPS cranial + peripheral (soles, affected leg) + taVNS supportive"],
            ["Aphasia", "tDCS F3/T3 left hemisphere anode + TPS left frontal + temporal + taVNS (paired language therapy protocol)"],
            ["Spatial Neglect", "tDCS P4 inhibition (right parietal up) + P3 facilitation + TPS right parietal + taVNS supportive"],
            ["Cognitive", "tDCS F3/F4 bilateral DLPFC + P3/P4 anode + TPS frontal + taVNS supportive"],
            ["Spasticity-Dominant", "tDCS contralateral M1 cathode (inhibitory, affected side) + TPS cranial + peripheral spastic muscles + taVNS"],
            ["Dysphagia", "tDCS bilateral motor cortex (swallowing area, C3/C4 up) + TPS cranial bilateral + taVNS (paired swallowing therapy)"],
            ["Post-Stroke Depression", "tDCS F3 anode / F4 cathode (L-DLPFC up) + TPS frontal + taVNS primary + CES daily"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },
}
