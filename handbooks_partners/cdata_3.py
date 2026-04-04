"""Partners Tier condition data — Set 3: ASD, Long COVID, Tinnitus, Insomnia"""

CDATA = {
    "asd": {
        "slug": "asd",
        "cover_title": "AUTISM SPECTRUM DISORDER",
        "name": "Autism Spectrum Disorder (ASD)",
        "short": "ASD",
        "abbr": "ASD",
        "med_name": "risperidone / aripiprazole",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Autism Spectrum Disorder (ASD). For use by the treating Doctor and "
            "authorised SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Autism Spectrum Disorder is "
            "INVESTIGATIONAL at SOZO Brain Center. It is not CE-marked or FDA-approved for ASD. All patients "
            "must provide written informed consent inclusive of the off-label TPS disclosure. TPS use is "
            "restricted to the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in ASD treatment. Where the patient lacks capacity, consent must be obtained from a legal "
            "guardian or authorised representative. Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient / caregiver-rated):",
        "prs_primary_items": [
            "Social interaction quality",
            "Verbal / non-verbal communication",
            "Repetitive behaviours (frequency and distress)",
            "Sensory sensitivity (over- or under-responsivity)",
            "Routine rigidity / intolerance of change",
            "Emotional regulation",
            "Eye contact and reciprocity",
            "Adaptive daily living skills",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Anxiety severity",
            "Sleep onset / maintenance problems",
            "Attention and concentration",
            "Executive function (planning, flexibility)",
            "Frustration tolerance / meltdown frequency",
            "Self-care independence",
            "Peer relationships and social participation",
            "Behavioural outbursts / self-injurious behaviour",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Social Communication, Restricted/Repetitive, Language-Dominant, "
            "Sensory, Executive, Emotional Dysregulation, ADHD Comorbid, Anxiety Comorbid, or Adaptive."
        ),

        "pre_session_med_check": "☐ Record current medication (risperidone, aripiprazole, stimulants if co-prescribed) — dose, timing, and last administration",
        "session_med_doc": "Medication state (ASD medication adherence, timing of last dose, any recent changes)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: Standardise assessment conditions and rater across "
            "baseline and follow-up. Caregiver-rated vs. self-rated changes must be documented consistently. "
            "Environmental or educational changes during the treatment period must be noted and factored into "
            "SOZO PRS interpretation."
        ),

        "inclusion_items": [
            "Confirmed ASD diagnosis (DSM-5 or ICD-11 criteria; clinical or formal assessment)",
            "Age 12+ years (or adult); parental/guardian consent for minors",
            "Able to tolerate device placement with adequate behavioural support",
            "Able to attend sessions or comply with home-use protocol with caregiver support",
            "Written informed consent (patient/guardian; including TPS off-label disclosure)",
            "Baseline SOZO PRS and functional outcome measures completed",
        ],
        "exclusion_items": [
            "Intracranial metallic hardware in stimulation path",
            "Cochlear implant",
            "Skull defects, craniectomy, or recent craniotomy",
            "Active intracranial tumour",
            "Open wounds at electrode sites",
            "Pregnancy (tDCS, TPS)",
            "Inability to tolerate device placement despite adequate preparation",
        ],
        "conditional_items": [
            "Cardiac pacemaker or defibrillator",
            "Epilepsy or seizure history (prevalent in ASD — requires neurology clearance)",
            "Severe intellectual disability limiting cooperation",
            "Unstable psychiatric comorbidity (severe aggression, active self-harm)",
            "Significant skin sensitivity or dermatological conditions at electrode sites",
            "Coagulation disorders or anticoagulants (especially TPS)",
            "Active psychosis or severe anxiety preventing device tolerance",
            "Recent medication change within 4 weeks (requires stability before baseline)",
        ],

        "modality_table": [
            ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Open-label", "5+"],
            ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Double-blind RCT, Sham-controlled", "2+"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked (epilepsy/depression)", "Open-label, Pilot", "0+"],
            ["CES", "Alpha-Stim\u00ae", "FDA-cleared (anxiety/insomnia/depression)", "Open-label, Pilot", "0+"],
            ["TMS", "NeuroStar / MagVenture / Magstim", "CE/FDA (research use)", "RCT, Open-label", "5+"],
        ],
        "best_modality": "TMS, TPS (emerging)",
        "offlabel_table": [
            ["Modality", "Regulatory Status", "ASD Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Investigational — emerging evidence for social/executive domains", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Emerging adjunctive — autonomic and emotional regulation", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "Off-label supportive — anxiety and sleep comorbidity", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Social Communication", "SN hypoactivation (social salience deficit), atypical DMN self-referential processing"],
            ["Restricted / Repetitive", "CEN rigidity (cognitive inflexibility), sensorimotor network over-coupling"],
            ["Language-Dominant", "Left hemisphere language network atypicality, CEN-ATTENTION dyscoordination"],
            ["Sensory", "SN hyper/hypo-responsivity, sensorimotor network threshold dysregulation"],
            ["Executive", "CEN fragmentation (planning, flexibility, inhibition failure), ATTENTION hypofunction"],
            ["Emotional Dysregulation", "LIMBIC hyperactivation, SN-LIMBIC overcoupling, prefrontal inhibition deficit"],
            ["ADHD Comorbid", "Dual CEN/ATTENTION hypofunction, DMN intrusion during tasks, impulsivity"],
            ["Anxiety Comorbid", "SN hyperactivation (threat over-detection), LIMBIC hyperactivity, DMN rumination"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["TP7/TP8 (temporoparietal)", "Social processing", "Social story review, facial emotion recognition task, video-based social scenarios"],
            ["F3/F4 bilateral DLPFC", "Executive flexibility", "Task-switching (card sort), computerised planning tasks, verbal fluency"],
            ["Cz/FCz", "Sensorimotor integration", "Sensory integration activities, proprioceptive exercises, tactile grading tasks"],
            ["F3 anode / F4 cathode (L-DLPFC)", "Emotional regulation", "Emotion labelling, guided mindfulness, distress tolerance exercises"],
            ["Fpz / F3", "Attention / inhibition", "Sustained attention tasks, go/no-go paradigm, verbal instruction following"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Social / Communication", "Clinically meaningful improvement in social interaction rating (PRS) + caregiver or clinician global impression"],
            ["Repetitive / Sensory", "Reduction in repetitive behaviour frequency or sensory distress rating (PRS) consistent with functional improvement"],
            ["Executive / Attention", "Improvement in executive function tasks (BRIEF or equivalent) and/or SOZO PRS executive items"],
            ["Adaptive / Functional", "Better daily living skills (caregiver-reported or clinician-observed); improved school or occupational participation"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Social Communication", "tDCS TP7/TP8 (bilateral temporoparietal anode) + TPS temporal cortex + taVNS supportive"],
            ["Restricted / Repetitive", "tDCS F3/F4 bilateral DLPFC (executive flexibility) + TPS SMA/frontal + taVNS"],
            ["Language-Dominant", "tDCS F3/T3 (left hemisphere language network) + TPS left frontal + temporal + taVNS"],
            ["Sensory", "tDCS Cz anode / Fpz cathode (sensorimotor calibration) + TPS cranial peripheral + CES supportive"],
            ["Executive", "tDCS F3/F4 bilateral DLPFC + TPS frontal targeted + taVNS supportive"],
            ["Emotional Dysregulation", "tDCS F3 anode / F4 cathode + TPS frontal + taVNS primary + CES (anxiety/sleep)"],
            ["ADHD Comorbid", "tDCS F3/F4 bilateral + Cz/FCz attention montage + TPS frontal + taVNS supportive"],
            ["Anxiety Comorbid", "tDCS F3 anode / F4 cathode + TPS frontal + taVNS primary + CES daily"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess dominant phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },

    "long_covid": {
        "slug": "long_covid",
        "cover_title": "LONG COVID / POST-COVID SYNDROME",
        "name": "Long COVID / Post-COVID Syndrome (LC)",
        "short": "Long COVID",
        "abbr": "LC",
        "med_name": "symptom-targeted medications",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Long COVID / Post-COVID Syndrome (LC). For use by the treating Doctor and "
            "authorised SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Long COVID / Post-COVID Syndrome is "
            "INVESTIGATIONAL at SOZO Brain Center. It is not CE-marked or FDA-approved for LC. All patients "
            "must provide written informed consent inclusive of the off-label TPS disclosure. TPS use is "
            "restricted to the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in Long COVID treatment. Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient-rated):",
        "prs_primary_items": [
            "Brain fog (cognitive cloudiness)",
            "Fatigue (physical and mental)",
            "Post-exertional malaise (worsening after activity)",
            "Memory difficulties (working / episodic)",
            "Concentration and sustained attention",
            "Word-finding difficulties",
            "Processing speed (mental sluggishness)",
            "Headache / head pressure",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Depression / low mood",
            "Anxiety",
            "Sleep quality",
            "Heart rate variability / palpitations",
            "Breathlessness at rest or with minimal exertion",
            "Muscle aches and pain",
            "Dizziness / orthostatic intolerance",
            "Social and occupational function",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Cognitive Fog, Fatigue-Dominant, Dysautonomia, Neuropsychiatric, "
            "Headache/Pain, Exercise Intolerance, Sleep-Dominant, Anosmia/Ageusia, or Multi-System."
        ),

        "pre_session_med_check": "☐ Record current medications (symptom-targeted agents, anticoagulants, antidepressants) — dose, timing, and adherence; note any recent symptom crashes",
        "session_med_doc": "Medication state (Long COVID symptom-targeted medications, timing of last dose, any post-exertional malaise since last session)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: Long COVID symptoms fluctuate significantly. Standardise "
            "assessment conditions between baseline and follow-up, including time of day, exertion level in the "
            "48 hours prior, and medication adherence. Post-exertional malaise episodes in the preceding week "
            "must be documented and factored into SOZO PRS interpretation."
        ),

        "inclusion_items": [
            "Confirmed Long COVID / Post-COVID Syndrome (WHO 2021 definition; symptoms ≥12 weeks post-infection)",
            "Cognitive or fatigue symptoms causing functional impairment",
            "Age 18+ years",
            "Able to attend sessions or comply with home-use protocol",
            "Written informed consent (including TPS off-label disclosure)",
            "Baseline SOZO PRS and cognitive outcome measures completed",
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
            "Severe cardiac dysrhythmia or active cardiopulmonary instability",
            "Unstable autonomic dysfunction with severe POTS or syncope",
            "Coagulation disorders or anticoagulants (especially TPS)",
            "Dermatological conditions at electrode sites",
            "Active psychosis or severe psychiatric instability",
            "Severe post-exertional malaise with inability to tolerate minimal stimulation",
        ],

        "modality_table": [
            ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Open-label, Case series", "3+"],
            ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Investigational", "0+"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked (epilepsy/depression)", "Open-label, Pilot", "3+"],
            ["CES", "Alpha-Stim\u00ae", "FDA-cleared (anxiety/insomnia/depression)", "Open-label, Observational", "3+"],
            ["TMS", "NeuroStar / MagVenture / Magstim", "CE/FDA (research use)", "Open-label, Pilot", "5+"],
        ],
        "best_modality": "CES, taVNS (emerging)",
        "offlabel_table": [
            ["Modality", "Regulatory Status", "Long COVID Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Investigational — emerging evidence for cognitive rehabilitation in LC", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Emerging — primary vagal/autonomic modulation for LC", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "Off-label supportive — anxiety, mood, and fatigue components", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Cognitive Fog", "CEN hypofunction (processing speed, working memory), DMN-CEN decoupling"],
            ["Fatigue-Dominant", "Global network energy deficit, SN sensitisation, reduced thalamo-cortical modulation"],
            ["Dysautonomia", "SN dysregulation (autonomic instability), reduced vagal tone, LIMBIC amplification"],
            ["Neuropsychiatric", "LIMBIC hyperactivation (depression/anxiety), SN threat amplification, DMN rumination"],
            ["Headache / Pain", "SN sensitisation (central sensitisation), DMN pain processing, descending inhibition failure"],
            ["Exercise Intolerance", "SMN deconditioning, SN post-exertional amplification, autonomic network disruption"],
            ["Sleep-Dominant", "SN hyperarousal (insomnia-type), LIMBIC dysregulation, circadian network disruption"],
            ["Multi-System", "Widespread network dysfunction; prioritise most disabling symptom cluster for initial FNON targeting"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["F3/F4 bilateral DLPFC", "Cognitive rehabilitation", "Graded computerised cognitive training (n-back, processing speed tasks) — low-intensity, paced"],
            ["Cz/Fz", "Fatigue and attention", "Mindfulness-based attention task, gentle breathing regulation, body scan"],
            ["F3 anode / Pz cathode", "Memory / word-finding", "Verbal fluency tasks, word association, structured recall exercises"],
            ["Fpz / F3", "Arousal modulation", "Relaxation response training, heart rate variability biofeedback (with taVNS)"],
            ["CES + taVNS (no tDCS)", "Autonomic stabilisation", "Slow breathing (5 breaths/min), parasympathetic activation protocol"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Cognitive / Brain Fog", "Clinically meaningful improvement in cognitive PRS items + objective cognitive screen (MoCA or equivalent)"],
            ["Fatigue", "Reduction in fatigue severity score (PRS) and improved post-exertional tolerance (patient-reported)"],
            ["Autonomic / Dysautonomia", "Improved heart rate variability, reduced POTS severity, reduced dizziness frequency"],
            ["Mood / Function", "Improvement in PHQ-9 / GAD-7 equivalent and return to occupational / social participation"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Cognitive Fog", "tDCS F3/F4 bilateral DLPFC (2 mA, 20 min) + TPS frontal + temporal + taVNS supportive"],
            ["Fatigue-Dominant", "tDCS Cz anode / Fpz cathode + TPS cranial + taVNS primary + CES daily (pre-session)"],
            ["Dysautonomia", "taVNS primary (vagal regulation, 2–4 h/day) + CES daily + tDCS F3/F4 supportive"],
            ["Neuropsychiatric", "tDCS F3 anode / F4 cathode (L-DLPFC up) + TPS frontal + taVNS + CES"],
            ["Headache / Pain", "tDCS M1 (C3/C4 anode) + TPS cranial + peripheral cervical + taVNS + CES"],
            ["Exercise Intolerance", "tDCS Cz/F3 graded protocol + TPS cranial + taVNS primary + CES supportive; strict session pacing"],
            ["Sleep-Dominant", "tDCS Fpz / F3 cathode (frontal inhibition) + TPS frontal + taVNS (pre-sleep) + CES primary"],
            ["Multi-System", "FNON alternating strategy: alternate cognitive and autonomic blocks per week; reassess at 4 weeks"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },

    "tinnitus": {
        "slug": "tinnitus",
        "cover_title": "TINNITUS",
        "name": "Tinnitus (Chronic)",
        "short": "Tinnitus",
        "abbr": "TIN",
        "med_name": "sound therapy / anxiolytics",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Tinnitus (Chronic). For use by the treating Doctor and authorised SOZO "
            "clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Tinnitus is INVESTIGATIONAL at SOZO Brain "
            "Center. It is not CE-marked or FDA-approved for TIN. All patients must provide written informed "
            "consent inclusive of the off-label TPS disclosure. TPS use is restricted to the prescribing "
            "Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in Tinnitus treatment. Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient-rated):",
        "prs_primary_items": [
            "Tinnitus loudness (perceived intensity)",
            "Tinnitus distress (emotional impact)",
            "Intrusiveness (interruption of daily activities)",
            "Sound sensitivity (hyperacusis / misophonia)",
            "Concentration impact",
            "Severity in quiet environments",
            "Perceived hearing difficulty",
            "Effectiveness of masking / sound therapy",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Sleep onset difficulty",
            "Sleep maintenance problems",
            "Depression / low mood",
            "Anxiety / worry",
            "Irritability",
            "Social avoidance (due to tinnitus)",
            "Work / occupational impact",
            "Ability to relax",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Tonal, Noise-Like, Pulsatile, Reactive, Somatic, Hyperacusis-Dominant, "
            "Depression Comorbid, Insomnia Comorbid, or Anxiety Comorbid."
        ),

        "pre_session_med_check": "☐ Record current medications (sound therapy devices in use, anxiolytics, antidepressants) — dose, timing; note tinnitus loudness rating for today",
        "session_med_doc": "Medication state (tinnitus-related medications and sound therapy adherence, timing of last dose)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: Tinnitus perception fluctuates with fatigue, stress, and "
            "ambient noise exposure. Standardise assessment conditions between baseline and follow-up — same "
            "time of day, same quiet environment, same rating method. Document acoustic environment changes, "
            "noise exposure events, or significant stress changes that may confound SOZO PRS comparison."
        ),

        "inclusion_items": [
            "Confirmed chronic tinnitus (duration ≥3 months; audiological assessment completed)",
            "Tinnitus causing functional distress or impairment (THI moderate or above, or PRS score ≥4)",
            "Age 18+ years",
            "Able to attend sessions or comply with home-use protocol",
            "Written informed consent (including TPS off-label disclosure)",
            "Baseline SOZO PRS and tinnitus outcome measures (THI or equivalent) completed",
        ],
        "exclusion_items": [
            "Intracranial metallic hardware in stimulation path",
            "Cochlear implant (stimulation near cochlea path — requires specialist review)",
            "Skull defects, craniectomy, or recent craniotomy",
            "Active intracranial tumour",
            "Open wounds at electrode sites",
            "Pregnancy (tDCS, TPS)",
            "Inability to provide informed consent",
        ],
        "conditional_items": [
            "Cardiac pacemaker or defibrillator",
            "Epilepsy or seizure history",
            "Active Meniere's disease or vestibular disorder (requires ENT clearance)",
            "Severe hyperacusis with inability to tolerate any environmental sound during session",
            "Coagulation disorders or anticoagulants (especially TPS)",
            "Dermatological conditions at electrode sites",
            "Active severe depression or suicidal ideation (requires psychiatric clearance first)",
            "Pulsatile tinnitus of vascular origin (requires vascular investigation before stimulation)",
        ],

        "modality_table": [
            ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Open-label", "40+"],
            ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Investigational", "0+"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked (epilepsy/depression)", "Open-label, Pilot RCT", "15+"],
            ["CES", "Alpha-Stim\u00ae", "FDA-cleared (anxiety/insomnia/depression)", "Open-label, Pilot", "0+"],
            ["TMS", "NeuroStar / MagVenture / Magstim", "CE/FDA (research use)", "RCT, Open-label", "40+"],
            ["tACS", "Starstim / NeuroConn", "CE Class IIa (research)", "Open-label, Pilot", "8+"],
            ["tRNS", "Starstim / NeuroConn", "CE Class IIa (research)", "RCT, Open-label", "15+"],
        ],
        "best_modality": "TMS (1 Hz), tDCS, tRNS",
        "offlabel_table": [
            ["Modality", "Regulatory Status", "Tinnitus Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Investigational — auditory cortex and DLPFC modulation for tinnitus suppression", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Emerging — auditory-vagal pathway modulation (paired VNS protocol)", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "Cleared for anxiety/insomnia; supportive for tinnitus distress component", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Tonal", "Primary auditory cortex hyperactivation, tonotopic map reorganisation, SN amplification"],
            ["Noise-Like", "Diffuse auditory network hyperactivation, SN-auditory overcoupling"],
            ["Pulsatile", "Vascular-auditory coupling; SN sensitisation to rhythmic input — vascular origin must be ruled out"],
            ["Reactive", "SN hyperresponsivity (sound-triggered amplification), LIMBIC-auditory coupling"],
            ["Somatic", "Somatosensory-auditory cross-modal interaction (SMN-auditory network), cervical/jaw involvement"],
            ["Hyperacusis-Dominant", "SN threshold dysregulation, central auditory gain amplification, LIMBIC threat coupling"],
            ["Depression Comorbid", "LIMBIC hyperactivation + CEN hypofunction + DMN rumination on tinnitus signal"],
            ["Insomnia Comorbid", "SN hyperarousal + LIMBIC-auditory coupling preventing sleep-onset inhibition"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["T3/TP7 cathode (L auditory cortex)", "Auditory cortex downregulation", "Sound therapy / notched music listening during stimulation"],
            ["F3 anode / T3 cathode", "Attention retraining", "Tinnitus retraining therapy (TRT) attention exercises; mindfulness of external sounds"],
            ["F3/F4 bilateral DLPFC", "Distress / emotional response", "Cognitive restructuring exercises; acceptance and commitment therapy (ACT) audio"],
            ["Fpz / F3 cathode", "Anxiety / sleep preparation", "Relaxation response training; progressive muscle relaxation; slow breathing"],
            ["taVNS + CES combined", "Auditory-vagal and arousal", "Paired VNS sound protocol (target tone presentation) + relaxation"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Loudness / Intrusiveness", "Clinically meaningful reduction in tinnitus loudness or intrusiveness (PRS) + THI score improvement"],
            ["Distress / Emotional", "Reduction in tinnitus-related distress (PRS) and improvement in emotional response to tinnitus"],
            ["Sleep", "Improvement in sleep onset latency and sleep maintenance (PRS) with reduced nocturnal tinnitus interference"],
            ["Function", "Better daily living function, reduced social avoidance, improved work performance (patient-reported)"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Tonal", "tDCS T3/TP7 cathode (L auditory cortex inhibition) + F3 anode (DLPFC up) + TPS temporal + taVNS"],
            ["Noise-Like", "tDCS T3/TP7 + F3/F4 bilateral + TPS bilateral temporal + taVNS + CES supportive"],
            ["Pulsatile", "Specialist vascular review first; if cleared: tDCS F3/F4 + TPS frontal + taVNS; avoid temporal TPS"],
            ["Reactive", "tDCS F3 anode / T3 cathode + TPS temporal (low energy) + taVNS primary + CES daily"],
            ["Somatic", "tDCS C3/C4 + Cz (somatosensory-auditory) + TPS temporal + peripheral cervical/jaw + taVNS"],
            ["Hyperacusis-Dominant", "CES primary (daily) + taVNS primary + tDCS T3 cathode / F3 anode; TPS deferred until hyperacusis reduced"],
            ["Depression Comorbid", "tDCS F3 anode / F4 cathode (L-DLPFC up) + TPS frontal + taVNS + CES daily"],
            ["Insomnia Comorbid", "tDCS Fpz cathode / F3 anode + TPS frontal + taVNS (pre-sleep) + CES primary (pre-sleep)"],
            ["No response after 8–10", "Return to FNON Level 1: Reassess phenotype → Re-map network → Adjust montage. DO NOT escalate intensity."],
        ],
    },

    "insomnia": {
        "slug": "insomnia",
        "cover_title": "CHRONIC INSOMNIA DISORDER",
        "name": "Chronic Insomnia Disorder (CID)",
        "short": "Insomnia",
        "abbr": "CID",
        "med_name": "sleep aids / melatonin",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1–5 clinical "
            "decision pathway for Chronic Insomnia Disorder (CID). For use by the treating Doctor and "
            "authorised SOZO clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH®) use in Chronic Insomnia Disorder is "
            "INVESTIGATIONAL at SOZO Brain Center. It is not CE-marked or FDA-approved for CID. All patients "
            "must provide written informed consent inclusive of the off-label TPS disclosure. TPS use is "
            "restricted to the prescribing Doctor only."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in Chronic Insomnia Disorder treatment. Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Symptoms Domain — score each relevant item on a 0–10 scale (patient-rated):",
        "prs_primary_items": [
            "Sleep onset latency (difficulty falling asleep)",
            "Night-time awakenings (number and duration)",
            "Early morning awakening (undesired early waking)",
            "Overall sleep quality (restorative value)",
            "Total sleep time (perceived hours)",
            "Daytime sleepiness (Epworth-type rating)",
            "Bedtime anxiety / pre-sleep arousal",
            "Sleep effort / trying too hard to sleep",
        ],
        "prs_secondary_label": "Secondary Symptoms Domain:",
        "prs_secondary_items": [
            "Daytime fatigue and energy level",
            "Concentration and cognitive performance",
            "Mood (irritability, low mood)",
            "Motivation and drive",
            "Physical energy",
            "Work or academic performance",
            "Social and relational function",
            "Medication dependence (sleep aids)",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Sleep-Onset, Sleep Maintenance, Early-Morning Awakening, "
            "Hyperarousal, Comorbid Psychiatric, Paradoxical Insomnia, Circadian Rhythm, Pain Comorbid, "
            "or Anxiety Comorbid."
        ),

        "pre_session_med_check": "☐ Record current sleep medications (hypnotics, melatonin, antidepressants for insomnia) — dose, timing, last administration; record previous night's sleep log",
        "session_med_doc": "Medication state (sleep medication adherence, timing of last dose, sleep diary entry for prior night)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: Sleep quality fluctuates significantly with life stressors, "
            "schedule changes, travel, and medication adjustments. Standardise baseline and follow-up assessment "
            "using a 7-day sleep diary average rather than single-night ratings. Document significant life "
            "events, schedule disruptions, or medication changes in the period before follow-up assessment."
        ),

        "inclusion_items": [
            "Confirmed chronic insomnia disorder (DSM-5 / ICSD-3; symptoms ≥3 months, ≥3 nights/week)",
            "Moderate or severe insomnia severity (ISI ≥15 or PRS primary score ≥5 average)",
            "Age 18+ years",
            "Able to attend sessions or comply with home-use protocol",
            "Written informed consent (including TPS off-label disclosure)",
            "Baseline SOZO PRS and insomnia outcome measures (ISI or equivalent) completed",
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
            "Untreated obstructive sleep apnoea (requires CPAP optimisation prior to NIBS)",
            "Severe restless legs syndrome or periodic limb movement disorder (requires specialist review)",
            "Coagulation disorders or anticoagulants (especially TPS)",
            "Dermatological conditions at electrode sites",
            "Active psychosis or bipolar disorder in manic phase",
            "Severe circadian rhythm disorder requiring specialist chronobiological management first",
        ],

        "modality_table": [
            ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Open-label", "5+"],
            ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Investigational", "0+"],
            ["taVNS", "Transcutaneous auricular VNS", "CE-marked (epilepsy/depression)", "Open-label, Pilot", "10+"],
            ["CES", "Alpha-Stim\u00ae", "FDA-cleared (anxiety/insomnia/depression)", "RCT, Meta-analysis", "25+"],
            ["TMS", "NeuroStar / MagVenture / Magstim", "CE/FDA (research use)", "RCT, Open-label", "5+"],
            ["tACS", "Starstim / NeuroConn", "CE Class IIa (research)", "RCT, Open-label", "15+"],
            ["PEMF", "Magstim / EMS Technologies", "CE/FDA (research)", "Open-label, Pilot", "5+"],
            ["tRNS", "Starstim / NeuroConn", "CE Class IIa (research)", "Open-label, Pilot", "2+"],
        ],
        "best_modality": "CES, tACS (Nexalin)",
        "offlabel_table": [
            ["Modality", "Regulatory Status", "Insomnia Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Investigational — frontal inhibition for cortical arousal reduction", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL / OFF-LABEL", "Mandatory off-label; Doctor sign-off"],
            ["taVNS", "CE-marked", "Primary adjunctive — parasympathetic activation for sleep induction", "Informed consent + evidence disclosure"],
            ["CES", "FDA-cleared", "FDA 510k cleared for insomnia — first-line SOZO modality", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Sleep-Onset", "SN hyperarousal (sleep-onset threat detection), LIMBIC anxiety amplification, CEN hyperactivation at bedtime"],
            ["Sleep Maintenance", "LIMBIC-SN mid-sleep arousal, light sleep architecture, thalamic relay dysfunction"],
            ["Early-Morning Awakening", "Circadian network disruption (early cortisol surge), LIMBIC amplification of arousal, DMN early activation"],
            ["Hyperarousal", "Global SN over-sensitisation, CEN hyperactivation (cognitive hyperarousal), DMN rumination loop"],
            ["Comorbid Psychiatric", "LIMBIC hyperactivity (depression/anxiety driving insomnia), SN-LIMBIC overcoupling"],
            ["Paradoxical Insomnia", "SN misperception of sleep state, CEN-DMN boundary failure, cortical arousal during objective sleep"],
            ["Circadian Rhythm", "Circadian network phase disruption, ATTENTION dysregulation, SN temporal mismatch"],
            ["Pain Comorbid", "SN sensitisation (pain-arousal coupling), LIMBIC amplification, descending inhibition failure during sleep"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["Fpz cathode / F3 cathode (frontal inhibition)", "Cortical arousal reduction", "Progressive muscle relaxation audio, body scan, guided sleep restriction therapy"],
            ["F3/F4 bilateral DLPFC (low intensity)", "Cognitive deactivation", "Sleep psychoeducation review, stimulus control instructions, sleep diary completion"],
            ["Fz cathode / Cz (midline inhibition)", "Hyperarousal", "4-7-8 breathing protocol, heart rate variability biofeedback"],
            ["CES (pre-sleep, 60 min before bed)", "Sleep induction", "Dim-light reading, no screens, cool environment — CES as sleep pre-conditioning"],
            ["taVNS (evening, 30 min)", "Parasympathetic activation", "Slow breathing (5 breaths/min), audio-guided relaxation, progressive muscle relaxation"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["Sleep Quality", "Clinically meaningful improvement in overall sleep quality (PRS + ISI or equivalent ≥6 point reduction)"],
            ["Sleep Continuity", "Reduction in sleep onset latency and/or night-time awakenings (PRS items + sleep diary average)"],
            ["Daytime Function", "Improvement in daytime fatigue, concentration, and mood (PRS secondary items, patient-reported)"],
            ["Hyperarousal / Anxiety", "Reduction in pre-sleep arousal, bedtime anxiety, and sleep effort (PRS items)"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Sleep-Onset", "CES primary (daily, pre-sleep) + taVNS (evening) + tDCS Fpz/F3 cathode + TPS frontal"],
            ["Sleep Maintenance", "CES primary + taVNS (evening) + tDCS Fz cathode / Cz + TPS frontal supportive"],
            ["Early-Morning Awakening", "tDCS Fpz cathode + CES (mid-night protocol if tolerated) + taVNS (evening) + TPS frontal"],
            ["Hyperarousal", "CES primary (daily) + taVNS primary + tDCS F3/F4 cathode bilateral + TPS frontal (inhibitory protocol)"],
            ["Comorbid Psychiatric", "tDCS F3 anode / F4 cathode (antidepressant montage) + CES + taVNS + TPS frontal"],
            ["Paradoxical Insomnia", "CES primary + taVNS + tDCS Fpz cathode; avoid high-intensity tDCS; prioritise arousal perception retraining"],
            ["Circadian Rhythm", "taVNS timed to target circadian phase shift + CES + tDCS Fz/Cz; coordinate with light therapy schedule"],
            ["Pain Comorbid", "tDCS M1/C3 anode (descending inhibition) + TPS peripheral (pain sites) + CES + taVNS (pain + sleep)"],
            ["No response after 8\u201310", "Return to FNON Level 1: Reassess phenotype \u2192 Re-map network \u2192 Adjust montage. DO NOT escalate intensity."],
        ],
    },

    "parkinsons": {
        "slug": "parkinsons",
        "cover_title": "PARKINSON'S DISEASE",
        "name": "Parkinson's Disease",
        "short": "Parkinson's",
        "abbr": "PD",
        "med_name": "levodopa / dopamine agonists",

        "partners_tier_body": (
            "PARTNERS TIER: This document contains the complete FNON framework including network hypothesis "
            "generation, 6-Network Bedside Assessment, S-O-Z-O sequencing, and full FNON Level 1\u20135 clinical "
            "decision pathway for Parkinson\u2019s Disease. For use by the treating Doctor and authorised SOZO "
            "clinical staff only."
        ),
        "tps_offlabel_body": (
            "WARNING: Off-Label Disclosure: TPS (NEUROLITH\u00ae) use in Parkinson\u2019s Disease is "
            "INVESTIGATIONAL at SOZO Brain Center. It is not CE-marked or FDA-approved for PD. All patients "
            "must provide written informed consent inclusive of the off-label TPS disclosure. TPS use is "
            "restricted to the prescribing Doctor only. NEUROLITH\u00ae 4 Hz, 0.25 mJ/mm\u00b2, 10,000 pulses; "
            "targets M1 + SMA + DLPFC over 25\u201330 min/session, 12 sessions/4 weeks."
        ),
        "mandatory_consent_body": (
            "WARNING: MANDATORY: No diagnostic or therapeutic procedures may be performed prior to informed "
            "consent being obtained. This includes the off-label disclosure for all investigational modalities "
            "used in Parkinson\u2019s Disease treatment. DBS patients: TPS is ABSOLUTELY CONTRAINDICATED. "
            "Non-compliance is a clinical governance violation."
        ),

        "prs_primary_label": "Primary Motor Symptoms Domain \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
        "prs_primary_items": [
            "Tremor severity (resting tremor)",
            "Rigidity (muscle stiffness)",
            "Bradykinesia (slowness of movement)",
            "Gait difficulty / freezing of gait",
            "Postural instability / balance impairment",
            "Fine motor tasks (writing, buttoning, grip)",
            "Falls frequency",
            "Dysarthria / speech difficulty",
        ],
        "prs_secondary_label": "Non-Motor Symptoms Domain:",
        "prs_secondary_items": [
            "Cognitive impairment / memory",
            "Depression / low mood",
            "Anxiety",
            "Sleep disturbance (insomnia / RBD)",
            "Fatigue",
            "Autonomic symptoms (orthostasis, constipation)",
            "Apathy / motivation loss",
            "Pain / sensory symptoms",
        ],

        "phenotype_prelim": (
            "Assign a preliminary phenotype: Motor Predominant (Tremor/Rigidity/Bradykinesia), "
            "Cognitive/MCI Predominant, Autonomic Predominant, Depression Comorbid, "
            "Freezing of Gait, or Advanced PD (H&Y 4-5)."
        ),

        "pre_session_med_check": "\u2610 Record current PD medications (levodopa dose, dopamine agonist, timing; last dose; document ON/OFF state at session start)",
        "session_med_doc": "PD medication state (levodopa/dopamine agonist dose and timing; ON/OFF state at session; wearing-off status)",

        "false_class_body": (
            "WARNING: AVOIDING FALSE CLASSIFICATION: UPDRS-III motor scores vary significantly with "
            "levodopa ON/OFF state. Always assess in the same medication state (ideally defined ON state: "
            "60\u201390 minutes post-levodopa). Document levodopa dose, timing, and time since last dose at "
            "every assessment. Morning assessments at a consistent time avoid diurnal fluctuation. "
            "Assess in the same room and same movement conditions between baseline and follow-up."
        ),

        "inclusion_items": [
            "Confirmed diagnosis of Parkinson\u2019s Disease (UK Brain Bank or MDS diagnostic criteria)",
            "H&Y Stage 1\u20133 (ambulatory with or without assistance)",
            "Stable PD medication regimen for \u22654 weeks",
            "UPDRS-III \u226515 at baseline (motor symptoms warrant intervention)",
            "Age 40\u201385; capable of informed consent (or supported consent with carer)",
            "No active DBS implant (absolute TPS contraindication)",
            "Written informed consent including TPS off-label disclosure",
            "Baseline SOZO PRS and UPDRS-III, MoCA completed",
        ],
        "exclusion_items": [
            "Active deep brain stimulator (DBS) \u2014 ABSOLUTE contraindication to TPS",
            "Metallic implants in head/neck stimulation field",
            "Cardiac pacemaker or ICD",
            "Active psychosis or dopamine dysregulation syndrome",
            "H&Y Stage 5 (bed/wheelchair-bound) without caregiver-supported protocol",
            "Pregnancy",
            "Recent neurosurgical procedure or skull defect over target area",
            "Inability to tolerate stimulation or cooperate with protocol",
        ],
        "conditional_items": [
            "Levodopa wearing-off: assess in defined ON state; document timing precisely",
            "Cognitive impairment (MoCA <21): supported consent; caregiver present; simplified protocol",
            "Orthostatic hypotension: seated or supine session; blood pressure monitoring pre/post",
            "REM Sleep Behaviour Disorder: CES evening; sleep specialist concurrent",
            "Comorbid essential tremor: clarify PD vs ET component; differentiated protocol",
            "Impulse control disorder: psychiatry input; monitor on dopamine agonist",
            "Severe dysarthria: speech therapy concurrent; AAC support for cognitive tasks",
            "Elderly (\u226575): reduce tDCS intensity (1\u20131.5 mA); shorter sessions; fall risk assessment",
        ],

        "modality_table": [
            ["Modality", "Device", "Regulatory", "Evidence Level", "Papers (est.)"],
            ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "RCT, Meta-analysis", "50+"],
            ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa \u2014 INVESTIGATIONAL OFF-LABEL", "Pilot RCT, Open-label", "5+"],
            ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Open-label, Pilot", "10+"],
            ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Open-label, Pilot", "5+"],
            ["TMS", "NeuroStar / MagVenture", "CE/FDA (research use)", "RCT, Meta-analysis", "60+"],
            ["DBS", "Medtronic / Abbott", "FDA-cleared for PD", "Gold Standard RCT", "500+"],
        ],
        "best_modality": "tDCS (M1 anodal), TMS (rTMS M1/DLPFC)",
        "offlabel_table": [
            ["Modality", "Regulatory Status", "PD Classification", "Disclosure Required"],
            ["tDCS", "CE Class IIa", "Level B evidence; M1 anodal motor facilitation for PD established", "Standard informed consent"],
            ["TPS", "CE Class IIa", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
            ["taVNS", "CE-marked (epilepsy/depression)", "Emerging for PD autonomic and motor symptoms", "Standard informed consent + evidence disclosure"],
            ["CES", "FDA-cleared (anxiety/depression/insomnia)", "Supportive for PD depression, anxiety, sleep", "Standard informed consent"],
        ],
        "phenotype_table": [
            ["Phenotype", "Key Features (Network Basis)"],
            ["Motor Predominant", "Tremor, rigidity, bradykinesia; M1+SMA hypoactivation; beta-band excess in BG-thalamic circuit"],
            ["Cognitive / MCI", "MoCA <26; DLPFC-PPC Executive Control Network hypoactivation; DMN disrupted PD-MCI"],
            ["Autonomic Predominant", "Orthostatic hypotension, POTS, constipation; brainstem-vagal circuit degeneration (Lewy body stage 1-2)"],
            ["Depression Comorbid", "PHQ-9 \u226510; L-DLPFC hypoactivation; LIMBIC-motor overlap; high in PD (30\u201340%)"],
            ["Freezing of Gait", "FoG-Q >7; SMA-basal ganglia circuit failure; cueing-responsive; high fall risk"],
            ["Tremor Predominant", "Resting tremor dominant; cerebellar-thalamic circuit; bilateral M1 tDCS; DBS if refractory"],
            ["Advanced PD (H&Y 4-5)", "Severe bilateral disability; limited ambulatory; CES+taVNS primary; tDCS low-intensity; caregiver-supported"],
        ],
        "task_pairing_table": [
            ["Montage Target", "Domain", "Concurrent Task"],
            ["M1 bilateral (C3/C4 anodal)", "Motor facilitation", "Gait training, balance exercises, physiotherapy during tDCS for motor cortex priming"],
            ["DLPFC (F3/F4 anodal)", "Cognitive-motor", "Dual-task gait, N-back, verbal fluency during tDCS for executive-motor integration"],
            ["SMA (Cz anodal)", "Gait initiation", "Rhythmic Auditory Stimulation (RAS), cueing gait training concurrent with stimulation"],
            ["taVNS extended (40 min)", "Autonomic / neuroprotective", "HRV biofeedback, paced breathing (6 cpm), orthostatic training, relaxation"],
            ["CES (Alpha-Stim)", "Sleep / mood / anxiety", "PD anxiety management; sleep hygiene; caregiver communication support"],
        ],
        "response_domains_table": [
            ["Domain", "Response Criteria"],
            ["UPDRS-III (Primary)", "MCID \u22652.3 points reduction; \u226520% improvement in motor score = clinical response"],
            ["MoCA (Cognitive)", "Stable or improved MoCA (\u22651 point) over treatment block; prevent cognitive decline"],
            ["PDQ-39 (QoL)", "MCID \u22654.2 point SI reduction; clinically meaningful QoL improvement"],
            ["PHQ-9 / GAD-7 (Mood)", "\u226550% reduction = response; score \u22644 = remission of PD depression/anxiety"],
            ["FoG-Q (Gait)", "\u22653-point reduction = clinical improvement in freezing; TUG \u226520% faster"],
        ],
        "montage_table": [
            ["Phenotype", "SOZO Device & Network Strategy"],
            ["Motor Predominant", "tDCS M1 bilateral (C3/C4 anodal 2\u202fmA) + TPS M1+SMA (4\u202fHz, 10,000 pulses, 0.25\u202fmJ/mm\u00b2) + taVNS 30min + physiotherapy"],
            ["Cognitive / MCI", "tDCS DLPFC bilateral (F3/F4 anodal 2\u202fmA) + TPS DLPFC (4\u202fHz, 1,000 pulses) + taVNS 30min + cognitive rehab"],
            ["Autonomic Predominant", "taVNS 40min primary + CES daily + tDCS M1 (1.5\u202fmA); TPS deferred until autonomic stable"],
            ["Depression Comorbid", "tDCS L-DLPFC (F3 anodal 2\u202fmA) + TPS DLPFC L (4\u202fHz, 800 pulses) + taVNS 30min + CES daily"],
            ["Freezing of Gait", "tDCS SMA (Cz anodal 2\u202fmA) + DLPFC + TPS M1+SMA (4\u202fHz, 10,000 pulses) + RAS gait training"],
            ["Tremor Predominant", "tDCS M1 bilateral (C3/C4 1.5\u202fmA) + TPS M1 bilateral (4\u202fHz, 800 pulses) + taVNS 30min"],
            ["Advanced PD (H&Y 4-5)", "CES primary (daily) + taVNS 20min + tDCS DLPFC (1\u202fmA, 15\u202fmin); TPS deferred"],
            ["No response after 8\u201310", "Return to FNON Level 1: Reassess phenotype \u2192 Confirm ON state assessment \u2192 Re-map network. DO NOT escalate intensity."],
        ],
    },
}
