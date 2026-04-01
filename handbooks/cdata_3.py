"""Condition data: OCD, MS, ASD, Long COVID, Tinnitus, Insomnia"""

CDATA = {}

# ─── OCD ──────────────────────────────────────────────────────────────────────
CDATA["ocd"] = dict(
    slug="ocd", cover_title="OBSESSIVE-COMPULSIVE DISORDER (OCD)",
    name="Obsessive-Compulsive Disorder (OCD)", short="OCD", abbr="OCD",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in OCD is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not currently extend to OCD. Mandatory off-label disclosure and Doctor "
        "sign-off are required before TPS treatment for OCD."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for OCD requires specific, documented off-label disclosure with Doctor sign-off. "
        "NIBS is used as augmentation to ERP (Exposure and Response Prevention) therapy, not as monotherapy."
    ),
    prs_domain_label="OCD Symptom Dimensions",
    prs_domain_header_line="OCD Symptom Dimensions \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
    exam_step_heading="4.1 OCD Clinical & Psychiatric Examination",
    exam_step_desc=(
        "Conduct a systematic OCD examination using the Clinical Examination Checklist. "
        "Rate obsession and compulsion severity across dimensions; assess insight and functional impairment:"
    ),
    exam_checklist_item="\u2610 OCD clinical examination completed (Y-BOCS administered; insight rated; compulsion domains documented)",
    med_check_item="Record SSRI/clomipramine compliance (last dose and current dose; any recent changes)",
    session_med_doc="medication compliance (SSRI/clomipramine dose; any dose changes; timing)",
    false_class_body=(
        "Standardise OCD assessment conditions between baseline and follow-up. Y-BOCS scores can "
        "fluctuate with stress and recent exposures. Ensure assessments are conducted in a consistent "
        "clinical setting with the same clinician-administered format to avoid false responder or "
        "false non-responder classification."
    ),
    modality_table=[
        ["Modality", "Device", "Classification", "OCD Evidence Status"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Level B evidence (SMA cathodal/DLPFC anodal; Narayanan 2016)"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL \u2014 OFF-LABEL for OCD"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Level C (serotonergic augmentation; anxiety reduction)"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Level B evidence (anxiety augmentation; SSRI adjunct)"],
    ],
    offlabel_table=[
        ["Modality", "Regulatory Status", "OCD Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Level B evidence; SMA cathodal + DLPFC anodal established", "Standard informed consent"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Level C; serotonergic augmentation mechanism", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety)", "Level B; anxiety/OCD symptom augmentation", "Standard informed consent"],
    ],
    prs_table=[
        ["Obsession Symptoms (0\u201310)", "Compulsion Symptoms (0\u201310)"],
        ["Contamination obsessions (germs, disease)", "Washing / cleaning rituals"],
        ["Harm obsessions (fear of harming self/others)", "Checking compulsions (locks, appliances, doors)"],
        ["Symmetry / exactness obsessions", "Ordering / arranging rituals"],
        ["Intrusive thoughts (taboo, sexual, religious)", "Mental rituals / counting / praying"],
        ["Doubt / uncertainty intolerance", "Reassurance seeking"],
        ["Unwanted aggressive images", "Hoarding / difficulty discarding (OCD-type)"],
        ["Time consumed by obsessions (hrs/day)", "Time consumed by compulsions (hrs/day)"],
        ["Overall OCD-related distress / avoidance", "Overall OCD-related functional impairment"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["Y-BOCS Obsession Subscale", "Yale-Brown OCS \u2014 Obsession items (5 items)", "0\u201320; \u22658 = mild; \u226516 = moderate-severe"],
        ["Y-BOCS Compulsion Subscale", "Yale-Brown OCS \u2014 Compulsion items (5 items)", "0\u201320; \u22658 = mild; \u226516 = moderate-severe"],
        ["OCD Dimension Assessment", "Symptom checklist by dimension (contamination, harm, symmetry, intrusive)", "Document primary + secondary dimensions"],
        ["Insight Assessment", "CGI-S insight rating; BABS (Brown Assessment of Beliefs)", "BABS total; CGI severity"],
        ["Mood & Anxiety Comorbidity", "PHQ-9; GAD-7; YBOCS total impact", "Standard thresholds + OCD interaction"],
        ["Functional Impairment", "CGI-S; WHODAS 2.0 functional domains", "CGI 1\u20137; WHODAS total"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["Y-BOCS Total (Yale-Brown Obsessive Compulsive Scale)", "___ / 40", "\u22648 = subclinical; 8\u201315 = mild; 16\u201323 = moderate; \u226524 = severe"],
        ["Y-BOCS Obsession Subscale", "___ / 20", "\u226516 = severe; MCID = \u226535% reduction"],
        ["Y-BOCS Compulsion Subscale", "___ / 20", "\u226516 = severe; MCID = \u226535% reduction"],
        ["CGI-S (Clinical Global Impressions Severity)", "___ / 7", "\u22654 = moderately ill; \u22666 = severely ill; \u22662 = much improved"],
        ["PHQ-9 (Depression comorbidity)", "___ / 27", "\u226510 = comorbid depression (50% OCD comorbidity)"],
        ["GAD-7 (Anxiety comorbidity)", "___ / 21", "\u226510 = comorbid anxiety"],
        ["OCI-R (OCD Inventory \u2014 Revised)", "___ / 72", ">21 = OCD probable; subscales for dimensional assessment"],
        ["BABS (Insight)", "___ / 24", ">18 = poor insight; >24 = absent insight (delusional)"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Contamination / Washing", "Contamination obsessions + washing compulsions; disgust-driven OFC-insula circuit; skin damage from washing"],
        ["Harm / Checking", "Harm obsessions + checking compulsions; dACC hyperactivity; doubt; guilt; excessive responsibility"],
        ["Symmetry / Ordering", "Symmetry obsessions + ordering compulsions; \u2018just-right\u2019 phenomenology; sensorimotor CSTC involvement"],
        ["Intrusive Thought Dominant", "Taboo/moral/sexual/violent intrusive thoughts; mental neutralising; ACC-DLPFC dysfunction"],
        ["Treatment-Refractory OCD", "\u22653 SSRI failures + ERP failure; severe CSTC pathology; all 4 modalities + intensive ERP"],
        ["OCD + Tic Comorbidity", "OCD + Tourette/chronic tics; SMA-striatal circuit predominance; specialised combined protocol"],
        ["OCD with Poor Insight", "Limited awareness of irrationality; BABS >18; delusional OCD: antipsychotic + NIBS"],
        ["Hoarding Disorder (OCD-spectrum)", "Pathological saving; ego-syntonic features; separate CBT backbone; DLPFC + OFC targeting"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["SMA Cathodal (Cz)", "Compulsion Inhibition", "ERP response prevention exercises; habit reversal training; urge surfing during compulsion urge"],
        ["L-DLPFC (F3)", "Top-Down OFC Regulation", "Cognitive defusion from obsessions; CPT-style thought challenging; insight-building exercises"],
        ["OFC (TPS)", "Error Signal Reduction", "Uncertainty tolerance exercises; contamination hierarchy exposures; ERP concurrent"],
        ["taVNS", "Serotonergic Augmentation", "Paced breathing; mindfulness of OCD thoughts; vagal activation before ERP exposure"],
        ["CES (Alpha-Stim)", "Anxiety / SSRI Augmentation", "Anxiety reduction before ERP; sleep hygiene for OCD sleep problems; relaxation between exposures"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["Y-BOCS Total (Primary)", "\u226535% reduction = Response; score \u22647 = Remission; 25\u201334% = Partial"],
        ["Y-BOCS Obsession Subscale", "\u226535% reduction; score \u22643 = subscale remission"],
        ["Y-BOCS Compulsion Subscale", "\u226535% reduction; score \u22643 = subscale remission"],
        ["CGI-S", "CGI-S \u22662 (much improved) = global response; CGI-S 1 = remission"],
        ["PHQ-9 / GAD-7 (comorbidity)", "\u226550% reduction in comorbid depression/anxiety"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "DSM-5 OCD diagnosis confirmed by structured interview (Y-BOCS \u226516)"],
        ["2", "Significant functional impairment (CGI-S \u22654); symptoms \u22656 months"],
        ["3", "Age 18\u201370; capable of informed consent"],
        ["4", "Inadequate response to \u22652 adequate SSRI trials (\u226512 weeks each) or prior ERP failure"],
        ["5", "Stable medication for \u22658 weeks prior to enrolment"],
        ["6", "Willing to maintain concurrent ERP throughout NIBS protocol"],
        ["7", "No planned SSRI dose changes for \u22658 weeks after enrolment"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Active suicidality requiring hospitalisation"],
        ["2", "Metallic implants in head/neck stimulation field"],
        ["3", "Cardiac pacemaker or ICD (CES / taVNS contraindication)"],
        ["4", "Pregnancy"],
        ["5", "Active psychosis or bipolar disorder (manic phase)"],
        ["6", "Prior DBS or ablative neurosurgery for OCD"],
        ["7", "Uncontrolled epilepsy or seizure disorder"],
        ["8", "Hoarding disorder as sole presentation without classic OCD circuitry involvement"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Poor insight / delusional OCD", "Antipsychotic augmentation required; NIBS role reduced; specialist assessment"],
        ["OCD + Tic disorder (Tourette)", "SMA cathodal primary; specialised tic management concurrent; lower intensities"],
        ["OCD + depression (PHQ-9 >14)", "DLPFC anodal antidepressant addition; taVNS + CES expanded role"],
        ["OCD + autism (ASD comorbidity)", "Adapted ERP with ABA support; lower NIBS intensities; social communication support"],
        ["OCD + eating disorder", "Specialist eating disorder team concurrent; body image NIBS considerations"],
        ["Paediatric OCD (18\u201321 years)", "Parental involvement; lower intensities; adapted ERP (CBT-OCD)"],
        ["Contamination OCD with skin damage", "Dermatology input; wound assessment before electrode placement"],
        ["Religious scrupulosity OCD", "Culturally competent ERP; religious leader involvement; chaplain referral option"],
        ["Cardiac history", "CES/taVNS: ECG and cardiac clearance required"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Contamination / Washing", "Cathodal SMA (Cz 1.5\u202fmA) + Anodal DLPFC (F3 2\u202fmA)", "OFC: 250 pulses, 0.2\u202fHz", "taVNS before ERP; CES anxiety augment"],
        ["Harm / Checking", "Cathodal SMA (Cz 1.5\u202fmA) + Anodal DLPFC (F3)", "ACC: 250 pulses, 0.2\u202fHz", "taVNS + CES; ERP concurrent essential"],
        ["Symmetry / Ordering", "Cathodal SMA (Cz 1.5\u202fmA)", "SMA + OFC: 300 pulses", "CES anxiolytic; ERP concurrent"],
        ["Intrusive Thought", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "ACC: 250 pulses", "taVNS serotonergic; ERP essential"],
        ["Refractory OCD", "Cathodal SMA + Anodal DLPFC bilateral 2\u202fmA", "OFC + ACC: 400 pulses", "All 4 modalities + intensive ERP"],
        ["OCD + Tics", "Cathodal SMA (Cz 1.5\u202fmA)", "SMA: 200 pulses", "CES + taVNS; tic management concurrent"],
        ["OCD + Depression", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "ACC + OFC: 250 pulses", "taVNS + CES nightly; SSRI maintained"],
        ["Maintenance", "Anodal L-DLPFC (F3) 1.5\u202fmA 2\u00d7/week", "None", "CES 3\u00d7/week; taVNS daily home"],
    ],
)

# ─── MS ───────────────────────────────────────────────────────────────────────
CDATA["ms"] = dict(
    slug="ms", cover_title="MULTIPLE SCLEROSIS (MS)",
    name="Multiple Sclerosis (MS)", short="MS", abbr="MS",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in Multiple Sclerosis is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not currently extend to MS symptom management. Mandatory off-label "
        "disclosure and Doctor sign-off are required before TPS treatment for MS."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for MS requires specific, documented off-label disclosure with Doctor sign-off. "
        "NIBS addresses symptom burden only \u2014 disease modification requires separate DMT management."
    ),
    prs_domain_label="MS Symptom Domains",
    prs_domain_header_line="MS Symptom Domains \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
    exam_step_heading="4.1 MS Neurological & Functional Examination",
    exam_step_desc=(
        "Conduct a systematic MS neurological and functional examination using the Clinical Examination Checklist. "
        "Score each domain; integrate with EDSS and MS-specific functional measures:"
    ),
    exam_checklist_item="\u2610 MS neurological & functional examination completed (EDSS estimated; all symptom domains assessed)",
    med_check_item="Record DMT compliance and last dose (interferons, ocrelizumab, siponimod etc.); note any recent relapse",
    session_med_doc="DMT compliance (disease-modifying therapy name and adherence); symptom medications (baclofen, modafinil etc.)",
    false_class_body=(
        "Standardise MS symptom assessment conditions between baseline and follow-up. MS symptoms "
        "fluctuate significantly with heat (Uhthoff phenomenon), fatigue, and relapses. Ensure assessments "
        "occur at the same time of day, at comparable temperature and exertion levels, and document "
        "relapse-free status to avoid false responder or false non-responder classification."
    ),
    modality_table=[
        ["Modality", "Device", "Classification", "MS Evidence Status"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Level B evidence (fatigue/motor/cognitive; Mattioli 2010; Fregni 2006)"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL \u2014 OFF-LABEL for MS"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Level C (anti-inflammatory; neuroinflammation; Tracey 2002)"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Level C (fatigue/sleep/mood in MS; Yusupov 2019)"],
    ],
    offlabel_table=[
        ["Modality", "Regulatory Status", "MS Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Level B evidence; fatigue and motor/cognitive protocols established", "Standard informed consent"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Level C; anti-inflammatory mechanism in autoimmune conditions", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety/depression/insomnia)", "Level C; fatigue/sleep/mood in MS comorbidities", "Standard informed consent"],
    ],
    prs_table=[
        ["MS Motor & Sensory Symptoms (0\u201310)", "MS Cognitive & Psychological Symptoms (0\u201310)"],
        ["Fatigue (MS-specific; MFIS-rated)", "Cognitive fog / processing speed reduction"],
        ["Spasticity / muscle stiffness", "Memory difficulty (working / episodic)"],
        ["Weakness (upper / lower limb)", "Depression / low mood (NPI)"],
        ["Gait impairment / balance problems", "Anxiety / worry"],
        ["Neuropathic pain (burning, electric)", "Sleep disturbance (insomnia)"],
        ["Tremor / incoordination", "Bladder / bowel dysfunction impact"],
        ["Sensory symptoms (numbness, tingling)", "Social/occupational participation"],
        ["Visual disturbance (ON-related)", "Overall quality of life (MSIS-29)"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["EDSS Estimate", "Functional system scores (pyramidal, cerebellar, brainstem, sensory, visual, bladder, cerebral)", "EDSS 0\u201310 (0.5 steps)"],
        ["Motor Function (Pyramidal)", "Grip strength; Timed 25-Foot Walk (T25FW); MAS spasticity", "T25FW seconds; MAS 0\u20134"],
        ["Upper Limb Dexterity", "9-Hole Peg Test (9HPT); dominant/non-dominant hand", "Time in seconds; MCID \u226520%"],
        ["Cognitive Screen", "Symbol Digit Modalities Test (SDMT); MoCA; BRB-N", "SDMT score; MoCA total"],
        ["Fatigue Assessment", "MFIS (Modified Fatigue Impact Scale); FSS", "MFIS total 0\u201384; FSS 1\u20137"],
        ["Mood Assessment", "PHQ-9; GAD-7; MSIS-29 psychological subscale", "Standard thresholds"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["MFIS (Modified Fatigue Impact Scale)", "___ / 84", "\u226538 = clinically significant MS fatigue (primary outcome)"],
        ["SDMT (Symbol Digit Modalities Test)", "___ raw", "<55 = cognitive impairment in MS; MCID = \u22654 points"],
        ["Timed 25-Foot Walk (T25FW)", "___ seconds", "MCID = 20% improvement; >5\u202fs = abnormal"],
        ["9-Hole Peg Test (9HPT)", "___ seconds", "MCID = 20% improvement in dominant hand"],
        ["PHQ-9 (MS depression)", "___ / 27", "\u226510 = clinically significant (50% MS comorbidity)"],
        ["MoCA (Cognitive screen)", "___ / 30", "<26 = post-MS cognitive impairment; <24 = significant"],
        ["EDSS (Expanded Disability Status Scale)", "0\u201310", "2\u20137 = eligible for SOZO protocol; >7 with Doctor approval"],
        ["PSQI (Sleep quality)", "___ / 21", ">5 = MS-related sleep disturbance"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Fatigue-Dominant", "Severe MS fatigue (MFIS \u226538); thalamocortical and cortico-striatal inefficiency; limits daily function"],
        ["Cognitive-Dominant", "Processing speed, working memory, attention impairment (SDMT <45); cognitive fog; occupational impairment"],
        ["Spasticity-Dominant", "Moderate-severe spasticity (MAS 2\u20133); corticospinal demyelination; gait limitation; pain from spasticity"],
        ["Pain-Dominant", "Central neuropathic pain \u22654/10 NRS; trigeminal neuralgia; Lhermitte sign; central sensitisation features"],
        ["Mood / Depression-Dominant", "MS-related depression (PHQ-9 \u226510); partly neuroinflammatory; reduced adherence; fatigue-depression interaction"],
        ["RRMS Active Symptoms", "Relapsing-remitting MS; active symptom burden between relapses; broad symptomatic NIBS approach"],
        ["SPMS / PPMS Progressive", "Progressive MS; plateau in DMT benefit; symptom maintenance focus; conservative NIBS intensities"],
        ["Mixed Fatigue + Cognitive", "Both MFIS \u226538 and SDMT <45; most common complex phenotype; combined DLPFC + M1 protocol"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["M1 (C3/C4)", "Motor / Spasticity / Fatigue", "Upper/lower limb exercises; stretching programme; gait training; physiotherapy concurrent"],
        ["L-DLPFC (F3)", "Cognitive / Mood / Fatigue", "Computerised cognitive training (SDMT practice); attention tasks; behavioural activation"],
        ["M1 + SMA (TPS)", "Motor Sequence / Coordination", "Repetitive motor tasks; gait training; fatigue-paced exercise protocol"],
        ["taVNS", "Anti-Inflammatory / Mood / Fatigue", "Paced breathing; mindfulness; rest and anti-fatigue strategies during taVNS"],
        ["CES (Alpha-Stim)", "Sleep / Fatigue / Mood", "Fatigue management education; energy conservation strategies; sleep hygiene for MS"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["MFIS (Fatigue \u2014 Primary)", "MCID \u22655-point reduction; \u226538 = clinically significant fatigue persisting"],
        ["SDMT (Cognitive)", "MCID \u22654-point improvement; >55 = normalisation of processing speed"],
        ["T25FW (Gait)", "MCID 20% improvement; or absolute reduction \u22651 second"],
        ["PHQ-9 (Depression)", "\u226550% reduction = response; score \u22644 = remission"],
        ["MAS (Spasticity)", "\u22661-point MAS reduction on the most affected limb segment"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "Confirmed MS diagnosis per McDonald 2017 criteria (RRMS, SPMS, or PPMS)"],
        ["2", "EDSS score 2.0\u20137.0 at baseline"],
        ["3", "Stable DMT for \u22653 months (or no DMT planned)"],
        ["4", "Age 18\u201370; capable of informed consent"],
        ["5", "Symptom burden: MFIS \u226538, SDMT <55, spasticity MAS \u22652, or PHQ-9 \u226510"],
        ["6", "No MS relapse within 3 months of enrolment"],
        ["7", "No planned DMT change for \u22668 weeks after enrolment"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Active MS relapse or corticosteroid treatment within 3 months"],
        ["2", "Metallic implants in head/neck stimulation field"],
        ["3", "Cardiac pacemaker or ICD (CES / taVNS contraindication)"],
        ["4", "Pregnancy"],
        ["5", "Severe cognitive impairment precluding consent (MMSE <18)"],
        ["6", "Rapidly progressive disease course (EDSS change >1.0 in past 6 months)"],
        ["7", "Active cancer or severe systemic illness"],
        ["8", "EDSS >7.0 without Doctor approval and specialist neurorehabilitation"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Uhthoff\u2019s phenomenon (heat sensitivity)", "Air-conditioned session room; cooling measures; hydration; shorter initial sessions"],
        ["High EDSS (5\u20137)", "Wheelchair-accessible setup; lower intensities; carer involvement; adapted home use"],
        ["Cognitive impairment (SDMT <45)", "Simplified home training protocol; caregiver involvement; adapted instruction"],
        ["Trigeminal neuralgia comorbidity", "TPS caution near trigeminal territory; specialist pain input"],
        ["Depression + fatigue interaction", "Treat depression concurrently; distinguish fatigue from depression clinically"],
        ["Bladder dysfunction", "Session timing around bladder management programme; continence nurse referral"],
        ["Progressive MS (SPMS/PPMS)", "Lower expectations for improvement; maintenance framing; conservative protocol"],
        ["Optic neuritis history", "Visual acuity monitoring; ophthalmology concurrent; CES caution near eyes"],
        ["Pregnancy (during course)", "Halt NIBS immediately; document; neurology referral for MS management in pregnancy"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Fatigue-Dominant", "Anodal M1 (C3 2\u202fmA) + Anodal DLPFC (F3 2\u202fmA) sequential", "None initial", "CES nightly 60min; taVNS 2\u00d7 daily"],
        ["Cognitive-Dominant", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "DLPFC BA46: 250 pulses, 0.2\u202fHz", "taVNS before session; CES adjunct"],
        ["Spasticity-Dominant", "Anodal M1 (C3/C4) 2\u202fmA 20\u202fmin", "M1/SMA: 300 pulses, 0.25\u202fHz", "Baclofen maintained; physiotherapy concurrent"],
        ["Pain-Dominant", "Anodal M1 (C3) 2\u202fmA 20\u202fmin", "ACC: 250 pulses", "CES nightly 60min; taVNS 2\u00d7 daily"],
        ["Mood / Depression", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "None initial", "taVNS + CES nightly; DMT maintained"],
        ["RRMS Active", "Anodal DLPFC (F3) + M1 (C3) sequential 2\u202fmA each", "DLPFC + M1: 300 pulses", "taVNS + CES; DMT maintained"],
        ["SPMS / PPMS", "Anodal M1 (C3) 1.5\u202fmA 20\u202fmin", "M1: 200 pulses (lower)", "CES primary; taVNS 2\u00d7 daily"],
        ["Maintenance", "Anodal DLPFC/M1 1.5\u202fmA 20\u202fmin 2\u00d7/week", "None", "CES 3\u00d7/week; taVNS daily home"],
    ],
)

# ─── ASD ──────────────────────────────────────────────────────────────────────
CDATA["asd"] = dict(
    slug="asd", cover_title="AUTISM SPECTRUM DISORDER (ASD)",
    name="Autism Spectrum Disorder (ASD)", short="ASD", abbr="ASD",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in Autism Spectrum Disorder is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not extend to ASD. Mandatory off-label disclosure and Doctor "
        "sign-off are required before TPS treatment for ASD."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for ASD requires specific, documented off-label disclosure with Doctor sign-off. "
        "All NIBS is embedded within a structured behavioural/therapeutic framework."
    ),
    prs_domain_label="ASD Symptom & Function Domains",
    prs_domain_header_line="ASD Symptom & Function Domains \u2014 score each relevant item on a 0\u201310 scale (patient/caregiver-rated):",
    exam_step_heading="4.1 ASD Behavioural & Cognitive Examination",
    exam_step_desc=(
        "Conduct a systematic ASD behavioural and cognitive examination. "
        "Rate social communication, restricted/repetitive behaviours, and executive function domains. "
        "Caregiver input is essential:"
    ),
    exam_checklist_item="\u2610 ASD behavioural & cognitive examination completed (SRS-2 administered; executive function rated; caregiver input recorded)",
    med_check_item="Record current medication compliance (risperidone/aripiprazole dose; ADHD medications; any recent changes)",
    session_med_doc="medication compliance (risperidone/aripiprazole; stimulants; any PRN taken; timing)",
    false_class_body=(
        "Standardise ASD assessment conditions between baseline and follow-up. SRS-2 and ADOS-2 "
        "scores are sensitive to environmental context, observer familiarity, and concurrent stressors. "
        "Ensure the same rater completes caregiver-rated measures at baseline and follow-up to avoid "
        "false responder or false non-responder classification."
    ),
    modality_table=[
        ["Modality", "Device", "Classification", "ASD Evidence Status"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Level C evidence (DLPFC social/executive; Schneider 2017)"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL \u2014 OFF-LABEL for ASD"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Level C (polyvagal/autonomic regulation; Patriquin 2019)"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Level C (anxiety/sleep comorbidity in ASD)"],
    ],
    offlabel_table=[
        ["Modality", "Regulatory Status", "ASD Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Level C preliminary evidence; DLPFC social cognition protocol", "Standard informed consent"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Level C; polyvagal autonomic regulation mechanism", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety)", "Comorbid anxiety/sleep; FDA-cleared anxiety indication", "Standard informed consent"],
    ],
    prs_table=[
        ["Social Communication Symptoms (0\u201310)", "Behaviour, Cognition & Sensory (0\u201310)"],
        ["Social reciprocity / back-and-forth interaction", "Repetitive behaviours / stereotypies"],
        ["Nonverbal communication (eye contact, gesture)", "Restricted interests (intensity/fixation)"],
        ["Peer relationships / friendships", "Insistence on sameness / rigidity"],
        ["Empathy / perspective-taking (ToM)", "Sensory hypersensitivity (light, sound, texture)"],
        ["Social language / pragmatics", "Executive dysfunction (planning, flexibility)"],
        ["Social anxiety / avoidance", "Anxiety / meltdowns / emotional dysregulation"],
        ["Adaptive communication (community)", "Sleep disturbance (insomnia; delayed onset)"],
        ["Overall social participation / quality of life", "Caregiver burden / family stress"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["Social Responsiveness (SRS-2)", "Social Responsiveness Scale (clinician/caregiver-rated)", "T-score >65 = clinically significant; >76 = severe"],
        ["Executive Function (BRIEF-2)", "Behaviour Rating Inventory of Executive Function", "GEC T-score; \u226565 = significant impairment"],
        ["Adaptive Behaviour (Vineland-3)", "Vineland Adaptive Behaviour Scales \u2014 3rd Edition", "Composite score; domain scores"],
        ["Repetitive Behaviour (RBS-R)", "Repetitive Behaviour Scale \u2014 Revised (6 subscales)", "Total score; subscale severity"],
        ["Anxiety Screen (SCARED/SPAI-C)", "Screen for Child Anxiety Related Disorders; SPAI-C", "Cutoffs: SCARED >25 = anxiety; SPAI-C >18"],
        ["Sensory Profile (SSP)", "Short Sensory Profile (caregiver-rated)", "Domain subscale scores; processing pattern"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["SRS-2 (Social Responsiveness Scale \u2014 2nd Edition)", "___ T-score", "66\u201375 = mild; 76\u201385 = moderate; >85 = severe ASD features"],
        ["BRIEF-2 GEC (Global Executive Composite)", "___ T-score", ">65 = clinically significant executive impairment"],
        ["RBS-R (Repetitive Behaviour Scale)", "___ / 129", "Total score; higher = greater RRB severity; MCID ~15%"],
        ["SCARED (Anxiety)", "___ / 82", ">25 = probable anxiety disorder; subscales for type"],
        ["PSQI (Sleep quality)", "___ / 21", ">5 = sleep disturbance (60\u201380% ASD prevalence)"],
        ["Vineland-3 Adaptive Composite", "___ standard score", "70\u201384 = below average; <70 = significantly below average"],
        ["PHQ-9 (Depression comorbidity)", "___ / 27", "\u226510 = comorbid depression"],
        ["Caregiver Stress Index (CSI)", "___ / 52", ">21 = significant caregiver stress"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Social Cognition Dominant", "Core social-communication deficits primary; mPFC/TPJ/STS hypoactivation; limited reciprocity, ToM deficits"],
        ["Executive Dysfunction / Rigidity", "Cognitive inflexibility, perseveration, rigid routines; DLPFC deficit; meltdowns at transitions"],
        ["Anxiety / Sensory-Overload", "Comorbid anxiety (40%); sensory hypersensitivity driving overwhelm; meltdowns; CES + taVNS primary"],
        ["Repetitive Behaviour Dominant", "Stereotypies, compulsive routines, restricted interests; SMA/striatal hyperactivation"],
        ["ASD + ADHD (Dual Diagnosis)", "Executive + attention deficits; stimulant timing considerations; combined behavioural approach"],
        ["Language Delay / Non-Verbal", "Communication differences; AAC concurrent; adapted outcome measures required"],
        ["High Anxiety + Social Phobia", "ASD + severe social anxiety; avoidance; taVNS + CES primary before social exposure tasks"],
        ["ASD + Depression", "Adolescent/adult ASD + MDD; common in females; bifrontal tDCS + taVNS + CES"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["L-DLPFC (F3)", "Executive / Social Cognition", "Social cognition computerised tasks; face-emotion recognition; theory of mind exercises"],
        ["mPFC (TPS)", "Social Brain Network", "Mentalising tasks; perspective-taking exercises; social scenario discussion with clinician"],
        ["SMA Cathodal (Cz)", "Repetitive Behaviour Inhibition", "Habit reversal training; competing behaviour instruction; repetitive behaviour diary"],
        ["taVNS", "Autonomic / Polyvagal / Anxiety", "Paced breathing; HRV biofeedback; social engagement grounding exercises"],
        ["CES (Alpha-Stim)", "Sleep / Anxiety Comorbidity", "Sleep hygiene for ASD; bedtime routine structuring; sensory calming routine"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["SRS-2 T-score (Primary)", "\u226510-point T-score reduction = clinically meaningful change"],
        ["BRIEF-2 GEC", "\u22655-point T-score reduction in GEC (Global Executive Composite)"],
        ["RBS-R (Repetitive Behaviour)", "\u226515% reduction in RBS-R total score"],
        ["SCARED (Anxiety)", "\u226510-point reduction in SCARED total; or below diagnostic threshold"],
        ["PSQI (Sleep)", "PSQI \u22645 or \u22653-point improvement in global score"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "DSM-5 ASD diagnosis confirmed by ADOS-2 and ADI-R"],
        ["2", "Age 12\u201345 years; Level 1 or Level 2 ASD"],
        ["3", "SRS-2 T-score \u226566 OR BRIEF-2 GEC \u226565 at baseline"],
        ["4", "Capable of informed consent or assent with guardian consent"],
        ["5", "Target symptoms: social cognition, repetitive behaviours, anxiety, or executive dysfunction"],
        ["6", "Stable behavioural/pharmacological intervention for \u22654 weeks prior to enrolment"],
        ["7", "Willing to engage with concurrent ABA/social skills/CBT programme"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Level 3 ASD (requiring very substantial support); non-verbal without AAC"],
        ["2", "Active seizure disorder not controlled with medication"],
        ["3", "Metallic implants in head/neck stimulation field"],
        ["4", "Cardiac pacemaker or ICD"],
        ["5", "Active psychiatric crisis (psychosis, suicidality)"],
        ["6", "Pregnancy"],
        ["7", "Severe intellectual disability (IQ <50) precluding consent/assent"],
        ["8", "Recent medication change (<4 weeks) that could confound outcomes"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Epilepsy comorbidity (10\u201330% ASD)", "Anti-epileptic confirmed and effective; neurology clearance; reduce tDCS intensity"],
        ["Extreme sensory sensitivity", "Electrode tolerance assessment first; gel electrodes; gradual exposure to device"],
        ["Non-verbal / limited communication", "AAC use during sessions; adapted consent; caregiver present; alternative outcome measures"],
        ["ADHD comorbidity", "Stimulant timing; separate ADHD elements; combined ASD-ADHD pathway"],
        ["Severe self-injurious behaviour", "Behaviour specialist concurrent; safety planning; CISD protocol"],
        ["High support needs (Level 2)", "Intensive caregiver training; home use caregiver-supervised; adapted tasks"],
        ["School/academic setting", "Coordination with school SENCO; generalisation of gains plan"],
        ["Anxiety so severe it prevents engagement", "CES + taVNS only phase first; desensitise to device before NIBS"],
        ["Hearing sensitivity (hyperacusis comorbidity)", "Use silent electrode setup; reduce ambient noise in session room"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Social Cognition Dominant", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "mPFC + STS: 250 pulses, 0.2\u202fHz", "taVNS 30min before; social skills concurrent"],
        ["Executive / Rigidity", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "DLPFC BA46: 250 pulses", "Flexibility training concurrent; CES adjunct"],
        ["Anxiety / Sensory-Overload", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "None initial", "taVNS primary + CES nightly; desensitisation"],
        ["Repetitive Behaviour", "Cathodal SMA (Cz) 1.5\u202fmA 20\u202fmin", "SMA: 200 pulses", "Habit reversal concurrent; CES adjunct"],
        ["ASD + ADHD", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "DLPFC: 200 pulses", "taVNS 30min; stimulant timing documented"],
        ["High Anxiety + Social Phobia", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "None initial", "taVNS primary; CES nightly; gradual social exposure"],
        ["ASD + Depression", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "DLPFC: 200 pulses", "taVNS + CES nightly; behavioural activation"],
        ["Maintenance", "Anodal L-DLPFC (F3) 1.5\u202fmA 2\u00d7/week", "None", "CES 3\u00d7/week; taVNS daily home device"],
    ],
)

# ─── LONG COVID ───────────────────────────────────────────────────────────────
CDATA["long_covid"] = dict(
    slug="long_covid", cover_title="LONG COVID \u2014 POST-ACUTE SEQUELAE OF SARS-CoV-2 (PASC)",
    name="Long COVID (PASC)", short="Long COVID", abbr="PASC",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in Long COVID / PASC is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not currently extend to Long COVID. Mandatory off-label disclosure and Doctor "
        "sign-off are required before TPS treatment for Long COVID."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for Long COVID requires specific, documented off-label disclosure with Doctor sign-off. "
        "Energy envelope management and PEM monitoring are mandatory throughout the protocol."
    ),
    prs_domain_label="Long COVID Symptom Domains",
    prs_domain_header_line="Long COVID Symptom Domains \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
    exam_step_heading="4.1 Long COVID Multisystem Examination",
    exam_step_desc=(
        "Conduct a systematic Long COVID multisystem examination using the Clinical Examination Checklist. "
        "Assess cognitive, autonomic, fatigue, and mood domains; document PEM status and energy envelope:"
    ),
    exam_checklist_item="\u2610 Long COVID multisystem examination completed (cognitive, autonomic, and fatigue domains assessed; PEM screen completed)",
    med_check_item="Record symptomatic medication compliance (LDN, antihistamines, SSRIs, POTS medications; last dose timing)",
    session_med_doc="medication compliance (symptomatic medications; POTS treatment; antihistamines; dose and timing)",
    false_class_body=(
        "Standardise Long COVID assessment conditions between baseline and follow-up. Cognitive and "
        "fatigue scores fluctuate significantly with post-exertional malaise (PEM) and day-to-day "
        "variation. Ensure assessments occur at the same time of day, on a non-PEM day, with "
        "comparable activity levels to avoid false responder or false non-responder classification."
    ),
    modality_table=[
        ["Modality", "Device", "Classification", "Long COVID Evidence Status"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "INVESTIGATIONAL \u2014 emerging evidence; DLPFC protocol (2023 case series)"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL \u2014 OFF-LABEL for Long COVID"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Level C (anti-inflammatory / autonomic; Clancy 2022)"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Level C (safest modality; fatigue/sleep/anxiety in PASC)"],
    ],
    offlabel_table=[
        ["Modality", "Regulatory Status", "Long COVID Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Investigational; emerging case series; energy-adapted protocol required", "Standard informed consent + PEM discussion"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Level C; anti-inflammatory and autonomic mechanism", "Standard informed consent + PEM monitoring"],
        ["CES", "FDA-cleared (anxiety/depression/insomnia)", "Safest NIBS in Long COVID; FDA-cleared for target symptoms", "Standard informed consent"],
    ],
    prs_table=[
        ["Cognitive & Neurological Symptoms (0\u201310)", "Systemic & Psychological Symptoms (0\u201310)"],
        ["Cognitive fog / brain fog severity", "Post-exertional malaise (PEM) frequency"],
        ["Memory impairment (working / episodic)", "Fatigue severity (disproportionate)"],
        ["Processing speed reduction", "Sleep disturbance"],
        ["Word-finding difficulty", "Autonomic symptoms (POTS / dizziness / palpitations)"],
        ["Concentration / attention", "Anxiety / depression"],
        ["Headache (new or worsened)", "Dyspnoea / breathlessness on exertion"],
        ["Sensory symptoms (paraesthesias, smell/taste)", "Activity level vs. pre-COVID (% capacity)"],
        ["Overall quality of life / functioning", "Caregiver/support needs change from pre-COVID"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["Cognitive Screen (MoCA)", "Montreal Cognitive Assessment; attention, memory, language", "MoCA total /30; <26 = cognitive impairment screen"],
        ["Fatigue (MFIS)", "Modified Fatigue Impact Scale (21 items)", "Total 0\u201384; \u226538 = clinically significant fatigue"],
        ["Autonomic / POTS Screen", "10-minute stand test: HR at rest vs. standing at 2, 5, 10 min", "HR increase >30bpm = POTS positive"],
        ["PEM Assessment (DSQ)", "DePaul Symptom Questionnaire \u2014 PEM module", "PEM frequency and severity rating"],
        ["Mood Assessment", "PHQ-9; GAD-7; DASS-21", "Standard thresholds"],
        ["HRV (Autonomic)", "Heart rate variability (RMSSD) if available; pulse oximetry", "RMSSD baseline; SpO2 \u226595% required"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["MoCA (Cognitive \u2014 primary)", "___ / 30", "<26 = cognitive impairment; MCID = 2 points improvement"],
        ["MFIS (Fatigue)", "___ / 84", "\u226538 = clinically significant fatigue (primary outcome)"],
        ["DSQ-PEM (Post-Exertional Malaise)", "Frequency/severity", "Any PEM \u22652/5 severity = PEM positive; adapt protocol"],
        ["10-Min Stand Test (POTS)", "HR change bpm", ">30bpm HR increase = POTS positive; cardiologist referral"],
        ["PHQ-9 (Depression)", "___ / 27", "\u226510 = comorbid depression in Long COVID"],
        ["GAD-7 (Anxiety)", "___ / 21", "\u226510 = comorbid anxiety in Long COVID"],
        ["PSQI (Sleep quality)", "___ / 21", ">5 = Long COVID-related sleep disturbance"],
        ["PROMIS Cognitive Function", "___ T-score", "<45 T-score = below-average cognitive function"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Cognitive-Dominant (Brain Fog)", "Processing speed, memory, word-finding deficits; DLPFC-thalamic network disruption; work/study incapacity"],
        ["Autonomic-Dominant (POTS/Fatigue)", "Orthostatic intolerance, tachycardia, exercise intolerance; ANS dysregulation primary; taVNS first-line"],
        ["Neuropsychiatric (Anxiety/Depression/Insomnia)", "Mood disorders, anxiety, insomnia; neuroinflammatory-serotonergic mechanism; tDCS DLPFC + CES + taVNS"],
        ["PEM-Dominant", "Post-exertional malaise >24h with minimal exertion; mitochondrial/metabolic; CES primary only; strict energy management"],
        ["Headache Subtype", "New-onset persistent headache; thalamic-cortical mechanisms; CES primary; tDCS DLPFC adjunct"],
        ["Sensory Symptoms", "Anosmia, parosmia, paraesthesias; TPS insula investigational; CES + taVNS supportive"],
        ["Dysautonomia + Cognitive Combined", "Overlapping POTS and brain fog; energy-adapted NIBS; taVNS + low-dose tDCS; strict pacing"],
        ["Stable Multi-Domain", "Stable Long COVID with multiple mild-moderate symptoms; comprehensive protocol (if PEM-free)"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["L-DLPFC (F3)", "Cognitive / Brain Fog", "Computerised cognitive tasks (low-exertion); attention training; word-finding exercises (energy-paced)"],
        ["DLPFC + Thalamic (TPS)", "Cognitive Network", "Cognitive activation tasks at low intensity; energy envelope monitoring during task"],
        ["taVNS", "Autonomic / Anti-Inflammatory", "Paced breathing; rest-and-activate cycle; HRV monitoring; anti-inflammatory protocol"],
        ["CES (Alpha-Stim)", "Sleep / Fatigue / Anxiety", "Sleep hygiene education; energy conservation planning; fatigue management; pacing education"],
        ["None (PEM-Dominant)", "Pacing Only", "Energy envelope diary; graded rest schedule; PEM trigger identification; pacing education ONLY"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["MoCA (Cognitive \u2014 Primary)", "\u22652-point improvement = clinically meaningful; stabilisation = partial response"],
        ["MFIS (Fatigue)", "MCID \u22655-point reduction; sustained improvement without PEM worsening"],
        ["HRV / POTS (Autonomic)", "\u226510% RMSSD increase; HR increase at stand <30bpm = POTS resolution"],
        ["PHQ-9 / GAD-7 (Mood)", "\u226550% reduction in PHQ-9 or GAD-7 = response; score \u22644 = remission"],
        ["PGIC (Global)", "PGIC \u22655 (much improved) = global responder; no PEM worsening essential"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "WHO-defined Long COVID: symptoms \u226512 weeks post-SARS-CoV-2, not explained by alternative diagnosis"],
        ["2", "Confirmed prior SARS-CoV-2 infection (PCR, antigen, or serology)"],
        ["3", "Symptom burden: MoCA \u226425, or MFIS \u226538, or PHQ-9 \u226510"],
        ["4", "Age 18\u201365; capable of informed consent"],
        ["5", "Stable symptoms for \u22654 weeks (not in acute post-COVID relapse)"],
        ["6", "PEM screen: PEM-dominant phenotype: CES-only protocol; other phenotypes: full assessment"],
        ["7", "POTS screen completed; cardiologist referral if positive"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Active SARS-CoV-2 infection (acute phase)"],
        ["2", "Metallic implants in head/neck stimulation field"],
        ["3", "Cardiac pacemaker or ICD; active myocarditis or pericarditis"],
        ["4", "Pregnancy"],
        ["5", "Pre-existing neurological/psychiatric diagnosis that fully explains symptoms"],
        ["6", "Severe PEM precluding any session participation (energy envelope too limited)"],
        ["7", "Active cancer or severe systemic illness"],
        ["8", "EDSS >6 equivalent disability from Long COVID"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Severe PEM (DSQ PEM >3/5)", "CES-only protocol first; defer tDCS/TPS; weekly PEM monitoring; escalate gradually"],
        ["POTS confirmed", "Cardiologist clearance before taVNS; cardiac monitoring; session supine if needed"],
        ["Mast Cell Activation Syndrome (MCAS)", "Antihistamine adherence; electrode gel allergy screen; dermatology concurrent"],
        ["Myalgic Encephalomyelitis (ME/CFS overlap)", "ME/CFS pacing guidelines apply; no graded exercise therapy"],
        ["Dysautonomia (non-POTS)", "Autonomic specialist concurrent; careful session positioning"],
        ["Cognitive impairment severe (MoCA <18)", "Simplified home use; caregiver supervision; adapted consent"],
        ["Anxiety / panic about diagnosis", "Psychoeducation first; CES + taVNS as initial approach; gradual escalation"],
        ["Post-COVID depression (PHQ-9 >14)", "Prioritise antidepressant approach; tDCS DLPFC anodal; taVNS + CES"],
        ["Long COVID in healthcare workers", "Occupational health integration; return-to-work planning; functional targets"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Cognitive-Dominant", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "DLPFC: 200 pulses, 0.2\u202fHz (low)", "CES nightly 60min; taVNS 30min; pacing essential"],
        ["Autonomic-Dominant (POTS)", "Anodal L-DLPFC (F3) 1\u202fmA 15\u202fmin (low)", "None initial", "taVNS primary 2\u00d7 daily; CES nightly; POTS management"],
        ["Neuropsychiatric", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "None initial", "taVNS + CES nightly; SSRI maintained if prescribed"],
        ["PEM-Dominant", "CES ONLY initially \u2014 no tDCS/TPS", "No TPS \u2014 defer", "CES nightly 60min primary; strict energy management"],
        ["Headache Subtype", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "None initial", "CES primary; taVNS 30min; pacing concurrent"],
        ["Dysautonomia + Cognitive", "Anodal L-DLPFC (F3) 1\u202fmA 15\u202fmin", "DLPFC: 150 pulses (minimal)", "taVNS before tDCS; CES nightly; ANS monitoring"],
        ["Stable Multi-Domain", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "DLPFC: 200 pulses", "taVNS + CES nightly; comprehensive pacing plan"],
        ["Maintenance", "Anodal L-DLPFC (F3) 1\u202fmA 15\u202fmin 2\u00d7/week", "None", "CES 3\u00d7/week; taVNS daily home; PEM diary ongoing"],
    ],
)

# ─── TINNITUS ─────────────────────────────────────────────────────────────────
CDATA["tinnitus"] = dict(
    slug="tinnitus", cover_title="CHRONIC TINNITUS",
    name="Chronic Tinnitus", short="Tinnitus", abbr="Tinnitus",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in Chronic Tinnitus is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not extend to tinnitus. Mandatory off-label disclosure and Doctor "
        "sign-off are required before TPS treatment for tinnitus."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for Tinnitus requires specific, documented off-label disclosure with Doctor sign-off. "
        "Audiological evaluation must be completed before any NIBS is initiated."
    ),
    prs_domain_label="Tinnitus Symptom & Impact Domains",
    prs_domain_header_line="Tinnitus Symptom & Impact Domains \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
    exam_step_heading="4.1 Audiological & Tinnitus Examination",
    exam_step_desc=(
        "Conduct a systematic audiological and tinnitus examination using the Clinical Examination Checklist. "
        "Document tinnitus characteristics, audiological profile, and associated symptoms:"
    ),
    exam_checklist_item="\u2610 Audiological & tinnitus examination completed (THI administered; audiogram reviewed; tinnitus characteristics documented)",
    med_check_item="Record any tinnitus-related medications (amitriptyline, gabapentin, melatonin; last dose timing)",
    session_med_doc="medication compliance (tinnitus-related medications; sleep aids; timing)",
    false_class_body=(
        "Standardise tinnitus assessment conditions between baseline and follow-up. THI and VAS scores "
        "can fluctuate with noise exposure, stress, and sleep quality. Ensure assessments occur in a "
        "quiet, consistent environment at comparable times of day to avoid false responder or false "
        "non-responder classification."
    ),
    modality_table=[
        ["Modality", "Device", "Classification", "Tinnitus Evidence Status"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Level B evidence (A1 cathodal/DLPFC anodal; Fregni 2006; Schecklmann 2011)"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL \u2014 OFF-LABEL for Tinnitus"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Level B evidence (VNS-tone pairing; Engineer 2011)"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Level B evidence (tinnitus sleep/anxiety; Lande 2018)"],
    ],
    offlabel_table=[
        ["Modality", "Regulatory Status", "Tinnitus Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Level B evidence; A1 cathodal and DLPFC anodal established", "Standard informed consent"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Level B; VNS-tone pairing cortical plasticity mechanism", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety/depression/insomnia)", "Level B; tinnitus-related sleep/anxiety; FDA-cleared", "Standard informed consent"],
    ],
    prs_table=[
        ["Tinnitus Percept & Distress (0\u201310)", "Functional Impact & Comorbidities (0\u201310)"],
        ["Tinnitus loudness (VAS 0\u201310)", "Sleep disturbance due to tinnitus"],
        ["Tinnitus distress / annoyance (VAS 0\u201310)", "Anxiety related to tinnitus"],
        ["Tinnitus intrusiveness (attention capture)", "Depression / low mood related to tinnitus"],
        ["Ability to mask / ignore tinnitus", "Concentration impairment due to tinnitus"],
        ["Tinnitus pitch (patient description)", "Hyperacusis / sound sensitivity"],
        ["Tinnitus character (tonal/noise/pulsatile)", "Avoidance of quiet / social situations"],
        ["Tinnitus variability (constant/fluctuating)", "Hearing impairment impact on communication"],
        ["Overall THI-rated handicap level", "Overall quality of life / wellbeing"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["THI Score (Handicap)", "Tinnitus Handicap Inventory (25 items)", "0\u201316 = no handicap; 18\u201336 = mild; 38\u201356 = moderate; 58\u201376 = severe"],
        ["Audiological Profile", "Audiogram review; pure tone averages; SNHL documentation", "PTA 0.5\u20134 kHz; hearing loss grade (WHO)"],
        ["Tinnitus Matching", "Loudness matching (dBSL above threshold); pitch matching", "dBSL above threshold; frequency in Hz"],
        ["Hyperacusis Assessment", "Loudness Discomfort Levels (LDL); Hyperacusis Questionnaire", "LDL <85 dB HL = hyperacusis; HQ total"],
        ["Mood & Sleep", "PHQ-9; GAD-7; PSQI", "Standard thresholds"],
        ["Minimum Masking Level (MML)", "Audiological tinnitus measure \u2014 masking level", "Lower MML = easier to mask"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["THI (Tinnitus Handicap Inventory)", "___ / 100", "38\u201356 = moderate handicap; 58\u201376 = severe; >76 = catastrophic"],
        ["TFI (Tinnitus Functional Index)", "___ / 100", ">25 = significant impact; MCID = 13 points"],
        ["VAS Loudness", "___ / 10", "\u22657 = severe perceived loudness"],
        ["VAS Distress", "___ / 10", "\u22657 = severe distress; MCID = 2-point reduction"],
        ["PHQ-9 (Depression comorbidity)", "___ / 27", "\u226510 = depression comorbidity present"],
        ["GAD-7 (Anxiety comorbidity)", "___ / 21", "\u226510 = anxiety comorbidity present"],
        ["PSQI (Sleep quality)", "___ / 21", ">5 = tinnitus-related sleep disturbance"],
        ["Hyperacusis Questionnaire (HQ)", "___ / 42", ">28 = significant hyperacusis comorbidity"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Audiological / Peripheral Dominant", "Tinnitus with significant SNHL; peripheral deafferentation primary; A1 reorganisation; hearing aid concurrent"],
        ["Central / Network Dominant", "Tinnitus without significant hearing loss; central reorganisation primary; high loudness/distress despite normal audiogram"],
        ["Distress-Dominant", "High THI (\u226556); anxiety, depression, catastrophising; amygdala-network activation; CBT concurrent essential"],
        ["Sleep-Dominant", "Tinnitus-insomnia cycle; hyperarousal; nocturnal tinnitus awareness; CES primary modality"],
        ["Hyperacusis Comorbid", "Tinnitus + sound sensitivity; auditory gain dysregulation; A1 cathodal; TPS limited by hyperacusis tolerance"],
        ["Pulsatile Tinnitus", "Vascular/structural aetiology; specialist evaluation required before any NIBS; cardiologist/neurosurgeon first"],
        ["Somatic Tinnitus", "Jaw/neck movement modulates tinnitus; TMJ or cervical spine component; specialist input"],
        ["Tinnitus with Depression", "High PHQ-9 (\u226510) comorbid; bifrontal tDCS + CES + taVNS combined"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["A1 Cathodal (T3/T4)", "Auditory Cortex Suppression", "Sound therapy / notched music during tDCS; broadband noise masking; tinnitus retraining audio"],
        ["L-DLPFC (F3)", "Top-Down Suppression / Mood", "Cognitive defusion from tinnitus sounds; attention training away from tinnitus; CBT tinnitus exercises"],
        ["ACC (TPS)", "Distress Network Modulation", "Mindfulness of tinnitus (defusion); acceptance-based tinnitus coping; CBT cognitive restructuring"],
        ["taVNS", "Auditory Plasticity / Distress", "VNS-tone pairing (if available): paired auditory stimuli during taVNS; otherwise breathing + relaxation"],
        ["CES (Alpha-Stim)", "Sleep / Anxiety Reduction", "Sleep hygiene for tinnitus; tinnitus bedtime masking device; relaxation and sound enrichment routine"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["THI (Primary)", "\u22657-point reduction = MCID; grade improvement = clinical response (e.g., severe \u2192 moderate)"],
        ["TFI", "\u226513-point reduction from baseline = clinically meaningful change"],
        ["VAS Loudness / Distress", "\u226520% reduction in VAS score = clinical response"],
        ["PHQ-9 / GAD-7 (Comorbidity)", "\u226550% reduction = response; score \u22644 = remission"],
        ["PSQI (Sleep)", "PSQI \u22645 or \u22653-point improvement in global score"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "Chronic tinnitus \u22656 months duration (unilateral or bilateral)"],
        ["2", "THI \u226538 (moderate-severe) at baseline; audiological assessment completed"],
        ["3", "Age 18\u201375; capable of informed consent"],
        ["4", "Inadequate response to \u22651 conventional treatment (sound therapy, CBT, hearing aids)"],
        ["5", "Stable audiological status for \u22653 months (no acute hearing loss)"],
        ["6", "Pulsatile tinnitus excluded (vascular aetiology ruled out)"],
        ["7", "Hyperacusis assessed; LDL >85 dB HL (if hyperacusis present: adapted protocol)"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Pulsatile tinnitus with vascular aetiology not yet evaluated (refer first)"],
        ["2", "Active Meni\u00e8re\u2019s disease with acute vertigo attacks"],
        ["3", "Metallic implants in head/neck stimulation field"],
        ["4", "Cochlear implant (evaluate carefully; may preclude T3/T4 electrode placement)"],
        ["5", "Active otological infection or post-surgical healing"],
        ["6", "Cardiac pacemaker or ICD (CES / taVNS contraindication)"],
        ["7", "Pregnancy"],
        ["8", "Severe hyperacusis (LDL <60 dB HL) precluding TPS tolerance"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Hyperacusis comorbidity", "TPS limited or avoided; lower CES volume; noise-protected session environment"],
        ["Significant hearing loss (>40 dB HL)", "Hearing aid trial first; audiologist concurrent; adjust electrode proximity"],
        ["TMJ / cervical somatic tinnitus", "Dental / physiotherapy input first; somatic component may respond to local treatment"],
        ["Hearing aid user", "Coordinate hearing aid use with tinnitus masking during sessions; audiologist input"],
        ["Cardiovascular disease", "CES + taVNS: ECG and cardiac clearance required"],
        ["Anxiety/depression comorbidity (PHQ-9 >14)", "Treat mental health concurrently; taVNS + CES primary"],
        ["Elderly (\u226570)", "Reduce electrode intensities; hearing examination annual; lower TPS pulse count"],
        ["Tinnitus following noise trauma (recent)", "Assess for acoustic shock; ENT referral; CES + rest first before NIBS"],
        ["Unilateral tinnitus only", "Ipsilateral A1 cathodal electrode (T3 or T4); lateralised protocol"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Audiological / Peripheral", "Cathodal A1 (T3/T4 1.5\u202fmA) + Anodal DLPFC (F3 2\u202fmA)", "A1: 200 pulses, 0.2\u202fHz", "CES nightly 60min; hearing aid concurrent"],
        ["Central / Network", "Cathodal A1 (T3/T4 1.5\u202fmA) + Anodal DLPFC (F3 2\u202fmA)", "A1 + DLPFC: 300 pulses", "taVNS-tone pairing; TRT concurrent"],
        ["Distress-Dominant", "Anodal L-DLPFC (F3) 2\u202fmA 20\u202fmin", "ACC: 250 pulses, 0.2\u202fHz", "taVNS + CES nightly; CBT concurrent essential"],
        ["Sleep-Dominant", "Anodal L-DLPFC (F3) 1.5\u202fmA 20\u202fmin", "None initial", "CES primary nightly 60min; taVNS pre-bed"],
        ["Hyperacusis Comorbid", "Cathodal A1 (T3/T4 1\u202fmA 15\u202fmin)", "None (TPS limited)", "CES primary; sound desensitisation concurrent"],
        ["Somatic Tinnitus", "Cathodal A1 + Anodal DLPFC", "A1: 200 pulses", "taVNS + physiotherapy concurrent"],
        ["Tinnitus + Depression", "Anodal L-DLPFC (F3) 2\u202fmA + Bifrontal option", "ACC + DLPFC: 300 pulses", "taVNS + CES nightly; antidepressant concurrent"],
        ["Maintenance", "Anodal L-DLPFC (F3) 1.5\u202fmA 2\u00d7/week", "None", "CES 3\u00d7/week; taVNS daily home; sound enrichment"],
    ],
)

# ─── INSOMNIA ─────────────────────────────────────────────────────────────────
CDATA["insomnia"] = dict(
    slug="insomnia", cover_title="CHRONIC INSOMNIA DISORDER",
    name="Chronic Insomnia Disorder", short="Insomnia", abbr="Insomnia",
    tps_offlabel_body=(
        "TPS (NEUROLITH\u00ae) use in Insomnia Disorder is INVESTIGATIONAL and OFF-LABEL. "
        "CE marking does not extend to insomnia. Mandatory off-label disclosure and Doctor "
        "sign-off are required before TPS treatment for insomnia."
    ),
    mandatory_consent_body=(
        "No diagnostic or therapeutic procedures may be performed prior to informed consent. "
        "TPS for Insomnia requires specific, documented off-label disclosure with Doctor sign-off. "
        "Obstructive sleep apnoea must be excluded or treated before NIBS is initiated."
    ),
    prs_domain_label="Sleep & Arousal Symptom Domains",
    prs_domain_header_line="Sleep & Arousal Symptom Domains \u2014 score each relevant item on a 0\u201310 scale (patient-rated):",
    exam_step_heading="4.1 Sleep & Arousal Examination",
    exam_step_desc=(
        "Conduct a systematic sleep and arousal examination using the Clinical Examination Checklist. "
        "Document sleep pattern, hyperarousal, and comorbid contributions; "
        "rule out primary sleep disorders (OSA, RLS, PLMD):"
    ),
    exam_checklist_item="\u2610 Sleep & arousal examination completed (ISI administered; sleep diary reviewed; OSA screened)",
    med_check_item="Record sleep medication compliance (Z-drug, melatonin, trazodone, suvorexant; last dose and timing)",
    session_med_doc="sleep medication compliance (hypnotic dose and timing; last night use; any PRN taken)",
    false_class_body=(
        "Standardise insomnia assessment conditions between baseline and follow-up. Actigraphy-derived "
        "measures (SOL, WASO, TST) vary significantly week-to-week. Use 7-night averages at baseline "
        "and follow-up rather than single-night data. Subjective ISI ratings can be influenced by "
        "recent good/bad nights; use multi-day averages to avoid false responder or false non-responder "
        "classification."
    ),
    modality_table=[
        ["Modality", "Device", "Classification", "Insomnia Evidence Status"],
        ["tDCS", "Newronika HDCkit / PlatoScience", "CE Class IIa", "Level B evidence (DLPFC cathodal; Frase 2016; hyperarousal reduction)"],
        ["TPS", "NEUROLITH\u00ae (Storz Medical)", "CE Class IIa", "INVESTIGATIONAL \u2014 OFF-LABEL for Insomnia"],
        ["taVNS", "Nemos / TENS tragus device", "CE-marked (epilepsy/depression)", "Level B evidence (autonomic/parasympathetic; Lehtim\u00e4ki 2013)"],
        ["CES", "Alpha-Stim AID", "FDA-cleared (anxiety/insomnia/depression)", "Level A evidence; FDA-CLEARED for insomnia \u2014 PRIMARY modality"],
    ],
    offlabel_table=[
        ["Modality", "Regulatory Status", "Insomnia Classification", "Disclosure Required"],
        ["tDCS", "CE Class IIa", "Level B evidence; DLPFC cathodal hyperarousal reduction", "Standard informed consent"],
        ["TPS", "CE Class IIa (Alzheimer\u2019s only)", "INVESTIGATIONAL \u2014 OFF-LABEL", "Full off-label disclosure + Doctor sign-off"],
        ["taVNS", "CE-marked (epilepsy/depression)", "Level B; autonomic parasympathetic activation pre-sleep", "Standard informed consent"],
        ["CES", "FDA-cleared (anxiety/insomnia/depression)", "FDA-CLEARED for insomnia \u2014 PRIMARY NIBS modality", "Standard informed consent"],
    ],
    prs_table=[
        ["Sleep Symptoms (0\u201310)", "Arousal & Daytime Symptoms (0\u201310)"],
        ["Sleep onset difficulty (SOL minutes)", "Daytime fatigue / tiredness"],
        ["Night-time awakenings (number/frequency)", "Concentration / cognitive impairment"],
        ["Early morning awakening (EMA)", "Mood disturbance (irritability, dysphoria)"],
        ["Non-restorative sleep (quality)", "Anxiety about sleep / performance anxiety"],
        ["Total sleep time (perceived hrs)", "Somatic arousal at bedtime (heart rate, tension)"],
        ["Pre-sleep rumination / racing thoughts", "Caffeine / stimulant use impacting sleep"],
        ["Sleep efficiency (subjective %)", "Alcohol / sedative use for sleep"],
        ["Overall functional impairment from insomnia", "Overall wellbeing / quality of life"],
    ],
    exam_table=[
        ["Examination Domain", "Key Tests / Observations", "Scoring"],
        ["Insomnia Severity (ISI)", "Insomnia Severity Index (7 items); primary screening tool", "Total /28; \u226515 = moderate-severe (primary target)"],
        ["Sleep Diary Review", "2-week sleep diary: SOL, WASO, TST, SE, quality rating", "Average SOL, WASO, TST, SE% over 7 nights"],
        ["Actigraphy (if available)", "Wrist actigraphy: objective sleep parameters", "SOL, WASO, TST from 7-night recording"],
        ["Pre-Sleep Arousal (PSAS)", "Pre-Sleep Arousal Scale (cognitive + somatic subscales)", "Cognitive \u226518 = high cognitive arousal; somatic \u226512"],
        ["OSA Screen (STOP-BANG)", "STOP-BANG questionnaire; Epworth Sleepiness Scale", "STOP-BANG \u22653 = high risk; refer for polysomnography"],
        ["Mood Assessment", "PHQ-9; GAD-7; comorbid psychiatric screen", "Standard thresholds; comorbid pathway if positive"],
    ],
    screening_table=[
        ["Assessment", "Score", "Clinical Threshold"],
        ["ISI (Insomnia Severity Index)", "___ / 28", "8\u201314 = subthreshold; 15\u201321 = moderate; 22\u201328 = severe insomnia"],
        ["PSQI (Pittsburgh Sleep Quality Index)", "___ / 21", ">5 = poor sleeper; MCID = 3-point improvement"],
        ["PSAS (Pre-Sleep Arousal Scale)", "Cognitive: ___ / 40; Somatic: ___ / 40", "Cognitive \u226518 = high arousal; somatic \u226512"],
        ["ESS (Epworth Sleepiness Scale)", "___ / 24", ">10 = excessive daytime sleepiness (OSA screen required)"],
        ["PHQ-9 (Depression comorbidity)", "___ / 27", "\u226510 = comorbid depression driving insomnia"],
        ["GAD-7 (Anxiety comorbidity)", "___ / 21", "\u226510 = comorbid anxiety driving insomnia"],
        ["STOP-BANG (OSA screen)", "___ / 8", "\u22653 = high risk; refer for polysomnography before NIBS"],
        ["Actigraphy SOL / WASO (7-night avg)", "___ min SOL; ___ min WASO", "SOL >30min or WASO >30min on \u22653 nights = insomnia confirmed"],
    ],
    phenotype_table=[
        ["Phenotype", "Key Features"],
        ["Sleep-Onset Insomnia", "Difficulty falling asleep; prolonged SOL >30min; pre-sleep cognitive arousal; conditioned arousal to bed"],
        ["Sleep-Maintenance Insomnia", "Multiple night-time awakenings; WASO >30min; light sleep predominance; thalamic gating failure"],
        ["Early Morning Awakening", "Waking \u226530min before intended time; unable to return to sleep; common in depression; HPA axis involvement"],
        ["Hyperarousal / Cognitive-Dominant", "High PSAS cognitive subscale (\u226518); racing thoughts; hypervigilance for sleep; DLPFC-DMN dysfunction"],
        ["Comorbid Insomnia + Anxiety", "GAD-7 \u226510 + ISI \u226515; anxiety driving hyperarousal; CES + taVNS + tDCS cathodal; CBT-I + anxiety treatment"],
        ["Comorbid Insomnia + Depression", "PHQ-9 \u226510 + ISI \u226515; early morning awakening; tDCS DLPFC anodal (antidepressant) + CES + taVNS"],
        ["Insomnia + Chronic Pain", "Bidirectional pain-sleep cycle; CES primary; tDCS M1 + DLPFC; pain management concurrent"],
        ["Refractory Insomnia", "Failed CBT-I + \u22662 hypnotics; ISI \u226522; all modalities; intensive CBT-I concurrent"],
    ],
    task_pairing_table=[
        ["Montage Target", "Domain", "Concurrent Task"],
        ["DLPFC Cathodal (F3)", "Cognitive Hyperarousal Reduction", "Worry postponement scheduling; stimulus control instruction; sleep diary review; cognitive defusion"],
        ["ACC (TPS)", "Arousal Monitoring Reduction", "Mindfulness of pre-sleep thoughts; attention training away from sleep effort; acceptance of wakefulness"],
        ["taVNS", "Autonomic / Pre-Sleep Calming", "Pre-sleep paced breathing (slow exhalation); HRV biofeedback; progressive muscle relaxation at bedtime"],
        ["CES (Alpha-Stim)", "Sleep Induction \u2014 Primary Modality", "CBT-I session concurrent; sleep hygiene education; sleep restriction guidance; relaxation instruction"],
        ["DLPFC Anodal (Depression)", "Antidepressant / EMA", "Behavioural activation; morning routine structuring; pleasant activity scheduling for early morning"],
    ],
    response_domains_table=[
        ["Domain", "Response Criteria"],
        ["ISI (Primary)", "\u22668-point reduction = MCID; score <8 = remission; <15 = response"],
        ["PSQI (Sleep Quality)", "PSQI \u22645 = good sleeper (target); MCID = 3-point improvement"],
        ["Actigraphy SOL", "Average SOL <30min over 7 nights = normalisation"],
        ["PHQ-9 / GAD-7 (Comorbidity)", "\u226550% reduction = response; score \u22644 = remission"],
        ["PSAS Cognitive", "PSAS cognitive subscale reduction <18 = normalisation of cognitive arousal"],
    ],
    inclusion_table=[
        ["#", "Criterion"],
        ["1", "DSM-5 Insomnia Disorder: difficulty \u22653 nights/week for \u22653 months"],
        ["2", "ISI \u226515 (moderate-severe) at baseline"],
        ["3", "Adequate sleep opportunity (\u22657 hours in bed) ruling out insufficient sleep syndrome"],
        ["4", "Age 18\u201375; capable of informed consent"],
        ["5", "Inadequate response to \u22651 CBT-I course or sleep hygiene optimisation"],
        ["6", "OSA excluded (STOP-BANG <3) or treated (CPAP adherent \u22654h/night)"],
        ["7", "Stable sleep medications for \u22654 weeks (if on hypnotics)"],
    ],
    exclusion_table=[
        ["#", "Criterion"],
        ["1", "Untreated obstructive sleep apnoea (STOP-BANG \u22653 without polysomnography)"],
        ["2", "Metallic implants in head/neck stimulation field"],
        ["3", "Cardiac pacemaker or ICD (CES / taVNS contraindication)"],
        ["4", "Pregnancy"],
        ["5", "Shift work sleep disorder as primary aetiology"],
        ["6", "Active substance use disorder (alcohol, benzodiazepine dependence requiring detox)"],
        ["7", "Active psychosis or bipolar disorder (manic phase)"],
        ["8", "Restless legs syndrome / PLMD as primary diagnosis (refer for treatment first)"],
    ],
    conditional_table=[
        ["Condition", "Consideration"],
        ["Treated OSA (CPAP)", "Confirm CPAP adherence \u22664h/night; CPAP data review; insomnia often persists post-OSA treatment"],
        ["Chronic pain comorbidity", "Bidirectional pain-sleep management; tDCS M1 + CES combined approach"],
        ["Benzodiazepine dependence", "Structured taper plan concurrent; NIBS after stable taper; withdrawal monitoring"],
        ["Depression comorbidity (PHQ-9 >10)", "tDCS DLPFC anodal (antidepressant) + CES; address depression-insomnia cycle"],
        ["Anxiety comorbidity (GAD-7 >10)", "CES primary anxiolytic; taVNS autonomic; CBT-I with anxiety component"],
        ["Menopause-related insomnia", "Hormonal assessment; HRT discussion; CES primary; sleep hygiene for menopause"],
        ["Elderly (\u226565)", "Reduce tDCS intensity; CES primary; medication review for iatrogenic insomnia; fall risk"],
        ["Stimulant use (caffeine, modafinil)", "Caffeine restriction guidance; stimulant timing education; document use"],
        ["Post-COVID insomnia", "Consider Long COVID protocol elements; PEM screen; taVNS anti-inflammatory"],
    ],
    protocol_table=[
        ["Phenotype", "tDCS Target", "TPS Protocol", "Adjuncts (taVNS + CES)"],
        ["Sleep-Onset Insomnia", "Cathodal DLPFC (F3) 1.5\u202fmA 20\u202fmin (daytime)", "DLPFC: 200 pulses, 0.2\u202fHz", "CES primary nightly 60min; taVNS 30min pre-bed"],
        ["Sleep-Maintenance Insomnia", "Cathodal DLPFC (F3) 1.5\u202fmA 20\u202fmin (daytime)", "None initial", "CES primary nightly 60min; taVNS pre-bed"],
        ["Early Morning Awakening", "Anodal DLPFC (F3) 2\u202fmA 20\u202fmin (daytime \u2014 antidepressant)", "None initial", "CES nightly + taVNS pre-bed; depression concurrent"],
        ["Hyperarousal / Cognitive", "Cathodal DLPFC (F3) 1.5\u202fmA + TPS", "DLPFC + ACC: 300 pulses", "CES primary nightly; CBT-I cognitive focus"],
        ["Comorbid + Anxiety", "Cathodal DLPFC (F3) 1.5\u202fmA 20\u202fmin", "None initial", "CES primary 60min + taVNS; anxiety treatment concurrent"],
        ["Comorbid + Depression", "Anodal DLPFC (F3) 2\u202fmA 20\u202fmin (daytime)", "None initial", "CES nightly + taVNS pre-bed; antidepressant concurrent"],
        ["Insomnia + Chronic Pain", "Anodal M1 (C3 1.5\u202fmA) + Cathodal DLPFC (sequential)", "None initial", "CES primary nightly; pain management concurrent"],
        ["Maintenance / Relapse Prevention", "Cathodal DLPFC (F3) 1\u202fmA 15\u202fmin 2\u00d7/week", "None", "CES 3\u00d7/week; taVNS as needed home"],
    ],
)
