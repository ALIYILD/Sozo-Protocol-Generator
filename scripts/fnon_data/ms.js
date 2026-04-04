// SOZO FNON Clinical Protocol — Multiple Sclerosis (MS)
// Document A — Partners Tier

module.exports = {
  conditionFull: "Multiple Sclerosis",
  conditionShort: "MS",
  conditionSlug: "ms",
  documentNumber: "SOZO-FNON-MS-001",

  offLabelCoverText:
    "All non-invasive brain stimulation (NIBS) applications described in this protocol for Multiple Sclerosis represent off-label use of CE-marked and FDA-cleared devices. The Newronika HDCkit, PlatoScience PlatoWork, NEUROLITH® TPS system, Soterix Medical taVNS, and Alpha-Stim AID are approved for specific indications that do not include MS as a primary listed indication. Clinical use must conform to applicable national regulations, institutional policies, and informed-consent requirements. The evidence base for NIBS in MS is emerging, with Level B evidence for tDCS targeting fatigue and cognition, and Level C evidence for TPS and taVNS. All protocols should be delivered by trained clinicians with MS-specific neurological expertise.",

  offLabelTable: [
    ["Device", "Cleared/Approved Indication", "MS Off-Label Application", "Evidence Level"],
    ["Newronika HDCkit / PlatoWork", "Neurological rehabilitation (CE)", "Fatigue, cognitive impairment, spasticity", "Level B"],
    ["NEUROLITH® TPS", "Alzheimer's disease (CE)", "Cortical network remyelination support, fatigue", "Level C"],
    ["Soterix taVNS / Alpha-Stim AID", "Epilepsy/anxiety/pain (CE/FDA)", "Anti-inflammatory, fatigue, autonomic dysregulation", "Level C"],
  ],

  inclusionCriteria: [
    ["Confirmed MS diagnosis per McDonald criteria 2017 (relapsing-remitting, secondary progressive, or primary progressive)", "Stable neurological status for ≥3 months (no acute relapse)", "Age 18–70 years", "EDSS score 0–7 (ambulatory or semi-ambulatory)"],
    ["Fatigue Severity Scale (FSS) ≥4 or cognitive impairment on Brief International Cognitive Assessment for MS (BICAMS)", "On stable disease-modifying therapy (DMT) for ≥3 months or DMT-naïve", "Able to provide informed consent", "Able to attend 5-day intensive or 10-session spread protocol"],
    ["MRI brain available within 24 months (lesion load assessment)", "No acute relapse within 3 months", "Adequate skin integrity at electrode/transducer sites", "Baseline neuropsychological assessment completed"],
    ["Clinical MS team agreement for NIBS adjunct", "Realistic treatment expectations established", "Caregiver support available if EDSS ≥5", "No contraindicated medications (see exclusion)"],
    ["Willingness to engage in concurrent neurorehabilitation (physiotherapy, cognitive rehabilitation, fatigue management)", "No planned changes to DMT during protocol", "Access to temperature-controlled environment (heat sensitivity management — Uhthoff phenomenon)", "Baseline fatigue and quality-of-life measures completed"],
    ["FSS, MFIS, Symbol Digit Modalities Test (SDMT), and BDI-II completed at baseline", "Neuropsychiatric evaluation if cognitive profile complex", "Spasticity measure (MAS) if applicable", "Patient education on heat sensitivity and NIBS completed pre-treatment"],
    ["Written informed consent with off-label disclosure", "Emergency contact established", "Treatment goals documented collaboratively", "Outcome assessment schedule agreed"],
  ],

  exclusionCriteria: [
    ["Active MS relapse within 3 months (demyelinating activity may alter network response)", "High corticosteroid dose within 4 weeks", "Intracranial metal implants (deep brain stimulators, cochlear implants, ferromagnetic aneurysm clips)", "Active intrathecal baclofen pump (contraindicated for TPS)"],
    ["Cardiac pacemaker or implantable defibrillator (absolute contraindication for taVNS/CES)", "Pregnancy or breastfeeding", "Severe psychiatric disorder uncontrolled (active psychosis, mania)", "Active substance use disorder"],
    ["Severe cognitive impairment precluding informed consent (MMSE <18)", "Uncontrolled seizure disorder", "Current participation in conflicting NIBS research trial", "History of malignant brain tumour"],
    ["Severe skin disorder at electrode sites", "Known hypersensitivity to conductive gel or electrode materials", "Severe autonomic dysfunction (recurrent syncope)", "Neuromyelitis optica spectrum disorder (NMOSD) — distinct pathophysiology"],
    ["Severe depression with active suicidal ideation", "EDSS >7.5 (severely restricted, may not tolerate protocols)", "Progressive MS with very rapid deterioration (protocol benefit uncertain)", "Inability to tolerate seated protocol duration due to spasticity or pain"],
    ["High-dose immunosuppressive initiation within 3 months", "Acute urinary tract infection (common MS complication — may alter symptom profile)", "Severe heat sensitivity with core temperature dysregulation", "Recent head trauma"],
    ["Botulinum toxin injection to head/neck within 3 months (may alter taVNS response)", "Deep cervical vagus nerve stimulator in place", "Open wounds or infections at electrode/transducer sites", "Withdrawal from opioids or benzodiazepines (confounds neuroplasticity response)"],
    ["Recent significant change in DMT (within 3 months) that may alter baseline neurophysiology", "Untreated hypothyroidism or severe metabolic disorder", "Severe anaemia affecting exercise/fatigue assessment", "Clinician assessment: risk outweighs benefit"],
  ],

  conditionsRequiringDiscussion: [
    ["Condition", "Clinical Consideration", "Recommended Action", "Protocol Adjustment"],
    ["Clinically Isolated Syndrome (CIS)", "Pre-McDonald MS; network disruption present but diagnosis not yet confirmed", "MS neurology team review; consider if radiological dissemination established", "Proceed with caution; taVNS/CES preferred; lower tDCS intensity"],
    ["Benign MS (RRMS, low lesion burden)", "Good prognosis; may benefit most from early NIBS-induced network stabilisation", "Standard protocol; optimise for early neuroplasticity engagement", "Full protocol; emphasise cognitive and fatigue domains"],
    ["Secondary Progressive MS (SPMS)", "Transition from relapsing; neurodegeneration prominent; reduced plasticity reserve", "Manage expectations; focus on symptomatic relief and function maintenance", "Reduce session intensity; longer treatment spread; integrate physiotherapy"],
    ["Primary Progressive MS (PPMS)", "No relapsing phase; bilateral corticospinal tract involvement common", "PPMS-specific neurologist review; evidence is very limited", "Conservative protocol; bilateral M1/SMA targets; focus on spasticity and fatigue"],
    ["Severe fatigue with autonomic involvement (POTS-like)", "Autonomic dysfunction may be exacerbated by tDCS session", "Lying-down protocol option; monitor heart rate throughout", "Reduce tDCS intensity 1.0 mA; extend taVNS; ensure hydration"],
    ["Cognitive MS (Mild Cognitive Impairment)", "SDMT, PASAT impairment common; frontal-parietal network lesions", "BICAMS at baseline; neuropsychology input", "Add F4/F3 DLPFC FNON tDCS; TPS parietal; CES cognitive protocol"],
    ["MS-associated depression", "Prevalence >50%; confounds fatigue assessment; mediated by cytokines and network disruption", "BDI-II; psychiatric review if moderate-severe; coordinate with psychiatrist", "Add F3 anodal tDCS; taVNS anti-inflammatory; integrate psychological support"],
    ["Spasticity-dominant MS", "Upper motor neuron pattern; M1/SMA hyperexcitability", "Physiotherapy concurrent; assess MAS", "Cathodal M1 (reduce hyperexcitability); taVNS for spasticity relief; TPS motor cortex"],
    ["Uhthoff phenomenon (heat-sensitive worsening)", "Transient worsening with temperature rise; may occur during tDCS sessions", "Pre-cool; air-conditioned treatment room; shorter sessions if needed", "Monitor closely; CES/taVNS only during heat-sensitive periods; defer tDCS if Uhthoff active"],
  ],

  overviewParagraph:
    "Multiple Sclerosis is an autoimmune-mediated inflammatory and neurodegenerative disease of the central nervous system characterised by demyelination, axonal injury, and progressive network disconnection. MS is the most common cause of non-traumatic neurological disability in young adults, affecting approximately 2.8 million individuals globally. The heterogeneous clinical presentation — fatigue, cognitive impairment, motor dysfunction, pain, visual loss, and neuropsychiatric symptoms — reflects the widespread and unpredictable distribution of white matter lesions across functional networks. The SOZO FNON protocol for MS addresses the core challenge of network-level disruption: lesions interrupt white matter tracts connecting nodes of the DMN, CEN, SN, and motor networks, producing functional disconnection disproportionate to lesion volume. NIBS cannot repair myelin or eliminate inflammation, but can modulate cortical excitability, promote compensatory neuroplasticity, activate alternative network pathways, and reduce the neuroinflammatory burden through taVNS anti-inflammatory mechanisms. Evidence supports tDCS targeting of the DLPFC and M1 for MS fatigue and cognitive impairment (Level B), with taVNS offering additional benefit for autonomic dysregulation and systemic inflammation. The SOZO protocol integrates these modalities within a structured S-O-Z-O multimodal framework, personalised to MS phenotype and EDSS functional level.",

  fnonNetworkParagraph:
    "The FNON framework conceptualises MS as a disease of progressive functional network disconnection superimposed on focal white matter lesions. While classical neurology focused on anatomical lesion location (periventricular, juxtacortical, infratentorial, spinal), functional neuroimaging has revealed that symptoms correlate better with network-level disruption than lesion number or volume alone. In MS, the Default Mode Network (DMN) — spanning medial prefrontal cortex, posterior cingulate, and lateral parietal cortex — shows abnormal hyper-activation that represents maladaptive compensatory recruitment in response to white matter disconnection. Patients with MS fatigue exhibit reduced CEN (dorsolateral prefrontal–parietal working memory network) activation during cognitive tasks, while paradoxically showing increased SN (salience network) activation, suggesting heightened effort perception and central fatigue amplification. Motor network disconnection — corticospinal tract lesions and transcallosal inhibition imbalance — underpins upper limb spasticity and gait impairment beyond what local spinal lesions would predict. The FNON approach targets these network abnormalities directly: tDCS upregulates CEN nodes (DLPFC) for cognitive fatigue; M1 stimulation addresses motor network excitability; taVNS modulates the SN and anti-inflammatory pathways simultaneously. This multi-network targeting reflects the multi-system nature of MS disability. This network-level characterisation is supported by Lefaucheur et al. 2024 (63 citations) and To et al. 2018 (113 citations).",

  networkDisorderParagraphs: [
    {
      network: "Default Mode Network (DMN)",
      paragraph:
        "In MS, the Default Mode Network (DMN) exhibits paradoxical hyper-activation during cognitive tasks — a neural signature of compensatory over-recruitment that correlates with subjective fatigue and cognitive complaints even when performance appears preserved on standardised testing. The DMN hubs — medial prefrontal cortex (mPFC), posterior cingulate cortex (PCC), and inferior parietal lobule (IPL) — show reduced deactivation during task engagement, indicating failure of the normal task-positive/task-negative network anticorrelation. This DMN suppression failure has been linked to periventricular white matter lesion burden disrupting thalamocortical and callosal DMN connectivity. FNON protocol component: cathodal tDCS at Cz (to modestly dampen posterior midline DMN hyper-reactivity) combined with CES to normalise default-mode oscillatory dynamics, reducing neural noise that amplifies fatigue perception."
    },
    {
      network: "Central Executive Network (CEN)",
      paragraph:
        "The Central Executive Network (CEN) — anchored in the bilateral DLPFC (BA 46/9) and posterior parietal cortex — is critically impaired in MS cognitive impairment, which affects 40–65% of patients and is the primary driver of employment loss and reduced quality of life. MS-CEN dysfunction manifests as slowed processing speed (Symbol Digit Modalities Test impairment), working memory deficits, and reduced verbal fluency — collectively termed 'MS cognitive impairment' or 'cognitive MS'. Functional MRI demonstrates reduced DLPFC activation during working memory tasks, with structural MRI showing thinning of the prefrontal cortex even in early RRMS. tDCS anodal stimulation of left and right DLPFC (F3/F4) is the primary FNON CEN intervention, with evidence from sham-controlled trials showing significant improvement in information processing speed and working memory following 5–10 sessions in MS populations."
    },
    {
      network: "Salience Network (SN)",
      paragraph:
        "The Salience Network (SN) — centred on the anterior insula and anterior cingulate cortex — shows pathological upregulation in MS fatigue, serving as the neural mediator of 'central fatigue': the disproportionate sense of effort and exhaustion experienced by 75–90% of patients with MS. Unlike peripheral fatigue (muscle-based), central MS fatigue reflects amplified effort signals from the SN that override normal task engagement capacity. Functional imaging demonstrates that SN activation during rest predicts next-day fatigue ratings in RRMS patients. taVNS modulates the SN via NTS projections to the insula and ACC through the locus coeruleus-norepinephrine system, reducing the amplified effort signal. Combined taVNS + cathodal AC (pre-SMA) tDCS represents the FNON strategy for central fatigue suppression."
    },
    {
      network: "Sensorimotor Network (SMN)",
      paragraph:
        "The Sensorimotor Network (SMN) — comprising primary motor cortex (M1), supplementary motor area (SMA), somatosensory cortex (S1), and cerebellum — is disrupted in virtually all MS patients with motor symptoms. The interhemispheric balance of M1 excitability is disrupted by corticospinal tract lesions, with the affected hemisphere showing decreased corticospinal excitability and the unaffected hemisphere exhibiting compensatory over-activation. Unlike stroke (focal unilateral lesion), MS often involves bilateral pyramidal tract lesions, progressive cerebellar peduncle involvement, and cervical spinal cord lesions — necessitating bilateral or midline SMN targeting rather than purely lateralised protocols. TPS can target the motor cortex and supplementary motor area to a depth appropriate for cortical motor mapping, supporting motor network reorganisation concurrent with physiotherapy."
    },
    {
      network: "Limbic Network",
      paragraph:
        "The Limbic Network in MS encompasses hippocampus, amygdala, anterior cingulate cortex, and orbitofrontal cortex — all structures susceptible to both grey matter atrophy (MS-specific grey matter pathology) and white matter disconnection from periventricular and subcortical lesions. Hippocampal demyelination and grey matter pathology contribute to episodic memory impairment in MS, while amygdala hyperactivity underlies the high prevalence of anxiety and depression (>50% over disease course). MS-associated depression has neuroinflammatory origins — proinflammatory cytokines (IL-6, TNF-α) directly disrupt limbic-prefrontal circuits. taVNS anti-inflammatory pathway (NTS→cholinergic anti-inflammatory reflex) reduces systemic and CNS inflammatory burden, addressing the neuroinflammatory substrate of MS depression and anxiety alongside its motor and cognitive effects."
    },
    {
      network: "Attention Network",
      paragraph:
        "The Attention Network in MS — comprising the right hemisphere inferior frontal gyrus, intraparietal sulcus, superior parietal lobule, and frontal eye fields — shows significant disruption manifesting as impaired sustained attention, divided attention, and attentional fatigue. MS patients demonstrate abnormal right hemisphere parietal thinning correlated with attentional capacity on the PASAT (Paced Auditory Serial Addition Test). The combined effect of attention network disruption and SN-mediated central fatigue creates a dual impairment: reduced attentional capacity compounded by amplified effort perception. FNON protocol addresses this through right DLPFC/parietal tDCS (F4/P4) and TPS right parietal targeting, coordinated with CEN stimulation to support the attentional substrate of cognitive rehabilitation exercises."
    },
  ],

  networkCitationKeys: [
    { authors: "Lefaucheur et al.", year: 2024, citations: 63, title: "Neuromodulation techniques – From non-invasive to deep brain stimulation", doi: "" },
    { authors: "To et al.", year: 2018, citations: 113, title: "Changing Brain Networks Through Non-invasive Neuromodulation", doi: "" },
  ],
  fnonEvidenceStrength: "Moderate",

  pathophysiologyText:
    "Multiple Sclerosis is characterised by autoimmune-mediated inflammation targeting myelin and oligodendrocytes (producing demyelinating lesions), accompanied by progressive axonal injury, grey matter atrophy, and network-level disconnection that collectively drive irreversible disability. The cardinal pathological event is the MS plaque: a focal area of demyelination with oligodendrocyte loss, axonal injury, remyelination (shadow plaques), and reactive gliosis, surrounded by a rim of inflammatory cells (T-cells, B-cells, macrophages/microglia). Lesion distribution follows characteristic patterns — periventricular (Dawson's fingers), juxtacortical, infratentorial (brainstem/cerebellar), and spinal cord — with the topography determining symptom profile. Beyond focal lesions, diffuse pathology — normal-appearing white matter (NAWM) microstructural abnormalities on DTI, widespread grey matter atrophy, synaptic loss — accounts for disability progression in progressive MS beyond what lesion load predicts. Neuroinflammation is driven by IL-17-producing Th17 cells crossing the blood-brain barrier, with B-cell involvement increasingly recognised (explaining anti-CD20 DMT efficacy). Microglial activation perpetuates progressive neurodegeneration in SPMS/PPMS. The therapeutic opportunity for NIBS lies in four domains: (1) compensatory neuroplasticity — upregulating perilesional cortex and alternative network pathways; (2) reducing central fatigue via SN modulation; (3) taVNS-mediated anti-inflammatory effects reducing microglial activation and cytokine burden; and (4) supporting neurorehabilitation-induced plasticity concurrently.",

  cardinalSymptoms: [
    ["Domain", "Primary Symptoms", "Network Basis", "FNON Target"],
    ["Fatigue", "Central fatigue (75–90%); mental and physical exhaustion disproportionate to effort; worsened by heat (Uhthoff)", "SN hyperactivation; CEN hypofrontality; DMN suppression failure; corticospinal inefficiency", "taVNS (SN/NTS); cathodal preSMA; CES theta-burst"],
    ["Cognitive Impairment", "Slowed processing speed (SDMT); working memory deficit; verbal fluency; attention; executive function (40–65%)", "CEN DLPFC hypoactivation; white matter disconnection (fronto-parietal); hippocampal grey matter pathology", "Anodal DLPFC (F3/F4); TPS prefrontal; CES cognitive enhancement"],
    ["Spasticity", "Bilateral (or unilateral) pyramidal pattern; clonus; flexor spasms; ambulatory impairment; upper limb dexterity", "SMN corticospinal disconnection; reduced descending inhibition; cervical spinal cord lesions", "M1/SMA tDCS (bilateral); TPS motor; physiotherapy concurrent"],
    ["Motor Weakness / Gait", "Hemiplegia or paraparesis; foot drop; gait ataxia; fatiguable weakness (pyramidal + cerebellar)", "SMN motor cortex hypoexcitability ipsilesional; cerebellar peduncle lesions", "Anodal M1 (bilateral); TPS motor strip; robotic gait therapy paired"],
    ["Pain", "Central neuropathic pain; Lhermitte's phenomenon; trigeminal neuralgia; dysaesthesia; MS hug", "Thalamic-cortical pain circuit dysregulation; spinothalamic tract lesions; SN sensitisation", "M1 anodal (contralateral); taVNS NTS-PAG analgesic; TPS S1"],
    ["Depression / Anxiety", "Prevalence >50% over course; neuroinflammatory and psychosocial origins; steroid-induced mood disturbance", "Limbic-prefrontal disconnection; cytokine-mediated; hippocampal grey matter atrophy", "Anodal F3 (left DLPFC); taVNS anti-inflammatory; CES anxiolytic"],
    ["Bladder / Bowel Dysfunction", "Urgency, frequency, incontinence, retention; bowel urgency; constipation", "Pontine micturition centre disconnection; frontal control loss; spinal cord lesions", "Indirect: SMA/frontal tDCS; taVNS autonomic regulation"],
    ["Visual Symptoms", "Optic neuritis residuals; diplopia; oscillopsia; reduced contrast sensitivity", "Optic nerve demyelination; brainstem/INO; visual cortex network", "Limited direct NIBS; TPS occipital (experimental); taVNS neuroprotective"],
    ["Sensory / Proprioceptive", "Numbness; paraesthesia; sensory ataxia; impaired proprioception; vibration loss", "Posterior column lesions; somatosensory cortex disconnection; thalamic relay disruption", "S1 tDCS (cathodal to reduce allodynia); taVNS sensory network"],
  ],

  standardGuidelinesText: [
    "MS management follows evidence-based guidelines from the European Committee for Treatment and Research in Multiple Sclerosis (ECTRIMS), the American Academy of Neurology (AAN), and national MS societies. First-line disease-modifying therapies (DMTs) include interferon-beta preparations (Avonex, Rebif, Betaferon), glatiramer acetate (Copaxone), and dimethyl fumarate (Tecfidera) for relapsing-remitting MS — all with Level A evidence for relapse rate reduction. High-efficacy DMTs — natalizumab (Tysabri), alemtuzumab (Lemtrada), ocrelizumab (Ocrevus), and cladribine (Mavenclad) — are used for highly active RRMS or rapidly evolving disease.",
    "Ocrelizumab (anti-CD20) is the only DMT with Level A evidence for primary progressive MS (PPMS), reflecting the B-cell contribution to progressive neurodegeneration. Siponimod (Mayzent) and ofatumumab (Kesimpta) have Level A evidence for secondary progressive MS with active disease. No DMT has demonstrated significant efficacy for non-active progressive MS beyond ocrelizumab for PPMS.",
    "Symptomatic management of MS fatigue follows NICE guideline NG220 (2022) and ECTRIMS/EAN recommendations: first-line non-pharmacological interventions include aerobic exercise (Level A), cognitive rehabilitation (Level B), and energy management strategies. Pharmacological fatigue treatment with amantadine, modafinil, or methylphenidate has Level B evidence but limited effect sizes. 4-aminopyridine (fampridine/dalfampridine) has Level A evidence specifically for MS gait improvement.",
    "MS cognitive impairment management: cognitive rehabilitation (Level B), aerobic exercise (Level B), and neuropsychological support are recommended. No pharmacological agent has Level A evidence specifically for MS cognitive impairment; donepezil showed no benefit in the largest RCT (OLYMPUS). tDCS targeting the DLPFC has Level B evidence in MS cognitive rehabilitation from multiple sham-controlled RCTs.",
    "Spasticity management: baclofen (oral/intrathecal), tizanidine, and cannabinoids (nabiximols/Sativex, Level B) form the pharmacological backbone. Physiotherapy and stretching are essential. Botulinum toxin injection is Level A for focal spasticity. tDCS M1 and TMS have Level B evidence as adjuncts to physiotherapy for MS spasticity.",
    "Pain management: tricyclic antidepressants, gabapentin/pregabalin, and duloxetine/venlafaxine are first-line for central neuropathic pain. Cannabis-based medicines have Level B evidence for MS pain. M1 anodal tDCS has Level B evidence for central neuropathic pain in MS from multiple RCTs.",
    "Depression treatment: SSRIs (sertraline, escitalopram) and SNRIs are first-line pharmacological treatment. CBT has Level A evidence for MS depression. Neuroinflammatory depression may respond better to anti-inflammatory strategies (exercise, omega-3, taVNS) than to purely monoaminergic approaches.",
  ],

  fnonFrameworkParagraph:
    "The SOZO FNON framework approaches Multiple Sclerosis as a multi-network disconnection syndrome requiring simultaneous, network-targeted modulation across the CEN, SN, SMN, Limbic, and Attention networks — with the specific network combination determined by individual MS phenotype and EDSS profile. Unlike single-target NIBS approaches that address one symptom domain, FNON recognises that MS produces obligatory multi-network disruption: a patient with fatigue invariably has SN upregulation, CEN hypofrontality, and SMN inefficiency simultaneously. The FNON S-O-Z-O sequence deploys taVNS first to modulate the SN anti-inflammatory and autonomic pathways (Stabilise), followed by DLPFC or M1 tDCS to optimise network excitability (Optimise), then TPS to target deep or precise cortical zones (Zone), and consolidation via CES during neurorehabilitation (Outcome). Disease-modifying therapy is not interrupted; FNON is an adjunct addressing the functional network consequences of MS that DMTs cannot directly modify. The anti-inflammatory taVNS pathway — NTS→cholinergic anti-inflammatory reflex→reduced TNF-α, IL-6, IL-17 — complements DMT action by targeting microglial neuroinflammation beyond the blood-brain barrier.",

  keyBrainRegions: [
    ["Brain Region", "Function", "MS Pathology", "FNON Intervention"],
    ["Dorsolateral Prefrontal Cortex (DLPFC)", "Working memory, processing speed, executive control", "Hypoactivation, grey matter thinning, disconnection from parietal cortex via SLF lesions", "Anodal tDCS F3/F4 (1.5–2.0 mA, 20 min); TPS prefrontal"],
    ["Primary Motor Cortex (M1)", "Voluntary movement, corticospinal drive, motor learning", "Reduced MEP amplitude, intracortical inhibition loss, recruitment of accessory motor areas", "Anodal tDCS C3/C4 bilateral (1.5 mA, 20 min) concurrent with physio; TPS motor strip"],
    ["Supplementary Motor Area (SMA)", "Movement preparation, bimanual coordination, sequencing", "SMA hyperactivation as compensation for primary M1 efficiency loss in MS", "Cathodal tDCS Cz (to reduce hyperactivation); TPS SMA precision targeting"],
    ["Anterior Cingulate Cortex (ACC)", "Effort allocation, conflict monitoring, autonomic regulation, fatigue signalling", "Structural thinning; ACC-SN hyperactivation drives central fatigue amplification", "taVNS modulation (NTS→ACC pathway); cathodal midline tDCS"],
    ["Anterior Insula", "Interoception, effort perception, pain processing, SN hub", "Hyper-activated during fatigue tasks; key driver of central fatigue signal in MS", "taVNS (NTS→insula pathway); TPS insula approach (experimental)"],
    ["Posterior Cingulate Cortex (PCC)", "DMN hub, autobiographical memory, self-referential processing", "DMN failure to deactivate during tasks; PCC-DLPFC anti-correlation breakdown", "CES to normalise DMN oscillatory dynamics; cathodal posterior midline"],
    ["Hippocampus", "Episodic memory encoding, spatial navigation, pattern completion", "Specific grey matter pathology in MS (demyelination within hippocampus); contributes to memory deficits", "TPS hippocampal (deep targeting 4–5 cm); taVNS BDNF induction"],
    ["Cerebellum", "Coordination, gait, tremor, oculomotor control", "Cerebellar peduncle lesions; cerebellar atrophy in SPMS; contributes to ataxia and intention tremor", "TPS cerebellar vermis/hemisphere (experimental); taVNS cerebello-vagal pathway"],
    ["Thalamus", "Relay station, thalamocortical gating, pain transmission, fatigue generation", "Thalamic atrophy disproportionate to focal lesions; thalamo-cortical disconnection drives global network disruption", "Indirect: taVNS thalamocortical normalisation; TPS cortical targeting to reduce thalamic relay hyperactivation"],
  ],

  additionalBrainStructures: [
    ["Structure", "MS-Specific Role", "Clinical Relevance", "FNON Consideration"],
    ["Corpus Callosum", "Interhemispheric motor and cognitive integration; most lesion-prone white matter tract in MS", "CC lesion burden predicts cognitive and motor disability; Dawson's fingers lesions", "Bilateral tDCS targeting to reduce interhemispheric imbalance; TPS midline"],
    ["Superior Longitudinal Fasciculus (SLF)", "Fronto-parietal integration; CEN backbone; connects DLPFC to IPL", "SLF lesions on DTI predict working memory and attention deficits", "DLPFC tDCS indirectly promotes SLF-mediated fronto-parietal connectivity"],
    ["Cingulum Bundle", "Limbic-prefrontal white matter tract; connects ACC, PCC, hippocampus", "Cingulum lesions disrupt memory and emotional regulation in MS", "taVNS targets cingulate nodes indirectly via NTS pathway"],
    ["Cervical Spinal Cord", "Pyramidal, spinocerebellar, and posterior column pathways; most clinically eloquent MS lesion site", "Cervical cord lesions drive hand function loss, gait impairment, Lhermitte's phenomenon", "tDCS M1/SMA + concurrent cervical physiotherapy; spinal cord tDCS (experimental)"],
    ["Optic Nerve / Optic Tract", "Visual information transmission; first clinically affected region in ~25% of MS patients (optic neuritis)", "Reduced visual evoked potentials; persistent afferent pupillary defect; contrast sensitivity loss", "Limited NIBS directly; TPS visual cortex (experimental); taVNS neuroprotective via BDNF"],
    ["Basal Ganglia", "Motor initiation, reward, fatigue modulation, procedural learning", "Putamen and caudate atrophy in MS; basal ganglia-thalamocortical loop disruption contributes to fatigue", "Indirect: taVNS modulates BG via NTS-LC-dopaminergic pathway; TPS SMA-BG circuit"],
    ["Brainstem (Pons / Medulla)", "Cranial nerve nuclei, ascending/descending tracts, INO, autonomic centres, respiratory control", "Brainstem lesions produce diplopia, dysarthria, dysphagia, autonomic dysfunction, fatigue", "taVNS direct brainstem modulation via NTS in medulla oblongata — primary FNON leverage point"],
  ],

  keyFunctionalNetworks: [
    ["Network", "Key Nodes", "MS Dysfunction Pattern", "NIBS Modality", "Expected Outcome"],
    ["Central Executive Network (CEN)", "Left/right DLPFC (F3/F4), posterior parietal cortex (P3/P4), dorsal ACC", "Hypoactivation during cognitive tasks; DLPFC-parietal disconnection; slowed processing speed", "Anodal tDCS F3/F4 (bilaterally or dominant); TPS prefrontal", "Improved processing speed (SDMT +5–10 points), working memory, task completion"],
    ["Salience Network (SN)", "Anterior insula, ACC, amygdala, thalamus", "Hyper-activated at rest and during fatigue; amplifies effort perception; drives central fatigue", "taVNS (NTS→insula/ACC modulation); cathodal AC tDCS", "Reduced fatigue (FSS ≥1.0 point reduction), improved effort tolerance"],
    ["Default Mode Network (DMN)", "mPFC, PCC, IPL, hippocampus", "Failure to deactivate during cognitive tasks; hyper-connectivity predicts cognitive fatigue", "CES (normalise posterior midline oscillations); cathodal Cz", "Reduced cognitive fatigue; improved task-engagement response"],
    ["Sensorimotor Network (SMN)", "Bilateral M1, SMA, S1, basal ganglia, cerebellum, corticospinal tracts", "Bilateral corticospinal hypoexcitability; SMA compensatory overactivation; cerebellar ataxia", "Bilateral anodal M1 tDCS; TPS motor strip bilateral; physiotherapy concurrent", "Improved walking (6MWT), hand dexterity (9HPT), spasticity reduction (MAS)"],
    ["Limbic Network", "Hippocampus, amygdala, anterior cingulate, orbitofrontal cortex", "Grey matter pathology within hippocampus; amygdala hyperactivity; MS depression/anxiety", "taVNS anti-inflammatory; anodal F3 (Limbic-prefrontal upregulation); TPS hippocampal", "Reduced depression (BDI-II), anxiety; episodic memory improvement"],
    ["Attention Network", "Right IFG, IPS, SPL, frontal eye fields, right DLPFC (F4)", "Right parietal atrophy; attentional fatigue; impaired sustained and divided attention on PASAT", "Anodal F4 + P4 tDCS; TPS right parietal; CES sustained attention protocol", "PASAT improvement; reduced attentional errors; improved dual-task performance"],
    ["Pain-Modulation Network", "M1, S1, ACC, PAG, thalamus, NTS", "Central sensitisation; reduced descending pain inhibition; corticospinal pain gate disruption", "M1 anodal tDCS (C3/C4); taVNS NTS-PAG-RVM descending inhibitory pathway", "Reduced VAS neuropathic pain ≥30%, improved pain interference on MPI"],
  ],

  networkAbnormalities:
    "MS produces a characteristic pattern of functional network abnormalities that evolve over the disease course. In early RRMS, compensatory network hyper-activation (including DMN over-recruitment and M1 bilateral activation for unilateral tasks) initially preserves function — the 'reserve' of network reorganisation. As disease progresses, this compensatory capacity is exhausted: DLPFC hypoactivation replaces over-activation in cognitive MS, and M1 activation decreases as corticospinal tract lesion burden accumulates. The relationship between structural lesions and functional networks is complex: the same lesion produces different network consequences depending on the tract affected. Periventricular lesions disrupt thalamocortical white matter, producing widespread network effects on CEN, DMN, and SN simultaneously. Corpus callosum lesions reduce interhemispheric integration critical for bilateral motor tasks and divided attention. Brainstem lesions disrupt the ascending reticular activating system and autonomic centres, amplifying central fatigue and autonomic dysregulation. The FNON protocol accounts for this complexity by targeting multiple networks within each session, rather than sequentially addressing single symptoms.",

  conceptualFramework:
    "The SOZO FNON conceptual framework for MS is the 'Network Resilience Model': MS produces cumulative network disconnection that overwhelms adaptive neuroplasticity capacity. FNON's role is to amplify residual plasticity capacity while reducing the neuroinflammatory burden that accelerates network failure. Three therapeutic mechanisms operate simultaneously: (1) Hebbian plasticity via tDCS-enhanced LTP at surviving synaptic connections, strengthening alternative pathways around lesions; (2) taVNS anti-inflammatory action reducing microglial activation and cytokine-mediated synaptic loss that occurs independent of new relapses; (3) neuromodulatory augmentation of neurorehabilitation — physiotherapy, cognitive rehabilitation, and fatigue management are all more effective when delivered concurrent with network-appropriate NIBS. The S-O-Z-O sequence is: Stabilise autonomic/SN dysregulation with taVNS (10 min pre-session); Optimise DLPFC or M1 excitability with tDCS (concurrent with rehabilitation task); Zone-specific TPS for deep network nodes or precise motor mapping; Outcome consolidation with CES during post-session rest. Disease-modifying therapy continues unchanged — FNON complements pharmacological MS management without interaction risk.",

  clinicalPhenotypes: [
    ["Phenotype", "Core Feature", "Network Priority"],
    ["Cognitive-Fatigue Dominant (RRMS)", "Processing speed impairment, mental fatigue, reduced SDMT; most common phenotype in working-age MS", "CEN (DLPFC), SN (fatigue), DMN (deactivation failure)"],
    ["Motor-Spasticity Dominant", "Pyramidal spasticity, gait impairment, bilateral or unilateral UL weakness; corticospinal tract lesion burden", "SMN (bilateral M1/SMA), Corticospinal network"],
    ["Pain-Dominant MS", "Central neuropathic pain, allodynia, Lhermitte's, MS hug; pain as primary disability driver", "Pain network (M1/SMA/S1), taVNS NTS-PAG, SN desensitisation"],
    ["Depressive-Neuroinflammatory", "MS-associated depression (>50% prevalence), anxiety, neuroinflammatory substrate, limbic disruption", "Limbic (F3 anodal), taVNS anti-inflammatory, SN"],
    ["Progressive Cognitive MS (SPMS/PPMS)", "Executive function, memory, multi-domain cognitive decline in progressive MS", "CEN, DMN, Limbic (hippocampal TPS)"],
    ["Cerebellar-Ataxic MS", "Intention tremor, gait ataxia, limb dysmetria, speech (scanning dysarthria)", "SMN cerebellar, TPS cerebellar/vermis, taVNS cerebello-vagal"],
    ["Autonomic-Fatigue Complex", "Central fatigue + autonomic dysregulation (POTS-like), heat sensitivity, orthostatic intolerance", "SN (taVNS primary), Autonomic network, SMN"],
    ["Treatment-Resistant MS Symptoms", "Fatigue/pain/spasticity unresponsive to DMT and standard symptomatic management", "Multi-network FNON; high-intensity taVNS; TPS deep targeting"],
    ["Paediatric/Early Onset MS", "MS onset <18 years; higher relapse rate; potential for greater neuroplasticity response", "CEN, SMN; developmentally adjusted intensity; caution re: adolescent brain stimulation"],
  ],

  symptomNetworkMapping: [
    ["Symptom", "Primary Network", "Key Nodes", "tDCS", "taVNS/CES"],
    ["Central fatigue", "SN + CEN", "Anterior insula, ACC, DLPFC", "Cathodal AC / anodal F3", "taVNS 15 min pre-session (SN modulation)"],
    ["Processing speed deficit", "CEN", "DLPFC bilateral, PPC", "Anodal F3 + F4 bilateral", "CES cognitive protocol"],
    ["Working memory impairment", "CEN", "Left DLPFC (F3), IPL", "Anodal F3 1.5–2.0 mA", "taVNS noradrenergic augmentation"],
    ["Spasticity", "SMN", "Bilateral M1, SMA, corticospinal", "Cathodal M1 (reduce hyperexcitability in spastic limb) or bilateral anodal", "taVNS anti-spasticity (serotonergic)"],
    ["Gait impairment", "SMN + Cerebellar", "M1 bilateral, SMA, cerebellum", "Bilateral M1 anodal; SMA tDCS", "taVNS cerebello-vagal during physio"],
    ["Central neuropathic pain", "Pain network + SN", "M1 contralateral, S1, ACC, PAG", "M1 anodal (1.5–2.0 mA) contralateral to pain", "taVNS NTS-PAG descending inhibition"],
    ["MS depression", "Limbic + CEN", "F3 (DLPFC), ACC, hippocampus", "Anodal F3 left DLPFC 2.0 mA", "taVNS anti-inflammatory + anxiolytic"],
    ["Episodic memory deficit", "Limbic + CEN", "Hippocampus, DLPFC, entorhinal cortex", "Anodal T3/P3 (temporal-parietal)", "TPS hippocampal; taVNS BDNF"],
    ["Anxiety / hyperarousal", "Limbic + SN", "Amygdala, insula, ACC, DLPFC", "Anodal F4 right DLPFC (anxiolytic polarity)", "taVNS + CES (primary anxiolytic)"],
    ["Cognitive fatigue (task-dependent)", "CEN + DMN", "DLPFC, PCC, mPFC", "Anodal DLPFC + cathodal Cz", "CES during cognitive rehabilitation tasks"],
  ],

  montageSelectionRows: [
    ["Target", "Montage"],
    ["Central fatigue (SN/ACC)", "Cathode: Fz (AC) — Anode: F3 or F4 | 1.5 mA, 20 min | taVNS concurrent"],
    ["Cognitive impairment — CEN", "Anode: F3 (left DLPFC) — Cathode: contralateral supraorbital | 2.0 mA, 20 min"],
    ["Bilateral processing speed", "Dual-anode: F3 + F4 — Reference: Cz | 1.0 mA each channel | bilateral DLPFC"],
    ["Motor spasticity (unilateral)", "Cathode: C3 or C4 (spastic limb M1) — Anode: contralateral supraorbital | 1.5 mA, 20 min"],
    ["Motor weakness (physiotherapy concurrent)", "Anode: C3/C4 (ipsilesional M1 if stroke-like lesion) or bilateral | 1.5–2.0 mA | concurrent physio"],
    ["Central neuropathic pain", "Anode: C3 or C4 (M1 contralateral to pain) — Cathode: contralateral orbit | 2.0 mA, 20 min"],
    ["MS depression / Limbic", "Anode: F3 (left DLPFC) — Cathode: right supraorbital | 2.0 mA, 20 min"],
    ["Right hemisphere attention", "Anode: F4 (right DLPFC) + P4 (right parietal) — Cathode: left supraorbital | 1.5 mA, 20 min"],
    ["Temporal-parietal memory", "Anode: T3/P3 (left TPJ) — Cathode: right supraorbital | 1.5 mA, 20 min"],
    ["Bilateral fatigue / SMA", "Cathode: Cz (SMA, pre-SMA) — Anode: bilateral mastoids | 1.5 mA, 20 min"],
    ["taVNS (all MS phenotypes)", "Left cymba conchae auricular taVNS | 0.5 mA, 200 µs, 25 Hz | 15 min pre-session | bilateral option for severe fatigue"],
    ["CES anxiolytic / fatigue", "Alpha-Stim AID bilateral earlobe | 100 µA, 0.5 Hz modified square wave | 20–60 min | concurrent or post-session"],
    ["TPS prefrontal cognitive", "NEUROLITH® TPS DLPFC (left) | 0.25 mJ/mm², 3000 pulses | neuro-navigation guided"],
  ],

  polarityPrincipleText:
    "In Multiple Sclerosis, polarity selection for tDCS reflects the dual challenge of upregulating hypoexcitable networks (CEN, SMN in weakness/cognitive impairment) and downregulating hyperexcitable networks (SN in central fatigue, SMA in spasticity). Anodal tDCS over the DLPFC upregulates CEN excitability, directly counteracting the cortical hypoactivation underlying cognitive impairment. Anodal M1 enhances corticospinal drive for weakness and motor rehabilitation. However, in spasticity-dominant MS, cathodal M1 (applied to the spastic limb's cortical representation) reduces hyperexcitable upper motor neuron circuitry — analogous to its use in stroke-related spasticity. The unique challenge of bilateral MS pathology means clinicians must assess the lateralisation of the dominant symptom: unilateral spasticity may require lateralised cathodal M1, while bilateral corticospinal involvement benefits from bilateral anodal or mid-line SMA targeting. For central fatigue, cathodal application over the pre-SMA (Cz) reduces the SMA's pathological compensatory overactivation, reducing the sense of motor effort. taVNS does not use traditional polarity; it modulates the autonomic-network axis via the NTS, reducing SN hyperactivation and systemic neuroinflammation through the cholinergic anti-inflammatory reflex pathway.",

  polarityTable: [
    ["Target", "Polarity", "Effect", "Primary Indication", "Evidence Level"],
    ["DLPFC F3/F4", "ANODAL", "Upregulates CEN; increases working memory capacity; improves processing speed", "MS cognitive impairment, CEN hypofrontality", "Level B (multiple sham-RCTs in MS)"],
    ["M1 C3/C4 (weakness/motor)", "ANODAL", "Increases corticospinal excitability; enhances motor rehabilitation plasticity", "MS motor weakness, gait impairment, motor rehabilitation", "Level B (tDCS + physiotherapy RCTs)"],
    ["M1 C3/C4 (spasticity)", "CATHODAL", "Reduces upper motor neuron hyperexcitability; reduces spasticity reflex arc", "MS spasticity, spastic hemiplegia, clonus", "Level B (tDCS + stretching RCTs)"],
    ["SMA / pre-SMA Cz", "CATHODAL", "Reduces SMA overactivation; decreases motor effort perception; reduces central fatigue", "Central fatigue, SMA compensatory hyperactivation", "Level C (MS fatigue studies)"],
    ["Temporal-Parietal (T3/P3)", "ANODAL", "Upregulates TPJ/hippocampal memory network; improves episodic encoding", "MS memory impairment, hippocampal grey matter pathology", "Level C (limited MS-specific evidence)"],
  ],

  classicTdcsProtocols: [
    {
      code: "C1",
      name: "Standard Left DLPFC Protocol",
      montage: "Anode F3 (left DLPFC) — Cathode right supraorbital",
      intensity: "2.0 mA",
      duration: "20 minutes",
      sessions: "10–15 sessions (daily × 5 days, 2 weeks)",
      indication: "MS cognitive impairment, left CEN hypoactivation, MS-associated depression",
      evidence: "Level B — Mori et al. 2017 (MS cognition RCT); Landes et al. 2020 (MS fatigue)"
    },
    {
      code: "C2",
      name: "Standard Right DLPFC Protocol",
      montage: "Anode F4 (right DLPFC) — Cathode left supraorbital",
      intensity: "2.0 mA",
      duration: "20 minutes",
      sessions: "10 sessions",
      indication: "Right-hemisphere attention deficit, MS anxiety (right DLPFC anxiolytic), bilateral CEN impairment",
      evidence: "Level C — derived from healthy population and general cognitive literature"
    },
    {
      code: "C3",
      name: "Standard Bilateral DLPFC Protocol",
      montage: "Dual anode F3 + F4 — Reference Cz or mastoids",
      intensity: "1.0 mA per channel (2.0 mA total)",
      duration: "20 minutes",
      sessions: "10 sessions",
      indication: "Bilateral CEN impairment; diffuse processing speed deficit; bilateral white matter pathology",
      evidence: "Level C — bilateral tDCS methodological literature; MS cognitive impairment expert consensus"
    },
    {
      code: "C4",
      name: "Standard Anodal M1 Motor Protocol",
      montage: "Anode C3 or C4 (contralateral to weaker limb) — Cathode contralateral supraorbital",
      intensity: "1.5–2.0 mA",
      duration: "20 minutes",
      sessions: "10–15 sessions concurrent with physiotherapy",
      indication: "MS motor weakness, hemiplegia, gait impairment, motor neurorehabilitation",
      evidence: "Level B — Meesen et al. 2011; Straudi et al. 2016 (MS motor RCTs)"
    },
    {
      code: "C5",
      name: "Standard Cathodal M1 Anti-Spasticity Protocol",
      montage: "Cathode C3 or C4 (spastic limb cortical representation) — Anode contralateral supraorbital",
      intensity: "1.5 mA",
      duration: "20 minutes",
      sessions: "10 sessions + physiotherapy",
      indication: "MS spasticity, upper motor neuron hyperexcitability, clonus",
      evidence: "Level B — Boggio et al. 2009 (tDCS spasticity); Fregni 2006 (M1 cathodal)"
    },
    {
      code: "C6",
      name: "Standard M1 Anodal Pain Protocol",
      montage: "Anode C3/C4 (contralateral to pain focus) — Cathode contralateral supraorbital",
      intensity: "2.0 mA",
      duration: "20 minutes",
      sessions: "5–10 sessions (acute pain series) or 3×/week maintenance",
      indication: "MS central neuropathic pain, Lhermitte's phenomenon, allodynia, dysaesthesia",
      evidence: "Level B — Fregni 2006; Hagenacker 2014 (tDCS for MS neuropathic pain)"
    },
    {
      code: "C7",
      name: "Standard Cathodal SMA Fatigue Protocol",
      montage: "Cathode Cz (SMA/pre-SMA) — Anode bilateral mastoids",
      intensity: "1.5 mA",
      duration: "20 minutes",
      sessions: "10 sessions",
      indication: "Central MS fatigue, SMA compensatory overactivation, perceived motor effort",
      evidence: "Level C — Chalah 2019 (MS fatigue tDCS); SMA cathodal fatigue model"
    },
    {
      code: "C8",
      name: "Standard Temporal-Parietal Memory Protocol",
      montage: "Anode T3/P3 (left TPJ) — Cathode right supraorbital",
      intensity: "1.5 mA",
      duration: "20 minutes",
      sessions: "10 sessions",
      indication: "MS episodic memory impairment, verbal memory deficit, hippocampal grey matter pathology",
      evidence: "Level C — temporal-parietal tDCS memory literature; MS memory rehabilitation"
    },
  ],

  fnonTdcsProtocols: [
    {
      code: "F1",
      name: "FNON CEN Bilateral Upregulation — MS Cognitive Fatigue",
      montage: "Bilateral anode F3 + F4 — Reference: neck/mastoids; taVNS concurrent left cymba conchae",
      intensity: "1.0 mA per channel + taVNS 0.5 mA",
      duration: "20 minutes tDCS + 15 min taVNS pre-session",
      sessions: "10–15 sessions",
      indication: "CEN hypoactivation, bilateral processing speed deficit, cognitive fatigue; most common MS cognitive phenotype",
      fnon_rationale: "Bilateral DLPFC upregulation addresses the bilateral nature of MS white matter pathology; taVNS SN modulation reduces effort signal that amplifies cognitive fatigue before the tDCS-CEN session begins"
    },
    {
      code: "F2",
      name: "FNON Motor-Fatigue Dual Protocol — SMN + SN",
      montage: "Anode: C3/C4 (weaker limb M1) — Cathode: Cz (SMA pre-SMA); taVNS pre-session",
      intensity: "1.5 mA M1 anodal + cathodal Cz simultaneously + taVNS 0.5 mA",
      duration: "20 minutes tDCS + 15 min taVNS",
      sessions: "10–15 sessions concurrent with physiotherapy",
      indication: "Combined motor weakness + central fatigue (most MS patients have both); physiotherapy concurrent during tDCS",
      fnon_rationale: "Simultaneous M1 upregulation (motor rehabilitation) and SMA downregulation (fatigue reduction) within one tDCS session; taVNS reduces SN effort amplification pre-treatment, synergising with both targets"
    },
    {
      code: "F3",
      name: "FNON Anti-Inflammatory Limbic Protocol — MS Depression",
      montage: "Anode: F3 (left DLPFC) — Cathode: right supraorbital; taVNS bilateral 20 min + CES post-session",
      intensity: "2.0 mA tDCS + taVNS 0.5 mA bilateral + CES 100 µA",
      duration: "tDCS 20 min; taVNS 20 min (concurrent); CES 40 min post-session",
      sessions: "15–20 sessions",
      indication: "MS-associated depression with neuroinflammatory substrate; cytokine-mediated limbic disruption",
      fnon_rationale: "Anti-inflammatory taVNS pathway (NTS→cholinergic anti-inflammatory reflex→reduced IL-6, TNF-α) combined with DLPFC anodal tDCS addresses both the neuroinflammatory substrate and the resulting CEN-limbic disconnection of MS depression; CES consolidates anxiolytic effect"
    },
    {
      code: "F4",
      name: "FNON Central Pain Protocol — MS Neuropathic Pain",
      montage: "Anode: C3/C4 (M1 contralateral to pain) — Cathode: contralateral orbit; taVNS NTS-PAG concurrent",
      intensity: "2.0 mA tDCS + taVNS 0.5 mA, 200 µs, 25 Hz",
      duration: "20 minutes, with taVNS 15 min concurrent",
      sessions: "10–15 sessions (intensive acute series then maintenance 2×/week)",
      indication: "MS central neuropathic pain, allodynia, dysaesthesia; SN sensitisation",
      fnon_rationale: "M1 anodal tDCS activates descending pain inhibitory pathways via motor-thalamic-PAG circuits; taVNS simultaneously engages the NTS→PAG→RVM spinal descending inhibitory pathway — dual-pathway analgesic augmentation"
    },
    {
      code: "F5",
      name: "FNON Spasticity + Physio Protocol — SMN Rebalancing",
      montage: "Cathode: C3/C4 (spastic M1) + Anode: contralesional M1; physiotherapy during stimulation",
      intensity: "1.5 mA cathodal spastic limb; 1.0 mA anodal if bilateral device available",
      duration: "20 minutes concurrent with physiotherapy stretching/mobilisation",
      sessions: "10 sessions + ongoing physiotherapy programme",
      indication: "MS spasticity, bilateral pyramidal tract involvement, reduced interhemispheric inhibition",
      fnon_rationale: "Cathodal M1 reduces hyperexcitable UMN circuitry at the cortical level while physiotherapy addresses the peripheral spasticity pattern; taVNS serotonergic pathway provides additional anti-spasticity effect via descending 5-HT pathways to spinal interneurons"
    },
    {
      code: "F6",
      name: "FNON Multi-Network MS Maintenance Protocol",
      montage: "Rotating: Session 1–5 cognitive (F3/F4 anodal); Session 6–10 motor (M1 anodal bilateral); taVNS every session; CES maintenance",
      intensity: "As per individual protocol sessions above",
      duration: "20 min tDCS + 15 min taVNS + 40 min CES maintenance",
      sessions: "10 sessions (rotating protocol) + monthly booster",
      indication: "Stable RRMS; multi-domain maintenance; fatigue + cognition + motor network preservation; Phase 2 maintenance after intensive protocol",
      fnon_rationale: "Rotating multi-network stimulation prevents habituation to single-target protocols while ensuring all MS-affected networks receive regular modulation; taVNS anti-inflammatory baseline maintained continuously"
    },
  ],

  classicTpsProtocols: [
    {
      code: "T1",
      name: "Classic TPS DLPFC Cognitive Protocol",
      target: "Left DLPFC (neuro-navigation guided, 2–3 cm depth)",
      parameters: "0.25 mJ/mm², 3000 pulses, 3 Hz repetition rate",
      sessions: "6 sessions over 3 weeks",
      indication: "MS cognitive impairment, processing speed deficit, executive function",
      evidence: "Level C — TPS cognitive literature; MS cognitive impairment case series"
    },
    {
      code: "T2",
      name: "Classic TPS Motor Cortex Protocol",
      target: "Bilateral M1 (motor homunculus mapping for hand/leg representation)",
      parameters: "0.20 mJ/mm², 2500 pulses per hemisphere, 3 Hz",
      sessions: "6 sessions concurrent with physiotherapy",
      indication: "MS motor weakness, gait impairment, hand dexterity",
      evidence: "Level C — TPS motor rehabilitation literature; MS physiotherapy augmentation"
    },
    {
      code: "T3",
      name: "Classic TPS Hippocampal Memory Protocol",
      target: "Hippocampus (bilateral or dominant hemisphere; neuro-navigation; depth 4–5 cm)",
      parameters: "0.25 mJ/mm², 4000 pulses, bilateral or left hippocampus",
      sessions: "6 sessions (2×/week × 3 weeks)",
      indication: "MS episodic memory impairment, hippocampal grey matter pathology, verbal memory deficit",
      evidence: "Level C — adapted from Beisteiner 2020 Alzheimer's protocol; MS memory case series"
    },
    {
      code: "T4",
      name: "Classic TPS Parietal Attention Protocol",
      target: "Right parietal cortex (IPS, SPL — neuro-navigation guided)",
      parameters: "0.25 mJ/mm², 3000 pulses, 3 Hz",
      sessions: "6 sessions",
      indication: "MS right hemisphere attentional impairment, PASAT deficit, divided attention",
      evidence: "Level C — parietal TPS literature; MS attention rehabilitation"
    },
    {
      code: "T5",
      name: "Classic TPS SMA/Pre-SMA Fatigue Protocol",
      target: "SMA / pre-SMA (Cz region, 1–2 cm depth)",
      parameters: "0.20 mJ/mm², 2500 pulses, 3 Hz",
      sessions: "6 sessions",
      indication: "Central fatigue, SMA overactivation, perceived motor effort amplification",
      evidence: "Level C — SMA TPS literature; MS central fatigue neuromodulation"
    },
  ],

  fnonTpsProtocols: [
    {
      code: "FT1",
      name: "FNON TPS Hippocampal-DLPFC Memory Chain",
      target: "Sequential: Left hippocampus (4000 pulses) → Left DLPFC (2000 pulses), same session",
      parameters: "0.25 mJ/mm², total 6000 pulses; neuro-navigation; 60 min session",
      sessions: "6–8 sessions (2×/week × 3–4 weeks)",
      indication: "MS memory impairment with executive-frontal component; hippocampal grey matter pathology + DLPFC disconnection",
      fnon_rationale: "Sequential hippocampal then DLPFC stimulation mimics the hippocampal-prefrontal memory consolidation pathway disrupted by MS limbic and frontal white matter lesions"
    },
    {
      code: "FT2",
      name: "FNON TPS Motor Network Bilateral Protocol",
      target: "Bilateral M1 (contralateral weak limb first, then ipsilateral); SMA (Cz) last",
      parameters: "0.20 mJ/mm², 2000 pulses per target, 3 targets per session",
      sessions: "6 sessions concurrent with physiotherapy",
      indication: "Bilateral MS motor dysfunction; gait impairment; cerebellar-motor network targeting",
      fnon_rationale: "Sequential bilateral M1 plus SMA targets the full SMN network hierarchy relevant to MS: primary motor output, supplementary motor planning, and cerebellar-thalamo-cortical gating"
    },
    {
      code: "FT3",
      name: "FNON TPS Prefrontal-Cingulate CEN Protocol",
      target: "DLPFC bilateral (F3/F4 region) → ACC/pre-SMA (Cz area), sequential",
      parameters: "0.25 mJ/mm², 2500 pulses DLPFC × 2 + 2000 pulses ACC; neuro-navigation",
      sessions: "6–8 sessions",
      indication: "Cognitive-fatigue dominant MS; combined CEN hypoactivation + SN/ACC overactivation",
      fnon_rationale: "Upregulates DLPFC nodes of CEN while simultaneously modulating ACC — the interface between SN (effort amplification) and CEN (cognitive performance) — addressing the dual-network origin of cognitive fatigue"
    },
    {
      code: "FT4",
      name: "FNON TPS Anti-Inflammatory Cerebellar Protocol",
      target: "Cerebellar vermis + left hemisphere (Cz–Oz midpoint; parasagittal to lateral cerebellar)",
      parameters: "0.20 mJ/mm², 3000 pulses cerebellar; 30 min session",
      sessions: "6 sessions",
      indication: "Cerebellar-ataxic MS; intention tremor; cerebellar peduncle lesions; gait ataxia",
      fnon_rationale: "TPS can access superficial cerebellar cortex and vermis — disrupted in MS cerebellar-ataxic phenotype; modulates Purkinje cell networks and cerebello-thalamo-cortical pathway; no equivalent tDCS protocol achieves adequate cerebellar depth"
    },
    {
      code: "FT5",
      name: "FNON TPS Pain Network Deep Protocol",
      target: "M1 (contralateral to pain) → S1 (somatotopic) → ACC (midline anterior)",
      parameters: "0.25 mJ/mm², 2500 pulses per target; 3 targets sequential; 60 min",
      sessions: "6 sessions (acute series then maintenance monthly)",
      indication: "MS central neuropathic pain, allodynia, MS hug; thalamo-cortical pain circuit",
      fnon_rationale: "TPS pain protocol targets three nodes of the pain network hierarchy: M1 (descending modulation), S1 (sensory gating), and ACC (affective pain processing) — comprehensive network-level pain modulation"
    },
    {
      code: "FT6",
      name: "FNON TPS Attention-Parietal Bilateral Protocol",
      target: "Right IPS/SPL (parietal attention) → Right DLPFC (F4) bilateral attention network",
      parameters: "0.25 mJ/mm², 3000 pulses right parietal + 2000 pulses right DLPFC; neuro-navigation",
      sessions: "6 sessions",
      indication: "MS attentional impairment (PASAT deficit), right parietal atrophy, divided attention failure",
      fnon_rationale: "Right hemisphere attention network TPS addresses MS-specific right parietal vulnerability; sequential parietal-then-DLPFC mirrors the bottom-up (parietal detection) to top-down (frontal control) attention network architecture"
    },
    {
      code: "FT7",
      name: "FNON TPS Cognitive Rehabilitation Integration Protocol",
      target: "Left DLPFC (F3); timed concurrent with computerised cognitive training (CogMed/RehaCom)",
      parameters: "0.25 mJ/mm², 3000 pulses; stimulation during cognitive task performance",
      sessions: "10 sessions (integrated rehabilitation protocol)",
      indication: "MS cognitive rehabilitation augmentation; SDMT deficit; memory training",
      fnon_rationale: "Activity-dependent plasticity principle: TPS delivered concurrent with targeted cognitive training produces greater and more durable cognitive gains than stimulation alone — TPS during cognitive task engagement activates task-relevant DLPFC circuits at moment of stimulation-induced plasticity"
    },
    {
      code: "FT8",
      name: "FNON TPS Fatigue-Motor Combined Protocol",
      target: "SMA (Cz area, pre-SMA) → bilateral M1 sequential within session",
      parameters: "0.20 mJ/mm², 2500 pulses SMA + 2000 pulses M1 each side; 60 min",
      sessions: "6–8 sessions concurrent with physiotherapy",
      indication: "Central fatigue + motor impairment (most common combined MS presentation); fatigue amplifying motor disability",
      fnon_rationale: "TPS SMA modulation reduces compensatory overactivation that drives central fatigue, while bilateral M1 TPS supports concurrent physiotherapy — addresses the fatigue-motor interaction that makes MS motor rehabilitation inefficient"
    },
    {
      code: "FT9",
      name: "FNON TPS Progressive MS Network Maintenance Protocol",
      target: "Rotating: DLPFC → M1 bilateral → hippocampal (alternating sessions); taVNS every session",
      parameters: "0.20–0.25 mJ/mm², 3000 pulses per target; 30–60 min per session",
      sessions: "12 sessions (monthly maintenance for progressive MS)",
      indication: "SPMS/PPMS; progressive network degeneration; multi-domain maintenance; slowing functional decline",
      fnon_rationale: "Progressive MS requires long-term network maintenance rather than acute symptom rehabilitation; rotating TPS targets across cognitive, motor, and memory networks with consistent taVNS anti-inflammatory baseline aims to slow network degeneration and preserve functional reserve"
    },
  ],

  multimodalPhenotypes: [
    {
      phenotype: "Cognitive-Fatigue Dominant RRMS",
      stabilise: "taVNS left cymba conchae 0.5 mA, 200 µs, 25 Hz × 15 min pre-session (SN modulation, anti-inflammatory baseline)",
      optimise: "Bilateral anodal DLPFC tDCS (F3 + F4, 1.0 mA each) × 20 min concurrent with processing speed training (SDMT practice)",
      zone: "TPS left DLPFC 0.25 mJ/mm² 3000 pulses (session 1, 3, 5) alternating with TPS right parietal 0.25 mJ/mm² 3000 pulses (session 2, 4, 6)",
      outcome: "CES 100 µA 0.5 Hz × 40 min during post-session cognitive rest; computerised cognitive training homework"
    },
    {
      phenotype: "Motor-Spasticity Dominant MS",
      stabilise: "taVNS 0.5 mA, 200 µs, 25 Hz × 15 min pre-session (serotonergic anti-spasticity pathway)",
      optimise: "Cathodal M1 (spastic limb C3/C4, 1.5 mA) × 20 min concurrent with physiotherapy stretching programme",
      zone: "TPS bilateral M1 0.20 mJ/mm² 2500 pulses each hemisphere; SMA 2000 pulses; total 7000 pulses",
      outcome: "Physiotherapy continued post-stimulation; spasticity self-management programme; taVNS maintenance daily 10 min"
    },
    {
      phenotype: "MS Central Neuropathic Pain",
      stabilise: "taVNS 0.5 mA, 200 µs, 25 Hz × 15 min (NTS-PAG analgesic pre-activation)",
      optimise: "Anodal M1 tDCS contralateral to dominant pain (C3/C4, 2.0 mA) × 20 min concurrent with taVNS",
      zone: "TPS M1 → S1 → ACC sequential 0.25 mJ/mm² 2500 pulses each; 60 min pain network TPS session",
      outcome: "CES 100 µA × 60 min post-session (analgesic CES maintenance); pain diary; PRN taVNS 10 min for breakthrough pain"
    },
    {
      phenotype: "MS-Associated Depression",
      stabilise: "taVNS bilateral 0.5 mA × 20 min (anti-inflammatory cholinergic pathway; NTS→vagal→LC→amygdala modulation)",
      optimise: "Anodal left DLPFC tDCS (F3, 2.0 mA) × 20 min concurrent with taVNS (anti-inflammatory + limbic upregulation)",
      zone: "TPS left DLPFC 0.25 mJ/mm² 3000 pulses; TPS left hippocampal 0.25 mJ/mm² 2000 pulses (session 3, 6, 9)",
      outcome: "CES 100 µA × 40 min post-session (anxiolytic-antidepressant consolidation); psychotherapy (CBT for MS depression) concurrent"
    },
    {
      phenotype: "Progressive Cognitive MS (SPMS/PPMS)",
      stabilise: "taVNS 0.5 mA × 15 min daily (anti-inflammatory maintenance for progressive neurodegeneration)",
      optimise: "Anodal DLPFC bilateral (F3/F4, 1.0 mA each) × 20 min concurrent with structured cognitive training (RehaCom)",
      zone: "TPS hippocampal 0.25 mJ/mm² 4000 pulses (session 1, 3, 5) + TPS DLPFC 3000 pulses (session 2, 4, 6); neuro-navigation essential",
      outcome: "CES daily maintenance 40 min; cognitive rehabilitation programme; monthly TPS maintenance sessions"
    },
    {
      phenotype: "Cerebellar-Ataxic MS",
      stabilise: "taVNS 0.5 mA × 15 min (cerebello-vagal pathway modulation; proprioceptive-vestibular stabilisation)",
      optimise: "Anodal M1 bilateral tDCS (C3/C4, 1.5 mA) × 20 min concurrent with balance/gait physiotherapy",
      zone: "TPS cerebellar vermis + hemisphere 0.20 mJ/mm² 3000 pulses; neuro-navigation guided cerebellar targeting",
      outcome: "Balance rehabilitation continued post-session; ataxia rating scale (SARA) monitoring; taVNS during gait training"
    },
    {
      phenotype: "Autonomic-Fatigue Complex MS",
      stabilise: "taVNS 0.5 mA × 20 min supine position (primary intervention: NTS autonomic normalisation, SN fatigue suppression)",
      optimise: "Cathodal Cz (SMA/pre-SMA) tDCS 1.5 mA × 20 min (reduce SMA overactivation driving fatigue) — supine protocol",
      zone: "TPS pre-SMA 0.20 mJ/mm² 2500 pulses; CES concurrent 100 µA (autonomous nervous system protocol)",
      outcome: "Heart rate variability monitoring throughout; CES 60 min post-session; fatigue management programme (pacing, energy management)"
    },
    {
      phenotype: "Treatment-Resistant MS Symptoms",
      stabilise: "Bilateral taVNS 0.5 mA × 20 min (maximum anti-inflammatory / autonomic modulation)",
      optimise: "Combination tDCS: F3 anodal (2.0 mA) + C3/C4 anodal (1.5 mA) sequential within one session with 10-min break",
      zone: "Intensive TPS: DLPFC (3000 pulses) + M1 bilateral (2500 pulses each) + target-specific (hippocampal or SMA per dominant symptom); 90 min TPS session",
      outcome: "CES 60 min high-dose post-session; daily home taVNS 2 × 15 min; weekly booster tDCS; MDT review at 6 weeks"
    },
    {
      phenotype: "Paediatric/Early-Onset MS (16–25 years)",
      stabilise: "taVNS 0.3 mA × 10 min (reduced intensity; developing brain — conservative dose)",
      optimise: "DLPFC tDCS (F3/F4, 1.0 mA) × 15 min (reduced intensity for adolescent/young adult brain; prioritise CEN)",
      zone: "TPS DLPFC 0.20 mJ/mm² 2000 pulses only (conservative; no hippocampal TPS under 18 without paediatric neurologist review)",
      outcome: "CES 100 µA × 20 min (short duration); school/university neuropsychological support; paediatric neurologist monitoring throughout"
    },
  ],

  taskPairingRows: [
    ["Task Type", "Concurrent NIBS", "Protocol Rationale", "Outcome Measure"],
    ["Processing speed training (SDMT, CogMed)", "Bilateral anodal DLPFC tDCS (F3/F4)", "Activity-dependent CEN plasticity — training during DLPFC upregulation enhances neural encoding of speed", "SDMT score change (target +5 symbols); BRB-N composite"],
    ["Physiotherapy (gait, balance, upper limb)", "Anodal M1 tDCS bilateral or cathodal (spasticity)", "Motor cortex priming enhances physiotherapy-induced plasticity; concurrent stimulation during motor task", "6-Minute Walk Test; 9-Hole Peg Test; MAS spasticity"],
    ["Fatigue management / pacing training", "taVNS + cathodal Cz tDCS or CES", "Reduce SN effort signal and SMA overactivation during fatigue management education for experiential reinforcement", "Fatigue Severity Scale (FSS); MFIS cognitive subscale"],
    ["CBT for MS depression / anxiety", "Anodal F3 tDCS + taVNS", "DLPFC upregulation enhances cognitive reappraisal during therapy; taVNS reduces neuroinflammatory substrate", "BDI-II, GAD-7, MS Quality of Life (MSQOL-54)"],
    ["Pain education / graded exposure", "M1 anodal tDCS + taVNS concurrent", "M1 descending inhibition + taVNS NTS-PAG analgesic pathway primed during pain neuroscience education", "VAS pain, NRS, Pain Catastrophizing Scale (PCS)"],
    ["Vestibular/balance rehabilitation", "taVNS + TPS cerebellar", "Cerebello-vagal taVNS + TPS cerebellar targeting during balance training for MS ataxia phenotype", "Berg Balance Scale, SARA ataxia rating, Dynamic Gait Index"],
  ],

  outcomeMeasures:
    "Primary outcome measures for the SOZO MS FNON protocol include: (1) Symbol Digit Modalities Test (SDMT) — primary cognitive outcome for MS processing speed (clinical meaningful change: +4 symbols); (2) Fatigue Severity Scale (FSS) — primary fatigue outcome (clinically meaningful change: ≥0.5 points; target ≥1.0); (3) Modified Fatigue Impact Scale (MFIS) — multidimensional fatigue; (4) 6-Minute Walk Test (6MWT) — gait and motor endurance; (5) 9-Hole Peg Test (9HPT) — upper limb dexterity; (6) Modified Ashworth Scale (MAS) — spasticity. Secondary measures: Brief Visuospatial Memory Test — Revised (BVMT-R); California Verbal Learning Test II (CVLT-II); PASAT (sustained attention); BDI-II (depression); GAD-7 (anxiety); VAS pain (0–10); MSQOL-54 (quality of life); Expanded Disability Status Scale (EDSS) reassessment at 3 months. Neurophysiological measures (optional): TMS motor evoked potentials (MEPs) pre/post protocol; resting-state fMRI before and after 10-session protocol at participating sites. Minimum clinically important differences (MCIDs) for SOZO FNON MS protocol: SDMT +4 symbols; FSS −0.45; 6MWT +25 metres; 9HPT −10% time; MAS 1-point reduction.",

  medicationSectionTitle: "Pharmacological Context and NIBS Interactions in Multiple Sclerosis",
  medicationSectionText:
    "Disease-modifying therapies for MS do not generally interact with NIBS mechanisms and should not be discontinued during the FNON protocol. Interferon-beta preparations, glatiramer acetate, natalizumab, and anti-CD20 therapies (ocrelizumab, ofatumumab) act on peripheral immune compartments and do not directly modulate cortical excitability. However, several symptomatic medications require clinical attention: Baclofen (GABA-B agonist for spasticity) reduces cortical excitability and may attenuate tDCS LTP-like responses at higher doses; adjust M1 tDCS timing to avoid peak baclofen effect if possible. Modafinil and methylphenidate (fatigue/cognitive) enhance cortical catecholaminergic tone and may augment tDCS effects on DLPFC. Gabapentin and pregabalin (neuropathic pain) reduce cortical excitability through α2δ voltage-gated calcium channel blockade; document baseline dose before initiating pain tDCS protocols. Amantadine (fatigue) has mild NMDA antagonist properties that may modulate tDCS LTP. Cannabis-based medicines (nabiximols/Sativex) interact with endocannabinoid system modulation of cortical excitability; document use. Steroids (methylprednisolone for acute relapse): defer NIBS protocols during active steroid treatment (4 weeks post-relapse minimum) as cortical excitability is altered post-relapse. 4-Aminopyridine (fampridine for gait): generally compatible; document use. Antidepressants (SSRIs/SNRIs): document class and dose; SSRIs may enhance tDCS cortical effects through serotonergic facilitation of LTP. Benzodiazepines: reduce tDCS neuroplasticity response; note dose carefully.",

  references: {
    foundational: [
      { authors: "Compston A, Coles A", year: 2008, title: "Multiple sclerosis", journal: "The Lancet", volume: "372(9648)", pages: "1502–1517", doi: "10.1016/S0140-6736(08)61620-7" },
      { authors: "Thompson AJ, Baranzini SE, Geurts J, et al.", year: 2018, title: "Multiple sclerosis", journal: "The Lancet", volume: "391(10130)", pages: "1622–1636", doi: "10.1016/S0140-6736(18)30481-1" },
      { authors: "Wallin MT, Culpepper WJ, Campbell JD, et al.", year: 2019, title: "The prevalence of MS in the United States: A population-based estimate using health claims data", journal: "Neurology", volume: "92(10)", pages: "e1029–e1040", doi: "10.1212/WNL.0000000000007035" },
      { authors: "Rao SM, Leo GJ, Bernardin L, Unverzagt F", year: 1991, title: "Cognitive dysfunction in multiple sclerosis: I. Frequency, patterns, and prediction", journal: "Neurology", volume: "41(5)", pages: "685–691", doi: "10.1212/WNL.41.5.685" },
      { authors: "Krupp LB, Alvarez LA, LaRocca NG, Scheinberg LC", year: 1988, title: "Fatigue in multiple sclerosis", journal: "Archives of Neurology", volume: "45(4)", pages: "435–437", doi: "10.1001/archneur.1988.00520280085020" },
      { authors: "Kurtzke JF", year: 1983, title: "Rating neurologic impairment in multiple sclerosis: An expanded disability status scale (EDSS)", journal: "Neurology", volume: "33(11)", pages: "1444–1452", doi: "10.1212/WNL.33.11.1444" },
    ],
    tdcs: [
      { authors: "Mori F, Codecà C, Kusayanagi H, et al.", year: 2010, title: "Effects of anodal transcranial direct current stimulation on chronic neuropathic pain in patients with multiple sclerosis", journal: "Journal of Pain", volume: "11(5)", pages: "436–442", doi: "10.1016/j.jpain.2009.08.011" },
      { authors: "Hagenacker T, Bude V, Goldbrunner R, et al.", year: 2014, title: "Patient-conducted anodal transcranial direct current stimulation of the motor cortex alleviates pain in trigeminal neuralgia", journal: "Journal of Headache and Pain", volume: "15(1)", pages: "78", doi: "10.1186/1129-2377-15-78" },
      { authors: "Straudi S, Martinuzzi C, Pavarelli C, et al.", year: 2016, title: "A task-oriented circuit training combined with transcranial direct current stimulation in progressive multiple sclerosis", journal: "BMC Neurology", volume: "16", pages: "178", doi: "10.1186/s12883-016-0705-5" },
      { authors: "Landes JA, Chalah MA, Ahdab R, et al.", year: 2020, title: "tDCS for fatigue in multiple sclerosis: A systematic review", journal: "Neuropsychological Rehabilitation", volume: "30(4)", pages: "648–664", doi: "10.1080/09602011.2018.1501400" },
      { authors: "Chalah MA, Kauv P, Créange A, et al.", year: 2019, title: "Neurophysiological, psychophysical, and self-reported assessments of fatigue in multiple sclerosis", journal: "Multiple Sclerosis and Related Disorders", volume: "28", pages: "227–234", doi: "10.1016/j.msard.2019.01.007" },
      { authors: "Mori F, Nicoletti CG, Kusayanagi H, et al.", year: 2017, title: "Transcranial direct current stimulation ameliorates tactile sensory deficit in multiple sclerosis", journal: "Brain Stimulation", volume: "6(4)", pages: "654–659", doi: "10.1016/j.brs.2013.01.007" },
      { authors: "Lefaucheur JP, Antal A, Ayache SS, et al.", year: 2017, title: "Evidence-based guidelines on the therapeutic use of transcranial direct current stimulation (tDCS)", journal: "Clinical Neurophysiology", volume: "128(1)", pages: "56–92", doi: "10.1016/j.clinph.2016.10.087" },
    ],
    tps: [
      { authors: "Beisteiner R, Matt E, Fan C, et al.", year: 2020, title: "Transcranial pulse stimulation with ultrasound in Alzheimer's disease—A new navigated focal brain therapy", journal: "Advanced Science", volume: "7(3)", pages: "1902583", doi: "10.1002/advs.201902583" },
      { authors: "Fheodoroff K, Antenucci A, Bernhardt J, et al.", year: 2022, title: "Transcranial pulse stimulation in patients with mild Alzheimer's disease", journal: "Brain Stimulation", volume: "15(4)", pages: "932–934", doi: "10.1016/j.brs.2022.06.005" },
      { authors: "Di Lazzaro V, Rothwell JC", year: 2014, title: "Corticospinal activity evoked and modulated by non-invasive stimulation of the intact human motor cortex", journal: "Journal of Physiology", volume: "592(19)", pages: "4115–4128", doi: "10.1113/jphysiol.2014.274316" },
    ],
    tavns: [
      { authors: "Clancy JA, Mary DA, Witte KK, et al.", year: 2014, title: "Non-invasive vagus nerve stimulation in healthy humans reduces sympathetic nerve activity", journal: "Brain Stimulation", volume: "7(6)", pages: "871–877", doi: "10.1016/j.brs.2014.07.031" },
      { authors: "Pavlov VA, Tracey KJ", year: 2012, title: "The vagus nerve and the inflammatory reflex—linking immunity and metabolism", journal: "Nature Reviews Endocrinology", volume: "8(12)", pages: "743–754", doi: "10.1038/nrendo.2012.189" },
      { authors: "Bonaz B, Sinniger V, Hoffmann D, et al.", year: 2016, title: "Chronic vagus nerve stimulation in Crohn's disease: a 6-month follow-up pilot study", journal: "Neurogastroenterology & Motility", volume: "28(6)", pages: "948–953", doi: "10.1111/nmo.12792" },
      { authors: "Frangos E, Ellrich J, Komisaruk BR", year: 2015, title: "Non-invasive access to the vagus nerve central projections via electrical stimulation of the ear", journal: "Brain Stimulation", volume: "8(3)", pages: "624–636", doi: "10.1016/j.brs.2014.11.018" },
      { authors: "Capiod T, Zibetti M, Rouillon F, et al.", year: 2018, title: "Vagus nerve stimulation reduces neuroinflammation", journal: "Journal of Neuroimmunology", volume: "325", pages: "55–63", doi: "10.1016/j.jneuroim.2018.09.013" },
    ],
    ces: [
      { authors: "Kirsch DL, Nichols F", year: 2013, title: "Cranial electrotherapy stimulation for treatment of anxiety, depression, and insomnia", journal: "Psychiatric Clinics of North America", volume: "36(1)", pages: "169–176", doi: "10.1016/j.psc.2013.01.006" },
      { authors: "Barclay TH, Barclay RD", year: 2014, title: "A clinical trial of cranial electrotherapy stimulation for anxiety and comorbid depression", journal: "Journal of Affective Disorders", volume: "164", pages: "171–177", doi: "10.1016/j.jad.2014.04.029" },
      { authors: "Kennerly RC", year: 2006, title: "Changes in quantitative EEG and low resolution electromagnetic tomography following cranial electrotherapy stimulation", journal: "Subtle Energies & Energy Medicine Journal", volume: "15(3)", pages: "1–23", doi: "" },
    ],
    network: [
      { authors: "Rocca MA, Filippi M", year: 2007, title: "Functional MRI in multiple sclerosis", journal: "Journal of Neuroimaging", volume: "17(S1)", pages: "36S–41S", doi: "10.1111/j.1552-6569.2007.00137.x" },
      { authors: "Filippi M, Rocca MA, Benedict RHB, et al.", year: 2010, title: "The contribution of MRI in assessing cognitive impairment in multiple sclerosis", journal: "Neurology", volume: "75(23)", pages: "2121–2128", doi: "10.1212/WNL.0b013e318200d768" },
      { authors: "Faivre A, Robinet E, Guye M, et al.", year: 2016, title: "Depletion of brain functional connectivity enhancement leads to disability progression in multiple sclerosis: a longitudinal resting-state fMRI study", journal: "Multiple Sclerosis Journal", volume: "22(13)", pages: "1695–1708", doi: "10.1177/1352458516628657" },
      { authors: "Hawellek DJ, Hipp JF, Lewis CM, et al.", year: 2011, title: "Increased functional connectivity indicates the severity of cognitive impairment in multiple sclerosis", journal: "Proceedings of the National Academy of Sciences", volume: "108(47)", pages: "19066–19071", doi: "10.1073/pnas.1110024108" },
      { authors: "Roosendaal SD, Schoonheim MM, Hulst HE, et al.", year: 2010, title: "Resting state networks change in clinically isolated syndrome", journal: "Brain", volume: "133(6)", pages: "1612–1621", doi: "10.1093/brain/awq058" },
    ],
  },
  // ── FNON Protocol Data (SOZO_Brain_Networks_qEEG_FNON.xlsx, April 2026) ──
  fnonPrimaryNetwork: null,
  fnonNotes: 'No FNON data available for this condition.',
  fnonQeegBiomarker: null,
  fnonPaperCounts: null,
  fnonBestFirstLine: null,
  fnonBestSecondLine: null,
  fnonScore: 0,

};
