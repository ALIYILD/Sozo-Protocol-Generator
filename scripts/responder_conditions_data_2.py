"""Condition data part 2 — conditions 8-14 for Responder Tracking Partners."""

CONDITIONS_2 = {}

# ── 8. PTSD ──────────────────────────────────────────────────────────────────
CONDITIONS_2["ptsd"] = dict(
    name="Post-Traumatic Stress Disorder (PTSD)", short="PTSD", slug="ptsd",
    med_class="SSRIs/Prazosin", med_name="SSRI/noradrenergic agent",
    phenotype_options="□ Fear/Re-experiencing  □ Dysphoric  □ Dissociative  □ Anxious  □ Mixed",
    subtitle="PTSD Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, SSRI/Prazosin-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to trauma trigger exposure before assessment and dissociation during testing.",
    measurement_confound_warning=(
        "WARNING: If baseline is assessed on a low-symptom day and follow-up occurs after a trauma trigger exposure "
        "or a nightmare-disrupted night, you can create a false non-responder. Dissociation during testing invalidates "
        "scores. Always document trigger exposure, nightmare frequency, sleep quality, and dissociation state at each assessment."
    ),
    sec7_title="7. SSRI/Prazosin-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. SSRIs modulate fear extinction circuitry; prazosin reduces noradrenergic hyperarousal — both interact with DLPFC/vmPFC tDCS mechanisms.",
    sec7a_title="7A. SSRI Steady-State vs Wash-in Phase Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Choose ONE medication state and trigger-exposure context for a block and keep it CONSISTENT. "
        "Trigger exposure before assessment and SSRI wash-in variability are the most common sources of false classification in PTSD."
    ),
    sec7c_title="7C. SSRI/Prazosin + tDCS Pairing by PTSD Phenotype",
    sec7d_title="7D. PTSD Medication-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Fear/Re-experiencing  □ Dysphoric  □ Dissociative  □ Anxious  □ Mixed"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Re-experiencing/Intrusion", "≥30% reduction in PCL-5 re-experiencing cluster or CAPS-5 criterion B", "□ Y □ N", ""],
        ["Hyperarousal/Hypervigilance", "Reduction in PCL-5 hyperarousal cluster; improved sleep", "□ Y □ N", ""],
        ["Avoidance/Numbing", "Reduced avoidance behaviours; improved engagement in daily activities", "□ Y □ N", ""],
        ["Function", "Better daily functioning, occupational engagement, relationship quality", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Fear/Re-experiencing (vmPFC/DLPFC)", "Intrusive memories, flashbacks; fear circuit hyperactivation; vmPFC hypoactivation", "L-DLPFC anodal + vmPFC + trauma processing tasks", "Emerging (pilot)"],
        ["Dysphoric (DLPFC+taVNS)", "Depression-dominant PTSD; anhedonia, emotional numbing; mesolimbic involvement", "L-DLPFC anodal + taVNS + behavioural activation", "Moderate"],
        ["Dissociative (CES+DLPFC)", "Depersonalisation/derealisation; cortical hyperinhibition; altered interoception", "CES + R-DLPFC cathodal + grounding tasks", "Emerging"],
        ["Anxious (DLPFC+CES)", "Hypervigilance, panic-overlap; amygdala-PFC dysregulation; high ANS reactivity", "L-DLPFC + CES + relaxation/safety tasks", "Emerging"],
        ["Nightmares-dominant (Prazosin+CES)", "Severe nightmare burden; noradrenergic hyperarousal at night; sleep disruption", "CES evening protocol + DLPFC daytime + prazosin support", "Emerging"],
        ["Complex PTSD (multi-target)", "Childhood trauma; affect dysregulation + identity + interpersonal issues", "DLPFC + taVNS + TPS FT4 + trauma-informed tasks", "Emerging"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["PTSD without active suicidality or acute crisis", "Safety prerequisite for all NIBS protocols", "□ Y □ N"],
        ["SSRI at therapeutic dose ≥4 weeks (steady-state)", "Fear extinction circuitry requires serotonergic support for tDCS", "□ Y □ N"],
        ["Engagement in trauma-informed concurrent tasks (not exposure without support)", "Activity-dependent plasticity requires therapeutic engagement", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON fear circuit (amygdala-vmPFC-DLPFC) mapping guides protocol", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "L-DLPFC for dysphoric/cognitive PTSD; vmPFC for fear/re-experiencing phenotype"],
        ["Trigger management", "No trauma trigger exposure within 24h of assessment session"],
        ["Concurrent task", "Safety-focused or grounding tasks during tDCS; avoid full trauma exposure without therapist"],
        ["Network alignment", "FNON fear extinction circuit (vmPFC hypoactivation) guides anodal target selection"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "≥30% PCL-5 reduction + meaningful functional improvement", "Continue protocol; plan maintenance"],
        ["Partial Responder", "15–29% PCL-5 reduction OR hyperarousal improvement without intrusion reduction", "Re-phenotype; adjust target; consider prazosin review"],
        ["Non-Responder", "<15% improvement in any domain after adequate trial", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Active trauma exposure (ongoing unsafe environment)", "Continued trauma precludes fear extinction and plasticity", "Safety planning priority; defer NIBS"],
        ["Severe dissociative subtype", "Cortical hyperinhibition; may paradoxically worsen with standard tDCS", "Adapted CES grounding protocol; specialist consultation"],
        ["Medication non-compliance or SSRI intolerance", "Unstable serotonergic tone limits fear extinction support", "Review medication options; psychiatric consultation"],
        ["Severe comorbid substance use", "Alcohol/substance use confounds ANS regulation and PFC access", "Address substance use first; trauma-informed addiction care"],
    ],
    med_state_comparison=[
        ["Factor", "SSRI Steady-State (Default SOZO)", "SSRI Wash-in / Adjustment Phase (Avoid)"],
        ["Definition", "tDCS during stable SSRI period (≥4 weeks at therapeutic dose)", "tDCS during SSRI initiation or dose change period"],
        ["Fear Circuit Access", "Serotonergic support for vmPFC fear extinction during tDCS tasks", "Unstable serotonin levels; fear extinction impaired"],
        ["Task Participation", "Better emotional regulation capacity during processing tasks", "Emotional volatility; poor task compliance; increased distress"],
        ["Comparison Validity", "Consistent within-block comparisons at stable state", "High symptom variability; cannot attribute change to tDCS"],
        ["Evidence Support", "SSRI + fear extinction + tDCS interaction studied at stable doses", "Avoid; document if SSRI is being initiated or adjusted"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["SSRI/Prazosin Name & Dose", ""],
        ["Duration at Current SSRI Dose", "___ weeks"],
        ["Prazosin Dose for Nightmares (if prescribed)", ""],
        ["Trauma Trigger Exposure in Last 24h?", "□ None  □ Yes — Type: ___"],
        ["Nightmare Disruption Night Before?", "□ None  □ Mild  □ Severe"],
        ["Dissociation State at Session Start", "□ Grounded  □ Mild dissociation  □ Significant — Defer session"],
        ["Session Start Time", "Keep consistent: ___:___ AM/PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Fear/Re-experiencing", "L-DLPFC anodal + vmPFC", "Grounding + safety-focused processing tasks", "PCL-5, CAPS-5 B cluster, IES-R"],
        ["Dysphoric/Numbing", "L-DLPFC + taVNS", "Behavioural activation + pleasant activity scheduling", "PCL-5, PHQ-9, SHAPS"],
        ["Anxious/Hyperarousal", "L-DLPFC + CES", "Relaxation + controlled breathing tasks", "PCL-5, GAD-7, HRV"],
        ["Dissociative", "CES + R-DLPFC cathodal", "Grounding exercises (5-4-3-2-1 sensory)", "DES-II, PCL-5, MQ"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["SSRI/prazosin name, dose, and duration at current dose recorded", "□ Yes", "□"],
        ["Trauma trigger exposure within 24h of session documented", "□ Yes", "□"],
        ["Nightmare frequency and sleep quality night before noted", "□ Yes", "□"],
        ["Dissociation screen completed at session start", "□ Yes", "□"],
        ["Baseline assessment symptom state and trigger context recorded", "□ Yes", "□"],
        ["Follow-up in same medication state and trigger-free context", "□ Yes", "□"],
        ["Medication changes during block documented", "□ Yes", "□"],
        ["Session start time consistent across block", "□ Yes", "□"],
        ["Outcomes interpreted with trigger exposure and sleep context", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive intervention alongside trauma-focused therapy and SSRI treatment", "tDCS processes or resolves trauma memories"],
        ["Effects may support fear extinction when used with grounding-based concurrent tasks", "tDCS eliminates PTSD or removes traumatic memories"],
        ["Evidence is emerging; this is not a standalone PTSD treatment", "tDCS is equivalent to EMDR or Prolonged Exposure therapy"],
    ],
)

# ── 9. OCD ───────────────────────────────────────────────────────────────────
CONDITIONS_2["ocd"] = dict(
    name="Obsessive-Compulsive Disorder (OCD)", short="OCD", slug="ocd",
    med_class="High-dose SSRIs/Clomipramine", med_name="anti-obsessional agent",
    phenotype_options="□ Contamination/Cleaning  □ Symmetry/Ordering  □ Harm/Checking  □ Rumination  □ Mixed",
    subtitle="OCD Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, SSRI/Clomipramine-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to OCD symptom fluctuation during dose adjustment periods and stress-triggered OCD worsening.",
    measurement_confound_warning=(
        "WARNING: If baseline is assessed during a low-stress period and follow-up occurs during a stress-triggered "
        "OCD worsening, or if SSRI dose has been recently adjusted, you can create a false non-responder. "
        "Always document current stress level, recent triggers, medication phase, and ERP therapy stage at each assessment."
    ),
    sec7_title="7. High-Dose SSRI/Clomipramine-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. High-dose SSRIs modulate orbitofrontal-striatal circuits; serotonergic tone interacts with tDCS inhibitory effects on hyperactive OCD circuits.",
    sec7a_title="7A. SSRI Therapeutic Dose vs Titration Phase Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Choose ONE medication phase for a block and keep it CONSISTENT. "
        "OCD symptom fluctuation during SSRI dose titration and stress-triggered worsening are the most common sources of false classification."
    ),
    sec7c_title="7C. Anti-Obsessional + tDCS Pairing by OCD Phenotype",
    sec7d_title="7D. OCD Medication-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Contamination/Cleaning  □ Symmetry/Ordering  □ Harm/Checking  □ Rumination  □ Mixed"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Obsessions", "≥35% reduction in Y-BOCS obsession subscale or OCI-R score", "□ Y □ N", ""],
        ["Compulsions", "≥35% reduction in Y-BOCS compulsion subscale; reduced ritual time", "□ Y □ N", ""],
        ["Anxiety/Distress", "Reduction in distress associated with obsessive thoughts (DASS/GAD-7)", "□ Y □ N", ""],
        ["Function", "Better daily functioning; reduced time lost to rituals; improved engagement", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Contamination/Cleaning (R-DLPFC cathodal)", "Contamination obsessions; cleaning compulsions; OFC hyperactivation", "R-DLPFC cathodal + SMA cathodal + ERP tasks", "Moderate (pilot RCT)"],
        ["Symmetry/Ordering (SMA cathodal)", "Symmetry/ordering compulsions; SMA hyperactivation; not-just-right experiences", "SMA cathodal tDCS + habit reversal tasks", "Emerging"],
        ["Harm/Checking (R-DLPFC cathodal)", "Harm obsessions; checking rituals; hyperactive OFC-thalamo-striatal circuit", "R-DLPFC cathodal + ERP-based checking prevention tasks", "Emerging"],
        ["Rumination/Pure-O (DLPFC bilateral)", "Mental compulsions, intrusive thoughts; DLPFC-OFC loop dysfunction", "L-DLPFC anodal + R-DLPFC cathodal + mindfulness tasks", "Emerging"],
        ["Treatment-resistant (multi-target)", "Partial SSRI response; severe impairment; OFC-basal ganglia-thalamic dysregulation", "TPS FT5/FT6 + tDCS + clomipramine optimisation", "Emerging"],
        ["Comorbid tic/Tourette (SMA cathodal)", "OCD + tics; SMA-striatal circuit hyperactivation", "SMA cathodal + habit reversal + CBIT elements", "Emerging"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["SSRI at high therapeutic dose ≥8 weeks (steady-state)", "OCD requires higher SSRI doses; serotonergic saturation needed for tDCS synergy", "□ Y □ N"],
        ["ERP therapy ongoing or recently completed", "tDCS appears to augment fear extinction and ERP response", "□ Y □ N"],
        ["Moderate rather than severe OCD (Y-BOCS <32)", "Sufficient cortical inhibitory reserve for cathodal tDCS to reduce OFC", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON OFC-striatal-thalamic loop mapping guides inhibitory target selection", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "R-DLPFC cathodal / SMA cathodal for inhibitory effect on hyperactive OFC-striatal circuit"],
        ["ERP integration", "tDCS before ERP session may augment extinction learning window"],
        ["Timing relative to ERP", "Administer tDCS 30–60 min before ERP session for priming effect if applicable"],
        ["Network alignment", "FNON OFC hyperactivation + striatal dysregulation guides cathodal montage selection"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "≥35% Y-BOCS reduction + meaningful functional improvement", "Continue protocol; plan maintenance with ERP"],
        ["Partial Responder", "20–34% Y-BOCS reduction OR obsession reduction without compulsion change", "Re-phenotype; adjust montage; review ERP integration"],
        ["Non-Responder", "<20% Y-BOCS change after adequate trial (10+ sessions)", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Severe OCD with no ERP engagement", "tDCS alone insufficient without extinction-based task component", "Intensify ERP engagement; reconsider standalone NIBS"],
        ["OCD + severe depression (BDI > 30)", "Depressive circuit competes with OCD circuit; dual pathology", "Treat depression first; switch to L-DLPFC anodal protocol"],
        ["SSRI non-compliance or sub-therapeutic dose", "Insufficient serotonergic tone for OFC-striatal modulation", "Optimise SSRI dose; psychiatry review; consider clomipramine"],
        ["OCD with significant hoarding as primary subtype", "Hoarding may involve different neural circuitry (vmPFC/ACC)", "Hoarding-specific protocol review; specialist consultation"],
    ],
    med_state_comparison=[
        ["Factor", "Stable High-Dose SSRI (Default SOZO)", "Titration / Dose Adjustment Phase (Avoid)"],
        ["Definition", "tDCS during stable SSRI period (≥8 weeks at full therapeutic dose)", "tDCS during SSRI initiation, dose increase, or augmentation"],
        ["OFC-Striatal State", "Consistent serotonergic modulation of OFC-basal ganglia circuit", "Fluctuating receptor occupancy; unpredictable circuit state"],
        ["Task Participation", "Better ERP compliance; more stable anxiety habituation", "OCD severity fluctuates with medication; compliance varies"],
        ["Comparison Validity", "Consistent within-block comparisons at stable dose", "High symptom variability; cannot attribute change to tDCS"],
        ["Evidence Support", "High-dose SSRI + tDCS cathodal synergy requires stable serotonergic tone", "Avoid; document if dose is being adjusted during block"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["SSRI/Clomipramine Name & Dose", ""],
        ["Duration at Current Dose", "___ weeks"],
        ["ERP Therapy Status", "□ Active  □ Completed  □ Not receiving"],
        ["Stress Level at Session Start", "□ Low  □ Moderate  □ High"],
        ["Recent OCD Trigger Exposure?", "□ None  □ Yes — Type: ___"],
        ["Chosen Phase for Block", "□ Stable high-dose (default)  □ Titration (document rationale)"],
        ["Session Start Time", "Keep consistent: ___:___ AM/PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Contamination/Cleaning", "R-DLPFC cathodal 2mA + SMA cathodal", "ERP: contamination hierarchy tasks", "Y-BOCS, OCI-R contamination"],
        ["Symmetry/Ordering", "SMA cathodal tDCS", "Habit reversal + response prevention tasks", "Y-BOCS, OCI-R ordering"],
        ["Harm/Checking", "R-DLPFC cathodal", "ERP: checking prevention hierarchy", "Y-BOCS, OCI-R checking"],
        ["Rumination/Pure-O", "L-DLPFC anodal + R-DLPFC cathodal", "Mindfulness-based defusion tasks", "Y-BOCS obsessions, OBQ, DOCS"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["SSRI/clomipramine name, dose, and duration at full therapeutic dose recorded", "□ Yes", "□"],
        ["ERP therapy status and recent session documented", "□ Yes", "□"],
        ["Stress level and OCD trigger exposure before session noted", "□ Yes", "□"],
        ["Baseline assessment OCD state and medication phase recorded", "□ Yes", "□"],
        ["Follow-up in same medication phase and stress context", "□ Yes", "□"],
        ["Medication dose changes during block documented", "□ Yes", "□"],
        ["ERP integration timing relative to tDCS documented", "□ Yes", "□"],
        ["Session start time consistent across block", "□ Yes", "□"],
        ["Outcomes interpreted with medication phase and ERP context", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive intervention alongside high-dose SSRI and ERP therapy", "tDCS replaces ERP or cures OCD"],
        ["Effects may augment ERP extinction learning when used as a priming tool", "tDCS eliminates obsessions or compulsions independently"],
        ["Evidence is emerging; response is better when ERP is ongoing", "tDCS is equivalent to high-dose SSRI for OCD treatment"],
    ],
)

# ── 10. MS ───────────────────────────────────────────────────────────────────
CONDITIONS_2["ms"] = dict(
    name="Multiple Sclerosis (MS)", short="MS", slug="ms",
    med_class="DMTs/Symptomatic", med_name="disease-modifying therapy/symptomatic agent",
    phenotype_options="□ Relapsing-Remitting  □ Secondary Progressive  □ Cognitive  □ Fatigue-dominant  □ Spasticity-dominant",
    subtitle="MS Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, DMT/Symptomatic-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to relapse-remission fluctuation and Uhthoff's phenomenon during heat exposure.",
    measurement_confound_warning=(
        "WARNING: If baseline is assessed during remission and follow-up occurs during a relapse (or vice versa), "
        "or if heat exposure triggers Uhthoff's phenomenon before assessment, you can create a false responder or "
        "non-responder. Always document relapse/remission status, Uhthoff's exposure, and fatigue time-of-day at assessment."
    ),
    sec7_title="7. DMT/Symptomatic-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. DMTs modulate inflammatory activity; symptomatic agents (e.g., fampridine, amantadine) interact with cortical excitability and fatigue mechanisms.",
    sec7a_title="7A. Remission State vs Relapse/Post-Relapse State Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Assess ONLY in clinically stable remission and keep this CONSISTENT across the block. "
        "Relapse vs remission state differences are the most critical source of false classification in MS."
    ),
    sec7c_title="7C. DMT/Symptomatic + tDCS Pairing by MS Phenotype",
    sec7d_title="7D. MS Medication-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Relapsing-Remitting  □ Secondary Progressive  □ Cognitive  □ Fatigue-dominant  □ Spasticity-dominant"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Fatigue", "≥4 point reduction on MFIS or clinically meaningful fatigue improvement", "□ Y □ N", ""],
        ["Cognition", "Improvement on MSNQ, PASAT, SDMT, or MoCA executive items", "□ Y □ N", ""],
        ["Motor/Spasticity", "Improved walking speed, reduced spasticity (MAS), better balance", "□ Y □ N", ""],
        ["Function/QoL", "Improved EDSS-related daily function or MS QoL-54 score", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Fatigue-dominant (DLPFC+CES)", "MS fatigue as primary complaint; CEN hypoactivation; frontal fatigue circuit", "L-DLPFC anodal + CES + paced cognitive tasks", "Moderate (RCT support)"],
        ["Cognitive MS (DLPFC)", "Cognitive slowing, memory, processing speed; periventricular lesion burden", "DLPFC tDCS + cognitive rehabilitation tasks", "Moderate"],
        ["Motor/Spasticity (M1)", "Spasticity, weakness, gait impairment; corticospinal tract involvement", "M1 anodal tDCS + physiotherapy tasks", "Moderate"],
        ["Relapsing-Remitting stable (multi-target)", "RRMS in stable remission; multiple domain involvement; awaiting DMT effect", "DLPFC + M1 tDCS + taVNS + task sequence", "Moderate"],
        ["Pain/Central Sensitisation (M1)", "Central neuropathic pain; MS-related central sensitisation", "M1 anodal + TPS FT9 + graded activity", "Emerging"],
        ["Depression comorbid (DLPFC+taVNS)", "MS + depression; limbic-PFC disruption; apathy + fatigue overlap", "DLPFC + taVNS + behavioural activation", "Emerging"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["Clinically stable remission (no relapse in preceding 3 months)", "Active relapse changes cortical excitability; confounds tDCS response", "□ Y □ N"],
        ["DMT at stable regimen (not mid-switch or initiation)", "Inflammatory fluctuation during DMT changes affects plasticity substrate", "□ Y □ N"],
        ["Capacity for morning session scheduling (avoid Uhthoff's/heat)", "Heat-related deterioration can be minimised with morning sessions", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON CEN/fatigue circuit and motor network mapping guides targeting", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "DLPFC for fatigue/cognitive; M1 for motor/spasticity; CES for sleep/ANS regulation"],
        ["Session timing", "Morning sessions preferred; avoid afternoon heat exposure; cooled environment"],
        ["Relapse monitoring", "Suspend sessions during relapse; resume only when clinically stable"],
        ["Network alignment", "FNON CEN hypoactivation + motor network asymmetry guides montage selection"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "Meaningful improvement in primary symptom domain + stable relapse status", "Continue protocol; plan 3-monthly maintenance"],
        ["Partial Responder", "Fatigue or cognition improvement but limited motor/functional transfer", "Adjust target; review session environment for heat control"],
        ["Non-Responder", "No improvement in any domain after adequate trial in remission", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Active relapse during treatment block", "Acute inflammatory lesion activity dominates; tDCS effect obscured", "Suspend; resume in remission; document relapse carefully"],
        ["Progressive MS (SPMS/PPMS) with significant disability", "Axonal loss limits cortical plasticity capacity", "Adjust expectations; symptomatic focus; CES for fatigue"],
        ["Severe Uhthoff's phenomenon limiting session tolerance", "Heat-induced temporary worsening reduces task engagement", "Air-conditioned sessions; cooling vest; very early morning scheduling"],
        ["DMT mid-switch or significant immunological instability", "Unpredictable inflammatory state confounds tDCS outcomes", "Complete DMT transition; re-baseline at stable remission"],
    ],
    med_state_comparison=[
        ["Factor", "Stable Remission + DMT (Default SOZO)", "Relapse / Post-Relapse Recovery Phase (Avoid)"],
        ["Definition", "tDCS during clinically stable remission on established DMT regimen", "tDCS during active relapse or within 4 weeks post-relapse"],
        ["Cortical State", "Stable excitability; consistent inflammatory and plasticity substrate", "Active lesion formation; cortical excitability dysregulated"],
        ["Task Participation", "Better function and compliance during stable remission", "Functional decline during relapse; poor task engagement"],
        ["Comparison Validity", "Valid within-block in remission; stable baseline", "Cannot attribute change to tDCS during relapse; results invalid"],
        ["Evidence Support", "All MS tDCS trials conducted in stable patients", "Contraindicated during active relapse; resume only in remission"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["DMT Name & Dosing Schedule", ""],
        ["Symptomatic Agents (fampridine, amantadine, etc.)", ""],
        ["Relapse Status", "□ Stable remission  □ Post-relapse (date: ___)  □ Active relapse — DEFER"],
        ["Last Relapse Date", ""],
        ["Uhthoff's Exposure Before Session?", "□ None  □ Yes — Type: ___"],
        ["Session Environment Temperature", "□ Cooled (<22°C)  □ Ambient  □ Warm — Adjust if needed"],
        ["Session Start Time", "Keep consistent (morning preferred): ___:___ AM/PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Fatigue-dominant", "L-DLPFC anodal + CES", "Paced cognitive tasks with rest breaks", "MFIS, FACIT-F, MSNQ"],
        ["Cognitive MS", "L-DLPFC anodal 2mA", "SDMT-type processing tasks, WM training", "PASAT, SDMT, MoCA, MSNQ"],
        ["Motor/Spasticity", "M1 anodal + contralesional cathodal", "Physiotherapy exercises during tDCS", "25FWT, 9HPT, BBS, MAS"],
        ["Depression/Apathy", "DLPFC + taVNS", "Behavioural activation + pleasurable activities", "PHQ-9, MFIS, MSNQ"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["DMT name, regimen, and stability confirmed at each session", "□ Yes", "□"],
        ["Relapse/remission status documented (suspend if relapse)", "□ Yes", "□"],
        ["Uhthoff's exposure before session checked and documented", "□ Yes", "□"],
        ["Session environment temperature controlled and recorded", "□ Yes", "□"],
        ["Baseline assessment relapse status and DMT state recorded", "□ Yes", "□"],
        ["Follow-up assessment in clinically stable remission only", "□ Yes", "□"],
        ["DMT changes or dose adjustments during block documented", "□ Yes", "□"],
        ["Session start time (morning) consistent across block", "□ Yes", "□"],
        ["Outcomes interpreted with relapse and heat-exposure context", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive symptomatic intervention alongside established DMT therapy", "tDCS modifies MS disease progression or reduces relapses"],
        ["Effects target fatigue, cognition, and motor symptoms during stable remission", "tDCS is a disease-modifying treatment for MS"],
        ["Evidence is moderate for fatigue and cognitive applications in stable RRMS", "tDCS replaces or reduces the need for DMT"],
    ],
)

# ── 11. ASD ──────────────────────────────────────────────────────────────────
CONDITIONS_2["asd"] = dict(
    name="Autism Spectrum Disorder (ASD)", short="ASD", slug="asd",
    med_class="Risperidone/SSRIs/Stimulants", med_name="ASD pharmacotherapy agent",
    phenotype_options="□ Social-Communication  □ Repetitive Behaviour  □ Sensory  □ ADHD-comorbid  □ Anxiety-comorbid",
    subtitle="ASD Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, ASD Pharmacotherapy-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to routine disruption effects on behaviour and informant reporting variance across settings.",
    measurement_confound_warning=(
        "WARNING: Environmental sensory load differences between baseline and follow-up, routine disruption, "
        "or inconsistent informant (parent vs teacher vs self-report) can create false responders or non-responders. "
        "Always assess in the same environment, same time of day, with the same primary informant."
    ),
    sec7_title="7. ASD Pharmacotherapy-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. Risperidone modulates dopaminergic/serotonergic tone; SSRIs affect repetitive behaviour circuits; stimulants modulate PFC attention networks relevant to tDCS.",
    sec7a_title="7A. Medicated vs Unmedicated/Titration State Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Use the SAME informant, same environment, and same medication state for all assessments in a block. "
        "Multi-informant variance and environmental inconsistency are the most common sources of false classification in ASD."
    ),
    sec7c_title="7C. ASD Pharmacotherapy + tDCS Pairing by ASD Phenotype",
    sec7d_title="7D. ASD Pharmacotherapy-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Social-Communication  □ Repetitive Behaviour  □ Sensory  □ ADHD-comorbid  □ Anxiety-comorbid"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Social Communication", "Improvement on SRS-2 social awareness/communication or CGI-I", "□ Y □ N", ""],
        ["Repetitive Behaviours", "Reduction on RBS-R total score or specific subscale", "□ Y □ N", ""],
        ["Attention/Executive", "Improvement in BRIEF-2 or cognitive tasks (particularly ADHD-comorbid)", "□ Y □ N", ""],
        ["Function/Adaptive", "Better adaptive functioning on Vineland-3 or caregiver daily report", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Social-Communication (DLPFC)", "Social processing deficit; superior temporal/PFC network underactivation", "L-DLPFC anodal + social cognition tasks", "Emerging (pilot)"],
        ["Repetitive Behaviour (SMA cathodal)", "Elevated repetitive/restrictive behaviours; SMA-striatal hyperactivation", "SMA cathodal tDCS + habit flexibility training", "Emerging"],
        ["Sensory-dominant (CES+DLPFC)", "Sensory overresponsivity; interoceptive dysregulation; sensory-seeking", "CES + DLPFC tDCS + sensory-based tasks (adapted)", "Emerging"],
        ["ADHD-comorbid (DLPFC bilateral)", "ASD + ADHD; combined CEN and attention network dysregulation", "Bilateral DLPFC + stimulant-timed sessions", "Emerging"],
        ["Anxiety-comorbid (DLPFC+CES)", "ASD + high anxiety; amygdala-PFC fear circuit overactivation", "L-DLPFC + CES + relaxation-based tasks", "Emerging"],
        ["Language/Communication (L temporal)", "Expressive language deficit; Broca's area underactivation", "L temporal/IFC tDCS + SLP tasks", "Emerging"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["Verbal/cooperative level sufficient for task engagement", "Activity-dependent plasticity requires active task participation", "□ Y □ N"],
        ["ASD medication at stable dose ≥4 weeks", "Stable dopaminergic/serotonergic tone for consistent neural state", "□ Y □ N"],
        ["Consistent routine maintained across assessment days", "Routine disruption confounds ASD symptom expression independent of tDCS", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON social-affective and CEN mapping guides DLPFC/temporal targeting", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "DLPFC for social/executive phenotype; SMA cathodal for repetitive behaviours; temporal for language"],
        ["Environment control", "Consistent sensory environment across all sessions; same room, same therapist"],
        ["Informant consistency", "Use same primary informant (parent/caregiver) for all outcome ratings"],
        ["Network alignment", "FNON social-affective underactivation + CEN disruption guides targeting"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "Meaningful improvement on primary ASD measure + adaptive functioning gain by consistent informant", "Continue protocol; plan maintenance"],
        ["Partial Responder", "Improvement in one domain (e.g., attention) but limited social/repetitive behaviour change", "Re-phenotype; adjust target; ensure informant/environment consistency"],
        ["Non-Responder", "No meaningful change in any domain after adequate trial with consistent methodology", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Severe sensory intolerance to electrodes/tDCS sensation", "Cannot complete session protocol; safety/distress concern", "Desensitisation protocol; consider CES only; discuss with family"],
        ["Significant routine disruption during treatment block", "Environmental confound; ASD symptoms fluctuate with routine changes", "Stabilise routine; defer assessment until routine re-established"],
        ["Medication non-compliance or ongoing titration", "Unstable pharmacological state confounds tDCS neural effects", "Stabilise medications; re-baseline"],
        ["Level 3 ASD with minimal verbal communication", "Task engagement insufficient for activity-dependent plasticity", "Adapted caregiver-assisted protocol; lower expectations for outcomes"],
    ],
    med_state_comparison=[
        ["Factor", "Stable Medication State (Default SOZO)", "Titration / Medication-Free State (Document)"],
        ["Definition", "tDCS during stable ASD medication dose (≥4 weeks at therapeutic dose)", "tDCS during medication initiation, titration, or washout"],
        ["Behavioural State", "More consistent behavioural baseline for within-block comparison", "Behaviour more variable; harder to attribute change to tDCS"],
        ["Task Participation", "Better attention and compliance with familiar stable medication state", "Titration side effects may reduce session tolerance"],
        ["Informant Reporting", "Caregiver reports more consistent at stable medication state", "Caregiver reporting confounded by medication change expectations"],
        ["Evidence Support", "Stable medication state required for consistent tDCS outcome interpretation", "Document carefully; avoid changing medication mid-block"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["ASD Medication(s) Name & Dose", ""],
        ["Duration at Current Dose", "___ weeks"],
        ["Primary Informant for Ratings", "□ Parent/Caregiver  □ Teacher  □ Self  — Name: ___"],
        ["Session Environment Consistency", "□ Same room  □ Different — Note: ___"],
        ["Routine Disruption Before Session?", "□ None  □ Mild  □ Significant — Note: ___"],
        ["Chosen State for Block", "□ Stable medication (default)  □ Titration (document rationale)"],
        ["Session Start Time", "Keep consistent: ___:___ AM/PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Social-Communication", "L-DLPFC anodal 1–2mA", "Social cognition tasks (emotion recognition)", "SRS-2, ADOS-2 social, CGI-I"],
        ["Repetitive Behaviour", "SMA cathodal tDCS", "Habit flexibility / schedule disruption tasks", "RBS-R, CYBOCS-ASD, CGI-I"],
        ["ADHD-comorbid", "Bilateral DLPFC tDCS", "Sustained attention / WM tasks during tDCS", "CAARS, BRIEF-2, Conners"],
        ["Anxiety-comorbid", "L-DLPFC + CES", "Relaxation + sensory regulation tasks", "SCARED, GAD-7 (adapted), BRIEF"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["ASD medication name, dose, and duration at current dose recorded", "□ Yes", "□"],
        ["Primary informant identified and consistent across all assessments", "□ Yes", "□"],
        ["Session environment controlled for sensory load consistency", "□ Yes", "□"],
        ["Routine disruption before session documented", "□ Yes", "□"],
        ["Baseline assessment medication state and informant recorded", "□ Yes", "□"],
        ["Follow-up in same medication state, same informant, same environment", "□ Yes", "□"],
        ["Medication changes during block documented", "□ Yes", "□"],
        ["Session tolerance and sensory response noted each session", "□ Yes", "□"],
        ["Outcomes interpreted with informant and environment context", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive intervention; goals are improving specific functional domains", "tDCS treats or cures autism spectrum disorder"],
        ["Effects are targeted at specific symptom clusters (attention, repetitive behaviour) rather than core ASD", "tDCS changes the fundamental nature of autism"],
        ["Evidence is preliminary; session tolerance varies; outcomes are individual", "tDCS is equivalent to ABA or standard ASD interventions"],
    ],
)

# ── 12. LONG COVID ───────────────────────────────────────────────────────────
CONDITIONS_2["long_covid"] = dict(
    name="Long COVID (Post-COVID Syndrome)", short="Long COVID", slug="long_covid",
    med_class="Symptomatic (LDN/SSRIs)", med_name="symptomatic/neuromodulatory agent",
    phenotype_options="□ Cognitive (Brain Fog)  □ Autonomic/POTS  □ Fatigue-dominant  □ Cardio-respiratory  □ Mixed",
    subtitle="Long COVID Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, LDN/SSRI-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to post-exertional malaise and good day/bad day fluctuation characteristic of Long COVID.",
    measurement_confound_warning=(
        "WARNING: Post-exertional malaise (PEM) triggered by activity before assessment can create a false "
        "non-responder. Good day vs bad day fluctuation is extreme in Long COVID. Always assess on a rested day, "
        "document exertion level 24–48h prior, screen for viral reactivation episodes, and use consistent pacing."
    ),
    sec7_title="7. LDN/SSRI-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. Low-dose naltrexone modulates microglial neuroinflammation; SSRIs address mood and autonomic components — both influence cortical excitability in Long COVID.",
    sec7a_title="7A. Rested Day vs Post-Exertional State Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Assess ONLY on a rested day with no significant exertion in the preceding 24–48 hours. "
        "Post-exertional malaise is the most critical source of false classification in Long COVID."
    ),
    sec7c_title="7C. LDN/SSRI + tDCS Pairing by Long COVID Phenotype",
    sec7d_title="7D. Long COVID Medication-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Cognitive (Brain Fog)  □ Autonomic/POTS  □ Fatigue-dominant  □ Cardio-respiratory  □ Mixed"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Cognitive (Brain Fog)", "Improvement on MoCA, PASAT, or patient-reported cognitive function (DSQ-2 cognitive)", "□ Y □ N", ""],
        ["Fatigue", "≥4 point improvement on FACIT-F or DSQ-2 fatigue subscale", "□ Y □ N", ""],
        ["Autonomic/HRV", "Improved orthostatic tolerance, HRV, or POTS symptom reduction", "□ Y □ N", ""],
        ["Function/Quality of Life", "Better daily activity tolerance; reduced PEM frequency; improved SF-36", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Cognitive/Brain Fog (DLPFC)", "Processing speed, WM, word-finding deficits; CEN hypoactivation; neuroinflammation", "L-DLPFC anodal + paced cognitive tasks (brief)", "Emerging (pilot)"],
        ["Fatigue-dominant (CES+DLPFC)", "Profound fatigue; post-exertional malaise; brainstem-autonomic dysregulation", "CES + DLPFC adjunct + paced micro-tasks", "Emerging"],
        ["Autonomic/POTS (taVNS-led)", "Orthostatic intolerance; vagal tone dysregulation; HRV reduction", "taVNS primary + DLPFC adjunct + breathing tasks", "Emerging"],
        ["Mood/Dysautonomia overlap (DLPFC+taVNS)", "Anxiety/depression + autonomic instability; limbic-ANS dysregulation", "DLPFC + taVNS + CES + relaxation", "Emerging"],
        ["Sleep disruption (CES-led)", "Non-restorative sleep; altered circadian rhythm; high fatigue on waking", "CES evening protocol + morning DLPFC tDCS", "Emerging"],
        ["Mixed/Multi-system (multi-target)", "Brain fog + fatigue + autonomic + mood; widespread network disruption", "Staged DLPFC + taVNS + CES approach; pacing-based protocol", "Emerging"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["Cognitive impairment as a core complaint (not fatigue-only)", "DLPFC tDCS most specific when CEN-brain fog is primary target", "□ Y □ N"],
        ["Stable post-COVID phase (no active viral reactivation)", "Active reactivation episodes confound neural state and symptom levels", "□ Y □ N"],
        ["Pacing protocol in place (no PEM cycles)", "PEM must be controlled to prevent false non-responder classification", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON CEN disruption and autonomic network mapping guides protocol", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "DLPFC for brain fog; CES for fatigue/sleep; taVNS for autonomic/POTS phenotype"],
        ["Session intensity", "Start with low-intensity short sessions (15–20 min); titrate up; strict pacing"],
        ["PEM monitoring", "Stop protocol if PEM is triggered; do not push through; restart only when rested"],
        ["Network alignment", "FNON CEN hypoactivation + ANS dysregulation + sleep network disruption guides protocol"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "Meaningful improvement in cognitive or fatigue domain + better activity tolerance without PEM increase", "Continue protocol; maintain pacing; plan maintenance"],
        ["Partial Responder", "Brain fog improvement without fatigue change OR fatigue improvement without PEM reduction", "Review pacing; adjust modality mix; consider taVNS addition"],
        ["Non-Responder", "No improvement in any domain after adequate trial with strict pacing", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Severe PEM triggered by tDCS sessions themselves", "Session-induced exertion paradoxically worsens condition", "Ultra-low dose CES only; consider discontinuation"],
        ["Active viral reactivation episode during treatment block", "Ongoing inflammatory activity confounds neural state", "Pause; resume only after stable for 2+ weeks"],
        ["Severe autonomic instability (POTS, syncope)", "Cardiovascular instability during sessions; safety concern", "Cardiologist/autonomic specialist clearance first; taVNS only"],
        ["Psychiatric comorbidity dominating presentation (severe depression)", "Depressive circuit may be primary target; Long COVID label may obscure", "Treat depression; reassess Long COVID phenotype"],
    ],
    med_state_comparison=[
        ["Factor", "Stable LDN/SSRI State (Default SOZO)", "Post-Exertional / Viral Reactivation State (Defer)"],
        ["Definition", "tDCS on rested day during stable LDN/SSRI dosing without recent PEM", "tDCS within 48h of significant exertion or during viral reactivation"],
        ["Cognitive State", "Stable brain fog level; consistent cognitive performance", "PEM-triggered cognitive worsening masks tDCS benefit"],
        ["Session Tolerance", "Better stamina; task completion more likely", "Severe fatigue; session may trigger further PEM"],
        ["Comparison Validity", "Valid within-block if pacing consistent", "Invalid comparison; reschedule to rested day"],
        ["Evidence Support", "All Long COVID NIBS protocols require rest-day administration", "Never assess during active PEM or viral episode"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["LDN/SSRI Name & Dose", ""],
        ["Duration at Current Dose", "___ weeks"],
        ["PEM Status in Last 48h?", "□ None  □ Mild  □ Moderate/Severe — Defer session"],
        ["Exertion Level in Last 24h", "□ Rest  □ Light activity  □ Moderate (note type): ___"],
        ["Viral Reactivation Signs?", "□ None  □ Yes (fever, fatigue spike) — Defer session"],
        ["Chosen State for Block", "□ Rested, stable (default)  □ Other (document rationale)"],
        ["Session Start Time", "Keep consistent (morning preferred): ___:___ AM/PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Brain Fog / Cognitive", "L-DLPFC anodal 1–2mA (20 min)", "Paced cognitive micro-tasks (brief WM)", "MoCA, PASAT, DSQ-2 cognitive, PHQ-9"],
        ["Fatigue-dominant", "CES primary + DLPFC adjunct", "Paced breathing + light cognitive task", "FACIT-F, DSQ-2, SF-36, ISI"],
        ["Autonomic/POTS", "taVNS primary + DLPFC adjunct", "Slow breathing HRV biofeedback tasks", "NASA-LBT, HRV, FACIT-F"],
        ["Mixed/Multi-system", "Staged: CES → DLPFC → taVNS", "Rotated micro-tasks with rest intervals", "DSQ-2 total, SF-36, FACIT-F, MoCA"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["LDN/SSRI name, dose, and duration at current dose recorded", "□ Yes", "□"],
        ["PEM status and exertion level in last 48h documented", "□ Yes", "□"],
        ["Viral reactivation symptoms screened and absent before session", "□ Yes", "□"],
        ["Session only proceeded on confirmed rested day", "□ Yes", "□"],
        ["Baseline assessment rested-day status and medication state recorded", "□ Yes", "□"],
        ["Follow-up assessment on rested day in same medication state", "□ Yes", "□"],
        ["Any PEM triggered by sessions documented and protocol adjusted", "□ Yes", "□"],
        ["Session start time consistent across block", "□ Yes", "□"],
        ["Outcomes interpreted with PEM and exertion context", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive symptom-management tool used within a pacing framework", "tDCS cures Long COVID or restores pre-illness function"],
        ["Effects target brain fog, fatigue, and autonomic regulation; strict pacing required", "tDCS eliminates post-exertional malaise"],
        ["Evidence is preliminary; this is an emerging application; individual response varies widely", "tDCS is an established treatment for Long COVID"],
    ],
)

# ── 13. TINNITUS ─────────────────────────────────────────────────────────────
CONDITIONS_2["tinnitus"] = dict(
    name="Tinnitus", short="Tinnitus", slug="tinnitus",
    med_class="Off-label (Gabapentin/Betahistine)", med_name="off-label tinnitus agent",
    phenotype_options="□ Tonal  □ Narrowband Noise  □ Pulsatile  □ Somatic  □ Musical (MH)",
    subtitle="Tinnitus Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, Off-Label Medication-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to tinnitus loudness fluctuation with noise exposure, stress level, and time-of-day variation.",
    measurement_confound_warning=(
        "WARNING: Noise exposure before assessment, high stress levels, sleep disruption, and time of day (tinnitus "
        "typically louder at night and in quiet environments) can create false responders or non-responders. "
        "Always assess at the same quiet-environment time of day with consistent pre-session noise exposure control."
    ),
    sec7_title="7. Off-Label Medication-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. Off-label agents (gabapentin, betahistine) modulate GABAergic and histaminergic auditory pathways; interaction with tDCS auditory cortex targeting is dose-dependent.",
    sec7a_title="7A. Medicated vs Unmedicated State Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Choose ONE pre-session noise environment and time-of-day window for all assessments. "
        "Noise exposure before assessment and time-of-day variability are the most common sources of false classification in tinnitus."
    ),
    sec7c_title="7C. Off-Label Medication + tDCS Pairing by Tinnitus Phenotype",
    sec7d_title="7D. Tinnitus Medication-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Tonal  □ Narrowband Noise  □ Pulsatile  □ Somatic  □ Musical (MH)"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Tinnitus Loudness", "≥20% reduction in VAS tinnitus loudness or THI loudness subscale", "□ Y □ N", ""],
        ["Tinnitus Distress", "≥20 point reduction in THI total score or clinically meaningful TFI change", "□ Y □ N", ""],
        ["Sleep/Function", "Improved sleep quality (ISI) related to tinnitus; reduced interference", "□ Y □ N", ""],
        ["Anxiety/Mood", "Reduction in tinnitus-related anxiety or depression (GAD-7, PHQ-9)", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Tonal/Narrowband (Auditory cortex)", "Pure tone or narrow-band tinnitus; auditory cortex maladaptive plasticity; hyperactivation of A1", "Cathodal tDCS over left A1/temporal + auditory tasks", "Moderate (pilot RCTs)"],
        ["Distress-dominant (DLPFC+A1)", "High THI distress; tinnitus-related anxiety/depression; PFC-limbic dysregulation", "L-DLPFC anodal + temporal cathodal + CBT tasks", "Moderate"],
        ["Somatic tinnitus (C3/4 + temporal)", "Tinnitus modulated by jaw/neck movement; somatosensory-auditory integration", "Temporal + somatosensory tDCS + somatic manoeuvre tasks", "Emerging"],
        ["Pulsatile (taVNS-led)", "Vascular/middle ear origin; autonomic component; altered interoception", "taVNS + temporal tDCS + attention diversion tasks", "Emerging"],
        ["Hyperacusis comorbid (A1 cathodal)", "Tinnitus + sound sensitivity; auditory cortex hyperexcitability", "A1 cathodal tDCS + sound enrichment protocol", "Emerging"],
        ["Musical hallucination (bilateral temporal)", "Musical ear syndrome; older adult; bilateral auditory hyperactivation", "Bilateral temporal cathodal + engaging auditory tasks", "Emerging"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["Chronic tinnitus <5 years duration", "Greater auditory cortex plasticity remaining; better tDCS response", "□ Y □ N"],
        ["High distress component (THI >36)", "PFC-limbic component accessible to DLPFC targeting adjunct", "□ Y □ N"],
        ["No significant sensorineural hearing loss (or aided)", "Peripheral hearing loss limits auditory cortex response; aids help", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON auditory-limbic network mapping guides temporal/DLPFC targeting", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "Left A1/temporal cathodal for tonal tinnitus; DLPFC anodal for distress phenotype"],
        ["Noise control", "No loud noise exposure within 2h pre-session; consistent quiet environment"],
        ["Sound enrichment", "Background sound enrichment during sessions may enhance tDCS effects"],
        ["Network alignment", "FNON auditory hyperactivation + limbic-distress circuit guides dual-target protocol"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "≥20 point THI reduction + meaningful loudness or distress improvement", "Continue protocol; plan maintenance"],
        ["Partial Responder", "Distress reduction without loudness change OR sleep improvement without THI change", "Re-phenotype; add DLPFC component or adjust auditory target"],
        ["Non-Responder", "<10 point THI change after adequate trial", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Tinnitus >10 years with complete habituation failure", "Chronic maladaptive plasticity deeply entrenched; cortical remodelling limited", "Sound therapy intensification; CBT for tinnitus; TPS referral"],
        ["Significant sensorineural hearing loss (unaided)", "Peripheral deprivation drives tinnitus centrally; tDCS cannot address peripheral source", "Hearing aid fitting first; reassess with adequate amplification"],
        ["Objective tinnitus with vascular/middle ear cause", "Non-neurological source not amenable to cortical neuromodulation", "ENT/vascular referral; consider discontinuation"],
        ["Severe hyperacusis preventing session tolerance", "Sound sensitivity during sessions; electrode discomfort compounds hyperacusis", "Adapted very low-intensity protocol; sound enrichment first"],
    ],
    med_state_comparison=[
        ["Factor", "Stable Medicated State (Default SOZO)", "Noise-Exposed / High-Stress State (Avoid for Assessment)"],
        ["Definition", "tDCS after consistent quiet period; stable off-label medication dose", "tDCS within 2h of loud noise or during high-stress/anxiety day"],
        ["Tinnitus Level", "More stable tinnitus loudness baseline for comparison", "Noise-elevated tinnitus may mask tDCS benefit or create false response"],
        ["Auditory Cortex State", "Stable excitability without recent sound-driven arousal", "Noise-induced temporary hyperactivation confounds cathodal effect"],
        ["Comparison Validity", "Valid within-block if noise control is consistent", "Invalid; reschedule if significant noise exposure occurred before session"],
        ["Evidence Support", "Quiet pre-session period required for auditory cortex tDCS protocols", "Document and flag if noise control could not be maintained"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["Off-Label Medication Name & Dose (if prescribed)", ""],
        ["Duration at Current Dose", "___ weeks"],
        ["Noise Exposure Within 2h Pre-Session?", "□ None  □ Mild  □ Loud — Type: ___"],
        ["Tinnitus Loudness at Session Start (VAS)", "___/10"],
        ["Sleep Quality Night Before", "□ Good  □ Fair  □ Poor"],
        ["Pre-Session Environment", "□ Quiet  □ Background noise  □ Loud — Ensure quiet before proceeding"],
        ["Session Start Time", "Keep consistent (same time of day): ___:___ AM/PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Tonal/Narrowband", "Left temporal cathodal (A1) 2mA", "Auditory attention diversion tasks", "THI, TFI, VAS loudness/distress"],
        ["Distress-dominant", "L-DLPFC anodal + temporal cathodal", "CBT-tinnitus attention tasks + relaxation", "THI, GAD-7, PHQ-9, ISI"],
        ["Somatic tinnitus", "Temporal + somatosensory tDCS", "Jaw/neck manoeuvre correction tasks", "THI somatic subtype, VAS"],
        ["Hyperacusis comorbid", "A1 cathodal (low intensity 1mA)", "Sound enrichment + graded exposure", "HQ, THI, LDL testing"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["Off-label medication name, dose, and duration at current dose recorded", "□ Yes", "□"],
        ["Noise exposure within 2h pre-session checked and documented", "□ Yes", "□"],
        ["Tinnitus loudness VAS at session start recorded", "□ Yes", "□"],
        ["Pre-session environment (quiet) confirmed", "□ Yes", "□"],
        ["Baseline assessment noise context and medication state recorded", "□ Yes", "□"],
        ["Follow-up at same time of day in same quiet environment", "□ Yes", "□"],
        ["Medication changes during block documented", "□ Yes", "□"],
        ["Sleep quality night before assessment noted", "□ Yes", "□"],
        ["Outcomes interpreted with noise exposure and time-of-day context", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS is an adjunctive intervention; goal is tinnitus distress and loudness reduction", "tDCS eliminates or cures tinnitus"],
        ["Effects target auditory cortex plasticity and limbic distress components", "tDCS repairs hearing or removes the tinnitus signal"],
        ["Evidence is emerging; response varies; this works best for central/distress phenotype", "tDCS is equivalent to sound therapy or CBT for tinnitus"],
    ],
)

# ── 14. INSOMNIA ─────────────────────────────────────────────────────────────
CONDITIONS_2["insomnia"] = dict(
    name="Insomnia Disorder", short="Insomnia", slug="insomnia",
    med_class="Z-drugs/Suvorexant/Trazodone", med_name="sleep pharmacotherapy agent",
    phenotype_options="□ Sleep-onset  □ Sleep-maintenance  □ Early-waking  □ Hyperarousal  □ Mixed",
    subtitle="Insomnia Responder Tracking & Classification",
    sec2_subtitle="SOZO Response Assessment, Sleep Medication-tDCS Documentation & FNON Non-Responder Pathway",
    false_nonresponder_note="This avoids \"false non-responder\" labelling due to night-to-night sleep variability and weekend vs weekday pattern differences.",
    measurement_confound_warning=(
        "WARNING: Night-to-night sleep variability is inherent in insomnia. If baseline uses a single poor-sleep night "
        "and follow-up uses a single good-sleep night (or vice versa), you will create false responders or non-responders. "
        "Always use 7-day sleep diary averages for assessments; document weekend vs weekday patterns and sleep medication use."
    ),
    sec7_title="7. Sleep Medication-tDCS Scheduling & Documentation",
    sec7_intro="tDCS effects are state-dependent. Z-drugs/suvorexant modulate GABA-A/orexin pathways; trazodone affects histaminergic arousal — all interact with tDCS effects on hyperarousal circuits.",
    sec7a_title="7A. Sleep-Medicated vs Medication-Free Night Comparison",
    scheduling_rule=(
        "SOZO Standard Rule: Assess using 7-day sleep diary averages, NOT single-night measures. "
        "Use the SAME sleep medication timing and weekday/weekend pattern for all assessment windows to ensure valid comparison."
    ),
    sec7c_title="7C. Sleep Medication + tDCS Pairing by Insomnia Phenotype",
    sec7d_title="7D. Sleep Medication-tDCS Documentation Checklist",
    phenotype_row=["Phenotype", "□ Sleep-onset  □ Sleep-maintenance  □ Early-waking  □ Hyperarousal  □ Mixed"],
    response_domains=[
        ["Domain", "Response Criteria", "Met?", "Notes"],
        ["Sleep Onset", "Reduction in SOL by ≥30 min on 7-day diary average or ISI sleep onset item", "□ Y □ N", ""],
        ["Sleep Maintenance", "Reduction in WASO by ≥30 min on 7-day diary average or ISI maintenance item", "□ Y □ N", ""],
        ["Sleep Quality", "≥6 point reduction on ISI total score (MCID) or PSQI meaningful improvement", "□ Y □ N", ""],
        ["Daytime Function", "Improved daytime fatigue, alertness, or daily function by self-report", "□ Y □ N", ""],
    ],
    responder_profiles=[
        ["Phenotype", "Best-Fit Patient Profile", "Protocol", "Evidence"],
        ["Hyperarousal/Sleep-onset (CES-led)", "Cognitive hyperarousal; racing thoughts at bedtime; cortical over-activation; high ANS arousal", "CES evening protocol + DLPFC cathodal + relaxation tasks", "Moderate (RCT support)"],
        ["Sleep-maintenance (CES+DLPFC)", "Frequent nocturnal awakenings; light sleep; reduced slow-wave activity", "CES + DLPFC tDCS + sleep restriction therapy support", "Moderate"],
        ["Early-waking (DLPFC+taVNS)", "Early morning awakening; often comorbid depression; circadian phase advance", "taVNS + DLPFC tDCS + CBT-I support", "Emerging"],
        ["Anxiety-driven insomnia (DLPFC+CES)", "Anticipatory anxiety about sleep; sleep effort paradox; amygdala hyperactivation", "L-DLPFC anodal + CES + stimulus control tasks", "Moderate"],
        ["Circadian-disrupted (taVNS+CES)", "Irregular sleep-wake timing; shift work; chronotype mismatch", "taVNS + CES + bright light therapy adjunct", "Emerging"],
        ["Comorbid depression/insomnia (DLPFC+CES)", "Sleep disruption driven by depression; early waking; non-restorative sleep", "DLPFC tDCS + taVNS + CES + CBT-I elements", "Moderate"],
    ],
    clinical_predictors=[
        ["Predictor", "Why It Matters", "Present?"],
        ["Primary insomnia with hyperarousal as core feature", "CES and DLPFC protocols most effective for cortical/ANS hyperarousal phenotype", "□ Y □ N"],
        ["CBT-I ongoing or willingness to engage with sleep hygiene", "tDCS augments CBT-I; sleep behaviours required for sustained gains", "□ Y □ N"],
        ["Sleep medication at stable dose (not acutely changing)", "Medication changes confound sleep architecture measurement", "□ Y □ N"],
        ["Network hypothesis confirmed by 6-Network Assessment", "FNON hyperarousal network and sleep circuit mapping guides CES/DLPFC targeting", "□ Y □ N"],
    ],
    protocol_predictors=[
        ["Factor", "Recommendation"],
        ["Target choice", "CES (evening) for hyperarousal; DLPFC tDCS for cognitive/anxiety phenotype; taVNS for circadian/depression"],
        ["Session timing", "CES in evening (1–2h before bed); DLPFC tDCS daytime; not immediately before sleep"],
        ["Diary requirement", "7-day sleep diary mandatory for valid assessment; single-night measurement unreliable"],
        ["Network alignment", "FNON hyperarousal circuit + default mode hyperactivation guides inhibitory montage selection"],
    ],
    response_classification=[
        ["Classification", "Criteria", "Action"],
        ["Responder", "≥6 point ISI reduction + meaningful SOL or WASO improvement on 7-day average", "Continue protocol; plan maintenance with CBT-I"],
        ["Partial Responder", "ISI reduction 3–5 points OR sleep quality improvement without SOL/WASO change", "Re-phenotype; adjust session timing; intensify CBT-I integration"],
        ["Non-Responder", "<3 point ISI change after adequate trial with diary-based assessment", "Follow FNON Non-Responder Pathway (Section 6)"],
    ],
    non_responder_profiles=[
        ["Profile", "Why Limited Response", "Alternative Strategy"],
        ["Insomnia with significant sleep apnoea (untreated)", "Respiratory arousal driving insomnia; cortical modulation insufficient", "Sleep study; CPAP initiation; reassess after treatment"],
        ["Chronic hypnotic dependence (benzodiazepines >3 months)", "Rebound insomnia and tolerance confound sleep measurement", "Gradual taper program; CBT-I intensification; specialist review"],
        ["Insomnia secondary to uncontrolled psychiatric disorder", "Primary diagnosis driving sleep disruption; tDCS insufficient", "Treat primary condition; reassess insomnia phenotype"],
        ["Extreme sleep phase disorder (severe DSPS/ASPS)", "Circadian misalignment requires chronotherapy; cortical protocols insufficient alone", "Chronotherapy; bright light; melatonin; reassess after phase correction"],
    ],
    med_state_comparison=[
        ["Factor", "Stable Sleep Medication State (Default SOZO)", "Medication Change / Acute Adjustment (Avoid)"],
        ["Definition", "tDCS during stable sleep medication dose with consistent use pattern", "tDCS during hypnotic initiation, dose change, or taper"],
        ["Sleep Architecture", "Consistent sleep structure for within-block diary comparison", "Medication change alters REM/NREM; confounds diary measures"],
        ["Task Participation", "Better daytime alertness at stable dose; consistent session engagement", "Residual sedation or rebound insomnia reduces session compliance"],
        ["Comparison Validity", "7-day diary averages valid at stable medication state", "Cannot attribute diary changes to tDCS during medication adjustment"],
        ["Evidence Support", "All CES/tDCS insomnia protocols require stable pharmacological baseline", "Document if medication changes are clinically necessary; flag in assessment"],
    ],
    med_documentation=[
        ["Domain", "Details"],
        ["Sleep Medication Name & Dose", ""],
        ["Frequency of Use", "□ Nightly  □ PRN (freq: ___ nights/week)"],
        ["Duration at Current Regimen", "___ weeks"],
        ["7-Day Sleep Diary Completed?", "□ Yes — Average SOL: ___ min, WASO: ___ min  □ No"],
        ["Weekend vs Weekday Pattern Difference?", "□ Similar  □ Different (weekend later by ___ hours)"],
        ["Chosen State for Block", "□ Stable medication regimen (default)  □ Tapering (document rationale)"],
        ["Session Timing for CES (if used)", "Evening: ___:___ PM"],
    ],
    phenotype_pairing=[
        ["Phenotype", "tDCS Config", "Concurrent Task", "Outcome Measures"],
        ["Hyperarousal/Sleep-onset", "CES evening (1–2h pre-bed) + DLPFC cathodal", "Relaxation + PMR + CBT-I stimulus control", "ISI, PSQI, 7-day diary SOL"],
        ["Sleep-maintenance", "CES + DLPFC tDCS daytime", "Sleep restriction support + wake-time activity tasks", "ISI, 7-day diary WASO, PSQI"],
        ["Anxiety-driven insomnia", "L-DLPFC anodal + CES evening", "Cognitive restructuring + worry time task", "ISI, GAD-7, DBAS-16, diary"],
        ["Comorbid depression + insomnia", "DLPFC + taVNS + CES evening", "Behavioural activation + CBT-I combined", "PHQ-9, ISI, PSQI, FACIT-F"],
    ],
    doc_checklist=[
        ["Documentation Item", "Completed", "N/A"],
        ["Sleep medication name, dose, and frequency of use recorded", "□ Yes", "□"],
        ["7-day sleep diary completed for each assessment window", "□ Yes", "□"],
        ["Weekend vs weekday sleep pattern difference documented", "□ Yes", "□"],
        ["Baseline assessment 7-day diary window and medication state recorded", "□ Yes", "□"],
        ["Follow-up 7-day diary window uses same weekday/weekend composition", "□ Yes", "□"],
        ["Medication changes during block documented", "□ Yes", "□"],
        ["CES session timing relative to bedtime documented (if applicable)", "□ Yes", "□"],
        ["DAYTIME session start time consistent across block", "□ Yes", "□"],
        ["Outcomes use 7-day averages, not single-night measures", "□ Yes", "□"],
    ],
    language_guide=[
        ["Appropriate to State", "AVOID Stating"],
        ["tDCS/CES is an adjunctive intervention best combined with CBT-I principles", "tDCS or CES replaces sleep medication or cures insomnia disorder"],
        ["Effects target cortical hyperarousal and ANS dysregulation; sleep behaviour change also required", "tDCS induces deep sleep or repairs sleep architecture independently"],
        ["Evidence is promising for hyperarousal phenotype; CBT-I remains gold standard", "tDCS is equivalent to CBT-I for chronic insomnia"],
    ],
)
