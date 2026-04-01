"""Condition-specific data for Responder Tracking & Classification — Partners Tier."""

CONDITIONS = {}

# ── 1. DEPRESSION ────────────────────────────────────────────────────────────
CONDITIONS["depression"] = dict(
    name="Major Depressive Disorder (MDD)", short="Depression", slug="depression",
    med_class="SSRI/SNRI", med_name="antidepressant",
    phenotype_options="□ Melancholic  □ Anxious/Somatic  □ Atypical  □ Cognitive  □ Psychomotor",
    subtitle="Depression Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, SSRI/SNRI-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to diurnal mood variation and antidepressant wash-in effects.",
    measurement_confound_warning=(
        "WARNING: If baseline is assessed during diurnal low-mood period and follow-up during a high-mood period "
        "(or vice versa), or if medication has not reached steady-state, you can create a false responder or "
        "non-responder. Always document time of day, sleep quality, and medication phase at each assessment."
    ),
    sec7_title="7. SSRI/SNRI-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. Serotonergic tone modulates prefrontal LTP-like plasticity mechanisms.",
    sec7a_title="7A. Medicated vs Wash-in Phase Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Choose ONE medication phase for a block and keep it CONSISTENT. "
        "Assessing patients during SSRI wash-in vs steady-state is one of the most common sources of false classification."
    ),
    sec7c_title="7C. SSRI/SNRI + tDCS Pairing by Depression Phenotype",
    sec7d_title="7D. SSRI/SNRI-tDCS Documentation Checklist",
    # Table[0] Row 3
    phenotype_row=["Phenotype", "□ Melancholic  □ Anxious/Somatic  □ Atypical  □ Cognitive  □ Psychomotor"],
    # Table[1]: 5r x 4c — response domains
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Mood", "≥50% reduction in PHQ-9 or HDRS; clinically meaningful mood improvement", "□ Y □ N", ""],
        ["Cognition", "Improvement in executive function, memory, or processing speed tasks", "□ Y □ N", ""],
        ["Somatic/Anxiety", "Reduction in somatic symptoms, sleep improvement, anxiety reduction", "□ Y □ N", ""],
        ["Function", "Better daily functioning (work, social, self-care) by patient/clinician report", "□ Y □ N", ""],
    ],
    # Table[2]: 7r x 4c — responder profiles
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Cognitive (DLPFC)", "Executive dysfunction, cognitive slowing, low motivation; DMN-CEN imbalance", "L-DLPFC anodal tDCS + cognitive activation tasks", "Strong (meta-analysis support)"],
        ["Melancholic (DLPFC+taVNS)", "Anhedonia, psychomotor retardation, early waking; mesolimbic hypoactivity", "L-DLPFC tDCS + taVNS + behavioural activation", "Moderate (RCT)"],
        ["Anxious/Somatic (DLPFC/PFC)", "Anxiety-depression overlap; hyperarousal; insula overactivation", "L-DLPFC tDCS + CES + relaxation tasks", "Moderate"],
        ["Atypical (taVNS-led)", "Mood reactivity, hypersomnia, leaden paralysis; vagal tone reduction", "taVNS + DLPFC tDCS adjunct", "Emerging"],
        ["Psychomotor (M1/DLPFC)", "Severe psychomotor retardation; motor-affective circuit involvement", "Bilateral DLPFC + TPS FT4", "Emerging"],
        ["Rumination/OCD-overlap", "Persistent rumination, negative bias; anterior cingulate hyperactivity", "R-DLPFC cathodal + L-DLPFC anodal + TPS", "Emerging"],
    ],
    # Table[3]: 5r x 3c — clinical predictors
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["Moderate rather than severe baseline depression", "Sufficient prefrontal reserve for plasticity-based gains", "□ Y □ N"],
        ["Cognitive dysfunction as a core symptom", "DLPFC-targeted tDCS most effective when cognition is impaired", "□ Y □ N"],
        ["SSRI/SNRI at stable dose ≥4 weeks", "Serotonergic tone required to optimise tDCS LTP-like effects", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON-guided targeting improves specificity of protocol selection", "□ Y □ N"],
    ],
    # Table[4]: 5r x 2c — protocol predictors
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "L-DLPFC anodal most evidence-based; bilateral montage for severe cases"],
        ["Dose and repetition", "10–20 sessions required; single-session effects not clinically meaningful"],
        ["Concurrent task", "Cognitive activation or behavioural tasks during tDCS enhance outcomes"],
        ["Network alignment", "FNON Level 2 hypothesis (CEN hypoactivation vs DMN hyperactivation) guides montage"],
    ],
    # Table[5]: 4r x 3c — classification
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "≥50% PHQ-9 reduction + clinically meaningful functional improvement", "Continue protocol; plan maintenance schedule"],
        ["Partial Responder", "25–49% PHQ-9 reduction OR improvement in one domain only", "Re-phenotype; adjust task pairing; consider taVNS addition"],
        ["Non-Responder", "< 25% improvement in any domain after adequate trial (10+ sessions)", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    # Table[6]: 5r x 3c — non-responder profiles
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Severe/treatment-resistant depression", "Prefrontal downregulation beyond neuromodulation threshold", "Consider TMS referral; TPS FT4; adjunct CES"],
        ["Active suicidality / psychiatric crisis", "Safety priority overrides neuromodulation scheduling", "Defer NIBS; prioritise psychiatric stabilisation"],
        ["Medication non-compliance or frequent changes", "Confounded neural state; cannot attribute change to tDCS", "Stabilise medications first; re-baseline"],
        ["Psychosis or bipolar mixed state", "Different circuit pathology; DLPFC protocol not appropriate", "Consider discontinuation; specialist review"],
    ],
    # Table[8]: 6r x 3c — medication state comparison
    med_state_comparison=[
        ["Factor", "Steady-State (Default SOZO)", "Wash-in Phase (Avoid)"],
        ["Definition", "tDCS during stable SSRI/SNRI period (≥4 weeks at therapeutic dose)", "tDCS during first 1–4 weeks of new antidepressant or dose change"],
        ["Task Participation", "Better engagement; stable mood state for concurrent tasks", "Mood volatility; reduced task compliance"],
        ["Plasticity Substrate", "Serotonergic tone supports LTP-like mechanisms", "Unstable receptor occupancy; unpredictable response"],
        ["Comparison Validity", "Valid within-block comparisons; stable baseline", "High variability; cannot attribute change to tDCS"],
        ["Evidence Support", "Supports task-paired neurorehabilitation approach", "Avoid; increases confounding; document if unavoidable"],
    ],
    # Table[9]: 8r x 2c — medication documentation
    med_documentation=[
        ["Domain", "Details"],
        ["SSRI/SNRI Name & Dose", ""],
        ["Duration at Current Dose", "___ weeks"],
        ["Time of Daily Dose", "___ AM / PM"],
        ["Dose Taken Before Session?", "□ Yes  □ No — Time of last dose: ___"],
        ["Chosen Phase for Block", "□ Steady-state (default)  □ Wash-in (document rationale)"],
        ["Target Session Window", "___ hours post-dose"],
        ["Session Start Time", "Keep consistent: ___:___ AM/PM"],
    ],
    # Table[10]: 5r x 4c — phenotype pairing
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Cognitive (CEN deficit)", "L-DLPFC anodal 2mA", "Executive cognitive training during tDCS", "PHQ-9, HDRS, MoCA, Trail Making"],
        ["Melancholic/Anhedonia", "L-DLPFC anodal + taVNS", "Behavioural activation tasks", "PHQ-9, SHAPS, GAD-7"],
        ["Anxious/Somatic", "L-DLPFC anodal + CES", "Relaxation + mindfulness tasks", "GAD-7, PHQ-9, DASS-21"],
        ["Psychomotor/Retarded", "Bilateral DLPFC + TPS FT4", "Motor-activation with verbal tasks", "HDRS, MADRS, MoCA"],
    ],
    # Table[11]: 10r x 3c — documentation checklist
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["SSRI/SNRI name, dose, and duration at current dose recorded", "□ Yes", "□"],
        ["Session timing relative to daily dose documented", "□ Yes", "□"],
        ["Medication phase (steady-state vs wash-in) recorded at each session", "□ Yes", "□"],
        ["Baseline assessment medication phase recorded", "□ Yes", "□"],
        ["Follow-up assessment in same medication phase", "□ Yes", "□"],
        ["Any medication changes during block documented", "□ Yes", "□"],
        ["Time of day of assessment consistent across block", "□ Yes", "□"],
        ["Sleep quality night before assessment noted", "□ Yes", "□"],
        ["Outcomes interpreted with medication context", "□ Yes", "□"],
    ],
    # Table[13]: 4r x 2c — language guide
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive intervention alongside stable antidepressant therapy", "tDCS replaces or reduces the need for antidepressants"],
        ["Effects may be enhanced when combined with concurrent cognitive activation", "tDCS cures or eliminates depressive episodes"],
        ["Evidence remains promising; effect sizes are moderate; response varies", "tDCS is equivalent to ECT or proven antidepressants"],
    ],
)

# ── 2. ANXIETY ───────────────────────────────────────────────────────────────
CONDITIONS["anxiety"] = dict(
    name="Generalised Anxiety Disorder (GAD)", short="Anxiety", slug="anxiety",
    med_class="SSRI/SNRI/Buspirone", med_name="anxiolytic",
    phenotype_options="□ Cognitive/Worry  □ Somatic  □ Social  □ Panic-overlap  □ Mixed",
    subtitle="Anxiety Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, SSRI/SNRI-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to situational anxiety variation and pre-assessment anticipatory anxiety.",
    measurement_confound_warning=(
        "WARNING: If baseline is assessed during a low-anxiety period and follow-up occurs before a stressful event "
        "(or vice versa), or if caffeine intake or sleep quality differs, you can create a false responder or "
        "non-responder. Document anxiety state, caffeine intake, and anticipatory triggers at each assessment."
    ),
    sec7_title="7. SSRI/SNRI/Buspirone-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. Anxiolytic medications modulate GABAergic and serotonergic tone relevant to prefrontal inhibitory control.",
    sec7a_title="7A. Medicated vs Pre-medication State Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Choose ONE medication state for a block and keep it CONSISTENT. "
        "Assessing during peak anxiolytic effect vs trough is one of the most common sources of false classification."
    ),
    sec7c_title="7C. Anxiolytic + tDCS Pairing by Anxiety Phenotype",
    sec7d_title="7D. Anxiolytic-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Cognitive/Worry  □ Somatic  □ Social  □ Panic-overlap  □ Mixed"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Worry/Cognitive", "≥50% reduction in GAD-7 or HAM-A; reduced worry frequency/duration", "□ Y □ N", ""],
        ["Somatic", "Reduction in physical symptoms (tension, GI, fatigue) by self-report", "□ Y □ N", ""],
        ["Function", "Improved daily functioning, reduced avoidance, better occupational capacity", "□ Y □ N", ""],
        ["Sleep", "Improved sleep onset, reduced anxiety-related insomnia (GAD-7 item 6)", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Cognitive/Worry (DLPFC)", "Excessive worry, rumination, DMN hyperactivation; poor cognitive control", "L-DLPFC anodal tDCS + CBT-based cognitive tasks", "Moderate (pilot RCTs)"],
        ["Somatic (R-DLPFC cathodal)", "Autonomic hyperarousal, tension, GI symptoms; insula-amygdala hyperactivity", "L-DLPFC anodal + CES + relaxation tasks", "Emerging"],
        ["Social anxiety overlap (vmPFC)", "Social evaluation fear; heightened threat detection in social contexts", "R-DLPFC cathodal + taVNS + exposure tasks", "Emerging"],
        ["Panic-overlap (CES-led)", "Panic attacks, interoceptive hypersensitivity; brainstem arousal dysregulation", "CES primary + L-DLPFC adjunct + relaxation", "Emerging"],
        ["Mixed/Comorbid depression", "GAD + MDD overlap; CEN-DMN imbalance across anxiety and mood domains", "L-DLPFC anodal tDCS + taVNS + TPS FT4", "Moderate"],
        ["Generalised high-arousal", "Pervasive hypervigilance; sleep disruption; autonomic dysregulation", "CES + taVNS + DLPFC tDCS sequence", "Emerging"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["Moderate rather than severe baseline anxiety", "Sufficient prefrontal inhibitory reserve for plasticity-based gains", "□ Y □ N"],
        ["Worry/cognitive symptoms as dominant feature", "DLPFC-targeted tDCS most effective for cognitive anxiety subtype", "□ Y □ N"],
        ["SSRI/SNRI at stable therapeutic dose ≥4 weeks", "Serotonergic tone supports prefrontal LTP-like mechanisms", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON-guided targeting improves specificity for anxiety circuit", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "L-DLPFC anodal for cognitive/worry; CES for somatic/autonomic subtype"],
        ["Dose and repetition", "10–20 sessions; single-session anxiolytic effects are transient only"],
        ["Concurrent task", "CBT-based tasks or relaxation during tDCS enhances specificity"],
        ["Network alignment", "FNON Level 2: DMN hyperactivation vs CEN hypoactivation guides montage"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "≥50% GAD-7 reduction + meaningful functional improvement", "Continue protocol; plan maintenance"],
        ["Partial Responder", "25–49% GAD-7 reduction OR improvement in somatic but not cognitive domain", "Re-phenotype; consider CES addition or task adjustment"],
        ["Non-Responder", "<25% improvement in any domain after adequate trial (10+ sessions)", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Severe GAD with significant avoidance", "Cortical modulation insufficient without exposure-based engagement", "Integrate exposure therapy; defer neuromodulation until engaged"],
        ["Panic disorder with agoraphobia", "Different circuit (locus coeruleus/amygdala); DLPFC not primary target", "CES primary; reconsider protocol approach"],
        ["Medication non-compliance or frequent changes", "Unstable GABAergic/serotonergic tone confounds tDCS effects", "Stabilise medications; re-baseline"],
        ["Comorbid substance use", "Neuromodulatory effects confounded by alcohol/benzodiazepine use", "Address substance use first; specialist review"],
    ],
    med_state_comparison=[
        ["Factor", "Steady-State (Default SOZO)", "Trough / Pre-dose State (Avoid)"],
        ["Definition", "tDCS at consistent time after SSRI/SNRI dose; stable anxiolytic level", "tDCS at medication trough or during dose adjustment period"],
        ["Task Participation", "Better cognitive engagement; stable anxiety level for tasks", "Heightened baseline anxiety; poor task compliance"],
        ["Plasticity Substrate", "Serotonergic/GABAergic tone supports prefrontal LTP", "Unstable receptor state; unpredictable cortical excitability"],
        ["Comparison Validity", "Valid within-block comparisons", "High session-to-session variability; cannot attribute change"],
        ["Evidence Support", "Consistent with task-paired neuromodulation framework", "Avoid; increases confounding risk"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["SSRI/SNRI/Buspirone Name & Dose", ""],
        ["Duration at Current Dose", "___ weeks"],
        ["Time of Daily Dose", "___ AM / PM"],
        ["Caffeine Intake Before Session?", "□ None  □ 1 cup  □ >1 cup — Time: ___"],
        ["Chosen State for Block", "□ Steady-state (default)  □ Other (document rationale)"],
        ["Target Session Window", "___ hours post-dose"],
        ["Session Start Time", "Keep consistent: ___:___ AM/PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Cognitive/Worry", "L-DLPFC anodal 2mA", "CBT thought-challenging tasks during tDCS", "GAD-7, HAM-A, PSWQ"],
        ["Somatic/Autonomic", "L-DLPFC anodal + CES", "Diaphragmatic breathing + body scan", "GAD-7, PHQ-15, HRV"],
        ["Social anxiety overlap", "R-DLPFC cathodal + taVNS", "Graded social exposure imagery", "LSAS, GAD-7, SPS"],
        ["Mixed/High arousal", "CES + taVNS + DLPFC", "Progressive muscle relaxation + mindfulness", "GAD-7, DASS-21, ISI"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["Anxiolytic name, dose, and duration at current dose recorded", "□ Yes", "□"],
        ["Session timing relative to daily dose documented", "□ Yes", "□"],
        ["Caffeine and stimulant intake before session noted", "□ Yes", "□"],
        ["Baseline anxiety state rated at session start (GAD-7 item)", "□ Yes", "□"],
        ["Any situational stressors or triggers before session noted", "□ Yes", "□"],
        ["Medication changes during block documented", "□ Yes", "□"],
        ["Time of day consistent across block", "□ Yes", "□"],
        ["Sleep quality night before assessment noted", "□ Yes", "□"],
        ["Outcomes interpreted with anxiety state context", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive intervention alongside stable anxiolytic therapy", "tDCS replaces or reduces anxiety medications"],
        ["Effects may be enhanced with concurrent CBT-based cognitive tasks", "tDCS eliminates anxiety disorders"],
        ["Evidence is emerging; response varies; this is not a standalone treatment", "tDCS is as effective as CBT or SSRIs for GAD"],
    ],
)

# ── 3. ADHD ──────────────────────────────────────────────────────────────────
CONDITIONS["adhd"] = dict(
    name="Attention Deficit Hyperactivity Disorder (ADHD)", short="ADHD", slug="adhd",
    med_class="Stimulants/Atomoxetine", med_name="ADHD medication",
    phenotype_options="□ Inattentive  □ Hyperactive-Impulsive  □ Combined  □ Emotional Dysregulation",
    subtitle="ADHD Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, Stimulant-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to stimulant peak/trough variability and sleep-dependent cognitive performance.",
    measurement_confound_warning=(
        "WARNING: If baseline is assessed at stimulant trough and follow-up at peak (or vice versa), or if the night "
        "before differed in sleep quality, you can create a false responder or non-responder. Always document "
        "stimulant timing, time of day, and prior-night sleep at each assessment."
    ),
    sec7_title="7. Stimulant/Atomoxetine-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. Dopaminergic/noradrenergic tone from stimulants modulates prefrontal excitability and NMDA-dependent plasticity.",
    sec7a_title="7A. Stimulant ON-Peak vs Trough State Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Choose ONE stimulant timing window for a block and keep it CONSISTENT. "
        "Assessing during stimulant peak vs trough is one of the most common sources of false classification in ADHD."
    ),
    sec7c_title="7C. Stimulant + tDCS Pairing by ADHD Phenotype",
    sec7d_title="7D. Stimulant-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Inattentive  □ Hyperactive-Impulsive  □ Combined  □ Emotional Dysregulation"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Attention", "≥30% improvement in CAARS inattention subscale or CPT omissions", "□ Y □ N", ""],
        ["Executive Function", "Improvement in working memory, planning, or inhibition tasks", "□ Y □ N", ""],
        ["Hyperactivity/Impulsivity", "Reduction in CAARS hyperactivity subscale or commission errors", "□ Y □ N", ""],
        ["Function", "Better occupational/academic performance by self/clinician report", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Inattentive (DLPFC)", "Chronic inattention, mind-wandering, DMN-CEN imbalance; low working memory", "L-DLPFC anodal tDCS + working memory training", "Moderate (RCT support)"],
        ["Hyperactive (R-IFC)", "Impulse control deficit; orbitofrontal/IFC underactivity; action monitoring deficit", "R-IFC/DLPFC tDCS + response inhibition tasks", "Emerging"],
        ["Combined (Bilateral DLPFC)", "Inattention + hyperactivity; widespread prefrontal dysregulation", "Bilateral DLPFC tDCS + dual-task training", "Moderate"],
        ["Emotional Dysregulation (DLPFC+taVNS)", "Mood instability, frustration intolerance; limbic-prefrontal dysregulation", "L-DLPFC tDCS + taVNS + emotion regulation tasks", "Emerging"],
        ["Working Memory-dominant", "Severe WM deficit; DLPFC-parietal network impairment", "DLPFC + parietal tDCS + N-back training", "Moderate"],
        ["Sleep-comorbid", "ADHD + chronic sleep disruption; PFC downregulation from sleep debt", "DLPFC tDCS + CES for sleep + morning scheduling", "Emerging"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["Inattention as primary symptom subtype", "DLPFC tDCS most effective for attention/WM phenotype", "□ Y □ N"],
        ["Stimulant at stable dose with predictable peak", "Dopaminergic tone required for optimal tDCS plasticity window", "□ Y □ N"],
        ["Capacity for cognitive training tasks during tDCS", "Activity-dependent plasticity is essential for ADHD gains", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON CEN/DMN imbalance confirmation guides target selection", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "L-DLPFC anodal for inattention; R-IFC for impulsivity; bilateral for combined"],
        ["Timing window", "Administer during stimulant peak (45–90 min post-dose) for optimal dopaminergic state"],
        ["Concurrent task", "Working memory or inhibition tasks during tDCS critical for ADHD outcomes"],
        ["Network alignment", "FNON CEN hypoactivation + DMN hyperactivation guides DLPFC montage selection"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "≥30% improvement in primary ADHD measure + functional gain", "Continue protocol; plan maintenance"],
        ["Partial Responder", "15–29% improvement OR attention but not executive gains", "Re-phenotype; adjust task; consider bilateral montage"],
        ["Non-Responder", "<15% improvement across domains after 10+ sessions", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Severe comorbid anxiety or depression", "Emotional dysregulation masking attention gains; competing circuits", "Treat comorbidity first; adjust protocol"],
        ["Medication non-compliance or inconsistent dosing", "Unstable dopaminergic tone confounds tDCS timing window", "Stabilise medication schedule; re-baseline"],
        ["ASD comorbidity with rigid routines", "Task compliance limited; sensory sensitivities reduce tolerance", "Adapted task protocol; sensory accommodations"],
        ["Chronic sleep deprivation", "PFC downregulation from sleep debt negates tDCS gains", "Address sleep first; morning session scheduling"],
    ],
    med_state_comparison=[
        ["Factor", "Stimulant Peak (Default SOZO)", "Stimulant Trough (Avoid for Primary Sessions)"],
        ["Definition", "tDCS 45–90 min after stimulant dose (peak plasma concentration)", "tDCS before stimulant dose or at wearing-off"],
        ["Task Participation", "Better focus and task engagement; optimal WM capacity", "Inattention and restlessness higher; poor compliance"],
        ["Plasticity Substrate", "Dopaminergic/NE tone supports DLPFC LTP-like plasticity", "Reduced dopaminergic modulation; suboptimal plasticity window"],
        ["Comparison Validity", "Stable within-block comparisons if timing is consistent", "High variability; cannot attribute change to tDCS"],
        ["Evidence Support", "Activity-dependent plasticity requires sufficient dopaminergic state", "Controlled off-drug protocols only; document carefully"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["Stimulant Name, Formulation & Dose", ""],
        ["Dose Schedule (IR/XR)", ""],
        ["Estimated Peak Window", "___ to ___ minutes post-dose"],
        ["Chosen State for Block", "□ Stimulant peak (default)  □ Off-medication (document rationale)"],
        ["Session Timing Post-Dose", "___ minutes after dose"],
        ["Sleep Quality Night Before", "□ Good  □ Fair  □ Poor"],
        ["Session Start Time", "Keep consistent: ___:___ AM/PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Inattentive", "L-DLPFC anodal 2mA during peak", "N-back / sustained attention tasks", "CAARS-Inattention, CPT omissions"],
        ["Hyperactive-Impulsive", "R-IFC/DLPFC tDCS during peak", "Response inhibition / Stop-Signal tasks", "CAARS-Hyperactivity, CPT commissions"],
        ["Combined", "Bilateral DLPFC tDCS", "Dual-task cognitive training", "Conners CAARS full scale, BRIEF"],
        ["Emotional Dysregulation", "L-DLPFC + taVNS", "Emotion regulation exercises", "CAARS, DERS, BRIEF-ERC"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["Stimulant/Atomoxetine name, formulation, and dose recorded", "□ Yes", "□"],
        ["Session timing relative to dose (minutes post-dose) documented", "□ Yes", "□"],
        ["Stimulant peak window confirmed at session start", "□ Yes", "□"],
        ["Baseline assessment stimulant state recorded", "□ Yes", "□"],
        ["Follow-up in same stimulant timing window", "□ Yes", "□"],
        ["Medication changes during block documented", "□ Yes", "□"],
        ["Sleep quality night before session noted", "□ Yes", "□"],
        ["Session start time consistent across block", "□ Yes", "□"],
        ["Outcomes interpreted with stimulant timing context", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive intervention alongside stable ADHD medication", "tDCS replaces stimulant medication in ADHD"],
        ["Effects may be enhanced during stimulant peak with concurrent cognitive training", "tDCS cures or resolves ADHD"],
        ["Evidence is promising; effect sizes are moderate; response varies by phenotype", "tDCS is equivalent to stimulants for ADHD"],
    ],
)

# ── 4. ALZHEIMER'S / MCI ─────────────────────────────────────────────────────
CONDITIONS["alzheimers"] = dict(
    name="Alzheimer's Disease / Mild Cognitive Impairment (MCI)", short="Alzheimer's", slug="alzheimers",
    med_class="ChEIs/Memantine", med_name="cholinesterase inhibitor",
    phenotype_options="□ Amnestic MCI  □ Non-amnestic MCI  □ Mild AD  □ Moderate AD  □ Mixed dementia",
    subtitle="Alzheimer's Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, ChEI/Memantine-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to sundowning, time-of-day cognitive fluctuation, and caregiver vs patient reporting discordance.",
    measurement_confound_warning=(
        "WARNING: If baseline is assessed in the morning (peak cognitive window) and follow-up in the afternoon "
        "(sundowning period), or if caregiver vs patient reporting differs across assessments, you can create a "
        "false responder or non-responder. Always assess at the same time of day with the same informant."
    ),
    sec7_title="7. ChEI/Memantine-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. Cholinergic tone from ChEIs modulates hippocampal and cortical plasticity windows relevant to memory-based tDCS protocols.",
    sec7a_title="7A. Medicated vs Pre-Medication State Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Choose ONE time-of-day window for all assessments and keep it CONSISTENT. "
        "Time-of-day cognitive fluctuation in Alzheimer's/MCI is one of the most common sources of false classification."
    ),
    sec7c_title="7C. ChEI/Memantine + tDCS Pairing by Cognitive Phenotype",
    sec7d_title="7D. ChEI/Memantine-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Amnestic MCI  □ Non-amnestic MCI  □ Mild AD  □ Moderate AD  □ Mixed dementia"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Episodic Memory", "Improvement or stabilisation on ADAS-Cog memory subscale or word-list recall", "□ Y □ N", ""],
        ["Executive/Attention", "Improvement on Trail Making B, Digit Span, or MoCA executive items", "□ Y □ N", ""],
        ["Language", "Improved naming (BNT), verbal fluency, or word-finding ability", "□ Y □ N", ""],
        ["Daily Function", "Stabilisation or improvement in ADLs by caregiver report (ADCS-ADL)", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Amnestic MCI (temporal)", "Isolated memory deficit; hippocampal-entorhinal circuit impairment", "Temporal tDCS (T3/T4) + memory encoding tasks", "Moderate (RCT support)"],
        ["Non-amnestic MCI (DLPFC)", "Executive/attention deficit primary; frontal network involved", "DLPFC tDCS + executive training", "Emerging"],
        ["Mild AD (multi-target)", "Memory + executive decline; temporo-parietal + prefrontal involvement", "DLPFC + temporal tDCS sequence + memory tasks", "Moderate"],
        ["Language-dominant", "Semantic/naming deficits; left temporal-parietal involvement", "Left temporal tDCS + language tasks (naming, fluency)", "Emerging"],
        ["Behavioural/BPSD", "Apathy, depression, agitation; mesolimbic-frontal circuit dysfunction", "DLPFC tDCS + taVNS + behavioural activation", "Emerging"],
        ["Moderate AD (stabilisation)", "Goal is stabilisation not improvement; advanced disease", "Low-intensity bilateral tDCS + caregiver-assisted tasks", "Emerging"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["MCI or mild AD stage (not moderate/severe)", "Sufficient cortical reserve for plasticity-based stabilisation", "□ Y □ N"],
        ["ChEI at stable dose ≥3 months", "Cholinergic tone supports hippocampal LTP-like mechanisms for tDCS", "□ Y □ N"],
        ["Capacity to engage in concurrent memory tasks", "Activity-dependent plasticity requires active engagement", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON hippocampal/temporal network mapping guides targeting", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "Temporal (T3/T4) for memory; DLPFC for executive; bilateral for mixed AD"],
        ["Session scheduling", "Morning sessions recommended to avoid sundowning and fatigue effects"],
        ["Concurrent task", "Memory encoding tasks during tDCS; caregiver-assisted for compliance"],
        ["Network alignment", "FNON hippocampal and default mode network mapping guides electrode placement"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "Stabilisation or improvement on primary cognitive measure + functional maintenance", "Continue protocol; plan 3-monthly maintenance"],
        ["Partial Responder", "Slower-than-expected decline OR improvement in one cognitive domain only", "Adjust target; review task engagement; add modality"],
        ["Non-Responder", "Continued decline at expected rate in all domains after adequate trial", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Moderate–severe Alzheimer's stage", "Network degeneration beyond plasticity capacity", "Shift to supportive/caregiver-focused protocol; CES only"],
        ["Severely reduced task engagement/compliance", "Activity-dependent plasticity requires active participation", "Caregiver-assisted adapted tasks; consider discontinuation"],
        ["Medication non-compliance or frequent changes", "Unstable cholinergic tone confounds tDCS plasticity window", "Stabilise medications; re-baseline"],
        ["Significant BPSD (agitation, psychosis)", "Behavioural symptoms interfere with tDCS session safety", "Address BPSD first; psychiatric review"],
    ],
    med_state_comparison=[
        ["Factor", "Stable ChEI State (Default SOZO)", "Unstable/Titration Phase (Avoid)"],
        ["Definition", "tDCS during stable ChEI dose (≥3 months at therapeutic dose)", "tDCS during ChEI initiation or dose titration period"],
        ["Task Participation", "Better cholinergic tone; more consistent memory task engagement", "GI side effects, titration variability; reduced compliance"],
        ["Plasticity Substrate", "Cholinergic support for hippocampal LTP-like mechanisms", "Unstable ACh levels; unpredictable plasticity substrate"],
        ["Comparison Validity", "Stable within-block comparisons; consistent cognitive state", "High variability; cannot attribute change to tDCS"],
        ["Evidence Support", "Cholinergic-tDCS synergy best studied at stable doses", "Avoid; document if unavoidable during titration"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["ChEI/Memantine Name & Dose", ""],
        ["Duration at Current Dose", "___ months"],
        ["Time of Daily Dose", "___ AM / PM"],
        ["Session Time of Day", "□ Morning (preferred)  □ Afternoon  □ Evening — Time: ___"],
        ["Sundowning Pattern?", "□ Yes — Peak time: ___  □ No"],
        ["Caregiver Present at Session?", "□ Yes  □ No"],
        ["Session Start Time", "Keep consistent: ___:___ AM/PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Amnestic MCI", "Temporal tDCS (T3/T4) anodal", "Word-list encoding + spaced retrieval", "ADAS-Cog memory, RBANS memory"],
        ["Non-amnestic MCI / Executive", "L-DLPFC anodal", "Cognitive training (Trail Making-type tasks)", "MoCA, TMT-B, WAIS Digit Span"],
        ["Mild AD (multi-domain)", "DLPFC + temporal sequence", "Caregiver-assisted memory tasks", "MoCA, ADAS-Cog, ADCS-ADL"],
        ["Behavioural/BPSD", "DLPFC + taVNS", "Structured behavioural activation", "NPI, PHQ-9, ADCS-ADL"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["ChEI/Memantine name, dose, and duration at current dose recorded", "□ Yes", "□"],
        ["Time of day of session (morning recommended) documented", "□ Yes", "□"],
        ["Sundowning pattern and peak time noted for scheduling", "□ Yes", "□"],
        ["Caregiver informant consistency across assessments documented", "□ Yes", "□"],
        ["Baseline assessment cognitive state and time of day recorded", "□ Yes", "□"],
        ["Follow-up assessment at same time of day with same informant", "□ Yes", "□"],
        ["Medication changes during block documented", "□ Yes", "□"],
        ["Session start time consistent across block", "□ Yes", "□"],
        ["Outcomes interpreted with time-of-day and informant context", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive intervention alongside stable ChEI therapy", "tDCS reverses or cures Alzheimer's disease"],
        ["Goal is cognitive stabilisation or slowing of decline; improvement possible in MCI", "tDCS restores lost memory or prevents progression"],
        ["Evidence is promising for MCI/mild AD; effect sizes are moderate", "tDCS is equivalent to cholinesterase inhibitors"],
    ],
)

# ── 5. STROKE ────────────────────────────────────────────────────────────────
CONDITIONS["stroke"] = dict(
    name="Post-Stroke Rehabilitation", short="Stroke", slug="stroke",
    med_class="Antiplatelets/SSRIs", med_name="antiplatelet/neurorestorative agent",
    phenotype_options="□ Motor (UL)  □ Motor (LL/Gait)  □ Aphasia  □ Cognitive  □ Mixed",
    subtitle="Stroke Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, Antiplatelet/SSRI-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to spontaneous recovery confounds and fatigue-related performance variability post-stroke.",
    measurement_confound_warning=(
        "WARNING: Spontaneous neurological recovery in the first 3–6 months post-stroke can create false "
        "responders independent of tDCS. Fatigue-related performance decline during sessions can create false "
        "non-responders. Always document time since stroke, session fatigue level, and recovery phase at each assessment."
    ),
    sec7_title="7. Antiplatelet/SSRI-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. SSRIs given post-stroke (e.g., fluoxetine) modulate motor cortex excitability and neuroplasticity; antiplatelet safety profile must be confirmed.",
    sec7a_title="7A. SSRI Medicated vs Non-Medicated State Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Choose ONE medication and recovery phase state for a block and keep it CONSISTENT. "
        "Spontaneous recovery combined with treatment effects is one of the most common attribution challenges in stroke rehabilitation."
    ),
    sec7c_title="7C. Antiplatelet/SSRI + tDCS Pairing by Stroke Phenotype",
    sec7d_title="7D. Post-Stroke Medication-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Motor (UL)  □ Motor (LL/Gait)  □ Aphasia  □ Cognitive  □ Mixed"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Upper Limb Motor", "Clinically meaningful improvement on Fugl-Meyer UL or ARAT", "□ Y □ N", ""],
        ["Gait / Lower Limb", "Improvement in 10m walk, 6MWT, or Tinetti balance assessment", "□ Y □ N", ""],
        ["Cognition/Aphasia", "Improvement on MoCA, BNT, or communication measures (WAB)", "□ Y □ N", ""],
        ["Function/ADLs", "Better independence on Barthel Index or FIM by clinician report", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Motor UL (M1 ipsilesional)", "Upper limb motor deficit; corticospinal tract partially preserved", "Ipsilesional M1 anodal + contralesional M1 cathodal + task", "Strong (RCT support)"],
        ["Motor LL / Gait (M1/SMA)", "Gait impairment; SMA and M1 LE involved; ambulatory patient", "SMA/M1 tDCS + gait training", "Moderate"],
        ["Aphasia (Wernicke/Broca)", "Expressive or receptive aphasia; left perisylvian involvement", "L temporal/parietal tDCS + speech therapy tasks", "Moderate (meta-analysis)"],
        ["Cognitive post-stroke", "Post-stroke cognitive impairment; PFC-thalamo-cortical disruption", "DLPFC tDCS + cognitive rehabilitation tasks", "Emerging"],
        ["Spasticity/Pain", "Post-stroke spasticity with central pain; motor-sensory circuit", "M1 + TPS FT9 + motor tasks", "Emerging"],
        ["Depression comorbid", "Post-stroke depression; limbic-PFC disruption; mood-motor interaction", "DLPFC tDCS + taVNS + behavioural activation", "Moderate"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["Subacute phase (1 week – 6 months post-stroke)", "Peak neuroplasticity window; best gains expected", "□ Y □ N"],
        ["Preserved motor evoked potential on TMS/clinical exam", "Intact corticospinal tract indicates plasticity substrate", "□ Y □ N"],
        ["Capacity for active task participation during tDCS", "Activity-dependent plasticity requires motor engagement", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON interhemispheric imbalance mapping guides montage", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "Ipsilesional M1 for motor; contralateral inhibition for interhemispheric balance"],
        ["Recovery phase", "Subacute phase offers best neuroplasticity window; chronic phase requires more sessions"],
        ["Concurrent task", "Task-specific rehabilitation during tDCS is essential (not rest)"],
        ["Network alignment", "FNON interhemispheric imbalance hypothesis guides bihemispheric montage"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "Clinically meaningful improvement on primary motor/functional measure", "Continue protocol; document recovery phase contribution"],
        ["Partial Responder", "Measurable gain below MCID threshold OR improvement in one domain only", "Adjust montage; intensify task; review recovery phase"],
        ["Non-Responder", "No meaningful improvement beyond expected spontaneous recovery", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Chronic stroke (>12 months) with severe deficit", "Limited remaining neuroplasticity; dense lesion", "TPS pathway; supportive rehabilitation; CES adjunct"],
        ["Complete corticospinal tract lesion (confirmed)", "No substrate for motor plasticity-based recovery", "Consider discontinuation; supportive ADL focus"],
        ["Significant post-stroke fatigue limiting sessions", "Fatigue reduces task engagement and plasticity induction", "Shorter sessions; CES for fatigue; schedule review"],
        ["Post-stroke seizure history (uncontrolled)", "Safety contraindication; seizure threshold concerns", "Neurology review; defer NIBS until seizure-controlled"],
    ],
    med_state_comparison=[
        ["Factor", "SSRI-Medicated State (Default SOZO)", "Non-Medicated State"],
        ["Definition", "tDCS during stable SSRI period (fluoxetine ≥4 weeks where prescribed)", "tDCS without neurorestorative SSRI (antiplatelet only)"],
        ["Motor Plasticity", "SSRI enhances motor cortex excitability and neuroplasticity post-stroke", "Baseline plasticity without serotonergic enhancement"],
        ["Task Participation", "Generally better mood and motivation with SSRI treatment", "May have lower engagement if post-stroke depression present"],
        ["Comparison Validity", "Consistent within-block if SSRI dose is stable", "Valid comparison if SSRI not used; document explicitly"],
        ["Evidence Support", "FLAME trial supports fluoxetine + motor rehab combination", "Standard rehabilitation without serotonergic augmentation"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["Antiplatelet/Anticoagulant Name & Dose", ""],
        ["SSRI (if prescribed post-stroke)", "___ Name/Dose — Duration: ___ weeks"],
        ["Time Since Stroke (Recovery Phase)", "□ Acute (<1wk)  □ Subacute (1wk–6mo)  □ Chronic (>6mo)"],
        ["Session Fatigue Level at Start", "□ Low  □ Moderate  □ High — VAS: ___/10"],
        ["Chosen Medication State for Block", "□ With SSRI (if prescribed)  □ Antiplatelet only"],
        ["Session Duration Adapted for Fatigue?", "□ Yes — Reduced to ___ min  □ No"],
        ["Session Start Time", "Keep consistent: ___:___ AM/PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Motor UL", "Ipsilesional M1 anodal 2mA", "Task-specific UL rehabilitation during tDCS", "Fugl-Meyer UL, ARAT, grip strength"],
        ["Motor LL / Gait", "SMA/M1 LE anodal + contralesional cathodal", "Gait training / stepping tasks", "10m walk, 6MWT, Tinetti, BBS"],
        ["Aphasia", "L temporal/parietal anodal + SLP tasks", "Speech-language therapy tasks during tDCS", "WAB-R, BNT, CETI"],
        ["Cognitive post-stroke", "DLPFC anodal + cognitive tasks", "Cognitive rehabilitation exercises", "MoCA, Barthel, TMT-B"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["Antiplatelet/SSRI name, dose, and duration recorded", "□ Yes", "□"],
        ["Recovery phase (acute/subacute/chronic) documented", "□ Yes", "□"],
        ["Spontaneous recovery contribution acknowledged in assessment", "□ Yes", "□"],
        ["Session fatigue level rated at each session start", "□ Yes", "□"],
        ["Baseline assessment recovery phase and medication state recorded", "□ Yes", "□"],
        ["Follow-up in same recovery phase window (within same block)", "□ Yes", "□"],
        ["Medication changes during block documented", "□ Yes", "□"],
        ["Session start time consistent across block", "□ Yes", "□"],
        ["Outcomes interpreted with recovery phase context", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive intervention alongside standard stroke rehabilitation", "tDCS independently drives stroke recovery"],
        ["Effects may reflect a combination of tDCS and spontaneous recovery; both are documented", "tDCS prevents further stroke events"],
        ["Evidence is moderate for motor and aphasia applications; effect sizes vary", "tDCS is as effective as intensive physiotherapy alone"],
    ],
)

# ── 6. TBI ───────────────────────────────────────────────────────────────────
CONDITIONS["tbi"] = dict(
    name="Traumatic Brain Injury (TBI)", short="TBI", slug="tbi",
    med_class="Methylphenidate/Amantadine", med_name="neuro-stimulant/NMDA modulator",
    phenotype_options="□ Cognitive  □ Affective/Behavioural  □ Post-Concussive  □ Executive  □ Mixed",
    subtitle="TBI Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, Methylphenidate/Amantadine-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to post-exertional symptom worsening and cognitive fatigue on testing day.",
    measurement_confound_warning=(
        "WARNING: If baseline is assessed during a low-symptom day and follow-up occurs after physical or cognitive "
        "exertion (or vice versa), post-exertional symptom worsening can create a false non-responder. Always document "
        "exertion level, headache state, and cognitive fatigue at each assessment."
    ),
    sec7_title="7. Methylphenidate/Amantadine-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. Methylphenidate enhances dopaminergic/noradrenergic PFC function; amantadine modulates NMDA receptors relevant to post-TBI plasticity.",
    sec7a_title="7A. Neuro-Stimulant ON vs Pre-Dose State Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Choose ONE medication timing window for a block and keep it CONSISTENT. "
        "Post-exertional symptom fluctuation and inconsistent medication timing are the most common sources of false classification in TBI."
    ),
    sec7c_title="7C. Methylphenidate/Amantadine + tDCS Pairing by TBI Phenotype",
    sec7d_title="7D. TBI Medication-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Cognitive  □ Affective/Behavioural  □ Post-Concussive  □ Executive  □ Mixed"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Cognition", "Improvement on RBANS, MoCA, or processing speed tasks", "□ Y □ N", ""],
        ["Executive Function", "Improvement in Trail Making B, verbal fluency, or planning tasks", "□ Y □ N", ""],
        ["Mood/Behaviour", "Reduction in aggression, irritability, or depression (PHQ-9, NRS-irritability)", "□ Y □ N", ""],
        ["Function/Independence", "Better daily independence or RTW progress by clinician/self report", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Cognitive TBI (DLPFC)", "PFC-targeted injury; attention, WM, processing speed impaired", "L-DLPFC anodal tDCS + cognitive rehabilitation", "Moderate (pilot RCT)"],
        ["Executive (DLPFC bilateral)", "Frontal lobe injury; planning, inhibition, cognitive flexibility impaired", "Bilateral DLPFC tDCS + executive training tasks", "Moderate"],
        ["Post-Concussive (CES+DLPFC)", "Mild TBI; headache, cognitive fog, sleep disruption; diffuse axonal", "CES + DLPFC tDCS + paced cognitive tasks", "Emerging"],
        ["Affective/Behavioural (DLPFC+taVNS)", "Irritability, aggression, emotional lability; orbito-frontal involvement", "DLPFC tDCS + taVNS + emotion regulation tasks", "Emerging"],
        ["Fatigue-dominant (CES-led)", "Chronic fatigue, cognitive exhaustion; brainstem-arousal disruption", "CES primary + DLPFC adjunct + paced tasks", "Emerging"],
        ["Motor-cognitive (M1+DLPFC)", "Combined motor-cognitive impairment; central motor + PFC injury", "M1 + DLPFC tDCS sequence + task-specific rehab", "Emerging"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["Mild-moderate TBI (not severe with minimal reserve)", "Sufficient cortical reserve for plasticity-based gains", "□ Y □ N"],
        ["Methylphenidate/Amantadine at stable dose", "Dopaminergic/NMDA modulation supports tDCS plasticity window", "□ Y □ N"],
        ["Capacity to engage without triggering symptom exacerbation", "Post-exertional worsening negates plasticity induction", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON PFC/CEN disruption mapping guides target selection", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "DLPFC for cognitive/executive; CES for fatigue/post-concussive; M1 for motor comorbidity"],
        ["Exertion management", "No heavy physical or cognitive exertion within 4 hours pre-session"],
        ["Session intensity", "Start at lower intensity; titrate up; monitor headache/fatigue throughout"],
        ["Network alignment", "FNON PFC-CEN hypoactivation + default mode disruption guides montage"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "Meaningful improvement on primary cognitive/functional measure + headache/fatigue reduction", "Continue protocol; plan maintenance"],
        ["Partial Responder", "Improvement in one domain but limited transfer to function", "Adjust task intensity; consider CES addition; review exertion management"],
        ["Non-Responder", "No improvement or symptom worsening after adequate trial", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Severe TBI with minimal cognitive reserve", "Network degeneration limits cortical plasticity capacity", "Supportive rehabilitation; CES for symptom management"],
        ["Chronic post-concussive syndrome with PTSD comorbidity", "Overlapping circuits; trauma response modulates PFC access", "Address PTSD first; integrated trauma-informed protocol"],
        ["Medication non-compliance or unstable psychiatric comorbidity", "Confounded neural state; unpredictable dopaminergic environment", "Stabilise medications; psychiatric review"],
        ["Active substance use (alcohol/cannabis)", "Cortical neuromodulation confounded; plasticity impaired", "Address substance use; re-baseline"],
    ],
    med_state_comparison=[
        ["Factor", "Stimulant/Amantadine ON (Default SOZO)", "Pre-Dose / Trough State (Avoid)"],
        ["Definition", "tDCS 45–90 min after methylphenidate or morning amantadine dose", "tDCS before dose or at medication trough"],
        ["Cognitive State", "Optimal PFC function; better attention and task engagement", "Cognitive fog; poor attention; symptom exacerbation risk"],
        ["Plasticity Substrate", "Dopaminergic/NMDA support for PFC LTP-like mechanisms", "Reduced neuromodulatory support; suboptimal plasticity"],
        ["Comparison Validity", "Stable within-block if timing is consistent", "High variability; cannot attribute change to tDCS"],
        ["Evidence Support", "Stimulant + tDCS synergy best at stable medicated state", "Avoid; document if medication timing varies"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["Methylphenidate/Amantadine Name & Dose", ""],
        ["Dose Schedule", ""],
        ["Session Timing Post-Dose", "___ minutes after dose"],
        ["Pre-Session Exertion Level", "□ None  □ Light  □ Moderate  □ Heavy — Type: ___"],
        ["Headache Level at Session Start", "NRS: ___/10"],
        ["Chosen State for Block", "□ Medicated (default)  □ Off-medication (document rationale)"],
        ["Session Start Time", "Keep consistent: ___:___ AM/PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Cognitive TBI", "L-DLPFC anodal 2mA", "Paced attention/WM tasks during tDCS", "RBANS, MoCA, TMT-A/B"],
        ["Executive", "Bilateral DLPFC tDCS", "Planning/inhibition tasks (Stroop, BADS)", "TMT-B, WCST, BRIEF"],
        ["Post-Concussive", "CES + DLPFC adjunct", "Paced breathing + light cognitive task", "RPQ, ISI, PHQ-9, MoCA"],
        ["Affective/Behavioural", "DLPFC + taVNS", "Emotion regulation tasks + CBT elements", "NRS-irritability, PHQ-9, PCL-5"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["Methylphenidate/Amantadine name, dose, and schedule recorded", "□ Yes", "□"],
        ["Session timing relative to dose documented", "□ Yes", "□"],
        ["Pre-session exertion level and headache state documented", "□ Yes", "□"],
        ["Baseline assessment medication state and symptom level recorded", "□ Yes", "□"],
        ["Follow-up in same medication timing window and exertion context", "□ Yes", "□"],
        ["Medication changes during block documented", "□ Yes", "□"],
        ["Post-exertional symptom protocol followed (no heavy exertion within 4h)", "□ Yes", "□"],
        ["Session start time consistent across block", "□ Yes", "□"],
        ["Outcomes interpreted with exertion and headache context", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive neurorehabilitation tool alongside TBI management", "tDCS repairs structural brain damage from TBI"],
        ["Cognitive gains may be enhanced when fatigue and exertion are managed", "tDCS eliminates post-concussive symptoms"],
        ["Evidence is emerging; response varies by TBI severity and phenotype", "tDCS is equivalent to neuropsychological rehabilitation alone"],
    ],
)

# ── 7. CHRONIC PAIN ──────────────────────────────────────────────────────────
CONDITIONS["chronic_pain"] = dict(
    name="Chronic Pain / Fibromyalgia", short="Chronic Pain", slug="chronic_pain",
    med_class="Pregabalin/Duloxetine", med_name="analgesic/neuromodulatory agent",
    phenotype_options="□ Central Sensitisation  □ Nociplastic  □ Neuropathic  □ Comorbid Depression  □ Mixed",
    subtitle="Chronic Pain Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, Pregabalin/Duloxetine-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to pain flare timing, rescue medication use, and day-to-day pain variability.",
    measurement_confound_warning=(
        "WARNING: If baseline is assessed on a low-pain day and follow-up during a pain flare (or vice versa), "
        "or if rescue medication was used differently before assessments, you can create a false responder or "
        "non-responder. Always document pain NRS, rescue medication use, activity level, and stress level at assessment."
    ),
    sec7_title="7. Pregabalin/Duloxetine-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. Pregabalin modulates central sensitisation; duloxetine enhances descending inhibitory tone — both interact with tDCS analgesia mechanisms.",
    sec7a_title="7A. Medicated vs Flare State Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Choose ONE baseline pain state context for a block and keep it CONSISTENT. "
        "Pain flare timing and rescue medication use are the most common sources of false classification in chronic pain."
    ),
    sec7c_title="7C. Analgesic + tDCS Pairing by Pain Phenotype",
    sec7d_title="7D. Analgesic-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Central Sensitisation  □ Nociplastic  □ Neuropathic  □ Comorbid Depression  □ Mixed"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Pain Intensity", "≥30% reduction in pain NRS or VAS; MCID met on BPI", "□ Y □ N", ""],
        ["Pain Interference", "Reduction in BPI interference subscale; improved daily activity", "□ Y □ N", ""],
        ["Mood/Affect", "Reduction in pain-related depression (PHQ-9) or anxiety (GAD-7)", "□ Y □ N", ""],
        ["Function/Sleep", "Better sleep quality, physical function, or fatigue reduction (FIQ/FACIT)", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Central Sensitisation (M1 anodal)", "Widespread pain amplification; cortical pain map expansion; poor descending inhibition", "M1 anodal tDCS + graded activity", "Strong (meta-analysis; fibromyalgia RCTs)"],
        ["Nociplastic / Fibromyalgia (M1+DLPFC)", "Fibromyalgia; fatigue + pain + mood overlap; CEN-limbic imbalance", "M1 + DLPFC tDCS + graded exercise", "Moderate (systematic reviews)"],
        ["Neuropathic (M1-led)", "Post-herpetic, CRPS, diabetic neuropathy; central pain sensitisation", "M1 anodal tDCS + sensory desensitisation", "Moderate"],
        ["Comorbid Depression (DLPFC+M1)", "Pain + depression overlap; mesolimbic-CEN dysregulation", "DLPFC + M1 tDCS + taVNS + behavioural activation", "Moderate"],
        ["Catastrophising-dominant (DLPFC)", "High pain catastrophising; PFC downregulation of pain matrix", "L-DLPFC anodal + cognitive restructuring tasks", "Emerging"],
        ["Sleep-pain cycle (CES+M1)", "Chronic pain driving sleep disruption and vice versa; arousal dysregulation", "CES + M1 tDCS + sleep hygiene tasks", "Emerging"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["Central sensitisation confirmed (not purely peripheral)", "M1 tDCS targets descending inhibitory control; most effective for central pain", "□ Y □ N"],
        ["Analgesic medication at stable dose ≥4 weeks", "Stable GABAergic/serotonergic tone supports tDCS analgesia mechanism", "□ Y □ N"],
        ["Capacity for graded activity tasks during tDCS", "Activity-dependent analgesia enhances tDCS analgesic effects", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON pain matrix and descending inhibitory network mapping guides protocol", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "M1 anodal for central/nociplastic; DLPFC for catastrophising/affective component"],
        ["Activity integration", "Graded activity during tDCS essential; rest-only sessions less effective"],
        ["Flare management", "Do not assess during known pain flare; maintain consistent activity level pre-session"],
        ["Network alignment", "FNON pain matrix (M1/DLPFC) vs descending inhibitory network guides montage"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "≥30% pain NRS reduction + functional improvement on BPI/FIQ", "Continue protocol; plan maintenance schedule"],
        ["Partial Responder", "10–29% pain reduction OR function improvement without pain change", "Re-phenotype; adjust target; consider taVNS addition"],
        ["Non-Responder", "<10% pain reduction in all domains after adequate trial", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Predominantly peripheral pain (non-central)", "M1/cortical tDCS not primary mechanism for peripheral nociception", "Review diagnosis; consider TPS FT9 + peripheral focus"],
        ["High opioid use confounding central sensitisation", "Opioid-induced hyperalgesia complicates response measurement", "Pain specialist review; opioid optimisation first"],
        ["Severe psychiatric comorbidity (PTSD, severe depression)", "Competing limbic circuit activation reduces analgesic effect", "Treat psychiatric comorbidity first; integrated protocol"],
        ["Medication non-compliance or frequent analgesic changes", "Unstable descending inhibitory tone confounds tDCS effects", "Stabilise medications; pain management plan review"],
    ],
    med_state_comparison=[
        ["Factor", "Stable Analgesic State (Default SOZO)", "Flare / Rescue Medication Use (Document)"],
        ["Definition", "tDCS during stable analgesic dose without recent rescue medication", "tDCS during pain flare or within 4h of rescue medication use"],
        ["Pain Level", "Baseline pain NRS consistent; valid comparison", "Elevated NRS masks tDCS analgesic effect or creates false response"],
        ["Task Participation", "Better engagement with graded activity tasks at stable pain", "Reduced compliance; pain-avoidance behaviour activated"],
        ["Comparison Validity", "Valid within-block if activity level is consistent", "High variability; document and flag in classification"],
        ["Evidence Support", "Stable analgesic state required for M1 tDCS analgesia protocol", "Avoid assessing on flare days; reschedule if NRS ≥7/10"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["Pregabalin/Duloxetine Name & Dose", ""],
        ["Duration at Current Dose", "___ weeks"],
        ["Rescue Medication Used Before Session?", "□ No  □ Yes — Type/Dose/Time: ___"],
        ["Pain NRS at Session Start", "___/10"],
        ["Activity Level Day Before Session", "□ Rest  □ Light  □ Moderate  □ Heavy"],
        ["Chosen State for Block", "□ Stable analgesic (default)  □ Other (document rationale)"],
        ["Session Start Time", "Keep consistent: ___:___ AM/PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Central Sensitisation", "M1 anodal 2mA + contralateral cathodal", "Graded activity tasks during tDCS", "Pain NRS, BPI, FIQ, QST"],
        ["Nociplastic/Fibromyalgia", "M1 + DLPFC tDCS", "Graded exercise + relaxation", "FIQ-R, FACIT-F, PHQ-9, NRS"],
        ["Catastrophising", "L-DLPFC anodal + M1", "Cognitive restructuring + graded exposure", "PCS, NRS, PHQ-9, BPI"],
        ["Comorbid Depression/Pain", "DLPFC + taVNS + M1", "Behavioural activation + light activity", "PHQ-9, NRS, SHAPS, FIQ"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["Analgesic name, dose, and duration at current dose recorded", "□ Yes", "□"],
        ["Rescue medication use within 4h of session documented", "□ Yes", "□"],
        ["Pain NRS at session start recorded", "□ Yes", "□"],
        ["Activity level day before session documented", "□ Yes", "□"],
        ["Baseline assessment pain state and medication context recorded", "□ Yes", "□"],
        ["Follow-up in same pain state context (not on flare day)", "□ Yes", "□"],
        ["Medication changes during block documented", "□ Yes", "□"],
        ["Session start time consistent across block", "□ Yes", "□"],
        ["Outcomes interpreted with pain state and rescue medication context", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive pain management tool alongside stable analgesic therapy", "tDCS eliminates chronic pain or replaces analgesic medications"],
        ["Effects target central sensitisation; peripheral pain mechanisms are not directly addressed", "tDCS repairs underlying tissue damage or pathology"],
        ["Evidence is moderate for central/nociplastic pain; effect sizes are clinically meaningful in responders", "tDCS is curative for fibromyalgia or chronic pain syndromes"],
    ],
)
