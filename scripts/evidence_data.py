# -*- coding: utf-8 -*-
"""
SOZO Evidence Base -- TPS, LIFU, and Conditions x Modality matrix.
Sourced from SOZO Master Neuromodulation Protocols Excel, April 2026.
1,505 unique papers (from 2,994 records); 13 TPS RCTs; 38 LIFU papers.
"""

# TPS_EVIDENCE[condition_name] = {
#   "total_papers", "rcts", "evidence_level", "highest_citation",
#   "year_range", "key_finding", "top_rct_ref", "journal", "regulatory", "notes"
# }
TPS_EVIDENCE = {
    "Alzheimer's Disease": {
        "total_papers": "31+",
        "rcts": "2 (1 RCT + 1 RCT protocol)",
        "evidence_level": "RCT, Systematic Review, Meta-analysis",
        "highest_citation": "Beisteiner 2019 (Advanced Science) -- 230 citations; n=35 multicenter, fMRI correlation",
        "year_range": "2019-2026",
        "key_finding": "CERAD CTS improved p=.017 (d=.32); 9.8-pt gain in top-quartile responders; 3-month durability; memory network upregulation on fMRI",
        "top_rct_ref": "JAMA Network Open RCT 2025 -- Ultrasound Neuromodulation With TPS in Alzheimer Disease",
        "journal": "JAMA Network Open / Advanced Science / Psychol Medicine",
        "regulatory": "CE Marked (Europe)",
        "notes": "Gold-standard evidence for TPS. CE-cleared indication. 10-session standard course. MRI-navigated protocol.",
    },
    "Parkinson's Disease": {
        "total_papers": "9+",
        "rcts": "1 RCT (2025)",
        "evidence_level": "Open-label, Pilot RCT",
        "highest_citation": "Osou 2023 (J Neurol) -- 20 citations; first TPS PD retrospective n=20",
        "year_range": "2021-2026",
        "key_finding": "Motor dexterity improved in sham-controlled RCT; EEG cortical oscillatory changes documented; foot+brain combined protocol",
        "top_rct_ref": "TPS Enhances Dexterity in PD -- Randomized Sham-Controlled Clinical Trial 2025",
        "journal": "Journal of Neurology / CNS Neurosci Ther / Brain Stimulation",
        "regulatory": "Investigational (research use)",
        "notes": "First RCT 2025 confirms efficacy. 10,000 pulses/session (8000 brain + 2000 foot). 4 Hz PRF.",
    },
    "MCI / Mild Neurocognitive Disorder": {
        "total_papers": "7+",
        "rcts": "0 (open-label trials)",
        "evidence_level": "Open-label, Observational, 24-wk trial",
        "highest_citation": "Nayeri 2023 (Annals Clin Transl Neurol) -- 19 citations",
        "year_range": "2021-2026",
        "key_finding": "Significant cognitive improvement; brain connectivity modulation on fMRI; 24-week trial shows sustained benefit",
        "top_rct_ref": "24-week TPS efficacy & safety trial in MCI (2025); Biomedicines 2024 connectivity paper",
        "journal": "Annals Clinical & Translational Neurology / Biomedicines",
        "regulatory": "Investigational",
        "notes": "7 papers. Evidence gap: no sham-controlled RCT yet for MCI specifically. 6-session standard course.",
    },
    "Depression (MDD)": {
        "total_papers": "14+",
        "rcts": "6 RCTs/protocols",
        "evidence_level": "Pilot RCT + Multiple 2025 RCTs",
        "highest_citation": "Keeser 2023 (IJERPH) -- 34 citations; Pilot RCT n=30",
        "year_range": "2022-2026",
        "key_finding": "Significant mood improvement in pilot RCT; Nucleus Accumbens target explored for TRD; 3 RCTs at CINP 2025",
        "top_rct_ref": "TPS for MDD -- Randomized Double-Blind Sham-Controlled Pilot Trial 2025 (Int J Neuropsychopharmacol)",
        "journal": "IJERPH / Int J Neuropsychopharmacol / Frontiers Neurology",
        "regulatory": "Investigational",
        "notes": "Rapidly expanding evidence base. 6000 pulses, L-DLPFC + DMN. 3 separate RCTs in 2025 alone.",
    },
    "ADHD": {
        "total_papers": "2+",
        "rcts": "2 RCTs",
        "evidence_level": "Double-blind, Sham-controlled RCT",
        "highest_citation": "Frontiers Neurology 2024 -- 11 citations; Adolescent pilot RCT",
        "year_range": "2023-2026",
        "key_finding": "Significant ADHD symptom reduction in adolescents; double-blind sham-controlled; well-tolerated",
        "top_rct_ref": "Efficacy and safety of TPS in young adolescents with ADHD -- pilot RCT 2024 (Frontiers Neurol)",
        "journal": "Frontiers in Neurology",
        "regulatory": "Investigational",
        "notes": "2 RCTs/protocols. Adolescent population. Prefrontal targeting. 6000 pulses, 5 Hz PRF.",
    },
    "Autism Spectrum Disorder (ASD)": {
        "total_papers": "4+",
        "rcts": "2 RCTs/protocols",
        "evidence_level": "Double-blind, Sham-controlled RCT",
        "highest_citation": "Beisteiner 2023 (Brain Communications) -- 21 citations; Double-blind RCT",
        "year_range": "2022-2026",
        "key_finding": "Significant ASD symptom reduction; brain network connectivity changes documented; Asian RCT confirms in independent cohort",
        "top_rct_ref": "Effects of TPS on ASD: double-blind, randomized, sham-controlled trial -- Brain Communications 2023",
        "journal": "Brain Communications / Autism Research",
        "regulatory": "Investigational",
        "notes": "4 RCTs/protocols. Strongest NIBS evidence for ASD to date. 6000 pulses, prefrontal + parietal.",
    },
    "Chronic Pain": {
        "total_papers": "2+",
        "rcts": "0",
        "evidence_level": "Case series, SA Perspective",
        "highest_citation": "SA Perspective 2025 (Brain Stimulation)",
        "year_range": "2023-2026",
        "key_finding": "Pain reduction reported; NAc stimulation case in TRD/pain; emerging South American clinical use",
        "top_rct_ref": "TPS in AD, PD, and chronic pain: South American perspective (Brain Stimulation 2025)",
        "journal": "Brain Stimulation",
        "regulatory": "Investigational",
        "notes": "Very early stage for pain. LIFU/tFUS has stronger pain evidence (15+ papers). Consider TPS as adjunct.",
    },
    "DOC (Disorders of Consciousness)": {
        "total_papers": "2+",
        "rcts": "0",
        "evidence_level": "Case series",
        "highest_citation": "Emerging DOC literature 2024",
        "year_range": "2024-2026",
        "key_finding": "Preliminary case data; frontoparietal consciousness network targeted",
        "top_rct_ref": "TPS Opens New Horizons in Psychiatric Patients 2025 (covers DOC)",
        "journal": "Emerging journals",
        "regulatory": "Investigational",
        "notes": "Very early stage. Limited to case reports and emerging single-arm data.",
    },
}

# LIFU_EVIDENCE[target_name] = same structure
LIFU_EVIDENCE = {
    "Primary Visual Cortex": {
        "total_papers": "38+ (tFUS)",
        "rcts": "1 (non-rct exp)",
        "evidence_level": "Non-RCT Experimental",
        "highest_citation": "Lee 2016 (Scientific Reports) -- 376 citations; first human tFUS V1 stimulation",
        "year_range": "2012-2026",
        "key_finding": "FUS sonication of V1 elicits phosphene perception and fMRI activation; EEG evoked potentials confirmed; safe profile",
        "top_rct_ref": "Lee et al 2016 Scientific Reports -- Transcranial FUS Stimulation of Human Primary Visual Cortex",
        "journal": "Scientific Reports",
        "regulatory": "Investigational",
        "notes": "Landmark paper. mm-level spatial selectivity confirmed. Individual variability in acoustic focus documented.",
    },
    "Primary Somatosensory Cortex": {
        "total_papers": "38+",
        "rcts": "0",
        "evidence_level": "Non-RCT Experimental",
        "highest_citation": "Lee 2015 (Scientific Reports) -- 356 citations; image-guided FUS somatosensory",
        "year_range": "2015-2026",
        "key_finding": "Elicits tactile sensations with finger-level anatomical specificity; EEG evoked potentials; safe profile",
        "top_rct_ref": "Lee et al 2015 Scientific Reports -- Image-Guided tFUS Stimulates Human Primary Somatosensory Cortex",
        "journal": "Scientific Reports",
        "regulatory": "Investigational",
        "notes": "356 citations. Neuronavigation-guided. Up to finger-level specificity. Threshold acoustic intensity identified.",
    },
    "Primary Motor Cortex (M1)": {
        "total_papers": "38+",
        "rcts": "0",
        "evidence_level": "Non-RCT Experimental",
        "highest_citation": "Legon 2018 (Scientific Reports) -- 265 citations; concurrent TMS+FUS paradigm",
        "year_range": "2016-2026",
        "key_finding": "FUS inhibits MEP amplitude; attenuates intracortical facilitation; reduces reaction time on simple tasks",
        "top_rct_ref": "Legon et al 2018 Scientific Reports -- Transcranial FUS Neuromodulation of Human Primary Motor Cortex",
        "journal": "Scientific Reports",
        "regulatory": "Investigational",
        "notes": "First human M1 ultrasound neuromodulation. Concurrent TMS+FUS paradigm validated.",
    },
    "Thalamus (deep target)": {
        "total_papers": "38+",
        "rcts": "0",
        "evidence_level": "Non-RCT Experimental",
        "highest_citation": "Kim 2023 (PLOS ONE) -- 18 citations; thalamic + cortical somatosensory stimulation",
        "year_range": "2020-2026",
        "key_finding": "FUS stimulation of VPL thalamus enhances resting-state functional connectivity for >1 hour; neuroplasticity potential",
        "top_rct_ref": "Kim et al 2023 PLOS ONE -- Transcranial FUS Stimulation of Cortical and Thalamic Somatosensory Areas",
        "journal": "PLOS ONE",
        "regulatory": "Investigational",
        "notes": "Deep target proof-of-concept. Connectivity changes lasting >1 hr post-stimulation.",
    },
    "Depression / DLPFC": {
        "total_papers": "10+",
        "rcts": "0",
        "evidence_level": "Open-label, Pilot",
        "highest_citation": "Sanguinetti 2020; Tyler 2019; Reznik 2020",
        "year_range": "2019-2026",
        "key_finding": "Significant mood improvement in open-label studies targeting right IFG/DLPFC; unique deep-brain access advantage",
        "top_rct_ref": "Reznik 2020; Sanguinetti 2020 -- LIFU tFUS for mood modulation",
        "journal": "Multiple journals",
        "regulatory": "Investigational",
        "notes": "10+ papers. Advantage: can reach deeper than TMS. No FDA/CE approval yet for depression.",
    },
    "Chronic Pain / Thalamus": {
        "total_papers": "15+",
        "rcts": "0",
        "evidence_level": "Open-label, Case series",
        "highest_citation": "Lee 2015 (pain); Kim 2018; multiple tFUS pain reviews",
        "year_range": "2015-2026",
        "key_finding": "Noninvasive thalamic pain relay modulation; ACC targeting also studied; unique access to deep pain structures",
        "top_rct_ref": "Lee 2015; systematic review Lee 2024 (Biomed Eng Lett, 22 clinical studies reviewed)",
        "journal": "Multiple journals",
        "regulatory": "Investigational",
        "notes": "15+ papers. Only noninvasive modality that can reach thalamus without surgery. Requires neuronavigation.",
    },
    "Alzheimer's / Hippocampus": {
        "total_papers": "10+",
        "rcts": "0",
        "evidence_level": "Open-label, Mouse RCT",
        "highest_citation": "Leinenga 2015 (Sci Translat Med); Beisteiner 2020; Lee 2024 review (32 citations)",
        "year_range": "2015-2026",
        "key_finding": "FUS can transiently open BBB for amyloid drug delivery; low-intensity neuromodulation distinct from ablation; hippocampal targeting",
        "top_rct_ref": "Lee 2024 Biomedical Eng Letters -- Review of functional neuromodulation in humans using low-intensity tFUS (22 clinical studies)",
        "journal": "Biomedical Engineering Letters / Sci Translat Med",
        "regulatory": "Investigational",
        "notes": "Dual mechanism: neuromodulation + BBB opening for drug delivery. 22 clinical studies reviewed by Lee 2024.",
    },
    "Essential Tremor / VIM": {
        "total_papers": "5+",
        "rcts": "0",
        "evidence_level": "Open-label, Pilot",
        "highest_citation": "Krishna 2017 (JAMA Neurol) -- 247 citations; systematic review tFUS/MRgFUS",
        "year_range": "2014-2026",
        "key_finding": "VIM thalamus targeting inhibits tremor circuits; distinct from high-intensity MRgFUS ablation; neuromodulation mode",
        "top_rct_ref": "Krishna 2017 JAMA Neurology -- Current Therapies, Challenges and Future Directions of tFUS",
        "journal": "JAMA Neurology",
        "regulatory": "Investigational (MRgFUS ablation FDA cleared; neuromodulation investigational)",
        "notes": "Same anatomical target as DBS/MRgFUS but noninvasive neuromodulation mode. 247-citation systematic review.",
    },
}

# STUDY_QUALITY = list of [study_type, count, pct_of_total, tps_specific, significance]
STUDY_QUALITY = [
    ["Non-RCT Experimental", 1037, "34.6%", 28,  "Core mechanistic and proof-of-concept studies"],
    ["RCT",                   166,  "5.5%",  13,  "Highest quality -- 13 TPS-specific RCTs identified (most 2022-2025)"],
    ["Literature Review",     156,  "5.2%",   8,  "Theoretical frameworks and narrative syntheses"],
    ["Non-RCT In Vitro",       89,  "3.0%",   2,  "Cellular/animal mechanistic studies"],
    ["Case Report",            54,  "1.8%",   3,  "Single-patient feasibility data"],
    ["Systematic Review",      46,  "1.5%",   3,  "High-quality evidence synthesis"],
    ["Non-RCT Observational",  32,  "1.1%",   4,  "Real-world retrospective data"],
    ["Meta-analysis",          20,  "0.7%",   1,  "Highest level -- 1 TPS-specific meta-analysis (2025)"],
    ["Total / Unique Papers",1505,  "100%",  62,  "1,505 unique papers after deduplication from 2,994 records"],
]

# CONDITIONS_MATRIX[condition_name] = {modality: paper_count_or_none, ..., "best": str}
CONDITIONS_MATRIX = {
    "Depression (MDD)": {
        "TPS": 14, "TMS": 500, "tDCS": 200, "taVNS": 80, "CES": 30,
        "tACS": 20, "PBM": 10, "PEMF": 15, "LIFU": 12, "tRNS": 3, "DBS": 30,
        "best": "TMS (rTMS/iTBS), tDCS",
    },
    "Alzheimer's/Dementia": {
        "TPS": 31, "TMS": 30, "tDCS": 20, "taVNS": 5, "CES": None,
        "tACS": 15, "PBM": 20, "PEMF": 5, "LIFU": 10, "tRNS": None, "DBS": 5,
        "best": "TPS, TMS + Cognitive Training",
    },
    "Parkinson's Disease": {
        "TPS": 9, "TMS": 80, "tDCS": 15, "taVNS": 10, "CES": None,
        "tACS": 10, "PBM": 10, "PEMF": 5, "LIFU": None, "tRNS": 3, "DBS": 1000,
        "best": "DBS (STN/GPi), TMS",
    },
    "Chronic Pain": {
        "TPS": 5, "TMS": 60, "tDCS": 150, "taVNS": 40, "CES": 35,
        "tACS": 10, "PBM": 10, "PEMF": 15, "LIFU": 15, "tRNS": 5, "DBS": 10,
        "best": "tDCS (M1), TMS (M1)",
    },
    "OCD": {
        "TPS": None, "TMS": 100, "tDCS": 10, "taVNS": 5, "CES": None,
        "tACS": None, "PBM": None, "PEMF": None, "LIFU": 3, "tRNS": None, "DBS": 50,
        "best": "TMS (Deep/H7), DBS (VC/VS)",
    },
    "Anxiety/GAD": {
        "TPS": None, "TMS": 20, "tDCS": 15, "taVNS": 10, "CES": 40,
        "tACS": 5, "PBM": 5, "PEMF": 5, "LIFU": None, "tRNS": None, "DBS": None,
        "best": "CES (Alpha-Stim), taVNS",
    },
    "PTSD": {
        "TPS": None, "TMS": 30, "tDCS": 10, "taVNS": 5, "CES": 10,
        "tACS": None, "PBM": None, "PEMF": None, "LIFU": None, "tRNS": None, "DBS": None,
        "best": "TMS, CES",
    },
    "Insomnia": {
        "TPS": None, "TMS": 5, "tDCS": 5, "taVNS": 10, "CES": 25,
        "tACS": 15, "PBM": None, "PEMF": 5, "LIFU": None, "tRNS": 2, "DBS": None,
        "best": "CES, tACS (Nexalin)",
    },
    "Epilepsy": {
        "TPS": None, "TMS": 20, "tDCS": 15, "taVNS": 50, "CES": None,
        "tACS": None, "PBM": None, "PEMF": 20, "LIFU": 5, "tRNS": None, "DBS": 30,
        "best": "taVNS, DBS (ANT)",
    },
    "Stroke Rehabilitation": {
        "TPS": None, "TMS": 100, "tDCS": 100, "taVNS": 25, "CES": None,
        "tACS": None, "PBM": 10, "PEMF": 20, "LIFU": None, "tRNS": None, "DBS": None,
        "best": "TMS, tDCS",
    },
    "Mild Cognitive Impairment": {
        "TPS": 3, "TMS": 15, "tDCS": 15, "taVNS": None, "CES": None,
        "tACS": 10, "PBM": 5, "PEMF": 5, "LIFU": None, "tRNS": 2, "DBS": None,
        "best": "TPS, TMS, tDCS",
    },
    "Tinnitus": {
        "TPS": None, "TMS": 40, "tDCS": 40, "taVNS": 15, "CES": None,
        "tACS": 8, "PBM": None, "PEMF": None, "LIFU": None, "tRNS": 15, "DBS": None,
        "best": "TMS (1 Hz), tDCS, tRNS",
    },
    "Schizophrenia": {
        "TPS": None, "TMS": 50, "tDCS": 30, "taVNS": None, "CES": None,
        "tACS": 10, "PBM": None, "PEMF": None, "LIFU": 3, "tRNS": 3, "DBS": None,
        "best": "TMS (1 Hz L-TPJ), tDCS",
    },
    "TBI/Concussion": {
        "TPS": None, "TMS": 10, "tDCS": 10, "taVNS": None, "CES": None,
        "tACS": None, "PBM": 25, "PEMF": 10, "LIFU": None, "tRNS": None, "DBS": None,
        "best": "PBM (810 nm), tDCS",
    },
    "Addiction": {
        "TPS": None, "TMS": 30, "tDCS": 30, "taVNS": None, "CES": None,
        "tACS": None, "PBM": None, "PEMF": 3, "LIFU": 3, "tRNS": None, "DBS": 5,
        "best": "TMS, tDCS",
    },
    "ADHD": {
        "TPS": 2, "TMS": 15, "tDCS": 20, "taVNS": None, "CES": None,
        "tACS": 5, "PBM": None, "PEMF": 5, "LIFU": None, "tRNS": None, "DBS": None,
        "best": "tDCS (DLPFC), TMS",
    },
    "Essential Tremor": {
        "TPS": None, "TMS": 10, "tDCS": None, "taVNS": None, "CES": None,
        "tACS": None, "PBM": None, "PEMF": None, "LIFU": 5, "tRNS": None, "DBS": 200,
        "best": "DBS (VIM), LIFU (MRgFUS)",
    },
    "Dystonia": {
        "TPS": None, "TMS": 10, "tDCS": 5, "taVNS": None, "CES": None,
        "tACS": None, "PBM": None, "PEMF": None, "LIFU": None, "tRNS": None, "DBS": 100,
        "best": "DBS (GPi)",
    },
    "Multiple Sclerosis": {
        "TPS": None, "TMS": 15, "tDCS": 10, "taVNS": None, "CES": None,
        "tACS": None, "PBM": None, "PEMF": 10, "LIFU": None, "tRNS": 5, "DBS": None,
        "best": "PEMF, tRNS",
    },
    "Fibromyalgia": {
        "TPS": None, "TMS": 15, "tDCS": 25, "taVNS": 5, "CES": 5,
        "tACS": None, "PBM": None, "PEMF": 5, "LIFU": None, "tRNS": None, "DBS": None,
        "best": "tDCS (M1), TMS",
    },
    "Autism Spectrum Disorder": {
        "TPS": 2, "TMS": 5, "tDCS": 5, "taVNS": None, "CES": None,
        "tACS": None, "PBM": None, "PEMF": None, "LIFU": None, "tRNS": None, "DBS": None,
        "best": "TMS, TPS (emerging)",
    },
    "Disorders of Consciousness": {
        "TPS": 2, "TMS": 5, "tDCS": 10, "taVNS": None, "CES": None,
        "tACS": None, "PBM": None, "PEMF": None, "LIFU": None, "tRNS": None, "DBS": None,
        "best": "TMS, tDCS",
    },
}

# Slug-to-condition-name lookup for the 15 SOZO conditions
SLUG_TO_CONDITION = {
    "parkinsons":   "Parkinson's Disease",
    "depression":   "Depression (MDD)",
    "anxiety":      "Anxiety/GAD",
    "adhd":         "ADHD",
    "alzheimers":   "Alzheimer's/Dementia",
    "stroke_rehab": "Stroke Rehabilitation",
    "tbi":          "TBI/Concussion",
    "chronic_pain": "Chronic Pain",
    "ptsd":         "PTSD",
    "ocd":          "OCD",
    "ms":           "Multiple Sclerosis",
    "asd":          "Autism Spectrum Disorder",
    "long_covid":   None,
    "tinnitus":     "Tinnitus",
    "insomnia":     "Insomnia",
}

# TPS evidence slug map (subset of conditions with TPS data)
TPS_SLUG_MAP = {
    "alzheimers":   "Alzheimer's Disease",
    "parkinsons":   "Parkinson's Disease",
    "depression":   "Depression (MDD)",
    "adhd":         "ADHD",
    "asd":          "Autism Spectrum Disorder (ASD)",
    "chronic_pain": "Chronic Pain",
}


if __name__ == "__main__":
    print(f"TPS conditions: {len(TPS_EVIDENCE)}")
    print(f"LIFU targets: {len(LIFU_EVIDENCE)}")
    print(f"Study quality rows: {len(STUDY_QUALITY)}")
    print(f"Matrix conditions: {len(CONDITIONS_MATRIX)}")
    print(f"Slug mappings: {len(SLUG_TO_CONDITION)}")
