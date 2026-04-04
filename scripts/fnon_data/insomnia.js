// SOZO FNON Clinical Protocol — Insomnia Disorder (Chronic Primary and Comorbid)
// Document A — Partners Tier

module.exports = {
  conditionFull: "Insomnia Disorder (Chronic Primary and Comorbid Insomnia)",
  conditionShort: "Insomnia",
  conditionSlug: "insomnia",
  documentNumber: "SOZO-FNON-INS-001",

  offLabelCoverText:
    "All non-invasive brain stimulation (NIBS) applications described in this protocol for Insomnia Disorder represent off-label use of CE-marked and FDA-cleared devices. The Newronika HDCkit, PlatoScience PlatoWork, NEUROLITH® TPS, and Soterix Medical taVNS are CE-marked for neurological rehabilitation and epilepsy indications respectively; none list insomnia as a primary indication. The Alpha-Stim AID (FDA-cleared for anxiety, depression, and insomnia) is the exception — Alpha-Stim CES is FDA-cleared for insomnia and represents the primary evidence-based NIBS component in this protocol. All other NIBS modalities (tDCS, TPS, taVNS) require off-label disclosure for insomnia application. The evidence base for CES in insomnia is Level B; tDCS and taVNS for insomnia is Level C. FNON protocols are adjunctive to Cognitive Behavioural Therapy for Insomnia (CBT-I), which retains Level A evidence as the gold-standard first-line treatment.",

  offLabelTable: [
    ["Device", "Cleared/Approved Indication", "Insomnia Off-Label/On-Label Application", "Evidence Level"],
    ["Alpha-Stim AID (CES)", "FDA-cleared: anxiety, depression, INSOMNIA", "Insomnia — ON-LABEL for Alpha-Stim AID; sleep onset facilitation", "Level B (FDA cleared; multiple RCTs)"],
    ["Soterix taVNS / auricular VNS", "Epilepsy (CE/FDA)", "Autonomic regulation, sleep-onset facilitation, circadian modulation", "Level C"],
    ["Newronika HDCkit / PlatoWork", "Neurological rehabilitation (CE)", "Frontal hyperarousal modulation, HPA axis normalisation", "Level C"],
    ["NEUROLITH® TPS", "Alzheimer's disease (CE)", "Prefrontal-hypothalamic sleep circuit, thalamo-cortical sleep gating", "Level C"],
  ],

  inclusionCriteria: [
    ["Chronic Insomnia Disorder per DSM-5 or ICSD-3: difficulty initiating or maintaining sleep, or early morning awakening, ≥3 nights/week, for ≥3 months, associated with significant distress or daytime impairment", "Sleep diary completed ≥2 weeks documenting SOL >30 min, WASO >30 min, or EMA ≥30 min before desired wake time", "ISI (Insomnia Severity Index) ≥15 (moderate to severe insomnia) at baseline", "Age 18–75 years"],
    ["Primary or comorbid insomnia (comorbid insomnia must have stable medical/psychiatric comorbidity; not attributable solely to untreated condition)", "Failed or incomplete response to CBT-I or currently enrolled in CBT-I (FNON is adjunctive, not standalone)", "Actigraphy or PSG if clinically indicated to rule out primary sleep disorder (obstructive sleep apnoea, restless legs syndrome, periodic limb movement disorder)", "No change in sleep medications for ≥4 weeks prior to protocol commencement"],
    ["Sleep physician or GP assessment confirming insomnia diagnosis and suitability for NIBS", "Adequate skin integrity at electrode sites", "Willingness to maintain sleep diary and actigraphy throughout protocol", "Baseline measures completed: ISI, PSQI, PHQ-9, GAD-7, ESS (Epworth Sleepiness Scale), Sleep Beliefs and Attitudes Questionnaire (DBAS-16)"],
    ["Stable employment/social schedule (irregular shift work may confound circadian outcomes; document)", "No severe underlying psychiatric disorder requiring priority separate management", "Willingness to engage with sleep hygiene programme alongside FNON protocol", "No active suicidal ideation"],
    ["Written informed consent with off-label disclosure for non-CES modalities", "Goals of treatment established (sleep onset, maintenance, early morning waking — identify dominant complaint)", "Partner/bedpartner interview if sleep-disorder components affect partner", "Circadian preference assessment (Horne-Ostberg MEQ if circadian phenotype suspected)"],
    ["No uncontrolled sleep-disruptive medical conditions (pain, nocturia, hot flushes not managed) — treat these first", "Caffeine and alcohol intake documented (both major sleep disruptors — quantify)", "Regular sleep schedule commitment discussed (irregular schedule is strong CBT-I contraindication)", "No active substance use disorder"],
    ["Physician review for secondary insomnia causes: pain, GORD, nocturia, thyroid dysfunction, anaemia — address modifiable causes concurrently", "Screen for restless legs syndrome (IRLS) and periodic limb movement disorder — separate specific management required", "Cardiac and respiratory assessment if taVNS indicated", "Realistic expectation counselling: CBT-I + FNON combination; not immediate effect; 4–6 weeks for meaningful change"],
  ],

  exclusionCriteria: [
    ["Untreated or undertreated obstructive sleep apnoea (OSA must be treated with CPAP/MAD before insomnia FNON — OSA is a primary sleep disorder requiring specific treatment)", "Untreated restless legs syndrome or periodic limb movement disorder (these are primary sleep disorders with specific pharmacological treatment — treat first)", "Narcolepsy or idiopathic hypersomnia (separate sleep disorder requiring specialist management)", "Circadian rhythm sleep-wake disorder (advanced/delayed sleep phase, non-24-hour) — requires specific chronotherapy/phototherapy"],
    ["Intracranial metal implants (DBS, cochlear implants, ferromagnetic clips)", "Cardiac pacemaker or implantable defibrillator", "Pregnancy or breastfeeding", "Active uncontrolled psychiatric disorder (psychosis, mania, severe depression) — treat psychiatric condition first before insomnia NIBS"],
    ["Active suicidal ideation", "Insomnia solely attributable to an unmanaged condition that should be treated (e.g., uncontrolled pain — treat pain first; uncontrolled PTSD — active PTSD protocol priority)", "Current use of hypnotic medications >5 nights/week (z-drugs, benzodiazepines) at high dose — taper supervised before adding NIBS; NIBS effectiveness reduced by GABAergic suppression", "Severe substance use disorder (alcohol, opioids — sleep disturbance managed through addiction treatment first)"],
    ["Known allergy or hypersensitivity to conductive gel or electrode materials", "Open wounds, skin conditions, or infections at electrode sites", "Uncontrolled seizure disorder", "History of malignant brain tumour"],
    ["Botulinum toxin injection to head/neck within 3 months", "Deep cervical vagus nerve stimulator in place", "Recent head trauma or new neurological symptoms requiring investigation", "Age <18 years (paediatric insomnia has distinct management and requires paediatric specialist)"],
    ["Severe hypotension (systolic <90 mmHg) that may be exacerbated by taVNS vagal effects", "Active significant cardiac arrhythmia", "Unable to provide informed consent", "Shift work disorder without willingness to modify schedule (irregular sleep-wake schedule undermines all insomnia treatment)"],
    ["Very high-dose benzodiazepine use (diazepam >30 mg equivalent daily) — withdrawal must be supervised before NIBS, not concurrent", "Severe obstructive lung disease with nocturnal desaturation (SpO2 <88% at night without supplemental oxygen)", "Sleep diary completion not feasible (cognitive impairment or unwillingness — CBT-I is diary-dependent)", "Clinician assessment: risk outweighs benefit"],
    ["Brain tumour or space-occupying lesion not previously excluded", "Active alcohol dependence (alcohol profoundly suppresses sleep architecture; address addiction first)", "Known paradoxical insomnia (sleep state misperception) — requires psychoeducational intervention before NIBS", "Refusal of CBT-I as concurrent treatment (FNON without CBT-I for insomnia has limited evidence basis)"],
  ],

  conditionsRequiringDiscussion: [
    ["Condition", "Clinical Consideration", "Recommended Action", "Protocol Adjustment"],
    ["Comorbid depression (insomnia most common symptom)", "Insomnia and depression bidirectional; neuroinflammatory and serotonergic overlap; insomnia precedes depression in 40% of cases", "PHQ-9; psychiatric review; treat depression alongside insomnia (both CBT-I and antidepressant may be indicated)", "Add anodal F3 tDCS (antidepressant component); taVNS anti-inflammatory; CES primary; may need 20-session protocol"],
    ["Comorbid anxiety (GAD, health anxiety, social anxiety)", "Hyperarousal model: anxiety maintains insomnia through cognitive and somatic arousal; GAD-7 ≥10 indicates significant anxiety comorbidity", "CBT-I with sleep restriction adapted; anxiety treatment concurrent; relaxation training", "Right DLPFC F4 anodal (anxiolytic); taVNS + CES primary anxiolytics; sleep restriction titration very cautious"],
    ["Comorbid chronic pain (pain-insomnia dyad)", "Bidirectional: pain disrupts sleep; sleep deprivation lowers pain threshold (central sensitisation); very common comorbidity", "Pain management optimised first; concurrent pain NIBS elements if needed; physiotherapy", "Add M1 anodal tDCS for pain component; taVNS NTS-PAG analgesic pathway; CES pain protocol elements"],
    ["Menopause-related insomnia", "Hot flushes, night sweats, and hormonal changes disrupt sleep architecture; vasomotor symptoms trigger arousal from sleep; HRT consideration", "Menopause clinic referral; HRT assessment; CBT-I adapted for menopause (CBTI-M)", "taVNS for hot flush reduction (hypothalamic modulation; emerging evidence); standard insomnia FNON + CES"],
    ["Insomnia in elderly (≥65 years)", "Circadian phase advance; reduced sleep duration; increased sleep fragmentation; polypharmacy risk; falls risk from sedating medications", "Reduce NIBS intensity to 1.0–1.5 mA (elderly brain); shorter sessions; very gradual titration; fall prevention reviewed", "Lower intensity CES and tDCS; taVNS primary (safest); avoid sedating evening tDCS if balance risk"],
    ["Insomnia following COVID-19 (post-COVID insomnia)", "COVID-19-related insomnia has neuroinflammatory and circadian components beyond standard insomnia; overlaps with Long COVID neurological phenotype", "Long COVID assessment; taVNS anti-inflammatory primary; standard insomnia protocol combined with Long COVID elements", "Integrate Long COVID FNON elements (taVNS anti-inflammatory, hippocampal if cognitive fog concurrent); see Long COVID protocol"],
    ["Psychophysiological insomnia (conditioned arousal)", "Classical conditioning of bed → arousal (Spielman model); most prevalent type in CBT-I populations; sleep restriction core treatment", "Sleep restriction therapy + stimulus control as CBT-I core; FNON amplifies the neuroplasticity for conditioned arousal extinction", "Standard insomnia FNON; emphasise CES in bed (during sleep opportunity) as deconditioning tool; cathodal frontal for arousal modulation"],
    ["Short sleep duration insomnia (objective short sleep)", "Subtype with physiological hyperarousal and EEG beta hyperactivation; higher cardiovascular and cognitive risk; more difficult to treat", "PSG/actigraphy to confirm short sleep; short sleep insomnia may require stronger intervention", "Cathodal frontal tDCS (reduce beta hyperarousal); taVNS HPA axis normalisation; highest CES dose; consider melatonin concurrent"],
    ["Insomnia with Paradoxical sleep state misperception", "Patient reports no sleep but objective sleep normal on PSG; cognitive distortion about sleep; anxiety about sleep", "PSG to demonstrate objective sleep; psychoeducation about sleep state misperception; CBT-I focus on catastrophising reduction", "taVNS + CES (reduce hyperarousal without targeting sleep architecture); cathodal frontal (reduce rumination); CBT-I catastrophising components"],
  ],

  overviewParagraph:
    "Insomnia Disorder — defined by DSM-5 and ICSD-3 as persistent difficulty with sleep initiation, maintenance, or early morning awakening, occurring ≥3 nights/week for ≥3 months, causing significant daytime distress or impairment — is the most prevalent sleep disorder globally, affecting 10–30% of adults with approximately 6–10% meeting full disorder criteria. Chronic insomnia is associated with substantial morbidity: 2–3× increased risk of depression, 1.4× increased risk of diabetes mellitus, elevated cardiovascular risk, cognitive impairment, and reduced quality of life. The neurobiological substrate of insomnia is now well-characterised as the 'hyperarousal model': persistent hyperactivation of the wake-promoting neural circuits — the ascending reticular activating system (ARAS), locus coeruleus (NE), dorsal raphe (5-HT), histaminergic hypothalamus, and orexinergic lateral hypothalamus — combined with reduced activity of the sleep-promoting ventrolateral preoptic area (VLPO), thalamic sleep spindle generation, and GABAergic cortical inhibition. EEG studies in chronic insomnia demonstrate elevated beta-band (15–35 Hz) activity during NREM sleep — a biomarker of cortical hyperarousal — alongside reduced sleep spindle density and reduced slow-wave sleep. The SOZO FNON insomnia protocol targets this hyperarousal network through CES (primary intervention — FDA-cleared for insomnia, promotes slow-wave sleep and delta entrainment), taVNS (autonomic and vagal parasympathetic restoration, HPA axis normalisation), and cathodal/inhibitory tDCS of frontal hyperarousal circuits, with TPS for thalamo-cortical sleep gating circuit enhancement.",

  fnonNetworkParagraph:
    "The FNON framework for insomnia is grounded in the 'Hyperarousal Network Dysregulation' model: insomnia is not merely a sleep deficit but a disorder of arousal-regulation circuits that fail to appropriately downregulate waking-state brain activity at sleep onset and during sleep. The Default Mode Network (DMN) and prefrontal self-referential circuits fail to deactivate at sleep onset in insomnia patients — EEG and fMRI studies show elevated DMN activity in pre-sleep and sleep-onset periods, manifesting as intrusive thoughts, rumination, and cognitive hyperarousal. The Salience Network (SN) is hyperactivated in insomnia, maintaining threat vigilance that prevents full cortical inhibition. The ascending noradrenergic (LC-NE), serotonergic (dorsal raphe), and orexinergic (lateral hypothalamus) wake-promoting systems remain excessively active during sleep opportunity periods, suppressing VLPO sleep-promoting GABA release. The thalamo-cortical sleep spindle generation system — dependent on reticular nucleus GABAergic oscillations — is disrupted, reducing the 12–14 Hz spindle density that normally gates sensory arousal during NREM sleep. The FNON approach: CES (primary — promotes delta and alpha entrainment, enhances slow-wave sleep); taVNS (vagal parasympathetic activation reduces LC-NE wake drive, normalises HPA axis cortisol rhythm); cathodal frontal tDCS (reduces prefrontal hyperarousal, facilitates DMN deactivation at sleep onset); TPS (thalamo-cortical sleep circuit modulation). All components are delivered pre-sleep or at sleep onset to align stimulation timing with the therapeutic target. This arousal-network dysregulation model is supported by Karabanov et al. 2023 (33 citations) and To et al. 2018 (113 citations).",

  networkDisorderParagraphs: [
    {
      network: "Default Mode Network (DMN)",
      paragraph:
        "The Default Mode Network in insomnia shows pathological failure to deactivate at sleep onset — the normal physiological process by which the brain transitions from task-positive (DMN-suppressed) waking to pre-sleep (DMN-active self-referential, memory consolidation) to unconscious sleep (DMN deactivated) is disrupted. Insomnia patients show elevated DMN activity during the sleep-onset period on fMRI, corresponding to the clinical phenomenon of cognitive hyperarousal: racing thoughts, inability to 'switch off,' intrusive worries, and mental hyperactivity at bedtime. The DMN-medial prefrontal cortex (mPFC) is particularly hyperactive in insomnia — generating the rumination and self-focused negative thoughts that characterise pre-sleep cognitive arousal. The DMN-amygdala functional connectivity is elevated in insomnia, amplifying emotionally valenced pre-sleep thoughts. FNON approach: cathodal Cz tDCS (dampens posterior midline DMN and pre-SMA arousal) and CES (promotes delta oscillatory entrainment that facilitates DMN deactivation at sleep onset)."
    },
    {
      network: "Central Executive Network (CEN)",
      paragraph:
        "The Central Executive Network (CEN) in insomnia shows a paradoxical pattern: during wake periods, CEN function is reduced (cognitive impairment from sleep deprivation — the daytime consequence); during pre-sleep periods, CEN is excessively active, generating the executive cognitive arousal of bedtime worry, planning, and problem-solving that prevents sleep onset. This daytime CEN hypofunction + nocturnal CEN hyperfunction is the cognitive dimension of the hyperarousal model. Paradoxically, the same prefrontal circuits that are too active at night (generating worry) are too inactive during the day (producing the cognitive impairment of insomnia). Anodal DLPFC tDCS (F3) delivered in the daytime context improves daytime cognitive function and, through normalising the CEN excitability cycle, may reduce nocturnal hyperactivation. However, the primary FNON insomnia strategy is NOT to upregulate the CEN at night — instead, cathodal/inhibitory approaches are used pre-sleep."
    },
    {
      network: "Salience Network (SN)",
      paragraph:
        "The Salience Network in insomnia — centred on the anterior insula and anterior cingulate cortex — is chronically hyperactivated, maintaining a state of physiological vigilance and threat monitoring that is fundamentally incompatible with sleep. The anterior insula mediates interoceptive monitoring (body awareness, heart rate perception, respiratory awareness), and elevated insula activity in insomnia produces the 'body noise' phenomenon: heightened awareness of breathing, heartbeat, and bodily sensations that insomnia patients report as keeping them awake. The ACC generates the conflict-monitoring and error-signalling that maintains cognitive vigilance. Insomnia patients show higher resting SN functional connectivity compared to good sleepers on resting-state fMRI. taVNS directly modulates the SN via NTS projections to the insula and ACC, reducing the vigilance-maintenance signal that prevents sleep onset. Combined taVNS + CES provides both neural (NTS-SN) and autonomic (vagal parasympathetic) calming."
    },
    {
      network: "Sensorimotor Network (SMN)",
      paragraph:
        "The Sensorimotor Network in insomnia is relevant through the somatic hyperarousal dimension: elevated muscle tension, increased body temperature, increased heart rate, and somatic restlessness that characterise the physiological arousal component of insomnia. Many insomnia patients report leg discomfort (distinct from restless legs syndrome but sharing some features), muscle tension headache, and whole-body restlessness that prevents sleep. The primary motor cortex and SMA show elevated resting state activity in psychophysiological insomnia. Progressive muscle relaxation (PMR) and body scan techniques — used in CBT-I — directly target this somatic SMN hyperarousal. Cathodal SMA tDCS (Cz) may complement PMR by reducing the cortical motor arousal contributing to the somatic component of insomnia hyperarousal."
    },
    {
      network: "Limbic Network",
      paragraph:
        "The Limbic Network in insomnia — particularly the amygdala, hippocampus, and anterior cingulate — shows hyperactivation that drives the emotional dimension of cognitive hyperarousal: worry, fear of not sleeping, catastrophising about consequences of sleep loss, and conditioned arousal responses. The amygdala is hyperresponsive to sleep-related stimuli in psychophysiological insomnia (conditioned arousal model): the bedroom, bedtime routine, and pre-sleep period trigger amygdala fear responses through classical conditioning (Spielman 3P model: predisposing, precipitating, perpetuating factors). Fear of not sleeping is conditioned to the sleep environment itself, producing a physiological arousal response at bedtime — the mirror image of Pavlovian sleep-onset conditioning disrupted. taVNS reduces amygdala hyperactivation via NTS-LC pathways, potentially facilitating extinction of the conditioned arousal to the sleep environment that CBT-I stimulus control seeks to achieve."
    },
    {
      network: "Attention Network",
      paragraph:
        "The Attention Network in insomnia is characterised by attentional bias toward sleep-related threat stimuli: insomnia patients show faster detection and longer dwell time on sleep-related threatening words (e.g., 'awake', 'tired', 'exhausted') on attentional tasks, and show selective attention to clock-checking, body sensations, and sleep-threatening environmental cues. This threat-monitoring attention bias maintains the hyperarousal state and perpetuates the insomnia cycle. The right hemisphere attention network (IFG, IPS, FEF) and ACC maintain vigilance for sleep-disrupting stimuli. Hypervigilance monitoring for sleep-related threat depletes the attentional resources needed for normal daytime functioning, contributing to the daytime impairment of chronic insomnia. FNON attention targets: taVNS reduces LC-NE hypervigilance; mindfulness-based CBT-I techniques reduce attentional bias with CES supporting reduced arousal during practice."
    },
  ],

  networkCitationKeys: [
    { authors: "Karabanov et al.", year: 2023, citations: 33, title: "Neuromodulation of Neural Oscillations in Health and Disease", doi: "" },
    { authors: "To et al.", year: 2018, citations: 113, title: "Changing Brain Networks Through Non-invasive Neuromodulation", doi: "" },
  ],
  fnonEvidenceStrength: "Moderate",

  pathophysiologyText:
    "Insomnia neurophysiology follows the established Spielman 3P model (predisposing, precipitating, perpetuating factors) underpinned by Hyperarousal Theory (Bonnet & Arand; Riemann; Perlis). Predisposing factors include genetic vulnerability to hyperarousal (familial insomnia risk, elevated physiological arousal baseline), trait anxiety, and female sex (2× prevalence). Precipitating factors trigger the acute episode (life stressor, illness, shift work). Perpetuating factors — cognitive (catastrophising, dysfunctional beliefs about sleep) and behavioural (extended time in bed, daytime napping, caffeine compensation) — maintain the insomnia beyond the precipitating event through: (1) Cortical hyperarousal — EEG beta power during NREM sleep is elevated in chronic insomnia, directly measuring cortical 'wakefulness' that intrudes into sleep; (2) HPA axis dysregulation — elevated late-day cortisol and morning ACTH in insomnia, reflecting altered circadian cortisol rhythm that promotes evening/nocturnal arousal; (3) Sympathetic over-activation — elevated heart rate, reduced heart rate variability (HRV), and elevated norepinephrine in insomnia; (4) Structural/functional brain changes — reduced hippocampal volume, reduced prefrontal thickness, and elevated amygdala connectivity documented in chronic insomnia; (5) Neuroinflammatory markers — elevated IL-6, TNF-α, and CRP in chronic insomnia, linking sleep loss to cardiovascular and metabolic disease risk. The FNON therapeutic targets address mechanisms (1)–(5): CES entrains delta slow-wave sleep oscillations to reduce EEG beta hyperarousal; taVNS reduces HPA cortisol excess via NTS-hypothalamic modulation and reduces sympathetic over-activation; cathodal frontal tDCS reduces prefrontal cognitive hyperarousal; and taVNS anti-inflammatory pathway addresses neuroinflammatory perpetuation.",

  cardinalSymptoms: [
    ["Domain", "Primary Symptoms", "Network Basis", "FNON Target"],
    ["Sleep Onset Insomnia", "SOL >30 min; inability to 'switch off'; racing thoughts; cognitive hyperarousal at bedtime; lying awake for 1–2+ hours", "DMN failure to deactivate; mPFC hyperactivity; SN vigilance; LC-NE wake drive persistence; cognitive arousal loop", "CES primary (delta entrainment, deactivation facilitation); taVNS (NTS→LC→NE reduction at sleep onset); cathodal Fz/Cz"],
    ["Sleep Maintenance Insomnia", "WASO >30 min; frequent awakenings; arousal from light sleep (NREM1/2); difficulty returning to sleep after waking; reduced NREM3 slow-wave", "Thalamic sleep spindle deficit (reduced sensory gating); SN threat monitoring during NREM; amygdala conditioned arousal; reduced VLPO GABA activity", "CES (enhances slow-wave sleep delta power, sleep spindle density); taVNS (VLPO activation via NTS pathway); TPS thalamo-cortical sleep circuit"],
    ["Early Morning Awakening", "Awakening ≥1 hour before desired wake time; inability to return to sleep; associated with depression; circadian phase advance", "Circadian phase advance; elevated morning cortisol; reduced REM sleep in late sleep cycles; LC-NE morning surge", "CES circadian protocol; taVNS (NTS→hypothalamus circadian modulation); anodal F3 tDCS (daytime depression comorbidity)"],
    ["Daytime Fatigue / Sleepiness", "Tiredness despite prolonged time in bed; cognitive impairment; reduced concentration; psychomotor slowing; paradox: cannot sleep at night but may nap in day", "CEN hypoactivation from sleep deprivation; prefrontal grey matter changes in chronic insomnia; hypocretin/orexin system disruption", "Daytime tDCS anodal DLPFC (cognitive function); NOT sedative NIBS during day; taVNS NE restoration daytime"],
    ["Cognitive Hyperarousal (Worry / Rumination)", "Bedtime worry; negative automatic thoughts about sleep; catastrophising consequences of poor sleep; 'performance anxiety' about sleeping", "DMN-mPFC hyperactivity (rumination); amygdala fear conditioning to sleep cues; frontal cognitive arousal; dysfunctional sleep beliefs", "Cathodal Fz tDCS (mPFC hyperarousal suppression); taVNS (amygdala inhibition); CES + CBT-I cognitive restructuring concurrent"],
    ["Somatic / Physiological Hyperarousal", "Elevated heart rate at bedtime; muscle tension; body temperature elevation; difficulty 'switching off' physically; restlessness", "SN anterior insula interoception hyperactivation; LC-NE sympathetic over-activation; SMA motor cortex arousal; autonomic sympathovagal imbalance", "taVNS primary (vagal parasympathetic vs. sympathetic balance); CES (tonic ANS calming); cathodal Cz SMA arousal reduction"],
    ["Conditioned Arousal (Bed = Arousal)", "Bedroom and bedtime routine trigger wakefulness; feel sleepier anywhere than in own bed; stimulus control failure", "Classical conditioning of bed/bedroom to waking state; amygdala conditioned fear response to sleep environment; Pavlovian arousal conditioned response", "taVNS + CES in bed environment (deconditioning); stimulus control CBT-I concurrent; CES use in bed promotes new 'bed = calm' association"],
    ["Sleep-Related Anxiety", "Fear of not sleeping; hypervigilance to sleep quality; clock-watching; anticipatory anxiety about next night; health anxiety about insomnia consequences", "Amygdala threat conditioning to sleep stimuli; SN hyperactivation (anticipatory anxiety); HPA axis cortisol excess; right hemisphere anxiety network", "Right DLPFC anodal F4 (anxiolytic); taVNS bilateral (amygdala inhibition); CES pre-sleep (anxiety reduction before sleep opportunity)"],
    ["Non-Restorative Sleep", "Waking feeling unrefreshed despite adequate duration; not rested; subjective poor sleep quality; dissociation between subjective and objective sleep", "Slow-wave sleep deficit (NREM3 reduction); sleep spindle density reduction; EEG delta power reduction; subjective-objective sleep discrepancy", "CES primary (slow-wave sleep enhancement — delta entrainment); TPS thalamo-cortical sleep spindle circuit; taVNS VLPO activation"],
  ],

  standardGuidelinesText: [
    "Insomnia management follows NICE guideline NG215 (2022), the European Insomnia Guideline (Riemann 2017), and the American Academy of Sleep Medicine (AASM) Clinical Practice Guidelines. Cognitive Behavioural Therapy for Insomnia (CBT-I) is the first-line treatment with Level A evidence and is recommended before pharmacological treatment. NICE NG215 recommends CBT-I as first-line for adults of all ages and explicitly states that CBT-I should be offered before medication.",
    "CBT-I components with Level A evidence: sleep restriction therapy (limiting time in bed to actual sleep time to build sleep pressure); stimulus control (bed/bedroom for sleep only; out of bed if awake >20 min); sleep hygiene education; cognitive therapy (addressing dysfunctional beliefs about sleep — DBAS-16); relaxation techniques (progressive muscle relaxation, guided imagery). Group CBT-I and digital CBT-I (dCBT-I — Sleepio, SHUTi, Daylight) have Level A evidence equivalent to individual therapy.",
    "Pharmacological treatment: NICE NG215 recommends short-term (maximum 2–4 weeks) use of hypnotics only when CBT-I has failed or is unavailable. Z-drugs (zaleplon, zolpidem, zopiclone) are short-term only; dependency risk is significant. Benzodiazepines (temazepam, nitrazepam) are not recommended for new prescriptions. Melatonin (Circadin 2 mg) is licensed for short-term insomnia in adults ≥55 years (European) and long-term for insomnia not associated with sleep maintenance. Low-dose doxepin (6 mg — Silenor in USA) is FDA-approved specifically for sleep maintenance insomnia. Daridorexant (Quviviq) and lemborexant — dual orexin receptor antagonists (DORAs) — are approved for insomnia with Level A evidence and a favourable safety profile vs. benzodiazepines; suvorexant (Belsomra) — also DORA — is FDA-approved.",
    "Sleep hygiene: consistent sleep-wake schedule (including weekends); bright light exposure in morning; dark, quiet, cool bedroom; no screens 1 hour before bed; limit caffeine after noon; moderate exercise (not within 2 hours of bedtime); limit alcohol (worsens sleep architecture despite initial sedation). NICE NG215 emphasises sleep hygiene is necessary but insufficient alone for chronic insomnia.",
    "Melatonin: Circadin 2 mg (prolonged-release) recommended for over-55s by NICE/EMA for insomnia; unlicensed lower-dose immediate-release melatonin widely used for circadian phase disorders; high-dose (5–10 mg) melatonin not recommended over 2 mg. Melatonin concurrent with FNON protocol: no interaction with NIBS; recommended for circadian component of insomnia.",
    "NIBS for insomnia: Alpha-Stim AID (CES) is FDA-cleared for insomnia — the strongest evidence base among NIBS for insomnia (Level B across multiple RCTs). Transcranial alternating current stimulation (tACS) at 0.75 Hz (slow oscillation frequency) has Level B evidence for enhancing slow-wave sleep (Marshall 2006, Science). tDCS for insomnia has Level C evidence; cathodal frontal tDCS shows some sleep-promoting effects. taVNS for insomnia has theoretical rationale through HPA axis and autonomic mechanisms with Level C evidence. FNON integrates these with the CBT-I gold standard.",
    "Mind-body interventions: Mindfulness-based therapy for insomnia (MBTI, adapted from MBSR) has Level B evidence. Yoga and tai chi for insomnia have Level B evidence in elderly populations. Acupuncture has Level C evidence for insomnia (heterogeneous studies). Exercise (moderate aerobic, 150 min/week) has Level B evidence for insomnia improvement.",
  ],

  fnonFrameworkParagraph:
    "The SOZO FNON framework for insomnia is the 'Hyperarousal Dampening with Sleep Architecture Enhancement' (HDSAE) model: insomnia requires simultaneous reduction of hyperarousal network activation and enhancement of sleep-promoting circuit activity — two parallel processes that must occur together for sleep onset and maintenance. CES is the anchor modality: FDA-cleared for insomnia, CES promotes slow-wave sleep (SWS) by entraining the thalamo-cortical delta oscillatory system (0.5–4 Hz), enhancing slow-wave sleep depth and duration, and reducing EEG beta activity during NREM. taVNS complements CES by reducing autonomic sympathovagal imbalance — the physiological dimension of hyperarousal — via NTS activation of vagal parasympathetic tone, HPA axis normalisation through NTS-hypothalamic projections, and LC-NE reduction of wake drive. Cathodal frontal tDCS (optional, pre-sleep) reduces the prefrontal/DMN cognitive hyperarousal that is the most distressing manifestation of insomnia. TPS offers thalamo-cortical circuit enhancement for sleep spindle generation and thalamic sensory gating. The S-O-Z-O sequence for insomnia is fundamentally different from wake-state conditions: Stabilise (taVNS 15 min pre-sleep — autonomic calming); Optimise (cathodal frontal tDCS 20 min — reduce cognitive hyperarousal); Zone (TPS thalamo-cortical — once-weekly deeper circuit targeting); Outcome (CES 60 min during sleep opportunity — primary sleep-promoting intervention at the time of sleep). Timing is critical: all insomnia FNON is delivered in the 1–2 hours before intended sleep time, not during daytime, to align with the therapeutic target.",

  keyBrainRegions: [
    ["Brain Region", "Function", "Insomnia Pathology", "FNON Intervention"],
    ["Medial Prefrontal Cortex (mPFC)", "DMN hub; self-referential processing; rumination; default-mode activation; emotion regulation; pre-sleep thought generation", "Failure to deactivate at sleep onset; mPFC hyperactivity generates pre-sleep rumination and worry; elevated mPFC-amygdala connectivity at bedtime", "Cathodal tDCS Fz (mPFC inhibition — reduce pre-sleep rumination); CES posterior midline normalisation; CBT-I cognitive restructuring concurrent"],
    ["Supplementary Motor Area (SMA) / Pre-SMA", "Motor preparation; motor arousal; movement intention; restlessness; pre-sleep sensorimotor activity", "SMA/pre-SMA elevated activity contributes to somatic restlessness and motor arousal at bedtime; pre-sleep SMA overactivation", "Cathodal tDCS Cz (preSMA inhibition — reduce somatic motor arousal); cathodal Cz is the primary FNON tDCS insomnia montage"],
    ["Thalamus (Reticular Nucleus / Sleep Spindle Generator)", "Sleep spindle generation (12–14 Hz); thalamo-cortical sensory gating during NREM; relay inhibition; circadian integration", "Reduced sleep spindle density in chronic insomnia; thalamic reticular nucleus GABAergic inhibition deficit; inadequate sensory gating allows arousal stimuli to wake patient", "TPS thalamo-cortical circuit (indirect via cortical targets); CES delta entrainment promotes thalamo-cortical slow oscillation; taVNS thalamocortical normalisation"],
    ["Locus Coeruleus (LC)", "Norepinephrine (NE) source; arousal system; wake promotion; sleep-wake switching; stress response; hyper-alert state mediator", "LC-NE hyperactivation in insomnia maintains wake drive at sleep onset; elevated NE at night — direct measure of physiological hyperarousal; CRH-LC-NE axis in HPA dysregulation", "taVNS (NTS→LC pathway — primary mechanism: reduces LC-NE hyperactivation at sleep onset; most direct FNON insomnia mechanism)"],
    ["Ventrolateral Preoptic Area (VLPO)", "Sleep-promoting GABAergic nucleus; inhibits wake-promoting systems (LC, TMN, DRN, ORX); flip-flop sleep-wake switch; temperature-sensitive", "VLPO reduced activity in insomnia; impaired VLPO inhibition of LC-NE and orexin wake systems; sleep-wake switch fails to flip to sleep mode", "taVNS NTS-VLPO activation (NTS has direct projections to hypothalamic sleep nuclei including VLPO — major FNON mechanism); CES promotes VLPO-delta oscillation"],
    ["Hypothalamus (SCN, Lateral Hypothalamus, Dorsomedial)", "Circadian pacemaker (SCN); orexin/hypocretin wake drive (lateral); HPA axis (dorsomedial); sleep-wake scheduling; cortisol circadian rhythm", "SCN circadian dysregulation in some insomnia subtypes; orexin over-activation maintaining wake drive; elevated late-day cortisol; hypothalamic-pituitary-adrenal (HPA) axis hyperactivation", "taVNS (NTS→hypothalamic projections — reduces HPA cortisol excess; modulates SCN circadian function); CES circadian normalisation"],
    ["Amygdala", "Fear conditioning; threat appraisal; emotional memory; conditioned arousal responses; sleep-related anxiety", "Amygdala hyperactivation in insomnia at bedtime; conditioned fear response to sleep environment (psychophysiological insomnia model); elevated amygdala-mPFC connectivity pre-sleep", "taVNS (NTS→LC→amygdala inhibition — primary amygdala target); CES (tonic ANS calm reduces amygdala hyperactivation); stimulus control CBT-I (extinction of conditioned arousal)"],
    ["Anterior Insula", "Interoceptive body awareness; SN hub; autonomic monitoring; somatic hyperarousal detection", "Elevated anterior insula activity in insomnia contributes to somatic hyperarousal awareness: heartbeat awareness, breathing awareness, body temperature awareness that keeps patients awake", "taVNS (NTS→insula modulation — reduces interoceptive hyperarousal); CES tonic ANS calming"],
    ["Anterior Cingulate Cortex (ACC)", "Effort monitoring; conflict detection; sleep-wake conflict; arousal-sleep transition gating; HPA axis interface", "ACC hyperactivation in insomnia maintains conflict between wanting to sleep and physiological arousal preventing it; ACC sleep-wake conflict gating failure", "taVNS (NTS→ACC pathway); cathodal Fz includes ACC-adjacent; relaxation response concurrent with NIBS"],
  ],

  additionalBrainStructures: [
    ["Structure", "Insomnia-Specific Role", "Clinical Relevance", "FNON Consideration"],
    ["Dorsal Raphe Nucleus (DRN)", "Serotonin (5-HT) source; sleep-wake modulation; mood; circadian; wake-promoting in daytime, sleep-facilitating at night", "5-HT circadian disruption in insomnia; DRN hyperactivity at sleep onset; serotonergic dysfunction links insomnia and depression", "taVNS serotonergic pathway (NTS→dorsal raphe); SSRIs complement taVNS at DRN level; melatonin concurrent (serotonin precursor pathway)"],
    ["Tuberomammillary Nucleus (TMN)", "Histamine (HA) source; wake promotion; arousal; antihistamine sedation mechanism", "TMN hyperactivation in insomnia; H1 receptor antagonism is mechanism of first-generation antihistamine sedation (diphenhydramine)", "taVNS indirectly modulates TMN via NTS-hypothalamic pathway; antihistamines contraindicated long-term (tolerance, cognitive effects)"],
    ["Lateral Hypothalamus (Orexin/Hypocretin Neurons)", "Orexin/hypocretin neurons: wake drive stabilisation; arousal; feeding; reward; DORAs block these for insomnia treatment", "Orexin over-activation in insomnia; DORAs (daridorexant, lemborexant, suvorexant) block orexin for sleep; loss in narcolepsy causes excessive sleepiness", "taVNS modulates hypothalamic function indirectly; concurrent DORA medication is complementary to taVNS for insomnia (different mechanisms)"],
    ["Hippocampus", "Memory consolidation during sleep (NREM slow oscillation–spindle–ripple coupling); spatial memory; emotional memory", "Hippocampal volume reduction in chronic insomnia (sleep loss→reduced neurogenesis); hippocampal-cortical memory consolidation impaired by insomnia", "CES promotes slow-wave sleep which drives hippocampal SWRs for memory consolidation; taVNS BDNF induction supports hippocampal neurogenesis; TPS hippocampal (if cognitive impairment comorbid)"],
    ["Pineal Gland", "Melatonin synthesis (converts 5-HT→N-acetylserotonin→melatonin; driven by SCN); circadian sleep-onset signal", "Melatonin onset timing disrupted in insomnia (DLMO delayed or blunted); light exposure history affects melatonin synthesis", "taVNS modulates sympathetic melatonin-synthesis pathway via NTS; melatonin concurrent with evening FNON protocol; light therapy for circadian phase disorders"],
    ["Cerebral Cortex (Slow Oscillation Generator)", "SWS slow oscillations (< 1 Hz) generated by UP/DOWN states in cortical neurons; neocortical origin; propagates to thalamus for spindle coupling", "Reduced slow oscillation amplitude and delta power in insomnia; cortical slow oscillation deficit drives non-restorative sleep", "CES 0.5 Hz and 0.75–1.0 Hz stimulation directly entrains cortical slow oscillations (Marshall 2006); TPS cortical slow oscillation enhancement"],
    ["Brainstem Reticular Formation (ARAS)", "Ascending reticular activating system; arousal generation; wake promotion; multimodal sensory alerting; projects to thalamus and cortex", "ARAS hyper-activation in insomnia maintains cortical arousal; EEG desynchronisation as neurophysiological signature of ARAS-driven cortical arousal", "taVNS modulates brainstem reticular formation via NTS; CES thalamo-cortical delta entrainment competes with ARAS-driven desynchronisation"],
  ],

  keyFunctionalNetworks: [
    ["Network", "Key Nodes", "Insomnia Dysfunction Pattern", "NIBS Modality", "Expected Outcome"],
    ["Default Mode Network (DMN)", "mPFC, PCC, IPL, hippocampus", "Failure to deactivate at sleep onset; mPFC pre-sleep rumination; DMN-amygdala hyperconnectivity at bedtime; default experience is intrusive thought", "Cathodal Fz tDCS (mPFC inhibition); CES (DMN delta entrainment); cathodal Cz (pre-SMA); CBT-I cognitive restructuring concurrent", "Reduced pre-sleep intrusive thoughts; DBAS-16 improvement; ISI cognitive component reduction"],
    ["Salience Network (SN)", "Anterior insula, ACC, amygdala, thalamus", "Hyperactivation maintaining threat vigilance at bedtime; somatic hyperarousal monitoring; sleep-incompatible interoceptive monitoring", "taVNS (primary SN modulator via NTS); CES tonic ANS calm; cathodal Cz/Fz; relaxation training concurrent", "Reduced somatic arousal; HRV improvement; ISI sleep anxiety subscale; physiological arousal measures (HR, SC)"],
    ["Autonomic Network (ANS)", "NTS, hypothalamus (SCN, VLPO, DMH), LC, vagal efferents", "Sympathovagal imbalance; reduced HRV; elevated sympathetic drive; HPA cortisol excess; reduced vagal tone; VLPO inhibition failure", "taVNS primary (vagal parasympathetic restoration; NTS-VLPO; NTS-hypothalamic HPA normalisation)", "HRV RMSSD improvement; salivary cortisol evening reduction; sleep onset latency improvement; physiological arousal normalisation"],
    ["Thalamo-Cortical Sleep Circuit", "Thalamic reticular nucleus, MGB, sleep spindle relay, cortical slow oscillation generator", "Reduced sleep spindle density; inadequate thalamic sensory gating; insufficient slow-wave sleep (NREM3); reduced SWS delta power", "CES (primary — slow-wave delta entrainment; spindle enhancement); TPS thalamo-cortical circuit; taVNS NTS-thalamic projections", "PSG/actigraphy slow-wave sleep duration increase; sleep spindle density improvement; PSQI sleep quality"],
    ["Limbic Network", "Amygdala, hippocampus, OFC, ACC", "Conditioned amygdala arousal to sleep environment; hippocampal fear memory for insomnia; OFC aversive sleep association", "taVNS (amygdala inhibition primary); CES anxiolytic; stimulus control CBT-I (extinction concurrent); TPS hippocampal (cognitive comorbidity)", "PSQI; ISI; conditioned arousal reduction (sleep efficiency improvement in own bed vs. other environments)"],
    ["Circadian Network", "SCN, pineal, hypothalamus, LC, retinal photoreceptors, peripheral clocks", "SCN-LC circadian desynchrony; melatonin onset delay; circadian phase disruption by light/schedule irregularity", "taVNS (NTS→SCN circadian modulation); CES evening entrainment; morning bright light therapy concurrent; melatonin concurrent", "DLMO advance (salivary melatonin); circadian alignment improvement; morning function improvement"],
    ["Frontal Inhibitory Network", "mPFC, DLPFC, ACC, orbitofrontal cortex", "Pre-sleep frontal hyperarousal — the 'racing mind'; prefrontal cognitive rumination; frontal-amygdala dysregulation; frontal lobe grey matter thinning in chronic insomnia", "Cathodal Fz (mPFC) + cathodal Cz (preSMA) pre-sleep; CES; taVNS concurrent; CBT-I sleep restriction therapy", "Pre-sleep arousal scale (PSAS); Glasgow Sleep Effort Scale (GSES); cognitive arousal reduction before sleep"],
  ],

  networkAbnormalities:
    "Insomnia network abnormalities are dominated by the EEG biomarker of cortical hyperarousal: elevated beta band (15–35 Hz) power during all sleep stages — NREM1, NREM2, NREM3, and REM — compared to good sleepers. This beta intrusion into NREM sleep is analogous to wakefulness neural activity persisting through sleep, reflecting incomplete cortical inhibition. Simultaneously, delta power (0.5–4 Hz) — the hallmark of slow-wave sleep depth and restorative quality — is reduced in chronic insomnia, particularly during NREM3. Sleep spindle density (12–14 Hz) is reduced in insomnia, reflecting thalamic reticular nucleus GABAergic inhibition insufficiency. Functional MRI reveals: elevated DMN activity during pre-sleep period; elevated amygdala resting-state functional connectivity; and increased connectivity between sensory cortex and SN. The CES primary mechanism of action directly addresses the core EEG insomnia biomarkers: 0.5 Hz CES entrains cortical slow oscillations (increasing delta power); tACS at sleep spindle frequency (12–14 Hz) may enhance spindle density (Marshall 2006); and CES-induced changes in cortisol, norepinephrine, and serotonin levels address the neurochemical hyperarousal substrate.",

  conceptualFramework:
    "The SOZO FNON conceptual framework for insomnia is 'Pre-Sleep Hyperarousal Suppression with Sleep Architecture Enhancement' (PHSSAE): insomnia requires two simultaneous interventions — (1) suppressing the hyperarousal network states that prevent sleep onset (cognitive, somatic, and autonomic hyperarousal); and (2) actively enhancing sleep-promoting oscillatory mechanisms (delta slow-wave entrainment, sleep spindle generation, thalamo-cortical inhibitory gating). These two processes correspond to the two-component FNON approach: the inhibitory components (cathodal frontal tDCS, taVNS SN/LC modulation) address (1); the sleep-architecture-enhancing component (CES delta entrainment) addresses (2). The S-O-Z-O sequence for insomnia is timing-sensitive: all FNON is delivered in the evening/pre-sleep context. Stabilise (taVNS 15 min — autonomic calming, LC-NE reduction, amygdala inhibition — begins 2 hours before sleep); Optimise (cathodal Fz/Cz tDCS 20 min — DMN/mPFC/preSMA inhibition — begins 1 hour before sleep); Zone (TPS thalamo-cortical once-weekly — deeper circuit modulation, not before sleep); Outcome (CES 60 min — slow-wave delta entrainment — during sleep opportunity, concurrent with attempting sleep or in the 30 min immediately before). CBT-I is non-negotiable alongside FNON — the cognitive and behavioural perpetuating factors of insomnia (dysfunctional beliefs, extended time in bed, daytime napping, stimulus control failure) must be addressed behaviourally; FNON reduces the neurophysiological barriers to CBT-I working.",

  clinicalPhenotypes: [
    ["Phenotype", "Core Feature", "Network Priority"],
    ["Sleep Onset Insomnia (SOI)", "Primary complaint: difficulty falling asleep; SOL >30 min consistently; pre-sleep cognitive hyperarousal; 'racing mind'", "DMN (mPFC hyperactivation at bedtime); SN; CES primary; taVNS; cathodal Fz"],
    ["Sleep Maintenance Insomnia (SMI)", "Primary complaint: frequent awakenings; WASO >30 min; light sleep; reduced NREM3; non-restorative", "Thalamo-cortical sleep spindle/gating; SN night monitoring; CES primary (SWS enhancement); TPS thalamo-cortical"],
    ["Early Morning Awakening (EMA)", "Waking ≥1 hour early; cannot return to sleep; often depression comorbid; circadian phase advance; morning cortisol excess", "Circadian network (SCN, LC, cortisol); Limbic (depression comorbidity); anodal F3 tDCS; taVNS HPA; melatonin concurrent"],
    ["Psychophysiological Insomnia (PI)", "Conditioned arousal to sleep environment; more anxious in own bed than elsewhere; Spielman 3P model; strong perpetuating factor", "Limbic (conditioned amygdala); SN; stimulus control CBT-I concurrent essential; taVNS amygdala deconditioning"],
    ["Short Sleep Duration Insomnia (objective)", "ISI elevated + objective short sleep (PSG/actigraphy <6h); beta EEG hyperarousal dominant; higher cardiometabolic risk subtype", "EEG beta hyperarousal; CES high-dose (increase delta, reduce beta); cathodal frontal; taVNS maximum dose; melatonin concurrent"],
    ["Comorbid Insomnia-Depression (Bidirectional)", "Insomnia and depression comorbid; either may be primary; HADS depression ≥8; early morning awakening + depression markers", "Limbic + CEN (F3 anodal tDCS antidepressant); taVNS anti-inflammatory; CES; combined insomnia + depression protocol"],
    ["Comorbid Insomnia-Anxiety", "GAD-7 ≥8; sleep anxiety dominant; cognitive arousal driven by generalised worry; DBAS-16 anxiety subscale elevated", "SN + Limbic; right DLPFC F4 anxiolytic anodal; taVNS + CES primary anxiolytics; CBT-I + GAD treatment concurrent"],
    ["Menopause-Related Insomnia", "Hot flushes/night sweats trigger awakening; hormonal circadian disruption; vasomotor symptoms; typically SMI subtype", "SN (vasomotor); Limbic; taVNS for hot flush hypothalamic modulation; CES; standard insomnia protocol + HRT concurrent"],
    ["Chronic Treatment-Resistant Insomnia", "Failed CBT-I and pharmacological treatment; ≥2 years duration; significant quality of life impact; multiple perpetuating factors", "Multi-network; highest-dose FNON; taVNS maximum + CES maximum; TPS thalamo-cortical; intensive CBT-I restart"],
  ],

  symptomNetworkMapping: [
    ["Symptom", "Primary Network", "Key Nodes", "tDCS", "taVNS/CES"],
    ["Pre-sleep cognitive hyperarousal (racing mind)", "DMN + Frontal", "mPFC, ACC, DLPFC, amygdala", "Cathodal Fz (mPFC inhibition, 1.0–1.5 mA, pre-sleep)", "taVNS 15 min pre-sleep + CES concurrent"],
    ["Pre-sleep somatic hyperarousal (body restlessness)", "SN + SMN", "Anterior insula, SMA, LC", "Cathodal Cz (preSMA inhibition, 1.0–1.5 mA) or cathodal Fz/Cz combined", "taVNS primary (vagal parasympathetic) + CES ANS calming"],
    ["Sleep onset delay (SOL >30 min)", "DMN + SN + ANS", "mPFC, insula, LC, VLPO (inhibited)", "Cathodal Fz + cathodal Cz combined pre-sleep (1.0 mA each or bifocal)", "taVNS 15 min → CES 60 min at sleep onset (primary SOI treatment)"],
    ["Nocturnal awakenings (WASO)", "Thalamo-cortical + SN", "Thalamic reticular nucleus, ACC, insula, amygdala", "Cathodal Cz (preSMA/DMN calming); no tDCS during sleep — CES overnight", "CES overnight (Alpha-Stim; delta entrainment; sleep spindle generation); taVNS pre-sleep"],
    ["Non-restorative sleep (EMA/low SWS)", "Thalamo-cortical + Circadian", "Thalamic SWS oscillators, SCN, LC-NE morning surge", "Cathodal frontal pre-sleep (reduce beta hyperarousal to increase delta proportion)", "CES primary (0.5 Hz delta entrainment; increases SWS duration and depth); taVNS HPA cortisol normalisation"],
    ["Pre-sleep anxiety / sleep fear", "Limbic + SN", "Amygdala, insula, right DLPFC (F4)", "Anodal F4 (right DLPFC anxiolytic, 1.5 mA) — 2 hours before sleep; not immediately pre-sleep", "taVNS bilateral (amygdala inhibition) + CES (primary anxiolytic)"],
    ["Depression comorbid insomnia (EMA)", "Limbic + CEN", "Left DLPFC (F3), ACC, amygdala, hippocampus", "Anodal F3 (left DLPFC 2.0 mA) — daytime or early evening; NOT immediately pre-sleep", "taVNS anti-inflammatory; CES post-session; antidepressant medication concurrent"],
    ["Conditioned arousal (bed = awake)", "Limbic", "Amygdala (conditioned fear), hippocampal fear memory", "No specific tDCS for conditioned arousal — stimulus control CBT-I primary", "taVNS + CES in bed (deconditioning — 'bed = CES calm' replaces 'bed = arousal')"],
    ["Daytime fatigue / cognitive impairment", "CEN (daytime)", "DLPFC bilateral, ACC", "Anodal F3/F4 DAYTIME tDCS (morning/afternoon — NOT pre-sleep) for cognitive restoration", "taVNS NE daytime restoration (morning taVNS 10 min); NOT sedative approach during day"],
    ["Hot flush-related awakening (menopause)", "SN + Hypothalamic + Limbic", "Hypothalamus (thermoregulation), insula, ACC", "Standard cathodal Fz/Cz pre-sleep; no specific tDCS for hot flushes", "taVNS primary for vasomotor (hypothalamic thermoregulatory modulation); CES ANS calming; HRT concurrent"],
  ],

  montageSelectionRows: [
    ["Target", "Montage"],
    ["Pre-sleep cognitive arousal (mPFC/DMN inhibition)", "Cathode: Fz (mPFC) — Anode: bilateral mastoids | 1.0–1.5 mA | 20 min pre-sleep (60 min before sleep) | DMN deactivation facilitation"],
    ["Somatic arousal (preSMA inhibition — standard insomnia tDCS)", "Cathode: Cz (preSMA/SMA) — Anode: bilateral mastoids | 1.0–1.5 mA | 20 min pre-sleep | somatic motor arousal reduction"],
    ["Combined cognitive + somatic arousal (bifocal)", "Cathode: Fz + Cz combined (bifocal cathodal) — Anode: bilateral mastoids | 1.0 mA | 20 min pre-sleep"],
    ["Sleep anxiety / right DLPFC anxiolytic (early evening)", "Anode: F4 (right DLPFC) — Cathode: left supraorbital | 1.5 mA | 20 min | 2 hours before sleep (not immediately pre-sleep)"],
    ["Depression + EMA insomnia (daytime F3)", "Anode: F3 (left DLPFC) — Cathode: right supraorbital | 2.0 mA | 20 min | DAYTIME (not pre-sleep) | antidepressant component"],
    ["taVNS insomnia (all phenotypes — standard)", "Left cymba conchae auricular taVNS | 0.5 mA, 200 µs, 25 Hz | 15–20 min | 60–90 min before sleep | HPA axis + LC-NE + VLPO pathway"],
    ["CES primary sleep-onset (FDA-cleared insomnia)", "Alpha-Stim AID bilateral earlobe | 100 µA, 0.5 Hz modified square wave | 40–60 min | during sleep opportunity or 30 min before | primary sleep-promoting intervention"],
    ["CES maintenance insomnia (overnight)", "Alpha-Stim AID | 100 µA | may run overnight (clinical device settings) | delta entrainment during sleep | check device instructions for overnight use"],
    ["TPS thalamo-cortical once-weekly", "NEUROLITH® TPS — vertex (Cz) approach for thalamo-cortical sleep circuit | 0.20 mJ/mm², 2500 pulses | NOT pre-sleep; daytime session; thalamic relay pathway"],
    ["TPS prefrontal sleep circuit (alternative)", "NEUROLITH® TPS mPFC (Fz) | 0.20 mJ/mm², 2000 pulses | daytime session (not evening) | DMN-sleep circuit mPFC targeting"],
    ["Bifocal cathodal frontal + cathodal Cz (combined)", "Dual cathode Fz + Cz — Anode mastoids bilateral | 0.75–1.0 mA per cathode | 20 min pre-sleep | maximum insomnia cathodal protocol"],
    ["Morning taVNS (HPA circadian reset)", "Left cymba conchae taVNS | 0.5 mA, 200 µs, 25 Hz | 10–15 min | morning (upon waking) | HPA cortisol normalisation; circadian LC reset"],
    ["CES daytime cognitive restoration", "Alpha-Stim AID | 100 µA | 20 min | daytime after poor night's sleep | cognitive restoration; NOT a replacement for night-time insomnia treatment"],
  ],

  polarityPrincipleText:
    "Insomnia tDCS polarity is dominated by the cathodal (inhibitory) approach — in the evening/pre-sleep context: the pathology is cortical hyperarousal (excessive neural activity), requiring inhibitory suppression rather than excitatory upregulation. Cathodal Cz (preSMA/SMA area) reduces motor arousal and somatic restlessness; cathodal Fz (mPFC area) reduces pre-sleep cognitive rumination and DMN hyperactivation. The bifocal cathodal approach (cathodes at Fz and Cz simultaneously) addresses both the cognitive (mPFC) and somatic (preSMA) arousal components simultaneously — the signature insomnia tDCS montage in the FNON protocol. This contrasts entirely with most other FNON conditions that use anodal upregulation: insomnia is one of the few conditions where cathodal inhibitory tDCS is the primary therapeutic polarity. The important exception is depression-comorbid insomnia (early morning awakening subtype): here, anodal F3 tDCS is delivered during the daytime (not pre-sleep) to address the depressive component — CEN upregulation for antidepressant effect, separately timed from the pre-sleep cathodal insomnia protocol. Anodal F4 (right DLPFC — anxiolytic) is also used for the anxiety-dominant insomnia phenotype but timed at least 2 hours before sleep to avoid producing a stimulatory effect immediately pre-sleep. taVNS does not use DC polarity; it modulates the NTS-vagal-autonomic-limbic system through afferent nerve stimulation — promoting the parasympathetic dominance (HRV increase, LC-NE reduction, VLPO activation) that is the physiological prerequisite for sleep onset.",

  polarityTable: [
    ["Target", "Polarity", "Effect", "Primary Indication", "Evidence Level"],
    ["preSMA/SMA Cz (pre-sleep)", "CATHODAL", "Inhibits motor arousal and somatic restlessness at bedtime; reduces SMA arousal contributing to restlessness", "Somatic/physiological hyperarousal insomnia; pre-sleep motor restlessness; SMN arousal reduction", "Level C — SMA cathodal sleep literature; insomnia somatic hyperarousal model"],
    ["mPFC Fz (pre-sleep)", "CATHODAL", "Inhibits pre-sleep DMN/mPFC hyperactivity; reduces cognitive rumination; facilitates DMN deactivation at sleep onset", "Cognitive hyperarousal insomnia; 'racing mind' phenotype; sleep onset insomnia dominant", "Level C — mPFC cathodal insomnia; DMN sleep model literature"],
    ["Right DLPFC F4 (early evening — not immediately pre-sleep)", "ANODAL", "Anxiolytic; reduces sleep anxiety and fear of not sleeping; right hemisphere emotional regulation", "Anxiety-dominant insomnia; sleep anxiety; HADS anxiety ≥8 in insomnia", "Level B (anxiety tDCS); Level C (insomnia-anxiety specific)"],
    ["Left DLPFC F3 (daytime only)", "ANODAL", "Antidepressant; CEN upregulation for depression + insomnia comorbidity; daytime cognitive restoration", "Depression-comorbid insomnia; EMA subtype; anhedonia; PHQ-9 ≥10 with insomnia", "Level B (depression tDCS); Level C (insomnia-depression comorbidity)"],
    ["Bifocal cathodal Fz + Cz (pre-sleep)", "CATHODAL BILATERAL", "Combined mPFC + preSMA inhibition; maximum cognitive and somatic hyperarousal reduction; dual cathodal insomnia protocol", "Combined cognitive + somatic hyperarousal insomnia; most common mixed presentation", "Level C — bifocal cathodal insomnia; expert consensus; combines established targets"],
  ],

  classicTdcsProtocols: [
    {
      code: "C1",
      name: "Standard Cathodal preSMA Pre-Sleep Protocol",
      montage: "Cathode Cz (preSMA/SMA) — Anode bilateral mastoids",
      intensity: "1.0–1.5 mA",
      duration: "20 minutes (60 min before sleep opportunity)",
      sessions: "Daily × 2 weeks; then 3–5×/week maintenance",
      indication: "Insomnia with somatic/physiological hyperarousal; motor restlessness; SMA arousal",
      evidence: "Level C — SMA cathodal sleep; somatic hyperarousal insomnia model"
    },
    {
      code: "C2",
      name: "Standard Cathodal mPFC Pre-Sleep Protocol",
      montage: "Cathode Fz (mPFC) — Anode bilateral mastoids",
      intensity: "1.0–1.5 mA",
      duration: "20 minutes (60–90 min before sleep)",
      sessions: "Daily × 2 weeks; then 3–5×/week maintenance",
      indication: "Cognitive hyperarousal insomnia; racing mind; rumination; DMN failure to deactivate",
      evidence: "Level C — mPFC cathodal insomnia; DMN sleep onset model"
    },
    {
      code: "C3",
      name: "Standard Bifocal Cathodal Protocol (Fz + Cz)",
      montage: "Dual cathode Fz + Cz — Anode bilateral mastoids",
      intensity: "1.0 mA per cathode (2.0 mA total)",
      duration: "20 minutes (60 min before sleep)",
      sessions: "Daily × 2 weeks; then 3–5×/week maintenance",
      indication: "Mixed cognitive + somatic hyperarousal insomnia; standard FNON insomnia dual-cathodal protocol",
      evidence: "Level C — bifocal cathodal insomnia; combined cognitive-somatic hyperarousal targeting"
    },
    {
      code: "C4",
      name: "Standard Right DLPFC Anxiolytic Protocol (early evening)",
      montage: "Anode F4 (right DLPFC) — Cathode left supraorbital",
      intensity: "1.5 mA",
      duration: "20 minutes (≥2 hours before intended sleep)",
      sessions: "10–15 sessions",
      indication: "Anxiety-dominant insomnia; sleep anxiety; HADS anxiety ≥8; fear of not sleeping",
      evidence: "Level B (anxiety tDCS); Level C (insomnia-anxiety specific application)"
    },
    {
      code: "C5",
      name: "Standard Left DLPFC Antidepressant Protocol (daytime)",
      montage: "Anode F3 (left DLPFC) — Cathode right supraorbital",
      intensity: "2.0 mA",
      duration: "20 minutes (daytime — morning or afternoon; NOT pre-sleep)",
      sessions: "15–20 sessions",
      indication: "Depression-comorbid insomnia; early morning awakening with depression; antidepressant component",
      evidence: "Level B (depression tDCS — Brunoni 2017); Level C (depression+insomnia comorbidity)"
    },
    {
      code: "C6",
      name: "Standard CES Primary Insomnia Protocol (FDA-cleared)",
      montage: "Alpha-Stim AID bilateral earlobe clips — 100 µA, 0.5 Hz modified square wave",
      intensity: "100 µA (may titrate to 200 µA if insufficient response)",
      duration: "40–60 minutes (at sleep onset or 30 min before sleep)",
      sessions: "Daily × 3 weeks minimum; then maintenance 3–5×/week or as needed",
      indication: "Insomnia — ON-LABEL for Alpha-Stim AID; sleep onset and maintenance; primary FNON insomnia intervention",
      evidence: "Level B — FDA-cleared insomnia; multiple RCTs (Kirsch 2013; Barclay 2014); systematic review Klawansky 1995"
    },
    {
      code: "C7",
      name: "Standard Morning taVNS HPA Reset Protocol",
      montage: "Left cymba conchae taVNS — 0.5 mA, 200 µs, 25 Hz",
      intensity: "0.5 mA",
      duration: "10–15 minutes (immediately on waking, morning)",
      sessions: "Daily concurrent with protocol",
      indication: "HPA axis cortisol circadian normalisation; morning cortisol excess in insomnia; circadian LC-NE reset; daytime function restoration",
      evidence: "Level C — taVNS HPA axis; LC circadian normalisation; insomnia autonomic model"
    },
    {
      code: "C8",
      name: "Standard Evening taVNS Sleep-Onset Protocol",
      montage: "Left cymba conchae taVNS — 0.5 mA, 200 µs, 25 Hz",
      intensity: "0.5 mA",
      duration: "15–20 minutes (60–90 min before sleep)",
      sessions: "Daily concurrent with protocol",
      indication: "Sleep onset insomnia; LC-NE evening suppression; VLPO activation; HPA cortisol reduction pre-sleep; autonomic calming",
      evidence: "Level C — taVNS sleep onset; NTS-LC-VLPO pathway; autonomic insomnia model"
    },
  ],

  fnonTdcsProtocols: [
    {
      code: "F1",
      name: "FNON Pre-Sleep Hyperarousal Suppression Protocol — Bifocal Cathodal + taVNS + CES",
      montage: "taVNS 0.5 mA × 15–20 min (60–90 min before sleep) → bifocal cathodal tDCS Fz+Cz 1.0 mA × 20 min (60 min before sleep) → CES 100 µA × 60 min at sleep onset",
      intensity: "taVNS 0.5 mA; tDCS cathodal 1.0 mA per cathode; CES 100 µA",
      duration: "Sequential: taVNS 15 min (T-90 min) → tDCS 20 min (T-60 min) → CES 60 min at sleep onset; total 3-step evening protocol",
      sessions: "Daily × 2 weeks intensive; then 5×/week maintenance",
      indication: "Sleep onset insomnia with cognitive + somatic hyperarousal; primary FNON insomnia protocol — covers all three hyperarousal dimensions",
      fnon_rationale: "Sequential timing mirrors the physiological pre-sleep cascade: taVNS (T-90 min) begins LC-NE and HPA calming first (vagal parasympathetic onset takes 10–15 min); bifocal cathodal tDCS (T-60 min) reduces cognitive and somatic arousal as pre-sleep cortical inhibition window; CES at sleep onset provides direct delta oscillatory entrainment at the moment of sleep opportunity — maximum temporal alignment of three complementary mechanisms"
    },
    {
      code: "F2",
      name: "FNON Sleep Maintenance Protocol — CES Overnight + Evening taVNS",
      montage: "Evening taVNS 0.5 mA × 20 min (T-90 min) + CES 100 µA × overnight/extended duration; cathodal Cz tDCS (T-60 min) if somatic component",
      intensity: "taVNS 0.5 mA; CES 100 µA overnight; cathodal tDCS 1.0 mA optional",
      duration: "Extended CES protocol for sleep maintenance; check Alpha-Stim device instructions for extended use",
      sessions: "Daily × 3 weeks; maintenance ongoing",
      indication: "Sleep maintenance insomnia (SMI); WASO dominant; frequent awakenings; non-restorative sleep; reduced NREM3",
      fnon_rationale: "Sleep maintenance insomnia requires sustained overnight sleep architecture enhancement rather than only sleep-onset facilitation; extended CES delta entrainment throughout sleep promotes continuous NREM3 maintenance and reduces thalamic arousal gating failure; evening taVNS pre-conditions the autonomic system for sustained parasympathetic dominance during sleep"
    },
    {
      code: "F3",
      name: "FNON Anxiety-Insomnia Protocol — Right DLPFC + taVNS + CES",
      montage: "Bilateral taVNS 0.5 mA × 20 min (T-120 min) → anodal F4 tDCS 1.5 mA × 20 min (T-90 min) → CES 100 µA × 60 min (T-30 min to sleep)",
      intensity: "Bilateral taVNS 0.5 mA; anodal tDCS F4 1.5 mA; CES 100 µA",
      duration: "Evening: taVNS (T-120) → F4 tDCS (T-90) → CES (T-30); total 2-hour pre-sleep window",
      sessions: "10–15 sessions concurrent with CBT-I anxiety-focused protocol",
      indication: "Anxiety-dominant insomnia; sleep anxiety; HADS anxiety ≥8; fear of not sleeping; anticipatory anxiety",
      fnon_rationale: "Bilateral taVNS maximum anxiolytic via NTS→amygdala inhibition (T-120 min — longest lead time for autonomic calming); anodal F4 right DLPFC anxiolytic tDCS (T-90 min — not too close to sleep to avoid stimulatory effect); CES primary sleep facilitation (T-30 min); CBT-I anxiety-insomnia components concurrent for cognitive-level extinction of conditioned arousal"
    },
    {
      code: "F4",
      name: "FNON Depression + Insomnia Dual Protocol — Morning F3 + Evening CES",
      montage: "Morning: anodal F3 tDCS 2.0 mA × 20 min + morning taVNS 0.5 mA × 10 min (HPA reset); Evening: CES 100 µA × 60 min + evening taVNS × 15 min",
      intensity: "Morning: tDCS 2.0 mA F3 + taVNS 0.5 mA; Evening: CES 100 µA + taVNS 0.5 mA",
      duration: "Morning session 30 min + Evening session 75 min; dual time-point protocol",
      sessions: "15–20 sessions",
      indication: "Depression + insomnia comorbidity; early morning awakening subtype; bidirectional depression-insomnia cycle",
      fnon_rationale: "Dual time-point protocol: morning anodal F3 tDCS for antidepressant CEN upregulation during daytime (correct timing for depression target — activatory in daytime context); morning taVNS for HPA cortisol circadian normalisation; evening CES + taVNS for insomnia sleep onset facilitation — each component timed optimally for its target rather than compromised by single-session delivery"
    },
    {
      code: "F5",
      name: "FNON Circadian + Insomnia Protocol — Morning Bright Light + taVNS + Evening CES",
      montage: "Morning: morning taVNS 0.5 mA × 15 min + bright light therapy 10,000 lux × 30 min; Evening: cathodal Fz 1.0 mA × 20 min + CES 60 min at sleep onset",
      intensity: "taVNS 0.5 mA; tDCS cathodal 1.0 mA; CES 100 µA; bright light 10,000 lux",
      duration: "Morning: 30 min bright light + 15 min taVNS; Evening: 20 min tDCS + 60 min CES",
      sessions: "Daily × 3 weeks",
      indication: "Insomnia with circadian component; delayed sleep phase; menopause-related circadian disruption; early morning awakening with phase advance",
      fnon_rationale: "Morning bright light + taVNS advance circadian phase and reset SCN-LC axis (cortisol morning peak normalisation); evening cathodal tDCS + CES suppress the arousal circuit at the correct circadian time; combined morning-evening protocol addresses both circadian (morning) and sleep-onset (evening) dimensions simultaneously"
    },
    {
      code: "F6",
      name: "FNON Comprehensive Insomnia Maintenance Protocol",
      montage: "Alternating: Week 1 — F1 (pre-sleep hyperarousal); Week 2 — F2 (sleep maintenance CES); taVNS daily both weeks; CES daily pre-sleep",
      intensity: "Per individual session protocols",
      duration: "Ongoing maintenance; adjust based on sleep diary response",
      sessions: "Ongoing maintenance (3–5×/week); reassess every 4 weeks",
      indication: "Phase 2 insomnia maintenance; post-CBT-I FNON support; long-term sleep health maintenance",
      fnon_rationale: "Chronic insomnia requires long-term neurobiological normalisation beyond the acute protocol period; alternating sleep-onset and sleep-maintenance targeted approaches prevents adaptation; daily CES pre-sleep and morning taVNS become sustainable daily practices supporting ongoing sleep architecture; CBT-I skills maintained as the behavioural foundation"
    },
  ],

  classicTpsProtocols: [
    {
      code: "T1",
      name: "Classic TPS Thalamo-Cortical Sleep Circuit Protocol",
      target: "Vertex (Cz) approach for thalamo-cortical circuit; medial thalamic projections via cortical relay",
      parameters: "0.20 mJ/mm², 2500 pulses, 3 Hz; DAYTIME session (not evening)",
      sessions: "4–6 sessions (once-weekly; not daily — thalamo-cortical sleep circuit modulation as booster)",
      indication: "Non-restorative sleep; sleep maintenance insomnia; thalamic sleep spindle generation deficit",
      evidence: "Level C — thalamo-cortical TPS; slow-wave sleep enhancement; adapted from tACS sleep spindle literature"
    },
    {
      code: "T2",
      name: "Classic TPS mPFC DMN Sleep Protocol",
      target: "Medial prefrontal cortex (Fz area; neuro-navigation; 1–2 cm depth)",
      parameters: "0.20 mJ/mm², 2000 pulses, 3 Hz; daytime session",
      sessions: "4–6 sessions",
      indication: "Cognitive hyperarousal insomnia; DMN-sleep onset coupling; mPFC pre-sleep hyperactivity",
      evidence: "Level C — mPFC TPS sleep; DMN insomnia model"
    },
    {
      code: "T3",
      name: "Classic TPS preSMA Sleep Protocol",
      target: "Pre-SMA/SMA (Cz-adjacent; neuro-navigation; 1 cm depth)",
      parameters: "0.20 mJ/mm², 2000 pulses, 3 Hz; daytime session",
      sessions: "4–6 sessions",
      indication: "Somatic hyperarousal insomnia; SMA/preSMA arousal at bedtime; motor restlessness",
      evidence: "Level C — SMA TPS sleep; somatic hyperarousal insomnia"
    },
    {
      code: "T4",
      name: "Classic TPS Prefrontal Sleep Architecture Protocol",
      target: "Bilateral DLPFC (F3/F4 area; neuro-navigation)",
      parameters: "0.20–0.25 mJ/mm², 2500 pulses per hemisphere; daytime session",
      sessions: "6 sessions (2×/week × 3 weeks)",
      indication: "Cognitive function restoration in chronic insomnia; DLPFC sleep-wake regulation; daytime function",
      evidence: "Level C — prefrontal TPS sleep; insomnia prefrontal network"
    },
    {
      code: "T5",
      name: "Classic TPS Limbic-Sleep Protocol",
      target: "ACC/mPFC (Fz area, 1–2 cm depth) — limbic-sleep interface; daytime",
      parameters: "0.20 mJ/mm², 2500 pulses, 3 Hz; daytime session",
      sessions: "4–6 sessions",
      indication: "Conditioned arousal insomnia; amygdala-mediated sleep anxiety; ACC-sleep gating failure",
      evidence: "Level C — ACC TPS sleep; conditioned arousal insomnia model"
    },
  ],

  fnonTpsProtocols: [
    {
      code: "FT1",
      name: "FNON TPS Thalamo-Cortical Sleep Enhancement Protocol",
      target: "Vertex (Cz area, thalamo-cortical relay) — mPFC (Fz, 2000 pulses) sequential; daytime session; taVNS evening same day",
      parameters: "0.20 mJ/mm² per target; 2500 pulses Cz + 2000 pulses Fz; neuro-navigation; daytime session",
      sessions: "6 sessions (daytime once-weekly + daily evening taVNS + CES)",
      indication: "Non-restorative sleep; sleep maintenance insomnia; thalamic + mPFC sleep circuit combined",
      fnon_rationale: "Sequential thalamo-cortical (Cz) → mPFC TPS during daytime targets the full sleep architecture network: thalamic sleep spindle generation + mPFC DMN-sleep coupling; daytime session ensures thalamo-cortical circuit modulation has time to integrate before evening sleep opportunity; complemented by daily evening taVNS + CES"
    },
    {
      code: "FT2",
      name: "FNON TPS Cognitive-Somatic Arousal Protocol",
      target: "mPFC (Fz, 2000 pulses) → preSMA (Cz area, 2000 pulses) sequential; daytime session; evening cathodal tDCS same day",
      parameters: "0.20 mJ/mm² per target; neuro-navigation; 40 min daytime; evening tDCS protocol same day",
      sessions: "6 sessions (daytime TPS + daily evening tDCS/taVNS/CES)",
      indication: "Combined cognitive + somatic hyperarousal insomnia; mPFC + preSMA dual-target; full hyperarousal circuit",
      fnon_rationale: "Daytime TPS mPFC + preSMA provides a weekly 'deep reset' of the hyperarousal circuit beyond the daily surface tDCS modulation; combined with daily evening cathodal tDCS and CES, creates a two-level intervention: TPS deep circuit modulation (once-weekly) + tDCS/CES surface daily modulation"
    },
    {
      code: "FT3",
      name: "FNON TPS Limbic-Sleep Deconditioning Protocol",
      target: "ACC/mPFC (Fz, 2500 pulses) → hippocampus (2000 pulses — conditioned fear memory); taVNS concurrent daytime; CBT-I concurrent",
      parameters: "0.20–0.25 mJ/mm²; neuro-navigation; 45 min; taVNS concurrent; CBT-I same day",
      sessions: "6 sessions concurrent with CBT-I stimulus control component",
      indication: "Psychophysiological insomnia; conditioned arousal; amygdala-hippocampal conditioned fear of bed; Spielman model perpetuating factor",
      fnon_rationale: "ACC + hippocampal TPS targets both the ACC (conditioned arousal maintenance — conflict monitoring between wanting to sleep and being aroused) and hippocampus (conditioned fear memory for sleep environment); taVNS concurrent reduces amygdala fear conditioning at the moment of TPS-induced neural reactivation — potential reconsolidation interference of conditioned arousal memory; CBT-I stimulus control provides behavioural deconditioning concurrent"
    },
    {
      code: "FT4",
      name: "FNON TPS Circadian-Sleep Protocol",
      target: "mPFC (Fz, 2000 pulses) — morning session targeting mPFC-SCN-circadian interface; taVNS morning concurrent",
      parameters: "0.20 mJ/mm², 2000 pulses; morning session (8–10 am); taVNS concurrent; bright light therapy post-TPS",
      sessions: "6 sessions (morning; once-weekly; morning taVNS daily between sessions)",
      indication: "Circadian insomnia component; delayed or advanced sleep phase; EMA with phase advance; menopause circadian disruption",
      fnon_rationale: "Morning mPFC TPS targeting the mPFC-SCN interface during the peak circadian morning window; concurrent morning taVNS for HPA cortisol circadian normalisation; post-TPS bright light therapy reinforces the morning zeitgeber signal — circadian reset protocol with TPS as the deep circuit component"
    },
    {
      code: "FT5",
      name: "FNON TPS Depression + Insomnia Protocol — DLPFC + Limbic",
      target: "Left DLPFC (F3, 3000 pulses) → ACC/mPFC (Fz, 2000 pulses) → hippocampus (2000 pulses); daytime session; evening CES + taVNS same day",
      parameters: "0.25 mJ/mm² DLPFC; 0.20 mJ/mm² ACC + hippocampus; neuro-navigation; 75 min daytime session",
      sessions: "6–8 sessions (depression + insomnia comorbidity protocol; 2×/week)",
      indication: "Depression + insomnia bidirectional comorbidity; EMA subtype; antidepressant + sleep architecture combined TPS",
      fnon_rationale: "Three-target daytime TPS: DLPFC (antidepressant upregulation) + ACC (sleep-wake conflict and depressive rumination) + hippocampus (episodic memory and neurogenesis for depression recovery); daytime session avoids pre-sleep stimulatory effects; evening CES + taVNS provides the sleep-promoting component"
    },
    {
      code: "FT6",
      name: "FNON TPS Chronic Treatment-Resistant Insomnia Protocol",
      target: "Rotating 6-session: Session 1,4 — thalamo-cortical (Cz+Fz); Session 2,5 — mPFC+preSMA; Session 3,6 — DLPFC+ACC; taVNS every session; CES daily",
      parameters: "0.20–0.25 mJ/mm², 2500 pulses per target; neuro-navigation; daytime all TPS sessions; evening CES + taVNS daily",
      sessions: "6 TPS sessions (rotating); daily CES + taVNS evening protocol; CBT-I concurrently; reassess at 6 weeks",
      indication: "Chronic treatment-resistant insomnia; failed CBT-I and pharmacological treatment; multi-network hyperarousal; ≥2 years insomnia",
      fnon_rationale: "Rotating three-domain TPS (thalamo-cortical sleep architecture, frontal hyperarousal, limbic-conditioned arousal) provides comprehensive network coverage for the most refractory insomnia presentations where single-target approaches have failed; daily CES + taVNS evening protocol as foundational maintenance; CBT-I concurrent for behavioural component"
    },
    {
      code: "FT7",
      name: "FNON TPS Menopause Insomnia Protocol",
      target: "Hypothalamic-adjacent targeting via mPFC/Fz (2000 pulses) + thalamo-cortical (Cz, 2000 pulses); daytime morning session; taVNS morning + evening",
      parameters: "0.20 mJ/mm² per target; neuro-navigation; 40 min daytime; taVNS morning + evening daily",
      sessions: "6 sessions (once-weekly) + daily taVNS morning (HPA/thermoregulation) + evening (sleep onset)",
      indication: "Menopause-related insomnia; hot flush sleep disruption; circadian-HPA-insomnia triad in menopause",
      fnon_rationale: "mPFC TPS for mPFC-hypothalamic thermoregulation circuit (emerging evidence that mPFC modulates hypothalamic thermoregulatory tone); thalamo-cortical TPS for sleep architecture; morning taVNS for HPA and thermoregulatory hypothalamic circadian normalisation — addresses the HPA-thermoregulatory-sleep triad of menopause insomnia; HRT concurrent if appropriate"
    },
    {
      code: "FT8",
      name: "FNON TPS Sleep Architecture Enhancement Protocol",
      target: "Vertex (Cz) deep thalamo-cortical; mPFC (Fz) for slow-oscillation; sessions timed once-weekly daytime",
      parameters: "0.20 mJ/mm², 2500 pulses Cz + 2000 pulses Fz; neuro-navigation; 45 min session",
      sessions: "6 sessions (once-weekly); daily CES overnight + evening taVNS protocol concurrent",
      indication: "Non-restorative sleep with objective sleep architecture deficit on PSG/EEG (reduced SWS, reduced spindle density)",
      fnon_rationale: "Weekly deep thalamo-cortical TPS addresses the sleep spindle generation circuit (thalamic reticular nucleus via vertex cortical relay) and slow oscillation cortical generator (mPFC); weekly deep circuit modulation is complementary to daily surface CES delta entrainment — acting at different depths and timescales of the same sleep circuit"
    },
    {
      code: "FT9",
      name: "FNON TPS Comprehensive Insomnia Recovery Programme",
      target: "12-session rotating: Session 1,4,7,10 — thalamo-cortical + mPFC; Session 2,5,8,11 — DLPFC bilateral; Session 3,6,9,12 — ACC + hippocampal; taVNS and CES daily",
      parameters: "0.20–0.25 mJ/mm², 2500–3000 pulses per target per session; neuro-navigation; daytime all TPS; 40–60 min",
      sessions: "12 TPS sessions (once-weekly × 12 weeks); daily taVNS evening + morning; daily CES pre-sleep",
      indication: "Multi-phenotype chronic insomnia; long-term neurobiological rehabilitation programme for insomnia disorder; combined sleep architecture + hyperarousal + cognitive restoration",
      fnon_rationale: "Twelve-week comprehensive programme provides long-term thalamo-cortical, frontal, and limbic network rehabilitation for chronic insomnia; rotating targets across the full insomnia network without adaptation; consistent daily taVNS and CES provide the continuous evening routine that neurologically re-associates the pre-sleep period with parasympathetic calming and delta entrainment — a complete neurobiological sleep re-conditioning programme"
    },
  ],

  multimodalPhenotypes: [
    {
      phenotype: "Sleep Onset Insomnia (SOI) — Cognitive Hyperarousal",
      stabilise: "Evening taVNS 0.5 mA, 200 µs, 25 Hz × 15–20 min (T-90 min before sleep; LC-NE reduction; VLPO activation; HPA pre-sleep cortisol blunting)",
      optimise: "Cathodal Fz tDCS 1.0–1.5 mA × 20 min (T-60 min; mPFC cognitive arousal suppression; DMN deactivation facilitation; concurrent with CBT-I cognitive restructuring or relaxation audio)",
      zone: "TPS mPFC (Fz, 0.20 mJ/mm², 2000 pulses) daytime once-weekly only (not pre-sleep); taVNS concurrent during daytime TPS session",
      outcome: "CES 100 µA × 60 min at sleep onset (primary SOI sleep-promoting intervention); sleep diary SOL monitoring (target <20 min by week 3); CBT-I cognitive restructuring homework"
    },
    {
      phenotype: "Sleep Maintenance Insomnia (SMI) — Frequent Awakenings",
      stabilise: "Evening taVNS 0.5 mA × 20 min (T-60 min; sustained parasympathetic tone for overnight sleep maintenance; delta sleep-promoting pathway via VLPO)",
      optimise: "Cathodal Cz tDCS 1.0 mA × 20 min (T-40 min; preSMA inhibition reducing motor arousal during light sleep stages that triggers awakening)",
      zone: "TPS vertex (Cz thalamo-cortical, 0.20 mJ/mm², 2500 pulses) daytime once-weekly + TPS mPFC (Fz, 2000 pulses) same session; weekly deep circuit enhancement",
      outcome: "CES 100 µA extended duration at sleep onset; WASO monitoring via actigraphy (target <20 min); PSQI sleep continuity subscale; melatonin concurrent if circadian component"
    },
    {
      phenotype: "Early Morning Awakening — Depression Comorbid",
      stabilise: "Morning taVNS 0.5 mA × 15 min (immediately on waking — HPA cortisol blunting; LC circadian reset for both depression and insomnia morning cortisol excess)",
      optimise: "Anodal F3 tDCS 2.0 mA × 20 min DAYTIME (morning/midday — CEN upregulation for antidepressant effect; NOT pre-sleep; correct timing is key for depression tDCS)",
      zone: "TPS left DLPFC 0.25 mJ/mm² 3000 pulses + TPS hippocampal 0.25 mJ/mm² 2000 pulses daytime session (antidepressant + memory circuit); once-weekly daytime TPS",
      outcome: "Evening: CES 60 min pre-sleep + evening taVNS 15 min; PHQ-9 and ISI dual monitoring; antidepressant medication concurrent and maintained; CBT-I early morning awakening protocol (sleep restriction with morning anchor)"
    },
    {
      phenotype: "Psychophysiological / Conditioned Arousal Insomnia",
      stabilise: "Bilateral taVNS 0.5 mA × 20 min (maximum amygdala inhibition via NTS→LC→amygdala — addresses the conditioned fear response to sleep environment; bilateral doubles NTS input)",
      optimise: "Bifocal cathodal tDCS (Fz + Cz, 1.0 mA each) × 20 min + bilateral taVNS concurrent — maximum combined cognitive-somatic arousal suppression during the pre-sleep deconditioning period",
      zone: "TPS ACC + hippocampal daytime (conditioned fear memory reconsolidation circuit) × 6 sessions concurrent with CBT-I stimulus control component; once-weekly daytime TPS",
      outcome: "CES 100 µA × 60 min at sleep onset IN OWN BED (deconditioning: CES-calm association in bed); stimulus control CBT-I (bed for sleep only; out of bed if awake >20 min); sleep efficiency monitoring (target >85%)"
    },
    {
      phenotype: "Short Sleep Duration Insomnia (Objective — PSG Confirmed)",
      stabilise: "Bilateral taVNS 0.5 mA × 20 min (maximum dose — bilateral; objective short sleep with physiological hyperarousal requires maximum autonomic intervention)",
      optimise: "Bifocal cathodal tDCS (Fz + Cz, 1.0 mA each) × 20 min + bilateral taVNS concurrent — maximum inhibitory protocol for objective hyperarousal insomnia",
      zone: "TPS thalamo-cortical (Cz, 2500 pulses) + mPFC (Fz, 2000 pulses) daytime; once-weekly deep circuit reset for thalamic sleep architecture",
      outcome: "High-dose CES 200 µA × 60 min at sleep onset; actigraphy total sleep time monitoring; EEG beta/delta ratio if available; cardiovascular risk monitoring (objective short sleep associated with cardiometabolic risk)"
    },
    {
      phenotype: "Anxiety-Dominant Insomnia",
      stabilise: "Bilateral taVNS 0.5 mA × 20 min (T-120 min; maximum anxiolytic via bilateral NTS→amygdala; bilateral doubles amygdala inhibition; early evening timing to allow full anxiolytic onset)",
      optimise: "Anodal F4 tDCS 1.5 mA × 20 min (T-90 min; right DLPFC anxiolytic — ≥90 min before sleep to avoid any activatory effect immediately pre-sleep); CBT-I anxiety-specific protocol concurrent",
      zone: "TPS right DLPFC (F4) 0.25 mJ/mm² 2500 pulses + TPS ACC (Fz, 2000 pulses) daytime — once-weekly anxiety-insomnia circuit; taVNS concurrent",
      outcome: "CES 100 µA × 60 min at sleep onset; GAD-7 anxiety monitoring; DBAS-16 sleep worry subscale; CBT-I with sleep restriction adapted for anxiety (very cautious sleep restriction titration); antidepressant/anxiolytic medication if HADS ≥11"
    },
    {
      phenotype: "Menopause-Related Insomnia",
      stabilise: "Morning taVNS 0.5 mA × 15 min (hypothalamic thermoregulatory normalisation; HPA-menopausal cortisol blunting; circadian reset at morning cortisol peak)",
      optimise: "Evening taVNS 0.5 mA × 15 min (T-60 min; parasympathetic induction for sleep onset; vasomotor arousal prevention during sleep opportunity) + cathodal Cz tDCS 1.0 mA × 20 min",
      zone: "TPS mPFC + thalamo-cortical daytime morning session (mPFC-hypothalamic thermoregulatory interface; weekly); morning taVNS concurrent with TPS session",
      outcome: "CES 100 µA × 60 min at sleep onset; HRT assessment concurrent if appropriate; PSQI sleep quality; hot flush diary (frequency and severity); CBT-I adapted for menopause (CBTI-M); phytoestrogens and MHT concurrent if indicated"
    },
    {
      phenotype: "Comorbid Pain-Insomnia Dyad",
      stabilise: "taVNS 0.5 mA × 15 min (T-90 min; dual NTS-PAG analgesic pre-activation + VLPO sleep activation — pain pathway and sleep pathway via NTS simultaneously)",
      optimise: "Anodal M1 tDCS (C3/C4, 2.0 mA) × 20 min (T-60 min; M1 descending pain inhibition — pain reduction during sleep opportunity reduces arousal from pain) + cathodal Cz concurrent if feasible",
      zone: "TPS M1 → ACC pain network daytime; TPS thalamo-cortical (Cz) for sleep architecture daytime — alternating sessions; once-weekly TPS each",
      outcome: "CES 100 µA × 60 min at sleep onset (analgesic + sleep promoting); VAS pain + ISI dual monitoring; pain management optimised concurrently; PSQI sleep and pain interference subscales"
    },
    {
      phenotype: "Chronic Treatment-Resistant Insomnia",
      stabilise: "Bilateral taVNS 0.5 mA × 20 min (maximum dose; bilateral; mandatory every session — the most consistent treatment element in refractory insomnia)",
      optimise: "Bifocal cathodal tDCS (Fz + Cz, 1.0 mA each) × 20 min + bilateral taVNS concurrent + morning anodal F3 tDCS (2.0 mA) daytime if depression comorbid",
      zone: "Rotating intensive TPS (FT6 protocol — 6 sessions rotating thalamo-cortical, frontal, limbic-conditioned); daytime; once-weekly; taVNS concurrent during TPS",
      outcome: "High-dose CES 200 µA × 60 min nightly; daily taVNS morning + evening; intensive CBT-I restart (group format if prior individual failed); pharmacological review: consider daridorexant (DORA) concurrent; MDT sleep review at 6 weeks"
    },
  ],

  taskPairingRows: [
    ["Task Type", "Concurrent NIBS", "Protocol Rationale", "Outcome Measure"],
    ["Progressive Muscle Relaxation (PMR) / body scan", "taVNS concurrent + optional cathodal Cz (preSMA)", "taVNS parasympathetic activation during PMR synergises: both reduce LC-NE sympathetic arousal and SMA motor tension; taVNS enhances relaxation response depth; pre-sleep combination", "Pre-sleep arousal scale (PSAS) somatic subscale; skin conductance during PMR; HR during relaxation session"],
    ["CBT-I sleep restriction therapy", "Evening bifocal cathodal tDCS (Fz+Cz) + taVNS during prescribed sleep window", "Sleep restriction reduces time in bed to build sleep pressure; cathodal tDCS reduces hyperarousal that undermines sleep pressure conversion to sleep; taVNS pre-sleep onset adds physiological calming", "Sleep efficiency (SE target ≥90% for bed-time extension); sleep diary SOL + WASO; ISI weekly"],
    ["CBT-I stimulus control / deconditioning", "taVNS + CES in own bed (deconditioning association)", "CES delivered in bed creates new association: bed → CES → calm → sleep; replaces conditioned bed → arousal; taVNS concurrent deepens parasympathetic-in-bed association", "Sleep efficiency in own bed vs. other environments; conditioned arousal questionnaire; ISI bedroom association item"],
    ["Mindfulness-based cognitive therapy for insomnia (MBCT-I)", "CES during mindfulness practice + taVNS pre-session", "CES tonic ANS calming during mindfulness practice reduces physiological barriers to present-moment awareness; taVNS pre-mindfulness reduces amygdala reactivity improving focus quality", "FFMQ mindfulness measure; GSES Glasgow Sleep Effort Scale; sleep catastrophising questionnaire"],
    ["Sleep hygiene education and stimulus control", "taVNS + CES as components of sleep hygiene routine", "taVNS and CES become integrated within the sleep hygiene routine: taVNS at T-60 min (consistent pre-bed routine); CES at sleep onset (consistent bed association); routine consistency amplifies circadian Zeitgeber effect", "DBAS-16 sleep hygiene beliefs; ISI; PSQI component scores"],
    ["Guided imagery / relaxation audio at sleep onset", "CES concurrent (primary)", "CES delta entrainment during guided imagery practice promotes synchronisation between the relaxation narrative and thalamo-cortical sleep oscillation initiation; facilitates transition from relaxed waking to sleep onset", "SOL (sleep onset latency); subjective sleep quality; PSQI sleep quality subscale"],
  ],

  outcomeMeasures:
    "Primary outcome measures for the SOZO Insomnia FNON protocol: (1) Insomnia Severity Index (ISI — 0–28 scale) — primary insomnia outcome; MCID: ≥6 points reduction; responder: ≥8 points; remission: ISI <8; (2) Sleep diary SOL (sleep onset latency) — primary objective target: <20 min; (3) Sleep diary WASO (wake after sleep onset) — target: <20 min; (4) Sleep diary sleep efficiency (SE) — target: ≥85%. Secondary measures: Pittsburgh Sleep Quality Index (PSQI — MCID: ≥3 points); actigraphy total sleep time, SOL, WASO, SE (objective sleep measures); Pre-Sleep Arousal Scale (PSAS — cognitive and somatic subscales); Glasgow Sleep Effort Scale (GSES — sleep effort/performance anxiety); Dysfunctional Beliefs and Attitudes About Sleep (DBAS-16 — cognitive perpetuating factors); Epworth Sleepiness Scale (ESS — daytime sleepiness); PHQ-9 and GAD-7 (comorbid depression and anxiety). Quality of life: SF-36 or WHOQOL-BREF vitality subscale. Neurophysiological (optional, participating sites): EEG delta/beta power ratio during NREM sleep pre/post protocol; sleep spindle density; salivary cortisol evening and morning (HPA axis); HRV RMSSD (autonomic outcome). Assessment schedule: ISI + sleep diary at baseline, week 2, week 4 (end of intensive protocol), and 1-month follow-up. Safety monitoring: ISI worsening criterion: any increase ≥4 points from baseline requires protocol review and reduction of session intensity.",

  medicationSectionTitle: "Pharmacological Context and NIBS Interactions in Insomnia Disorder",
  medicationSectionText:
    "Hypnotic medications are the most important pharmacological consideration for FNON insomnia protocols, both as context and as potential neuroplasticity modulators: Z-drugs (zopiclone, zolpidem, zaleplon — GABA-A positive allosteric modulators): significantly reduce cortical excitability and LTP capacity; tDCS neuroplasticity responses are substantially reduced with chronic Z-drug use; if possible, gradual supervised taper concurrent with CBT-I before adding tDCS; CES and taVNS are not as affected by GABAergic drugs. Benzodiazepines (temazepam, nitrazepam): same GABA-A potentiation issue; NICE NG215 recommends against new prescriptions — existing users should be supported in supervised taper; CES/taVNS are the primary NIBS modalities during benzodiazepine taper period. Melatonin (Circadin 2 mg or unlicensed preparations): no interaction with NIBS; complementary to CES and taVNS circadian components; recommended concurrent for circadian insomnia component and elderly insomnia. Daridorexant/lemborexant (dual orexin receptor antagonists — DORAs): blocks orexin wake signal; compatible with all FNON modalities; DORA + taVNS provides complementary mechanisms (DORA blocks orexin; taVNS reduces LC-NE wake drive — different wake systems); DORAs do not reduce neuroplasticity. Low-dose doxepin (6 mg Silenor): antihistamine + weak TCA; mild cortical excitability reduction; compatible with FNON; document dose. SSRIs/SNRIs (for comorbid depression/anxiety with insomnia): serotonergic facilitation may augment anodal DLPFC tDCS; document class and dose; SSRIs may worsen sleep latency acutely (REM suppression) — manage with dose timing. Mirtazapine (noradrenergic + histaminergic; sedating): H1 antagonism produces sedation independently; complementary to taVNS in reducing evening LC-NE drive; may enhance CES sleep-promoting effect. Antihistamines (diphenhydramine, promethazine) as OTC sleep aids: cognitive side effects, rapid tolerance development; discourage use alongside NIBS. Caffeine: document habitual intake; advise ≤200 mg total/day; no caffeine after noon for insomnia protocol participants; caffeine and CES have opposing mechanisms on sleep architecture.",

  references: {
    foundational: [
      { authors: "American Academy of Sleep Medicine", year: 2014, title: "International Classification of Sleep Disorders, Third Edition (ICSD-3)", journal: "American Academy of Sleep Medicine", volume: "", pages: "", doi: "" },
      { authors: "Riemann D, Baglioni C, Bassetti C, et al.", year: 2017, title: "European guideline for the diagnosis and treatment of insomnia", journal: "Journal of Sleep Research", volume: "26(6)", pages: "675–700", doi: "10.1111/jsr.12594" },
      { authors: "Perlis ML, Giles DE, Mendelson WB, et al.", year: 1997, title: "Psychophysiological insomnia: The behavioural model and a neurocognitive perspective", journal: "Journal of Sleep Research", volume: "6(3)", pages: "179–188", doi: "10.1046/j.1365-2869.1997.00045.x" },
      { authors: "Bonnet MH, Arand DL", year: 1997, title: "Hyperarousal and insomnia", journal: "Sleep Medicine Reviews", volume: "1(2)", pages: "97–108", doi: "10.1016/S1087-0792(97)90012-5" },
      { authors: "Morin CM, Bastien C, Savard J", year: 2003, title: "Current directions in the treatment of insomnia", journal: "Annual Review of Clinical Psychology", volume: "1", pages: "1–34", doi: "10.1146/annurev.clinpsy.1.102803.144026" },
      { authors: "Harvey AG, Tang NK, Browning L", year: 2005, title: "Cognitive approaches to insomnia", journal: "Clinical Psychology Review", volume: "25(5)", pages: "593–611", doi: "10.1016/j.cpr.2005.04.005" },
    ],
    tdcs: [
      { authors: "Lefaucheur JP, Antal A, Ayache SS, et al.", year: 2017, title: "Evidence-based guidelines on the therapeutic use of transcranial direct current stimulation (tDCS)", journal: "Clinical Neurophysiology", volume: "128(1)", pages: "56–92", doi: "10.1016/j.clinph.2016.10.087" },
      { authors: "Marshall L, Helgadóttir H, Mölle M, Born J", year: 2006, title: "Boosting slow oscillations during sleep potentiates memory", journal: "Nature", volume: "444(7119)", pages: "610–613", doi: "10.1038/nature05278" },
      { authors: "Fregni F, Boggio PS, Nitsche MA, et al.", year: 2006, title: "Treatment of major depression with transcranial direct current stimulation", journal: "Bipolar Disorders", volume: "8(2)", pages: "203–204", doi: "10.1111/j.1399-5618.2006.00291.x" },
    ],
    tps: [
      { authors: "Beisteiner R, Matt E, Fan C, et al.", year: 2020, title: "Transcranial pulse stimulation with ultrasound in Alzheimer's disease—A new navigated focal brain therapy", journal: "Advanced Science", volume: "7(3)", pages: "1902583", doi: "10.1002/advs.201902583" },
      { authors: "Legon W, Bansal P, Tyberg M, et al.", year: 2014, title: "Transcranial focused ultrasound modulates the activity of human somatosensory cortex", journal: "Nature Neuroscience", volume: "17(2)", pages: "322–329", doi: "10.1038/nn.3620" },
    ],
    tavns: [
      { authors: "Clancy JA, Mary DA, Witte KK, et al.", year: 2014, title: "Non-invasive vagus nerve stimulation in healthy humans reduces sympathetic nerve activity", journal: "Brain Stimulation", volume: "7(6)", pages: "871–877", doi: "10.1016/j.brs.2014.07.031" },
      { authors: "Frangos E, Ellrich J, Komisaruk BR", year: 2015, title: "Non-invasive access to the vagus nerve central projections via electrical stimulation of the ear", journal: "Brain Stimulation", volume: "8(3)", pages: "624–636", doi: "10.1016/j.brs.2014.11.018" },
      { authors: "Tracey KJ", year: 2002, title: "The inflammatory reflex", journal: "Nature", volume: "420(6917)", pages: "853–859", doi: "10.1038/nature01321" },
      { authors: "Pavlov VA, Tracey KJ", year: 2012, title: "The vagus nerve and the inflammatory reflex—linking immunity and metabolism", journal: "Nature Reviews Endocrinology", volume: "8(12)", pages: "743–754", doi: "10.1038/nrendo.2012.189" },
    ],
    ces: [
      { authors: "Kirsch DL, Nichols F", year: 2013, title: "Cranial electrotherapy stimulation for treatment of anxiety, depression, and insomnia", journal: "Psychiatric Clinics of North America", volume: "36(1)", pages: "169–176", doi: "10.1016/j.psc.2013.01.006" },
      { authors: "Barclay TH, Barclay RD", year: 2014, title: "A clinical trial of cranial electrotherapy stimulation for anxiety and comorbid depression", journal: "Journal of Affective Disorders", volume: "164", pages: "171–177", doi: "10.1016/j.jad.2014.04.029" },
      { authors: "Klawansky S, Yeung A, Berkey C, et al.", year: 1995, title: "Meta-analysis of randomized controlled trials of cranial electrostimulation: Efficacy in treating selected psychological and physiological conditions", journal: "Journal of Nervous and Mental Disease", volume: "183(7)", pages: "478–484", doi: "10.1097/00005053-199507000-00007" },
      { authors: "Kennerly RC", year: 2006, title: "Changes in quantitative EEG and low resolution electromagnetic tomography following cranial electrotherapy stimulation", journal: "Subtle Energies & Energy Medicine Journal", volume: "15(3)", pages: "1–23", doi: "" },
    ],
    network: [
      { authors: "Nofzinger EA, Buysse DJ, Germain A, et al.", year: 2004, title: "Functional neuroimaging evidence for hyperarousal in insomnia", journal: "American Journal of Psychiatry", volume: "161(11)", pages: "2126–2128", doi: "10.1176/appi.ajp.161.11.2126" },
      { authors: "Perlis ML, Smith MT, Andrews PJ, et al.", year: 2001, title: "Beta/Gamma EEG activity in patients with primary and secondary insomnia and good sleeper controls", journal: "Sleep", volume: "24(1)", pages: "110–117", doi: "10.1093/sleep/24.1.110" },
      { authors: "Spiegelhalder K, Regen W, Baglioni C, et al.", year: 2015, title: "Insomnia does not appear to be associated with substantial structural brain changes", journal: "Sleep", volume: "36(5)", pages: "731–737", doi: "10.5665/sleep.2638" },
      { authors: "Buysse DJ", year: 2013, title: "Insomnia", journal: "JAMA", volume: "309(7)", pages: "706–716", doi: "10.1001/jama.2013.193" },
      { authors: "Riemann D, Spiegelhalder K, Feige B, et al.", year: 2010, title: "The hyperarousal model of insomnia: A review of the concept and its evidence", journal: "Sleep Medicine Reviews", volume: "14(1)", pages: "19–31", doi: "10.1016/j.smrv.2009.04.002" },
    ],
  },
  // ── FNON Protocol Data (SOZO_Brain_Networks_qEEG_FNON.xlsx, April 2026) ──
  fnonPrimaryNetwork: 'Thalamocortical sleep + DMN',
  fnonSecondaryNetwork: 'DMN hyperarousal',
  fnonFBand: 'Delta/theta facilitation + beta suppression',
  fnonEegNodes: 'Fz/F3/F4(frontal)+Cz(central spindles)+bilateral mastoid (tACS/CES path)',
  fnonOscillationGoal: 'Facilitate sleep spindles(12-15Hz)+delta(0.5-4Hz); suppress hyperarousal beta; restore thalamocortical sleep rhythm',
  fnonPrimaryModalityParams: 'tACS Nexalin (77.5Hz, 15mA, forehead-bilateral mastoid, FDA cleared) OR CES Alpha-Stim (0.5Hz, 100-500μA, 20-60min before sleep)',
  fnonAddonModality: 'PEMF (delta/theta 1-8Hz, 30min pre-sleep); PBM bilateral frontal; taVNS (25Hz, 30min pre-sleep)',
  fnonSessions: '8 weeks (tACS) or 3-5 weeks (CES)',
  fnonEvidenceLevel: 'RCT (CES+tACS); High quality',
  fnonLitCount: '25+ CES; 15+ tACS; 5+ PEMF',
  fnonKeyReferences: 'Barclay 2014 meta (CES ES=-1.02); Nexalin RCTs 2022-2024; Gilula 2007 CES insomnia',
  fnonNotes: 'FNON: Sleep spindle+delta deficit are primary targets. Nexalin 77.5Hz paradoxically entrains via thalamocortical resonance. CES 0.5Hz = direct slow oscillation entrainment.',
  fnonQeegBiomarker: '↓Spindles; ↓Delta; ↑Beta',
  fnonPaperCounts: {
    tps: null, tms: null, tdcs: 10,
    tavns: 80, ces: 25, tacs: 15,
    pbm: 5, lifu: null, pemf: 5, dbs: null,
  },
  fnonBestFirstLine: 'CES (FDA cleared)',
  fnonBestSecondLine: 'tACS 77.5Hz Nexalin',
  fnonScore: 4,

};
