"""Partners Tier condition data — Set 2: TBI, Chronic Pain, PTSD, OCD, MS"""

CDATA = {
    "tbi": {
        "slug": "tbi",
        "cover_title": "TRAUMATIC BRAIN INJURY",
        "name": "Traumatic Brain Injury (TBI)",
        "short": "TBI",
        "abbr": "TBI",
        "med_name": "neuroprotective agents / analgesics",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Traumatic Brain Injury (TBI). For use by the treating Doctor and authorised "
            "SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Traumatic Brain Injury is "
            "INVESTIGATIONAL at SOZO Brain Center. It is not CE-marked or FDA-approved for TBI. All patients "
            "must provide written informed consent inclusive of the off-label TPS disclosure. TPS use is "
            "restricted to the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in TBI treatment. Where cognitive capacity is reduced, an authorised representative must "
            "provide consent. Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient-rated):",
        "prs_primary_items": [
            "Headache (frequency and intensity)",
            "Concentration (sustained focus difficulty)",
            "Memory (short-term recall, working memory)",
            "Processing speed (mental slowing)",
            "Balance and dizziness",
            "Fatigue (cognitive and physical)",
            "Light sensitivity (photophobia)",
            "Noise sensitivity (phonophobia)",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Mood / irritability",
            "Sleep quality",
            "Anxiety",
            "Frustration tolerance",
            "Social function",
            "Motivation",
            "Word-finding difficulty",
            "Decision-making impairment",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Post-Concussion, Executive-Dominant, Headache-Dominant, "
            "Behavioural, Vestibular, Fatigue-Dominant, Memory-Impaired, Processing Speed, or Sleep-Dominant."
        ),

        "pre_session_med_check": "☐ Record current medications (analgesics, neuroprotective agents, antidepressants, sleep aids) — dose, timing, last administration; note headache status today",
        "session_med_doc": "Medication state (TBI medication adherence, timing of last dose, headache rating and fatigue level at session start)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: TBI symptom recovery is non-linear and confounded by "
            "spontaneous recovery, sleep quality, and psychological factors. Standardise assessment conditions "
            "between baseline and follow-up. Acute illness, stress events, or medication changes in the "
            "preceding two weeks must be documented. Distinguish NIBS-attributable change from ongoing "
            "spontaneous neurological recovery, particularly in the first 12 months post-injury."
        ),

        "inclusion_items": [
            "Confirmed TBI diagnosis (mild, moderate, or severe; specialist-confirmed with CT/MRI or clinical criteria)",
            "Persistent post-TBI symptoms causing functional impairment (>3 months from injury for mild TBI)",
            "Age 16+ years",
            "Able to attend sessions or comply with home-use protocol",
            "Written informed consent (including TPS off-label disclosure)",
            "Baseline SOZO PRS and TBI outcome measures (PCSS or equivalent) completed",
        ],
        "exclusion_items": [
            "Intracranial metallic hardware at or near planned stimulation sites",
            "Cochlear implant",
            "Skull defects, craniectomy, or craniotomy (within 12 months; requires specialist review)",
            "Active intracranial haemorrhage or unstable intracranial pathology",
            "Open wounds at electrode sites",
            "Pregnancy (tDCS, TPS)",
            "Inability to provide informed consent and no available legal representative",
        ],
        "conditional_items": [
            "Cardiac pacemaker or defibrillator",
            "Post-TBI epilepsy or seizure history (requires neurology clearance)",
            "Severe cognitive impairment limiting cooperation and consent capacity",
            "Unstable psychiatric comorbidity (PTSD, severe depression) requiring stabilisation first",
            "Active substance abuse",
            "Coagulation disorders or anticoagulants (especially TPS — check INR/platelets before session)",
            "Dermatological conditions at electrode sites",
            "Acute post-TBI phase (<3 months) — use only with neurology specialist approval",
        ],

        "modality_table": [
            ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Open-label", "10+"],
            ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Investigational", "0+"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked (epilepsy/depression)", "Open-label, Pilot", "0+"],
            ["CES", "Alpha-Stim\u00ae", "FDA-cleared (anxiety/insomnia/depression)", "Open-label, Pilot", "0+"],
            ["TMS", "NeuroStar / MagVenture / Magstim", "CE/FDA (research use)", "RCT, Open-label", "10+"],
            ["PBM", "Vielight Neuro / Coronet", "CE/FDA (research)", "Open-label, Pilot RCT", "25+"],
            ["PEMF", "BrainsWay / MagPro", "CE/FDA (research)", "RCT, Open-label", "10+"],
        ],
        "best_modality": "PBM (810 nm), tDCS",
        "offlabel_table": [
            ["Modality", "Regulatory Status", "TBI Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Investigational — emerging evidence for cognitive and mood rehabilitation post-TBI", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Emerging adjunctive — neuroprotection, pain, and autonomic modulation post-TBI", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "Off-label supportive — post-TBI headache, sleep, and anxiety component", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Post-Concussion", "Diffuse CEN-SN-DMN disruption; widespread network inefficiency; multisymptom mild TBI presentation"],
            ["Executive-Dominant", "CEN fragmentation (frontal lobe impact); planning, inhibition, and cognitive flexibility impairment"],
            ["Headache-Dominant", "SN sensitisation (central sensitisation + trigeminal pathway); pain-attention network coupling"],
            ["Behavioural", "CEN-LIMBIC dysregulation (orbitofrontal / temporal injury); disinhibition, impulsivity, emotional lability"],
            ["Vestibular", "SMN-cerebellar-ATTENTION pathway disruption; balance, dizziness, and oculomotor network impairment"],
            ["Fatigue-Dominant", "Global network energy impairment; thalamo-cortical modulation disruption; cognitive fatigue circuit"],
            ["Memory-Impaired", "DMN-hippocampal network disruption + CEN working memory deficit; encoding and retrieval impairment"],
            ["Processing Speed", "Diffuse white matter disruption (axonal injury); CEN-ATTENTION network slowing; reaction time impairment"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["F3/F4 bilateral DLPFC", "Executive / working memory", "Graded cognitive rehabilitation (task-switching, planning tasks, structured problem-solving)"],
            ["Cz / Fz", "Processing speed / attention", "Reaction time tasks, visual vigilance (CPT), simple go/no-go paradigm"],
            ["F3 anode / Pz cathode", "Memory / DMN modulation", "Structured recall tasks, spaced repetition, verbal and visual memory exercises"],
            ["Fpz cathode / F3 anode", "Headache / arousal reduction", "Relaxation response, guided breathing, biofeedback; reduce screen exposure during session"],
            ["taVNS + CES combined", "Fatigue and pain", "Slow breathing, body scan, paced activity scheduling; no high-effort cognitive load"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Cognitive", "Clinically meaningful improvement in PCSS cognitive items + objective cognitive screen (MoCA or processing speed battery)"],
            ["Headache / Pain", "Reduction in headache frequency and intensity (PRS headache item + headache diary)"],
            ["Fatigue", "Reduction in fatigue severity (PRS fatigue item) and improved activity tolerance and daily functioning"],
            ["Mood / Function", "Improvement in mood, irritability, and social/occupational function (PRS secondary + patient-reported)"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Post-Concussion", "tDCS F3/F4 bilateral DLPFC + TPS frontal + taVNS + CES daily; low-intensity graduated protocol"],
            ["Executive-Dominant", "tDCS F3/F4 bilateral DLPFC (2 mA) + TPS frontal targeted + taVNS supportive"],
            ["Headache-Dominant", "CES primary (daily) + taVNS (pain/autonomic) + tDCS Fpz cathode + TPS frontal (low energy); avoid temporal TPS"],
            ["Behavioural", "tDCS F3/F4 bilateral + TPS orbitofrontal / temporal + taVNS + CES (behavioural regulation)"],
            ["Vestibular", "tDCS Cz / cerebellar (Cz + C7 posterior) + TPS cranial + peripheral vestibular-cervical + taVNS"],
            ["Fatigue-Dominant", "tDCS Cz anode / Fpz cathode + TPS frontal + taVNS primary + CES daily; strict energy management"],
            ["Memory-Impaired", "tDCS P3/P4 anode (temporal-parietal) + F3/F4 supportive + TPS cranial + taVNS"],
            ["Processing Speed", "tDCS F3/F4 bilateral + Cz/FCz + TPS frontal + taVNS; pair with reaction time and speed-of-processing tasks"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },

    "chronic_pain": {
        "slug": "chronic_pain",
        "cover_title": "CHRONIC PAIN / FIBROMYALGIA",
        "name": "Chronic Pain / Fibromyalgia (CP)",
        "short": "Chronic Pain",
        "abbr": "CP",
        "med_name": "analgesics / gabapentinoids",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Chronic Pain / Fibromyalgia (CP). For use by the treating Doctor and "
            "authorised SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Chronic Pain / Fibromyalgia is "
            "INVESTIGATIONAL at SOZO Brain Center. It is not CE-marked or FDA-approved for CP. All patients "
            "must provide written informed consent inclusive of the off-label TPS disclosure. TPS use is "
            "restricted to the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in Chronic Pain treatment. Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient-rated):",
        "prs_primary_items": [
            "Pain intensity (average over past week)",
            "Pain frequency (proportion of waking hours in pain)",
            "Pain interference with activities",
            "Tenderness / allodynia",
            "Stiffness (morning or movement-related)",
            "Fatigue (pain-related exhaustion)",
            "Physical function (ability to perform daily tasks)",
            "Flare frequency and severity",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Sleep quality (pain-disturbed sleep)",
            "Depression / low mood",
            "Anxiety",
            "Cognitive fog (fibro-fog)",
            "Social withdrawal (due to pain)",
            "Medication dependence",
            "Exercise tolerance",
            "Overall quality of life",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Nociceptive, Neuropathic, Nociplastic, Fibromyalgia, CRPS, "
            "Musculoskeletal, Headache/Migraine, Visceral, or Pain-Depression Comorbid."
        ),

        "pre_session_med_check": "☐ Record analgesic medication (name, dose, timing of last dose, opioid status if applicable); note current pain rating (NRS 0–10)",
        "session_med_doc": "Medication state (analgesic adherence, timing of last dose, current pain NRS rating at session start)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: Chronic pain fluctuates with weather, activity level, "
            "sleep quality, and medication timing. Standardise baseline and follow-up assessments — same time "
            "of day, same medication state relative to last dose, and same physical activity level in the "
            "preceding 24 hours. Flare events in the week prior to assessment must be documented before "
            "interpreting SOZO PRS changes."
        ),

        "inclusion_items": [
            "Confirmed chronic pain condition (≥3 months duration; specialist-diagnosed or GP-referred with documented history)",
            "Moderate to severe pain interference with function (NRS ≥5 average, or PRS ≥5)",
            "Age 18+ years",
            "Able to attend sessions or comply with home-use protocol",
            "Written informed consent (including TPS off-label disclosure)",
            "Baseline SOZO PRS and pain outcome measures (NRS + BPI or equivalent) completed",
        ],
        "exclusion_items": [
            "Intracranial metallic hardware in stimulation path",
            "Cochlear implant",
            "Skull defects, craniectomy, or recent craniotomy",
            "Active intracranial tumour",
            "Open wounds at electrode sites or stimulation target regions (skin)",
            "Pregnancy (tDCS, TPS)",
            "Inability to provide informed consent",
        ],
        "conditional_items": [
            "Cardiac pacemaker or defibrillator",
            "Epilepsy or seizure history",
            "CRPS Stage II/III — active sympathetically-maintained pain (requires specialist review for TPS)",
            "Active substance abuse or opioid dependence (requires pain specialist co-management)",
            "Unstable psychiatric comorbidity (severe depression, suicidal ideation)",
            "Coagulation disorders or anticoagulants (especially TPS — assess peripheral application sites)",
            "Dermatological conditions at electrode sites or TPS peripheral application sites",
            "Implanted spinal cord stimulator or peripheral nerve stimulator (requires specialist review)",
        ],

        "modality_table": [
            ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Meta-analysis", "150+"],
            ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Investigational", "5+"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked (epilepsy/depression)", "RCT, Open-label", "40+"],
            ["CES", "Alpha-Stim\u00ae", "FDA-cleared (anxiety/insomnia/depression)", "RCT, Open-label", "35+"],
            ["TMS", "NeuroStar / MagVenture / Magstim", "CE/FDA (research use)", "RCT, Meta-analysis", "60+"],
            ["tACS", "Starstim / NeuroConn", "CE Class IIa (research)", "Open-label, Pilot", "10+"],
            ["PBM", "Vielight Neuro / Coronet", "CE/FDA (research)", "Open-label, Pilot RCT", "10+"],
            ["PEMF", "BrainsWay / MagPro", "CE/FDA (research)", "RCT, Open-label", "15+"],
            ["LIFU", "Sonic Concepts / FUS Instruments", "Investigational", "Pilot RCT, Open-label", "15+"],
            ["tRNS", "Starstim / NeuroConn", "CE Class IIa (research)", "Open-label, Pilot", "5+"],
            ["DBS", "Medtronic / Abbott", "FDA (research \u2014 chronic pain)", "RCT, Open-label", "10+"],
        ],
        "best_modality": "tDCS (M1), TMS (M1)",
        "offlabel_table": [
            ["Modality", "Regulatory Status", "Chronic Pain Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Established NIBS; Level B evidence for M1 and DLPFC montages in chronic pain", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Emerging — vagal anti-inflammatory pathway and descending pain inhibition", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "FDA 510k cleared for pain, anxiety, and insomnia", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Nociceptive", "Peripheral nociceptor activation with intact central processing; SN activation proportionate to tissue damage"],
            ["Neuropathic", "Peripheral or central nervous system damage; SN sensitisation + SMN dysregulation; burning/shooting quality"],
            ["Nociplastic", "Central sensitisation without tissue damage; SN global hypersensitivity; DMN pain rumination amplification"],
            ["Fibromyalgia", "Widespread nociplastic pain; SN hyperactivation + DMN rumination + CEN hypofunction (fibro-fog)"],
            ["CRPS", "Sympathetic-somatic coupling; SMN-SN dysregulation; severe allodynia; autonomic network involvement"],
            ["Musculoskeletal", "Peripheral nociceptive + SN amplification; localised SMN involvement; activity-related pattern"],
            ["Headache / Migraine", "Trigeminovascular-SN pathway sensitisation; cortical spreading depression; ATTENTION network disruption"],
            ["Pain-Depression Comorbid", "SN-LIMBIC overcoupling; bidirectional pain-mood amplification; CEN hypofunction (catastrophising)"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["M1 anode (C3/C4 contralateral)", "Descending pain inhibition", "Graded motor imagery, mirror box therapy, gentle repetitive movement tasks"],
            ["F3 anode / Pz cathode (DLPFC up)", "Pain catastrophising / mood", "Pain acceptance exercises (ACT), cognitive defusion, pleasant imagery"],
            ["F3/F4 bilateral DLPFC", "Cognitive and mood", "Mindfulness-based pain management, structured pacing and activity scheduling"],
            ["TPS peripheral + taVNS", "Peripheral pain + vagal", "Passive positioning, progressive relaxation, breathing exercises — no active movement required"],
            ["CES + taVNS combined", "Sleep and anxiety", "Relaxation response training, sleep hygiene education, slow breathing"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Pain Intensity / Frequency", "Clinically meaningful reduction in NRS (≥30%) + PRS pain intensity and frequency items"],
            ["Physical Function", "Improved physical activity tolerance, daily task completion, and PRS functional items"],
            ["Sleep / Fatigue", "Better sleep quality (PRS secondary) and reduced pain-related fatigue (PRS fatigue item)"],
            ["Mood / Quality of Life", "Improvement in depression/anxiety (PRS secondary) and global quality of life rating"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Nociceptive", "tDCS M1 anode (C3/C4) + TPS peripheral (pain ROIs) + taVNS + CES supportive"],
            ["Neuropathic", "tDCS M1 anode (contralateral C3/C4) + F3 anode / Pz cathode + TPS peripheral nerve pathway + taVNS + CES"],
            ["Nociplastic", "tDCS F3/F4 bilateral DLPFC + M1 anode + TPS cranial + peripheral + taVNS primary + CES daily"],
            ["Fibromyalgia", "tDCS F3/F4 bilateral + M1 anode (C3/C4) + TPS cranial + peripheral widespread + taVNS primary + CES daily"],
            ["CRPS", "tDCS contralateral M1 anode + TPS peripheral (affected limb) + taVNS primary; start low intensity; specialist review"],
            ["Musculoskeletal", "tDCS M1 anode (C3/C4) + TPS peripheral (affected muscle group) + taVNS + CES supportive"],
            ["Headache / Migraine", "CES primary + taVNS + tDCS Fpz cathode / F3 anode + TPS cranial (low energy); avoid during acute migraine"],
            ["Pain-Depression Comorbid", "tDCS F3 anode / F4 cathode (L-DLPFC up) + M1 anode + TPS frontal + peripheral + taVNS + CES daily"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },

    "ptsd": {
        "slug": "ptsd",
        "cover_title": "POST-TRAUMATIC STRESS DISORDER",
        "name": "Post-Traumatic Stress Disorder (PTSD)",
        "short": "PTSD",
        "abbr": "PTSD",
        "med_name": "SSRIs / SNRIs / prazosin",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Post-Traumatic Stress Disorder (PTSD). For use by the treating Doctor and "
            "authorised SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Post-Traumatic Stress Disorder is "
            "INVESTIGATIONAL at SOZO Brain Center. It is not CE-marked or FDA-approved for PTSD. All "
            "patients must provide written informed consent inclusive of the off-label TPS disclosure. TPS "
            "use is restricted to the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in PTSD treatment. Trauma-sensitive consent procedures must be followed. "
            "Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient-rated):",
        "prs_primary_items": [
            "Intrusive memories (unwanted, recurring trauma memories)",
            "Flashbacks (reliving the trauma as if happening now)",
            "Nightmares (trauma-related disturbing dreams)",
            "Emotional reactivity (intense distress to triggers)",
            "Avoidance of trauma-related situations",
            "Avoidance of trauma-related thoughts / feelings",
            "Hypervigilance (constantly on guard, scanning for danger)",
            "Exaggerated startle response",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Sleep disturbance (insomnia, fragmented sleep)",
            "Depression / persistent low mood",
            "Anger and irritability",
            "Concentration difficulty",
            "Guilt and shame",
            "Emotional detachment / numbing",
            "Trust and relationship difficulties",
            "Substance use (as coping mechanism)",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Re-experiencing, Avoidance-Dominant, Hyperarousal, Dissociative, "
            "Complex PTSD, TBI Comorbid, Depression Comorbid, Nightmare-Dominant, or Moral Injury."
        ),

        "pre_session_med_check": "☐ Record SSRI / SNRI / prazosin (name, dose, timing of last dose, adherence); note current distress rating and any recent trauma exposure or flashback episode",
        "session_med_doc": "Medication state (SSRI/SNRI adherence, timing of last dose, current distress rating, any trauma exposure since last session)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: PTSD symptoms fluctuate with trauma anniversaries, "
            "media exposure, and social triggers. Standardise assessment conditions between baseline and "
            "follow-up. Document significant trauma-related events, exposure therapy milestones, and "
            "concurrent psychotherapy progress when interpreting SOZO PRS changes. Avoidance behaviours "
            "may mask symptom severity at follow-up — use corroborating clinician assessment."
        ),

        "inclusion_items": [
            "Confirmed PTSD diagnosis (DSM-5 / ICD-11 criteria; clinician-administered CAPS-5 or PCL-5 ≥33 preferred)",
            "Moderate to severe PTSD symptom burden causing functional impairment",
            "Age 18+ years; sufficient stabilisation for NIBS (not in acute crisis)",
            "Able to attend sessions or comply with home-use protocol",
            "Written informed consent (including TPS off-label disclosure; trauma-sensitive process)",
            "Baseline SOZO PRS and PTSD outcome measures (PCL-5 or equivalent) completed",
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
            "Active suicidal ideation with plan or intent (requires psychiatric stabilisation first)",
            "Active dissociative episodes during sessions (pause; ground first; proceed only when stabilised)",
            "Active substance abuse or dependence (requires co-management with addiction specialist)",
            "Coagulation disorders or anticoagulants (especially TPS)",
            "Dermatological conditions at electrode sites",
            "Severe comorbid bipolar disorder in acute phase (requires mood stabilisation first)",
        ],

        "modality_table": [
            ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Open-label", "10+"],
            ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Investigational", "0+"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked (epilepsy/depression)", "Open-label, Pilot", "5+"],
            ["CES", "Alpha-Stim\u00ae", "FDA-cleared (anxiety/insomnia/depression)", "Open-label, Military cohort studies", "10+"],
            ["TMS", "NeuroStar / MagVenture / Magstim", "CE/FDA (research use)", "RCT, Open-label", "30+"],
        ],
        "best_modality": "TMS, CES",
        "offlabel_table": [
            ["Modality", "Regulatory Status", "PTSD Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Investigational — prefrontal upregulation for fear regulation and trauma memory reconsolidation", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Primary adjunctive — parasympathetic vagal regulation and fear extinction enhancement", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "FDA 510k cleared for anxiety; supportive for PTSD hyperarousal and sleep", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Re-experiencing", "Hippocampal-amygdala hyperconnectivity; SN over-encoding of trauma signal; DMN trauma-narrative intrusion"],
            ["Avoidance-Dominant", "CEN-mediated behavioural suppression; SN avoidance routing; LIMBIC fear avoidance coupling"],
            ["Hyperarousal", "SN tonic hyperactivation; LIMBIC-autonomic coupling; reduced prefrontal inhibition (CEN hypofunction)"],
            ["Dissociative", "DMN-SN dissociation (depersonalisation/derealisation); altered interoceptive processing; LIMBIC suppression"],
            ["Complex PTSD", "Multi-network disruption; CEN-LIMBIC-SN triad; identity and emotional regulation impairment; prolonged trauma"],
            ["TBI Comorbid", "CEN damage + SN hyperactivation; dual pathology — requires TBI and PTSD network mapping simultaneously"],
            ["Depression Comorbid", "LIMBIC hyperactivation + CEN hypofunction; overlapping MDD-PTSD network disruption profile"],
            ["Nightmare-Dominant", "LIMBIC-hippocampal sleep consolidation disruption; SN arousal during REM; night-specific re-experiencing"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["F3 anode / F4 cathode (L-DLPFC up)", "Fear regulation / executive", "Trauma-focused CBT (with therapist), cognitive processing, safe-memory activation"],
            ["Bilateral prefrontal (F3/F4 anode)", "Hyperarousal / mood", "Grounding techniques, present-moment awareness, diaphragmatic breathing"],
            ["Right temporal inhibition (TP8 cathode / F3 anode)", "Trauma intrusion", "EMDR preparation tasks, bilateral sensory stimulation, calm-place imagery"],
            ["taVNS primary", "Parasympathetic / fear extinction", "Slow breathing (5 breaths/min), progressive muscle relaxation, fear hierarchy exposure (low level)"],
            ["CES + taVNS combined", "Hyperarousal and sleep", "Sleep restriction therapy, relaxation response training, grounding protocol"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Intrusion / Re-experiencing", "Clinically meaningful reduction in PCL-5 intrusion subscale + PRS re-experiencing items"],
            ["Hyperarousal / Avoidance", "Reduction in hypervigilance and avoidance ratings (PRS + PCL-5 arousal and avoidance subscales)"],
            ["Sleep / Nightmares", "Improvement in sleep quality and nightmare frequency (PRS + sleep diary)"],
            ["Function / Mood", "Better social and occupational function, reduced depression/guilt (PRS secondary items + patient-reported)"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Re-experiencing", "tDCS F3 anode / F4 cathode (L-DLPFC up) + TPS frontal + right temporal + taVNS primary + CES"],
            ["Avoidance-Dominant", "tDCS F3/F4 bilateral DLPFC + TPS frontal + taVNS primary; pair with graduated exposure hierarchy"],
            ["Hyperarousal", "CES primary (daily) + taVNS primary + tDCS F3 anode / Fpz cathode + TPS frontal"],
            ["Dissociative", "taVNS primary + CES + tDCS F3/F4 bilateral (low intensity) + TPS frontal; avoid high stimulation intensity"],
            ["Complex PTSD", "tDCS F3/F4 bilateral + TPS frontal comprehensive + taVNS primary + CES; extended treatment block"],
            ["TBI Comorbid", "tDCS F3/F4 bilateral + Cz (TBI processing) + TPS frontal + taVNS + CES; address TBI network first"],
            ["Depression Comorbid", "tDCS F3 anode / F4 cathode + TPS frontal + taVNS primary + CES daily; integrated PTSD-MDD protocol"],
            ["Nightmare-Dominant", "CES (pre-sleep primary) + taVNS (evening) + tDCS Fpz / F3 cathode + TPS frontal supportive"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },

    "ocd": {
        "slug": "ocd",
        "cover_title": "OBSESSIVE-COMPULSIVE DISORDER",
        "name": "Obsessive-Compulsive Disorder (OCD)",
        "short": "OCD",
        "abbr": "OCD",
        "med_name": "SSRIs / clomipramine",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Obsessive-Compulsive Disorder (OCD). For use by the treating Doctor and "
            "authorised SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Obsessive-Compulsive Disorder is "
            "INVESTIGATIONAL at SOZO Brain Center. It is not CE-marked or FDA-approved for OCD. All patients "
            "must provide written informed consent inclusive of the off-label TPS disclosure. TPS use is "
            "restricted to the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in OCD treatment. Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient-rated):",
        "prs_primary_items": [
            "Obsession frequency (how often obsessions occur)",
            "Obsession distress (level of anxiety or distress caused)",
            "Time spent on obsessions (hours per day)",
            "Compulsion frequency (how often compulsions are performed)",
            "Compulsion distress (distress if compulsions are resisted)",
            "Resistance ability (capacity to resist compulsions)",
            "Control over obsessions (ability to dismiss them)",
            "Insight (recognition that obsessions/compulsions are excessive)",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Anxiety severity",
            "Depression / low mood",
            "Avoidance behaviours",
            "Social and relational impairment",
            "Work and occupational impact",
            "Sleep quality",
            "Decision-making difficulty",
            "Frustration and shame",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Contamination, Symmetry/Ordering, Harm/Checking, Hoarding, "
            "Pure Obsessional, Treatment-Resistant, Tic-Related, Insight-Poor, or OCD-Depression Comorbid."
        ),

        "pre_session_med_check": "☐ Record SSRI / clomipramine (name, dose, timing of last dose, adherence, duration of current regimen); note today's obsession severity rating",
        "session_med_doc": "Medication state (SSRI/clomipramine adherence, timing of last dose, OCD symptom severity rating at session start)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: OCD symptoms fluctuate with stress, life changes, and "
            "the natural waxing/waning course of the disorder. Standardise assessment conditions between "
            "baseline and follow-up. Document concurrent ERP (Exposure and Response Prevention) therapy "
            "milestones, medication changes, and significant life stressors when interpreting SOZO PRS "
            "changes. OCD insight variability must be considered when comparing self-rated scores."
        ),

        "inclusion_items": [
            "Confirmed OCD diagnosis (DSM-5 / ICD-11 criteria; Y-BOCS ≥16 or equivalent)",
            "Moderate to severe OCD burden causing significant functional impairment",
            "Age 16+ years",
            "Able to attend sessions or comply with home-use protocol",
            "Written informed consent (including TPS off-label disclosure)",
            "Baseline SOZO PRS and OCD outcome measures (Y-BOCS or OCI-R) completed",
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
            "Severe insight impairment (Y-BOCS insight item 0) — requires careful consent assessment",
            "Active psychosis (OCD with poor insight must be distinguished from psychosis)",
            "Active severe depression with suicidal ideation (requires psychiatric stabilisation first)",
            "Coagulation disorders or anticoagulants (especially TPS)",
            "Dermatological conditions at electrode sites",
            "Hoarding disorder with severe environmental obstacles — home-use safety assessment required",
        ],

        "modality_table": [
            ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Open-label", "10+"],
            ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Investigational", "0+"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked (epilepsy/depression)", "Open-label, Pilot", "5+"],
            ["CES", "Alpha-Stim\u00ae", "FDA-cleared (anxiety/insomnia/depression)", "Open-label, Pilot", "0+"],
            ["TMS", "NeuroStar / MagVenture / Magstim", "FDA-cleared (Deep TMS H7-OCD) / CE", "RCT, Meta-analysis", "100+"],
            ["DBS", "Medtronic / Abbott", "FDA-cleared (Refractory OCD \u2014 HDE)", "RCT, Open-label", "50+"],
            ["LIFU", "Sonic Concepts / FUS Instruments", "Investigational", "Pilot, Open-label", "3+"],
        ],
        "best_modality": "TMS (Deep/H7), DBS (VC/VS)",
        "offlabel_table": [
            ["Modality", "Regulatory Status", "OCD Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Investigational — SMA inhibition and DLPFC upregulation for OCD symptom reduction", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Emerging — autonomic and CSTC circuit modulation for OCD", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "Off-label supportive — anxiety and depression components in OCD", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Contamination", "OFC-caudate hyperactivation (disgust circuit); SN threat detection for contamination cues; CEN inhibitory failure"],
            ["Symmetry / Ordering", "SMA-putamen loop hyperactivation; sensorimotor 'not-just-right' experience; SMN-CEN coupling"],
            ["Harm / Checking", "OFC-DLPFC-caudate hyperactivation; doubt and error-detection amplification; SN-CEN failure to resolve uncertainty"],
            ["Hoarding", "Frontal-limbic dysregulation; decision-making network impairment; excessive attachment circuitry activation"],
            ["Pure Obsessional", "Intrusive thought network (DMN-SN coupling); CEN suppression failure for unwanted thoughts; LIMBIC amplification"],
            ["Treatment-Resistant", "CSTC circuit deeply entrenched; low insight; multi-network rigidity; poor prefrontal modulation"],
            ["Tic-Related", "SMN-SMA-basal ganglia loop dysregulation; sensorimotor urge circuit (SMN) + OCD network co-activation"],
            ["Insight-Poor", "CEN-mediated insight network impairment; reduced ability to evaluate obsession excessiveness; frontal hypoactivation"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["SMA inhibition (Cz cathode / F3 anode)", "Compulsion urge reduction", "ERP (Exposure and Response Prevention) hierarchy exercises — resist compulsion during stimulation"],
            ["F3/F4 bilateral DLPFC", "Executive / insight", "Cognitive restructuring, OCD thought record, meta-cognitive therapy exercises"],
            ["F3 anode / F4 cathode (L-DLPFC up)", "Anxiety / decision-making", "Uncertainty tolerance exercises, decision-making drills, CAT-based flexibility training"],
            ["Fpz / F3 cathode (frontal inhibition)", "Hyperarousal / anxiety", "Relaxation response, diaphragmatic breathing, progressive muscle relaxation"],
            ["taVNS + CES combined", "Autonomic and anxiety", "Guided parasympathetic activation, slow breathing (5 breaths/min), mindfulness of OCD thoughts"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Obsessions", "Clinically meaningful reduction in Y-BOCS obsession subscale (≥35%) + PRS obsession frequency and distress items"],
            ["Compulsions", "Reduction in compulsion frequency and distress (Y-BOCS compulsion subscale + PRS items)"],
            ["Insight / Control", "Improved insight and resistance ability (Y-BOCS insight items + PRS control items)"],
            ["Function / Anxiety", "Better social and occupational function, reduced anxiety and avoidance (PRS secondary items)"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Contamination", "tDCS F3/F4 bilateral DLPFC + SMA cathode (Cz) + TPS frontal OFC vicinity + taVNS + CES"],
            ["Symmetry / Ordering", "tDCS SMA cathode (Cz) + F3/F4 bilateral + TPS SMA / frontal + taVNS supportive"],
            ["Harm / Checking", "tDCS F3/F4 bilateral DLPFC + SMA cathode + TPS frontal + taVNS primary + CES"],
            ["Hoarding", "tDCS F3/F4 bilateral DLPFC + OFC vicinity + TPS frontal + taVNS + CES (decision-making tasks)"],
            ["Pure Obsessional", "tDCS F3 anode / Cz cathode + TPS frontal + taVNS primary + CES; pair with metacognitive therapy"],
            ["Treatment-Resistant", "tDCS F3/F4 bilateral + SMA cathode + TPS frontal comprehensive + taVNS primary + CES daily"],
            ["Tic-Related", "tDCS SMA cathode (Cz) + M1 supportive + TPS SMA + frontal + taVNS; target both tic and OCD circuits"],
            ["Insight-Poor", "tDCS F3/F4 bilateral DLPFC + TPS frontal + taVNS + CES; pair with motivational interviewing"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },

    "ms": {
        "slug": "ms",
        "cover_title": "MULTIPLE SCLEROSIS",
        "name": "Multiple Sclerosis (MS)",
        "short": "MS",
        "abbr": "MS",
        "med_name": "disease-modifying therapy (DMT)",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Multiple Sclerosis (MS). For use by the treating Doctor and authorised "
            "SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Multiple Sclerosis is INVESTIGATIONAL "
            "at SOZO Brain Center. It is not CE-marked or FDA-approved for MS. All patients must provide "
            "written informed consent inclusive of the off-label TPS disclosure. TPS use is restricted to "
            "the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in MS treatment. Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient-rated):",
        "prs_primary_items": [
            "Fatigue (MS fatigue — distinct from sleepiness)",
            "Walking ability (distance, speed, and safety)",
            "Hand and arm coordination",
            "Balance (standing and moving balance)",
            "Visual clarity (blurring, double vision)",
            "Spasticity (muscle stiffness and spasms)",
            "Bladder / bowel function",
            "Sensory symptoms (numbness, tingling, pain)",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Cognitive fog (MS-related cognitive slowing)",
            "Depression / low mood",
            "Sleep quality",
            "Pain (neuropathic and musculoskeletal)",
            "Heat sensitivity (Uhthoff phenomenon)",
            "Social and relational function",
            "Work and occupational capacity",
            "Independence in daily activities",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Motor/Spasticity, Fatigue-Dominant, Cognitive, Ataxia-Dominant, "
            "Pain-Dominant, Bladder/Autonomic, Depression-Dominant, Visual, or Walking-Impaired."
        ),

        "pre_session_med_check": "☐ Record disease-modifying therapy (name, regimen, last dose); note any recent relapse, Uhthoff worsening, or heat exposure before session",
        "session_med_doc": "Medication state (DMT regimen and adherence, timing of symptom-management medications, current fatigue and heat sensitivity rating)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: MS symptoms are profoundly heat-sensitive (Uhthoff "
            "phenomenon) and fluctuate with fatigue, infection, and relapse. Standardise assessment "
            "conditions — same ambient temperature, same fatigue level, same time relative to DMT dosing. "
            "Any relapse event within 6 weeks of assessment must be documented and baseline reset. Do not "
            "attribute PRS changes to NIBS if a relapse or pseudo-relapse occurred during the treatment block."
        ),

        "inclusion_items": [
            "Confirmed Multiple Sclerosis diagnosis (McDonald criteria 2017 or equivalent; neurologist-confirmed)",
            "Clinically stable MS (no relapse within 3 months; EDSS ≤7.0 for active participation)",
            "Age 18+ years",
            "Able to attend sessions or comply with home-use protocol (with caregiver if needed)",
            "Written informed consent (including TPS off-label disclosure)",
            "Baseline SOZO PRS and MS outcome measures (MFIS, EDSS, MoCA) completed",
        ],
        "exclusion_items": [
            "Intracranial metallic hardware in stimulation path",
            "Cochlear implant",
            "Skull defects, craniectomy, or recent craniotomy",
            "Active intracranial tumour or lesion in planned stimulation path",
            "Open wounds at electrode sites",
            "Pregnancy (tDCS, TPS)",
            "Inability to provide informed consent",
        ],
        "conditional_items": [
            "Cardiac pacemaker or defibrillator",
            "Epilepsy or seizure history (higher prevalence in MS — requires neurology review)",
            "Recent relapse (within 3 months) — defer NIBS until clinically stable; reassess EDSS",
            "Severe heat sensitivity — temperature-controlled session environment required; monitor closely",
            "Severe cognitive impairment limiting cooperation and outcome measurement",
            "Coagulation disorders or anticoagulants (especially TPS)",
            "Dermatological conditions at electrode sites",
            "Active severe depression with suicidal ideation (requires psychiatric stabilisation first)",
        ],

        "modality_table": [
            ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Open-label", "10+"],
            ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Investigational", "0+"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked (epilepsy/depression)", "Open-label, Pilot", "0+"],
            ["CES", "Alpha-Stim\u00ae", "FDA-cleared (anxiety/insomnia/depression)", "Open-label, Pilot", "0+"],
            ["TMS", "NeuroStar / MagVenture / Magstim", "CE/FDA (research use)", "RCT, Open-label", "15+"],
            ["PEMF", "Magstim / EMS Technologies", "CE/FDA (research)", "RCT, Open-label", "10+"],
            ["tRNS", "Starstim / NeuroConn", "CE Class IIa (research)", "Open-label, Pilot", "5+"],
        ],
        "best_modality": "PEMF, tRNS",
        "offlabel_table": [
            ["Modality", "Regulatory Status", "MS Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Established NIBS; Level B evidence for fatigue reduction and motor rehabilitation in MS", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Emerging adjunctive — neuroinflammation, fatigue, and autonomic modulation in MS", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "Off-label supportive — MS fatigue, depression, and sleep comorbidity", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Motor / Spasticity", "SMN disruption (demyelination of corticospinal tract); upper motor neuron syndrome; CEN-SMN disconnection"],
            ["Fatigue-Dominant", "Thalamo-cortical fatigue network; widespread network inefficiency; CEN-DMN energy dysregulation"],
            ["Cognitive", "CEN fragmentation (periventricular lesion burden); processing speed reduction; DMN-CEN decoupling"],
            ["Ataxia-Dominant", "Cerebellar-SMN pathway disruption; coordination and balance network impairment; ATTENTION involvement"],
            ["Pain-Dominant", "SN sensitisation (central sensitisation) + SMN sensory pathway disruption; neuropathic pain network"],
            ["Bladder / Autonomic", "SMN-autonomic network disruption; pontine micturition centre disconnection; SN sensitisation"],
            ["Depression-Dominant", "LIMBIC hyperactivation + CEN hypofunction; MS-specific depression network; adjustment and organic components"],
            ["Walking-Impaired", "SMN lower limb pathway disruption + cerebellar-SMA network; fatigue-motor interaction; ATTENTION burden during gait"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["Contralateral M1 (C3/C4 anode)", "Motor / spasticity", "Graded physiotherapy — repetitive task training, resistance exercises, Frenkel coordination exercises"],
            ["F3/F4 bilateral DLPFC", "Fatigue and cognition", "Graded cognitive training (low-intensity, energy-managed), working memory tasks, paced activity scheduling"],
            ["Cz / SMA anode", "Gait and balance", "Treadmill walking (slow, supported), balance board, physiotherapy-guided stepping"],
            ["F3 anode / F4 cathode (L-DLPFC)", "Depression / mood", "Behavioural activation, pleasant activity scheduling, structured social engagement"],
            ["taVNS + CES combined", "Fatigue and neuroinflammation", "Rest-based relaxation, slow breathing, energy conservation strategies — no active task"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Fatigue", "Clinically meaningful reduction in MS fatigue (MFIS ≥4 point reduction + PRS fatigue item improvement)"],
            ["Motor / Walking", "Improvement in 10m walk test, TUG, or grip strength + PRS motor items; improved EDSS stability or improvement"],
            ["Cognition", "Improvement in SDMT or MoCA + PRS cognitive items; improved processing speed and working memory"],
            ["Mood / Function", "Better depression and mood scores (PHQ-9 equivalent) + improved independence and quality of life (PRS secondary)"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Motor / Spasticity", "tDCS contralateral M1 anode (C3/C4) + TPS cranial + peripheral affected limb + taVNS supportive"],
            ["Fatigue-Dominant", "tDCS F3/F4 bilateral DLPFC + Cz (energy modulation) + TPS cranial + taVNS primary + CES daily"],
            ["Cognitive", "tDCS F3/F4 bilateral DLPFC + P3/P4 anode + TPS frontal + taVNS supportive"],
            ["Ataxia-Dominant", "tDCS Cz / cerebellar (C7 posterior) + M1 anode + TPS cranial + peripheral cerebellar ROI + taVNS"],
            ["Pain-Dominant", "tDCS M1 anode (C3/C4) + F3 anode / Pz cathode + TPS cranial + peripheral pain sites + taVNS + CES"],
            ["Bladder / Autonomic", "taVNS primary (daily) + CES + tDCS F3/F4 supportive + TPS frontal; bladder diary tracking"],
            ["Depression-Dominant", "tDCS F3 anode / F4 cathode (L-DLPFC up) + TPS frontal + taVNS primary + CES daily"],
            ["Walking-Impaired", "tDCS Cz / SMA + M1 anode (C3/C4) + TPS cranial + peripheral lower limb + taVNS supportive"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },
}
