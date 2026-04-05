# DEPRECATED: This script is superseded by the canonical generation pipeline.
# Use instead: GenerationService.generate(condition="...", tier="...", doc_type="...")
# Or CLI: PYTHONPATH=src python -m sozo_generator.cli.main build condition --condition <slug> --tier <tier> --doc-type <type>
# See docs/MIGRATION_PLAN.md for details.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Appends Depression, Anxiety, ADHD conditions"""
from pathlib import Path

BLOCK = r'''
# ══════════════════════════════════════
# 2. MAJOR DEPRESSIVE DISORDER
# ══════════════════════════════════════
CONDITIONS["depression"] = dict(
    name="Major Depressive Disorder", icd10="F32/F33",
    doc_num="SOZO-MDD-FEL-002",
    tps_status="INVESTIGATIONAL / OFF-LABEL",
    tdcs_class="Level A evidence (multiple RCTs); CE-marked",
    tps_class="INVESTIGATIONAL / OFF-LABEL",
    tavns_class="Emerging adjunctive; CE-marked",
    ces_class="FDA-cleared adjunctive for mood/anxiety/sleep",
    inclusion=[
        "Confirmed diagnosis of MDD (DSM-5 or ICD-11 criteria) by qualified clinician",
        "PHQ-9 score \u226510 at baseline (moderate-to-severe)",
        "Age 18+ years",
        "Stable or no psychotropic medication (no change in 4 weeks prior to enrolment)",
        "Written informed consent (including TPS off-label disclosure)",
        "Baseline assessments completed (PHQ-9, HDRS-17, MoCA, GAD-7)",
    ],
    exclusion=[
        "Intracranial metallic hardware in stimulation path",
        "Cochlear implant or DBS device",
        "Active psychotic features or bipolar I disorder (manic episode)",
        "Active suicidal ideation with plan or intent (requires immediate psychiatric referral)",
        "Skull defects, craniectomy, or recent craniotomy",
        "Pregnancy (tDCS, TPS)",
        "Inability to provide informed consent",
    ],
    discussion=[
        "Cardiac pacemaker or defibrillator \u2014 individual risk\u2013benefit assessment",
        "Epilepsy or seizure history \u2014 formal risk\u2013benefit with documented rationale",
        "Bipolar II disorder or cyclothymia \u2014 requires mood stabiliser coverage and close monitoring",
        "Active substance use disorder",
        "Benzodiazepine use \u2014 may reduce cortical excitability and blunt tDCS response",
        "Coagulation disorders or anticoagulants (especially TPS)",
        "Dermatological conditions at electrode sites",
        "Severe personality disorder complicating treatment engagement",
    ],
    overview=[
        "Major Depressive Disorder (MDD) is a highly prevalent, recurrent psychiatric disorder characterised "
        "by persistent low mood, anhedonia, and a range of cognitive, somatic, and neurovegetative symptoms. "
        "MDD affects approximately 264 million people globally, with lifetime prevalence of 15\u201320% in "
        "high-income countries. It is a leading cause of disability worldwide (WHO, 2021).",
        "Approximately 30\u201340% of MDD patients fail to respond to two or more adequate antidepressant "
        "trials, meeting criteria for Treatment-Resistant Depression (TRD). tDCS targeting the left DLPFC "
        "represents one of the best-evidenced non-invasive neuromodulation approaches in psychiatry, "
        "supported by multiple sham-controlled RCTs and meta-analyses (Brunoni et al., 2013, 2016).",
        "The network model of MDD identifies three core disruptions: (1) Default Mode Network (DMN) "
        "hyperactivation driving rumination; (2) Central Executive Network (CEN) hypoactivation impairing "
        "cognitive control; (3) Salience Network (SN) dysregulation disrupting network switching. Prefrontal "
        "tDCS is proposed to restore CEN excitability and reduce SN-DMN coupling.",
        "NIBS Evidence in MDD: tDCS is the most evidence-based non-invasive neuromodulation for MDD after "
        "TMS. Multiple RCTs and meta-analyses demonstrate clinically meaningful antidepressant effects "
        "with left DLPFC anodal tDCS (Brunoni et al., 2016; Lefaucheur et al., 2017). TPS is investigational "
        "in MDD with emerging pilot data. CES is FDA-cleared as adjunctive for mood and anxiety.",
    ],
    pathophysiology=[
        "MDD involves dysfunction across multiple neurobiological systems. Left DLPFC hypoactivation and "
        "subgenual ACC (sgACC/Cg25) hyperactivation are consistently demonstrated in neuroimaging studies. "
        "The sgACC hyperactivity propagates depressogenic tone throughout the DMN. Monoaminergic deficits "
        "(serotonin, noradrenaline, dopamine) underpin the pharmacological treatment rationale.",
        "Neuroplasticity impairment is key: reduced BDNF signalling, hippocampal volume loss in recurrent MDD, "
        "and impaired synaptic plasticity in prefrontal circuits. HPA axis hyperactivity drives "
        "glucocorticoid-mediated prefrontal and hippocampal damage. Neuroinflammatory markers (IL-6, TNF-alpha, "
        "CRP) are elevated in a significant subset of MDD patients.",
    ],
    std_treatment=[
        "First-line pharmacotherapy includes SSRIs and SNRIs. Tricyclic antidepressants and MAOIs are "
        "second-line due to side-effect profiles. Lithium and atypical antipsychotics are used for augmentation "
        "in TRD. Psychotherapy (CBT, behavioural activation) has comparable evidence to pharmacotherapy for "
        "mild-to-moderate MDD and is recommended in combination with NIBS. ECT remains the gold standard for "
        "severe, treatment-resistant MDD. rTMS (left DLPFC) is FDA-cleared and NICE-recommended for TRD.",
    ],
    symptoms=[
        ["Depressed Mood",           "Persistent low mood most of the day, nearly every day",                          "Core criterion",    "DSM-5; ICD-11"],
        ["Anhedonia",                "Markedly diminished interest or pleasure in all/almost all activities",           "Core criterion",    "DSM-5; ICD-11"],
        ["Weight / Appetite Change", "Significant weight loss/gain; decreased/increased appetite",                     "60\u201380%",       "DSM-5"],
        ["Sleep Disturbance",        "Insomnia (early morning awakening) or hypersomnia",                              "70\u201390%",       "DSM-5; Riemann 2020"],
        ["Psychomotor Changes",      "Psychomotor agitation or retardation observable by others",                      "40\u201360%",       "DSM-5"],
        ["Fatigue / Anergia",        "Fatigue or loss of energy nearly every day",                                     "70\u201390%",       "DSM-5"],
        ["Worthlessness / Guilt",    "Feelings of worthlessness or excessive/inappropriate guilt",                     "60\u201380%",       "DSM-5"],
        ["Cognitive Impairment",     "Diminished ability to think, concentrate, or make decisions",                    "50\u201380%",       "Rock et al. 2014"],
        ["Suicidal Ideation",        "Recurrent thoughts of death; suicidal ideation or attempt",                      "Variable",          "DSM-5"],
        ["Somatic Symptoms",         "Headache, GI symptoms, pain without clear medical cause",                        "50\u201375%",       "Simon et al. 1999"],
        ["Anxiety Comorbidity",      "Comorbid anxiety symptoms present in majority of MDD patients",                  "50\u201370%",       "Kessler et al. 2003"],
    ],
    brain_regions=[
        ["Left DLPFC (F3/F4)",          "Hypoactivation in MDD; impaired cognitive control and emotion regulation",      "Anodal tDCS primary target; restores CEN excitability (Level A evidence)",     "Brunoni 2016; Lefaucheur 2017"],
        ["Subgenual ACC (sgACC/Cg25)",   "Hyperactivation; propagates depressogenic tone via DMN; key DBS target",       "TPS investigational deep target; indirectly modulated by prefrontal tDCS",     "Mayberg 2005"],
        ["Anterior Cingulate Cortex",    "Conflict monitoring, pain, emotional processing; disrupted in MDD",             "Cathodal tDCS of right PFC / anodal left; TPS (investigational)",             "Drevets 2001"],
        ["Amygdala",                     "Hyperactivation to negative stimuli; impaired fear extinction",                  "Modulated indirectly via prefrontal and taVNS limbic pathways",               "Sheline 2001"],
        ["Hippocampus",                  "Volume loss in recurrent MDD; impaired neurogenesis; memory consolidation",     "Indirect target via TPS (deep investigational) and BDNF upregulation by tDCS", "MacQueen 2003"],
        ["Medial Prefrontal Cortex",     "DMN hub; excessive self-referential processing and rumination",                  "Prefrontal tDCS modulates DMN-CEN balance",                                   "Sheline 2009"],
        ["Insula",                       "Interoceptive processing, somatic symptoms; hyperactivation in MDD",             "Indirectly modulated; taVNS acts on insula-brainstem-limbic circuits",        "Mayberg 2005"],
        ["Basal Ganglia (Striatum)",     "Anhedonia circuitry; reduced reward activation in MDD",                         "TPS deep investigational target; prefrontal tDCS modulates fronto-striatal circuits", "Pizzagalli 2009"],
    ],
    brainstem=[
        ["Locus Coeruleus (LC)",        "Noradrenergic dysregulation; arousal impairment; antidepressant target",       "taVNS modulates LC via NTS; key mechanism for mood stabilisation",             "Nieuwenhuis 2005"],
        ["Dorsal Raphe Nucleus (DRN)",  "Serotonergic dysregulation; primary antidepressant pharmacological target",    "Indirectly modulated by prefrontal tDCS and taVNS pathways",                   "Deakin 1991"],
        ["Nucleus Tractus Solitarius",  "Vagal afferent relay; central autonomic regulation hub",                       "Primary afferent target of taVNS; influences limbic and prefrontal regions",  "Frangos 2015"],
        ["Habenula",                    "Anti-reward signal; hyperactivation in MDD contributes to anhedonia",           "Indirect target via prefrontal modulation and taVNS pathways",                 "Lecca 2014"],
        ["VTA (Ventral Tegmental Area)","Dopaminergic reward processing; hypoactivation in anhedonic MDD",              "Indirectly targeted via mesolimbic pathway modulation (tDCS, taVNS)",          "Nestler 2006"],
    ],
    phenotypes=[
        ["Melancholic MDD",             "Severe anhedonia, psychomotor changes, early morning wakening, diurnal variation","Anhedonia, early waking, psychomotor retardation/agitation","Left DLPFC anodal tDCS; TPS DLPFC + sgACC; taVNS"],
        ["Anxious MDD",                 "Prominent anxiety, tension, worry alongside depressive core symptoms",           "Low mood, anxiety, worry, insomnia, somatic tension",           "Bilateral DLPFC tDCS; taVNS primary; CES"],
        ["Cognitive MDD",               "Cognitive symptoms dominant: concentration, memory, executive dysfunction",      "Concentration loss, memory impairment, indecisiveness",         "Left DLPFC anodal tDCS; TPS DLPFC; cognitive training"],
        ["Atypical MDD",                "Mood reactivity; hypersomnia; hyperphagia; rejection sensitivity; leaden paralysis","Variable mood, hypersomnia, overeating, heavy limbs",       "L-DLPFC tDCS; taVNS; CES; consider right parietal cathodal"],
        ["TRD (Treatment-Resistant)",   "Failed \u22652 adequate antidepressant trials",                                 "Full MDD syndromal features with pharmacological non-response",  "Bilateral DLPFC tDCS at 2 mA; TPS DLPFC + ACC; taVNS; CES"],
        ["MDD with Somatic Features",   "Prominent somatic complaints: fatigue, pain, headache, GI symptoms",            "Fatigue, pain, concentration, mood",                            "L-DLPFC tDCS + M1 (for pain); taVNS; CES"],
        ["MDD with Psychotic Features", "Mood-congruent psychotic features; hallucinations or delusions",                "Depressed mood + psychotic symptoms",                           "Doctor assessment required; tDCS only after antipsychotic cover"],
    ],
    symptom_map=[
        ["Depressed Mood",             "Left DLPFC, sgACC, DMN",       "Left DLPFC anodal tDCS (F3) + TPS (DLPFC/sgACC investigational) + taVNS",         "Level A (Brunoni 2016)"],
        ["Anhedonia",                  "Striatum, OFC, DLPFC",          "Left DLPFC tDCS + TPS (OFC/striatum investigational) + taVNS",                    "Moderate (Brunoni 2013)"],
        ["Cognitive Impairment",       "Left DLPFC, Parietal, Hippocampus","Left DLPFC anodal tDCS + TPS (DLPFC targeted)",                               "Moderate (Brunoni 2013)"],
        ["Anxiety / Tension",          "Right DLPFC, Amygdala, SN",    "Right DLPFC cathodal / bilateral DLPFC + taVNS primary + CES",                    "Moderate (Loo 2012)"],
        ["Sleep Disturbance",          "Frontal slow-wave, Thalamus",   "CES primary; taVNS adjunctive; tDCS (frontal slow-wave protocols)",               "Moderate (Philip 2017)"],
        ["Fatigue / Anergia",          "Left DLPFC, Mesolimbic",        "Left DLPFC tDCS + CES; taVNS for arousal modulation",                            "Moderate (Brunoni 2016)"],
        ["Psychomotor Retardation",    "Left DLPFC, SMA, Striatum",     "Left DLPFC + SMA anodal tDCS; TPS frontal targeted; behavioural activation",      "Limited (Loo 2012)"],
        ["Suicidality Monitoring",     "Prefrontal-limbic circuits",    "Protocol continues with enhanced monitoring; escalate to Doctor if PHQ-9 item 9 \u22651","Monitoring priority"],
        ["Somatic Pain Overlay",       "M1, ACC, Thalamus",             "Left DLPFC tDCS + M1 cathodal (contralateral to pain); taVNS; CES",              "Limited (Fregni 2006)"],
    ],
    montage=[
        ["Melancholic MDD",            "F3 anode + F4 cathode (standard L-DLPFC protocol); 2 mA, 20\u201330 min", "Cranial (global + targeted DLPFC/sgACC)",    "taVNS, CES (sleep)"],
        ["Anxious MDD",                "F3 anode + F4 anode (bilateral); or F3 anode + F4 cathode",               "Cranial (global + targeted DLPFC/ACC)",       "taVNS primary, CES"],
        ["Cognitive MDD",              "F3 anode + Fp2 cathode; T3/T4 options for temporal memory targets",       "Cranial (global + targeted DLPFC)",          "taVNS, CES supportive"],
        ["Atypical MDD",               "F3 anode + Fp2 cathode; consider P3 anode for parietal involvement",     "Cranial (global + targeted)",                "taVNS, CES; sleep focus"],
        ["TRD",                        "Bilateral DLPFC (F3 + F4 anode); or high-density HD-tDCS if available",  "Cranial (global + targeted DLPFC/ACC) \u00d7 intensive block","taVNS + CES; consider adjunct CBT"],
        ["MDD + Somatic Pain",         "F3 anode + C3/C4 cathode (contralateral to pain) / extracephalic",       "Cranial (global + targeted) + peripheral (pain dermatomes)","taVNS, CES supportive"],
        ["MDD + Psychotic Features",   "Defer tDCS until antipsychotic stabilisation achieved",                  "Defer TPS until psychosis in remission",      "CES; taVNS adjunctive only"],
        ["No response after 8\u201310 sessions","Reassess diagnosis; consider bilateral protocol or TPS",       "Add TPS DLPFC; consider sgACC targeting",    "Review full adjunct regimen"],
    ],
    tdcs_protocols=[
        ["C1","Depressed mood (primary)",      "F3 (L-DLPFC)","Fp2 / F4 / extracephalic",        "2 mA, 20\u201330 min, 5\u00d7/wk \u00d7 6\u201310 wks","Level A; RCT meta-analysis (Brunoni 2016)"],
        ["C2","Anxious depression",            "F3 + F4 bilateral anode","Extracephalic shoulder/arm","2 mA, 20\u201330 min, 5\u00d7/wk",               "Moderate (Loo 2012)"],
        ["C3","Cognitive symptoms / TRD",      "F3 anode + Fz","Fp2, extracephalic",              "2 mA, 20\u201330 min, 5\u00d7/wk",                   "Moderate (Brunoni 2013)"],
        ["C4","Anhedonia / reward",            "F3 anode + Oz","F4, extracephalic",               "2 mA, 20\u201330 min, 5\u00d7/wk",                   "Emerging (Lefaucheur 2017)"],
        ["C5","TRD \u2014 intensive bilateral", "F3 + F4 bilateral","Fp2 + Fp1, extracephalic",   "2 mA, 20\u201330 min, 2\u00d7/day \u00d7 5 days then 5\u00d7/wk","SELECT-TDCS (Brunoni 2013)"],
        ["C6","Sleep disturbance",             "Fz anode (frontal slow-wave)","Pz / extracephalic","1\u20132 mA, 20 min, evening",                       "Moderate (Brunoni 2016; Philip 2017)"],
        ["C7","Somatic fatigue / anergia",     "F3 anode + Cz","Fp2, extracephalic",              "2 mA, 20\u201330 min, 5\u00d7/wk",                   "Moderate (Brunoni 2016)"],
        ["C8","MDD + pain overlay",            "F3 anode + C3/C4 (contra to pain)","F4, extracephalic","2 mA, 20\u201330 min, 5\u00d7/wk",              "Limited; analgesic tDCS evidence (Fregni 2006)"],
    ],
    plato_protocols=[
        ["C1-PS","Depressed mood",             "Frontal (F3 area)","F3","Right shoulder",   "1.6 mA, 20\u201330 min","Daily or 5\u00d7/wk","L-DLPFC anodal; primary MDD protocol"],
        ["C2-PS","Anxious depression",         "Frontal (F3 area)","F3","Right shoulder",   "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Adjunct taVNS for anxiety component"],
        ["C3-PS","Cognitive / TRD",            "Frontal (F3 area)","F3","Shoulder",         "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Pair with cognitive activation tasks"],
        ["C4-PS","Anhedonia / reward",         "Frontal (F3 area)","F3","Shoulder",         "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Combine with behavioural activation"],
        ["C5-PS","TRD maintenance",            "Frontal (F3 area)","F3","Right shoulder",   "1.6 mA, 20\u201330 min","5\u00d7/wk",         "After in-clinic HDCkit induction phase"],
        ["C6-PS","Sleep disturbance",          "Frontal (Fz area)","Fz","Shoulder",         "1.6 mA, 20 min",        "Evening only",       "Combine with CES evening session"],
        ["C7-PS","Fatigue / anergia",          "Frontal (F3 area)","F3","Shoulder",         "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Morning use preferred for energy"],
        ["C8-PS","MDD + pain",                 "Motor (Cz area)",  "Cz","Shoulder/arm",     "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Motor cortex for pain modulation"],
    ],
    tps_protocols=[
        ["T1","Depressed mood (primary)",        "DLPFC bilateral, mPFC, OFC",   "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz; 10 sessions/2 wks","4,000 Tgt (DLPFC) + 2,000 PRE; total 6\u20138K","Preliminary (Leyman 2024)"],
        ["T2","TRD / sgACC modulation",          "DLPFC + sgACC (Cg25) region",  "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",               "4,000 Tgt + 2,000 Std; total 6\u20138K",          "Investigational (pilot data only)"],
        ["T3","Anhedonia / reward",              "OFC, striatum, ACC",            "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",               "4,000 Tgt (OFC) + 2,000 Std; total 6\u20138K",   "Investigational"],
        ["T4","Cognitive MDD / memory",          "DLPFC + Hippocampal region",   "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",               "4,000 Tgt (DLPFC) + 2,000 PRE; total 6\u20138K", "Investigational"],
        ["T5","Anxious depression",              "DLPFC + anterior insula",      "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",               "4,000 Tgt + 2,000 Std; total 6\u20138K",          "Investigational"],
    ],
    ces_role=[
        ["Mood stabilisation",    "Supportive antidepressant adjunct; augments tDCS mood benefit",                "Daily or 5\u00d7/wk; 20\u201340 min session; morning or evening"],
        ["Anxiety reduction",     "Reduces comorbid anxiety and somatic tension; reduces CEN-SN hyperarousal",    "Before tDCS session or evening; 20\u201340 min"],
        ["Sleep disturbance",     "Enhances sleep onset, duration, and quality; key target in MDD",               "Evening before bed; 20\u201340 min; coordinate with tDCS timing"],
        ["Fatigue / anergia",     "May improve subjective energy and motivation as adjunct to prefrontal tDCS",   "Morning; 20\u201330 min; avoid late afternoon if activating"],
    ],
    tavns_role="taVNS serves as a limbic and autonomic modulator in MDD, enhancing noradrenergic and serotonergic tone via locus coeruleus and dorsal raphe, reducing amygdala hyperactivity, and augmenting antidepressant tDCS effects.",
    combinations=[
        ("1) Melancholic MDD", [
            ["tDCS + Behavioural Activation","L-DLPFC anodal tDCS + structured behavioural activation; most supported combination in MDD neuromodulation (Brunoni 2016; Loo 2018)","tDCS before activation tasks","Severe anhedonia, psychomotor retardation"],
            ["taVNS + tDCS","taVNS priming before tDCS enhances cortical receptivity; plausible combination (Redgrave 2018; Hein 2021)","taVNS 20\u201330 min before tDCS session","Melancholic features with autonomic dysregulation"],
            ["CES + Standard Care","Evening CES for sleep; morning CES for energy; adjunct to tDCS treatment block (Philip 2017)","Evening and/or morning as prescribed","Sleep disturbance, early waking, anergia"],
        ]),
        ("2) Anxious MDD", [
            ["tDCS + CBT / Mindfulness","Bilateral DLPFC tDCS + CBT or mindfulness; addresses both emotional and cognitive regulation (Brunoni 2016)","tDCS before therapy session","Anxious rumination, tension, hyperarousal"],
            ["taVNS + tDCS","taVNS provides autonomic downshift before cortical stimulation; reduces treatment-session anxiety (Hein 2021; Redgrave 2018)","taVNS 20 min before tDCS","Anxiety, somatic tension, autonomic hyperarousal"],
            ["CES + Standard Care","CES reduces anxiety and improves sleep in anxious MDD; FDA-cleared indication (Philip 2017)","Evening \u00d7 7 nights/wk or as needed","Anxiety, sleep onset difficulties, somatic tension"],
        ]),
        ("3) Cognitive MDD", [
            ["tDCS + Cognitive Training","L-DLPFC anodal tDCS + computerised cognitive training; targets executive and memory deficits (Brunoni 2016; Segrave 2014)","tDCS immediately before or during cognitive training","Concentration loss, memory impairment, indecisiveness"],
            ["taVNS + Cognitive Training","taVNS enhances prefrontal excitability; adjunct to cognitive rehabilitation (Hein 2021)","taVNS before cognitive training session","Attentional fatigue, processing speed reduction"],
            ["CES + Standard Care","Sleep and energy support; indirectly improves cognitive performance in MDD (Philip 2017)","Evening (sleep) and morning (energy) sessions","Cognitive MDD with insomnia and fatigue"],
        ]),
        ("4) TRD (Treatment-Resistant)", [
            ["Intensive bilateral tDCS + Pharmacotherapy","Bilateral DLPFC tDCS (SELECT-TDCS protocol) combined with maintained antidepressant (Brunoni 2013); consider TPS add-on","Intensive: 2\u00d7/day \u00d7 5 days induction, then 5\u00d7/wk","Failed \u22652 adequate antidepressant trials"],
            ["taVNS + Intensive tDCS","taVNS as adjunct priming for intensive tDCS block; addresses autonomic and limbic components of TRD (Hein 2021; Redgrave 2018)","taVNS before each tDCS session during intensive block","TRD with anxiety, autonomic, or melancholic features"],
            ["CES + Intensive Protocol","CES daily throughout TRD treatment block for sleep and anxiety; reduces dropout (Philip 2017)","Evening daily throughout TRD block","TRD with severe sleep disturbance and anxiety"],
        ]),
        ("5) MDD + Somatic Pain", [
            ["tDCS (DLPFC + M1) + Graded Activity","L-DLPFC anodal + M1 cathodal (contra to pain) tDCS with graded activity/physiotherapy; targets both mood and pain circuits (Fregni 2006)","tDCS before activity/physiotherapy","MDD with comorbid chronic pain or fibromyalgia"],
            ["taVNS + tDCS","taVNS modulates ascending pain pathways and limbic-pain circuits; additive with tDCS for MDD-pain overlap (Adair 2020)","taVNS before tDCS session","Depression with autonomic dysregulation and pain"],
            ["CES + Standard Care","CES addresses sleep, anxiety, and pain-related distress; supportive throughout treatment block (Philip 2017)","Evening (sleep) and as needed for pain/anxiety","MDD with chronic pain, insomnia, somatic distress"],
        ]),
        ("6) MDD + Cognitive Decline (Older Adults)", [
            ["tDCS + Cognitive Stimulation","L-DLPFC anodal tDCS + cognitive stimulation; benefits cognitive symptoms alongside depression in older adults (Brunoni 2016; Yamada 2020)","tDCS before cognitive stimulation activity","MDD in older adults with mild cognitive complaints"],
            ["taVNS + Standard Care","taVNS supports autonomic stability and sleep quality; low-risk in older adults (Hein 2021)","Daily or 5\u00d7/wk; morning or pre-session","MDD with autonomic dysregulation, fatigue, insomnia"],
            ["CES + Standard Care","CES reduces anxiety/insomnia in older adults with MDD; FDA-cleared; generally well-tolerated (Philip 2017)","Evening; 20\u201340 min","MDD in older adults with anxiety and sleep disturbance"],
        ]),
    ],
    combination_summary=[
        ["Melancholic MDD",    "tDCS + Behavioural Activation","L-DLPFC anodal tDCS + structured behavioural activation (Brunoni 2016; Loo 2018)","tDCS before activation tasks","Severe anhedonia, retardation","Level A (tDCS); Moderate overall"],
        ["Melancholic MDD",    "taVNS + tDCS",                  "Priming: taVNS before tDCS enhances cortical receptivity (Hein 2021; Redgrave 2018)","taVNS 20\u201330 min before tDCS","Melancholic + autonomic features","Emerging"],
        ["Anxious MDD",        "tDCS + CBT",                    "Bilateral DLPFC tDCS + CBT; addresses emotional and cognitive regulation (Brunoni 2016)","tDCS before therapy","Anxious rumination, hyperarousal","Moderate"],
        ["Anxious MDD",        "taVNS + tDCS",                  "taVNS autonomic downshift before cortical stimulation (Hein 2021)","taVNS 20 min before tDCS","Anxiety, somatic tension","Emerging"],
        ["TRD",                "Intensive bilateral tDCS",       "Bilateral DLPFC tDCS SELECT-TDCS protocol + maintained antidepressant (Brunoni 2013)","Intensive: 2\u00d7/day \u00d7 5 days then 5\u00d7/wk","TRD, pharmacological non-response","Level A"],
        ["MDD + Somatic Pain", "tDCS (DLPFC + M1) + Activity",  "L-DLPFC + M1 tDCS with graded activity; targets mood and pain circuits (Fregni 2006)","tDCS before activity/physio","MDD with comorbid chronic pain","Limited\u2013Moderate"],
    ],
    outcomes=[
        ["PHQ-9",                   "Depressive symptoms (self-report)",  "Baseline, weeks 2, 4, 8, 12",  "\u226510 moderate; \u226515 severe; \u22655-point change = response"],
        ["HDRS-17",                 "Clinician-rated depression severity", "Baseline, weeks 4, 8, 12",     "\u226550% reduction from baseline = response; \u22647 = remission"],
        ["BDI-II",                  "Depressive symptoms (self-report)",  "Baseline, weeks 4, 8, 12",     "Score 0\u201313 minimal; 14\u201319 mild; 20\u201328 moderate; 29\u201363 severe"],
        ["MoCA",                    "Global cognition screening",          "Baseline, month 3",            "Score <26 cognitive impairment; track improvement"],
        ["GAD-7",                   "Comorbid anxiety symptoms",           "Baseline, weeks 4, 8, 12",     "\u226510 moderate; \u226515 severe"],
        ["QIDS-SR",                 "Quick Inventory of Depressive Symptoms","Baseline, weeks 2, 4, 8, 12","Score 0\u20135 normal; 6\u201310 mild; 11\u201315 moderate; \u226516 severe"],
        ["PHQ-9 Item 9",            "Suicidality monitoring",              "Every session",                "Any score \u22651 \u2192 Doctor review required immediately"],
        ["CGI-S / CGI-I",           "Clinical Global Impression",          "Baseline, weeks 4, 8, 12",     "CGI-I \u22642 = much improved; \u22643 = minimally improved"],
        ["SOZO PRS",                "NIBS-specific functional outcome",    "Baseline, weeks 2, 4, 8, 12", "Proprietary; composite mood/cognitive/functional domains"],
    ],
    outcomes_abbrev=["PHQ-9", "HDRS-17", "MoCA", "GAD-7", "SOZO PRS"],
)

# ══════════════════════════════════════
# 3. GENERALIZED ANXIETY DISORDER
# ══════════════════════════════════════
CONDITIONS["anxiety"] = dict(
    name="Generalized Anxiety Disorder", icd10="F41.1",
    doc_num="SOZO-GAD-FEL-003",
    tps_status="INVESTIGATIONAL / OFF-LABEL",
    tdcs_class="Level B evidence; CE-marked",
    tps_class="INVESTIGATIONAL / OFF-LABEL",
    tavns_class="Emerging; CE-marked; primary adjunct modality",
    ces_class="FDA-cleared adjunctive for anxiety/mood/sleep",
    inclusion=[
        "Confirmed diagnosis of GAD or primary anxiety disorder (DSM-5 or ICD-11) by qualified clinician",
        "GAD-7 score \u226510 at baseline (moderate-to-severe anxiety)",
        "Age 18+ years",
        "Stable or no anxiolytic/antidepressant medication (no change in 4 weeks prior to enrolment)",
        "Written informed consent (including TPS off-label disclosure)",
        "Baseline assessments completed (GAD-7, HAMA, PHQ-9, ISI)",
    ],
    exclusion=[
        "Intracranial metallic hardware in stimulation path",
        "Cochlear implant or DBS device",
        "Active psychotic features",
        "Severe alcohol or substance dependence as primary diagnosis",
        "Skull defects, craniectomy, or recent craniotomy",
        "Pregnancy (tDCS, TPS)",
        "Inability to provide informed consent",
    ],
    discussion=[
        "Cardiac pacemaker or defibrillator \u2014 individual risk\u2013benefit assessment",
        "Epilepsy or seizure history \u2014 formal risk\u2013benefit with documented rationale",
        "Benzodiazepine dependence \u2014 protocol requires specialist input; titration planning required",
        "Comorbid MDD requiring protocol modification",
        "PTSD comorbidity \u2014 trauma-informed approach required",
        "Coagulation disorders or anticoagulants (especially TPS)",
        "Dermatological conditions at electrode sites",
        "Severe health anxiety or cyberchondria about device use",
    ],
    overview=[
        "Generalized Anxiety Disorder (GAD) is characterised by excessive, uncontrollable worry about "
        "multiple domains occurring on more days than not for at least 6 months, accompanied by somatic "
        "symptoms such as muscle tension, sleep disturbance, and fatigue. GAD has a lifetime prevalence "
        "of 5\u20139% and is one of the most common anxiety disorders worldwide (Kessler et al., 2005).",
        "Neurobiologically, GAD involves hyperactivation of the amygdala and anterior insula, "
        "hypoactivation of the prefrontal cortex (particularly the right DLPFC), and dysregulation of "
        "the salience network (SN) and default mode network (DMN). The SN-DMN interaction underpins "
        "the ruminative and threat-hypervigilant phenomenology of GAD.",
        "tDCS targeting the right DLPFC (cathodal) and/or left DLPFC (anodal) modulates prefrontal "
        "control over amygdala hyperactivity. taVNS is a primary adjunctive modality given its role "
        "in autonomic downregulation via the vagal-NTS-LC pathway.",
        "NIBS Evidence in GAD: Evidence for tDCS in anxiety is growing but less mature than in MDD. "
        "Right DLPFC cathodal tDCS (to reduce hyperactivation) and bilateral approaches have shown "
        "anxiolytic effects in RCTs. taVNS is CE-marked and FDA-cleared (VNS) for depression/anxiety "
        "and is a key component of the SOZO anxiety protocol. CES is FDA-cleared for anxiety.",
    ],
    pathophysiology=[
        "GAD pathophysiology involves a failure of prefrontal inhibitory control over amygdala-driven "
        "threat responses. Right DLPFC and vmPFC show reduced activation, impairing emotion regulation "
        "and worry termination. The amygdala and anterior insula are hyperactivated, amplifying interoceptive "
        "threat signals. HPA axis dysregulation and chronic cortisol elevation contribute to hippocampal "
        "volume changes and further impair prefrontal function.",
        "The salience network (insula, dACC) shows persistent hyperactivation, maintaining threat vigilance "
        "and preventing effective disengagement from worry. GABAergic deficits (particularly in prefrontal "
        "and limbic circuits) underpin the anxiolytic mechanism of benzodiazepines and are relevant to "
        "neuromodulation targeting.",
    ],
    std_treatment=[
        "First-line pharmacotherapy includes SSRIs (sertraline, escitalopram) and SNRIs (venlafaxine, "
        "duloxetine). Buspirone is an alternative. Benzodiazepines are reserved for short-term or "
        "acute use due to dependence risk. Pregabalin has evidence for GAD. Cognitive Behavioural Therapy "
        "(CBT) has the strongest evidence base for GAD and is recommended in combination with NIBS.",
    ],
    symptoms=[
        ["Excessive Worry",          "Uncontrollable worry about multiple life domains; persistent and pervasive",                "Core criterion",    "Kessler 2005; DSM-5"],
        ["Difficulty Controlling Worry","Inability to stop or redirect worry despite effort",                                    "Core criterion",    "DSM-5; ICD-11"],
        ["Restlessness",             "Feeling keyed up, on edge, or unable to relax",                                           "60\u201380%",       "DSM-5"],
        ["Fatigue",                  "Easily fatigued; reduced energy from chronic arousal burden",                              "50\u201370%",       "DSM-5"],
        ["Concentration Difficulties","Mind going blank; difficulty maintaining focus due to worry intrusion",                   "50\u201370%",       "DSM-5"],
        ["Irritability",             "Heightened irritability and emotional reactivity",                                         "40\u201360%",       "DSM-5"],
        ["Muscle Tension",           "Chronic muscle tension, aches, soreness; somatic symptom burden",                         "60\u201380%",       "DSM-5"],
        ["Sleep Disturbance",        "Difficulty falling or staying asleep; restless unsatisfying sleep",                       "60\u201380%",       "DSM-5; Wittchen 2011"],
        ["Autonomic Symptoms",       "Palpitations, sweating, tremor, GI disturbance, dry mouth",                               "50\u201370%",       "Wittchen 2011"],
        ["Somatic Hypervigilance",   "Excessive attention to bodily sensations; amplification of normal physiological signals", "30\u201350%",       "Barsky 2001"],
    ],
    brain_regions=[
        ["Right DLPFC",              "Hypoactivation; impaired prefrontal control over amygdala threat responses",              "Cathodal tDCS (inhibitory) or bilateral normalisation; Level B evidence",    "Ironside 2019"],
        ["Left DLPFC",               "CEN hypoactivation; impaired cognitive control over worry",                               "Anodal tDCS (excitatory); supports emotion regulation",                       "Brunoni 2016"],
        ["Amygdala",                 "Hyperactivation to threat cues; drives fear and worry circuitry",                         "Modulated indirectly via prefrontal tDCS and taVNS limbic pathways",          "Etkin 2010"],
        ["Anterior Insula",          "Interoceptive hypervigilance; amplifies somatic anxiety signals",                         "Modulated via taVNS (vagal-insular pathway) and tDCS (indirect)",             "Simmons 2006"],
        ["Anterior Cingulate Cortex","dACC hyperactivation; threat monitoring and conflict detection",                          "Bilateral DLPFC tDCS modulates ACC activity; TPS (investigational)",          "Whalen 1998"],
        ["vmPFC / OFC",              "Impaired fear extinction and worry termination",                                           "Prefrontal tDCS supports vmPFC engagement; TPS investigational",              "Hartley 2011"],
        ["Hippocampus",              "Contextual fear; safety learning; reduced volume with chronic stress",                     "Indirectly targeted via TPS and BDNF upregulation pathways",                  "Lissek 2014"],
        ["Basal Ganglia",            "Habit-based worry patterns; striatal engagement in anxiety perseveration",                 "Indirectly modulated via prefrontal-striatal circuits",                       "Pitman 2012"],
    ],
    brainstem=[
        ["Locus Coeruleus (LC)",     "Noradrenergic hyperactivation; drives hyperarousal and anxiety",                          "taVNS modulates LC activity via NTS; primary mechanism for anxiety reduction","Aston-Jones 2005"],
        ["Nucleus Tractus Solitarius","Vagal afferent relay; central autonomic hub; key for HRV",                               "Primary target of taVNS; modulates amygdala, ACC, and prefrontal cortex",    "Frangos 2015"],
        ["Periaqueductal Gray",      "Defensive behaviour; threat-escape processing; chronic anxiety maintenance",               "Modulated indirectly via prefrontal and vagal neuromodulation",               "Canteras 2002"],
        ["Dorsal Raphe Nucleus",     "Serotonergic dysregulation; comorbid anxiety-depression pathway",                         "taVNS and tDCS (DLPFC) may influence serotonergic projections",               "Deakin 1991"],
        ["Parabrachial Nucleus",     "Visceral and somatic threat integration; autonomic fear circuits",                         "Modulated indirectly via vagal and prefrontal neuromodulation",               "Bhatt 2020"],
    ],
    phenotypes=[
        ["Classic GAD",              "Full DSM-5 criteria met; excessive worry across multiple domains \u22656 months",         "Excessive worry, fatigue, muscle tension, sleep disturbance",   "Bilateral DLPFC tDCS; taVNS; CES"],
        ["Anxious MDD (Mixed)",      "Significant depression + anxiety; HDRS anxiety/somatisation subscale elevated",           "Low mood, anxiety, tension, sleep disturbance",                 "L-DLPFC anodal tDCS; taVNS; CES; bilateral approach"],
        ["Health Anxiety (Somatic)", "Persistent preoccupation with having serious illness; somatic amplification",              "Health worry, somatic vigilance, reassurance-seeking",          "Right DLPFC cathodal; taVNS; CES"],
        ["Social Anxiety (SAD)",     "Marked fear or anxiety about social situations; avoidance; performance anxiety",           "Social fear, avoidance, physical symptoms in social contexts",  "Right DLPFC cathodal tDCS + taVNS; CES"],
        ["Panic Disorder",           "Recurrent unexpected panic attacks; anticipatory anxiety; avoidance",                      "Panic attacks, palpitations, derealization, avoidance",         "Bilateral DLPFC tDCS; taVNS primary; CES"],
        ["GAD + Insomnia",           "GAD with prominent insomnia as a maintaining and exacerbating factor",                    "Worry, insomnia, fatigue, daytime impairment",                  "L-DLPFC tDCS; CES primary (sleep); taVNS"],
        ["GAD + Chronic Pain",       "Anxiety maintaining central sensitisation and pain amplification",                        "Worry, somatic tension, pain, sleep disturbance",               "Bilateral tDCS + M1; taVNS; CES"],
    ],
    symptom_map=[
        ["Excessive Worry",          "Right DLPFC, vmPFC, dACC",      "Right DLPFC cathodal tDCS + bilateral tDCS option; TPS (PFC, ACC) investigational",    "Moderate (Ironside 2019)"],
        ["Autonomic Hyperarousal",   "LC, NTS, Amygdala",              "taVNS primary (vagal-NTS-LC); bilateral tDCS supportive; CES adjunct",                "Level A (taVNS: VNS evidence)"],
        ["Sleep Disturbance",        "Frontal, Thalamus, LC",          "CES primary; taVNS adjunctive; tDCS (frontal slow-wave); sleep hygiene",              "Moderate (Philip 2017)"],
        ["Muscle Tension",           "SMA, Motor cortex, Autonomic",   "taVNS primary; CES; M1/SMA tDCS supportive; relaxation training",                    "Moderate (taVNS evidence)"],
        ["Cognitive Anxiety",        "Left DLPFC, ACC",                "L-DLPFC anodal tDCS + CBT; TPS DLPFC investigational",                               "Moderate (Brunoni 2016)"],
        ["Somatic Symptoms",         "Insula, Anterior Cingulate",     "taVNS (vagal-insular pathway) + CES; bilateral tDCS supportive",                      "Moderate (taVNS)"],
        ["Concentration / Attention","Left DLPFC, Parietal",           "L-DLPFC anodal tDCS + cognitive training",                                           "Moderate (Brunoni 2016)"],
        ["Comorbid Depression",      "Left DLPFC, sgACC",              "L-DLPFC anodal tDCS (primary); taVNS + CES; bilateral for mixed presentations",       "Level A (for MDD component)"],
        ["Panic / Avoidance",        "Amygdala, Insula, PFC",          "taVNS primary + bilateral DLPFC tDCS; CES; exposure therapy integration",             "Moderate (taVNS; Brunoni 2016)"],
    ],
    montage=[
        ["Classic GAD",              "F3 anode + F4 cathode (bilateral normalisation); or right F4 cathodal alone","Cranial (global + targeted DLPFC/ACC)", "taVNS primary, CES"],
        ["Anxious MDD",              "F3 anode + Fp2 cathode; or F3 + F4 bilateral anode",                         "Cranial (global + targeted DLPFC)",     "taVNS + CES; L-DLPFC anodal"],
        ["Health Anxiety / Somatic", "F4 cathode + shoulder anode (right DLPFC cathodal)",                         "Cranial (global + targeted right PFC)", "taVNS primary; CES"],
        ["Social Anxiety",           "F4 cathode + F3 anode; bilateral DLPFC approach",                            "Cranial (global + targeted PFC)",       "taVNS; CES; CBT integration"],
        ["Panic Disorder",           "F3 + F4 bilateral anode; or right F4 cathodal",                              "Cranial (global + targeted DLPFC)",     "taVNS primary; CES"],
        ["GAD + Insomnia",           "F3 anode + Fp2 cathode; Fz evening slow-wave protocol",                      "Cranial (global + targeted DLPFC)",     "CES primary (sleep); taVNS"],
        ["GAD + Chronic Pain",       "F3 + F4 bilateral + C3/C4 (contra to pain) option",                          "Cranial + peripheral (pain dermatomes)","taVNS; CES"],
        ["No response after 8\u201310 sessions","Reassess phenotype; consider bilateral vs. unilateral; add TPS","Adjust parameters; TPS add-on",           "Review all adjuncts; CBT referral"],
    ],
    tdcs_protocols=[
        ["C1","GAD \u2014 right DLPFC cathodal (primary)","F3 anode",         "F4 / right shoulder",       "2 mA, 20\u201330 min, 5\u00d7/wk \u00d7 6\u201310 wks","Level B; anxiolytic (Ironside 2019; Brunoni 2016)"],
        ["C2","Bilateral DLPFC normalisation",             "F3 + F4 bilateral anode","Fp2 + Fp1 / shoulders","2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate; bilateral approach (Loo 2012)"],
        ["C3","Anxious MDD \u2014 L-DLPFC anodal",        "F3 anode",         "Fp2 / extracephalic",        "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Level A (MDD component; Brunoni 2016)"],
        ["C4","Panic / arousal reduction",                 "F3 + F4 bilateral","Extracephalic shoulder",     "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Brunoni 2016)"],
        ["C5","Sleep disturbance",                         "Fz anode",         "Pz / extracephalic",         "1\u20132 mA, 20 min, evening",                       "Moderate (Philip 2017)"],
        ["C6","Somatic anxiety / muscle tension",          "F3 + Cz anode",    "F4 / extracephalic",         "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Brunoni 2016)"],
        ["C7","Cognitive anxiety / concentration",         "F3 anode",         "Fp2, extracephalic",         "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Brunoni 2016)"],
        ["C8","Chronic GAD maintenance",                   "F3 + F4 bilateral","Extracephalic shoulder",     "2 mA, 20\u201330 min, 3\u00d7/wk maintenance",      "Moderate (Loo 2012; Brunoni 2016)"],
    ],
    plato_protocols=[
        ["C1-PS","GAD \u2014 primary",              "Frontal (F3 area)","F3","Right shoulder",   "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Combine with taVNS as primary protocol"],
        ["C2-PS","Bilateral normalisation",         "Frontal (F3 area)","F3","Right shoulder",   "1.6 mA, 20\u201330 min","5\u00d7/wk",         "R-DLPFC cathodal not directly achievable; use L anodal"],
        ["C3-PS","Anxious MDD",                     "Frontal (F3 area)","F3","Right shoulder",   "1.6 mA, 20\u201330 min","5\u00d7/wk",         "L-DLPFC anodal primary; adjunct to CES"],
        ["C4-PS","Panic / arousal",                 "Frontal (F3 area)","F3","Right shoulder",   "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Pre-session taVNS recommended"],
        ["C5-PS","Sleep disturbance",               "Frontal (Fz area)","Fz","Shoulder",         "1.6 mA, 20 min",        "Evening",            "Evening use; combine with CES"],
        ["C6-PS","Somatic / muscle tension",        "Frontal (F3 area)","F3","Shoulder",         "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Combine with relaxation training"],
        ["C7-PS","Cognitive anxiety",               "Frontal (F3 area)","F3","Shoulder",         "1.6 mA, 20\u201330 min","5\u00d7/wk",         "CBT session pairing recommended"],
        ["C8-PS","Maintenance GAD",                 "Frontal (F3 area)","F3","Right shoulder",   "1.6 mA, 20\u201330 min","3\u00d7/wk",         "Maintenance block after initial intensive"],
    ],
    tps_protocols=[
        ["T1","GAD \u2014 prefrontal (primary)",    "R-DLPFC + L-DLPFC bilateral, OFC","0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz; 10 sessions/2 wks","4,000 Tgt (DLPFC) + 2,000 PRE; total 6\u20138K","Investigational (pilot data)"],
        ["T2","Amygdala / limbic hyperactivation",  "Medial PFC + ACC (closest accessible deep target)","0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",           "4,000 Tgt + 2,000 Std; total 6\u20138K",       "Investigational"],
        ["T3","Somatic anxiety / interoceptive",    "Anterior insula (accessible via temporal ROI), ACC","0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",          "4,000 Tgt + 2,000 Std; total 6\u20138K",       "Investigational"],
        ["T4","Sleep disturbance",                  "Frontal slow-wave circuits, mPFC",                  "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",          "4,000 Tgt + 2,000 PRE; total 6\u20138K",       "Investigational"],
        ["T5","Panic / autonomic dysregulation",    "DLPFC + ACC",                                       "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",          "4,000 Tgt + 2,000 Std; total 6\u20138K",       "Investigational"],
    ],
    ces_role=[
        ["Anxiety reduction",     "Primary FDA-cleared indication; reduces somatic and cognitive anxiety features",            "Daily or 5\u00d7/wk; 20\u201340 min; morning or as needed"],
        ["Sleep disturbance",     "Enhances sleep onset and quality; key target in GAD maintenance",                          "Evening before bed; 20\u201340 min; coordinate with taVNS"],
        ["Autonomic stabilisation","Stabilises HRV and autonomic tone; complements taVNS vagal modulation",                  "Before tDCS session or standalone; 20\u201330 min"],
        ["Muscle tension",        "Reduces somatic muscle tension and physical anxiety symptoms",                              "As needed; morning or pre-session; 20\u201330 min"],
    ],
    tavns_role="taVNS is a primary adjunct in GAD, providing autonomic downregulation via the vagal-NTS-LC pathway, reducing amygdala hyperactivity, improving HRV, and attenuating the physiological substrate of chronic anxiety.",
    combinations=[
        ("1) Classic GAD", [
            ["tDCS + CBT","Bilateral DLPFC tDCS + CBT; addresses cognitive and neural substrates of excessive worry (Brunoni 2016; Fasotti 2020)","tDCS before CBT session","Excessive worry, avoidance, somatic tension"],
            ["taVNS + tDCS","taVNS priming before tDCS; autonomic downshift before cortical stimulation (Hein 2021; Redgrave 2018)","taVNS 20\u201330 min before tDCS","Autonomic hyperarousal, somatic anxiety"],
            ["CES + Standard Care","CES primary FDA-cleared approach for anxiety; daily use (Philip 2017)","Daily; morning and/or evening as prescribed","Anxiety, sleep disturbance, somatic tension"],
        ]),
        ("2) Anxious MDD", [
            ["tDCS + Psychotherapy","L-DLPFC anodal tDCS + CBT or behavioural activation; targets both MDD and GAD components (Brunoni 2016)","tDCS before therapy","Low mood + excessive worry + tension"],
            ["taVNS + tDCS","taVNS reduces physiological anxiety before tDCS session; additive for mixed anxiety-depression (Hein 2021)","taVNS before tDCS","Autonomic hyperarousal with depressive features"],
            ["CES + Standard Care","CES for anxiety and sleep; FDA-cleared; complements tDCS treatment block (Philip 2017)","Evening and/or morning","Anxious MDD with sleep disturbance"],
        ]),
        ("3) Panic Disorder", [
            ["tDCS + Exposure Therapy","Bilateral DLPFC tDCS before/during graded exposure; enhances fear extinction via prefrontal facilitation (Herrmann 2017)","tDCS before exposure session","Panic attacks, avoidance, anticipatory anxiety"],
            ["taVNS + tDCS","taVNS reduces interoceptive threat amplification before tDCS; key for panic (Hein 2021)","taVNS 20\u201330 min before tDCS","Panic with autonomic arousal and somatic features"],
            ["CES + Standard Care","CES daily for baseline anxiety reduction; improves between-session state for exposure work (Philip 2017)","Daily; morning and/or evening","Panic disorder with chronic anticipatory anxiety"],
        ]),
        ("4) Health Anxiety / Somatic", [
            ["tDCS + ACT / Mindfulness","Right DLPFC cathodal tDCS + ACT or mindfulness; addresses somatic hypervigilance (Brunoni 2016)","tDCS before mindfulness/ACT session","Health worry, somatic amplification, reassurance-seeking"],
            ["taVNS + Somatic Relaxation","taVNS + progressive muscle relaxation; reduces interoceptive amplification (Hein 2021)","taVNS concurrent with relaxation practice","Muscle tension, somatic symptoms, physical anxiety"],
            ["CES + Standard Care","CES for anxiety and somatic tension; FDA-cleared (Philip 2017)","Daily as prescribed","Chronic somatic anxiety, sleep disturbance"],
        ]),
        ("5) GAD + Insomnia", [
            ["tDCS + Sleep Therapy (CBT-I)","DLPFC tDCS + CBT for insomnia; targets both anxiety and sleep maintenance (Brunoni 2016; Edinger 2021)","tDCS before CBT-I session; evening slow-wave protocol","GAD with severe insomnia as maintaining factor"],
            ["taVNS + CES","Dual adjunct: taVNS for autonomic downshift + CES for sleep; maximum non-pharmacological sleep support (Hein 2021; Philip 2017)","taVNS 20 min before bed; CES at bedtime","Sleep-onset difficulty, nocturnal arousal"],
            ["CES Primary + tDCS","CES as primary sleep and anxiety modality; tDCS supportive for cognitive anxiety (Philip 2017)","CES evening primary; tDCS morning 5\u00d7/wk","GAD where insomnia is most impairing feature"],
        ]),
        ("6) GAD + Chronic Pain", [
            ["tDCS (DLPFC + M1) + Graded Activity","Bilateral DLPFC + M1 cathodal tDCS with graded activity; anxiety-pain circuit modulation (Fregni 2006; Brunoni 2016)","tDCS before graded activity","GAD maintaining central sensitisation and pain"],
            ["taVNS + Standard Care","taVNS modulates autonomic arousal and ascending pain pathways; key for anxiety-pain overlap (Adair 2020)","taVNS before tDCS or activity","Autonomic hyperarousal with somatic pain"],
            ["CES + Standard Care","CES reduces anxiety and sleep disturbance maintaining pain; supportive throughout (Philip 2017)","Daily as prescribed","GAD + chronic pain with sleep and anxiety amplification"],
        ]),
    ],
    combination_summary=[
        ["Classic GAD",         "tDCS + CBT",           "Bilateral DLPFC tDCS + CBT; addresses cognitive and neural worry substrate (Brunoni 2016)","tDCS before CBT","Excessive worry, avoidance, somatic tension","Moderate"],
        ["Classic GAD",         "taVNS + tDCS",         "taVNS autonomic priming before tDCS; dual-pathway engagement (Hein 2021)","taVNS 20\u201330 min before tDCS","Autonomic hyperarousal","Emerging"],
        ["Anxious MDD",         "tDCS + Psychotherapy", "L-DLPFC anodal tDCS + CBT/BA; addresses both MDD and GAD components (Brunoni 2016)","tDCS before therapy","Low mood + excessive worry","Moderate"],
        ["Panic Disorder",      "tDCS + Exposure Therapy","Bilateral DLPFC tDCS before graded exposure; enhances fear extinction (Herrmann 2017)","tDCS before exposure session","Panic attacks, avoidance","Moderate"],
        ["GAD + Insomnia",      "taVNS + CES",           "Dual adjunct for sleep and autonomic downregulation (Hein 2021; Philip 2017)","taVNS + CES at bedtime","GAD with insomnia as maintaining factor","Emerging"],
        ["GAD + Chronic Pain",  "tDCS (DLPFC+M1) + Activity","Anxiety-pain circuit modulation via bilateral tDCS + activity (Fregni 2006; Brunoni 2016)","tDCS before activity","GAD maintaining central sensitisation","Limited\u2013Moderate"],
    ],
    outcomes=[
        ["GAD-7",             "Anxiety severity (self-report)",         "Baseline, weeks 2, 4, 8, 12",  "\u226510 moderate; \u226515 severe; \u22655-point change = response"],
        ["HAMA",              "Clinician-rated anxiety severity",        "Baseline, weeks 4, 8, 12",     "Score \u226417 mild; 18\u201324 moderate; \u226525 severe"],
        ["PHQ-9",             "Comorbid depressive symptoms",           "Baseline, weeks 4, 8, 12",     "\u226510 moderate; \u226515 severe"],
        ["ISI",               "Insomnia severity",                      "Baseline, weeks 4, 8, 12",     "Score 0\u20137 no clinically significant insomnia; \u226715 moderate insomnia"],
        ["PSQI",              "Sleep quality",                          "Baseline, months 1, 3",        "Score >5 poor sleep quality"],
        ["STAI-State/Trait",  "State and trait anxiety dimensions",     "Baseline, months 1, 3",        "Normative values by age/gender; track change from baseline"],
        ["CGI-S / CGI-I",     "Clinical Global Impression",             "Baseline, weeks 4, 8, 12",     "CGI-I \u22642 = much improved"],
        ["WHO-5",             "Wellbeing and quality of life",          "Baseline, months 1, 3",        "Score \u226452 poor wellbeing (max 100)"],
        ["SOZO PRS",          "NIBS-specific functional outcome",       "Baseline, weeks 2, 4, 8, 12", "Proprietary; composite anxiety/sleep/functional domains"],
    ],
    outcomes_abbrev=["GAD-7", "HAMA", "PHQ-9", "ISI", "SOZO PRS"],
)

# ══════════════════════════════════════
# 4. ADHD
# ══════════════════════════════════════
CONDITIONS["adhd"] = dict(
    name="Attention Deficit Hyperactivity Disorder", icd10="F90",
    doc_num="SOZO-ADHD-FEL-004",
    tps_status="INVESTIGATIONAL / OFF-LABEL",
    tdcs_class="Level B evidence; CE-marked",
    tps_class="INVESTIGATIONAL / OFF-LABEL",
    tavns_class="Emerging adjunctive; CE-marked",
    ces_class="FDA-cleared adjunctive for mood/anxiety/sleep",
    inclusion=[
        "Confirmed ADHD diagnosis (DSM-5 or ICD-11) by qualified clinician; all subtypes eligible",
        "ADHD symptoms causing functional impairment (CAARS or BRIEF \u22651.5 SD above norm)",
        "Age 18+ years (adult ADHD protocol)",
        "Stable or no ADHD medication (no change in 4 weeks prior to enrolment)",
        "Written informed consent (including TPS off-label disclosure)",
        "Baseline assessments completed (CAARS, BRIEF-2, MoCA, PHQ-9)",
    ],
    exclusion=[
        "Intracranial metallic hardware in stimulation path",
        "Cochlear implant or DBS device",
        "Active psychotic features",
        "Skull defects, craniectomy, or recent craniotomy",
        "Pregnancy (tDCS, TPS)",
        "Inability to provide informed consent",
        "Intellectual disability (IQ <70) as primary diagnosis",
    ],
    discussion=[
        "Cardiac pacemaker or defibrillator \u2014 individual risk\u2013benefit assessment",
        "Epilepsy or seizure history \u2014 formal risk\u2013benefit with documented rationale",
        "Stimulant medication use \u2014 may interact with tDCS cortical excitability; timing consideration",
        "Comorbid bipolar disorder \u2014 mood stabiliser coverage required",
        "Comorbid ASD \u2014 requires adapted protocol and slower titration",
        "Coagulation disorders or anticoagulants (especially TPS)",
        "Dermatological conditions at electrode sites",
        "Substance use disorder comorbidity",
    ],
    overview=[
        "Attention Deficit Hyperactivity Disorder (ADHD) is a neurodevelopmental disorder characterised by "
        "pervasive patterns of inattention, hyperactivity, and/or impulsivity that impair functioning across "
        "multiple settings. Adult ADHD has a prevalence of 2.5\u20135% globally. The majority of children with "
        "ADHD continue to experience clinically significant symptoms into adulthood (Faraone et al., 2021).",
        "ADHD involves dysregulation of the prefrontal-striatal-cerebellar circuit, with core deficits in "
        "executive function, working memory, inhibitory control, and attentional regulation. The dopaminergic "
        "and noradrenergic systems are the primary pharmacological targets. Neuroimaging demonstrates consistent "
        "DLPFC, ACC, and inferior frontal gyrus (IFG) hypoactivation in ADHD.",
        "tDCS targeting the left DLPFC (anodal) enhances prefrontal excitability and has shown improvements "
        "in working memory, inhibitory control, and attention in ADHD across multiple studies (Westwood et al., "
        "2021). The right IFG (a key response inhibition node) is an emerging cathodal target.",
        "NIBS Evidence in ADHD: Meta-analyses support modest but consistent tDCS effects on working memory "
        "and inhibitory control in ADHD (Westwood et al., 2021). TPS targeting prefrontal circuits is "
        "investigational. taVNS has plausible mechanisms via noradrenergic modulation relevant to ADHD.",
    ],
    pathophysiology=[
        "ADHD pathophysiology involves hypofunction of the mesocortical dopaminergic pathway (VTA\u2192PFC) "
        "and locus coeruleus noradrenergic projections, resulting in DLPFC, IFG, and ACC hypoactivation. "
        "This impairs the top-down executive control network (CEN). The default mode network (DMN) fails "
        "to suppress adequately during task demands (DMN suppression failure), generating internal "
        "distraction and mind-wandering.",
        "Cerebellar-cortical timing circuits are implicated in temporal processing deficits and motor "
        "impulsivity in ADHD. Reward circuitry (ventral striatum) shows altered delay discounting, "
        "contributing to motivational dysregulation. Structural MRI shows reduced cortical thickness "
        "and volume in prefrontal regions.",
    ],
    std_treatment=[
        "First-line pharmacotherapy: methylphenidate (ADHD-specific dopamine-noradrenaline reuptake "
        "inhibitor) and amphetamine derivatives (lisdexamfetamine) for attention and executive function. "
        "Atomoxetine (non-stimulant SNRI) for comorbid anxiety or stimulant contraindication. "
        "Guanfacine and clonidine (alpha-2 agonists) for hyperactivity/impulsivity. CBT is recommended "
        "in combination with pharmacotherapy for adult ADHD. NIBS is adjunctive.",
    ],
    symptoms=[
        ["Inattention",           "Sustained difficulty maintaining attention; careless mistakes; easily distracted",        "Core criterion", "Faraone 2021; DSM-5"],
        ["Hyperactivity",         "Restlessness, fidgeting, inability to stay seated; excessive talking",                    "Core criterion", "DSM-5; Barkley 2015"],
        ["Impulsivity",           "Interrupting others; blurting out answers; difficulty waiting turn; poor inhibition",     "Core criterion", "DSM-5"],
        ["Working Memory Deficit","Poor retention and manipulation of information in short-term memory",                     "80\u201390%",    "Barkley 1997"],
        ["Executive Dysfunction", "Poor planning, organisation, time management, cognitive flexibility",                     "70\u201390%",    "Brown 2006"],
        ["Emotional Dysregulation","Low frustration tolerance; emotional reactivity; mood lability",                         "50\u201370%",    "Barkley 2015"],
        ["Motivation Dysregulation","Difficulty initiating tasks; procrastination; variable motivation depending on interest","60\u201380%",    "Volkow 2009"],
        ["Sleep Disturbance",     "Delayed sleep phase; insomnia; non-restorative sleep; circadian dysregulation",           "50\u201370%",    "Becker 2019"],
        ["Anxiety Comorbidity",   "Comorbid anxiety in 30\u201350% of adults with ADHD",                                    "30\u201350%",    "Kessler 2006"],
        ["Substance Use Risk",    "Elevated risk of substance use disorders (self-medication of ADHD symptoms)",              "20\u201335%",    "Charach 2011"],
    ],
    brain_regions=[
        ["Left DLPFC (F3)",         "Hypoactivation; core executive function, working memory, top-down attentional control",  "Anodal tDCS primary target; enhances executive excitability (Level B)",     "Westwood 2021"],
        ["Right IFG (F4/F8)",       "Response inhibition; go/no-go processing; motor impulse control",                        "Cathodal tDCS (R-IFG) or bilateral; targets inhibitory deficits",            "Aron 2004"],
        ["Anterior Cingulate Cortex","Conflict monitoring; error detection; executive attention; DMN suppression",             "DLPFC tDCS indirectly modulates ACC; TPS (investigational)",                 "Barch 2001"],
        ["Striatum (Caudate/Putamen)","Dopaminergic reward; motor control; habit formation",                                   "Modulated via prefrontal-striatal circuits by tDCS and TPS",                 "Volkow 2009"],
        ["Cerebellum",              "Timing circuits; motor impulsivity; motor coordination and sequencing",                   "Cerebellar tDCS has limited ADHD evidence; TPS (investigational)",           "Stoodley 2014"],
        ["Insula",                  "Interoceptive awareness; impulsivity; self-monitoring deficit in ADHD",                   "Indirectly modulated via prefrontal tDCS and taVNS (vagal-insular)",         "Wittmann 2010"],
        ["vmPFC / OFC",             "Delay discounting; reward valuation; motivational regulation",                            "Prefrontal tDCS modulates vmPFC via fronto-limbic connections",               "Barkley 2001"],
        ["Thalamus",                "Sensory gating; arousal regulation; thalamocortical synchrony in attention",              "TPS investigational deep target; tDCS effects thalamus indirectly",          "Satterthwaite 2009"],
    ],
    brainstem=[
        ["Locus Coeruleus (LC)",    "Noradrenergic arousal and attentional modulation; key atomoxetine target",               "taVNS modulates LC via NTS; augments noradrenergic tone for attention",     "Aston-Jones 2005"],
        ["VTA (Dopaminergic)",      "Mesocortical dopamine; motivation, reward, prefrontal activation",                       "Indirectly modulated via prefrontal tDCS and mesolimbic pathway",            "Volkow 2009"],
        ["Nucleus Tractus Solitarius","Vagal afferent relay; central autonomic hub; modulates cortical arousal",              "Primary target of taVNS; affects LC and prefrontal circuits",               "Frangos 2015"],
        ["Periaqueductal Gray",     "Arousal; defensive behaviour; motor inhibition circuits",                                 "Modulated indirectly via prefrontal and vagal neuromodulation",              "Bari 2013"],
        ["Reticular Activating System","General arousal; thalamocortical gating; attention maintenance",                      "taVNS and tDCS indirectly modulate ascending arousal systems",               "Moruzzi 1949"],
    ],
    phenotypes=[
        ["ADHD \u2014 Predominantly Inattentive", "Inattention dominant; minimal hyperactivity; often under-diagnosed in adults", "Concentration, working memory, organisation, task-completion failures","L-DLPFC anodal tDCS; cognitive training; taVNS"],
        ["ADHD \u2014 Combined Type",             "Both inattention and hyperactivity-impulsivity meeting full criteria",         "Inattention + impulsivity + hyperactivity + executive dysfunction",     "L-DLPFC anodal + R-IFG cathodal tDCS; taVNS; CES"],
        ["ADHD \u2014 Hyperactive-Impulsive",     "Hyperactivity and impulsivity dominant; inattention subthreshold",            "Impulsivity, hyperactivity, poor frustration tolerance",                "R-IFG cathodal tDCS; bilateral DLPFC; taVNS"],
        ["ADHD + Executive Function Profile",     "Severe EF deficits beyond core ADHD criteria",                               "Planning, organisation, time management, working memory failures",      "L-DLPFC anodal tDCS; TPS DLPFC; cognitive training"],
        ["ADHD + Anxiety",                        "ADHD with significant comorbid anxiety",                                      "Inattention + worry + tension + sleep disturbance",                     "Bilateral DLPFC; taVNS primary; CES; slower titration"],
        ["ADHD + Depression",                     "ADHD with comorbid MDD",                                                      "Inattention + low mood + anergia + cognitive slowing",                  "L-DLPFC anodal tDCS; CES; taVNS; treat MDD component"],
        ["ADHD + Sleep Disorder",                 "ADHD with circadian dysregulation and insomnia as maintaining factors",       "Inattention + delayed sleep phase + daytime fatigue",                   "DLPFC tDCS; CES primary (sleep); taVNS"],
    ],
    symptom_map=[
        ["Inattention / Sustained Attention","Left DLPFC, ACC",        "L-DLPFC anodal tDCS + cognitive training (attention tasks)",                      "Level B (Westwood 2021)"],
        ["Working Memory Deficit",            "Left DLPFC, Parietal",   "L-DLPFC anodal tDCS + n-back/working memory training; TPS DLPFC investigational", "Level B (Westwood 2021)"],
        ["Response Inhibition / Impulsivity", "Right IFG, ACC",         "R-IFG cathodal tDCS (F4 cathode) + inhibitory training; TPS IFG investigational", "Moderate (Aron 2004; Lefaucheur 2017)"],
        ["Executive Dysfunction",             "Left DLPFC, ACC, SMA",   "L-DLPFC anodal tDCS + executive function training; TPS DLPFC investigational",    "Level B (Westwood 2021)"],
        ["Emotional Dysregulation",           "Left DLPFC, Amygdala",   "L-DLPFC tDCS + taVNS for limbic modulation; CES for baseline arousal",           "Moderate (Brunoni 2016)"],
        ["Motivation / Reward",               "OFC, Striatum, vmPFC",   "L-DLPFC tDCS + motivational interventions; taVNS for noradrenergic enhancement",  "Limited (Volkow 2009)"],
        ["Sleep Disturbance",                 "Frontal, Thalamus",      "CES primary (evening); taVNS; tDCS evening slow-wave protocol",                   "Moderate (Philip 2017)"],
        ["Anxiety Comorbidity",               "Right DLPFC, Amygdala",  "Bilateral DLPFC tDCS; taVNS primary; CES; address anxiety component explicitly",  "Moderate (Brunoni 2016)"],
        ["Hyperactivity / Arousal",           "Right IFG, SMA, ACC",    "R-IFG cathodal tDCS + mindfulness/behavioural inhibition training; taVNS",        "Moderate (Aron 2004)"],
    ],
    montage=[
        ["Inattentive ADHD",          "F3 anode + Fp2 cathode (L-DLPFC primary)",                                     "Cranial (global + targeted L-DLPFC)", "taVNS, CES (sleep)"],
        ["Combined ADHD",             "F3 anode + F4 cathode (bilateral asymmetric); 2 mA, 20\u201330 min",           "Cranial (global + targeted DLPFC/IFG)","taVNS; CES"],
        ["Hyperactive-Impulsive",     "F4 cathode + F3 anode (R-IFG cathodal emphasis); or F3 anode + shoulder cathode","Cranial (global + targeted R-IFG)", "taVNS primary; CES"],
        ["ADHD + Executive Function", "F3 anode + T3/T4 anodal (add parietal); Fz option",                           "Cranial (global + targeted DLPFC/PPC)","taVNS; CES (sleep)"],
        ["ADHD + Anxiety",            "Bilateral DLPFC (F3 + F4) or F3 anode + F4 cathode",                           "Cranial (global + targeted PFC)",       "taVNS primary; CES"],
        ["ADHD + Depression",         "F3 anode + Fp2 cathode (L-DLPFC anodal primary)",                              "Cranial (global + targeted L-DLPFC)",  "CES; taVNS"],
        ["ADHD + Sleep",              "F3 anode + Fp2 cathode; Fz evening slow-wave protocol",                         "Cranial (global + targeted)",           "CES primary (sleep); taVNS"],
        ["No response after 8\u201310 sessions","Reassess medication status; consider bilateral or cathodal IFG addition","Adjust parameters; TPS add-on",   "Review all adjuncts; CBT referral"],
    ],
    tdcs_protocols=[
        ["C1","Inattention / working memory (primary)","F3 anode",       "Fp2 / F4 / extracephalic",      "2 mA, 20\u201330 min, 5\u00d7/wk \u00d7 6\u201310 wks","Level B; WM improvement (Westwood 2021)"],
        ["C2","Response inhibition / impulsivity",      "F3 anode + F4 cathode","Extracephalic shoulder", "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Aron 2004; Lefaucheur 2017)"],
        ["C3","Combined ADHD \u2014 bilateral",         "F3 + F4 bilateral anode","Fp1 + Fp2 / shoulders","2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Westwood 2021)"],
        ["C4","Executive function / organisation",      "F3 anode + T3/T4 anode","F4 / extracephalic",    "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Brunoni 2016; Westwood 2021)"],
        ["C5","Emotional dysregulation",               "F3 anode",        "Fp2, extracephalic",           "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Brunoni 2016)"],
        ["C6","ADHD + anxiety overlay",                "F3 + F4 bilateral","Extracephalic shoulders",     "2 mA, 20\u201330 min, 5\u00d7/wk",                  "Moderate (Brunoni 2016)"],
        ["C7","Sleep disturbance",                     "Fz anode",        "Pz / extracephalic",           "1\u20132 mA, 20 min, evening",                       "Moderate (Philip 2017)"],
        ["C8","Maintenance block",                     "F3 anode",        "Fp2 / extracephalic",          "2 mA, 20\u201330 min, 3\u00d7/wk maintenance",      "Moderate (Westwood 2021)"],
    ],
    plato_protocols=[
        ["C1-PS","Inattention / WM",      "Frontal (F3 area)","F3","Right shoulder","1.6 mA, 20\u201330 min","5\u00d7/wk",         "Pair with attention/WM tasks"],
        ["C2-PS","Impulsivity",           "Frontal (F3 area)","F3","Right shoulder","1.6 mA, 20\u201330 min","5\u00d7/wk",         "Combine with inhibitory training"],
        ["C3-PS","Combined ADHD",         "Frontal (F3 area)","F3","Right shoulder","1.6 mA, 20\u201330 min","5\u00d7/wk",         "After HDCkit induction phase"],
        ["C4-PS","Executive function",    "Frontal (F3 area)","F3","Shoulder",       "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Pair with organisation tasks"],
        ["C5-PS","Emotional dysregulation","Frontal (F3 area)","F3","Shoulder",      "1.6 mA, 20\u201330 min","5\u00d7/wk",         "Pre-session taVNS recommended"],
        ["C6-PS","ADHD + anxiety",        "Frontal (F3 area)","F3","Right shoulder","1.6 mA, 20\u201330 min","5\u00d7/wk",         "Combine with CES and taVNS"],
        ["C7-PS","Sleep disturbance",     "Frontal (Fz area)","Fz","Shoulder",       "1.6 mA, 20 min",        "Evening",            "CES concurrent recommended"],
        ["C8-PS","Maintenance",           "Frontal (F3 area)","F3","Shoulder",       "1.6 mA, 20\u201330 min","3\u00d7/wk",         "After initial intensive block"],
    ],
    tps_protocols=[
        ["T1","Inattention / WM (primary)","L-DLPFC, R-DLPFC bilateral, ACC",    "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz; 10 sessions/2 wks","4,000 Tgt (DLPFC) + 2,000 PRE; total 6\u20138K","Investigational"],
        ["T2","Response inhibition",        "R-IFG (pars triangularis/opercularis), R-DLPFC","0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz","4,000 Tgt (IFG) + 2,000 Std; total 6\u20138K",  "Investigational"],
        ["T3","Executive dysfunction",      "L-DLPFC + ACC",                       "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",                 "4,000 Tgt + 2,000 PRE; total 6\u20138K",       "Investigational"],
        ["T4","Emotional dysregulation",    "L-DLPFC + ACC + OFC",                 "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",                 "4,000 Tgt + 2,000 Std; total 6\u20138K",       "Investigational"],
        ["T5","ADHD + anxiety/sleep",       "DLPFC + mPFC",                        "0.20\u20130.25 mJ/mm\u00b2; 1\u20136 Hz",                 "4,000 Tgt + 2,000 PRE; total 6\u20138K",       "Investigational"],
    ],
    ces_role=[
        ["Sleep disturbance",     "Targets delayed sleep phase and insomnia common in ADHD; FDA-cleared",                     "Evening before bed; 20\u201340 min; coordinate with sleep hygiene"],
        ["Anxiety comorbidity",   "Reduces comorbid anxiety in ADHD; FDA-cleared for anxiety",                                "Before tDCS session or evening; 20\u201340 min"],
        ["Emotional dysregulation","Stabilises baseline arousal and emotional reactivity",                                    "As needed; pre-session or morning; 20\u201330 min"],
        ["Motivation / anergia",  "May improve energy and motivation as adjunct",                                             "Morning; 20\u201330 min; avoid late afternoon"],
    ],
    tavns_role="taVNS augments noradrenergic tone via locus coeruleus, directly relevant to ADHD catecholaminergic pathophysiology; supports attentional regulation and reduces emotional/autonomic dysregulation.",
    combinations=[
        ("1) Inattentive ADHD", [
            ["tDCS + Cognitive Training","L-DLPFC anodal tDCS + attention/WM computerised training; most supported combination (Westwood 2021)","tDCS before/during cognitive tasks","Inattention, WM deficit, task-completion failures"],
            ["taVNS + tDCS","taVNS priming enhances noradrenergic prefrontal tone before tDCS (Hein 2021; Aston-Jones 2005)","taVNS 20 min before tDCS","Attentional fatigue, motivation dysregulation"],
            ["CES + Standard Care","CES for sleep and baseline arousal stability; supports daytime attention (Philip 2017)","Evening (sleep) and morning (energy) as prescribed","Delayed sleep phase, fatigue-driven inattention"],
        ]),
        ("2) Combined ADHD", [
            ["tDCS + Behavioural Training","Bilateral DLPFC tDCS + behavioural ADHD training; addresses both attention and impulsivity (Westwood 2021; Lefaucheur 2017)","tDCS before/during training session","Inattention + impulsivity + executive dysfunction"],
            ["taVNS + tDCS","Dual catecholaminergic and cortical modulation; taVNS primes noradrenergic system (Hein 2021)","taVNS before tDCS","Emotional dysregulation, impulsivity, arousal variability"],
            ["CES + Standard Care","CES for sleep, anxiety, and arousal stabilisation (Philip 2017)","Daily as prescribed","Sleep disturbance, anxiety comorbidity, emotional dysregulation"],
        ]),
        ("3) ADHD + Executive Dysfunction", [
            ["tDCS + Executive Training","L-DLPFC anodal tDCS + structured executive function training (planning, WM, flexibility) (Westwood 2021)","tDCS before executive training","Planning, organisation, time management failures"],
            ["taVNS + Cognitive Training","taVNS + cognitive flexibility tasks; LC-NE modulation augments prefrontal plasticity (Hein 2021)","taVNS before cognitive training","Cognitive flexibility, task-switching, WM deficits"],
            ["CES + Standard Care","CES for sleep; indirect improvement in executive performance through better sleep (Philip 2017)","Evening","Executive dysfunction with sleep disorder"],
        ]),
        ("4) ADHD + Anxiety", [
            ["tDCS + CBT","Bilateral DLPFC tDCS + CBT; addresses both ADHD executive deficits and anxiety cognitive distortions (Brunoni 2016)","tDCS before CBT session","Inattention + worry + tension"],
            ["taVNS + tDCS","taVNS reduces physiological anxiety before tDCS; critical when anxiety limits tDCS engagement (Hein 2021)","taVNS 20\u201330 min before tDCS","Autonomic hyperarousal, physiological anxiety"],
            ["CES + Standard Care","CES primary for anxiety component; FDA-cleared (Philip 2017)","Daily as prescribed","ADHD with anxiety, sleep disturbance, somatic tension"],
        ]),
        ("5) ADHD + Sleep Disorder", [
            ["tDCS + Sleep Hygiene","DLPFC tDCS + CBT-I or sleep hygiene programme; targets arousal regulation (Westwood 2021)","tDCS morning; evening slow-wave protocol if used","ADHD with delayed sleep phase, insomnia"],
            ["taVNS + CES","Dual adjunct for sleep: taVNS autonomic downshift + CES sleep facilitation (Hein 2021; Philip 2017)","taVNS + CES at bedtime","Sleep-onset difficulties, nocturnal hyperarousal"],
            ["CES Primary + tDCS","CES as primary sleep modality with morning tDCS for daytime attention (Philip 2017)","CES evening; tDCS morning","ADHD where sleep is most impairing feature"],
        ]),
        ("6) ADHD + Emotional Dysregulation", [
            ["tDCS + DBT / Mindfulness","L-DLPFC tDCS + DBT skills or mindfulness; enhances prefrontal regulation of limbic reactivity (Brunoni 2016)","tDCS before therapy session","Emotional lability, frustration, impulsive reactions"],
            ["taVNS + tDCS","taVNS modulates autonomic and limbic reactivity; additive with prefrontal tDCS (Hein 2021)","taVNS before tDCS","Autonomic arousal with emotional dysregulation"],
            ["CES + Standard Care","CES stabilises baseline arousal; reduces emotional reactivity threshold (Philip 2017)","As needed; morning or pre-session","Emotional dysregulation with anxiety and sleep disturbance"],
        ]),
    ],
    combination_summary=[
        ["Inattentive ADHD",      "tDCS + Cognitive Training",   "L-DLPFC anodal tDCS + attention/WM training (Westwood 2021)",                        "tDCS before/during tasks","Inattention, WM deficit",           "Level B"],
        ["Combined ADHD",         "tDCS + Behavioural Training", "Bilateral DLPFC tDCS + ADHD behavioural training (Westwood 2021; Lefaucheur 2017)",   "tDCS before training",    "Inattention + impulsivity",          "Moderate"],
        ["ADHD + EF",             "tDCS + Executive Training",   "L-DLPFC tDCS + structured EF training; planning and WM (Westwood 2021)",              "tDCS before EF training", "Planning, organisation, WM",        "Level B"],
        ["ADHD + Anxiety",        "tDCS + CBT",                  "Bilateral DLPFC tDCS + CBT; addresses ADHD + anxiety (Brunoni 2016)",                  "tDCS before CBT",         "Inattention + worry + tension",      "Moderate"],
        ["ADHD + Sleep",          "taVNS + CES",                 "Dual adjunct for sleep and autonomic stabilisation (Hein 2021; Philip 2017)",          "taVNS + CES at bedtime",  "Delayed sleep phase, insomnia",      "Emerging"],
        ["ADHD + Emotional Dysreg","tDCS + DBT / Mindfulness",   "L-DLPFC tDCS + DBT/mindfulness; prefrontal limbic regulation (Brunoni 2016)",          "tDCS before therapy",     "Emotional lability, impulsivity",    "Moderate"],
    ],
    outcomes=[
        ["CAARS (Self-Report)",   "ADHD symptom severity",                 "Baseline, weeks 4, 8, 12",     "T-score \u226565 clinically significant; track change from baseline"],
        ["BRIEF-2 (Adult)",       "Executive function (self/observer)",    "Baseline, months 1, 3",        "T-score \u226565 indicates EF impairment; track improvement"],
        ["MoCA",                  "Global cognition screening",            "Baseline, month 3",            "Score <26 cognitive impairment"],
        ["PHQ-9",                 "Comorbid depressive symptoms",          "Baseline, weeks 4, 8, 12",     "\u226510 moderate; \u226515 severe"],
        ["GAD-7",                 "Comorbid anxiety",                      "Baseline, weeks 4, 8, 12",     "\u226510 moderate; \u226515 severe"],
        ["ISI",                   "Insomnia severity",                     "Baseline, weeks 4, 8, 12",     "Score \u226715 moderate insomnia"],
        ["Conners CPT-3",         "Sustained attention (objective)",       "Baseline, month 3",            "T-score >65 on commission/omission errors; track change"],
        ["CGI-S / CGI-I",         "Clinical Global Impression",            "Baseline, weeks 4, 8, 12",     "CGI-I \u22642 = much improved"],
        ["SOZO PRS",              "NIBS-specific functional outcome",      "Baseline, weeks 2, 4, 8, 12", "Proprietary; composite attention/EF/emotional/sleep domains"],
    ],
    outcomes_abbrev=["CAARS", "BRIEF-2", "MoCA", "PHQ-9", "SOZO PRS"],
)
'''

with open(str(Path(__file__).resolve().parent / "generate_fellow_protocols.py"), "a", encoding="utf-8") as f:
    f.write(BLOCK)
print("MDD + GAD + ADHD appended OK")
