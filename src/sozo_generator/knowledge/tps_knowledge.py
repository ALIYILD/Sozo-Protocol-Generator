"""
TPS Knowledge Library -- Transcranial Pulse Stimulation.

Structured, fully-cited reference module synthesised from open-access
peer-reviewed literature. Importable by condition generators, window
subagents, and document builders. Every value carries a source tag
(PMID / PMC) so generated documents remain fully traceable.

Primary sources (all open-access via PMC / MDPI):
  TPS-001  Beisteiner R et al. 2025   JAMA Psychiatry RCT          PMC11866033 / PMID 40009384
  TPS-002  Beisteiner R et al. 2020   Adv Sci founding pilot        PMID 32042569
  TPS-003  Beisteiner R et al. 2022   Long-term TPS healthy RCT     PMC8760674
  TPS-004  Gozzi L et al. 2023        AD systematic review          PMC10848065 / PMID 37469252
  TPS-005  Tan L et al. 2023          TPS Depression pilot RCT      PMC9915638
  TPS-006  Ren Z et al. 2024          TPS Parkinson retrospective   PMC10896933
  TPS-007  Kwok CC et al. 2023        TPS Mild NCD pilot            PMC10578878
  TPS-008  Mueller P et al. 2025      TPS specificity/params        PMC11871398
  TPS-009  Popescu T et al. 2021      TPS cortical thickness AD     PMID 34671041
  TPS-010  Matt E et al. 2022         TPS depression network AD     PMC8829892

Compiled: 2026-04-04.
"""
from __future__ import annotations

# ===========================================================================
# 1 -- DEVICE SPECIFICATIONS
# ===========================================================================

TPS_DEVICE_SPECS: dict[str, dict] = {
    "NEUROLITH": {
        "manufacturer": "Storz Medical AG, Tagerwilen, Switzerland",
        "full_name": "NEUROLITH TPS System",
        "regulatory_status": "CE-marked (Europe); FDA 510(k) clearance pending as of 2024",
        "navigated": True,
        "navigation_type": "MRI-based real-time neuronavigation with infrared camera tracking",
        "pulse_type": "Single ultrashort positive-pressure acoustic (shockwave) pulses",
        "pulse_duration_microseconds": 3,
        "frequency_range_hz": "1-5 (clinically approved); published studies use 3-5 Hz",
        "energy_flux_density_range_mj_mm2": "0.20-0.25",
        "energy_flux_density_max_4hz": 0.25,
        "peak_positive_pressure_MPa": 25,
        "ispta_mw_cm2": 100,
        "isppa_w_cm2": 111,
        "mechanical_index": 10.95,
        "frequency_band_mhz": "0.05-0.45 (multifrequency acoustic; not diagnostic ultrasound range)",
        "below_skull_intensity_mw_cm2": 24,
        "max_pulses_per_session": 6000,
        "focal_depth_cm": "up to 8",
        "ispta_limit_cm2": 0.1,
        "source_pmids": ["40009384", "PMC11871398", "PMC8760674"],
    },
    "DUOLITH_SD1_MODIFIED": {
        "manufacturer": "Storz Medical AG",
        "full_name": "Modified Duolith SD1 (prototype; early Vienna trials)",
        "notes": "Predecessor to NEUROLITH. Used in Beisteiner 2020 (PMID 32042569) and JAMA 2025 RCT (PMC11866033).",
        "source_pmids": ["32042569", "40009384"],
    },
}


# ===========================================================================
# 2 -- MECHANISM OF ACTION
# ===========================================================================

TPS_MECHANISM: dict[str, str] = {
    "overview": (
        "TPS delivers single ultrashort (3 microsecond) acoustic pressure pulses to focal brain "
        "regions via MRI-navigated targeting. Unlike tDCS/TMS (electrical/magnetic), TPS uses "
        "mechanical energy (shockwaves) that penetrate the intact skull to depths up to 8 cm, "
        "enabling deep cortical and subcortical targeting. [PMC11871398, PMID 32042569]"
    ),
    "cellular_mechanisms": (
        "1. MECHANOSENSITIVE ION CHANNELS: Acoustic pressure activates Piezo1/TRPV4, triggering "
        "calcium influx and neuroplasticity cascades. [MDPI 2035-8377/17/11/188]\n\n"
        "2. BDNF UPREGULATION: TPS upregulates BDNF in hippocampal/cortical neurons, enhancing "
        "synaptic plasticity and neurogenesis. [MDPI 2035-8377/17/11/188]\n\n"
        "3. VEGF/ANGIOGENESIS: Promotes VEGF-mediated angiogenesis, improving cerebral perfusion. "
        "[MDPI 2035-8377/17/11/188]\n\n"
        "4. CORTICAL EXCITABILITY: Increases cortical/corticospinal excitability (LTP-like plasticity "
        "induction). [MDPI 2035-8377/17/11/188]\n\n"
        "5. FUNCTIONAL CONNECTIVITY: Post-TPS fMRI shows increased network global efficiency "
        "(healthy: PMC8760674; AD: PMC11866033; PD: PMC10896933).\n\n"
        "6. WHITE MATTER INTEGRITY: DTI reduced axial diffusivity in stimulated tracts, suggesting "
        "improved axonal organisation. [PMC8760674]"
    ),
    "network_effects": (
        "TPS modulates large-scale networks proportional to the targeted cortical node:\n"
        "  DLPFC targeting       -> CEN upregulation, DMN decoupling (cognitive/mood effects)\n"
        "  Hippocampus/parahippo -> memory network enhancement (AD, MCI)\n"
        "  Precuneus             -> DMN modulation, default-mode connectivity normalisation\n"
        "  Motor/SMA             -> SMN facilitation (Parkinsons, stroke)\n"
        "  Multifocal global     -> distributed connectivity enhancement (MCI, dementia)\n"
        "[PMC11866033, PMC10896933, PMC8760674, PMC10848065]"
    ),
    "distinction_from_other_modalities": (
        "tDCS/tACS: no electrodes, no electrical current -- TPS is mechanical not electrical.\n"
        "TMS/iTBS:  no coil, no magnetic field -- TPS is acoustic not electromagnetic.\n"
        "tPCS:      ELECTRICAL stimulation -- fundamentally different from TPS (acoustic). "
        "Do NOT cite tPCS studies as TPS evidence. [PMC11871398]\n"
        "Diagnostic US: TPS up to 25 MPa vs diagnostic <1 MPa; single pulses; neuromodulatory not imaging.\n"
        "Key advantage: deeper penetration (up to 8 cm vs ~2-3 cm tDCS), no skull heating, "
        "no electrode-site skin reactions, MRI-navigated precision targeting."
    ),
    "time_course": (
        "ACUTE:  Single-session excitability effects detectable immediately post-stimulation.\n"
        "SHORT:  Cognitive/mood improvements at 1-2 week post-treatment assessment.\n"
        "MEDIUM: Sustained at 3-month follow-up in AD [PMC11866033], depression [PMC9915638], "
        "and MCI [PMC10578878].\n"
        "LONG:   DTI/connectivity changes persist >=1 week after 3 sessions [PMC8760674]. "
        "Clinical durability at 6-12 months: limited data currently."
    ),
}


# ===========================================================================
# 3 -- STANDARD PARAMETER RANGES (cross-study consensus)
# ===========================================================================

TPS_PARAMETER_STANDARDS: dict = {
    "pulse_duration_microseconds": 3,
    "energy_flux_density_mj_mm2": {
        "minimum": 0.20,
        "standard": 0.25,
        "maximum_approved": 0.25,
        "note": "0.20 used in some AD trials; 0.25 standard for neurological conditions",
    },
    "pulse_repetition_frequency_hz": {
        "range": "1-5",
        "approved_ceiling": 5,
        "standard_clinical": 4,
        "ad_trials": 5,
        "depression_trials": "3-4",
        "parkinson_trials": 4,
        "healthy_research": 4,
        "warning": (
            "Above 5 Hz is outside current clinical approval. "
            "Do NOT conflate with tPCS frequencies (6-10 Hz). [PMC11871398]"
        ),
    },
    "pulses_per_session": {
        "minimum": 300,
        "standard_psychiatric": 1800,
        "standard_neurological": 4000,
        "maximum_approved": 6000,
        "by_condition": {
            "alzheimers": 6000,
            "mci": 6000,
            "depression": 300,
            "parkinson": 4000,
            "healthy_research": 1000,
        },
    },
    "sessions_per_week": 3,
    "standard_course_weeks": 2,
    "standard_total_sessions": 6,
    "extended_total_sessions": 10,
    "navigation": "MRI-based real-time neuronavigation mandatory for all clinical applications",
    "depth_penetration_cm": "up to 8",
    "source_pmids": ["40009384", "PMC9915638", "PMC10896933", "PMC8760674", "PMC10578878"],
}


# ===========================================================================
# 4 -- PROTOCOL BY CONDITION
# ===========================================================================

TPS_PROTOCOL_BY_CONDITION: dict[str, dict] = {

    "alzheimers": {
        "condition": "Alzheimers Disease / Mild-to-Moderate Dementia",
        "icd10": "G30",
        "indication_status": "CE-marked (Europe); off-label elsewhere",
        "device": "NEUROLITH (Storz Medical AG)",
        "navigation": "MRI-based real-time neuronavigation",
        "parameters": {
            "pulse_duration_us": 3,
            "energy_flux_density_mj_mm2": 0.20,
            "pulse_repetition_hz": 5,
            "pulses_per_session": 6000,
            "sessions_per_week": 3,
            "total_sessions": 6,
            "course_duration_weeks": 2,
        },
        "brain_targets": [
            "Bilateral dorsolateral prefrontal cortex (DLPFC)",
            "Inferior frontal cortex (bilateral)",
            "Lateral parietal cortex (bilateral, extending to Wernicke area)",
            "Precuneus cortex (bilateral)",
        ],
        "target_rationale": (
            "Targets cover core DMN nodes disrupted in AD: DLPFC (executive control), inferior frontal "
            "(language/verbal memory), lateral parietal (visuospatial/episodic memory), precuneus "
            "(self-referential processing, memory retrieval). Bilateral targeting reflects bilateral "
            "AD network disruption. [PMC11866033]"
        ),
        "primary_outcomes": ["CERAD Corrected Total Score (CTS)", "ADAS-Cog", "MoCA/MMSE"],
        "secondary_outcomes": ["BDI-II", "GDS", "fMRI memory activation", "Resting-state connectivity", "ADL"],
        "key_evidence": {
            "best_study": "Beisteiner et al. 2025 JAMA Psychiatry RCT (PMC11866033)",
            "n": 60,
            "design": "Randomised double-blind sham-controlled crossover",
            "primary_result": (
                "Younger pts (<=70yr, n=26): CERAD CTS +3.91 vs sham -1.83 (p=.005, np2=0.16). "
                "Overall ITT (n=60): ns (p=.68). Age x treatment: r=-0.409 (p=.001)."
            ),
            "depression_result": "BDI-II significantly reduced (p=.008, np2=0.23); older patients p=.02",
            "fmri_result": "Dorsal attention network connectivity increased (p=.03); precuneus/frontal activation up",
            "safety": "Well-tolerated; all AEs mild-moderate, reversible; no serious adverse events",
        },
        "source_pmids": ["40009384", "32042569", "37469252", "PMC10848065"],
        "evidence_level": "HIGH",
        "evidence_note": "1 crossover RCT + 4 open-label pilots + systematic review (N=99 across 5 trials)",
    },

    "depression": {
        "condition": "Major Depressive Disorder",
        "icd10": "F32",
        "indication_status": "Off-label; pilot RCT evidence only",
        "device": "NEUROLITH (Storz Medical AG)",
        "navigation": "MRI-based real-time neuronavigation with infrared camera",
        "parameters": {
            "pulse_duration_us": 3,
            "energy_flux_density_mj_mm2": "0.20-0.25",
            "pulse_repetition_hz": "3-4",
            "pulses_per_session": 300,
            "sessions_per_week": 3,
            "total_sessions": 6,
            "course_duration_weeks": 2,
        },
        "brain_targets": ["Left dorsolateral prefrontal cortex (L-DLPFC)"],
        "target_rationale": (
            "L-DLPFC is consistently hypoactive in MDD and the primary target of evidence-based "
            "prefrontal neuromodulation. TPS excitation upregulates CEN and reduces DMN hyperactivation "
            "via cortico-cortical connectivity. [PMC9915638]"
        ),
        "primary_outcomes": ["HDRS-17"],
        "secondary_outcomes": ["MoCA", "SHAPS (anhedonia)", "Lawton IADL", "TMT A+B", "Digit Span"],
        "key_evidence": {
            "best_study": "Tan et al. 2023 pilot RCT (PMC9915638)",
            "n": 30,
            "design": "Single-blind RCT vs waitlist control",
            "primary_result": "HDRS-17 mean difference -6.60 (p=.02, Cohen d=-0.93); 3-month: d=-1.35",
            "cognitive_result": "MoCA d=0.88 post, d=1.20 at 3 months",
            "anhedonia_result": "SHAPS d=-0.79 post, d=-0.81 at 3 months",
            "safety": "Headache 4%; nausea 1pt (resolved <2h); no serious AEs; no MRI abnormalities",
        },
        "limitations": [
            "Single-blind (not double-blind sham-controlled)",
            "Waitlist comparator not active sham TPS",
            "N=30 underpowered; pilot only",
            "Single centre, predominantly ethnic Chinese sample",
        ],
        "source_pmids": ["PMC9915638"],
        "evidence_level": "LOW",
        "evidence_note": "1 single-blind pilot RCT. Large effect sizes (d=0.93-1.35) require sham-controlled replication.",
    },

    "alzheimers_depression": {
        "condition": "Depressive Symptoms in Alzheimers Disease",
        "icd10": "F06.32",
        "indication_status": "Off-label; secondary-outcome evidence from AD trials",
        "device": "NEUROLITH / Modified Duolith SD1",
        "parameters": {
            "pulse_duration_us": 3,
            "energy_flux_density_mj_mm2": 0.20,
            "pulse_repetition_hz": 5,
            "pulses_per_session": 6000,
            "sessions_per_week": 3,
            "total_sessions": 6,
        },
        "brain_targets": [
            "Bilateral DLPFC",
            "Lateral parietal cortex",
            "Precuneus",
            "Left frontal orbital cortex (vmPFC) -- targeted in Matt 2022 for depression network",
        ],
        "key_evidence": {
            "best_study": "Beisteiner 2025 JAMA Psychiatry (PMC11866033) -- secondary outcome",
            "primary_result": "BDI-II significantly reduced (p=.008, np2=0.23)",
            "mechanism_note": (
                "Matt et al. 2022 (PMC8829892): TPS reduced AD depression by decreasing "
                "vmPFC-SN functional connectivity -- normalising the hyperconnected vmPFC-salience circuit."
            ),
        },
        "source_pmids": ["40009384", "PMC8829892"],
        "evidence_level": "MEDIUM",
        "evidence_note": "Multiple AD trials show consistent depression secondary outcomes; fMRI mechanistic evidence available.",
    },

    "parkinson": {
        "condition": "Parkinsons Disease -- Motor Symptoms",
        "icd10": "G20",
        "indication_status": "Off-label; retrospective analysis evidence",
        "device": "NEUROLITH (Storz Medical AG)",
        "navigation": "Real-time neuronavigation with infrared tracking",
        "parameters": {
            "pulse_duration_us": 3,
            "energy_flux_density_mj_mm2": 0.25,
            "pulse_repetition_hz": 4,
            "pulses_per_session": 4000,
            "sessions_total": 10,
            "sessions_per_week": 5,
            "course_duration_weeks": 2,
            "session_duration_minutes": "30-45",
        },
        "brain_targets": [
            "Primary sensorimotor cortex (M1/S1)",
            "Supplementary motor area (SMA)",
            "Cingulate motor area (CMA)",
            "Left DLPFC (optional add-on when depression co-present)",
        ],
        "target_rationale": (
            "PD motor deficits reflect basal ganglia-thalamocortical loop dysfunction affecting M1 and SMA. "
            "TPS targets these cortical motor nodes to upregulate SMN excitability and restore cortical drive. "
            "CMA targeting addresses bradykinesia and gait initiation. [PMC10896933]"
        ),
        "primary_outcomes": ["MDS-UPDRS Part III (motor score)"],
        "secondary_outcomes": ["TUG", "FOGQ", "BDI/GDS"],
        "key_evidence": {
            "best_study": "Ren et al. 2024 retrospective (PMC10896933)",
            "n": 20,
            "design": "Open-label retrospective uncontrolled",
            "primary_result": (
                "UPDRS-III: 16.70->12.95 (p<0.001, Cohen d=1.38); "
                "19/20 patients improved; 7/20 achieved clinically meaningful >=5-point improvement"
            ),
            "safety": "65% mild AEs: fatigue 50%, headache 30%, dizziness 30%; all resolved <24h; no serious AEs",
        },
        "limitations": [
            "Uncontrolled open-label retrospective -- high placebo susceptibility",
            "N=20; single centre",
            "No sham arm",
            "Mixed disease severity; no Hoehn-Yahr stratification",
        ],
        "source_pmids": ["PMC10896933"],
        "evidence_level": "LOW",
        "evidence_note": "Preliminary retrospective data only. Large effect (d=1.38) but no blinded control. RCT urgently needed.",
    },

    "mci": {
        "condition": "Mild Neurocognitive Disorder / Mild Cognitive Impairment",
        "icd10": "F06.70",
        "indication_status": "Off-label; open-label pilot evidence",
        "device": "NEUROLITH (Storz Medical AG)",
        "navigation": "MRI-based real-time neuronavigation",
        "parameters": {
            "pulse_duration_us": 3,
            "energy_flux_density_mj_mm2": "0.20-0.25",
            "pulse_repetition_hz": "4-5",
            "pulses_per_session": 6000,
            "sessions_total": 6,
            "sessions_per_week": 3,
            "course_duration_weeks": 2,
        },
        "brain_targets": [
            "Global multifocal distribution: frontal, parietal, temporal, and occipital lobes",
        ],
        "target_rationale": (
            "MCI involves distributed early network disruption across frontal executive, "
            "temporal-parietal memory, and attention networks. Global multifocal approach "
            "targets all at-risk circuits simultaneously. [PMC10578878]"
        ),
        "primary_outcomes": ["HK-MoCA (Hong Kong Montreal Cognitive Assessment)"],
        "secondary_outcomes": ["Verbal fluency (30-sec)", "Stroop interference", "IADL", "TMT", "Digit Span"],
        "key_evidence": {
            "best_study": "Kwok et al. 2023 open-label pilot (PMC10578878)",
            "n": 19,
            "design": "Open-label interventional with TAU comparator period",
            "primary_result": "HK-MoCA improved post-intervention and 12-week follow-up (F(3,54)=4.99, p=.004)",
            "other_results": "Verbal fluency p=.041; Stroop p=.023; IADL p=.050",
            "safety": "No severe adverse effects reported",
        },
        "source_pmids": ["PMC10578878"],
        "evidence_level": "LOW",
        "evidence_note": "Single open-label pilot N=19. Requires sham-controlled RCT.",
    },

    "healthy_research": {
        "condition": "Healthy Participants (Neuroplasticity Research)",
        "indication_status": "Research only -- not a clinical indication",
        "device": "NEUROLITH (Storz Medical AG)",
        "parameters": {
            "pulse_duration_us": 3,
            "energy_flux_density_mj_mm2": 0.25,
            "pulse_repetition_hz": 4,
            "pulses_per_session": 1000,
            "sessions_total": 3,
            "sessions_per_week": 3,
        },
        "brain_targets": [
            "Left postcentral gyrus (primary somatosensory cortex -- right hand representation)",
        ],
        "key_evidence": {
            "best_study": "Beisteiner et al. 2022 (PMC8760674)",
            "n": 12,
            "design": "Randomised sham-controlled crossover (healthy volunteers)",
            "neuroimaging_results": [
                "Increased global efficiency left sensorimotor network (p=0.040)",
                "Enhanced coupling: precentral gyrus, postcentral gyrus, superior parietal lobule",
                "Reduced axial diffusivity left somatosensory/motor white matter (p=0.034-0.038; 10-11/12 participants)",
                "No structural volumetric changes (VBM negative)",
                "Effects persisted >=1 week post-stimulation",
            ],
            "safety": "No bleeds, oedema, or lesions on MRI; transient scalp sensations 2-3/10",
        },
        "source_pmids": ["PMC8760674"],
        "evidence_level": "MEDIUM",
        "evidence_note": "Gold-standard neuroimaging design; demonstrates mechanism but not clinical efficacy.",
    },
}

# Alias for backwards compatibility
TPS_EVIDENCE_BY_CONDITION = TPS_PROTOCOL_BY_CONDITION


# ===========================================================================
# 5 -- SAFETY PROFILE (cross-study synthesis)
# ===========================================================================

TPS_SAFETY_PROFILE: dict = {
    "overall_safety_statement": (
        "TPS has a consistent mild-to-moderate adverse event profile across all published studies "
        "(N>150 patients and healthy participants). No serious adverse events directly attributable "
        "to TPS have been reported. No structural MRI changes detected in any study. All AEs were "
        "transient, resolving within 24 hours. [PMC11866033, PMC9915638, PMC10896933, PMC8760674]"
    ),
    "adverse_events": {
        "headache": {
            "incidence_percent": "4-30",
            "severity": "Mild",
            "duration": "<24h",
            "management": "Simple analgesia if required; dose reduction if recurrent",
            "source": "PMC11866033/PMC9915638/PMC10896933",
        },
        "fatigue": {
            "incidence_percent": "2-50",
            "severity": "Mild",
            "duration": "<24h",
            "note": "High PD incidence (50%) may reflect disease state not TPS; AD RCT 2%",
            "source": "PMC10896933/PMC11866033",
        },
        "dizziness": {
            "incidence_percent": "5-30",
            "severity": "Mild",
            "duration": "Transient",
            "source": "PMC10896933",
        },
        "scalp_pressure_pain": {
            "incidence_percent": "8-17",
            "severity": "Mild; 2-3/10 VAS",
            "duration": "Session only",
            "management": "Adjust transducer pressure; optimise coupling gel",
            "source": "PMC8760674/32042569",
        },
        "nausea": {
            "incidence_percent": "1-4",
            "severity": "Mild",
            "duration": "<2h",
            "source": "PMC9915638/37469252",
        },
        "transient_mood_change": {
            "incidence_percent": "3-12",
            "severity": "Mild-moderate",
            "note": "Monitor mood at every session; resolved spontaneously in all cases",
            "source": "PMC11866033",
        },
        "neck_shoulder_pain": {
            "incidence_percent": "7",
            "severity": "Mild",
            "note": "Likely positioning-related; not attributable to TPS energy delivery",
            "source": "PMC11866033",
        },
    },
    "serious_adverse_events": (
        "None directly attributable to TPS in any published study. "
        "One mild TIA occurred in JAMA RCT (PMID 40009384) during washout after sham cycle -- unlikely causal."
    ),
    "absolute_contraindications": [
        "Metallic implants in stimulation pathway (pacemakers, cochlear implants, DBS, aneurysm clips, metal skull fragments)",
        "Skull defects or craniectomy at targeted stimulation sites",
        "Active CNS malignancy",
        "Active uncontrolled epilepsy (relative; neurologist clearance required)",
        "Pregnancy (insufficient safety data)",
        "Therapeutic anticoagulation (relative contraindication)",
        "Open wounds or skin lesions at transducer contact sites on scalp",
        "Severe agitation preventing 30-45 min stillness",
    ],
    "monitoring_requirements": [
        "Mood VAS at every session (critical for psychiatric indications)",
        "Headache/pain NRS 0-10 at every session",
        "Structural MRI before initiation -- required for neuronavigation and contraindication check",
        "Follow-up MRI at 6 months if any neurological change during treatment",
    ],
    "mri_compatibility": (
        "TPS is fully MRI-compatible (external device; no implant; no metal used during stimulation). "
        "Standard pre-treatment structural MRI required for neuronavigation. No post-session MRI restrictions."
    ),
    "source_pmids": ["40009384", "PMC9915638", "PMC10896933", "PMC8760674", "PMC10578878"],
}


# ===========================================================================
# 6 -- COMPLETE REFERENCE LIST
# ===========================================================================

TPS_REFERENCES: list[dict] = [
    {
        "ref_id": "TPS-001",
        "authors": "Beisteiner R, Matt E, Fan C, et al.",
        "year": 2025,
        "title": "Ultrasound Neuromodulation With Transcranial Pulse Stimulation in Alzheimer Disease: A Randomized Clinical Trial",
        "journal": "JAMA Psychiatry",
        "pmid": "40009384",
        "pmc": "PMC11866033",
        "doi": "10.1001/jamapsychiatry.2024.4876",
        "evidence_level": "highest",
        "study_type": "RCT double-blind sham-controlled crossover",
        "n": 60,
        "key_finding": "TPS improved cognition in younger AD patients (<=70yr) and reduced depression; fMRI dorsal attention network enhanced",
    },
    {
        "ref_id": "TPS-002",
        "authors": "Beisteiner R, Holler Y, Goldenstedt C, et al.",
        "year": 2020,
        "title": "Transcranial Pulse Stimulation with Ultrasound in Alzheimers Disease -- A New Navigated Focal Brain Therapy",
        "journal": "Advanced Science",
        "pmid": "32042569",
        "doi": "10.1002/advs.201902583",
        "evidence_level": "low",
        "study_type": "Open-label pilot",
        "n": 35,
        "key_finding": "First TPS AD study: CERAD and depression improved; fMRI hippocampal/parietal connectivity increased; 3-month sustained",
    },
    {
        "ref_id": "TPS-003",
        "authors": "Beisteiner R, Matt E, Fischmeister FPS, et al.",
        "year": 2022,
        "title": "First evidence of long-term effects of transcranial pulse stimulation (TPS) on the human brain",
        "journal": "NeuroImage",
        "pmc": "PMC8760674",
        "evidence_level": "medium",
        "study_type": "Randomised sham-controlled crossover (healthy volunteers)",
        "n": 12,
        "key_finding": "TPS increased sensorimotor network connectivity and reduced axial diffusivity (DTI); effects persisted >=1 week",
    },
    {
        "ref_id": "TPS-004",
        "authors": "Gozzi L, Balzarro B, Pini LA, et al.",
        "year": 2023,
        "title": "Transcranial pulse stimulation in Alzheimers disease",
        "journal": "Ageing Research Reviews",
        "pmid": "37469252",
        "pmc": "PMC10848065",
        "evidence_level": "medium",
        "study_type": "Systematic review (5 studies, N=99)",
        "key_finding": "TPS consistently improved cognition and depression across 5 AD trials; all AEs reversible",
    },
    {
        "ref_id": "TPS-005",
        "authors": "Tan L, Chan ACM, Tse ACY, et al.",
        "year": 2023,
        "title": "Effects of Transcranial Pulse Stimulation (TPS) on Adults with Symptoms of Depression -- A Pilot Randomized Controlled Trial",
        "journal": "Brain Sciences",
        "pmc": "PMC9915638",
        "evidence_level": "low",
        "study_type": "Single-blind RCT vs waitlist control",
        "n": 30,
        "key_finding": "HDRS-17 d=0.93 (p=.02); sustained d=1.35 at 3 months; cognition, anhedonia, functioning improved",
    },
    {
        "ref_id": "TPS-006",
        "authors": "Ren Z, Shi Z, He C, et al.",
        "year": 2024,
        "title": "Novel ultrasound neuromodulation therapy with TPS in Parkinsons disease: a first retrospective analysis",
        "journal": "Frontiers in Neurology",
        "pmc": "PMC10896933",
        "evidence_level": "low",
        "study_type": "Open-label retrospective uncontrolled",
        "n": 20,
        "key_finding": "UPDRS-III significantly improved (d=1.38); 19/20 patients improved; AEs mild and transient",
    },
    {
        "ref_id": "TPS-007",
        "authors": "Kwok CC, Chan ACM, Ho TH, et al.",
        "year": 2023,
        "title": "Transcranial pulse stimulation in the treatment of mild neurocognitive disorders",
        "journal": "Brain Sciences",
        "pmc": "PMC10578878",
        "evidence_level": "low",
        "study_type": "Open-label interventional pilot",
        "n": 19,
        "key_finding": "MoCA, verbal fluency, Stroop, and IADL improved; effects maintained at 12-week follow-up",
    },
    {
        "ref_id": "TPS-008",
        "authors": "Mueller P, Mueller NG, et al.",
        "year": 2025,
        "title": "Clarifying the Specificity of Transcranial Pulse Stimulation in Neuromodulatory-Based Therapeutic Applications",
        "journal": "Annals of Neurology",
        "pmc": "PMC11871398",
        "evidence_level": "medium",
        "study_type": "Technical letter / parameter clarification",
        "key_finding": "Canonical TPS parameters: 3 us pulse, 0.2-0.25 mJ/mm2, 1-5 Hz. Distinguishes TPS (acoustic) from tPCS (electrical).",
    },
    {
        "ref_id": "TPS-009",
        "authors": "Popescu T, Pernet C, Beisteiner R.",
        "year": 2021,
        "title": "Transcranial ultrasound pulse stimulation reduces cortical atrophy in Alzheimers patients",
        "journal": "Alzheimers and Dementia: Translational Research",
        "pmid": "34671041",
        "evidence_level": "low",
        "study_type": "Open-label pilot",
        "n": 17,
        "key_finding": "Cortical thickness increases in DMN regions post-TPS; first structural evidence of TPS-induced neuroplasticity in AD",
    },
    {
        "ref_id": "TPS-010",
        "authors": "Matt E, Grab C, Sladky R, et al.",
        "year": 2022,
        "title": "TPS alleviated depressive symptoms in AD patients on state-of-the-art treatment",
        "journal": "Alzheimers and Dementia: Translational Research",
        "pmc": "PMC8829892",
        "evidence_level": "low",
        "study_type": "Open-label pilot with fMRI",
        "n": 18,
        "key_finding": "TPS reduced AD depression by decreasing vmPFC-SN connectivity; fMRI mechanistic evidence",
    },
]


# ===========================================================================
# 7 -- ACCESSOR FUNCTIONS (for condition generators and window agents)
# ===========================================================================

def get_tps_protocol(condition_slug: str) -> dict | None:
    """
    Return TPS protocol dict for a condition slug, or None if not evidenced.

    Supported slugs:
        'alzheimers', 'depression', 'alzheimers_depression',
        'parkinson', 'mci', 'healthy_research'
    """
    return TPS_PROTOCOL_BY_CONDITION.get(condition_slug)


def get_tps_evidence(condition_slug: str) -> dict | None:
    """Return the key_evidence sub-dict for a condition slug."""
    p = TPS_PROTOCOL_BY_CONDITION.get(condition_slug)
    return p.get("key_evidence") if p else None


def get_tps_references_for_condition(condition_slug: str) -> list[dict]:
    """Return TPS_REFERENCES filtered to those relevant for a condition."""
    p = TPS_PROTOCOL_BY_CONDITION.get(condition_slug)
    if not p:
        return []
    pmids = set(p.get("source_pmids", []))
    return [
        r for r in TPS_REFERENCES
        if r.get("pmid") in pmids or r.get("pmc") in pmids
    ]


def get_tps_parameter_table_rows() -> list[list[str]]:
    """
    Return parameter rows ready for add_clinical_table() in document builders.
    Format: [[Parameter, Value, Source], ...]
    """
    return [
        ["Pulse type",            "Single ultrashort positive-pressure acoustic (shockwave) pulse", "PMC11871398"],
        ["Pulse duration",        "3 microseconds (us)",                                             "PMC11871398"],
        ["Energy flux density",   "0.20-0.25 mJ/mm2 (max 0.25 mJ/mm2 at 4 Hz)",                   "PMC11871398"],
        ["Pulse repetition freq", "1-5 Hz (clinical approval); standard 4-5 Hz",                    "PMC11871398"],
        ["Max pulses/session",    "6,000",                                                           "PMC11866033"],
        ["Focal depth",           "Up to 8 cm (skull-penetrating)",                                 "MDPI 2035-8377"],
        ["Peak pressure",         "Up to 25 MegaPascal",                                            "PMC11871398"],
        ["ISPTA",                 "100 mW/cm2",                                                     "PMC8760674"],
        ["Navigation",            "MRI-based real-time neuronavigation (mandatory)",                 "All studies"],
        ["Device (CE-marked)",    "NEUROLITH TPS System (Storz Medical AG)",                        "CE approval"],
    ]


def get_tps_evidence_summary_table() -> list[list[str]]:
    """
    Return evidence summary rows for document tables.
    Format: [[Condition, Study, N, Design, Key Result, Evidence Level], ...]
    """
    return [
        ["Alzheimers Disease",        "Beisteiner 2025 (JAMA Psychiatry)", "60", "RCT sham-controlled",  "CERAD +3.91 vs -1.83 (<=70yr, p=.005); BDI-II reduced (p=.008)", "HIGH"],
        ["MDD / Depression",          "Tan 2023 (Brain Sci)",               "30", "Single-blind RCT",     "HDRS-17 d=0.93 (p=.02); d=1.35 at 3 months",                     "LOW - pilot"],
        ["Parkinsons Disease",        "Ren 2024 (Front Neurol)",            "20", "Open-label retro",     "UPDRS-III d=1.38 (p<0.001); 19/20 improved",                      "LOW - pilot"],
        ["Mild Cognitive Impairment", "Kwok 2023 (Brain Sci)",              "19", "Open-label pilot",     "MoCA improved (p=.004); verbal fluency, Stroop, IADL improved",   "LOW - pilot"],
        ["Healthy/Neuroplasticity",   "Beisteiner 2022 (NeuroImage)",       "12", "RCT sham crossover",   "SMN connectivity +efficiency (p=.040); DTI axial diffusivity down","MEDIUM - mechanistic"],
    ]
