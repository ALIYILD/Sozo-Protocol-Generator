// SOZO FNON Clinical Protocol — Autism Spectrum Disorder (ASD)
// Document A — Partners Tier

module.exports = {
  conditionFull: "Autism Spectrum Disorder",
  conditionShort: "ASD",
  conditionSlug: "asd",
  documentNumber: "SOZO-FNON-ASD-001",

  offLabelCoverText:
    "All non-invasive brain stimulation (NIBS) applications described in this protocol for Autism Spectrum Disorder represent off-label use of CE-marked and FDA-cleared devices. The Newronika HDCkit, PlatoScience PlatoWork, NEUROLITH® TPS system, Soterix Medical taVNS, and Alpha-Stim AID are approved for specific indications that do not include ASD as a primary indication. Clinical application in ASD requires specialised neurodevelopmental expertise, individualized sensory assessment prior to NIBS (tolerance of electrode application, auditory environment), thorough caregiver involvement, and institutional ethics committee consideration for paediatric or minimally verbal participants. The evidence base for NIBS in ASD is preliminary (Level C), with emerging signals from rTMS and tDCS studies. All protocols must be individualised with careful sensory accommodation.",

  offLabelTable: [
    ["Device", "Cleared/Approved Indication", "ASD Off-Label Application", "Evidence Level"],
    ["Newronika HDCkit / PlatoWork", "Neurological rehabilitation (CE)", "Executive function, repetitive behaviours, social cognition", "Level C"],
    ["NEUROLITH® TPS", "Alzheimer's disease (CE)", "Prefrontal social-cognitive network, language network", "Level C"],
    ["Soterix taVNS / Alpha-Stim AID", "Epilepsy/anxiety/pain (CE/FDA)", "Autonomic dysregulation, anxiety, sensory overload, vagal tone", "Level C"],
  ],

  inclusionCriteria: [
    ["Confirmed ASD diagnosis per DSM-5 criteria (licensed clinician assessment; ADOS-2 and/or ADI-R supported)", "Age 12–55 years (protocol accommodations for age range)", "Level 1 or Level 2 ASD (sufficient cooperation for electrode application; verbal or AAC-augmented communication)", "Stable medication regimen for ≥3 months"],
    ["Primary presenting concern amenable to FNON: executive function deficit, anxiety, repetitive behaviours, or language-pragmatic impairment", "Caregiver/support person available for protocol support and home tasks", "Sensory tolerance assessment: tolerable to electrode gel application and mild electrical sensation (0.1 mA trial)", "Neuropsychological assessment at baseline (ADOS-2; SRS-2; BRIEF-2; AQ)"],
    ["FSIQ ≥50 or equivalent adaptive functioning for protocol comprehension (with accommodations)", "No acute psychiatric crisis", "No uncontrolled epilepsy (ASD has elevated seizure prevalence — EEG review required)", "Written informed consent (and assent where appropriate)"],
    ["Caregiver provides ASD-specific sensory profile (sensory-seeking or sensory-avoiding; sound/touch tolerance)", "Treatment environment adapted for ASD sensory needs (low noise, dimmed lighting, predictable routine)", "Goals of treatment documented collaboratively with participant and caregiver", "Baseline social communication, executive function, and anxiety measures completed"],
    ["Concurrent ASD-specific therapies documented (ABA, SLT, OT) — FNON adjunct to existing programme", "Neuroimaging (brain MRI) if available to rule out structural abnormality", "Documented baseline EEG if seizure history", "Clear informed consent for off-label experimental protocol"],
    ["Identified network target based on FNON assessment (social cognition / executive function / sensory regulation / language)", "Sensory desensitisation to NIBS environment completed over 1–2 preparatory sessions if needed", "Heat and skin sensitivity assessment (many ASD individuals have skin sensitivity)", "Psychiatrist or neurodevelopmentalist oversight confirmed"],
    ["Realistic treatment expectations discussed with participant and family", "Communication system established for reporting discomfort during protocol (verbal, AAC, signal)", "No plans to significantly change medication during protocol period", "MDT involvement confirmed (paediatrician/psychiatrist, neuropsychologist, OT, SLT)"],
  ],

  exclusionCriteria: [
    ["ASD Level 3 (requiring very substantial support) with inability to tolerate NIBS electrode placement despite adaptations", "Uncontrolled epilepsy or seizure disorder without stable AED therapy (ASD carries 20–30% comorbid epilepsy rate)", "Intracranial metal implants (DBS, cochlear implants, ferromagnetic clips)", "Active psychosis or severe psychiatric decompensation"],
    ["Cardiac pacemaker or implantable cardiac device", "Active suicidal ideation", "Pregnancy or breastfeeding", "Severe head wound or skull defect at electrode site"],
    ["Current participation in conflicting NIBS trial", "Severe behavioural dysregulation that cannot be managed to allow safe protocol administration", "Known hypersensitivity to conductive gel or electrode materials (after gel alternatives attempted)", "Absence of caregiver support for individuals unable to self-report adverse events"],
    ["Recent significant medication change within 3 months (may alter neuroplasticity baseline)", "Active severe inflammatory, autoimmune, or metabolic illness", "Claustrophobia or extreme anxiety preventing electrode application (after sensory desensitisation attempted)", "NIBS contraindicated by neurodevelopmental paediatrician or psychiatrist assessment"],
    ["History of malignant brain tumour", "Active substance use disorder", "Rett syndrome, Fragile X syndrome with severe hyperexcitability, or Angelman syndrome (distinct neurobiological substrates requiring separate protocols)", "Withdrawal from benzodiazepines or AED medications (seizure risk)"],
    ["Unable to maintain seated or lying position safely for protocol duration", "Severe skin disorder at electrode sites", "Uncontrolled tic disorder at severity level that precludes safe electrode placement", "Recent head trauma"],
    ["Botulinum toxin injection to head or neck within 3 months", "Deep cervical vagus nerve stimulator in place", "Open wounds or infections at electrode sites", "Clinician assessment: risk outweighs benefit for individual"],
    ["Age <12 years without specialised paediatric NIBS centre ethics approval", "Implanted intracochlear devices incompatible with electrical stimulation", "Severe hypotension or autonomic instability", "Catatonia variant in ASD (specialised psychiatric management required first)"],
  ],

  conditionsRequiringDiscussion: [
    ["Condition", "Clinical Consideration", "Recommended Action", "Protocol Adjustment"],
    ["Comorbid ADHD (very common in ASD, 30–80% co-occurrence)", "ADHD and ASD share DLPFC dysfunction; some protocol overlap; risk of over-stimulation", "Neuropsychological differentiation; prioritise dominant functional impairment", "Reduce tDCS session duration to 15 min initially; slower titration; taVNS for shared autonomic benefit"],
    ["Comorbid anxiety (70–80% ASD individuals)", "High anxiety prevalence in ASD; may be primary functional barrier; SN hyperactivation", "GAD-7 at baseline; psychiatric review; integrate anxiety protocol elements", "Prioritise taVNS + CES anxiety protocol; add right DLPFC (F4) anxiolytic tDCS component"],
    ["Comorbid epilepsy (20–30%)", "Elevated seizure risk in ASD; NIBS could lower seizure threshold in susceptible individuals", "Neurology/epileptology review; stable AED therapy required; EEG pre-protocol; defer if poorly controlled", "Lower tDCS intensity (1.0 mA max); avoid bilateral tDCS in active epilepsy; taVNS may have anti-seizure properties"],
    ["Minimal/limited verbal communication", "Difficulty reporting adverse events; requires robust non-verbal communication system", "Pre-establish clear signal system (hand raise, visual card); caregiver present throughout all sessions", "Shorter sessions (15 min max tDCS); monitor closely; titrate very slowly; home protocol limited"],
    ["Sensory hypersensitivity profile", "Tactile hypersensitivity to electrodes; auditory sensitivity to stimulator device sounds; visual sensitivity", "Sensory desensitisation preparatory sessions; electrode alternatives; earmuffs for sound; dim lighting", "taVNS earpiece may need custom fitting for ear canal sensitivity; CES earlobe clips may require gel tolerance trial"],
    ["High intellectual ability (PDA or 'masking' profile)", "Very high IQ ASD individuals may mask symptoms; report tolerance when distressed; FNON targets less obvious", "SRS-2 and AQ for autism features; BRIEF-2 executive function; subjective experience prioritised", "Full protocol with close monitoring; home taVNS may be feasible; participant drives goal-setting"],
    ["ASD with catatonia features", "Catatonic ASD episodes may be exacerbated or triggered; lorazepam-sensitive; separate from Parkinson's", "Psychiatrist assessment and management prior to NIBS; lorazepam trial first per NICE guidance", "Defer FNON protocol until catatonia resolved; cautious reintroduction with low-intensity taVNS only"],
    ["Female ASD (often later-diagnosed, masking profile)", "Social masking/camouflaging may mean different phenotypic presentation; anxiety often more prominent", "FNON phenotyping considers anxiety and social cognition domains; validate lived experience", "Emphasise anxiety/SN targets; incorporate psychological support; taVNS + CES primary"],
    ["ASD in intellectual disability (Level 2 co-occurring ID)", "Reduced capacity for informed consent; caregiver advocacy; altered neuroplasticity parameters unknown", "Ethics committee review; parent/guardian consent + participant assent; simplest protocol elements only", "taVNS only initially; CES with caregiver supervision; tDCS cautiously with single target; TPS deferred"],
  ],

  overviewParagraph:
    "Autism Spectrum Disorder (ASD) is a heterogeneous neurodevelopmental condition characterised by persistent deficits in social communication and social interaction, alongside restricted, repetitive patterns of behaviour, interests, or activities — with onset in the early developmental period and producing significant functional impairment. ASD affects approximately 1 in 36 children in the United States (CDC 2023) and is a lifelong condition with no pharmacological cure. The neural substrate of ASD has been characterised by converging evidence as a 'local over-connectivity, long-range under-connectivity' network pattern: hyper-connected local circuits producing sensory over-processing, rigid thinking, and repetitive behaviour, alongside under-connected long-range networks — particularly the social brain network (SBN) linking temporal-parietal junction, superior temporal sulcus, medial prefrontal cortex, and amygdala — producing social cognition and communication deficits. The SOZO FNON protocol for ASD targets these network-level abnormalities using an individualized, phenotype-driven multimodal NIBS approach, with taVNS for autonomic dysregulation and anxiety, tDCS for executive function and social cognition networks, and TPS for precise prefrontal and temporoparietal targeting. All protocols are adjunctive to existing ASD-specific therapies (ABA, SLT, OT) and require specialist sensory accommodation.",

  fnonNetworkParagraph:
    "The FNON framework for ASD is grounded in the 'network-level social brain hypothesis': ASD does not arise from a single-region deficit but from disrupted long-range functional connectivity across the social brain network (SBN), central executive network (CEN), and default mode network (DMN). Social cognition, theory of mind, and pragmatic communication depend on the coordinated activity of temporal-parietal junction (TPJ), superior temporal sulcus (STS), medial prefrontal cortex (mPFC), and amygdala — a network for mentalising and social perception. In ASD, this social brain network shows hypo-connectivity on functional MRI, particularly the mPFC-TPJ pathway mediating theory of mind. Simultaneously, the CEN (DLPFC-parietal working memory network) is hypoactivated during executive function tasks, producing the executive inflexibility, poor cognitive flexibility, and task-switching difficulty characteristic of ASD. The DMN — which mediates self-referential processing and perspective-taking — shows atypical organisation in ASD, with reduced mPFC-PCC connectivity. The Salience Network (SN) is hyperactivated in ASD, mediating sensory overload, interoceptive hypersensitivity, and anxiety amplification. FNON targets: tDCS upregulation of mPFC/DLPFC (social cognition + executive function); taVNS SN modulation for anxiety and sensory regulation; TPS for temporal-parietal precision targeting of social brain regions; CES for autonomic nervous system calming. This modular network framework is supported by Sporns & Betzel 2016 (1192 citations) and Lefaucheur et al. 2024 (63 citations).",

  networkDisorderParagraphs: [
    {
      network: "Default Mode Network (DMN)",
      paragraph:
        "The Default Mode Network in ASD shows atypical organisation that is one of the most replicated neuroimaging findings in the condition. Typically developing individuals show strong mPFC-PCC functional connectivity at rest and robust DMN activation during perspective-taking, social cognition, and theory of mind tasks. In ASD, mPFC-PCC connectivity is reduced, while local parietal DMN connectivity may be relatively preserved or increased — reflecting the broader local over-connectivity, long-range under-connectivity ASD network signature. The TPJ, a critical DMN-social brain overlap region for theory of mind and social perspective-taking, shows reduced activation in ASD during mentalising tasks (Reading the Mind in the Eyes; false-belief tasks). FNON approach: anodal tDCS targeting the mPFC (Fz) and bilateral TPJ (CP5/CP6 positions) to upregulate the hypo-connected DMN-social brain nodes; TPS temporal-parietal for precision targeting."
    },
    {
      network: "Central Executive Network (CEN)",
      paragraph:
        "The Central Executive Network (CEN) in ASD is characterised by reduced DLPFC activation during executive function tasks, impaired cognitive flexibility (set-shifting), and poor working memory updating — contributing to the restricted and repetitive behaviours seen in ASD through an inability to flexibly disengage from current states or behaviours. The CEN-DMN anticorrelation — typically, when CEN is active DMN deactivates and vice versa — is disrupted in ASD, with both networks showing simultaneous activation during cognitive tasks in some ASD individuals. This simultaneous CEN-DMN co-activation may reflect the difficulty ASD individuals have suppressing self-referential processing during externally-directed tasks. tDCS anodal DLPFC (F3/F4) upregulates CEN, potentially reducing repetitive behaviour frequency by improving behavioural flexibility, and improving working memory for social interaction. Evidence from tDCS in ASD executive function (Level C) is emerging."
    },
    {
      network: "Salience Network (SN)",
      paragraph:
        "The Salience Network in ASD — centred on the anterior insula and anterior cingulate cortex — shows a complex pattern of dysregulation: hyperactivation mediating sensory overload, interoceptive hypersensitivity, and anxiety, but with impaired switching between task-positive and task-negative states. The anterior insula, which mediates interoception (awareness of internal body states) and is critical for social-emotional processing, shows both structural and functional differences in ASD — with altered grey matter volume and atypical functional connectivity to amygdala and ACC. Sensory over-responsivity (one of the DSM-5 specifiers for ASD) is mediated by this hyperactive SN-insula circuit: ordinary sensory stimuli (sounds, textures, lights) generate exaggerated SN responses, producing distress and avoidance. taVNS is the primary FNON SN modulator: NTS projections to the insula and ACC reduce SN hyper-reactivity, supporting sensory regulation and anxiety reduction."
    },
    {
      network: "Sensorimotor Network (SMN)",
      paragraph:
        "The Sensorimotor Network in ASD shows a pattern of atypical sensorimotor integration that underpins motor clumsiness (affecting 50–80% of ASD individuals, formerly 'developmental coordination disorder' overlap), altered proprioception, and repetitive motor behaviours (stereotypies). M1 and SMA show altered connectivity with sensory cortex in ASD, and mirror neuron system function — which overlaps with the SMN at premotor cortex (BA 44) — has been hypothesised to contribute to the social cognition deficits in ASD, though this 'broken mirror theory' remains debated. Functionally, ASD motor impairments include hypotonia, dyspraxia, poor fine motor coordination, and gait differences. The SMN contributes to social engagement through gesture, imitation, and joint action. Occupational therapy paired with M1 tDCS may benefit motor coordination in ASD, though evidence is nascent."
    },
    {
      network: "Limbic Network",
      paragraph:
        "The Limbic Network in ASD — comprising amygdala, hippocampus, orbitofrontal cortex, and ACC — is central to the social and emotional features of ASD. The amygdala shows early over-growth in infancy in ASD (followed by normalisation) and exhibits atypical activation patterns: over-activation during social threat and unfamiliar face processing, with under-activation during explicit social cognition tasks. This amygdala dysregulation contributes to both anxiety (the most common ASD comorbidity, 70–80%) and social avoidance — the amygdala over-responds to social novelty, producing aversive associations with social interaction that reinforce avoidance. Hippocampal differences in ASD affect episodic and semantic memory for social information. taVNS modulates the amygdala via NTS-LC-amygdala pathways, reducing amygdala hyperactivation and anxiety; combined with CES for tonic autonomic calming."
    },
    {
      network: "Attention Network",
      paragraph:
        "The Attention Network in ASD shows a characteristic profile: enhanced local (detail-focused) attention within narrow interest domains alongside impaired global, social, and joint attention. Joint attention — the ability to share attentional focus with another person toward an object or event, mediated by the right TPJ and superior temporal sulcus — is a defining early marker of ASD and is supported by the social brain network-attention network interface. The right inferior frontal gyrus, a key attention network node, also mediates response inhibition, imitation, and mirror neuron function — all impaired in ASD. Superior parietal lobule hypo-connectivity in ASD impairs top-down attentional control and contributes to attentional inflexibility. FNON attention targets: right TPJ/parietal tDCS; TPS temporal-parietal precision; taVNS for orienting system modulation."
    },
  ],

  networkCitationKeys: [
    { authors: "Sporns & Betzel", year: 2016, citations: 1192, title: "Modular Brain Networks", doi: "" },
    { authors: "Lefaucheur et al.", year: 2024, citations: 63, title: "Neuromodulation techniques – From non-invasive to deep brain stimulation", doi: "" },
  ],
  fnonEvidenceStrength: "Emerging",

  pathophysiologyText:
    "ASD pathophysiology is genetically heterogeneous, with >100 high-confidence ASD risk genes identified through GWAS and exome studies (SFARI Gene database; Satterstrom 2020), converging on synaptic function (SHANK3, SYNGAP1, NRXN1), transcriptional regulation (CHD8, ADNP, TBR1), and chromatin remodelling pathways. The unifying neural mechanism — despite genetic heterogeneity — appears to be an imbalance between excitation (E) and inhibition (I) in cortical circuits: elevated E/I ratio in local circuits, driven by reduced GABAergic interneuron function and excess glutamatergic excitation, produces the sensory over-responsivity, local hyper-connectivity, and seizure susceptibility characteristic of ASD. Long-range cortical connectivity is disrupted by deficient white matter development (DTI studies show reduced mean diffusivity in arcuate fasciculus, corpus callosum, and uncinate fasciculus connecting frontal social cognition regions with temporal social perception regions). The social brain network (SBN) — connecting superior temporal sulcus, temporal-parietal junction, medial prefrontal cortex, and amygdala — develops under the influence of social experience and mirror neuron activity in infancy and toddlerhood; in ASD, early reduction in social attention (gaze, social orienting) produces a cascade of under-stimulated SBN synaptic development. Additionally, autonomic nervous system dysregulation — reduced heart rate variability, elevated sympathetic tone, reduced vagal tone — is increasingly recognised as a core ASD feature, not merely a comorbidity, underlying anxiety, interoceptive differences, and social-emotional regulation deficits. taVNS directly targets this autonomic substrate.",

  cardinalSymptoms: [
    ["Domain", "Primary Symptoms", "Network Basis", "FNON Target"],
    ["Social Communication Deficits", "Reduced eye contact initiation; pragmatic language impairment; difficulty with back-and-forth conversation; limited affect sharing", "Social brain network hypo-connectivity (STS-mPFC-TPJ); DMN social cognition impairment", "Anodal mPFC (Fz); TPS right TPJ; TPS STS (temporal precision)"],
    ["Social Cognition / Theory of Mind", "Difficulty inferring mental states of others; literal interpretation; alexithymia; reduced empathy response", "TPJ-mPFC hypo-connectivity; reduced right hemisphere social processing; DMN mentalising network", "TPS temporal-parietal (TPJ/STS); anodal F4 (right DLPFC for social cognition)"],
    ["Repetitive Behaviours (RRBs)", "Motor stereotypies; insistence on sameness; restricted interests; ritualistic behaviour; sensory-seeking behaviours", "CEN inflexibility (DLPFC set-shifting deficit); over-active local motor-frontal circuits; BG-thalamo-cortical loop", "Anodal DLPFC (F3/F4); cathodal SMA (Cz) for motor stereotypy; TPS prefrontal flexibility"],
    ["Sensory Over-Responsivity", "Auditory hypersensitivity; tactile avoidance; visual over-sensitivity; vestibular/proprioceptive differences", "SN anterior insula hyperactivation; E/I imbalance local sensory cortex; reduced cortical habituation", "taVNS (SN modulation primary); CES tonic ANS calming; S1 cathodal tDCS for allodynia"],
    ["Executive Function Deficits", "Poor cognitive flexibility; perseveration; difficulty with planning and initiation; poor inhibitory control; working memory impairment", "CEN DLPFC hypoactivation; DLPFC-PFC-striatum loop inefficiency; ACC conflict monitoring deficit", "Anodal DLPFC bilateral (F3/F4); TPS prefrontal; CogMed concurrent training"],
    ["Anxiety / Autonomic Dysregulation", "High anxiety prevalence (70–80%); social anxiety; separation anxiety; GAD; reduced HRV; elevated resting sympathetic tone", "SN hyperactivation; amygdala over-reactivity; reduced vagal tone (low RMSSD); autonomic sympathovagal imbalance", "taVNS (primary — vagal tone restoration); CES (tonic ANS calm); anodal F4 (right DLPFC anxiolytic)"],
    ["Language / Communication", "Delayed language development; echolalia; pragmatic language impairment; prosody differences; AAC dependency in some", "Arcuate fasciculus under-connectivity; left STS-IFG language network; Broca-Wernicke disconnection", "Anodal F5/F3 (Broca area); TPS left IFG/STS language network; concurrent SLT"],
    ["Motor Coordination", "Developmental dyspraxia; hypotonia; motor stereotypies; gait differences; poor fine motor control", "SMN motor cortex-cerebellum-basal ganglia loop; premotor cortex E/I imbalance", "M1 anodal tDCS + OT concurrent; TPS motor; taVNS for motor learning augmentation"],
    ["Sleep Disturbance", "Prevalence 50–80% in ASD; sleep-onset insomnia; non-24-hour rhythm; night waking; melatonin deficiency common", "Circadian rhythm dysregulation; reduced melatonin synthesis; hyperarousal preventing sleep initiation", "CES evening protocol (primary sleep intervention); taVNS for circadian reset; FNON sleep phenotype"],
  ],

  standardGuidelinesText: [
    "ASD management follows NICE guidelines NG142 (2021) and DSM-5-TR diagnostic criteria, with internationally recognised best practice from the Autism Evidence-Based Practice Review Group (AEFP). There is no approved pharmacological treatment for core ASD features (social communication deficits, repetitive behaviours). Evidence-based interventions target associated symptoms and functional participation.",
    "Applied Behaviour Analysis (ABA) and its derivatives (EIBI, JASPER, PECS, PRT) have the strongest evidence base for improving adaptive behaviours, communication, and reducing interfering behaviours in early childhood ASD (NICE NG142, Level A for early intensive behavioural intervention). Social Skills Training (SST) programmes have Level B evidence for social competence in higher-functioning ASD adolescents and adults.",
    "Speech and Language Therapy (SLT) for communication, pragmatic language, and AAC (Augmentative and Alternative Communication) development is recommended for all ASD individuals with communication needs (NICE NG142). Occupational Therapy (OT) for sensory integration, fine motor, and adaptive skills has Level B evidence. Parent-mediated interventions (Hanen More Than Words, PECS) have Level A evidence for parent-child interaction outcomes.",
    "Pharmacological management targets comorbid symptoms: risperidone and aripiprazole are FDA-approved for irritability/aggression in ASD (Level A). Methylphenidate and atomoxetine for comorbid ADHD have Level B evidence. SSRIs for ASD anxiety have mixed evidence — the MECA and SOFIA trials showed limited core ASD benefit but may reduce anxiety. Melatonin has Level A evidence for ASD sleep-onset insomnia.",
    "Sensory integration approaches, though widely used, have been controversial in evidence quality; systematic reviews show emerging positive evidence for sensory-based occupational therapy (Schaaf et al. 2018, Level B). Social Stories™ have Level C evidence for social behaviour understanding. Video modelling has Level B evidence for communication and social skills.",
    "Mental health comorbidities in ASD require adapted cognitive behavioural therapy (CBT-ASD adaptations): modified CBT with visual supports, concrete language, reduced metaphor use, and caregiver involvement has Level B evidence for ASD anxiety (Wood et al. 2009; Sofronoff et al. 2005). Mindfulness-based interventions show emerging positive evidence for ASD adults.",
    "NIBS in ASD: No NIBS modality is currently approved or recommended in national guidelines for core ASD features. Emerging evidence (small sham-controlled studies) suggests: rTMS over DLPFC may reduce repetitive behaviours (Wassermann & Lisanby 2001; Sokhadze 2012); cathodal tDCS over DLPFC reduced repetitive behaviours in small studies (D'Urso 2015; Costanzo 2020); taVNS for ASD anxiety has theoretical rationale and case series support. FNON protocols represent experimental clinical practice requiring individual ethics review.",
  ],

  fnonFrameworkParagraph:
    "The SOZO FNON framework for ASD is centred on the 'Social Brain Network Connectivity Enhancement' model: ASD produces long-range hypo-connectivity of the social brain network (SBN) alongside local hyper-connectivity and E/I imbalance. FNON targets upregulate hypo-connected SBN nodes (mPFC, DLPFC for social cognition, TPJ for mentalising) while taVNS modulates the hyperactive SN driving sensory overload and anxiety. Unlike pharmacological approaches, FNON does not aim to change the core neurodevelopmental signature of ASD — it aims to modulate functional network states that are contributing to measurable functional impairment (anxiety, executive dysfunction, sensory dysregulation, communication barriers) and to amplify the neuroplasticity that supports ASD-specific therapies (SLT, OT, social skills training). The S-O-Z-O sequence for ASD: Stabilise sensory/autonomic state with taVNS and CES (essential first step for ASD individuals who are often in a dysregulated state before any cognitive intervention); Optimise DLPFC excitability with tDCS during therapeutic tasks; Zone-target social brain network nodes with TPS; Outcome consolidation with CES during quiet relaxation or preferred sensory activity. All sessions require high-level sensory accommodation and participant-centred adaptation.",

  keyBrainRegions: [
    ["Brain Region", "Function", "ASD Pathology", "FNON Intervention"],
    ["Medial Prefrontal Cortex (mPFC)", "Self-referential processing, mentalising, theory of mind, DMN hub, social prediction", "Hypo-activated during social cognition tasks; reduced mPFC-PCC connectivity; social prediction impairment", "Anodal tDCS Fz (mPFC); TPS mPFC neuro-navigation guided"],
    ["Dorsolateral Prefrontal Cortex (DLPFC)", "Working memory, cognitive flexibility, top-down social attention, executive control, inhibitory control", "Hypoactivated during executive tasks; reduced CEN-DMN anticorrelation; repetitive behaviour linked", "Anodal tDCS F3/F4 (bilateral); TPS DLPFC; concurrent executive function training"],
    ["Temporal-Parietal Junction (TPJ)", "Theory of mind, attribution of mental states, social attention orienting, self-other distinction", "Hypo-activated during mentalising tasks; reduced mPFC-TPJ connectivity; associated with ToM impairment", "TPS right TPJ (CP6 position, neuro-navigation); anodal tDCS right temporal-parietal region"],
    ["Superior Temporal Sulcus (STS)", "Biological motion perception, gaze processing, voice recognition, social perception, language", "Reduced grey matter and functional activation; STS hypo-activation during biological motion; STS-amygdala disconnect", "TPS left/right STS neuro-navigation; anodal temporal tDCS (T3/T4)"],
    ["Amygdala", "Threat detection, social-emotional learning, fear conditioning, social salience, gaze-direction", "Atypical early over-growth; amygdala hyperactivation to unfamiliar faces; anxiety amplification; social avoidance", "taVNS (NTS→LC→amygdala modulation — primary); CES autonomic calming"],
    ["Anterior Insula", "Interoception, body-self, SN hub, social-emotional experience, empathy, sensory integration", "ASD-specific interoceptive impairment; insula E/I imbalance; central role in sensory over-responsivity", "taVNS (NTS-insula pathway modulation); cathodal Cz for SN/insula hyperactivation reduction"],
    ["Anterior Cingulate Cortex (ACC)", "Error monitoring, conflict detection, social pain, autonomic regulation, reward for social interaction", "Reduced activation during error-monitoring in ASD; reduced social pain neural response", "taVNS (NTS→ACC pathway); cathodal Fz (reduce hyperactive ACC anxiety component)"],
    ["Broca's Area (IFG, BA 44/45)", "Language production, syntax, semantic processing, phonological loop, mirror neuron area, pragmatic inference", "Reduced left IFG-STS connectivity (arcuate fasciculus); pragmatic language impairment; literal processing bias", "Anodal tDCS F5/F3 (left DLPFC-IFG); TPS left IFG language network; concurrent SLT"],
    ["Cerebellum", "Motor coordination, predictive coding, error correction, timing, social timing/rhythm, implicit learning", "Cerebellar atrophy in ASD (Courchesne 1988); Purkinje cell loss; cerebellar-cortical timing disruption", "TPS cerebellar (motor/coordination component); taVNS cerebello-vagal; OT concurrent"],
  ],

  additionalBrainStructures: [
    ["Structure", "ASD-Specific Role", "Clinical Relevance", "FNON Consideration"],
    ["Arcuate Fasciculus", "Connects Broca's area (IFG) with Wernicke's area (STS) — core language pathway; also social communication", "Reduced mean diffusivity on DTI in ASD; associated with language delay and pragmatic impairment", "DLPFC-temporal tDCS indirectly promotes AF-mediated fronto-temporal connectivity; TPS along language network"],
    ["Corpus Callosum (Genu/Body)", "Interhemispheric transfer of social and language information; right-left social brain integration", "Corpus callosum size and connectivity differences in ASD; genu reduction linked to social cognition deficit", "Bilateral tDCS targeting may promote interhemispheric integration; TPS midline cautiously"],
    ["Uncinate Fasciculus", "Connects orbitofrontal cortex with amygdala-temporal social brain regions; social-emotional regulation", "Reduced uncinate fasciculus integrity in ASD; ASD social-emotional dysregulation substrate", "taVNS indirectly modulates amygdala-OFC pathway via NTS-LC pathway; anodal OFC (Fp1/Fp2) experimental"],
    ["Striatum / Basal Ganglia", "Reward processing (social reward), habit learning, motor routine, perseveration, repetitive behaviour circuit", "ASD striatum hypo-responsive to social reward; BG-thalamo-cortical loop implicated in RRBs; dopaminergic differences", "Anodal DLPFC tDCS modulates BG-thalamo-cortical loop indirectly; social reward training during tDCS"],
    ["Thalamus", "Relay hub for all sensory modalities; gating sensory input to cortex; thalamo-cortical filtering", "ASD thalamic over-relay — reduced sensory gating allowing excessive sensory throughput to cortex (sensory overload)", "taVNS thalamocortical normalisation via NTS thalamic projections; indirect sensory gating modulation"],
    ["Fusiform Face Area (FFA)", "Face identity recognition; face perception; gaze direction coding; part of social brain", "Reduced FFA activation during face processing in ASD; preferential object-over-face processing", "TPS occipitotemporal (experimental FFA targeting); concurrent face recognition training"],
    ["Locus Coeruleus (LC)", "Norepinephrine source; arousal regulation; attention; novelty detection; autonomic gating", "ASD LC-NE dysregulation contributes to hyperarousal, attention difficulties, and anxiety", "taVNS directly targets NTS→LC→NE pathway — primary noradrenergic modulation mechanism"],
  ],

  keyFunctionalNetworks: [
    ["Network", "Key Nodes", "ASD Dysfunction Pattern", "NIBS Modality", "Expected Outcome"],
    ["Social Brain Network (SBN)", "mPFC (Fz), TPJ (CP5/CP6), STS (T3/T4), amygdala, FFA", "Long-range hypo-connectivity; mPFC-TPJ disconnection; STS hypo-activation during social perception", "TPS right TPJ + STS; anodal mPFC (Fz) tDCS; TPS left IFG (language SBN)", "Improved theory of mind (RMET); social communication ratings (SRS-2); SLT outcomes"],
    ["Central Executive Network (CEN)", "DLPFC bilateral (F3/F4), posterior parietal, dorsal ACC", "DLPFC hypoactivation during executive tasks; reduced cognitive flexibility; CEN-DMN co-activation", "Bilateral anodal DLPFC tDCS (F3/F4); TPS DLPFC; concurrent executive function training", "Reduced RRB frequency (RBS-R); improved BRIEF-2 scores; cognitive flexibility tests"],
    ["Default Mode Network (DMN)", "mPFC, PCC, TPJ, hippocampus", "Reduced mPFC-PCC connectivity; DMN-social brain overlap impaired; atypical DMN organisation", "CES (DMN normalisation); anodal mPFC tDCS; TPS TPJ", "Social cognition improvement; reduced self-focused perseveration; memory for social information"],
    ["Salience Network (SN)", "Anterior insula, ACC, amygdala, thalamus", "Hyperactivation mediating sensory over-responsivity; anxiety amplification; social novelty aversion", "taVNS (primary SN modulator via NTS); CES (tonic ANS calm); cathodal Cz optional", "Reduced sensory over-responsivity (SOR questionnaire); GAD-7 anxiety; HRV improvement"],
    ["Limbic Network", "Amygdala, hippocampus, OFC, ACC, insula", "Amygdala hyperactivation (social threat); OFC reward dysregulation; hippocampal social memory impairment", "taVNS amygdala modulation; CES anxiolytic; anodal F3 (DLPFC-OFC circuit); TPS hippocampal", "Reduced anxiety (GAD-7, SCARED); improved emotional regulation; social memory"],
    ["Language Network", "Left IFG (Broca), left STS (Wernicke), arcuate fasciculus, left DLPFC", "Arcuate fasciculus under-connectivity; left STS-IFG disconnection; pragmatic language impairment", "Anodal F5/F3 tDCS (left IFG); TPS left IFG + STS; concurrent SLT", "CELF-5 language scores; pragmatic language ratings; MLU in spontaneous speech"],
    ["Attention Network", "Right IFG, right TPJ, IPS, FEF, STS (social attention)", "Right TPJ hypo-activation impairing joint attention; social orienting deficit; attentional inflexibility", "TPS right TPJ + IPS; anodal F4 + P4 tDCS; taVNS orienting system", "Joint attention measures (ESCS); PASAT; attentional flexibility tasks"],
  ],

  networkAbnormalities:
    "ASD network abnormalities follow the 'local over-connectivity, long-range under-connectivity' model, with the most consistent finding being reduced resting-state functional connectivity between prefrontal cortex and temporal regions mediating social cognition. The DMN shows atypical organisation: mPFC-PCC connectivity is reduced (long-range component), while within-parietal or within-frontal DMN connectivity may be relatively preserved or increased. SN hyper-connectivity within local insula-ACC circuits drives sensory overload and anxiety. The social brain network — which is only weakly delineated from the DMN in task-negative states — shows systematic long-range under-connectivity in ASD. The CEN shows reduced resting-state amplitude and task-related hypoactivation during executive function. White matter DTI consistently identifies reduced arcuate fasciculus and corpus callosum integrity. The E/I imbalance (elevated local cortical excitation relative to GABAergic inhibition) produces elevated intrinsic gamma-band oscillations on EEG, reduced alpha-band amplitude, and altered mismatch negativity (MMN) — all biomarkers of ASD cortical processing differences. FNON protocols account for the E/I context: tDCS at ASD-appropriate intensities (not above 2 mA) to avoid exacerbating local over-excitability while upregulating long-range network connectivity.",

  conceptualFramework:
    "The SOZO FNON conceptual framework for ASD is the 'Social Network Connectivity Enhancement with Autonomic Stabilisation' model. ASD is conceptualised as producing two parallel network problems: (1) Social brain network long-range hypo-connectivity — the SBN nodes cannot communicate efficiently, impairing theory of mind, social perception, and pragmatic communication; (2) SN hyperactivation and autonomic sympathovagal imbalance — the ASD nervous system is chronically over-sensitised, producing anxiety, sensory overload, and reduced capacity for social engagement even when SBN connectivity is upregulated. FNON therefore operates on both tracks simultaneously: taVNS and CES Stabilise the autonomic state (Track 1 — prerequisite), then tDCS and TPS Optimise and Zone social brain network nodes (Track 2 — social cognition upregulation). The S-O-Z-O sequence in ASD is: Stabilise with taVNS (10–15 min, mandatory pre-session); Optimise DLPFC/mPFC with tDCS during SLT or social skills task; Zone with TPS right TPJ or left IFG depending on phenotype; Outcome consolidation with CES and preferred sensory calming activity. All NIBS is adjunctive to evidence-based ASD therapies — the stimulation amplifies plasticity during targeted therapy, not as a standalone intervention.",

  clinicalPhenotypes: [
    ["Phenotype", "Core Feature", "Network Priority"],
    ["Social Cognition / ToM Deficit (ASD Level 1)", "Theory of mind impairment; social misattribution; difficulty inferring mental states; social isolation", "SBN (mPFC, TPJ — right hemisphere); DMN mentalising"],
    ["Executive Inflexibility / RRB-Dominant", "Rigid behaviour patterns; insistence on sameness; high RBS-R score; poor cognitive flexibility; perseveration", "CEN (bilateral DLPFC); BG-thalamo-cortical loop"],
    ["Anxiety-Dominant ASD", "Anxiety as primary functional barrier; social anxiety; separation anxiety; GAD features; school refusal", "SN (taVNS primary); Limbic (amygdala); right DLPFC (F4) anxiolytic"],
    ["Language / Pragmatic Communication Focus", "Expressive/receptive language delay; pragmatic impairment; echolalia; AAC user", "Language network (left IFG, STS); arcuate fasciculus; Broca-Wernicke"],
    ["Sensory Over-Responsivity / Regulation", "Sensory meltdowns; auditory/tactile hypersensitivity; avoidance behaviours; proprioceptive seeking", "SN anterior insula (taVNS primary); CES tonic ANS; S1 gating"],
    ["Sleep Disturbance Dominant", "Sleep-onset insomnia; circadian dysregulation; non-restorative sleep; impact on daytime behaviour", "CES evening (primary); taVNS circadian-sleep pathway; melatonin concurrent"],
    ["Comorbid ADHD-ASD (Dual Diagnosis)", "Combined ASD + ADHD features; inattentive; impulsive; hyperactive; working memory dual impairment", "CEN (DLPFC bilateral); SN; taVNS noradrenergic"],
    ["Motor-Dyspraxic ASD", "Gross and fine motor dyspraxia; hypotonia; motor stereotypies; OT referral; gait differences", "SMN (M1/SMA); cerebellum; TPS motor; concurrent OT"],
    ["Minimally Verbal / AAC-Supported ASD", "Limited speech; AAC-dependent; possible intellectual disability; ASD Level 2/3 features", "Language network conservative protocol; taVNS + CES primary; tDCS low-intensity with caution"],
  ],

  symptomNetworkMapping: [
    ["Symptom", "Primary Network", "Key Nodes", "tDCS", "taVNS/CES"],
    ["Social isolation / ToM deficit", "SBN", "Right TPJ, mPFC, STS", "Anodal Fz (mPFC) + right temporal-parietal", "taVNS (NTS→social brain via LC-NE)"],
    ["Repetitive behaviours (RRBs)", "CEN + BG loop", "DLPFC bilateral, SMA, striatum", "Anodal F3/F4 (DLPFC bilateral) or cathodal SMA (Cz)", "CES (reduce perseverative arousal)"],
    ["Sensory over-responsivity", "SN + S1", "Anterior insula, ACC, thalamus", "Cathodal S1 optional (allodynia); cathodal Cz (SN)", "taVNS primary + CES (tonic ANS calm)"],
    ["Anxiety / autonomic dysregulation", "SN + Limbic", "Amygdala, insula, ACC, DLPFC (F4)", "Anodal F4 (right DLPFC anxiolytic)", "taVNS bilateral + CES (primary anxiolytics)"],
    ["Executive inflexibility / cognitive set-shifting", "CEN", "DLPFC bilateral, ACC, BG", "Bilateral anodal DLPFC (F3+F4, 1.0 mA each)", "CES during cognitive flexibility training"],
    ["Language / pragmatic impairment", "Language network", "Left IFG (F5), STS (T3), arcuate fasciculus", "Anodal left F3/F5 (Broca area)", "taVNS NTS→LC→NE (noradrenergic language augmentation)"],
    ["Sleep onset insomnia", "Circadian + ANS", "SCN, pineal, LC, thalamus", "Cathodal Cz (evening SMA/DMN calming)", "CES 0.5 Hz 100 µA 60 min pre-sleep (primary)"],
    ["Emotional dysregulation / meltdowns", "Limbic + SN", "Amygdala, insula, ACC", "Cathodal Fz (reduce ACC hyperactivation)", "taVNS + CES (immediate autonomic de-escalation)"],
    ["Joint attention deficit", "Attention + SBN", "Right TPJ, STS, IPS, FEF", "Anodal right F4 + P4 (right hemisphere attention-social)", "TPS right TPJ (precision social attention targeting)"],
    ["Motor coordination / dyspraxia", "SMN", "M1, SMA, cerebellum, premotor", "Anodal M1 (C3/C4) + concurrent OT", "taVNS cerebello-vagal; TPS motor"],
  ],

  montageSelectionRows: [
    ["Target", "Montage"],
    ["Social cognition / mPFC (SBN)", "Anode: Fz (mPFC) — Cathode: Inion (occipital reference) | 1.5 mA, 15–20 min | concurrent social skills training"],
    ["Right TPJ / social attention", "Anode: CP6 (right TPJ) — Cathode: left supraorbital | 1.5 mA, 15–20 min | concurrent SLT social tasks"],
    ["Bilateral DLPFC / executive function", "Dual anode: F3 + F4 — Reference: Cz or mastoids | 1.0 mA per channel | concurrent executive function training"],
    ["Left IFG / language network", "Anode: F5 or F3 (left IFG/DLPFC) — Cathode: right supraorbital | 1.5 mA, 15 min | concurrent SLT language tasks"],
    ["Right DLPFC / anxiolytic", "Anode: F4 (right DLPFC) — Cathode: left supraorbital | 1.5 mA, 20 min | anxiety reduction protocol"],
    ["SMA cathodal / RRB reduction", "Cathode: Cz (SMA/pre-SMA) — Anode: bilateral mastoids | 1.5 mA, 15 min | behaviour therapy concurrent"],
    ["taVNS standard (all ASD phenotypes)", "Left cymba conchae auricular taVNS | 0.3–0.5 mA, 200 µs, 25 Hz | 10–15 min pre-session | essential first step"],
    ["CES anxiolytic / sleep (ASD)", "Alpha-Stim AID bilateral earlobe | 100 µA, 0.5 Hz | 20–60 min | pre-sleep or post-session | caregiver supervised"],
    ["TPS right TPJ (social brain precision)", "NEUROLITH® TPS CP6 (right TPJ) | 0.20–0.25 mJ/mm², 2500–3000 pulses | neuro-navigation guided"],
    ["TPS left IFG / language", "NEUROLITH® TPS F5 region (left IFG/Broca) | 0.20 mJ/mm², 2500 pulses | concurrent SLT"],
    ["S1 cathodal / sensory gating (allodynia)", "Cathode: C3/C4 contralateral to dominant sensory hypersensitivity | 1.0 mA, 15 min | sensory desensitisation concurrent"],
    ["Temporal tDCS (STS region)", "Anode: T3 or T4 (STS region) — Cathode: contralateral supraorbital | 1.5 mA, 15–20 min | biological motion training"],
    ["Cathodal Fz (ACC anxiety reduction)", "Cathode: Fz (ACC/mPFC) — Anode: mastoids bilateral | 1.0 mA, 15 min | for ACC hyperactivation in ASD anxiety"],
  ],

  polarityPrincipleText:
    "In ASD, polarity selection for tDCS requires careful consideration of the E/I imbalance underpinning cortical hyperexcitability. Anodal tDCS increases cortical excitability — beneficial for hypo-connected long-range social brain network nodes (mPFC, DLPFC, TPJ) where upregulation supports social cognition and executive function. However, excessively high anodal intensity risks aggravating local over-connectivity and E/I imbalance; therefore, tDCS intensities are capped at 1.5–2.0 mA in ASD and session duration may be shortened to 15 minutes initially. Cathodal tDCS is used to reduce hyperexcitable local circuits: cathodal SMA (Cz) reduces the motor circuit overactivation driving repetitive motor behaviours; cathodal S1 reduces somatosensory hyperexcitability contributing to tactile over-responsivity; cathodal ACC (Fz) may reduce the conflict monitoring hyperactivation driving anxiety and compulsive-repetitive cycles. Right DLPFC (F4) anodal stimulation is preferred for anxiety in ASD (same anxiolytic polarity as in GAD) rather than left DLPFC upregulation, which may increase rumination in some ASD profiles. taVNS uses neither anodal nor cathodal DC; it modulates the NTS-autonomic-limbic axis, reducing amygdala hyperactivation and SN over-reactivity without the E/I polarity risks of DC stimulation — making it particularly safe as the first-line and pre-session FNON component in ASD.",

  polarityTable: [
    ["Target", "Polarity", "Effect", "Primary Indication", "Evidence Level"],
    ["mPFC (Fz)", "ANODAL", "Upregulates social cognition network; enhances mentalising and perspective-taking circuitry", "ASD social cognition deficit; ToM impairment; SBN hypo-connectivity", "Level C (ASD specific); Level B (mPFC tDCS social cognition literature)"],
    ["DLPFC F3/F4 bilateral", "ANODAL", "Upregulates CEN; increases cognitive flexibility; reduces perseverative executive patterns", "RRB-dominant ASD; executive inflexibility; CEN hypoactivation", "Level C (D'Urso 2015; Costanzo 2020 — ASD tDCS)"],
    ["Right DLPFC F4", "ANODAL", "Anxiolytic; reduces right-hemisphere emotional reactivity to social threat; prefrontal inhibition of amygdala", "ASD anxiety; social anxiety; right amygdala hyperactivation", "Level C — extrapolated from anxiety literature; ASD-specific case series"],
    ["SMA / pre-SMA (Cz)", "CATHODAL", "Reduces motor circuit overactivation; decreases repetitive motor stereotypies; reduces motor perseveration", "Motor stereotypies; repetitive motor behaviours; SMA overactivation", "Level C — ASD motor stereotypy tDCS literature"],
    ["S1 Somatosensory (C3/C4)", "CATHODAL", "Reduces somatosensory cortex hyperexcitability; tactile allodynia; sensory gating enhancement", "Tactile hypersensitivity; sensory over-responsivity; ASD tactile avoidance", "Level C — sensory cortex tDCS; ASD sensory case series"],
  ],

  classicTdcsProtocols: [
    {
      code: "C1",
      name: "Standard Anodal mPFC Social Cognition Protocol",
      montage: "Anode Fz (mPFC) — Cathode inion",
      intensity: "1.5 mA",
      duration: "15–20 minutes",
      sessions: "10 sessions concurrent with social skills training",
      indication: "ASD social cognition deficit, theory of mind impairment, social brain network upregulation",
      evidence: "Level C — tDCS social cognition literature (Santiesteban 2012); ASD-adjacent"
    },
    {
      code: "C2",
      name: "Standard Left DLPFC Executive Protocol",
      montage: "Anode F3 (left DLPFC) — Cathode right supraorbital",
      intensity: "1.5 mA",
      duration: "15–20 minutes",
      sessions: "10 sessions concurrent with cognitive flexibility training",
      indication: "ASD executive inflexibility, RRB reduction, CEN upregulation",
      evidence: "Level C — D'Urso 2015 (ASD tDCS RRBs); Costanzo 2020"
    },
    {
      code: "C3",
      name: "Standard Right DLPFC Anxiolytic Protocol",
      montage: "Anode F4 (right DLPFC) — Cathode left supraorbital",
      intensity: "1.5 mA",
      duration: "15–20 minutes",
      sessions: "10 sessions",
      indication: "ASD anxiety, social anxiety, right hemisphere anxiolytic",
      evidence: "Level C — right DLPFC anxiolytic extrapolation from GAD literature"
    },
    {
      code: "C4",
      name: "Standard Bilateral DLPFC Protocol",
      montage: "Dual anode F3 + F4 — Reference Cz",
      intensity: "1.0 mA per channel",
      duration: "15 minutes",
      sessions: "10 sessions",
      indication: "Bilateral CEN upregulation; combined executive + social cognition targets in ASD",
      evidence: "Level C — bilateral tDCS methodology; ASD expert consensus"
    },
    {
      code: "C5",
      name: "Standard Cathodal SMA RRB Protocol",
      montage: "Cathode Cz (SMA) — Anode bilateral mastoids",
      intensity: "1.5 mA",
      duration: "15 minutes",
      sessions: "10 sessions",
      indication: "Motor stereotypies, repetitive motor behaviours, SMA overactivation in ASD",
      evidence: "Level C — SMA cathodal tDCS ASD stereotypy literature"
    },
    {
      code: "C6",
      name: "Standard Left Temporal Language Protocol",
      montage: "Anode F5/T3 (left IFG/STS region) — Cathode right supraorbital",
      intensity: "1.5 mA",
      duration: "15 minutes",
      sessions: "10 sessions concurrent with SLT",
      indication: "ASD language network upregulation; pragmatic language impairment; arcuate fasciculus targeting",
      evidence: "Level C — tDCS language networks; ASD SLT augmentation case series"
    },
    {
      code: "C7",
      name: "Standard CES Evening Sleep Protocol",
      montage: "Alpha-Stim AID bilateral earlobe clips — 100 µA, 0.5 Hz modified square wave",
      intensity: "100 µA",
      duration: "40–60 minutes pre-sleep",
      sessions: "Daily × 3 weeks; then maintenance 3×/week",
      indication: "ASD sleep-onset insomnia; hyperarousal preventing sleep; circadian dysregulation",
      evidence: "Level C — CES sleep literature; ASD sleep management consensus"
    },
    {
      code: "C8",
      name: "Standard Cathodal S1 Sensory Protocol",
      montage: "Cathode C3 or C4 (dominant sensory hypersensitivity side) — Anode contralateral supraorbital",
      intensity: "1.0 mA",
      duration: "15 minutes",
      sessions: "10 sessions concurrent with sensory desensitisation OT",
      indication: "Tactile hypersensitivity; sensory over-responsivity; ASD sensory gating deficit",
      evidence: "Level C — sensory cortex tDCS literature; ASD OT augmentation"
    },
  ],

  fnonTdcsProtocols: [
    {
      code: "F1",
      name: "FNON Social Brain Priming Protocol — SBN + taVNS",
      montage: "Anode Fz (mPFC) + optional CP6 (right TPJ bilateral if available) — Cathode inion; taVNS pre-session 10–15 min",
      intensity: "1.5 mA mPFC; taVNS 0.3–0.5 mA, 200 µs, 25 Hz",
      duration: "15–20 min tDCS + 10–15 min taVNS pre-session",
      sessions: "10–12 sessions concurrent with social skills training",
      indication: "Social cognition deficit; ToM impairment; SBN upregulation; primary ASD social phenotype",
      fnon_rationale: "taVNS pre-session stabilises autonomic state and reduces amygdala hyperactivation that impedes social engagement; mPFC anodal tDCS during social skills training upregulates SBN at the moment of maximal task-relevant neural activation — activity-dependent plasticity for social cognition"
    },
    {
      code: "F2",
      name: "FNON Executive Flexibility Protocol — CEN + Behaviour Therapy",
      montage: "Bilateral anodal DLPFC (F3+F4, 1.0 mA each) — Reference Cz; CES post-session",
      intensity: "1.0 mA per channel bilateral; CES 100 µA post-session",
      duration: "15 min tDCS concurrent with cognitive flexibility training; CES 40 min post",
      sessions: "10 sessions",
      indication: "RRB-dominant ASD; executive inflexibility; poor cognitive flexibility; CEN hypoactivation",
      fnon_rationale: "Bilateral DLPFC upregulation during cognitive flexibility tasks (set-shifting, task-switching paradigms) promotes activity-dependent CEN plasticity; CES post-session consolidates reduced perseverative arousal"
    },
    {
      code: "F3",
      name: "FNON Anxiety Reduction Protocol — SN + Right DLPFC",
      montage: "Anode F4 (right DLPFC, 1.5 mA) + taVNS bilateral + CES",
      intensity: "1.5 mA tDCS F4; taVNS 0.5 mA bilateral; CES 100 µA",
      duration: "15 min tDCS; 15 min taVNS concurrent; CES 40–60 min post",
      sessions: "10–15 sessions",
      indication: "Anxiety-dominant ASD; social anxiety; autonomic dysregulation; amygdala hyperactivation",
      fnon_rationale: "Right DLPFC anodal tDCS (anxiolytic polarity) + bilateral taVNS (NTS→amygdala modulation + vagal tone restoration) + CES tonic calming: triple-modality anxiety protocol targeting SN at SN hub, amygdala, and DLPFC prefrontal inhibitory pathway simultaneously"
    },
    {
      code: "F4",
      name: "FNON Language Network Protocol — Left IFG + SLT",
      montage: "Anode F5/F3 (left IFG 1.5 mA) — Cathode right supraorbital; taVNS pre-session; concurrent SLT",
      intensity: "1.5 mA; taVNS 0.3–0.5 mA pre-session 10 min",
      duration: "15–20 min tDCS concurrent with SLT language therapy session",
      sessions: "10–15 sessions (minimum 2× per week to align with SLT)",
      indication: "Language/pragmatic ASD phenotype; SLT augmentation; arcuate fasciculus and left IFG network",
      fnon_rationale: "Activity-dependent principle: left IFG anodal tDCS during active SLT session upregulates Broca's area at the moment of maximal language task engagement, amplifying SLT-induced language network plasticity; taVNS pre-session noradrenergic priming enhances learning"
    },
    {
      code: "F5",
      name: "FNON Sensory Regulation Protocol — SN + CES + OT",
      montage: "taVNS (primary) + CES concurrent; optional cathodal Cz (1.0 mA) during OT sensory desensitisation",
      intensity: "taVNS 0.3–0.5 mA; CES 100 µA; cathodal Cz 1.0 mA optional",
      duration: "taVNS 15 min; CES 40 min; tDCS 15 min if tolerated",
      sessions: "10–15 sessions concurrent with OT sensory integration programme",
      indication: "Sensory over-responsivity; tactile/auditory hypersensitivity; ASD sensory meltdowns",
      fnon_rationale: "taVNS + CES modulate the SN and autonomic nervous system — prerequisite for sensory tolerance; cathodal S1/Cz optionally reduces local sensory cortex hyperexcitability concurrently with OT desensitisation; combined approach addresses both cortical (tDCS) and autonomic (taVNS/CES) sensory over-responsivity mechanisms"
    },
    {
      code: "F6",
      name: "FNON Multi-Network ASD Maintenance Protocol",
      montage: "Rotating: odd sessions — social cognition (Fz + right TPJ tDCS + taVNS); even sessions — executive (bilateral DLPFC + CES); taVNS every session",
      intensity: "Per individual session protocols above",
      duration: "Per individual session protocols; 15–20 min tDCS; 10–15 min taVNS; CES as needed",
      sessions: "12 sessions rotating + monthly booster sessions",
      indication: "Multi-phenotype ASD; maintenance after intensive protocol; Phase 2 long-term FNON for ASD",
      fnon_rationale: "Rotating dual-network protocol ensures social brain network and CEN both receive regular FNON modulation without habituation; taVNS autonomic baseline maintained every session as prerequisite for all ASD NIBS engagement"
    },
  ],

  classicTpsProtocols: [
    {
      code: "T1",
      name: "Classic TPS Right TPJ Social Cognition Protocol",
      target: "Right TPJ (CP6 region; neuro-navigation guided)",
      parameters: "0.20–0.25 mJ/mm², 2500–3000 pulses, 3 Hz",
      sessions: "6 sessions concurrent with social skills training",
      indication: "ASD theory of mind impairment, social attention, SBN right TPJ upregulation",
      evidence: "Level C — TPJ TPS social cognition literature; ASD social brain case series"
    },
    {
      code: "T2",
      name: "Classic TPS Left DLPFC Executive Protocol",
      target: "Left DLPFC (F3 region; neuro-navigation)",
      parameters: "0.25 mJ/mm², 3000 pulses, 3 Hz",
      sessions: "6 sessions concurrent with executive function training",
      indication: "ASD executive function deficit, RRB reduction, CEN left DLPFC upregulation",
      evidence: "Level C — DLPFC TPS executive function; ASD cognitive flexibility case series"
    },
    {
      code: "T3",
      name: "Classic TPS Left IFG Language Protocol",
      target: "Left IFG/Broca (F5 region; neuro-navigation)",
      parameters: "0.20 mJ/mm², 2500 pulses, 3 Hz",
      sessions: "6 sessions concurrent with SLT",
      indication: "ASD language network; pragmatic communication; Broca area upregulation",
      evidence: "Level C — language network TPS; ASD SLT augmentation"
    },
    {
      code: "T4",
      name: "Classic TPS mPFC Social Cognition Protocol",
      target: "Medial prefrontal cortex (Fz region; neuro-navigation)",
      parameters: "0.20 mJ/mm², 2500 pulses, 3 Hz",
      sessions: "6 sessions",
      indication: "ASD mentalising deficit, DMN-SBN mPFC targeting, theory of mind",
      evidence: "Level C — mPFC TPS social cognition; ASD pilot studies"
    },
    {
      code: "T5",
      name: "Classic TPS SMA Motor Stereotypy Protocol",
      target: "SMA / pre-SMA (Cz area; neuro-navigation)",
      parameters: "0.20 mJ/mm², 2500 pulses, 3 Hz",
      sessions: "6 sessions",
      indication: "ASD motor stereotypies, repetitive motor behaviours, SMA overactivation",
      evidence: "Level C — SMA TPS inhibitory effects; ASD motor stereotypy literature"
    },
  ],

  fnonTpsProtocols: [
    {
      code: "FT1",
      name: "FNON TPS Social Brain Network Chain — TPJ + mPFC",
      target: "Sequential: Right TPJ (CP6, 2500 pulses) → mPFC (Fz, 2000 pulses) same session",
      parameters: "0.20–0.25 mJ/mm² per target; neuro-navigation; 50 min total",
      sessions: "6–8 sessions concurrent with social skills training",
      indication: "ASD social cognition; theory of mind impairment; SBN hypo-connectivity; TPJ-mPFC disconnection",
      fnon_rationale: "Sequential TPJ then mPFC stimulation targets both ends of the social brain network arc: TPJ (social perception, attention orienting) first, then mPFC (mentalising, social prediction) — mimicking the bottom-up (perceptual) to top-down (interpretive) social cognition pathway disrupted in ASD"
    },
    {
      code: "FT2",
      name: "FNON TPS Language Network Bilateral Protocol",
      target: "Left IFG (Broca, F5) → left STS (T3) sequential within session",
      parameters: "0.20 mJ/mm², 2500 pulses each target; neuro-navigation; 40 min",
      sessions: "6–8 sessions concurrent with SLT",
      indication: "ASD language/pragmatic phenotype; arcuate fasciculus disconnection; Broca-Wernicke network",
      fnon_rationale: "Sequential Broca then STS stimulation activates both ends of the arcuate fasciculus pathway for language production (IFG) and comprehension/social-linguistic processing (STS) — the long-range language arc most disrupted in ASD communication"
    },
    {
      code: "FT3",
      name: "FNON TPS CEN-Social Brain Combined Protocol",
      target: "Left DLPFC (F3, 2500 pulses) → right TPJ (CP6, 2500 pulses) → mPFC (Fz, 2000 pulses)",
      parameters: "0.20–0.25 mJ/mm² per target; neuro-navigation; 75 min total session",
      sessions: "6 sessions (extended session format)",
      indication: "Combined executive + social cognition ASD phenotype; CEN + SBN dual network impairment",
      fnon_rationale: "Three-node sequential TPS addresses the CEN (DLPFC for executive function) and SBN (TPJ + mPFC for social cognition) — the two principal long-range networks disrupted in ASD — in one extended session for maximum network remapping"
    },
    {
      code: "FT4",
      name: "FNON TPS SBN Right Hemisphere Social Attention Protocol",
      target: "Right IPS/SPL (parietal attention) → right TPJ (social attention, CP6) sequential",
      parameters: "0.25 mJ/mm², 2500 pulses per target; neuro-navigation; right hemisphere session",
      sessions: "6 sessions concurrent with joint attention tasks",
      indication: "ASD joint attention deficit; social orienting; right hemisphere attention-SBN interface",
      fnon_rationale: "Right hemisphere sequential parietal (attentional orienting) then TPJ (social attention) TPS targets the attention-social brain interface critical for joint attention development — the earliest and most fundamental social communication skill impaired in ASD"
    },
    {
      code: "FT5",
      name: "FNON TPS Anxiety-Limbic Network Protocol",
      target: "Right DLPFC (F4, 2500 pulses) → ACC/mPFC (Fz, 2000 pulses); taVNS concurrent",
      parameters: "0.20–0.25 mJ/mm²; neuro-navigation; taVNS 0.5 mA bilateral concurrent",
      sessions: "6–8 sessions concurrent with anxiety-adapted CBT",
      indication: "Anxiety-dominant ASD; social anxiety; ACC-DLPFC prefrontal inhibition of amygdala",
      fnon_rationale: "Right DLPFC TPS activates prefrontal inhibitory pathway for amygdala; ACC TPS modulates conflict monitoring (anxiety loop); taVNS concurrent NTS→amygdala pathway — triple-pathway anxiety circuit TPS for ASD anxiety phenotype"
    },
    {
      code: "FT6",
      name: "FNON TPS Sensory Network Protocol",
      target: "ACC/insula-adjacent (Fz, 2000 pulses) + SMA (Cz, 2000 pulses) for sensory circuit modulation",
      parameters: "0.20 mJ/mm² per target; neuro-navigation; 40 min; taVNS concurrent",
      sessions: "6 sessions concurrent with OT sensory integration",
      indication: "Sensory over-responsivity; ASD sensory meltdowns; SN-insula hyperactivation",
      fnon_rationale: "ACC-adjacent TPS reduces SN hyperactivation at the cortical level; SMA cathodal TPS reduces motor circuit overactivation triggered by sensory overload (motor stereotypies as sensory regulation); taVNS addresses thalamic sensory gating and autonomic component"
    },
    {
      code: "FT7",
      name: "FNON TPS Motor-Social Integration Protocol",
      target: "Left M1 (premotor/IFG, C3 area) → right TPJ (social imitation network) sequential",
      parameters: "0.20 mJ/mm², 2500 pulses M1/premotor + 2500 pulses right TPJ; neuro-navigation",
      sessions: "6 sessions concurrent with imitation and social motor tasks",
      indication: "ASD motor dyspraxia + social motor deficit; imitation impairment; mirror neuron hypothesis",
      fnon_rationale: "Premotor cortex (IFG BA 44) + TPJ sequential TPS targets the imitation-social cognition interface: premotor TPS activates action-observation and imitation circuitry while TPJ TPS upregulates social interpretation of others' actions — supporting ASD social motor learning"
    },
    {
      code: "FT8",
      name: "FNON TPS Sleep-Circadian Protocol",
      target: "Medial prefrontal / ACC (Fz, 2000 pulses) for evening DMN/circadian regulation",
      parameters: "0.20 mJ/mm², 2000 pulses; evening session; taVNS concurrent; CES post-session",
      sessions: "6 sessions (evening timing 7–9 pm)",
      indication: "ASD sleep-onset insomnia; circadian rhythm dysregulation; hyperarousal",
      fnon_rationale: "Evening mPFC/ACC TPS to normalise default mode-circadian interface (mPFC has direct SCN projections); taVNS concurrent for vagal tone increase at sleep onset; CES 60 min post-TPS as primary sleep-onset intervention"
    },
    {
      code: "FT9",
      name: "FNON TPS Multi-Network ASD Maintenance Protocol",
      target: "Alternating: SBN sessions (right TPJ + mPFC) and CEN sessions (left DLPFC); taVNS every session",
      parameters: "0.20–0.25 mJ/mm², 3000 pulses per session; neuro-navigation; 30 min per target",
      sessions: "12 sessions rotating (monthly maintenance after intensive); taVNS daily home",
      indication: "Multi-domain ASD maintenance; long-term social and cognitive network support; Phase 2 ASD FNON",
      fnon_rationale: "Alternating SBN and CEN TPS sessions prevent adaptation to single-target stimulation while maintaining network-level engagement across both primary ASD network deficits; taVNS daily autonomic baseline maintained throughout"
    },
  ],

  multimodalPhenotypes: [
    {
      phenotype: "Social Cognition / ToM Deficit ASD",
      stabilise: "taVNS left cymba conchae 0.3–0.5 mA, 200 µs, 25 Hz × 10–15 min (amygdala deactivation; autonomic pre-session stabilisation — essential for social brain engagement)",
      optimise: "Anodal mPFC tDCS (Fz, 1.5 mA) × 15–20 min concurrent with social skills training (SST group or individual social cognition tasks — Reading the Mind in the Eyes, false-belief tasks)",
      zone: "TPS right TPJ (CP6, 0.20–0.25 mJ/mm², 2500 pulses) sessions 1,3,5; TPS mPFC (Fz, 2000 pulses) sessions 2,4,6; neuro-navigation guided",
      outcome: "CES 100 µA × 20 min post-session during quiet preferred activity; social skills homework tasks; caregiver-reinforced social practice between sessions"
    },
    {
      phenotype: "Executive Inflexibility / RRB-Dominant ASD",
      stabilise: "taVNS 0.3–0.5 mA × 10 min pre-session (reduce perseverative arousal; SN modulation before executive demand)",
      optimise: "Bilateral anodal DLPFC tDCS (F3+F4, 1.0 mA each) × 15 min concurrent with cognitive flexibility training (WCST, ICS, set-shifting tasks)",
      zone: "TPS left DLPFC 0.25 mJ/mm² 3000 pulses (odd sessions); TPS SMA cathodal (Cz, 0.20 mJ/mm² 2500 pulses) for motor stereotypy (even sessions)",
      outcome: "CES 40 min post-session; ABA-based behaviour intervention concurrent; RBS-R monitoring every 5 sessions"
    },
    {
      phenotype: "Anxiety-Dominant ASD",
      stabilise: "Bilateral taVNS 0.5 mA × 15 min (primary intervention — vagal tone restoration; NTS→amygdala inhibition; HRV improvement pre-session)",
      optimise: "Anodal right DLPFC tDCS (F4, 1.5 mA) × 15 min concurrent with anxiety-adapted CBT session or relaxation/mindfulness task",
      zone: "TPS right DLPFC (F4, 0.25 mJ/mm², 2500 pulses) + ACC (Fz, 2000 pulses) same session; neuro-navigation; concurrent CBT",
      outcome: "CES bilateral earlobe 100 µA × 40–60 min post-session or pre-sleep; home taVNS 2 × 10 min daily; GAD-7 monitoring fortnightly"
    },
    {
      phenotype: "Language / Pragmatic Communication Focus",
      stabilise: "taVNS 0.3–0.5 mA × 10 min (NTS→LC→NE priming — noradrenergic augmentation of language learning; reduce anxiety before SLT demand)",
      optimise: "Anodal left F5/F3 tDCS (left IFG, 1.5 mA) × 15–20 min concurrent with SLT session (pragmatic language tasks, conversation practice, narrative tasks)",
      zone: "TPS left IFG (F5, 0.20 mJ/mm², 2500 pulses) + left STS (T3, 2500 pulses) sequential; neuro-navigation guided language network session",
      outcome: "Post-session language practice (structured conversation, AAC reinforcement); caregiver-reinforced communication goals; CELF-5 at 6 weeks"
    },
    {
      phenotype: "Sensory Over-Responsivity / Regulation",
      stabilise: "taVNS 0.5 mA × 15 min (primary — SN anterior insula modulation; autonomic de-escalation before OT sensory demand); quiet sensory-adapted environment mandatory",
      optimise: "CES 100 µA × 40 min concurrent with taVNS (if tDCS not tolerated — CES + taVNS as primary dyad for sensory phenotype); optional cathodal S1 tDCS (C3/C4, 1.0 mA) if skin tolerance permits",
      zone: "TPS ACC/SMA (Cz area, 0.20 mJ/mm², 2000 pulses) for SN cortical modulation if tolerated; short sessions (30 min max TPS)",
      outcome: "OT sensory integration programme concurrent; sensory diet home plan; ASD sensory questionnaire (SSP-2) monitoring; taVNS home 10 min pre-challenging sensory exposure"
    },
    {
      phenotype: "Sleep Disturbance Dominant ASD",
      stabilise: "taVNS 0.3–0.5 mA × 10 min (evening, circadian reset protocol; vagal tone increase for sleep onset; NTS-LC pathway modulation)",
      optimise: "Evening tDCS optional: cathodal Cz (SMA/DMN calming, 1.0 mA, 15 min) if hyperarousal prominent; otherwise CES primary (no tDCS if child/adolescent < 16 in evening)",
      zone: "TPS mPFC (Fz, 0.20 mJ/mm², 2000 pulses) evening session for mPFC-circadian circuit; once weekly TPS (not daily for sleep protocol)",
      outcome: "CES 0.5 Hz 100 µA × 60 min pre-sleep (primary sleep intervention); melatonin concurrent as per NICE NG142; sleep diary; actigraphy monitoring; avoid stimulant-like protocols (no anodal DLPFC) in evening"
    },
    {
      phenotype: "Comorbid ADHD-ASD (Dual Diagnosis)",
      stabilise: "taVNS 0.5 mA × 15 min (shared ADHD+ASD autonomic dysregulation; NTS→LC→NE pathway for both attention and anxiety)",
      optimise: "Bilateral anodal DLPFC tDCS (F3+F4, 1.0 mA each) × 15 min (shared CEN target for both ADHD executive and ASD executive phenotypes); concurrent attention training task",
      zone: "TPS left DLPFC 0.25 mJ/mm² 3000 pulses (ADHD-dominant sessions) alternating with TPS right TPJ 0.20 mJ/mm² 2500 pulses (ASD-dominant sessions); neuro-navigation guided",
      outcome: "CES post-session; ADHD medication documented (note potential additive effect with tDCS); BRIEF-2 and SDMT monitoring; caregiver and school feedback"
    },
    {
      phenotype: "Motor-Dyspraxic ASD",
      stabilise: "taVNS 0.3–0.5 mA × 10 min (cerebello-vagal pathway; motor learning augmentation; autonomic stabilisation pre-OT)",
      optimise: "Anodal M1 tDCS bilateral (C3/C4, 1.5 mA) × 15–20 min concurrent with OT fine motor and gross motor tasks",
      zone: "TPS bilateral M1 (0.20 mJ/mm², 2000 pulses each hemisphere) + optional TPS cerebellar (0.20 mJ/mm², 2500 pulses); neuro-navigation guided motor mapping",
      outcome: "OT programme concurrent; motor task practice (MABC-2 monitoring); caregiver motor activity programme; physiotherapy for gait if indicated"
    },
    {
      phenotype: "Minimally Verbal / AAC-Supported ASD",
      stabilise: "taVNS 0.3 mA × 10 min (low-intensity; primary modality — well tolerated; autonomic calming prerequisite) — caregiver present throughout",
      optimise: "CES 100 µA × 20 min (primary — low demand; caregiver supervised); tDCS deferred until sensory tolerance established (3+ sessions of taVNS/CES only first)",
      zone: "TPS deferred until tDCS tolerance confirmed; minimal protocol; taVNS + CES only initially; reassess at 6 sessions",
      outcome: "AAC-supported communication during all sessions; SLT leading; caregiver-delivered home taVNS (brief 5–10 min); ethics committee review for participants with ID; outcome via caregiver-report and functional communication measures"
    },
  ],

  taskPairingRows: [
    ["Task Type", "Concurrent NIBS", "Protocol Rationale", "Outcome Measure"],
    ["Social skills training (SST group or individual)", "Anodal mPFC tDCS (Fz) + taVNS pre-session", "Activity-dependent SBN plasticity: mPFC upregulation during social task maximises social cognition network engagement", "SRS-2 (Social Responsiveness Scale); RMET score; SST goal attainment"],
    ["Speech and Language Therapy (pragmatic tasks)", "Anodal left F5/F3 tDCS + taVNS", "Left IFG upregulation during active language production: amplifies SLT-induced arcuate fasciculus and Broca area plasticity", "CELF-5 (language composite); pragmatic language assessment; MLU; PECS levels"],
    ["Cognitive flexibility / executive training (WCST)", "Bilateral DLPFC anodal tDCS (F3+F4)", "CEN bilateral upregulation during set-shifting task: maximises tDCS-augmented CEN plasticity for executive flexibility", "BRIEF-2 (Shift subscale); WCST perseverative errors; RBS-R"],
    ["OT sensory integration programme", "taVNS + CES (primary); optional cathodal S1", "Autonomic + SN modulation during sensory exposure: taVNS reduces SN overreaction during OT sensory challenges", "SSP-2 (Short Sensory Profile); sensory-related meltdown frequency; OT goal attainment"],
    ["Anxiety-adapted CBT (ASD-adapted)", "Anodal right F4 tDCS + taVNS bilateral + CES", "Anxiolytic DLPFC priming + vagal tone restoration + tonic ANS calm: triple-modality anxiety reduction during cognitive restructuring", "GAD-7; SCARED; social anxiety avoidance frequency; MSSD (mood variability)"],
    ["Pre-sleep relaxation / wind-down routine", "CES 100 µA × 60 min (primary); taVNS 10 min", "Tonic ANS calming + vagal parasympathetic dominance for sleep onset; delivered during quiet sensory preferred activity", "Actigraphy sleep onset latency; parent-report sleep quality; CSHQ (Children's Sleep Habits Questionnaire)"],
  ],

  outcomeMeasures:
    "Primary outcome measures for the SOZO ASD FNON protocol are individualised to phenotype: (1) Social Responsiveness Scale-2 (SRS-2, parent/caregiver and teacher report) — primary social communication outcome; clinically meaningful change: ≥5T-score points; (2) Repetitive Behaviour Scale – Revised (RBS-R) — primary RRB outcome for executive/RRB phenotype; (3) GAD-7 — primary anxiety outcome for anxiety-dominant phenotype (clinically meaningful: ≥5 points); (4) BRIEF-2 (Behaviour Rating Inventory of Executive Function) — Shift subscale for executive flexibility; (5) CELF-5 (Clinical Evaluation of Language Fundamentals) — language composite for language phenotype. Secondary measures: ADOS-2 calibrated severity score reassessment at 3 months; Quality of Life in ASD scale (QoL-ASD or WHOQOL-ASD); Sensory Profile 2 (SP-2); Heart Rate Variability (RMSSD — autonomic outcome); SDMT for cognitive speed; social goal attainment scaling (GAS); caregiver burden measure (ZBI). Neurophysiological monitoring (optional, participating sites): resting EEG (alpha power, gamma coherence) before and after protocol; TMS MEP cortical excitability; fMRI resting-state connectivity at baseline and post-10 sessions. All outcome measures must be adapted to communication needs of individual participants; proxy/caregiver-report versions used for minimally verbal individuals.",

  medicationSectionTitle: "Pharmacological Context and NIBS Interactions in Autism Spectrum Disorder",
  medicationSectionText:
    "No pharmacological agent is approved for core ASD features. Medication interactions with FNON protocols are relevant for comorbid symptom management: Risperidone and aripiprazole (FDA-approved for ASD irritability/aggression): dopamine D2 receptor blockade reduces cortical excitability; may attenuate tDCS LTP responses — document dose; consider reducing tDCS intensity 0.5 mA if high-dose antipsychotic. Methylphenidate (ADHD comorbidity): enhances catecholaminergic tone; may augment tDCS effects on DLPFC; document formulation and timing relative to session (extended-release vs. immediate-release). Atomoxetine (ADHD): NE reuptake inhibitor; may synergise with taVNS noradrenergic pathway — monitor for excessive arousal or blood pressure change. SSRIs (anxiety/OCD comorbidity): serotonergic facilitation may enhance tDCS LTP effects; document dose; sertraline and fluoxetine most commonly prescribed. Melatonin (sleep): no interaction with NIBS; concurrent use encouraged for sleep phenotype. Valproate (ASD comorbid epilepsy, mood): GABA potentiation reduces cortical excitability — may reduce tDCS LTP; lower tDCS intensity; document EEG stability. Lamotrigine (epilepsy/mood): reduces cortical excitability through sodium channel stabilisation; document dose; tDCS intensity may need reduction. Clonidine/guanfacine (ADHD/sleep/aggression in ASD): reduces sympathetic tone and NE signalling; complementary to taVNS vagal activation; monitor HR throughout taVNS sessions. Benzodiazepines: reduce neuroplasticity response; avoid during tDCS sessions; PRN use only with careful timing. Baclofen (ASD tone/sleep off-label): GABA-B agonist; reduces cortical excitability — document dose.",

  references: {
    foundational: [
      { authors: "American Psychiatric Association", year: 2022, title: "Diagnostic and Statistical Manual of Mental Disorders, Fifth Edition, Text Revision (DSM-5-TR)", journal: "American Psychiatric Association Publishing", volume: "", pages: "", doi: "" },
      { authors: "Maenner MJ, Warren Z, Williams AR, et al.", year: 2023, title: "Prevalence and characteristics of autism spectrum disorder among children aged 8 years — Autism and Developmental Disabilities Monitoring Network, 11 Sites, United States, 2020", journal: "MMWR Surveillance Summaries", volume: "72(2)", pages: "1–14", doi: "10.15585/mmwr.ss7202a1" },
      { authors: "Geschwind DH, Levitt P", year: 2007, title: "Autism spectrum disorders: developmental disconnection syndromes", journal: "Current Opinion in Neurobiology", volume: "17(1)", pages: "103–111", doi: "10.1016/j.conb.2007.01.009" },
      { authors: "Just MA, Cherkassky VL, Keller TA, Minshew NJ", year: 2004, title: "Cortical activation and synchronization during sentence comprehension in high-functioning autism: Evidence of underconnectivity", journal: "Brain", volume: "127(8)", pages: "1811–1821", doi: "10.1093/brain/awh199" },
      { authors: "Satterstrom FK, Kosmicki JA, Wang J, et al.", year: 2020, title: "Large-scale exome sequencing study implicates both developmental and functional changes in the neurobiology of autism", journal: "Cell", volume: "180(3)", pages: "568–584", doi: "10.1016/j.cell.2019.12.036" },
      { authors: "Rubenstein JL, Merzenich MM", year: 2003, title: "Model of autism: increased ratio of excitation/inhibition in key neural systems", journal: "Genes, Brain and Behavior", volume: "2(5)", pages: "255–267", doi: "10.1034/j.1601-183X.2003.00037.x" },
    ],
    tdcs: [
      { authors: "D'Urso G, Bruzzese D, Ferrucci R, et al.", year: 2015, title: "Transcranial direct current stimulation for hyperactivity and noncompliance in autistic disorder", journal: "World Journal of Biological Psychiatry", volume: "16(5)", pages: "361–366", doi: "10.3109/15622975.2015.1014411" },
      { authors: "Costanzo F, Varuzza C, Rossi S, et al.", year: 2020, title: "Evidence for reading improvement following tDCS treatment in children and adolescents with autism spectrum disorder", journal: "Neuropsychologia", volume: "141", pages: "107376", doi: "10.1016/j.neuropsychologia.2020.107376" },
      { authors: "Ulam P, Jaffe N, Shelton S, et al.", year: 2015, title: "Cerebral neuroplasticity in autism spectrum disorder as measured by functional connectivity and cortical thickness", journal: "Frontiers in Human Neuroscience", volume: "9", pages: "503", doi: "10.3389/fnhum.2015.00503" },
      { authors: "Santiesteban I, Banissy MJ, Catmur C, Bird G", year: 2012, title: "Enhancing social ability by stimulating right temporoparietal junction", journal: "Current Biology", volume: "22(23)", pages: "2274–2277", doi: "10.1016/j.cub.2012.10.018" },
      { authors: "Lefaucheur JP, Antal A, Ayache SS, et al.", year: 2017, title: "Evidence-based guidelines on the therapeutic use of transcranial direct current stimulation (tDCS)", journal: "Clinical Neurophysiology", volume: "128(1)", pages: "56–92", doi: "10.1016/j.clinph.2016.10.087" },
    ],
    tps: [
      { authors: "Beisteiner R, Matt E, Fan C, et al.", year: 2020, title: "Transcranial pulse stimulation with ultrasound in Alzheimer's disease—A new navigated focal brain therapy", journal: "Advanced Science", volume: "7(3)", pages: "1902583", doi: "10.1002/advs.201902583" },
      { authors: "Legon W, Bansal P, Tyberg M, et al.", year: 2014, title: "Transcranial focused ultrasound modulates the activity of human somatosensory cortex", journal: "Nature Neuroscience", volume: "17(2)", pages: "322–329", doi: "10.1038/nn.3620" },
    ],
    tavns: [
      { authors: "Clancy JA, Mary DA, Witte KK, et al.", year: 2014, title: "Non-invasive vagus nerve stimulation in healthy humans reduces sympathetic nerve activity", journal: "Brain Stimulation", volume: "7(6)", pages: "871–877", doi: "10.1016/j.brs.2014.07.031" },
      { authors: "Pavlov VA, Tracey KJ", year: 2012, title: "The vagus nerve and the inflammatory reflex—linking immunity and metabolism", journal: "Nature Reviews Endocrinology", volume: "8(12)", pages: "743–754", doi: "10.1038/nrendo.2012.189" },
      { authors: "Frangos E, Ellrich J, Komisaruk BR", year: 2015, title: "Non-invasive access to the vagus nerve central projections via electrical stimulation of the ear", journal: "Brain Stimulation", volume: "8(3)", pages: "624–636", doi: "10.1016/j.brs.2014.11.018" },
      { authors: "Porges SW", year: 2007, title: "The polyvagal perspective", journal: "Biological Psychology", volume: "74(2)", pages: "116–143", doi: "10.1016/j.biopsycho.2006.06.009" },
    ],
    ces: [
      { authors: "Kirsch DL, Nichols F", year: 2013, title: "Cranial electrotherapy stimulation for treatment of anxiety, depression, and insomnia", journal: "Psychiatric Clinics of North America", volume: "36(1)", pages: "169–176", doi: "10.1016/j.psc.2013.01.006" },
      { authors: "Barclay TH, Barclay RD", year: 2014, title: "A clinical trial of cranial electrotherapy stimulation for anxiety and comorbid depression", journal: "Journal of Affective Disorders", volume: "164", pages: "171–177", doi: "10.1016/j.jad.2014.04.029" },
    ],
    network: [
      { authors: "Monk CS, Peltier SJ, Wiggins JL, et al.", year: 2009, title: "Abnormalities of intrinsic functional connectivity in autism spectrum disorders", journal: "NeuroImage", volume: "47(2)", pages: "764–772", doi: "10.1016/j.neuroimage.2009.04.069" },
      { authors: "Kennedy DP, Courchesne E", year: 2008, title: "The intrinsic functional organization of the brain is altered in autism", journal: "NeuroImage", volume: "39(4)", pages: "1877–1885", doi: "10.1016/j.neuroimage.2007.10.052" },
      { authors: "Assaf M, Jagannathan K, Calhoun VD, et al.", year: 2010, title: "Abnormal functional connectivity of default mode sub-networks in autism spectrum disorder patients", journal: "NeuroImage", volume: "53(1)", pages: "247–256", doi: "10.1016/j.neuroimage.2010.05.067" },
      { authors: "Uddin LQ, Supekar K, Menon V", year: 2013, title: "Reconceptualizing functional brain connectivity in autism from a developmental perspective", journal: "Frontiers in Human Neuroscience", volume: "7", pages: "458", doi: "10.3389/fnhum.2013.00458" },
      { authors: "Menon V, Uddin LQ", year: 2010, title: "Saliency, switching, attention and control: A network model of insula function", journal: "Brain Structure and Function", volume: "214(5–6)", pages: "655–667", doi: "10.1007/s00429-010-0262-0" },
    ],
  },
  // ── FNON Protocol Data (SOZO_Brain_Networks_qEEG_FNON.xlsx, April 2026) ──
  fnonPrimaryNetwork: 'Social Brain + Cerebellar-Limbic',
  fnonSecondaryNetwork: 'Cerebellar-Limbic',
  fnonFBand: 'Alpha facilitation + Theta-gamma coupling',
  fnonEegNodes: 'F3/F4(DLPFC)+P3/P4(TPJ-ToM)+Pz(DMN)+cerebellar surface',
  fnonOscillationGoal: 'Improve social brain network coherence; restore TGC; normalise frontal alpha; reduce sensory gamma hyperactivity',
  fnonPrimaryModalityParams: 'TPS NEUROLITH: 6000 pulses, EFD 0.20 mJ/mm², 5 Hz PRF, 6-12 sessions. Multi-site: prefrontal+parietal+temporal. RCT 2023 Brain Commun (21 cit)',
  fnonAddonModality: 'tACS 40Hz gamma temporal nodes; taVNS (social via vagal-LC-social axis); Cerebellar TMS (vermis 1Hz)',
  fnonSessions: '6–12',
  fnonEvidenceLevel: 'Double-blind RCT 2023',
  fnonLitCount: '4+ TPS; 20+ TMS; 10+ tDCS',
  fnonKeyReferences: 'Beisteiner 2023 Brain Commun (21 cit); Autism Research 2025; Asian RCT 2025',
  fnonNotes: 'Social brain (TPJ+mPFC+STG) = primary target. TPS covers all nodes per session. taVNS for autonomic-social integration.',
  fnonQeegBiomarker: '↓Alpha social; ↑Gamma sensory',
  fnonPaperCounts: {
    tps: 4, tms: 20, tdcs: 10,
    tavns: 10, ces: null, tacs: 5,
    pbm: 5, lifu: null, pemf: 5, dbs: null,
  },
  fnonBestFirstLine: 'TPS RCT 2023 Brain Commun',
  fnonBestSecondLine: 'Cerebellar TMS + taVNS',
  fnonScore: 4,

};
