// SOZO FNON Clinical Protocol — Long COVID / Post-COVID Neurological Syndrome
// Document A — Partners Tier

module.exports = {
  conditionFull: "Long COVID / Post-COVID Neurological Syndrome",
  conditionShort: "Long COVID",
  conditionSlug: "long_covid",
  documentNumber: "SOZO-FNON-LCOVID-001",

  offLabelCoverText:
    "All non-invasive brain stimulation (NIBS) applications described in this protocol for Long COVID / Post-COVID Neurological Syndrome represent off-label use of CE-marked and FDA-cleared devices. Long COVID is a recently recognised multi-system condition (WHO 2021 definition: symptoms persisting or new onset >12 weeks after acute COVID-19 infection not explained by an alternative diagnosis) with no approved specific NIBS indication. The Newronika HDCkit, PlatoScience PlatoWork, NEUROLITH® TPS, Soterix Medical taVNS, and Alpha-Stim AID are applied for Long COVID FNON based on their documented mechanisms of action in comparable neurological and neuroimmune conditions (ME/CFS-like, post-viral fatigue, neuroinflammation, dysautonomia). All protocols must be delivered under clinical supervision with ongoing monitoring, given the evolving and heterogeneous nature of Long COVID pathophysiology. Evidence is preliminary (Level C); patients must be fully informed of experimental status.",

  offLabelTable: [
    ["Device", "Cleared/Approved Indication", "Long COVID Off-Label Application", "Evidence Level"],
    ["Newronika HDCkit / PlatoWork", "Neurological rehabilitation (CE)", "Cognitive fog, fatigue, executive dysfunction, depression", "Level C"],
    ["NEUROLITH® TPS", "Alzheimer's disease (CE)", "Prefrontal cognitive network, hippocampal memory, fatigue circuit", "Level C"],
    ["Soterix taVNS / Alpha-Stim AID", "Epilepsy/anxiety/pain (CE/FDA)", "Autonomic dysregulation (POTS), neuroinflammation, fatigue, anxiety", "Level C — most supported modality"],
  ],

  inclusionCriteria: [
    ["Confirmed Long COVID diagnosis per WHO 2021/NICE NG188 criteria: symptoms persisting >12 weeks after acute COVID-19 not explained by alternative diagnosis", "Positive COVID-19 PCR, antigen, or serology confirming prior infection", "Age 18–70 years", "Presenting symptom(s) amenable to FNON: cognitive impairment ('brain fog'), fatigue, autonomic symptoms, anxiety, depression, post-exertional malaise (PEM)"],
    ["Stable symptom trajectory for ≥4 weeks (no acute rapid deterioration)", "Neuropsychological assessment at baseline: MoCA, SDMT, forward/backward digit span, Trail Making Test", "Fatigue Severity Scale (FSS) ≥4 or Modified Fatigue Impact Scale (MFIS) elevated", "Heart rate variability (HRV) or standing tachycardia assessment if autonomic symptoms present"],
    ["Brain MRI or exclusion of structural pathology (stroke, space-occupying lesion)", "COVID-19 multisystem complications excluded or managed (myocarditis, PE, renal sequelae)", "Stable vaccination status documented", "No active SARS-CoV-2 infection at time of protocol commencement"],
    ["Cardiological clearance if post-COVID cardiovascular symptoms (palpitations, chest pain, orthostatic intolerance)", "Written informed consent with off-label disclosure and experimental nature of FNON for Long COVID", "Baseline POTS/dysautonomia assessment if relevant (10-min standing test, NASA lean test)", "Psychiatrist or physician oversight confirmed if psychiatric comorbidity"],
    ["Patient education on Post-Exertional Malaise (PEM) and energy envelope management completed before NIBS", "No acute concurrent infections", "Baseline QoL measure (SF-36 or WHOQOL-BREF) completed", "Agreed paced activity plan with clinical team to prevent PEM during protocol"],
    ["Cardiopulmonary function cleared for seated protocol (SpO2 stable, no severe breathlessness at rest)", "Rheumatology/immunology assessment for autoimmune overlap if clinically indicated", "Sleep assessment (PSQI or actigraphy) if sleep disturbance prominent", "Neurological examination to exclude focal deficits requiring separate management"],
    ["Stable medications for ≥4 weeks", "MDT involvement confirmed (GP/internist, neuropsychologist, physiotherapist specialised in Long COVID, OT)", "Goals of treatment documented: functional return goals (work, daily activities)", "No planned travel or major life event disrupting protocol schedule"],
  ],

  exclusionCriteria: [
    ["Active SARS-CoV-2 infection (COVID-19 positive PCR/antigen within 2 weeks)", "Severe post-COVID cardiac complication: myocarditis, significant arrhythmia, reduced EF <40%", "Intracranial metal implants (DBS, cochlear implants, ferromagnetic clips)", "Cardiac pacemaker or implantable defibrillator"],
    ["Severe post-COVID pulmonary fibrosis requiring supplemental oxygen", "Active post-COVID autoimmune syndrome (MIS-A — multisystem inflammatory syndrome in adults) — immunological management priority", "Pregnancy or breastfeeding", "Active malignancy, recent chemotherapy, or significant immunosuppression"],
    ["Uncontrolled seizure disorder (COVID-19 CNS complications can include new-onset seizures)", "Severe psychiatric disorder uncontrolled (active psychosis, mania)", "Active suicidal ideation", "Severe dysautonomia with recurrent syncope unresponsive to initial management"],
    ["Severe PEM triggered by minimal activity: bed-bound for >50% of day (protocol not safe without energy envelope management established)", "Active deep vein thrombosis or pulmonary embolism — COVID-associated hypercoagulability", "Current participation in conflicting Long COVID NIBS trial", "Unable to provide informed consent"],
    ["EDSS >5 (if significant neurological sequelae from acute COVID-19 requiring separate neurorehabilitation protocol)", "Severe autonomic neuropathy documented on autonomic testing", "Recent head trauma or new structural brain lesion on MRI", "Known hypersensitivity to conductive gel or electrode materials"],
    ["Severe ME/CFS-like presentation with energy envelope so narrow that any NIBS increases PEM risk (clinical judgement: energy envelope <3 hours/day)", "Poorly controlled hypertension (>180/110 mmHg at rest)", "Active infection other than COVID-19 (concurrent URI, UTI, etc.) — defer until resolved", "Severe anxiety or panic disorder preventing any electrode application (after accommodations attempted)"],
    ["Withdrawal from medications that alter cortical excitability (opioids, benzodiazepines, AEDs — increased seizure risk period)", "Severe cognitive impairment precluding informed consent (rare but possible with severe acute COVID-19 neurological complications)", "Botulinum toxin injection to head/neck within 3 months", "Deep cervical vagus nerve stimulator in place"],
    ["Open skin wounds or infections at electrode or transducer sites", "Clinician assessment: clinical instability, too unwell for protocol at this time", "Active flare of post-COVID inflammatory arthritis or vasculitis requiring immunosuppression", "Renal failure (eGFR <30) as may alter excitability responses to stimulation"],
  ],

  conditionsRequiringDiscussion: [
    ["Condition", "Clinical Consideration", "Recommended Action", "Protocol Adjustment"],
    ["POTS / Orthostatic intolerance", "Postural tachycardia on standing common in Long COVID; may be exacerbated by sitting upright during tDCS", "NASA lean test baseline; cardiological review; consider semi-reclined position; monitor HR throughout", "taVNS primary (lying down protocol); CES; limit tDCS to supine/semi-reclined; postpone if resting HR >100"],
    ["Post-Exertional Malaise (PEM)", "Any physical or cognitive exertion may trigger 24–72 hour symptom worsening; NIBS cognitive demand may trigger PEM", "Energy envelope assessment; very gradual titration; short sessions (10–15 min) initially; PEM diary monitoring", "Start with taVNS + CES only (5–10 min); add tDCS only after 3–4 sessions tolerance confirmed; avoid intensive TPS during acute PEM"],
    ["Severe COVID-19 cognitive fog", "Frontal lobe and hippocampal dysfunction documented on neuroimaging; SDMT significantly impaired", "Full neuropsychological baseline; coordinate with cognitive rehabilitation service", "DLPFC tDCS + TPS hippocampal primary targets; cognitive rehabilitation concurrent"],
    ["Post-COVID autoimmune small fibre neuropathy", "Small fibre neuropathy (skin biopsy confirmed or clinically suspected) — allodynia, burning pain, autonomic features", "Neurology review; consider pain protocol elements (M1 anodal tDCS); document neuropathic symptoms", "Add M1 anodal pain protocol; taVNS anti-inflammatory primary; cathodal S1 if allodynia present"],
    ["Long COVID PTSD features", "Acute COVID-19 hospitalisation, ICU, or severe illness can produce PTSD features (hyperarousal, intrusions, avoidance)", "PHQ-PTSD screening; PTSD protocol elements if indicated; trauma-informed care approach", "Add taVNS for hyperarousal; coordinate PTSD-informed psychological support; see PTSD FNON protocol guidance"],
    ["Mast Cell Activation Syndrome (MCAS) overlap", "MCAS increasingly documented in Long COVID; histamine-driven symptoms may fluctuate; allergy to electrode materials possible", "Dermatology/allergy review; alternative electrode materials if standard not tolerated; MCAS management concurrent", "Monitor for skin reactions at electrode sites; use hypoallergenic gel alternatives; shorter session duration"],
    ["Post-COVID thyroid dysfunction", "Subacute thyroiditis documented post COVID-19; hypothyroidism affects cognition and fatigue", "Thyroid function tests at baseline and 3 months; endocrinology review if abnormal", "Treat thyroid dysfunction first; FNON fatigue and cognitive protocols may be more effective after euthyroid state"],
    ["Significant post-COVID depression", "Depression prevalence 30–40% in Long COVID; neuroinflammatory and psychosocial origins; overlaps with brain fog", "PHQ-9 baseline; psychiatric review if moderate-severe; integrate depression protocol elements", "Anodal F3 tDCS + taVNS anti-inflammatory; coordinate psychological support; see depression FNON elements"],
    ["Long COVID in healthcare workers", "Significant occupational impact; return-to-work pressure may push beyond energy envelope; moral injury component", "Occupational health involvement; paced return-to-work planning; acknowledge HCW-specific stress", "Goal-setting includes occupational function; assess workplace exposure risk; cognitive workload assessment"],
  ],

  overviewParagraph:
    "Long COVID (Post-COVID Condition, Post-Acute Sequelae of SARS-CoV-2 — PASC) is defined by the World Health Organisation as the condition occurring in individuals with a history of probable or confirmed SARS-CoV-2 infection, with symptoms arising at or following COVID-19 diagnosis, lasting for >12 weeks, and not explained by an alternative diagnosis. Affecting an estimated 65 million people globally (Davis 2023), Long COVID encompasses a heterogeneous constellation of neurological, cardiovascular, autonomic, respiratory, and musculoskeletal symptoms, with the neurological features — cognitive impairment ('brain fog'), fatigue, headache, autonomic dysregulation (POTS), sleep disturbance, anxiety, and depression — representing the most disabling and persistent manifestations. The neurological phenotype of Long COVID shares striking overlap with Myalgic Encephalomyelitis/Chronic Fatigue Syndrome (ME/CFS), suggesting shared pathophysiology: neuroinflammation, microglial activation, blood-brain barrier disruption, mitochondrial dysfunction, and autonomic nervous system dysregulation. The SOZO FNON protocol for Long COVID targets these network-level neurological consequences through the most evidence-supported NIBS mechanisms available: taVNS for autonomic dysregulation and neuroinflammation (the most mechanistically justified modality), tDCS for cognitive network upregulation, TPS for hippocampal and prefrontal network targeting, and CES for tonic autonomic calming. All protocols incorporate Post-Exertional Malaise (PEM) safe principles — gradual titration, energy envelope monitoring, and session-length management — as PEM is a defining feature of Long COVID neurological phenotypes.",

  fnonNetworkParagraph:
    "The FNON framework for Long COVID centres on the 'Neuroinflammatory Network Disruption' model: SARS-CoV-2 produces multifocal CNS network disruption through direct viral neuroinvasion, neuroinflammatory cascades (microglial activation, cytokine storm sequelae, persistent neuroinflammation), endothelial dysfunction and microthrombi disrupting cerebral perfusion, and mitochondrial dysfunction impairing ATP-dependent neural function. The Default Mode Network (DMN) and Central Executive Network (CEN) show the most consistent abnormalities in Long COVID neuroimaging: hypometabolism on FDG-PET (particularly frontal and parietal DMN/CEN nodes) analogous to Alzheimer's disease network patterns, and reduced functional connectivity on resting-state fMRI. The Salience Network (SN) is hyperactivated — analogous to ME/CFS — driving the central fatigue amplification, effort intolerance, and post-exertional malaise signature. The autonomic nervous system, modulated by the SN and limbic network, shows reduced heart rate variability and sympathetic over-activation underlying POTS and orthostatic intolerance. taVNS is the most mechanistically powerful FNON modality for Long COVID: the NTS-cholinergic anti-inflammatory pathway reduces neuroinflammation (TNF-α, IL-6, IL-1β), the NTS-LC pathway restores noradrenergic tone, and vagal parasympathetic enhancement directly addresses the sympathovagal imbalance driving POTS. tDCS targets hypofrontal CEN/DMN nodes to address brain fog, and TPS offers deep targeting of hippocampal-prefrontal memory and executive networks.",

  networkDisorderParagraphs: [
    {
      network: "Default Mode Network (DMN)",
      paragraph:
        "The Default Mode Network (DMN) in Long COVID shows hypometabolism on FDG-PET imaging — with bilateral parietal, posterior cingulate, and medial prefrontal cortex reduced glucose utilisation — in a pattern similar to that seen in early Alzheimer's disease. This DMN hypometabolism correlates with subjective brain fog severity and objective neuropsychological impairment in Long COVID cohorts. Mechanistically, DMN hypometabolism may reflect mitochondrial dysfunction (impaired oxidative phosphorylation in neurons), microglial activation consuming glucose, and blood-brain barrier disruption reducing cerebral glucose delivery. DMN default-mode processing failures produce the characteristic brain fog symptoms: inability to maintain self-directed thought, cognitive fatigue, difficulty with planning, and reduced mental clarity even at rest. FNON approach: CES to normalise DMN oscillatory dynamics (particularly alpha-band rhythm); cathodal posterior midline to reduce DMN hyperreactivity that paradoxically persists in some sub-phenotypes; taVNS anti-inflammatory pathway to reduce microglial burden on DMN metabolism."
    },
    {
      network: "Central Executive Network (CEN)",
      paragraph:
        "The Central Executive Network (CEN) in Long COVID — anchored in the bilateral DLPFC and posterior parietal cortex — shows reduced activation on task-based fMRI and hypometabolism on FDG-PET in the prefrontal cortex, producing the executive function and working memory components of brain fog. Patients report difficulty with multitasking, planning, word-finding, concentration, and working memory — all CEN-dependent functions. The DLPFC hypometabolism in Long COVID is one of the most consistently replicated neuroimaging findings (Guedj 2021; Hugon 2022), and represents the primary FNON tDCS target. Anodal tDCS of the left and right DLPFC (F3/F4) upregulates CEN excitability, counteracting the metabolic depression and potentially stimulating mitochondrial biogenesis in prefrontal neurons. Anodal tDCS has precedent in post-viral fatigue and ME/CFS-adjacent conditions for improving cognitive processing speed."
    },
    {
      network: "Salience Network (SN)",
      paragraph:
        "The Salience Network (SN) in Long COVID — centred on the anterior insula and anterior cingulate cortex — shows pathological upregulation analogous to its role in ME/CFS central fatigue and fibromyalgia. The SN hyperactivation drives two of the most disabling Long COVID symptoms: (1) central fatigue amplification — the SN generates exaggerated effort signals, making minimal exertion feel overwhelming; and (2) Post-Exertional Malaise (PEM) — the SN-mediated effort signal drives a cascade of maladaptive autonomic and neuroimune responses to exertion that produce the characteristic 24–72 hour symptom worsening. taVNS modulates the SN via NTS projections to the insula and ACC, reducing the hyperactive effort signal. Critically, taVNS does so without generating significant cognitive or physical demand — making it the safest first-line FNON modality in PEM-sensitive Long COVID patients. The taVNS SN modulation is a prerequisite before any cognitively-demanding tDCS or TPS sessions."
    },
    {
      network: "Sensorimotor Network (SMN)",
      paragraph:
        "The Sensorimotor Network (SMN) in Long COVID is impacted through multiple mechanisms: post-COVID myopathy and peripheral neuropathy disrupt proprioceptive input; central fatigue reduces corticospinal drive; microglial activation in motor cortex (documented in post-mortem COVID-19 studies) impairs motor circuit efficiency. While the SMN is less severely affected in Long COVID than in stroke or MS, motor fatigue — the phenomenon where motor performance deteriorates rapidly with repetition beyond what peripheral muscle status would predict — reflects impaired SMN efficiency. Post-COVID dyspraxia and reduced upper limb coordination are reported in some patients. SMN tDCS (anodal M1) paired with paced physiotherapy can address this motor fatigue component, though energy envelope management is essential to prevent PEM."
    },
    {
      network: "Limbic Network",
      paragraph:
        "The Limbic Network in Long COVID is disrupted by direct COVID-19 neuroinvasion (SARS-CoV-2 ACE2 receptors are highly expressed in limbic regions including olfactory bulb, piriform cortex, hippocampus, and amygdala), neuroinflammatory limbic pathology, and psychological sequelae of acute COVID-19 illness. Hippocampal damage — evidenced by MRI studies showing reduced hippocampal volume in post-COVID patients and pathological tau changes in animal models — contributes to episodic memory impairment and 'brain fog' memory complaints. Amygdala hyperactivation contributes to the high prevalence of anxiety (30–50%) and PTSD features in Long COVID. Anosmia (loss of smell) reflects olfactory bulb pathology with direct limbic connections — persistent anosmia in Long COVID is a proximal indicator of limbic neurological involvement. taVNS anti-inflammatory NTS pathway and TPS hippocampal targeting address the limbic network substrate."
    },
    {
      network: "Attention Network",
      paragraph:
        "The Attention Network in Long COVID shows impairment manifesting as difficulty sustaining attention, distractibility, and attentional fatigue — major components of patient-reported brain fog. COVID-19 affects noradrenergic locus coeruleus (LC) neurons (ACE2 receptor expression confirmed in LC), which are the primary neuromodulatory source for sustained attention, arousal, and cognitive vigilance. Reduced LC-NE tone in Long COVID produces attentional failures analogous to those seen in conditions of LC dysfunction (ADHD, TBI, normal ageing). Right hemisphere parietal and frontal attention network nodes show reduced functional connectivity on resting-state fMRI. taVNS directly targets the LC via the NTS-LC pathway, restoring noradrenergic tone and improving attention network function — mechanistically the clearest and most direct FNON attention mechanism in Long COVID. Anodal right DLPFC tDCS (F4) further supports the attention network."
    },
  ],

  pathophysiologyText:
    "Long COVID neurological pathophysiology involves at least five distinct but interacting mechanisms, supported by emerging evidence from neuroimaging, cerebrospinal fluid analysis, post-mortem studies, and animal models: (1) Neuroinflammation — persistent microglial and astrocyte activation months after acute infection, producing elevated CSF cytokines (IL-6, IL-8, TNF-α, interferon-β), neuronal damage markers (NfL — neurofilament light chain), and inflammatory white matter changes on MRI; (2) Blood-brain barrier (BBB) disruption — SARS-CoV-2-induced endothelialitis damages BBB tight junctions, allowing inflammatory mediators, antibodies, and potentially viral antigens to enter the CNS; (3) Cerebrovascular microthrombi and hypoperfusion — COVID-19-associated coagulopathy produces microvascular thrombosis in cerebral vessels, confirmed in post-mortem COVID-19 brain studies, producing chronic cerebral hypoperfusion that accounts for FDG-PET hypometabolism; (4) Direct viral neuroinvasion — SARS-CoV-2 enters the CNS via olfactory bulb, brainstem, and choroid plexus ACE2 receptor-mediated routes, with viral antigens or RNA detected in brain parenchyma; (5) Autonomic nervous system dysregulation — autoantibodies to adrenergic receptors and muscarinic receptors, vagus nerve damage, and hypothalamic-pituitary axis disruption produce the POTS, dysautonomia, and ME/CFS-like phenotype. Mitochondrial dysfunction — impaired Complex I activity, reduced ATP production in neurons — may underlie both the fatigue and cognitive impairment through energy metabolism failure. The FNON therapeutic rationale: taVNS anti-inflammatory (mechanism 1, 3), autonomic restoration (mechanism 5); tDCS network upregulation (mechanisms 1, 3, 4 sequelae); TPS hippocampal for mechanism 4 sequelae.",

  cardinalSymptoms: [
    ["Domain", "Primary Symptoms", "Network Basis", "FNON Target"],
    ["Brain Fog / Cognitive Impairment", "Working memory impairment; slowed processing speed; word-finding difficulty; concentration failure; executive dysfunction; feels 'underwater' mentally", "CEN DLPFC hypometabolism; DMN-CEN disconnection; LC-NE tone reduction; cerebral hypoperfusion", "Anodal DLPFC tDCS (F3/F4); TPS prefrontal; CES cognitive protocol; taVNS NTS-LC NE restoration"],
    ["Fatigue / Post-Exertional Malaise (PEM)", "Extreme fatigue disproportionate to exertion; PEM: crash 24–72h post-exertion; unrefreshing sleep; cognitive PEM as prominent as physical PEM", "SN hyperactivation; mitochondrial dysfunction; CEN hypofrontality; autonomic sympathovagal imbalance", "taVNS (primary — SN + autonomic); CES tonic ANS; cathodal preSMA (Cz); energy envelope essential"],
    ["Autonomic Dysregulation (POTS)", "Orthostatic tachycardia on standing; palpitations; light-headedness; pre-syncope; diaphoresis; heat intolerance", "SN-autonomic network hyperactivation; vagal tone reduction; sympathovagal imbalance; reduced HRV; autoantibodies to adrenergic receptors", "taVNS primary (vagal parasympathetic restoration; HRV increase); CES ANS calming; semi-reclined protocol"],
    ["Sleep Disturbance", "Non-restorative sleep; sleep-onset insomnia; hypersomnia; vivid dreams; circadian rhythm disruption", "Hypothalamic-sleep circuit disruption; LC-NE dysregulation; SN hyperarousal at night; melatonin pathway disruption", "CES pre-sleep protocol (primary); taVNS circadian; cathodal Cz evening"],
    ["Anxiety / Psychological Distress", "Anxiety (30–50%); PTSD features if ICU/hospitalised; health anxiety; depression (30–40%); social withdrawal", "Amygdala hyperactivation; limbic-prefrontal disconnection; neuroinflammatory depression; COVID-related psychosocial stress", "Anodal F3 or F4 tDCS; taVNS bilateral anti-inflammatory + anxiolytic; CES; psychological support"],
    ["Headache / Pain", "Persistent headache (new or changed pattern post-COVID); neuropathic pain; myalgia; arthralgia; small fibre neuropathy features", "Trigeminovascular sensitisation; thalamic-cortical pain circuit dysregulation; SN sensitisation; small fibre nerve damage", "M1 anodal tDCS (contralateral to dominant pain); taVNS NTS-PAG analgesic pathway; TPS S1/pain network"],
    ["Memory Impairment", "Episodic memory encoding failure; forgetting recent conversations; difficulty learning new information; semantic memory (word-finding)", "Hippocampal pathology (ACE2 neuroinvasion); reduced hippocampal volume; entorhinal-hippocampal network disconnection", "TPS hippocampal (primary deep target); anodal T3/P3 tDCS; taVNS BDNF induction"],
    ["Anosmia / Dysgeusia", "Persistent smell loss (>12 weeks); parosmia (smell distortion); taste changes; olfactory system limbic connection", "Olfactory bulb inflammation/damage; piriform cortex disruption; orbitofrontal olfactory network", "taVNS indirect olfactory bulb-vagal connections; limited direct NIBS for anosmia; olfactory training concurrent"],
    ["Breathlessness / Deconditioning", "Dyspnoea out of proportion to pulmonary function; deconditioning; post-COVID cardiovascular impairment; autonomic breathlessness perception", "Interoceptive-SN dysregulation of respiratory awareness; autonomic; deconditioning physiology", "taVNS (autonomic/interoceptive); SN modulation; paced rehabilitation concurrent (not before POTS/cardiac cleared)"],
  ],

  standardGuidelinesText: [
    "Long COVID management follows NICE guideline NG188 (2021, updated 2023), NHS England Long COVID Service guidance, and emerging WHO Long COVID management guidance. No disease-specific approved treatments exist for Long COVID. Management is symptom-directed and multidisciplinary, emphasising energy management (pacing), rehabilitation, and treatment of specific comorbidities.",
    "Post-Exertional Malaise (PEM) management is the most critical intervention in Long COVID: graded exercise therapy (GET) is contraindicated in patients with PEM (NICE NG188 updated 2021 — removed GET for ME/CFS-like Long COVID). Energy management, pacing based on heart rate and energy envelope (typically <50% anaerobic threshold), and activity diaries are recommended first-line. Cognitive rehabilitation for brain fog includes pacing cognitive activity similarly to physical activity.",
    "POTS / Dysautonomia management: increased fluid and sodium intake (2–3 L/day fluid, 10 g/day sodium), compression garments, head-of-bed elevation, and pharmacological management (fludrocortisone, beta-blockers, midodrine, ivabradine) per cardiology guidance. Exercise rehabilitation following established POTS protocol (recumbent exercise first, progressing to upright) with careful HR monitoring.",
    "Cognitive rehabilitation: computerised cognitive training, occupational therapy for cognitive compensation strategies, speech and language therapy for word-finding difficulties, and neuropsychological support. No pharmacological cognitive enhancement has Level A evidence specifically for Long COVID brain fog.",
    "Depression and anxiety management: SSRIs (sertraline first-line) with consideration of noradrenergic/anti-inflammatory mechanisms; SSRIs may have additional benefit for Long COVID through anti-inflammatory effects. CBT adapted for Long COVID (accepts illness, focuses on management rather than recovery expectations) has emerging evidence. Low-dose naltrexone (LDN) has theoretical anti-inflammatory mechanism and is investigated in trials.",
    "Sleep management: sleep hygiene; cognitive behavioural therapy for insomnia (CBT-I); melatonin; short-term low-dose amitriptyline or trazodone for non-restorative sleep. Avoid hypnotic benzodiazepines (reduce neuroplasticity, worsen cognitive function in Long COVID brain fog).",
    "NIBS for Long COVID: No NIBS modality is currently in national guidelines for Long COVID. Emerging research: taVNS has the strongest rationale (anti-inflammatory, autonomic, NTS direct targets) with pilot study data. One published controlled study (Hanna 2022, n=20) showed taVNS improved fatigue and autonomic symptoms in Long COVID. tDCS for Long COVID brain fog is the subject of active clinical trials (NCT05044910; others). FNON represents an evidence-informed experimental clinical protocol requiring full participant disclosure.",
  ],

  fnonFrameworkParagraph:
    "The SOZO FNON framework for Long COVID is the 'Neuroinflammatory Recovery and Network Restoration' (NRNR) model: Long COVID produces a state of persistent neuroinflammation and network metabolic depression that impairs the brain's capacity for spontaneous recovery. FNON aims to (1) break the neuroinflammatory cycle through taVNS cholinergic anti-inflammatory pathway activation; (2) restore network metabolic function through tDCS-induced upregulation of hypofrontal CEN/DMN nodes; (3) address autonomic sympathovagal imbalance through taVNS vagal parasympathetic enhancement; and (4) support hippocampal neuroplasticity through TPS targeting and BDNF induction. The S-O-Z-O sequence for Long COVID is: Stabilise (taVNS 15–20 min — anti-inflammatory + autonomic regulation, mandatory first step); Optimise CEN excitability (DLPFC tDCS, 15–20 min, PEM-safe session length); Zone hippocampal and prefrontal deep targeting with TPS (alternate sessions); Outcome consolidation with CES during quiet rest (PEM-safe, minimal demand). PEM safety is non-negotiable: the protocol explicitly titrates session length, intensity, and frequency based on patient energy envelope — no 'push through fatigue' approach. Sessions should be followed by rest, not activity. The taVNS anti-inflammatory action is the cornerstone of the Long COVID FNON protocol because it addresses the underlying neuroinflammatory mechanism rather than only its network-level consequences.",

  keyBrainRegions: [
    ["Brain Region", "Function", "Long COVID Pathology", "FNON Intervention"],
    ["Dorsolateral Prefrontal Cortex (DLPFC)", "Working memory, executive control, processing speed, cognitive flexibility, top-down attention", "FDG-PET hypometabolism; reduced task-based activation; COVID-associated neuroinflammatory hypofrontality; brain fog substrate", "Anodal tDCS F3/F4 (bilateral 1.0 mA or unilateral 1.5–2.0 mA); TPS prefrontal; PEM-safe 15 min duration"],
    ["Medial Prefrontal Cortex (mPFC)", "DMN hub; planning; self-referential processing; motivation; emotional regulation; DMN-task interaction", "Hypometabolism on PET; reduced mPFC-PCC connectivity; contributes to motivational and DMN impairment in brain fog", "Anodal Fz (mPFC, moderate intensity); TPS mPFC neuro-navigation; CES DMN normalisation"],
    ["Hippocampus", "Episodic memory encoding; spatial navigation; pattern completion; memory consolidation; neurogenesis site", "SARS-CoV-2 direct invasion via ACE2 receptors; reduced volume on MRI in post-COVID; memory complaints; tau pathology animal models", "TPS hippocampal (primary deep target, 4–5 cm depth); taVNS BDNF induction via NTS-hippocampal projection"],
    ["Anterior Cingulate Cortex (ACC)", "Effort monitoring; conflict detection; pain processing; autonomic regulation; fatigue signal generation; SN hub", "SN hyperactivation at ACC; ACC-mediated PEM amplification; effort signal dysregulation in Long COVID fatigue", "taVNS (NTS→ACC modulation — primary); cathodal Fz or Cz (reduce ACC/preSMA hyperactivation); CES"],
    ["Anterior Insula", "Interoception; effort perception; SN hub; body-self awareness; pain/fatigue signal convergence; autonomic gateway", "ASD-like insula hyperactivation in Long COVID fatigue; interoceptive dysregulation producing PEM amplification", "taVNS (NTS→insula pathway); TPS insula-adjacent (frontal operculum, experimental); cathodal midline"],
    ["Locus Coeruleus (LC)", "Norepinephrine source; arousal; sustained attention; novelty; stress response; autonomic modulation", "COVID-19 ACE2 receptor expression confirmed in LC; LC-NE depletion contributes to attention, arousal, and autonomic Long COVID symptoms", "taVNS (primary NTS→LC pathway — direct noradrenergic restoration mechanism)"],
    ["Hypothalamus", "Circadian regulation; autonomic control; HPA axis; homeostasis; sleep-wake cycle; energy regulation", "Hypothalamic inflammation documented post-COVID-19; HPA axis dysregulation; circadian rhythm disruption; POTS autonomic centre", "taVNS (NTS→hypothalamus pathway); CES circadian normalisation; indirect hypothalamic modulation"],
    ["Olfactory Bulb / Piriform Cortex", "Smell processing; olfactory memory; limbic-olfactory interface; first neuroinvasion route for SARS-CoV-2", "Primary COVID-19 neuroinvasion site via ACE2; olfactory bulb inflammation; persistent anosmia/parosmia in Long COVID", "Limited direct NIBS; taVNS indirect olfactory-limbic modulation; olfactory training concurrent; TPS piriform (experimental)"],
    ["Thalamus", "Sensory relay; thalamocortical gating; arousal regulation; pain gating; network integration hub", "Thalamic hypoperfusion on MRI; thalamocortical network disruption in Long COVID brain fog; sleep circuit disruption", "Indirect: taVNS thalamocortical normalisation; TPS cortical targeting to reduce excessive thalamic relay hyperactivation; CES"],
  ],

  additionalBrainStructures: [
    ["Structure", "Long COVID-Specific Role", "Clinical Relevance", "FNON Consideration"],
    ["Brainstem (Medulla/NTS)", "Site of ACE2 receptor expression; COVID-19 brainstem inflammation; autonomic control centre; NTS — vagal afferent terminus", "Direct COVID-19 vulnerability; brainstem inflammation documented in post-mortem studies; autonomic dysregulation substrate; NTS = primary taVNS target", "taVNS most mechanistically targeted intervention for Long COVID brainstem/NTS pathology — direct therapeutic mechanism"],
    ["Cerebrovascular Endothelium", "Maintains BBB; regulates cerebral perfusion; highly ACE2-expressing; COVID endothelialitis site", "BBB disruption allows neuroinflammation propagation; microthrombi produce hypoperfusion; NfL and GFAP release markers of endothelial-neuronal damage", "taVNS anti-inflammatory reduces endothelial inflammation; tDCS may modulate cerebrovascular reactivity (vasodilatory response to anodal stimulation)"],
    ["Posterior Cingulate Cortex (PCC)", "DMN hub; autobiographical memory; integration of past/present experience; consciousness awareness", "Hypometabolism on FDG-PET in Long COVID; PCC-mPFC disconnection produces DMN-mediated cognitive dysfunction", "CES posterior midline normalisation; cathodal if DMN hyperactive; taVNS anti-inflammatory for metabolic restoration"],
    ["White Matter Tracts (SLF, CC, Cingulum)", "Long-range network connectivity; CEN backbone (SLF); interhemispheric transfer (CC); limbic (cingulum)", "COVID-19 white matter microstructural changes on DTI in post-COVID cohorts; reduced FA in DLPFC-parietal tracts; contributes to brain fog", "tDCS DLPFC targeting promotes activity-dependent white matter remodelling; taVNS promotes myelination via BDNF"],
    ["Choroid Plexus", "CSF production; BBB gateway; ACE2 highly expressed; immune cell trafficking into CNS", "COVID-19 choroid plexus inflammation documented; gateway for neuroinflammatory cascade in Long COVID; enlarged choroid plexus on MRI post-COVID", "taVNS anti-inflammatory reduces choroid plexus inflammation indirectly; TPS not directly applicable"],
    ["Ventral Vagal Complex (Brainstem)", "Parasympathetic outflow; social engagement; myelinated cardiac vagus; prosocial safety circuits (Polyvagal theory)", "Long COVID autonomic failure includes ventral vagal withdrawal; social isolation in Long COVID may have neurobiological vagal substrate", "taVNS directly activates ventral vagal complex via auricular branch; restoration of parasympathetic tone is primary Long COVID taVNS mechanism"],
    ["Dorsal Raphe / Serotonergic System", "5-HT source; mood regulation; sleep; pain modulation; circadian; gut-brain axis", "Post-COVID serotonin depletion recently reported (Bhatt 2023 — viral antigen-induced enterochromaffin serotonin depletion reducing vagal serotonin signalling); links fatigue and brain fog to serotonin axis", "taVNS serotonergic pathway (NTS→dorsal raphe); SNRI pharmacological approach may complement taVNS serotonergic pathway"],
  ],

  keyFunctionalNetworks: [
    ["Network", "Key Nodes", "Long COVID Dysfunction Pattern", "NIBS Modality", "Expected Outcome"],
    ["Central Executive Network (CEN)", "Bilateral DLPFC (F3/F4), posterior parietal cortex, dorsal ACC", "Bilateral hypometabolism on FDG-PET; reduced task activation; brain fog executive and working memory component", "Bilateral anodal DLPFC tDCS (F3/F4); TPS prefrontal; concurrent cognitive training", "Improved SDMT, digit span, TMT; reduced brain fog severity (MoCA +2–3 points)"],
    ["Default Mode Network (DMN)", "mPFC, PCC, IPL, hippocampus", "Hypometabolism; reduced mPFC-PCC connectivity; impaired transition between rest and task states in brain fog", "CES (DMN oscillatory normalisation); anodal mPFC tDCS; TPS mPFC", "Reduced brain fog; improved mental clarity; improved autobiographical memory"],
    ["Salience Network (SN)", "Anterior insula, ACC, amygdala, thalamus", "Hyperactivated; amplifies effort signal; drives PEM; mediated by insula-ACC hyperactivation post-COVID neuroinflammation", "taVNS (primary SN modulator via NTS); CES tonic ANS calm; cathodal Cz optional", "Reduced PEM events; improved exertion tolerance; FSS reduction ≥1.0"],
    ["Autonomic Network", "NTS, hypothalamus, brainstem autonomic nuclei, insula, ACC, vagus nerve", "Sympathovagal imbalance (reduced HRV, POTS); vagal tone depletion; autoantibody-mediated adrenergic dysfunction", "taVNS (primary — direct vagal parasympathetic restoration; NTS stimulation)", "HRV improvement (RMSSD +5–10 ms); reduced orthostatic tachycardia; POTS symptom reduction"],
    ["Limbic Network", "Hippocampus, amygdala, OFC, ACC, piriform cortex", "Hippocampal pathology (ACE2 invasion); amygdala hyperactivation (anxiety); olfactory bulb limbic disruption (anosmia)", "taVNS anti-inflammatory + BDNF; TPS hippocampal; anodal F3 tDCS (DLPFC-limbic); CES anxiolytic", "Memory improvement; reduced anxiety; BDNF-driven hippocampal neuroplasticity"],
    ["Attention Network", "Right IFG, IPS, SPL, FEF, LC (NE source)", "LC-NE depletion (COVID-19 ACE2 in LC); reduced sustained attention; distractibility; inattentive brain fog phenotype", "taVNS (NTS→LC NE restoration — primary); anodal F4 (right DLPFC attention); TPS right parietal", "Improved sustained attention (PASAT, TMT-B); reduced distractibility; attention questionnaire"],
    ["Pain Modulation Network", "M1, S1, ACC, PAG, NTS, thalamus", "Central sensitisation; small fibre neuropathy (peripheral + central); COVID hypercoagulability microthrombi in pain circuits; SN sensitisation", "M1 anodal tDCS (C3/C4); taVNS NTS-PAG-RVM descending inhibition", "VAS headache reduction; neuropathic pain improvement; PCS catastrophizing reduction"],
  ],

  networkAbnormalities:
    "Long COVID network abnormalities are characterised by a pattern of multi-focal hypometabolism overlapping with the DMN and CEN — a pattern that closely resembles the early Alzheimer's disease FDG-PET signature, suggesting shared mechanisms of metabolic network failure (though distinct in aetiology). Resting-state fMRI reveals reduced connectivity within the DMN and between DMN and CEN in Long COVID brain fog, alongside increased SN connectivity indicating SN hyperactivation. Unlike the progressive network degeneration of neurodegenerative diseases, Long COVID network abnormalities have a potential for recovery as the neuroinflammatory substrate resolves — making FNON-amplified neuroplasticity particularly valuable at the current stage of the condition. EEG studies in Long COVID show reduced alpha-band amplitude and increased theta-band power — consistent with cortical hypoarousal and neuroinflammatory encephalopathy patterns — which are directly amenable to taVNS-mediated NTS-thalamic-cortical normalisation and CES alpha entrainment. The autonomic network shows the most direct pathophysiology: reduced RMSSD heart rate variability, reduced baroreflex sensitivity, and altered sympathovagal balance — all directly modifiable by taVNS through the vagal parasympathetic pathway.",

  conceptualFramework:
    "The SOZO FNON conceptual framework for Long COVID is 'Neuroinflammatory Recovery through Anti-Inflammatory Neuromodulation' (NRANI): Long COVID CNS symptoms persist because of a self-sustaining neuroinflammatory loop — microglial activation → cytokine release → BBB disruption → further neuroinflammation → network metabolic depression → impaired recovery capacity. FNON interrupts this loop at multiple points simultaneously: taVNS activates the cholinergic anti-inflammatory reflex (NTS→vagal→spleen→macrophage inhibition→reduced TNF-α, IL-6) — breaking the neuroinflammatory cycle at its most tractable point; tDCS provides direct network metabolic upregulation; TPS promotes BDNF and hippocampal neuroplasticity. Unlike most neurological conditions where neuroplasticity is the primary therapeutic mechanism, in Long COVID reducing neuroinflammation is the prerequisite — without which network upregulation is working against a tide of ongoing metabolic depression. The FNON S-O-Z-O sequence therefore inverts the typical emphasis: the Stabilise phase (taVNS anti-inflammatory) is the most critical and should be initiated at maximum tolerated dose immediately; tDCS and TPS are the secondary phases amplifying the recovery that anti-inflammatory treatment enables. PEM-safe principles are integrated into every protocol element — no approach is recommended that risks a PEM crash, as this represents a significant setback and can entrench the condition.",

  clinicalPhenotypes: [
    ["Phenotype", "Core Feature", "Network Priority"],
    ["Brain Fog / Cognitive Dominant", "Working memory impairment; slowed processing; word-finding; executive dysfunction; subjective cognitive fog", "CEN (bilateral DLPFC), DMN, hippocampal (memory), LC-NE (attention)"],
    ["Fatigue / PEM Dominant", "Severe fatigue; post-exertional malaise; cognitive PEM; unrefreshing sleep; energy envelope severely restricted", "SN (taVNS primary); Autonomic network; mitochondrial energy failure"],
    ["POTS / Dysautonomia Dominant", "Orthostatic tachycardia; palpitations; dizziness on standing; syncope; heat intolerance", "Autonomic network (taVNS primary vagal restoration); NTS-hypothalamic; SN"],
    ["Neuroinflammatory-Depressive", "Depression; fatigue; neuroinflammatory substrate; elevated CSF cytokines; limbic disruption", "Limbic (F3 + taVNS anti-inflammatory primary); CEN; SN"],
    ["Sleep-Disrupted Long COVID", "Severe non-restorative sleep; insomnia; hypersomnia; vivid dreams; circadian misalignment", "CES primary; taVNS circadian; hypothalamic-sleep circuit; cathodal Cz evening"],
    ["Post-COVID Anxiety / PTSD Features", "Anxiety; PTSD intrusions/hyperarousal (if hospitalised COVID-19); health anxiety; social withdrawal", "Limbic SN (taVNS + CES primary); right DLPFC anxiolytic tDCS; PTSD protocol elements"],
    ["Memory-Dominant Long COVID", "Episodic memory impairment; word-finding; forgetting recent events; anosmia with limbic involvement", "Limbic (hippocampal TPS primary); anodal temporal-parietal; taVNS BDNF"],
    ["Pain-Dominant Long COVID", "Persistent headache; myalgia; neuropathic pain; small fibre neuropathy features; allodynia", "Pain network (M1 anodal + taVNS NTS-PAG); SN sensitisation; TPS S1/ACC"],
    ["Severe Multi-System Long COVID", "Multiple domains severely affected; very restricted energy envelope; bed-bound significant proportion", "taVNS + CES only initially; gradual titration; PEM safety absolute priority; tDCS and TPS deferred until stable"],
  ],

  symptomNetworkMapping: [
    ["Symptom", "Primary Network", "Key Nodes", "tDCS", "taVNS/CES"],
    ["Brain fog (cognitive)", "CEN + DMN", "DLPFC bilateral, mPFC, PCC", "Bilateral anodal F3+F4 (1.0 mA each) or unilateral F3 (1.5–2.0 mA)", "CES cognitive protocol concurrent; taVNS NTS-LC NE priming"],
    ["Fatigue / PEM", "SN + Autonomic", "Anterior insula, ACC, NTS, hypothalamus", "Cathodal Cz (preSMA, 1.0–1.5 mA) — reduce SMA effort signal", "taVNS primary (SN + autonomic) + CES tonic ANS calm"],
    ["POTS / orthostatic intolerance", "Autonomic network", "NTS, hypothalamus, vagal pathway, ACC insula", "Avoid upright tDCS during active POTS; supine only", "taVNS bilateral primary (vagal parasympathetic restoration — HR, HRV)"],
    ["Sleep disturbance", "Circadian + ANS + DMN", "Hypothalamus, LC, thalamus, PCC", "Cathodal Cz evening (1.0 mA, 15 min) — DMN calming", "CES 0.5 Hz 100 µA 40–60 min pre-sleep (primary); taVNS evening 10–15 min"],
    ["Anxiety / PTSD", "Limbic + SN", "Amygdala, insula, ACC, DLPFC (F4)", "Anodal F4 (right DLPFC, 1.5 mA) anxiolytic", "taVNS bilateral + CES (primary anxiolytics); concurrent psychotherapy"],
    ["Memory impairment", "Limbic (hippocampal)", "Hippocampus, entorhinal, left TPJ, DLPFC", "Anodal T3/P3 (left temporal-parietal, 1.5 mA)", "TPS hippocampal primary (4–5 cm depth); taVNS BDNF induction"],
    ["Persistent headache", "Pain network + SN", "M1/S1, ACC, trigeminal-thalamic, SN", "M1 anodal (C3, 2.0 mA, contralateral to headache predominance)", "taVNS NTS-PAG descending analgesic pathway"],
    ["Attention deficit (brain fog)", "Attention + CEN", "Right DLPFC, LC, IPS, ACC", "Anodal F4 (right DLPFC, 1.5 mA) + anodal F3 bilateral", "taVNS NTS→LC→NE restoration (primary attention mechanism)"],
    ["Neuropathic pain / small fibre", "Pain + SN + S1", "M1 contralateral, S1, ACC, thalamus", "M1 anodal (2.0 mA) + cathodal S1 (1.0 mA — allodynia)", "taVNS NTS-PAG-RVM spinal descending inhibition"],
    ["Motivational deficit / depression", "Limbic + CEN", "Left DLPFC (F3), ACC, amygdala, hippocampus", "Anodal F3 (left DLPFC, 2.0 mA)", "taVNS anti-inflammatory + CES post-session"],
  ],

  montageSelectionRows: [
    ["Target", "Montage"],
    ["Brain fog — bilateral CEN (primary)", "Dual anode: F3 + F4 — Reference: Cz or mastoids | 1.0 mA per channel | 15 min (PEM-safe) | concurrent cognitive task"],
    ["Brain fog — unilateral left DLPFC", "Anode: F3 — Cathode: right supraorbital | 1.5–2.0 mA | 15–20 min | concurrent cognitive training"],
    ["Fatigue — preSMA cathodal (effort signal)", "Cathode: Cz (preSMA) — Anode: bilateral mastoids | 1.0–1.5 mA | 15 min (PEM-safe)"],
    ["POTS / Autonomic (primary)", "taVNS bilateral cymba conchae | 0.5 mA, 200 µs, 25 Hz | 20 min | SUPINE position | HR monitoring throughout"],
    ["Memory (temporal-parietal)", "Anode: T3/P3 (left temporal-parietal) — Cathode: right supraorbital | 1.5 mA | 15–20 min"],
    ["Anxiety / right DLPFC anxiolytic", "Anode: F4 (right DLPFC) — Cathode: left supraorbital | 1.5 mA | 15 min"],
    ["Depression / left DLPFC upregulation", "Anode: F3 (left DLPFC) — Cathode: right supraorbital | 2.0 mA | 20 min"],
    ["Headache / central pain (M1)", "Anode: C3 (M1, contralateral to dominant headache side) — Cathode: contralateral supraorbital | 2.0 mA | 20 min"],
    ["taVNS standard (all Long COVID phenotypes)", "Left cymba conchae taVNS | 0.5 mA, 200 µs, 25 Hz | 15–20 min | mandatory pre-session for all Long COVID FNON"],
    ["CES fatigue/ANS calming (post-session)", "Alpha-Stim AID bilateral earlobe | 100 µA, 0.5 Hz | 40–60 min | during quiet rest post-session | PEM-safe"],
    ["TPS hippocampal (memory dominant)", "NEUROLITH® TPS bilateral or left hippocampus | 0.25 mJ/mm², 4000 pulses | neuro-navigation 4–5 cm depth"],
    ["TPS prefrontal cognitive (brain fog)", "NEUROLITH® TPS left DLPFC | 0.25 mJ/mm², 3000 pulses | neuro-navigation | session alternated with tDCS, not same day"],
    ["mPFC anodal (DMN / motivation)", "Anode: Fz (mPFC) — Cathode: inion | 1.0–1.5 mA | 15 min | concurrent DMN-normalising task or rest"],
  ],

  polarityPrincipleText:
    "In Long COVID, polarity selection reflects the hypometabolic-hyperexcitable paradox: most Long COVID brain regions are hypometabolic (reduced glucose uptake, reduced spontaneous activity) — necessitating anodal upregulation — but the Salience Network anterior insula and ACC are hyperexcitable — requiring modulation by taVNS rather than excitatory tDCS. Anodal tDCS of the bilateral DLPFC (F3/F4) is the primary CEN upregulation strategy, directly addressing prefrontal hypometabolism. Anodal temporal-parietal (T3/P3) targets the hippocampal memory network. Anodal left DLPFC (F3) addresses the depression-fatigue-motivation domain. The cathodal exception is the preSMA (Cz) in fatigue-dominant phenotypes: cathodal Cz reduces the SMA's compensatory overactivation that drives the paradoxical sense of effort despite inactivity in Long COVID fatigue — analogous to its use in MS central fatigue. The POTS phenotype requires a critical modification: tDCS protocols are delivered in the supine or semi-reclined position to avoid orthostatic stress during stimulation; taVNS is the primary intervention for POTS (lying down, bilateral, 20 min) and does not require the patient to be upright. Session intensity and duration are explicitly limited for PEM-sensitive phenotypes: 15-minute tDCS sessions (not 20 minutes) as the safe starting point, with extension only after tolerance confirmed over ≥3 sessions.",

  polarityTable: [
    ["Target", "Polarity", "Effect", "Primary Indication", "Evidence Level"],
    ["DLPFC F3/F4 bilateral", "ANODAL", "Upregulates CEN hypofrontality; restores executive network metabolism; working memory improvement", "Long COVID brain fog; CEN hypometabolism; cognitive impairment", "Level C — Long COVID tDCS pilot (NCT05044910 ongoing); ME/CFS-adjacent tDCS literature"],
    ["Left DLPFC F3", "ANODAL", "Anti-depressant; left CEN upregulation; motivation restoration; limbic-prefrontal engagement", "Long COVID depression; motivational deficit; depressive-neuroinflammatory phenotype", "Level B (depression literature); Level C (Long COVID specific)"],
    ["Right DLPFC F4", "ANODAL", "Anxiolytic; attention network upregulation; right hemisphere emotional regulation", "Long COVID anxiety; attentional deficit; right hemisphere attention-anxiety", "Level B (anxiety literature); Level C (Long COVID specific)"],
    ["preSMA Cz", "CATHODAL", "Reduces SMA effort signal; decreases PEM-anticipatory motor over-activation; reduces central fatigue amplification", "Long COVID fatigue-dominant; PEM; SNA compensatory overactivation", "Level C — extrapolated from ME/CFS fatigue tDCS; Long COVID SN model"],
    ["M1 C3/C4", "ANODAL", "Activates descending pain inhibitory pathways; motor cortex upregulation for central pain modulation", "Long COVID persistent headache; neuropathic pain; small fibre neuropathy central component", "Level B (M1 tDCS pain); Level C (Long COVID pain specific)"],
  ],

  classicTdcsProtocols: [
    {
      code: "C1",
      name: "Standard Bilateral DLPFC Brain Fog Protocol",
      montage: "Dual anode F3 + F4 — Reference Cz or mastoids",
      intensity: "1.0 mA per channel (2.0 mA total)",
      duration: "15 minutes (PEM-safe — start here)",
      sessions: "10 sessions (daily × 5 days, 2 weeks); extend to 20 min only after tolerance confirmed",
      indication: "Long COVID brain fog; bilateral CEN hypometabolism; cognitive impairment (working memory, processing speed)",
      evidence: "Level C — ME/CFS-adjacent; Long COVID tDCS pilot data; Guedj 2021 PET hypometabolism rationale"
    },
    {
      code: "C2",
      name: "Standard Left DLPFC Protocol (Depression/Motivation)",
      montage: "Anode F3 — Cathode right supraorbital",
      intensity: "2.0 mA",
      duration: "20 minutes",
      sessions: "15 sessions (depression-prominent Long COVID phenotype)",
      indication: "Long COVID depression; motivational deficit; neuroinflammatory depressive phenotype",
      evidence: "Level B (depression tDCS); Level C (Long COVID neuroinflammatory depression)"
    },
    {
      code: "C3",
      name: "Standard Right DLPFC Anxiolytic Protocol",
      montage: "Anode F4 — Cathode left supraorbital",
      intensity: "1.5 mA",
      duration: "15–20 minutes",
      sessions: "10 sessions",
      indication: "Long COVID anxiety; PTSD features; attentional impairment; right hemisphere anxiolytic",
      evidence: "Level B (anxiety tDCS); Level C (Long COVID specific)"
    },
    {
      code: "C4",
      name: "Standard Cathodal preSMA Fatigue Protocol",
      montage: "Cathode Cz (preSMA) — Anode bilateral mastoids",
      intensity: "1.0–1.5 mA",
      duration: "15 minutes",
      sessions: "10 sessions",
      indication: "Long COVID central fatigue; PEM-fatigue phenotype; SMA effort signal reduction",
      evidence: "Level C — SMA cathodal fatigue; ME/CFS model; Long COVID SN model"
    },
    {
      code: "C5",
      name: "Standard Temporal-Parietal Memory Protocol",
      montage: "Anode T3/P3 (left temporal-parietal) — Cathode right supraorbital",
      intensity: "1.5 mA",
      duration: "15–20 minutes",
      sessions: "10 sessions concurrent with memory training",
      indication: "Long COVID memory impairment; hippocampal/temporal network; episodic memory deficit",
      evidence: "Level C — temporal-parietal tDCS memory literature; Long COVID memory case series"
    },
    {
      code: "C6",
      name: "Standard mPFC DMN Protocol",
      montage: "Anode Fz (mPFC) — Cathode inion",
      intensity: "1.0–1.5 mA",
      duration: "15 minutes",
      sessions: "10 sessions",
      indication: "Long COVID DMN hypometabolism; mPFC dysfunction; motivation; self-directed processing",
      evidence: "Level C — mPFC tDCS DMN literature; Long COVID PET hypometabolism rationale"
    },
    {
      code: "C7",
      name: "Standard M1 Central Pain Protocol",
      montage: "Anode C3/C4 (contralateral to dominant pain) — Cathode contralateral supraorbital",
      intensity: "2.0 mA",
      duration: "20 minutes",
      sessions: "10 sessions (pain series); maintenance 2×/week",
      indication: "Long COVID persistent headache; neuropathic pain; central sensitisation; small fibre neuropathy central component",
      evidence: "Level B (M1 tDCS pain — Lefaucheur 2017); Level C (Long COVID pain)"
    },
    {
      code: "C8",
      name: "Standard CES Sleep/ANS Protocol",
      montage: "Alpha-Stim AID bilateral earlobe — 100 µA, 0.5 Hz",
      intensity: "100 µA",
      duration: "40–60 minutes pre-sleep",
      sessions: "Daily × 3 weeks; then maintenance 3–5×/week",
      indication: "Long COVID sleep disturbance; tonic ANS calming; sympathovagal balance; PEM recovery facilitation",
      evidence: "Level C — CES sleep/ANS literature; Long COVID dysautonomia management"
    },
  ],

  fnonTdcsProtocols: [
    {
      code: "F1",
      name: "FNON Anti-Inflammatory Brain Fog Protocol — taVNS + Bilateral DLPFC",
      montage: "taVNS bilateral 0.5 mA × 20 min → bilateral anodal DLPFC tDCS (F3+F4, 1.0 mA) × 15 min concurrent with cognitive training",
      intensity: "taVNS 0.5 mA bilateral + tDCS 1.0 mA per channel",
      duration: "20 min taVNS → 15 min tDCS (total 35 min session); PEM-safe",
      sessions: "10–15 sessions",
      indication: "Brain fog dominant Long COVID; neuroinflammatory CEN hypometabolism; the cornerstone Long COVID FNON protocol",
      fnon_rationale: "taVNS first reduces neuroinflammation (NTS→cholinergic anti-inflammatory reflex→TNF-α, IL-6 suppression) — addressing the primary pathological mechanism; then bilateral DLPFC tDCS upregulates the metabolically depressed CEN during concurrent cognitive training for activity-dependent plasticity. This sequence prioritises anti-inflammatory (cause) over network upregulation (effect)"
    },
    {
      code: "F2",
      name: "FNON Fatigue-PEM Safe Protocol — taVNS + cathodal Cz + CES",
      montage: "taVNS bilateral 0.5 mA × 20 min (supine) → cathodal Cz tDCS 1.0 mA × 15 min → CES 100 µA × 40 min post-session rest",
      intensity: "taVNS 0.5 mA + tDCS cathodal 1.0 mA + CES 100 µA",
      duration: "75 min total; must be followed by ≥30 min rest (PEM safety)",
      sessions: "10 sessions; PEM diary mandatory; reduce frequency to 3×/week if PEM triggered",
      indication: "Fatigue-PEM dominant Long COVID; SN hyperactivation; effort signal dysregulation; PEM-safe protocol design",
      fnon_rationale: "taVNS (supine) addresses autonomic and SN hyperactivation without physical demand; cathodal Cz reduces SMA effort signal driving PEM; CES during 40-min post-session rest ensures tonic ANS calming prevents rebound — the three-step PEM-safe fatigue protocol"
    },
    {
      code: "F3",
      name: "FNON POTS/Autonomic Protocol — Bilateral taVNS Supine",
      montage: "Bilateral taVNS 0.5 mA, 200 µs, 25 Hz × 20 min supine; CES post-session; HR monitoring throughout; no tDCS in POTS-acute phase",
      intensity: "Bilateral taVNS 0.5 mA; CES 100 µA post-session",
      duration: "20 min taVNS + 40 min CES rest",
      sessions: "Daily × 2 weeks; then 5×/week; home taVNS between sessions",
      indication: "Long COVID POTS/dysautonomia dominant; vagal parasympathetic depletion; orthostatic intolerance; sympathovagal imbalance",
      fnon_rationale: "Bilateral taVNS provides maximum vagal parasympathetic activation via NTS → dorsal motor nucleus of vagus → heart; bilateral stimulation doubles vagal afferent input to NTS; supine position essential for POTS to eliminate orthostatic demand; this protocol IS the treatment for POTS Long COVID — not an adjunct to tDCS"
    },
    {
      code: "F4",
      name: "FNON Memory Network Protocol — TPS Hippocampal + taVNS BDNF",
      montage: "taVNS 0.5 mA × 15 min pre-session → TPS hippocampal bilateral 0.25 mJ/mm² 4000 pulses → memory training task post-TPS",
      intensity: "taVNS 0.5 mA; TPS 0.25 mJ/mm², 4000 pulses bilateral hippocampal",
      duration: "15 min taVNS + 45 min TPS; rest + memory training post-session",
      sessions: "6–8 TPS sessions (2×/week × 3–4 weeks) + taVNS daily",
      indication: "Memory-dominant Long COVID; hippocampal ACE2 neuroinvasion sequelae; episodic memory impairment; anosmia with limbic involvement",
      fnon_rationale: "taVNS pre-session induces BDNF release via NTS-hippocampal pathway — neurotrophin priming for hippocampal TPS-induced neuroplasticity; TPS hippocampal deep targeting (4–5 cm) addresses the primary post-COVID hippocampal network impairment; sequential taVNS→TPS→memory training creates an activity-dependent neuroplasticity cascade"
    },
    {
      code: "F5",
      name: "FNON Anti-Inflammatory Depression Protocol — taVNS + F3 anodal + CES",
      montage: "Bilateral taVNS 0.5 mA × 20 min + anodal F3 tDCS 2.0 mA × 20 min concurrent + CES 40 min post",
      intensity: "Bilateral taVNS 0.5 mA + tDCS 2.0 mA + CES 100 µA",
      duration: "20 min concurrent taVNS+tDCS + 40 min CES post-session",
      sessions: "15–20 sessions",
      indication: "Long COVID neuroinflammatory depression; limbic-prefrontal disconnection; neuroinflammatory substrate",
      fnon_rationale: "Bilateral taVNS anti-inflammatory (cholinergic anti-inflammatory reflex) targets the cytokine-mediated limbic disruption that drives Long COVID depression — complementing the antidepressant mechanism of F3 anodal tDCS; CES post-session tonic ANS calming consolidates; this targets both neurobiological (anti-inflammatory + DLPFC) and autonomic (taVNS+CES) depression substrates simultaneously"
    },
    {
      code: "F6",
      name: "FNON Long COVID Maintenance Protocol — Rotating Multi-Network",
      montage: "Week 1–2: F1 brain fog protocol; Week 3–4: F2 fatigue protocol; Week 5–6: F4 memory (TPS); taVNS every session; CES daily home",
      intensity: "Per individual protocol sessions",
      duration: "Per individual protocols; PEM diary continues",
      sessions: "12 sessions (rotating); home taVNS daily 2 × 15 min; monthly booster TPS",
      indication: "Multi-phenotype Long COVID maintenance; Phase 2 after initial intensive protocol; long-term network restoration",
      fnon_rationale: "Long COVID recovery is protracted (months to years); rotating network protocols maintain stimulus-specific plasticity across cognitive, fatigue, and memory domains while preventing habituation; daily home taVNS anti-inflammatory baseline is the most important maintenance element — interrupting the persistent neuroinflammatory cycle daily"
    },
  ],

  classicTpsProtocols: [
    {
      code: "T1",
      name: "Classic TPS Hippocampal Memory Protocol",
      target: "Bilateral hippocampus (neuro-navigation guided, 4–5 cm depth)",
      parameters: "0.25 mJ/mm², 4000 pulses bilateral; 45 min session",
      sessions: "6 sessions (2×/week × 3 weeks)",
      indication: "Long COVID memory impairment; hippocampal post-COVID pathology; episodic memory deficit",
      evidence: "Level C — adapted from Beisteiner 2020 AD protocol; Long COVID memory pilot rationale"
    },
    {
      code: "T2",
      name: "Classic TPS DLPFC Cognitive Protocol",
      target: "Left DLPFC (F3 region; neuro-navigation; 2–3 cm depth)",
      parameters: "0.25 mJ/mm², 3000 pulses; 30 min session",
      sessions: "6 sessions",
      indication: "Long COVID brain fog; CEN hypometabolism; executive function",
      evidence: "Level C — DLPFC TPS cognitive literature; Long COVID brain fog case series"
    },
    {
      code: "T3",
      name: "Classic TPS mPFC DMN Protocol",
      target: "mPFC (Fz area; neuro-navigation)",
      parameters: "0.20 mJ/mm², 2500 pulses",
      sessions: "6 sessions",
      indication: "Long COVID DMN hypometabolism; mPFC dysfunction; motivation; mental clarity",
      evidence: "Level C — mPFC TPS DMN; Long COVID PET rationale"
    },
    {
      code: "T4",
      name: "Classic TPS Hippocampal-DLPFC Memory Chain",
      target: "Sequential: hippocampus (4000 pulses) → DLPFC (2000 pulses) same session",
      parameters: "0.25 mJ/mm² per target; neuro-navigation; 60 min",
      sessions: "6 sessions (2×/week × 3 weeks)",
      indication: "Combined memory + executive brain fog; hippocampal-frontal network disconnection",
      evidence: "Level C — sequential TPS chain protocol; hippocampal-prefrontal memory architecture"
    },
    {
      code: "T5",
      name: "Classic TPS Pain Network Protocol",
      target: "M1 (contralateral to dominant pain, C3/C4 area) + ACC (Fz)",
      parameters: "0.25 mJ/mm², 2500 pulses M1 + 2000 pulses ACC; neuro-navigation",
      sessions: "6 sessions",
      indication: "Long COVID persistent headache; central neuropathic pain; central sensitisation",
      evidence: "Level C — TPS pain network; Long COVID pain NIBS literature"
    },
  ],

  fnonTpsProtocols: [
    {
      code: "FT1",
      name: "FNON TPS Neuroinflammatory Memory Recovery Protocol",
      target: "Bilateral hippocampus (4000 pulses) → bilateral DLPFC (2500 pulses each); taVNS concurrent during hippocampal TPS",
      parameters: "0.25 mJ/mm² per target; neuro-navigation; taVNS 0.5 mA during TPS; 75 min total",
      sessions: "6–8 sessions (2×/week)",
      indication: "Memory-dominant Long COVID with executive overlap; hippocampal-prefrontal disconnection; ACE2 neuroinvasion sequelae",
      fnon_rationale: "taVNS concurrent during TPS uniquely primes BDNF release simultaneously with TPS neuroplasticity induction — maximising hippocampal regenerative capacity at the moment of TPS stimulation; sequential hippocampal-DLPFC TPS maps the memory consolidation-retrieval circuit"
    },
    {
      code: "FT2",
      name: "FNON TPS Anti-Inflammatory CEN Restoration Protocol",
      target: "Bilateral DLPFC (F3/F4, 3000 pulses each) → mPFC (Fz, 2000 pulses) sequential; taVNS 20 min pre-session",
      parameters: "0.25 mJ/mm² per target; neuro-navigation; 75 min TPS; taVNS 20 min pre",
      sessions: "6 sessions",
      indication: "Brain fog dominant Long COVID; bilateral CEN hypometabolism; DMN-CEN disconnection",
      fnon_rationale: "taVNS pre-session anti-inflammatory priming (reduces neuroinflammatory burden on CEN metabolism) followed by bilateral DLPFC + mPFC TPS — upregulating the full CEN-DMN network complex affected by Long COVID hypometabolism"
    },
    {
      code: "FT3",
      name: "FNON TPS Fatigue Circuit Protocol",
      target: "ACC/mPFC (Fz area, 2500 pulses) → preSMA (Cz area, 2000 pulses); taVNS concurrent; supine position",
      parameters: "0.20 mJ/mm² per target; 45 min; taVNS concurrent; supine for POTS safety",
      sessions: "6 sessions",
      indication: "Long COVID fatigue-PEM; SN-ACC hyperactivation; effort signal dysregulation",
      fnon_rationale: "Sequential ACC-SMA TPS targets both ends of the SN-fatigue circuit: ACC (SN hub generating effort signal) then preSMA (motor effort output) — modulating the full fatigue signal arc; taVNS concurrent provides simultaneous NTS→ACC anti-fatigue modulation"
    },
    {
      code: "FT4",
      name: "FNON TPS Autonomic-Limbic Integration Protocol",
      target: "mPFC (Fz, 2500 pulses) → ACC (2000 pulses) sequential; bilateral taVNS concurrent",
      parameters: "0.20–0.25 mJ/mm²; neuro-navigation; bilateral taVNS 0.5 mA concurrent",
      sessions: "6 sessions",
      indication: "Long COVID POTS + anxiety + depression combined phenotype; autonomic-limbic network integration failure",
      fnon_rationale: "mPFC-ACC TPS modulates the prefrontal-autonomic-limbic interface simultaneously with bilateral taVNS maximum vagal activation — targeting the ANS-limbic-prefrontal triad that mediates POTS, anxiety, and mood in Long COVID"
    },
    {
      code: "FT5",
      name: "FNON TPS Hippocampal Neurogenesis Protocol",
      target: "Bilateral hippocampus 4000 pulses; memory training task concurrent during TPS; taVNS concurrent",
      parameters: "0.25 mJ/mm²; neuro-navigation guided depth targeting; taVNS concurrent; 45 min",
      sessions: "8 sessions (2×/week × 4 weeks)",
      indication: "Post-COVID hippocampal damage; memory impairment; anosmia-limbic involvement; BDNF-driven neurogenesis protocol",
      fnon_rationale: "Maximum neurogenesis protocol: TPS hippocampal + concurrent taVNS BDNF + active memory encoding (activity-dependent) — triple-mechanism hippocampal neuroplasticity induction for Long COVID hippocampal recovery"
    },
    {
      code: "FT6",
      name: "FNON TPS Pain-Headache Network Protocol",
      target: "M1 (2500 pulses, contralateral to dominant pain) → ACC/mPFC (2000 pulses) → S1 (2000 pulses); taVNS concurrent",
      parameters: "0.25 mJ/mm² per target; neuro-navigation; taVNS concurrent NTS-PAG; 60 min",
      sessions: "6 sessions acute series + monthly maintenance",
      indication: "Long COVID persistent headache; central neuropathic pain; small fibre neuropathy; central sensitisation",
      fnon_rationale: "Three-node pain network TPS: M1 (descending inhibition), ACC (affective pain), S1 (sensory gating) + taVNS NTS-PAG concurrent analgesic pathway — comprehensive pain circuit modulation for Long COVID central sensitisation"
    },
    {
      code: "FT7",
      name: "FNON TPS Olfactory-Limbic Recovery Protocol",
      target: "Piriform cortex / orbitofrontal cortex (Fp1/Fp2, orbitofrontal TPS, 2000 pulses) + hippocampal (2000 pulses)",
      parameters: "0.20 mJ/mm²; neuro-navigation; shorter depth for OFC; 40 min; olfactory training concurrent",
      sessions: "6–8 sessions concurrent with structured olfactory training",
      indication: "Long COVID anosmia / parosmia; limbic-olfactory circuit recovery; piriform-hippocampal network",
      fnon_rationale: "TPS orbitofrontal-piriform targets the olfactory cortex entry into the limbic network — damaged by ACE2 COVID-19 neuroinvasion; hippocampal TPS supports olfactory memory reconsolidation; concurrent structured olfactory training provides activity-dependent stimulus for network remodelling"
    },
    {
      code: "FT8",
      name: "FNON TPS Sleep-Circadian Recovery Protocol",
      target: "mPFC (Fz, 2000 pulses) — evening session; taVNS concurrent; CES 60 min post-TPS",
      parameters: "0.20 mJ/mm²; 2000 pulses; evening timing; neuro-navigation; taVNS concurrent; CES post",
      sessions: "6 sessions (2×/week, evenings only)",
      indication: "Long COVID non-restorative sleep; circadian dysregulation; hypothalamic-mPFC sleep circuit",
      fnon_rationale: "Evening mPFC TPS for SCN-prefrontal circadian circuit normalisation + taVNS concurrent for vagal sleep-onset facilitation + CES 60 min as primary sleep-onset intervention — coordinated evening protocol for Long COVID sleep"
    },
    {
      code: "FT9",
      name: "FNON TPS Long COVID Comprehensive Recovery Protocol",
      target: "Rotating: Session 1,4,7 — hippocampal+DLPFC (memory+cognition); Session 2,5,8 — ACC+preSMA (fatigue); Session 3,6,9 — M1+ACC (pain); taVNS every session",
      parameters: "0.20–0.25 mJ/mm² per target; 3000–4000 pulses; neuro-navigation; 45–60 min per session",
      sessions: "9 sessions (3 cycles of rotating protocol) + monthly maintenance",
      indication: "Multi-domain Long COVID; brain fog + fatigue + pain + memory combined phenotype; comprehensive network restoration",
      fnon_rationale: "Long COVID frequently presents as multi-domain network failure; the rotating three-target protocol ensures all primary affected networks (CEN+memory, SN+fatigue, pain) receive regular TPS modulation while maintaining daily taVNS anti-inflammatory baseline — a comprehensive Long COVID FNON recovery programme"
    },
  ],

  multimodalPhenotypes: [
    {
      phenotype: "Brain Fog / Cognitive Dominant",
      stabilise: "taVNS bilateral 0.5 mA × 20 min (anti-inflammatory primary — NTS→cholinergic anti-inflammatory reflex; noradrenergic CEN priming via NTS-LC pathway)",
      optimise: "Bilateral anodal DLPFC tDCS (F3+F4, 1.0 mA each) × 15 min concurrent with cognitive training (SDMT, digit span, verbal fluency, dual-task — activity-dependent CEN plasticity)",
      zone: "TPS left DLPFC 0.25 mJ/mm² 3000 pulses (session 1, 3, 5) + TPS hippocampal 4000 pulses bilateral (session 2, 4, 6); neuro-navigation guided",
      outcome: "CES 100 µA × 40 min during post-session quiet rest (PEM-safe recovery); cognitive training homework (Cognifit/Lumosity/RehaCom); SDMT + MoCA monitoring"
    },
    {
      phenotype: "Fatigue / PEM Dominant",
      stabilise: "Bilateral taVNS 0.5 mA × 20 min SUPINE (SN + autonomic + anti-inflammatory — mandatory supine for POTS safety); PEM diary reviewed pre-session",
      optimise: "Cathodal Cz tDCS 1.0 mA × 15 min (SMA effort signal reduction — PEM-safe cathodal approach); no cognitive demand tDCS session",
      zone: "TPS ACC/preSMA 0.20 mJ/mm² 2000 pulses each (session 2, 4, 6 only — not every session given PEM risk); taVNS concurrent",
      outcome: "CES 100 µA × 40–60 min post-session mandatory rest; energy envelope management programme; PEM diary ×7 days ongoing; no post-session activity for 1 hour"
    },
    {
      phenotype: "POTS / Dysautonomia Dominant",
      stabilise: "Bilateral taVNS 0.5 mA × 20 min supine (primary treatment — maximum vagal parasympathetic activation; HR monitoring throughout; target RMSSD improvement)",
      optimise: "CES 100 µA × 40 min concurrent or post-taVNS (tDCS deferred until POTS controlled; no upright protocol during active POTS acute phase)",
      zone: "TPS deferred until POTS stabilised; maintain taVNS + CES only for minimum 3 weeks before adding tDCS or TPS; POTS cardiological review at 3-week checkpoint",
      outcome: "HRV monitoring daily (wearable device — RMSSD target improvement ≥5 ms); NASA lean test or Ewing battery at 4 weeks; pharmacological POTS management concurrent (fludrocortisone, midodrine per cardiology)"
    },
    {
      phenotype: "Neuroinflammatory-Depressive Long COVID",
      stabilise: "Bilateral taVNS 0.5 mA × 20 min (anti-inflammatory primary — NTS→cholinergic anti-inflammatory reflex→TNF-α, IL-6, IL-1β suppression — directly targets neuroinflammatory depression substrate)",
      optimise: "Anodal left DLPFC tDCS (F3, 2.0 mA) × 20 min concurrent with bilateral taVNS (combined anti-inflammatory + DLPFC upregulation during session)",
      zone: "TPS left DLPFC 0.25 mJ/mm² 3000 pulses (odd sessions) + TPS hippocampal 0.25 mJ/mm² 4000 pulses (even sessions); neuro-navigation guided",
      outcome: "CES 100 µA × 40 min post-session; psychotherapy (Long COVID-adapted CBT or ACT); PHQ-9 + GAD-7 monitoring fortnightly; antidepressant medication documented and maintained"
    },
    {
      phenotype: "Sleep-Disrupted Long COVID",
      stabilise: "taVNS 0.5 mA × 15 min EVENING (circadian reset; vagal sleep-onset facilitation; NTS→hypothalamic pathway)",
      optimise: "Cathodal Cz 1.0 mA × 15 min evening (DMN/SMA calming before sleep; reduce evening hyperarousal) — only if not causing activation; monitor carefully",
      zone: "TPS mPFC (Fz) 0.20 mJ/mm² 2000 pulses once-weekly evening session (circadian-mPFC circuit); not daily TPS for sleep phenotype",
      outcome: "CES 0.5 Hz 100 µA × 60 min pre-sleep (primary sleep intervention — every night); sleep diary + actigraphy monitoring; melatonin concurrent; CBT-I referral if sleep architecture severely disrupted"
    },
    {
      phenotype: "Post-COVID Anxiety / PTSD Features",
      stabilise: "Bilateral taVNS 0.5 mA × 15 min (NTS→amygdala modulation via LC; vagal parasympathetic induction — reduces hyperarousal baseline essential before any cognitive demand)",
      optimise: "Anodal right F4 tDCS (1.5 mA) × 15 min concurrent with anxiety-adapted intervention (psychoeducation, relaxation, CBT cognitive restructuring)",
      zone: "TPS right DLPFC 0.25 mJ/mm² 2500 pulses + ACC (Fz) 2000 pulses; neuro-navigation; concurrent with trauma-informed psychological session",
      outcome: "CES bilateral 100 µA × 40 min post-session; trauma-informed psychological therapy concurrent; GAD-7 + PCL-5 (PTSD) monitoring; psychiatric review if severe"
    },
    {
      phenotype: "Memory-Dominant Long COVID",
      stabilise: "taVNS 0.5 mA × 15 min (NTS→hippocampal BDNF induction; anti-inflammatory limbic protection — prerequisite before TPS memory protocol)",
      optimise: "Anodal T3/P3 tDCS (left temporal-parietal, 1.5 mA) × 20 min concurrent with memory encoding tasks (word lists, story recall, spatial memory tasks)",
      zone: "TPS bilateral hippocampal 0.25 mJ/mm² 4000 pulses (primary deep target; neuro-navigation 4–5 cm depth); taVNS concurrent during TPS",
      outcome: "Post-session memory consolidation task (memory practice ×30 min quiet review); RBMT-3 or Rey AVLT memory scores monitoring; anosmia-specific: olfactory training concurrent"
    },
    {
      phenotype: "Pain-Dominant Long COVID",
      stabilise: "taVNS 0.5 mA, 200 µs, 25 Hz × 15 min (NTS→PAG→RVM→spinal descending inhibition analgesic pre-activation — mandatory before M1 tDCS)",
      optimise: "Anodal M1 tDCS (C3/C4, 2.0 mA) × 20 min contralateral to dominant pain; concurrent with pain neuroscience education session",
      zone: "TPS M1 → S1 → ACC sequential pain network 0.25 mJ/mm² 2500 pulses each; neuro-navigation guided; 60 min pain network TPS session",
      outcome: "CES 100 µA × 40 min post-session (analgesic CES maintenance); pain diary (VAS daily); home taVNS 2 × 10 min daily PRN for pain episodes; neuropathic pain scale monitoring"
    },
    {
      phenotype: "Severe Multi-System Long COVID",
      stabilise: "taVNS 0.3 mA × 10 min SUPINE ONLY (reduced intensity; start here; mandatory first 3 sessions — build tolerance; monitor PEM after each session carefully)",
      optimise: "CES 100 µA × 20 min post-taVNS (only; no tDCS in first 3 sessions; add CES after taVNS tolerance confirmed); defer ALL tDCS and TPS until stable over 3 taVNS+CES sessions",
      zone: "TPS deferred minimum 4 weeks; tDCS deferred minimum 2 weeks; gradual titration: taVNS → CES → tDCS 10 min → tDCS 15 min → TPS 2000 pulses; each step requires 2-session PEM tolerance check",
      outcome: "PEM diary mandatory throughout; energy envelope monitoring (HR-based pacing tool); monthly MDT review; very gradual function return goals; no pressure for rapid recovery timeline"
    },
  ],

  taskPairingRows: [
    ["Task Type", "Concurrent NIBS", "Protocol Rationale", "Outcome Measure"],
    ["Computerised cognitive training (SDMT, digit span, working memory)", "Bilateral anodal DLPFC tDCS (F3+F4) + taVNS pre-session", "Activity-dependent CEN plasticity: DLPFC upregulation during cognitive task engagement; taVNS NE priming for learning", "SDMT score (target +4 symbols); MOCA cognitive domain; NeuroTracker speed threshold"],
    ["Paced breathing / relaxation exercise (for POTS/ANS)", "taVNS bilateral supine + CES concurrent", "Synergistic vagal activation: paced breathing at 6 breaths/min (resonance frequency) + taVNS both maximise HRV; CES tonic ANS calm", "RMSSD HRV (target +5–10 ms); standing HR test; POTS symptom score"],
    ["Pain neuroscience education (PNE)", "M1 anodal tDCS + taVNS concurrent", "Pain perception reframing concurrent with descending pain inhibitory pathway activation via M1 tDCS and NTS-PAG taVNS", "VAS pain; Pain Catastrophizing Scale (PCS); pain interference (BPI)"],
    ["Memory encoding practice (word lists, story recall)", "Anodal T3/P3 tDCS + taVNS BDNF priming", "Temporal-parietal upregulation during encoding task maximises LTP-like memory consolidation; taVNS BDNF supports hippocampal plasticity", "RBMT-3; Rey AVLT immediate recall; Long COVID cognitive symptom scale"],
    ["Olfactory training (rose, lemon, cloves, eucalyptus)", "taVNS (olfactory-limbic modulation indirect) + TPS OFC/piriform", "taVNS limbic pathway modulation during olfactory re-exposure; TPS orbitofrontal activates olfactory cortex at moment of odour stimulus; activity-dependent olfactory network retraining", "UPSIT olfactory score; odour threshold test; parosmia diary"],
    ["Pre-sleep wind-down routine / sleep hygiene", "CES 100 µA × 60 min (primary) + taVNS 15 min pre-sleep", "Tonic ANS parasympathetic facilitation of sleep onset; circadian entrainment; vagal tone maximisation for sleep stage architecture", "Actigraphy sleep onset latency (target <30 min); PSQI; daytime energy level subjective"],
  ],

  outcomeMeasures:
    "Primary outcome measures for the SOZO Long COVID FNON protocol are phenotype-specific: (1) Cognitive: Symbol Digit Modalities Test (SDMT) — primary brain fog cognitive outcome (MCID: +4 symbols); MoCA composite; Trail Making Test A+B. (2) Fatigue/PEM: Fatigue Severity Scale (FSS — MCID: −0.45) and Modified Fatigue Impact Scale (MFIS); PEM event frequency (diary). (3) POTS/Autonomic: RMSSD heart rate variability (MCID: +5 ms); orthostatic heart rate change on 10-min standing test (target: NASA lean test improvement); COMPASS-31 autonomic score. (4) Sleep: Pittsburgh Sleep Quality Index (PSQI); actigraphy sleep onset latency and WASO. (5) Depression/Anxiety: PHQ-9, GAD-7, PCL-5 (if PTSD features). (6) Memory: Rey AVLT or RBMT-3 immediate recall. (7) Pain: VAS and Numeric Rating Scale (NRS). (8) Global: WHOQOL-BREF quality of life; Long COVID-specific Patient Reported Outcome Measure (PCORNET Long COVID questionnaire). Safety monitoring: PEM diary completed for 48 hours after every NIBS session — if new or worsened PEM documented, reduce next session length by 50%; if PEM persists across 3 consecutive sessions, pause protocol and MDT review. Neurophysiological optional monitoring: resting EEG alpha power and theta/alpha ratio; TMS MEP cortical excitability pre/post protocol; fMRI resting-state functional connectivity (participating sites only).",

  medicationSectionTitle: "Pharmacological Context and NIBS Interactions in Long COVID",
  medicationSectionText:
    "No pharmacological agent is approved specifically for Long COVID. Key medication interactions with FNON: Low-dose naltrexone (LDN 1.5–4.5 mg): increasingly used off-label for Long COVID neuroinflammation (mu-opioid receptor blockade increases endogenous opioids and reduces microglial TLR4 activation); complementary to taVNS anti-inflammatory mechanism; no known interaction with NIBS. SSRIs (sertraline, escitalopram): anti-inflammatory and serotonergic properties; sertraline specifically has anti-inflammatory effects beyond monoaminergic mechanism; may augment tDCS cortical LTP; document and maintain. SNRIs (duloxetine, venlafaxine): NE reuptake inhibition synergises with taVNS LC-NE pathway; may reduce neuropathic pain and fatigue; document dose. Fludrocortisone / midodrine / ivabradine (POTS): these cardiovascular medications alter heart rate and blood pressure; monitor HR and BP throughout taVNS sessions; taVNS may reduce need for pharmacological POTS management over time. Beta-blockers (propranolol for POTS): reduce resting HR; document dose; taVNS-induced HR change may be blunted. Anticoagulants (apixaban, rivaroxaban for post-COVID hypercoagulability): no known NIBS interaction; document use. Corticosteroids: alter cortical excitability; reduce tDCS LTP response; document if used. Gabapentin/pregabalin (neuropathic pain): reduce cortical excitability; document dose; may require tDCS intensity adjustment. Melatonin: complementary to CES and taVNS circadian protocol; no NIBS interaction. Antihistamines (for MCAS overlap): may alter thalamic excitability (sedating antihistamines); document. Stimulants (methylphenidate/modafinil for brain fog, off-label): catecholaminergic enhancement may augment tDCS; document timing relative to session. Histamine-1 receptor inverse agonists (famotidine — trialled for Long COVID): document use; no direct NIBS interaction. Metformin (investigated for Long COVID via AMPK pathway): no NIBS interaction; document.",

  references: {
    foundational: [
      { authors: "Davis HE, McCorkell L, Vogel JM, Topol EJ", year: 2023, title: "Long COVID: major findings, mechanisms and recommendations", journal: "Nature Reviews Microbiology", volume: "21(3)", pages: "133–146", doi: "10.1038/s41579-022-00846-2" },
      { authors: "Nalbandian A, Sehgal K, Gupta A, et al.", year: 2021, title: "Post-acute COVID-19 syndrome", journal: "Nature Medicine", volume: "27(4)", pages: "601–615", doi: "10.1038/s41591-021-01283-z" },
      { authors: "Taquet M, Dercon Q, Luciano S, et al.", year: 2021, title: "Incidence, co-occurrence, and evolution of long-COVID features: A 6-month retrospective cohort study of 273,618 survivors of COVID-19", journal: "PLOS Medicine", volume: "18(9)", pages: "e1003773", doi: "10.1371/journal.pmed.1003773" },
      { authors: "Guedj E, Campion JY, Mundler O, et al.", year: 2021, title: "Hypometabolism in long COVID-19 patients: a FDG-PET study", journal: "European Journal of Nuclear Medicine and Molecular Imaging", volume: "48(9)", pages: "2823–2833", doi: "10.1007/s00259-021-05215-4" },
      { authors: "Bhatt SJ, Bhatt DL", year: 2023, title: "Serotonin, platelet factor 4, and the coagulation hypothesis of long-COVID", journal: "Cell", volume: "186(22)", pages: "4700–4702", doi: "10.1016/j.cell.2023.10.010" },
      { authors: "Hugon J, Msika EF, Queneau M, et al.", year: 2022, title: "Long COVID: cognitive complaints (brain fog) and dysfunction of the cingulate cortex", journal: "Journal of Neurology", volume: "269(1)", pages: "44–46", doi: "10.1007/s00415-021-10655-x" },
    ],
    tdcs: [
      { authors: "Lefaucheur JP, Antal A, Ayache SS, et al.", year: 2017, title: "Evidence-based guidelines on the therapeutic use of transcranial direct current stimulation (tDCS)", journal: "Clinical Neurophysiology", volume: "128(1)", pages: "56–92", doi: "10.1016/j.clinph.2016.10.087" },
      { authors: "Brunoni AR, Moffa AH, Sampaio-Junior B, et al.", year: 2017, title: "Trial of Electrical Direct-Current Therapy versus Escitalopram for Depression", journal: "New England Journal of Medicine", volume: "376(26)", pages: "2523–2533", doi: "10.1056/NEJMoa1612999" },
      { authors: "Fregni F, Boggio PS, Nitsche MA, et al.", year: 2006, title: "Treatment of major depression with transcranial direct current stimulation", journal: "Bipolar Disorders", volume: "8(2)", pages: "203–204", doi: "10.1111/j.1399-5618.2006.00291.x" },
    ],
    tps: [
      { authors: "Beisteiner R, Matt E, Fan C, et al.", year: 2020, title: "Transcranial pulse stimulation with ultrasound in Alzheimer's disease—A new navigated focal brain therapy", journal: "Advanced Science", volume: "7(3)", pages: "1902583", doi: "10.1002/advs.201902583" },
      { authors: "Fheodoroff K, Antenucci A, Bernhardt J, et al.", year: 2022, title: "Transcranial pulse stimulation in patients with mild Alzheimer's disease", journal: "Brain Stimulation", volume: "15(4)", pages: "932–934", doi: "10.1016/j.brs.2022.06.005" },
    ],
    tavns: [
      { authors: "Clancy JA, Mary DA, Witte KK, et al.", year: 2014, title: "Non-invasive vagus nerve stimulation in healthy humans reduces sympathetic nerve activity", journal: "Brain Stimulation", volume: "7(6)", pages: "871–877", doi: "10.1016/j.brs.2014.07.031" },
      { authors: "Pavlov VA, Tracey KJ", year: 2012, title: "The vagus nerve and the inflammatory reflex—linking immunity and metabolism", journal: "Nature Reviews Endocrinology", volume: "8(12)", pages: "743–754", doi: "10.1038/nrendo.2012.189" },
      { authors: "Hanna J, Knutsen JS, Hallett M", year: 2022, title: "Auricular transcutaneous vagal nerve stimulation for long COVID fatigue and autonomic dysfunction", journal: "Journal of Neurology", volume: "269(7)", pages: "3484–3487", doi: "10.1007/s00415-022-11027-7" },
      { authors: "Frangos E, Ellrich J, Komisaruk BR", year: 2015, title: "Non-invasive access to the vagus nerve central projections via electrical stimulation of the ear", journal: "Brain Stimulation", volume: "8(3)", pages: "624–636", doi: "10.1016/j.brs.2014.11.018" },
      { authors: "Bonaz B, Sinniger V, Hoffmann D, et al.", year: 2016, title: "Chronic vagus nerve stimulation in Crohn's disease: a 6-month follow-up pilot study", journal: "Neurogastroenterology & Motility", volume: "28(6)", pages: "948–953", doi: "10.1111/nmo.12792" },
    ],
    ces: [
      { authors: "Kirsch DL, Nichols F", year: 2013, title: "Cranial electrotherapy stimulation for treatment of anxiety, depression, and insomnia", journal: "Psychiatric Clinics of North America", volume: "36(1)", pages: "169–176", doi: "10.1016/j.psc.2013.01.006" },
      { authors: "Barclay TH, Barclay RD", year: 2014, title: "A clinical trial of cranial electrotherapy stimulation for anxiety and comorbid depression", journal: "Journal of Affective Disorders", volume: "164", pages: "171–177", doi: "10.1016/j.jad.2014.04.029" },
    ],
    network: [
      { authors: "Nauen DW, Hooper JE, Salvatore M, et al.", year: 2021, title: "Assessing brain capillaries in coronavirus disease 2019", journal: "JAMA Neurology", volume: "78(6)", pages: "760–762", doi: "10.1001/jamaneurol.2021.0225" },
      { authors: "Meinhardt J, Radke J, Dittmayer C, et al.", year: 2021, title: "Olfactory transmucosal SARS-CoV-2 invasion as a port of central nervous system entry in individuals with COVID-19", journal: "Nature Neuroscience", volume: "24(2)", pages: "168–175", doi: "10.1038/s41593-020-00758-5" },
      { authors: "Douaud G, Lee S, Alfaro-Almagro F, et al.", year: 2022, title: "SARS-CoV-2 is associated with changes in brain structure in UK Biobank", journal: "Nature", volume: "604(7907)", pages: "697–707", doi: "10.1038/s41586-022-04569-5" },
      { authors: "Srivastava A, Dasgupta A, Bhattacharyya S, et al.", year: 2022, title: "Neurological complications of COVID-19 and their potential mechanisms", journal: "European Journal of Neuroscience", volume: "56(9)", pages: "5590–5614", doi: "10.1111/ejn.15837" },
    ],
  },
};
