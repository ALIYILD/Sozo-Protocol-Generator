# DEPRECATED: This script is superseded by the canonical generation pipeline.
# Use instead: GenerationService.generate(condition="...", tier="...", doc_type="...")
# Or CLI: PYTHONPATH=src python -m sozo_generator.cli.main build condition --condition <slug> --tier <tier> --doc-type <type>
# See docs/MIGRATION_PLAN.md for details.

"""Append Tinnitus and Insomnia condition data, then add runner block."""
import os
OUTFILE = os.path.join(os.path.dirname(__file__), "generate_fellow_protocols.py")

BLOCK = '''
# ---------------------------------------------------------------------------
# CONDITION: TINNITUS
# ---------------------------------------------------------------------------
CONDITIONS["tinnitus"] = dict(
    name="Chronic Tinnitus",
    icd10="H93.19",
    doc_num="SPG-TN-001",
    tps_status="Investigational",
    tdcs_class="Class IIb",
    tps_class="Investigational",
    tavns_class="Class IIb",
    ces_class="Class IIb",
    inclusion=[
        "Chronic tinnitus ≥6 months duration (unilateral or bilateral; tonal or noise-like)",
        "THI (Tinnitus Handicap Inventory) score ≥38 (moderate-severe) at baseline",
        "Audiological assessment confirming tinnitus etiology and excluding treatable causes",
        "Age 18–75; capable of informed consent",
        "Inadequate response to ≥1 conventional treatment (sound therapy, CBT, hearing aids)",
        "Stable audiological status for ≥3 months (no acute hearing loss)",
    ],
    exclusion=[
        "Pulsatile tinnitus (vascular/structural etiology requiring separate workup)",
        "Active Meniere disease with acute vertigo attacks",
        "Metallic implants in head/neck or implanted neurostimulator (cochlear implant — evaluate carefully)",
        "Active otological infection or post-surgical healing",
        "Pregnancy",
        "Active psychiatric comorbidity requiring immediate intervention (psychosis, active suicidality)",
        "Severe hyperacusis requiring noise-restricted environment (assess TPS compatibility)",
    ],
    discussion=[
        "Chronic tinnitus involves maladaptive central auditory network reorganization following peripheral deafferentation or acoustic trauma.",
        "The primary auditory cortex (A1) shows increased spontaneous activity and decreased lateral inhibition, generating a phantom auditory percept.",
        "The parahippocampal area and amygdala are recruited into the tinnitus network, driving the affective distress and attention capture dimensions.",
        "DLPFC hypoactivity impairs top-down suppression of the auditory phantom via the salience and executive networks.",
        "tDCS targeting auditory cortex (cathodal) reduces A1 hyperexcitability; tDCS over DLPFC (anodal) strengthens top-down suppression.",
        "TPS directly targets A1 and DLPFC to normalize the tinnitus network node hyperactivation.",
        "taVNS combined with auditory tone presentation (VNS-tone pairing) facilitates auditory cortex reorganization through neuromodulatory plasticity.",
        "CES addresses tinnitus-related insomnia and anxiety through thalamic and brainstem auditory relay modulation.",
    ],
    overview=[
        "Chronic tinnitus — the perception of sound without an external acoustic source — affects approximately 15% of the global population, with 2-3% experiencing severe, debilitating symptoms. The neurobiological substrate involves maladaptive central auditory plasticity: increased spontaneous firing in primary auditory cortex (A1), reduced lateral inhibition, and pathological coupling between the auditory network and distress-generating regions (amygdala, parahippocampal gyrus, prefrontal cortex).",
        "The SOZO NIBS protocol targets the tinnitus neural network through a phenotype-guided multimodal approach: tDCS (A1 cathodal / DLPFC anodal), TPS (A1/DLPFC), taVNS (auditory cortex plasticity/neuromodulation), and CES (Alpha-Stim, anxiety/sleep). The tinnitus network — not just the auditory cortex — is the target.",
        "Five clinical phenotypes guide protocol selection: audiological/peripheral (hearing loss dominant), central/network (no hearing loss; central reorganization dominant), distress-dominant (high THI, anxiety, depression), sleep-dominant (tinnitus-insomnia cycle), and hyperacusis comorbid. Each phenotype receives a tailored NIBS combination.",
    ],
    pathophysiology=[
        "Central auditory reorganization: peripheral deafferentation triggers tonotopic map reorganization in A1; neurons adjacent to deafferented frequencies expand territory, generating spurious signals perceived as tinnitus.",
        "Increased spontaneous neural activity: A1 and secondary auditory cortex (A2) show elevated baseline firing rates; reduced lateral inhibition allows phantom percept to dominate.",
        "Tinnitus distress network: amygdala, parahippocampal gyrus, and anterior cingulate are recruited into the tinnitus network, generating affective suffering and attention capture.",
        "DLPFC top-down suppression failure: prefrontal inhibition of auditory attention is impaired, allowing tinnitus percept to dominate attentional resources.",
        "Thalamocortical dysrhythmia: delta band power increases and gamma power decreases in auditory thalamus (MGN), producing a pathological oscillatory signature.",
        "Default mode network coupling: DMN incorporates tinnitus-related activity, causing persistent awareness even during mind-wandering states.",
    ],
    std_treatment=[
        "Sound therapy: broadband noise, tinnitus masking, notched music therapy",
        "Cognitive behavioral therapy (CBT) for tinnitus distress: gold-standard psychological intervention",
        "Tinnitus retraining therapy (TRT): habituation-based counseling + sound therapy",
        "Hearing aids: amplification-based tinnitus management for hearing loss subtype",
        "rTMS: 1Hz low-frequency rTMS over left temporoparietal cortex (investigational)",
        "Pharmacological: no FDA-approved drug; off-label melatonin, clonazepam, acamprosate (limited evidence)",
    ],
    symptoms=[
        ["Tinnitus Percept", "Persistent sound (ringing, buzzing, hissing, roaring) without external source", "100%", "Jastreboff 2004"],
        ["Tinnitus Distress", "Emotional distress, annoyance, suffering related to tinnitus", "80%", "Andersson 2002"],
        ["Sleep Disturbance", "Difficulty falling/staying asleep due to tinnitus", "60%", "Crummer 2004"],
        ["Anxiety", "Tinnitus-related anxiety; health anxiety; GAD features", "45%", "Andersson 2004"],
        ["Depression", "Comorbid depressive disorder", "30%", "Sullivan 1988"],
        ["Concentration Impairment", "Difficulty concentrating; tinnitus captures attention", "70%", "Andersson 2002"],
        ["Hyperacusis", "Sound sensitivity; discomfort from everyday sounds", "40%", "Andersson 2002"],
        ["Avoidance Behavior", "Avoiding quiet/social situations; compensatory behaviors", "55%", "Jastreboff 2004"],
        ["Hearing Loss", "Sensorineural hearing loss as frequent comorbidity/trigger", "70%", "Axelsson 1996"],
        ["Catastrophizing", "Tinnitus catastrophizing scale; excessive negative appraisal", "50%", "Andersson 2002"],
    ],
    brain_regions=[
        ["Primary Auditory Cortex (A1)", "Tinnitus generator; hyperactive spontaneous firing; tonotopic reorganization", "tDCS cathodal, TPS", "Eggermont 2004"],
        ["Secondary Auditory Cortex (A2)", "Auditory association; tinnitus percept elaboration", "TPS", "Lockwood 2002"],
        ["DLPFC", "Top-down suppression of auditory attention; hypoactive in tinnitus", "tDCS anodal", "Schecklmann 2011"],
        ["Parahippocampal Gyrus", "Tinnitus memory and emotional tagging; tinnitus network node", "TPS", "Lockwood 2002"],
        ["Amygdala", "Tinnitus distress, threat appraisal, affective suffering", "taVNS, TPS", "Rauschecker 2010"],
        ["ACC", "Tinnitus distress monitoring, attention capture", "TPS", "Landgrebe 2009"],
        ["Medial Geniculate Nucleus", "Auditory thalamic relay; thalamocortical dysrhythmia source", "CES", "Llinás 1999"],
        ["Nucleus Accumbens", "Reward-gating of auditory attention; tinnitus gating failure", "TPS indirect", "Rauschecker 2010"],
    ],
    brainstem=[
        ["Cochlear Nucleus", "First central auditory relay; compensatory hyperactivity post-deafferentation", "None direct NIBS", "Moller 2000"],
        ["Inferior Colliculus (IC)", "Auditory midbrain; gain control; hyperactive in tinnitus", "None direct", "Salvi 2000"],
        ["Medial Geniculate Nucleus", "Thalamic auditory relay; thalamocortical dysrhythmia generator", "CES indirect", "Llinás 1999"],
        ["Locus Coeruleus", "Noradrenergic gating of auditory attention; anxiety-arousal in tinnitus", "taVNS, CES", "Brozoski 2007"],
        ["Nucleus Tractus Solitarius", "Vagal relay; taVNS mechanism for auditory plasticity", "taVNS direct", "Engineer 2011"],
    ],
    phenotypes=[
        ["Audiological/Peripheral Dominant", "Tinnitus with significant SNHL; peripheral deafferentation primary; A1 reorganization", "Hearing loss + tinnitus; audiological management primary", "tDCS A1 cathodal + DLPFC anodal + CES"],
        ["Central/Network Dominant", "Tinnitus without significant hearing loss; central reorganization primary", "High tinnitus loudness/distress despite normal audiogram", "tDCS A1 cathodal + TPS A1/DLPFC + taVNS"],
        ["Distress-Dominant", "High THI (≥56); anxiety, depression, catastrophizing; amygdala-network activation", "Severe distress, life quality impact, depression", "tDCS DLPFC + TPS ACC/amygdala + taVNS + CES"],
        ["Sleep-Dominant", "Tinnitus-insomnia cycle; hyperarousal maintaining tinnitus awareness at night", "Severe sleep disruption; fatigue; daytime cognitive impairment", "CES primary + tDCS DLPFC + taVNS"],
        ["Hyperacusis Comorbid", "Tinnitus + sound sensitivity; auditory gain dysregulation", "Avoidance of sound environments; reduced TPS tolerance", "tDCS A1 cathodal + CES; TPS with caution"],
    ],
    symptom_map=[
        ["Tinnitus loudness", "A1/A2", "tDCS A1 cathodal + TPS A1", "Eggermont 2004"],
        ["Tinnitus distress", "Amygdala/ACC/Parahippocampal", "TPS ACC + taVNS + tDCS DLPFC", "Rauschecker 2010"],
        ["Attention capture", "DLPFC/SN", "tDCS DLPFC anodal", "Schecklmann 2011"],
        ["Anxiety", "Amygdala/DLPFC", "taVNS + CES + tDCS DLPFC", "Andersson 2004"],
        ["Sleep disruption", "Thalamus/LC", "CES primary", "Lande 2018"],
        ["Depression comorbidity", "DLPFC/Limbic", "tDCS DLPFC + taVNS", "Brunoni 2013"],
        ["Hyperacusis", "A1/A2 gain", "tDCS A1 cathodal; CES", "Andersson 2002"],
        ["Concentration impairment", "DLPFC/CEN", "tDCS DLPFC anodal", "Schecklmann 2011"],
        ["Thalamocortical dysrhythmia", "MGN/A1", "CES indirect", "Llinas 1999"],
    ],
    montage=[
        ["Audiological/Peripheral", "Cathodal A1 (T3/T4, 1.5mA, 20min) + Anodal DLPFC (F3)", "A1 (200 pulses)", "Hearing aid; CES nightly; sound therapy concurrent"],
        ["Central/Network", "Cathodal A1 (T3/T4, 1.5mA, 20min) + Anodal DLPFC (F3)", "A1 + DLPFC (300 pulses)", "taVNS-tone pairing; TRT concurrent"],
        ["Distress-Dominant", "Anodal DLPFC (F3, 2mA, 20min)", "ACC (250 pulses)", "taVNS + CES nightly; CBT concurrent essential"],
        ["Sleep-Dominant", "Anodal DLPFC (F3, 1.5mA, 20min)", "None initial", "CES primary nightly; taVNS before bed"],
        ["Hyperacusis Comorbid", "Cathodal A1 (T3/T4, 1mA, 15min)", "None (TPS limited by hyperacusis)", "CES primary; sound desensitization concurrent"],
        ["Maintenance Phase", "Anodal DLPFC (F3, 1.5mA, 20min)", "None", "CES 3x/week; taVNS daily home"],
        ["Elderly Adjusted", "Cathodal A1 (T3, 1mA, 15min)", "A1 (150 pulses)", "CES primary; hearing aid"],
        ["High THI Refractory", "Cathodal A1 + Anodal DLPFC (2mA, 20min each)", "A1 + DLPFC (400 pulses)", "All 4 modalities; intensive CBT"],
        ["Unilateral Tinnitus", "Cathodal A1 ipsilateral (T3 or T4)", "A1 ipsilateral (200 pulses)", "Lateralized protocol; taVNS standard"],
        ["Sham Protocol", "F3 anodal (30s ramp, 0mA, 20min)", "None", "Sham control condition"],
    ],
    tdcs_protocols=[
        ["TN-tDCS-01", "A1 Cathodal (Tinnitus Percept Reduction)", "Fp1 or Fp2", "T3 or T4 (A1 ipsilateral)", "1.5mA, 20min, 10 sessions", "Fregni 2006"],
        ["TN-tDCS-02", "DLPFC Anodal (Top-Down Suppression)", "F3", "F4", "2mA, 20min, 10 sessions", "Schecklmann 2011"],
        ["TN-tDCS-03", "A1 Cathodal + DLPFC Anodal Combined", "F3 anodal; T3 cathodal", "F4; Fpz", "1.5–2mA, 15 sessions", "Expert consensus 2023"],
        ["TN-tDCS-04", "Bifrontal (Distress/Depression)", "F3 anodal", "F4 cathodal", "2mA, 20min, 10 sessions", "Brunoni 2013"],
        ["TN-tDCS-05", "Maintenance", "F3 anodal", "F4", "1.5mA, 20min, 2x/week", "Bikson 2016"],
        ["TN-tDCS-06", "Low Intensity (Hyperacusis)", "T3 cathodal", "Fpz", "1mA, 15min, 10 sessions", "Adjusted"],
        ["TN-tDCS-07", "Elderly Adjusted", "T3 cathodal", "Fp1", "1mA, 15min, 10 sessions", "Lefaucheur 2016"],
        ["TN-tDCS-08", "Sham", "F3", "F4", "30s ramp, 0mA, 20min", "Schecklmann 2011"],
    ],
    plato_protocols=[
        ["TN-PLATO-01", "A1 Cathodal", "T3/Fpz", "A1 ipsilateral", "T3", "1.5mA", "N/A", "Cathodal 20min"],
        ["TN-PLATO-02", "DLPFC Anodal", "F3/F4", "Left DLPFC", "F3", "2.0mA", "N/A", "Continuous 20min"],
        ["TN-PLATO-03", "Combined A1+DLPFC", "T3; F3", "A1 + DLPFC", "T3 cathodal; F3 anodal", "1.5; 2.0mA", "N/A", "Sequential"],
        ["TN-PLATO-04", "HD-tDCS A1", "T3 center", "4-electrode ring", "T3", "0.75mA", "N/A", "HD cathodal 20min"],
        ["TN-PLATO-05", "Maintenance", "F3", "DLPFC", "F3", "1.5mA", "N/A", "2x/week"],
        ["TN-PLATO-06", "Alpha tACS Auditory", "T3", "A1", "T3", "1.0mA", "10Hz", "tACS 20min — alpha normalization"],
        ["TN-PLATO-07", "Elderly/Hyperacusis", "T3", "A1", "T3", "1.0mA", "N/A", "15min cathodal"],
        ["TN-PLATO-08", "Sham", "F3", "DLPFC", "F3", "0mA", "N/A", "30s ramp"],
    ],
    tps_protocols=[
        ["TN-TPS-01", "A1 Hyperexcitability Reduction", "Primary Auditory Cortex (A1)", "200 pulses, 0.2Hz, 0.2mJ/mm²", "3 sessions/week", "Eggermont 2004"],
        ["TN-TPS-02", "DLPFC Top-Down Enhancement", "DLPFC (BA46)", "250 pulses, 0.2Hz", "3 sessions/week", "Schecklmann 2011"],
        ["TN-TPS-03", "ACC Distress Network", "ACC (BA24/32)", "200 pulses, 0.2Hz", "2 sessions/week", "Landgrebe 2009"],
        ["TN-TPS-04", "Parahippocampal (Memory/Distress)", "Parahippocampal Gyrus", "150 pulses, 0.2Hz", "2 sessions/week", "Lockwood 2002"],
        ["TN-TPS-05", "Full Network Protocol", "A1 + DLPFC + ACC sequential", "400 pulses total", "5 sessions/week x2 weeks", "Expert consensus 2024"],
    ],
    ces_role=[
        ["Sleep-Dominant Tinnitus", "Primary modality for tinnitus-insomnia cycle; reduces nighttime awareness", "Nightly 60min; in-ear or electrode"],
        ["Anxiety/Distress", "Reduces tinnitus-related anxiety and emotional reactivity", "Daily 60min; before high-stress periods"],
        ["Thalamic Dysrhythmia", "Indirect thalamic modulation via thalamocortical network", "Daily 60min; concurrent with sound therapy"],
        ["Maintenance", "Long-term distress and sleep maintenance", "3–5x/week; patient home use"],
    ],
    tavns_role="taVNS (tragus, 25Hz, 200µs, 0.5mA, 30min) for tinnitus leverages two mechanisms: (1) Auditory cortex plasticity facilitation — vagus nerve stimulation paired with tones drives targeted auditory cortex reorganization (Engineer 2011 demonstrated VNS-tone pairing reverses noise-induced tonotopic reorganization in animal models); (2) Distress network modulation via NTS → LC → amygdala pathway reduces tinnitus-related anxiety and emotional suffering. Clinical translation of VNS-tone pairing to taVNS is under active investigation. Standalone taVNS (without tone pairing) provides anxiolytic and autonomic benefits in tinnitus distress.",
    combinations=[
        ("Central/Network Dominant", [
            ["tDCS A1 cathodal + TPS A1 + taVNS", "Convergent A1 hyperexcitability reduction + vagal plasticity", "taVNS (tone pairing if available) → TPS → tDCS", "Central tinnitus without hearing loss"],
            ["tDCS A1 cathodal + tDCS DLPFC anodal + TPS DLPFC", "A1 inhibition + DLPFC top-down enhancement", "TPS DLPFC → tDCS DLPFC → tDCS A1", "Network dominant; high attention capture"],
        ]),
        ("Distress-Dominant", [
            ["tDCS DLPFC + TPS ACC + taVNS + CES", "Top-down suppression + distress network + vagal + anxiolytic", "taVNS → TPS → tDCS + CES nightly", "High THI, anxiety, depression comorbid"],
        ]),
        ("Sleep-Dominant", [
            ["CES + tDCS DLPFC + taVNS", "Sleep primary + top-down + vagal anxiety", "CES nightly; tDCS + taVNS daytime", "Tinnitus-insomnia cycle"],
        ]),
        ("Audiological/Peripheral", [
            ["tDCS A1 cathodal + TPS A1 + CES", "A1 inhibition + thalamic + sleep", "TPS → tDCS; CES nightly", "SNHL + tinnitus; hearing aid concurrent"],
        ]),
        ("Hyperacusis Comorbid", [
            ["tDCS A1 cathodal + CES", "A1 gain reduction + thalamic; TPS avoided in severe hyperacusis", "tDCS; CES nightly; sound desensitization", "Tinnitus + sound hypersensitivity"],
        ]),
        ("Refractory High THI", [
            ["tDCS A1 cathodal + tDCS DLPFC + TPS A1/DLPFC/ACC + taVNS + CES", "Full circuit: A1 + top-down + distress + vagal + sleep", "taVNS → TPS → tDCS (A1+DLPFC) + CES nightly", "THI ≥56, refractory to CBT and sound therapy"],
        ]),
    ],
    combination_summary=[
        ["Central/Network", "tDCS A1 cathodal + TPS A1 + taVNS", "A1 inhibition + vagal plasticity", "taVNS → TPS → tDCS A1", "Central tinnitus", "IIb"],
        ["Distress-Dominant", "tDCS DLPFC + TPS ACC + taVNS + CES", "Top-down + distress + vagal + sleep", "taVNS → TPS → tDCS + CES", "High distress/anxiety", "IIb"],
        ["Sleep-Dominant", "CES + tDCS DLPFC + taVNS", "Sleep + top-down + vagal", "CES nightly + daytime NIBS", "Tinnitus-insomnia", "IIb"],
        ["Audiological", "tDCS A1 cathodal + TPS A1 + CES", "A1 inhibition + thalamic", "TPS → tDCS + CES", "SNHL + tinnitus", "IIb"],
        ["Hyperacusis Comorbid", "tDCS A1 cathodal + CES", "A1 gain + thalamic; TPS avoided", "tDCS + CES nightly", "Hyperacusis + tinnitus", "IIb"],
        ["Refractory", "All modalities full protocol", "Full tinnitus network attack", "taVNS → TPS → tDCS × 2 + CES", "THI ≥56 refractory", "IIb"],
    ],
    outcomes=[
        ["Tinnitus Handicap Inventory (THI)", "Tinnitus-related handicap", "Baseline, 4wk, 8wk", "≥7-point reduction (MCID); ≥38-point reduction = grade improvement"],
        ["Tinnitus Functional Index (TFI)", "Multidimensional tinnitus impact", "Baseline, 4wk, 8wk", "≥13-point reduction (MCID)"],
        ["Visual Analog Scale — Loudness (VAS-L)", "Perceived tinnitus loudness", "Weekly", "≥20% reduction"],
        ["Visual Analog Scale — Distress (VAS-D)", "Emotional distress from tinnitus", "Weekly", "≥20% reduction"],
        ["Pittsburgh Sleep Quality Index (PSQI)", "Sleep quality", "Baseline, 4wk, 8wk", "≥3-point improvement"],
        ["GAD-7 / HADS-A", "Tinnitus-related anxiety", "Baseline, 4wk, 8wk", "≥5-point reduction"],
        ["PHQ-9", "Depression comorbidity", "Baseline, 4wk, 8wk", "≥5-point reduction"],
        ["Tinnitus Catastrophizing Scale (TCS)", "Catastrophizing about tinnitus", "Baseline, 4wk, 8wk", "≥30% reduction"],
        ["Minimum Masking Level (MML)", "Audiological tinnitus measure", "Baseline, 8wk", "≥5dB reduction"],
    ],
    outcomes_abbrev=[
        "THI: Tinnitus Handicap Inventory",
        "TFI: Tinnitus Functional Index",
        "VAS-L/D: Visual Analog Scale — Loudness/Distress",
        "PSQI: Pittsburgh Sleep Quality Index",
        "GAD-7: Generalized Anxiety Disorder 7",
        "HADS-A: Hospital Anxiety and Depression Scale — Anxiety",
        "PHQ-9: Patient Health Questionnaire-9",
        "TCS: Tinnitus Catastrophizing Scale",
        "MML: Minimum Masking Level",
        "SNHL: Sensorineural Hearing Loss",
    ],
)

# ---------------------------------------------------------------------------
# CONDITION: INSOMNIA
# ---------------------------------------------------------------------------
CONDITIONS["insomnia"] = dict(
    name="Chronic Insomnia Disorder",
    icd10="G47.00",
    doc_num="SPG-IN-001",
    tps_status="Investigational",
    tdcs_class="Class IIb",
    tps_class="Investigational",
    tavns_class="Class IIb",
    ces_class="Class IIa",
    inclusion=[
        "DSM-5 Insomnia Disorder: difficulty initiating/maintaining sleep ≥3 nights/week for ≥3 months",
        "ISI (Insomnia Severity Index) score ≥15 (moderate-severe) at baseline",
        "Adequate sleep opportunity (≥7 hours in bed) ruling out insufficient sleep syndrome",
        "Age 18–75; capable of informed consent",
        "Inadequate response to ≥1 CBT-I course or sleep hygiene optimization",
        "Stable medication regimen for ≥4 weeks (sleep medications, antidepressants)",
    ],
    exclusion=[
        "Untreated obstructive sleep apnea (AHI ≥15) as primary sleep disorder",
        "Metallic implants in head/neck or implanted neurostimulator",
        "Shift work sleep disorder as primary etiology",
        "Pregnancy",
        "Active substance use disorder (alcohol, hypnotics, stimulants)",
        "Active psychosis or bipolar disorder in manic phase",
        "Restless legs syndrome or periodic limb movement disorder as primary diagnosis",
    ],
    discussion=[
        "Chronic insomnia involves hyperarousal at cortical, cognitive, and autonomic levels — the 3P (predisposing-precipitating-perpetuating) model explains its persistence.",
        "Cortical hyperarousal: increased high-frequency (beta) EEG activity during sleep, particularly in frontal regions, reflects hyperactive salience processing inhibiting sleep onset.",
        "The thalamic reticular nucleus (TRN) normally gates sensory input to promote sleep; dysfunction leads to inappropriate sensory intrusion and sleep fragmentation.",
        "The DLPFC is implicated in rumination, worry, and cognitive hyperarousal that perpetuates insomnia through top-down thalamic excitation.",
        "CES (Alpha-Stim) is the primary NIBS modality for insomnia: direct thalamic and brainstem modulation promotes sleep-promoting delta/alpha oscillations.",
        "tDCS targeting DLPFC (cathodal) reduces cognitive hyperarousal and pre-sleep rumination.",
        "taVNS activates the parasympathetic nervous system, reduces autonomic hyperarousal (elevated sympathetic tone in insomnia), and promotes sleep via LC downregulation.",
        "TPS targeting frontal hyperarousal nodes (DLPFC, ACC) is investigational but mechanistically plausible.",
    ],
    overview=[
        "Chronic Insomnia Disorder affects approximately 10-15% of adults globally, representing the most prevalent sleep disorder. Characterized by persistent difficulty initiating or maintaining sleep, early morning awakening, and significant daytime impairment, insomnia involves bidirectional interactions with mood disorders, chronic pain, cardiovascular disease, and cognitive decline. The core neurobiological mechanism is hyperarousal — excessive activation of arousal systems (LC, hypothalamic arousal pathways) relative to sleep-promoting systems (VLPO, thalamic reticular nucleus).",
        "The SOZO NIBS protocol for insomnia is built around CES (Alpha-Stim) as the primary modality, supplemented by tDCS (DLPFC cathodal for cognitive hyperarousal), taVNS (autonomic arousal reduction), and TPS (investigational frontal hyperarousal targeting). All NIBS is integrated with CBT-I (Cognitive Behavioral Therapy for Insomnia) as the evidence-based psychotherapy backbone.",
        "Five clinical phenotypes guide protocol selection: sleep-onset insomnia (DLPFC/arousal system hyperactivation), sleep-maintenance insomnia (thalamic gating failure), comorbid insomnia-anxiety, comorbid insomnia-depression, and hyperarousal/cognitive dominant insomnia.",
    ],
    pathophysiology=[
        "Cortical hyperarousal: elevated frontal beta (16–32Hz) EEG power during NREM sleep reflects ongoing cognitive processing preventing consolidated sleep.",
        "Thalamic gating failure: thalamic reticular nucleus (TRN) inadequately filters sensory input; inappropriate sleep-to-wake transitions (micro-awakenings).",
        "Hypothalamic arousal system overdrive: lateral hypothalamus (orexin/hypocretin neurons) and locus coeruleus maintain excessive wakefulness drive.",
        "VLPO dysfunction: ventrolateral preoptic area sleep-promoting neurons are insufficient to flip the sleep-wake switch toward sleep.",
        "HPA axis dysregulation: elevated cortisol and CRF in insomnia perpetuate physiological arousal and disrupt sleep architecture.",
        "Autonomic hyperarousal: elevated sympathetic tone (low HRV, elevated heart rate) during sleep onset; taVNS and CES target this mechanism.",
    ],
    std_treatment=[
        "First-line: CBT-I (Cognitive Behavioral Therapy for Insomnia) — stimulus control, sleep restriction, relaxation, cognitive restructuring",
        "Pharmacological: Z-drugs (zolpidem, eszopiclone), doxepin, ramelteon, suvorexant/lemborexant, low-dose TCAs",
        "Sleep hygiene: consistent sleep schedule, light management, temperature, caffeine/alcohol restriction",
        "Relaxation techniques: progressive muscle relaxation, mindfulness, biofeedback",
        "Emerging: CBTI digital apps (digital therapeutics), low-dose lithium, chronotherapy",
    ],
    symptoms=[
        ["Sleep Onset Difficulty", "Takes >30min to fall asleep ≥3 nights/week", "100% (onset type)", "APA DSM-5 2013"],
        ["Sleep Maintenance Difficulty", "Waking during night with difficulty returning to sleep", "100% (maintenance type)", "APA DSM-5 2013"],
        ["Early Morning Awakening", "Waking ≥30min before intended rise time", "60%", "Morin 2006"],
        ["Non-Restorative Sleep", "Unrefreshing, poor quality sleep subjectively", "80%", "Buysse 2008"],
        ["Daytime Fatigue/Sleepiness", "Fatigue, tiredness despite adequate sleep opportunity", "90%", "Morin 2006"],
        ["Cognitive Impairment", "Concentration, memory, decision-making deficits", "75%", "Fortier-Brochu 2012"],
        ["Mood Disturbance", "Irritability, dysphoria, anxiety", "65%", "Riemann 2010"],
        ["Pre-sleep Cognitive Arousal", "Worry, rumination, racing thoughts at bedtime", "85%", "Harvey 2002"],
        ["Somatic Hyperarousal", "Muscle tension, elevated heart rate, body temperature at sleep onset", "70%", "Bonnet 2000"],
        ["Performance Anxiety (Conditioned Arousal)", "Anticipatory anxiety about sleep; bedroom conditioned stimulus", "75%", "Bootzin 1972"],
    ],
    brain_regions=[
        ["DLPFC", "Pre-sleep rumination, cognitive hyperarousal, worry generation", "tDCS cathodal, TPS", "Harvey 2002"],
        ["ACC", "Conflict monitoring during sleep onset; hyperarousal monitoring", "TPS cathodal", "Drummond 2004"],
        ["Thalamus (TRN)", "Sensory gating, sleep spindle generation; TRN dysfunction in insomnia", "CES primary", "Llinás 1999"],
        ["VLPO (Hypothalamus)", "Sleep-promoting nucleus; insufficient activation in insomnia", "CES indirect, taVNS", "Sherin 1996"],
        ["Locus Coeruleus", "Wakefulness promotion; excessive activation in insomnia", "taVNS, CES", "Aston-Jones 2005"],
        ["Default Mode Network", "Rumination, mind-wandering; DMN fails to deactivate at sleep onset", "tDCS DLPFC cathodal", "Nofzinger 2004"],
        ["Prefrontal Cortex (vmPFC)", "Emotional regulation, sleep anxiety inhibition", "TPS, tDCS", "Harvey 2002"],
        ["Hippocampus", "Fear memory of bed/sleep; conditioned arousal consolidation", "taVNS", "Bootzin 1972"],
    ],
    brainstem=[
        ["Locus Coeruleus (LC)", "Noradrenergic wakefulness driver; hyperactive in insomnia", "taVNS, CES", "Aston-Jones 2005"],
        ["Raphe Nuclei", "Serotonergic sleep-wake modulation; reduced in insomnia", "taVNS", "Pace-Schott 2002"],
        ["Parabrachial Nucleus", "Arousal relay; projects to BF and cortex", "taVNS indirect", "Fuller 2011"],
        ["Nucleus Tractus Solitarius", "Vagal integration; parasympathetic-sleep interface", "taVNS direct", "Porges 2007"],
        ["Tuberomammillary Nucleus", "Histaminergic wakefulness (H1 target of antihistamine hypnotics)", "None direct NIBS", "Saper 2005"],
    ],
    phenotypes=[
        ["Sleep-Onset Insomnia", "Difficulty falling asleep; presleep cognitive-somatic arousal; DLPFC hyperactivation", "Racing thoughts, muscle tension, conditioned arousal", "CES primary + tDCS DLPFC cathodal + taVNS"],
        ["Sleep-Maintenance Insomnia", "Multiple awakenings; thalamic gating failure; light sleep predominance", "Fragmented sleep, early morning waking", "CES primary + taVNS; tDCS if cognition impaired"],
        ["Comorbid Insomnia-Anxiety", "Insomnia driven by anxiety disorder; hyperarousal-anxiety interaction", "Pre-sleep worry, autonomic arousal, GAD features", "CES + taVNS + tDCS DLPFC cathodal; CBT-I + anxiety treatment"],
        ["Comorbid Insomnia-Depression", "Insomnia as prodrome/symptom of MDD; DLPFC-limbic dysfunction", "Early morning awakening, depressive rumination", "CES + tDCS DLPFC anodal (antidepressant) + taVNS"],
        ["Hyperarousal/Cognitive Dominant", "High cognitive pre-sleep arousal (PSAS-C ≥18); minimal somatic", "Intense rumination, racing thoughts, hypervigilance for sleep", "tDCS DLPFC cathodal + TPS + CES + CBT-I cognitive focus"],
    ],
    symptom_map=[
        ["Sleep onset difficulty", "DLPFC/Conditioned arousal", "tDCS DLPFC cathodal + CES", "Harvey 2002, Lande 2018"],
        ["Sleep maintenance", "Thalamus/TRN", "CES primary", "Llinas 1999"],
        ["Pre-sleep rumination", "DLPFC/DMN", "tDCS DLPFC cathodal + TPS", "Harvey 2002"],
        ["Autonomic hyperarousal", "LC/Sympathetic", "taVNS + CES", "Bonnet 2000"],
        ["Early morning awakening", "Thalamus/HPA", "CES + taVNS", "Morin 2006"],
        ["Anxiety comorbidity", "Amygdala/DLPFC", "taVNS + CES + tDCS DLPFC cathodal", "Riemann 2010"],
        ["Depression comorbidity", "DLPFC/Limbic", "tDCS DLPFC anodal + taVNS", "Brunoni 2013"],
        ["Conditioned arousal", "Hippocampus/Amygdala", "CBT-I stimulus control + taVNS", "Bootzin 1972"],
        ["Cognitive impairment (daytime)", "DLPFC/CEN", "tDCS DLPFC anodal (daytime)", "Fortier-Brochu 2012"],
    ],
    montage=[
        ["Sleep-Onset Insomnia", "Cathodal DLPFC (F3, 1.5mA, 20min — daytime)", "DLPFC (200 pulses)", "CES primary nightly 60min; taVNS before bed"],
        ["Sleep-Maintenance Insomnia", "Cathodal DLPFC (F3, 1.5mA, 20min — daytime)", "None initial", "CES primary nightly 60min; taVNS before bed"],
        ["Comorbid Insomnia-Anxiety", "Cathodal DLPFC (F3, 1.5mA, 20min) — daytime", "None initial", "CES primary nightly + daytime taVNS; anxiety treatment concurrent"],
        ["Comorbid Insomnia-Depression", "Anodal DLPFC (F3, 2mA, 20min) — daytime", "None initial", "CES nightly; taVNS 2x daily; antidepressant maintained"],
        ["Hyperarousal/Cognitive", "Cathodal DLPFC (F3, 1.5mA, 20min) + TPS daytime", "DLPFC/ACC (200 pulses)", "CES nightly; CBT-I cognitive component essential"],
        ["Maintenance Phase", "Cathodal DLPFC (F3, 1mA, 15min — daytime)", "None", "CES 3–5x/week; taVNS as needed home"],
        ["Elderly Adjusted", "Cathodal DLPFC (F3, 1mA, 15min)", "None", "CES primary nightly; taVNS standard; reduce zolpidem"],
        ["Refractory Insomnia", "Cathodal DLPFC (F3, 1.5mA) + TPS (300 pulses)", "DLPFC + ACC (300 pulses)", "All modalities + intensive CBT-I"],
        ["Comorbid Sleep Apnea (treated)", "Cathodal DLPFC (F3, 1.5mA, 20min)", "None", "CES nightly; CPAP confirmed adherent"],
        ["Sham Protocol", "F3 cathodal (30s ramp, 0mA, 20min)", "None", "Sham control condition"],
    ],
    tdcs_protocols=[
        ["IN-tDCS-01", "DLPFC Cathodal (Cognitive Hyperarousal Reduction)", "F4", "F3 cathodal", "1.5mA, 20min, 10 sessions (daytime)", "Frase 2016"],
        ["IN-tDCS-02", "DLPFC Anodal (Comorbid Depression)", "F3 anodal", "F4", "2mA, 20min, 10 sessions", "Brunoni 2013"],
        ["IN-tDCS-03", "Bifrontal (Hyperarousal with Anxiety)", "F3 anodal (antidepressant); F4 cathodal", "F4 anodal; F3 cathodal", "1.5mA, 20min, 10 sessions", "Frase 2016"],
        ["IN-tDCS-04", "Vertex/SMA Cathodal (Somatic Hyperarousal)", "Fpz", "Cz cathodal", "1.5mA, 20min, 10 sessions", "Expert consensus 2023"],
        ["IN-tDCS-05", "Maintenance", "F4 (cathodal F3)", "F3", "1mA, 15min, 2x/week", "Bikson 2016"],
        ["IN-tDCS-06", "Combined DLPFC Cathodal + CES", "F3 cathodal", "F4", "1.5mA, 20min + CES concurrent or sequential", "Expert consensus 2024"],
        ["IN-tDCS-07", "Elderly Adjusted", "F3 cathodal", "F4", "1mA, 15min, 10 sessions", "Lefaucheur 2016"],
        ["IN-tDCS-08", "Sham", "F3", "F4", "30s ramp, 0mA, 20min", "Frase 2016"],
    ],
    plato_protocols=[
        ["IN-PLATO-01", "DLPFC Cathodal", "F3/F4", "Left DLPFC", "F3", "1.5mA", "N/A", "Cathodal 20min daytime"],
        ["IN-PLATO-02", "DLPFC Anodal (Depression)", "F3/F4", "Left DLPFC anodal", "F3", "2.0mA", "N/A", "Anodal 20min"],
        ["IN-PLATO-03", "Vertex Cathodal", "Cz/Fpz", "Vertex/SMA", "Cz", "1.5mA", "N/A", "Cathodal 20min"],
        ["IN-PLATO-04", "HD-tDCS DLPFC Cathodal", "F3 center", "4-electrode ring", "F3", "0.75mA", "N/A", "HD cathodal 20min"],
        ["IN-PLATO-05", "Maintenance", "F3", "DLPFC", "F3", "1.0mA", "N/A", "2x/week 15min"],
        ["IN-PLATO-06", "Delta tACS Sleep-Promoting", "Cz", "Vertex", "Cz", "1.0mA", "1Hz", "Delta tACS 20min — investigational"],
        ["IN-PLATO-07", "Elderly", "F3", "DLPFC cathodal", "F3", "1.0mA", "N/A", "15min"],
        ["IN-PLATO-08", "Sham", "F3", "DLPFC", "F3", "0mA", "N/A", "30s ramp"],
    ],
    tps_protocols=[
        ["IN-TPS-01", "DLPFC Hyperarousal Reduction", "DLPFC (BA46)", "200 pulses, 0.2Hz, 0.15mJ/mm²", "2 sessions/week (daytime)", "Frase 2016"],
        ["IN-TPS-02", "ACC Arousal Monitoring", "ACC (BA24/32)", "150 pulses, 0.15Hz", "2 sessions/week", "Drummond 2004"],
        ["IN-TPS-03", "vmPFC Sleep Anxiety", "vmPFC (BA10/11)", "150 pulses, 0.15Hz", "2 sessions/week", "Harvey 2002"],
        ["IN-TPS-04", "Full Frontal Hyperarousal Protocol", "DLPFC + ACC sequential", "300 pulses total", "3 sessions/week x3 weeks", "Expert consensus 2024"],
        ["IN-TPS-05", "Hyperarousal/Cognitive Dominant", "DLPFC + vmPFC", "250 pulses total", "3 sessions/week", "Expert consensus 2024"],
    ],
    ces_role=[
        ["Primary Insomnia Modality", "First-line NIBS for insomnia; direct thalamic and brainstem sleep-promoting modulation; safest overall", "Nightly 60min; begin 30–60min before bed"],
        ["Sleep Onset Insomnia", "Reduces pre-sleep arousal; promotes alpha shift and sleep onset", "Nightly 60min; pre-bed application"],
        ["Sleep Maintenance Insomnia", "Improves sleep architecture, spindle density, and reduces awakenings", "Nightly 60min continuous application"],
        ["Maintenance Phase", "Long-term independent sleep management; patient self-administered", "3–5x/week indefinitely; home device program"],
    ],
    tavns_role="taVNS (tragus, 25Hz, 200µs, 0.5mA, 30min) is applied pre-sleep (30–60min before bedtime) to downregulate locus coeruleus noradrenergic hyperarousal and increase parasympathetic tone (HRV). The autonomic normalization effect promotes the physiological shift from sympathetic to parasympathetic dominance required for sleep onset. Home device (Nemos/TENS tragus) used nightly. In comorbid insomnia-anxiety, taVNS provides additional anxiolytic benefit. PEM monitoring is not required in insomnia (Vonck 2014, Lehtimäki 2013).",
    combinations=[
        ("Sleep-Onset Insomnia", [
            ["CES + tDCS DLPFC cathodal + taVNS", "Thalamic sleep-promoting + cognitive hyperarousal reduction + autonomic", "taVNS 30min pre-bed; CES nightly; tDCS daytime", "Racing thoughts, conditioned arousal at sleep onset"],
            ["CES + taVNS", "Core combination; thalamic + autonomic; minimal exertion", "taVNS 30min before CES nightly", "Onset insomnia without cognitive component"],
        ]),
        ("Sleep-Maintenance Insomnia", [
            ["CES + taVNS", "Thalamic gating + autonomic; minimal additional intervention", "CES nightly; taVNS pre-bed", "Fragmented sleep, multiple awakenings"],
            ["CES + tDCS DLPFC cathodal", "Thalamic + cognitive hyperarousal if cognition implicated", "tDCS daytime; CES nightly", "Maintenance insomnia with daytime rumination"],
        ]),
        ("Comorbid Insomnia-Anxiety", [
            ["CES + taVNS + tDCS DLPFC cathodal", "Thalamic + autonomic + prefrontal arousal reduction", "taVNS pre-bed; CES nightly; tDCS daytime", "High pre-sleep anxiety, autonomic arousal"],
        ]),
        ("Comorbid Insomnia-Depression", [
            ["CES + tDCS DLPFC anodal (daytime) + taVNS", "Sleep-promoting + antidepressant + autonomic", "tDCS daytime anodal; CES nightly; taVNS pre-bed", "MDD + insomnia; early morning awakening"],
        ]),
        ("Hyperarousal/Cognitive Dominant", [
            ["tDCS DLPFC cathodal + TPS DLPFC/ACC + CES + CBT-I", "Prefrontal inhibition + frontal TPS + sleep-promoting + psychological", "TPS → tDCS (daytime); CES nightly; CBT-I concurrent", "Intense rumination, hypervigilance for sleep"],
        ]),
        ("Refractory Insomnia", [
            ["tDCS DLPFC cathodal + TPS DLPFC/ACC + taVNS + CES", "Full circuit: frontal hyperarousal + autonomic + thalamic", "TPS → tDCS daytime; taVNS pre-bed; CES nightly", "Failed CBT-I + medication; ISI ≥22"],
        ]),
    ],
    combination_summary=[
        ["Sleep-Onset", "CES + tDCS DLPFC cathodal + taVNS", "Thalamic + prefrontal + autonomic", "taVNS pre-bed; CES nightly; tDCS daytime", "Onset insomnia", "IIa/IIb"],
        ["Sleep-Maintenance", "CES + taVNS", "Thalamic gating + autonomic", "taVNS pre-bed + CES nightly", "Maintenance insomnia", "IIa/IIb"],
        ["Insomnia-Anxiety", "CES + taVNS + tDCS DLPFC cathodal", "Sleep + autonomic + arousal", "taVNS pre-bed; CES nightly; tDCS day", "Insomnia + anxiety", "IIb"],
        ["Insomnia-Depression", "CES + tDCS DLPFC anodal + taVNS", "Sleep + antidepressant + autonomic", "tDCS day anodal; CES + taVNS night", "Insomnia + MDD", "IIb"],
        ["Hyperarousal-Cognitive", "tDCS DLPFC cathodal + TPS + CES + CBT-I", "Prefrontal + frontal TPS + sleep + psych", "TPS → tDCS day; CES + taVNS night", "Racing thoughts dominant", "IIb"],
        ["Refractory", "All four modalities + CBT-I", "Full frontal + autonomic + thalamic", "TPS → tDCS day; taVNS + CES night", "Failed CBT-I + medication", "IIb"],
    ],
    outcomes=[
        ["Insomnia Severity Index (ISI)", "Insomnia severity", "Baseline, 4wk, 8wk", "≥8-point reduction (MCID); ISI <8 = remission"],
        ["Actigraphy — Sleep Onset Latency (SOL)", "Objective sleep onset", "Baseline week, 4wk week, 8wk week", "SOL <30min average"],
        ["Actigraphy — Wake After Sleep Onset (WASO)", "Objective sleep maintenance", "Baseline, 4wk, 8wk", "WASO <30min average"],
        ["Actigraphy — Total Sleep Time (TST)", "Objective sleep duration", "Baseline, 4wk, 8wk", "TST ≥6.5 hours average"],
        ["Pittsburgh Sleep Quality Index (PSQI)", "Subjective sleep quality", "Baseline, 4wk, 8wk", "PSQI ≤5 (good sleeper threshold)"],
        ["Pre-Sleep Arousal Scale (PSAS)", "Cognitive and somatic pre-sleep arousal", "Baseline, 4wk, 8wk", "≥5-point reduction in cognitive subscale"],
        ["PHQ-9", "Depression comorbidity", "Baseline, 4wk, 8wk", "≥5-point reduction"],
        ["GAD-7", "Anxiety comorbidity", "Baseline, 4wk, 8wk", "≥5-point reduction"],
        ["Daytime Functioning (PROMIS Sleep-Related Impairment)", "Daytime impact", "Baseline, 4wk, 8wk", "≥5-point T-score improvement"],
    ],
    outcomes_abbrev=[
        "ISI: Insomnia Severity Index",
        "SOL: Sleep Onset Latency",
        "WASO: Wake After Sleep Onset",
        "TST: Total Sleep Time",
        "PSQI: Pittsburgh Sleep Quality Index",
        "PSAS: Pre-Sleep Arousal Scale",
        "PHQ-9: Patient Health Questionnaire-9",
        "GAD-7: Generalized Anxiety Disorder 7",
        "PROMIS: Patient-Reported Outcomes Measurement Information System",
        "TRN: Thalamic Reticular Nucleus",
        "VLPO: Ventrolateral Preoptic Area",
        "CBT-I: Cognitive Behavioral Therapy for Insomnia",
    ],
)

# ---------------------------------------------------------------------------
# RUNNER
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from pathlib import Path
    OUTPUT_ROOT = Path("outputs/documents")
    for slug, cond in CONDITIONS.items():
        out = OUTPUT_ROOT / slug / "fellow" / "Evidence_Based_Protocol_Fellow.docx"
        print(f"Building: {slug}")
        build_document(cond, out)
    print("\\nAll 15 documents generated.")
print("Tinnitus + Insomnia + Runner appended OK")
'''

with open(OUTFILE, "a", encoding="utf-8") as f:
    f.write(BLOCK)

print("Tinnitus + Insomnia + Runner appended OK")
