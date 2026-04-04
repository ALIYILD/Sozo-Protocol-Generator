// SOZO FNON Clinical Protocol — Tinnitus (Chronic, Subjective)
// Document A — Partners Tier

module.exports = {
  conditionFull: "Tinnitus (Chronic Subjective Tinnitus)",
  conditionShort: "Tinnitus",
  conditionSlug: "tinnitus",
  documentNumber: "SOZO-FNON-TIN-001",

  offLabelCoverText:
    "All non-invasive brain stimulation (NIBS) applications described in this protocol for chronic subjective tinnitus represent off-label use of CE-marked and FDA-cleared devices. Chronic tinnitus is not listed as a primary approved indication for the Newronika HDCkit, PlatoScience PlatoWork, NEUROLITH® TPS, Soterix Medical taVNS, or Alpha-Stim AID. The evidence base for NIBS in tinnitus — principally from rTMS and tDCS — is classified as Level B (tDCS over left temporoparietal cortex for chronic tinnitus; Lefaucheur 2017 evidence-based guidelines) with important caveats about small sample sizes, heterogeneous populations, and limited long-term follow-up. Application must be performed by clinicians with audiological expertise, accompanied by comprehensive audiological assessment, and integrated within a multidisciplinary tinnitus management programme. Patients must be counselled that NIBS is adjunctive to, not a replacement for, evidence-based tinnitus retraining therapy (TRT), cognitive behavioural therapy (CBT), and sound therapy.",

  offLabelTable: [
    ["Device", "Cleared/Approved Indication", "Tinnitus Off-Label Application", "Evidence Level"],
    ["Newronika HDCkit / PlatoWork", "Neurological rehabilitation (CE)", "Auditory cortex hyperactivation, distress, attention to tinnitus", "Level B (tDCS temporoparietal)"],
    ["NEUROLITH® TPS", "Alzheimer's disease (CE)", "Auditory cortex, thalamic-auditory circuit, prefrontal attention control", "Level C"],
    ["Soterix taVNS / Alpha-Stim AID", "Epilepsy/anxiety/pain (CE/FDA)", "Tinnitus-related distress, anxiety, VNS-paired auditory tone therapy", "Level C — VNS-paired tone therapy principle"],
  ],

  inclusionCriteria: [
    ["Chronic subjective tinnitus ≥3 months duration (bilateral, unilateral, or asymmetric)", "Audiological assessment completed: pure tone audiogram, tinnitus pitch and loudness matching, minimum masking level", "Tinnitus Handicap Inventory (THI) ≥36 (moderate to catastrophic impairment) or significant functional impairment", "Age 18–75 years"],
    ["Stable tinnitus pitch and character for ≥4 weeks (not acutely fluctuating/worsening)", "MRI brain and/or CT temporal bone available or arranged to exclude retrocochlear pathology (acoustic neuroma, vascular loop, central lesion)", "Neurological and audiological clearance confirming no surgically correctable or medically urgent cause", "Realistic expectations established through tinnitus counselling"],
    ["Completed or actively enrolled in audiological tinnitus management (TRT, CBT, sound therapy)", "No active ear infection (otitis media, otitis externa)", "Willingness to continue sound therapy and behavioural elements alongside FNON protocol", "Baseline measures: THI, TFI (Tinnitus Functional Index), Hospital Anxiety and Depression Scale (HADS), Pittsburgh Sleep Quality Index (PSQI)"],
    ["Informed consent with off-label disclosure", "No acute worsening tinnitus (sudden-onset or rapidly progressive tinnitus requires ENT/audiology assessment first)", "Adequate skin integrity at electrode and transducer sites (temporal/parietal region)", "ENT/audiology and neurology joint assessment completed or in progress"],
    ["Stable hearing aid use if applicable (document settings and fitting)", "No ototoxic medication change within 3 months", "Documented tinnitus aetiology (sensorineural hearing loss, noise-induced, age-related, idiopathic, Meniere's disease, etc.)", "PHQ-9 and GAD-7 completed (high psychological comorbidity prevalence in tinnitus)"],
    ["No acute psychiatric crisis or active suicidal ideation (strong tinnitus-suicide association — screen carefully)", "Agreement to continue all components of multidisciplinary tinnitus management", "Stable neurological status (no recent stroke, head injury, or new neurological symptoms)", "Vestibular assessment if dizziness prominent (exclude Meniere's disease requiring specific management)"],
    ["Written informed consent and treatment goals established", "Emergency contact confirmed", "No plans for changes to tinnitus management during protocol", "Audiologist involvement confirmed in MDT approach"],
  ],

  exclusionCriteria: [
    ["Pulsatile tinnitus (may indicate vascular cause: arteriovenous malformation, glomus tumour, carotid stenosis) — investigate before NIBS", "Unilateral rapidly progressive tinnitus with asymmetric sensorineural hearing loss (exclude acoustic neuroma by MRI)", "Active Meniere's disease in acute phase (endolymphatic hydrops fluctuation) — defer until stable", "Otosclerosis or cholesteatoma — requires surgical management priority"],
    ["Intracranial metal implants (DBS, cochlear implants, ferromagnetic clips) — absolute contraindication for TPS; cochlear implant is absolute contraindication for ipsilateral temporal tDCS", "Cardiac pacemaker or implantable defibrillator", "Active central nervous system pathology producing tinnitus (acoustic neuroma, intracranial tumour, MS plaque affecting auditory pathway)", "Pregnancy or breastfeeding"],
    ["Uncontrolled psychiatric disorder (active psychosis, mania)", "Active suicidal ideation (tinnitus-related suicidality is a genuine risk — immediate psychiatric referral required)", "Current participation in conflicting tinnitus NIBS trial", "Severe hearing loss (total deafness) preventing tinnitus characterisation and response assessment"],
    ["Known allergy or hypersensitivity to conductive gel or electrode materials", "Active ear infections (otitis media or externa)", "Severe skin condition at temporal/parietal electrode sites", "Uncontrolled seizure disorder"],
    ["Botulinum toxin injection to head or neck within 3 months", "Deep cervical vagus nerve stimulator in place", "Head injury within 3 months", "Open wounds or infections at electrode/transducer sites"],
    ["Inability to tolerate electrode application at temporal sites (extreme skin sensitivity)", "Age <18 (paediatric tinnitus has distinct considerations)", "Very recent onset tinnitus <3 months (may spontaneously resolve; conservative management first)", "Purely psychological/functional tinnitus without audiological correlate (psychotherapy-only management indicated)"],
    ["Objective tinnitus (pulsatile, palatal myoclonus, stapedial myoclonus) — mechanical/vascular aetiology requires specific treatment", "Tinnitus solely attributable to medication (aspirin, quinine, loop diuretics, aminoglycosides) that can be stopped — address pharmacological cause first", "Active malignancy with cranial involvement", "Clinician assessment: risk outweighs benefit"],
    ["Refusal of audiological assessment (NIBS without full audiological characterisation is inappropriate)", "Unable to provide informed consent", "Severe vertigo making sitting protocol unsafe", "Active autoimmune inner ear disease in acute phase"],
  ],

  conditionsRequiringDiscussion: [
    ["Condition", "Clinical Consideration", "Recommended Action", "Protocol Adjustment"],
    ["Sensorineural hearing loss (SNHL)", "Most common tinnitus aetiology; peripheral deafferentation drives central auditory hyperactivity; degree of HL determines network adaptation", "Audiogram; hearing aid fitting if indicated; HL severity affects temporal cortex target selection", "Standard temporoparietal protocol; consider hearing aid concurrent with NIBS; bilateral temporal targeting if bilateral SNHL"],
    ["Noise-induced hearing loss / noise-induced tinnitus", "Occupational or recreational noise exposure; cochlear hair cell damage; often bilateral; ongoing noise exposure worsens prognosis", "Noise exposure history; HSE noise assessment; hearing protection advice; remove from noise exposure if possible", "Full tinnitus FNON protocol; emphasise taVNS anti-inflammatory for cochlear inflammatory component"],
    ["Meniere's disease / endolymphatic hydrops", "Episodic vertigo, fluctuating SNHL, tinnitus, aural fullness; distinct from pure tinnitus; acute phase distinct from stable phase", "ENT vestibular assessment; betahistine; NIBS only in stable inter-attack phase", "Defer NIBS during vertigo or acute attacks; conservative protocol; emphasise taVNS autonomic for Meniere's episodic component"],
    ["Tinnitus with significant anxiety/depression (HADS ≥11)", "Psychological distress is the most important predictor of tinnitus handicap; bidirectional neural reinforcement between tinnitus and limbic distress", "Psychiatric/psychological assessment; CBT for tinnitus mandatory concurrent; HADS monitoring", "Add F3/F4 DLPFC tDCS (anxiety/depression protocol element); taVNS + CES anti-anxiety; psychological therapy concurrent"],
    ["Hyperacusis (reduced sound tolerance)", "30–40% of tinnitus patients; auditory cortex hyperexcitability; cathodal auditory cortex may worsen hyperacusis if applied inappropriately", "Hyperacusis questionnaire (HQ); sound desensitisation programme; careful polarity selection", "Avoid excessive cathodal auditory cortex intensity; taVNS SN modulation primary for hyperacusis; CES tonic; gradual sound enrichment"],
    ["Tinnitus following head injury / whiplash", "Post-traumatic tinnitus; somatic tinnitus component (modulated by jaw/neck movement); central sensitisation", "C-spine and TMJ assessment; somatic modulation test; physiotherapy if somatic component prominent", "Add DLPFC tDCS for post-traumatic distress; somatosensory cortex tDCS for somatic tinnitus component; taVNS anti-inflammatory"],
    ["Somatic / cervicogenic tinnitus", "Tinnitus modulated by jaw pressure, neck position, tooth clenching; somatosensory-auditory convergence in dorsal cochlear nucleus", "TMJ/dental assessment; physiotherapy; document modulation characteristics", "Add somatosensory cortex tDCS component; TPS temporal-parietal for dorsal cochlear nucleus-cortical pathway"],
    ["Tinnitus in musicians / acoustic trauma", "Noise-induced; often temporary worsening with performance; psychological impact on professional identity; risk of overuse of hearing", "Audiological monitoring; hearing protection education; noise retraining; psychological support for identity impact", "Standard protocol; address anxiety and distress components; concurrent CBT with musical identity focus"],
    ["Tinnitus with sleep disturbance (PSQI >5)", "Sleep disturbance in 60–70% of tinnitus patients; bidirectional: tinnitus disrupts sleep; sleep deprivation amplifies tinnitus distress", "PSQI baseline; CBT-I referral if insomnia prominent; sleep hygiene advice", "Add CES evening protocol (primary sleep intervention); taVNS evening for circadian calming; cathodal Cz optional"],
  ],

  overviewParagraph:
    "Tinnitus — the perception of sound in the absence of an external acoustic stimulus — affects approximately 15% of the global adult population, with 2–3% experiencing severe, distressing, or disabling chronic tinnitus. The most prevalent form is chronic subjective tinnitus, most commonly associated with sensorineural hearing loss (SNHL), though it occurs with normal audiograms in approximately 30% of patients. The defining neural substrate of chronic tinnitus is central auditory network hyperactivity: peripheral deafferentation (cochlear hair cell loss in SNHL) produces aberrant spontaneous firing in the central auditory pathway, particularly within the dorsal cochlear nucleus, inferior colliculus, medial geniculate body (thalamus), and primary auditory cortex (A1) — generating a phantom auditory percept that becomes self-sustaining through thalamo-cortical and limbic-auditory memory loop reinforcement. The SOZO FNON protocol for tinnitus targets the auditory network hyperactivity through cathodal tDCS of the left temporal cortex (Level B evidence), combined with taVNS for tinnitus-associated anxiety/distress (via SN and limbic modulation), prefrontal tDCS for top-down attentional control over tinnitus salience, and TPS for precise auditory cortex and prefrontal targeting. The protocol is integrated within a multidisciplinary tinnitus management framework including TRT, CBT, and sound therapy.",

  fnonNetworkParagraph:
    "The FNON framework for tinnitus is grounded in the 'Thalamocortical Dysrhythmia and Auditory Network Hyperactivity' model: peripheral deafferentation drives compensatory increases in spontaneous firing rate throughout the central auditory pathway, culminating in auditory cortex (A1, secondary auditory cortex A2) hyperexcitability that generates the phantom sound percept. This auditory cortex hyperactivity is reinforced by: (1) thalamic gating failure — the medial geniculate body (MGB) normally gates auditory information from the inferior colliculus to A1; in tinnitus, thalamo-cortical burst firing patterns (instead of tonic patterns) create rhythmic reinforcement of the phantom percept; (2) limbic-auditory reinforcement — the amygdala and hippocampus, via the parahippocampal cortex, reinforce the tinnitus memory trace and emotional significance, preventing habituation; (3) prefrontal attention control failure — the DLPFC normally suppresses irrelevant auditory stimuli via top-down attentional gating; in distressing tinnitus, depleted prefrontal top-down control allows the tinnitus signal to dominate attentional resources. The FNON strategy simultaneously targets all three nodes: cathodal tDCS of the left temporal cortex reduces A1 hyperexcitability; anodal DLPFC tDCS restores top-down attentional suppression; taVNS modulates the SN and limbic-emotional reinforcement of tinnitus distress. TPS offers precision targeting of the temporoparietal auditory cortex and DLPFC beyond tDCS spatial resolution.",

  networkDisorderParagraphs: [
    {
      network: "Default Mode Network (DMN)",
      paragraph:
        "In chronic tinnitus, the Default Mode Network shows pathological engagement that reinforces the tinnitus percept: increased connectivity between the DMN and the auditory cortex means that self-referential processing — which dominates DMN function — incorporates the tinnitus signal into the default experiential baseline. This is believed to underlie the 'habituation failure' seen in distressing tinnitus: the DMN normally suppresses internally generated signals during default-mode processing, but in tinnitus the DMN-auditory coupling integrates the phantom sound into the self-model, making it feel 'always present' and impossible to ignore. Posterior cingulate cortex-auditory cortex functional connectivity is increased in tinnitus patients compared to matched controls. FNON implication: CES and taVNS modulation of DMN dynamics, combined with tinnitus retraining therapy, aims to reduce DMN-auditory coupling and promote habituation to the tinnitus signal as a 'non-threatening neutral stimulus' (core TRT principle)."
    },
    {
      network: "Central Executive Network (CEN)",
      paragraph:
        "The Central Executive Network (CEN) — anchored in the DLPFC — normally exerts top-down attentional suppression over auditory cortex, allowing selective filtering of irrelevant auditory stimuli. In chronic distressing tinnitus, DLPFC function is depleted: reduced grey matter volume and reduced resting-state connectivity between DLPFC and auditory cortex have been documented in tinnitus patients with high handicap. This DLPFC hypoactivation produces the 'cognitive capture' phenomenon: tinnitus competes successfully for attentional resources because DLPFC cannot suppress it. Anodal DLPFC tDCS (F3) is the primary CEN target in the FNON tinnitus protocol: upregulating DLPFC restores top-down auditory cortex suppression, reducing the attentional salience of the tinnitus percept. This is the proposed mechanism for why DLPFC tDCS reduces tinnitus distress even when tinnitus loudness matching is unchanged."
    },
    {
      network: "Salience Network (SN)",
      paragraph:
        "The Salience Network in chronic tinnitus shows heightened activation — particularly the anterior insula — which flags the tinnitus signal as 'salient and threatening,' preventing habituation. The SN-amygdala-auditory circuit creates the distress loop: SN detects tinnitus as a potentially threatening signal, amygdala assigns emotional significance and fear conditioning to the percept, and the combined SN-amygdala activation drives the cycle of attention → distress → attention that characterises chronic distressing tinnitus. The degree of SN hyperactivation correlates with tinnitus handicap (THI) more strongly than tinnitus loudness or pitch matching — confirming that the distress dimension, not the signal itself, is the primary determinant of disability. taVNS modulates the SN via NTS projections to the insula and ACC, reducing the SN hyperactivation that maintains the tinnitus-distress cycle."
    },
    {
      network: "Sensorimotor Network (SMN)",
      paragraph:
        "The Sensorimotor Network is relevant to tinnitus primarily through the somatosensory-auditory convergence mechanism underlying somatic tinnitus: approximately 20–40% of tinnitus patients can modulate their tinnitus by jaw movements, neck pressure, or gaze deviation — a phenomenon explained by somatosensory afferents converging with auditory afferents in the dorsal cochlear nucleus (DCN) and inferior colliculus. This DCN somatosensory-auditory convergence is mediated by trigeminal and C2 somatosensory inputs. For the somatic tinnitus subtype, tDCS targeting of the somatosensory cortex (cathodal S1) may complement the auditory cortex protocol. TPS can target the temporoparietal junction where auditory and somatosensory cortices interface, addressing this auditory-somatosensory convergence directly."
    },
    {
      network: "Limbic Network",
      paragraph:
        "The Limbic Network — particularly the amygdala, hippocampus, and anterior cingulate cortex — is critically involved in the transition from 'non-distressing tinnitus' (perceived but not affecting quality of life) to 'distressing tinnitus' (associated with anxiety, depression, sleep disturbance, and suicidality). The amygdala, through fear conditioning mechanisms, assigns emotional threat value to the tinnitus sound, creating a conditioned emotional response. The hippocampus encodes the 'tinnitus memory trace' that maintains the percept even when auditory input is manipulated. Neuroplastic reinforcement of the limbic-auditory circuit — analogous to fear conditioning — explains why simply removing the tinnitus signal (e.g., by masking) provides only temporary relief. taVNS modulates the amygdala (NTS→LC→amygdala inhibition) and hippocampal memory consolidation pathways, while CES provides tonic anxiolytic autonomic modulation that reduces the emotional arousal maintaining the tinnitus distress loop."
    },
    {
      network: "Attention Network",
      paragraph:
        "The Attention Network is central to tinnitus disability: tinnitus is defined by its relationship to attention — it is not the signal strength but the attentional capture by the signal that drives distress. The right hemisphere attention network (right DLPFC, right inferior frontal gyrus, intraparietal sulcus) normally mediates attentional disengagement from salient stimuli. In tinnitus, this disengagement mechanism fails — the tinnitus signal generates sustained attentional capture that prevents disengagement and perpetuates conscious awareness. Functional connectivity between the anterior cingulate cortex (ACC) and auditory cortex is increased in high-distress tinnitus, representing the ACC's failure to redirect attention away from the tinnitus percept. Anodal right DLPFC tDCS (F4) and cathodal ACC may support the attentional disengagement deficit in tinnitus, complementing the bottom-up auditory cortex inhibition approach of cathodal temporal tDCS."
    },
  ],

  pathophysiologyText:
    "Tinnitus pathophysiology is multi-level: peripheral deafferentation (cochlear hair cell loss, cochlear nerve fibre loss) drives central compensatory changes that ultimately generate and sustain the phantom percept. At the cochlear level, outer hair cell loss in SNHL reduces afferent input from the damaged frequency region, triggering homeostatic upregulation of gain in the central auditory pathway — increasing spontaneous firing rates in dorsal cochlear nucleus (DCN) neurons projecting to inferior colliculus, medial geniculate body (thalamus), and auditory cortex. At the DCN level, fusiform cell spontaneous hyperactivity is the earliest identifiable neural correlate of noise-induced tinnitus. Thalamocortical dysrhythmia — proposed by Llinas et al. — posits that reduced thalamocortical input in the deafferented frequency range produces a shift from tonic (normal) to burst firing in MGB neurons, generating rhythmic alpha-band oscillations in auditory cortex that underlie the tinnitus percept. At the auditory cortex level, tonotopic map reorganisation expands the cortical representation of frequencies adjacent to the cochlear dead region into the deafferented zone, producing 'winner-take-all' hyperactivity in the expanded regions. Tinnitus distress is then maintained by limbic-auditory circuit reinforcement: the anterior cingulate cortex, amygdala, and hippocampus maintain the percept through emotional significance assignment (amygdala fear conditioning) and memory consolidation (hippocampal tinnitus trace). The FNON tinnitus protocol specifically targets the auditory cortex and temporoparietal auditory network (cathodal tDCS — inhibiting hyperexcitable A1), the DLPFC (anodal tDCS — restoring top-down attention suppression), and the limbic-SN distress loop (taVNS + CES).",

  cardinalSymptoms: [
    ["Domain", "Primary Symptoms", "Network Basis", "FNON Target"],
    ["Tinnitus Percept", "Continuous or intermittent phantom sound (ringing, buzzing, hissing, roaring); bilateral or unilateral; pitch typically 1–8 kHz; loudness typically only 5–10 dB above threshold", "Auditory cortex (A1/A2) hyperexcitability; thalamocortical dysrhythmia; spontaneous DCN hyperactivity; tonotopic map reorganisation", "Cathodal tDCS left temporal (T3/TP7); TPS auditory cortex precision; taVNS thalamo-cortical normalisation"],
    ["Tinnitus Distress / Handicap", "Emotional distress; suffering; catastrophising; perceived inability to cope; quality of life impairment (THI ≥36)", "SN hyperactivation; amygdala fear conditioning to tinnitus; ACC attentional capture failure; limbic-auditory coupling", "taVNS (SN modulation primary); CES anxiolytic; anodal F3 (DLPFC top-down control); TPS prefrontal"],
    ["Anxiety", "Prevalence 60–70% in chronic tinnitus; generalised anxiety; health anxiety; panic attacks in severe cases; bidirectional reinforcement with tinnitus", "SN-amygdala hyperactivation; tinnitus-anxiety conditioned loop; HPA axis and LC-NE dysregulation", "taVNS bilateral + CES (primary anxiolytic); anodal F4 right DLPFC anxiolytic tDCS"],
    ["Sleep Disturbance", "60–70% prevalence; sleep-onset difficulty (tinnitus louder without masking sounds); non-restorative sleep; tinnitus perceived louder on waking", "Tinnitus signal prominence in quiet (no competing sounds); SN/limbic hyperarousal preventing sleep; circadian disruption", "CES pre-sleep (primary — sound enrichment + CES); taVNS evening; cathodal Cz evening calming"],
    ["Depression", "Prevalence 30–60% in distressing tinnitus; neuroinflammatory and psychosocial; reduced reward processing; hopelessness", "Limbic-prefrontal disconnection; tinnitus helplessness/hopelessness model; DLPFC hypoactivation", "Anodal F3 tDCS; taVNS anti-inflammatory; CES; CBT tinnitus-depression concurrent"],
    ["Cognitive Difficulties", "Concentration difficulty; irritability; reduced working memory in noise; executive function impairment; attention capture by tinnitus", "DLPFC hypoactivation (top-down attention); tinnitus competing for cognitive resources; SN-attention interference", "Anodal F3/F4 DLPFC tDCS; TPS prefrontal; cognitive rehabilitation concurrent"],
    ["Hyperacusis", "Reduced sound tolerance (comorbid in 30–40%); loudness discomfort at normal sound levels; auditory cortex hyperexcitability overlapping with tinnitus", "A1/A2 hyperexcitability — overlap with tinnitus mechanism; reduced olivocochlear efferent function; SN hyperactivation", "Cathodal temporal tDCS (reduce A1 hyperexcitability); taVNS SN; gradual sound desensitisation"],
    ["Somatic Modulation", "Tinnitus changed by jaw, neck, eye movement (positive somatic modulation test); prevalent in noise-induced and cervicogenic tinnitus", "DCN somatosensory-auditory convergence; trigeminal and C2 input to DCN; temporomandibular joint contribution", "Somatosensory cortex tDCS; TPS TPJ auditory-somatosensory interface; physiotherapy concurrent"],
    ["Concentration / Attentional Capture", "Inability to ignore tinnitus; attention drawn to sound involuntarily; difficulty in multi-tasking; reduced occupational function", "DLPFC top-down suppression failure; ACC-auditory cortex hyperconnectivity; attention network deficit", "Anodal DLPFC F3/F4; TPS prefrontal; mindfulness-based tinnitus attention training"],
  ],

  standardGuidelinesText: [
    "Tinnitus management follows NICE guideline NG155 (2020), the British Tinnitus Association (BTA) guidelines, and the American Academy of Otolaryngology-Head and Neck Surgery (AAO-HNS) clinical practice guideline (2014, updated 2019). There are no pharmacological agents with Level A evidence for chronic tinnitus; NICE NG155 recommends against ginkgo biloba, acamprosate, benzodiazepines, anticonvulsants, and low-power laser therapy.",
    "Audiological management: tinnitus retraining therapy (TRT) and tinnitus counselling have Level B evidence (NICE NG155). Sound therapy — using broadband noise generators, hearing aids (if SNHL is present), or partial masking devices — is recommended. Hearing aids for patients with SNHL + tinnitus have Level A evidence for tinnitus benefit. Complete masking is discouraged; partial masking is preferred.",
    "Cognitive Behavioural Therapy (CBT) for tinnitus has Level A evidence for reducing tinnitus handicap (THI), distress, and depression — it is the most strongly evidenced psychological intervention (CBT delivered by trained therapists or via internet-based programmes). Acceptance and Commitment Therapy (ACT) has emerging Level B evidence. Mindfulness-based cognitive therapy (MBCT) for tinnitus has Level B evidence.",
    "Psychological management: anxiety and depression screening is mandatory (HADS, PHQ-9, GAD-7). Tinnitus-associated suicidality must be assessed given the elevated risk (tinnitus patients have 2–3× elevated suicide risk). Referral to psychological services is essential for HADS ≥11 in either anxiety or depression subscale.",
    "NIBS for tinnitus: Lefaucheur 2017 evidence-based guidelines (Clinical Neurophysiology) classify cathodal tDCS over the left temporoparietal cortex as Level B evidence for tinnitus (Grade B recommendation). rTMS — particularly 1 Hz (inhibitory) over the left auditory cortex — has Level B evidence from multiple sham-controlled RCTs but is not the FNON modality. taVNS for tinnitus has Level C evidence with emerging pilot data. TPS for tinnitus is experimental (Level C). FNON integrates these modalities in a network-level multimodal protocol.",
    "Hearing aid fitting: NICE NG155 recommends hearing aid referral for all patients with tinnitus and hearing loss ≥20 dBHL. Modern hearing aids with notched noise therapy (based on lateral inhibition principle) have emerging Level B evidence. Cochlear implants for severe-profound SNHL with tinnitus have Level A evidence for tinnitus reduction.",
    "Lifestyle modifications: NICE NG155 recommends sleep hygiene, relaxation techniques, avoidance of known exacerbating factors (caffeine in susceptible patients, excessive silence, ototoxic medications), and noise protection. Regular aerobic exercise has emerging Level B evidence for tinnitus distress reduction.",
  ],

  fnonFrameworkParagraph:
    "The SOZO FNON framework for tinnitus is the 'Auditory Network Hyperactivity Dampening with Limbic-Prefrontal Restoration' (ANHDLPR) model: tinnitus is maintained by three mutually reinforcing mechanisms that must be addressed simultaneously — auditory cortex hyperexcitability (bottom-up), prefrontal attentional control failure (top-down), and limbic-SN emotional reinforcement (distress amplification). Standard NIBS approaches targeting only the auditory cortex achieve modest results because they address only one dimension. The FNON multimodal approach: (1) cathodal temporal tDCS (or TPS auditory cortex) reduces bottom-up A1 hyperexcitability; (2) anodal DLPFC tDCS (F3/F4) restores top-down prefrontal attentional suppression of the tinnitus signal; (3) taVNS reduces SN and limbic hyperactivation maintaining the distress dimension; (4) CES provides tonic autonomic calming that supports sleep and reduces the hyperarousal state in which tinnitus is most distressing. The S-O-Z-O sequence for tinnitus: Stabilise (taVNS 15 min + CES pre-session — reduce limbic-SN distress state before auditory cortex intervention); Optimise (bilateral tDCS: cathodal temporal + anodal frontal — dual target within one session); Zone (TPS auditory cortex precision for temporoparietal targeting); Outcome (CES during sound therapy or TRT session — consolidation of limbic quieting concurrent with tinnitus habituation training). All FNON tinnitus protocols are adjunctive to ongoing TRT and CBT — the neuroplasticity amplification role.",

  keyBrainRegions: [
    ["Brain Region", "Function", "Tinnitus Pathology", "FNON Intervention"],
    ["Primary Auditory Cortex (A1)", "Frequency-specific sound representation; tonotopic map; conscious sound perception; auditory feature extraction", "Hyperexcitability; spontaneous gamma-band oscillations; expanded tonotopic map into deafferented frequency zone; maladaptive plasticity", "Cathodal tDCS T3/TP7 (left hemisphere primary); TPS auditory cortex neuro-navigation; inhibits A1 hyperexcitability (Level B evidence)"],
    ["Secondary Auditory Cortex / Auditory Association Cortex (A2/STG)", "Complex sound processing; auditory object recognition; auditory memory; emotional colouring of sound; auditory-limbic interface", "Hyperactivation; A2-amygdala hyperconnectivity; auditory memory consolidation of tinnitus trace; STG involvement in tinnitus percept", "Cathodal temporal tDCS extends to A2/STG; TPS superior temporal gyrus; taVNS limbic-auditory modulation"],
    ["Dorsolateral Prefrontal Cortex (DLPFC)", "Top-down attentional suppression of auditory cortex; working memory; cognitive control; tinnitus salience filtering", "Reduced grey matter; DLPFC-auditory cortex connectivity reduced; top-down suppression failure allowing attentional capture", "Anodal tDCS F3 (left DLPFC) — Level B restores top-down suppression; TPS DLPFC neuro-navigation; cognitive control training concurrent"],
    ["Medial Geniculate Body (MGB) / Thalamus", "Auditory relay station; thalamo-cortical gating of auditory information; burst vs. tonic firing mode determines signal quality", "Thalamocortical dysrhythmia — burst firing mode generates alpha oscillations in A1 that produce tinnitus; MGB hyperactivation", "taVNS thalamocortical normalisation via NTS-thalamic projections; indirect thalamic modulation via cortical tDCS"],
    ["Amygdala", "Emotional significance assignment; fear conditioning; threat detection; auditory-emotional association", "Fear conditioning to tinnitus sound; amygdala-A1 hyperconnectivity; maintains distress dimension of tinnitus; conditioned emotional response to tinnitus", "taVNS (NTS→LC→amygdala inhibition — primary limbic target); CES anxiolytic; TRT concurrent for extinction of amygdala conditioned response"],
    ["Anterior Cingulate Cortex (ACC)", "Attentional monitoring; conflict detection; emotional-attentional interface; auditory attention gate", "ACC-auditory cortex hyperconnectivity in high-distress tinnitus; ACC fails to redirect attention from tinnitus; contributes to attentional capture", "taVNS (NTS→ACC modulation); anodal DLPFC tDCS reduces ACC hyperactivation via DLPFC→ACC top-down control; TPS prefrontal-cingulate"],
    ["Anterior Insula", "Interoception; SN hub; body-self awareness; emotional experience; tinnitus distress monitoring", "Insula hyperactivation in tinnitus distress; SN-driven tinnitus emotional significance; insula mediates the 'suffering' dimension", "taVNS (primary NTS→insula modulation — reduces SN distress signal); TPS insula-adjacent frontal operculum"],
    ["Hippocampus", "Auditory memory; tinnitus memory trace consolidation; contextual memory; emotional memory", "Hippocampal encoding of tinnitus as persistent autobiographical auditory memory; memory trace that maintains percept", "taVNS (hippocampal modulation via NTS-LC pathway); TPS hippocampal (reduce memory trace consolidation); memory reconsolidation-based CBT concurrent"],
    ["Dorsal Cochlear Nucleus (DCN)", "First central auditory relay; somatosensory-auditory convergence; spontaneous hyperactivity in tinnitus; 'tinnitus generator' site", "Spontaneous fusiform cell hyperactivity; DCN = primary spontaneous tinnitus generation site; somatosensory input from trigeminal and C2 nerve", "Indirect modulation: taVNS brainstem projections near DCN level; TPS and tDCS act on cortical targets; somatic tinnitus subtype: somatosensory cortex tDCS"],
  ],

  additionalBrainStructures: [
    ["Structure", "Tinnitus-Specific Role", "Clinical Relevance", "FNON Consideration"],
    ["Superior Temporal Gyrus (STG)", "Higher-order auditory processing; speech perception; auditory scene analysis; auditory-limbic bridge", "Hyperactivation in tinnitus; STG-amygdala hyperconnectivity; STG grey matter changes in tinnitus", "TPS STG neuro-navigation (precision auditory cortex targeting); cathodal temporal tDCS covers STG"],
    ["Inferior Colliculus (IC)", "Brainstem auditory relay; binaural integration; frequency selectivity; DCN→IC pathway", "IC hyperactivity documented in animal tinnitus models; central gain amplification at IC level", "Indirect taVNS brainstem modulation; IC is too deep for direct surface NIBS"],
    ["Parahippocampal Cortex", "Auditory memory context; auditory familiarity; linking auditory percepts to environmental context", "Parahippocampal hyperactivation in tinnitus maintains memory trace; involved in perpetuating tinnitus as a 'familiar' sound", "taVNS hippocampal-parahippocampal modulation; TPS hippocampal indirectly"],
    ["Nucleus Accumbens / Reward System", "Hedonic valuation; salience detection; reward-aversion balance; auditory pleasure/aversion", "Disrupted auditory reward processing in tinnitus; inability to experience auditory pleasure (music); tinnitus takes aversive reward value", "taVNS (NTS→VTA→dopaminergic reward system modulation); music therapy paired with NIBS (emerging)"],
    ["Auditory Thalamus (Reticular Nucleus)", "Thalamo-cortical gate control; inhibitory gating of auditory relay; sleep-related auditory gating", "Reticular nucleus inhibitory gating failure in tinnitus allows unrestricted MGB→A1 spontaneous activity at night", "Indirect taVNS thalamocortical normalisation; CES for sleep-related thalamic gating improvement"],
    ["Locus Coeruleus (LC)", "Norepinephrine; arousal; attention; stress response; auditory arousal gating", "LC hyperactivation in tinnitus distress mediates hyperarousal state that amplifies tinnitus; NE dysregulation in tinnitus anxiety", "taVNS (NTS→LC NE normalisation — primary); LC over-activation reduction supports habituation"],
    ["Orbitofrontal Cortex (OFC)", "Emotional valuation of sounds; sound aversion vs. reward; tinnitus aversive value coding", "OFC assigns aversive emotional value to tinnitus sound; OFC-amygdala loop perpetuates tinnitus aversion", "Anodal DLPFC tDCS (modulates OFC via frontal network); TPS OFC (experimental); CBT for tinnitus aversion concurrent"],
  ],

  keyFunctionalNetworks: [
    ["Network", "Key Nodes", "Tinnitus Dysfunction Pattern", "NIBS Modality", "Expected Outcome"],
    ["Auditory Network", "A1 (T3/TP7), A2/STG, MGB (thalamus), IC, DCN", "Spontaneous hyperactivity; thalamocortical dysrhythmia; burst firing; tonotopic map reorganisation; maladaptive plasticity", "Cathodal temporal tDCS (T3/TP7 — Level B); TPS auditory cortex precision targeting", "THI reduction ≥20 points; tinnitus loudness matching reduction; TFI global score improvement"],
    ["Central Executive Network (CEN)", "DLPFC bilateral (F3/F4), ACC, posterior parietal", "DLPFC hypoactivation; top-down auditory suppression failure; attentional capture by tinnitus; CEN-auditory disconnection", "Anodal DLPFC tDCS (F3 — Level B); TPS DLPFC neuro-navigation; concurrent cognitive training", "Reduced tinnitus attentional capture; improved concentration; DLPFC-auditory connectivity restoration"],
    ["Default Mode Network (DMN)", "mPFC, PCC, IPL, hippocampus", "DMN-auditory coupling maintaining tinnitus in default experience; habituation failure; PCC-auditory hyperconnectivity", "CES (DMN normalisation); anodal mPFC; TRT concurrent (extinction of DMN-auditory pairing)", "Tinnitus habituation (TRT outcome measure); reduced self-referential tinnitus attention"],
    ["Salience Network (SN)", "Anterior insula, ACC, amygdala, thalamus", "SN hyperactivation flagging tinnitus as salient threat; SN-driven distress loop; insula amplifying suffering dimension", "taVNS (primary SN modulator — NTS→insula/ACC); CES tonic ANS calm; cathodal ACC optional", "THI subscale distress reduction; HADS anxiety reduction; tinnitus intrusiveness VAS improvement"],
    ["Limbic Network", "Amygdala, hippocampus, OFC, ACC, parahippocampal cortex", "Amygdala fear conditioning to tinnitus; hippocampal tinnitus memory trace; aversive emotional reinforcement perpetuating habituation failure", "taVNS amygdala-hippocampal modulation; CES anxiolytic; TRT extinction concurrent", "HADS depression reduction; tinnitus emotional distress (TFI emotional subscale); quality of life improvement"],
    ["Attention Network", "Right DLPFC, right IFG, IPS, ACC, FEF", "Attentional disengagement failure; right hemisphere attention network connectivity with auditory cortex increased", "Anodal F4 (right DLPFC); cathodal ACC optional; TPS right DLPFC/parietal; mindfulness-based attention training", "Tinnitus attentional capture reduction; TMT-B; attention questionnaire (PANAS)"],
    ["Somatosensory-Auditory Network (somatic tinnitus)", "S1, S2, DCN-somatosensory afferents, TPJ", "Somatosensory-auditory convergence at DCN; somatic modulation of tinnitus by jaw/neck/eye; trigeminal-DCN input", "Cathodal S1 (somatosensory cortex normalisation); TPS TPJ (auditory-somatosensory interface); physiotherapy concurrent", "Somatic modulation reduction; jaw/neck contribution to tinnitus reduced; concurrent TMJ physiotherapy outcome"],
  ],

  networkAbnormalities:
    "Tinnitus network abnormalities centre on three pathological patterns: (1) auditory cortex hyperexcitability — spontaneous gamma-band (40 Hz) oscillatory activity in A1 is the most consistent neurophysiological signature of tinnitus across EEG and MEG studies; gamma power in A1 correlates with tinnitus loudness perception; (2) increased alpha oscillations — reduced alpha power in the deafferented frequency band region of A1 represents an 'alpha deficit' from thalamic deafferentation, which paradoxically reduces thalamocortical inhibition and allows unconstrained gamma hyperactivity; and (3) increased connectivity between auditory cortex and limbic networks — DMN-auditory, amygdala-A1, and ACC-auditory connectivity are all elevated in distressing tinnitus. EEG oscillatory biomarkers provide objective tinnitus neurophysiology: pre-treatment gamma power, alpha-delta ratio, and auditory cortex resting connectivity predict treatment response to tDCS. The FNON protocol aims to: reduce A1 gamma hyperactivity (cathodal temporal tDCS); restore normal thalamo-cortical alpha rhythm (taVNS thalamocortical normalisation via NTS); and reduce auditory-limbic coupling (taVNS + CES + TRT concurrent).",

  conceptualFramework:
    "The SOZO FNON conceptual framework for tinnitus is the 'Triple Network Recalibration' model: tinnitus is sustained by the simultaneous pathological state of three networks — (1) Auditory Network hyperexcitability (bottom-up signal generation), (2) CEN/Prefrontal top-down suppression failure (attention control failure), and (3) SN-Limbic distress amplification (emotional reinforcement preventing habituation). Standard single-target NIBS approaches (cathodal temporal tDCS alone) address only the bottom-up dimension, achieving modest 30–50% responder rates. The FNON approach simultaneously targets all three: cathodal temporal tDCS + anodal DLPFC tDCS (dual bipolar montage addresses bottom-up and top-down in the same session); taVNS pre-session reduces SN-Limbic distress; CES maintains tonic autonomic calming. The S-O-Z-O sequence: Stabilise (taVNS + CES — reduce the distress amplification network before any auditory-targeting stimulation); Optimise (dual tDCS — cathodal temporal + anodal frontal simultaneously; the key innovation of FNON vs. single-target protocols); Zone (TPS — precision auditory cortex and DLPFC when deeper, more focal targeting is warranted); Outcome (CES + sound therapy during TRT session — consolidating limbic calming concurrent with habituation training). The VNS-paired acoustic stimulation principle (originally from MicroTransponder for tinnitus treatment) is incorporated: taVNS concurrent with carefully selected sounds (residual inhibition or notched-noise therapy) may enhance auditory cortex plasticity through VNS-induced acetylcholine-driven neuromodulatory broadening of auditory cortex receptive fields.",

  clinicalPhenotypes: [
    ["Phenotype", "Core Feature", "Network Priority"],
    ["Noise-Induced / SNHL Tinnitus", "SNHL with tinnitus; tonotopic reorganisation; audiometric notch; most common phenotype", "Auditory network (cathodal temporal primary); TPS A1; taVNS thalamocortical"],
    ["High-Distress / Catastrophising Tinnitus", "High THI (≥56); catastrophising; negative appraisal; disability; 'can't cope' narrative", "SN + Limbic (taVNS + CES primary); DLPFC (CEN top-down control); CBT concurrent"],
    ["Tinnitus with Anxiety/Depression", "HADS ≥11 either subscale; bidirectional tinnitus-distress reinforcement; reduced quality of life", "Limbic + CEN; anodal F3 (depression) or F4 (anxiety) tDCS; taVNS; CES"],
    ["Sleep-Disturbed Tinnitus", "PSQI >5; sleep-onset disruption by tinnitus in quiet; daytime fatigue; tinnitus perceived louder on waking", "CES primary (sleep + anxiolytic); taVNS evening; cathodal Cz evening calming protocol"],
    ["Hyperacusis-Comorbid Tinnitus", "Reduced sound tolerance with tinnitus; loudness discomfort at normal levels; auditory cortex hyperexcitability bilateral", "Auditory network (cathodal temporal, bilateral); taVNS SN for hyperacusis; sound desensitisation concurrent"],
    ["Somatic / Cervicogenic Tinnitus", "Modulated by jaw, neck, eye movements; somatic modulation positive; often noise-induced with cervicogenic component", "Somatosensory-auditory network; cathodal S1 + cathodal temporal; TPJ TPS; physiotherapy concurrent"],
    ["Post-Acute Noise Trauma Tinnitus", "Onset after single acoustic trauma (gunshot, explosion, concert); often high-pitched; acute-to-chronic transition", "Auditory network (immediate); taVNS anti-inflammatory (cochlear inflammation); early intervention to prevent chronification"],
    ["Treatment-Resistant Tinnitus", "Failed TRT, CBT, hearing aids, sound therapy; high handicap persisting >2 years; multiple treatment attempts", "Multi-network intensive FNON; TPS precision + tDCS; maximum taVNS + CES dosing; TRT concurrent"],
    ["Tinnitus with Cognitive Complaints", "Attention difficulties; concentration impairment; working memory affected by tinnitus distraction; occupational impairment", "CEN (DLPFC anodal primary); Attention network; auditory network; cognitive rehabilitation concurrent"],
  ],

  symptomNetworkMapping: [
    ["Symptom", "Primary Network", "Key Nodes", "tDCS", "taVNS/CES"],
    ["Tinnitus loudness / intensity", "Auditory network", "A1/A2 left temporal cortex (T3/TP7)", "Cathodal T3/TP7 (left temporal, 1.5–2.0 mA) — Level B", "taVNS thalamocortical; TPS A1 precision"],
    ["Tinnitus distress (THI)", "SN + Limbic", "Anterior insula, amygdala, ACC", "Anodal F3 (DLPFC top-down) + cathodal T3 dual montage", "taVNS bilateral (SN modulation primary) + CES"],
    ["Attentional capture", "CEN + Attention", "DLPFC, ACC, right IFG", "Anodal F3/F4 (DLPFC bilateral — restores top-down suppression)", "CES during mindfulness attention training; taVNS"],
    ["Tinnitus anxiety", "SN + Limbic", "Amygdala, insula, DLPFC (F4)", "Anodal F4 (right DLPFC anxiolytic, 1.5 mA)", "taVNS bilateral + CES primary anxiolytic"],
    ["Sleep onset difficulty (tinnitus)", "Limbic + ANS + Circadian", "Amygdala, LC, thalamus", "Cathodal Cz optional (evening calming)", "CES 0.5 Hz 60 min pre-sleep (primary); taVNS 15 min evening"],
    ["Depression comorbid tinnitus", "Limbic + CEN", "Left DLPFC (F3), ACC, amygdala", "Anodal F3 (left DLPFC 2.0 mA, antidepressant polarity)", "taVNS anti-inflammatory; CES post-session"],
    ["Hyperacusis", "Auditory network + SN", "Bilateral A1/A2, anterior insula, thalamus", "Cathodal bilateral temporal (T3 + T4, 1.0–1.5 mA each) if bilateral device", "taVNS SN primary; gradual sound desensitisation (SRT); CES tonic"],
    ["Somatic tinnitus modulation", "Somatosensory-Auditory", "S1, DCN, TPJ", "Cathodal S1 (C3/C4, 1.0 mA) + cathodal temporal (T3)", "TPS TPJ; physiotherapy TMJ/C-spine concurrent"],
    ["Cognitive difficulties", "CEN", "DLPFC bilateral, ACC", "Bilateral anodal DLPFC (F3+F4) + cathodal temporal (T3)", "CES cognitive protocol; taVNS NE priming for attention"],
    ["Tinnitus in quiet / night-time", "Auditory network + DMN", "A1, mPFC, PCC", "Cathodal T3 + CES evening", "CES primary + sound enrichment (partial masking) at night"],
  ],

  montageSelectionRows: [
    ["Target", "Montage"],
    ["Auditory cortex inhibition — primary (cathodal temporal)", "Cathode: T3/TP7 (left temporal cortex, over A1/STG) — Anode: right supraorbital | 1.5–2.0 mA | 20 min | Level B evidence"],
    ["Dual montage — cathodal temporal + anodal frontal (FNON standard)", "Cathode: T3/TP7 — Anode: F3 (left DLPFC) | 1.5–2.0 mA | 20 min | simultaneous bottom-up + top-down"],
    ["Bilateral temporal (bilateral SNHL/bilateral tinnitus)", "Cathode bilateral: T3 + T4 — Reference: vertex (Cz) or bilateral anodes supraorbital | 1.0 mA per side"],
    ["Anodal left DLPFC (top-down attention restoration)", "Anode: F3 (left DLPFC) — Cathode: right supraorbital | 2.0 mA | 20 min | DLPFC attentional control"],
    ["Anodal right DLPFC (anxiety / attention)", "Anode: F4 (right DLPFC) — Cathode: left supraorbital | 1.5 mA | 20 min | right hemisphere anxiolytic"],
    ["Anodal mPFC / DMN (habituation support)", "Anode: Fz (mPFC) — Cathode: inion | 1.0–1.5 mA | 15–20 min | DMN-auditory coupling reduction"],
    ["Cathodal somatosensory (somatic tinnitus)", "Cathode: C3/C4 (S1, contralateral to dominant somatic modulation) — Anode: contralateral supraorbital | 1.0 mA | 15 min"],
    ["taVNS standard (all tinnitus phenotypes)", "Left cymba conchae auricular taVNS | 0.5 mA, 200 µs, 25 Hz | 15 min pre-session | limbic-SN distress modulation prerequisite"],
    ["CES anxiolytic / sleep tinnitus", "Alpha-Stim AID bilateral earlobe | 100 µA, 0.5 Hz | 40–60 min | pre-sleep or post-session | during sound therapy/TRT"],
    ["TPS auditory cortex precision", "NEUROLITH® TPS left STG/A1 (T3/TP7 region) | 0.20 mJ/mm², 2500–3000 pulses | neuro-navigation guided"],
    ["TPS left DLPFC (attention)", "NEUROLITH® TPS F3 DLPFC | 0.25 mJ/mm², 2500 pulses | neuro-navigation"],
    ["Anodal F3 (antidepressant/motivation)", "Anode: F3 — Cathode: right supraorbital | 2.0 mA | 20 min | tinnitus-depression comorbidity"],
    ["Bilateral cathodal temporal + anodal F3 + taVNS (full FNON tinnitus)", "Cathode T3/T4 (bilateral) — Anode F3 — taVNS left cymba conchae; 1.0–1.5 mA per side; full FNON protocol"],
  ],

  polarityPrincipleText:
    "Tinnitus represents the most specific polarity rationale in the FNON protocol library: the primary target (left temporal cortex — auditory cortex A1) requires cathodal (inhibitory) tDCS — uniquely, the treatment-relevant polarity is inhibitory, not excitatory, because the pathology is auditory cortex hyperexcitability. Cathodal tDCS reduces spontaneous neuronal firing rates through membrane hyperpolarisation, directly addressing the A1 hyperexcitability that generates the phantom percept. This Level B evidence cathodal temporal application contrasts with the anodal polarity used in most other FNON conditions. The second target — DLPFC (F3) — requires anodal tDCS (excitatory) to upregulate the hypoactive prefrontal top-down suppression mechanism. The FNON dual montage uniquely combines these two polarities in a single session: cathode over left temporal cortex (T3/TP7) and anode over left DLPFC (F3), with the return electrode at the right supraorbital region or contralateral mastoid. This dual montage simultaneously addresses the hyperexcitable auditory source and the hypoactive cortical suppression target within a single 20-minute session — the core FNON tinnitus innovation. For bilateral tinnitus or bilateral SNHL, bilateral cathodal temporal can be applied (T3 + T4) with a frontal anode reference. taVNS uses no DC polarity but modulates the NTS-limbic-SN pathway through afferent vagal nerve stimulation, complementing both cathodal temporal and anodal frontal mechanisms without direct polarity-mediated effects.",

  polarityTable: [
    ["Target", "Polarity", "Effect", "Primary Indication", "Evidence Level"],
    ["Left temporal cortex T3/TP7 (A1/STG)", "CATHODAL", "Inhibits A1 spontaneous hyperexcitability; reduces gamma oscillatory activity; dampens tinnitus signal generator", "Chronic tinnitus — primary auditory cortex target; SNHL-associated tinnitus; phantom percept reduction", "Level B — Lefaucheur 2017; De Ridder 2011; Vanneste 2013 (tDCS tinnitus RCTs)"],
    ["Left DLPFC F3", "ANODAL", "Upregulates top-down prefrontal suppression of auditory cortex; restores attentional filtering; reduces cognitive capture", "Tinnitus distress; attentional capture; cognitive complaints; DLPFC-auditory disconnection", "Level B — tDCS DLPFC tinnitus distress; Fregni 2006 evidence extrapolated"],
    ["Right DLPFC F4", "ANODAL", "Anxiolytic; right hemisphere emotional regulation; reduces tinnitus-associated anxiety; attention network", "Tinnitus anxiety; HADS anxiety ≥8; attentional disengagement support", "Level B (anxiety) — Level C (tinnitus-anxiety specific)"],
    ["mPFC Fz", "ANODAL", "Upregulates DMN mPFC; reduces DMN-auditory coupling; supports habituation neuroplasticity", "Habituation failure; DMN-auditory hyperconnectivity; tinnitus as self-referential default experience", "Level C — mPFC tDCS habituation literature; tinnitus DMN model"],
    ["Somatosensory cortex C3/C4", "CATHODAL", "Reduces somatosensory cortex excitability; reduces somatosensory-auditory convergence at DCN level; somatic tinnitus modulation", "Somatic tinnitus; jaw/neck-modulated tinnitus; somatosensory contribution to tinnitus percept", "Level C — somatosensory tDCS; somatic tinnitus model"],
  ],

  classicTdcsProtocols: [
    {
      code: "C1",
      name: "Standard Cathodal Left Temporal Protocol (Level B)",
      montage: "Cathode T3/TP7 (left temporal cortex) — Anode right supraorbital",
      intensity: "1.5–2.0 mA",
      duration: "20 minutes",
      sessions: "5–10 sessions (5 daily consecutive sessions standard; extend to 10 for moderate-severe THI)",
      indication: "Chronic tinnitus primary; auditory cortex hyperexcitability reduction; SNHL-associated tinnitus",
      evidence: "Level B — Lefaucheur 2017 Grade B recommendation; De Ridder 2011 (Neuroscience); Vanneste 2013"
    },
    {
      code: "C2",
      name: "Standard Dual Montage Protocol (cathodal temporal + anodal frontal)",
      montage: "Cathode T3/TP7 — Anode F3 (left DLPFC); single bifocal session",
      intensity: "1.5 mA",
      duration: "20 minutes",
      sessions: "10 sessions",
      indication: "Tinnitus with attentional capture and distress; combined auditory + prefrontal target",
      evidence: "Level B — bifocal tDCS tinnitus; DLPFC + temporal montage RCTs (Vanneste 2010)"
    },
    {
      code: "C3",
      name: "Standard Left DLPFC Anodal Protocol",
      montage: "Anode F3 — Cathode right supraorbital",
      intensity: "2.0 mA",
      duration: "20 minutes",
      sessions: "10 sessions",
      indication: "Tinnitus distress (high THI); tinnitus depression comorbidity; prefrontal top-down restoration",
      evidence: "Level B — DLPFC tDCS tinnitus distress; depression tDCS evidence (Brunoni 2017)"
    },
    {
      code: "C4",
      name: "Standard Right DLPFC Anxiolytic Protocol",
      montage: "Anode F4 — Cathode left supraorbital",
      intensity: "1.5 mA",
      duration: "20 minutes",
      sessions: "10 sessions",
      indication: "Tinnitus anxiety; HADS anxiety ≥8; right hemisphere attentional anxiety",
      evidence: "Level B (anxiety tDCS); Level C (tinnitus-anxiety specific)"
    },
    {
      code: "C5",
      name: "Standard Bilateral Temporal Protocol",
      montage: "Cathode T3 + T4 bilateral — Anode Cz (reference)",
      intensity: "1.0 mA per side (2.0 mA total)",
      duration: "20 minutes",
      sessions: "10 sessions",
      indication: "Bilateral tinnitus; bilateral SNHL with bilateral hyperexcitability",
      evidence: "Level C — bilateral temporal tDCS tinnitus; derived from unilateral Level B evidence"
    },
    {
      code: "C6",
      name: "Standard Cathodal Somatosensory Protocol (somatic tinnitus)",
      montage: "Cathode C3/C4 (contralateral to dominant somatic modulation) — Anode contralateral supraorbital",
      intensity: "1.0 mA",
      duration: "15 minutes",
      sessions: "10 sessions + physiotherapy TMJ/C-spine",
      indication: "Somatic tinnitus; jaw/neck modulation positive; somatosensory-auditory convergence",
      evidence: "Level C — somatosensory tDCS; somatic tinnitus model"
    },
    {
      code: "C7",
      name: "Standard CES Sleep / Distress Protocol",
      montage: "Alpha-Stim AID bilateral earlobe — 100 µA, 0.5 Hz",
      intensity: "100 µA",
      duration: "40–60 minutes (pre-sleep or concurrent with sound therapy/TRT)",
      sessions: "Daily × 3 weeks; then 3–5×/week maintenance",
      indication: "Tinnitus sleep disruption; tinnitus anxiety distress; tonic ANS calming",
      evidence: "Level C — CES sleep/anxiety; tinnitus distress management"
    },
    {
      code: "C8",
      name: "Standard mPFC Habituation Support Protocol",
      montage: "Anode Fz (mPFC) — Cathode inion",
      intensity: "1.0–1.5 mA",
      duration: "15–20 minutes",
      sessions: "10 sessions concurrent with TRT",
      indication: "Habituation failure in tinnitus; DMN-auditory coupling; tinnitus as default experiential baseline",
      evidence: "Level C — mPFC tDCS habituation; DMN tinnitus model"
    },
  ],

  fnonTdcsProtocols: [
    {
      code: "F1",
      name: "FNON Dual-Network Tinnitus Protocol — Cathodal Temporal + Anodal Frontal + taVNS",
      montage: "Cathode T3/TP7 + Anode F3 (bifocal) — Cathode return: right supraorbital; taVNS left cymba conchae 15 min pre-session",
      intensity: "1.5–2.0 mA bifocal tDCS; taVNS 0.5 mA, 200 µs, 25 Hz",
      duration: "15 min taVNS pre-session + 20 min bifocal tDCS",
      sessions: "10–15 sessions",
      indication: "Chronic tinnitus with distress; primary FNON tinnitus protocol; simultaneous bottom-up (A1 inhibition) + top-down (DLPFC upregulation) + limbic-SN (taVNS)",
      fnon_rationale: "The FNON tinnitus signature protocol: simultaneous cathodal temporal (inhibit A1) + anodal frontal (upregulate DLPFC suppression) addresses both dimensions of tinnitus in one session; taVNS pre-session reduces limbic-SN distress amplification before cortical stimulation — maximum triple-network tinnitus intervention"
    },
    {
      code: "F2",
      name: "FNON High-Distress Tinnitus Protocol — Limbic + Prefrontal",
      montage: "Anode F3 (2.0 mA) + taVNS bilateral (0.5 mA) + CES post-session (100 µA)",
      intensity: "2.0 mA tDCS + bilateral taVNS + CES 100 µA",
      duration: "20 min tDCS + bilateral taVNS concurrent + CES 40–60 min post",
      sessions: "15–20 sessions",
      indication: "High-distress tinnitus (THI ≥56); catastrophising; significant anxiety/depression comorbidity",
      fnon_rationale: "Limbic-first approach for high-distress tinnitus: bilateral taVNS maximum anti-distress (NTS→amygdala, NTS→insula) + anodal F3 (prefrontal-limbic regulation upregulation) + CES post-session sustained calming — addressing the distress dimension before the signal dimension, which predicts better treatment response in high-THI patients"
    },
    {
      code: "F3",
      name: "FNON Tinnitus-Sleep Protocol — CES + taVNS + Evening Cathodal",
      montage: "taVNS 0.5 mA × 15 min evening + cathodal Cz 1.0 mA × 15 min (optional) + CES 100 µA × 60 min pre-sleep",
      intensity: "taVNS 0.5 mA + tDCS cathodal 1.0 mA optional + CES 100 µA",
      duration: "Evening protocol: 15 min taVNS → 15 min tDCS → 60 min CES pre-sleep",
      sessions: "Daily × 2 weeks evening protocol; then maintenance 5×/week",
      indication: "Sleep-disrupted tinnitus; PSQI >5; tinnitus auditory cortex quiet-loudness amplification at night",
      fnon_rationale: "Evening tinnitus protocol: taVNS vagal parasympathetic induction and LC calming at sleep onset; cathodal Cz reduces SMA/DMN hyperarousal preventing sleep; CES primary sleep-onset intervention simultaneously calming tinnitus-distress arousal and facilitating sleep — combined tinnitus-sleep intervention"
    },
    {
      code: "F4",
      name: "FNON VNS-Paired Acoustic Therapy Protocol — taVNS + Sound Therapy",
      montage: "taVNS 0.5 mA, 200 µs, 25 Hz concurrent with residual inhibition tone or notched noise therapy",
      intensity: "taVNS 0.5 mA; sound therapy at comfortable level (partial masking level)",
      duration: "20 min taVNS concurrent with sound therapy session; daily if possible",
      sessions: "10–20 sessions (may extend to maintenance)",
      indication: "Chronic tinnitus with residual inhibition response; VNS-paired sound therapy (neuromodulation + acoustic); modelled on MicroTransponder Serenity system principle",
      fnon_rationale: "VNS-paired auditory tone therapy principle (adapted from Kilgard 2011, Berry 2019): VNS during acoustic stimulation induces acetylcholine-mediated broadening of auditory cortex receptive fields, promoting tonotopic map reorganisation away from the tinnitus frequency — taVNS delivers the VNS neuromodulatory component; residual inhibition tone or notched noise provides the paired acoustic stimulus"
    },
    {
      code: "F5",
      name: "FNON Bilateral Tinnitus / Hyperacusis Protocol — Bilateral Cathodal + taVNS",
      montage: "Bilateral cathodal temporal (T3 + T4, 1.0 mA each) — Reference Cz; taVNS pre-session; CES post-session; sound desensitisation concurrent",
      intensity: "Bilateral cathodal 1.0 mA per side; taVNS 0.5 mA; CES 100 µA post",
      duration: "20 min bilateral tDCS + taVNS 15 min pre + CES 40 min post",
      sessions: "10–15 sessions concurrent with sound desensitisation programme",
      indication: "Bilateral tinnitus with hyperacusis; bilateral A1 hyperexcitability; bilateral SNHL; SN-driven auditory cortex hyper-reactivity",
      fnon_rationale: "Bilateral cathodal temporal addresses bilateral A1 hyperexcitability; taVNS reduces SN contribution to both tinnitus and hyperacusis (shared SN-insula mechanism); CES post provides tonic autonomic calming during sound desensitisation gradual re-exposure programme"
    },
    {
      code: "F6",
      name: "FNON Multi-Network Tinnitus Maintenance Protocol",
      montage: "Rotating: Session 1,3,5 — FNON F1 (dual cathodal temporal + anodal frontal + taVNS); Session 2,4,6 — FNON F4 (VNS-paired acoustic); taVNS and CES every session",
      intensity: "Per individual session protocols",
      duration: "Per individual sessions; taVNS every session; CES daily home",
      sessions: "12 sessions (rotating) + monthly booster sessions",
      indication: "Chronic refractory tinnitus; Phase 2 maintenance after intensive protocol; multi-network tinnitus management",
      fnon_rationale: "Rotating auditory-network (cathodal temporal tDCS) and VNS-paired acoustic sessions prevents adaptation to single-target stimulation; taVNS daily home maintenance as anti-distress baseline; CES nightly pre-sleep to maintain tinnitus-sleep domain improvement"
    },
  ],

  classicTpsProtocols: [
    {
      code: "T1",
      name: "Classic TPS Auditory Cortex Inhibition Protocol",
      target: "Left primary auditory cortex (T3/TP7 area; neuro-navigation for A1/STG precision)",
      parameters: "0.20 mJ/mm², 2500–3000 pulses, 3 Hz",
      sessions: "6 sessions (2×/week × 3 weeks)",
      indication: "Chronic tinnitus; A1 hyperexcitability; SNHL-associated tinnitus; precision auditory cortex targeting",
      evidence: "Level C — TPS auditory cortex; adapted from rTMS auditory cortex tinnitus protocols"
    },
    {
      code: "T2",
      name: "Classic TPS Left DLPFC Top-Down Protocol",
      target: "Left DLPFC (F3 area; neuro-navigation; 2–3 cm depth)",
      parameters: "0.25 mJ/mm², 2500 pulses, 3 Hz",
      sessions: "6 sessions concurrent with mindfulness-based attention training",
      indication: "Tinnitus attentional capture; DLPFC hypoactivation; top-down suppression restoration",
      evidence: "Level C — DLPFC TPS attention; tinnitus attention network"
    },
    {
      code: "T3",
      name: "Classic TPS Temporoparietal Junction Protocol",
      target: "Left TPJ (CP5 area; neuro-navigation — auditory-attention-somatosensory interface)",
      parameters: "0.20 mJ/mm², 2500 pulses, 3 Hz",
      sessions: "6 sessions",
      indication: "Tinnitus auditory-attentional network; somatic tinnitus component; TPJ auditory-somatosensory convergence",
      evidence: "Level C — TPJ TPS; auditory attention tinnitus model"
    },
    {
      code: "T4",
      name: "Classic TPS Bilateral Auditory Cortex Protocol",
      target: "Bilateral STG/A1 (T3 then T4; alternating within session); neuro-navigation",
      parameters: "0.20 mJ/mm², 2500 pulses per hemisphere; bilateral session 50 min",
      sessions: "6 sessions",
      indication: "Bilateral tinnitus; bilateral SNHL; bilateral A1 hyperexcitability",
      evidence: "Level C — bilateral auditory cortex TPS; bilateral tinnitus model"
    },
    {
      code: "T5",
      name: "Classic TPS ACC/mPFC Habituation Protocol",
      target: "ACC/mPFC (Fz area, 1–2 cm depth; neuro-navigation)",
      parameters: "0.20 mJ/mm², 2500 pulses, 3 Hz",
      sessions: "6 sessions concurrent with TRT",
      indication: "Habituation failure; ACC-auditory hyperconnectivity; tinnitus DMN-auditory coupling",
      evidence: "Level C — ACC TPS habituation; tinnitus DMN model"
    },
  ],

  fnonTpsProtocols: [
    {
      code: "FT1",
      name: "FNON TPS Dual-Network Auditory-Frontal Protocol",
      target: "Left A1/STG (T3/TP7, 2500 pulses) → left DLPFC (F3, 2500 pulses) sequential; taVNS concurrent",
      parameters: "0.20–0.25 mJ/mm² per target; neuro-navigation; taVNS concurrent; 50 min",
      sessions: "6–8 sessions (2×/week)",
      indication: "Chronic tinnitus with distress; dual A1 inhibition + DLPFC upregulation; TPS precision for both targets",
      fnon_rationale: "Sequential TPS replicates the FNON dual tDCS montage rationale but with TPS precision: A1 inhibitory stimulation then DLPFC upregulatory stimulation — targeting both auditory network hyperexcitability and prefrontal attentional suppression failure in sequence; taVNS concurrent SN-limbic modulation"
    },
    {
      code: "FT2",
      name: "FNON TPS Tinnitus-Limbic Protocol — Auditory + Amygdala-Adjacent",
      target: "Left STG/A1 (2500 pulses) → temporal-amygdala transition zone (T3-T5, 2000 pulses, amygdala-adjacent); taVNS concurrent",
      parameters: "0.20 mJ/mm² per target; neuro-navigation; 45 min; taVNS concurrent",
      sessions: "6 sessions",
      indication: "High-distress tinnitus; amygdala-auditory hyperconnectivity; fear conditioning to tinnitus sound",
      fnon_rationale: "Sequential A1 inhibition then amygdala-adjacent TPS targets both ends of the auditory-limbic arc: A1 reduces the phantom sound generator, while temporal-amygdala transition zone TPS modulates the auditory-emotional conditioning circuit maintaining tinnitus distress; taVNS concurrent provides NTS-amygdala inhibition as third modality"
    },
    {
      code: "FT3",
      name: "FNON TPS VNS-Paired Sound Protocol — Auditory Cortex Remodelling",
      target: "Left A1/STG TPS (2500 pulses) during residual inhibition tone playback; taVNS concurrent during TPS session",
      parameters: "0.20 mJ/mm², 2500 pulses; TPS delivered concurrent with specific tone (residual inhibition frequency); taVNS concurrent",
      sessions: "6–8 sessions; each session: taVNS + specific tone playback + A1 TPS simultaneously",
      indication: "Tinnitus with demonstrable residual inhibition response; tonotopic reorganisation target; activity-dependent plasticity auditory cortex",
      fnon_rationale: "Activity-dependent plasticity principle: A1 TPS delivered concurrent with sound therapy (during neural activation by the therapeutic acoustic stimulus) promotes tonotopic map reorganisation at the moment of TPS plasticity induction — amplifying the acoustic therapy effect through triple-concurrent mechanism: taVNS ACh neuromodulatory broadening + TPS focal plasticity + therapeutic sound stimulus"
    },
    {
      code: "FT4",
      name: "FNON TPS Prefrontal-Cingulate Attention Protocol",
      target: "Left DLPFC (F3, 2500 pulses) → ACC/mPFC (Fz, 2000 pulses) sequential",
      parameters: "0.25 mJ/mm² per target; neuro-navigation; 45 min",
      sessions: "6 sessions concurrent with mindfulness-based attention training for tinnitus",
      indication: "Tinnitus attentional capture dominant; DLPFC-ACC attention network; cognitive complaints from tinnitus",
      fnon_rationale: "DLPFC then ACC TPS targets the full top-down attentional suppression hierarchy: DLPFC (executive attentional control) → ACC (conflict/salience monitoring gate) — both impaired in tinnitus; sequential stimulation mimics the top-down signal flow needed to suppress tinnitus attentional capture"
    },
    {
      code: "FT5",
      name: "FNON TPS Somatic-Auditory Protocol — TPJ + A1",
      target: "Left TPJ (CP5, 2500 pulses) → left A1/STG (T3, 2500 pulses) sequential",
      parameters: "0.20 mJ/mm² per target; neuro-navigation; 45 min; physiotherapy concurrent",
      sessions: "6 sessions concurrent with TMJ/cervical physiotherapy",
      indication: "Somatic tinnitus; jaw/neck-modulated tinnitus; somatosensory-auditory convergence",
      fnon_rationale: "TPJ TPS targets the somatosensory-auditory interface (TPJ is the cortical convergence zone for somatic and auditory information); sequential A1 TPS then addresses the auditory cortex that receives aberrant somatosensory-auditory input; physiotherapy TMJ/C-spine concurrent addresses the peripheral somatosensory driver"
    },
    {
      code: "FT6",
      name: "FNON TPS Bilateral Tinnitus + Hyperacusis Protocol",
      target: "Bilateral STG/A1 (T3 then T4, 2500 pulses each hemisphere); taVNS concurrent; CES post",
      parameters: "0.20 mJ/mm² per hemisphere; bilateral session 50 min; taVNS + CES",
      sessions: "6–8 sessions concurrent with bilateral sound desensitisation",
      indication: "Bilateral tinnitus + hyperacusis; bilateral auditory cortex hyperexcitability; bilateral SNHL",
      fnon_rationale: "Sequential bilateral A1 TPS inhibits bilateral auditory cortex hyperexcitability; taVNS concurrent modulates SN contribution to both tinnitus and hyperacusis; CES post-session tonic ANS calming supports bilateral sound desensitisation programme"
    },
    {
      code: "FT7",
      name: "FNON TPS Tinnitus-Depression Protocol — A1 + DLPFC + F3",
      target: "Left A1/STG (T3, 2500 pulses) → left DLPFC (F3, 2500 pulses) → TPS mPFC (Fz, 2000 pulses)",
      parameters: "0.20–0.25 mJ/mm² per target; neuro-navigation; 75 min; taVNS concurrent",
      sessions: "6–8 sessions concurrent with CBT-tinnitus-depression protocol",
      indication: "Tinnitus with significant depression comorbidity (HADS depression ≥8); three-node TPS for tinnitus-depression circuit",
      fnon_rationale: "Three-target TPS: A1 inhibition (tinnitus signal) + DLPFC upregulation (depression + attentional control) + mPFC (DMN antidepressant) — addressing the tinnitus-depression comorbidity from all three dimensions simultaneously; taVNS concurrent anti-inflammatory and anti-depressant augmentation"
    },
    {
      code: "FT8",
      name: "FNON TPS Tinnitus Maintenance Protocol — Alternating Networks",
      target: "Alternating: odd sessions — auditory (A1 + DLPFC TPS); even sessions — limbic-frontal (DLPFC + ACC + mPFC); taVNS every session",
      parameters: "0.20–0.25 mJ/mm², 2500 pulses per target; neuro-navigation; 45–60 min",
      sessions: "12 sessions rotating; monthly maintenance single session post-protocol",
      indication: "Chronic treatment-resistant tinnitus; long-term network maintenance; Phase 2 tinnitus FNON",
      fnon_rationale: "Alternating auditory-network and limbic-frontal TPS sessions prevent adaptation while maintaining stimulation of all three pathological networks (auditory, prefrontal, limbic); taVNS daily home between sessions as anti-distress ANS baseline"
    },
    {
      code: "FT9",
      name: "FNON TPS Comprehensive Tinnitus Protocol — Full Network",
      target: "Session sequence: 1,4,7 — A1+DLPFC (primary); 2,5,8 — TPJ+A1 (somatic-auditory); 3,6,9 — DLPFC+ACC (attention-distress); taVNS every session",
      parameters: "0.20–0.25 mJ/mm², 2500 pulses per target; neuro-navigation; 45 min per session",
      sessions: "9 sessions rotating (3 cycles); monthly TPS maintenance",
      indication: "Multi-phenotype chronic tinnitus; high THI + somatic component + cognitive complaints + sleep disturbance",
      fnon_rationale: "Comprehensive 9-session rotating TPS protocol covers all three tinnitus network domains: auditory-frontal (tinnitus signal + attention), somatic-auditory (somatosensory contribution), and attention-distress (prefrontal-cingulate) — the most comprehensive tinnitus TPS protocol for complex presentations"
    },
  ],

  multimodalPhenotypes: [
    {
      phenotype: "Noise-Induced / SNHL Tinnitus",
      stabilise: "taVNS left cymba conchae 0.5 mA, 200 µs, 25 Hz × 15 min (SN modulation; NTS→LC anxiety calming; thalamocortical normalisation pre-stimulation)",
      optimise: "Bifocal tDCS: cathode T3/TP7 (left temporal, 1.5–2.0 mA) + anode F3 (left DLPFC) × 20 min concurrent — dual bottom-up + top-down tinnitus protocol (FNON standard montage)",
      zone: "TPS left A1/STG 0.20 mJ/mm² 2500 pulses (neuro-navigation precision) + TPS left DLPFC 2500 pulses sequential; 50 min TPS session",
      outcome: "CES 100 µA × 40 min concurrent with TRT session or sound therapy; THI and TFI monitoring at 5 and 10 sessions; hearing aid fitting if SNHL ≥20 dBHL concurrent"
    },
    {
      phenotype: "High-Distress / Catastrophising Tinnitus",
      stabilise: "Bilateral taVNS 0.5 mA × 20 min (maximum limbic-SN distress modulation — bilateral doubles vagal-amygdala inhibition; mandatory first intervention for high-THI)",
      optimise: "Anodal F3 tDCS (2.0 mA × 20 min) concurrent with bilateral taVNS — antidepressant-anxiolytic DLPFC upregulation combined with taVNS limbic distress suppression; CBT tinnitus session concurrent",
      zone: "TPS left DLPFC 0.25 mJ/mm² 2500 pulses + TPS A1/STG 2500 pulses (odd sessions); TPS DLPFC + ACC Fz (even sessions for habituation support); neuro-navigation",
      outcome: "CES 100 µA × 40–60 min post-session (sustained limbic calming); CBT for tinnitus catastrophising concurrent; THI catastrophising subscale monitoring; psychiatric review if suicidal ideation present"
    },
    {
      phenotype: "Tinnitus with Anxiety/Depression",
      stabilise: "Bilateral taVNS 0.5 mA × 15 min (anti-inflammatory + NTS→amygdala inhibition; vagal parasympathetic restoration — reduces anxiety-tinnitus loop arousal)",
      optimise: "Anodal F3 or F4 tDCS (2.0 mA; F3 if depression dominant, F4 if anxiety dominant) × 20 min; cathodal T3 simultaneously if dual-channel device available; CBT for tinnitus-anxiety/depression concurrent",
      zone: "TPS A1/STG 2500 pulses + DLPFC 2500 pulses (primary); TPS hippocampal 2000 pulses (memory-fear conditioning for tinnitus, session 3/6/9); neuro-navigation",
      outcome: "CES 40–60 min post-session; HADS monitoring fortnightly; antidepressant medication if PHQ-9 ≥10; psychological therapy concurrent; suicide risk assessment at every session in high-HADS tinnitus"
    },
    {
      phenotype: "Sleep-Disturbed Tinnitus",
      stabilise: "taVNS 0.5 mA × 15 min EVENING (circadian reset; LC-NE calming at sleep onset; NTS→thalamic sleep circuit modulation)",
      optimise: "Cathodal Cz tDCS 1.0 mA × 15 min evening (DMN/arousal calming — not cathodal temporal in evening to avoid activating auditory cortex paradoxically in some patients); optional: cathodal T3 if tinnitus loudness particularly prominent at night",
      zone: "TPS mPFC (Fz) 0.20 mJ/mm² 2000 pulses ONCE WEEKLY evening session only; not daily TPS for sleep phenotype",
      outcome: "CES 0.5 Hz 100 µA × 60 min pre-sleep (primary sleep-tinnitus intervention every night); sound enrichment device at bedside (fan, white noise, music — partial masking NOT complete masking); PSQI monitoring at 2 and 4 weeks"
    },
    {
      phenotype: "Hyperacusis-Comorbid Tinnitus",
      stabilise: "taVNS 0.5 mA × 15 min (SN anterior insula modulation — reduces both tinnitus SN-distress AND hyperacusis insula-mediated auditory oversensitivity; primary shared mechanism)",
      optimise: "Bilateral cathodal temporal tDCS (T3+T4, 1.0 mA each) × 20 min concurrent with gradual sound desensitisation (SRT protocol) — bilateral A1 inhibition + sound re-exposure",
      zone: "TPS bilateral STG/A1 (T3 then T4, 2500 pulses each) × bilateral session; CES post-session during sound desensitisation homework",
      outcome: "CES 100 µA × 40 min post-session; hyperacusis questionnaire (HQ) monitoring; LDL (loudness discomfort levels) audiometric monitoring; cautious graduated noise exposure programme; avoid noise overstimulation during protocol"
    },
    {
      phenotype: "Somatic / Cervicogenic Tinnitus",
      stabilise: "taVNS 0.5 mA × 15 min (standard SN pre-session); physiotherapy TMJ/C-spine session same day (before or after NIBS) for somatic component",
      optimise: "Cathodal S1 tDCS (C3/C4, 1.0 mA) × 15 min (somatosensory cortex inhibition of aberrant somatosensory-auditory convergence) + cathodal T3 (1.5 mA) × 20 min — dual somatosensory + auditory cathodal protocol",
      zone: "TPS left TPJ (CP5, 2500 pulses) → left A1/STG (T3, 2500 pulses) sequential; neuro-navigation; physiotherapy TMJ/C-spine concurrent",
      outcome: "Somatic modulation re-test at 5 sessions (positive somatic modulation test should reduce); TMJ/C-spine physiotherapy outcome; THI monitoring; combined NIBS + physiotherapy expected better response than either alone"
    },
    {
      phenotype: "Treatment-Resistant Tinnitus",
      stabilise: "Bilateral taVNS 0.5 mA × 20 min (maximum anti-distress; bilateral doubles efficacy); review previous treatments and failure modes with patient",
      optimise: "Full FNON F1 protocol (bifocal cathodal temporal + anodal frontal tDCS 2.0 mA × 20 min) + bilateral taVNS concurrent — maximum intensity dual tDCS + taVNS",
      zone: "Intensive TPS: A1/STG (3000 pulses) + DLPFC (2500 pulses) + ACC (2000 pulses) per session; 3 targets × neuro-navigation; 60–75 min TPS; sessions 2×/week × 6 weeks",
      outcome: "CES 40–60 min daily (home device); home taVNS 2 × 15 min daily; monthly TPS maintenance; MDT review at 6 weeks; consider VNS-paired acoustic therapy as add-on; psychological support for treatment expectations management"
    },
    {
      phenotype: "Tinnitus with Cognitive Complaints",
      stabilise: "taVNS 0.5 mA × 15 min (NTS→LC→NE priming — noradrenergic enhancement of attention and cognitive function pre-session; standard tinnitus SN pre-conditioning)",
      optimise: "Bilateral anodal DLPFC tDCS (F3+F4, 1.0 mA each) + cathodal T3 (1.5 mA) — tri-montage: bilateral CEN upregulation + auditory inhibition; concurrent with cognitive task or mindfulness attention training",
      zone: "TPS left DLPFC 0.25 mJ/mm² 3000 pulses + left A1 2500 pulses (cognitive dominant sessions); TPS ACC (2500 pulses) for attention-cingulate sessions",
      outcome: "SDMT cognitive monitoring; PANAS attention/cognition self-report; occupational function return monitoring; CBT for tinnitus cognitive interference concurrent"
    },
    {
      phenotype: "Post-Acute Noise Trauma Tinnitus (early <6 months)",
      stabilise: "taVNS bilateral 0.5 mA × 20 min (anti-inflammatory — NTS→cholinergic anti-inflammatory reflex→cochlear and central neuroinflammation suppression immediately post-trauma; primary early intervention)",
      optimise: "Cathodal T3/TP7 tDCS (1.5 mA × 20 min) — early auditory cortex maladaptive plasticity prevention; concurrent with hearing protection advice and HADS screening",
      zone: "TPS A1/STG 0.20 mJ/mm² 2500 pulses × 3 sessions in first 2 weeks (early intervention window); taVNS concurrent",
      outcome: "Early intervention goal: prevent chronification of acute tinnitus to chronic distressing tinnitus; THI monitoring at 4 and 8 weeks; residual inhibition testing at 4 weeks; hearing protection strict; CES for concurrent sleep and anxiety management in acute phase"
    },
    {
      phenotype: "Bilateral Tinnitus / Bilateral SNHL",
      stabilise: "taVNS 0.5 mA × 15 min (standard; thalamocortical bilateral normalisation via NTS projections; SN bilateral modulation)",
      optimise: "Bilateral cathodal temporal tDCS (T3+T4, 1.0 mA each) + anodal F3 (1.5 mA) — bilateral auditory inhibition + left DLPFC top-down restoration",
      zone: "TPS bilateral A1/STG (T3 then T4, 2500 pulses each; 50 min bilateral session); TPS left DLPFC (2500 pulses, add-on session 3, 6); neuro-navigation",
      outcome: "Bilateral hearing aid fitting concurrent if SNHL ≥20 dBHL bilateral; bilateral THI tracking; binaural sound therapy; CES post-session"
    },
  ],

  taskPairingRows: [
    ["Task Type", "Concurrent NIBS", "Protocol Rationale", "Outcome Measure"],
    ["Tinnitus Retraining Therapy (TRT) counselling session", "taVNS + CES during TRT session", "taVNS SN modulation + CES tonic calming during habituation counselling: limbic system in reduced distress state during TRT learning enhances habituation neuroplasticity", "THI global score (target −20 points); TFI global score; tinnitus habituation self-report"],
    ["CBT for tinnitus (cognitive restructuring)", "Anodal F3 tDCS + taVNS bilateral", "DLPFC upregulation during cognitive reappraisal tasks: prefrontal top-down control enhanced during CBT cognitive restructuring for maximum tinnitus catastrophising extinction", "THI emotional subscale; HADS; Tinnitus Catastrophizing Scale (TCS)"],
    ["Sound therapy / notched noise therapy", "taVNS concurrent + cathodal T3 (pre-session)", "VNS-paired sound therapy principle: taVNS during sound exposure promotes ACh-mediated auditory cortex plasticity; cathodal pre-session primes A1 for sound therapy", "Tinnitus loudness matching (dB SL); residual inhibition duration; notched noise therapy response"],
    ["Mindfulness-based attention training for tinnitus", "Bilateral anodal DLPFC tDCS (F3+F4) + taVNS", "CEN upregulation during mindfulness attention training: DLPFC enhancement of attentional flexibility training; taVNS autonomic calming supports mindfulness state", "Tinnitus Mindfulness Scale; cognitive defusion from tinnitus; FFMQ (mindfulness measure)"],
    ["Physiotherapy TMJ / cervical spine (somatic tinnitus)", "Cathodal S1 + cathodal T3 tDCS + physiotherapy concurrent", "Somatosensory and auditory cortex inhibition during somatic mobilisation: reduces cortical somatosensory-auditory excitability during manual therapy producing the somatic tinnitus signal", "Somatic modulation test (positive→negative at follow-up); VAS tinnitus loudness during somatic provocation; TMJ ROM"],
    ["Sleep hygiene education / pre-sleep routine", "CES 60 min pre-sleep + taVNS 15 min evening", "Tonic ANS calming during sleep hygiene practice; vagal parasympathetic induction concurrent with wind-down routine; tinnitus-sleep interference reduction", "Actigraphy sleep onset latency; PSQI; tinnitus intrusion on sleep VAS"],
  ],

  outcomeMeasures:
    "Primary outcome measures for the SOZO Tinnitus FNON protocol: (1) Tinnitus Handicap Inventory (THI — 0–100 scale) — primary outcome; clinically meaningful change: ≥7 points (MCID established); categorical change: ≥20 points (grade shift, e.g., severe→moderate). (2) Tinnitus Functional Index (TFI) — multidimensional outcome; global score and subscale scores (intrusiveness, sense of control, cognitive, sleep, auditory, relaxation, quality of life, emotional); MCID: ≥13 points. (3) Hospital Anxiety and Depression Scale (HADS) — both anxiety and depression subscales; MCID ≥1.5 points per subscale. (4) Pittsburgh Sleep Quality Index (PSQI) — sleep component MCID: ≥3 points. (5) Visual Analogue Scale (VAS) tinnitus loudness (0–100) — assessed at each session. Secondary measures: tinnitus pitch and loudness matching (audiometric, dB SL above threshold); residual inhibition duration and percentage (audiometric); EEG gamma power spectral analysis A1 region (if available, participating sites); HADS anxiety and depression subscales; SF-36 quality of life; minimal masking level. Safety monitoring: skin inspection at electrode sites after every session; audiometric assessment if tinnitus significantly worsens. Neurophysiological optional: EEG alpha-gamma ratio in A1; auditory evoked potentials; TMS auditory cortex excitability mapping pre/post protocol. THI assessment at baseline, 5 sessions, 10 sessions, and 1-month follow-up.",

  medicationSectionTitle: "Pharmacological Context and NIBS Interactions in Tinnitus",
  medicationSectionText:
    "No pharmacological agent has Level A or B evidence for chronic tinnitus. NICE NG155 explicitly recommends against benzodiazepines, ginkgo biloba, anticonvulsants, and low-power laser. Key medication interactions with FNON: Tricyclic antidepressants (amitriptyline, nortriptyline): used off-label for tinnitus distress; may augment tDCS cortical effects through noradrenergic and serotonergic facilitation; document dose. SSRIs (sertraline, escitalopram): for tinnitus-associated depression/anxiety; serotonergic facilitation may enhance DLPFC tDCS LTP; document and continue. Beta-blockers (propranolol, metoprolol): used for tinnitus-related anxiety/arousal; reduce LC-NE mediated hyperarousal; complementary to taVNS vagal pathway; monitor HR throughout taVNS sessions. Betahistine (Meniere's disease subtype): anti-histaminergic vasodilatory effect on inner ear; no direct NIBS interaction; document use. Gabapentin/pregabalin (tinnitus off-label): reduce auditory cortex excitability through α2δ calcium channel; complementary to cathodal temporal tDCS; document dose — may reduce tDCS response in CEN targets. Carbamazepine (typewriter tinnitus, off-label): sodium channel stabilisation reduces A1 excitability; complementary to cathodal tDCS; document and maintain stable dose. Hearing aids: wearing during sessions interferes with temporal electrode placement — remove hearing aids during electrode application; replace immediately post-session; hearing aid use does not preclude FNON protocols. Loop diuretics (furosemide), aspirin (high-dose), aminoglycoside antibiotics: ototoxic medications that may worsen tinnitus — document; advise liaison with prescribing team if ototoxic drug identified as modifiable cause. Zinc / melatonin (tinnitus supplement use): no known NIBS interaction; document use. Caffeine: document habitual intake; caffeine avoidance may reduce tinnitus hyperarousal in caffeine-sensitive individuals — counsel regarding caffeine and sound sensitivity.",

  references: {
    foundational: [
      { authors: "Baguley D, McFerran D, Hall D", year: 2013, title: "Tinnitus", journal: "The Lancet", volume: "382(9904)", pages: "1600–1607", doi: "10.1016/S0140-6736(13)60142-7" },
      { authors: "Bhatt JM, Lin HW, Bhattacharyya N", year: 2016, title: "Prevalence, severity, exposures, and treatment patterns of tinnitus in the United States", journal: "JAMA Otolaryngology–Head & Neck Surgery", volume: "142(10)", pages: "959–965", doi: "10.1001/jamaoto.2016.1700" },
      { authors: "Henry JA, Roberts LE, Caspary DM, et al.", year: 2014, title: "Underlying mechanisms of tinnitus: review and clinical implications", journal: "Journal of the American Academy of Audiology", volume: "25(1)", pages: "5–22", doi: "10.3766/jaaa.25.1.2" },
      { authors: "Llinas RR, Ribary U, Jeanmonod D, et al.", year: 1999, title: "Thalamocortical dysrhythmia: A neurological and neuropsychiatric syndrome characterized by magnetoencephalography", journal: "Proceedings of the National Academy of Sciences", volume: "96(26)", pages: "15222–15227", doi: "10.1073/pnas.96.26.15222" },
      { authors: "Eggermont JJ, Roberts LE", year: 2004, title: "The neuroscience of tinnitus", journal: "Trends in Neurosciences", volume: "27(11)", pages: "676–682", doi: "10.1016/j.tins.2004.08.010" },
      { authors: "De Ridder D, Elgoyhen AB, Romo R, Langguth B", year: 2011, title: "Phantom percepts: tinnitus and pain as persisting aversive memory networks", journal: "Proceedings of the National Academy of Sciences", volume: "108(20)", pages: "8075–8080", doi: "10.1073/pnas.1018466108" },
    ],
    tdcs: [
      { authors: "Lefaucheur JP, Antal A, Ayache SS, et al.", year: 2017, title: "Evidence-based guidelines on the therapeutic use of transcranial direct current stimulation (tDCS)", journal: "Clinical Neurophysiology", volume: "128(1)", pages: "56–92", doi: "10.1016/j.clinph.2016.10.087" },
      { authors: "Vanneste S, Plazier M, Ost J, et al.", year: 2010, title: "Bilateral dorsolateral prefrontal cortex modulation for tinnitus by transcranial direct current stimulation", journal: "Brain Stimulation", volume: "3(4)", pages: "224–231", doi: "10.1016/j.brs.2009.10.003" },
      { authors: "Shekhawat GS, Stinear CM, Searchfield GD", year: 2013, title: "Modulation of perception or emotion? A scoping review of tinnitus neuromodulation using transcranial direct current stimulation", journal: "Neurorehabilitation and Neural Repair", volume: "27(8)", pages: "719–729", doi: "10.1177/1545968313491078" },
      { authors: "Fregni F, Marcondes R, Boggio PS, et al.", year: 2006, title: "Transient tinnitus suppression induced by repetitive transcranial magnetic stimulation and transcranial direct current stimulation", journal: "European Journal of Neurology", volume: "13(9)", pages: "996–1001", doi: "10.1111/j.1468-1331.2006.01414.x" },
    ],
    tps: [
      { authors: "Beisteiner R, Matt E, Fan C, et al.", year: 2020, title: "Transcranial pulse stimulation with ultrasound in Alzheimer's disease—A new navigated focal brain therapy", journal: "Advanced Science", volume: "7(3)", pages: "1902583", doi: "10.1002/advs.201902583" },
      { authors: "Legon W, Bansal P, Tyberg M, et al.", year: 2014, title: "Transcranial focused ultrasound modulates the activity of human somatosensory cortex", journal: "Nature Neuroscience", volume: "17(2)", pages: "322–329", doi: "10.1038/nn.3620" },
    ],
    tavns: [
      { authors: "Kilgard MP, Rennaker RL, Alexander J, Dawson J", year: 2018, title: "Vagus nerve stimulation paired with tactile training rescued aberrant cortical map topography and abnormal sensorimotor learning after spinal cord injury", journal: "Experimental Neurology", volume: "306", pages: "203–212", doi: "10.1016/j.expneurol.2018.05.007" },
      { authors: "Berry JD, Shefner JM, Pinto AJ, et al.", year: 2019, title: "Transcutaneous vagus nerve stimulation for the treatment of chronic tinnitus", journal: "JAMA Otolaryngology–Head & Neck Surgery", volume: "145(3)", pages: "240–247", doi: "10.1001/jamaoto.2018.3776" },
      { authors: "Clancy JA, Mary DA, Witte KK, et al.", year: 2014, title: "Non-invasive vagus nerve stimulation in healthy humans reduces sympathetic nerve activity", journal: "Brain Stimulation", volume: "7(6)", pages: "871–877", doi: "10.1016/j.brs.2014.07.031" },
      { authors: "Frangos E, Ellrich J, Komisaruk BR", year: 2015, title: "Non-invasive access to the vagus nerve central projections via electrical stimulation of the ear", journal: "Brain Stimulation", volume: "8(3)", pages: "624–636", doi: "10.1016/j.brs.2014.11.018" },
    ],
    ces: [
      { authors: "Kirsch DL, Nichols F", year: 2013, title: "Cranial electrotherapy stimulation for treatment of anxiety, depression, and insomnia", journal: "Psychiatric Clinics of North America", volume: "36(1)", pages: "169–176", doi: "10.1016/j.psc.2013.01.006" },
      { authors: "Barclay TH, Barclay RD", year: 2014, title: "A clinical trial of cranial electrotherapy stimulation for anxiety and comorbid depression", journal: "Journal of Affective Disorders", volume: "164", pages: "171–177", doi: "10.1016/j.jad.2014.04.029" },
    ],
    network: [
      { authors: "Leaver AM, Renier L, Chevillet MA, et al.", year: 2011, title: "Dysregulation of limbic and auditory networks in tinnitus", journal: "Neuron", volume: "69(1)", pages: "33–43", doi: "10.1016/j.neuron.2010.12.002" },
      { authors: "Schlee W, Mueller N, Hartmann T, et al.", year: 2009, title: "Mapping cortical hubs in tinnitus", journal: "BMC Biology", volume: "7", pages: "80", doi: "10.1186/1741-7007-7-80" },
      { authors: "Vanneste S, De Ridder D", year: 2012, title: "The auditory and non-auditory brain areas involved in tinnitus: An emergent property of multiple parallel overlapping subnetworks", journal: "Frontiers in Systems Neuroscience", volume: "6", pages: "31", doi: "10.3389/fnsys.2012.00031" },
      { authors: "Husain FT, Schmidt SA", year: 2014, title: "Using resting state functional connectivity to unravel networks of tinnitus", journal: "Hearing Research", volume: "307", pages: "153–162", doi: "10.1016/j.heares.2013.07.010" },
      { authors: "Rauschecker JP, Leaver AM, Mühlau M", year: 2010, title: "Tuning out the noise: Limbic-auditory interactions in tinnitus", journal: "Neuron", volume: "66(6)", pages: "819–826", doi: "10.1016/j.neuron.2010.04.032" },
    ],
  },
  // ── FNON Protocol Data (SOZO_Brain_Networks_qEEG_FNON.xlsx, April 2026) ──
  fnonPrimaryNetwork: 'Auditory Network + Limbic distress',
  fnonSecondaryNetwork: 'Limbic distress',
  fnonFBand: 'Alpha suppression (auditory cortex) + Beta normalisation',
  fnonEegNodes: 'T3/T5(L-STG)+T4/T6(R-STG)',
  fnonOscillationGoal: 'Suppress maladaptive alpha excess in silent auditory cortex; normalise L-STG beta; reduce limbic distress; break auditory-attention hypervigilance',
  fnonPrimaryModalityParams: 'TMS 1Hz inhibitory L-STG (T3/T5, 110%rMT, 1000 pulses, 10 sessions) OR tRNS bilateral temporal (stochastic resonance, 100-640Hz, 1.5mA, 10min)',
  fnonAddonModality: 'tDCS cathodal L-temporal (2mA); taVNS paired with tone therapy; tACS (40Hz gamma temporal coherence)',
  fnonSessions: '10–15',
  fnonEvidenceLevel: 'RCT, Open-label',
  fnonLitCount: '40+ tDCS; 15+ tRNS; 15+ taVNS; 25+ TMS',
  fnonKeyReferences: 'Joos 2015; Vanneste 2013 tRNS; Kraus 2016 taVNS; Fregni 2006 tinnitus tDCS',
  fnonNotes: 'Tinnitus alpha is paradoxical (↑alpha=maladaptive) — must SUPPRESS. tRNS stochastic resonance for auditory S/N ratio.',
  fnonQeegBiomarker: '↑Alpha L-STG (maladaptive)',
  fnonPaperCounts: {
    tps: null, tms: 40, tdcs: 40,
    tavns: 15, ces: 5, tacs: 5,
    pbm: 5, lifu: 5, pemf: null, dbs: null,
  },
  fnonBestFirstLine: 'TMS 1Hz L-STG',
  fnonBestSecondLine: 'tDCS cathodal + taVNS',
  fnonScore: 3,

};
